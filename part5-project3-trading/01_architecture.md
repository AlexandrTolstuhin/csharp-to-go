# Архитектура и доменная модель

---

## Введение

> **Для C# разработчиков**: Trading платформа на C# типично строится на ASP.NET Core + SignalR (WebSocket) + Kafka/RabbitMQ + EF Core. В Go мы заменяем всё это на более тонкие инструменты с меньшим overhead: `gorilla/websocket` (или stdlib net/http), NATS JetStream, `pgx`. Главное отличие — отсутствие ORM и управляемая вручную конкурентность через горутины.

---

## Доменные концепции

### Базовые типы

```go
package domain

import (
    "time"

    "github.com/shopspring/decimal"
)

// Symbol — торговый инструмент (тикер)
type Symbol string

const (
    SymbolBTCUSD Symbol = "BTCUSD"
    SymbolETHUSD Symbol = "ETHUSD"
)

// Side — направление ордера
type Side int8

const (
    SideBuy  Side = 1
    SideSell Side = -1
)

func (s Side) String() string {
    if s == SideBuy {
        return "BUY"
    }
    return "SELL"
}

// OrderType — тип ордера
type OrderType uint8

const (
    OrderTypeLimit  OrderType = iota // исполняется только по указанной цене
    OrderTypeMarket                   // исполняется немедленно по лучшей цене
    OrderTypeIOC                      // Immediate Or Cancel
    OrderTypeFOK                      // Fill Or Kill
)

// OrderStatus — статус ордера
type OrderStatus uint8

const (
    OrderStatusNew       OrderStatus = iota
    OrderStatusPartial               // частично исполнен
    OrderStatusFilled                // полностью исполнен
    OrderStatusCancelled
    OrderStatusRejected
)
```

### Ордер

```go
// Order — торговый ордер
// Используем decimal для точных финансовых вычислений
// (float64 неприемлем: 0.1 + 0.2 ≠ 0.3)
type Order struct {
    ID        string          // UUID v7 (монотонно возрастающий)
    ClientID  string          // ID клиента
    Symbol    Symbol
    Side      Side
    Type      OrderType
    Price     decimal.Decimal // для Market ордеров = 0
    Quantity  decimal.Decimal
    Filled    decimal.Decimal // сколько уже исполнено
    Status    OrderStatus
    CreatedAt time.Time
    UpdatedAt time.Time
}

// Remaining — остаток к исполнению
func (o *Order) Remaining() decimal.Decimal {
    return o.Quantity.Sub(o.Filled)
}

// IsFilled — полностью исполнен
func (o *Order) IsFilled() bool {
    return o.Filled.Equal(o.Quantity)
}
```

### Котировка и сделка

```go
// Tick — рыночная котировка
type Tick struct {
    Symbol    Symbol
    Price     decimal.Decimal
    Volume    decimal.Decimal
    Timestamp time.Time
}

// Trade — совершённая сделка (результат матчинга)
type Trade struct {
    ID          string
    Symbol      Symbol
    BuyOrderID  string
    SellOrderID string
    Price       decimal.Decimal
    Quantity    decimal.Decimal
    ExecutedAt  time.Time
}

// Position — позиция клиента по инструменту
type Position struct {
    ClientID    string
    Symbol      Symbol
    Quantity    decimal.Decimal // отрицательная = short
    AvgPrice    decimal.Decimal
    UnrealizedPnL decimal.Decimal
    RealizedPnL   decimal.Decimal
    UpdatedAt   time.Time
}
```

> **Почему `decimal.Decimal`, а не `float64`?**
> ```go
> // float64 — НЕ для финансов
> var price float64 = 0.1 + 0.2
> fmt.Println(price == 0.3) // false! → 0.30000000000000004
>
> // decimal — точная арифметика
> p := decimal.NewFromFloat(0.1).Add(decimal.NewFromFloat(0.2))
> fmt.Println(p.Equal(decimal.NewFromFloat(0.3))) // true
> ```
> В C# для этого используется `decimal` тип — в Go эквивалент `github.com/shopspring/decimal`.

---

## Событийная модель (NATS Subjects)

Все сервисы общаются через NATS JetStream. Subject-пространство:

