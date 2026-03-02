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

<!-- AUTO: STRUCTURE -->
### [Часть 1: Основы Go (Быстрый старт)](./part1-basics/)

- [Установка и настройка окружения Go](./part1-basics/01_setup_environment.md)
- [Синтаксис и базовые концепции (сравнение с C#)](./part1-basics/02_syntax_basics.md)
- [Коллекции и производительность: Шпаргалка для C# разработчика](./part1-basics/02a_collections_performance_cheatsheet.md)
- [Ключевые отличия от C#](./part1-basics/03_key_differences.md)
- [Практика: Закрепление основ](./part1-basics/04_practice.md)

---

### [Часть 2: Продвинутые темы](./part2-advanced/)

- [Горутины и каналы](./part2-advanced/01_goroutines_channels.md)
- [Go Runtime и планировщик](./part2-advanced/02_runtime_scheduler.md)
- [2.2a Аллокатор памяти Go (Memory Allocator Internals)](./part2-advanced/02a_memory_allocator.md)
- [Сборка мусора (GC)](./part2-advanced/03_gc.md)
- [Примитивы синхронизации](./part2-advanced/04_sync_primitives.md)
- [Обработка ошибок (продвинутый уровень)](./part2-advanced/05_error_handling.md)
- [Тестирование и бенчмаркинг](./part2-advanced/06_testing_benchmarking.md)
- [Профилирование и оптимизация](./part2-advanced/07_profiling_optimization.md)

---

### [Часть 3: Web API разработка](./part3-web-api/)

- [HTTP в Go: Создание веб-серверов](./part3-web-api/01_http_server.md)
- [Структура проекта Go](./part3-web-api/02_project_structure.md)
- [Работа с данными (PostgreSQL)](./part3-web-api/03_database.md)
- [Валидация и сериализация](./part3-web-api/04_validation_serialization.md)
- [Документация API](./part3-web-api/05_api_documentation.md)

---

### [Часть 4: Инфраструктура и интеграции](./part4-infrastructure/)

- [Production PostgreSQL](./part4-infrastructure/01_production_postgresql.md)
- [Кэширование](./part4-infrastructure/02_caching.md)
- [Очереди сообщений](./part4-infrastructure/03_message_queues.md)
- [gRPC](./part4-infrastructure/04_grpc.md)
- [Observability: Логирование, Метрики, Трейсинг](./part4-infrastructure/05_observability.md)
- [Конфигурация: Управление настройками в Go](./part4-infrastructure/06_config.md)
- [Контейнеризация: Docker, Compose и Kubernetes для Go](./part4-infrastructure/07_containerization.md)

---

### [Проект 1: URL Shortener](./part5-project1-url-shortener/)

- [Доменная модель и сервисный слой](./part5-project1-url-shortener/01_domain.md)
- [Хранилище: PostgreSQL и Redis](./part5-project1-url-shortener/02_storage.md)
- [HTTP слой: net/http и chi](./part5-project1-url-shortener/03_http.md)
- [Тестирование и бенчмарки](./part5-project1-url-shortener/04_testing.md)
- [Деплой: Docker Compose и Production](./part5-project1-url-shortener/05_deployment.md)

---

### [Проект 2: E-commerce Platform](./part5-project2-ecommerce/)

- [Доменная модель и контракты](./part5-project2-ecommerce/01_domain.md)
- [User Service](./part5-project2-ecommerce/02_user_service.md)
- [Catalog Service (CQRS)](./part5-project2-ecommerce/03_catalog_service.md)
- [Order Service (Saga Pattern)](./part5-project2-ecommerce/04_order_service.md)
- [Payment Service и Notification Service](./part5-project2-ecommerce/05_payment_notification.md)
- [API Gateway](./part5-project2-ecommerce/06_api_gateway.md)
- [Деплой и наблюдаемость](./part5-project2-ecommerce/07_deployment.md)

---

### [Часть 6: Best Practices Go](./part6-best-practices/)

- [Код и архитектура](./part6-best-practices/01_code_architecture.md)
- [Инструменты](./part6-best-practices/02_tools.md)
- [Производительность](./part6-best-practices/03_performance.md)
- [Production Checklist](./part6-best-practices/04_production_checklist.md)

---

### [Часть 7: Лайфкодинг на собеседованиях в российских компаниях](./part7-interview/)

- [Задачи на слайсы и массивы](./part7-interview/01_slices_arrays.md)
- [Задачи на горутины и каналы](./part7-interview/02_goroutines_channels.md)
- [Задачи на map и синхронизацию](./part7-interview/03_maps_sync.md)
- [Алгоритмические задачи](./part7-interview/04_algorithms.md)
- [Системный дизайн на Go](./part7-interview/05_system_design.md)
<!-- /AUTO: STRUCTURE -->

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
- Go: идиомы и паттерны проектирования — Джон Боднер
- 100 ошибок Go и как их избежать — Теива Харшани

### Style Guides
- [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md)
- [Google Go Style Guide](https://google.github.io/styleguide/go/)

---

## Лицензия

Этот проект распространяется под лицензией **MIT License** — см. файл [LICENSE](./LICENSE).

---

<!-- AUTO: VERSION -->
**Версия**: 0.8.0 (Части 1-4, 6 и 7 завершены; Проекты 1-2 завершены; Целевая версия Go 1.26+)
<!-- /AUTO: VERSION -->
