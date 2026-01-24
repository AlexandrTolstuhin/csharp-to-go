# 🚀 Переход с C# на Go: Курс для Senior разработчика

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Go Version](https://img.shields.io/badge/Go-1.23+-00ADD8?logo=go)](https://go.dev/)
[![Progress](https://img.shields.io/badge/Progress-26%25-orange)](./STRUCTURE.md)
[![GitHub Stars](https://img.shields.io/github/stars/AlexandrTolstuhin/csharp-to-go?style=social)](https://github.com/AlexandrTolstuhin/csharp-to-go)

> Комплексный курс по изучению Go для опытного C# разработчика с фокусом на async/await, concurrency, производительность и продакшн-ready практики.

**🎯 Репозиторий:** [github.com/AlexandrTolstuhin/csharp-to-go](https://github.com/AlexandrTolstuhin/csharp-to-go)

---

## 📋 О курсе

**Целевая аудитория**: Senior C# разработчик с глубоким опытом async/await, TPL, высоконагруженных систем

**Формат**: Теория + практика + реальные проекты (E-commerce, Fintech, SaaS)

**Особенности**:
- 🔄 Постоянное сравнение с C#
- ⚡ Фокус на производительность и GC
- 🏗️ Продакшн-ready практики
- 🎯 Практические проекты

---

## 📚 Структура курса

### [Часть 1: Основы Go (Быстрый старт)](./part1-basics/)

#### 1.1 [Установка и настройка окружения](./part1-basics/01_setup_environment.md)
- ✅ Установка Go 1.23+
- ✅ Настройка GOPATH, GOROOT, Go Modules
- ✅ IDE: GoLand vs VSCode
- ✅ Инструменты: go fmt, go vet, golangci-lint
- ✅ Первый проект

#### 1.2 [Синтаксис и базовые концепции](./part1-basics/02_syntax_basics.md)
- ✅ Сравнение синтаксиса C# ↔ Go
- ✅ Переменные, типы, константы
- ✅ Коллекции: массивы, слайсы, мапы
- ✅ **Производительность коллекций и GC** ⚡
- ✅ Управляющие конструкции
- ✅ Функции и замыкания
- ✅ Defer
- ✅ Указатели
- ✅ Структуры и методы
- ✅ Интерфейсы (duck typing)
- ✅ Пакеты и импорты

#### 📎 [Шпаргалка: Производительность коллекций](./part1-basics/02a_collections_performance_cheatsheet.md)
- ✅ Оптимизация слайсов, мап, строк
- ✅ Escape Analysis
- ✅ Паттерны оптимизации
- ✅ Профилирование

#### 1.3 [Ключевые отличия от C#](./part1-basics/03_key_differences.md)
- ✅ Философия языков (C# vs Go)
- ✅ Отсутствие классов и наследования
- ✅ Error handling vs Exceptions
- ✅ Композиция vs наследование
- ✅ Zero values
- ✅ Видимость через регистр
- ✅ **Идиоматичные различия** (nil, LINQ vs циклы, async/await vs goroutines, конструкторы, generics, properties)
- ✅ Практические примеры (HTTP handlers, работа с БД)

#### 1.4 [Практика: мини-проекты](./part1-basics/04_practice.md)
- ✅ CLI-утилита для работы с файлами
- ✅ HTTP-сервер с JSON API
- ✅ Конкурентная обработка данных
- ✅ Парсер логов

---

### [Часть 2: Продвинутые темы](./part2-advanced/)

#### 2.1 [Горутины и каналы](./part2-advanced/01_goroutines_channels.md)
- ✅ Goroutines vs C# Task/Thread
- ✅ Каналы vs C# Channel<T>
- ✅ Буферизированные и небуферизированные каналы
- ✅ Select statement (vs Task.WhenAny)
- ✅ Context и cancellation (vs CancellationToken)
- ✅ Паттерны: Worker Pool, Fan-Out/Fan-In, Pipeline, Semaphore
- ✅ errgroup для обработки ошибок
- ✅ Утечки горутин и их предотвращение

#### 2.2 [Go Runtime и планировщик](./part2-advanced/02_runtime_scheduler.md)
- ✅ Архитектура GMP (Goroutine, Machine, Processor)
- ✅ Work-stealing алгоритм
- ✅ Cooperative vs Signal-based preemption
- ✅ GOMAXPROCS и его влияние
- ✅ Сравнение с .NET ThreadPool
- ✅ Трассировка: go tool trace, GODEBUG=schedtrace
- ✅ Оптимизация под планировщик

#### 2.3 [Сборка мусора (GC)](./part2-advanced/03_gc.md)
- ✅ Tri-color mark-and-sweep алгоритм
- ✅ Архитектура Go GC vs .NET GC (generational vs concurrent)
- ✅ Write barriers и concurrent GC
- ✅ GOGC и GOMEMLIMIT — настройка памяти
- ✅ Escape Analysis: Stack vs Heap аллокации
- ✅ Профилирование с pprof и GODEBUG=gctrace
- ✅ Оптимизация под GC (избегание аллокаций)
- ✅ sync.Pool для переиспользования объектов
- ✅ Практика: JSON парсинг, мониторинг GC, настройка для контейнеров

#### 2.4 [Примитивы синхронизации](./part2-advanced/04_sync_primitives.md)
- ✅ Mutex vs C# lock (defer для разблокировки)
- ✅ RWMutex vs ReaderWriterLockSlim
- ✅ Deadlock и как его избежать
- ✅ WaitGroup vs Task.WhenAll (с errgroup)
- ✅ Once vs Lazy<T> (singleton инициализация)
- ✅ Cond vs Monitor.Wait/Pulse (предпочтение каналам)
- ✅ Atomic операции: atomic.Int64, atomic.Value
- ✅ sync.Map vs ConcurrentDictionary
- ✅ Выбор правильного примитива
- ✅ **golang.org/x/sync**: errgroup, semaphore, singleflight
- ✅ Практика: Rate Limiter, метрики, Connection Pool

#### 2.5 Обработка ошибок _(в разработке)_
- error как интерфейс
- Wrapping ошибок
- errors.Is() и errors.As()
- Sentinel vs typed errors
- Panic/recover

#### 2.6 Тестирование и бенчмаркинг _(в разработке)_
- testing package
- Table-driven tests
- Benchmarks
- Fuzzing (Go 1.18+)
- Моки и интеграционные тесты

#### 2.7 Профилирование и оптимизация _(в разработке)_
- pprof (CPU, Memory)
- go tool trace
- Race detector
- Benchstat

---

### [Часть 3: Web API разработка](./part3-web-api/)

#### 3.1 HTTP в Go _(в разработке)_
- net/http
- Роутеры: chi, gin, echo
- Middleware pattern

#### 3.2 Структура проекта _(в разработке)_
- Standard Go Project Layout
- Clean Architecture в Go
- Dependency Injection (Wire, Fx)

#### 3.3 Работа с данными _(в разработке)_
- PostgreSQL (pgx, sqlc, GORM)
- Валидация (go-playground/validator)
- OpenAPI/Swagger

---

### [Часть 4: Инфраструктура и интеграции](./part4-infrastructure/)

#### 4.1 Базы данных _(в разработке)_
- PostgreSQL: pgx, sqlc
- Миграции
- Connection pooling

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

## 🌐 Полезные ресурсы

### Официальная документация
- [Go Documentation](https://go.dev/doc/)
- [Effective Go](https://go.dev/doc/effective_go)
- [Go by Example](https://gobyexample.com)
- [Go Blog](https://go.dev/blog)

### Style Guides
- [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md)
- [Google Go Style Guide](https://google.github.io/styleguide/go/)

---

## 📄 Лицензия

Этот проект распространяется под лицензией **MIT License** — см. файл [LICENSE](./LICENSE).

---

**Версия**: 0.2.7
**Последнее обновление**: 2026-01-24
**Статус**: 🟢 Часть 1 завершена, Часть 2 в разработке (57%)
