# Analytics Service: TimescaleDB и агрегации

---

## Введение

Analytics Service отвечает за хранение и анализ временных рядов: котировок, объёмов торгов, сделок. Он получает тики из NATS, записывает их в TimescaleDB и предоставляет HTTP API для исторических запросов (OHLCV свечи, объёмы, volatility).

> **Для C# разработчиков**: TimescaleDB — это PostgreSQL с расширением для time-series. SQL знакомый, но добавляются специальные функции: `time_bucket()`, `first()`, `last()`, continuous aggregates. Аналог в .NET-мире — InfluxDB или Prometheus, но с полным SQL.

---

## TimescaleDB: концепции

### Гипертаблица (Hypertable)

Обычная таблица PostgreSQL, автоматически разбитая на чанки по времени:

```sql
-- Создаём обычную таблицу
CREATE TABLE market_ticks (
    symbol     VARCHAR(20)    NOT NULL,
    price      NUMERIC(20, 8) NOT NULL,
    volume     NUMERIC(20, 8) NOT NULL,
    created_at TIMESTAMPTZ    NOT NULL
);

-- Преобразуем в гипертаблицу с чанками по 1 дню
SELECT create_hypertable(
    'market_ticks',
    by_range('created_at', INTERVAL '1 day')
);

-- TimescaleDB сам управляет партиционированием
-- Запросы по времени автоматически идут только в нужные чанки
```

### Continuous Aggregates

Автоматически обновляемые материализованные представления:

```sql
-- OHLCV за 1 минуту
CREATE MATERIALIZED VIEW ohlcv_1m
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', created_at) AS bucket,
    symbol,
    FIRST(price, created_at)  AS open,   -- цена в начале интервала
    MAX(price)                AS high,
    MIN(price)                AS low,
    LAST(price, created_at)   AS close,  -- цена в конце интервала
    SUM(volume)               AS volume,
    COUNT(*)                  AS tick_count
FROM market_ticks
GROUP BY bucket, symbol
WITH NO DATA; -- не заполняем при создании

-- Политика автообновления: каждые 30 секунд
SELECT add_continuous_aggregate_policy('ohlcv_1m',
    start_offset => INTERVAL '2 minutes',
    end_offset   => INTERVAL '10 seconds',
    schedule_interval => INTERVAL '30 seconds'
);

-- OHLCV за 5 минут — поверх 1-минутного агрегата (иерархические агрегаты)
CREATE MATERIALIZED VIEW ohlcv_5m
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('5 minutes', bucket) AS bucket,
    symbol,
    FIRST(open, bucket)  AS open,
    MAX(high)            AS high,
    MIN(low)             AS low,
    LAST(close, bucket)  AS close,
    SUM(volume)          AS volume
FROM ohlcv_1m
GROUP BY time_bucket('5 minutes', bucket), symbol
WITH NO DATA;

SELECT add_continuous_aggregate_policy('ohlcv_5m',
    start_offset => INTERVAL '10 minutes',
    end_offset   => INTERVAL '30 seconds',
    schedule_interval => INTERVAL '1 minute'
);
```

---

## Analytics Service: запись тиков

### NATS Consumer → TimescaleDB

