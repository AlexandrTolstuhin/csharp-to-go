# 2.4 Примитивы синхронизации

## Содержание

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Введение](#%D0%B2%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5)
- [Mutex: взаимное исключение](#mutex-%D0%B2%D0%B7%D0%B0%D0%B8%D0%BC%D0%BD%D0%BE%D0%B5-%D0%B8%D1%81%D0%BA%D0%BB%D1%8E%D1%87%D0%B5%D0%BD%D0%B8%D0%B5)
  - [sync.Mutex vs C# lock](#syncmutex-vs-c-lock)
    - [Сравнительная таблица: Mutex vs lock](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F-%D1%82%D0%B0%D0%B1%D0%BB%D0%B8%D1%86%D0%B0-mutex-vs-lock)
    - [Распространённые ошибки](#%D1%80%D0%B0%D1%81%D0%BF%D1%80%D0%BE%D1%81%D1%82%D1%80%D0%B0%D0%BD%D1%91%D0%BD%D0%BD%D1%8B%D0%B5-%D0%BE%D1%88%D0%B8%D0%B1%D0%BA%D0%B8)
  - [sync.RWMutex vs ReaderWriterLockSlim](#syncrwmutex-vs-readerwriterlockslim)
    - [Когда использовать RWMutex?](#%D0%BA%D0%BE%D0%B3%D0%B4%D0%B0-%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D1%8C-rwmutex)
  - [Deadlock и как его избежать](#deadlock-%D0%B8-%D0%BA%D0%B0%D0%BA-%D0%B5%D0%B3%D0%BE-%D0%B8%D0%B7%D0%B1%D0%B5%D0%B6%D0%B0%D1%82%D1%8C)
    - [1. Рекурсивный lock](#1-%D1%80%D0%B5%D0%BA%D1%83%D1%80%D1%81%D0%B8%D0%B2%D0%BD%D1%8B%D0%B9-lock)
    - [2. Circular wait (циклическое ожидание)](#2-circular-wait-%D1%86%D0%B8%D0%BA%D0%BB%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%BE%D0%B5-%D0%BE%D0%B6%D0%B8%D0%B4%D0%B0%D0%BD%D0%B8%D0%B5)
- [WaitGroup: ожидание завершения горутин](#waitgroup-%D0%BE%D0%B6%D0%B8%D0%B4%D0%B0%D0%BD%D0%B8%D0%B5-%D0%B7%D0%B0%D0%B2%D0%B5%D1%80%D1%88%D0%B5%D0%BD%D0%B8%D1%8F-%D0%B3%D0%BE%D1%80%D1%83%D1%82%D0%B8%D0%BD)
  - [WaitGroup vs errgroup](#waitgroup-vs-errgroup)
  - [WaitGroup.Go() — новый API (Go 1.25)](#waitgroupgo--%D0%BD%D0%BE%D0%B2%D1%8B%D0%B9-api-go-125)
- [Once: однократное выполнение](#once-%D0%BE%D0%B4%D0%BD%D0%BE%D0%BA%D1%80%D0%B0%D1%82%D0%BD%D0%BE%D0%B5-%D0%B2%D1%8B%D0%BF%D0%BE%D0%BB%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5)
  - [Практическое применение](#%D0%BF%D1%80%D0%B0%D0%BA%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%BE%D0%B5-%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5)
    - [1. Инициализация singleton](#1-%D0%B8%D0%BD%D0%B8%D1%86%D0%B8%D0%B0%D0%BB%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-singleton)
    - [2. Ленивая инициализация с ошибками](#2-%D0%BB%D0%B5%D0%BD%D0%B8%D0%B2%D0%B0%D1%8F-%D0%B8%D0%BD%D0%B8%D1%86%D0%B8%D0%B0%D0%BB%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-%D1%81-%D0%BE%D1%88%D0%B8%D0%B1%D0%BA%D0%B0%D0%BC%D0%B8)
- [Cond: условные переменные](#cond-%D1%83%D1%81%D0%BB%D0%BE%D0%B2%D0%BD%D1%8B%D0%B5-%D0%BF%D0%B5%D1%80%D0%B5%D0%BC%D0%B5%D0%BD%D0%BD%D1%8B%D0%B5)
- [Atomic операции](#atomic-%D0%BE%D0%BF%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D0%B8)
  - [Поддерживаемые типы](#%D0%BF%D0%BE%D0%B4%D0%B4%D0%B5%D1%80%D0%B6%D0%B8%D0%B2%D0%B0%D0%B5%D0%BC%D1%8B%D0%B5-%D1%82%D0%B8%D0%BF%D1%8B)
  - [atomic.Value: хранение произвольных типов](#atomicvalue-%D1%85%D1%80%D0%B0%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%B2%D0%BE%D0%BB%D1%8C%D0%BD%D1%8B%D1%85-%D1%82%D0%B8%D0%BF%D0%BE%D0%B2)
  - [Mutex vs Atomic: что выбрать?](#mutex-vs-atomic-%D1%87%D1%82%D0%BE-%D0%B2%D1%8B%D0%B1%D1%80%D0%B0%D1%82%D1%8C)
- [sync.Map: потокобезопасная карта](#syncmap-%D0%BF%D0%BE%D1%82%D0%BE%D0%BA%D0%BE%D0%B1%D0%B5%D0%B7%D0%BE%D0%BF%D0%B0%D1%81%D0%BD%D0%B0%D1%8F-%D0%BA%D0%B0%D1%80%D1%82%D0%B0)
  - [Когда использовать sync.Map?](#%D0%BA%D0%BE%D0%B3%D0%B4%D0%B0-%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D1%8C-syncmap)
  - [sync.Map и Swiss Tables (Go 1.24)](#syncmap-%D0%B8-swiss-tables-go-124)
- [Выбор правильного примитива](#%D0%B2%D1%8B%D0%B1%D0%BE%D1%80-%D0%BF%D1%80%D0%B0%D0%B2%D0%B8%D0%BB%D1%8C%D0%BD%D0%BE%D0%B3%D0%BE-%D0%BF%D1%80%D0%B8%D0%BC%D0%B8%D1%82%D0%B8%D0%B2%D0%B0)
- [Практические примеры](#%D0%BF%D1%80%D0%B0%D0%BA%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B5-%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80%D1%8B)
  - [Пример 1: Rate Limiter (ограничение частоты запросов)](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-1-rate-limiter-%D0%BE%D0%B3%D1%80%D0%B0%D0%BD%D0%B8%D1%87%D0%B5%D0%BD%D0%B8%D0%B5-%D1%87%D0%B0%D1%81%D1%82%D0%BE%D1%82%D1%8B-%D0%B7%D0%B0%D0%BF%D1%80%D0%BE%D1%81%D0%BE%D0%B2)
  - [Пример 2: Метрики с low contention](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-2-%D0%BC%D0%B5%D1%82%D1%80%D0%B8%D0%BA%D0%B8-%D1%81-low-contention)
  - [Пример 3: Connection Pool](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-3-connection-pool)
- [golang.org/x/sync: расширенные примитивы](#golangorgxsync-%D1%80%D0%B0%D1%81%D1%88%D0%B8%D1%80%D0%B5%D0%BD%D0%BD%D1%8B%D0%B5-%D0%BF%D1%80%D0%B8%D0%BC%D0%B8%D1%82%D0%B8%D0%B2%D1%8B)
  - [errgroup: WaitGroup с обработкой ошибок](#errgroup-waitgroup-%D1%81-%D0%BE%D0%B1%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%BA%D0%BE%D0%B9-%D0%BE%D1%88%D0%B8%D0%B1%D0%BE%D0%BA)
  - [semaphore: взвешенный семафор](#semaphore-%D0%B2%D0%B7%D0%B2%D0%B5%D1%88%D0%B5%D0%BD%D0%BD%D1%8B%D0%B9-%D1%81%D0%B5%D0%BC%D0%B0%D1%84%D0%BE%D1%80)
  - [singleflight: дедупликация вызовов](#singleflight-%D0%B4%D0%B5%D0%B4%D1%83%D0%BF%D0%BB%D0%B8%D0%BA%D0%B0%D1%86%D0%B8%D1%8F-%D0%B2%D1%8B%D0%B7%D0%BE%D0%B2%D0%BE%D0%B2)
  - [Сравнительная таблица: golang.org/x/sync](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F-%D1%82%D0%B0%D0%B1%D0%BB%D0%B8%D1%86%D0%B0-golangorgxsync)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

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

### WaitGroup.Go() — новый API (Go 1.25)

> 💡 **Для C# разработчиков**: Аналог `Task.WhenAll(tasks)` — запустить горутину и автоматически зарегистрировать её в группе.

В Go 1.25 у `sync.WaitGroup` появился метод `Go(func())`, который объединяет `wg.Add(1)` + `go` + `wg.Done()` в одну операцию:

**До Go 1.25 (многословно, легко забыть `Done`):**
```go
var wg sync.WaitGroup

for _, url := range urls {
    wg.Add(1)
    go func(u string) {
        defer wg.Done() // Легко забыть!
        process(u)
    }(url)
}

wg.Wait()
```

**Go 1.25+ с `WaitGroup.Go()` (идиоматично):**
```go
var wg sync.WaitGroup

for _, url := range urls {
    wg.Go(func() {            // Add(1) + go + Done() — всё в одном
        process(url)
    })
}

wg.Wait()
```

**Сравнение с C#:**
```csharp
// C# — Task.WhenAll
var tasks = urls.Select(url => Task.Run(() => Process(url)));
await Task.WhenAll(tasks);
```

```go
// Go 1.25 — WaitGroup.Go
var wg sync.WaitGroup
for _, url := range urls {
    wg.Go(func() { process(url) })
}
wg.Wait()
```

> ⚠️ **Важно**: `WaitGroup.Go()` не поддерживает возврат ошибок. Для этого по-прежнему используйте `errgroup.Group.Go()`.

| Случай | Рекомендация |
|--------|-------------|
| Запустить горутины, ждать завершения | `wg.Go()` (Go 1.25+) |
| Горутины возвращают ошибки | `errgroup.Group.Go()` |
| Горутины + cancellation | `errgroup.WithContext()` |

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

### sync.Map и Swiss Tables (Go 1.24)

В Go 1.24 внутренняя реализация `sync.Map` переписана с использованием **Swiss Tables** — алгоритма хэш-таблицы от Google, который также применяется во встроенных `map` (Go 1.24). Это **прозрачное улучшение**: никаких изменений в API, только прирост производительности.

**Что изменилось внутри:**
- Лучшая cache-locality за счёт группировки ключей в «buckets» по 8 записей
- SIMD-оптимизации на современных CPU (Ice Lake, AMD Zen 4+)
- Меньше промахов кэша при lookup

**Для вас это значит:**
```go
// API не изменился — код работает быстрее «бесплатно»
var cache sync.Map

cache.Store("key", "value")
val, ok := cache.Load("key")
_ = val
_ = ok
```

> 💡 **Контекст**: Swiss Tables (Go 1.24) дают ~2-3% ускорения CPU на map-тяжёлых workload-ах. Встроенные `map` получили то же улучшение. Подробнее — в разделе [2.3 Сборка мусора](./03_gc.md).

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

## golang.org/x/sync: расширенные примитивы

Пакет `golang.org/x/sync` предоставляет дополнительные примитивы синхронизации, не вошедшие в стандартную библиотеку.

### errgroup: WaitGroup с обработкой ошибок

Мы уже видели `errgroup` в примерах выше. Это расширение `WaitGroup` с поддержкой ошибок и cancellation.

**Установка**:
```bash
go get golang.org/x/sync/errgroup
```

**Основные возможности**:

```go
import "golang.org/x/sync/errgroup"

// 1. Базовое использование
func ProcessFiles(files []string) error {
    g := new(errgroup.Group)

    for _, file := range files {
        file := file // Для Go < 1.22
        g.Go(func() error {
            return processFile(file)
        })
    }

    // Wait() вернёт первую ошибку (если была)
    return g.Wait()
}

// 2. С контекстом и cancellation
func DownloadWithTimeout(ctx context.Context, urls []string) error {
    g, ctx := errgroup.WithContext(ctx)

    for _, url := range urls {
        url := url
        g.Go(func() error {
            // Если одна горутина вернёт ошибку, ctx будет отменён
            return download(ctx, url)
        })
    }

    return g.Wait()
}

// 3. Ограничение конкурентности с SetLimit (Go 1.20+)
func ProcessWithLimit(items []string) error {
    g := new(errgroup.Group)
    g.SetLimit(10) // Максимум 10 горутин одновременно

    for _, item := range items {
        item := item
        g.Go(func() error {
            return processItem(item)
        })
    }

    return g.Wait()
}
```

**Сравнение с C#**:
```csharp
// C# (Task.WhenAll с обработкой ошибок)
public async Task ProcessFilesAsync(List<string> files)
{
    var tasks = files.Select(file => ProcessFileAsync(file));

    try
    {
        await Task.WhenAll(tasks);
    }
    catch (Exception ex)
    {
        // Только первое исключение (как в errgroup)
        throw;
    }
}
```

> 💡 **Идиома Go**: Используйте `errgroup` вместо `WaitGroup`, если нужна обработка ошибок или автоматический cancellation.

---

### semaphore: взвешенный семафор

`semaphore.Weighted` — это семафор с поддержкой весов (можно захватывать N слотов за раз).

**Установка**:
```bash
go get golang.org/x/sync/semaphore
```

**Использование**:
```go
import "golang.org/x/sync/semaphore"

func RateLimitedDownload(ctx context.Context, urls []string, maxConcurrent int64) error {
    sem := semaphore.NewWeighted(maxConcurrent)
    g, ctx := errgroup.WithContext(ctx)

    for _, url := range urls {
        url := url
        g.Go(func() error {
            // Захватываем 1 слот (блокируемся, если достигнут лимит)
            if err := sem.Acquire(ctx, 1); err != nil {
                return err
            }
            defer sem.Release(1)

            return download(ctx, url)
        })
    }

    return g.Wait()
}

// Пример с весами: тяжёлые файлы занимают больше слотов
func DownloadWithWeights(ctx context.Context, files []FileInfo, maxWeight int64) error {
    sem := semaphore.NewWeighted(maxWeight)
    g, ctx := errgroup.WithContext(ctx)

    for _, file := range files {
        file := file
        g.Go(func() error {
            weight := file.Size / (1024 * 1024) // MB
            if weight < 1 {
                weight = 1
            }

            if err := sem.Acquire(ctx, weight); err != nil {
                return err
            }
            defer sem.Release(weight)

            return downloadFile(ctx, file)
        })
    }

    return g.Wait()
}
```

**Сравнение с C#**:
```csharp
// C# (SemaphoreSlim)
var semaphore = new SemaphoreSlim(10);

foreach (var url in urls)
{
    await semaphore.WaitAsync();
    _ = Task.Run(async () =>
    {
        try
        {
            await DownloadAsync(url);
        }
        finally
        {
            semaphore.Release();
        }
    });
}
```

**Альтернатива: буферизированный канал** (более идиоматично для Go):
```go
func RateLimitedDownload(urls []string, maxConcurrent int) {
    sem := make(chan struct{}, maxConcurrent)

    for _, url := range urls {
        sem <- struct{}{} // Захватываем слот
        go func(url string) {
            defer func() { <-sem }() // Освобождаем
            download(url)
        }(url)
    }

    // Ждём, пока все завершатся
    for i := 0; i < cap(sem); i++ {
        sem <- struct{}{}
    }
}
```

> 💡 **Идиома Go**: Для простых сценариев используйте **буферизированный канал** как семафор. `semaphore.Weighted` нужен только для взвешенных слотов или интеграции с `context`.

---

### singleflight: дедупликация вызовов

`singleflight.Group` устраняет дублирование одновременных вызовов одной и той же функции. Полезно для кэширования.

**Установка**:
```bash
go get golang.org/x/sync/singleflight
```

**Проблема**:
```go
// ❌ БЕЗ singleflight: 1000 одновременных запросов = 1000 вызовов БД
func (c *Cache) GetUser(id int) (*User, error) {
    if user := c.get(id); user != nil {
        return user, nil
    }

    // Если кэш пуст, все горутины пойдут в БД!
    user, err := db.Query("SELECT * FROM users WHERE id = ?", id)
    if err != nil {
        return nil, err
    }

    c.set(id, user)
    return user, nil
}
```

**Решение с singleflight**:
```go
import "golang.org/x/sync/singleflight"

type Cache struct {
    mu    sync.RWMutex
    data  map[int]*User
    group singleflight.Group
}

func (c *Cache) GetUser(id int) (*User, error) {
    // Проверяем кэш
    c.mu.RLock()
    if user := c.data[id]; user != nil {
        c.mu.RUnlock()
        return user, nil
    }
    c.mu.RUnlock()

    // Дедупликация: только ОДНА горутина выполнит запрос в БД
    key := fmt.Sprintf("user:%d", id)
    v, err, shared := c.group.Do(key, func() (interface{}, error) {
        user, err := db.Query("SELECT * FROM users WHERE id = ?", id)
        if err != nil {
            return nil, err
        }

        // Сохраняем в кэш
        c.mu.Lock()
        c.data[id] = user
        c.mu.Unlock()

        return user, nil
    })

    if err != nil {
        return nil, err
    }

    // shared == true, если результат получен от другой горутины
    return v.(*User), nil
}
```

**Пример: защита от cache stampede**:
```go
type APICache struct {
    mu    sync.RWMutex
    cache map[string][]byte
    group singleflight.Group
    ttl   time.Duration
}

func (c *APICache) Get(ctx context.Context, url string) ([]byte, error) {
    // Проверяем кэш
    c.mu.RLock()
    if data, ok := c.cache[url]; ok {
        c.mu.RUnlock()
        return data, nil
    }
    c.mu.RUnlock()

    // Дедупликация запросов
    v, err, _ := c.group.Do(url, func() (interface{}, error) {
        // Только одна горутина выполнит HTTP запрос
        resp, err := http.Get(url)
        if err != nil {
            return nil, err
        }
        defer resp.Body.Close()

        data, err := io.ReadAll(resp.Body)
        if err != nil {
            return nil, err
        }

        // Кэшируем
        c.mu.Lock()
        c.cache[url] = data
        c.mu.Unlock()

        // Автоматическое удаление через TTL
        time.AfterFunc(c.ttl, func() {
            c.mu.Lock()
            delete(c.cache, url)
            c.mu.Unlock()
        })

        return data, nil
    })

    if err != nil {
        return nil, err
    }

    return v.([]byte), nil
}
```

**Методы singleflight.Group**:

| Метод | Описание |
|-------|----------|
| `Do(key, fn)` | Выполняет `fn` для ключа, дедуплицируя одновременные вызовы. Возвращает `(result, error, shared)`. |
| `DoChan(key, fn)` | Асинхронная версия, возвращает канал с результатом. |
| `Forget(key)` | Забывает ключ (следующий вызов выполнит `fn` снова). |

**Сравнение с C#**:
```csharp
// C# (нет встроенного аналога, можно реализовать через SemaphoreSlim + Dictionary)
public class SingleFlight<TKey, TValue>
{
    private readonly ConcurrentDictionary<TKey, SemaphoreSlim> _locks = new();

    public async Task<TValue> DoAsync(TKey key, Func<Task<TValue>> fn)
    {
        var semaphore = _locks.GetOrAdd(key, _ => new SemaphoreSlim(1, 1));

        await semaphore.WaitAsync();
        try
        {
            return await fn();
        }
        finally
        {
            semaphore.Release();
            _locks.TryRemove(key, out _);
        }
    }
}
```

> 💡 **Когда использовать singleflight**:
> - Защита от **cache stampede** (когда кэш истекает под нагрузкой)
> - Дедупликация дорогих операций (БД, внешние API)
> - Снижение нагрузки при одновременных запросах одних данных

---

### Сравнительная таблица: golang.org/x/sync

| Примитив | Назначение | Аналог в C# | Когда использовать |
|----------|-----------|-------------|-------------------|
| `errgroup.Group` | WaitGroup + ошибки + cancellation | `Task.WhenAll` + exception handling | Конкурентная обработка с ошибками |
| `semaphore.Weighted` | Взвешенный семафор | `SemaphoreSlim` | Ограничение конкурентности (особенно с весами) |
| `singleflight.Group` | Дедупликация вызовов | Нет (реализовать вручную) | Защита от cache stampede |

---

**Вопросы?** Открой issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Назад: 2.3 Сборка мусора (GC)](03_gc.md) | [Вперёд: 2.5 Обработка ошибок →](05_error_handling.md)
