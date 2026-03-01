# Часть 5: Практические проекты

## Описание

Реальные проекты для закрепления навыков: от простого URL Shortener до сложной SaaS платформы.

## Статус

🚧 **В разработке** (2/4 завершено)

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

### [Проект 2: E-commerce Platform](./project2-ecommerce/) ✅
**Сложность**: Intermediate

**Цель**: Микросервисная архитектура

**Сервисы**:
1. API Gateway (chi, JWT, Circuit Breaker)
2. User Service (JWT auth, bcrypt)
3. Catalog Service (CQRS, Redis cache)
4. Order Service (Saga Pattern, Kafka)
5. Payment Service (идемпотентность)
6. Notification Service (Kafka consumer)

**Технологии**:
- gRPC (`google.golang.org/grpc`) для межсервисного взаимодействия
- Kafka (`kafka-go`) для событий
- PostgreSQL + pgx/v5 (per service)
- Redis для кэша каталога
- OpenTelemetry + Jaeger для трейсинга
- `sony/gobreaker` для Circuit Breaker

**Паттерны**:
- Saga pattern (хореография через Kafka)
- CQRS (Catalog Service: write→PG, read→Redis)
- Circuit Breaker (API Gateway → upstream)
- Идемпотентность (Payment Service)
- State Machine (статусы заказа)

**Разделы**:
1. [Доменная модель и контракты](./project2-ecommerce/01_domain.md)
2. [User Service](./project2-ecommerce/02_user_service.md)
3. [Catalog Service (CQRS)](./project2-ecommerce/03_catalog_service.md)
4. [Order Service (Saga)](./project2-ecommerce/04_order_service.md)
5. [Payment & Notification](./project2-ecommerce/05_payment_notification.md)
6. [API Gateway](./project2-ecommerce/06_api_gateway.md)
7. [Деплой и наблюдаемость](./project2-ecommerce/07_deployment.md)

**Время**: ~3-4 недели | **Статус**: ✅ Завершено

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
