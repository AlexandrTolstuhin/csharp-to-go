# Задачи на map и синхронизацию

---

## Введение: что проверяют

Map и примитивы синхронизации — это проверка понимания **модели памяти Go** и умения выбирать правильный инструмент:

- `sync.RWMutex` vs `sync.Mutex` — когда что использовать
- `sync.Map` — для каких сценариев создан
- Почему concurrent write в обычный map — **panic**, а не race condition
- `sync.Once` — гарантия единственной инициализации

### Модель памяти Go (кратко)

> "Если два горутины обращаются к одной переменной без синхронизации, и хотя бы одна пишет — это гонка данных."

В Go нет `volatile`. Правильная синхронизация — через mutex, atomic, или канал.

---

## Задача 1: Concurrent Cache

**Компания**: Авито, Яндекс, Тинькофф
**Уровень**: Middle
**Время**: 20 минут

### Формулировка

> Реализуй потокобезопасный in-memory cache с методами `Get(key string) (int, bool)` и `Set(key string, value int)`. Оптимизируй для случая, когда чтений значительно больше, чем записей.

### Что проверяют

- Выбор `RWMutex` вместо `Mutex` (read-heavy workload)
- Правильный lock/unlock (defer)
- Понимание критической секции

**C# аналог**:
```csharp
// C# — ConcurrentDictionary или ReaderWriterLockSlim
var cache = new ConcurrentDictionary<string, int>();
// или
private readonly ReaderWriterLockSlim _lock = new();
```

**Go решение**:
```go
package cache

import "sync"

// ✅ RWMutex — оптимален для read-heavy
type Cache struct {
    mu    sync.RWMutex
    items map[string]int
}

func NewCache() *Cache {
    return &Cache{
        items: make(map[string]int),
    }
}

func (c *Cache) Get(key string) (int, bool) {
    c.mu.RLock()         // множество горутин могут читать одновременно
    defer c.mu.RUnlock()
    v, ok := c.items[key]
    return v, ok
}

func (c *Cache) Set(key string, value int) {
    c.mu.Lock()          // эксклюзивный доступ для записи
    defer c.mu.Unlock()
    c.items[key] = value
}

func (c *Cache) Delete(key string) {
    c.mu.Lock()
    defer c.mu.Unlock()
    delete(c.items, key)
}

func (c *Cache) Len() int {
    c.mu.RLock()
    defer c.mu.RUnlock()
    return len(c.items)
}
```

### Версия с TTL

```go
// ✅ Cache с TTL — реальная задача на Senior интервью
type entry struct {
    value     int
    expiresAt time.Time
}

type TTLCache struct {
    mu    sync.RWMutex
    items map[string]entry
}

func (c *TTLCache) Get(key string) (int, bool) {
    c.mu.RLock()
    e, ok := c.items[key]
    c.mu.RUnlock()

    if !ok || time.Now().After(e.expiresAt) {
        return 0, false
    }
    return e.value, true
}

func (c *TTLCache) Set(key string, value int, ttl time.Duration) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.items[key] = entry{
        value:     value,
        expiresAt: time.Now().Add(ttl),
    }
}

// Фоновая очистка просроченных ключей
func (c *TTLCache) StartCleanup(ctx context.Context, interval time.Duration) {
    go func() {
        ticker := time.NewTicker(interval)
        defer ticker.Stop()
        for {
            select {
            case <-ticker.C:
                c.cleanup()
            case <-ctx.Done():
                return
            }
        }
    }()
}

func (c *TTLCache) cleanup() {
    now := time.Now()
    c.mu.Lock()
    defer c.mu.Unlock()
    for k, e := range c.items {
        if now.After(e.expiresAt) {
            delete(c.items, k)
        }
    }
}
```

### Когда использовать sync.Map вместо RWMutex?

```go
// sync.Map создан для специфических сценариев:
// 1. Ключи устанавливаются один раз, а затем только читаются
// 2. Горутины работают с непересекающимися наборами ключей

var m sync.Map

// Set
m.Store("key", 42)

// Get
v, ok := m.Load("key")
if ok {
    fmt.Println(v.(int)) // требует type assertion!
}

// GetOrSet (атомарно)
actual, loaded := m.LoadOrStore("key", 100)

// Delete
m.Delete("key")

// Iterate
m.Range(func(k, v any) bool {
    fmt.Println(k, v)
    return true // false = остановить
})
```

> ⚠️ `sync.Map` не типизирован — требует type assertion. Для большинства production задач `RWMutex + map` лучше читаем и быстрее при write-heavy нагрузке.

### Типичные ошибки

