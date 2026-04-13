# io.Reader и io.Writer: потоковая обработка данных

---

## Введение

> 💡 **Для C# разработчиков**: В C# абстракция потоков строится на `System.IO.Stream` — абстрактном классе с десятками методов (`Read`, `Write`, `Seek`, `Flush`, `CopyTo`, `Length`, свойства `CanRead`, `CanWrite`, `CanSeek`...). В Go вся потоковая модель строится на **двух интерфейсах по одному методу**: `io.Reader` и `io.Writer`. Эта минималистичность — не ограничение, а сила: любая структура, реализующая один метод, автоматически совместима со всей экосистемой Go.

### Что вы узнаете

- `io.Reader` и `io.Writer`: контракт и семантика
- Композиция потоков: `io.TeeReader`, `io.MultiWriter`, `io.Pipe`
- `bufio`: буферизированный I/O и сканирование
- Потоковая обработка JSON, CSV и бинарных данных
- Паттерны: обёртки, декораторы, middleware для потоков
- Типичные ошибки C# разработчиков при работе с I/O в Go
- Производительность: аллокации, буферы, `sync.Pool`

---

## Сравнительная таблица: .NET Stream vs Go io

| Аспект | C# (System.IO) | Go (io) |
|--------|----------------|---------|
| **Базовая абстракция** | `Stream` (абстрактный класс, ~30 методов) | `io.Reader` / `io.Writer` (по 1 методу) |
| **Тип реализации** | Наследование | Утиная типизация (implicit interfaces) |
| **Буферизация** | `BufferedStream` | `bufio.Reader` / `bufio.Writer` |
| **Копирование** | `stream.CopyTo(dst)` | `io.Copy(dst, src)` |
| **Ограничение чтения** | Ручная реализация | `io.LimitReader` |
| **Чтение целиком** | `stream.ReadToEnd()` / `BinaryReader` | `io.ReadAll` |
| **Pipe** | `System.IO.Pipes` (OS-level) | `io.Pipe()` (in-memory, goroutine-safe) |
| **Декорирование** | Наследование / `DelegatingStream` | Обёртка структурой |
| **Закрытие** | `IDisposable` + `using` | `io.Closer` + `defer` |
| **Позиционирование** | `Stream.Seek()` | `io.Seeker` (отдельный интерфейс) |

---

## io.Reader: контракт

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}
```

Контракт `Read` прост, но содержит важные нюансы:

1. Читает **до** `len(p)` байт в `p`
2. Возвращает количество прочитанных байт `n` (0 <= n <= len(p))
3. Возвращает `io.EOF` когда данные закончились
4. **Может вернуть `n > 0` и `io.EOF` одновременно** — это валидное поведение
5. Не должен оставлять `p` частично заполненным без причины

### C# Stream.Read vs Go io.Reader

**C#**:
```csharp
// Stream.Read может вернуть меньше байт, чем запрошено
byte[] buffer = new byte[4096];
int bytesRead = stream.Read(buffer, 0, buffer.Length);
// bytesRead может быть от 0 до 4096
// 0 означает конец потока
```

**Go**:
```go
// io.Reader.Read — аналогичная семантика, но конец потока — io.EOF
buf := make([]byte, 4096)
n, err := reader.Read(buf)
// n может быть от 0 до 4096
// err == io.EOF означает конец потока
// Важно: СНАЧАЛА обработать buf[:n], ПОТОМ проверить err
```

### Главная ловушка: порядок обработки n и err

```go
// ❌ Неправильно: теряем последнюю порцию данных
n, err := reader.Read(buf)
if err != nil {
    return err // n байт данных потеряны!
}
process(buf[:n])

