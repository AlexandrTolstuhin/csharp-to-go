# Часть 3: Web API разработка

## Описание

Разработка HTTP API на Go: от базового net/http до продакшн-ready приложений с правильной архитектурой.

## Статус

🚧 **В разработке** (20%)

## Материалы

### ✅ Завершено

#### 3.1 [HTTP в Go](./01_http_server.md)
- net/http: Handler и HandlerFunc
- ServeMux и роутинг (включая Go 1.22+)
- Работа с Request и Response
- Graceful Shutdown
- Middleware pattern
- Популярные роутеры: chi, gin, echo, fiber
- Context в HTTP handlers
- 3 практических примера

### 🚧 В разработке

#### 3.2 Структура проекта
- Standard Go Project Layout
- Flat structure vs DDD
- Clean Architecture в Go
- Dependency Injection (Wire, Fx, manual)

#### 3.3 Работа с данными
- PostgreSQL: database/sql, pgx
- ORM vs Query Builder vs Raw SQL
- sqlc: type-safe SQL
- Миграции: golang-migrate, goose

#### 3.4 Валидация и сериализация
- encoding/json
- go-playground/validator
- Protocol Buffers

#### 3.5 Документация API
- Swagger/OpenAPI с swaggo
- OpenAPI-first подход

## Время изучения

**Примерно**: 2-3 недели

---

[← Назад к оглавлению](../README.md) | [Предыдущая часть](../part2-advanced/) | [Следующая часть →](../part4-infrastructure/)
