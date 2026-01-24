# План перехода с C# на Go для Senior разработчика

## Общая информация
- **Целевая аудитория**: Senior C# разработчик с глубоким опытом async/await, TPL
- **Формат обучения**: Книги + документация + практика
- **Практические проекты**: E-commerce, Финтех, SaaS платформа

---

## Часть 1: Основы Go (быстрый старт)

### 1.1 Установка и настройка окружения
- [ ] Установка Go (версия 1.22+)
- [ ] Настройка GOPATH, GOROOT, Go Modules
- [ ] IDE: GoLand или VSCode + Go extension
- [ ] Инструменты: `go fmt`, `go vet`, `golangci-lint`

### 1.2 Синтаксис и базовые концепции (сравнение с C#)
| Концепция | C# | Go |
|-----------|-----|-----|
| Типизация | `int x = 5;` | `var x int = 5` или `x := 5` |
| Классы | `class` | `struct` + методы |
| Интерфейсы | Явная реализация | Неявная (duck typing) |
| Наследование | `class : Base` | Композиция (embedding) |
| Exceptions | `try/catch/finally` | `error` как значение |
| Nullable | `int?` | Указатели `*int` |
| LINQ | `Where().Select()` | Циклы или библиотеки |

### 1.3 Ключевые отличия от C#
- [ ] Отсутствие классов — только структуры и интерфейсы
- [ ] Множественное возвращаемое значение (особенно `value, error`)
- [ ] Defer для cleanup (аналог using/finally)
- [ ] Указатели без арифметики
- [ ] Zero values вместо null по умолчанию
- [ ] Пакетная система и видимость (заглавная буква = public)

### 1.4 Практика: мини-проекты
1. CLI-утилита (работа с файлами, флаги)
2. Простой HTTP-сервер
3. JSON парсер/сериализатор

---

## Часть 2: Продвинутые темы (глубокое погружение)

### 2.1 Горутины и каналы (Goroutines & Channels)

#### Сравнение с C# async/await
| C# | Go |
|----|-----|
| `Task` | `goroutine` |
| `await` | `<-channel` |
| `Task.WhenAll` | `sync.WaitGroup` или `errgroup` |
| `CancellationToken` | `context.Context` |
| `Channel<T>` | `chan T` |

#### Темы для изучения:
- [ ] Создание горутин (`go func()`)
- [ ] Буферизированные vs небуферизированные каналы
- [ ] Select statement (мультиплексирование каналов)
- [ ] Паттерны: fan-in, fan-out, pipeline, worker pool
- [ ] Graceful shutdown с context.Context
- [ ] Утечки горутин — как избегать и детектировать

### 2.2 Go Runtime и планировщик (Scheduler)

#### Архитектура GMP:
- **G (Goroutine)** — легковесный "поток" (~2KB стека)
- **M (Machine)** — OS thread
- **P (Processor)** — логический процессор (GOMAXPROCS)

#### Темы для изучения:
- [ ] Work-stealing алгоритм планировщика
- [ ] Preemption (вытеснение) — как Go прерывает долгие горутины
- [ ] Local Run Queue vs Global Run Queue
- [ ] Системные вызовы и hand-off
- [ ] GOMAXPROCS и его влияние
- [ ] Трассировка: `go tool trace`

### 2.3 Сборка мусора (Garbage Collector)

#### Особенности Go GC:
- Concurrent, tri-color mark-and-sweep
- Низкая латентность (target: <1ms STW)
- Нет поколений (в отличие от .NET GC)

#### Темы для изучения:
- [ ] Tri-color marking algorithm
- [ ] Write barriers
- [ ] GOGC и GOMEMLIMIT переменные
- [ ] Анализ GC: `GODEBUG=gctrace=1`
- [ ] Оптимизации: sync.Pool, arena (Go 1.20+)
- [ ] Escape analysis и stack vs heap allocation
- [ ] Профилирование памяти: `pprof`

### 2.4 Примитивы синхронизации