// ✅ Правильно: обрабатываем данные ДО проверки ошибки
n, err := reader.Read(buf)
if n > 0 {
    process(buf[:n])
}
if err != nil {
    if err == io.EOF {
        break // нормальное завершение
    }
    return err
}
```

> 💡 **Для C# разработчиков**: в C# `Stream.Read` возвращает 0 при конце потока, нет отдельного сигнала об ошибке. В Go конец данных и ошибка — два независимых значения, и они могут прийти одновременно. Это фундаментальное отличие, которое вызывает баги у новичков.

---

## io.Writer: контракт

```go
type Writer interface {
    Write(p []byte) (n int, err error)
}
```

Контракт `Write`:

1. Записывает данные из `p`
2. Возвращает количество записанных байт `n` (0 <= n <= len(p))
3. **Если `n < len(p)` — обязана вернуть ненулевую ошибку**
4. Не должна модифицировать `p` (даже временно)

```go
// Запись в io.Writer
data := []byte("hello, world")
n, err := writer.Write(data)
if err != nil {
    return fmt.Errorf("запись: %w", err)
}
// n == len(data) гарантировано, если err == nil
```

### Стандартные реализации

```go
// Файл
f, _ := os.Create("output.txt")
defer f.Close()
f.Write([]byte("данные"))

// Буфер в памяти
var buf bytes.Buffer
buf.Write([]byte("данные"))
fmt.Println(buf.String()) // "данные"

// HTTP response
func handler(w http.ResponseWriter, r *http.Request) {
    w.Write([]byte("ответ")) // w реализует io.Writer
}

// Хеш-функция
h := sha256.New() // hash.Hash реализует io.Writer
h.Write([]byte("данные"))
sum := h.Sum(nil)

// /dev/null
io.Discard.Write([]byte("в никуда"))
```

---

## Композиция: сила маленьких интерфейсов

### Составные интерфейсы в стандартной библиотеке

```go
// io пакет определяет составные интерфейсы через embedding
type ReadWriter interface {
    Reader
    Writer
}

type ReadCloser interface {
    Reader
    Closer
}

type WriteCloser interface {
    Writer
    Closer
}

type ReadWriteCloser interface {
    Reader
    Writer
    Closer
}

type ReadSeeker interface {
    Reader
    Seeker
}
```

В C# всё это — один класс `Stream` с флагами `CanRead`, `CanSeek`. В Go — явная композиция: если функция принимает `io.ReadSeeker`, она гарантированно получает и чтение, и позиционирование.

### io.Copy: универсальное копирование

```go
// Копирование из Reader в Writer
n, err := io.Copy(dst, src)
```

`io.Copy` — рабочая лошадка Go I/O. Использует буфер 32KB по умолчанию.

**C#**:
```csharp
await source.CopyToAsync(destination);
// или с указанием размера буфера
await source.CopyToAsync(destination, bufferSize: 81920);
```

**Go**:
```go
// Стандартный буфер 32KB
io.Copy(dst, src)

// Свой буфер
buf := make([]byte, 64*1024) // 64KB
io.CopyBuffer(dst, src, buf)

// Копирование ровно N байт
io.CopyN(dst, src, 1024) // ровно 1024 байта
```

**Оптимизация**: если `src` реализует `io.WriterTo` или `dst` реализует `io.ReaderFrom`, `io.Copy` вызывает их напрямую, минуя промежуточный буфер. Например, `*os.File` реализует `ReadFrom` через `sendfile` syscall — копирование файлов без выхода из kernel space.

```go
// Под капотом io.Copy проверяет:
// 1. dst.(io.ReaderFrom) → dst.ReadFrom(src) — zero-copy если возможно
// 2. src.(io.WriterTo) → src.WriteTo(dst) — прямая запись
// 3. Fallback: буфер 32KB + цикл Read/Write
```

### io.TeeReader: чтение с дублированием

```go
// Читаем body HTTP-ответа и параллельно считаем хеш
resp, _ := http.Get("https://example.com/file.tar.gz")
defer resp.Body.Close()

h := sha256.New()
body := io.TeeReader(resp.Body, h) // каждый Read из body дублируется в h

// Сохраняем файл — данные ОДНОВРЕМЕННО пишутся в хеш
f, _ := os.Create("file.tar.gz")
defer f.Close()
io.Copy(f, body)