| Subject | Издатель | Подписчики | Описание |
|---------|----------|------------|----------|
| `market.tick.{symbol}` | Market Data | Analytics, Risk | Рыночная котировка |
| `orders.new` | API Gateway | Order Engine | Новый ордер от клиента |
| `orders.cancel` | API Gateway | Order Engine | Отмена ордера |
| `orders.matched.{symbol}` | Order Engine | Portfolio, Risk | Сделка совершена |
| `orders.status.{clientId}` | Order Engine | API Gateway | Статус ордера клиенту |
| `risk.alert.{clientId}` | Risk Service | API Gateway | Риск-алерт |
| `portfolio.updated.{clientId}` | Portfolio | API Gateway | Обновление портфеля |

### Схема событий

```go
// events/events.go — общий пакет событий
package events

import (
    "time"
    "github.com/shopspring/decimal"
)

// TickEvent — событие котировки
type TickEvent struct {
    Symbol    string          `json:"symbol"`
    Price     decimal.Decimal `json:"price"`
    Volume    decimal.Decimal `json:"volume"`
    Timestamp time.Time       `json:"ts"`
}

// OrderEvent — новый/изменённый ордер
type OrderEvent struct {
    OrderID  string          `json:"order_id"`
    ClientID string          `json:"client_id"`
    Symbol   string          `json:"symbol"`
    Side     string          `json:"side"`
    Type     string          `json:"type"`
    Price    decimal.Decimal `json:"price"`
    Quantity decimal.Decimal `json:"qty"`
}

// TradeEvent — исполненная сделка
type TradeEvent struct {
    TradeID     string          `json:"trade_id"`
    Symbol      string          `json:"symbol"`
    BuyOrderID  string          `json:"buy_order_id"`
    SellOrderID string          `json:"sell_order_id"`
    Price       decimal.Decimal `json:"price"`
    Quantity    decimal.Decimal `json:"qty"`
    ExecutedAt  time.Time       `json:"executed_at"`
}

// RiskAlertEvent — превышение лимитов
type RiskAlertEvent struct {
    ClientID  string          `json:"client_id"`
    AlertType string          `json:"alert_type"` // "MARGIN_CALL", "POSITION_LIMIT"
    Message   string          `json:"message"`
    Severity  string          `json:"severity"` // "WARNING", "CRITICAL"
    At        time.Time       `json:"at"`
}
```

---

## Структура сервиса (шаблон)

Каждый сервис следует одной структуре:

```
service-name/
├── cmd/
│   └── server/
│       └── main.go          # точка входа, wire-up зависимостей
├── internal/
│   ├── domain/              # доменные типы (если не shared)
│   ├── <core-package>/      # основная бизнес-логика
│   ├── <infra-package>/     # адаптеры (NATS, DB, Redis)
│   └── server/              # HTTP/gRPC/WebSocket сервер
├── go.mod
└── Dockerfile
```

### Точка входа — паттерн инициализации

```go
// cmd/server/main.go
package main

import (
    "context"
    "log/slog"
    "os"
    "os/signal"
    "syscall"
    "time"
)

func main() {
    // Структурированный логгер
    logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
        Level: slog.LevelInfo,
    }))
    slog.SetDefault(logger)

    // Graceful shutdown контекст
    ctx, stop := signal.NotifyContext(context.Background(),
        syscall.SIGTERM, syscall.SIGINT)
    defer stop()

    // Инициализация приложения
    app, err := newApp(ctx)
    if err != nil {
        slog.Error("failed to initialize app", "err", err)
        os.Exit(1)
    }

    // Запуск в горутине
    errCh := make(chan error, 1)
    go func() {
        errCh <- app.Run(ctx)
    }()

    // Ожидание сигнала или ошибки
    select {
    case <-ctx.Done():
        slog.Info("shutdown signal received")
    case err := <-errCh:
        slog.Error("app error", "err", err)
    }

    // Graceful shutdown с таймаутом
    shutdownCtx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
    defer cancel()

    if err := app.Shutdown(shutdownCtx); err != nil {
        slog.Error("shutdown error", "err", err)
        os.Exit(1)
    }

    slog.Info("shutdown complete")
}
```

---

## NATS JetStream: инициализация и паттерны

### Подключение и создание streams

