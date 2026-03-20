# Деплой: Kubernetes и observability

---

## Введение

> **Для C# разработчиков**: В .NET экосистеме observability строится через Application Insights, Serilog + Seq, или OpenTelemetry .NET SDK. В Go стандарт де-факто — OpenTelemetry Go SDK + Prometheus. Kubernetes-деплой идентичен: Deployment, Service, ConfigMap, Secret — теже объекты. Разница в деталях: Go-бинари компилируются в единый статический файл (~15MB), поэтому Docker-образы на `scratch` или `distroless` — без runtime-зависимостей.

Этот раздел охватывает:
- Dockerfile для Go-сервисов (multi-stage build)
- Kubernetes манифесты для всех компонентов SaaS
- Prometheus метрики: custom metrics для SaaS
- OpenTelemetry distributed tracing
- HPA (Horizontal Pod Autoscaler) по RPS

---

## Dockerfile: Multi-stage Build

```dockerfile
# Stage 1: сборка
FROM golang:1.26-alpine AS builder

WORKDIR /app

# Сначала копируем go.mod/go.sum — слой кэшируется при неизменённых зависимостях
COPY go.mod go.sum ./
RUN go mod download

COPY . .

# CGO_ENABLED=0 — статическая линковка, нет зависимостей от libc
# -ldflags "-s -w" — убираем debug-символы и DWARF (-s), отладочную информацию (-w)
# Итого: ~7-12MB бинарь вместо ~20MB с символами
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-s -w" \
    -o /app/server \
    ./cmd/server

# Stage 2: минимальный runtime-образ
# scratch — пустой образ, только бинарь. Нет shell, нет package manager.
# distroless/static — альтернатива: есть CA-сертификаты и timezone data.
FROM gcr.io/distroless/static-debian12

COPY --from=builder /app/server /server

# Непривилегированный пользователь
USER nonroot:nonroot

EXPOSE 8080

ENTRYPOINT ["/server"]
```

---

## Kubernetes манифесты

### Namespace и общие ресурсы

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: saas-platform
  labels:
    app.kubernetes.io/part-of: saas-platform
```

### API Gateway Deployment

```yaml
# gateway/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: saas-platform
  labels:
    app: api-gateway
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
      annotations:
        # Prometheus автоматически обнаружит и начнёт scrape метрики
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/metrics"
    spec:
      containers:
        - name: api-gateway
          image: your-registry/api-gateway:latest
          ports:
            - containerPort: 8080
              name: http
            - containerPort: 9090
              name: metrics
          env:
            - name: JWT_SECRET
              valueFrom:
                secretKeyRef:
                  name: saas-secrets
                  key: jwt-secret
            - name: REDIS_ADDR
              value: "redis:6379"
            - name: AUTH_SERVICE_URL
              value: "http://auth-service:8081"
            - name: APP_SERVICE_URL
              value: "http://app-service:8084"
          resources:
            requests:
              cpu: "100m"
              memory: "64Mi"
            limits:
              cpu: "500m"
              memory: "256Mi"
          # Probes — Kubernetes проверяет здоровье пода
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /readyz
              port: 8080
            initialDelaySeconds: 3
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
  namespace: saas-platform
spec:
  selector:
    app: api-gateway
  ports:
    - port: 80
      targetPort: 8080
      name: http
  type: ClusterIP
```

### Webhook Worker Deployment

```yaml
# worker/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webhook-worker
  namespace: saas-platform
spec:
  # Webhook workers можно масштабировать горизонтально:
  # FOR UPDATE SKIP LOCKED гарантирует, что два воркера не возьмут одно событие
  replicas: 3
  selector:
    matchLabels:
      app: webhook-worker
  template:
    metadata:
      labels:
        app: webhook-worker
    spec:
      containers:
        - name: webhook-worker
          image: your-registry/webhook-worker:latest
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: saas-secrets
                  key: database-url
            - name: WORKER_CONCURRENCY
              value: "10"
          resources:
            requests:
              cpu: "50m"
              memory: "32Mi"
            limits:
              cpu: "200m"
              memory: "128Mi"
          # Webhook workers не принимают HTTP — нет readiness probe
          # Только liveness через healthcheck команду
          livenessProbe:
            exec:
              command: ["/worker", "--healthcheck"]
            periodSeconds: 30