```go
// internal/ingest/ingester.go
package ingest

import (
    "context"
    "encoding/json"
    "fmt"
    "log/slog"
    "sync"
    "time"

    "github.com/jackc/pgx/v5"
    "github.com/jackc/pgx/v5/pgxpool"
    "github.com/nats-io/nats.go/jetstream"
    "github.com/shopspring/decimal"
)

// TickRecord — запись тика для batch insert
type TickRecord struct {
    Symbol    string
    Price     decimal.Decimal
    Volume    decimal.Decimal
    CreatedAt time.Time
}

// Ingester — батчевая запись тиков в TimescaleDB
// Группируем тики по батчам для снижения нагрузки на БД
type Ingester struct {
    pool    *pgxpool.Pool
    batch   []TickRecord
    mu      sync.Mutex
    maxSize int           // максимальный размер батча
    maxWait time.Duration // максимальное ожидание перед flush
    logger  *slog.Logger
}

// NewIngester — создание ingester
func NewIngester(pool *pgxpool.Pool, maxSize int, maxWait time.Duration, logger *slog.Logger) *Ingester {
    return &Ingester{
        pool:    pool,
        batch:   make([]TickRecord, 0, maxSize),
        maxSize: maxSize,
        maxWait: maxWait,
        logger:  logger,
    }
}

// Run — запуск фонового flush по таймеру
func (ing *Ingester) Run(ctx context.Context) {
    ticker := time.NewTicker(ing.maxWait)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            // Финальный flush при завершении
            ing.flush(context.Background())
            return
        case <-ticker.C:
            ing.flush(ctx)
        }
    }
}

// Add — добавление тика в батч
// Thread-safe: может вызываться из разных горутин (NATS consumers)
func (ing *Ingester) Add(tick TickRecord) {
    ing.mu.Lock()
    defer ing.mu.Unlock()

    ing.batch = append(ing.batch, tick)

    if len(ing.batch) >= ing.maxSize {
        // Срочный flush — батч заполнен
        batch := ing.batch
        ing.batch = make([]TickRecord, 0, ing.maxSize)
        ing.mu.Unlock()
        ing.writeBatch(context.Background(), batch)
        ing.mu.Lock()
    }
}

// flush — запись накопленного батча
func (ing *Ingester) flush(ctx context.Context) {
    ing.mu.Lock()
    if len(ing.batch) == 0 {
        ing.mu.Unlock()
        return
    }
    batch := ing.batch
    ing.batch = make([]TickRecord, 0, ing.maxSize)
    ing.mu.Unlock()

    ing.writeBatch(ctx, batch)
}

// writeBatch — batch insert в TimescaleDB через pgx COPY
// pgx COPY значительно быстрее batch INSERT для time-series данных
func (ing *Ingester) writeBatch(ctx context.Context, batch []TickRecord) {
    if len(batch) == 0 {
        return
    }

    start := time.Now()

    // pgx.CopyFromRows — самый быстрый способ bulk insert
    rows := make([][]any, len(batch))
    for i, tick := range batch {
        rows[i] = []any{tick.Symbol, tick.Price, tick.Volume, tick.CreatedAt}
    }

    conn, err := ing.pool.Acquire(ctx)
    if err != nil {
        ing.logger.Error("acquire connection", "err", err)
        return
    }
    defer conn.Release()

    n, err := conn.Conn().CopyFrom(
        ctx,
        pgx.Identifier{"market_ticks"},
        []string{"symbol", "price", "volume", "created_at"},
        pgx.CopyFromRows(rows),
    )

    elapsed := time.Since(start)

    if err != nil {
        ing.logger.Error("copy from", "err", err, "batch_size", len(batch))
        return
    }

    ing.logger.Debug("batch written",
        "rows", n,
        "batch_size", len(batch),
        "elapsed_ms", elapsed.Milliseconds(),
    )
}

// HandleTick — обработчик NATS сообщения
func (ing *Ingester) HandleTick(msg jetstream.Msg) {
    var event struct {
        Symbol string          `json:"symbol"`
        Price  decimal.Decimal `json:"price"`
        Volume decimal.Decimal `json:"volume"`
        Ts     int64           `json:"ts"` // unix milliseconds
    }

    if err := json.Unmarshal(msg.Data(), &event); err != nil {
        msg.Nak()
        return
    }

    ing.Add(TickRecord{
        Symbol:    event.Symbol,
        Price:     event.Price,
        Volume:    event.Volume,
        CreatedAt: time.UnixMilli(event.Ts).UTC(),
    })

    msg.Ack()
}
```

---

## HTTP API: исторические запросы

### Репозиторий

