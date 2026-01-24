# 2.4 Примитивы синхронизации

## Содержание
- [Введение](#введение)
- [Mutex: взаимное исключение](#mutex-взаимное-исключение)
  - [sync.Mutex vs C# lock](#syncmutex-vs-c-lock)
  - [sync.RWMutex vs ReaderWriterLockSlim](#syncrwmutex-vs-readerwriterlockslim)
  - [Deadlock и как его избежать](#deadlock-и-как-его-избежать)
- [WaitGroup: ожидание завершения горутин](#waitgroup-ожидание-завершения-горутин)
- [Once: однократное выполнение](#once-однократное-выполнение)
- [Cond: условные переменные](#cond-условные-переменные)
- [Atomic операции](#atomic-операции)
- [sync.Map: потокобезопасная карта](#syncmap-потокобезопасная-карта)
- [Выбор правильного примитива](#выбор-правильного-примитива)
- [Практические примеры](#практические-примеры)
- [Чек-лист](#чек-лист)

---

## Введение

Go предоставляет богатый набор примитивов синхронизации в пакете `sync` для координации работы горутин. В этом разделе мы рассмотрим каждый примитив в сравнении с аналогами из C#.

> 💡 **Для C# разработчиков**: В Go философия синхронизации отличается от C#. Вместо "share memory by communicating" (как в .NET с lock и Interlocked), в Go предпочитают "communicate to share memory" через каналы. Но для низкоуровневой синхронизации примитивы `sync` незаменимы.

**Когда использовать каналы, а когда sync примитивы?**

| Сценарий | Решение | Почему |
|----------|---------|--------|
| Передача данных между горутинами | **Каналы** | Естественный способ коммуникации |
| Защита разделяемого состояния | **Mutex** | Простота и производительность |
| Ожидание N горутин | **WaitGroup** или **errgroup** | Явное выражение намерения |
| Инициализация singleton | **Once** | Гарантия однократности |
| Атомарные счетчики | **atomic** | Максимальная производительность |
| Редкая запись, частое чтение | **RWMutex** или **atomic.Value** | Оптимизация для читателей |

---

## Mutex: взаимное исключение

### sync.Mutex vs C# lock

`sync.Mutex` — это базовый примитив взаимного исключения, аналог `lock` в C#.

**C# (lock statement)**:
```csharp
public class Counter
{
    private int _count;
    private readonly object _lock = new object();

    public void Increment()
    {
        lock (_lock)
        {
            _count++;
        }
    }

    public int GetCount()
    {
        lock (_lock)
        {
            return _count;
        }
    }
}
```

**Go (sync.Mutex)**:
```go
type Counter struct {
    mu    sync.Mutex
    count int
}

func (c *Counter) Increment() {
    c.mu.Lock()
    c.count++
    c.mu.Unlock()
}

func (c *Counter) GetCount() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.count
}
```

> ⚠️ **Важно**: В Go **нет автоматической разблокировки** при выходе из области видимости (как `lock` в C#). Всегда используйте `defer` для гарантии разблокировки!

**Идиоматичный паттерн**:
```go
func (c *Counter) Increment() {
    c.mu.Lock()
    defer c.mu.Unlock()

    c.count++
    // Даже если здесь будет panic, Unlock() выполнится
}
```

#### Сравнительная таблица: Mutex vs lock

| Аспект | C# `lock` | Go `sync.Mutex` |
|--------|-----------|-----------------|
| **Автоматическая разблокировка** | ✅ Да (при выходе из блока) | ❌ Нет (используй `defer`) |
| **Рекурсивность** | ❌ Нет (но есть `Monitor.Enter` с флагом) | ❌ Нет (deadlock!) |
| **Стоимость** | ~20-50 нс (uncontended) | ~10-20 нс (uncontended) |
| **Вложенные блокировки** | Deadlock | Deadlock |
| **Try-Lock** | `Monitor.TryEnter` | ❌ Нет (но можно через канал) |

#### Распространённые ошибки

**❌ Забыть defer**:
```go
func (c *Counter) Increment() {
    c.mu.Lock()
    c.count++
    c.mu.Unlock() // Если panic на строке выше — deadlock!
}
```

**✅ Правильно**:
```go
func (c *Counter) Increment() {
    c.mu.Lock()
    defer c.mu.Unlock()

    c.count++
}
```

**❌ Копирование структуры с Mutex**:
```go
func main() {
    c1 := Counter{}
    c2 := c1 // ❌ Копируется Mutex — undefined behavior!
}
```

**✅ Правильно**:
```go
func main() {
    c1 := &Counter{} // Используй указатели
    c2 := c1
}
```

> 💡 **Идиома Go**: `go vet` предупредит о копировании Mutex. Всегда используйте указатели на структуры с примитивами синхронизации.

---

### sync.RWMutex vs ReaderWriterLockSlim

`sync.RWMutex` — мьютекс для чтения-записи, позволяющий множественным читателям одновременный доступ.

**C# (ReaderWriterLockSlim)**:
```csharp
public class Cache
{
    private readonly Dictionary<string, string> _data = new();
    private readonly ReaderWriterLockSlim _lock = new();

    public string Get(string key)
    {
        _lock.EnterReadLock();
        try
        {
            return _data.TryGetValue(key, out var value) ? value : null;
        }
        finally
        {
            _lock.ExitReadLock();
        }
    }

    public void Set(string key, string value)
    {
        _lock.EnterWriteLock();
        try
        {
            _data[key] = value;
        }
        finally
        {
            _lock.ExitWriteLock();
        }
    }
}
```

**Go (sync.RWMutex)**:
```go
type Cache struct {
    mu   sync.RWMutex
    data map[string]string
}

func NewCache() *Cache {
    return &Cache{
        data: make(map[string]string),
    }
}

func (c *Cache) Get(key string) (string, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()

    val, ok := c.data[key]
    return val, ok
}

func (c *Cache) Set(key, value string) {
    c.mu.Lock()
    defer c.mu.Unlock()

    c.data[key] = value
}
```

#### Когда использовать RWMutex?

**✅ Используйте RWMutex**:
- Чтение происходит **значительно чаще** записи (90%+ чтений)
- Критическая секция для чтения **не мгновенна** (> 100 нс)

**❌ Не используйте RWMutex**:
- Запись такая же частая, как чтение
- Критическая секция очень короткая (< 50 нс) — overhead RWMutex больше выигрыша

**Benchmark**:
```go
// BenchmarkMutex-8         50000000    25.3 ns/op
// BenchmarkRWMutex-8       20000000    68.1 ns/op  (для записи)
// BenchmarkRWMutexRead-8  100000000    12.5 ns/op  (для чтения без конкуренции)
```

> 💡 **Идиома Go**: Если не уверены — начните с `sync.Mutex`. Переход на `RWMutex` — это оптимизация, которую нужно проверять бенчмарками.

---

### Deadlock и как его избежать

**Типичные причины deadlock**:

#### 1. Рекурсивный lock
```go
func (c *Counter) IncrementTwice() {
    c.mu.Lock()
    defer c.mu.Unlock()

    c.Increment() // ❌ Deadlock! Increment() тоже вызывает Lock()
}
```

**Решение**: выделить метод без блокировки:
```go
func (c *Counter) Increment() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.incrementUnsafe()
}

func (c *Counter) IncrementTwice() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.incrementUnsafe()
    c.incrementUnsafe()
}

// incrementUnsafe предполагает, что блокировка уже захвачена
func (c *Counter) incrementUnsafe() {
    c.count++
}
```

#### 2. Circular wait (циклическое ожидание)
```go
func Transfer(from, to *Account, amount int) {
    from.mu.Lock()
    defer from.mu.Unlock()

    to.mu.Lock() // ❌ Если другая горутина делает Transfer(to, from, ...) — deadlock!
    defer to.mu.Unlock()

    from.balance -= amount
    to.balance += amount
}
```

**Решение**: упорядочить захват блокировок:
```go
func Transfer(from, to *Account, amount int) {
    // Всегда захватываем блокировки в порядке возрастания ID
    if from.id < to.id {
        from.mu.Lock()
        defer from.mu.Unlock()
        to.mu.Lock()
        defer to.mu.Unlock()
    } else {
        to.mu.Lock()
        defer to.mu.Unlock()
        from.mu.Lock()
        defer from.mu.Unlock()
    }

    from.balance -= amount
    to.balance += amount
}
```

> 💡 **Идиома Go**: Используйте детектор deadlock из `-race` флага: `go run -race main.go`

---

## WaitGroup: ожидание завершения горутин

`sync.WaitGroup` ожидает завершения группы горутин. Аналог `CountdownEvent` или `Task.WhenAll` в C#.

**C# (Task.WhenAll)**:
```csharp
public async Task ProcessItemsAsync(List<string> items)
{
    var tasks = items.Select(item => Task.Run(() => ProcessItem(item)));
    await Task.WhenAll(tasks);
    Console.WriteLine("All items processed");
}
```

**Go (sync.WaitGroup)**:
```go
func ProcessItems(items []string) {
    var wg sync.WaitGroup

    for _, item := range items {
        wg.Add(1) // Увеличиваем счётчик

        go func(item string) {
            defer wg.Done() // Уменьшаем счётчик при завершении
            ProcessItem(item)
        }(item)
    }

    wg.Wait() // Блокируемся до тех пор, пока счётчик не станет 0
    fmt.Println("All items processed")
}
```

> ⚠️ **Важно**: Передавайте переменную цикла как параметр в горутину! Иначе все горутины получат одно и то же значение (последнее).

**❌ Распространённая ошибка**:
```go
for _, item := range items {
    wg.Add(1)
    go func() {
        defer wg.Done()
        ProcessItem(item) // ❌ Замыкание захватывает переменную цикла!
    }()
}
// Все горутины обработают последний item!
```

**✅ Правильно**:
```go
for _, item := range items {
    wg.Add(1)
    go func(item string) { // Передаём item как параметр
        defer wg.Done()
        ProcessItem(item)
    }(item)
}
```

### WaitGroup vs errgroup

Для обработки ошибок используйте `golang.org/x/sync/errgroup` вместо `WaitGroup`:

**Базовый WaitGroup (ошибки игнорируются)**:
```go
func DownloadFiles(urls []string) {
    var wg sync.WaitGroup

    for _, url := range urls {
        wg.Add(1)
        go func(url string) {
            defer wg.Done()
            if err := Download(url); err != nil {
                // ❌ Как сообщить об ошибке?
                log.Println(err)
            }
        }(url)
    }

    wg.Wait()
}
```

**errgroup (с обработкой ошибок)**:
```go
import "golang.org/x/sync/errgroup"

func DownloadFiles(ctx context.Context, urls []string) error {
    g, ctx := errgroup.WithContext(ctx)

    for _, url := range urls {
        url := url // Для Go < 1.22
        g.Go(func() error {
            return Download(ctx, url) // Возвращаем ошибку
        })
    }

    // Wait() вернёт первую ошибку (если была)
    if err := g.Wait(); err != nil {
        return fmt.Errorf("failed to download files: %w", err)
    }

    return nil
}
```

> 💡 **Идиома Go**: Используйте `errgroup` вместо `WaitGroup`, если нужна обработка ошибок или cancellation.

---

## Once: однократное выполнение

`sync.Once` гарантирует, что функция выполнится ровно **один раз**, даже при вызове из множества горутин. Аналог `Lazy<T>` в C#.

**C# (Lazy<T>)**:
```csharp
public class Config
{
    private static readonly Lazy<Config> _instance =
        new Lazy<Config>(() => LoadConfig());

    public static Config Instance => _instance.Value;

    private static Config LoadConfig()
    {
        // Дорогая операция загрузки
        Thread.Sleep(1000);
        return new Config();
    }
}
```

**Go (sync.Once)**:
```go
type Config struct {
    // поля конфигурации
}

var (
    instance *Config
    once     sync.Once
)

func GetConfig() *Config {
    once.Do(func() {
        // Выполнится только один раз
        instance = loadConfig()
    })
    return instance
}

func loadConfig() *Config {
    // Дорогая операция загрузки
    time.Sleep(1 * time.Second)
    return &Config{}
}
```

### Практическое применение

#### 1. Инициализация singleton
```go
type Database struct {
    conn *sql.DB
}

var (
    db   *Database
    once sync.Once
)

func GetDB() *Database {
    once.Do(func() {
        conn, err := sql.Open("postgres", "connection_string")
        if err != nil {
            panic(err) // В production лучше вернуть ошибку
        }
        db = &Database{conn: conn}
    })
    return db
}
```

#### 2. Ленивая инициализация с ошибками
```go
type Service struct {
    client *http.Client
    once   sync.Once
    initErr error
}

func (s *Service) init() {
    s.once.Do(func() {
        // Дорогая инициализация
        s.client, s.initErr = createHTTPClient()
    })
}

func (s *Service) MakeRequest(url string) error {
    s.init()
    if s.initErr != nil {
        return s.initErr
    }

    // Используем s.client
    return nil
}
```

> 💡 **Идиома Go**: `sync.Once` удобен для ленивой инициализации, но для singleton паттерна часто достаточно `init()` функции.

---

## Cond: условные переменные

`sync.Cond` — это условная переменная, позволяющая горутинам ждать или сигнализировать об изменении состояния. Аналог `Monitor.Wait/Pulse` в C#.

> ⚠️ **Внимание**: `sync.Cond` — это низкоуровневый примитив. В большинстве случаев лучше использовать **каналы**.

**C# (Monitor.Wait/Pulse)**:
```csharp
public class Queue<T>
{
    private readonly object _lock = new object();
    private readonly System.Collections.Generic.Queue<T> _queue = new();

    public void Enqueue(T item)
    {
        lock (_lock)
        {
            _queue.Enqueue(item);
            Monitor.Pulse(_lock); // Разбудить одного ожидающего
        }
    }

    public T Dequeue()
    {
        lock (_lock)
        {
            while (_queue.Count == 0)
            {
                Monitor.Wait(_lock); // Ждём, пока не появятся данные
            }
            return _queue.Dequeue();
        }
    }
}
```

**Go (sync.Cond) — не идиоматично**:
```go
type Queue struct {
    mu    sync.Mutex
    cond  *sync.Cond
    items []interface{}
}

func NewQueue() *Queue {
    q := &Queue{}
    q.cond = sync.NewCond(&q.mu)
    return q
}

func (q *Queue) Enqueue(item interface{}) {
    q.mu.Lock()
    defer q.mu.Unlock()

    q.items = append(q.items, item)
    q.cond.Signal() // Разбудить одну горутину
}

func (q *Queue) Dequeue() interface{} {
    q.mu.Lock()
    defer q.mu.Unlock()

    for len(q.items) == 0 {
        q.cond.Wait() // Ждём, пока не появятся данные
    }

    item := q.items[0]
    q.items = q.items[1:]
    return item
}
```

**Go (каналы) — идиоматично** ✅:
```go
type Queue struct {
    ch chan interface{}
}

func NewQueue(size int) *Queue {
    return &Queue{
        ch: make(chan interface{}, size),
    }
}

func (q *Queue) Enqueue(item interface{}) {
    q.ch <- item // Блокируется, если буфер полон
}

func (q *Queue) Dequeue() interface{} {
    return <-q.ch // Блокируется, если канал пуст
}
```

> 💡 **Идиома Go**: В 99% случаев используйте **каналы** вместо `sync.Cond`. Каналы проще, безопаснее и более идиоматичны.

**Когда использовать Cond**:
- Нужно разбудить **все** ожидающие горутины (`Broadcast()`)
- Сложная логика ожидания с несколькими условиями
- Миграция legacy кода с Monitor.Wait/Pulse

---

## Atomic операции

Пакет `sync/atomic` предоставляет атомарные операции для базовых типов. Аналог `Interlocked` в C#.

**C# (Interlocked)**:
```csharp
public class Metrics
{
    private long _requestCount;
    private long _errorCount;

    public void IncrementRequests()
    {
        Interlocked.Increment(ref _requestCount);
    }

    public void IncrementErrors()
    {
        Interlocked.Increment(ref _errorCount);
    }

    public (long requests, long errors) GetCounts()
    {
        return (
            Interlocked.Read(ref _requestCount),
            Interlocked.Read(ref _errorCount)
        );
    }
}
```

**Go (sync/atomic) — старый API**:
```go
type Metrics struct {
    requestCount int64
    errorCount   int64
}

func (m *Metrics) IncrementRequests() {
    atomic.AddInt64(&m.requestCount, 1)
}

func (m *Metrics) IncrementErrors() {
    atomic.AddInt64(&m.errorCount, 1)
}

func (m *Metrics) GetCounts() (requests, errors int64) {
    return atomic.LoadInt64(&m.requestCount),
           atomic.LoadInt64(&m.errorCount)
}
```

**Go 1.19+ (atomic.Int64) — новый type-safe API** ✅:
```go
type Metrics struct {
    requestCount atomic.Int64
    errorCount   atomic.Int64
}

func (m *Metrics) IncrementRequests() {
    m.requestCount.Add(1)
}

func (m *Metrics) IncrementErrors() {
    m.errorCount.Add(1)
}

func (m *Metrics) GetCounts() (requests, errors int64) {
    return m.requestCount.Load(), m.errorCount.Load()
}
```

> 💡 **Идиома Go**: В Go 1.19+ используйте типизированные `atomic.Int64`, `atomic.Uint64` и т.д. вместо старого API с указателями.

### Поддерживаемые типы

| Go 1.19+ | Старый API | Описание |
|----------|-----------|----------|
| `atomic.Int32` | `atomic.AddInt32(&v, delta)` | 32-bit signed integer |
| `atomic.Int64` | `atomic.AddInt64(&v, delta)` | 64-bit signed integer |
| `atomic.Uint32` | `atomic.AddUint32(&v, delta)` | 32-bit unsigned integer |
| `atomic.Uint64` | `atomic.AddUint64(&v, delta)` | 64-bit unsigned integer |
| `atomic.Uintptr` | `atomic.AddUintptr(&v, delta)` | Pointer-sized unsigned integer |
| `atomic.Pointer[T]` | `atomic.LoadPointer/StorePointer` | Type-safe указатель |
| `atomic.Value` | `atomic.Value{}` | Любой тип (через interface{}) |

### atomic.Value: хранение произвольных типов

`atomic.Value` позволяет атомарно читать/записывать значения **любого типа**.

**Пример: атомарная замена конфигурации**:
```go
type Config struct {
    Timeout time.Duration
    MaxConn int
}

var config atomic.Value

func init() {
    config.Store(&Config{
        Timeout: 30 * time.Second,
        MaxConn: 100,
    })
}

// Чтение конфигурации (из любой горутины)
func GetConfig() *Config {
    return config.Load().(*Config)
}

// Обновление конфигурации (атомарно)
func UpdateConfig(newConfig *Config) {
    config.Store(newConfig)
}

// Использование
func MakeRequest() {
    cfg := GetConfig()
    client := &http.Client{
        Timeout: cfg.Timeout,
    }
    // ...
}
```

> ⚠️ **Важно**: Тип значения в `atomic.Value` должен быть **одинаковым** для всех `Store()`. Иначе — panic!

**❌ Ошибка**:
```go
var v atomic.Value
v.Store("string")
v.Store(123) // panic: sync/atomic: store of inconsistently typed value into Value
```

### Mutex vs Atomic: что выбрать?

| Сценарий | Решение | Почему |
|----------|---------|--------|
| Простой счётчик | `atomic.Int64` | В ~10x быстрее Mutex |
| Несколько связанных полей | `Mutex` | Атомарность группы операций |
| Чтение конфигурации | `atomic.Value` | Нет аллокаций, lock-free чтение |
| Сложная логика | `Mutex` | Простота и читаемость |

**Benchmark**:
```go
// BenchmarkMutex-8         50000000    25.3 ns/op
// BenchmarkAtomic-8       500000000     3.2 ns/op
```

> 💡 **Идиома Go**: Используйте `atomic` для простых операций (счётчики, флаги). Для всего остального — `Mutex`.

---

## sync.Map: потокобезопасная карта

`sync.Map` — это потокобезопасная карта, оптимизированная для сценариев с редкими записями и частыми чтениями. Аналог `ConcurrentDictionary<K,V>` в C#.

**C# (ConcurrentDictionary)**:
```csharp
var cache = new ConcurrentDictionary<string, string>();

// Запись
cache.TryAdd("key1", "value1");
cache["key2"] = "value2"; // Или перезапись

// Чтение
if (cache.TryGetValue("key1", out var value))
{
    Console.WriteLine(value);
}

// Удаление
cache.TryRemove("key1", out _);
```

**Go (sync.Map)**:
```go
var cache sync.Map

// Запись
cache.Store("key1", "value1")
cache.Store("key2", "value2")

// Чтение
if val, ok := cache.Load("key1"); ok {
    fmt.Println(val.(string)) // Требуется type assertion
}

// Удаление
cache.Delete("key1")

// Load или Store (аналог GetOrAdd)
actual, loaded := cache.LoadOrStore("key3", "value3")
if loaded {
    fmt.Println("Уже существует:", actual)
} else {
    fmt.Println("Создали новое значение")
}
```

### Когда использовать sync.Map?

**✅ Используйте sync.Map**:
- **(1) Ключи записываются один раз и потом только читаются** (write-once, read-many)
- **(2) Множество горутин читает/записывает разные ключи** (low contention)

**❌ Не используйте sync.Map**:
- Частые обновления одних и тех же ключей
- Нужна типобезопасность (sync.Map использует `interface{}`)
- Нужны методы вроде `Len()` или итерация

**Альтернативы**:
```go
// Вариант 1: map + RWMutex (типобезопасно, более гибко)
type SafeMap struct {
    mu   sync.RWMutex
    data map[string]string
}

func (m *SafeMap) Get(key string) (string, bool) {
    m.mu.RLock()
    defer m.mu.RUnlock()
    val, ok := m.data[key]
    return val, ok
}

func (m *SafeMap) Set(key, value string) {
    m.mu.Lock()
    defer m.mu.Unlock()
    m.data[key] = value
}

// Вариант 2: Sharded map (для высокой конкуренции)
type ShardedMap struct {
    shards [16]*shard // 16 шардов
}

type shard struct {
    mu   sync.RWMutex
    data map[string]string
}

func (m *ShardedMap) getShard(key string) *shard {
    hash := fnv.New32()
    hash.Write([]byte(key))
    return m.shards[hash.Sum32()%16]
}
```

> 💡 **Идиома Go**: В большинстве случаев `map + RWMutex` проще и эффективнее `sync.Map`. Используйте `sync.Map` только для write-once сценариев.

---

## Выбор правильного примитива

**Блок-схема выбора**:

```
Нужна синхронизация?
│
├─ Передача данных → Каналы
│
├─ Простой счётчик → atomic.Int64
│
├─ Ожидание N горутин → WaitGroup (или errgroup)
│
├─ Singleton инициализация → sync.Once
│
├─ Защита разделяемого состояния
│  │
│  ├─ Одно поле (int/bool) → atomic
│  │
│  ├─ Несколько связанных полей → Mutex
│  │
│  ├─ Редкая запись, частое чтение → RWMutex или atomic.Value
│  │
│  └─ Конкурентная карта
│     │
│     ├─ Write-once, read-many → sync.Map
│     │
│     ├─ Высокая конкуренция → Sharded map
│     │
│     └─ Остальное → map + RWMutex
│
└─ Сложное ожидание условия → Каналы (или редко sync.Cond)
```

---

## Практические примеры

### Пример 1: Rate Limiter (ограничение частоты запросов)

**Задача**: Ограничить количество одновременных HTTP запросов до 10.

**C# решение**:
```csharp
public class RateLimiter
{
    private readonly SemaphoreSlim _semaphore = new SemaphoreSlim(10);

    public async Task<T> ExecuteAsync<T>(Func<Task<T>> action)
    {
        await _semaphore.WaitAsync();
        try
        {
            return await action();
        }
        finally
        {
            _semaphore.Release();
        }
    }
}

// Использование
var limiter = new RateLimiter();
var tasks = urls.Select(url =>
    limiter.ExecuteAsync(() => httpClient.GetStringAsync(url))
);
await Task.WhenAll(tasks);
```

**Go решение (буферизированный канал как семафор)**:
```go
func RateLimitedFetch(urls []string, maxConcurrent int) []string {
    // Буферизированный канал как семафор
    semaphore := make(chan struct{}, maxConcurrent)

    results := make([]string, len(urls))
    var wg sync.WaitGroup

    for i, url := range urls {
        wg.Add(1)
        go func(i int, url string) {
            defer wg.Done()

            // Захватываем слот
            semaphore <- struct{}{}
            defer func() { <-semaphore }() // Освобождаем

            // Выполняем запрос
            resp, err := http.Get(url)
            if err != nil {
                results[i] = fmt.Sprintf("Error: %v", err)
                return
            }
            defer resp.Body.Close()

            body, _ := io.ReadAll(resp.Body)
            results[i] = string(body)
        }(i, url)
    }

    wg.Wait()
    return results
}
```

**Go решение (с errgroup и context)**:
```go
import "golang.org/x/sync/semaphore"

func RateLimitedFetch(ctx context.Context, urls []string, maxConcurrent int) ([]string, error) {
    sem := semaphore.NewWeighted(int64(maxConcurrent))
    g, ctx := errgroup.WithContext(ctx)

    results := make([]string, len(urls))

    for i, url := range urls {
        i, url := i, url // Для Go < 1.22

        g.Go(func() error {
            // Захватываем семафор с учётом cancellation
            if err := sem.Acquire(ctx, 1); err != nil {
                return err
            }
            defer sem.Release(1)

            req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
            resp, err := http.DefaultClient.Do(req)
            if err != nil {
                return err
            }
            defer resp.Body.Close()

            body, err := io.ReadAll(resp.Body)
            if err != nil {
                return err
            }

            results[i] = string(body)
            return nil
        })
    }

    if err := g.Wait(); err != nil {
        return nil, err
    }

    return results, nil
}
```

---

### Пример 2: Метрики с low contention

**Задача**: Собирать метрики HTTP сервера (RPS, latency) с минимальными потерями производительности.

**Наивное решение (высокая конкуренция)**:
```go
type Metrics struct {
    mu            sync.Mutex
    requestCount  int64
    totalDuration time.Duration
}

func (m *Metrics) Record(duration time.Duration) {
    m.mu.Lock()
    m.requestCount++
    m.totalDuration += duration
    m.mu.Unlock()
}

// Проблема: каждый запрос конкурирует за один мьютекс
```

**Оптимизированное решение (atomic + sharding)**:
```go
type Metrics struct {
    requestCount atomic.Int64

    // Sharded счётчики для latency (чтобы избежать конкуренции)
    shards [16]shard
}

type shard struct {
    _            [64]byte // Padding для избежания false sharing
    totalNanos   atomic.Int64
}

func (m *Metrics) Record(duration time.Duration) {
    m.requestCount.Add(1)

    // Распределяем latency по шардам (на основе goroutine ID)
    shardIdx := runtime_fastrand() % 16
    m.shards[shardIdx].totalNanos.Add(duration.Nanoseconds())
}

func (m *Metrics) GetStats() (count int64, avgLatency time.Duration) {
    count = m.requestCount.Load()

    var totalNanos int64
    for i := range m.shards {
        totalNanos += m.shards[i].totalNanos.Load()
    }

    if count > 0 {
        avgLatency = time.Duration(totalNanos / count)
    }
    return
}

// runtime_fastrand — недокументированная функция для быстрого rand
//go:linkname runtime_fastrand runtime.fastrand
func runtime_fastrand() uint32
```

> 💡 **Производительность**: Sharding снижает конкуренцию, а padding (`[64]byte`) предотвращает false sharing на CPU cache line.

---

### Пример 3: Connection Pool

**Задача**: Реализовать пул соединений к базе данных.

**Go решение (каналы + sync.Once)**:
```go
type ConnPool struct {
    conns     chan *sql.DB
    factory   func() (*sql.DB, error)
    initOnce  sync.Once
    closeOnce sync.Once
}

func NewConnPool(size int, factory func() (*sql.DB, error)) *ConnPool {
    return &ConnPool{
        conns:   make(chan *sql.DB, size),
        factory: factory,
    }
}

func (p *ConnPool) init() error {
    var initErr error
    p.initOnce.Do(func() {
        // Создаём соединения лениво
        for i := 0; i < cap(p.conns); i++ {
            conn, err := p.factory()
            if err != nil {
                initErr = err
                return
            }
            p.conns <- conn
        }
    })
    return initErr
}

func (p *ConnPool) Get(ctx context.Context) (*sql.DB, error) {
    if err := p.init(); err != nil {
        return nil, err
    }

    select {
    case conn := <-p.conns:
        return conn, nil
    case <-ctx.Done():
        return nil, ctx.Err()
    }
}

func (p *ConnPool) Put(conn *sql.DB) {
    select {
    case p.conns <- conn:
    default:
        // Пул переполнен (не должно случиться)
        conn.Close()
    }
}

func (p *ConnPool) Close() error {
    var firstErr error
    p.closeOnce.Do(func() {
        close(p.conns)
        for conn := range p.conns {
            if err := conn.Close(); err != nil && firstErr == nil {
                firstErr = err
            }
        }
    })
    return firstErr
}

// Использование
func main() {
    pool := NewConnPool(10, func() (*sql.DB, error) {
        return sql.Open("postgres", "connection_string")
    })
    defer pool.Close()

    ctx := context.Background()
    conn, err := pool.Get(ctx)
    if err != nil {
        log.Fatal(err)
    }
    defer pool.Put(conn)

    // Используем соединение
    rows, err := conn.QueryContext(ctx, "SELECT * FROM users")
    // ...
}
```

---

## Чек-лист

После изучения этого раздела вы должны:

- [ ] Понимать разницу между `Mutex` и каналами (когда что использовать)
- [ ] Всегда использовать `defer` для разблокировки `Mutex`
- [ ] Знать, когда применять `RWMutex` вместо `Mutex`
- [ ] Уметь предотвращать deadlock (упорядочивание блокировок, `go run -race`)
- [ ] Использовать `WaitGroup` для ожидания горутин или `errgroup` для обработки ошибок
- [ ] Применять `sync.Once` для singleton инициализации
- [ ] Предпочитать **каналы** вместо `sync.Cond`
- [ ] Использовать `atomic.Int64` и другие типизированные типы (Go 1.19+)
- [ ] Понимать, когда `sync.Map` эффективнее `map + RWMutex`
- [ ] Выбирать правильный примитив синхронизации для задачи
- [ ] Знать про sharding и padding для оптимизации метрик

---

## Следующие шаги

Переходите к [2.5 Работа с памятью и производительность](05_memory_performance.md)

---

**Вопросы?** Открой issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Назад: 2.3 Сборка мусора (GC)](03_gc.md) | [Вперёд: 2.5 Работа с памятью и производительность →](05_memory_performance.md)
