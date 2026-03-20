# Производительность: GC Tuning и профилирование

---

## Введение

Trading система — один из немногих контекстов, где Go GC действительно нужно тюнить. Обычные веб-сервисы прекрасно работают с настройками по умолчанию. Но когда требования — latency P99 < 1ms для order matching и < 5ms для WebSocket fan-out — нужно понимать, как GC влияет на паузы и как это контролировать.

> **Для C# разработчиков**: CLR GC — сложнее и "умнее" (поколения, LOH, server/workstation режимы). Go GC — проще: единственный параметр `GOGC`, трёхцветная маркировка, конкурентный sweep. Основной инструмент — снижение аллокаций в hot path, а не конфигурация.

---

## Понимание Go GC в контексте trading

### Что вызывает паузы GC

```
STW (Stop-the-World) фазы в Go GC:
1. GC start — <1ms — включение write barriers
2. GC end   — <1ms — финализация

Всё остальное конкурентно с программой.

Реальная проблема — не STW паузы, а:
- CPU overhead от mark goroutines (25% CPU по умолчанию)
- Частые GC циклы при высокой частоте аллокаций → jitter
```

### Измерение GC давления

```go
// internal/metrics/gc_metrics.go
package metrics

import (
    "context"
    "log/slog"
    "runtime"
    "runtime/metrics"
    "time"
)

// GCMonitor — мониторинг GC в реальном времени
type GCMonitor struct {
    logger   *slog.Logger
    interval time.Duration
}

// NewGCMonitor — создание монитора
func NewGCMonitor(logger *slog.Logger, interval time.Duration) *GCMonitor {
    return &GCMonitor{logger: logger, interval: interval}
}

// Run — периодический сбор GC метрик
func (m *GCMonitor) Run(ctx context.Context) {
    // Используем runtime/metrics для точных измерений (Go 1.16+)
    samples := []metrics.Sample{
        {Name: "/gc/cycles/total:gc-cycles"},
        {Name: "/gc/pauses/total/other:seconds"},
        {Name: "/memory/classes/heap/objects:bytes"},
        {Name: "/memory/classes/total:bytes"},
        {Name: "/sched/latencies:seconds"},
    }

    ticker := time.NewTicker(m.interval)
    defer ticker.Stop()

    var lastGCCycles uint64

    for {
        select {
        case <-ctx.Done():
            return
        case <-ticker.C:
            metrics.Read(samples)

            gcCycles := samples[0].Value.Uint64()
            newCycles := gcCycles - lastGCCycles
            lastGCCycles = gcCycles

            var ms runtime.MemStats
            runtime.ReadMemStats(&ms)

            m.logger.Info("gc stats",
                "gc_cycles_in_period", newCycles,
                "gc_pause_us_last", ms.PauseNs[(ms.NumGC+255)%256]/1000,
                "heap_alloc_mb", ms.HeapAlloc/1024/1024,
                "heap_objects", ms.HeapObjects,
                "next_gc_mb", ms.NextGC/1024/1024,
                "gc_cpu_fraction", ms.GCCPUFraction,
            )
        }
    }
}
```

---

## GOGC и GOMEMLIMIT

### GOGC — контроль частоты GC

```bash
# GOGC = 100 (по умолчанию)
# GC запускается когда heap вырастает на 100% от предыдущего размера после GC
# Heap после GC = 100MB → GC запустится при 200MB

# GOGC = 200 — реже GC, больше памяти, меньше CPU на GC
GOGC=200 ./order-engine

# GOGC = off — никогда не запускать GC автоматически
# Опасно: использовать только в тестах или при ручном управлении
GOGC=off ./order-engine

# Для trading: GOGC=200-400 — меньше пауз, приемлемое потребление памяти
```

### GOMEMLIMIT — ограничение памяти (Go 1.19+)

