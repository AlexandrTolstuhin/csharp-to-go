# Часть 4: Инфраструктура и интеграции

## Описание

Интеграция с базами данных, очередями сообщений, gRPC и настройка observability.

## Статус

🚧 **В разработке** — 57% (4 из 7 разделов)

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

### 4.3 [Очереди сообщений](./03_message_queues.md) ✅
- Kafka (segmentio/kafka-go): producer, consumer, consumer groups, production config, DLT
- RabbitMQ (amqp091-go): exchanges/queues/bindings, publisher confirms, prefetch, reconnection, DLX
- NATS (nats.go): Core pub/sub, JetStream, push/pull consumers, KV Store
- Redis Streams: XADD/XREAD, consumer groups, acknowledgment, claiming
- Сравнительная таблица и блок-схема выбора технологий
- Паттерны: идемпотентность, graceful shutdown, retry, Outbox, Saga
- Production: Prometheus метрики, OpenTelemetry trace propagation, health checks
- 3 практических примера: event-driven order processing (Kafka), task queue (RabbitMQ), real-time notifications (NATS)

### 4.4 [gRPC](./04_grpc.md) ✅
- Protocol Buffers для gRPC: API design best practices, well-known types, сервисные определения
- buf: современный tooling (lint, breaking, generate, BSR, CI/CD)
- Сервер gRPC: Unary, Server Streaming, Client Streaming, Bidirectional Streaming, Graceful Shutdown
- Клиент gRPC: grpc.NewClient, стримы, connection management
- Контекст, дедлайны, metadata, коды ошибок, Rich Error Model
- Interceptors: server/client, unary/stream, chaining, go-grpc-middleware v2
- gRPC-Gateway: HTTP annotations, reverse proxy, Swagger/OpenAPI
- ConnectRPC: современная альтернатива (HTTP/1.1, browser-friendly)
- Health Checking Protocol, Server Reflection, grpcurl/grpcui
- Безопасность: TLS, mTLS, JWT аутентификация
- Тестирование: bufconn (in-memory), стримы, grpcurl
- Production: Prometheus метрики, OpenTelemetry, load balancing, retry, keepalive
- 3 практических примера: CRUD User Service, real-time стриминг цен, gRPC-Gateway + REST

## Планируемые материалы

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
