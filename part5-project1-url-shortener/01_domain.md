# 1. Доменная модель и сервисный слой

## Содержание

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Анализ требований](#%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7-%D1%82%D1%80%D0%B5%D0%B1%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B9)
- [Доменная модель](#%D0%B4%D0%BE%D0%BC%D0%B5%D0%BD%D0%BD%D0%B0%D1%8F-%D0%BC%D0%BE%D0%B4%D0%B5%D0%BB%D1%8C)
  - [C# подход](#c-%D0%BF%D0%BE%D0%B4%D1%85%D0%BE%D0%B4)
  - [Go подход (идиоматично)](#go-%D0%BF%D0%BE%D0%B4%D1%85%D0%BE%D0%B4-%D0%B8%D0%B4%D0%B8%D0%BE%D0%BC%D0%B0%D1%82%D0%B8%D1%87%D0%BD%D0%BE)
- [Кастомные ошибки](#%D0%BA%D0%B0%D1%81%D1%82%D0%BE%D0%BC%D0%BD%D1%8B%D0%B5-%D0%BE%D1%88%D0%B8%D0%B1%D0%BA%D0%B8)
  - [C# подход](#c-%D0%BF%D0%BE%D0%B4%D1%85%D0%BE%D0%B4-1)
  - [Go подход](#go-%D0%BF%D0%BE%D0%B4%D1%85%D0%BE%D0%B4)
- [Интерфейс репозитория](#%D0%B8%D0%BD%D1%82%D0%B5%D1%80%D1%84%D0%B5%D0%B9%D1%81-%D1%80%D0%B5%D0%BF%D0%BE%D0%B7%D0%B8%D1%82%D0%BE%D1%80%D0%B8%D1%8F)
  - [C# подход](#c-%D0%BF%D0%BE%D0%B4%D1%85%D0%BE%D0%B4-2)
  - [Go подход](#go-%D0%BF%D0%BE%D0%B4%D1%85%D0%BE%D0%B4-1)
- [Алгоритм генерации кода (Base62)](#%D0%B0%D0%BB%D0%B3%D0%BE%D1%80%D0%B8%D1%82%D0%BC-%D0%B3%D0%B5%D0%BD%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D0%B8-%D0%BA%D0%BE%D0%B4%D0%B0-base62)
  - [C# подход](#c-%D0%BF%D0%BE%D0%B4%D1%85%D0%BE%D0%B4-3)
  - [Go подход](#go-%D0%BF%D0%BE%D0%B4%D1%85%D0%BE%D0%B4-2)
- [Сервисный слой](#%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D0%BD%D1%8B%D0%B9-%D1%81%D0%BB%D0%BE%D0%B9)
  - [C# подход](#c-%D0%BF%D0%BE%D0%B4%D1%85%D0%BE%D0%B4-4)
  - [Go подход](#go-%D0%BF%D0%BE%D0%B4%D1%85%D0%BE%D0%B4-3)
- [Точка входа: main.go](#%D1%82%D0%BE%D1%87%D0%BA%D0%B0-%D0%B2%D1%85%D0%BE%D0%B4%D0%B0-maingo)
- [Сравнительная таблица](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F-%D1%82%D0%B0%D0%B1%D0%BB%D0%B8%D1%86%D0%B0)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

---

## Анализ требований

Перед написанием кода — как в C#, так и в Go — полезно зафиксировать,
**что именно** наш сервис должен делать.

**Операции**:

1. `CreateURL(originalURL string) → (URL, error)` — принять длинный URL,
   сгенерировать уникальный код, сохранить и вернуть запись
2. `GetByCode(code string) → (URL, error)` — найти запись по коду (для редиректа)
3. `RecordClick(code string) → error` — атомарно инкрементировать счётчик переходов
4. `GetStats(code string) → (URLStats, error)` — вернуть статистику по коду

**Ограничения**:
- Код должен быть уникальным, длиной 6 символов, Base62 (a-z, A-Z, 0-9)
- Длинный URL должен быть валидным (схема http/https)
- Операция редиректа должна быть быстрой — кэшируем в Redis

> 💡 **Для C# разработчиков**: В C# мы обычно начинаем с написания интерфейсов
> (`IUrlRepository`, `IUrlService`) и классов. В Go подход похожий, но интерфейсы
> **маленькие** и определяются в том пакете, который их **использует** (не реализует).

---

## Доменная модель

### C# подход

```csharp
// Models/Url.cs
public class Url
{
    public Guid Id { get; init; }
    public string OriginalUrl { get; init; } = string.Empty;
    public string Code { get; init; } = string.Empty;
    public DateTime CreatedAt { get; init; }
    public long ClickCount { get; set; }
}

public class UrlStats
{
    public string Code { get; init; } = string.Empty;
    public string OriginalUrl { get; init; } = string.Empty;
    public long ClickCount { get; init; }
    public DateTime CreatedAt { get; init; }
}
```

### Go подход (идиоматично)

```go
// internal/domain/url.go
package domain

import "time"

// URL — доменная модель записи сокращённого адреса.
// Экспортированные поля (с заглавной буквы) доступны из других пакетов.
type URL struct {
    ID          int64     // суррогатный ключ из БД
    Code        string    // уникальный 6-символьный код (Base62)
    OriginalURL string    // исходный длинный URL
    ClickCount  int64     // счётчик переходов
    CreatedAt   time.Time // время создания
}

// URLStats — DTO для ответа на запрос статистики.
// В Go нет отдельного понятия "DTO" — обычный struct.
type URLStats struct {
    Code        string
    OriginalURL string
    ClickCount  int64
    CreatedAt   time.Time
}
```

**Ключевые отличия от C#**:

| Аспект | C# | Go |
|--------|----|----|
| Определение | `class Url { }` | `type URL struct { }` |
| Поля | `public string Code { get; init; }` | `Code string` |
| Иммутабельность | `init` accessor | Нет встроенной — передаём по значению или используем конструктор |
| Null-безопасность | `string?` для nullable | Используем указатель `*URL` только когда нужно |
| Наследование | Можно наследовать | Нет наследования — только embedding |

> ⚠️ **Частая ошибка C# разработчиков**: использовать `*URL` везде по аналогии
> с объектными ссылками C#. В Go передача struct по значению (копирование) — норма
> для небольших структур. Указатель нужен когда: структура большая (>64 байт),
> нужно изменить значение, или nil имеет смысловую нагрузку.

---

## Кастомные ошибки

### C# подход

```csharp
// Exceptions/UrlNotFoundException.cs
public class UrlNotFoundException : Exception
{
    public string Code { get; }
    public UrlNotFoundException(string code)
        : base($"URL with code '{code}' not found")
    {
        Code = code;
    }
}

public class InvalidUrlException : Exception
{
    public InvalidUrlException(string message) : base(message) { }
}
```

### Go подход

```go
// internal/domain/errors.go
package domain

import (
    "errors"
    "fmt"
)

// Sentinel-ошибки — для проверки через errors.Is()
var (
    // ErrNotFound возвращается когда URL по коду не найден.
    ErrNotFound = errors.New("url not found")

    // ErrInvalidURL возвращается при невалидном исходном URL.
    ErrInvalidURL = errors.New("invalid url")

    // ErrCodeConflict возвращается при коллизии сгенерированного кода.
    ErrCodeConflict = errors.New("code conflict")
)

// NotFoundError — структурированная ошибка с дополнительным контекстом.
// Реализует интерфейс error через метод Error() string.
type NotFoundError struct {
    Code string
}

func (e *NotFoundError) Error() string {
    return fmt.Sprintf("url with code %q not found", e.Code)
}

// Unwrap позволяет errors.Is(err, ErrNotFound) работать через цепочку.
func (e *NotFoundError) Unwrap() error {
    return ErrNotFound
}

// Конструкторы-хелперы
func NewNotFoundError(code string) error {
    return &NotFoundError{Code: code}
}
```

**Использование в коде**:

```go
// Проверка типа ошибки (аналог catch (UrlNotFoundException))
err := service.GetByCode(code)
if errors.Is(err, domain.ErrNotFound) {
    // аналог catch (UrlNotFoundException)
    http.Error(w, "not found", http.StatusNotFound)
    return
}

// Извлечение деталей ошибки (аналог catch (UrlNotFoundException e) { e.Code })
var notFound *domain.NotFoundError
if errors.As(err, &notFound) {
    log.Printf("code %q не найден", notFound.Code)
}
```

> 💡 **Идиома Go**: В Go ошибки — это значения, а не исключения. Нет `try/catch`.
> `errors.Is` проверяет идентичность по цепочке `Unwrap()`.
> `errors.As` извлекает конкретный тип из цепочки — аналог `catch (MyException e)`.

---

## Интерфейс репозитория

> 💡 **Ключевая идиома**: В Go интерфейс определяется **там, где он используется**,
> а не там, где он реализован. `URLRepository` живёт в пакете `domain`, а его реализация —
> в `storage/postgres`. Это инверсия зависимостей без DI-фреймворка.

### C# подход

```csharp
// Repositories/IUrlRepository.cs
public interface IUrlRepository
{
    Task<Url?> GetByCodeAsync(string code, CancellationToken ct = default);
    Task<Url> CreateAsync(Url url, CancellationToken ct = default);
    Task IncrementClickCountAsync(string code, CancellationToken ct = default);
}
```

### Go подход

```go
// internal/domain/repository.go
package domain

import "context"

// URLRepository — интерфейс для работы с хранилищем URL.
// Маленький интерфейс (3 метода) — Go-идиома: "accept interfaces, return structs".
//
// context.Context передаётся первым параметром в каждый метод —
// стандарт Go для поддержки отмены, дедлайнов, трейсинга.
// Аналог CancellationToken в C#, но мощнее.
type URLRepository interface {
    // GetByCode возвращает URL по коду.
    // Возвращает ErrNotFound если запись не существует.
    GetByCode(ctx context.Context, code string) (URL, error)

    // Create сохраняет новую запись и возвращает её с заполненными ID и CreatedAt.
    Create(ctx context.Context, url URL) (URL, error)

    // IncrementClickCount атомарно увеличивает счётчик переходов.
    IncrementClickCount(ctx context.Context, code string) error
}

// Cache — интерфейс кэша (Redis).
// Намеренно отделён от URLRepository — single responsibility.
type Cache interface {
    // Get возвращает кэшированный original URL по коду.
    // Возвращает ErrNotFound если кэш-промах.
    Get(ctx context.Context, code string) (string, error)

    // Set кэширует запись (TTL задаётся реализацией).
    Set(ctx context.Context, code string, originalURL string) error

    // Delete инвалидирует запись в кэше.
    Delete(ctx context.Context, code string) error
}
```

**Сравнение с C#**:

| Аспект | C# | Go |
|--------|----|----|
| Определение | `interface IUrlRepository` | `type URLRepository interface` |
| Async | `Task<Url>` | Синхронный возврат — горутины управляют параллелизмом |
| Cancellation | `CancellationToken ct = default` | `context.Context` (первый аргумент) |
| Null | `Url?` | `(URL, error)` — явный error вместо null |
| Именование | `IUrlRepository` (с I-префиксом) | `URLRepository` (без префикса) |

> ⚠️ **Важно**: Go-интерфейсы реализуются **неявно** (duck typing). Если struct
> имеет все методы интерфейса — она его реализует автоматически. Не нужно писать
> `implements IUrlRepository`. Это позволяет PostgreSQL-репозиторий подменить
> in-memory реализацией в тестах без изменений в коде клиента.

---

## Алгоритм генерации кода (Base62)

Нам нужна функция, которая генерирует случайный 6-символьный код из алфавита
`[0-9a-zA-Z]` (62 символа). 62^6 ≈ 56 миллиардов уникальных кодов.

### C# подход

```csharp
// Services/CodeGenerator.cs
public static class CodeGenerator
{
    private const string Alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    private const int CodeLength = 6;

    public static string Generate()
    {
        var bytes = RandomNumberGenerator.GetBytes(CodeLength);
        var sb = new StringBuilder(CodeLength);
        foreach (var b in bytes)
            sb.Append(Alphabet[b % Alphabet.Length]);
        return sb.ToString();
    }
}
```

### Go подход

```go
// internal/domain/codegen.go
package domain

import (
    "crypto/rand"
    "math/big"
)

const (
    alphabet   = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    codeLength = 6
)

// GenerateCode генерирует криптографически безопасный Base62 код длиной 6 символов.
// Использует crypto/rand (аналог RandomNumberGenerator в C#), не math/rand.
func GenerateCode() (string, error) {
    result := make([]byte, codeLength)
    alphabetLen := big.NewInt(int64(len(alphabet)))

    for i := range result {
        // crypto/rand.Int возвращает случайное число в диапазоне [0, alphabetLen)
        n, err := rand.Int(rand.Reader, alphabetLen)
        if err != nil {
            // В Go ошибки не игнорируются — возвращаем вызывающему
            return "", fmt.Errorf("генерация кода: %w", err)
        }
        result[i] = alphabet[n.Int64()]
    }

    return string(result), nil
}
```

> ⚠️ **Ошибка C# разработчиков**: использовать `math/rand` вместо `crypto/rand`
> для генерации кодов. `math/rand` предсказуем и не подходит для чего-либо, что
> должно быть уникальным или безопасным. Аналог ошибки — использовать `new Random()`
> вместо `RandomNumberGenerator` в C#.

**Обработка коллизий**:

```go
// В сервисном слое — повторная попытка при коллизии
func (s *URLService) generateUniqueCode(ctx context.Context) (string, error) {
    const maxAttempts = 5

    for attempt := range maxAttempts { // Go 1.22+: range по int
        code, err := GenerateCode()
        if err != nil {
            return "", err
        }

        // Проверяем что код свободен
        _, err = s.repo.GetByCode(ctx, code)
        if errors.Is(err, ErrNotFound) {
            return code, nil // код свободен — используем
        }
        if err != nil {
            return "", fmt.Errorf("проверка кода (попытка %d): %w", attempt+1, err)
        }
        // Если err == nil — код занят, пробуем ещё раз
    }

    return "", fmt.Errorf("не удалось сгенерировать уникальный код за %d попыток", maxAttempts)
}
```

> 💡 **Go 1.22+**: `for attempt := range maxAttempts` — новый синтаксис для итерации
> по целому числу. Раньше писали `for attempt := 0; attempt < maxAttempts; attempt++`.

---

## Сервисный слой

### C# подход

```csharp
// Services/UrlService.cs
public class UrlService : IUrlService
{
    private readonly IUrlRepository _repository;
    private readonly ILogger<UrlService> _logger;

    public UrlService(IUrlRepository repository, ILogger<UrlService> logger)
    {
        _repository = repository;
        _logger = logger;
    }

    public async Task<Url> CreateAsync(string originalUrl, CancellationToken ct)
    {
        if (!Uri.TryCreate(originalUrl, UriKind.Absolute, out var uri) ||
            (uri.Scheme != "http" && uri.Scheme != "https"))
        {
            throw new InvalidUrlException($"Invalid URL: {originalUrl}");
        }

        var code = await GenerateUniqueCodeAsync(ct);
        var url = new Url { OriginalUrl = originalUrl, Code = code, CreatedAt = DateTime.UtcNow };
        return await _repository.CreateAsync(url, ct);
    }
}
```

### Go подход

```go
// internal/domain/service.go
package domain

import (
    "context"
    "fmt"
    "net/url"
    "time"
)

// URLService реализует бизнес-логику работы с URL.
// Зависимости передаются явно через поля структуры — нет DI-контейнера.
type URLService struct {
    repo  URLRepository // интерфейс — легко подменить в тестах
    cache Cache         // интерфейс Redis-кэша
}

// NewURLService — конструктор (Go-идиома вместо dependency injection).
// Принимает интерфейсы, возвращает конкретный тип — "accept interfaces, return structs".
func NewURLService(repo URLRepository, cache Cache) *URLService {
    return &URLService{
        repo:  repo,
        cache: cache,
    }
}

// CreateURL валидирует URL, генерирует код и сохраняет запись.
func (s *URLService) CreateURL(ctx context.Context, originalURL string) (URL, error) {
    // Валидация входных данных
    if err := validateURL(originalURL); err != nil {
        return URL{}, err // ошибка оборачивается, не бросается
    }

    // Генерируем уникальный код
    code, err := s.generateUniqueCode(ctx)
    if err != nil {
        return URL{}, fmt.Errorf("создание URL: %w", err)
    }

    // Создаём доменную модель
    record := URL{
        Code:        code,
        OriginalURL: originalURL,
        CreatedAt:   time.Now().UTC(),
    }

    // Сохраняем в репозиторий
    saved, err := s.repo.Create(ctx, record)
    if err != nil {
        return URL{}, fmt.Errorf("сохранение URL: %w", err)
    }

    return saved, nil
}

// Redirect возвращает оригинальный URL по коду.
// Сначала проверяет кэш, при промахе — базу данных.
func (s *URLService) Redirect(ctx context.Context, code string) (string, error) {
    // Попытка получить из кэша
    originalURL, err := s.cache.Get(ctx, code)
    if err == nil {
        // Кэш-попадание — записываем клик асинхронно, не блокируя ответ
        go func() {
            // Создаём новый контекст т.к. родительский может закончиться
            if err := s.repo.IncrementClickCount(context.Background(), code); err != nil {
                // Логируем но не фейлим — статистика некритична
                _ = err // в реальном проекте: logger.Error("increment click", "err", err)
            }
        }()
        return originalURL, nil
    }

    // Кэш-промах — идём в БД
    record, err := s.repo.GetByCode(ctx, code)
    if err != nil {
        return "", err // ErrNotFound проброшен из репозитория
    }

    // Заполняем кэш асинхронно
    go func() {
        _ = s.cache.Set(context.Background(), code, record.OriginalURL)
    }()

    // Асинхронно инкрементируем клик
    go func() {
        _ = s.repo.IncrementClickCount(context.Background(), code)
    }()

    return record.OriginalURL, nil
}

// GetStats возвращает статистику переходов по коду.
func (s *URLService) GetStats(ctx context.Context, code string) (URLStats, error) {
    record, err := s.repo.GetByCode(ctx, code)
    if err != nil {
        return URLStats{}, err
    }

    return URLStats{
        Code:        record.Code,
        OriginalURL: record.OriginalURL,
        ClickCount:  record.ClickCount,
        CreatedAt:   record.CreatedAt,
    }, nil
}

// validateURL проверяет что URL валидный и использует http/https схему.
func validateURL(rawURL string) error {
    parsed, err := url.Parse(rawURL)
    if err != nil {
        return fmt.Errorf("%w: %s", ErrInvalidURL, err.Error())
    }
    if parsed.Scheme != "http" && parsed.Scheme != "https" {
        return fmt.Errorf("%w: схема должна быть http или https, получено %q",
            ErrInvalidURL, parsed.Scheme)
    }
    if parsed.Host == "" {
        return fmt.Errorf("%w: отсутствует хост", ErrInvalidURL)
    }
    return nil
}

// generateUniqueCode пытается сгенерировать свободный код до 5 раз.
func (s *URLService) generateUniqueCode(ctx context.Context) (string, error) {
    const maxAttempts = 5

    for attempt := range maxAttempts {
        code, err := GenerateCode()
        if err != nil {
            return "", fmt.Errorf("генерация кода (попытка %d): %w", attempt+1, err)
        }

        _, err = s.repo.GetByCode(ctx, code)
        if errors.Is(err, ErrNotFound) {
            return code, nil // код свободен
        }
        if err != nil {
            return "", fmt.Errorf("проверка уникальности кода: %w", err)
        }
        // err == nil означает что код уже занят — пробуем снова
    }

    return "", fmt.Errorf("не удалось сгенерировать уникальный код за %d попыток", maxAttempts)
}
```

> 💡 **Горутины в сервисном слое**: запись клика происходит асинхронно (`go func() {}`),
> что не блокирует ответ на редирект. В C# аналог — `Task.Run(() => ...)` без `await`.
> Важно: создаём `context.Background()` т.к. родительский контекст HTTP-запроса
> может завершиться до того, как горутина завершит работу.

---

## Точка входа: main.go

```go
// cmd/server/main.go
package main

import (
    "context"
    "log/slog"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "github.com/yourname/urlshortener/internal/domain"
    "github.com/yourname/urlshortener/internal/handler"
    "github.com/yourname/urlshortener/internal/storage/postgres"
    "github.com/yourname/urlshortener/internal/storage/redis"
)

func main() {
    // Структурированное логирование (Go 1.21+)
    // Аналог Serilog/NLog в C#, но из стандартной библиотеки
    logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
        Level: slog.LevelInfo,
    }))
    slog.SetDefault(logger)

    // Конфигурация из переменных окружения (аналог IConfiguration в C#)
    cfg := mustLoadConfig()

    // Инициализация PostgreSQL пула
    pool, err := postgres.NewPool(cfg.DatabaseURL)
    if err != nil {
        slog.Error("не удалось подключиться к PostgreSQL", "err", err)
        os.Exit(1)
    }
    defer pool.Close()

    // Инициализация Redis клиента
    redisClient, err := redis.NewClient(cfg.RedisURL)
    if err != nil {
        slog.Error("не удалось подключиться к Redis", "err", err)
        os.Exit(1)
    }
    defer redisClient.Close()

    // Сборка графа зависимостей вручную (нет DI-контейнера)
    // В C#: services.AddScoped<IUrlRepository, PostgresUrlRepository>();
    //        services.AddScoped<IUrlService, UrlService>();
    repo := postgres.NewURLRepository(pool)
    cache := redis.NewURLCache(redisClient)
    service := domain.NewURLService(repo, cache)

    // Инициализация HTTP роутера и хэндлеров (см. 03_http.md)
    router := handler.NewRouter(service, cfg)

    // Запуск сервера с graceful shutdown
    srv := &http.Server{
        Addr:         cfg.Addr,
        Handler:      router,
        ReadTimeout:  15 * time.Second,
        WriteTimeout: 15 * time.Second,
        IdleTimeout:  60 * time.Second,
    }

    // Ждём сигнала завершения в горутине
    go func() {
        slog.Info("сервер запущен", "addr", cfg.Addr)
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            slog.Error("ошибка сервера", "err", err)
            os.Exit(1)
        }
    }()

    // Graceful shutdown по SIGINT/SIGTERM
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    slog.Info("получен сигнал завершения, shutdown...")
    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := srv.Shutdown(ctx); err != nil {
        slog.Error("ошибка graceful shutdown", "err", err)
    }
    slog.Info("сервер остановлен")
}

// Config — конфигурация приложения из переменных окружения.
type Config struct {
    Addr        string // :8080
    DatabaseURL string // postgres://user:pass@host/db
    RedisURL    string // redis://localhost:6379
    BaseURL     string // http://localhost:8080 (для формирования короткой ссылки)
}

func mustLoadConfig() Config {
    cfg := Config{
        Addr:        getEnv("ADDR", ":8080"),
        DatabaseURL: getEnv("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/urlshortener"),
        RedisURL:    getEnv("REDIS_URL", "redis://localhost:6379"),
        BaseURL:     getEnv("BASE_URL", "http://localhost:8080"),
    }
    return cfg
}

func getEnv(key, defaultValue string) string {
    if v := os.Getenv(key); v != "" {
        return v
    }
    return defaultValue
}
```

> 💡 **Конфигурация в Go**: Нет `appsettings.json` и `IConfiguration`. Стандартный
> подход — переменные окружения через `os.Getenv`. Для production используют
> библиотеки вроде `github.com/caarlos0/env` для struct-тегов, но для простого
> проекта хватает `os.Getenv`.

---

## Сравнительная таблица

| Концепция | C# | Go |
|-----------|----|----|
| Доменная модель | `class Url` | `type URL struct` |
| Интерфейс | `interface IUrlRepository` | `type URLRepository interface` |
| Реализация | `: IUrlRepository` (явно) | Неявная (duck typing) |
| Конструктор | `public UrlService(IRepo r)` | `func NewURLService(r URLRepository)` |
| DI | `services.AddScoped<>()` | Ручная сборка в `main()` |
| Ошибки | `throw new UrlNotFoundException()` | `return URL{}, ErrNotFound` |
| Проверка ошибки | `catch (UrlNotFoundException e)` | `errors.Is(err, ErrNotFound)` |
| Async | `async Task<Url>` | Нет — горутины снаружи |
| Отмена | `CancellationToken` | `context.Context` |
| Конфигурация | `appsettings.json` + `IConfiguration` | `os.Getenv` |
| Логирование | Serilog / NLog | `log/slog` (stdlib) |

---

<!-- AUTO: NAV -->
**Вопросы?** Открой issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Назад к оглавлению](./README.md) | [Вперёд: 2. Хранилище: PostgreSQL и Redis →](./02_storage.md)
<!-- /AUTO: NAV -->