- [ ] `sync.Mutex`, `sync.RWMutex`
- [ ] `sync.WaitGroup`
- [ ] `sync.Once` (singleton pattern)
- [ ] `sync.Map` (concurrent map)
- [ ] `sync.Pool` (object pooling)
- [ ] `sync/atomic` — атомарные операции
- [ ] `golang.org/x/sync/errgroup` — группы с ошибками
- [ ] `golang.org/x/sync/semaphore` — семафоры
- [ ] `golang.org/x/sync/singleflight` — дедупликация запросов

### 2.5 Обработка ошибок

#### Идиоматический Go:
- [ ] `error` как интерфейс
- [ ] Wrapping ошибок (`fmt.Errorf` с `%w`)
- [ ] `errors.Is()` и `errors.As()`
- [ ] Sentinel errors vs typed errors
- [ ] Panic/recover — когда использовать (спойлер: почти никогда)

### 2.6 Тестирование и бенчмаркинг

- [ ] Стандартный пакет `testing`
- [ ] Table-driven tests (идиоматический подход)
- [ ] Subtests и `t.Run()`
- [ ] Бенчмарки (`func BenchmarkXxx`)
- [ ] Fuzzing (Go 1.18+)
- [ ] Моки: `gomock`, `testify/mock`
- [ ] Integration tests с `testcontainers-go`

### 2.7 Профилирование и оптимизация

- [ ] `pprof` — CPU и memory профилирование
- [ ] `go tool trace` — анализ планировщика
- [ ] Race detector (`go run -race`)
- [ ] Escape analysis (`go build -gcflags="-m"`)
- [ ] Benchstat для сравнения бенчмарков

---

## Часть 3: Web API разработка

### 3.1 HTTP в Go

#### Стандартная библиотека:
- [ ] `net/http` — сервер и клиент
- [ ] `http.Handler` и `http.HandlerFunc`
- [ ] Middleware pattern
- [ ] `http.ServeMux` (улучшен в Go 1.22)

#### Популярные роутеры и фреймворки:
| Библиотека | Характеристика |
|------------|----------------|
| `chi` | Легковесный, идиоматичный, совместим с net/http |
| `gin` | Высокая производительность, популярный |
| `echo` | Минималистичный, хорошая документация |
| `fiber` | Fasthttp-based, Express-like API |

**Рекомендация**: Начать с `chi` или чистого `net/http` (Go 1.22+)

### 3.2 Структура проекта

#### Популярные layouts:
- [ ] Standard Go Project Layout (спорный, но известный)
- [ ] Flat structure для небольших сервисов
- [ ] Domain-Driven Design структура
- [ ] Hexagonal/Clean Architecture в Go

#### Рекомендуемая структура:
```
/cmd/api/           — точка входа
/internal/          — приватный код
  /handler/         — HTTP handlers
  /service/         — бизнес-логика
  /repository/      — работа с данными
  /domain/          — domain models
/pkg/               — публичные библиотеки
/config/            — конфигурация
/migrations/        — миграции БД
```

### 3.3 Dependency Injection

- [ ] Wire (Google) — compile-time DI
- [ ] Fx (Uber) — runtime DI
- [ ] Ручной DI через конструкторы (идиоматичный подход)

### 3.4 Валидация и сериализация

- [ ] `encoding/json` — стандартная библиотека
- [ ] `json-iterator/go` — быстрый JSON
- [ ] `go-playground/validator` — валидация структур
- [ ] Protocol Buffers + gRPC

### 3.5 Документация API

- [ ] Swagger/OpenAPI с `swaggo/swag`
- [ ] OpenAPI-first с `oapi-codegen`

---

## Часть 4: Инфраструктура и интеграции

### 4.1 PostgreSQL

- [ ] `database/sql` — стандартный интерфейс
- [ ] `pgx` — нативный драйвер PostgreSQL (рекомендуется)
- [ ] `sqlx` — расширения для database/sql
- [ ] `sqlc` — генерация кода из SQL (type-safe)
- [ ] `gorm` — ORM (если нужен)
- [ ] Connection pooling и настройка
- [ ] Миграции: `golang-migrate`, `goose`, `atlas`

