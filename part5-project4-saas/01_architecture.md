# Архитектура и multi-tenancy

---

## Введение

> **Для C# разработчиков**: В ASP.NET Core multi-tenancy часто реализуется через `IHttpContextAccessor` + кастомный `ITenantContext`, а изоляция данных — через `IDbContextFactory<AppDbContext>` с разными строками подключения или через `HasQueryFilter` на уровне EF Core. В Go нет DI-контейнера, поэтому tenant context передаётся явно через `context.Context`, а переключение схемы делается на уровне соединения с PostgreSQL.

Multi-tenancy — это способность одного экземпляра приложения обслуживать множество изолированных организаций (тенантов). Правильный выбор стратегии изоляции определяет стоимость инфраструктуры, сложность реализации и уровень безопасности.

---

## Стратегии изоляции данных

### Сравнение подходов

| Стратегия | Изоляция | Стоимость | Сложность | Применение |
|-----------|----------|-----------|-----------|------------|
| **Shared table** (tenant_id колонка) | Низкая | Минимальная | Простая | Стартапы, низкие требования к изоляции |
| **Separate schema** | Средняя | Низкая | Средняя | Большинство B2B SaaS |
| **Separate database** | Высокая | Высокая | Сложная | Enterprise, регуляторные требования |
| **Separate instance** | Максимальная | Очень высокая | Очень сложная | On-premise, банки, госструктуры |

### Выбор для нашей платформы: Separate Schema

Мы используем **schema-per-tenant** в PostgreSQL:

```
public/                   ← системные таблицы (tenants, plans, billing)
tenant_acme/              ← данные тенанта "acme"
  ├── users
  ├── projects
  └── audit_log
tenant_globex/            ← данные тенанта "globex"
  ├── users
  ├── projects
  └── audit_log
```

**Преимущества**:
- Все тенанты в одной БД — один экземпляр PostgreSQL
- Полная изоляция на уровне SQL: `SELECT * FROM users` в схеме `tenant_acme` не видит данные `tenant_globex`
- Миграции схемы применяются к каждому тенанту независимо
- Легко экспортировать/удалить данные тенанта: `DROP SCHEMA tenant_acme CASCADE`

---

## Доменная модель

### Основные сущности

```go
package domain

import (
    "time"

    "github.com/google/uuid"
)

// Tenant — организация-клиент платформы.
// Хранится в public-схеме, видна всем сервисам.
type Tenant struct {
    ID        uuid.UUID  `db:"id"`
    Slug      string     `db:"slug"`       // уникальный идентификатор: "acme", "globex"
    Name      string     `db:"name"`
    Schema    string     `db:"schema_name"` // "tenant_acme"
    PlanID    uuid.UUID  `db:"plan_id"`
    Status    TenantStatus `db:"status"`
    CreatedAt time.Time  `db:"created_at"`
}

type TenantStatus string

const (
    TenantStatusActive    TenantStatus = "active"
    TenantStatusSuspended TenantStatus = "suspended"  // неоплата
    TenantStatusDeleted   TenantStatus = "deleted"
)

// User — пользователь тенанта.
// Хранится в схеме тенанта (tenant_acme.users).
type User struct {
    ID           uuid.UUID `db:"id"`
    TenantID     uuid.UUID `db:"tenant_id"`
    Email        string    `db:"email"`
    PasswordHash string    `db:"password_hash"`
    Role         UserRole  `db:"role"`
    CreatedAt    time.Time `db:"created_at"`
}

type UserRole string

const (
    RoleOwner  UserRole = "owner"
    RoleAdmin  UserRole = "admin"
    RoleMember UserRole = "member"
)

// Plan — тарифный план.
type Plan struct {
    ID           uuid.UUID `db:"id"`
    Name         string    `db:"name"`       // "Starter", "Pro", "Enterprise"
    PriceMonthly int64     `db:"price_monthly_cents"`
    Limits       PlanLimits
}

// PlanLimits — ограничения плана.
// Хранится как JSONB в таблице plans.
type PlanLimits struct {
    MaxUsers       int `json:"max_users"`
    MaxProjects    int `json:"max_projects"`
    APIRequestsDay int `json:"api_requests_day"` // для rate limiting
    StorageGB      int `json:"storage_gb"`
}
```