fmt.Printf("SHA-256: %x\n", h.Sum(nil))
```

**C# аналог** потребовал бы `CryptoStream` или ручного дублирования:

```csharp
using var sha256 = SHA256.Create();
using var cryptoStream = new CryptoStream(fileStream, sha256, CryptoStreamMode.Write);
await responseStream.CopyToAsync(cryptoStream);
byte[] hash = sha256.Hash;
```

### io.MultiWriter: запись в несколько потоков

```go
// Логируем в файл и в stdout одновременно
logFile, _ := os.Create("app.log")
defer logFile.Close()

multi := io.MultiWriter(os.Stdout, logFile)
fmt.Fprintln(multi, "сообщение идёт в оба места")

// Более сложный пример: файл + хеш + счётчик байт
h := sha256.New()
counter := &CountWriter{}
w := io.MultiWriter(f, h, counter)
io.Copy(w, src) // данные пишутся во все три Writer
```

### io.MultiReader: последовательное чтение

```go
// Конкатенация нескольких источников
header := strings.NewReader("HEADER\n")
body := bytes.NewReader(bodyData)
footer := strings.NewReader("\nFOOTER")

combined := io.MultiReader(header, body, footer)
io.Copy(os.Stdout, combined) // читает последовательно: header → body → footer
```

### io.Pipe: синхронный канал между Reader и Writer

```go
// io.Pipe создаёт пару (Reader, Writer) — запись в PipeWriter
// блокируется до чтения из PipeReader. Горутино-безопасен.

pr, pw := io.Pipe()

// Горутина-писатель
go func() {
    defer pw.Close()
    json.NewEncoder(pw).Encode(largeData) // пишем JSON прямо в pipe
}()

// Горутина-читатель (или основная горутина)
req, _ := http.NewRequest("POST", url, pr) // pipe как body запроса
resp, _ := http.DefaultClient.Do(req)
```

> 💡 **Для C# разработчиков**: `io.Pipe` — аналог `System.IO.Pipelines` (`PipeReader`/`PipeWriter`), но проще. Нет back-pressure и memory pooling, зато нулевая церемония: создал пару, передал в горутины, готово.

**Типичные сценарии для io.Pipe:**
- Потоковая отправка JSON/XML по HTTP без буферизации в памяти
- Трансформация данных на лету между горутинами
- Тестирование: имитация потокового ввода

---

## io.LimitReader и io.SectionReader

### LimitReader: защита от бесконечного чтения

```go
// Ограничиваем чтение тела запроса до 1MB
// Защита от атак с огромным body
body := io.LimitReader(r.Body, 1<<20) // 1MB
data, err := io.ReadAll(body)
```

**C# аналог**:
```csharp
// В ASP.NET Core — через конфигурацию
services.Configure<KestrelServerOptions>(options =>
{
    options.Limits.MaxRequestBodySize = 1_048_576; // 1MB
});
```

В Go защита — явная и на уровне I/O, а не конфигурации фреймворка.

### SectionReader: чтение фрагмента

```go
// Чтение 100 байт начиная с позиции 500
// Полезно для range-запросов, работы с архивами
section := io.NewSectionReader(file, 500, 100)
data, _ := io.ReadAll(section) // ровно 100 байт (или меньше, если файл короче)
```

---

## bufio: буферизированный I/O

Прямое использование `io.Reader.Read` неэффективно для мелких чтений — каждый вызов может приводить к syscall. `bufio` добавляет буфер, уменьшая количество системных вызовов.

### bufio.Reader

```go
// Оборачиваем любой io.Reader в буферизированный
br := bufio.NewReader(file)           // буфер 4096 байт по умолчанию
br = bufio.NewReaderSize(file, 64*1024) // буфер 64KB

