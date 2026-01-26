# Переход с C# на Go: Курс для Senior разработчика

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Go Version](https://img.shields.io/badge/Go-1.23+-00ADD8?logo=go)](https://go.dev/)
[![Progress](https://img.shields.io/badge/Progress-53%25-yellow)](./STRUCTURE.md)
[![GitHub Stars](https://img.shields.io/github/stars/AlexandrTolstuhin/csharp-to-go?style=social)](https://github.com/AlexandrTolstuhin/csharp-to-go)

> Комплексный курс по изучению Go для опытного C# разработчика с фокусом на async/await, concurrency, производительность и продакшн-ready практики.

**Репозиторий:** [github.com/AlexandrTolstuhin/csharp-to-go](https://github.com/AlexandrTolstuhin/csharp-to-go)

---

## О курсе

**Целевая аудитория**: Senior C# разработчик с глубоким опытом async/await, TPL, высоконагруженных систем

**Формат**: Теория + практика + реальные проекты (E-commerce, Fintech, SaaS)

**Особенности**:
- Постоянное сравнение с C#
- Фокус на производительность и GC
- Продакшн-ready практики
- Практические проекты

---

## Структура курса

### [Часть 1: Основы Go (Быстрый старт)](./part1-basics/) — **Завершено**

- **1.1** [Установка и настройка окружения](./part1-basics/01_setup_environment.md)
- **1.2** [Синтаксис и базовые концепции](./part1-basics/02_syntax_basics.md)
- **+** [Шпаргалка: Производительность коллекций](./part1-basics/02a_collections_performance_cheatsheet.md)
- **1.3** [Ключевые отличия от C#](./part1-basics/03_key_differences.md)
- **1.4** [Практика: мини-проекты](./part1-basics/04_practice.md)

---

### [Часть 2: Продвинутые темы](./part2-advanced/) — **Завершено**

- **2.1** [Горутины и каналы](./part2-advanced/01_goroutines_channels.md)
- **2.2** [Go Runtime и планировщик](./part2-advanced/02_runtime_scheduler.md)
- **2.3** [Сборка мусора (GC)](./part2-advanced/03_gc.md)
- **2.4** [Примитивы синхронизации](./part2-advanced/04_sync_primitives.md)
- **2.5** [Обработка ошибок (продвинутый уровень)](./part2-advanced/05_error_handling.md)
- **2.6** [Тестирование и бенчмаркинг](./part2-advanced/06_testing_benchmarking.md)
- **2.7** [Профилирование и оптимизация](./part2-advanced/07_profiling_optimization.md)

---

### [Часть 3: Web API разработка](./part3-web-api/) — **Завершено**

- **3.1** [HTTP в Go](./part3-web-api/01_http_server.md)
- **3.2** [Структура проекта](./part3-web-api/02_project_structure.md)
- **3.3** [Работа с данными](./part3-web-api/03_database.md)
- **3.4** [Валидация и сериализация](./part3-web-api/04_validation_serialization.md)
- **3.5** [Документация API](./part3-web-api/05_api_documentation.md)

---

### [Часть 4: Инфраструктура и интеграции](./part4-infrastructure/)

#### 4.1 [Production PostgreSQL](./part4-infrastructure/01_production_postgresql.md)
- ✅ Advanced pgx: конфигурация, custom types, tracing hooks
- ✅ Production connection pooling: pgxpool vs PgBouncer
- ✅ Продвинутый sqlc: CTE, dynamic queries, batch
- ✅ Zero-downtime migrations
- ✅ Query performance и оптимизация
- ✅ High availability: replicas, retry, circuit breaker
- ✅ Security и Observability

#### 4.2 Кэширование _(в разработке)_
- Redis
- In-memory кэши

#### 4.3 Очереди сообщений _(в разработке)_
- Kafka
- RabbitMQ
- NATS

#### 4.4 gRPC _(в разработке)_
- Protocol Buffers
- Unary и Streaming RPC
- gRPC-Gateway

#### 4.5 Observability _(в разработке)_
- Логирование: log/slog, zap, zerolog
- Метрики: Prometheus
- Трейсинг: OpenTelemetry

#### 4.6 Контейнеризация _(в разработке)_
- Multi-stage Docker builds
- Distroless образы
- Kubernetes

---

### [Часть 5: Практические проекты](./part5-projects/)

#### Проект 1: URL Shortener _(в разработке)_
**Сложность**: Beginner → Intermediate

**Стек**: chi/net/http, PostgreSQL, Redis, Docker

#### Проект 2: E-commerce Platform _(в разработке)_
**Сложность**: Intermediate

**Архитектура**: Микросервисы (gRPC, Kafka, PostgreSQL, Redis)

**Паттерны**: Saga, CQRS, Event Sourcing, Circuit Breaker

#### Проект 3: Trading/Fintech Platform _(в разработке)_
**Сложность**: Advanced

**Фокус**: High-performance, real-time, low-latency

**Технологии**: WebSocket, NATS, TimescaleDB

#### Проект 4: SaaS Platform _(в разработке)_
**Сложность**: Advanced

**Фокус**: Multi-tenant архитектура

---

### [Часть 6: Best Practices](./part6-best-practices/)

#### 6.1 Код и архитектура _(в разработке)_
- Accept interfaces, return structs
- Маленькие интерфейсы
- Composition over inheritance

#### 6.2 Современные возможности Go _(в разработке)_
- Generics (Go 1.18+)
- log/slog
- Улучшения в Go 1.22+

#### 6.3 Инструменты _(в разработке)_
- golangci-lint
- staticcheck
- govulncheck

#### 6.4 Производительность _(в разработке)_
- Минимизация аллокаций
- sync.Pool
- Профилирование

---

## Полезные ресурсы

### Официальная документация
- [Go Documentation](https://go.dev/doc/)
- [Effective Go](https://go.dev/doc/effective_go)
- [Go by Example](https://gobyexample.com)
- [Go Blog](https://go.dev/blog)

### Style Guides
- [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md)
- [Google Go Style Guide](https://google.github.io/styleguide/go/)

---

## Лицензия

Этот проект распространяется под лицензией **MIT License** — см. файл [LICENSE](./LICENSE).

---

**Версия**: 0.4.1
**Последнее обновление**: 2026-01-26
**Статус**: Части 1-3 завершены, Часть 4 в разработке (1/7 разделов)