```

### HPA по RPS (кастомные метрики)

```yaml
# gateway/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
  namespace: saas-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 20
  metrics:
    # Стандартная метрика: CPU
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    # Кастомная метрика: RPS через Prometheus Adapter
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "500"  # 500 RPS на под
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30   # быстро масштабируемся вверх
    scaleDown:
      stabilizationWindowSeconds: 300  # медленно масштабируемся вниз
```

---

## Prometheus Метрики

### Регистрация SaaS-специфичных метрик

```go
package metrics

import (
    "net/http"
    "time"

    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
    // HTTP метрики
    HTTPRequestsTotal = promauto.NewCounterVec(prometheus.CounterOpts{
        Namespace: "saas",
        Subsystem: "gateway",
        Name:      "http_requests_total",
        Help:      "Общее количество HTTP запросов",
    }, []string{"method", "path", "status", "tenant_plan"})

    HTTPRequestDuration = promauto.NewHistogramVec(prometheus.HistogramOpts{
        Namespace: "saas",
        Subsystem: "gateway",
        Name:      "http_request_duration_seconds",
        Help:      "Время обработки HTTP запроса",
        Buckets:   []float64{.005, .01, .025, .05, .1, .25, .5, 1, 2.5},
    }, []string{"method", "path"})

    // SaaS бизнес-метрики
    ActiveTenantsTotal = promauto.NewGauge(prometheus.GaugeOpts{
        Namespace: "saas",
        Name:      "active_tenants_total",
        Help:      "Количество активных тенантов",
    })

    WebhookDeliveryTotal = promauto.NewCounterVec(prometheus.CounterOpts{
        Namespace: "saas",
        Subsystem: "webhook",
        Name:      "delivery_total",
        Help:      "Доставки webhook по результату",
    }, []string{"result"}) // "success", "failed", "dlq"

    WebhookDeliveryDuration = promauto.NewHistogram(prometheus.HistogramOpts{
        Namespace: "saas",
        Subsystem: "webhook",
        Name:      "delivery_duration_seconds",
        Help:      "Время доставки webhook",
        Buckets:   []float64{.1, .25, .5, 1, 2.5, 5, 10},
    })

    OutboxPendingEvents = promauto.NewGauge(prometheus.GaugeOpts{
        Namespace: "saas",
        Subsystem: "outbox",
        Name:      "pending_events",
        Help:      "Количество необработанных событий в Outbox",
    })

    RateLimitedRequests = promauto.NewCounterVec(prometheus.CounterOpts{
        Namespace: "saas",
        Subsystem: "gateway",
        Name:      "rate_limited_requests_total",
        Help:      "Запросы, отклонённые rate limiter",
    }, []string{"tenant_plan"})
)

// MetricsHandler возвращает Prometheus /metrics endpoint.
func MetricsHandler() http.Handler {
    return promhttp.Handler()
}
```

### Использование метрик в middleware

```go
// Middleware для записи HTTP-метрик
func InstrumentedHandler(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        ww := middleware.NewWrapResponseWriter(w, r.ProtoMajor)

        next.ServeHTTP(ww, r)

        duration := time.Since(start).Seconds()
        status := strconv.Itoa(ww.Status())

        // Нормализуем путь: "/api/projects/123" → "/api/projects/{id}"
        // Иначе метрика взорвётся по кардинальности
        path := chi.RouteContext(r.Context()).RoutePattern()

        plan := "unknown"
        if tenant, ok := tenantctx.TryTenantFromContext(r.Context()); ok {
            plan = tenant.PlanName // добавляем в context в SuspensionCheck
        }

        metrics.HTTPRequestsTotal.WithLabelValues(r.Method, path, status, plan).Inc()
        metrics.HTTPRequestDuration.WithLabelValues(r.Method, path).Observe(duration)
    })
}
```

---

## OpenTelemetry Distributed Tracing

```go
package tracing

import (
    "context"
    "fmt"
    "os"

    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    "go.opentelemetry.io/otel/propagation"
    "go.opentelemetry.io/otel/sdk/resource"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.21.0"
    "go.opentelemetry.io/otel/trace"
)

