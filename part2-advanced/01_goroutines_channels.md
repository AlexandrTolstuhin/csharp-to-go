# 2.1 Горутины и каналы

## Содержание
- [Введение](#введение)
- [Горутины vs C# Task/Thread](#горутины-vs-c-taskthread)
- [Каналы: основы](#каналы-основы)
- [Буферизированные каналы](#буферизированные-каналы)
- [Select statement](#select-statement)
- [Context и cancellation](#context-и-cancellation)
- [Паттерны конкурентности](#паттерны-конкурентности)
- [Утечки горутин](#утечки-горутин)
- [Практические примеры](#практические-примеры)
- [Чек-лист](#чек-лист)

---

## Введение

Конкурентность в Go - это один из главных козырей языка и **радикально отличается** от C# async/await.

### Философия

**C#**:
- Async/await построен вокруг **Promise/Future** модели
- Task представляет **результат** асинхронной операции
- Использует **Thread Pool** под капотом
- Callback-based (continuation)

**Go**:
- Горутины - это **легковесные потоки**
- Каналы для **коммуникации** между горутинами
- "Don't communicate by sharing memory; share memory by communicating"
- CSP (Communicating Sequential Processes) модель

> 💡 **Ключевое отличие**: В C# вы работаете с Task<T> (результат), в Go - с горутинами (процесс) и каналами (коммуникация).

---

## Горутины vs C# Task/Thread

### Что такое горутина?

Горутина - это **функция**, выполняющаяся конкурентно с другим кодом. Это НЕ OS thread.

**Характеристики**:
- Легковесная (~2KB стека против 1MB у OS thread)
- Множественное мультиплексирование на OS threads (Go runtime управляет)
- Быстрое создание (nanoseconds)
- Можно создать миллионы горутин

### C# Thread

**C#**:
```csharp
// OS Thread - тяжеловесный
var thread = new Thread(() =>
{
    Console.WriteLine("Running in thread");
    Thread.Sleep(1000);
});
thread.Start();
thread.Join(); // Ждём завершения
```

**Go** (горутина):
```go
// Горутина - легковесная
go func() {
    fmt.Println("Running in goroutine")
    time.Sleep(1 * time.Second)
}()

// Нет прямого аналога Join - используем другие механизмы
```

### C# Task (async/await)

**C#**:
```csharp
public async Task<string> FetchDataAsync(string url)
{
    using var client = new HttpClient();
    var response = await client.GetStringAsync(url);
    return response;
}

// Использование
var data = await FetchDataAsync("https://api.example.com");
Console.WriteLine(data);

// Параллельные запросы
var task1 = FetchDataAsync("url1");
var task2 = FetchDataAsync("url2");
var results = await Task.WhenAll(task1, task2);
```

**Go** (горутины + каналы):
```go
func fetchData(url string) (string, error) {
    resp, err := http.Get(url)
    if err != nil {
        return "", err
    }
    defer resp.Body.Close()

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return "", err
    }

    return string(body), nil
}

// Использование с горутиной
func main() {
    // Канал для результата
    resultCh := make(chan string, 1)
    errCh := make(chan error, 1)

    go func() {
        data, err := fetchData("https://api.example.com")
        if err != nil {
            errCh <- err
            return
        }
        resultCh <- data
    }()

    // Ожидание результата
    select {
    case data := <-resultCh:
        fmt.Println(data)
    case err := <-errCh:
        fmt.Printf("Error: %v\n", err)
    }
}

// Параллельные запросы
func fetchMultiple(urls []string) ([]string, error) {
    type result struct {
        data string
        err  error
    }

    resultsCh := make(chan result, len(urls))

    // Запускаем горутину для каждого URL
    for _, url := range urls {
        go func(u string) {
            data, err := fetchData(u)
            resultsCh <- result{data: data, err: err}
        }(url)
    }

    // Собираем результаты
    results := make([]string, 0, len(urls))
    for i := 0; i < len(urls); i++ {
        res := <-resultsCh
        if res.err != nil {
            return nil, res.err
        }
        results = append(results, res.data)
    }

    return results, nil
}
```

### Сравнение: создание и запуск

**C#**:
```csharp
// Task.Run - запуск в ThreadPool
Task.Run(() => DoWork());

// async метод
await DoWorkAsync();

// Параллельно
await Task.WhenAll(
    DoWork1Async(),
    DoWork2Async()
);
```

**Go**:
```go
// Запуск горутины
go doWork()

// Нет async/await - используем горутины напрямую

// Параллельно (с sync.WaitGroup)
var wg sync.WaitGroup

wg.Add(2)
go func() {
    defer wg.Done()
    doWork1()
}()
go func() {
    defer wg.Done()
    doWork2()
}()

wg.Wait() // Ждём завершения всех
```

### Сравнительная таблица

| Аспект | C# Task | C# Thread | Go Goroutine |
|--------|---------|-----------|--------------|
| **Вес** | Легковесный | Тяжёлый (1MB) | Очень легковесный (2KB) |
| **Стоимость создания** | Низкая | Высокая | Минимальная |
| **Количество** | Тысячи | Десятки | Миллионы |
| **Планировщик** | .NET ThreadPool | OS | Go runtime |
| **Возвращаемое значение** | Task<T> | Нет | Через каналы |
| **Отмена** | CancellationToken | Thread.Abort (deprecated) | context.Context |
| **Await** | async/await | thread.Join() | WaitGroup/каналы |

> ⚠️ **Важно**: В Go нет прямого аналога `await`. Вы **не ждёте горутину напрямую** - вы используете каналы или sync.WaitGroup.

---

## Каналы: основы

Канал - это **typed conduit** (типизированный канал) для передачи данных между горутинами.

### Создание канала

```go
// Создание канала для int
ch := make(chan int)

// Канал для строк
messages := make(chan string)

// Канал для структур
type User struct {
    ID   int
    Name string
}
users := make(chan User)
```

### Отправка и получение

```go
ch := make(chan string)

// Отправка в канал (блокирующая операция)
go func() {
    ch <- "hello" // Запись в канал
}()

// Получение из канала (блокирующая операция)
msg := <-ch // Чтение из канала
fmt.Println(msg) // "hello"
```

> 💡 **Важно**: Отправка и получение **блокируют** горутину до тех пор, пока другая сторона не готова.

### C# аналог: Channel<T>

**C#** (System.Threading.Channels):
```csharp
var channel = Channel.CreateUnbounded<string>();

// Отправка
await channel.Writer.WriteAsync("hello");

// Получение
var msg = await channel.Reader.ReadAsync();
Console.WriteLine(msg);

// Закрытие
channel.Writer.Complete();
```

**Go**:
```go
ch := make(chan string)

// Отправка
ch <- "hello"

// Получение
msg := <-ch
fmt.Println(msg)

// Закрытие
close(ch)
```

### Закрытие канала

```go
ch := make(chan int, 3)

// Отправляем данные
ch <- 1
ch <- 2
ch <- 3

// Закрываем канал
close(ch)

// Читаем все значения
for val := range ch {
    fmt.Println(val) // 1, 2, 3
}

// После close() чтение вернёт zero value
val := <-ch
fmt.Println(val) // 0

// Проверка, закрыт ли канал
val, ok := <-ch
if !ok {
    fmt.Println("Channel closed")
}
```

> ⚠️ **Важно**: Закрывать канал должен **отправитель**, не получатель. Отправка в закрытый канал вызовет **panic**.

### Идиоматичный паттерн: range over channel

**Go**:
```go
func producer(ch chan<- int) {
    for i := 0; i < 10; i++ {
        ch <- i
    }
    close(ch) // Важно закрыть!
}

func consumer(ch <-chan int) {
    for val := range ch { // Читаем до close()
        fmt.Println(val)
    }
}

func main() {
    ch := make(chan int)

    go producer(ch)
    consumer(ch) // Блокируется до закрытия канала
}
```

**C#** (аналог):
```csharp
async Task Producer(ChannelWriter<int> writer)
{
    for (int i = 0; i < 10; i++)
    {
        await writer.WriteAsync(i);
    }
    writer.Complete();
}

async Task Consumer(ChannelReader<int> reader)
{
    await foreach (var val in reader.ReadAllAsync())
    {
        Console.WriteLine(val);
    }
}

var channel = Channel.CreateUnbounded<int>();
_ = Producer(channel.Writer);
await Consumer(channel.Reader);
```

### Направленные каналы (directional channels)

```go
// Только для отправки
func send(ch chan<- int, value int) {
    ch <- value
    // val := <-ch // ОШИБКА: нельзя читать
}

// Только для получения
func receive(ch <-chan int) int {
    return <-ch
    // ch <- 5 // ОШИБКА: нельзя писать
}

// Двунаправленный
func bidirectional(ch chan int) {
    ch <- 42
    val := <-ch
}
```

> 💡 **Идиома Go**: Используйте направленные каналы в сигнатурах функций для ясности и безопасности.

---

## Буферизированные каналы

### Небуферизированный канал (по умолчанию)

```go
ch := make(chan int) // Буфер = 0

// Отправка блокируется до получения
go func() {
    ch <- 42 // Блокируется здесь
}()

val := <-ch // Разблокирует отправку
fmt.Println(val)
```

### Буферизированный канал

```go
ch := make(chan int, 3) // Буфер на 3 элемента

// Отправки не блокируются, пока буфер не заполнен
ch <- 1 // OK
ch <- 2 // OK
ch <- 3 // OK
// ch <- 4 // Блокируется - буфер полон

val := <-ch // Освобождает место
ch <- 4     // Теперь OK

fmt.Println(len(ch)) // 3 (текущее количество)
fmt.Println(cap(ch)) // 3 (capacity)
```

### C# аналог

**C#**:
```csharp
// Unbounded (бесконечный буфер)
var channel = Channel.CreateUnbounded<int>();

// Bounded (ограниченный буфер)
var options = new BoundedChannelOptions(3)
{
    FullMode = BoundedChannelFullMode.Wait
};
var bounded = Channel.CreateBounded<int>(options);

// Отправка
await bounded.Writer.WriteAsync(1);
await bounded.Writer.WriteAsync(2);
await bounded.Writer.WriteAsync(3);
// Следующий WriteAsync заблокируется
```

**Go**:
```go
// Небуферизированный (синхронный)
ch := make(chan int)

// Буферизированный
ch := make(chan int, 3)
```

### Когда использовать буферизированные каналы?

✅ **Используйте буферизированные каналы**:
- Когда знаете точное количество элементов
- Для decoupling отправителя и получателя
- Для семафоров (ограничение конкурентности)
- Для worker pools

❌ **Не используйте**:
- Как "решение" deadlock (обычно скрывает проблему)
- Произвольные большие буферы "на всякий случай"

```go
// ✅ Хорошо: буфер = количество workers
results := make(chan Result, numWorkers)

// ✅ Хорошо: семафор для ограничения конкурентности
sem := make(chan struct{}, maxConcurrent)

// ❌ Плохо: произвольный большой буфер
ch := make(chan int, 10000) // Зачем так много?
```

---

## Select statement

`select` - это как `switch` для каналов. Позволяет ждать на **нескольких каналах** одновременно.

### Основы select

```go
ch1 := make(chan string)
ch2 := make(chan string)

go func() {
    time.Sleep(1 * time.Second)
    ch1 <- "from ch1"
}()

go func() {
    time.Sleep(2 * time.Second)
    ch2 <- "from ch2"
}()

// Ждём первый доступный канал
select {
case msg1 := <-ch1:
    fmt.Println(msg1) // Сработает первым
case msg2 := <-ch2:
    fmt.Println(msg2)
}
```

### C# аналог: Task.WhenAny

**C#**:
```csharp
var task1 = Task.Run(async () =>
{
    await Task.Delay(1000);
    return "from task1";
});

var task2 = Task.Run(async () =>
{
    await Task.Delay(2000);
    return "from task2";
});

// Ждём первую завершившуюся задачу
var completed = await Task.WhenAny(task1, task2);
var result = await completed;
Console.WriteLine(result); // "from task1"
```

**Go**:
```go
select {
case msg := <-ch1:
    fmt.Println(msg)
case msg := <-ch2:
    fmt.Println(msg)
}
```

### Default case (неблокирующая операция)

```go
ch := make(chan string)

// Неблокирующая попытка чтения
select {
case msg := <-ch:
    fmt.Println("Received:", msg)
default:
    fmt.Println("No message available")
}

// Неблокирующая попытка записи
select {
case ch <- "hello":
    fmt.Println("Sent message")
default:
    fmt.Println("Channel full or no receiver")
}
```

### Timeout паттерн

**C#**:
```csharp
var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));

try
{
    var result = await LongRunningTask(cts.Token);
    Console.WriteLine(result);
}
catch (OperationCanceledException)
{
    Console.WriteLine("Timeout!");
}
```

**Go**:
```go
ch := make(chan string)

go func() {
    time.Sleep(10 * time.Second)
    ch <- "result"
}()

select {
case result := <-ch:
    fmt.Println(result)
case <-time.After(5 * time.Second):
    fmt.Println("Timeout!")
}
```

### Ticker паттерн (периодическое выполнение)

**C#**:
```csharp
using var timer = new PeriodicTimer(TimeSpan.FromSeconds(1));

while (await timer.WaitForNextTickAsync())
{
    Console.WriteLine("Tick");
}
```

**Go**:
```go
ticker := time.NewTicker(1 * time.Second)
defer ticker.Stop()

for {
    select {
    case <-ticker.C:
        fmt.Println("Tick")
    case <-done:
        return
    }
}
```

### Идиоматичный select loop

```go
func worker(jobs <-chan Job, results chan<- Result, quit <-chan struct{}) {
    for {
        select {
        case job := <-jobs:
            // Обрабатываем задачу
            result := process(job)
            results <- result

        case <-quit:
            // Graceful shutdown
            fmt.Println("Worker stopping")
            return
        }
    }
}
```

---

## Context и cancellation

`context.Context` - это стандартный способ передачи **deadline**, **cancellation signals** и **request-scoped values**.

### C# CancellationToken

**C#**:
```csharp
public async Task DoWorkAsync(CancellationToken cancellationToken)
{
    while (!cancellationToken.IsCancellationRequested)
    {
        await Task.Delay(1000, cancellationToken);
        Console.WriteLine("Working...");
    }
}

// Использование
var cts = new CancellationTokenSource();
var task = DoWorkAsync(cts.Token);

// Отмена через 5 секунд
await Task.Delay(5000);
cts.Cancel();

await task;
```

### Go context.Context

**Go**:
```go
func doWork(ctx context.Context) {
    for {
        select {
        case <-ctx.Done():
            // Контекст отменён
            fmt.Println("Cancelled:", ctx.Err())
            return
        default:
            time.Sleep(1 * time.Second)
            fmt.Println("Working...")
        }
    }
}

// Использование
ctx, cancel := context.WithCancel(context.Background())
defer cancel()

go doWork(ctx)

// Отмена через 5 секунд
time.Sleep(5 * time.Second)
cancel()

time.Sleep(1 * time.Second) // Даём время завершиться
```

### Типы контекстов

#### 1. WithCancel - ручная отмена

```go
ctx, cancel := context.WithCancel(context.Background())
defer cancel()

go func() {
    <-time.After(5 * time.Second)
    cancel() // Отменяем через 5 сек
}()

doWork(ctx)
```

#### 2. WithTimeout - автоматическая отмена по таймауту

```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

result, err := fetchWithTimeout(ctx, "https://api.example.com")
if err != nil {
    if errors.Is(err, context.DeadlineExceeded) {
        fmt.Println("Timeout!")
    }
}
```

#### 3. WithDeadline - отмена в конкретное время

```go
deadline := time.Now().Add(10 * time.Second)
ctx, cancel := context.WithDeadline(context.Background(), deadline)
defer cancel()

doWork(ctx)
```

#### 4. WithValue - передача значений

```go
type key string

ctx := context.WithValue(context.Background(), key("userID"), 123)

// В другой функции
if userID, ok := ctx.Value(key("userID")).(int); ok {
    fmt.Printf("User ID: %d\n", userID)
}
```

> ⚠️ **Важно**: Не злоупотребляйте `WithValue`. Используйте только для request-scoped данных (trace ID, auth tokens и т.д.).

### Идиоматичное использование context

```go
func fetchData(ctx context.Context, url string) ([]byte, error) {
    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return nil, err
    }

    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    return io.ReadAll(resp.Body)
}

// Использование с таймаутом
func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()

    data, err := fetchData(ctx, "https://api.example.com")
    if err != nil {
        log.Fatal(err)
    }

    fmt.Println(string(data))
}
```

### Сравнение: отмена операции

**C#**:
```csharp
var cts = new CancellationTokenSource();

var task = Task.Run(async () =>
{
    for (int i = 0; i < 100; i++)
    {
        cts.Token.ThrowIfCancellationRequested();
        await Task.Delay(100);
    }
}, cts.Token);

// Отменяем через 2 секунды
await Task.Delay(2000);
cts.Cancel();

try
{
    await task;
}
catch (OperationCanceledException)
{
    Console.WriteLine("Task was cancelled");
}
```

**Go**:
```go
ctx, cancel := context.WithCancel(context.Background())

go func() {
    for i := 0; i < 100; i++ {
        select {
        case <-ctx.Done():
            return
        default:
            time.Sleep(100 * time.Millisecond)
        }
    }
}()

// Отменяем через 2 секунды
time.Sleep(2 * time.Second)
cancel()
```

---

## Паттерны конкурентности

### 1. Worker Pool

**Задача**: Обработка большого количества задач фиксированным числом workers.

```go
func workerPool(numWorkers int, jobs <-chan Job, results chan<- Result) {
    var wg sync.WaitGroup

    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()

            for job := range jobs {
                fmt.Printf("Worker %d processing job %d\n", id, job.ID)
                result := process(job)
                results <- result
            }
        }(i)
    }

    wg.Wait()
    close(results)
}

func main() {
    jobs := make(chan Job, 100)
    results := make(chan Result, 100)

    // Запускаем worker pool
    go workerPool(5, jobs, results)

    // Отправляем задачи
    for i := 0; i < 100; i++ {
        jobs <- Job{ID: i}
    }
    close(jobs)

    // Собираем результаты
    for result := range results {
        fmt.Printf("Result: %v\n", result)
    }
}
```

**C# аналог**:
```csharp
var jobs = Channel.CreateBounded<Job>(100);
var results = Channel.CreateBounded<Result>(100);

// Workers
var workers = Enumerable.Range(0, 5)
    .Select(id => Task.Run(async () =>
    {
        await foreach (var job in jobs.Reader.ReadAllAsync())
        {
            Console.WriteLine($"Worker {id} processing {job.ID}");
            var result = Process(job);
            await results.Writer.WriteAsync(result);
        }
    }))
    .ToArray();

// Отправляем задачи
_ = Task.Run(async () =>
{
    for (int i = 0; i < 100; i++)
    {
        await jobs.Writer.WriteAsync(new Job { ID = i });
    }
    jobs.Writer.Complete();
});

// Собираем результаты
_ = Task.Run(async () =>
{
    await Task.WhenAll(workers);
    results.Writer.Complete();
});

await foreach (var result in results.Reader.ReadAllAsync())
{
    Console.WriteLine($"Result: {result}");
}
```

### 2. Fan-Out, Fan-In

**Fan-Out**: Распределение работы по нескольким горутинам
**Fan-In**: Сбор результатов из нескольких каналов в один

```go
// Fan-Out: одна горутина порождает N workers
func fanOut(in <-chan int, n int) []<-chan int {
    outputs := make([]<-chan int, n)

    for i := 0; i < n; i++ {
        out := make(chan int)
        outputs[i] = out

        go func(out chan<- int) {
            defer close(out)
            for val := range in {
                out <- val * 2 // Обработка
            }
        }(out)
    }

    return outputs
}

// Fan-In: несколько каналов сливаются в один
func fanIn(channels ...<-chan int) <-chan int {
    out := make(chan int)

    var wg sync.WaitGroup
    wg.Add(len(channels))

    for _, ch := range channels {
        go func(c <-chan int) {
            defer wg.Done()
            for val := range c {
                out <- val
            }
        }(ch)
    }

    go func() {
        wg.Wait()
        close(out)
    }()

    return out
}

// Использование
func main() {
    in := make(chan int)

    // Fan-Out: создаём 3 workers
    outputs := fanOut(in, 3)

    // Fan-In: объединяем результаты
    merged := fanIn(outputs...)

    // Отправляем данные
    go func() {
        for i := 0; i < 10; i++ {
            in <- i
        }
        close(in)
    }()

    // Получаем результаты
    for result := range merged {
        fmt.Println(result)
    }
}
```

### 3. Pipeline

Последовательная обработка данных через несколько стадий.

```go
// Стадия 1: генератор
func generator(nums ...int) <-chan int {
    out := make(chan int)

    go func() {
        defer close(out)
        for _, n := range nums {
            out <- n
        }
    }()

    return out
}

// Стадия 2: возведение в квадрат
func square(in <-chan int) <-chan int {
    out := make(chan int)

    go func() {
        defer close(out)
        for n := range in {
            out <- n * n
        }
    }()

    return out
}

// Стадия 3: фильтр (только чётные)
func filter(in <-chan int) <-chan int {
    out := make(chan int)

    go func() {
        defer close(out)
        for n := range in {
            if n%2 == 0 {
                out <- n
            }
        }
    }()

    return out
}

// Использование pipeline
func main() {
    // Строим pipeline: generator -> square -> filter
    nums := generator(1, 2, 3, 4, 5)
    squared := square(nums)
    filtered := filter(squared)

    // Читаем результаты
    for result := range filtered {
        fmt.Println(result) // 4, 16
    }
}
```

### 4. Semaphore (ограничение конкурентности)

```go
// Ограничиваем количество одновременных операций
func processWithLimit(urls []string, maxConcurrent int) {
    sem := make(chan struct{}, maxConcurrent)

    var wg sync.WaitGroup

    for _, url := range urls {
        wg.Add(1)

        go func(u string) {
            defer wg.Done()

            // Захватываем semaphore
            sem <- struct{}{}
            defer func() { <-sem }() // Освобождаем

            // Обрабатываем
            process(u)
        }(url)
    }

    wg.Wait()
}
```

**C# аналог (SemaphoreSlim)**:
```csharp
var semaphore = new SemaphoreSlim(maxConcurrent);
var tasks = new List<Task>();

foreach (var url in urls)
{
    tasks.Add(Task.Run(async () =>
    {
        await semaphore.WaitAsync();
        try
        {
            await Process(url);
        }
        finally
        {
            semaphore.Release();
        }
    }));
}

await Task.WhenAll(tasks);
```

### 5. errgroup (golang.org/x/sync/errgroup)

Удобная обёртка для управления группой горутин с обработкой ошибок.

```go
import "golang.org/x/sync/errgroup"

func fetchMultipleWithErrgroup(ctx context.Context, urls []string) ([]string, error) {
    g, ctx := errgroup.WithContext(ctx)
    results := make([]string, len(urls))

    for i, url := range urls {
        i, url := i, url // Захват переменных
        g.Go(func() error {
            data, err := fetchData(ctx, url)
            if err != nil {
                return err
            }
            results[i] = data
            return nil
        })
    }

    if err := g.Wait(); err != nil {
        return nil, err
    }

    return results, nil
}
```

**C# аналог**:
```csharp
var tasks = urls.Select(async url =>
{
    var data = await FetchData(url);
    return data;
});

var results = await Task.WhenAll(tasks); // Бросит исключение при первой ошибке
```

---

## Утечки горутин

Горутина "утекает", если она **никогда не завершится**. Это утечка ресурсов.

### Пример утечки

```go
// ❌ Утечка: горутина никогда не завершится
func leak() {
    ch := make(chan int)

    go func() {
        val := <-ch // Блокируется навсегда
        fmt.Println(val)
    }()

    // Канал не закрыли, ничего не отправили
    // Горутина висит вечно
}
```

### Как избежать утечек

#### 1. Всегда закрывайте каналы

```go
// ✅ Правильно
func noLeak() {
    ch := make(chan int)

    go func() {
        for val := range ch {
            fmt.Println(val)
        }
    }()

    ch <- 1
    ch <- 2
    close(ch) // Горутина завершится
}
```

#### 2. Используйте context для отмены

```go
// ✅ Правильно: с контекстом
func fetchWithCancel(ctx context.Context, url string) error {
    resultCh := make(chan []byte)
    errCh := make(chan error)

    go func() {
        data, err := http.Get(url)
        if err != nil {
            errCh <- err
            return
        }
        resultCh <- data
    }()

    select {
    case <-ctx.Done():
        return ctx.Err()
    case err := <-errCh:
        return err
    case data := <-resultCh:
        process(data)
        return nil
    }
}
```

#### 3. Используйте буферизированные каналы с осторожностью

```go
// ❌ Может утечь при панике в получателе
ch := make(chan int)
go func() {
    ch <- 42 // Блокируется, если получатель умер
}()

// ✅ Буфер = 1 предотвращает блокировку
ch := make(chan int, 1)
go func() {
    ch <- 42 // Не блокируется
}()
```

#### 4. Graceful shutdown

```go
type Server struct {
    quit chan struct{}
}

func (s *Server) Start() {
    s.quit = make(chan struct{})

    go func() {
        ticker := time.NewTicker(1 * time.Second)
        defer ticker.Stop()

        for {
            select {
            case <-ticker.C:
                s.doWork()
            case <-s.quit:
                fmt.Println("Shutting down")
                return
            }
        }
    }()
}

func (s *Server) Stop() {
    close(s.quit)
}
```

### Обнаружение утечек

Используйте **goleak** (go.uber.org/goleak) в тестах:

```go
import "go.uber.org/goleak"

func TestMyFunction(t *testing.T) {
    defer goleak.VerifyNone(t)

    // Тест код
}
```

---

## Практические примеры

### Пример 1: Конкурентная загрузка URL

**Задача**: Загрузить несколько URL конкурентно с ограничением и таймаутом.

```go
package main

import (
    "context"
    "fmt"
    "io"
    "net/http"
    "sync"
    "time"
)

type Result struct {
    URL  string
    Data string
    Err  error
}

func fetchURL(ctx context.Context, url string) (string, error) {
    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return "", err
    }

    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return "", err
    }
    defer resp.Body.Close()

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return "", err
    }

    return string(body), nil
}

func fetchMultiple(ctx context.Context, urls []string, maxConcurrent int) []Result {
    results := make([]Result, len(urls))
    sem := make(chan struct{}, maxConcurrent)

    var wg sync.WaitGroup

    for i, url := range urls {
        wg.Add(1)

        go func(index int, u string) {
            defer wg.Done()

            // Захватываем семафор
            sem <- struct{}{}
            defer func() { <-sem }()

            // Загружаем с таймаутом
            data, err := fetchURL(ctx, u)
            results[index] = Result{
                URL:  u,
                Data: data,
                Err:  err,
            }
        }(i, url)
    }

    wg.Wait()
    return results
}

func main() {
    urls := []string{
        "https://example.com",
        "https://golang.org",
        "https://github.com",
    }

    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()

    results := fetchMultiple(ctx, urls, 2) // Макс 2 одновременных запроса

    for _, result := range results {
        if result.Err != nil {
            fmt.Printf("%s: ERROR - %v\n", result.URL, result.Err)
        } else {
            fmt.Printf("%s: %d bytes\n", result.URL, len(result.Data))
        }
    }
}
```

### Пример 2: Producer-Consumer с graceful shutdown

```go
package main

import (
    "context"
    "fmt"
    "math/rand"
    "sync"
    "time"
)

type Job struct {
    ID int
}

type Result struct {
    JobID int
    Value int
}

func producer(ctx context.Context, jobs chan<- Job, count int) {
    defer close(jobs)

    for i := 0; i < count; i++ {
        select {
        case <-ctx.Done():
            fmt.Println("Producer cancelled")
            return
        case jobs <- Job{ID: i}:
            fmt.Printf("Produced job %d\n", i)
        }
    }
}

func worker(id int, ctx context.Context, jobs <-chan Job, results chan<- Result, wg *sync.WaitGroup) {
    defer wg.Done()

    for {
        select {
        case <-ctx.Done():
            fmt.Printf("Worker %d cancelled\n", id)
            return

        case job, ok := <-jobs:
            if !ok {
                fmt.Printf("Worker %d finished (no more jobs)\n", id)
                return
            }

            // Симуляция работы
            time.Sleep(time.Duration(rand.Intn(500)) * time.Millisecond)

            result := Result{
                JobID: job.ID,
                Value: job.ID * 2,
            }

            select {
            case <-ctx.Done():
                return
            case results <- result:
                fmt.Printf("Worker %d completed job %d\n", id, job.ID)
            }
        }
    }
}

func main() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    jobs := make(chan Job, 10)
    results := make(chan Result, 10)

    const numWorkers = 3
    var wg sync.WaitGroup

    // Запускаем workers
    for i := 1; i <= numWorkers; i++ {
        wg.Add(1)
        go worker(i, ctx, jobs, results, &wg)
    }

    // Запускаем producer
    go producer(ctx, jobs, 20)

    // Закрываем results после завершения всех workers
    go func() {
        wg.Wait()
        close(results)
    }()

    // Собираем результаты (или отменяем через 5 секунд)
    timeout := time.After(5 * time.Second)

    for {
        select {
        case result, ok := <-results:
            if !ok {
                fmt.Println("All results collected")
                return
            }
            fmt.Printf("Result: Job %d = %d\n", result.JobID, result.Value)

        case <-timeout:
            fmt.Println("Timeout! Cancelling...")
            cancel()
            // Даём время workers завершиться
            wg.Wait()
            return
        }
    }
}
```

### Пример 3: Rate Limiter

```go
package main

import (
    "context"
    "fmt"
    "time"
)

type RateLimiter struct {
    rate     time.Duration
    tokens   chan struct{}
    stopOnce sync.Once
    stop     chan struct{}
}

func NewRateLimiter(requestsPerSecond int) *RateLimiter {
    rl := &RateLimiter{
        rate:   time.Second / time.Duration(requestsPerSecond),
        tokens: make(chan struct{}, requestsPerSecond),
        stop:   make(chan struct{}),
    }

    // Заполняем буфер токенами
    for i := 0; i < requestsPerSecond; i++ {
        rl.tokens <- struct{}{}
    }

    // Горутина пополнения токенов
    go rl.refill()

    return rl
}

func (rl *RateLimiter) refill() {
    ticker := time.NewTicker(rl.rate)
    defer ticker.Stop()

    for {
        select {
        case <-ticker.C:
            select {
            case rl.tokens <- struct{}{}:
            default:
                // Буфер полон, пропускаем
            }
        case <-rl.stop:
            return
        }
    }
}

func (rl *RateLimiter) Allow(ctx context.Context) error {
    select {
    case <-ctx.Done():
        return ctx.Err()
    case <-rl.tokens:
        return nil
    }
}

func (rl *RateLimiter) Stop() {
    rl.stopOnce.Do(func() {
        close(rl.stop)
    })
}

func main() {
    limiter := NewRateLimiter(5) // 5 запросов в секунду
    defer limiter.Stop()

    ctx := context.Background()

    for i := 0; i < 20; i++ {
        if err := limiter.Allow(ctx); err != nil {
            fmt.Printf("Request %d failed: %v\n", i, err)
            break
        }

        fmt.Printf("Request %d allowed at %v\n", i, time.Now().Format("15:04:05.000"))
        // Выполняем запрос...
    }
}
```

---

## Чек-лист

После изучения этого раздела вы должны уметь:

- [ ] Запускать горутины с `go`
- [ ] Создавать и использовать каналы
- [ ] Понимать разницу между буферизированными и небуферизированными каналами
- [ ] Использовать `select` для ожидания на нескольких каналах
- [ ] Правильно закрывать каналы
- [ ] Использовать `context.Context` для cancellation
- [ ] Реализовывать паттерны: Worker Pool, Fan-Out/Fan-In, Pipeline
- [ ] Избегать утечек горутин
- [ ] Использовать `sync.WaitGroup` для ожидания горутин
- [ ] Понимать отличия от C# async/await

---

## Следующие шаги

Переходите к [2.2 Go Runtime и планировщик](02_runtime_scheduler.md) для понимания того, как Go выполняет горутины под капотом.

---

**Вопросы?** Открой issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Назад: Часть 1](../part1-basics/04_practice.md) | [Вперёд: Runtime и планировщик →](02_runtime_scheduler.md)
