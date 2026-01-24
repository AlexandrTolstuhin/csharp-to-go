# Коллекции и производительность: Шпаргалка для Senior разработчика

## Краткий справочник по оптимизации коллекций в контексте GC

---

## Слайсы (Slices)

### ✅ DO: Хорошие практики

```go
// Предвыделяйте capacity
s := make([]int, 0, expectedSize)

// Используйте точный размер, если известен
s := make([]int, exactSize)
for i := range s {
    s[i] = computeValue(i)
}

// Переиспользуйте слайсы
buffer := make([]byte, 0, 4096)
for {
    buffer = buffer[:0] // Сброс без аллокации
    // ... использование buffer ...
}

// Копируйте маленькие подслайсы больших массивов
smallPart := make([]byte, 100)
copy(smallPart, bigSlice[:100])
return smallPart // bigSlice может быть освобожден GC

// Очищайте ссылки при удалении
s[len(s)-1] = nil
s = s[:len(s)-1]

// Используйте массивы для фиксированных размеров
var buffer [4096]byte // На стеке, нет GC давления
```

### ❌ DON'T: Антипаттерны

```go
// НЕ растите слайс без capacity
s := []int{}
for i := 0; i < 10000; i++ {
    s = append(s, i) // Множественные реаллокации!
}

// НЕ возвращайте подслайсы больших массивов
func getBigData() []byte {
    data := make([]byte, 1_000_000)
    // ...
    return data[:100] // Утечка: 1MB остается в памяти!
}

// НЕ создавайте новые слайсы в циклах
for range items {
    temp := []int{} // Аллокация каждую итерацию!
}

// НЕ забывайте очищать ссылки
func remove(s []*BigStruct, i int) []*BigStruct {
    return append(s[:i], s[i+1:]...) // Последний элемент "висит"
}
```

---

## Мапы (Maps)

### ✅ DO: Хорошие практики

```go
// Предвыделяйте размер
m := make(map[string]int, expectedSize)

// Используйте примитивные ключи
m := make(map[int]User) // Лучше, чем map[string]User

// Struct ключи для составных ключей
type CacheKey struct {
    UserID int
    Type   string
}
cache := make(map[CacheKey]Value)

// Очищайте большие мапы заменой
m = make(map[K]V) // Вместо множественных delete

// Для конкурентного доступа: sync.RWMutex или sync.Map
type SafeCache struct {
    mu sync.RWMutex
    m  map[string]Data
}

// Переиспользуйте мапы через sync.Pool
var pool = sync.Pool{
    New: func() interface{} {
        return make(map[string]int)
    },
}
m := pool.Get().(map[string]int)
defer func() {
    clear(m)
    pool.Put(m)
}()
```

### ❌ DON'T: Антипаттерны

```go
// НЕ используйте строковые составные ключи
key := fmt.Sprintf("%d:%s", id, name) // Аллокация!
m[key] = value

// НЕ ожидайте освобождения памяти после delete
for k := range m {
    delete(m, k) // Buckets остаются!
}

// НЕ используйте обычные мапы конкурентно
m := make(map[string]int)
go func() { m["key"] = 1 }() // Race condition!
go func() { m["key"] = 2 }()

// НЕ создавайте мапы без размера для больших данных
m := make(map[string]int) // Будет расти с реаллокациями
for i := 0; i < 1_000_000; i++ {
    m[fmt.Sprintf("%d", i)] = i
}
```

---

## Строки (Strings)

### ✅ DO: Хорошие практики

```go
// Используйте strings.Builder для конкатенации
var builder strings.Builder
builder.Grow(estimatedSize) // Предвыделение
for _, s := range parts {
    builder.WriteString(s)
}
result := builder.String()

// Переиспользуйте Builder
builder.Reset() // Сохраняет capacity

// Для известного количества строк: strings.Join
result := strings.Join(parts, ",")

// Для чисел: используйте strconv напрямую
s := strconv.Itoa(42)
s := strconv.FormatInt(n, 10)
```

### ❌ DON'T: Антипаттерны