// Методы чтения
line, err := br.ReadString('\n') // до разделителя (включая его)
b, err := br.ReadByte()          // один байт
bytes, err := br.ReadBytes('\n') // []byte до разделителя
n := br.Buffered()               // сколько байт в буфере
_ = br.UnreadByte()              // вернуть байт в буфер
data, _ := br.Peek(10)           // подсмотреть 10 байт, не продвигая позицию
```

### bufio.Scanner: построчное чтение

```go
// Чтение файла построчно — идиоматичный Go
scanner := bufio.NewScanner(file)
for scanner.Scan() {
    line := scanner.Text() // строка без \n
    fmt.Println(line)
}
if err := scanner.Err(); err != nil {
    log.Fatal(err)
}
```

**C# аналог**:
```csharp
// StreamReader.ReadLine()
using var reader = new StreamReader(file);
while (reader.ReadLine() is { } line)
{
    Console.WriteLine(line);
}
```

**Настройка Scanner**: по умолчанию максимальная длина строки — 64KB. Для больших строк:

```go
scanner := bufio.NewScanner(file)
scanner.Buffer(make([]byte, 0), 10*1024*1024) // до 10MB на строку
```

**Пользовательские split-функции**:

```go
// Встроенные: ScanLines, ScanWords, ScanBytes, ScanRunes

// Чтение по словам
scanner := bufio.NewScanner(strings.NewReader("hello world foo"))
scanner.Split(bufio.ScanWords)
for scanner.Scan() {
    fmt.Println(scanner.Text()) // "hello", "world", "foo"
}

// Пользовательский split: чтение записей, разделённых \0
scanner.Split(func(data []byte, atEOF bool) (advance int, token []byte, err error) {
    if i := bytes.IndexByte(data, 0); i >= 0 {
        return i + 1, data[:i], nil
    }
    if atEOF && len(data) > 0 {
        return len(data), data, nil
    }
    return 0, nil, nil // запросить больше данных
})
```

### bufio.Writer

```go
bw := bufio.NewWriter(file)
defer bw.Flush() // обязательно: без Flush данные останутся в буфере

bw.WriteString("строка\n")
bw.Write([]byte{0x01, 0x02, 0x03})
bw.WriteByte('\n')
```

> 💡 **Для C# разработчиков**: `bufio.Writer` — аналог `BufferedStream`, но с важным отличием: `Flush()` надо вызывать **явно**. В C# `using` + `Dispose` обычно делают flush автоматически. В Go `defer bw.Flush()` — обязательный паттерн.

---

## Практические паттерны

### Паттерн 1: обёртка-декоратор (Counting Writer)

```go
// Считаем количество записанных байт
type CountWriter struct {
    W     io.Writer
    Count int64
}

func (cw *CountWriter) Write(p []byte) (int, error) {
    n, err := cw.W.Write(p)
    cw.Count += int64(n)
    return n, err
}

// Использование
cw := &CountWriter{W: file}
io.Copy(cw, src)
fmt.Printf("Записано: %d байт\n", cw.Count)
```

**C# аналог** — наследование от `Stream` (переопределить ~5 методов + свойства):

```csharp
class CountingStream : Stream
{
    private readonly Stream _inner;
    public long BytesWritten { get; private set; }

    public override void Write(byte[] buffer, int offset, int count)
    {
        _inner.Write(buffer, offset, count);
        BytesWritten += count;
    }

    // + CanRead, CanWrite, CanSeek, Length, Position, Flush, Read, Seek...
}
```

В Go декоратор — **3 строки кода**. В C# — целый класс с десятком обязательных переопределений.

### Паттерн 2: Progress Reader

```go
// Отображение прогресса загрузки
type ProgressReader struct {
    R         io.Reader
    Total     int64
    Current   int64
    OnProgress func(current, total int64)
}

func (pr *ProgressReader) Read(p []byte) (int, error) {
    n, err := pr.R.Read(p)
    pr.Current += int64(n)
    if pr.OnProgress != nil {
        pr.OnProgress(pr.Current, pr.Total)
    }
    return n, err
}

// Использование: загрузка файла с прогрессом
resp, _ := http.Get(url)
defer resp.Body.Close()

pr := &ProgressReader{
    R:     resp.Body,
    Total: resp.ContentLength,
    OnProgress: func(current, total int64) {
        fmt.Printf("\r%d / %d (%.1f%%)", current, total, float64(current)/float64(total)*100)
    },
}
io.Copy(file, pr)
```

### Паттерн 3: потоковый JSON без загрузки в память

```go
// ❌ Загрузка всего JSON в память
data, _ := io.ReadAll(resp.Body) // весь файл в RAM
var users []User
json.Unmarshal(data, &users)