### Сравнение с C#

**C# (EF Core + multi-tenancy)**:
```csharp
// Глобальный фильтр — удобно, но скрывает логику
public class AppDbContext : DbContext
{
    private readonly ITenantContext _tenantContext;

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<User>()
            .HasQueryFilter(u => u.TenantId == _tenantContext.TenantId);
    }
}

// Получение tenant из HTTP-контекста через DI
public class TenantMiddleware
{
    public async Task InvokeAsync(HttpContext context, ITenantContext tenantCtx)
    {
        var tenantId = context.Request.Headers["X-Tenant-ID"];
        tenantCtx.TenantId = Guid.Parse(tenantId);
        await _next(context);
    }
}
```

**Go (явный context)**:
```go
// Нет скрытых фильтров — tenant передаётся явно
type contextKey string

const tenantKey contextKey = "tenant"

// WithTenant добавляет тенанта в context.
func WithTenant(ctx context.Context, t *domain.Tenant) context.Context {
    return context.WithValue(ctx, tenantKey, t)
}

// TenantFromContext извлекает тенанта из context.
// Паника при отсутствии — ошибка программиста, не runtime-ошибка.
func TenantFromContext(ctx context.Context) *domain.Tenant {
    t, ok := ctx.Value(tenantKey).(*domain.Tenant)
    if !ok {
        panic("tenant not in context: middleware not applied")
    }
    return t
}
```

---

## Переключение схемы PostgreSQL

Ключевой механизм schema-per-tenant: перед каждым запросом устанавливаем `search_path` соединения.

```go
package pgschema

import (
    "context"
    "fmt"

    "github.com/jackc/pgx/v5/pgxpool"
)

// SchemaPool оборачивает pgxpool и автоматически устанавливает search_path.
type SchemaPool struct {
    pool *pgxpool.Pool
}

func NewSchemaPool(pool *pgxpool.Pool) *SchemaPool {
    return &SchemaPool{pool: pool}
}

// Acquire возвращает соединение с установленным search_path для схемы тенанта.
// Важно: search_path действует только на время жизни соединения,
// поэтому мы устанавливаем его сразу после Acquire.
func (s *SchemaPool) Acquire(ctx context.Context, schema string) (*pgxpool.Conn, error) {
    conn, err := s.pool.Acquire(ctx)
    if err != nil {
        return nil, fmt.Errorf("acquire connection: %w", err)
    }

    // Устанавливаем схему тенанта + public для доступа к системным таблицам.
    // Параметризация через $1 невозможна для SET-команд в PostgreSQL,
    // но schema — это slug из нашей БД, а не пользовательский ввод.
    _, err = conn.Exec(ctx, fmt.Sprintf("SET search_path TO %s, public", schema))
    if err != nil {
        conn.Release()
        return nil, fmt.Errorf("set search_path to %s: %w", schema, err)
    }

    return conn, nil
}

// WithTenantConn выполняет fn с соединением, настроенным на схему тенанта.
func (s *SchemaPool) WithTenantConn(ctx context.Context, schema string, fn func(*pgxpool.Conn) error) error {
    conn, err := s.Acquire(ctx, schema)
    if err != nil {
        return err
    }
    defer conn.Release()
    return fn(conn)
}
```

### Использование в репозитории

```go
package user

import (
    "context"
    "fmt"

    "github.com/google/uuid"
    "saas-platform/shared/pgschema"
    "saas-platform/shared/tenantctx"
    "saas-platform/domain"
)

type Repository struct {
    sp *pgschema.SchemaPool
}

func NewRepository(sp *pgschema.SchemaPool) *Repository {
    return &Repository{sp: sp}
}

func (r *Repository) GetByID(ctx context.Context, id uuid.UUID) (*domain.User, error) {
    // Извлекаем тенанта из контекста — установлен middleware.
    tenant := tenantctx.TenantFromContext(ctx)

    var user domain.User
    err := r.sp.WithTenantConn(ctx, tenant.Schema, func(conn *pgxpool.Conn) error {
        return conn.QueryRow(ctx,
            `SELECT id, tenant_id, email, role, created_at FROM users WHERE id = $1`,
            id,
        ).Scan(&user.ID, &user.TenantID, &user.Email, &user.Role, &user.CreatedAt)
    })
    if err != nil {
        return nil, fmt.Errorf("get user %s: %w", id, err)
    }
    return &user, nil
}
```