```go
// НЕ используйте += для конкатенации в цикле
s := ""
for i := 0; i < 1000; i++ {
    s += "x" // O(n²) сложность!
}

// НЕ злоупотребляйте fmt.Sprintf
s := fmt.Sprintf("ID: %d", id) // Медленнее strconv

// НЕ конвертируйте []byte ↔ string в hot paths
for _, b := range data {
    s := string(b) // Копирование!
    process(s)
}
```

---

## Производительность: Сравнительная таблица

| Операция | Сложность | GC давление | Комментарий |
|----------|-----------|-------------|-------------|
| `append` без capacity | O(n) амортизированная | Высокое | Множественные реаллокации |
| `append` с capacity | O(1) | Низкое | Одна аллокация |
| Слайс от массива | O(1) | Нет | Ссылка на существующий массив |
| `copy(slice)` | O(n) | Средние | Новая аллокация |
| `map[key]` чтение | O(1) среднее | Нет | - |
| `map[key] = val` вставка | O(1) среднее | Низкое/Высокое | Высокое при rehashing |
| `delete(map, key)` | O(1) | Нет* | *Память не освобождается! |
| `string + string` | O(n+m) | Высокое | Новая аллокация |
| `strings.Builder` | O(1) амортизированная | Низкое | - |
| `[]byte(string)` | O(n) | Среднее | Копирование |

---

## Escape Analysis: Стек vs Heap

### Когда переменная "убегает" на heap:

```go
// 1. Возврат указателя
func newInt() *int {
    x := 42
    return &x // x escape to heap
}

// 2. Присваивание в структуру на heap
type Container struct {
    Data []int
}

func fillContainer(c *Container) {
    s := []int{1, 2, 3} // Может escape
    c.Data = s
}

// 3. Передача в другую горутину
func spawn() {
    x := 42
    go func() {
        fmt.Println(x) // x escape to heap
    }()
}

// 4. Присваивание в интерфейс
func toInterface() interface{} {
    x := 42
    return x // x escape to heap (boxing)
}

// 5. Слишком большой размер
func bigArray() {
    var a [100000]int // Может escape если слишком большой
}
```

### Как проверить Escape Analysis:

```bash
go build -gcflags="-m -m" main.go

# Вывод покажет:
# ./main.go:5:2: x escapes to heap
# ./main.go:5:2:   flow: ~r0 = &x
```

---

## Паттерны оптимизации

### 1. Object Pooling (sync.Pool)

**Когда использовать**: Часто создаваемые временные объекты

```go
var bufferPool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

func processData(data []byte) {
    buf := bufferPool.Get().(*bytes.Buffer)
    defer func() {
        buf.Reset()
        bufferPool.Put(buf)
    }()

    buf.Write(data)
    // ... обработка ...
}
```

**Предупреждение**: `sync.Pool` может очищаться GC! Не храните критичные данные.

### 2. Preallocate + Reuse

```go
type Processor struct {
    buffer []byte
}

func NewProcessor() *Processor {
    return &Processor{
        buffer: make([]byte, 0, 4096),
    }
}

func (p *Processor) Process(data []byte) {
    p.buffer = p.buffer[:0] // Сброс без аллокации
    p.buffer = append(p.buffer, data...)
    // ... обработка ...
}
```

### 3. Batch Processing

```go
// Плохо: обработка по одному элементу
for _, item := range items {
    process(item) // Множественные вызовы
}

// Хорошо: батчами
const batchSize = 100
for i := 0; i < len(items); i += batchSize {
    end := i + batchSize
    if end > len(items) {
        end = len(items)
    }
    processBatch(items[i:end])
}
```

### 4. In-place операции

```go
// Плохо: создание нового слайса
func transform(items []Item) []Item {
    result := make([]Item, len(items))
    for i, item := range items {
        result[i] = item.Transform()
    }
    return result
}

// Хорошо: модификация in-place
func transform(items []Item) {
    for i := range items {
        items[i].Transform()
    }
}
```

---

## Профилирование и измерения

### CPU Профилирование

```go
import (
    "os"
    "runtime/pprof"
)

func main() {
    f, _ := os.Create("cpu.prof")
    defer f.Close()
    pprof.StartCPUProfile(f)
    defer pprof.StopCPUProfile()

    // Ваш код
}
```