```bash
# GOMEMLIMIT = жёсткий лимит на heap
# GC будет агрессивнее при приближении к лимиту
# Предотвращает OOM kill

# Для контейнера с 2GB RAM
GOMEMLIMIT=1800MiB GOGC=200 ./order-engine

# В коде (для динамических сред):
import "runtime/debug"

func init() {
    // Устанавливаем лимит = 90% от cgroup memory limit
    // В production читаем из /sys/fs/cgroup/memory/memory.limit_in_bytes
    debug.SetMemoryLimit(1800 * 1024 * 1024) // 1800 MiB
    debug.SetGCPercent(200)                   // GOGC=200
}
```

### Эффект настроек (benchmarks)

```
GOGC=100 (default):
  GC cycles/sec: 45
  P99 latency:   2.3ms
  RSS memory:    380MB

GOGC=200:
  GC cycles/sec: 22
  P99 latency:   1.1ms  ← -52%
  RSS memory:    580MB  ← +53%

GOGC=200 + GOMEMLIMIT=600MiB:
  GC cycles/sec: 28
  P99 latency:   1.4ms
  RSS memory:    550MB  ← под контролем
```

---

## Снижение аллокаций в hot path

### 1. sync.Pool для переиспользования объектов

```go
// internal/pool/pools.go
package pool

import (
    "bytes"
    "sync"
)

// BytesPool — пул байтовых буферов для сериализации
var BytesPool = sync.Pool{
    New: func() any {
        buf := make([]byte, 0, 512)
        return &buf
    },
}

// GetBytes — получение буфера из пула
func GetBytes() *[]byte {
    return BytesPool.Get().(*[]byte)
}

// PutBytes — возврат буфера в пул
func PutBytes(buf *[]byte) {
    *buf = (*buf)[:0] // сброс длины, сохранение capacity
    BytesPool.Put(buf)
}

// BufferPool — пул bytes.Buffer
var BufferPool = sync.Pool{
    New: func() any {
        return bytes.NewBuffer(make([]byte, 0, 1024))
    },
}

// Использование в marshaling:
func marshalTickFast(symbol, price, volume string, ts int64) []byte {
    buf := BytesPool.Get().(*[]byte)
    defer PutBytes(buf)

    *buf = append(*buf, `{"s":"`...)
    *buf = append(*buf, symbol...)
    *buf = append(*buf, `","p":"`...)
    *buf = append(*buf, price...)
    *buf = append(*buf, `","v":"`...)
    *buf = append(*buf, volume...)
    *buf = append(*buf, `","t":`...)
    *buf = strconv.AppendInt(*buf, ts, 10)
    *buf = append(*buf, '}')

    result := make([]byte, len(*buf))
    copy(result, *buf)
    return result
}
```

### 2. Избегание аллокаций в структурах

```go
// ❌ Каждый тик — новая аллокация Tick
type Tick struct {
    Symbol string          // аллокация строки
    Price  decimal.Decimal // аллокация decimal
}

// ✅ Числовые типы вместо decimal в hot path
// decimal используем только для хранения/вывода
type TickFast struct {
    Symbol [8]byte // фиксированный массив, нет аллокации
    Price  int64   // цена * 1e8 (fixed-point)
    Volume int64   // объём * 1e8
    Time   int64   // unix milliseconds
}

// Конвертация из decimal в int64 (один раз при получении)
func tickToFast(t domain.Tick) TickFast {
    price, _ := t.Price.Mul(decimal.NewFromInt(1e8)).Int64()
    volume, _ := t.Volume.Mul(decimal.NewFromInt(1e8)).Int64()

    var sym [8]byte
    copy(sym[:], t.Symbol)

    return TickFast{
        Symbol: sym,
        Price:  price,
        Volume: volume,
        Time:   t.Timestamp.UnixMilli(),
    }
}
```

### 3. Предаллоцированные срезы

```go
// ❌ Рост среза вызывает реаллокацию + копирование
trades := []domain.Trade{}
for {
    trade := match(order)
    trades = append(trades, trade) // может реаллоцировать
}

