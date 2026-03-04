# 4.1 Production PostgreSQL

## Содержание

- [Введение](#%D0%B2%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5)
  - [Что отличает production от development](#%D1%87%D1%82%D0%BE-%D0%BE%D1%82%D0%BB%D0%B8%D1%87%D0%B0%D0%B5%D1%82-production-%D0%BE%D1%82-development)
  - [Что вы узнаете](#%D1%87%D1%82%D0%BE-%D0%B2%D1%8B-%D1%83%D0%B7%D0%BD%D0%B0%D0%B5%D1%82%D0%B5)
- [Advanced pgx Configuration](#advanced-pgx-configuration)
  - [Детальная конфигурация pgxpool](#%D0%B4%D0%B5%D1%82%D0%B0%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F-%D0%BA%D0%BE%D0%BD%D1%84%D0%B8%D0%B3%D1%83%D1%80%D0%B0%D1%86%D0%B8%D1%8F-pgxpool)
  - [Сравнение с ADO.NET](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81-adonet)
  - [Runtime Parameters](#runtime-parameters)
  - [Custom Types с pgtype](#custom-types-%D1%81-pgtype)
  - [Nullable типы в pgx vs C#](#nullable-%D1%82%D0%B8%D0%BF%D1%8B-%D0%B2-pgx-vs-c)
  - [Query Tracing](#query-tracing)
  - [OpenTelemetry Tracer](#opentelemetry-tracer)
  - [Connection Hooks](#connection-hooks)
  - [Prepared Statement Cache](#prepared-statement-cache)
  - [Сравнение Hooks с C#](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-hooks-%D1%81-c)
- [Production Connection Pooling](#production-connection-pooling)
  - [pgxpool vs PgBouncer](#pgxpool-vs-pgbouncer)
  - [Когда нужен PgBouncer](#%D0%BA%D0%BE%D0%B3%D0%B4%D0%B0-%D0%BD%D1%83%D0%B6%D0%B5%D0%BD-pgbouncer)
  - [Настройка PgBouncer](#%D0%BD%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0-pgbouncer)
  - [Go с PgBouncer](#go-%D1%81-pgbouncer)
  - [Мониторинг пула](#%D0%BC%D0%BE%D0%BD%D0%B8%D1%82%D0%BE%D1%80%D0%B8%D0%BD%D0%B3-%D0%BF%D1%83%D0%BB%D0%B0)
  - [Pool Statistics](#pool-statistics)
  - [Graceful Shutdown](#graceful-shutdown)
  - [Health Checks](#health-checks)
  - [Connection Warming](#connection-warming)
    - [Window Functions](#window-functions)
    - [Recursive CTE](#recursive-cte)
  - [Dynamic Queries](#dynamic-queries)
    - [Optional Filters с sqlc.narg()](#optional-filters-%D1%81-sqlcnarg)
    - [Arrays с sqlc.slice()](#arrays-%D1%81-sqlcslice)
  - [Транзакции в sqlc](#%D1%82%D1%80%D0%B0%D0%BD%D0%B7%D0%B0%D0%BA%D1%86%D0%B8%D0%B8-%D0%B2-sqlc)
    - [Transaction Manager](#transaction-manager)
  - [Batch Operations в sqlc](#batch-operations-%D0%B2-sqlc)
  - [Custom Types и Overrides](#custom-types-%D0%B8-overrides)
  - [sqlc.embed для композиции](#sqlcembed-%D0%B4%D0%BB%D1%8F-%D0%BA%D0%BE%D0%BC%D0%BF%D0%BE%D0%B7%D0%B8%D1%86%D0%B8%D0%B8)
  - [Сравнение sqlc с Dapper (C#)](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-sqlc-%D1%81-dapper-c)
- [Zero-Downtime Migrations](#zero-downtime-migrations)
  - [Опасные операции](#%D0%BE%D0%BF%D0%B0%D1%81%D0%BD%D1%8B%D0%B5-%D0%BE%D0%BF%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D0%B8)
    - [Блокировки в PostgreSQL](#%D0%B1%D0%BB%D0%BE%D0%BA%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D0%B8-%D0%B2-postgresql)
  - [Безопасные паттерны](#%D0%B1%D0%B5%D0%B7%D0%BE%D0%BF%D0%B0%D1%81%D0%BD%D1%8B%D0%B5-%D0%BF%D0%B0%D1%82%D1%82%D0%B5%D1%80%D0%BD%D1%8B)
    - [1. Добавление nullable колонки (безопасно)](#1-%D0%B4%D0%BE%D0%B1%D0%B0%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5-nullable-%D0%BA%D0%BE%D0%BB%D0%BE%D0%BD%D0%BA%D0%B8-%D0%B1%D0%B5%D0%B7%D0%BE%D0%BF%D0%B0%D1%81%D0%BD%D0%BE)
    - [2. Добавление NOT NULL колонки (3-step pattern)](#2-%D0%B4%D0%BE%D0%B1%D0%B0%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5-not-null-%D0%BA%D0%BE%D0%BB%D0%BE%D0%BD%D0%BA%D0%B8-3-step-pattern)
    - [3. Создание индекса без блокировки](#3-%D1%81%D0%BE%D0%B7%D0%B4%D0%B0%D0%BD%D0%B8%D0%B5-%D0%B8%D0%BD%D0%B4%D0%B5%D0%BA%D1%81%D0%B0-%D0%B1%D0%B5%D0%B7-%D0%B1%D0%BB%D0%BE%D0%BA%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D0%B8)
    - [4. Безопасное добавление Foreign Key](#4-%D0%B1%D0%B5%D0%B7%D0%BE%D0%BF%D0%B0%D1%81%D0%BD%D0%BE%D0%B5-%D0%B4%D0%BE%D0%B1%D0%B0%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5-foreign-key)
    - [5. Переименование колонки (Expand/Contract)](#5-%D0%BF%D0%B5%D1%80%D0%B5%D0%B8%D0%BC%D0%B5%D0%BD%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5-%D0%BA%D0%BE%D0%BB%D0%BE%D0%BD%D0%BA%D0%B8-expandcontract)
  - [Expand/Contract Pattern](#expandcontract-pattern)
  - [Atlas: Declarative Migrations](#atlas-declarative-migrations)
    - [Декларативный подход](#%D0%B4%D0%B5%D0%BA%D0%BB%D0%B0%D1%80%D0%B0%D1%82%D0%B8%D0%B2%D0%BD%D1%8B%D0%B9-%D0%BF%D0%BE%D0%B4%D1%85%D0%BE%D0%B4)
    - [Atlas с Go](#atlas-%D1%81-go)
  - [Сравнение инструментов миграций](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-%D0%B8%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D0%BE%D0%B2-%D0%BC%D0%B8%D0%B3%D1%80%D0%B0%D1%86%D0%B8%D0%B9)
- [Query Performance](#query-performance)
  - [EXPLAIN ANALYZE из Go](#explain-analyze-%D0%B8%D0%B7-go)
  - [Чтение планов запросов](#%D1%87%D1%82%D0%B5%D0%BD%D0%B8%D0%B5-%D0%BF%D0%BB%D0%B0%D0%BD%D0%BE%D0%B2-%D0%B7%D0%B0%D0%BF%D1%80%D0%BE%D1%81%D0%BE%D0%B2)
  - [Типы индексов](#%D1%82%D0%B8%D0%BF%D1%8B-%D0%B8%D0%BD%D0%B4%D0%B5%D0%BA%D1%81%D0%BE%D0%B2)
  - [Сравнение индексов с SQL Server (C#)](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-%D0%B8%D0%BD%D0%B4%D0%B5%D0%BA%D1%81%D0%BE%D0%B2-%D1%81-sql-server-c)
  - [Query Tuning](#query-tuning)
    - [Connection-level settings](#connection-level-settings)
    - [Параллельные запросы PostgreSQL](#%D0%BF%D0%B0%D1%80%D0%B0%D0%BB%D0%BB%D0%B5%D0%BB%D1%8C%D0%BD%D1%8B%D0%B5-%D0%B7%D0%B0%D0%BF%D1%80%D0%BE%D1%81%D1%8B-postgresql)
  - [pg_stat_statements](#pg_stat_statements)
  - [Auto EXPLAIN](#auto-explain)
- [High Availability](#high-availability)
  - [Read Replicas](#read-replicas)
    - [Context-based routing](#context-based-routing)
  - [Connection String для HA](#connection-string-%D0%B4%D0%BB%D1%8F-ha)
  - [Retry Strategies](#retry-strategies)
  - [Сравнение с Polly (C#)](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81-polly-c)
  - [Circuit Breaker](#circuit-breaker)
- [Security](#security)
  - [SSL/TLS Connections](#ssltls-connections)
  - [SSL Mode сравнение](#ssl-mode-%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5)
  - [Row-Level Security](#row-level-security)
  - [Secrets Management](#secrets-management)
  - [Ротация секретов](#%D1%80%D0%BE%D1%82%D0%B0%D1%86%D0%B8%D1%8F-%D1%81%D0%B5%D0%BA%D1%80%D0%B5%D1%82%D0%BE%D0%B2)
- [Observability для PostgreSQL](#observability-%D0%B4%D0%BB%D1%8F-postgresql)
  - [Метрики pg_stat_*](#%D0%BC%D0%B5%D1%82%D1%80%D0%B8%D0%BA%D0%B8-pg_stat_)
  - [Prometheus Integration](#prometheus-integration)
  - [Ключевые метрики для алертов](#%D0%BA%D0%BB%D1%8E%D1%87%D0%B5%D0%B2%D1%8B%D0%B5-%D0%BC%D0%B5%D1%82%D1%80%D0%B8%D0%BA%D0%B8-%D0%B4%D0%BB%D1%8F-%D0%B0%D0%BB%D0%B5%D1%80%D1%82%D0%BE%D0%B2)
  - [OpenTelemetry Instrumentation](#opentelemetry-instrumentation)
- [Практические примеры](#%D0%BF%D1%80%D0%B0%D0%BA%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B5-%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80%D1%8B)
  - [Пример 1: Production-Ready Connection Setup](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-1-production-ready-connection-setup)
  - [Пример 2: Zero-Downtime Migration](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-2-zero-downtime-migration)
  - [Пример 3: Read Replica Routing](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-3-read-replica-routing)

---

## Введение

В [разделе 3.3](../part3-web-api/03_database.md) мы рассмотрели основы работы с PostgreSQL в Go: database/sql, pgx, sqlc, миграции и Repository pattern. Этот раздел углубляется в **production-ready паттерны** — то, что отличает прототип от системы, обслуживающей миллионы запросов.

> 💡 **Для C# разработчиков**: Если раздел 3.3 был аналогом "Getting Started with EF Core", то этот раздел — "EF Core in Production". Connection resilience, query optimization, zero-downtime deployments — всё это здесь.

### Что отличает production от development

| Аспект | Development | Production |
|--------|-------------|------------|
| **Connection Pool** | 5-10 соединений | 50-200 соединений, возможно PgBouncer |
| **Миграции** | `DROP TABLE`, `ALTER` без ограничений | Zero-downtime, backward-compatible |
| **Ошибки** | Паника при ошибке | Graceful degradation, retry, fallback |
| **Мониторинг** | `log.Println` | Structured logging, metrics, tracing |
| **Безопасность** | `sslmode=disable` | TLS, certificate verification, RLS |
| **Производительность** | "Работает и ладно" | EXPLAIN ANALYZE, индексы, partitioning |

### Что вы узнаете

- Продвинутая конфигурация pgx для production
- External connection pooling с PgBouncer
- Сложные запросы и dynamic queries в sqlc
- Zero-downtime миграции без блокировок
- Оптимизация производительности запросов
- High Availability: replicas, failover, retry
- Security: TLS, Row-Level Security
- Observability: метрики, трейсинг, логирование

---

## Advanced pgx Configuration

### Детальная конфигурация pgxpool

В production `pgxpool.New(ctx, connString)` недостаточно. Нужна детальная настройка.

```go
package postgres

import (
    "context"
    "fmt"
    "time"

    "github.com/jackc/pgx/v5"
    "github.com/jackc/pgx/v5/pgxpool"
)

type Config struct {
    // Connection
    Host     string
    Port     int
    User     string
    Password string
    Database string
    SSLMode  string

    // Pool
    MaxConns          int32
    MinConns          int32
    MaxConnLifetime   time.Duration
    MaxConnIdleTime   time.Duration
    HealthCheckPeriod time.Duration

    // Timeouts
    ConnectTimeout   time.Duration
    QueryTimeout     time.Duration
    StatementTimeout time.Duration
}

func DefaultConfig() Config {
    return Config{
        // Connection
        Host:    "localhost",
        Port:    5432,
        SSLMode: "prefer",

        // Pool — production values
        MaxConns:          50,
        MinConns:          10,
        MaxConnLifetime:   time.Hour,
        MaxConnIdleTime:   30 * time.Minute,
        HealthCheckPeriod: time.Minute,

        // Timeouts
        ConnectTimeout:   10 * time.Second,
        QueryTimeout:     30 * time.Second,
        StatementTimeout: 30 * time.Second,
    }
}

func NewPool(ctx context.Context, cfg Config) (*pgxpool.Pool, error) {
    connString := fmt.Sprintf(
        "postgres://%s:%s@%s:%d/%s?sslmode=%s",
        cfg.User, cfg.Password, cfg.Host, cfg.Port, cfg.Database, cfg.SSLMode,
    )

    poolConfig, err := pgxpool.ParseConfig(connString)
    if err != nil {
        return nil, fmt.Errorf("parse config: %w", err)
    }

    // Pool settings
    poolConfig.MaxConns = cfg.MaxConns
    poolConfig.MinConns = cfg.MinConns
    poolConfig.MaxConnLifetime = cfg.MaxConnLifetime
    poolConfig.MaxConnIdleTime = cfg.MaxConnIdleTime
    poolConfig.HealthCheckPeriod = cfg.HealthCheckPeriod

    // Connection settings
    poolConfig.ConnConfig.ConnectTimeout = cfg.ConnectTimeout

    // Runtime parameters — выполняются для каждого соединения
    poolConfig.ConnConfig.RuntimeParams = map[string]string{
        "application_name":  "myapp",
        "statement_timeout": fmt.Sprintf("%dms", cfg.StatementTimeout.Milliseconds()),
        "lock_timeout":      "10s",
        "idle_in_transaction_session_timeout": "60s",
    }

    pool, err := pgxpool.NewWithConfig(ctx, poolConfig)
    if err != nil {
        return nil, fmt.Errorf("create pool: %w", err)
    }

    // Verify connection
    if err := pool.Ping(ctx); err != nil {
        pool.Close()
        return nil, fmt.Errorf("ping: %w", err)
    }

    return pool, nil
}
```

### Сравнение с ADO.NET

| pgx (Go) | ADO.NET/SqlClient (C#) |
|----------|------------------------|
| `MaxConns` | `Max Pool Size` |
| `MinConns` | `Min Pool Size` |
| `MaxConnLifetime` | `Connection Lifetime` |
| `MaxConnIdleTime` | — (нет прямого аналога) |
| `HealthCheckPeriod` | — (внутренняя валидация) |
| `RuntimeParams` | `Initial Catalog`, connection string options |
| `ConnectTimeout` | `Connect Timeout` |

> 💡 **Ключевое отличие**: В ADO.NET многие параметры задаются в connection string. В pgx — программно через структуры конфигурации, что даёт больше контроля.

### Runtime Parameters

Runtime Parameters — это PostgreSQL session settings, применяемые к каждому соединению:

```go
poolConfig.ConnConfig.RuntimeParams = map[string]string{
    // Имя приложения — видно в pg_stat_activity
    "application_name": "order-service",

    // Timeout для запросов (отменяет долгие запросы)
    "statement_timeout": "30s",

    // Timeout для получения блокировки
    "lock_timeout": "10s",

    // Timeout для idle транзакций
    "idle_in_transaction_session_timeout": "60s",

    // Timezone
    "timezone": "UTC",

    // Search path
    "search_path": "public,extensions",

    // Work memory для сортировок и хэш-таблиц
    "work_mem": "64MB",
}
```

> ⚠️ **Важно**: `statement_timeout` защищает от "убийственных" запросов. Без него один плохой запрос может заблокировать соединение навсегда.

### Custom Types с pgtype

pgx использует пакет `pgtype` для работы с PostgreSQL типами. Это эффективнее, чем `database/sql`, который всё конвертирует через строки.

```go
import (
    "github.com/jackc/pgx/v5/pgtype"
)

// Модель с PostgreSQL-specific типами
type Product struct {
    ID          int64
    Name        string
    Price       pgtype.Numeric     // NUMERIC — точные деньги
    Tags        []string           // TEXT[] — массив
    Metadata    pgtype.JSONBCodec  // JSONB
    ValidFrom   pgtype.Timestamptz // TIMESTAMP WITH TIME ZONE
    ValidTo     pgtype.Timestamptz
    Coordinates pgtype.Point       // POINT — геоданные
}

// Работа с Numeric
func CreateProduct(ctx context.Context, pool *pgxpool.Pool) error {
    price := pgtype.Numeric{}
    // Установка значения 99.99
    if err := price.Scan("99.99"); err != nil {
        return err
    }

    _, err := pool.Exec(ctx,
        `INSERT INTO products (name, price) VALUES ($1, $2)`,
        "Widget", price,
    )
    return err
}

// Работа с массивами
func GetProductsByTags(ctx context.Context, pool *pgxpool.Pool, tags []string) ([]Product, error) {
    rows, err := pool.Query(ctx,
        `SELECT id, name, tags FROM products WHERE tags && $1`,
        tags, // pgx автоматически конвертирует []string в TEXT[]
    )
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var products []Product
    for rows.Next() {
        var p Product
        if err := rows.Scan(&p.ID, &p.Name, &p.Tags); err != nil {
            return nil, err
        }
        products = append(products, p)
    }
    return products, rows.Err()
}
```

### Nullable типы в pgx vs C#

| PostgreSQL | pgx (Go) | C# |
|------------|----------|-----|
| `INTEGER NULL` | `pgtype.Int4` или `*int32` | `int?` |
| `TEXT NULL` | `pgtype.Text` или `*string` | `string?` |
| `TIMESTAMP NULL` | `pgtype.Timestamptz` | `DateTime?` |
| `JSONB` | `pgtype.JSONBCodec` или `map[string]any` | `JsonDocument` |
| `UUID` | `pgtype.UUID` или `[16]byte` | `Guid` |
| `NUMERIC` | `pgtype.Numeric` | `decimal` |

```go
// Использование pgtype для nullable
type User struct {
    ID        int64
    Email     string
    Phone     pgtype.Text // NULL-able
    DeletedAt pgtype.Timestamptz
}

func (u *User) GetPhone() string {
    if u.Phone.Valid {
        return u.Phone.String
    }
    return ""
}

func (u *User) IsDeleted() bool {
    return u.DeletedAt.Valid
}
```

### Query Tracing

pgx поддерживает tracing через интерфейс `pgx.QueryTracer`. Это необходимо для интеграции с OpenTelemetry.

```go
import (
    "context"
    "log/slog"
    "time"

    "github.com/jackc/pgx/v5"
)

// Простой tracer для логирования
type LoggingTracer struct {
    logger *slog.Logger
}

func (t *LoggingTracer) TraceQueryStart(
    ctx context.Context,
    conn *pgx.Conn,
    data pgx.TraceQueryStartData,
) context.Context {
    return context.WithValue(ctx, "query_start", time.Now())
}

func (t *LoggingTracer) TraceQueryEnd(
    ctx context.Context,
    conn *pgx.Conn,
    data pgx.TraceQueryEndData,
) {
    start := ctx.Value("query_start").(time.Time)
    duration := time.Since(start)

    // Логируем медленные запросы
    if duration > 100*time.Millisecond {
        t.logger.Warn("slow query",
            slog.String("sql", data.SQL),
            slog.Duration("duration", duration),
            slog.Int64("rows", data.CommandTag.RowsAffected()),
        )
    } else {
        t.logger.Debug("query executed",
            slog.String("sql", data.SQL),
            slog.Duration("duration", duration),
        )
    }

    // Логируем ошибки
    if data.Err != nil {
        t.logger.Error("query failed",
            slog.String("sql", data.SQL),
            slog.String("error", data.Err.Error()),
        )
    }
}

// Применение tracer
func NewPoolWithTracing(ctx context.Context, cfg Config, logger *slog.Logger) (*pgxpool.Pool, error) {
    poolConfig, err := pgxpool.ParseConfig(cfg.ConnectionString())
    if err != nil {
        return nil, err
    }

    poolConfig.ConnConfig.Tracer = &LoggingTracer{logger: logger}

    return pgxpool.NewWithConfig(ctx, poolConfig)
}
```

### OpenTelemetry Tracer

Для production рекомендуется использовать OpenTelemetry:

```go
import (
    "context"

    "github.com/jackc/pgx/v5"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/codes"
    "go.opentelemetry.io/otel/trace"
)

type OTelTracer struct {
    tracer trace.Tracer
}

func NewOTelTracer() *OTelTracer {
    return &OTelTracer{
        tracer: otel.Tracer("pgx"),
    }
}

func (t *OTelTracer) TraceQueryStart(
    ctx context.Context,
    conn *pgx.Conn,
    data pgx.TraceQueryStartData,
) context.Context {
    ctx, span := t.tracer.Start(ctx, "postgresql.query",
        trace.WithAttributes(
            attribute.String("db.system", "postgresql"),
            attribute.String("db.statement", data.SQL),
            attribute.String("db.name", conn.Config().Database),
        ),
    )
    return ctx
}

func (t *OTelTracer) TraceQueryEnd(
    ctx context.Context,
    conn *pgx.Conn,
    data pgx.TraceQueryEndData,
) {
    span := trace.SpanFromContext(ctx)
    defer span.End()

    span.SetAttributes(
        attribute.Int64("db.rows_affected", data.CommandTag.RowsAffected()),
    )

    if data.Err != nil {
        span.RecordError(data.Err)
        span.SetStatus(codes.Error, data.Err.Error())
    }
}
```

### Connection Hooks

pgx предоставляет hooks для выполнения кода при событиях жизненного цикла соединения.

```go
func NewPoolWithHooks(ctx context.Context, cfg Config) (*pgxpool.Pool, error) {
    poolConfig, err := pgxpool.ParseConfig(cfg.ConnectionString())
    if err != nil {
        return nil, err
    }

    // AfterConnect — выполняется после установки соединения
    poolConfig.AfterConnect = func(ctx context.Context, conn *pgx.Conn) error {
        // Загрузка расширений
        _, err := conn.Exec(ctx, "CREATE EXTENSION IF NOT EXISTS pg_trgm")
        if err != nil {
            return fmt.Errorf("create extension: %w", err)
        }

        // Установка search_path
        _, err = conn.Exec(ctx, "SET search_path TO public, extensions")
        if err != nil {
            return fmt.Errorf("set search_path: %w", err)
        }

        // Регистрация custom types
        // (если используете custom PostgreSQL types)

        slog.Info("connection established",
            slog.String("db", conn.Config().Database),
        )
        return nil
    }

    // BeforeAcquire — выполняется перед выдачей соединения из пула
    poolConfig.BeforeAcquire = func(ctx context.Context, conn *pgx.Conn) bool {
        // Проверяем, что соединение живое
        // Возвращаем false, если соединение нужно закрыть
        if conn.IsClosed() {
            return false
        }

        // Можно проверить, что соединение не в broken state
        // Например, если была отменена транзакция

        return true
    }

    // AfterRelease — выполняется после возврата соединения в пул
    poolConfig.AfterRelease = func(conn *pgx.Conn) bool {
        // Очистка session state
        // Возвращаем false, если соединение нужно закрыть

        // Например, сбрасываем prepared statements
        // (pgx кэширует их автоматически)

        return true
    }

    return pgxpool.NewWithConfig(ctx, poolConfig)
}
```

### Prepared Statement Cache

pgx автоматически кэширует prepared statements. Это даёт значительный прирост производительности для повторяющихся запросов.

```go
// pgx автоматически делает это:
// 1. Первый вызов Query("SELECT * FROM users WHERE id = $1", 1)
//    - Отправляет Parse + Bind + Execute
// 2. Второй вызов Query("SELECT * FROM users WHERE id = $1", 2)
//    - Использует кэшированный prepared statement
//    - Отправляет только Bind + Execute

// Настройка кэша
poolConfig.ConnConfig.DefaultQueryExecMode = pgx.QueryExecModeCacheStatement

// Режимы выполнения запросов:
// - QueryExecModeSimpleProtocol — простой протокол, без prepared statements
// - QueryExecModeExec — Extended Query Protocol, без кэширования
// - QueryExecModeCacheStatement — кэширование (default)
// - QueryExecModeCacheDescribe — кэширование с describe
// - QueryExecModeDescribeExec — describe перед каждым выполнением
```

> ⚠️ **PgBouncer и prepared statements**: В transaction mode PgBouncer не поддерживает prepared statements. Используйте `QueryExecModeSimpleProtocol` или session mode.

### Сравнение Hooks с C#

| pgx (Go) | ADO.NET (C#) |
|----------|--------------|
| `AfterConnect` | `SqlConnection.StateChange` event + manual setup |
| `BeforeAcquire` | — (нет прямого аналога) |
| `AfterRelease` | `SqlConnection.StateChange` + `ClearPool` |
| `QueryTracer` | `SqlClientEventSource` / DiagnosticSource |

```csharp
// C# аналог AfterConnect
connection.StateChange += (sender, e) => {
    if (e.CurrentState == ConnectionState.Open) {
        using var cmd = connection.CreateCommand();
        cmd.CommandText = "SET search_path TO public";
        cmd.ExecuteNonQuery();
    }
};
```

```go
// Go — чище и декларативнее
poolConfig.AfterConnect = func(ctx context.Context, conn *pgx.Conn) error {
    _, err := conn.Exec(ctx, "SET search_path TO public")
    return err
}
```

---

## Production Connection Pooling

### pgxpool vs PgBouncer

| Аспект | pgxpool (встроенный) | PgBouncer (внешний) |
|--------|---------------------|---------------------|
| **Простота** | Включён в pgx | Отдельный процесс |
| **Масштабирование** | Per-application | Shared across apps |
| **Макс. соединений** | Ограничен памятью app | Десятки тысяч |
| **Prepared statements** | Полная поддержка | Только в session mode |
| **Overhead** | Минимальный | Небольшой |
| **Failover** | Нет | Можно настроить |

### Когда нужен PgBouncer

```
✅ Используйте PgBouncer если:
- Много сервисов (>20) подключаются к одной БД
- Serverless/Lambda функции (холодный старт)
- PostgreSQL достиг max_connections
- Нужен connection multiplexing

❌ Достаточно pgxpool если:
- Один-два сервиса
- Стабильная нагрузка
- Используете prepared statements
- Не превышаете max_connections
```

### Настройка PgBouncer

```ini
; /etc/pgbouncer/pgbouncer.ini

[databases]
mydb = host=postgres.internal port=5432 dbname=mydb

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432

; Режим пула
; session — соединение держится на время сессии клиента
; transaction — соединение выдаётся на время транзакции
; statement — соединение выдаётся на время запроса (ограничения!)
pool_mode = transaction

; Размер пула
default_pool_size = 50
max_client_conn = 1000
min_pool_size = 10

; Timeouts
server_connect_timeout = 5
server_idle_timeout = 600
query_timeout = 30

; Аутентификация
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

; Логирование
log_connections = 1
log_disconnections = 1
log_pooler_errors = 1
```

### Go с PgBouncer

```go
func NewPoolWithPgBouncer(ctx context.Context) (*pgxpool.Pool, error) {
    poolConfig, err := pgxpool.ParseConfig(
        "postgres://user:pass@pgbouncer.internal:6432/mydb",
    )
    if err != nil {
        return nil, err
    }

    // ⚠️ ВАЖНО: Отключаем prepared statement cache для transaction mode
    poolConfig.ConnConfig.DefaultQueryExecMode = pgx.QueryExecModeSimpleProtocol

    // Или используем ExecSimpleProtocol для каждого запроса
    // poolConfig.ConnConfig.DefaultQueryExecMode = pgx.QueryExecModeExec

    // Меньше соединений — PgBouncer управляет пулом
    poolConfig.MaxConns = 10
    poolConfig.MinConns = 2

    return pgxpool.NewWithConfig(ctx, poolConfig)
}
```

### Мониторинг пула

```go
import (
    "context"
    "log/slog"
    "time"

    "github.com/jackc/pgx/v5/pgxpool"
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    poolConnsTotal = promauto.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "db_pool_connections_total",
            Help: "Total number of connections in the pool",
        },
        []string{"state"}, // acquired, idle, max
    )

    poolWaitDuration = promauto.NewHistogram(
        prometheus.HistogramOpts{
            Name:    "db_pool_wait_duration_seconds",
            Help:    "Time spent waiting for a connection",
            Buckets: prometheus.ExponentialBuckets(0.001, 2, 10),
        },
    )
)

// PoolMonitor периодически собирает метрики пула
type PoolMonitor struct {
    pool   *pgxpool.Pool
    logger *slog.Logger
}

func NewPoolMonitor(pool *pgxpool.Pool, logger *slog.Logger) *PoolMonitor {
    return &PoolMonitor{pool: pool, logger: logger}
}

func (m *PoolMonitor) Start(ctx context.Context) {
    ticker := time.NewTicker(10 * time.Second)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            return
        case <-ticker.C:
            m.collect()
        }
    }
}

func (m *PoolMonitor) collect() {
    stat := m.pool.Stat()

    // Prometheus метрики
    poolConnsTotal.WithLabelValues("acquired").Set(float64(stat.AcquiredConns()))
    poolConnsTotal.WithLabelValues("idle").Set(float64(stat.IdleConns()))
    poolConnsTotal.WithLabelValues("max").Set(float64(stat.MaxConns()))
    poolConnsTotal.WithLabelValues("total").Set(float64(stat.TotalConns()))

    // Логирование для отладки
    m.logger.Debug("pool stats",
        slog.Int32("acquired", stat.AcquiredConns()),
        slog.Int32("idle", stat.IdleConns()),
        slog.Int32("total", stat.TotalConns()),
        slog.Int32("max", stat.MaxConns()),
        slog.Int64("acquire_count", stat.AcquireCount()),
        slog.Duration("acquire_duration", stat.AcquireDuration()),
        slog.Int64("canceled_acquire", stat.CanceledAcquireCount()),
    )

    // Алерт при высокой утилизации
    utilization := float64(stat.AcquiredConns()) / float64(stat.MaxConns())
    if utilization > 0.8 {
        m.logger.Warn("high pool utilization",
            slog.Float64("utilization", utilization),
        )
    }
}

// Middleware для измерения времени ожидания
func (m *PoolMonitor) AcquireWithMetrics(ctx context.Context) (*pgxpool.Conn, error) {
    start := time.Now()
    conn, err := m.pool.Acquire(ctx)
    poolWaitDuration.Observe(time.Since(start).Seconds())
    return conn, err
}
```

### Pool Statistics

pgxpool предоставляет богатую статистику:

```go
stat := pool.Stat()

// Соединения
stat.TotalConns()      // Всего соединений
stat.AcquiredConns()   // Занятые соединения
stat.IdleConns()       // Свободные соединения
stat.MaxConns()        // Максимум соединений

// Операции
stat.AcquireCount()        // Сколько раз запрашивали соединение
stat.AcquireDuration()     // Суммарное время ожидания
stat.CanceledAcquireCount() // Отменённые запросы соединений
stat.EmptyAcquireCount()   // Запросы, когда пул был пуст

// Создание/закрытие
stat.NewConnsCount()        // Сколько соединений создано
stat.MaxLifetimeDestroyCount() // Закрыто по MaxConnLifetime
stat.MaxIdleDestroyCount()    // Закрыто по MaxConnIdleTime
```

### Graceful Shutdown

Правильное завершение работы критично для избежания прерванных транзакций.

```go
package main

import (
    "context"
    "log/slog"
    "os"
    "os/signal"
    "syscall"
    "time"

    "github.com/jackc/pgx/v5/pgxpool"
)

func main() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    pool, err := NewPool(ctx, DefaultConfig())
    if err != nil {
        slog.Error("failed to create pool", slog.String("error", err.Error()))
        os.Exit(1)
    }

    // Запуск сервера...
    server := startServer(pool)

    // Ожидание сигнала завершения
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    slog.Info("shutting down...")

    // 1. Прекращаем принимать новые запросы
    shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer shutdownCancel()

    if err := server.Shutdown(shutdownCtx); err != nil {
        slog.Error("server shutdown failed", slog.String("error", err.Error()))
    }

    // 2. Закрываем пул соединений
    // pool.Close() ждёт завершения всех acquired соединений
    pool.Close()

    slog.Info("shutdown complete")
}

// Альтернатива: drain connections с timeout
func drainPool(pool *pgxpool.Pool, timeout time.Duration) error {
    ctx, cancel := context.WithTimeout(context.Background(), timeout)
    defer cancel()

    // Ждём, пока все соединения освободятся
    ticker := time.NewTicker(100 * time.Millisecond)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            pool.Close()
            return ctx.Err()
        case <-ticker.C:
            if pool.Stat().AcquiredConns() == 0 {
                pool.Close()
                return nil
            }
        }
    }
}
```

### Health Checks

```go
import (
    "context"
    "time"

    "github.com/jackc/pgx/v5/pgxpool"
)

type HealthChecker struct {
    pool *pgxpool.Pool
}

func NewHealthChecker(pool *pgxpool.Pool) *HealthChecker {
    return &HealthChecker{pool: pool}
}

// Simple ping check
func (h *HealthChecker) Ping(ctx context.Context) error {
    return h.pool.Ping(ctx)
}

// Detailed health check
func (h *HealthChecker) Check(ctx context.Context) HealthStatus {
    status := HealthStatus{
        Healthy: true,
        Details: make(map[string]any),
    }

    // Pool stats
    stat := h.pool.Stat()
    status.Details["pool"] = map[string]any{
        "total":    stat.TotalConns(),
        "acquired": stat.AcquiredConns(),
        "idle":     stat.IdleConns(),
        "max":      stat.MaxConns(),
    }

    // Check pool utilization
    utilization := float64(stat.AcquiredConns()) / float64(stat.MaxConns())
    if utilization > 0.9 {
        status.Healthy = false
        status.Details["warning"] = "pool near capacity"
    }

    // Try to execute a query
    start := time.Now()
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()

    var result int
    err := h.pool.QueryRow(ctx, "SELECT 1").Scan(&result)
    queryDuration := time.Since(start)

    status.Details["query_latency_ms"] = queryDuration.Milliseconds()

    if err != nil {
        status.Healthy = false
        status.Details["error"] = err.Error()
    }

    // Check for slow queries
    if queryDuration > time.Second {
        status.Details["warning"] = "slow query response"
    }

    return status
}

type HealthStatus struct {
    Healthy bool
    Details map[string]any
}

// HTTP handler для health check
func (h *HealthChecker) HTTPHandler(w http.ResponseWriter, r *http.Request) {
    status := h.Check(r.Context())

    w.Header().Set("Content-Type", "application/json")
    if !status.Healthy {
        w.WriteHeader(http.StatusServiceUnavailable)
    }

    json.NewEncoder(w).Encode(status)
}
```

### Connection Warming

При старте сервиса полезно "прогреть" пул соединений:

```go
func WarmPool(ctx context.Context, pool *pgxpool.Pool, minConns int) error {
    // Захватываем соединения для инициализации
    conns := make([]*pgxpool.Conn, 0, minConns)

    for i := 0; i < minConns; i++ {
        conn, err := pool.Acquire(ctx)
        if err != nil {
            // Освобождаем уже захваченные
            for _, c := range conns {
                c.Release()
            }
            return fmt.Errorf("warm pool: %w", err)
        }
        conns = append(conns, conn)
    }

    // Освобождаем соединения обратно в пул
    for _, conn := range conns {
        conn.Release()
    }

    slog.Info("pool warmed", slog.Int("connections", len(conns)))
    return nil
}

// Использование
func main() {
    pool, _ := NewPool(ctx, cfg)

    // Прогреваем пул перед приёмом трафика
    if err := WarmPool(ctx, pool, 10); err != nil {
        slog.Warn("pool warming failed", slog.String("error", err.Error()))
    }

    // Теперь готовы принимать трафик
    startServer(pool)
}

---

## Продвинутый sqlc

В [разделе 3.3](../part3-web-api/03_database.md) мы рассмотрели основы sqlc. Здесь — продвинутые паттерны для production.

### Сложные запросы

#### CTE (Common Table Expressions)

```sql
-- queries/analytics.sql

-- name: GetUserOrderStats :many
-- Статистика заказов пользователей с CTE
WITH order_stats AS (
    SELECT
        user_id,
        COUNT(*) as total_orders,
        SUM(total_amount) as total_spent,
        AVG(total_amount) as avg_order_value,
        MAX(created_at) as last_order_at
    FROM orders
    WHERE status = 'completed'
    GROUP BY user_id
),
user_rank AS (
    SELECT
        user_id,
        total_spent,
        RANK() OVER (ORDER BY total_spent DESC) as spending_rank
    FROM order_stats
)
SELECT
    u.id,
    u.email,
    u.name,
    COALESCE(os.total_orders, 0)::int as total_orders,
    COALESCE(os.total_spent, 0)::numeric as total_spent,
    COALESCE(os.avg_order_value, 0)::numeric as avg_order_value,
    os.last_order_at,
    COALESCE(ur.spending_rank, 0)::int as spending_rank
FROM users u
LEFT JOIN order_stats os ON u.id = os.user_id
LEFT JOIN user_rank ur ON u.id = ur.user_id
WHERE u.deleted_at IS NULL
ORDER BY os.total_spent DESC NULLS LAST
LIMIT sqlc.arg(limit_count)::int;
```

#### Window Functions

```sql
-- queries/reports.sql

-- name: GetSalesReport :many
-- Отчёт с накопительным итогом и скользящим средним
SELECT
    date_trunc('day', created_at)::date as order_date,
    COUNT(*) as order_count,
    SUM(total_amount) as daily_revenue,
    -- Накопительный итог
    SUM(SUM(total_amount)) OVER (
        ORDER BY date_trunc('day', created_at)
    ) as cumulative_revenue,
    -- Скользящее среднее за 7 дней
    AVG(SUM(total_amount)) OVER (
        ORDER BY date_trunc('day', created_at)
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as moving_avg_7d
FROM orders
WHERE created_at >= sqlc.arg(start_date)::timestamp
  AND created_at < sqlc.arg(end_date)::timestamp
  AND status = 'completed'
GROUP BY date_trunc('day', created_at)
ORDER BY order_date;

-- name: GetProductRankByCategory :many
-- Ранжирование продуктов внутри категории
SELECT
    p.id,
    p.name,
    p.category_id,
    c.name as category_name,
    p.price,
    p.sales_count,
    ROW_NUMBER() OVER (
        PARTITION BY p.category_id
        ORDER BY p.sales_count DESC
    ) as rank_in_category,
    PERCENT_RANK() OVER (
        PARTITION BY p.category_id
        ORDER BY p.sales_count DESC
    ) as percentile
FROM products p
JOIN categories c ON p.category_id = c.id
WHERE p.active = true;
```

#### Recursive CTE

```sql
-- queries/categories.sql

-- name: GetCategoryTree :many
-- Получение дерева категорий (иерархия)
WITH RECURSIVE category_tree AS (
    -- Базовый случай: корневые категории
    SELECT
        id,
        name,
        parent_id,
        0 as depth,
        ARRAY[id] as path,
        name as full_path
    FROM categories
    WHERE parent_id IS NULL

    UNION ALL

    -- Рекурсивный случай: дочерние категории
    SELECT
        c.id,
        c.name,
        c.parent_id,
        ct.depth + 1,
        ct.path || c.id,
        ct.full_path || ' > ' || c.name
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT
    id,
    name,
    parent_id,
    depth,
    path,
    full_path
FROM category_tree
ORDER BY path;

-- name: GetCategoryDescendants :many
-- Получение всех потомков категории
WITH RECURSIVE descendants AS (
    SELECT id, name, parent_id
    FROM categories
    WHERE id = sqlc.arg(category_id)

    UNION ALL

    SELECT c.id, c.name, c.parent_id
    FROM categories c
    JOIN descendants d ON c.parent_id = d.id
)
SELECT * FROM descendants
WHERE id != sqlc.arg(category_id);
```

### Dynamic Queries

sqlc поддерживает динамические запросы через `sqlc.narg()` и `sqlc.slice()`.

#### Optional Filters с sqlc.narg()

```sql
-- queries/users.sql

-- name: SearchUsers :many
-- Поиск с опциональными фильтрами
SELECT id, email, name, role, created_at
FROM users
WHERE deleted_at IS NULL
  AND (sqlc.narg(email)::text IS NULL OR email ILIKE sqlc.narg(email))
  AND (sqlc.narg(name)::text IS NULL OR name ILIKE sqlc.narg(name))
  AND (sqlc.narg(role)::text IS NULL OR role = sqlc.narg(role))
  AND (sqlc.narg(created_after)::timestamp IS NULL OR created_at >= sqlc.narg(created_after))
  AND (sqlc.narg(created_before)::timestamp IS NULL OR created_at < sqlc.narg(created_before))
ORDER BY
    CASE WHEN sqlc.narg(sort_by)::text = 'email' THEN email END,
    CASE WHEN sqlc.narg(sort_by)::text = 'name' THEN name END,
    CASE WHEN sqlc.narg(sort_by)::text = 'created_at' OR sqlc.narg(sort_by)::text IS NULL THEN created_at END DESC
LIMIT sqlc.arg(limit_count)
OFFSET sqlc.arg(offset_count);
```

```go
// Сгенерированный код
type SearchUsersParams struct {
    Email         pgtype.Text      `json:"email"`
    Name          pgtype.Text      `json:"name"`
    Role          pgtype.Text      `json:"role"`
    CreatedAfter  pgtype.Timestamp `json:"created_after"`
    CreatedBefore pgtype.Timestamp `json:"created_before"`
    SortBy        pgtype.Text      `json:"sort_by"`
    LimitCount    int32            `json:"limit_count"`
    OffsetCount   int32            `json:"offset_count"`
}

// Использование
func (s *UserService) Search(ctx context.Context, filter UserFilter) ([]User, error) {
    params := db.SearchUsersParams{
        LimitCount:  int32(filter.Limit),
        OffsetCount: int32(filter.Offset),
    }

    // Устанавливаем только заданные фильтры
    if filter.Email != "" {
        params.Email = pgtype.Text{String: "%" + filter.Email + "%", Valid: true}
    }
    if filter.Name != "" {
        params.Name = pgtype.Text{String: "%" + filter.Name + "%", Valid: true}
    }
    if filter.Role != "" {
        params.Role = pgtype.Text{String: filter.Role, Valid: true}
    }
    if !filter.CreatedAfter.IsZero() {
        params.CreatedAfter = pgtype.Timestamp{Time: filter.CreatedAfter, Valid: true}
    }

    return s.queries.SearchUsers(ctx, params)
}
```

#### Arrays с sqlc.slice()

```sql
-- queries/products.sql

-- name: GetProductsByIDs :many
-- Получение продуктов по списку ID
SELECT * FROM products
WHERE id = ANY(sqlc.slice(ids)::int[])
ORDER BY array_position(sqlc.slice(ids)::int[], id);

-- name: GetProductsByTags :many
-- Продукты с любым из указанных тегов
SELECT DISTINCT p.*
FROM products p
WHERE p.tags && sqlc.slice(tags)::text[]
  AND p.active = true;

-- name: GetProductsWithAllTags :many
-- Продукты со ВСЕМИ указанными тегами
SELECT * FROM products
WHERE tags @> sqlc.slice(tags)::text[]
  AND active = true;
```

```go
// Использование
products, err := queries.GetProductsByIDs(ctx, []int32{1, 2, 3, 4, 5})

products, err = queries.GetProductsByTags(ctx, []string{"electronics", "sale"})
```

### Транзакции в sqlc

sqlc генерирует метод `WithTx` для работы с транзакциями.

```go
// Паттерн: транзакции с sqlc
func (s *OrderService) CreateOrder(ctx context.Context, order CreateOrderRequest) (*Order, error) {
    // Начинаем транзакцию
    tx, err := s.pool.Begin(ctx)
    if err != nil {
        return nil, fmt.Errorf("begin tx: %w", err)
    }
    defer tx.Rollback(ctx)

    // Создаём queries с транзакцией
    qtx := s.queries.WithTx(tx)

    // 1. Создаём заказ
    dbOrder, err := qtx.CreateOrder(ctx, db.CreateOrderParams{
        UserID:      order.UserID,
        TotalAmount: order.Total,
        Status:      "pending",
    })
    if err != nil {
        return nil, fmt.Errorf("create order: %w", err)
    }

    // 2. Добавляем позиции заказа
    for _, item := range order.Items {
        _, err := qtx.CreateOrderItem(ctx, db.CreateOrderItemParams{
            OrderID:   dbOrder.ID,
            ProductID: item.ProductID,
            Quantity:  item.Quantity,
            Price:     item.Price,
        })
        if err != nil {
            return nil, fmt.Errorf("create order item: %w", err)
        }

        // 3. Уменьшаем остатки
        err = qtx.DecrementStock(ctx, db.DecrementStockParams{
            ProductID: item.ProductID,
            Quantity:  item.Quantity,
        })
        if err != nil {
            return nil, fmt.Errorf("decrement stock: %w", err)
        }
    }

    // Коммитим транзакцию
    if err := tx.Commit(ctx); err != nil {
        return nil, fmt.Errorf("commit: %w", err)
    }

    return mapOrder(dbOrder), nil
}
```

#### Transaction Manager

Для переиспользования логики транзакций:

```go
// internal/database/txmanager.go
package database

import (
    "context"
    "fmt"

    "github.com/jackc/pgx/v5"
    "github.com/jackc/pgx/v5/pgxpool"
    "myapp/internal/db"
)

type TxManager struct {
    pool *pgxpool.Pool
}

func NewTxManager(pool *pgxpool.Pool) *TxManager {
    return &TxManager{pool: pool}
}

// TxFunc — функция, выполняемая в транзакции
type TxFunc func(ctx context.Context, q *db.Queries) error

// WithTx выполняет функцию в транзакции
func (m *TxManager) WithTx(ctx context.Context, fn TxFunc) error {
    tx, err := m.pool.Begin(ctx)
    if err != nil {
        return fmt.Errorf("begin: %w", err)
    }
    defer tx.Rollback(ctx)

    q := db.New(tx)
    if err := fn(ctx, q); err != nil {
        return err
    }

    return tx.Commit(ctx)
}

// WithTxResult — с возвратом результата
func WithTxResult[T any](
    m *TxManager,
    ctx context.Context,
    fn func(ctx context.Context, q *db.Queries) (T, error),
) (T, error) {
    var result T

    tx, err := m.pool.Begin(ctx)
    if err != nil {
        return result, fmt.Errorf("begin: %w", err)
    }
    defer tx.Rollback(ctx)

    q := db.New(tx)
    result, err = fn(ctx, q)
    if err != nil {
        return result, err
    }

    if err := tx.Commit(ctx); err != nil {
        return result, fmt.Errorf("commit: %w", err)
    }

    return result, nil
}

// Использование
func (s *OrderService) CreateOrder(ctx context.Context, req CreateOrderRequest) (*Order, error) {
    return WithTxResult(s.txManager, ctx, func(ctx context.Context, q *db.Queries) (*Order, error) {
        order, err := q.CreateOrder(ctx, db.CreateOrderParams{...})
        if err != nil {
            return nil, err
        }
        // ... остальная логика
        return mapOrder(order), nil
    })
}
```

### Batch Operations в sqlc

sqlc поддерживает batch queries через `pgx.Batch`.

```sql
-- queries/users.sql

-- name: CreateUser :one
INSERT INTO users (email, name, role)
VALUES ($1, $2, $3)
RETURNING *;

-- name: CreateUsersBatch :batchone
INSERT INTO users (email, name, role)
VALUES ($1, $2, $3)
RETURNING *;
```

```go
// Сгенерированный batch код
type CreateUsersBatchParams struct {
    Email string
    Name  string
    Role  string
}

func (q *Queries) CreateUsersBatch(ctx context.Context, arg []CreateUsersBatchParams) *CreateUsersBatchResults {
    batch := &pgx.Batch{}
    for _, a := range arg {
        batch.Queue(createUsersBatch, a.Email, a.Name, a.Role)
    }
    return &CreateUsersBatchResults{br: q.db.SendBatch(ctx, batch), ind: -1}
}

// Использование
func (s *UserService) BulkCreate(ctx context.Context, users []CreateUserRequest) ([]User, error) {
    params := make([]db.CreateUsersBatchParams, len(users))
    for i, u := range users {
        params[i] = db.CreateUsersBatchParams{
            Email: u.Email,
            Name:  u.Name,
            Role:  u.Role,
        }
    }

    results := s.queries.CreateUsersBatch(ctx, params)
    defer results.Close()

    var created []User
    for results.Next() {
        user, err := results.One()
        if err != nil {
            return nil, fmt.Errorf("batch result: %w", err)
        }
        created = append(created, mapUser(user))
    }

    return created, nil
}
```

### Custom Types и Overrides

sqlc позволяет переопределять типы Go для колонок.

```yaml
# sqlc.yaml
version: "2"
sql:
  - engine: "postgresql"
    queries: "queries/"
    schema: "schema/"
    gen:
      go:
        package: "db"
        out: "internal/db"
        sql_package: "pgx/v5"
        emit_json_tags: true
        overrides:
          # UUID → google/uuid
          - db_type: "uuid"
            go_type:
              import: "github.com/google/uuid"
              type: "UUID"

          # NUMERIC → shopspring/decimal
          - db_type: "numeric"
            go_type:
              import: "github.com/shopspring/decimal"
              type: "Decimal"

          # JSONB → custom type
          - column: "users.metadata"
            go_type:
              import: "myapp/internal/types"
              type: "UserMetadata"

          # Custom enum
          - db_type: "pg_catalog.varchar"
            column: "orders.status"
            go_type:
              import: "myapp/internal/types"
              type: "OrderStatus"

          # Nullable override
          - db_type: "text"
            nullable: true
            go_type:
              type: "string"
              pointer: true
```

```go
// internal/types/types.go
package types

import (
    "database/sql/driver"
    "encoding/json"
    "fmt"
)

// UserMetadata — структурированные метаданные пользователя
type UserMetadata struct {
    Timezone   string            `json:"timezone"`
    Locale     string            `json:"locale"`
    Preferences map[string]any   `json:"preferences"`
}

// Scan реализует sql.Scanner
func (m *UserMetadata) Scan(src any) error {
    if src == nil {
        return nil
    }

    switch v := src.(type) {
    case []byte:
        return json.Unmarshal(v, m)
    case string:
        return json.Unmarshal([]byte(v), m)
    default:
        return fmt.Errorf("cannot scan %T into UserMetadata", src)
    }
}

// Value реализует driver.Valuer
func (m UserMetadata) Value() (driver.Value, error) {
    return json.Marshal(m)
}

// OrderStatus — enum для статуса заказа
type OrderStatus string

const (
    OrderStatusPending   OrderStatus = "pending"
    OrderStatusPaid      OrderStatus = "paid"
    OrderStatusShipped   OrderStatus = "shipped"
    OrderStatusDelivered OrderStatus = "delivered"
    OrderStatusCancelled OrderStatus = "cancelled"
)

func (s OrderStatus) IsValid() bool {
    switch s {
    case OrderStatusPending, OrderStatusPaid, OrderStatusShipped,
         OrderStatusDelivered, OrderStatusCancelled:
        return true
    }
    return false
}
```

### sqlc.embed для композиции

```sql
-- queries/orders.sql

-- name: GetOrderWithUser :one
SELECT
    sqlc.embed(orders),
    sqlc.embed(users)
FROM orders
JOIN users ON orders.user_id = users.id
WHERE orders.id = $1;
```

```go
// Сгенерированная структура
type GetOrderWithUserRow struct {
    Order Order // Встроенная структура Order
    User  User  // Встроенная структура User
}

// Использование
row, err := queries.GetOrderWithUser(ctx, orderID)
fmt.Println(row.Order.ID, row.User.Email)
```

### Сравнение sqlc с Dapper (C#)

| Аспект | sqlc (Go) | Dapper (C#) |
|--------|-----------|-------------|
| **Время проверки** | Compile-time | Runtime |
| **SQL** | В .sql файлах | В строках C# |
| **Type safety** | Полная | Частичная |
| **Генерация** | Да (go generate) | Нет |
| **Dynamic queries** | sqlc.narg, sqlc.slice | Анонимные объекты |
| **Transactions** | WithTx | connection.BeginTransaction |
| **Batch** | Встроенный | Через Dapper Plus |

```csharp
// Dapper — runtime SQL, reflection для маппинга
var users = connection.Query<User>(
    "SELECT * FROM users WHERE role = @Role",
    new { Role = "admin" }
);

// Ошибки типов — только в runtime
var users = connection.Query<User>(
    "SELECT * FROM users WHERE role = @Roe", // Typo!
    new { Role = "admin" } // Несоответствие имён!
);
```

```go
// sqlc — compile-time SQL, генерация кода
users, err := queries.ListUsersByRole(ctx, "admin")

// Ошибки типов — при компиляции
// Если SQL некорректный — sqlc generate упадёт с ошибкой
```

---

## Zero-Downtime Migrations

### Опасные операции

При работе с production БД многие операции, которые безобидны в development, могут вызвать даунтайм.

#### Блокировки в PostgreSQL

| Операция | Блокировка | Влияние |
|----------|-----------|---------|
| `ALTER TABLE ... ADD COLUMN` (nullable, без default) | `AccessExclusiveLock` (мгновенно) | Минимальное |
| `ALTER TABLE ... ADD COLUMN ... DEFAULT` (PG < 11) | `AccessExclusiveLock` + перезапись | **Долгая блокировка** |
| `ALTER TABLE ... ADD COLUMN ... DEFAULT` (PG >= 11) | `AccessExclusiveLock` (мгновенно) | Минимальное |
| `ALTER TABLE ... ALTER COLUMN SET NOT NULL` | `AccessExclusiveLock` (scan) | **Блокирует чтение и запись** |
| `ALTER TABLE ... DROP COLUMN` | `AccessExclusiveLock` (мгновенно) | Ломает старый код |
| `CREATE INDEX` | `ShareLock` | **Блокирует запись** |
| `CREATE INDEX CONCURRENTLY` | Без блокировки | Безопасно |
| `ALTER TABLE ... ADD CONSTRAINT` (CHECK, FK) | `AccessExclusiveLock` (scan) | **Долгая блокировка** |
| `DROP TABLE` | `AccessExclusiveLock` | Мгновенно, но необратимо |

> ⚠️ **Критично**: `AccessExclusiveLock` блокирует **все** операции с таблицей — даже `SELECT`. На таблице с миллионами строк это может занять минуты.

**C# аналогия**:
```csharp
// EF Core миграция — может блокировать таблицу
migrationBuilder.AddColumn<string>(
    name: "Phone",
    table: "Users",
    nullable: false,
    defaultValue: ""); // ⚠️ Перезаписывает все строки в PG < 11!
```

### Безопасные паттерны

#### 1. Добавление nullable колонки (безопасно)

```sql
-- ✅ Мгновенная операция, не перезаписывает данные
ALTER TABLE users ADD COLUMN phone TEXT;
```

```go
// migrations/000010_add_users_phone.up.sql
ALTER TABLE users ADD COLUMN phone TEXT;

// migrations/000010_add_users_phone.down.sql
ALTER TABLE users DROP COLUMN phone;
```

#### 2. Добавление NOT NULL колонки (3-step pattern)

```sql
-- ❌ ОПАСНО: блокирует таблицу на большой таблице
ALTER TABLE users ADD COLUMN status TEXT NOT NULL DEFAULT 'active';

-- ✅ БЕЗОПАСНО: 3 шага
```

**Шаг 1: Добавить nullable колонку**
```sql
-- migrations/000011_add_status_nullable.up.sql
ALTER TABLE users ADD COLUMN status TEXT;
```

**Шаг 2: Заполнить данные батчами**
```go
// Заполнение данных батчами (не в миграции!)
func BackfillUserStatus(ctx context.Context, pool *pgxpool.Pool) error {
    const batchSize = 10000

    for {
        result, err := pool.Exec(ctx, `
            UPDATE users
            SET status = 'active'
            WHERE id IN (
                SELECT id FROM users
                WHERE status IS NULL
                LIMIT $1
                FOR UPDATE SKIP LOCKED
            )
        `, batchSize)
        if err != nil {
            return fmt.Errorf("backfill: %w", err)
        }

        rowsAffected := result.RowsAffected()
        slog.Info("backfill progress",
            slog.Int64("rows_updated", rowsAffected),
        )

        if rowsAffected == 0 {
            break // Все строки обновлены
        }

        // Небольшая пауза, чтобы не перегружать БД
        time.Sleep(100 * time.Millisecond)
    }

    return nil
}
```

**Шаг 3: Добавить NOT NULL constraint**
```sql
-- migrations/000012_add_status_not_null.up.sql
-- Используем CHECK constraint — валидируется без полной блокировки
ALTER TABLE users ADD CONSTRAINT users_status_not_null
    CHECK (status IS NOT NULL) NOT VALID;

-- Затем валидируем (берёт ShareUpdateExclusiveLock, не блокирует записи)
ALTER TABLE users VALIDATE CONSTRAINT users_status_not_null;

-- Опционально: заменяем CHECK на настоящий NOT NULL
-- (требует AccessExclusiveLock, но мгновенно если CHECK уже validated)
ALTER TABLE users ALTER COLUMN status SET NOT NULL;
ALTER TABLE users DROP CONSTRAINT users_status_not_null;
```

#### 3. Создание индекса без блокировки

```sql
-- ❌ ОПАСНО: ShareLock блокирует INSERT/UPDATE/DELETE
CREATE INDEX idx_users_email ON users(email);

-- ✅ БЕЗОПАСНО: не блокирует DML
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```

> ⚠️ **Важно**: `CREATE INDEX CONCURRENTLY` нельзя выполнять внутри транзакции. Большинство migration tools выполняют каждую миграцию в транзакции, поэтому нужна специальная обработка.

```go
// golang-migrate: используем отдельный файл без транзакции
// migrations/000013_add_users_email_index.up.sql

-- +migrate StatementBegin
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email);
-- +migrate StatementEnd
```

```go
// goose: используем аннотацию для отключения транзакции
// migrations/000013_add_users_email_index.sql

-- +goose Up
-- +goose NO TRANSACTION
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email);

-- +goose Down
DROP INDEX IF EXISTS idx_users_email;
```

#### 4. Безопасное добавление Foreign Key

```sql
-- ❌ ОПАСНО: AccessExclusiveLock + scan всех строк
ALTER TABLE orders ADD CONSTRAINT fk_orders_user
    FOREIGN KEY (user_id) REFERENCES users(id);

-- ✅ БЕЗОПАСНО: два шага
-- Шаг 1: Добавить constraint без валидации (мгновенно)
ALTER TABLE orders ADD CONSTRAINT fk_orders_user
    FOREIGN KEY (user_id) REFERENCES users(id) NOT VALID;

-- Шаг 2: Валидировать (ShareUpdateExclusiveLock — не блокирует записи)
ALTER TABLE orders VALIDATE CONSTRAINT fk_orders_user;
```

#### 5. Переименование колонки (Expand/Contract)

```sql
-- ❌ ОПАСНО: ломает работающее приложение
ALTER TABLE users RENAME COLUMN name TO full_name;
```

### Expand/Contract Pattern

Безопасное изменение схемы в 4 фазы:

```
Phase 1: Expand      — Добавить новую структуру
Phase 2: Migrate     — Перенести данные
Phase 3: Code Switch — Переключить код
Phase 4: Contract    — Удалить старую структуру
```

**Пример: переименование колонки `name` → `full_name`**

```sql
-- Phase 1: Expand (Deploy 1)
ALTER TABLE users ADD COLUMN full_name TEXT;

-- Триггер для синхронизации данных
CREATE OR REPLACE FUNCTION sync_user_name() RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        IF NEW.full_name IS NULL AND NEW.name IS NOT NULL THEN
            NEW.full_name := NEW.name;
        ELSIF NEW.name IS NULL AND NEW.full_name IS NOT NULL THEN
            NEW.name := NEW.full_name;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sync_user_name
    BEFORE INSERT OR UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION sync_user_name();
```

```sql
-- Phase 2: Migrate (между Deploy 1 и Deploy 2)
UPDATE users SET full_name = name WHERE full_name IS NULL;
```

```go
// Phase 3: Code Switch (Deploy 2)
// Код начинает использовать full_name вместо name
type User struct {
    ID       int64
    FullName string `db:"full_name"` // Было: Name string `db:"name"`
}
```

```sql
-- Phase 4: Contract (Deploy 3 — через несколько дней)
DROP TRIGGER trg_sync_user_name ON users;
DROP FUNCTION sync_user_name;
ALTER TABLE users DROP COLUMN name;
```

> 💡 **Для C# разработчиков**: Этот паттерн аналогичен тому, что делает EF Core с "Two-phase migration" — только вручную и с полным контролем.

### Atlas: Declarative Migrations

Atlas — современный инструмент для declarative (а не imperative) миграций.

```bash
# Установка
curl -sSf https://atlasgo.sh | sh
```

#### Декларативный подход

```hcl
# schema.hcl — описываем желаемое состояние
schema "public" {
  table "users" {
    column "id" {
      type = serial
    }
    column "email" {
      type = text
      null = false
    }
    column "name" {
      type = text
      null = false
    }
    column "status" {
      type = text
      null = false
      default = "active"
    }
    column "created_at" {
      type    = timestamptz
      null    = false
      default = sql("now()")
    }

    primary_key {
      columns = [column.id]
    }

    index "idx_users_email" {
      unique  = true
      columns = [column.email]
    }

    index "idx_users_status" {
      columns = [column.status]
    }
  }

  table "orders" {
    column "id" {
      type = serial
    }
    column "user_id" {
      type = integer
      null = false
    }
    column "total_amount" {
      type = numeric
      null = false
    }
    column "status" {
      type = text
      null = false
    }
    column "created_at" {
      type    = timestamptz
      null    = false
      default = sql("now()")
    }

    primary_key {
      columns = [column.id]
    }

    foreign_key "fk_orders_user" {
      columns     = [column.user_id]
      ref_columns = [table.users.column.id]
      on_delete   = CASCADE
    }
  }
}
```

```bash
# Atlas вычисляет разницу и генерирует SQL
atlas schema diff \
  --from "postgres://localhost:5432/mydb?sslmode=disable" \
  --to "file://schema.hcl" \
  --dev-url "docker://postgres/15"

# Применяет миграцию
atlas schema apply \
  --url "postgres://localhost:5432/mydb?sslmode=disable" \
  --to "file://schema.hcl" \
  --dev-url "docker://postgres/15"
```

#### Atlas с Go

```go
// atlas.hcl — конфигурация
variable "db_url" {
  type    = string
  default = getenv("DATABASE_URL")
}

env "production" {
  url = var.db_url
  migration {
    dir = "file://migrations"
  }
  lint {
    destructive {
      error = true
    }
    // Предупреждать об опасных операциях
    data_depend {
      error = true
    }
  }
}
```

```bash
# Lint миграций перед применением
atlas migrate lint --env production

# Проверка: найдёт опасные операции
# Error: destructive change detected:
#   Dropping column "name" from table "users"
```

### Сравнение инструментов миграций

| Аспект | golang-migrate | goose | Atlas |
|--------|---------------|-------|-------|
| **Подход** | Imperative | Imperative | Declarative |
| **SQL файлы** | Отдельные up/down | Один файл | HCL или SQL |
| **Go миграции** | Нет | Да | Да |
| **Lint** | Нет | Нет | Да (опасные операции) |
| **Diff** | Нет | Нет | Автоматический |
| **CONCURRENTLY** | Сложно | `NO TRANSACTION` | Встроено |
| **C# аналог** | DbUp | FluentMigrator | EF Core |

---

## Query Performance

### EXPLAIN ANALYZE из Go

Анализ производительности запросов — ключевой навык для production.

```go
package pgutil

import (
    "context"
    "encoding/json"
    "fmt"
    "log/slog"
    "strings"

    "github.com/jackc/pgx/v5/pgxpool"
)

// QueryPlan представляет план запроса PostgreSQL
type QueryPlan struct {
    Plan              PlanNode `json:"Plan"`
    PlanningTime      float64  `json:"Planning Time"`
    ExecutionTime     float64  `json:"Execution Time"`
    // Triggers
    Triggers          []any    `json:"Triggers"`
}

type PlanNode struct {
    NodeType          string     `json:"Node Type"`
    RelationName      string     `json:"Relation Name"`
    Alias             string     `json:"Alias"`
    StartupCost       float64    `json:"Startup Cost"`
    TotalCost         float64    `json:"Total Cost"`
    PlanRows          int64      `json:"Plan Rows"`
    PlanWidth         int        `json:"Plan Width"`
    ActualStartupTime float64    `json:"Actual Startup Time"`
    ActualTotalTime   float64    `json:"Actual Total Time"`
    ActualRows        int64      `json:"Actual Rows"`
    ActualLoops       int        `json:"Actual Loops"`
    SharedHitBlocks   int64      `json:"Shared Hit Blocks"`
    SharedReadBlocks  int64      `json:"Shared Read Blocks"`
    Plans             []PlanNode `json:"Plans"`
}

// ExplainAnalyze выполняет EXPLAIN ANALYZE и возвращает план
func ExplainAnalyze(ctx context.Context, pool *pgxpool.Pool, query string, args ...any) (*QueryPlan, error) {
    explainQuery := fmt.Sprintf(
        "EXPLAIN (ANALYZE, FORMAT JSON, BUFFERS, TIMING) %s",
        query,
    )

    var planJSON string
    err := pool.QueryRow(ctx, explainQuery, args...).Scan(&planJSON)
    if err != nil {
        return nil, fmt.Errorf("explain: %w", err)
    }

    var plans []QueryPlan
    if err := json.Unmarshal([]byte(planJSON), &plans); err != nil {
        return nil, fmt.Errorf("parse plan: %w", err)
    }

    if len(plans) == 0 {
        return nil, fmt.Errorf("empty plan")
    }

    return &plans[0], nil
}

// LogSlowQuery анализирует и логирует медленные запросы
func LogSlowQuery(ctx context.Context, pool *pgxpool.Pool, logger *slog.Logger,
    query string, threshold float64, args ...any) {

    plan, err := ExplainAnalyze(ctx, pool, query, args...)
    if err != nil {
        logger.Error("explain failed", slog.String("error", err.Error()))
        return
    }

    if plan.ExecutionTime > threshold {
        logger.Warn("slow query detected",
            slog.String("query", query),
            slog.Float64("execution_time_ms", plan.ExecutionTime),
            slog.Float64("planning_time_ms", plan.PlanningTime),
            slog.String("node_type", plan.Plan.NodeType),
            slog.Int64("actual_rows", plan.Plan.ActualRows),
            slog.Int64("planned_rows", plan.Plan.PlanRows),
        )

        // Проверяем проблемные паттерны
        checkPlanIssues(logger, &plan.Plan, 0)
    }
}

func checkPlanIssues(logger *slog.Logger, node *PlanNode, depth int) {
    // Seq Scan на большой таблице
    if node.NodeType == "Seq Scan" && node.ActualRows > 10000 {
        logger.Warn("sequential scan on large table",
            slog.String("table", node.RelationName),
            slog.Int64("rows", node.ActualRows),
            slog.String("suggestion", "consider adding an index"),
        )
    }

    // Большая разница между planned и actual rows (плохая статистика)
    if node.PlanRows > 0 && node.ActualRows > 0 {
        ratio := float64(node.ActualRows) / float64(node.PlanRows)
        if ratio > 10 || ratio < 0.1 {
            logger.Warn("row estimate mismatch",
                slog.Int64("planned", node.PlanRows),
                slog.Int64("actual", node.ActualRows),
                slog.Float64("ratio", ratio),
                slog.String("suggestion", "run ANALYZE on the table"),
            )
        }
    }

    // Много disk reads (buffer cache miss)
    if node.SharedReadBlocks > 0 {
        hitRatio := float64(node.SharedHitBlocks) /
            float64(node.SharedHitBlocks+node.SharedReadBlocks)
        if hitRatio < 0.95 {
            logger.Warn("low buffer cache hit ratio",
                slog.Float64("hit_ratio", hitRatio),
                slog.Int64("read_blocks", node.SharedReadBlocks),
                slog.String("suggestion", "increase shared_buffers or check query"),
            )
        }
    }

    // Рекурсивно проверяем дочерние узлы
    for i := range node.Plans {
        checkPlanIssues(logger, &node.Plans[i], depth+1)
    }
}
```

### Чтение планов запросов

```
-- Типы сканирования (от лучшего к худшему)
Index Only Scan  → Данные читаются из индекса (лучший)
Index Scan       → Индекс + heap lookup
Bitmap Scan      → Индекс + bitmap + heap
Seq Scan         → Полное сканирование (худший для больших таблиц)

-- Типы соединений
Nested Loop      → O(n*m) — хорошо для малых таблиц / индексного доступа
Hash Join        → O(n+m) — хорошо для больших таблиц
Merge Join       → O(n+m) — хорошо для отсортированных данных
```

```sql
-- Пример: плохой план
EXPLAIN ANALYZE
SELECT * FROM orders o
JOIN users u ON o.user_id = u.id
WHERE u.email = 'user@example.com';

-- Результат:
-- Nested Loop (cost=0.56..16.61 rows=1 width=...)
--   -> Index Scan using idx_users_email on users u (cost=0.28..8.30 rows=1 width=...)
--        Index Cond: (email = 'user@example.com')
--   -> Index Scan using idx_orders_user_id on orders o (cost=0.28..8.30 rows=1 width=...)
--        Index Cond: (user_id = u.id)
-- Planning Time: 0.182 ms
-- Execution Time: 0.045 ms   ✅ Быстро
```

```sql
-- Пример: плохой план (без индекса)
EXPLAIN ANALYZE
SELECT * FROM orders WHERE status = 'pending';

-- Результат:
-- Seq Scan on orders (cost=0.00..25000.00 rows=50000 width=...)
--   Filter: (status = 'pending')
--   Rows Removed by Filter: 950000
-- Planning Time: 0.100 ms
-- Execution Time: 1250.000 ms   ❌ Медленно — Seq Scan на 1M строк
```

### Типы индексов

```sql
-- B-tree (default) — для операторов =, <, >, <=, >=, BETWEEN, IN, LIKE 'prefix%'
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_created ON orders(created_at DESC);

-- Composite index — порядок важен!
CREATE INDEX idx_orders_user_status ON orders(user_id, status);
-- ✅ Работает для: WHERE user_id = 1
-- ✅ Работает для: WHERE user_id = 1 AND status = 'pending'
-- ❌ НЕ работает для: WHERE status = 'pending' (нужен отдельный индекс)

-- Partial index — индексирует только часть строк
CREATE INDEX idx_orders_pending ON orders(created_at)
    WHERE status = 'pending';
-- Меньший размер, быстрее обновляется

-- Covering index (INCLUDE) — PG 11+
CREATE INDEX idx_orders_user_covering ON orders(user_id)
    INCLUDE (status, total_amount);
-- Index Only Scan — не нужно обращаться к heap

-- GIN (Generalized Inverted Index) — для массивов, JSONB, full-text
CREATE INDEX idx_products_tags ON products USING GIN(tags);
CREATE INDEX idx_products_metadata ON products USING GIN(metadata jsonb_path_ops);

-- GiST — для геоданных, диапазонов
CREATE INDEX idx_events_period ON events USING GiST(
    tstzrange(start_time, end_time)
);

-- BRIN (Block Range Index) — для больших таблиц с естественной сортировкой
CREATE INDEX idx_logs_created ON logs USING BRIN(created_at);
-- Очень маленький индекс, хорош для append-only таблиц
```

### Сравнение индексов с SQL Server (C#)

| PostgreSQL | SQL Server | Использование |
|-----------|------------|---------------|
| B-tree | Clustered/Non-clustered | Основной тип |
| Partial Index | Filtered Index | WHERE condition |
| Covering (INCLUDE) | Covering Index (INCLUDE) | Index Only Scan |
| GIN | Full-Text Index | Массивы, JSONB, FTS |
| GiST | Spatial Index | Геоданные |
| BRIN | — (нет аналога) | Append-only таблицы |

### Query Tuning

#### Connection-level settings

```go
// Настройки на уровне соединения для тяжёлых запросов
func ExecuteHeavyQuery(ctx context.Context, pool *pgxpool.Pool) error {
    conn, err := pool.Acquire(ctx)
    if err != nil {
        return err
    }
    defer conn.Release()

    // Увеличиваем work_mem для этого запроса
    // (используется для сортировок и хэш-таблиц)
    _, err = conn.Exec(ctx, "SET LOCAL work_mem = '256MB'")
    if err != nil {
        return err
    }

    // Увеличиваем таймаут
    _, err = conn.Exec(ctx, "SET LOCAL statement_timeout = '120s'")
    if err != nil {
        return err
    }

    // Выполняем тяжёлый запрос
    rows, err := conn.Query(ctx, `
        SELECT ...
        FROM large_table
        ORDER BY complex_expression
    `)
    // ...

    return nil
}
```

#### Параллельные запросы PostgreSQL

```go
// PostgreSQL может выполнять запрос параллельно (PG 9.6+)
// Настройки контролируют это поведение

func ConfigureParallelQueries(ctx context.Context, pool *pgxpool.Pool) {
    // Runtime params для всех соединений
    poolConfig.ConnConfig.RuntimeParams = map[string]string{
        // Максимум воркеров на запрос
        "max_parallel_workers_per_gather": "4",

        // Минимальный размер таблицы для параллельного сканирования
        "min_parallel_table_scan_size": "8MB",

        // Минимальный размер индекса для параллельного сканирования
        "min_parallel_index_scan_size": "512kB",
    }
}
```

### pg_stat_statements

Расширение для мониторинга всех запросов к БД.

```sql
-- Включение расширения
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

```go
// Получение Top-N медленных запросов
type SlowQuery struct {
    Query          string
    Calls          int64
    TotalTimeMs    float64
    MeanTimeMs     float64
    MaxTimeMs      float64
    Rows           int64
    SharedBlksHit  int64
    SharedBlksRead int64
}

func GetSlowQueries(ctx context.Context, pool *pgxpool.Pool, limit int) ([]SlowQuery, error) {
    rows, err := pool.Query(ctx, `
        SELECT
            query,
            calls,
            total_exec_time as total_time_ms,
            mean_exec_time as mean_time_ms,
            max_exec_time as max_time_ms,
            rows,
            shared_blks_hit,
            shared_blks_read
        FROM pg_stat_statements
        WHERE query NOT LIKE '%pg_stat_statements%'
        ORDER BY total_exec_time DESC
        LIMIT $1
    `, limit)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var queries []SlowQuery
    for rows.Next() {
        var q SlowQuery
        err := rows.Scan(
            &q.Query, &q.Calls, &q.TotalTimeMs,
            &q.MeanTimeMs, &q.MaxTimeMs, &q.Rows,
            &q.SharedBlksHit, &q.SharedBlksRead,
        )
        if err != nil {
            return nil, err
        }
        queries = append(queries, q)
    }

    return queries, rows.Err()
}

// Утилита для анализа
func AnalyzeSlowQueries(ctx context.Context, pool *pgxpool.Pool, logger *slog.Logger) {
    queries, err := GetSlowQueries(ctx, pool, 20)
    if err != nil {
        logger.Error("failed to get slow queries", slog.String("error", err.Error()))
        return
    }

    for _, q := range queries {
        // Buffer cache hit ratio
        totalBlocks := q.SharedBlksHit + q.SharedBlksRead
        var hitRatio float64
        if totalBlocks > 0 {
            hitRatio = float64(q.SharedBlksHit) / float64(totalBlocks) * 100
        }

        logger.Info("slow query",
            slog.String("query", truncate(q.Query, 100)),
            slog.Int64("calls", q.Calls),
            slog.Float64("total_time_ms", q.TotalTimeMs),
            slog.Float64("mean_time_ms", q.MeanTimeMs),
            slog.Float64("max_time_ms", q.MaxTimeMs),
            slog.Float64("cache_hit_ratio", hitRatio),
        )
    }
}

func truncate(s string, maxLen int) string {
    if len(s) <= maxLen {
        return s
    }
    return s[:maxLen] + "..."
}
```

### Auto EXPLAIN

Автоматическое логирование планов медленных запросов:

```sql
-- postgresql.conf
shared_preload_libraries = 'auto_explain'
auto_explain.log_min_duration = '100ms'  -- Логировать запросы > 100ms
auto_explain.log_analyze = true          -- Включить ANALYZE
auto_explain.log_buffers = true          -- Включить buffer stats
auto_explain.log_format = 'json'         -- JSON формат
auto_explain.log_nested_statements = true
```

```go
// Программная активация для конкретного соединения
func EnableAutoExplain(ctx context.Context, conn *pgx.Conn) error {
    _, err := conn.Exec(ctx, `
        LOAD 'auto_explain';
        SET auto_explain.log_min_duration = '50ms';
        SET auto_explain.log_analyze = true;
    `)
    return err
}
```

---

## High Availability

### Read Replicas

В production часто используют read replicas для масштабирования чтения. В Go это реализуется через маршрутизацию запросов.

```go
package postgres

import (
    "context"
    "fmt"
    "math/rand"
    "sync/atomic"

    "github.com/jackc/pgx/v5/pgxpool"
)

// DBCluster управляет primary и replica соединениями
type DBCluster struct {
    primary  *pgxpool.Pool
    replicas []*pgxpool.Pool
    counter  atomic.Uint64 // для round-robin
}

func NewDBCluster(ctx context.Context, primaryDSN string, replicaDSNs []string) (*DBCluster, error) {
    primary, err := pgxpool.New(ctx, primaryDSN)
    if err != nil {
        return nil, fmt.Errorf("connect primary: %w", err)
    }

    replicas := make([]*pgxpool.Pool, 0, len(replicaDSNs))
    for _, dsn := range replicaDSNs {
        replica, err := pgxpool.New(ctx, dsn)
        if err != nil {
            // Закрываем уже открытые соединения
            primary.Close()
            for _, r := range replicas {
                r.Close()
            }
            return nil, fmt.Errorf("connect replica: %w", err)
        }
        replicas = append(replicas, replica)
    }

    return &DBCluster{
        primary:  primary,
        replicas: replicas,
    }, nil
}

// Primary возвращает пул для записи
func (c *DBCluster) Primary() *pgxpool.Pool {
    return c.primary
}

// Replica возвращает пул для чтения (round-robin)
func (c *DBCluster) Replica() *pgxpool.Pool {
    if len(c.replicas) == 0 {
        return c.primary // Fallback на primary
    }

    idx := c.counter.Add(1) % uint64(len(c.replicas))
    return c.replicas[idx]
}

// ReplicaRandom возвращает случайную реплику
func (c *DBCluster) ReplicaRandom() *pgxpool.Pool {
    if len(c.replicas) == 0 {
        return c.primary
    }
    return c.replicas[rand.Intn(len(c.replicas))]
}

// Close закрывает все соединения
func (c *DBCluster) Close() {
    c.primary.Close()
    for _, r := range c.replicas {
        r.Close()
    }
}
```

#### Context-based routing

```go
// Маршрутизация через context
type ctxKey string

const readOnlyKey ctxKey = "read_only"

// WithReadOnly помечает запрос как read-only
func WithReadOnly(ctx context.Context) context.Context {
    return context.WithValue(ctx, readOnlyKey, true)
}

func IsReadOnly(ctx context.Context) bool {
    v, ok := ctx.Value(readOnlyKey).(bool)
    return ok && v
}

// Repository с автоматической маршрутизацией
type UserRepository struct {
    cluster *DBCluster
}

func (r *UserRepository) pool(ctx context.Context) *pgxpool.Pool {
    if IsReadOnly(ctx) {
        return r.cluster.Replica()
    }
    return r.cluster.Primary()
}

func (r *UserRepository) GetByID(ctx context.Context, id int64) (*User, error) {
    // Чтение → используем реплику
    ctx = WithReadOnly(ctx)

    var u User
    err := r.pool(ctx).QueryRow(ctx,
        "SELECT id, email, name FROM users WHERE id = $1", id,
    ).Scan(&u.ID, &u.Email, &u.Name)

    return &u, err
}

func (r *UserRepository) Create(ctx context.Context, user *User) error {
    // Запись → используем primary (по умолчанию)
    _, err := r.pool(ctx).Exec(ctx,
        "INSERT INTO users (email, name) VALUES ($1, $2)",
        user.Email, user.Name,
    )
    return err
}
```

> 💡 **Для C# разработчиков**: Аналог в EF Core — это `context.Database.UseTransaction()` с read-only connection, или split read/write DbContext. В Go подход более явный.

### Connection String для HA

PostgreSQL поддерживает multi-host connection strings:

```go
// Multi-host connection string — pgx попробует каждый хост
primaryDSN := "postgres://user:pass@host1:5432,host2:5432/mydb?target_session_attrs=read-write"

// Для реплик
replicaDSN := "postgres://user:pass@replica1:5432,replica2:5432/mydb?target_session_attrs=read-only"
```

| Параметр | Значение | Описание |
|----------|----------|----------|
| `target_session_attrs` | `read-write` | Primary (для записи) |
| `target_session_attrs` | `read-only` | Replica (для чтения) |
| `target_session_attrs` | `any` | Любой доступный |
| `target_session_attrs` | `primary` | Только primary |
| `target_session_attrs` | `standby` | Только standby |

### Retry Strategies

Транзиентные ошибки — нормальная часть production. Нужна стратегия повторных попыток.

```go
package pgutil

import (
    "context"
    "errors"
    "math"
    "math/rand"
    "time"

    "github.com/jackc/pgx/v5/pgconn"
)

// RetryConfig настройки повторных попыток
type RetryConfig struct {
    MaxRetries     int
    InitialBackoff time.Duration
    MaxBackoff     time.Duration
    Multiplier     float64
    Jitter         bool
}

func DefaultRetryConfig() RetryConfig {
    return RetryConfig{
        MaxRetries:     3,
        InitialBackoff: 100 * time.Millisecond,
        MaxBackoff:     5 * time.Second,
        Multiplier:     2.0,
        Jitter:         true,
    }
}

// WithRetry выполняет функцию с повторными попытками
func WithRetry[T any](
    ctx context.Context,
    cfg RetryConfig,
    fn func(ctx context.Context) (T, error),
) (T, error) {
    var result T
    var lastErr error

    for attempt := 0; attempt <= cfg.MaxRetries; attempt++ {
        result, lastErr = fn(ctx)
        if lastErr == nil {
            return result, nil
        }

        // Проверяем, можно ли повторить
        if !IsRetryable(lastErr) {
            return result, lastErr
        }

        // Не ждём после последней попытки
        if attempt == cfg.MaxRetries {
            break
        }

        // Exponential backoff
        backoff := cfg.InitialBackoff * time.Duration(math.Pow(cfg.Multiplier, float64(attempt)))
        if backoff > cfg.MaxBackoff {
            backoff = cfg.MaxBackoff
        }

        // Jitter (случайный разброс для избежания thundering herd)
        if cfg.Jitter {
            backoff = time.Duration(rand.Int63n(int64(backoff)))
        }

        select {
        case <-ctx.Done():
            return result, ctx.Err()
        case <-time.After(backoff):
            // Продолжаем
        }
    }

    return result, fmt.Errorf("max retries exceeded: %w", lastErr)
}

// IsRetryable определяет, можно ли повторить ошибку
func IsRetryable(err error) bool {
    if err == nil {
        return false
    }

    // Context cancelled — не повторяем
    if errors.Is(err, context.Canceled) || errors.Is(err, context.DeadlineExceeded) {
        return false
    }

    // PostgreSQL error codes
    var pgErr *pgconn.PgError
    if errors.As(err, &pgErr) {
        switch pgErr.Code {
        case "40001": // serialization_failure
            return true
        case "40P01": // deadlock_detected
            return true
        case "08000", "08003", "08006": // connection errors
            return true
        case "57P01": // admin_shutdown
            return true
        case "57P03": // cannot_connect_now
            return true
        default:
            return false
        }
    }

    // Ошибки соединения
    if isConnectionError(err) {
        return true
    }

    return false
}

func isConnectionError(err error) bool {
    msg := err.Error()
    connectionErrors := []string{
        "connection refused",
        "connection reset",
        "broken pipe",
        "no such host",
        "connection timed out",
        "EOF",
    }
    for _, ce := range connectionErrors {
        if strings.Contains(msg, ce) {
            return true
        }
    }
    return false
}

// Использование
func (r *OrderRepository) GetByID(ctx context.Context, id int64) (*Order, error) {
    return WithRetry(ctx, DefaultRetryConfig(), func(ctx context.Context) (*Order, error) {
        var o Order
        err := r.pool.QueryRow(ctx,
            "SELECT id, user_id, total_amount FROM orders WHERE id = $1", id,
        ).Scan(&o.ID, &o.UserID, &o.TotalAmount)
        return &o, err
    })
}
```

### Сравнение с Polly (C#)

| Аспект | Go (ручная реализация) | C# (Polly) |
|--------|----------------------|-------------|
| **API** | `WithRetry(ctx, cfg, fn)` | `Policy.Handle<>().WaitAndRetry()` |
| **Jitter** | Ручной | `Backoff.DecorrelatedJitterBackoffV2` |
| **Circuit Breaker** | Ручной или go-circuitbreaker | `Policy.CircuitBreaker()` |
| **Комбинирование** | Вложенные вызовы | `Policy.Wrap()` |
| **Dependency** | Нет | NuGet пакет |

```csharp
// C# Polly
var retryPolicy = Policy
    .Handle<SqlException>(ex => ex.IsTransient)
    .WaitAndRetryAsync(3, attempt =>
        TimeSpan.FromMilliseconds(100 * Math.Pow(2, attempt)));

var result = await retryPolicy.ExecuteAsync(async () =>
    await connection.QueryFirstAsync<Order>(sql, new { Id = id })
);
```

### Circuit Breaker

Circuit Breaker предотвращает перегрузку БД при проблемах.

```go
package pgutil

import (
    "context"
    "errors"
    "sync"
    "time"
)

type CircuitState int

const (
    CircuitClosed   CircuitState = iota // Нормальная работа
    CircuitOpen                          // Все запросы отклоняются
    CircuitHalfOpen                      // Пробный запрос
)

var ErrCircuitOpen = errors.New("circuit breaker is open")

type CircuitBreaker struct {
    mu              sync.RWMutex
    state           CircuitState
    failures        int
    successes       int
    threshold       int           // Порог ошибок для открытия
    halfOpenMax     int           // Макс. пробных запросов
    resetTimeout    time.Duration // Время до перехода в half-open
    lastFailureTime time.Time
}

func NewCircuitBreaker(threshold int, resetTimeout time.Duration) *CircuitBreaker {
    return &CircuitBreaker{
        state:        CircuitClosed,
        threshold:    threshold,
        halfOpenMax:  3,
        resetTimeout: resetTimeout,
    }
}

func (cb *CircuitBreaker) Execute(ctx context.Context, fn func(ctx context.Context) error) error {
    if !cb.allowRequest() {
        return ErrCircuitOpen
    }

    err := fn(ctx)

    if err != nil {
        cb.recordFailure()
    } else {
        cb.recordSuccess()
    }

    return err
}

func (cb *CircuitBreaker) allowRequest() bool {
    cb.mu.RLock()
    defer cb.mu.RUnlock()

    switch cb.state {
    case CircuitClosed:
        return true
    case CircuitOpen:
        // Проверяем, прошло ли время для перехода в half-open
        if time.Since(cb.lastFailureTime) > cb.resetTimeout {
            cb.mu.RUnlock()
            cb.mu.Lock()
            cb.state = CircuitHalfOpen
            cb.successes = 0
            cb.mu.Unlock()
            cb.mu.RLock()
            return true
        }
        return false
    case CircuitHalfOpen:
        return cb.successes < cb.halfOpenMax
    }

    return false
}

func (cb *CircuitBreaker) recordFailure() {
    cb.mu.Lock()
    defer cb.mu.Unlock()

    cb.failures++
    cb.lastFailureTime = time.Now()

    if cb.failures >= cb.threshold {
        cb.state = CircuitOpen
    }
}

func (cb *CircuitBreaker) recordSuccess() {
    cb.mu.Lock()
    defer cb.mu.Unlock()

    if cb.state == CircuitHalfOpen {
        cb.successes++
        if cb.successes >= cb.halfOpenMax {
            cb.state = CircuitClosed
            cb.failures = 0
        }
    } else {
        cb.failures = 0
    }
}

func (cb *CircuitBreaker) State() CircuitState {
    cb.mu.RLock()
    defer cb.mu.RUnlock()
    return cb.state
}
```

```go
// Использование с пулом
type ResilientPool struct {
    pool    *pgxpool.Pool
    breaker *CircuitBreaker
    retry   RetryConfig
}

func (p *ResilientPool) QueryRow(ctx context.Context, sql string, args ...any) pgx.Row {
    // Circuit breaker + retry
    var row pgx.Row
    err := p.breaker.Execute(ctx, func(ctx context.Context) error {
        _, retryErr := WithRetry(ctx, p.retry, func(ctx context.Context) (struct{}, error) {
            row = p.pool.QueryRow(ctx, sql, args...)
            // QueryRow не возвращает ошибку сразу — проверяем при Scan
            return struct{}{}, nil
        })
        return retryErr
    })
    if err != nil {
        // Возвращаем row, который при Scan вернёт ошибку
        return &errorRow{err: err}
    }
    return row
}
```

---

## Security

### SSL/TLS Connections

В production **обязательно** используйте TLS для соединения с PostgreSQL.

```go
import (
    "crypto/tls"
    "crypto/x509"
    "os"

    "github.com/jackc/pgx/v5/pgxpool"
)

func NewSecurePool(ctx context.Context, cfg Config) (*pgxpool.Pool, error) {
    poolConfig, err := pgxpool.ParseConfig(cfg.ConnectionString())
    if err != nil {
        return nil, err
    }

    // Вариант 1: Verify-full (рекомендуется)
    // Проверяет сертификат сервера и hostname
    certPool := x509.NewCertPool()
    caCert, err := os.ReadFile(cfg.CACertFile)
    if err != nil {
        return nil, fmt.Errorf("read CA cert: %w", err)
    }
    certPool.AppendCertsFromPEM(caCert)

    poolConfig.ConnConfig.TLSConfig = &tls.Config{
        ServerName: cfg.Host,
        RootCAs:    certPool,
        MinVersion: tls.VersionTLS12,
    }

    // Вариант 2: Client certificate authentication (mTLS)
    if cfg.ClientCertFile != "" && cfg.ClientKeyFile != "" {
        clientCert, err := tls.LoadX509KeyPair(cfg.ClientCertFile, cfg.ClientKeyFile)
        if err != nil {
            return nil, fmt.Errorf("load client cert: %w", err)
        }
        poolConfig.ConnConfig.TLSConfig.Certificates = []tls.Certificate{clientCert}
    }

    return pgxpool.NewWithConfig(ctx, poolConfig)
}
```

### SSL Mode сравнение

| sslmode | Защита | Production |
|---------|--------|------------|
| `disable` | Нет шифрования | ❌ Никогда |
| `allow` | Опциональное | ❌ Ненадёжно |
| `prefer` | Предпочтительное (default) | ⚠️ Не гарантирует |
| `require` | Обязательное, без проверки | ⚠️ Man-in-the-middle |
| `verify-ca` | Проверка CA | ✅ Хорошо |
| `verify-full` | Проверка CA + hostname | ✅ Лучший вариант |

> ⚠️ **Критично**: В production всегда используйте `verify-ca` или `verify-full`. `prefer` и `require` не защищают от man-in-the-middle атак.

### Row-Level Security

RLS позволяет ограничить доступ к строкам на уровне БД — идеально для multi-tenant приложений.

```sql
-- Включаем RLS на таблице
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Политика: пользователи видят только свои заказы
CREATE POLICY user_orders ON orders
    USING (user_id = current_setting('app.current_user_id')::int);

-- Политика: tenant isolation
CREATE POLICY tenant_isolation ON orders
    USING (tenant_id = current_setting('app.tenant_id')::int);

-- Применяется даже к owner (по умолчанию owner обходит RLS)
ALTER TABLE orders FORCE ROW LEVEL SECURITY;
```

```go
// Middleware для установки tenant_id
type TenantMiddleware struct {
    pool *pgxpool.Pool
}

func (m *TenantMiddleware) WithTenant(ctx context.Context, tenantID int64) *pgxpool.Pool {
    // ⚠️ Нельзя использовать SET для pool — он shared!
    // Используем AfterConnect или per-connection setup
    return m.pool
}

// Правильный подход: устанавливаем tenant_id для каждого запроса
func (r *OrderRepository) ListForTenant(ctx context.Context, tenantID int64) ([]Order, error) {
    conn, err := r.pool.Acquire(ctx)
    if err != nil {
        return nil, err
    }
    defer conn.Release()

    // Устанавливаем tenant_id для этого соединения
    _, err = conn.Exec(ctx,
        fmt.Sprintf("SET LOCAL app.tenant_id = '%d'", tenantID),
    )
    if err != nil {
        return nil, fmt.Errorf("set tenant: %w", err)
    }

    // Теперь RLS автоматически фильтрует данные
    rows, err := conn.Query(ctx, "SELECT * FROM orders ORDER BY created_at DESC")
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var orders []Order
    for rows.Next() {
        var o Order
        if err := rows.Scan(&o.ID, &o.TenantID, &o.UserID, &o.TotalAmount); err != nil {
            return nil, err
        }
        orders = append(orders, o)
    }
    return orders, rows.Err()
}

// Лучший подход: через транзакцию
func (r *OrderRepository) WithTenant(ctx context.Context, tenantID int64,
    fn func(ctx context.Context, conn *pgxpool.Conn) error) error {

    conn, err := r.pool.Acquire(ctx)
    if err != nil {
        return err
    }
    defer conn.Release()

    tx, err := conn.Begin(ctx)
    if err != nil {
        return err
    }
    defer tx.Rollback(ctx)

    // SET LOCAL работает в рамках транзакции
    _, err = tx.Exec(ctx,
        fmt.Sprintf("SET LOCAL app.tenant_id = '%d'", tenantID),
    )
    if err != nil {
        return fmt.Errorf("set tenant: %w", err)
    }

    if err := fn(ctx, conn); err != nil {
        return err
    }

    return tx.Commit(ctx)
}
```

> 💡 **Для C# разработчиков**: RLS — аналог глобального query filter в EF Core (`HasQueryFilter`), но реализованный на уровне БД. Невозможно обойти из приложения.

```csharp
// EF Core — query filter (application-level)
modelBuilder.Entity<Order>()
    .HasQueryFilter(o => o.TenantId == _tenantService.TenantId);
// ⚠️ Можно обойти с IgnoreQueryFilters()

// PostgreSQL RLS — database-level
// ✅ Невозможно обойти из приложения
```

### Secrets Management

Не храните пароли БД в коде или ENV переменных в открытом виде.

```go
package config

import (
    "context"
    "encoding/json"
    "fmt"
    "os"
    "time"

    "github.com/aws/aws-sdk-go-v2/service/secretsmanager"
)

// DatabaseSecret — структура секрета из AWS Secrets Manager / Vault
type DatabaseSecret struct {
    Host     string `json:"host"`
    Port     int    `json:"port"`
    Username string `json:"username"`
    Password string `json:"password"`
    Database string `json:"dbname"`
}

// Вариант 1: AWS Secrets Manager
func GetDBSecretAWS(ctx context.Context, client *secretsmanager.Client, secretID string) (*DatabaseSecret, error) {
    result, err := client.GetSecretValue(ctx, &secretsmanager.GetSecretValueInput{
        SecretId: &secretID,
    })
    if err != nil {
        return nil, fmt.Errorf("get secret: %w", err)
    }

    var secret DatabaseSecret
    if err := json.Unmarshal([]byte(*result.SecretString), &secret); err != nil {
        return nil, fmt.Errorf("parse secret: %w", err)
    }

    return &secret, nil
}

// Вариант 2: HashiCorp Vault
func GetDBSecretVault(ctx context.Context, vaultAddr, token, path string) (*DatabaseSecret, error) {
    // Используем vault API
    client, err := vault.New(
        vault.WithAddress(vaultAddr),
        vault.WithRequestTimeout(10*time.Second),
    )
    if err != nil {
        return nil, err
    }

    if err := client.SetToken(token); err != nil {
        return nil, err
    }

    s, err := client.Secrets.KvV2Read(ctx, path, vault.WithMountPath("secret"))
    if err != nil {
        return nil, err
    }

    return &DatabaseSecret{
        Host:     s.Data.Data["host"].(string),
        Port:     int(s.Data.Data["port"].(float64)),
        Username: s.Data.Data["username"].(string),
        Password: s.Data.Data["password"].(string),
        Database: s.Data.Data["dbname"].(string),
    }, nil
}

// Вариант 3: Kubernetes Secrets (самый простой)
func GetDBSecretK8s() (*DatabaseSecret, error) {
    // K8s монтирует секреты как файлы или ENV
    return &DatabaseSecret{
        Host:     os.Getenv("DB_HOST"),
        Port:     5432,
        Username: os.Getenv("DB_USER"),
        Password: readFileOrEnv("/run/secrets/db-password", "DB_PASSWORD"),
        Database: os.Getenv("DB_NAME"),
    }, nil
}

func readFileOrEnv(filePath, envKey string) string {
    data, err := os.ReadFile(filePath)
    if err == nil {
        return strings.TrimSpace(string(data))
    }
    return os.Getenv(envKey)
}
```

### Ротация секретов

```go
// Пул с автоматическим обновлением credentials
type RotatingPool struct {
    mu          sync.RWMutex
    pool        *pgxpool.Pool
    secretFunc  func(ctx context.Context) (*DatabaseSecret, error)
    refreshEvery time.Duration
}

func NewRotatingPool(ctx context.Context,
    secretFunc func(ctx context.Context) (*DatabaseSecret, error),
    refreshEvery time.Duration,
) (*RotatingPool, error) {
    rp := &RotatingPool{
        secretFunc:   secretFunc,
        refreshEvery: refreshEvery,
    }

    // Создаём начальный пул
    if err := rp.refresh(ctx); err != nil {
        return nil, err
    }

    // Запускаем фоновое обновление
    go rp.rotateLoop(ctx)

    return rp, nil
}

func (rp *RotatingPool) Pool() *pgxpool.Pool {
    rp.mu.RLock()
    defer rp.mu.RUnlock()
    return rp.pool
}

func (rp *RotatingPool) refresh(ctx context.Context) error {
    secret, err := rp.secretFunc(ctx)
    if err != nil {
        return err
    }

    dsn := fmt.Sprintf("postgres://%s:%s@%s:%d/%s?sslmode=verify-ca",
        secret.Username, secret.Password, secret.Host, secret.Port, secret.Database)

    newPool, err := pgxpool.New(ctx, dsn)
    if err != nil {
        return err
    }

    rp.mu.Lock()
    oldPool := rp.pool
    rp.pool = newPool
    rp.mu.Unlock()

    // Закрываем старый пул после перехода
    if oldPool != nil {
        go func() {
            time.Sleep(30 * time.Second) // Ждём завершения активных запросов
            oldPool.Close()
        }()
    }

    return nil
}

func (rp *RotatingPool) rotateLoop(ctx context.Context) {
    ticker := time.NewTicker(rp.refreshEvery)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            return
        case <-ticker.C:
            if err := rp.refresh(ctx); err != nil {
                slog.Error("failed to rotate DB credentials",
                    slog.String("error", err.Error()),
                )
            }
        }
    }
}
```

---

## Observability для PostgreSQL

### Метрики pg_stat_*

PostgreSQL предоставляет системные представления для мониторинга.

```go
package pgmetrics

import (
    "context"

    "github.com/jackc/pgx/v5/pgxpool"
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    dbSize = promauto.NewGauge(prometheus.GaugeOpts{
        Name: "postgresql_database_size_bytes",
        Help: "Database size in bytes",
    })

    tableRows = promauto.NewGaugeVec(prometheus.GaugeOpts{
        Name: "postgresql_table_rows_estimate",
        Help: "Estimated number of rows in table",
    }, []string{"table"})

    cacheHitRatio = promauto.NewGauge(prometheus.GaugeOpts{
        Name: "postgresql_cache_hit_ratio",
        Help: "Buffer cache hit ratio",
    })

    activeConnections = promauto.NewGauge(prometheus.GaugeOpts{
        Name: "postgresql_active_connections",
        Help: "Number of active connections",
    })

    deadTuples = promauto.NewGaugeVec(prometheus.GaugeOpts{
        Name: "postgresql_dead_tuples",
        Help: "Number of dead tuples (need VACUUM)",
    }, []string{"table"})

    replicationLag = promauto.NewGauge(prometheus.GaugeOpts{
        Name: "postgresql_replication_lag_seconds",
        Help: "Replication lag in seconds",
    })

    longRunningQueries = promauto.NewGauge(prometheus.GaugeOpts{
        Name: "postgresql_long_running_queries",
        Help: "Number of queries running longer than 30 seconds",
    })
)

// PGCollector собирает метрики из PostgreSQL
type PGCollector struct {
    pool *pgxpool.Pool
}

func NewPGCollector(pool *pgxpool.Pool) *PGCollector {
    return &PGCollector{pool: pool}
}

func (c *PGCollector) Collect(ctx context.Context) error {
    // Database size
    var size int64
    if err := c.pool.QueryRow(ctx,
        "SELECT pg_database_size(current_database())").Scan(&size); err != nil {
        return err
    }
    dbSize.Set(float64(size))

    // Cache hit ratio
    var ratio float64
    if err := c.pool.QueryRow(ctx, `
        SELECT
            CASE WHEN (blks_hit + blks_read) = 0 THEN 0
            ELSE blks_hit::float / (blks_hit + blks_read)
            END
        FROM pg_stat_database
        WHERE datname = current_database()
    `).Scan(&ratio); err != nil {
        return err
    }
    cacheHitRatio.Set(ratio)

    // Active connections
    var active int
    if err := c.pool.QueryRow(ctx, `
        SELECT count(*) FROM pg_stat_activity
        WHERE state = 'active' AND pid != pg_backend_pid()
    `).Scan(&active); err != nil {
        return err
    }
    activeConnections.Set(float64(active))

    // Table stats
    rows, err := c.pool.Query(ctx, `
        SELECT
            schemaname || '.' || relname as table_name,
            n_live_tup,
            n_dead_tup
        FROM pg_stat_user_tables
        ORDER BY n_dead_tup DESC
        LIMIT 50
    `)
    if err != nil {
        return err
    }
    defer rows.Close()

    for rows.Next() {
        var tableName string
        var liveTup, deadTup int64
        if err := rows.Scan(&tableName, &liveTup, &deadTup); err != nil {
            return err
        }
        tableRows.WithLabelValues(tableName).Set(float64(liveTup))
        deadTuples.WithLabelValues(tableName).Set(float64(deadTup))
    }

    // Long running queries
    var longQueries int
    if err := c.pool.QueryRow(ctx, `
        SELECT count(*) FROM pg_stat_activity
        WHERE state = 'active'
          AND now() - query_start > interval '30 seconds'
          AND pid != pg_backend_pid()
    `).Scan(&longQueries); err != nil {
        return err
    }
    longRunningQueries.Set(float64(longQueries))

    // Replication lag (если есть реплики)
    var lag *float64
    _ = c.pool.QueryRow(ctx, `
        SELECT EXTRACT(EPOCH FROM replay_lag)
        FROM pg_stat_replication
        LIMIT 1
    `).Scan(&lag)
    if lag != nil {
        replicationLag.Set(*lag)
    }

    return nil
}

// StartCollector запускает периодический сбор метрик
func StartCollector(ctx context.Context, pool *pgxpool.Pool, interval time.Duration) {
    collector := NewPGCollector(pool)
    ticker := time.NewTicker(interval)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            return
        case <-ticker.C:
            if err := collector.Collect(ctx); err != nil {
                slog.Error("metrics collection failed",
                    slog.String("error", err.Error()),
                )
            }
        }
    }
}
```

### Prometheus Integration

```go
// Полный пример с HTTP endpoint
package main

import (
    "net/http"

    "github.com/prometheus/client_golang/prometheus/promhttp"
)

func main() {
    pool, _ := NewPool(ctx, cfg)

    // Запуск сбора метрик
    go StartCollector(ctx, pool, 15*time.Second)

    // Запуск pool monitor
    monitor := NewPoolMonitor(pool, slog.Default())
    go monitor.Start(ctx)

    // Prometheus endpoint
    http.Handle("/metrics", promhttp.Handler())
    http.ListenAndServe(":9090", nil)
}
```

### Ключевые метрики для алертов

```yaml
# Prometheus alerting rules
groups:
  - name: postgresql
    rules:
      # Низкий cache hit ratio
      - alert: PostgreSQLLowCacheHitRatio
        expr: postgresql_cache_hit_ratio < 0.95
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low buffer cache hit ratio"

      # Много dead tuples (нужен VACUUM)
      - alert: PostgreSQLHighDeadTuples
        expr: postgresql_dead_tuples > 100000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Table {{ $labels.table }} needs VACUUM"

      # Долгие запросы
      - alert: PostgreSQLLongRunningQueries
        expr: postgresql_long_running_queries > 0
        for: 1m
        labels:
          severity: critical

      # Высокая утилизация пула
      - alert: PostgreSQLPoolNearCapacity
        expr: db_pool_connections_total{state="acquired"} / db_pool_connections_total{state="max"} > 0.8
        for: 5m
        labels:
          severity: warning

      # Replication lag
      - alert: PostgreSQLReplicationLag
        expr: postgresql_replication_lag_seconds > 10
        for: 2m
        labels:
          severity: critical
```

### OpenTelemetry Instrumentation

Полная интеграция pgx с OpenTelemetry для distributed tracing.

```go
package otel

import (
    "context"

    "github.com/jackc/pgx/v5"
    "github.com/jackc/pgx/v5/pgxpool"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/codes"
    semconv "go.opentelemetry.io/otel/semconv/v1.21.0"
    "go.opentelemetry.io/otel/trace"
)

// PgxTracer реализует полный OpenTelemetry instrumentation для pgx
type PgxTracer struct {
    tracer trace.Tracer
    dbName string
}

func NewPgxTracer(dbName string) *PgxTracer {
    return &PgxTracer{
        tracer: otel.Tracer("github.com/myapp/pgx"),
        dbName: dbName,
    }
}

// TraceQueryStart — начало запроса
func (t *PgxTracer) TraceQueryStart(
    ctx context.Context,
    conn *pgx.Conn,
    data pgx.TraceQueryStartData,
) context.Context {
    attrs := []attribute.KeyValue{
        semconv.DBSystemPostgreSQL,
        semconv.DBName(t.dbName),
        semconv.DBStatement(data.SQL),
        semconv.DBUser(conn.Config().User),
        attribute.String("db.postgresql.host", conn.Config().Host),
        attribute.Int("db.postgresql.port", int(conn.Config().Port)),
    }

    ctx, _ = t.tracer.Start(ctx, "postgresql.query",
        trace.WithSpanKind(trace.SpanKindClient),
        trace.WithAttributes(attrs...),
    )

    return ctx
}

// TraceQueryEnd — завершение запроса
func (t *PgxTracer) TraceQueryEnd(
    ctx context.Context,
    conn *pgx.Conn,
    data pgx.TraceQueryEndData,
) {
    span := trace.SpanFromContext(ctx)
    defer span.End()

    span.SetAttributes(
        attribute.Int64("db.rows_affected", data.CommandTag.RowsAffected()),
        attribute.String("db.command_tag", data.CommandTag.String()),
    )

    if data.Err != nil {
        span.RecordError(data.Err)
        span.SetStatus(codes.Error, data.Err.Error())
    } else {
        span.SetStatus(codes.Ok, "")
    }
}

// TraceBatchStart — начало batch
func (t *PgxTracer) TraceBatchStart(
    ctx context.Context,
    conn *pgx.Conn,
    data pgx.TraceBatchStartData,
) context.Context {
    ctx, _ = t.tracer.Start(ctx, "postgresql.batch",
        trace.WithSpanKind(trace.SpanKindClient),
        trace.WithAttributes(
            semconv.DBSystemPostgreSQL,
            attribute.Int("db.batch.size", data.Batch.Len()),
        ),
    )
    return ctx
}

// TraceBatchEnd — завершение batch
func (t *PgxTracer) TraceBatchEnd(
    ctx context.Context,
    conn *pgx.Conn,
    data pgx.TraceBatchEndData,
) {
    span := trace.SpanFromContext(ctx)
    defer span.End()

    if data.Err != nil {
        span.RecordError(data.Err)
        span.SetStatus(codes.Error, data.Err.Error())
    }
}

// Применение к пулу
func NewInstrumentedPool(ctx context.Context, dsn, dbName string) (*pgxpool.Pool, error) {
    poolConfig, err := pgxpool.ParseConfig(dsn)
    if err != nil {
        return nil, err
    }

    poolConfig.ConnConfig.Tracer = NewPgxTracer(dbName)

    return pgxpool.NewWithConfig(ctx, poolConfig)
}
```

> 💡 **Для C# разработчиков**: В .NET используется `DiagnosticSource` и `Activity` (System.Diagnostics) для трейсинга SQL. В Go — явный tracer interface, что даёт полный контроль над тем, какие данные собираются.

---

## Практические примеры

### Пример 1: Production-Ready Connection Setup

Полная настройка подключения к PostgreSQL для production сервиса.

```go
package main

import (
    "context"
    "crypto/tls"
    "crypto/x509"
    "fmt"
    "log/slog"
    "os"
    "strconv"
    "time"

    "github.com/jackc/pgx/v5"
    "github.com/jackc/pgx/v5/pgxpool"
)

// AppConfig — конфигурация приложения
type AppConfig struct {
    DB DBConfig
}

type DBConfig struct {
    Host     string
    Port     int
    User     string
    Password string
    Database string

    // Pool
    MaxConns        int32
    MinConns        int32
    MaxConnLifetime time.Duration
    MaxConnIdleTime time.Duration

    // SSL
    SSLMode    string
    CACertPath string

    // Timeouts
    ConnectTimeout   time.Duration
    StatementTimeout time.Duration
}

func LoadDBConfig() DBConfig {
    return DBConfig{
        Host:     getEnv("DB_HOST", "localhost"),
        Port:     getEnvInt("DB_PORT", 5432),
        User:     getEnv("DB_USER", "app"),
        Password: getEnv("DB_PASSWORD", ""),
        Database: getEnv("DB_NAME", "myapp"),

        MaxConns:        int32(getEnvInt("DB_MAX_CONNS", 50)),
        MinConns:        int32(getEnvInt("DB_MIN_CONNS", 10)),
        MaxConnLifetime: time.Hour,
        MaxConnIdleTime: 30 * time.Minute,

        SSLMode:    getEnv("DB_SSL_MODE", "verify-ca"),
        CACertPath: getEnv("DB_CA_CERT", ""),

        ConnectTimeout:   10 * time.Second,
        StatementTimeout: 30 * time.Second,
    }
}

func NewProductionPool(ctx context.Context, cfg DBConfig, logger *slog.Logger) (*pgxpool.Pool, error) {
    dsn := fmt.Sprintf(
        "postgres://%s:%s@%s:%d/%s?sslmode=%s",
        cfg.User, cfg.Password, cfg.Host, cfg.Port, cfg.Database, cfg.SSLMode,
    )

    poolConfig, err := pgxpool.ParseConfig(dsn)
    if err != nil {
        return nil, fmt.Errorf("parse config: %w", err)
    }

    // --- Pool settings ---
    poolConfig.MaxConns = cfg.MaxConns
    poolConfig.MinConns = cfg.MinConns
    poolConfig.MaxConnLifetime = cfg.MaxConnLifetime
    poolConfig.MaxConnIdleTime = cfg.MaxConnIdleTime
    poolConfig.HealthCheckPeriod = time.Minute

    // --- Connection settings ---
    poolConfig.ConnConfig.ConnectTimeout = cfg.ConnectTimeout
    poolConfig.ConnConfig.RuntimeParams = map[string]string{
        "application_name":  "myapp",
        "statement_timeout": fmt.Sprintf("%dms", cfg.StatementTimeout.Milliseconds()),
        "lock_timeout":      "10s",
        "idle_in_transaction_session_timeout": "60s",
        "timezone": "UTC",
    }

    // --- TLS ---
    if cfg.CACertPath != "" {
        certPool := x509.NewCertPool()
        caCert, err := os.ReadFile(cfg.CACertPath)
        if err != nil {
            return nil, fmt.Errorf("read CA cert: %w", err)
        }
        certPool.AppendCertsFromPEM(caCert)

        poolConfig.ConnConfig.TLSConfig = &tls.Config{
            ServerName: cfg.Host,
            RootCAs:    certPool,
            MinVersion: tls.VersionTLS12,
        }
    }

    // --- Tracing ---
    poolConfig.ConnConfig.Tracer = &LoggingTracer{logger: logger}

    // --- Hooks ---
    poolConfig.AfterConnect = func(ctx context.Context, conn *pgx.Conn) error {
        logger.Info("new db connection established")
        return nil
    }

    poolConfig.BeforeAcquire = func(ctx context.Context, conn *pgx.Conn) bool {
        return !conn.IsClosed()
    }

    // --- Create pool ---
    pool, err := pgxpool.NewWithConfig(ctx, poolConfig)
    if err != nil {
        return nil, fmt.Errorf("create pool: %w", err)
    }

    // --- Verify ---
    if err := pool.Ping(ctx); err != nil {
        pool.Close()
        return nil, fmt.Errorf("ping: %w", err)
    }

    // --- Warm pool ---
    warmConns := min(5, int(cfg.MinConns))
    conns := make([]*pgxpool.Conn, 0, warmConns)
    for i := 0; i < warmConns; i++ {
        c, err := pool.Acquire(ctx)
        if err != nil {
            break
        }
        conns = append(conns, c)
    }
    for _, c := range conns {
        c.Release()
    }

    logger.Info("database pool ready",
        slog.Int("warm_connections", len(conns)),
        slog.Int32("max_connections", cfg.MaxConns),
    )

    return pool, nil
}

func getEnv(key, fallback string) string {
    if v := os.Getenv(key); v != "" {
        return v
    }
    return fallback
}

func getEnvInt(key string, fallback int) int {
    if v := os.Getenv(key); v != "" {
        if i, err := strconv.Atoi(v); err == nil {
            return i
        }
    }
    return fallback
}
```

### Пример 2: Zero-Downtime Migration

Добавление нового поля к таблице с миллионами записей без даунтайма.

```go
// cmd/migrate/add_user_preferences.go
//
// Задача: добавить колонку preferences JSONB NOT NULL с default значением
// к таблице users (5 млн записей)
//
// Стратегия: 3-step migration

package main

import (
    "context"
    "fmt"
    "log/slog"
    "time"

    "github.com/jackc/pgx/v5/pgxpool"
)

func main() {
    ctx := context.Background()
    pool, _ := pgxpool.New(ctx, os.Getenv("DATABASE_URL"))
    defer pool.Close()

    logger := slog.Default()

    // Шаг 1: Добавить nullable колонку (мгновенно)
    logger.Info("Step 1: Adding nullable column")
    _, err := pool.Exec(ctx, `
        ALTER TABLE users ADD COLUMN IF NOT EXISTS preferences JSONB;
    `)
    if err != nil {
        logger.Error("step 1 failed", slog.String("error", err.Error()))
        return
    }
    logger.Info("Step 1 complete")

    // Шаг 2: Backfill данных батчами
    logger.Info("Step 2: Backfilling data")
    defaultPrefs := `{"theme": "light", "notifications": true, "locale": "en"}`

    totalUpdated := int64(0)
    batchSize := 5000

    for {
        result, err := pool.Exec(ctx, `
            UPDATE users
            SET preferences = $1::jsonb
            WHERE id IN (
                SELECT id FROM users
                WHERE preferences IS NULL
                LIMIT $2
                FOR UPDATE SKIP LOCKED
            )
        `, defaultPrefs, batchSize)
        if err != nil {
            logger.Error("backfill batch failed", slog.String("error", err.Error()))
            return
        }

        rowsAffected := result.RowsAffected()
        totalUpdated += rowsAffected

        logger.Info("backfill progress",
            slog.Int64("batch_rows", rowsAffected),
            slog.Int64("total_updated", totalUpdated),
        )

        if rowsAffected == 0 {
            break
        }

        // Пауза, чтобы не перегружать БД
        time.Sleep(50 * time.Millisecond)
    }
    logger.Info("Step 2 complete", slog.Int64("total_rows", totalUpdated))

    // Шаг 3: Добавить NOT NULL constraint
    logger.Info("Step 3: Adding NOT NULL constraint")

    // 3a. Добавляем CHECK constraint (NOT VALID — без скана)
    _, err = pool.Exec(ctx, `
        ALTER TABLE users ADD CONSTRAINT users_preferences_not_null
            CHECK (preferences IS NOT NULL) NOT VALID;
    `)
    if err != nil {
        logger.Error("step 3a failed", slog.String("error", err.Error()))
        return
    }

    // 3b. Валидируем constraint (ShareUpdateExclusiveLock — не блокирует запись)
    _, err = pool.Exec(ctx, `
        ALTER TABLE users VALIDATE CONSTRAINT users_preferences_not_null;
    `)
    if err != nil {
        logger.Error("step 3b failed", slog.String("error", err.Error()))
        return
    }

    // 3c. Устанавливаем реальный NOT NULL и удаляем CHECK
    _, err = pool.Exec(ctx, `
        ALTER TABLE users ALTER COLUMN preferences SET NOT NULL;
        ALTER TABLE users DROP CONSTRAINT users_preferences_not_null;
    `)
    if err != nil {
        logger.Error("step 3c failed", slog.String("error", err.Error()))
        return
    }

    // 3d. Добавляем DEFAULT для новых строк
    _, err = pool.Exec(ctx, fmt.Sprintf(`
        ALTER TABLE users ALTER COLUMN preferences SET DEFAULT '%s'::jsonb;
    `, defaultPrefs))
    if err != nil {
        logger.Error("step 3d failed", slog.String("error", err.Error()))
        return
    }

    logger.Info("Migration complete! Column 'preferences' is now NOT NULL with default")
}
```

### Пример 3: Read Replica Routing

Полная реализация маршрутизации запросов между primary и replicas.

```go
package postgres

import (
    "context"
    "fmt"
    "log/slog"
    "sync/atomic"
    "time"

    "github.com/jackc/pgx/v5/pgxpool"
)

// ClusterConfig — конфигурация кластера
type ClusterConfig struct {
    PrimaryDSN   string
    ReplicaDSNs  []string
    MaxConns     int32
    MinConns     int32
    HealthCheck  time.Duration
}

// Cluster управляет primary и replica пулами
type Cluster struct {
    primary  *pgxpool.Pool
    replicas []*pgxpool.Pool
    healthy  []atomic.Bool
    counter  atomic.Uint64
    logger   *slog.Logger
}

func NewCluster(ctx context.Context, cfg ClusterConfig, logger *slog.Logger) (*Cluster, error) {
    // Primary
    primaryCfg, err := pgxpool.ParseConfig(cfg.PrimaryDSN)
    if err != nil {
        return nil, fmt.Errorf("parse primary config: %w", err)
    }
    primaryCfg.MaxConns = cfg.MaxConns
    primaryCfg.MinConns = cfg.MinConns

    primary, err := pgxpool.NewWithConfig(ctx, primaryCfg)
    if err != nil {
        return nil, fmt.Errorf("connect primary: %w", err)
    }

    // Replicas
    replicas := make([]*pgxpool.Pool, 0, len(cfg.ReplicaDSNs))
    healthy := make([]atomic.Bool, len(cfg.ReplicaDSNs))

    for i, dsn := range cfg.ReplicaDSNs {
        repCfg, err := pgxpool.ParseConfig(dsn)
        if err != nil {
            closeAll(primary, replicas)
            return nil, fmt.Errorf("parse replica config: %w", err)
        }
        repCfg.MaxConns = cfg.MaxConns / 2 // Реплики — меньше соединений
        repCfg.MinConns = cfg.MinConns / 2

        replica, err := pgxpool.NewWithConfig(ctx, repCfg)
        if err != nil {
            closeAll(primary, replicas)
            return nil, fmt.Errorf("connect replica %d: %w", i, err)
        }
        replicas = append(replicas, replica)
        healthy[i].Store(true)
    }

    c := &Cluster{
        primary:  primary,
        replicas: replicas,
        healthy:  healthy,
        logger:   logger,
    }

    // Запускаем health checks для реплик
    if cfg.HealthCheck > 0 {
        go c.healthCheckLoop(ctx, cfg.HealthCheck)
    }

    return c, nil
}

// Writer возвращает primary pool (для INSERT/UPDATE/DELETE)
func (c *Cluster) Writer() *pgxpool.Pool {
    return c.primary
}

// Reader возвращает здоровую реплику (round-robin) или primary как fallback
func (c *Cluster) Reader() *pgxpool.Pool {
    if len(c.replicas) == 0 {
        return c.primary
    }

    // Round-robin по здоровым репликам
    attempts := len(c.replicas)
    for i := 0; i < attempts; i++ {
        idx := c.counter.Add(1) % uint64(len(c.replicas))
        if c.healthy[idx].Load() {
            return c.replicas[idx]
        }
    }

    // Все реплики нездоровы — fallback на primary
    c.logger.Warn("all replicas unhealthy, falling back to primary")
    return c.primary
}

func (c *Cluster) healthCheckLoop(ctx context.Context, interval time.Duration) {
    ticker := time.NewTicker(interval)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            return
        case <-ticker.C:
            c.checkReplicas(ctx)
        }
    }
}

func (c *Cluster) checkReplicas(ctx context.Context) {
    for i, replica := range c.replicas {
        checkCtx, cancel := context.WithTimeout(ctx, 5*time.Second)

        err := replica.Ping(checkCtx)
        cancel()

        wasHealthy := c.healthy[i].Load()
        isHealthy := err == nil

        c.healthy[i].Store(isHealthy)

        // Логируем изменения состояния
        if wasHealthy && !isHealthy {
            c.logger.Warn("replica became unhealthy",
                slog.Int("replica", i),
                slog.String("error", err.Error()),
            )
        } else if !wasHealthy && isHealthy {
            c.logger.Info("replica recovered", slog.Int("replica", i))
        }
    }
}

func (c *Cluster) Close() {
    c.primary.Close()
    for _, r := range c.replicas {
        r.Close()
    }
}

func closeAll(primary *pgxpool.Pool, replicas []*pgxpool.Pool) {
    if primary != nil {
        primary.Close()
    }
    for _, r := range replicas {
        r.Close()
    }
}

// --- Использование в сервисе ---

type OrderService struct {
    cluster *Cluster
}

func NewOrderService(cluster *Cluster) *OrderService {
    return &OrderService{cluster: cluster}
}

func (s *OrderService) Create(ctx context.Context, order Order) (int64, error) {
    // Запись → primary
    var id int64
    err := s.cluster.Writer().QueryRow(ctx,
        "INSERT INTO orders (user_id, total_amount, status) VALUES ($1, $2, $3) RETURNING id",
        order.UserID, order.TotalAmount, "pending",
    ).Scan(&id)
    return id, err
}

func (s *OrderService) GetByID(ctx context.Context, id int64) (*Order, error) {
    // Чтение → replica (с возможным отставанием)
    var o Order
    err := s.cluster.Reader().QueryRow(ctx,
        "SELECT id, user_id, total_amount, status, created_at FROM orders WHERE id = $1",
        id,
    ).Scan(&o.ID, &o.UserID, &o.TotalAmount, &o.Status, &o.CreatedAt)
    if err != nil {
        return nil, err
    }
    return &o, nil
}

func (s *OrderService) GetByIDConsistent(ctx context.Context, id int64) (*Order, error) {
    // Консистентное чтение → primary (когда нужны свежие данные)
    var o Order
    err := s.cluster.Writer().QueryRow(ctx,
        "SELECT id, user_id, total_amount, status, created_at FROM orders WHERE id = $1",
        id,
    ).Scan(&o.ID, &o.UserID, &o.TotalAmount, &o.Status, &o.CreatedAt)
    if err != nil {
        return nil, err
    }
    return &o, nil
}

func (s *OrderService) List(ctx context.Context, limit, offset int) ([]Order, error) {
    // Список → replica
    rows, err := s.cluster.Reader().Query(ctx,
        "SELECT id, user_id, total_amount, status, created_at FROM orders ORDER BY created_at DESC LIMIT $1 OFFSET $2",
        limit, offset,
    )
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var orders []Order
    for rows.Next() {
        var o Order
        if err := rows.Scan(&o.ID, &o.UserID, &o.TotalAmount, &o.Status, &o.CreatedAt); err != nil {
            return nil, err
        }
        orders = append(orders, o)
    }
    return orders, rows.Err()
}
```

---