```go
// internal/query/repository.go
package query

import (
    "context"
    "fmt"
    "time"

    "github.com/jackc/pgx/v5/pgxpool"
    "github.com/shopspring/decimal"
)

// OHLCVBar — одна OHLCV свеча
type OHLCVBar struct {
    Time   time.Time
    Open   decimal.Decimal
    High   decimal.Decimal
    Low    decimal.Decimal
    Close  decimal.Decimal
    Volume decimal.Decimal
}

// Interval — интервал свечи
type Interval string

const (
    Interval1m  Interval = "1m"
    Interval5m  Interval = "5m"
    Interval1h  Interval = "1h"
    Interval1d  Interval = "1d"
)

// Repository — запросы к аналитическим данным
type Repository struct {
    pool *pgxpool.Pool
}

// NewRepository — создание репозитория
func NewRepository(pool *pgxpool.Pool) *Repository {
    return &Repository{pool: pool}
}

// GetOHLCV — получение свечей из continuous aggregate
func (r *Repository) GetOHLCV(ctx context.Context, symbol string, interval Interval, from, to time.Time) ([]OHLCVBar, error) {
    // Выбираем нужный aggregate view по интервалу
    view := r.ohlcvView(interval)

    query := fmt.Sprintf(`
        SELECT bucket, open, high, low, close, volume
        FROM %s
        WHERE symbol = $1
          AND bucket >= $2
          AND bucket < $3
        ORDER BY bucket ASC
    `, view)

    rows, err := r.pool.Query(ctx, query, symbol, from, to)
    if err != nil {
        return nil, fmt.Errorf("query ohlcv: %w", err)
    }
    defer rows.Close()

    var bars []OHLCVBar
    for rows.Next() {
        var bar OHLCVBar
        var o, h, l, c, v string
        if err := rows.Scan(&bar.Time, &o, &h, &l, &c, &v); err != nil {
            return nil, fmt.Errorf("scan bar: %w", err)
        }
        bar.Open, _ = decimal.NewFromString(o)
        bar.High, _ = decimal.NewFromString(h)
        bar.Low, _ = decimal.NewFromString(l)
        bar.Close, _ = decimal.NewFromString(c)
        bar.Volume, _ = decimal.NewFromString(v)
        bars = append(bars, bar)
    }

    return bars, rows.Err()
}

// ohlcvView — имя continuous aggregate view по интервалу
func (r *Repository) ohlcvView(interval Interval) string {
    switch interval {
    case Interval1m:
        return "ohlcv_1m"
    case Interval5m:
        return "ohlcv_5m"
    case Interval1h:
        return "ohlcv_1h"
    default:
        return "ohlcv_1d"
    }
}

// TickStats — статистика тиков за период
type TickStats struct {
    Symbol    string
    Period    string
    MinPrice  decimal.Decimal
    MaxPrice  decimal.Decimal
    AvgPrice  decimal.Decimal
    TotalVol  decimal.Decimal
    TickCount int64
}

// GetStats — агрегированная статистика
func (r *Repository) GetStats(ctx context.Context, symbol string, from, to time.Time) (*TickStats, error) {
    const query = `
        SELECT
            symbol,
            MIN(price)   AS min_price,
            MAX(price)   AS max_price,
            AVG(price)   AS avg_price,
            SUM(volume)  AS total_volume,
            COUNT(*)     AS tick_count
        FROM market_ticks
        WHERE symbol = $1
          AND created_at >= $2
          AND created_at < $3
        GROUP BY symbol
    `

    var stats TickStats
    var min, max, avg, vol string

    err := r.pool.QueryRow(ctx, query, symbol, from, to).
        Scan(&stats.Symbol, &min, &max, &avg, &vol, &stats.TickCount)
    if err != nil {
        return nil, fmt.Errorf("query stats: %w", err)
    }

    stats.MinPrice, _ = decimal.NewFromString(min)
    stats.MaxPrice, _ = decimal.NewFromString(max)
    stats.AvgPrice, _ = decimal.NewFromString(avg)
    stats.TotalVol, _ = decimal.NewFromString(vol)
    return &stats, nil
}

// GetRecentTicks — последние N тиков (для WebSocket snapshot)
func (r *Repository) GetRecentTicks(ctx context.Context, symbol string, limit int) ([]TickRecord, error) {
    const query = `
        SELECT symbol, price, volume, created_at
        FROM market_ticks
        WHERE symbol = $1
        ORDER BY created_at DESC
        LIMIT $2
    `
    rows, err := r.pool.Query(ctx, query, symbol, limit)
    if err != nil {
        return nil, fmt.Errorf("query recent ticks: %w", err)
    }
    defer rows.Close()

    var ticks []TickRecord
    for rows.Next() {
        var tick TickRecord
        var price, volume string
        if err := rows.Scan(&tick.Symbol, &price, &volume, &tick.CreatedAt); err != nil {
            return nil, err
        }
        tick.Price, _ = decimal.NewFromString(price)
        tick.Volume, _ = decimal.NewFromString(volume)
        ticks = append(ticks, tick)
    }
    return ticks, rows.Err()
}

// GetVolatility — историческая волатильность (стандартное отклонение доходностей)
func (r *Repository) GetVolatility(ctx context.Context, symbol string, days int) (float64, error) {
    // TimescaleDB: используем lag() для расчёта доходностей
    const query = `
        WITH daily_returns AS (
            SELECT
                time_bucket('1 day', bucket) AS day,
                LAST(close, bucket)          AS close_price
            FROM ohlcv_1h
            WHERE symbol = $1
              AND bucket >= NOW() - make_interval(days => $2)
            GROUP BY day
        ),
        returns AS (
            SELECT
                (close_price - LAG(close_price) OVER (ORDER BY day)) /
                LAG(close_price) OVER (ORDER BY day) * 100 AS daily_return
            FROM daily_returns
        )
        SELECT STDDEV(daily_return)
        FROM returns
        WHERE daily_return IS NOT NULL
    `

    var stddev *float64
    if err := r.pool.QueryRow(ctx, query, symbol, days).Scan(&stddev); err != nil {
        return 0, fmt.Errorf("query volatility: %w", err)
    }
    if stddev == nil {
        return 0, nil
    }
    return *stddev, nil
}
```