// ✅ Потоковый декодер: читает и парсит по одному объекту
dec := json.NewDecoder(resp.Body)

// Пропускаем начало массива '['
dec.Token()

for dec.More() {
    var user User
    if err := dec.Decode(&user); err != nil {
        return err
    }
    processUser(user) // обрабатываем по одному, не держим весь массив
}
```

**C# аналог** — `System.Text.Json.Utf8JsonReader` или `JsonSerializer.DeserializeAsyncEnumerable`:

```csharp
// .NET 6+: потоковая десериализация
await foreach (var user in JsonSerializer.DeserializeAsyncEnumerable<User>(stream))
{
    ProcessUser(user);
}
```

### Паттерн 4: потоковая запись JSON

```go
// Кодируем JSON прямо в Writer, без промежуточного []byte
enc := json.NewEncoder(w) // w — любой io.Writer: файл, HTTP response, pipe
enc.SetIndent("", "  ")

for _, user := range users {
    if err := enc.Encode(user); err != nil {
        return err
    }
}
```

### Паттерн 5: HTTP response как io.Writer

```go
func downloadHandler(w http.ResponseWriter, r *http.Request) {
    file, _ := os.Open("report.csv")
    defer file.Close()

    w.Header().Set("Content-Type", "text/csv")
    w.Header().Set("Content-Disposition", "attachment; filename=report.csv")

    // Файл → HTTP response без буферизации в памяти
    io.Copy(w, file) // http.ResponseWriter реализует io.Writer
}
```

### Паттерн 6: io.Pipe для потоковой отправки

```go
// Отправляем большой JSON по HTTP без сериализации в []byte
func sendLargePayload(ctx context.Context, url string, data any) error {
    pr, pw := io.Pipe()

    go func() {
        defer pw.Close()
        // Если Encode вернёт ошибку, pw.Close закроет pipe
        // и http.Client получит ошибку чтения из pr
        if err := json.NewEncoder(pw).Encode(data); err != nil {
            pw.CloseWithError(err) // передаём ошибку читателю
        }
    }()

    req, err := http.NewRequestWithContext(ctx, "POST", url, pr)
    if err != nil {
        return err
    }
    req.Header.Set("Content-Type", "application/json")

    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return err
    }
    defer resp.Body.Close()

    if resp.StatusCode >= 400 {
        body, _ := io.ReadAll(resp.Body)
        return fmt.Errorf("HTTP %d: %s", resp.StatusCode, body)
    }
    return nil
}
```

---

## strings, bytes, os: стандартные реализации

### Создание Reader из данных в памяти

```go
// Из строки
r := strings.NewReader("hello, world")

// Из байтового слайса
r := bytes.NewReader(data)

// Из буфера (можно и читать, и писать)
var buf bytes.Buffer
buf.WriteString("hello")
r := &buf // *bytes.Buffer реализует и Reader, и Writer
```

### io.ReadAll: чтение всего содержимого

```go
// Осторожно: загружает ВЕСЬ контент в память
data, err := io.ReadAll(reader)
```

> 💡 **Для C# разработчиков**: `io.ReadAll` — аналог `StreamReader.ReadToEnd()` или `BinaryReader.ReadBytes()`. Используйте только когда уверены в размере данных. Для больших файлов — `io.Copy` или `bufio.Scanner`.

### io.NopCloser: добавление Closer к Reader

```go
// Оборачиваем io.Reader в io.ReadCloser с пустым Close()
// Полезно для тестов и адаптации интерфейсов
rc := io.NopCloser(strings.NewReader("test data"))
defer rc.Close() // ничего не делает, но удовлетворяет интерфейс
```

---

## Написание своих Reader и Writer

### Правила реализации

```go
// Reader: обязательные контрактные условия
type MyReader struct { /* ... */ }

func (r *MyReader) Read(p []byte) (n int, err error) {
    if len(p) == 0 {
        return 0, nil // пустой буфер — не ошибка
    }
    // 1. Читаем данные в p
    // 2. Возвращаем n > 0 если что-то прочитали
    // 3. Возвращаем io.EOF когда данных больше нет
    // 4. Можно вернуть n > 0 И io.EOF одновременно
    // 5. НЕ возвращаем io.EOF преждевременно
    return n, err
}