### Memory Профилирование

```go
import (
    "os"
    "runtime"
    "runtime/pprof"
)

func main() {
    // Ваш код

    f, _ := os.Create("mem.prof")
    defer f.Close()
    runtime.GC()
    pprof.WriteHeapProfile(f)
}
```

### Просмотр профилей

```bash
# CPU profile
go tool pprof cpu.prof
(pprof) top10
(pprof) list functionName

# Memory profile
go tool pprof mem.prof
(pprof) top10
(pprof) list functionName

# Web UI
go tool pprof -http=:8080 mem.prof
```

### Benchmark тесты

```go
func BenchmarkSliceAppend(b *testing.B) {
    b.ReportAllocs() // Показывать аллокации

    for i := 0; i < b.N; i++ {
        s := []int{}
        for j := 0; j < 1000; j++ {
            s = append(s, j)
        }
    }
}

func BenchmarkSlicePrealloc(b *testing.B) {
    b.ReportAllocs()

    for i := 0; i < b.N; i++ {
        s := make([]int, 0, 1000)
        for j := 0; j < 1000; j++ {
            s = append(s, j)
        }
    }
}
```

Запуск:
```bash
go test -bench=. -benchmem
```

Результат:
```
BenchmarkSliceAppend-8      50000   35420 ns/op   57344 B/op   10 allocs/op
BenchmarkSlicePrealloc-8   100000   10234 ns/op    8192 B/op    1 allocs/op
```

---

## Метрики GC

### Отслеживание GC

```bash
# Включить GC trace
GODEBUG=gctrace=1 ./myapp

# Вывод:
# gc 1 @0.005s 0%: 0.018+1.2+0.003 ms clock, 0.14+0.35/1.0/2.3+0.025 ms cpu, 4->4->1 MB, 5 MB goal, 8 P
```

**Расшифровка**:
- `gc 1` — номер GC цикла
- `4->4->1 MB` — heap до GC → после mark → после sweep
- `0.018+1.2+0.003 ms` — STW sweep term + concurrent mark + STW mark term

### Настройка GC

```bash
# GOGC: процент роста heap перед следующим GC (по умолчанию 100%)
GOGC=200 ./myapp  # Меньше частота GC, больше память

# GOMEMLIMIT: мягкий лимит памяти (Go 1.19+)
GOMEMLIMIT=1GiB ./myapp
```

В коде:
```go
import "runtime/debug"

// Отключить GC (только для специфичных случаев!)
debug.SetGCPercent(-1)

// Установить limit памяти
debug.SetMemoryLimit(1 << 30) // 1GB
```

---

## Checklist перед production

### Производительность коллекций:

- [ ] Слайсы с предвыделенным capacity там, где это возможно
- [ ] Мапы с начальным размером для больших данных
- [ ] Используется `strings.Builder` вместо конкатенации
- [ ] Очищаются ссылки при удалении из слайсов указателей
- [ ] Нет утечек через подслайсы больших массивов
- [ ] Конкурентный доступ к мапам защищен (Mutex/RWMutex/sync.Map)
- [ ] Используется `sync.Pool` для часто создаваемых объектов
- [ ] Escape analysis проверен для hot paths (`-gcflags="-m"`)

### Профилирование:

- [ ] CPU профиль снят и проанализирован
- [ ] Memory профиль проверен на утечки
- [ ] Benchmark тесты написаны для критичных функций
- [ ] GC metrics отслеживаются в production

### GC оптимизация:

- [ ] Минимизированы аллокации в hot paths
- [ ] Используются значения (value types) там, где возможно
- [ ] GOGC/GOMEMLIMIT настроены под workload
- [ ] Объекты переиспользуются через sync.Pool

---

## Полезные ссылки

- [Go Memory Model](https://go.dev/ref/mem)
- [Escape Analysis](https://go.dev/doc/faq#stack_or_heap)
- [GC Guide](https://go.dev/doc/gc-guide)
- [Effective Go](https://go.dev/doc/effective_go)
- [Performance Tips](https://github.com/dgryski/go-perfbook)

---

**Ключевое правило**: Измеряйте перед оптимизацией! Используйте профилировщики и бенчмарки.
