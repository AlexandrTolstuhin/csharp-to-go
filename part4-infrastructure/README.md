# Часть 4: Инфраструктура и интеграции

## Описание

Интеграция с базами данных, очередями сообщений, gRPC и настройка observability.

<!-- AUTO: MATERIALS -->
## Материалы

### 1. [4.1 Production PostgreSQL](./01_production_postgresql.md)

- Введение
- Advanced pgx Configuration
- Production Connection Pooling
- Zero-Downtime Migrations
- Query Performance
- High Availability
- Security
- Observability для PostgreSQL
- Практические примеры

### 2. [4.2 Кэширование](./02_caching.md)

- Введение
- Redis в Go: go-redis
- In-Memory кэширование
- Абстракция над кэшами: eko/gocache
- Паттерны кэширования
- Multi-Level кэширование (L1 + L2)
- Production Concerns
- Практические примеры

### 3. [4.3 Очереди сообщений](./03_message_queues.md)

- Введение
- Экосистема: C# vs Go
- Apache Kafka (segmentio/kafka-go)
- RabbitMQ (amqp091-go)
- NATS (nats.go)
- Redis Streams
- Сравнение технологий
- Паттерны и Best Practices
- Production Concerns
- Практические примеры

### 4. [4.4 gRPC](./04_grpc.md)

- Введение
- Экосистема: C# vs Go
- Protocol Buffers для gRPC
- buf: современный Protobuf tooling
- Сервер gRPC
- Клиент gRPC
- Контекст, дедлайны и метаданные
- Interceptors (Middleware для gRPC)
- gRPC-Gateway: REST API из gRPC
- ConnectRPC: современная альтернатива
- Health Checking и Reflection
- Безопасность
- Тестирование gRPC
- Production Concerns
- Практические примеры

### 5. [4.5 Observability: Логирование, Метрики, Трейсинг](./05_observability.md)

- Введение
- Экосистема: C# vs Go
- Столп 1: Structured Logging
- Столп 2: Метрики с Prometheus
- Столп 3: Distributed Tracing с OpenTelemetry
- Интеграция трёх столпов
- Health Checks и Readiness Probes
- SLI/SLO
- Production Concerns
- Практические примеры

### 6. [4.6 Конфигурация: Управление настройками в Go](./06_config.md)

- Введение
- Экосистема: C# vs Go
- Стандартная библиотека: os и flag
- caarlos0/env: struct-based ENV парсинг
- kelseyhightower/envconfig
- Сравнение env-библиотек
- Viper: полнофункциональная конфигурация
- koanf: современная альтернатива Viper
- cleanenv: лёгкая альтернатива
- Сравнительная таблица всех библиотек
- Блок-схема выбора библиотеки
- Валидация конфигурации
- Паттерны конфигурации
- Секреты и безопасность
- Feature Flags
- Production Concerns
- Практические примеры

### 7. [4.7 Контейнеризация: Docker, Compose и Kubernetes для Go](./07_containerization.md)

- Введение
- Экосистема: C# vs Go
- Docker для Go приложений
- Production Docker Patterns
- Docker Compose
- Kubernetes Basics
- CI/CD интеграция
- Сравнение с .NET
- Типичные ошибки C# разработчиков
- Практические примеры
<!-- /AUTO: MATERIALS -->

---

<!-- AUTO: NAV -->
[← Назад к оглавлению](../README.md) | [Предыдущая часть: Часть 3: Web & API](../part3-web-api/) | [Следующая часть: Проект 1: URL Shortener →](../part5-project1-url-shortener/)
<!-- /AUTO: NAV -->
