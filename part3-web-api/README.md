# Часть 3: Web API разработка

## Описание

Разработка HTTP API на Go: от базового net/http до продакшн-ready приложений с правильной архитектурой.

## Статус

✅ **Завершено** (100%)

## Материалы

### 3.1 [HTTP в Go](./01_http_server.md)
- net/http: Handler и HandlerFunc
- ServeMux и роутинг (включая Go 1.22+)
- Работа с Request и Response
- Graceful Shutdown
- Middleware pattern
- Популярные роутеры: chi, gin, echo, fiber
- Context в HTTP handlers
- 3 практических примера

### 3.2 [Структура проекта](./02_project_structure.md)
- Flat structure для микросервисов
- Standard Go Project Layout
- Clean Architecture в Go
- Dependency Injection: Manual, Wire, Fx
- Configuration: env vars, viper
- 3 практических примера

### 3.3 [Работа с данными](./03_database.md)
- database/sql: connection pool, queries, transactions
- pgx: batch, COPY, Listen/Notify
- sqlc: type-safe SQL, code generation
- GORM: когда нужен ORM
- Миграции: golang-migrate, goose
- Repository Pattern
- 3 практических примера

### 3.4 [Валидация и сериализация](./04_validation_serialization.md)
- encoding/json: struct tags, custom marshal
- Быстрые библиотеки: easyjson, sonic
- go-playground/validator
- Request/Response DTO
- Protocol Buffers
- 3 практических примера

### 3.5 [Документация API](./05_api_documentation.md)
- OpenAPI Specification
- swaggo: документация из кода
- oapi-codegen: OpenAPI-first подход
- Swagger UI интеграция
- Версионирование API
- CI/CD интеграция
- 2 практических примера

## Время изучения

**Примерно**: 2-3 недели

## Ключевые навыки

После изучения этой части вы сможете:

- Создавать production-ready HTTP API
- Организовывать код по Clean Architecture
- Работать с PostgreSQL через pgx и sqlc
- Валидировать входные данные
- Генерировать документацию Swagger

---

[← Назад к оглавлению](../README.md) | [Предыдущая часть](../part2-advanced/) | [Следующая часть →](../part4-infrastructure/)
