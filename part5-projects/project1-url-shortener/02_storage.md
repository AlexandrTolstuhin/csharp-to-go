# 2. Хранилище: PostgreSQL и Redis

## Содержание

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Схема базы данных](#%D1%81%D1%85%D0%B5%D0%BC%D0%B0-%D0%B1%D0%B0%D0%B7%D1%8B-%D0%B4%D0%B0%D0%BD%D0%BD%D1%8B%D1%85)
  - [Миграции](#%D0%BC%D0%B8%D0%B3%D1%80%D0%B0%D1%86%D0%B8%D0%B8)
- [PostgreSQL с pgx v5](#postgresql-%D1%81-pgx-v5)
  - [C# подход (EF Core / Dapper)](#c-%D0%BF%D0%BE%D0%B4%D1%85%D0%BE%D0%B4-ef-core--dapper)
  - [Go подход: инициализация пула](#go-%D0%BF%D0%BE%D0%B4%D1%85%D0%BE%D0%B4-%D0%B8%D0%BD%D0%B8%D1%86%D0%B8%D0%B0%D0%BB%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-%D0%BF%D1%83%D0%BB%D0%B0)
- [Реализация URLRepository](#%D1%80%D0%B5%D0%B0%D0%BB%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-urlrepository)
  - [Работа с транзакциями](#%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%B0-%D1%81-%D1%82%D1%80%D0%B0%D0%BD%D0%B7%D0%B0%D0%BA%D1%86%D0%B8%D1%8F%D0%BC%D0%B8)
- [Redis кэш](#redis-%D0%BA%D1%8D%D1%88)
  - [C# подход (IDistributedCache / StackExchange.Redis)](#c-%D0%BF%D0%BE%D0%B4%D1%85%D0%BE%D0%B4-idistributedcache--stackexchangeredis)
  - [Go подход (go-redis/v9)](#go-%D0%BF%D0%BE%D0%B4%D1%85%D0%BE%D0%B4-go-redisv9)
- [Паттерн cache-aside](#%D0%BF%D0%B0%D1%82%D1%82%D0%B5%D1%80%D0%BD-cache-aside)
- [Обработка ошибок хранилища](#%D0%BE%D0%B1%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%BA%D0%B0-%D0%BE%D1%88%D0%B8%D0%B1%D0%BE%D0%BA-%D1%85%D1%80%D0%B0%D0%BD%D0%B8%D0%BB%D0%B8%D1%89%D0%B0)
- [Сравнительная таблица](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F-%D1%82%D0%B0%D0%B1%D0%BB%D0%B8%D1%86%D0%B0)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

---

## Схема базы данных

### Миграции

В Go нет встроенного механизма миграций как в EF Core. Для простого проекта
используем SQL-файлы, применяемые вручную или через `migrate` CLI.

```sql
-- migrations/001_create_urls.sql
CREATE TABLE IF NOT EXISTS urls (
    id          BIGSERIAL PRIMARY KEY,
    code        VARCHAR(10)  NOT NULL UNIQUE,
    original_url TEXT        NOT NULL,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Индекс по коду — основной способ поиска (O(log n) вместо seq scan)
CREATE INDEX IF NOT EXISTS idx_urls_code ON urls(code);
```

```sql
-- migrations/002_create_stats.sql
-- Счётчик кликов — отдельная таблица для изоляции hot update-ов
-- от immutable записей URLs (оптимизация для высокой нагрузки)
CREATE TABLE IF NOT EXISTS url_clicks (
    code       VARCHAR(10) NOT NULL REFERENCES urls(code) ON DELETE CASCADE,
    click_count BIGINT     NOT NULL DEFAULT 0,
    PRIMARY KEY (code)
);

-- Функция для атомарного инкремента или первоначальной вставки
CREATE OR REPLACE FUNCTION increment_click(p_code VARCHAR)
RETURNS VOID AS $$
BEGIN
    INSERT INTO url_clicks(code, click_count) VALUES (p_code, 1)
    ON CONFLICT (code)
    DO UPDATE SET click_count = url_clicks.click_count + 1;
END;
$$ LANGUAGE plpgsql;
```

> 💡 **Для C# разработчиков**: Аналог — `dotnet ef migrations add InitialCreate`.
> В production-проектах на Go используют [golang-migrate](https://github.com/golang-migrate/migrate)
> или [goose](https://github.com/pressly/goose) для версионированных миграций.

> ⚠️ **Дизайнерское решение**: Счётчик кликов вынесен в отдельную таблицу `url_clicks`.
> Это позволяет часто-пишущуюся строку (инкремент при каждом переходе) изолировать
> от редко меняющейся записи URL. В PostgreSQL это снижает lock contention.

---

## PostgreSQL с pgx v5

### C# подход (EF Core / Dapper)

```csharp
// Data/AppDbContext.cs — EF Core
public class AppDbContext : DbContext
{
    public DbSet<Url> Urls { get; set; }

    protected override void OnModelCreating(ModelBuilder b)
    {
        b.Entity<Url>(e =>
        {
            e.ToTable("urls");
            e.HasKey(x => x.Id);
            e.Property(x => x.Code).HasColumnName("code");
            e.Property(x => x.OriginalUrl).HasColumnName("original_url");
        });
    }
}

// Репозиторий через Dapper (аналогично pgx по стилю)
public class UrlRepository : IUrlRepository
{
    private readonly IDbConnection _db;

    public async Task<Url?> GetByCodeAsync(string code, CancellationToken ct)
    {
        return await _db.QuerySingleOrDefaultAsync<Url>(
            "SELECT id, code, original_url, created_at FROM urls WHERE code = @Code",
            new { Code = code });
    }
}
```

### Go подход: инициализация пула

```go
// internal/storage/postgres/pool.go
package postgres

import (
    "context"
    "fmt"
    "time"

    "github.com/jackc/pgx/v5/pgxpool"
)

// NewPool создаёт пул соединений к PostgreSQL.
// pgxpool — аналог SqlConnection pool в C# / ConnectionPool в EF Core.
func NewPool(databaseURL string) (*pgxpool.Pool, error) {
    config, err := pgxpool.ParseConfig(databaseURL)
    if err != nil {
        return nil, fmt.Errorf("парсинг конфига БД: %w", err)
    }

    // Настройки пула соединений
    config.MaxConns = 25                       // аналог MaxPoolSize в C#
    config.MinConns = 5                        // минимум горячих соединений
    config.MaxConnLifetime = 1 * time.Hour     // пересоздавать соединения раз в час
    config.MaxConnIdleTime = 10 * time.Minute  // убирать idle соединения
    config.HealthCheckPeriod = 30 * time.Second

    // Контекст с таймаутом на подключение
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()

    pool, err := pgxpool.NewWithConfig(ctx, config)
    if err != nil {
        return nil, fmt.Errorf("создание пула: %w", err)
    }

    // Проверяем что БД доступна
    if err := pool.Ping(ctx); err != nil {
        return nil, fmt.Errorf("пинг БД: %w", err)
    }

    return pool, nil
}
```

---

## Реализация URLRepository

```go
// internal/storage/postgres/url_repo.go
package postgres

import (
    "context"
    "errors"
    "fmt"

    "github.com/jackc/pgx/v5"
    "github.com/jackc/pgx/v5/pgxpool"
    "github.com/yourname/urlshortener/internal/domain"
)

// URLRepository реализует domain.URLRepository через PostgreSQL.
// Структура является конкретной реализацией интерфейса —
// импортёр видит только интерфейс, не этот тип напрямую.
type URLRepository struct {
    pool *pgxpool.Pool
}

// NewURLRepository конструктор репозитория.
func NewURLRepository(pool *pgxpool.Pool) *URLRepository {
    return &URLRepository{pool: pool}
}

// GetByCode ищет URL по коду.
// Возвращает domain.ErrNotFound если запись не найдена.
func (r *URLRepository) GetByCode(ctx context.Context, code string) (domain.URL, error) {
    // SQL выполняется напрямую — нет ORM, нет рефлексии, нет магии
    // Производительность сравнима с Dapper, лучше чем EF Core
    query := `
        SELECT u.id, u.code, u.original_url, u.created_at,
               COALESCE(c.click_count, 0) as click_count
        FROM urls u
        LEFT JOIN url_clicks c ON c.code = u.code
        WHERE u.code = $1`

    var record domain.URL

    // pgx.Row — аналог SqlDataReader, но типобезопасный
    err := r.pool.QueryRow(ctx, query, code).Scan(
        &record.ID,
        &record.Code,
        &record.OriginalURL,
        &record.CreatedAt,
        &record.ClickCount,
    )

    if err != nil {
        // pgx возвращает pgx.ErrNoRows когда строка не найдена
        // Конвертируем в доменную ошибку
        if errors.Is(err, pgx.ErrNoRows) {
            return domain.URL{}, domain.NewNotFoundError(code)
        }
        return domain.URL{}, fmt.Errorf("GetByCode(%q): %w", code, err)
    }

    return record, nil
}

// Create сохраняет новую запись URL и возвращает её с заполненными ID и CreatedAt.
func (r *URLRepository) Create(ctx context.Context, url domain.URL) (domain.URL, error) {
    // RETURNING возвращает сгенерированные значения — аналог OUTPUT в SQL Server
    // или GetGeneratedKeys в Java
    query := `
        INSERT INTO urls (code, original_url)
        VALUES ($1, $2)
        RETURNING id, created_at`

    err := r.pool.QueryRow(ctx, query, url.Code, url.OriginalURL).Scan(
        &url.ID,
        &url.CreatedAt,
    )
    if err != nil {
        return domain.URL{}, fmt.Errorf("Create: %w", err)
    }

    return url, nil
}

// IncrementClickCount атомарно инкрементирует счётчик переходов.
// Использует UPSERT (INSERT ... ON CONFLICT) — атомарная операция без race condition.
func (r *URLRepository) IncrementClickCount(ctx context.Context, code string) error {
    // Вызываем PostgreSQL функцию (определена в миграции 002)
    _, err := r.pool.Exec(ctx, "SELECT increment_click($1)", code)
    if err != nil {
        return fmt.Errorf("IncrementClickCount(%q): %w", code, err)
    }
    return nil
}
```

### Работа с транзакциями

В некоторых случаях нужны транзакции. Вот как это выглядит в Go vs C#:

**C# (EF Core)**:
```csharp
using var tx = await _db.Database.BeginTransactionAsync(ct);
try
{
    await _db.Urls.AddAsync(url, ct);
    await _db.SaveChangesAsync(ct);
    await tx.CommitAsync(ct);
}
catch
{
    await tx.RollbackAsync(ct);
    throw;
}
```

**Go (pgx)**:
```go
// Транзакция в pgx — явная, без магии Unit of Work
func (r *URLRepository) CreateWithStats(ctx context.Context, url domain.URL) (domain.URL, error) {
    // Начинаем транзакцию из пула
    tx, err := r.pool.Begin(ctx)
    if err != nil {
        return domain.URL{}, fmt.Errorf("begin tx: %w", err)
    }
    // defer rollback — выполнится если CommitTx не был вызван
    // После Commit() pgx игнорирует Rollback(), так что defer безопасен
    defer tx.Rollback(ctx) //nolint:errcheck

    // Вставляем URL
    var created domain.URL
    err = tx.QueryRow(ctx,
        `INSERT INTO urls (code, original_url) VALUES ($1, $2) RETURNING id, code, original_url, created_at`,
        url.Code, url.OriginalURL,
    ).Scan(&created.ID, &created.Code, &created.OriginalURL, &created.CreatedAt)
    if err != nil {
        return domain.URL{}, fmt.Errorf("insert url: %w", err)
    }

    // Инициализируем счётчик
    _, err = tx.Exec(ctx,
        `INSERT INTO url_clicks (code, click_count) VALUES ($1, 0)`,
        url.Code,
    )
    if err != nil {
        return domain.URL{}, fmt.Errorf("init clicks: %w", err)
    }

    // Коммитим
    if err := tx.Commit(ctx); err != nil {
        return domain.URL{}, fmt.Errorf("commit tx: %w", err)
    }

    return created, nil
}
```

> 💡 **Паттерн `defer tx.Rollback(ctx)`**: Стандартная Go-идиома для транзакций.
> После `tx.Commit()` вызов `Rollback()` возвращает ошибку которую мы игнорируем
> (`//nolint:errcheck`). Если до Commit() произошла паника или возврат с ошибкой —
> Rollback() откатит транзакцию автоматически.

---

## Redis кэш

### C# подход (IDistributedCache / StackExchange.Redis)

```csharp
// Services/UrlCache.cs
public class UrlCache : IUrlCache
{
    private readonly IDistributedCache _cache;
    private readonly TimeSpan _ttl = TimeSpan.FromHours(1);

    public async Task<string?> GetAsync(string code, CancellationToken ct)
    {
        var bytes = await _cache.GetAsync($"url:{code}", ct);
        return bytes == null ? null : Encoding.UTF8.GetString(bytes);
    }

    public async Task SetAsync(string code, string originalUrl, CancellationToken ct)
    {
        var options = new DistributedCacheEntryOptions { AbsoluteExpirationRelativeToNow = _ttl };
        await _cache.SetStringAsync($"url:{code}", originalUrl, options, ct);
    }
}
```

### Go подход (go-redis/v9)

```go
// internal/storage/redis/client.go
package redis

import (
    "context"
    "fmt"
    "time"

    "github.com/redis/go-redis/v9"
    "github.com/yourname/urlshortener/internal/domain"
)

const (
    urlKeyPrefix = "url:"        // "url:aB3xY9" → оригинальный URL
    defaultTTL   = time.Hour     // TTL кэша
)

// URLCache реализует domain.Cache через Redis.
type URLCache struct {
    client *redis.Client
}

// NewClient создаёт Redis клиент.
func NewClient(redisURL string) (*redis.Client, error) {
    opts, err := redis.ParseURL(redisURL)
    if err != nil {
        return nil, fmt.Errorf("парсинг Redis URL: %w", err)
    }

    client := redis.NewClient(opts)

    // Проверяем соединение
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    if err := client.Ping(ctx).Err(); err != nil {
        return nil, fmt.Errorf("пинг Redis: %w", err)
    }

    return client, nil
}

// NewURLCache конструктор кэша.
func NewURLCache(client *redis.Client) *URLCache {
    return &URLCache{client: client}
}

// Get возвращает оригинальный URL из кэша.
// Возвращает domain.ErrNotFound при кэш-промахе.
func (c *URLCache) Get(ctx context.Context, code string) (string, error) {
    key := urlKeyPrefix + code

    // redis.Nil — специальная ошибка при отсутствии ключа (аналог null в C#)
    val, err := c.client.Get(ctx, key).Result()
    if err != nil {
        if err == redis.Nil {
            // Кэш-промах — не ошибка, возвращаем domain.ErrNotFound
            return "", domain.ErrNotFound
        }
        return "", fmt.Errorf("redis GET %s: %w", key, err)
    }

    return val, nil
}

// Set кэширует оригинальный URL с TTL.
func (c *URLCache) Set(ctx context.Context, code string, originalURL string) error {
    key := urlKeyPrefix + code

    // SET key value EX 3600 — стандартная Redis операция
    if err := c.client.Set(ctx, key, originalURL, defaultTTL).Err(); err != nil {
        return fmt.Errorf("redis SET %s: %w", key, err)
    }

    return nil
}

// Delete инвалидирует запись в кэше.
func (c *URLCache) Delete(ctx context.Context, code string) error {
    key := urlKeyPrefix + code

    if err := c.client.Del(ctx, key).Err(); err != nil {
        return fmt.Errorf("redis DEL %s: %w", key, err)
    }

    return nil
}

// Close закрывает соединение с Redis.
func (c *URLCache) Close() error {
    return c.client.Close()
}
```

---

## Паттерн cache-aside

Паттерн cache-aside (он же lazy loading cache) — основной способ кэширования
при работе с Redis. Уже реализован в `URLService.Redirect` из предыдущего раздела,
здесь покажем его полностью со всеми деталями.

```mermaid
flowchart TD
    A[Запрос GET /{code}] --> B{Есть в Redis?}
    B -- Да --> C[Вернуть из Redis]
    B -- Нет --> D[Запрос в PostgreSQL]
    D --> E{Найден в БД?}
    E -- Нет --> F[Вернуть ErrNotFound]
    E -- Да --> G[Записать в Redis TTL=1h]
    G --> H[Вернуть из БД]
    C --> I[Асинхронно: IncrementClick]
    H --> I
```

**Ключевые решения дизайна**:

1. **Асинхронный инкремент клика** — не ждём запись статистики перед ответом.
   Снижает latency редиректа с ~5ms до ~1ms.

2. **Запись в кэш при промахе** — горутина записывает в Redis пока клиент уже
   получил редирект. Не блокируем ответ.

3. **TTL = 1 час** — баланс между памятью Redis и частотой обращений к PostgreSQL.
   Популярные ссылки будут всегда в кэше; непопулярные — вытеснятся.

```go
// Полная реализация Redirect для справки:
func (s *URLService) Redirect(ctx context.Context, code string) (string, error) {
    // 1. Проверяем кэш
    if originalURL, err := s.cache.Get(ctx, code); err == nil {
        // Кэш-попадание: hit ratio учитывается метриками
        go func() {
            _ = s.repo.IncrementClickCount(context.Background(), code)
        }()
        return originalURL, nil
    }

    // 2. Кэш-промах: идём в PostgreSQL
    record, err := s.repo.GetByCode(ctx, code)
    if err != nil {
        // Пробрасываем ErrNotFound наверх — хэндлер вернёт 404
        return "", err
    }

    // 3. Заполняем кэш + записываем клик асинхронно
    go func() {
        bg := context.Background()
        _ = s.cache.Set(bg, code, record.OriginalURL)
        _ = s.repo.IncrementClickCount(bg, code)
    }()

    return record.OriginalURL, nil
}
```

> ⚠️ **Тонкость**: при использовании `go func()` нужно создать новый контекст.
> Если использовать родительский `ctx` (из HTTP-запроса), он может быть отменён
> к моменту выполнения горутины, что приведёт к ошибке записи в кэш/БД.

---

## Обработка ошибок хранилища

В Go принято **оборачивать** ошибки с помощью `fmt.Errorf("контекст: %w", err)`.
Это сохраняет оригинальную ошибку в цепочке для проверки через `errors.Is/As`.

```go
// Пример цепочки ошибок:
// pgx.ErrNoRows → domain.NotFoundError → "GetByCode: url not found"

// В репозитории:
if errors.Is(err, pgx.ErrNoRows) {
    return domain.URL{}, domain.NewNotFoundError(code)  // обёртывает ErrNotFound
}
return domain.URL{}, fmt.Errorf("GetByCode(%q): %w", code, err)

// В сервисе:
record, err := s.repo.GetByCode(ctx, code)
if err != nil {
    // Не добавляем лишний контекст — ошибка уже содержательна
    return "", err
}

// В хэндлере:
originalURL, err := s.service.Redirect(ctx, code)
if errors.Is(err, domain.ErrNotFound) {
    http.Error(w, "ссылка не найдена", http.StatusNotFound)
    return
}
if err != nil {
    // Неожиданная ошибка — логируем и возвращаем 500
    slog.Error("redirect error", "code", code, "err", err)
    http.Error(w, "внутренняя ошибка", http.StatusInternalServerError)
    return
}
```

**Сравнение с C#**:

```csharp
// C# — exception bubbling
try
{
    var url = await _repo.GetByCodeAsync(code, ct);
    // ...
}
catch (UrlNotFoundException)
{
    return Results.NotFound();
}
catch (Exception ex)
{
    _logger.LogError(ex, "Redirect error for code {Code}", code);
    return Results.InternalServerError();
}
```

```go
// Go — явный возврат ошибок
url, err := repo.GetByCode(ctx, code)
if errors.Is(err, domain.ErrNotFound) {
    // аналог catch (UrlNotFoundException)
    return "", err
}
if err != nil {
    // аналог catch (Exception ex)
    slog.Error("redirect error", "code", code, "err", err)
    return "", err
}
```

> 💡 **Преимущество Go подхода**: каждый вызов явно показывает, что он может
> вернуть ошибку. Нет скрытых исключений (checked exceptions как в Java, но
> без необходимости декларировать их). Линтер `errcheck` поймает игнорирование ошибок.

---

## Сравнительная таблица

| Аспект | C# | Go |
|--------|----|----|
| ORM | EF Core | Нет — pgx raw SQL |
| Маппинг | Reflection / атрибуты | Явный `.Scan(&field1, &field2)` |
| Транзакции | `BeginTransactionAsync()` | `pool.Begin(ctx)` |
| Откат транзакции | `try/catch/rollback` | `defer tx.Rollback(ctx)` |
| Миграции | `dotnet ef migrations` | golang-migrate / goose / SQL-файлы |
| Кэш | `IDistributedCache` | `go-redis/v9` напрямую |
| Кэш null | `null` или `CacheMiss` exception | `redis.Nil` ошибка |
| NULL в БД | Nullable types `int?` | `pgtype.Int8` или `*int64` |
| Connection pool | Встроен в драйвер | `pgxpool.Pool` |
| Prepared statements | Автоматически через EF | Автоматически в pgx |

---

<!-- AUTO: NAV -->
**Вопросы?** Открой issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Назад: 1. Доменная модель и сервисный слой](./01_domain.md) | [Вперёд: 3. HTTP слой: net/http и chi →](./03_http.md)
<!-- /AUTO: NAV -->
