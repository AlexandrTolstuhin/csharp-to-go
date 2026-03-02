
---

## Доработки существующих частей

### Part 1: Generics (новый файл)

**Файл**: `part1-basics/05_generics.md`

**Обоснование**: В курсе есть фрагменты с дженериками в контексте performance и sync.Pool, но нет самостоятельного введения для C# разработчиков, которые привыкли к `List<T>`, `Dictionary<TKey,TValue>`, generic-методам и constraints.

**Содержание**:
- Type parameters: синтаксис `[T any]`, `[T comparable]`
- Встроенные constraints (`comparable`, `constraints.Ordered`)
- Generic функции vs generic типы
- Параметризованные структуры
- Сравнение с C# generics (where T : class, new(), IComparable)
- Ограничения: нет specialization, нет variance
- Когда использовать generics, когда interface{}
- Паттерны: typed collections, functional helpers (Map, Filter, Reduce)

---

### Part 3: Аутентификация и авторизация (новый файл)

**Файл**: `part3-web-api/06_auth.md`

**Обоснование**: В курсе Auth упоминается в 7 файлах (~50-100 строк суммарно), но нет полного раздела. C# разработчики знают ASP.NET Identity, [Authorize], JWT Bearer — нужна прямая проекция на Go.

**Содержание**:
- JWT: генерация, подпись, проверка (golang-jwt/jwt)
- Middleware для аутентификации в net/http и популярных роутерах
- Access token + Refresh token: реализация и хранение
- OAuth2: client credentials и authorization code flow (golang.org/x/oauth2)
- RBAC: простая ролевая модель
- Сравнение с C#: [Authorize], ClaimsPrincipal, IAuthenticationHandler
- Типичные ошибки: хранение секрета в коде, отсутствие проверки alg

---

### Part 2: Reflection (новый файл)

**Файл**: `part2-advanced/08_reflection.md`

**Обоснование**: В курсе reflection встречается вскользь (reflect.Select в задаче на каналы, reflect.Type в конфиге), с акцентом на антипаттерны. Нет систематического раздела для C# разработчиков, привыкших к богатому Reflection API.

**Содержание**:
- reflect.Type и reflect.Value: основы
- Инспекция struct-тегов (как работает encoding/json внутри)
- Динамический вызов методов
- Сравнение с C# Reflection: Type.GetProperties, MethodInfo.Invoke
- Когда reflect оправдан: сериализаторы, ORM, DI-контейнеры, codegen
- Антипаттерны: reflect в hot path, альтернативы через codegen
- reflect.Select: динамический select по каналам
- go/ast как альтернатива для codegen

---

### Part 6: Code generation (расширение существующего файла)

**Файл**: `part6-best-practices/02_tools.md` — добавить разделы

**Обоснование**: Базовый раздел `go generate` с таблицей инструментов есть, но нет практических примеров. C# разработчики знают Source Generators и T4 — нужна проекция.

**Что добавить**:
- `sqlc`: полный workflow — схема → `sqlc.yaml` → генерация → использование
- `mockgen` vs `moq`: сравнение подходов, когда что выбрать
- `stringer` + `enumer`: генерация String()/MarshalJSON() для const-перечислений
- `buf generate`: современный protoc workflow вместо прямого вызова protoc
- Сравнение с C# Source Generators и T4 Templates

---

### Part 1: go work / workspaces (расширение существующего файла)

**Файл**: `part1-basics/01_setup_environment.md` или `part6-best-practices/02_tools.md`

**Обоснование**: `go.work` (Go 1.18+) не раскрыт. Нужен для монорепозиториев и локальной разработки нескольких связанных модулей — типичный сценарий при переходе с .NET Solution.

**Что добавить**:
- `go work init`, `go work use`, `go work sync`
- Структура `go.work` файла
- Когда использовать workspaces vs `replace` directive
- Сравнение с .NET Solution (.sln) и project references

---

### Проект 3: Trading/Fintech Platform
**Сложность**: Advanced

**Цель**: High-performance, real-time система

**Компоненты**:
1. Market Data Service (WebSocket)
2. Order Matching Engine
3. Portfolio Service
4. Risk Service
5. Analytics Service

**Технологии**:
- WebSocket + горутины
- NATS для low-latency
- TimescaleDB
- Redis Streams
- Kubernetes + HPA

**Фокус**:
- Оптимизация latency
- Lock-free структуры
- Профилирование и тюнинг GC

**Время**: ~4 недели

---

### Проект 4: SaaS Platform
**Сложность**: Advanced

**Цель**: Multi-tenant архитектура

**Компоненты**:
1. Tenant Service
2. Identity Service (OAuth2, RBAC)
3. Core API
4. Webhook Service
5. Background Workers
6. Admin Dashboard API
7. Analytics Service (ClickHouse)

**Технологии**:
- Schema-per-tenant PostgreSQL (транзакционные данные)
- Row-level security
- Feature flags
- Rate limiting per tenant
- **ClickHouse** — аналитика и метрики (OLAP)

**ClickHouse в проекте**:
- Usage metrics per tenant: запросы, API calls, потребление ресурсов
- Billing events — агрегация для тарификации
- Audit log — действия пользователей, compliance
- Изоляция тенантов: Row Policies, отдельные схемы per tenant
- Архитектурный паттерн: OLTP (PostgreSQL) + OLAP (ClickHouse) разделение

**Паттерны**:
- Multi-tenant isolation
- OLTP + OLAP separation
- Event-driven analytics

**Время**: ~4-5 недель

---
