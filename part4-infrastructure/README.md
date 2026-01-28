# Часть 4: Инфраструктура и интеграции

## Описание

Интеграция с базами данных, очередями сообщений, gRPC и настройка observability.

## Статус

✅ **Завершено** — 100% (7 из 7 разделов)

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

### 4.5 [Observability](./05_observability.md) ✅
- Structured logging: log/slog (Go 1.21+), uber-go/zap, rs/zerolog — сравнение, бенчмарки, выбор
- slog как стандартный интерфейс, zap/zerolog как backend
- Production patterns: log rotation, PII redaction, dynamic log level
- Метрики: prometheus/client_golang, VictoriaMetrics, типы метрик, custom buckets
- HTTP Metrics Middleware (RED: Rate, Errors, Duration)
- Бизнес-метрики, PromQL запросы, alerting rules, Grafana дашборды
- Distributed Tracing: OpenTelemetry Go SDK, TracerProvider, Sampler, Propagator
- Manual instrumentation: spans, attributes, events, ошибки, вложенные spans
- Auto-instrumentation: otelhttp, otelgrpc, otelsql, redisotel
- Jaeger, Zipkin, OpenTelemetry Collector (receivers → processors → exporters)
- Интеграция трёх столпов: корреляция логов/трейсов, Exemplars, context propagation
- Агрегация логов: Grafana Loki vs ELK Stack
- Health Checks: liveness/readiness/startup probes, Kubernetes интеграция
- SLI/SLO: error budgets, burn rate, SLI recording middleware
- Production: overhead бенчмарки, graceful shutdown, тестирование, безопасность
- 3 практических примера: full observability setup, distributed tracing, Grafana Stack Docker Compose

### 4.6 [Конфигурация](./06_config.md) ✅
- Стандартная библиотека: os.Getenv, os.LookupEnv, flag, pflag
- caarlos0/env: struct-based ENV парсинг, custom parsers, вложенные структуры, file secrets, godotenv
- kelseyhightower/envconfig: prefix-based подход, auto-naming, Usage()
- Viper: файлы + env + flags + remote config, AutomaticEnv, WatchConfig, проблемы и ограничения
- koanf: модульная альтернатива Viper (Providers + Parsers), hot reload
- cleanenv: лёгкая альтернатива (файл + ENV)
- Сравнительные таблицы и блок-схема выбора библиотеки
- Валидация: fail fast, go-playground/validator, custom validation
- Паттерны: 12-Factor App, multi-environment, immutable vs hot reload, Functional Options
- Секреты: HashiCorp Vault, AWS Secrets Manager, K8s Secrets, маскирование в логах
- Feature Flags: config-based, OpenFeature SDK, сторонние сервисы
- Production: порядок инициализации, graceful reload (SIGHUP), тестирование (t.Setenv), observability
- 3 практических примера: production-ready config (caarlos0/env + validator), multi-source config (koanf + hot reload), config с секретами (Vault + feature flags)

### 4.7 [Контейнеризация](./07_containerization.md) ✅
- Multi-stage Docker builds для минимальных образов (~5-15 MB)
- Scratch, Alpine, Distroless — сравнение и выбор базового образа
- Безопасность: non-root, .dockerignore, Trivy сканирование, BuildKit secrets
- Production Docker Patterns: HEALTHCHECK, graceful shutdown, логирование, сигналы
- Docker Compose: структура, health checks, depends_on, profiles, hot reload с air
- Kubernetes basics: Pod, Deployment, Service, Ingress, ConfigMaps, Secrets
- Health Probes: liveness, readiness, startup — интеграция с K8s
- Resource Limits: GOMEMLIMIT, automaxprocs, HPA автоскейлинг
- CI/CD: GitHub Actions, multi-platform builds, Container Registry
- Сравнение с .NET: ASP.NET Core Docker vs Go Docker, .NET Aspire vs Compose
- 3 практических примера: production Dockerfile, Docker Compose для микросервисов, K8s Deployment

## Время изучения

**Примерно**: 2-3 недели

---

[← Назад к оглавлению](../README.md) | [Предыдущая часть](../part3-web-api/) | [Следующая часть →](../part5-projects/)
