# Summary

[Введение](README.md)

# Часть 1: Основы Go

- [1.1 Установка и настройка окружения](part1-basics/01_setup_environment.md)
- [1.2 Синтаксис и базовые концепции](part1-basics/02_syntax_basics.md)
  - [Коллекции и производительность: шпаргалка](part1-basics/02a_collections_performance_cheatsheet.md)
- [1.3 Ключевые отличия от C#](part1-basics/03_key_differences.md)

# Часть 2: Углублённые темы

- [2.1 Горутины и каналы](part2-advanced/01_goroutines_channels.md)
- [2.2 Go Runtime и планировщик](part2-advanced/02_runtime_scheduler.md)
  - [2.2a Аллокатор памяти Go](part2-advanced/02a_memory_allocator.md)
- [2.3 Сборка мусора (GC)](part2-advanced/03_gc.md)
- [2.4 Примитивы синхронизации](part2-advanced/04_sync_primitives.md)
- [2.5 Обработка ошибок](part2-advanced/05_error_handling.md)
- [2.6 Тестирование и бенчмаркинг](part2-advanced/06_testing_benchmarking.md)
- [2.7 Профилирование и оптимизация](part2-advanced/07_profiling_optimization.md)

# Часть 3: Web API

- [3.1 HTTP в Go: веб-серверы](part3-web-api/01_http_server.md)
- [3.2 Структура проекта](part3-web-api/02_project_structure.md)
- [3.3 Работа с данными (PostgreSQL)](part3-web-api/03_database.md)
- [3.4 Валидация и сериализация](part3-web-api/04_validation_serialization.md)
- [3.5 Документация API](part3-web-api/05_api_documentation.md)

# Часть 4: Инфраструктура

- [4.1 Production PostgreSQL](part4-infrastructure/01_production_postgresql.md)
- [4.2 Кэширование](part4-infrastructure/02_caching.md)
- [4.3 Очереди сообщений](part4-infrastructure/03_message_queues.md)
- [4.4 gRPC](part4-infrastructure/04_grpc.md)
- [4.5 Observability](part4-infrastructure/05_observability.md)
- [4.6 Конфигурация](part4-infrastructure/06_config.md)
- [4.7 Контейнеризация](part4-infrastructure/07_containerization.md)

# Часть 5: Практические проекты

- [Проект 1: URL Shortener](part5-project1-url-shortener/README.md)
  - [1. Доменная модель](part5-project1-url-shortener/01_domain.md)
  - [2. Хранилище](part5-project1-url-shortener/02_storage.md)
  - [3. HTTP слой](part5-project1-url-shortener/03_http.md)
  - [4. Тестирование](part5-project1-url-shortener/04_testing.md)
  - [5. Деплой](part5-project1-url-shortener/05_deployment.md)
- [Проект 2: E-Commerce Platform](part5-project2-ecommerce/README.md)
  - [1. Доменная модель](part5-project2-ecommerce/01_domain.md)
  - [2. User Service](part5-project2-ecommerce/02_user_service.md)
  - [3. Catalog Service](part5-project2-ecommerce/03_catalog_service.md)
  - [4. Order Service](part5-project2-ecommerce/04_order_service.md)
  - [5. Payment & Notification](part5-project2-ecommerce/05_payment_notification.md)
  - [6. API Gateway](part5-project2-ecommerce/06_api_gateway.md)
  - [7. Деплой](part5-project2-ecommerce/07_deployment.md)

# Часть 6: Лучшие практики

- [6.1 Код и архитектура](part6-best-practices/01_code_architecture.md)
- [6.2 Инструменты](part6-best-practices/02_tools.md)
- [6.3 Производительность](part6-best-practices/03_performance.md)
- [6.4 Production Checklist](part6-best-practices/04_production_checklist.md)

# Часть 7: Подготовка к собеседованию

- [7.1 Задачи на слайсы и массивы](part7-interview/01_slices_arrays.md)
- [7.2 Задачи на горутины и каналы](part7-interview/02_goroutines_channels.md)
- [7.3 Задачи на map и синхронизацию](part7-interview/03_maps_sync.md)
- [7.4 Алгоритмические задачи](part7-interview/04_algorithms.md)
- [7.5 Системный дизайн на Go](part7-interview/05_system_design.md)