### HTTP Handlers

```go
// internal/server/handlers.go
package server

import (
    "encoding/json"
    "net/http"
    "strconv"
    "time"

    "trading/analytics/internal/query"
)

// AnalyticsHandler — HTTP обработчики аналитики
type AnalyticsHandler struct {
    repo *query.Repository
}

// NewAnalyticsHandler — создание handler
func NewAnalyticsHandler(repo *query.Repository) *AnalyticsHandler {
    return &AnalyticsHandler{repo: repo}
}

// RegisterRoutes — регистрация маршрутов
// GET /api/ohlcv?symbol=BTCUSD&interval=5m&from=...&to=...
// GET /api/stats?symbol=BTCUSD&from=...&to=...
// GET /api/volatility?symbol=BTCUSD&days=30
func (h *AnalyticsHandler) RegisterRoutes(mux *http.ServeMux) {
    mux.HandleFunc("GET /api/ohlcv", h.OHLCV)
    mux.HandleFunc("GET /api/stats", h.Stats)
    mux.HandleFunc("GET /api/volatility", h.Volatility)
}

// OHLCV — получение свечей
func (h *AnalyticsHandler) OHLCV(w http.ResponseWriter, r *http.Request) {
    q := r.URL.Query()
    symbol := q.Get("symbol")
    if symbol == "" {
        http.Error(w, "symbol required", http.StatusBadRequest)
        return
    }

    interval := query.Interval(q.Get("interval"))
    if interval == "" {
        interval = query.Interval1m
    }

    from, to, err := parseTimeRange(q.Get("from"), q.Get("to"))
    if err != nil {
        http.Error(w, "invalid time range: "+err.Error(), http.StatusBadRequest)
        return
    }

    bars, err := h.repo.GetOHLCV(r.Context(), symbol, interval, from, to)
    if err != nil {
        http.Error(w, "internal error", http.StatusInternalServerError)
        return
    }

    // Конвертируем в JSON-friendly формат
    type barJSON struct {
        Time   int64  `json:"t"`  // unix seconds
        Open   string `json:"o"`
        High   string `json:"h"`
        Low    string `json:"l"`
        Close  string `json:"c"`
        Volume string `json:"v"`
    }

    result := make([]barJSON, len(bars))
    for i, bar := range bars {
        result[i] = barJSON{
            Time:   bar.Time.Unix(),
            Open:   bar.Open.String(),
            High:   bar.High.String(),
            Low:    bar.Low.String(),
            Close:  bar.Close.String(),
            Volume: bar.Volume.String(),
        }
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]any{
        "symbol":   symbol,
        "interval": interval,
        "bars":     result,
        "count":    len(result),
    })
}

// Stats — статистика за период
func (h *AnalyticsHandler) Stats(w http.ResponseWriter, r *http.Request) {
    q := r.URL.Query()
    symbol := q.Get("symbol")
    if symbol == "" {
        http.Error(w, "symbol required", http.StatusBadRequest)
        return
    }

    from, to, err := parseTimeRange(q.Get("from"), q.Get("to"))
    if err != nil {
        http.Error(w, "invalid time range: "+err.Error(), http.StatusBadRequest)
        return
    }

    stats, err := h.repo.GetStats(r.Context(), symbol, from, to)
    if err != nil {
        http.Error(w, "internal error", http.StatusInternalServerError)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(stats)
}

// Volatility — историческая волатильность
func (h *AnalyticsHandler) Volatility(w http.ResponseWriter, r *http.Request) {
    q := r.URL.Query()
    symbol := q.Get("symbol")
    daysStr := q.Get("days")
    days := 30
    if daysStr != "" {
        if d, err := strconv.Atoi(daysStr); err == nil && d > 0 {
            days = d
        }
    }

    vol, err := h.repo.GetVolatility(r.Context(), symbol, days)
    if err != nil {
        http.Error(w, "internal error", http.StatusInternalServerError)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]any{
        "symbol":     symbol,
        "days":       days,
        "volatility": vol, // стандартное отклонение дневных доходностей в %
    })
}

// parseTimeRange — парсинг диапазона времени из строковых параметров
func parseTimeRange(fromStr, toStr string) (from, to time.Time, err error) {
    if fromStr == "" {
        from = time.Now().Add(-24 * time.Hour)
    } else {
        from, err = time.Parse(time.RFC3339, fromStr)
        if err != nil {
            return time.Time{}, time.Time{}, err
        }
    }

    if toStr == "" {
        to = time.Now()
    } else {
        to, err = time.Parse(time.RFC3339, toStr)
        if err != nil {
            return time.Time{}, time.Time{}, err
        }
    }

    return from, to, nil
}
```

