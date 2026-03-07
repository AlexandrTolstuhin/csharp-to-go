## Доработки существующих частей

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
- Redis Streams  <!-- TODO: пересмотреть — NATS JetStream покрывает те же сценарии; Redis Streams оправдан только если Redis уже в стеке ради кэша/rate limiting -->
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
