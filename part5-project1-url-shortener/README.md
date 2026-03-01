# Проект 1: URL Shortener

> Практический проект для C# разработчиков, осваивающих Go.
> Сложность: **Beginner → Intermediate**

## Содержание

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Что мы построим](#%D1%87%D1%82%D0%BE-%D0%BC%D1%8B-%D0%BF%D0%BE%D1%81%D1%82%D1%80%D0%BE%D0%B8%D0%BC)
- [Архитектура](#%D0%B0%D1%80%D1%85%D0%B8%D1%82%D0%B5%D0%BA%D1%82%D1%83%D1%80%D0%B0)
- [Технологии](#%D1%82%D0%B5%D1%85%D0%BD%D0%BE%D0%BB%D0%BE%D0%B3%D0%B8%D0%B8)
  - [go.mod](#gomod)
- [Структура проекта](#%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D1%83%D1%80%D0%B0-%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0)
  - [Сравнение структур проектов](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D1%83%D1%80-%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%BE%D0%B2)
- [Разделы гайда](#%D1%80%D0%B0%D0%B7%D0%B4%D0%B5%D0%BB%D1%8B-%D0%B3%D0%B0%D0%B9%D0%B4%D0%B0)
- [Требования](#%D1%82%D1%80%D0%B5%D0%B1%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F)
- [Запуск](#%D0%B7%D0%B0%D0%BF%D1%83%D1%81%D0%BA)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

---

## Что мы построим

Полноценный сервис сокращения URL с:

- **API для создания коротких ссылок** (`POST /api/urls`)
- **Редиректом по коду** (`GET /{code}`) с 301/302 ответом
- **Статистикой переходов** (`GET /api/stats/{code}`)
- **Rate limiting** на основе token bucket
- **Health check** endpoint
- **Кэшированием** в Redis (паттерн cache-aside)
- **Хранением** в PostgreSQL

Проект реализуется дважды: сначала на стандартной библиотеке **net/http** (Go 1.22+),
затем мигрируем на **chi** — показывая разницу и мотивацию.

> 💡 **Для C# разработчиков**: Аналог — ASP.NET Core Minimal API + EF Core + IDistributedCache.
> В Go мы получаем ту же функциональность, но с другими идиомами и без heavy DI-контейнера.

---

## Архитектура

```mermaid
graph TB
    Client["Клиент (curl / браузер)"]
    HTTP["HTTP Handler Layer<br/>(net/http → chi)"]
    SVC["Service Layer<br/>(URLService)"]
    REPO["Repository Interface<br/>(URLRepository)"]
    PG[("PostgreSQL<br/>(pgx v5)")]
    REDIS[("Redis<br/>(go-redis v9)")]
    RL["Rate Limiter<br/>(golang.org/x/time/rate)"]

    Client -->|"POST /api/urls<br/>GET /{code}<br/>GET /api/stats/{code}"| HTTP
    HTTP --> RL
    HTTP --> SVC
    SVC --> REPO
    REPO -->|"write / read"| PG
    REPO -->|"cache-aside"| REDIS
```

```mermaid
sequenceDiagram
    participant C as Клиент
    participant H as Handler
    participant S as URLService
    participant Cache as Redis
    participant DB as PostgreSQL

    C->>H: GET /{code}
    H->>S: Redirect(code)
    S->>Cache: GET url:{code}
    alt Кэш-попадание
        Cache-->>S: originalURL
    else Кэш-промах
        S->>DB: SELECT WHERE code = ?
        DB-->>S: URL record
        S->>Cache: SET url:{code} TTL=1h
    end
    S-->>H: originalURL
    H-->>C: 301 Redirect
```

---

## Технологии

| Компонент | Go | C# аналог |
|-----------|-----|-----------|
| HTTP сервер | `net/http` + `chi` | ASP.NET Core |
| PostgreSQL | `pgx/v5` | EF Core / Npgsql |
| Redis | `go-redis/v9` | StackExchange.Redis |
| Rate limiting | `golang.org/x/time/rate` | AspNetCoreRateLimit |
| Тесты | `testing` + `testify` | xUnit + Moq |
| Контейнеры для тестов | `testcontainers-go` | TestContainers.NET |
| Логирование | `log/slog` (stdlib) | Serilog / NLog |
| Конфигурация | `os.Getenv` / env-файл | `appsettings.json` |

### go.mod

```go
module github.com/yourname/urlshortener

go 1.26

require (
    github.com/go-chi/chi/v5 v5.1.0
    github.com/jackc/pgx/v5 v5.7.1
    github.com/redis/go-redis/v9 v9.7.0
    github.com/stretchr/testify v1.10.0
    github.com/testcontainers/testcontainers-go v0.35.0
    golang.org/x/time v0.9.0
)
```

---

## Структура проекта

```
urlshortener/
├── cmd/
│   └── server/
│       └── main.go          # Точка входа: инициализация, запуск
├── internal/
│   ├── domain/
│   │   ├── url.go           # Доменная модель + кастомные ошибки
│   │   └── service.go       # URLService — бизнес-логика
│   ├── storage/
│   │   ├── postgres/
│   │   │   └── url_repo.go  # PostgreSQL реализация репозитория
│   │   └── redis/
│   │       └── cache.go     # Redis кэш
│   └── handler/
│       ├── url.go           # HTTP хэндлеры
│       └── middleware.go    # Logging, recovery, rate limiting
├── migrations/
│   ├── 001_create_urls.sql
│   └── 002_create_stats.sql
├── docker-compose.yml
├── Dockerfile
├── .env.example
└── go.mod
```

> 💡 **Идиома Go**: Код в `internal/` не доступен снаружи модуля — это встроенная
> инкапсуляция без модификаторов доступа. В C# аналог — `internal` классы в отдельном assembly.

### Сравнение структур проектов

**C# (ASP.NET Core Web API)**:
```
MyUrlShortener/
├── Controllers/
│   └── UrlController.cs
├── Models/
│   └── Url.cs
├── Services/
│   ├── IUrlService.cs
│   └── UrlService.cs
├── Repositories/
│   ├── IUrlRepository.cs
│   └── UrlRepository.cs
├── Data/
│   └── AppDbContext.cs
├── Program.cs
└── appsettings.json
```

**Go (идиоматично)**:
```
urlshortener/
├── cmd/server/main.go       # ≈ Program.cs
├── internal/
│   ├── domain/              # ≈ Models/ + Services/ + Repositories/ (интерфейсы)
│   └── storage/             # ≈ Repositories/ (реализации) + Data/
└── internal/handler/        # ≈ Controllers/
```

**Ключевые отличия**:
- Нет DI-контейнера — зависимости передаются явно через конструкторы (struct fields)
- Нет ORM — SQL пишется руками, pgx даёт прямой контроль
- `internal/` = встроенная защита от случайного импорта
- Конфигурация через переменные окружения, не XML/JSON файл

---

<!-- AUTO: MATERIALS -->
## Материалы

### 1. [1. Доменная модель и сервисный слой](./01_domain.md)

- Анализ требований
- Доменная модель
- Кастомные ошибки
- Интерфейс репозитория
- Алгоритм генерации кода (Base62)
- Сервисный слой
- Точка входа: main.go
- Сравнительная таблица

### 2. [2. Хранилище: PostgreSQL и Redis](./02_storage.md)

- Схема базы данных
- PostgreSQL с pgx v5
- Реализация URLRepository
- Redis кэш
- Паттерн cache-aside
- Обработка ошибок хранилища
- Сравнительная таблица

### 3. [3. HTTP слой: net/http и chi](./03_http.md)

- Архитектура HTTP слоя
- Часть 1: net/http (Go 1.22+)
- Часть 2: Миграция на chi
- Сравнительная таблица

### 4. [4. Тестирование и бенчмарки](./04_testing.md)

- Стратегия тестирования
- Unit тесты сервисного слоя
- Тесты HTTP хэндлеров
- Integration тесты с testcontainers-go
- Бенчмарки
- Покрытие кода
- Сравнительная таблица

### 5. [5. Деплой: Docker Compose и Production](./05_deployment.md)

- Dockerfile
- Docker Compose
- Конфигурация через переменные окружения
- Graceful shutdown
- Health checks
- Структурированное логирование
- Production чек-лист
- Сравнительная таблица
- Итоги проекта
<!-- /AUTO: MATERIALS -->

---

## Требования

- Go 1.22+
- Docker + Docker Compose (для PostgreSQL и Redis)
- Знание основ Go из Частей 1-4 курса

---

## Запуск

```bash
# Поднять зависимости
docker compose up -d postgres redis

# Применить миграции (см. 05_deployment.md)
psql $DATABASE_URL < migrations/001_create_urls.sql
psql $DATABASE_URL < migrations/002_create_stats.sql

# Запустить сервер
go run ./cmd/server

# Тестируем
curl -X POST http://localhost:8080/api/urls \
  -H "Content-Type: application/json" \
  -d '{"url": "https://go.dev/doc/effective_go"}'
# {"code": "aB3xY9", "short_url": "http://localhost:8080/aB3xY9"}

curl -L http://localhost:8080/aB3xY9
# 301 → https://go.dev/doc/effective_go
```

---

<!-- AUTO: NAV -->
[← Назад к оглавлению](../README.md) | [Предыдущая часть: Часть 4: Инфраструктура](../part4-infrastructure/) | [Следующая часть: Проект 2: E-Commerce →](../part5-project2-ecommerce/)
<!-- /AUTO: NAV -->