### 4.2 Кэширование

- [ ] `go-redis/redis` — клиент Redis
- [ ] `eko/gocache` — абстракция над кэшами
- [ ] In-memory: `patrickmn/go-cache`, `dgraph-io/ristretto`
- [ ] Distributed caching patterns

### 4.3 Очереди сообщений

- [ ] Kafka: `segmentio/kafka-go`, `confluent-kafka-go`
- [ ] RabbitMQ: `rabbitmq/amqp091-go`
- [ ] NATS: `nats-io/nats.go`
- [ ] Redis Streams

### 4.4 gRPC

- [ ] Protocol Buffers
- [ ] Unary и streaming RPC
- [ ] Interceptors (middleware для gRPC)
- [ ] gRPC-Gateway (REST to gRPC)
- [ ] `buf` — современный инструментарий для protobuf

### 4.5 Observability

#### Логирование:
- [ ] `log/slog` (Go 1.21+) — структурированные логи
- [ ] `zerolog` — высокопроизводительный
- [ ] `zap` (Uber) — популярный выбор

#### Метрики:
- [ ] `prometheus/client_golang`
- [ ] OpenTelemetry Metrics

#### Трейсинг:
- [ ] OpenTelemetry — стандарт индустрии
- [ ] Jaeger, Zipkin интеграция

### 4.6 Конфигурация

- [ ] `spf13/viper` — популярная библиотека
- [ ] `kelseyhightower/envconfig` — из переменных окружения
- [ ] `caarlos0/env` — struct tags для env vars

### 4.7 Контейнеризация

- [ ] Multi-stage Docker builds
- [ ] Distroless/scratch образы
- [ ] Docker Compose для локальной разработки
- [ ] Kubernetes basics для Go сервисов

---

## Часть 5: Практические проекты

### Проект 1: URL Shortener (Beginner → Intermediate)
**Цель**: Освоение базовых концепций

**Технологии**:
- net/http или chi
- PostgreSQL + pgx
- Redis для кэширования
- Docker Compose

**Функциональность**:
- Создание короткой ссылки
- Редирект
- Статистика переходов
- Rate limiting

### Проект 2: E-commerce Platform (Intermediate)
**Цель**: Микросервисная архитектура

**Сервисы**:
1. **API Gateway** — маршрутизация, аутентификация
2. **User Service** — регистрация, JWT
3. **Catalog Service** — товары, категории
4. **Order Service** — заказы, состояния
5. **Payment Service** — интеграция с платёжными системами
6. **Notification Service** — email, push

**Технологии**:
- gRPC для межсервисного взаимодействия
- Kafka для событий
- PostgreSQL (per service)
- Redis для сессий и кэша
- OpenTelemetry для трейсинга

**Паттерны**:
- Saga pattern для распределённых транзакций
- CQRS для Catalog Service
- Event Sourcing для Order Service
- Circuit Breaker

### Проект 3: Trading/Fintech Platform (Advanced)
**Цель**: High-performance, real-time система

**Компоненты**:
1. **Market Data Service** — WebSocket стримы котировок
2. **Order Matching Engine** — обработка ордеров
3. **Portfolio Service** — позиции, баланс
4. **Risk Service** — лимиты, проверки
5. **Analytics Service** — агрегация данных

**Технологии**:
- WebSocket + горутины для real-time
- NATS для low-latency messaging
- TimescaleDB для time-series данных
- Redis Streams для event log
- Kubernetes с HPA

**Фокус**:
- Оптимизация latency
- Lock-free структуры данных
- Профилирование и тюнинг GC
- Graceful degradation

### Проект 4: SaaS Platform (Advanced)
**Цель**: Multi-tenant архитектура

**Компоненты**:
1. **Tenant Service** — управление тенантами
2. **Identity Service** — OAuth2, RBAC
3. **Core API** — основной функционал
4. **Webhook Service** — исходящие webhooks
5. **Background Workers** — фоновые задачи
6. **Admin Dashboard API**

