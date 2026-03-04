
---

### Part 3: Дополнения к разделу JSON (04_validation_serialization.md)

**Файл**: `part3-web-api/04_validation_serialization.md` — дополнить существующий раздел

**Обоснование**: Раздел хорошо покрывает `encoding/json`, easyjson, sonic и экспериментальный v2. Однако есть несколько практически важных тем, которых нет совсем:

**Что добавить**:

1. **json.Number при работе с `any`**
   - Стандартная ловушка: `json.Unmarshal` в `map[string]any` преобразует все числа в `float64`, что теряет точность для больших `int64`
   - Решение через `json.Decoder.UseNumber()` и `json.Number`
   - Сравнение с C#: `JsonElement`, `JsonDocument` и точное хранение чисел в `System.Text.Json`
   - Актуально для fintech, ID пользователей > 2^53

2. **Потоковая обработка больших JSON (Decoder.Token())**
   - `json.Decoder.Token()` — низкоуровневый streaming, аналог `Utf8JsonReader` / `JsonTextReader` в C#
   - Когда использовать: файлы > 10 MB, неограниченные массивы, парсинг NDJSON-потоков
   - Паттерн: итерация по массиву без загрузки всего в память

3. **go-json (github.com/goccy/go-json)**
   - Добавить в таблицу benchmarks и описание рядом с easyjson/sonic
   - Drop-in замена без кодогенерации, в отличие от easyjson
   - Популярная альтернатива: сравнение трёх быстрых библиотек по сценариям

4. **gjson (github.com/tidwall/gjson)**
   - Быстрое извлечение полей из JSON без полного парсинга структуры
   - Аналог `JObject.SelectToken()` / `JsonPath` в Newtonsoft.Json
   - Когда уместно: middleware, логирование, парсинг webhook-payload без схемы

5. **Актуализация статуса encoding/json/v2**
   - Уточнить текущий статус (март 2026): пакет `github.com/go-json-experiment/json` vs `GOEXPERIMENT=jsonv2`
   - Добавить информацию о новых тегах: `json:",omitzero"`, `json:",format:..."`, `json:",unknown"`
   - Обновить рекомендацию: когда уже можно применять в продакшне

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
- `mockgen` vs `moq`: сравнение подходов, когда что выбрать; расширить до трёх вариантов: `gomock (uber-go)` vs `testify/mock` vs `mockery`
- `stringer` + `enumer`: генерация String()/MarshalJSON() для const-перечислений
- `buf generate`: современный protoc workflow вместо прямого вызова protoc
- Сравнение с C# Source Generators и T4 Templates
- `mockery` (github.com/vektra/mockery) — testify-совместимые моки, `mockery.yaml`, автообнаружение интерфейсов; добавить в сравнительную таблицу
- `ent` (entgo.io) — ORM с кодогенерацией: схема на Go → типобезопасный query builder; C# аналог: EF Core `Scaffold-DbContext`; нет нигде в курсе
- Написание собственного генератора: `go/ast` для анализа → `text/template` для вывода → `go/format` для форматирования; C# аналог: Roslyn `ISourceGenerator`
- Актуализировать путь `golang/mock` → `go.uber.org/mock` в `06_testing_benchmarking.md` (оригинал заархивирован в 2023, в тексте курса указан устаревший путь)
- Актуализировать `oapi-codegen` в `05_api_documentation.md`: пакет переехал `deepmap/oapi-codegen` → `oapi-codegen/oapi-codegen` (с v2, 2023)

---

### Part 6: Публикация модуля на GitHub (расширение существующего файла)

**Файл**: `part6-best-practices/02_tools.md` — добавить подраздел в секцию `go mod`

**Обоснование**: В курсе описано только **потребление** пакетов (import, GOPROXY, GOPRIVATE). Темы публикации собственного модуля нет нигде — ни в part1 (раздел "Пакеты и импорты" покрывает лишь синтаксис), ни в part6. C# разработчики знают NuGet publish workflow (`dotnet pack`, `dotnet nuget push`, nuget.org) — нужна прямая проекция на Go-эквивалент.

**Что добавить**:
- Правильный module path: `go mod init github.com/user/pkg` и почему путь = URL репозитория
- Git-теги для версионирования: `git tag v1.2.3 && git push --tags`
- Семантическое версионирование и major version suffix (`v2/`, `/v2` в пути модуля)
- pkg.go.dev: автоматическая индексация и документация
- godoc-комментарии для публичного API (Package comment, exported symbols)
- Структура репозитория-библиотеки (vs бинарного проекта)
- Сравнение с NuGet: `dotnet pack` → git tag, `nuget push` → git push, nuspec → go.mod
- Типичные ошибки: неверный module path, публикация v2 без /v2, отсутствие тегов

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