// ✅ Предаллоцируем с запасом (максимальное количество сделок известно)
trades := make([]domain.Trade, 0, 8) // Order book обычно даёт < 8 сделок
```

### 4. Строки без аллокаций

```go
// ❌ fmt.Sprintf аллоцирует
subject := fmt.Sprintf("orders.matched.%s", symbol)

// ✅ strings.Builder или конкатенация
subject := "orders.matched." + string(symbol)

// Ещё лучше — precomputed subjects:
var subjects = map[domain.Symbol]string{
    domain.SymbolBTCUSD: "orders.matched.BTCUSD",
    domain.SymbolETHUSD: "orders.matched.ETHUSD",
}
subject := subjects[symbol]
```

---

## pprof профилирование

### Включение pprof endpoint

```go
// cmd/server/main.go
import (
    _ "net/http/pprof" // side-effect import включает /debug/pprof/
    "net/http"
)

// Отдельный сервер для профилирования (не на prod порту)
go func() {
    http.ListenAndServe("localhost:6060", nil)
}()
```

### Сбор CPU профиля

```bash
# Собираем профиль за 30 секунд под нагрузкой
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

# Интерактивный анализ
(pprof) top20          # топ 20 функций по CPU
(pprof) top20 -cum     # с учётом вызовов
(pprof) list matchOrder # построчный анализ функции
(pprof) web            # flame graph в браузере

# Сохранение для последующего анализа
curl -s "localhost:6060/debug/pprof/profile?seconds=30" > cpu.prof
go tool pprof -http=:8081 cpu.prof
```

### Сбор профиля аллокаций

```bash
# Heap профиль (текущее состояние)
go tool pprof http://localhost:6060/debug/pprof/heap

# Что аллоцирует больше всего:
(pprof) top20 -cum -inuse_objects

# Allocs профиль (все аллокации с момента старта)
go tool pprof http://localhost:6060/debug/pprof/allocs

# Типичные находки в trading системах:
# - json.Marshal (временные map/slice)
# - fmt.Sprintf (строковые буферы)
# - time.Time (аллокация в некоторых операциях)
# - decimal.Decimal (если в hot path)
```

### Benchmark-driven оптимизация

```go
// internal/book/book_bench_test.go

// Перед оптимизацией: измеряем baseline
// go test -bench=BenchmarkMatch -benchmem -cpuprofile=before.prof

// BenchmarkMatch-8   500000   2800 ns/op   480 B/op   8 allocs/op

func BenchmarkMatch(b *testing.B) {
    ob := book.NewOrderBook(domain.SymbolBTCUSD)

    // Заполняем стакан
    for i := 0; i < 100; i++ {
        ob.Add(newLimitOrder(
            fmt.Sprintf("sell-%d", i),
            domain.SideSell,
            65000+float64(i)*10,
            1.0,
        ))
    }

    b.ResetTimer()
    b.ReportAllocs()

    for i := 0; i < b.N; i++ {
        buy := newLimitOrder("buy", domain.SideBuy, 65500, 1.0)
        ob.Add(buy)
    }
}

// После оптимизации (sync.Pool + предаллоцированные срезы):
// BenchmarkMatch-8   1200000   980 ns/op   64 B/op   1 allocs/op
// → 2.9x быстрее, 7.5x меньше аллокаций
```

---

## Трассировка: go tool trace

```go
// Трассировка для анализа goroutine scheduling
import "runtime/trace"

// Запуск трассировки
f, _ := os.Create("trace.out")
trace.Start(f)
defer trace.Stop()

// ... рабочая нагрузка ...
```

```bash
# Анализ трассировки
go tool trace trace.out

