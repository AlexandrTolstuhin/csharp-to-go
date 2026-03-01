# Часть 3: Web API разработка

## Описание

Разработка HTTP API на Go: от базового net/http до продакшн-ready приложений с правильной архитектурой.

<!-- AUTO: MATERIALS -->
## Материалы

### 1. [3.1 HTTP в Go: Создание веб-серверов](./01_http_server.md)

- Введение
- Философия: net/http vs ASP.NET Core
- net/http: основы
- Middleware Pattern
- Популярные роутеры
- Context в HTTP handlers
- Практические примеры

### 2. [3.2 Структура проекта Go](./02_project_structure.md)

- Введение
- Философия структуры в Go
- Flat Structure (плоская структура)
- Standard Go Project Layout
- Clean Architecture в Go
- Dependency Injection
- Configuration
- Практические примеры

### 3. [3.3 Работа с данными (PostgreSQL)](./03_database.md)

- Введение
- Подходы к работе с БД в Go
- database/sql: стандартная библиотека
- pgx: Production PostgreSQL Driver
- sqlc: Type-Safe SQL
- GORM: когда нужен ORM
- Миграции базы данных
- Repository Pattern
- Практические примеры

### 4. [3.4 Валидация и сериализация](./04_validation_serialization.md)

- Введение
- JSON в Go
- Быстрые JSON библиотеки
- Валидация: go-playground/validator
- Request/Response DTO
- Protocol Buffers
- JSON v2 и производительность io.ReadAll (Go 1.25-1.26)
- Практические примеры

### 5. [3.5 Документация API](./05_api_documentation.md)

- Введение
- Подходы к документации
- OpenAPI Specification
- swaggo: документация из кода
- OpenAPI-first подход
- Практические аспекты
- Практические примеры
<!-- /AUTO: MATERIALS -->

---

<!-- AUTO: NAV -->
[← Назад к оглавлению](../README.md) | [Предыдущая часть: Часть 2: Продвинутые темы](../part2-advanced/) | [Следующая часть: Часть 4: Инфраструктура →](../part4-infrastructure/)
<!-- /AUTO: NAV -->