// Init инициализирует OpenTelemetry с OTLP экспортером (Jaeger/Tempo).
func Init(ctx context.Context, serviceName string) (func(context.Context) error, error) {
    exporter, err := otlptracegrpc.New(ctx,
        otlptracegrpc.WithEndpoint(os.Getenv("OTEL_EXPORTER_OTLP_ENDPOINT")),
        otlptracegrpc.WithInsecure(),
    )
    if err != nil {
        return nil, fmt.Errorf("create otlp exporter: %w", err)
    }

    res := resource.NewWithAttributes(
        semconv.SchemaURL,
        semconv.ServiceNameKey.String(serviceName),
        semconv.ServiceVersionKey.String(os.Getenv("APP_VERSION")),
        semconv.DeploymentEnvironmentKey.String(os.Getenv("ENV")), // "production", "staging"
    )

    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exporter),
        sdktrace.WithResource(res),
        // Sampling: в production - 10% трейсов, в staging - 100%
        sdktrace.WithSampler(sdktrace.ParentBased(
            sdktrace.TraceIDRatioBased(samplingRate()),
        )),
    )

    otel.SetTracerProvider(tp)
    // W3C Trace Context: стандартный заголовок "traceparent"
    otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
        propagation.TraceContext{},
        propagation.Baggage{},
    ))

    return tp.Shutdown, nil
}

func samplingRate() float64 {
    if os.Getenv("ENV") == "production" {
        return 0.1
    }
    return 1.0
}
```

### Инструментирование запросов

```go
// OpenTelemetry middleware для chi
func OpenTelemetry(next http.Handler) http.Handler {
    tracer := otel.Tracer("api-gateway")

    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Извлекаем трейс-контекст из входящего запроса (для distributed tracing)
        ctx := otel.GetTextMapPropagator().Extract(r.Context(),
            propagation.HeaderCarrier(r.Header),
        )

        spanName := r.Method + " " + r.URL.Path
        ctx, span := tracer.Start(ctx, spanName,
            trace.WithSpanKind(trace.SpanKindServer),
        )
        defer span.End()

        // Добавляем tenant_id в span — удобно при поиске трейсов
        if tenant, ok := tenantctx.TryTenantFromContext(ctx); ok {
            span.SetAttributes(
                attribute.String("tenant.id", tenant.ID.String()),
                attribute.String("tenant.slug", tenant.Slug),
            )
        }

        ww := middleware.NewWrapResponseWriter(w, r.ProtoMajor)
        next.ServeHTTP(ww, r.WithContext(ctx))

        span.SetAttributes(attribute.Int("http.status_code", ww.Status()))
    })
}
```

---

## Health Checks

```go
package health

import (
    "context"
    "encoding/json"
    "net/http"
    "time"

    "github.com/jackc/pgx/v5/pgxpool"
    "github.com/redis/go-redis/v9"
)

type Checker struct {
    pool *pgxpool.Pool
    rdb  *redis.Client
}

type healthResponse struct {
    Status     string            `json:"status"`
    Components map[string]string `json:"components"`
}

// Liveness — pod жив (не зациклен, не в deadlock).
// Kubernetes перезапустит под при failure.
func (c *Checker) Liveness(w http.ResponseWriter, r *http.Request) {
    w.WriteHeader(http.StatusOK)
    w.Write([]byte("ok"))
}