---

## TimescaleDB: производительность

### Сравнение с plain PostgreSQL

```sql
-- Запрос к plain PostgreSQL: полный скан таблицы
EXPLAIN ANALYZE
SELECT time_bucket('1h', created_at), AVG(price)
FROM market_ticks
WHERE symbol = 'BTCUSD'
  AND created_at >= NOW() - INTERVAL '7 days';

-- Без партиционирования: Seq Scan, ~500ms на 10M строках

-- С TimescaleDB гипертаблицей: только чанки за 7 дней
-- Execution Time: 12ms (40x быстрее через chunk exclusion)
```

### Политики retention

```sql
-- Автоматическое удаление старых данных
SELECT add_retention_policy('market_ticks',
    drop_after => INTERVAL '90 days'
);

-- Сжатие данных старше 7 дней (TimescaleDB columnar compression)
ALTER TABLE market_ticks SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol',
    timescaledb.compress_orderby = 'created_at DESC'
);

SELECT add_compression_policy('market_ticks',
    compress_after => INTERVAL '7 days'
);

-- Эффект сжатия: 10x меньше места, 5-10x быстрее range queries
```

### Мониторинг гипертаблицы

```sql
-- Размер чанков
SELECT chunk_name,
       pg_size_pretty(before_compression_total_bytes) AS before,
       pg_size_pretty(after_compression_total_bytes) AS after,
       compression_ratio
FROM chunk_compression_stats('market_ticks');

-- Количество строк по чанкам
SELECT chunk_name, range_start, range_end, row_count
FROM timescaledb_information.chunks
WHERE hypertable_name = 'market_ticks'
ORDER BY range_start DESC;
```

---

## Тестирование

### Интеграционный тест с testcontainers