```go
// ❌ Освобождение Lock между чтением и записью (TOCTOU)
func (c *Cache) GetOrSet(key string, value int) int {
    c.mu.RLock()
    if v, ok := c.items[key]; ok {
        c.mu.RUnlock()
        return v
    }
    c.mu.RUnlock()     // освобождаем RLock...
    // gap! другая горутина может записать сюда
    c.mu.Lock()        // берём WLock
    c.items[key] = value
    c.mu.Unlock()
    return value
}

// ✅ Правильно: Lock сразу для записи или double-check
func (c *Cache) GetOrSet(key string, value int) int {
    c.mu.Lock()
    defer c.mu.Unlock()
    if v, ok := c.items[key]; ok {
        return v
    }
    c.items[key] = value
    return value
}
```

---

## Задача 2: Частотный анализ слов (concurrent)

**Компания**: Яндекс, Авито (обработка данных)
**Уровень**: Middle
**Время**: 20 минут

### Формулировка

> Дан большой массив строк (слов). Подсчитай частоту каждого слова, используя параллельную обработку. Раздели входные данные на части, обработай каждую часть в отдельной горутине, затем объедини результаты.

### Go решение

```go
package main

import (
    "strings"
    "sync"
)

// ✅ Parallel word count: map-reduce подход
func wordCount(words []string, numWorkers int) map[string]int {
    // Разбиваем на части
    chunkSize := (len(words) + numWorkers - 1) / numWorkers

    var mu sync.Mutex
    result := make(map[string]int)
    var wg sync.WaitGroup

    for i := 0; i < len(words); i += chunkSize {
        end := i + chunkSize
        if end > len(words) {
            end = len(words)
        }
        chunk := words[i:end]

        wg.Add(1)
        go func(chunk []string) {
            defer wg.Done()

            // Локальный подсчёт (без блокировки)
            local := make(map[string]int, len(chunk))
            for _, w := range chunk {
                local[strings.ToLower(w)]++
            }

            // Merge в глобальный результат (с блокировкой)
            mu.Lock()
            for k, v := range local {
                result[k] += v
            }
            mu.Unlock()
        }(chunk)
    }

    wg.Wait()
    return result
}

// ✅ Альтернатива: через канал (избегаем mutex совсем)
func wordCountWithChannel(words []string, numWorkers int) map[string]int {
    partials := make(chan map[string]int, numWorkers)
    chunkSize := (len(words) + numWorkers - 1) / numWorkers

    var wg sync.WaitGroup
    for i := 0; i < len(words); i += chunkSize {
        end := i + chunkSize
        if end > len(words) {
            end = len(words)
        }
        chunk := words[i:end]

        wg.Add(1)
        go func(chunk []string) {
            defer wg.Done()
            local := make(map[string]int)
            for _, w := range chunk {
                local[strings.ToLower(w)]++
            }
            partials <- local
        }(chunk)
    }

    go func() {
        wg.Wait()
        close(partials)
    }()

    // Merge в одной горутине — не нужен mutex
    result := make(map[string]int)
    for partial := range partials {
        for k, v := range partial {
            result[k] += v
        }
    }
    return result
}
```

### Дополнительные вопросы

- "Когда локальный map + merge лучше глобального map + mutex?" → при высокой конкуренции на запись локальный map снижает contention
- "Как протестировать на race condition?" → `go test -race`

---

## Задача 3: Реализация Once

**Компания**: Яндекс, ВКонтакте
**Уровень**: Senior
**Время**: 20 минут

### Формулировка

> Реализуй аналог `sync.Once` без использования стандартной библиотеки. Метод `Do(f func())` должен вызвать `f` ровно один раз, даже при конкурентных вызовах.

### Что проверяют

- Понимание memory visibility в Go
- Использование atomic для быстрого пути (fast path)
- Mutex для гарантии однократного выполнения

```go
// ✅ Собственная реализация Once

type MyOnce struct {
    done atomic.Uint32  // 0 = не выполнено, 1 = выполнено
    mu   sync.Mutex
}

func (o *MyOnce) Do(f func()) {
    // Fast path: уже выполнено → атомарная проверка без блокировки
    if o.done.Load() == 1 {
        return
    }

    // Slow path: первый вызов
    o.mu.Lock()
    defer o.mu.Unlock()

    // Double-check: другая горутина могла выполнить f пока мы ждали Lock
    if o.done.Load() == 0 {
        defer o.done.Store(1) // устанавливаем ПОСЛЕ выполнения f
        f()
    }
}

// Сравнение со стандартным sync.Once:
var once sync.Once
once.Do(func() {
    // инициализация singleton
})
```

