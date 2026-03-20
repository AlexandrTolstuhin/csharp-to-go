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
