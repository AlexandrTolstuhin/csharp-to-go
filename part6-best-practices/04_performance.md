# 6.4 Производительность

## Содержание
- [Введение](#введение)
- [1. Философия оптимизации](#1-философия-оптимизации)
  - [1.1 Premature optimization](#11-premature-optimization)
  - [1.2 Cost/Benefit анализ](#12-costbenefit-анализ)
  - [1.3 Когда оптимизировать](#13-когда-оптимизировать)
- [2. Zero-Allocation Patterns](#2-zero-allocation-patterns)
  - [2.1 HTTP Handlers без аллокаций](#21-http-handlers-без-аллокаций)
  - [2.2 Работа с []byte вместо string](#22-работа-с-byte-вместо-string)
  - [2.3 sync.Pool: продвинутые паттерны](#23-syncpool-продвинутые-паттерны)
  - [2.4 Stack-allocated buffers](#24-stack-allocated-buffers)
- [3. Контроль Escape Analysis](#3-контроль-escape-analysis)
  - [3.1 Правила размещения](#31-правила-размещения)
  - [3.2 Паттерны предотвращения escape](#32-паттерны-предотвращения-escape)
  - [3.3 Измерение и CI интеграция](#33-измерение-и-ci-интеграция)
- [4. Memory Layout и Alignment](#4-memory-layout-и-alignment)
  - [4.1 Struct padding в Go](#41-struct-padding-в-go)
  - [4.2 fieldalignment линтер](#42-fieldalignment-линтер)
  - [4.3 Cache-friendly структуры](#43-cache-friendly-структуры)
- [5. Compiler Optimizations](#5-compiler-optimizations)
  - [5.1 Inlining](#51-inlining)
  - [5.2 Bounds Check Elimination](#52-bounds-check-elimination)
  - [5.3 Dead Code Elimination](#53-dead-code-elimination)
  - [5.4 Как помочь компилятору](#54-как-помочь-компилятору)
- [6. Runtime в контейнерах](#6-runtime-в-контейнерах)
  - [6.1 GOMAXPROCS и cgroups](#61-gomaxprocs-и-cgroups)
  - [6.2 uber-go/automaxprocs](#62-uber-goautomaxprocs)
  - [6.3 GOMEMLIMIT в Kubernetes](#63-gomemlimit-в-kubernetes)
- [7. Production Memory Patterns](#7-production-memory-patterns)
  - [7.1 Backpressure через bounded channels](#71-backpressure-через-bounded-channels)
  - [7.2 Rate limiting memory usage](#72-rate-limiting-memory-usage)
  - [7.3 Graceful degradation](#73-graceful-degradation)
- [8. Real-World Case Studies](#8-real-world-case-studies)
  - [8.1 High-throughput JSON API](#81-high-throughput-json-api)
  - [8.2 Memory-efficient batch processing](#82-memory-efficient-batch-processing)
- [Практические примеры](#практические-примеры)
  - [Пример 1: Zero-Allocation HTTP Service](#пример-1-zero-allocation-http-service)
  - [Пример 2: Memory-Efficient Data Pipeline](#пример-2-memory-efficient-data-pipeline)
  - [Пример 3: Production Performance Audit](#пример-3-production-performance-audit)
- [Чек-лист](#чек-лист)

---

## Введение

Этот раздел фокусируется на **превентивных практиках производительности** — best practices, которые помогают избежать проблем изначально. Он дополняет материалы по профилированию и GC, рассмотренные ранее:

- **[Раздел 2.3 (GC)](../part2-advanced/03_gc.md)** — сборка мусора, базовый escape analysis, GOGC/GOMEMLIMIT
- **[Раздел 2.7 (Профилирование)](../part2-advanced/07_profiling_optimization.md)** — pprof, go tool trace, методология "Measure → Identify → Optimize → Verify"

> 💡 **Ключевое различие**: Раздел 2.7 отвечает на вопрос "Как найти проблему?". Этот раздел отвечает на вопрос "Как не создавать проблем изначально?".

### Для кого этот раздел

Для Senior C# разработчиков, которые:
- Уже знакомы с профилированием Go (pprof, benchmarks)
- Понимают, как работает GC в Go
- Хотят писать production-ready код с предсказуемой производительностью

### C# vs Go: культура производительности

| Аспект | C# / .NET | Go |
|--------|-----------|-----|
| **Hot path оптимизация** | `Span<T>`, `stackalloc`, `ArrayPool<T>` | `[]byte`, stack arrays, `sync.Pool` |
| **Object pooling** | `ObjectPool<T>` (MS.Extensions) | `sync.Pool` |
| **Memory alignment** | `StructLayout`, `FieldOffset` | Автоматическое + `fieldalignment` |
| **Container awareness** | .NET 5+ автоматически | Требует `automaxprocs` |
| **Inlining hints** | `[MethodImpl(AggressiveInlining)]` | `//go:noinline` (hint) |
| **Zero-copy strings** | `Span<char>`, `ReadOnlySpan<char>` | `unsafe.String()`, `[]byte` |
| **Escape analysis** | Нет (всё на heap кроме stackalloc) | Автоматический, можно контролировать |
| **GC tuning** | `GCSettings`, `GCHeapHardLimit` | `GOGC`, `GOMEMLIMIT` |

**Философское различие**:

```
┌─────────────────────────────────────────────────────────────────┐
│                 КУЛЬТУРА ПРОИЗВОДИТЕЛЬНОСТИ                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   C# / .NET:                                                     │
│   ──────────                                                     │
│   • GC достаточно умный — доверяй ему                           │
│   • Оптимизируй только после профилирования                     │
│   • Span<T> и stackalloc для критических путей                  │
│   • Богатый набор high-level абстракций                         │
│                                                                  │
│   Go:                                                            │
│   ────                                                           │
│   • Простота важнее микро-оптимизаций                           │
│   • Аллокации дешевле, чем в Java/C#, но не бесплатны           │
│   • Предпочитай value types и stack allocation                  │
│   • Меньше абстракций = меньше overhead                         │
│                                                                  │
│   Общее:                                                         │
│   ──────                                                         │
│   • Measure first, optimize second                               │
│   • Premature optimization — корень зла                          │
│   • Читаемость > производительность (в большинстве случаев)     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Философия оптимизации

### 1.1 Premature optimization

> "Premature optimization is the root of all evil" — Donald Knuth

Эта цитата часто неправильно интерпретируется. Полная версия:

> "We should forget about small efficiencies, say about 97% of the time: premature optimization is the root of all evil. **Yet we should not pass up our opportunities in that critical 3%.**"

**Что это значит для Go разработчика**:

```go
// ❌ Преждевременная оптимизация: sync.Pool для редко создаваемых объектов
var configPool = sync.Pool{
    New: func() any { return &Config{} },
}

func LoadConfig() *Config {
    cfg := configPool.Get().(*Config)
    // ... загрузка конфига (раз в минуту)
    return cfg
}
// Overhead пула больше, чем выигрыш — конфиг создаётся редко

// ❌ Преждевременная оптимизация: ручное управление памятью
func processItems(items []Item) {
    // Зачем? items и так на стеке если не escape
    buf := make([]byte, 0, 1024)
    _ = buf
}

// ✅ Правильно: оптимизируй после профилирования
// Сначала напиши читаемый код:
func processItems(items []Item) []Result {
    results := make([]Result, 0, len(items)) // ← OK: preallocation при известном размере
    for _, item := range items {
        results = append(results, process(item))
    }
    return results
}
```

**Признаки преждевременной оптимизации**:
- Нет benchmarks, доказывающих проблему
- Оптимизация кода, который вызывается редко
- Усложнение ради теоретического выигрыша
- "Это может понадобиться в будущем"

### 1.2 Cost/Benefit анализ

Перед оптимизацией задай вопросы:

```
┌─────────────────────────────────────────────────────────────────┐
│               COST/BENEFIT АНАЛИЗ ОПТИМИЗАЦИИ                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ВОПРОСЫ:                                                       │
│                                                                  │
│   1. Какой текущий latency P99? ──────────── [   ] ms            │
│   2. Какой целевой SLO? ──────────────────── [   ] ms            │
│   3. Сколько RPS на этот endpoint? ────────── [   ] req/s        │
│   4. Сколько времени займёт оптимизация? ─── [   ] часов         │
│   5. Насколько усложнится код? ──────────── [низко/средне/высоко]│
│   6. Кто будет поддерживать этот код? ────── [   ]               │
│                                                                  │
│   ФОРМУЛА:                                                       │
│                                                                  │
│   ROI = (Latency_saved × RPS × Hours_saved) /                    │
│         (Dev_hours × Maintenance_cost)                           │
│                                                                  │
│   Если ROI < 1 — оптимизация не оправдана                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Пример расчёта**:

```go
/*
Ситуация A: Оптимизация endpoint с 100 RPS
─────────────────────────────────────────
- Текущий P99: 50ms
- После оптимизации: 30ms (экономия 20ms)
- Время на оптимизацию: 8 часов
- Усложнение: среднее

Выигрыш: 20ms × 100 req/s = 2 секунды CPU в секунду
Вопрос: стоит ли 8 часов работы ради 2s CPU/s?
Ответ: Вероятно НЕТ (если P99 в рамках SLO)

Ситуация B: Оптимизация endpoint с 50,000 RPS
─────────────────────────────────────────────
- Текущий P99: 50ms
- После оптимизации: 30ms
- Время на оптимизацию: 8 часов

Выигрыш: 20ms × 50,000 req/s = 1000 секунд CPU в секунду
Ответ: Однозначно ДА
*/
```

### 1.3 Когда оптимизировать

**Checklist: пора оптимизировать**

```go
/*
Оптимизация ОПРАВДАНА если:

[ ] P99 latency превышает SLO
    └── Пример: SLO = 100ms, текущий P99 = 150ms

[ ] Memory usage приближается к limit
    └── Пример: Pod limit = 512MB, usage = 480MB

[ ] CPU throttling в Kubernetes
    └── Пример: container_cpu_cfs_throttled_seconds_total растёт

[ ] GC pause влияет на latency
    └── Пример: GODEBUG=gctrace=1 показывает паузы >10ms

[ ] Benchmark показывает hot path
    └── Пример: pprof показывает 60% времени в одной функции

[ ] Известный паттерн с простым решением
    └── Пример: конкатенация строк в цикле → strings.Builder

Оптимизация НЕ ОПРАВДАНА если:

[ ] "Может пригодиться в будущем"
[ ] "Я видел так в статье"
[ ] "Это выглядит неэффективно"
[ ] Нет измерений до и после
[ ] Код станет значительно сложнее
*/
```

**Сравнение с C#**:

```csharp
// C# — типичный путь к оптимизации
// 1. Application Insights показывает slow endpoint
// 2. dotTrace/PerfView для профилирования
// 3. Span<T> / stackalloc для hot paths
// 4. BenchmarkDotNet для верификации

[Benchmark]
public void ProcessData()
{
    Span<byte> buffer = stackalloc byte[256];
    // ...
}
```

```go
// Go — типичный путь к оптимизации
// 1. Prometheus/Grafana показывает slow endpoint
// 2. pprof для профилирования
// 3. Preallocations / sync.Pool для hot paths
// 4. go test -bench для верификации

func BenchmarkProcessData(b *testing.B) {
    for i := 0; i < b.N; i++ {
        processData()
    }
}
```

---

## 2. Zero-Allocation Patterns

Zero-allocation (или low-allocation) паттерны критичны для high-throughput сервисов. Каждая аллокация — это потенциальная работа для GC.

> 💡 **Связь с другими разделами**: Базовые концепции аллокаций описаны в [разделе 2.3 (GC)](../part2-advanced/03_gc.md). Здесь фокус на практических паттернах.

### 2.1 HTTP Handlers без аллокаций

**Проблема**: типичный HTTP handler создаёт много объектов на каждый запрос.

```go
// ❌ Типичный handler — много аллокаций
func handleUserBad(w http.ResponseWriter, r *http.Request) {
    // Аллокация 1: декодирование JSON в новую структуру
    var req UserRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

    // Аллокация 2: создание ответа
    resp := UserResponse{
        ID:        req.ID,
        Name:      req.Name,
        CreatedAt: time.Now(),
    }

    // Аллокация 3: сериализация JSON
    json.NewEncoder(w).Encode(resp)
}
```

**Решение**: пулы объектов + переиспользование encoder/decoder.

```go
// ✅ Optimized handler с sync.Pool

// Пулы для запросов и ответов
var (
    requestPool = sync.Pool{
        New: func() any {
            return &UserRequest{}
        },
    }

    responsePool = sync.Pool{
        New: func() any {
            return &UserResponse{}
        },
    }

    // Пул для bytes.Buffer (для JSON encoding)
    bufferPool = sync.Pool{
        New: func() any {
            return bytes.NewBuffer(make([]byte, 0, 1024))
        },
    }
)

func handleUserGood(w http.ResponseWriter, r *http.Request) {
    // Получаем объекты из пула
    req := requestPool.Get().(*UserRequest)
    resp := responsePool.Get().(*UserResponse)
    buf := bufferPool.Get().(*bytes.Buffer)

    // Гарантируем возврат в пул
    defer func() {
        // Очищаем перед возвратом
        *req = UserRequest{}
        requestPool.Put(req)

        *resp = UserResponse{}
        responsePool.Put(resp)

        buf.Reset()
        bufferPool.Put(buf)
    }()

    // Декодируем в существующий объект
    if err := json.NewDecoder(r.Body).Decode(req); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

    // Заполняем существующий объект
    resp.ID = req.ID
    resp.Name = req.Name
    resp.CreatedAt = time.Now()

    // Сериализуем в буфер
    if err := json.NewEncoder(buf).Encode(resp); err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    w.Write(buf.Bytes())
}

// Структуры с Reset методом для удобства
type UserRequest struct {
    ID   int64  `json:"id"`
    Name string `json:"name"`
}

type UserResponse struct {
    ID        int64     `json:"id"`
    Name      string    `json:"name"`
    CreatedAt time.Time `json:"created_at"`
}
```

**Benchmark сравнение**:

```go
func BenchmarkHandlerBad(b *testing.B) {
    req := httptest.NewRequest("POST", "/user",
        strings.NewReader(`{"id":1,"name":"test"}`))
    w := httptest.NewRecorder()

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        handleUserBad(w, req)
        req.Body = io.NopCloser(strings.NewReader(`{"id":1,"name":"test"}`))
        w.Body.Reset()
    }
}

func BenchmarkHandlerGood(b *testing.B) {
    req := httptest.NewRequest("POST", "/user",
        strings.NewReader(`{"id":1,"name":"test"}`))
    w := httptest.NewRecorder()

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        handleUserGood(w, req)
        req.Body = io.NopCloser(strings.NewReader(`{"id":1,"name":"test"}`))
        w.Body.Reset()
    }
}

/*
Результаты:
BenchmarkHandlerBad-8     500000    2840 ns/op    1024 B/op    12 allocs/op
BenchmarkHandlerGood-8   1500000     856 ns/op      64 B/op     2 allocs/op

Улучшение: 3.3x по скорости, 16x по аллокациям
*/
```

### 2.2 Работа с []byte вместо string

В Go `string` — immutable, а `[]byte` — mutable. Для high-performance кода часто лучше работать с `[]byte`.

```go
// ❌ Много конвертаций string ↔ []byte
func processBad(data []byte) string {
    s := string(data)           // Аллокация: копия данных в string
    s = strings.ToUpper(s)      // Аллокация: новая строка
    s = strings.TrimSpace(s)    // Аллокация: новая строка
    return s
}

// ✅ Работа с []byte напрямую
func processGood(data []byte) []byte {
    // bytes.ToUpper модифицирует in-place если capacity достаточен
    data = bytes.ToUpper(data)
    data = bytes.TrimSpace(data)
    return data
}
```

**Zero-copy конвертация** (Go 1.20+):

```go
import "unsafe"

// Zero-copy string → []byte (ТОЛЬКО для чтения!)
func stringToBytes(s string) []byte {
    return unsafe.Slice(unsafe.StringData(s), len(s))
}

// Zero-copy []byte → string
func bytesToString(b []byte) string {
    return unsafe.String(unsafe.SliceData(b), len(b))
}

// Пример использования
func processZeroCopy(data []byte) string {
    // Обрабатываем как bytes
    data = bytes.ToUpper(data)
    data = bytes.TrimSpace(data)

    // Zero-copy конвертация в string
    // ⚠️ ВАЖНО: data НЕ должна модифицироваться после этого!
    return bytesToString(data)
}
```

> ⚠️ **Предупреждение**: `unsafe.String` и `unsafe.Slice` создают string/slice, которые делят память с оригиналом. Модификация оригинала после конвертации — undefined behavior.

**Сравнение с C#**:

```csharp
// C# — Span<T> для zero-copy операций
ReadOnlySpan<char> span = "Hello World".AsSpan();
ReadOnlySpan<char> trimmed = span.Trim(); // Zero-copy

// Для bytes
ReadOnlySpan<byte> bytes = data.AsSpan();
```

```go
// Go — работа с []byte
data := []byte("Hello World")
trimmed := bytes.TrimSpace(data) // Может быть zero-copy

// Или explicit zero-copy через unsafe
s := unsafe.String(&data[0], len(data))
```

### 2.3 sync.Pool: продвинутые паттерны

> 💡 **Базовое использование sync.Pool**: см. [раздел 2.3 (GC)](../part2-advanced/03_gc.md). Здесь рассмотрим продвинутые паттерны.

**Паттерн 1: Typed Pool с Generics (Go 1.18+)**

```go
// TypedPool — generic-обёртка над sync.Pool
type TypedPool[T any] struct {
    pool sync.Pool
    new  func() T
}

// NewTypedPool создаёт типизированный пул
func NewTypedPool[T any](newFunc func() T) *TypedPool[T] {
    return &TypedPool[T]{
        pool: sync.Pool{
            New: func() any {
                return newFunc()
            },
        },
        new: newFunc,
    }
}

func (p *TypedPool[T]) Get() T {
    return p.pool.Get().(T)
}

func (p *TypedPool[T]) Put(x T) {
    p.pool.Put(x)
}

// Использование
var bufPool = NewTypedPool(func() *bytes.Buffer {
    return bytes.NewBuffer(make([]byte, 0, 4096))
})

func processWithTypedPool() {
    buf := bufPool.Get()
    defer func() {
        buf.Reset()
        bufPool.Put(buf)
    }()

    buf.WriteString("Hello")
    // ...
}
```

**Паттерн 2: Pool с метриками**

```go
import (
    "sync"
    "sync/atomic"

    "github.com/prometheus/client_golang/prometheus"
)

// MeteredPool — пул с Prometheus метриками
type MeteredPool[T any] struct {
    pool    sync.Pool
    name    string
    gets    atomic.Int64
    puts    atomic.Int64
    news    atomic.Int64

    // Prometheus метрики
    getsTotal prometheus.Counter
    putsTotal prometheus.Counter
    newsTotal prometheus.Counter
}

func NewMeteredPool[T any](name string, newFunc func() T) *MeteredPool[T] {
    p := &MeteredPool[T]{
        name: name,
        getsTotal: prometheus.NewCounter(prometheus.CounterOpts{
            Name: "pool_gets_total",
            Help: "Total number of Get calls",
            ConstLabels: prometheus.Labels{"pool": name},
        }),
        putsTotal: prometheus.NewCounter(prometheus.CounterOpts{
            Name: "pool_puts_total",
            Help: "Total number of Put calls",
            ConstLabels: prometheus.Labels{"pool": name},
        }),
        newsTotal: prometheus.NewCounter(prometheus.CounterOpts{
            Name: "pool_news_total",
            Help: "Total number of New allocations",
            ConstLabels: prometheus.Labels{"pool": name},
        }),
    }

    p.pool.New = func() any {
        p.news.Add(1)
        p.newsTotal.Inc()
        return newFunc()
    }

    // Регистрируем метрики
    prometheus.MustRegister(p.getsTotal, p.putsTotal, p.newsTotal)

    return p
}

func (p *MeteredPool[T]) Get() T {
    p.gets.Add(1)
    p.getsTotal.Inc()
    return p.pool.Get().(T)
}

func (p *MeteredPool[T]) Put(x T) {
    p.puts.Add(1)
    p.putsTotal.Inc()
    p.pool.Put(x)
}

// Stats возвращает статистику пула
func (p *MeteredPool[T]) Stats() (gets, puts, news int64) {
    return p.gets.Load(), p.puts.Load(), p.news.Load()
}
```

**Паттерн 3: Pool с ограничением размера объектов**

```go
// SizedPool — пул с проверкой размера буфера
type SizedPool struct {
    pool    sync.Pool
    maxSize int
}

func NewSizedPool(initialSize, maxSize int) *SizedPool {
    return &SizedPool{
        pool: sync.Pool{
            New: func() any {
                return bytes.NewBuffer(make([]byte, 0, initialSize))
            },
        },
        maxSize: maxSize,
    }
}

func (p *SizedPool) Get() *bytes.Buffer {
    return p.pool.Get().(*bytes.Buffer)
}

func (p *SizedPool) Put(buf *bytes.Buffer) {
    // Не возвращаем слишком большие буферы — они занимают много памяти
    if buf.Cap() > p.maxSize {
        // Пусть GC соберёт
        return
    }
    buf.Reset()
    p.pool.Put(buf)
}
```

**Когда sync.Pool вреден**:

```go
/*
НЕ используй sync.Pool если:

1. Объекты маленькие (< 64 bytes)
   └── Overhead пула > выигрыш

2. Объекты создаются редко
   └── Пул очищается между GC циклами

3. Объекты имеют сложную инициализацию
   └── Reset может пропустить состояние

4. Нужен детерминированный lifetime
   └── sync.Pool не гарантирует сохранение объектов
*/

// ❌ Плохо: маленький объект
var pointPool = sync.Pool{
    New: func() any { return &Point{} }, // 16 bytes — слишком мало
}

// ❌ Плохо: редко создаётся
var configPool = sync.Pool{
    New: func() any { return &Config{} }, // Создаётся раз в минуту
}

// ✅ Хорошо: большой объект, часто создаётся
var bufferPool = sync.Pool{
    New: func() any { return make([]byte, 0, 4096) }, // 4KB, каждый запрос
}
```

### 2.4 Stack-allocated buffers

Небольшие буферы можно размещать на стеке, избегая heap allocation.

```go
// ❌ Heap allocation
func formatIntBad(n int64) string {
    buf := make([]byte, 0, 20) // Escapes to heap
    buf = strconv.AppendInt(buf, n, 10)
    return string(buf)
}

// ✅ Stack allocation
func formatIntGood(n int64) string {
    var buf [20]byte // Stack-allocated array
    result := strconv.AppendInt(buf[:0], n, 10)
    return string(result)
}

// Benchmark:
// BenchmarkFormatIntBad-8    10000000    112 ns/op    24 B/op    2 allocs/op
// BenchmarkFormatIntGood-8   20000000     64 ns/op     8 B/op    1 allocs/op
```

**Паттерн: буфер для небольших строк**

```go
// SmallString оптимизирован для коротких строк
const smallStringSize = 64

func buildSmallString(parts ...string) string {
    // Считаем общий размер
    total := 0
    for _, p := range parts {
        total += len(p)
    }

    // Если помещается в stack buffer
    if total <= smallStringSize {
        var buf [smallStringSize]byte
        b := buf[:0]
        for _, p := range parts {
            b = append(b, p...)
        }
        return string(b)
    }

    // Иначе используем heap
    var sb strings.Builder
    sb.Grow(total)
    for _, p := range parts {
        sb.WriteString(p)
    }
    return sb.String()
}
```

**Сравнение с C#**:

```csharp
// C# — stackalloc для stack allocation
Span<byte> buffer = stackalloc byte[20];
// Используем buffer...

// Или для строк
Span<char> chars = stackalloc char[64];
```

```go
// Go — массив фиксированного размера
var buffer [20]byte
// buffer[:] для получения slice

// Или для строк
var chars [64]byte
result := string(chars[:n])
```

---

## 3. Контроль Escape Analysis

Escape Analysis определяет, где размещать объект: на стеке (быстро, автоматически очищается) или на heap (требует GC).

> 💡 **Базовые концепции**: см. [раздел 2.3 (GC)](../part2-advanced/03_gc.md). Здесь фокус на том, как **контролировать** размещение.

### 3.1 Правила размещения

```
┌─────────────────────────────────────────────────────────────────┐
│                    ESCAPE ANALYSIS: DECISION TREE                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Объект размещается на STACK если:                             │
│   ─────────────────────────────────                             │
│   1. Размер известен на этапе компиляции                        │
│   2. Не возвращается из функции                                 │
│   3. Не сохраняется в heap-allocated структуру                  │
│   4. Не передаётся в interface{}                                │
│   5. Не захватывается closure, которая escapes                  │
│   6. Размер < некоторого порога (~64KB, зависит от версии Go)   │
│                                                                  │
│   Объект размещается на HEAP если:                              │
│   ─────────────────────────────────                             │
│   • Любое из условий выше не выполняется                        │
│   • Компилятор не может доказать, что объект "умрёт" с функцией │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Таблица: что вызывает escape**

| Ситуация | Escapes? | Пример |
|----------|----------|--------|
| Возврат указателя | Да | `return &x` |
| Возврат значения | Нет | `return x` |
| Сохранение в поле struct на heap | Да | `obj.field = &x` |
| Передача в `interface{}` | Да | `fmt.Println(x)` |
| Slice с неизвестным размером | Зависит | `make([]int, n)` |
| Closure захватывает переменную | Зависит | `go func() { use(x) }()` |
| Передача в другую горутину | Да | `ch <- &x` |

### 3.2 Паттерны предотвращения escape

**Паттерн 1: Возврат значения вместо указателя**

```go
// ❌ Escapes: возвращаем указатель
func newPointBad(x, y int) *Point {
    p := Point{X: x, Y: y}
    return &p // p escapes to heap
}

// ✅ Не escapes: возвращаем значение
func newPointGood(x, y int) Point {
    return Point{X: x, Y: y} // Копируется, но остаётся на stack
}

// Использование
func process() {
    p1 := newPointBad(1, 2)   // Heap allocation
    p2 := newPointGood(3, 4)  // Stack allocation
    _ = p1
    _ = p2
}
```

**Паттерн 2: Out-параметр вместо возврата (C-style)**

```go
// ❌ Escapes: возвращаем slice
func parseBad(data []byte) ([]Token, error) {
    tokens := make([]Token, 0, 100) // Escapes
    // ... parsing
    return tokens, nil
}

// ✅ Не escapes: out-параметр
func parseGood(data []byte, tokens *[]Token) error {
    *tokens = (*tokens)[:0] // Переиспользуем backing array
    // ... parsing
    return nil
}

// Использование
func process(data []byte) {
    // Вариант 1: каждый раз новый slice (heap)
    tokens, _ := parseBad(data)

    // Вариант 2: переиспользование (может быть stack)
    var tokens []Token
    for _, data := range chunks {
        parseGood(data, &tokens)
        // process tokens...
    }
}
```

**Паттерн 3: Slice of values вместо slice of pointers**

```go
// ❌ Slice of pointers: каждый элемент — отдельная heap allocation
type NodeBad struct {
    Children []*NodeBad
}

// ✅ Slice of values: одна allocation на весь slice
type NodeGood struct {
    Children []NodeGood
}

// Для рекурсивных структур — иногда указатели неизбежны
// Но для плоских данных:

// ❌ Плохо
users := make([]*User, n)
for i := range users {
    users[i] = &User{ID: i} // n allocations
}

// ✅ Хорошо
users := make([]User, n)
for i := range users {
    users[i] = User{ID: i} // 1 allocation
}
```

**Паттерн 4: Избегание `interface{}`**

```go
// ❌ interface{} вызывает boxing
func processBad(items []any) {
    for _, item := range items {
        if v, ok := item.(int); ok {
            // ...
        }
    }
}

// ✅ Конкретный тип
func processGood(items []int) {
    for _, item := range items {
        // item уже int, без boxing
        _ = item
    }
}

// ✅ Generics (Go 1.18+)
func processGeneric[T any](items []T) {
    for _, item := range items {
        _ = item
    }
}
```

### 3.3 Измерение и CI интеграция

**Просмотр решений escape analysis**:

```bash
# Базовый вывод
go build -gcflags="-m" ./...

# Подробный вывод (рекомендуется)
go build -gcflags="-m -m" ./...

# Для конкретного пакета
go build -gcflags="-m -m" ./pkg/handler/...

# Вывод в файл для анализа
go build -gcflags="-m -m" ./... 2>&1 | grep "escapes to heap"
```

**Пример вывода**:

```
./handler.go:42:6: req escapes to heap:
./handler.go:42:6:   flow: ~r0 = &req:
./handler.go:42:6:     from &req (address-of) at ./handler.go:45:9
./handler.go:42:6:     from return &req (return) at ./handler.go:45:2
```

**CI интеграция: детектирование новых escapes**

```yaml
# .github/workflows/escape-check.yml
name: Escape Analysis Check

on: [pull_request]

jobs:
  escape-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Для сравнения с main

      - uses: actions/setup-go@v5
        with:
          go-version: '1.23'

      - name: Check for new heap escapes
        run: |
          # Escape analysis для текущей ветки
          go build -gcflags="-m" ./... 2>&1 | grep "escapes to heap" | sort > current_escapes.txt

          # Checkout main и анализ
          git checkout main
          go build -gcflags="-m" ./... 2>&1 | grep "escapes to heap" | sort > main_escapes.txt
          git checkout -

          # Сравнение
          NEW_ESCAPES=$(comm -23 current_escapes.txt main_escapes.txt)
          if [ -n "$NEW_ESCAPES" ]; then
            echo "::warning::New heap escapes detected:"
            echo "$NEW_ESCAPES"
            # Не фейлим, но предупреждаем
          fi
```

**Makefile target**:

```makefile
.PHONY: escape
escape:
	@echo "Analyzing escape analysis..."
	@go build -gcflags="-m -m" ./... 2>&1 | grep -E "(escapes to heap|moved to heap)" | \
		sort | uniq -c | sort -rn | head -20
```

---

## 4. Memory Layout и Alignment

Go автоматически выравнивает поля структур для эффективного доступа CPU. Понимание этого помогает оптимизировать память.

### 4.1 Struct padding в Go

**Правила выравнивания**:
- `bool`, `int8`, `uint8`: 1 byte alignment
- `int16`, `uint16`: 2 byte alignment
- `int32`, `uint32`, `float32`: 4 byte alignment
- `int64`, `uint64`, `float64`, указатели: 8 byte alignment (на 64-bit)

```go
import (
    "fmt"
    "unsafe"
)

// ❌ Неоптимальный порядок: 24 bytes
type BadLayout struct {
    a bool    // 1 byte
    // 7 bytes padding
    b int64   // 8 bytes
    c bool    // 1 byte
    // 7 bytes padding
}

// ✅ Оптимальный порядок: 16 bytes
type GoodLayout struct {
    b int64   // 8 bytes
    a bool    // 1 byte
    c bool    // 1 byte
    // 6 bytes padding (в конце struct для array alignment)
}

func main() {
    fmt.Printf("BadLayout size: %d\n", unsafe.Sizeof(BadLayout{}))   // 24
    fmt.Printf("GoodLayout size: %d\n", unsafe.Sizeof(GoodLayout{})) // 16

    // Проверка offset полей
    var good GoodLayout
    fmt.Printf("b offset: %d\n", unsafe.Offsetof(good.b)) // 0
    fmt.Printf("a offset: %d\n", unsafe.Offsetof(good.a)) // 8
    fmt.Printf("c offset: %d\n", unsafe.Offsetof(good.c)) // 9
}
```

**Визуализация памяти**:

```
BadLayout (24 bytes):
┌────┬───────────────┬────────────────┬────┬───────────────┐
│ a  │    padding    │       b        │ c  │    padding    │
│1 B │     7 B       │      8 B       │1 B │     7 B       │
└────┴───────────────┴────────────────┴────┴───────────────┘

GoodLayout (16 bytes):
┌────────────────┬────┬────┬──────────────┐
│       b        │ a  │ c  │   padding    │
│      8 B       │1 B │1 B │     6 B      │
└────────────────┴────┴────┴──────────────┘
```

**Сложный пример**:

```go
// ❌ 40 bytes
type User struct {
    Active    bool      // 1 + 7 padding
    ID        int64     // 8
    Age       uint8     // 1 + 3 padding
    Score     float32   // 4
    Name      string    // 16 (ptr + len)
}

// ✅ 32 bytes (20% экономии)
type UserOptimized struct {
    ID        int64     // 8
    Name      string    // 16
    Score     float32   // 4
    Age       uint8     // 1
    Active    bool      // 1 + 2 padding
}
```

### 4.2 fieldalignment линтер

**Установка и использование**:

```bash
# Установка
go install golang.org/x/tools/go/analysis/passes/fieldalignment/cmd/fieldalignment@latest

# Проверка
fieldalignment ./...

# Автоматическое исправление
fieldalignment -fix ./...
```

**Интеграция с golangci-lint**:

```yaml
# .golangci.yml
linters:
  enable:
    - fieldalignment

linters-settings:
  govet:
    enable:
      - fieldalignment

issues:
  # Можно исключить определённые пакеты
  exclude-rules:
    - path: _test\.go
      linters:
        - fieldalignment
    - path: pkg/api/
      linters:
        - fieldalignment  # API стабильность важнее
```

**Когда игнорировать**:

```go
// Иногда порядок полей важен для читаемости или API

// ✅ OK: логическая группировка важнее
type Config struct {
    // Connection settings
    Host string
    Port int

    // Timeouts (логически связаны)
    ConnectTimeout time.Duration
    ReadTimeout    time.Duration
    WriteTimeout   time.Duration

    // Feature flags
    EnableTLS bool
    EnableLog bool
}

//nolint:fieldalignment // Порядок полей — часть API
type APIResponse struct {
    Status  string `json:"status"`
    Message string `json:"message"`
    Data    any    `json:"data"`
}
```

### 4.3 Cache-friendly структуры

CPU загружает данные из RAM в cache lines (обычно 64 bytes). Структуры, помещающиеся в cache line, обрабатываются быстрее.

**Hot/Cold separation**:

```go
// ❌ Все поля вместе
type Entity struct {
    // Hot data (часто используется)
    ID       int64
    Position Vector3
    Velocity Vector3

    // Cold data (редко используется)
    Name        string
    Description string
    CreatedAt   time.Time
    UpdatedAt   time.Time
    Metadata    map[string]string
}

// ✅ Разделение hot/cold
type EntityHot struct {
    ID       int64   // 8
    Position Vector3 // 24
    Velocity Vector3 // 24
    // Итого: 56 bytes — помещается в cache line
}

type EntityCold struct {
    Name        string
    Description string
    CreatedAt   time.Time
    UpdatedAt   time.Time
    Metadata    map[string]string
}

type Entity struct {
    EntityHot              // Embedded hot data
    Cold      *EntityCold  // Указатель на cold data
}
```

**Array of Structs vs Struct of Arrays**:

```go
// AoS (Array of Structs) — стандартный подход
type ParticleAoS struct {
    X, Y, Z    float64
    VX, VY, VZ float64
}
particles := make([]ParticleAoS, 10000)

// SoA (Struct of Arrays) — cache-friendly для SIMD
type ParticlesSoA struct {
    X, Y, Z    []float64
    VX, VY, VZ []float64
}

// SoA позволяет обрабатывать X координаты всех частиц подряд
// Лучше для SIMD и prefetching
func updatePositionsSoA(p *ParticlesSoA, dt float64) {
    for i := range p.X {
        p.X[i] += p.VX[i] * dt
        p.Y[i] += p.VY[i] * dt
        p.Z[i] += p.VZ[i] * dt
    }
}

// Benchmark показывает 2-4x улучшение для SoA в тесных циклах
```

**Сравнение с C#**:

```csharp
// C# — явное управление layout
[StructLayout(LayoutKind.Sequential)]
public struct Point
{
    public int X;
    public int Y;
}

[StructLayout(LayoutKind.Explicit)]
public struct Union
{
    [FieldOffset(0)] public int Int;
    [FieldOffset(0)] public float Float;
}
```

```go
// Go — автоматическое управление, но можно влиять через порядок полей
type Point struct {
    X int
    Y int
}

// Union в Go невозможен без unsafe
// Но редко нужен
```

---

## 5. Compiler Optimizations

Go compiler выполняет множество оптимизаций. Понимание их помогает писать код, который компилятор может оптимизировать.

### 5.1 Inlining

Inlining — замена вызова функции её телом. Устраняет overhead вызова и открывает возможности для дальнейших оптимизаций.

**Просмотр решений об inlining**:

```bash
# Какие функции заинлайнены
go build -gcflags="-m" ./...

# Подробнее: почему функция НЕ заинлайнена
go build -gcflags="-m -m" ./...
```

**Факторы, влияющие на inlining**:

```go
// ✅ Будет заинлайнена: маленькая, простая
func add(a, b int) int {
    return a + b
}

// ❌ НЕ будет заинлайнена: слишком большая
func complexFunction(data []int) int {
    result := 0
    for i := 0; i < len(data); i++ {
        if data[i] > 0 {
            result += data[i] * 2
        } else {
            result -= data[i]
        }
        // ... много кода
    }
    return result
}

// ❌ НЕ будет заинлайнена: содержит defer
func withDefer() {
    defer cleanup()
    // ...
}

// ❌ НЕ будет заинлайнена: содержит recover
func withRecover() {
    defer func() {
        if r := recover(); r != nil {
            // ...
        }
    }()
}

// ❌ НЕ будет заинлайнена: вызов через interface
type Worker interface {
    Do()
}

func callWorker(w Worker) {
    w.Do() // Virtual call, не инлайнится
}
```

**Бюджет inlining**:

Go использует "бюджет" для решения об inlining. Каждая операция имеет "стоимость":
- Простые операции: 1
- Вызовы функций: 57 (если функция не инлайнится)
- Условия, циклы: увеличивают стоимость

Бюджет по умолчанию: 80 (может меняться между версиями).

**Директивы компилятора**:

```go
// Запретить inlining (для бенчмарков, отладки)
//go:noinline
func mustNotInline(x int) int {
    return x * 2
}

// Подсказка инлайнить (не гарантия!)
// Появилась в Go 1.20, но официально не документирована
//go:inline
func shouldInline(x int) int {
    return x + 1
}

// Запретить оптимизации (для отладки)
//go:norace
//go:nosplit
```

### 5.2 Bounds Check Elimination

Go проверяет границы массивов/слайсов при каждом доступе. BCE (Bounds Check Elimination) убирает эти проверки, когда компилятор доказывает их безопасность.

**Паттерны для BCE**:

```go
// ❌ Bounds check на каждой итерации
func sumBad(data []int) int {
    sum := 0
    for i := 0; i < len(data); i++ {
        sum += data[i] // Bounds check
    }
    return sum
}

// ✅ BCE: range автоматически безопасен
func sumGood(data []int) int {
    sum := 0
    for _, v := range data {
        sum += v // Без bounds check
    }
    return sum
}

// ✅ BCE: явная проверка в начале
func processSlice(data []byte) {
    if len(data) < 8 {
        return
    }
    // Компилятор знает: len >= 8
    _ = data[0] // Без bounds check
    _ = data[7] // Без bounds check
}

// ✅ BCE: трюк с последним элементом
func processFixed(data []byte) {
    if len(data) < 8 {
        return
    }
    _ = data[7] // Проверяем последний нужный индекс
    // Теперь все data[0:8] без bounds check
    for i := 0; i < 8; i++ {
        _ = data[i]
    }
}
```

**Просмотр bounds checks**:

```bash
# Показать, где остались bounds checks
go build -gcflags="-d=ssa/check_bce/debug=1" ./...
```

### 5.3 Dead Code Elimination

Компилятор удаляет код, который никогда не выполняется.

```go
const debug = false

func process() {
    // Этот блок будет полностью удалён компилятором
    if debug {
        log.Println("Debug info...")
        expensiveDebugOperation()
    }

    // Реальный код
    doWork()
}
```

**Build tags для conditional compilation**:

```go
// debug.go
//go:build debug

package mypackage

const Debug = true

// release.go
//go:build !debug

package mypackage

const Debug = false

// usage.go
package mypackage

func Process() {
    if Debug {
        // Удаляется в release build
        debugLog()
    }
}
```

```bash
# Debug build
go build -tags debug ./...

# Release build (по умолчанию)
go build ./...
```

### 5.4 Как помочь компилятору

**1. Используй `const` где возможно**:

```go
// ❌ var не оптимизируется
var bufSize = 1024
buf := make([]byte, bufSize)

// ✅ const позволяет оптимизации
const bufSize = 1024
buf := make([]byte, bufSize) // Размер известен на compile time
```

**2. Простые циклы**:

```go
// ❌ Сложное условие в цикле
for i := 0; i < len(data) && !done; i++ {
    // ...
}

// ✅ Простой цикл
for i := 0; i < len(data); i++ {
    if done {
        break
    }
    // ...
}

// ✅ Ещё лучше: range
for i, v := range data {
    if done {
        break
    }
    _ = i
    _ = v
}
```

**3. Избегай complex expressions в условиях**:

```go
// ❌ Вычисление в условии
for i := 0; i < computeLimit(); i++ {
    // computeLimit() вызывается каждую итерацию!
}

// ✅ Вычисление до цикла
limit := computeLimit()
for i := 0; i < limit; i++ {
    // ...
}
```

**4. Помогай escape analysis**:

```go
// ❌ Escapes из-за interface{}
func process(v any) {
    // ...
}

// ✅ Конкретный тип
func processInt(v int) {
    // Не escapes
}

// ✅ Generics
func processGeneric[T any](v T) {
    // Может не escape в зависимости от T
}
```

---

## 6. Runtime в контейнерах

Go runtime по умолчанию не знает о container limits. Это приводит к проблемам в Kubernetes/Docker.

### 6.1 GOMAXPROCS и cgroups

**Проблема**:

```go
/*
Хост: 32 CPU cores
Container limit: 2 CPU cores

По умолчанию:
- GOMAXPROCS = 32 (видит все CPU хоста)
- Go создаёт 32 OS threads для P (processors)
- Результат: чрезмерный context switching, CPU throttling

Container CPU = requests: 2, limits: 2
GOMAXPROCS = 32
→ 32 горутины конкурируют за 2 CPU
→ Kubernetes throttles container
→ Latency spikes
*/

import "runtime"

func main() {
    // По умолчанию — все CPU хоста
    fmt.Println(runtime.GOMAXPROCS(0)) // 32 (не 2!)
}
```

**Ручное решение**:

```go
import (
    "os"
    "runtime"
    "strconv"
)

func init() {
    // Читаем из environment
    if val := os.Getenv("GOMAXPROCS"); val == "" {
        // Kubernetes не устанавливает GOMAXPROCS
        // Нужно вычислять из cgroup limits
    }
}

// Можно установить через переменную окружения
// GOMAXPROCS=2 ./myapp
```

### 6.2 uber-go/automaxprocs

**Автоматическое решение**:

```go
import (
    _ "go.uber.org/automaxprocs" // Автоматически устанавливает GOMAXPROCS
)

func main() {
    // GOMAXPROCS теперь соответствует container CPU limit
    // Например, 2 для container с 2 CPU
}
```

**С логированием**:

```go
import (
    "log/slog"

    "go.uber.org/automaxprocs"
    "go.uber.org/automaxprocs/maxprocs"
)

func main() {
    // С кастомным логгером
    undo, err := maxprocs.Set(
        maxprocs.Logger(func(format string, args ...any) {
            slog.Info("automaxprocs", "message", fmt.Sprintf(format, args...))
        }),
    )
    if err != nil {
        slog.Error("failed to set GOMAXPROCS", "error", err)
    }
    defer undo()

    // ... приложение
}
```

**Kubernetes deployment**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
      - name: myapp
        image: myapp:latest
        resources:
          requests:
            cpu: "2"      # Гарантированные 2 CPU
            memory: "512Mi"
          limits:
            cpu: "2"      # Максимум 2 CPU
            memory: "512Mi"
        # automaxprocs автоматически установит GOMAXPROCS=2
```

**Сравнение с .NET**:

```csharp
// .NET 5+ автоматически определяет container limits
// Но можно переопределить:
Environment.SetEnvironmentVariable("DOTNET_PROCESSOR_COUNT", "2");
Environment.SetEnvironmentVariable("COMPlus_gcServer", "1");
```

```go
// Go требует явной библиотеки
import _ "go.uber.org/automaxprocs"
```

### 6.3 GOMEMLIMIT в Kubernetes

**GOMEMLIMIT** (Go 1.19+) — soft limit для памяти Go runtime.

```go
/*
Формула:
GOMEMLIMIT = container_memory_limit * 0.8

Почему 0.8:
- OS и non-Go allocations нуждаются в памяти
- OOM killer срабатывает на container limit
- 20% запас для безопасности
*/

// Пример: container limit = 512MB
// GOMEMLIMIT = 512 * 0.8 = 410MB ≈ 400MiB
```

**Способ 1: Environment variable**

```yaml
# Kubernetes deployment
spec:
  containers:
  - name: myapp
    env:
    - name: GOMEMLIMIT
      value: "400MiB"  # 80% от 512MB limit
    - name: GOGC
      value: "100"     # Или меньше для агрессивного GC
    resources:
      limits:
        memory: "512Mi"
```

**Способ 2: Downward API**

```yaml
spec:
  containers:
  - name: myapp
    env:
    - name: POD_MEMORY_LIMIT
      valueFrom:
        resourceFieldRef:
          containerName: myapp
          resource: limits.memory
    resources:
      limits:
        memory: "512Mi"
```

```go
import (
    "os"
    "runtime/debug"
    "strconv"
)

func init() {
    if limitStr := os.Getenv("POD_MEMORY_LIMIT"); limitStr != "" {
        limit, err := strconv.ParseInt(limitStr, 10, 64)
        if err == nil {
            // 80% от limit
            goMemLimit := int64(float64(limit) * 0.8)
            debug.SetMemoryLimit(goMemLimit)
        }
    }
}
```

**Способ 3: Автоматическая библиотека**

```go
import (
    _ "go.uber.org/automaxprocs"
    "github.com/KimMachineGun/automemlimit"
)

func init() {
    // Автоматически устанавливает GOMEMLIMIT на основе cgroup
    automemlimit.SetGoMemLimitWithOpts(
        automemlimit.WithRatio(0.8),
        automemlimit.WithProvider(automemlimit.FromCgroup),
    )
}
```

**Production configuration**:

```go
package main

import (
    "log/slog"
    "os"
    "runtime"
    "runtime/debug"

    _ "go.uber.org/automaxprocs"
)

func main() {
    // Log runtime settings
    slog.Info("runtime configuration",
        "GOMAXPROCS", runtime.GOMAXPROCS(0),
        "GOMEMLIMIT", debug.SetMemoryLimit(-1), // -1 возвращает текущее значение
        "GOGC", os.Getenv("GOGC"),
    )

    // ... приложение
}
```

---

## 7. Production Memory Patterns

Паттерны для контроля потребления памяти в production.

### 7.1 Backpressure через bounded channels

**Backpressure** — механизм, при котором producer замедляется, когда consumer не успевает обрабатывать.

```go
// ❌ Unbounded: producer может заполнить всю память
tasks := make(chan Task) // unbounded (на самом деле 0, но producer блокируется)

// Хуже: буферизованный без контроля
tasks := make(chan Task, 1000000) // 1M задач в памяти!

// ✅ Bounded channel с backpressure
const maxPendingTasks = 1000
tasks := make(chan Task, maxPendingTasks)

// Producer блокируется, когда буфер полон
func produce(tasks chan<- Task) {
    for {
        task := generateTask()
        tasks <- task // Блокируется при len(tasks) == maxPendingTasks
    }
}

// Consumer
func consume(tasks <-chan Task) {
    for task := range tasks {
        process(task)
    }
}
```

**Semaphore pattern**:

```go
// Ограничение concurrent operations
type Semaphore struct {
    ch chan struct{}
}

func NewSemaphore(max int) *Semaphore {
    return &Semaphore{
        ch: make(chan struct{}, max),
    }
}

func (s *Semaphore) Acquire() {
    s.ch <- struct{}{}
}

func (s *Semaphore) Release() {
    <-s.ch
}

// Использование
func processWithLimit(items []Item, maxConcurrent int) {
    sem := NewSemaphore(maxConcurrent)
    var wg sync.WaitGroup

    for _, item := range items {
        sem.Acquire()
        wg.Add(1)

        go func(item Item) {
            defer func() {
                sem.Release()
                wg.Done()
            }()
            process(item)
        }(item)
    }

    wg.Wait()
}
```

**errgroup с лимитом**:

```go
import "golang.org/x/sync/errgroup"

func processItems(ctx context.Context, items []Item) error {
    g, ctx := errgroup.WithContext(ctx)

    // Ограничиваем concurrent goroutines
    g.SetLimit(10)

    for _, item := range items {
        item := item // Capture для closure
        g.Go(func() error {
            return processItem(ctx, item)
        })
    }

    return g.Wait()
}
```

### 7.2 Rate limiting memory usage

**Мониторинг памяти**:

```go
import "runtime"

// MemoryMonitor отслеживает использование памяти
type MemoryMonitor struct {
    threshold uint64 // Порог в bytes
    interval  time.Duration
    onExceed  func(current, threshold uint64)
}

func (m *MemoryMonitor) Start(ctx context.Context) {
    ticker := time.NewTicker(m.interval)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            return
        case <-ticker.C:
            var stats runtime.MemStats
            runtime.ReadMemStats(&stats)

            if stats.Alloc > m.threshold {
                m.onExceed(stats.Alloc, m.threshold)
            }
        }
    }
}

// Использование
func main() {
    monitor := &MemoryMonitor{
        threshold: 400 * 1024 * 1024, // 400MB
        interval:  5 * time.Second,
        onExceed: func(current, threshold uint64) {
            slog.Warn("memory threshold exceeded",
                "current_mb", current/1024/1024,
                "threshold_mb", threshold/1024/1024,
            )
            // Можно запустить GC или снизить нагрузку
            runtime.GC()
        },
    }

    go monitor.Start(context.Background())
}
```

**Adaptive rate limiting**:

```go
// AdaptiveRateLimiter снижает throughput при высоком memory usage
type AdaptiveRateLimiter struct {
    baseRate      float64 // Базовый rate (requests/sec)
    memThreshold  uint64  // Порог памяти

    mu            sync.RWMutex
    currentRate   float64
    limiter       *rate.Limiter
}

func NewAdaptiveRateLimiter(baseRate float64, memThreshold uint64) *AdaptiveRateLimiter {
    arl := &AdaptiveRateLimiter{
        baseRate:     baseRate,
        memThreshold: memThreshold,
        currentRate:  baseRate,
        limiter:      rate.NewLimiter(rate.Limit(baseRate), int(baseRate)),
    }

    go arl.monitor()
    return arl
}

func (arl *AdaptiveRateLimiter) monitor() {
    ticker := time.NewTicker(time.Second)
    for range ticker.C {
        var stats runtime.MemStats
        runtime.ReadMemStats(&stats)

        // Вычисляем коэффициент
        ratio := float64(stats.Alloc) / float64(arl.memThreshold)

        var newRate float64
        switch {
        case ratio > 0.9:
            newRate = arl.baseRate * 0.1 // 10% при критичной памяти
        case ratio > 0.8:
            newRate = arl.baseRate * 0.5 // 50%
        case ratio > 0.7:
            newRate = arl.baseRate * 0.8 // 80%
        default:
            newRate = arl.baseRate // 100%
        }

        arl.mu.Lock()
        if newRate != arl.currentRate {
            arl.currentRate = newRate
            arl.limiter.SetLimit(rate.Limit(newRate))
            slog.Info("rate limit adjusted",
                "new_rate", newRate,
                "memory_ratio", ratio,
            )
        }
        arl.mu.Unlock()
    }
}

func (arl *AdaptiveRateLimiter) Allow() bool {
    return arl.limiter.Allow()
}

func (arl *AdaptiveRateLimiter) Wait(ctx context.Context) error {
    return arl.limiter.Wait(ctx)
}
```

### 7.3 Graceful degradation

**Circuit breaker для памяти**:

```go
// MemoryCircuitBreaker прекращает приём запросов при критичной памяти
type MemoryCircuitBreaker struct {
    threshold    uint64
    cooldown     time.Duration

    mu           sync.RWMutex
    isOpen       bool
    lastTripped  time.Time
}

func NewMemoryCircuitBreaker(threshold uint64, cooldown time.Duration) *MemoryCircuitBreaker {
    mcb := &MemoryCircuitBreaker{
        threshold: threshold,
        cooldown:  cooldown,
    }

    go mcb.monitor()
    return mcb
}

func (mcb *MemoryCircuitBreaker) monitor() {
    ticker := time.NewTicker(time.Second)
    for range ticker.C {
        var stats runtime.MemStats
        runtime.ReadMemStats(&stats)

        mcb.mu.Lock()
        if stats.Alloc > mcb.threshold {
            if !mcb.isOpen {
                mcb.isOpen = true
                mcb.lastTripped = time.Now()
                slog.Warn("memory circuit breaker OPEN",
                    "memory_mb", stats.Alloc/1024/1024,
                )
            }
        } else if mcb.isOpen && time.Since(mcb.lastTripped) > mcb.cooldown {
            mcb.isOpen = false
            slog.Info("memory circuit breaker CLOSED")
        }
        mcb.mu.Unlock()
    }
}

func (mcb *MemoryCircuitBreaker) Allow() bool {
    mcb.mu.RLock()
    defer mcb.mu.RUnlock()
    return !mcb.isOpen
}

// Middleware для HTTP
func (mcb *MemoryCircuitBreaker) Middleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        if !mcb.Allow() {
            http.Error(w, "Service temporarily unavailable", http.StatusServiceUnavailable)
            return
        }
        next.ServeHTTP(w, r)
    })
}
```

**Load shedding**:

```go
// LoadShedder отбрасывает запросы при перегрузке
type LoadShedder struct {
    maxQueueSize int
    queue        chan struct{}
}

func NewLoadShedder(maxQueueSize int) *LoadShedder {
    return &LoadShedder{
        maxQueueSize: maxQueueSize,
        queue:        make(chan struct{}, maxQueueSize),
    }
}

// TryEnqueue пытается добавить в очередь, возвращает false если очередь полна
func (ls *LoadShedder) TryEnqueue() bool {
    select {
    case ls.queue <- struct{}{}:
        return true
    default:
        return false // Очередь полна, отбрасываем
    }
}

func (ls *LoadShedder) Dequeue() {
    <-ls.queue
}

// Middleware
func (ls *LoadShedder) Middleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        if !ls.TryEnqueue() {
            // Load shedding: отбрасываем запрос
            w.Header().Set("Retry-After", "5")
            http.Error(w, "Server overloaded", http.StatusServiceUnavailable)

            // Метрика
            loadSheddedTotal.Inc()
            return
        }
        defer ls.Dequeue()

        next.ServeHTTP(w, r)
    })
}
```

---

## 8. Real-World Case Studies

### 8.1 High-throughput JSON API

**Ситуация**: REST API с 50,000 RPS, P99 latency 200ms (SLO: 100ms).

**Анализ** (pprof):
```
(pprof) top
Showing nodes accounting for 65% of total
      flat  flat%   sum%        cum   cum%
    2.30s  35.0%  35.0%      2.30s  35.0%  encoding/json.(*decodeState).object
    1.20s  18.0%  53.0%      1.20s  18.0%  runtime.mallocgc
    0.80s  12.0%  65.0%      0.80s  12.0%  encoding/json.Marshal
```

**Проблема**: JSON encoding/decoding занимает 50%+ CPU, много аллокаций.

**Решение**:

```go
// До: стандартная библиотека
func handleRequest(w http.ResponseWriter, r *http.Request) {
    var req Request
    json.NewDecoder(r.Body).Decode(&req)

    resp := process(req)
    json.NewEncoder(w).Encode(resp)
}

// После: easyjson + sync.Pool
//go:generate easyjson -all types.go

var (
    requestPool = sync.Pool{
        New: func() any { return &Request{} },
    }
    responsePool = sync.Pool{
        New: func() any { return &Response{} },
    }
)

func handleRequestOptimized(w http.ResponseWriter, r *http.Request) {
    req := requestPool.Get().(*Request)
    defer func() {
        req.Reset()
        requestPool.Put(req)
    }()

    // easyjson — без reflection
    if _, err := easyjson.UnmarshalFromReader(r.Body, req); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

    resp := responsePool.Get().(*Response)
    defer func() {
        resp.Reset()
        responsePool.Put(resp)
    }()

    processInto(req, resp)

    w.Header().Set("Content-Type", "application/json")
    easyjson.MarshalToHTTPResponseWriter(resp, w)
}
```

**Результат**:
```
Before:
  P99 latency: 200ms
  Allocs/req: 45
  GC pause: 15ms avg

After:
  P99 latency: 45ms (77% improvement)
  Allocs/req: 8
  GC pause: 3ms avg
```

### 8.2 Memory-efficient batch processing

**Ситуация**: Обработка 10M записей из файла, OOM при 2GB limit.

**Анализ**:
```go
// Проблема: загрузка всех данных в память
func processBad(filename string) error {
    data, err := os.ReadFile(filename) // 5GB файл в память
    if err != nil {
        return err
    }

    var records []Record
    json.Unmarshal(data, &records) // Ещё 3GB для структур

    for _, r := range records {
        process(r)
    }
    return nil
}
```

**Решение: streaming + bounded concurrency**:

```go
func processGood(ctx context.Context, filename string) error {
    file, err := os.Open(filename)
    if err != nil {
        return err
    }
    defer file.Close()

    // Streaming JSON decoder
    decoder := json.NewDecoder(file)

    // Bounded worker pool
    const numWorkers = 10
    const batchSize = 100

    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(numWorkers)

    // Пул для batch буферов
    batchPool := sync.Pool{
        New: func() any {
            return make([]Record, 0, batchSize)
        },
    }

    batch := batchPool.Get().([]Record)

    // Читаем token за token
    _, err = decoder.Token() // Открывающая скобка массива
    if err != nil {
        return err
    }

    for decoder.More() {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
        }

        var record Record
        if err := decoder.Decode(&record); err != nil {
            return err
        }

        batch = append(batch, record)

        // Отправляем batch на обработку
        if len(batch) >= batchSize {
            batchToProcess := batch
            batch = batchPool.Get().([]Record)[:0]

            g.Go(func() error {
                defer func() {
                    batchPool.Put(batchToProcess[:0])
                }()
                return processBatch(ctx, batchToProcess)
            })
        }
    }

    // Обрабатываем остаток
    if len(batch) > 0 {
        g.Go(func() error {
            defer batchPool.Put(batch[:0])
            return processBatch(ctx, batch)
        })
    }

    return g.Wait()
}

func processBatch(ctx context.Context, records []Record) error {
    for _, r := range records {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
        }

        if err := processRecord(r); err != nil {
            return err
        }
    }
    return nil
}
```

**Результат**:
```
Before:
  Peak memory: 8GB
  Result: OOM killed

After:
  Peak memory: 150MB (constant)
  Processing time: 12 minutes
  Memory usage: stable throughout
```

---

## Практические примеры

### Пример 1: Zero-Allocation HTTP Service

Полная реализация HTTP сервиса с минимальными аллокациями.

```go
package main

import (
    "bytes"
    "context"
    "encoding/json"
    "log/slog"
    "net/http"
    "sync"
    "time"

    _ "go.uber.org/automaxprocs"
)

// Request и Response structures
type UserRequest struct {
    ID   int64  `json:"id"`
    Name string `json:"name"`
}

func (r *UserRequest) Reset() {
    r.ID = 0
    r.Name = ""
}

type UserResponse struct {
    ID        int64     `json:"id"`
    Name      string    `json:"name"`
    CreatedAt time.Time `json:"created_at"`
    Status    string    `json:"status"`
}

func (r *UserResponse) Reset() {
    r.ID = 0
    r.Name = ""
    r.CreatedAt = time.Time{}
    r.Status = ""
}

// Pools
var (
    requestPool = sync.Pool{
        New: func() any { return &UserRequest{} },
    }
    responsePool = sync.Pool{
        New: func() any { return &UserResponse{} },
    }
    bufferPool = sync.Pool{
        New: func() any { return bytes.NewBuffer(make([]byte, 0, 1024)) },
    }
)

// Handler
type UserHandler struct {
    logger *slog.Logger
}

func NewUserHandler(logger *slog.Logger) *UserHandler {
    return &UserHandler{logger: logger}
}

func (h *UserHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        return
    }

    // Get objects from pools
    req := requestPool.Get().(*UserRequest)
    resp := responsePool.Get().(*UserResponse)
    buf := bufferPool.Get().(*bytes.Buffer)

    defer func() {
        req.Reset()
        requestPool.Put(req)

        resp.Reset()
        responsePool.Put(resp)

        buf.Reset()
        bufferPool.Put(buf)
    }()

    // Decode request
    if err := json.NewDecoder(r.Body).Decode(req); err != nil {
        http.Error(w, "Invalid JSON", http.StatusBadRequest)
        return
    }

    // Process (simulate business logic)
    resp.ID = req.ID
    resp.Name = req.Name
    resp.CreatedAt = time.Now()
    resp.Status = "created"

    // Encode response
    if err := json.NewEncoder(buf).Encode(resp); err != nil {
        http.Error(w, "Internal error", http.StatusInternalServerError)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    w.Write(buf.Bytes())
}

func main() {
    logger := slog.Default()

    handler := NewUserHandler(logger)

    server := &http.Server{
        Addr:         ":8080",
        Handler:      handler,
        ReadTimeout:  5 * time.Second,
        WriteTimeout: 10 * time.Second,
        IdleTimeout:  120 * time.Second,
    }

    logger.Info("starting server", "addr", server.Addr)
    if err := server.ListenAndServe(); err != nil {
        logger.Error("server error", "error", err)
    }
}
```

### Пример 2: Memory-Efficient Data Pipeline

Streaming обработка больших файлов с контролем памяти.

```go
package main

import (
    "bufio"
    "context"
    "encoding/csv"
    "fmt"
    "io"
    "log/slog"
    "os"
    "runtime"
    "sync"
    "time"

    "golang.org/x/sync/errgroup"
)

// Record представляет одну запись
type Record struct {
    ID    string
    Name  string
    Value float64
}

// Pipeline обрабатывает данные потоково
type Pipeline struct {
    workers    int
    batchSize  int
    logger     *slog.Logger

    // Memory monitoring
    memThreshold uint64
}

func NewPipeline(workers, batchSize int, memThresholdMB uint64, logger *slog.Logger) *Pipeline {
    return &Pipeline{
        workers:      workers,
        batchSize:    batchSize,
        memThreshold: memThresholdMB * 1024 * 1024,
        logger:       logger,
    }
}

func (p *Pipeline) Process(ctx context.Context, inputPath, outputPath string) error {
    // Open input
    inputFile, err := os.Open(inputPath)
    if err != nil {
        return fmt.Errorf("open input: %w", err)
    }
    defer inputFile.Close()

    // Open output
    outputFile, err := os.Create(outputPath)
    if err != nil {
        return fmt.Errorf("create output: %w", err)
    }
    defer outputFile.Close()

    outputWriter := bufio.NewWriter(outputFile)
    defer outputWriter.Flush()

    // CSV reader
    reader := csv.NewReader(bufio.NewReader(inputFile))

    // Skip header
    if _, err := reader.Read(); err != nil {
        return fmt.Errorf("read header: %w", err)
    }

    // Channels for pipeline
    batches := make(chan []Record, p.workers)
    results := make(chan []Record, p.workers)

    // Batch pool
    batchPool := sync.Pool{
        New: func() any {
            return make([]Record, 0, p.batchSize)
        },
    }

    g, ctx := errgroup.WithContext(ctx)

    // Memory monitor goroutine
    memCtx, memCancel := context.WithCancel(ctx)
    defer memCancel()

    go p.monitorMemory(memCtx)

    // Reader goroutine
    g.Go(func() error {
        defer close(batches)

        batch := batchPool.Get().([]Record)[:0]

        for {
            select {
            case <-ctx.Done():
                return ctx.Err()
            default:
            }

            row, err := reader.Read()
            if err == io.EOF {
                break
            }
            if err != nil {
                return fmt.Errorf("read row: %w", err)
            }

            record := Record{
                ID:   row[0],
                Name: row[1],
            }
            fmt.Sscanf(row[2], "%f", &record.Value)

            batch = append(batch, record)

            if len(batch) >= p.batchSize {
                select {
                case batches <- batch:
                    batch = batchPool.Get().([]Record)[:0]
                case <-ctx.Done():
                    return ctx.Err()
                }
            }
        }

        if len(batch) > 0 {
            batches <- batch
        }

        return nil
    })

    // Worker goroutines
    var workerWg sync.WaitGroup
    for i := 0; i < p.workers; i++ {
        workerWg.Add(1)
        g.Go(func() error {
            defer workerWg.Done()

            for batch := range batches {
                processed := p.processBatch(batch)

                select {
                case results <- processed:
                case <-ctx.Done():
                    return ctx.Err()
                }

                // Return batch to pool
                batchPool.Put(batch[:0])
            }
            return nil
        })
    }

    // Close results when workers done
    go func() {
        workerWg.Wait()
        close(results)
    }()

    // Writer goroutine
    g.Go(func() error {
        for batch := range results {
            for _, record := range batch {
                fmt.Fprintf(outputWriter, "%s,%s,%.2f\n",
                    record.ID, record.Name, record.Value)
            }
            // Return to pool
            batchPool.Put(batch[:0])
        }
        return nil
    })

    return g.Wait()
}

func (p *Pipeline) processBatch(batch []Record) []Record {
    // Process records in place
    for i := range batch {
        batch[i].Value = batch[i].Value * 1.1 // Example transformation
    }
    return batch
}

func (p *Pipeline) monitorMemory(ctx context.Context) {
    ticker := time.NewTicker(time.Second)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            return
        case <-ticker.C:
            var stats runtime.MemStats
            runtime.ReadMemStats(&stats)

            if stats.Alloc > p.memThreshold {
                p.logger.Warn("high memory usage",
                    "alloc_mb", stats.Alloc/1024/1024,
                    "threshold_mb", p.memThreshold/1024/1024,
                )
                runtime.GC()
            }
        }
    }
}

func main() {
    logger := slog.Default()

    pipeline := NewPipeline(
        4,    // workers
        1000, // batchSize
        400,  // memThresholdMB
        logger,
    )

    ctx := context.Background()

    start := time.Now()
    if err := pipeline.Process(ctx, "input.csv", "output.csv"); err != nil {
        logger.Error("pipeline failed", "error", err)
        os.Exit(1)
    }

    logger.Info("pipeline completed", "duration", time.Since(start))
}
```

### Пример 3: Production Performance Audit

Инструменты для аудита производительности.

**Makefile**:

```makefile
.PHONY: bench bench-compare profile-cpu profile-mem escape lint-perf

# Benchmark
bench:
	go test -bench=. -benchmem -count=5 ./... | tee bench.txt

bench-compare:
	@if [ ! -f bench-old.txt ]; then \
		echo "No baseline. Run 'make bench' first and save to bench-old.txt"; \
		exit 1; \
	fi
	go test -bench=. -benchmem -count=5 ./... | tee bench-new.txt
	benchstat bench-old.txt bench-new.txt

# Profiling
profile-cpu:
	go test -bench=BenchmarkHotPath -cpuprofile=cpu.prof ./pkg/handler
	go tool pprof -http=:8080 cpu.prof

profile-mem:
	go test -bench=BenchmarkHotPath -memprofile=mem.prof ./pkg/handler
	go tool pprof -http=:8080 mem.prof

profile-live:
	curl -o cpu.prof http://localhost:6060/debug/pprof/profile?seconds=30
	go tool pprof -http=:8080 cpu.prof

# Escape analysis
escape:
	go build -gcflags="-m -m" ./... 2>&1 | grep -E "(escapes|moved)" | \
		sort | uniq -c | sort -rn | head -30

escape-diff:
	@echo "Checking for new escapes..."
	@go build -gcflags="-m" ./... 2>&1 | grep "escapes to heap" | sort > /tmp/escapes-current.txt
	@git stash
	@go build -gcflags="-m" ./... 2>&1 | grep "escapes to heap" | sort > /tmp/escapes-base.txt
	@git stash pop
	@echo "New escapes:"
	@comm -23 /tmp/escapes-current.txt /tmp/escapes-base.txt

# Performance linters
lint-perf:
	golangci-lint run --enable=prealloc,gocritic,govet ./...

# Full audit
audit: lint-perf escape bench
	@echo "Performance audit complete"
```

**.golangci.yml** (performance focused):

```yaml
# .golangci.yml - performance-focused configuration
linters:
  enable:
    # Memory
    - prealloc          # Suggest preallocations
    - gocritic          # Various checks including performance
    - govet             # Including fieldalignment

    # General quality that affects performance
    - ineffassign       # Unused assignments
    - staticcheck       # SA* checks
    - unused            # Unused code

linters-settings:
  govet:
    enable:
      - fieldalignment  # Struct field ordering

  gocritic:
    enabled-checks:
      - appendAssign     # Inefficient append
      - appendCombine    # Can combine appends
      - hugeParam        # Large params by value
      - rangeValCopy     # Large values in range
      - sliceClear       # Use clear() instead of loop

  prealloc:
    simple: true
    range-loops: true
    for-loops: true

issues:
  exclude-rules:
    # Тесты могут быть менее оптимальными
    - path: _test\.go
      linters:
        - prealloc
        - gocritic

    # Generated code
    - path: \.pb\.go
      linters:
        - govet
```

**GitHub Actions workflow**:

```yaml
# .github/workflows/performance.yml
name: Performance Check

on:
  pull_request:
    branches: [main]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-go@v5
        with:
          go-version: '1.23'

      - name: Run benchmarks (current)
        run: go test -bench=. -benchmem -count=5 ./... | tee bench-new.txt

      - name: Checkout base branch
        run: git checkout ${{ github.base_ref }}

      - name: Run benchmarks (base)
        run: go test -bench=. -benchmem -count=5 ./... | tee bench-old.txt

      - name: Checkout PR branch
        run: git checkout ${{ github.head_ref }}

      - name: Install benchstat
        run: go install golang.org/x/perf/cmd/benchstat@latest

      - name: Compare benchmarks
        run: |
          benchstat bench-old.txt bench-new.txt | tee comparison.txt

          # Check for significant regressions (>10%)
          if grep -E "\+[1-9][0-9]\.[0-9]+%" comparison.txt; then
            echo "::warning::Significant performance regression detected"
          fi

      - name: Upload benchmark results
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-results
          path: |
            bench-old.txt
            bench-new.txt
            comparison.txt

  escape-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-go@v5
        with:
          go-version: '1.23'

      - name: Check escape analysis
        run: |
          go build -gcflags="-m" ./... 2>&1 | grep "escapes to heap" | sort > escapes.txt

          NEW_COUNT=$(wc -l < escapes.txt)
          echo "Total heap escapes: $NEW_COUNT"

          # Optional: compare with baseline
          if [ -f .baseline-escapes.txt ]; then
            BASE_COUNT=$(wc -l < .baseline-escapes.txt)
            if [ $NEW_COUNT -gt $BASE_COUNT ]; then
              echo "::warning::New heap escapes detected: $NEW_COUNT vs baseline $BASE_COUNT"
            fi
          fi

      - name: Upload escape analysis
        uses: actions/upload-artifact@v4
        with:
          name: escape-analysis
          path: escapes.txt
```

---

## Чек-лист

После изучения этого раздела вы должны:

### Философия оптимизации
- [ ] Понимать, когда оптимизация оправдана (SLO, метрики)
- [ ] Применять cost/benefit анализ перед оптимизацией
- [ ] Знать признаки premature optimization
- [ ] Всегда измерять до и после оптимизации

### Zero-Allocation Patterns
- [ ] Использовать `sync.Pool` для часто создаваемых объектов
- [ ] Знать typed pool pattern с generics
- [ ] Работать с `[]byte` вместо `string` в hot paths
- [ ] Применять stack-allocated buffers для небольших данных
- [ ] Понимать, когда sync.Pool вреден

### Escape Analysis
- [ ] Знать правила, вызывающие escape на heap
- [ ] Применять паттерны предотвращения escape
- [ ] Использовать `-gcflags="-m"` для анализа
- [ ] Интегрировать escape check в CI

### Memory Layout
- [ ] Понимать struct padding и alignment
- [ ] Использовать `fieldalignment` линтер
- [ ] Знать про cache-friendly структуры
- [ ] Применять hot/cold separation где уместно

### Compiler Optimizations
- [ ] Понимать inlining и его влияние
- [ ] Знать паттерны для bounds check elimination
- [ ] Помогать компилятору (const, простые циклы)
- [ ] Использовать build tags для conditional compilation

### Runtime в контейнерах
- [ ] Понимать проблему GOMAXPROCS в контейнерах
- [ ] Использовать `automaxprocs`
- [ ] Настраивать `GOMEMLIMIT` в Kubernetes
- [ ] Знать формулу: `GOMEMLIMIT = container_limit * 0.8`

### Production Memory Patterns
- [ ] Применять backpressure через bounded channels
- [ ] Использовать semaphore для ограничения concurrency
- [ ] Знать паттерны graceful degradation
- [ ] Мониторить память и реагировать на проблемы

---

## Следующие шаги

Переходите к [6.5 Production Checklist](./05_production_checklist.md), где рассмотрим:
- Graceful shutdown
- Health checks (liveness, readiness)
- Structured logging
- Metrics и tracing
- Rate limiting и circuit breakers

---

**Вопросы?** Открой issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Назад: 6.3 Инструменты](./03_tools.md) | [Вперёд: 6.5 Production Checklist →](./05_production_checklist.md)