```go
// internal/messaging/nats.go
package messaging

import (
    "context"
    "fmt"
    "time"

    "github.com/nats-io/nats.go"
    "github.com/nats-io/nats.go/jetstream"
)

// Config — конфигурация NATS
type Config struct {
    URL             string
    StreamName      string
    Subjects        []string
    ConsumerName    string
    MaxPendingMsgs  int
}

// Client — обёртка над NATS JetStream
type Client struct {
    conn   *nats.Conn
    js     jetstream.JetStream
    stream jetstream.Stream
}

// NewClient — создание клиента с настройкой stream
func NewClient(ctx context.Context, cfg Config) (*Client, error) {
    // Подключение с reconnect логикой
    nc, err := nats.Connect(cfg.URL,
        nats.MaxReconnects(-1),           // бесконечный reconnect
        nats.ReconnectWait(2*time.Second),
        nats.DisconnectErrHandler(func(nc *nats.Conn, err error) {
            // log disconnect
        }),
        nats.ReconnectHandler(func(nc *nats.Conn) {
            // log reconnect
        }),
    )
    if err != nil {
        return nil, fmt.Errorf("nats connect: %w", err)
    }

    js, err := jetstream.New(nc)
    if err != nil {
        return nil, fmt.Errorf("jetstream: %w", err)
    }

    // Создание или обновление stream (идемпотентно)
    stream, err := js.CreateOrUpdateStream(ctx, jetstream.StreamConfig{
        Name:      cfg.StreamName,
        Subjects:  cfg.Subjects,
        Retention: jetstream.LimitsPolicy,
        MaxAge:    24 * time.Hour, // хранить 24 часа
        Storage:   jetstream.FileStorage,
        Replicas:  1, // в prod: 3
    })
    if err != nil {
        return nil, fmt.Errorf("create stream: %w", err)
    }

    return &Client{conn: nc, js: js, stream: stream}, nil
}

// Publish — публикация события
func (c *Client) Publish(ctx context.Context, subject string, data []byte) error {
    _, err := c.js.Publish(ctx, subject, data)
    return err
}

// Subscribe — подписка с durable consumer
func (c *Client) Subscribe(ctx context.Context, cfg Config, handler func(msg jetstream.Msg)) error {
    consumer, err := c.stream.CreateOrUpdateConsumer(ctx, jetstream.ConsumerConfig{
        Name:           cfg.ConsumerName,
        Durable:        cfg.ConsumerName,
        FilterSubjects: cfg.Subjects,
        AckPolicy:      jetstream.AckExplicitPolicy,
        MaxAckPending:  cfg.MaxPendingMsgs,
        DeliverPolicy:  jetstream.DeliverNewPolicy,
    })
    if err != nil {
        return fmt.Errorf("create consumer: %w", err)
    }

    // Consume — неблокирующий pull-based consumer
    _, err = consumer.Consume(handler)
    return err
}

// Close — закрытие соединения
func (c *Client) Close() {
    c.conn.Drain() // ждёт завершения всех сообщений
}
```

### Паттерн публикации с JSON

```go
// internal/messaging/publisher.go
package messaging

import (
    "context"
    "encoding/json"
    "fmt"
)

// Publisher — типизированный издатель событий
type Publisher[T any] struct {
    client  *Client
    subject string
}

// NewPublisher — создание издателя для типа T
func NewPublisher[T any](client *Client, subject string) *Publisher[T] {
    return &Publisher[T]{client: client, subject: subject}
}

// Publish — сериализация и отправка
func (p *Publisher[T]) Publish(ctx context.Context, event T) error {
    data, err := json.Marshal(event)
    if err != nil {
        return fmt.Errorf("marshal event: %w", err)
    }
    return p.client.Publish(ctx, p.subject, data)
}

// Пример использования:
// tickPublisher := messaging.NewPublisher[events.TickEvent](natsClient, "market.tick.BTCUSD")
// tickPublisher.Publish(ctx, events.TickEvent{...})
```

---

## Сравнение с C# архитектурой