# В браузере:
# - Goroutine analysis: видим блокировки и ожидания
# - Network blocking: задержки в NATS/PostgreSQL
# - Scheduler latency: время ожидания в очереди планировщика
# - GC: когда и сколько длились GC паузы
```

---

## Lock contention анализ

```bash
# Mutex профиль (contention на блокировках)
# Сначала включаем в коде:
# runtime.SetMutexProfileFraction(5)

go tool pprof http://localhost:6060/debug/pprof/mutex

(pprof) top10
# Показывает какие мьютексы наиболее конкурентны

# Для Order Book: ожидаемо что ob.mu будет в топе при высокой нагрузке
# Решение: шардирование по первой букве символа
```

### Шардирование Order Book при высокой нагрузке

```go
// internal/book/sharded_engine.go
package book

import (
    "trading/order-engine/internal/domain"
)

const numShards = 16

// ShardedEngine — шардированный движок для масштабирования
// Каждый символ попадает в свой шард → нет конкуренции между символами
type ShardedEngine struct {
    shards [numShards]*shard
}

type shard struct {
    books map[domain.Symbol]*OrderBook
    // Каждый шард — одна горутина + канал для ордеров
    orders chan *domain.Order
    trades chan []domain.Trade
}

// symbolToShard — детерминированный выбор шарда по символу
func symbolToShard(symbol domain.Symbol) int {
    h := 0
    for _, b := range symbol {
        h = (h*31 + int(b)) & (numShards - 1)
    }
    return h
}

// Преимущество: BTCUSD и ETHUSD в разных шардах
// → независимые горутины → нет lock contention между символами
```

---

## Latency budget для trading системы

```
Полный путь ордера (целевые значения P99):

Client → NATS publish:     0.5ms  (WebSocket + network)
NATS → Order Engine:       0.3ms  (NATS internal latency)
Order matching:            0.01ms (lock + matching)
NATS publish results:      0.3ms  (2 publishes)
Portfolio/Risk processing: 1.0ms  (NATS + DB)
Result → Client:           0.5ms  (NATS + WebSocket)

Total end-to-end:          ~2.6ms P99

Для сравнения:
- Биржи (HFT): <1µs (FPGA + kernel bypass)
- Institutional: 10-100µs
- Retail algo trading: 1-10ms
- Наша цель: < 5ms → вполне достижимо
```

---

## NUMA и CPU affinity (продвинутый уровень)

```bash
# Запуск Go сервиса с CPU affinity (NUMA-aware)
# Привязка к конкретным CPU ядрам снижает cache miss

# Привязываем Order Engine к CPU 0-3 (одна NUMA нода)
taskset -c 0-3 ./order-engine

# Устанавливаем GOMAXPROCS равным количеству выделенных ядер
GOMAXPROCS=4 taskset -c 0-3 ./order-engine

# Проверка NUMA топологии
numactl --hardware

# В Go коде:
import "runtime"
runtime.GOMAXPROCS(4) // явно устанавливаем
```

---

## Итоговый чеклист оптимизации

| Шаг | Метод | Эффект |
|-----|-------|--------|
| 1. Измерить baseline | `go test -bench -benchmem` | Есть цифры для сравнения |
| 2. CPU профиль | `pprof /profile` | Найти hot functions |
| 3. Allocs профиль | `pprof /allocs` | Найти ненужные аллокации |
| 4. sync.Pool | Переиспользование объектов | -50-80% аллокаций |
| 5. Предаллоцировать срезы | `make([]T, 0, n)` | Меньше реаллокаций |
| 6. Избегать fmt.Sprintf | Конкатенация / strings.Builder | -аллокации строк |
| 7. GOGC=200 | env var | -50% GC циклов |
| 8. GOMEMLIMIT | env var | Контролируемое потребление |
| 9. Mutex profiling | `pprof /mutex` | Найти lock contention |
| 10. Шардирование | По символу | Параллелизм без конкуренции |

> **Правило**: Оптимизируй только то, что измерено. Premature optimization is the root of all evil. Сначала profile, потом код.