// Writer: обязательные контрактные условия
type MyWriter struct { /* ... */ }

func (w *MyWriter) Write(p []byte) (n int, err error) {
    // 1. Пишем данные из p
    // 2. Если n < len(p) — ОБЯЗАНЫ вернуть err != nil
    // 3. НЕ модифицируем p (даже временно)
    return n, err
}
```

### Пример: Reader с ограничением скорости

```go
// RateLimitedReader ограничивает скорость чтения
type RateLimitedReader struct {
    R         io.Reader
    BytesPerSec int
    last      time.Time
    read      int
}

func (r *RateLimitedReader) Read(p []byte) (int, error) {
    now := time.Now()

    // Если с прошлого вызова прошло меньше секунды и лимит достигнут — ждём
    if !r.last.IsZero() && now.Sub(r.last) < time.Second && r.read >= r.BytesPerSec {
        time.Sleep(time.Second - now.Sub(r.last))
        r.read = 0
        r.last = time.Now()
    }
    if r.last.IsZero() || now.Sub(r.last) >= time.Second {
        r.read = 0
        r.last = now
    }

    // Ограничиваем размер чтения оставшимся лимитом
    limit := r.BytesPerSec - r.read
    if limit <= 0 {
        limit = r.BytesPerSec
    }
    if len(p) > limit {
        p = p[:limit]
    }

    n, err := r.R.Read(p)
    r.read += n
    return n, err
}
```

---

## Типичные ошибки C# разработчиков

### 1. Забытый defer Close

```go
// ❌ Утечка файлового дескриптора
func readFile(path string) ([]byte, error) {
    f, err := os.Open(path)
    if err != nil {
        return nil, err
    }
    // Если ReadAll вернёт ошибку — f не закроется
    return io.ReadAll(f)
}

// ✅ defer сразу после проверки ошибки
func readFile(path string) ([]byte, error) {
    f, err := os.Open(path)
    if err != nil {
        return nil, err
    }
    defer f.Close()
    return io.ReadAll(f)
}
```

> 💡 **Для C# разработчиков**: `defer f.Close()` — аналог `using`. Разница: `defer` выполняется при выходе из функции, а не при выходе из блока. Нет аналога `using` с блочным scope — если нужно закрыть ресурс до конца функции, вызывайте `Close()` явно.

### 2. Игнорирование n при Read

```go
// ❌ Обработка полного буфера, хотя прочитано меньше
n, _ := reader.Read(buf)
process(buf) // buf может быть заполнен не полностью!

// ✅ Обрабатываем ровно прочитанное
n, err := reader.Read(buf)
process(buf[:n])
```

### 3. Использование ReadAll для больших файлов

```go
// ❌ 2GB файл загружается целиком в память
data, _ := io.ReadAll(hugeFile)

// ✅ Потоковая обработка
scanner := bufio.NewScanner(hugeFile)
for scanner.Scan() {
    processLine(scanner.Text())
}
```

### 4. Забытый Flush для bufio.Writer

```go
// ❌ Данные остались в буфере — файл пустой или неполный
bw := bufio.NewWriter(file)
bw.WriteString("важные данные")
file.Close()

// ✅ Flush перед закрытием
bw := bufio.NewWriter(file)
bw.WriteString("важные данные")
bw.Flush() // записываем буфер на диск
file.Close()

// ✅✅ Идиоматично: defer в правильном порядке
bw := bufio.NewWriter(file)
defer func() {
    bw.Flush()
    file.Close()
}()
```

### 5. Повторное чтение из Reader

```go
// ❌ Reader — одноразовый, второе чтение вернёт пустоту
data1, _ := io.ReadAll(resp.Body) // прочитали всё
data2, _ := io.ReadAll(resp.Body) // data2 == []byte{} — пусто!

// ✅ Вариант 1: сохранить в буфер и создать новый Reader
data, _ := io.ReadAll(resp.Body)
r1 := bytes.NewReader(data)
r2 := bytes.NewReader(data)