> 💡 Паттерн "fast path + slow path с double-check" — фундаментальный паттерн конкурентного программирования. Встречается в Java (Double-Checked Locking), C++ (call_once).

### Реальное применение: lazy singleton

```go
// ✅ Паттерн singleton в Go — через Once
type DBPool struct {
    pool *sql.DB
}

var (
    instance *DBPool
    once     sync.Once
)

func GetDB() *DBPool {
    once.Do(func() {
        db, err := sql.Open("postgres", dsn)
        if err != nil {
            panic(err) // или log.Fatal
        }
        instance = &DBPool{pool: db}
    })
    return instance
}
```

---

## Задача 4: Семафор

**Компания**: Авито, Яндекс (ограничение параллельных запросов к БД)
**Уровень**: Middle / Senior
**Время**: 15 минут

### Формулировка

> Реализуй семафор — примитив, который ограничивает количество одновременно выполняющихся горутин. Метод `Acquire()` блокируется если лимит достигнут, `Release()` освобождает слот.

### Что проверяют

- Паттерн "buffered channel как семафор" — идиома Go
- Блокирующие vs неблокирующие операции
- Интеграция с context

```go
// ✅ Семафор через буферизованный канал
type Semaphore struct {
    ch chan struct{}
}

func NewSemaphore(n int) *Semaphore {
    return &Semaphore{ch: make(chan struct{}, n)}
}

// Acquire блокируется пока не освободится слот
func (s *Semaphore) Acquire(ctx context.Context) error {
    select {
    case s.ch <- struct{}{}:
        return nil
    case <-ctx.Done():
        return ctx.Err()
    }
}

// Release освобождает слот
func (s *Semaphore) Release() {
    <-s.ch
}

// TryAcquire: неблокирующий вариант
func (s *Semaphore) TryAcquire() bool {
    select {
    case s.ch <- struct{}{}:
        return true
    default:
        return false
    }
}

// Использование: ограничение параллельных запросов к БД
func fetchUsers(ctx context.Context, ids []int64) ([]User, error) {
    sem := NewSemaphore(10) // не более 10 параллельных запросов
    var mu sync.Mutex
    var users []User
    g, ctx := errgroup.WithContext(ctx)

    for _, id := range ids {
        id := id
        g.Go(func() error {
            if err := sem.Acquire(ctx); err != nil {
                return err
            }
            defer sem.Release()

            user, err := db.GetUser(ctx, id)
            if err != nil {
                return err
            }
            mu.Lock()
            users = append(users, user)
            mu.Unlock()
            return nil
        })
    }

    return users, g.Wait()
}
```

> 💡 `golang.org/x/sync/semaphore` — стандартная реализация для production. Но на интервью покажи собственную реализацию.

---

## Задача 5: Что выведет код — map gotchas

**Компания**: Яндекс, ВКонтакте (проверка знания)
**Уровень**: Middle

### Gotcha 1: Concurrent map write — panic

```go
func main() {
    m := make(map[string]int)
    var wg sync.WaitGroup

    for i := range 10 {
        wg.Add(1)
        go func(i int) {
            defer wg.Done()
            m[fmt.Sprintf("key%d", i)] = i // ?
        }(i)
    }
    wg.Wait()
}
```

<details>
<summary>Ответ</summary>

