# Часть 4: Инфраструктура и интеграции

## Описание

Интеграция с базами данных, очередями сообщений, gRPC и настройка observability.

## Статус

🚧 **В разработке** — 29% (2 из 7 разделов)

## Завершённые материалы

### 4.1 [Production PostgreSQL](./01_production_postgresql.md) ✅
- Advanced pgx: конфигурация, custom types, tracing hooks
- Production connection pooling: pgxpool vs PgBouncer, мониторинг
- Продвинутый sqlc: CTE, window functions, dynamic queries, batch
- Zero-downtime migrations: безопасные паттерны, Expand/Contract, Atlas
- Query performance: EXPLAIN ANALYZE, индексы, pg_stat_statements
- High availability: read replicas, retry, circuit breaker
- Security: SSL/TLS, Row-Level Security, secrets management
- Observability: Prometheus метрики, OpenTelemetry instrumentation

### 4.2 [Кэширование](./02_caching.md) ✅
- Redis (go-redis v9): подключение, операции, pipelining, транзакции, Pub/Sub
- Распределённые блокировки (Redlock): redsync
- In-memory: go-cache, ristretto v2, bigcache — сравнение и выбор
- Абстракция: eko/gocache (chain cache, loadable, metrics)
- Паттерны: Cache-Aside, Write-Through/Behind, Read-Through
- Cache stampede prevention (singleflight)
- Multi-level кэширование (L1 ristretto + L2 Redis + Pub/Sub инвалидация)
- Production: мониторинг, сериализация, GC impact, circuit breaker
- 3 практических примера: Redis cache layer, multi-level cache, session storage

## Планируемые материалы

### 4.3 Очереди сообщений
- Kafka: segmentio/kafka-go
- RabbitMQ: amqp091-go
- NATS: nats.go
- Redis Streams

### 4.4 gRPC
- Protocol Buffers
- Unary и Streaming RPC
- Interceptors
- gRPC-Gateway
- buf: современный tooling

### 4.5 Observability
- Логирование: log/slog, zap, zerolog
- Метрики: Prometheus
- Трейсинг: OpenTelemetry
- Jaeger, Zipkin

### 4.6 Конфигурация
- viper
- envconfig
- caarlos0/env

### 4.7 Контейнеризация
- Multi-stage Docker builds
- Distroless образы
- Docker Compose
- Kubernetes basics

## Время изучения

**Примерно**: 2-3 недели

---

[← Назад к оглавлению](../README.md) | [Предыдущая часть](../part3-web-api/) | [Следующая часть →](../part5-projects/)
