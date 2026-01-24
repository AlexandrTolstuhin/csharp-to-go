# Часть 5: Практические проекты

## Описание

Реальные проекты для закрепления навыков: от простого URL Shortener до сложной SaaS платформы.

## Статус

🚧 **В разработке**

## Проекты

### Проект 1: URL Shortener
**Сложность**: Beginner → Intermediate

**Цель**: Освоение базовых концепций

**Технологии**:
- net/http или chi
- PostgreSQL + pgx
- Redis для кэша
- Docker Compose

**Функциональность**:
- Создание короткой ссылки
- Редирект по ключу
- Статистика переходов
- Rate limiting
- Health checks

**Время**: ~1 неделя

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

**Технологии**:
- Schema-per-tenant PostgreSQL
- Row-level security
- Feature flags
- Rate limiting per tenant

**Время**: ~4 недели

---

## Рекомендации

- Начните с Проекта 1 даже если вы Senior
- Каждый проект должен быть production-ready
- Используйте Docker Compose для локальной разработки
- Пишите тесты (unit + integration)
- Настройте CI/CD
- Добавьте observability с первого дня

---

[← Назад к оглавлению](../README.md) | [Предыдущая часть](../part4-infrastructure/) | [Следующая часть →](../part6-best-practices/)