// ✅ Вариант 2: TeeReader для одновременного чтения и сохранения
var buf bytes.Buffer
tee := io.TeeReader(resp.Body, &buf)
process(tee)               // основная обработка
secondPass(bytes.NewReader(buf.Bytes())) // повторное чтение из буфера

// ✅ Вариант 3: io.Seeker (если поддерживается)
file.Seek(0, io.SeekStart) // перемотка в начало — работает для файлов
```

> 💡 **Для C# разработчиков**: в C# `Stream.Position = 0` перематывает поток (если `CanSeek == true`). В Go `io.Reader` — **forward-only** по умолчанию. Позиционирование — отдельный интерфейс `io.Seeker`, и не все Reader его реализуют.

---

## Производительность

### Аллокации при работе с io

```go
// ❌ Аллокация буфера на каждый вызов
func processChunks(r io.Reader) error {
    for {
        buf := make([]byte, 4096) // аллокация на каждой итерации
        n, err := r.Read(buf)
        if n > 0 {
            process(buf[:n])
        }
        if err != nil {
            if err == io.EOF { return nil }
            return err
        }
    }
}

// ✅ Один буфер на весь цикл
func processChunks(r io.Reader) error {
    buf := make([]byte, 4096) // одна аллокация
    for {
        n, err := r.Read(buf)
        if n > 0 {
            process(buf[:n])
        }
        if err != nil {
            if err == io.EOF { return nil }
            return err
        }
    }
}
```

### sync.Pool для буферов

```go
var bufPool = sync.Pool{
    New: func() any {
        buf := make([]byte, 32*1024)
        return &buf
    },
}

func copyWithPool(dst io.Writer, src io.Reader) (int64, error) {
    bufp := bufPool.Get().(*[]byte)
    defer bufPool.Put(bufp)
    return io.CopyBuffer(dst, src, *bufp)
}
```

### Бенчмарк: буферизированное vs прямое чтение

```go
func BenchmarkDirectRead(b *testing.B) {
    data := bytes.Repeat([]byte("a"), 1<<20) // 1MB
    for b.Loop() {
        r := bytes.NewReader(data)
        buf := make([]byte, 1) // побайтовое чтение
        for {
            _, err := r.Read(buf)
            if err == io.EOF { break }
        }
    }
}

func BenchmarkBufioRead(b *testing.B) {
    data := bytes.Repeat([]byte("a"), 1<<20)
    for b.Loop() {
        r := bufio.NewReader(bytes.NewReader(data))
        for {
            _, err := r.ReadByte()
            if err == io.EOF { break }
        }
    }
}

// Результат (типичный):
// BenchmarkDirectRead-8    38    31_000_000 ns/op    0 B/op    0 allocs/op
// BenchmarkBufioRead-8    610     1_900_000 ns/op    4096 B/op    1 allocs/op
//
// bufio быстрее в ~16x при побайтовом чтении за счёт уменьшения
// количества вызовов нижележащего Reader
```

### Таблица: когда какой подход

| Сценарий | Подход | Почему |
|----------|--------|--------|
| Побайтовое чтение | `bufio.Reader` | Минимизация syscall |
| Построчное чтение | `bufio.Scanner` | Удобный API, автоматическое разбиение |
| Копирование файлов | `io.Copy` | Zero-copy через sendfile |
| Чтение маленьких файлов (<1MB) | `os.ReadFile` | Один вызов, простой код |
| Потоковый JSON | `json.NewDecoder` | Не загружает всё в память |
| Мелкие записи | `bufio.Writer` | Группировка в большие write |
| Горячий путь, высокий RPS | `sync.Pool` для буферов | Уменьшение GC pressure |

---

## Практический пример: обработка CSV с прогрессом

Комплексный пример, объединяющий несколько паттернов:

```go
package main

import (
    "bufio"
    "encoding/csv"
    "fmt"
    "io"
    "os"
    "strconv"
)

// CountReader считает прочитанные байты
type CountReader struct {
    R     io.Reader
    Count int64
}

func (cr *CountReader) Read(p []byte) (int, error) {
    n, err := cr.R.Read(p)
    cr.Count += int64(n)
    return n, err
}