---

## SQL-схема

### Системные таблицы (public-схема)

```sql
-- Тарифные планы
CREATE TABLE public.plans (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name          TEXT NOT NULL UNIQUE,
    price_monthly_cents BIGINT NOT NULL DEFAULT 0,
    limits        JSONB NOT NULL DEFAULT '{}',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Тенанты
CREATE TABLE public.tenants (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug          TEXT NOT NULL UNIQUE,
    name          TEXT NOT NULL,
    schema_name   TEXT NOT NULL UNIQUE,
    plan_id       UUID NOT NULL REFERENCES public.plans(id),
    status        TEXT NOT NULL DEFAULT 'active'
                  CHECK (status IN ('active', 'suspended', 'deleted')),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ON public.tenants(slug);
CREATE INDEX ON public.tenants(status);
```

### Таблицы в схеме тенанта

```sql
-- Создание схемы тенанта при онбординге (выполняется динамически)
-- CREATE SCHEMA tenant_acme;

-- Пользователи тенанта
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id     UUID NOT NULL,  -- денормализовано для аудита
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'member'
                  CHECK (role IN ('owner', 'admin', 'member')),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Лог аудита — все действия пользователей
CREATE TABLE audit_log (
    id         BIGSERIAL PRIMARY KEY,
    user_id    UUID NOT NULL REFERENCES users(id),
    action     TEXT NOT NULL,
    resource   TEXT NOT NULL,
    metadata   JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ON audit_log(user_id, created_at DESC);
```

---

## Безопасность: валидация slug схемы

Схема тенанта — это slug, который мы вставляем в SQL-запрос. Необходимо строго валидировать:

```go
package pgschema

import (
    "fmt"
    "regexp"
)

// validSlug разрешает только строчные буквы, цифры и подчёркивания.
var validSlug = regexp.MustCompile(`^[a-z][a-z0-9_]{1,62}$`)

// SchemaName строит имя схемы из slug тенанта.
// Возвращает ошибку, если slug не соответствует требованиям.
func SchemaName(slug string) (string, error) {
    if !validSlug.MatchString(slug) {
        return "", fmt.Errorf("invalid tenant slug %q: must match [a-z][a-z0-9_]{1,62}", slug)
    }
    return "tenant_" + slug, nil
}
```

---

## Инициализация при старте

```go
package main

import (
    "context"
    "log/slog"
    "os"

    "github.com/jackc/pgx/v5/pgxpool"
    "saas-platform/shared/pgschema"
)

func main() {
    ctx := context.Background()

    // Подключение к PostgreSQL.
    pool, err := pgxpool.New(ctx, os.Getenv("DATABASE_URL"))
    if err != nil {
        slog.Error("connect to postgres", "err", err)
        os.Exit(1)
    }
    defer pool.Close()

    // SchemaPool для работы с tenant-схемами.
    sp := pgschema.NewSchemaPool(pool)

    // ... инициализация сервисов
    _ = sp
}
```

---

## Docker Compose для разработки

```yaml
version: "3.9"

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: saas
      POSTGRES_USER: saas
      POSTGRES_PASSWORD: saas
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./migrations/init.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --save 60 1 --loglevel warning

volumes:
  pgdata:
```

---

## Сравнительная таблица

| Аспект | C# / ASP.NET Core | Go |
|--------|-------------------|----|
| Tenant context | `IHttpContextAccessor` + DI | `context.Context` с явными helpers |
| DB изоляция | `HasQueryFilter` в EF Core | `SET search_path` на уровне соединения |
| Middleware | `IMiddleware` интерфейс, атрибуты | Функция `func(http.Handler) http.Handler` |
| DI контейнер | Встроен (`IServiceCollection`) | Нет — зависимости передаются явно |
| Миграции | EF Core Migrations | golang-migrate, SQL-файлы |
| Конфигурация | `appsettings.json` + `IOptions<T>` | Переменные окружения, envconfig |

---

## Следующий шаг

Доменная модель и механизм изоляции готовы. Следующий раздел — [Auth Service: OAuth2 и JWT](02_auth_service.md): как выдавать токены с tenant-контекстом и верифицировать их во всех сервисах.