**Технологии**:
- Schema-per-tenant в PostgreSQL
- Row-level security
- Feature flags
- Rate limiting per tenant
- Billing integration

---

## Часть 6: Best Practices Go 2024-2025

### 6.1 Код и архитектура
- [ ] "Accept interfaces, return structs"
- [ ] Маленькие интерфейсы (1-3 метода)
- [ ] Composition over inheritance
- [ ] Explicit is better than implicit
- [ ] Errors are values, handle them

### 6.2 Современные возможности
- [ ] Generics (Go 1.18+) — когда использовать
- [ ] `log/slog` для структурированного логирования
- [ ] `slices` и `maps` пакеты
- [ ] Improved routing в `net/http` (Go 1.22)
- [ ] Range over integers (Go 1.22)

### 6.3 Инструменты
- [ ] `golangci-lint` — линтер (обязательно)
- [ ] `staticcheck` — статический анализ
- [ ] `govulncheck` — проверка уязвимостей
- [ ] `go mod tidy` — управление зависимостями
- [ ] `air` — hot reload для разработки

### 6.4 Производительность
- [ ] Избегать аллокаций в hot paths
- [ ] `sync.Pool` для переиспользования объектов
- [ ] Правильный размер слайсов и map
- [ ] Избегать interface{} в критичных местах
- [ ] Профилирование до оптимизации

---

## Рекомендуемые ресурсы

### Книги
1. **"The Go Programming Language"** — Donovan & Kernighan (базовая)
2. **"Concurrency in Go"** — Katherine Cox-Buday (обязательно)
3. **"100 Go Mistakes and How to Avoid Them"** — Teiva Harsanyi (практичная)
4. **"Let's Go" / "Let's Go Further"** — Alex Edwards (web development)
5. **"Efficient Go"** — Bartłomiej Płotka (оптимизация)

### Онлайн-ресурсы
- [Go by Example](https://gobyexample.com)
- [Effective Go](https://go.dev/doc/effective_go)
- [Go Blog](https://go.dev/blog)
- [Uber Go Style Guide](https://github.com/uber-go/guide)
- [Ardan Labs Blog](https://www.ardanlabs.com/blog)

### Видео
- GopherCon talks (YouTube)
- Ardan Labs Ultimate Go (курс)

---

## План обучения по неделям (примерный)

### Недели 1-2: Основы
- Синтаксис, типы, структуры
- Интерфейсы и методы
- Error handling
- **Практика**: CLI утилита

### Недели 3-4: Concurrency
- Горутины и каналы
- Паттерны concurrency
- Context и cancellation
- **Практика**: Concurrent file processor

### Недели 5-6: Runtime Deep Dive
- Планировщик GMP
- Garbage Collector
- Профилирование
- **Практика**: Оптимизация hot paths

### Недели 7-8: Web Development
- HTTP сервер
- Middleware, routing
- База данных, кэш
- **Практика**: URL Shortener

### Недели 9-12: Микросервисы
- gRPC, Kafka
- Observability
- Docker, K8s
- **Практика**: E-commerce (2-3 сервиса)

### Недели 13-16: Advanced Projects
- Real-time системы
- Performance optimization
- Production readiness
- **Практика**: Fintech или SaaS платформа

---

## Верификация

### Как проверять прогресс:
1. **Unit тесты** — покрытие >80% для критичного кода
2. **Бенчмарки** — сравнение с baseline
3. **Race detector** — `go test -race`
4. **Linters** — `golangci-lint run`
5. **Load testing** — k6 или vegeta
6. **Observability** — метрики, логи, трейсы работают
7. **Docker build** — образ собирается и запускается
8. **Integration tests** — с testcontainers

### Критерии готовности к production:
- [ ] Graceful shutdown
- [ ] Health checks (liveness, readiness)
- [ ] Structured logging
- [ ] Metrics exported
- [ ] Tracing configured
- [ ] Rate limiting
- [ ] Circuit breakers
- [ ] Proper error handling
- [ ] Configuration from env
- [ ] Minimal Docker image
