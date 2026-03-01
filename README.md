# Переход с C# на Go: Курс для C# разработчика

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Go Version](https://img.shields.io/badge/Go-1.26+-00ADD8?logo=go)](https://go.dev/)
[![Progress](https://img.shields.io/badge/Progress-95%25-green)](./STRUCTURE.md)
[![GitHub Stars](https://img.shields.io/github/stars/AlexandrTolstuhin/csharp-to-go?style=social)](https://github.com/AlexandrTolstuhin/csharp-to-go)

> Комплексный курс по изучению Go для опытного C# разработчика с фокусом на async/await, concurrency, производительность и продакшн-ready практики.

**Репозиторий:** [github.com/AlexandrTolstuhin/csharp-to-go](https://github.com/AlexandrTolstuhin/csharp-to-go)

---

## О курсе

**Целевая аудитория**: C# разработчик с опытом async/await, TPL, высоконагруженных систем

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
- **+** [Аллокатор памяти Go](./part2-advanced/02a_memory_allocator.md)
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

### [Часть 4: Инфраструктура и интеграции](./part4-infrastructure/) — **Завершено**

- **4.1** [Production PostgreSQL](./part4-infrastructure/01_production_postgresql.md)
- **4.2** [Кэширование](./part4-infrastructure/02_caching.md)
- **4.3** [Очереди сообщений](./part4-infrastructure/03_message_queues.md)
- **4.4** [gRPC](./part4-infrastructure/04_grpc.md)
- **4.5** [Observability](./part4-infrastructure/05_observability.md)
- **4.6** [Конфигурация](./part4-infrastructure/06_config.md)
- **4.7** [Контейнеризация](./part4-infrastructure/07_containerization.md)

---

### [Часть 5: Практические проекты](./part5-projects/)

#### [Проект 1: URL Shortener](./part5-projects/project1-url-shortener/) ✅
**Сложность**: Beginner → Intermediate

**Стек**: net/http + chi, PostgreSQL (pgx), Redis, Docker Compose

- ✅ Доменная модель, интерфейсы, генерация Base62 кодов
- ✅ PostgreSQL репозиторий (pgx v5), Redis cache-aside
- ✅ HTTP API: net/http (Go 1.22+) → миграция на chi
- ✅ Middleware: logging, recovery, rate limiting
- ✅ Unit + handler + integration тесты, бенчмарки
- ✅ Docker Compose, Dockerfile (scratch), graceful shutdown

#### [Проект 2: E-commerce Platform](./part5-projects/project2-ecommerce/) ✅
**Сложность**: Intermediate

**Стек**: gRPC + buf, Kafka (kafka-go), PostgreSQL (pgx), Redis, OpenTelemetry + Jaeger, Kubernetes

- ✅ Proto контракты (buf), доменные модели, Kafka события (shared/events)
- ✅ User Service: JWT (golang-jwt/v5), bcrypt, gRPC сервер, testcontainers
- ✅ Catalog Service: CQRS (command/ + query/), SELECT FOR UPDATE, Redis кэш, Kafka инвалидация
- ✅ Order Service: Saga (хореография), state machine, Kafka consumer/producer
- ✅ Payment Service: идемпотентность (ON CONFLICT DO NOTHING), Kafka consumer
- ✅ Notification Service: Kafka consumer, SMTP / LogSender
- ✅ API Gateway: chi, JWT middleware, Circuit Breaker (gobreaker), rate limiting
- ✅ Docker Compose (dev + prod), Distroless Dockerfile, Kubernetes HPA, Makefile

#### Проект 3: Trading/Fintech Platform _(в разработке)_
**Сложность**: Advanced

**Фокус**: High-performance, real-time, low-latency

**Технологии**: WebSocket, NATS, TimescaleDB

#### Проект 4: SaaS Platform _(в разработке)_
**Сложность**: Advanced

**Фокус**: Multi-tenant архитектура

---

### [Часть 6: Best Practices](./part6-best-practices/) — **Завершено**

- **6.1** [Код и архитектура](./part6-best-practices/01_code_architecture.md)
- **6.2** [Инструменты](./part6-best-practices/02_tools.md)
- **6.3** [Производительность](./part6-best-practices/03_performance.md)
- **6.4** [Production Checklist](./part6-best-practices/04_production_checklist.md)

---

### [Часть 7: Лайфкодинг на собеседованиях](./part7-interview/) — **Завершено**

> Реальные задачи от Яндекса, Авито, Озона, Тинькофф, ВКонтакте, Wildberries и других российских компаний.

- **7.1** [Задачи на слайсы и массивы](./part7-interview/01_slices_arrays.md) — reverse, deduplicate, rotate, gotchas
- **7.2** [Задачи на горутины и каналы](./part7-interview/02_goroutines_channels.md) — worker pool, fan-out/in, pipeline, pub/sub
- **7.3** [Задачи на map и синхронизацию](./part7-interview/03_maps_sync.md) — concurrent cache, Once, semaphore, COW map
- **7.4** [Алгоритмические задачи](./part7-interview/04_algorithms.md) — LRU cache, two sum, стек, очередь, бинарный поиск
- **7.5** [Системный дизайн на Go](./part7-interview/05_system_design.md) — TTL cache, rate limiter, priority queue, circuit breaker

---

## Полезные ресурсы

### Официальная документация
- [Go Documentation](https://go.dev/doc/)
- [Effective Go](https://go.dev/doc/effective_go)
- [Go by Example](https://gobyexample.com)
- [Go Blog](https://go.dev/blog)
- [Go Source Code](https://cs.opensource.google/go/go)

### Интерактивное обучение
- [Ultimate Go Tour (Ardan Labs)](https://tour.ardanlabs.com/tour)

### Книги
- Язык программирования Go — Донован, Керниган
- Go: идиомы и паттерны проектирования — Джон Бодner
- 100 ошибок Go и как их избежать — Теива Харшани

### Style Guides
- [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md)
- [Google Go Style Guide](https://google.github.io/styleguide/go/)

---

## Лицензия

Этот проект распространяется под лицензией **MIT License** — см. файл [LICENSE](./LICENSE).

---

**Версия**: 0.8.0
**Последнее обновление**: 2026-03-01
**Статус**: Части 1-4, 6 и 7 завершены, Часть 5 — Проекты 1-2 завершены (2/4)