**Паника** (в Go 1.6+): `concurrent map read and map write`. Go runtime обнаруживает конкурентный доступ к map и **паникует** (в отличие от C# где это просто undefined behavior).

Это не race condition в классическом смысле — это специальная проверка в runtime.

**Исправление**:
```go
var mu sync.Mutex
m := make(map[string]int)
// ...
mu.Lock()
m[key] = value
mu.Unlock()
```

</details>

---

### Gotcha 2: Итерация по map — порядок

```go
m := map[string]int{"a": 1, "b": 2, "c": 3}

for k, v := range m {
    fmt.Printf("%s: %d\n", k, v)
}
```

<details>
<summary>Ответ</summary>

Порядок итерации **случаен** и **намеренно рандомизирован** в Go (с версии 1.0). Каждый запуск может выдать разный порядок.

**C# отличие**: `Dictionary<K,V>` тоже не гарантирует порядок, но `SortedDictionary` — гарантирует.

Для детерминированного вывода в Go:
```go
import "slices"

keys := make([]string, 0, len(m))
for k := range m {
    keys = append(keys, k)
}
slices.Sort(keys)
for _, k := range keys {
    fmt.Printf("%s: %d\n", k, m[k])
}
```

</details>

---

### Gotcha 3: Zero value при чтении

```go
m := make(map[string]int)
fmt.Println(m["nonexistent"]) // ?

m["counter"]++  // работает?
fmt.Println(m["counter"]) // ?
```

<details>
<summary>Ответ</summary>

```
0            // zero value для int — не паника!
1            // m["counter"] = 0 + 1 = 1
```

В Go чтение из map по несуществующему ключу возвращает zero value типа. Это позволяет писать идиому `m[key]++` без предварительной инициализации.

**Опасная ловушка** с указателями:
```go
m := make(map[string]*int)
p := m["nonexistent"]
*p = 42 // PANIC: nil pointer dereference!

// Правильно:
if p, ok := m["key"]; ok {
    *p = 42
}
```

</details>

---

### Gotcha 4: Изменение map во время итерации

```go
m := map[string]int{"a": 1, "b": 2, "c": 3, "d": 4}

for k, v := range m {
    if v%2 == 0 {
        delete(m, k) // безопасно?
    }
}
fmt.Println(m) // ?
```

<details>
<summary>Ответ</summary>

**Безопасно**: Go гарантирует, что удаление во время итерации `range` не вызывает panic. Но:
- Удалённые ключи не появятся снова в текущей итерации
- Добавленные ключи могут появиться или не появиться — гарантий нет

```
map[a:1 c:3]  // или другое подмножество нечётных
```

</details>

---

## Задача 6: CopyOnWrite Map

**Компания**: Яндекс (конфигурация, feature flags)
**Уровень**: Senior
**Время**: 25 минут

### Формулировка

> Реализуй thread-safe map с семантикой "copy-on-write": чтения не блокируются совсем, запись создаёт новую копию map и атомарно подменяет указатель.

### Что проверяют

- Паттерн immutable data + atomic pointer swap
- `atomic.Pointer[T]` (Go 1.19+)
- Понимание trade-offs: читаем быстро, пишем медленно

```go
// ✅ Copy-on-Write Map через atomic.Pointer
type COWMap struct {
    mu      sync.Mutex // только для координации записей
    current atomic.Pointer[map[string]int]
}

func NewCOWMap() *COWMap {
    m := &COWMap{}
    initial := make(map[string]int)
    m.current.Store(&initial)
    return m
}

// Get не требует блокировки — атомарная загрузка указателя
func (m *COWMap) Get(key string) (int, bool) {
    mp := m.current.Load()
    v, ok := (*mp)[key]
    return v, ok
}

// Set: copy → modify → swap
func (m *COWMap) Set(key string, value int) {
    m.mu.Lock()
    defer m.mu.Unlock()

    // Копируем текущий map
    old := *m.current.Load()
    newMap := make(map[string]int, len(old)+1)
    for k, v := range old {
        newMap[k] = v
    }

    // Модифицируем копию
    newMap[key] = value

    // Атомарно подменяем указатель
    m.current.Store(&newMap)
}

// Delete: аналогично
func (m *COWMap) Delete(key string) {
    m.mu.Lock()
    defer m.mu.Unlock()

    old := *m.current.Load()
    newMap := make(map[string]int, len(old))
    for k, v := range old {
        if k != key {
            newMap[k] = v
        }
    }
    m.current.Store(&newMap)
}
```

### Когда это полезно

```go
// Реальный пример: конфигурация feature flags
// - Читается на каждый HTTP запрос (очень часто)
// - Обновляется редко (раз в минуту)
type FeatureFlags struct {
    flags COWMap
}

func (f *FeatureFlags) IsEnabled(feature string) bool {
    v, _ := f.flags.Get(feature)
    return v == 1
}

func (f *FeatureFlags) Reload(newFlags map[string]int) {
    for k, v := range newFlags {
        f.flags.Set(k, v) // можно оптимизировать одной atomic swap
    }
}
```

### Trade-offs

| Подход | Чтение | Запись | Память |
|--------|--------|--------|--------|
| `RWMutex + map` | RLock (быстро) | Lock (блокирует читателей) | O(n) |
| `sync.Map` | Без блокировки | Атомарно | Больше накладных |
| `COW Map` | **Без блокировки** | Копирование O(n) | 2x при записи |

---

## Итоги

| Задача | Что показывает | Уровень |
|--------|---------------|---------|
| Concurrent Cache | Знание RWMutex, критической секции | Middle |
| Word Count | Map-reduce, локальные аккумуляторы | Middle |
| Once | Double-check locking, atomic | Senior |
| Семафор | Buffered channel = counting semaphore | Middle |
| Map Gotchas | Глубина знания runtime | Middle+ |
| COW Map | Immutable data + atomic pointer | Senior |

---