```go
// internal/query/repository_test.go
package query_test

import (
    "context"
    "testing"
    "time"

    "github.com/jackc/pgx/v5/pgxpool"
    "github.com/shopspring/decimal"
    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/modules/postgres"

    "trading/analytics/internal/query"
)

// TestRepository_GetOHLCV — интеграционный тест с реальным TimescaleDB
func TestRepository_GetOHLCV(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test")
    }

    ctx := context.Background()

    // Запускаем TimescaleDB в контейнере
    container, err := postgres.Run(ctx,
        "timescale/timescaledb:latest-pg16",
        postgres.WithDatabase("testdb"),
        postgres.WithUsername("test"),
        postgres.WithPassword("test"),
    )
    if err != nil {
        t.Fatalf("start container: %v", err)
    }
    t.Cleanup(func() { container.Terminate(ctx) })

    // Подключаемся
    connStr, _ := container.ConnectionString(ctx, "sslmode=disable")
    pool, err := pgxpool.New(ctx, connStr)
    if err != nil {
        t.Fatalf("connect: %v", err)
    }
    defer pool.Close()

    // Применяем миграции
    if err := applyMigrations(ctx, pool); err != nil {
        t.Fatalf("migrations: %v", err)
    }

    // Вставляем тестовые данные
    now := time.Now().UTC().Truncate(time.Minute)
    ticks := [][]any{
        {"BTCUSD", "65000", "1.0", now},
        {"BTCUSD", "65100", "0.5", now.Add(10 * time.Second)},
        {"BTCUSD", "64900", "2.0", now.Add(20 * time.Second)},
        {"BTCUSD", "65050", "0.8", now.Add(50 * time.Second)},
    }
    for _, tick := range ticks {
        pool.Exec(ctx,
            "INSERT INTO market_ticks (symbol, price, volume, created_at) VALUES ($1, $2, $3, $4)",
            tick...)
    }

    // Принудительно обновляем continuous aggregate
    pool.Exec(ctx, "CALL refresh_continuous_aggregate('ohlcv_1m', $1, $2)",
        now.Add(-time.Minute), now.Add(time.Minute))

    // Запрашиваем OHLCV
    repo := query.NewRepository(pool)
    bars, err := repo.GetOHLCV(ctx, "BTCUSD", query.Interval1m,
        now.Add(-time.Minute), now.Add(time.Minute))
    if err != nil {
        t.Fatalf("GetOHLCV: %v", err)
    }

    if len(bars) == 0 {
        t.Fatal("expected at least 1 bar")
    }

    bar := bars[0]
    // Open = первый тик = 65000
    if !bar.Open.Equal(decimal.NewFromFloat(65000)) {
        t.Errorf("open: got %s, want 65000", bar.Open)
    }
    // High = максимум = 65100
    if !bar.High.Equal(decimal.NewFromFloat(65100)) {
        t.Errorf("high: got %s, want 65100", bar.High)
    }
    // Low = минимум = 64900
    if !bar.Low.Equal(decimal.NewFromFloat(64900)) {
        t.Errorf("low: got %s, want 64900", bar.Low)
    }
    // Close = последний тик = 65050
    if !bar.Close.Equal(decimal.NewFromFloat(65050)) {
        t.Errorf("close: got %s, want 65050", bar.Close)
    }
}

// applyMigrations — применение SQL миграций в тест-контейнере
func applyMigrations(ctx context.Context, pool *pgxpool.Pool) error {
    _, err := pool.Exec(ctx, `
        CREATE EXTENSION IF NOT EXISTS timescaledb;

        CREATE TABLE market_ticks (
            symbol     VARCHAR(20)    NOT NULL,
            price      NUMERIC(20, 8) NOT NULL,
            volume     NUMERIC(20, 8) NOT NULL,
            created_at TIMESTAMPTZ    NOT NULL
        );

        SELECT create_hypertable('market_ticks', by_range('created_at'));

        CREATE MATERIALIZED VIEW ohlcv_1m
        WITH (timescaledb.continuous) AS
        SELECT
            time_bucket('1 minute', created_at) AS bucket,
            symbol,
            FIRST(price, created_at) AS open,
            MAX(price)               AS high,
            MIN(price)               AS low,
            LAST(price, created_at)  AS close,
            SUM(volume)              AS volume
        FROM market_ticks
        GROUP BY bucket, symbol
        WITH NO DATA;
    `)
    return err
}
```

---

## Сравнение подходов к time-series

| Аспект | Plain PostgreSQL | TimescaleDB | InfluxDB |
|--------|-----------------|-------------|---------|
| SQL совместимость | Полная | Полная | Нет (Flux/InfluxQL) |
| Партиционирование | Ручное | Автоматическое | Встроенное |
| Continuous aggregates | Ручной REFRESH | Автоматический | Continuous queries |
| Сжатие | pg_compression | Колончатое (10x) | TSI |
| Go клиент | pgx | pgx | influxdb-client-go |
| JOINS с другими таблицами | Да | Да | Нет |
| Знакомость для C# разработчика | Высокая | Высокая | Низкая |

> **Вывод**: TimescaleDB — оптимальный выбор для trading платформы. Получаем SQL гибкость (JOIN с клиентами, ордерами), автоматическое партиционирование, continuous aggregates и сжатие — всё в одной БД через pgx.