func processLargeCSV(path string) error {
    f, err := os.Open(path)
    if err != nil {
        return fmt.Errorf("открытие файла: %w", err)
    }
    defer f.Close()

    // Размер файла для прогресса
    stat, err := f.Stat()
    if err != nil {
        return fmt.Errorf("stat: %w", err)
    }
    total := stat.Size()

    // Цепочка: File → CountReader → bufio → csv.Reader
    cr := &CountReader{R: f}
    br := bufio.NewReaderSize(cr, 64*1024) // буфер 64KB
    csvr := csv.NewReader(br)

    // Пропускаем заголовок
    header, err := csvr.Read()
    if err != nil {
        return fmt.Errorf("заголовок: %w", err)
    }
    fmt.Printf("Колонки: %v\n", header)

    var (
        lineCount int
        sumAmount float64
    )

    for {
        record, err := csvr.Read()
        if err == io.EOF {
            break
        }
        if err != nil {
            return fmt.Errorf("строка %d: %w", lineCount+1, err)
        }

        lineCount++

        // Обработка: предположим, сумма в 3-й колонке
        if len(record) > 2 {
            if amount, err := strconv.ParseFloat(record[2], 64); err == nil {
                sumAmount += amount
            }
        }

        // Прогресс каждые 100_000 строк
        if lineCount%100_000 == 0 {
            pct := float64(cr.Count) / float64(total) * 100
            fmt.Printf("\r  Обработано: %d строк (%.1f%%)", lineCount, pct)
        }
    }

    fmt.Printf("\r  Итого: %d строк, сумма: %.2f\n", lineCount, sumAmount)
    return nil
}
```

---

## Шпаргалка: ключевые функции io

| Функция | Описание | Аналог в C# |
|---------|----------|--------------|
| `io.Copy(dst, src)` | Копирование потока | `Stream.CopyTo()` |
| `io.CopyN(dst, src, n)` | Копирование N байт | `Read` в цикле до N |
| `io.CopyBuffer(dst, src, buf)` | Копирование с указанным буфером | `CopyTo(dst, bufferSize)` |
| `io.ReadAll(r)` | Чтение всего | `StreamReader.ReadToEnd()` |
| `io.ReadFull(r, buf)` | Чтение ровно len(buf) байт | `BinaryReader.ReadBytes()` |
| `io.WriteString(w, s)` | Запись строки | `StreamWriter.Write(s)` |
| `io.LimitReader(r, n)` | Ограничение размера | нет прямого аналога |
| `io.TeeReader(r, w)` | Дублирование чтения | `CryptoStream` (частично) |
| `io.MultiReader(r...)` | Конкатенация Reader | `ConcatStream` (нет в stdlib) |
| `io.MultiWriter(w...)` | Разветвление Writer | нет прямого аналога |
| `io.Pipe()` | In-memory pipe | `System.IO.Pipelines` |
| `io.NopCloser(r)` | Reader → ReadCloser | нет прямого аналога |
| `io.Discard` | /dev/null Writer | `Stream.Null` |

---

## Итоги

Модель I/O в Go построена на принципе **минимальных интерфейсов**:

| Принцип | C# | Go |
|---------|----|----|
| Базовая единица | `Stream` (монолит) | `io.Reader` / `io.Writer` (атомы) |
| Расширение | Наследование + override | Композиция обёрток |
| Декорирование | `DelegatingStream` + 10 методов | Обёртка + 1 метод |
| Буферизация | `BufferedStream` | `bufio.Reader` / `bufio.Writer` |
| Закрытие | `IDisposable` + `using` | `io.Closer` + `defer` |

Главное преимущество Go подхода — **лёгкость создания обёрток**. Реализация одного метода `Read` или `Write` даёт совместимость со всей экосистемой: `io.Copy`, `json.Decoder`, `gzip.Writer`, `http.ResponseWriter` и сотнями других.

Главный риск — нарушение контракта: забыть обработать `n > 0` при `err != nil`, забыть `Flush()`, забыть `defer Close()`. В C# многие из этих проблем решаются `using` и `Stream.Dispose()`, но в Go ответственность явно на разработчике.