| Аспект | C# (.NET) | Go |
|--------|-----------|-----|
| WebSocket fan-out | SignalR Hub groups | goroutines + channels |
| Messaging | MassTransit / NServiceBus | NATS JetStream (прямой) |
| Event serialization | System.Text.Json + MediatR | encoding/json + типы |
| Dependency injection | Microsoft.Extensions.DI | ручная композиция в main |
| Domain types | classes + records | structs |
| Financial arithmetic | `decimal` тип CLR | shopspring/decimal |
| Background workers | IHostedService | goroutine + ctx |
| Graceful shutdown | IHostApplicationLifetime | signal.NotifyContext |

> **Ключевое отличие**: В C# DI-контейнер автоматически резолвит зависимости. В Go зависимости создаются явно в `main()` или `newApp()`. Это делает граф зависимостей явным и тестируемым без reflection.

---

## Инициализация базы данных

### TimescaleDB — схема

```sql
-- migrations/001_initial.sql

-- Расширение TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Таблица котировок (time-series)
CREATE TABLE market_ticks (
    symbol      VARCHAR(20) NOT NULL,
    price       NUMERIC(20, 8) NOT NULL,
    volume      NUMERIC(20, 8) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Преобразование в гипертаблицу
SELECT create_hypertable('market_ticks', by_range('created_at'));

-- Индекс по символу
CREATE INDEX ON market_ticks (symbol, created_at DESC);

-- Сделки
CREATE TABLE trades (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol       VARCHAR(20) NOT NULL,
    buy_order_id UUID NOT NULL,
    sell_order_id UUID NOT NULL,
    price        NUMERIC(20, 8) NOT NULL,
    quantity     NUMERIC(20, 8) NOT NULL,
    executed_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

SELECT create_hypertable('trades', by_range('executed_at'));

-- Continuous aggregate: OHLCV по минутам
CREATE MATERIALIZED VIEW ohlcv_1m
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', created_at) AS bucket,
    symbol,
    FIRST(price, created_at)  AS open,
    MAX(price)                AS high,
    MIN(price)                AS low,
    LAST(price, created_at)   AS close,
    SUM(volume)               AS volume
FROM market_ticks
GROUP BY bucket, symbol
WITH NO DATA;

-- Автоматическое обновление агрегата
SELECT add_continuous_aggregate_policy('ohlcv_1m',
    start_offset => INTERVAL '2 minutes',
    end_offset   => INTERVAL '30 seconds',
    schedule_interval => INTERVAL '30 seconds'
);
```

### PostgreSQL — позиции и ордера

```sql
-- migrations/002_trading.sql

-- Клиенты
CREATE TABLE clients (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name       VARCHAR(255) NOT NULL,
    email      VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Ордера
CREATE TABLE orders (
    id          UUID PRIMARY KEY,
    client_id   UUID NOT NULL REFERENCES clients(id),
    symbol      VARCHAR(20) NOT NULL,
    side        SMALLINT NOT NULL,  -- 1=BUY, -1=SELL
    type        SMALLINT NOT NULL,
    price       NUMERIC(20, 8),     -- NULL для Market ордеров
    quantity    NUMERIC(20, 8) NOT NULL,
    filled      NUMERIC(20, 8) NOT NULL DEFAULT 0,
    status      SMALLINT NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ON orders (client_id, created_at DESC);
CREATE INDEX ON orders (symbol, status) WHERE status IN (0, 1); -- активные

-- Позиции
CREATE TABLE positions (
    client_id    UUID NOT NULL REFERENCES clients(id),
    symbol       VARCHAR(20) NOT NULL,
    quantity     NUMERIC(20, 8) NOT NULL DEFAULT 0,
    avg_price    NUMERIC(20, 8),
    realized_pnl NUMERIC(20, 8) NOT NULL DEFAULT 0,
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (client_id, symbol)
);
```

---

## Docker Compose для разработки

```yaml
# docker-compose.yml
version: '3.9'

services:
  nats:
    image: nats:2.10-alpine
    ports:
      - "4222:4222"
      - "8222:8222"  # monitoring
    command: ["--jetstream", "--store_dir=/data"]
    volumes:
      - nats_data:/data

  postgres:
    image: timescale/timescaledb:latest-pg16
    environment:
      POSTGRES_PASSWORD: trading_pass
      POSTGRES_DB: trading
    ports:
      - "5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data
      - ./migrations:/docker-entrypoint-initdb.d

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru

  # Мониторинг
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

volumes:
  nats_data:
  pg_data:
```
