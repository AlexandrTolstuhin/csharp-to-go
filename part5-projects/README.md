# Часть 5: Практические проекты

## Описание

Реальные проекты для закрепления навыков: от простого URL Shortener до сложной SaaS платформы.

## Статус

🚧 **В разработке** (1/4 завершено)

## Проекты

### [Проект 1: URL Shortener](./project1-url-shortener/) ✅
**Сложность**: Beginner → Intermediate

**Цель**: Освоение базовых концепций

**Технологии**:
- net/http (Go 1.22+) и chi
- PostgreSQL + pgx v5
- Redis для кэша (cache-aside)
- Docker Compose

**Функциональность**:
- Создание короткой ссылки
- Редирект по ключу
- Статистика переходов
- Rate limiting (token bucket)
- Health checks

**Разделы**:
1. [Доменная модель и сервисный слой](./project1-url-shortener/01_domain.md)
2. [Хранилище: PostgreSQL и Redis](./project1-url-shortener/02_storage.md)
3. [HTTP слой: net/http и chi](./project1-url-shortener/03_http.md)
4. [Тестирование и бенчмарки](./project1-url-shortener/04_testing.md)
5. [Деплой: Docker Compose и Production](./project1-url-shortener/05_deployment.md)

**Время**: ~1 неделя | **Статус**: ✅ Завершено

---

### Проект 2: E-commerce Platform
**Сложность**: Intermediate

**Цель**: Микросервисная архитектура

**Сервисы**:
1. API Gateway
2. User Service (JWT auth)
3. Catalog Service
4. Order Service
5. Payment Service
6. Notification Service

**Технологии**:
- gRPC для межсервисного взаимодействия
- Kafka для событий
- PostgreSQL (per service)
- Redis для кэша
- OpenTelemetry для трейсинга

**Паттерны**:
- Saga pattern
- CQRS
- Event Sourcing
- Circuit Breaker

**Время**: ~3-4 недели

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

## Рекомендации

- Начните с Проекта 1 вне зависимости от опыта
- Каждый проект должен быть production-ready
- Используйте Docker Compose для локальной разработки
- Пишите тесты (unit + integration)
- Настройте CI/CD
- Добавьте observability с первого дня

---

[← Назад к оглавлению](../README.md) | [Предыдущая часть](../part4-infrastructure/) | [Следующая часть →](../part6-best-practices/)