// Readiness — pod готов принимать трафик.
// Kubernetes уберёт под из балансировки при failure.
func (c *Checker) Readiness(w http.ResponseWriter, r *http.Request) {
    ctx, cancel := context.WithTimeout(r.Context(), 3*time.Second)
    defer cancel()

    resp := healthResponse{
        Status:     "ok",
        Components: make(map[string]string),
    }
    allOk := true

    // Проверяем PostgreSQL
    if err := c.pool.Ping(ctx); err != nil {
        resp.Components["postgres"] = "unavailable"
        allOk = false
    } else {
        resp.Components["postgres"] = "ok"
    }

    // Проверяем Redis
    if err := c.rdb.Ping(ctx).Err(); err != nil {
        resp.Components["redis"] = "unavailable"
        allOk = false
    } else {
        resp.Components["redis"] = "ok"
    }

    if !allOk {
        resp.Status = "degraded"
        w.WriteHeader(http.StatusServiceUnavailable)
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(resp)
}
```

---

## Grafana Dashboard

Ключевые панели для мониторинга SaaS-платформы:

```
Строки (rows):
├── Business Metrics
│   ├── Active Tenants (gauge)
│   ├── New Tenants Today (counter)
│   └── Tenants by Plan (pie chart)
│
├── API Performance
│   ├── RPS по сервисам (time series)
│   ├── P50/P95/P99 latency (time series)
│   ├── Error Rate 5xx (time series)
│   └── Rate Limited Requests (counter)
│
├── Billing
│   ├── MRR (Monthly Recurring Revenue) из Stripe
│   └── Payment Failures (counter)
│
└── Webhooks
    ├── Pending Outbox Events (gauge)
    ├── Delivery Success Rate (%)
    ├── Delivery Latency P95
    └── DLQ Events (counter — алерт при > 0)
```

---

## Alerting Rules (Prometheus)

```yaml
# alerts.yaml
groups:
  - name: saas-platform
    rules:
      # Высокий error rate — срочно
      - alert: HighErrorRate
        expr: |
          rate(saas_gateway_http_requests_total{status=~"5.."}[5m])
          / rate(saas_gateway_http_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Error rate > 5% в течение 2 минут"

      # Накопились события в Outbox — проблема с webhook worker
      - alert: OutboxBacklog
        expr: saas_outbox_pending_events > 1000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Outbox: > 1000 необработанных событий"

      # Webhook доставки уходят в DLQ
      - alert: WebhookDLQ
        expr: increase(saas_webhook_delivery_total{result="dlq"}[1h]) > 0
        labels:
          severity: warning
        annotations:
          summary: "Webhook события попадают в Dead Letter Queue"

      # PostgreSQL connection pool насыщен
      - alert: PGPoolSaturated
        expr: go_sql_open_connections / go_sql_max_open_connections > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL connection pool заполнен на 90%+"
```

---

## Сравнение с C#

| Аспект | C# / .NET | Go |
|--------|-----------|-----|
| Docker образ | `mcr.microsoft.com/dotnet/aspnet:8.0` (~200MB) | `distroless/static` (~5MB + бинарь ~12MB) |
| Startup time | 1-3 секунды (JIT) | 50-100ms (AOT аналог через нативные бинари) |
| Health checks | `AddHealthChecks()` в ASP.NET | Ручной endpoint `/healthz`, `/readyz` |
| Metrics | `AddOpenTelemetryMetrics()` / App Insights | `prometheus/client_golang` |
| Tracing | OpenTelemetry .NET SDK | OpenTelemetry Go SDK |
| HPA | По CPU (стандарт) + KEDA для Azure | По CPU + Prometheus Adapter |
| Graceful shutdown | `IHostApplicationLifetime.StopApplication()` | `signal.NotifyContext` |

---

## Итоги проекта

Вы построили полноценную SaaS-платформу на Go:

| Компонент | Ключевые концепции |
|-----------|--------------------|
| **Архитектура** | Schema-per-tenant, context propagation, явная передача зависимостей |
| **Auth** | JWT с tenant-claims, refresh token rotation, OAuth2 PKCE |
| **Tenant** | Транзакционный онбординг, Saga без оркестратора, feature flags |
| **Billing** | Stripe Checkout, webhook с HMAC верификацией, идемпотентность |
| **Gateway** | Redis sliding window rate limiting, middleware chain, structured logging |
| **Workers** | Outbox Pattern, Redis Streams consumer groups, exponential backoff |
| **Deploy** | Multi-stage Docker, Kubernetes HPA, Prometheus, OpenTelemetry |

### Что дальше

- Добавить **SSO/SAML** через feature flag `FlagSSO` — интеграция с корпоративными IdP
- Реализовать **custom domains** — subdomain routing (`acme.yourplatform.com`)
- **Audit log UI** — страница с полной историей действий пользователей тенанта
- **Admin panel** — управление тенантами, планами и billing без прямого SQL
