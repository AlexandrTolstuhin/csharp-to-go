# Деплой: Kubernetes и HPA

---

## Введение

Trading платформа в production требует высокой доступности, авто-масштабирования и наблюдаемости. Kubernetes с Horizontal Pod Autoscaler (HPA) позволяет масштабировать сервисы по нагрузке — как по стандартным метрикам (CPU), так и по кастомным (latency, queue depth).

> **Для C# разработчиков**: Если вы деплоили ASP.NET Core в Kubernetes, большинство концепций знакомы. Главное отличие — Go-контейнеры значительно меньше (scratch или distroless вместо mcr.microsoft.com/dotnet/aspnet) и стартуют мгновенно (~50ms vs ~1-2s).

---

## Dockerfile для Go сервисов

### Multi-stage build

```dockerfile
# Dockerfile (одинаков для всех сервисов)
# Аргумент SERVICE_DIR — поддиректория сервиса (market-data, order-engine, etc.)
ARG SERVICE_DIR=market-data

# Этап 1: сборка
FROM golang:1.23-alpine AS builder

WORKDIR /app

# Кэш зависимостей (слой обновляется только при изменении go.mod/go.sum)
COPY ${SERVICE_DIR}/go.mod ${SERVICE_DIR}/go.sum ./
RUN go mod download

# Сборка
COPY ${SERVICE_DIR}/ .
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-s -w" \       # strip debug info → меньше бинарник
    -trimpath \               # убираем пути разработчика
    -o /server ./cmd/server

# Этап 2: минимальный runtime образ
FROM gcr.io/distroless/static-debian12

# Копируем только бинарник
COPY --from=builder /server /server

# Пользователь без root привилегий
USER nonroot:nonroot

EXPOSE 8080
ENTRYPOINT ["/server"]
```

### Размеры образов

```
mcr.microsoft.com/dotnet/aspnet:8.0    ~220MB
golang:1.23-alpine (full)              ~300MB
distroless/static + Go binary           ~15MB  ← наш образ

Причина: Go компилируется в статически линкованный бинарник.
Нет runtime, нет JIT, нет виртуальной машины.
```

---

## Kubernetes манифесты

### Namespace и ConfigMap

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: trading
  labels:
    app.kubernetes.io/part-of: trading-platform

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: trading-config
  namespace: trading
data:
  NATS_URL: "nats://nats-jetstream:4222"
  LOG_LEVEL: "info"
  GOGC: "200"
  GOMEMLIMIT: "900MiB"
```

### Market Data Service

```yaml
# k8s/market-data/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: market-data
  namespace: trading
  labels:
    app: market-data
spec:
  replicas: 2
  selector:
    matchLabels:
      app: market-data
  template:
    metadata:
      labels:
        app: market-data
      annotations:
        # Prometheus scraping
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/metrics"
    spec:
      containers:
        - name: market-data
          image: trading/market-data:latest
          ports:
            - containerPort: 8080
              name: http
            - containerPort: 9090
              name: metrics
          envFrom:
            - configMapRef:
                name: trading-config
          env:
            - name: HTTP_ADDR
              value: ":8080"
          resources:
            requests:
              cpu: "200m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
          # Readiness: сервис готов принимать трафик
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
            failureThreshold: 3
          # Liveness: перезапуск при зависании
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 15
            periodSeconds: 30
            failureThreshold: 3
          # Graceful shutdown: ждём завершения WebSocket соединений
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 5"]
      terminationGracePeriodSeconds: 30
      # Распределение по нодам
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: kubernetes.io/hostname
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: market-data

---
# k8s/market-data/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: market-data
  namespace: trading
spec:
  selector:
    app: market-data
  ports:
    - name: http
      port: 80
      targetPort: 8080
    - name: metrics
      port: 9090
      targetPort: 9090
  type: ClusterIP
```

### Order Matching Engine

```yaml
# k8s/order-engine/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-engine
  namespace: trading
spec:
  # Order Engine — singleton (только 1 replica!)
  # Несколько инстансов нарушат price-time priority
  replicas: 1
  selector:
    matchLabels:
      app: order-engine
  strategy:
    type: Recreate  # не RollingUpdate: избегаем dual-write
  template:
    metadata:
      labels:
        app: order-engine
    spec:
      containers:
        - name: order-engine
          image: trading/order-engine:latest
          envFrom:
            - configMapRef:
                name: trading-config
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "2000m"     # больше CPU для matching
              memory: "1Gi"
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 3
            periodSeconds: 5
          # PodDisruptionBudget защищает от случайного удаления
```

### HPA для Market Data (WebSocket нагрузка)

```yaml
# k8s/market-data/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: market-data-hpa
  namespace: trading
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: market-data
  minReplicas: 2
  maxReplicas: 10
  metrics:
    # Стандартная метрика: CPU
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60

    # Кастомная метрика: количество WebSocket соединений
    # Требует KEDA или custom metrics server
    - type: Pods
      pods:
        metric:
          name: websocket_connections_per_pod
        target:
          type: AverageValue
          averageValue: "1000"  # масштабируем при > 1000 соед/pod

  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30   # быстрый scale-up
      policies:
        - type: Pods
          value: 2
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300  # медленный scale-down (5 минут)
      policies:
        - type: Pods
          value: 1
          periodSeconds: 120
```

### KEDA для масштабирования по NATS

```yaml
# k8s/analytics/keda-scaledobject.yaml
# KEDA — Kubernetes Event-Driven Autoscaling
# Масштабирует Analytics Service по глубине очереди NATS
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: analytics-scaledobject
  namespace: trading
spec:
  scaleTargetRef:
    name: analytics-service
  minReplicaCount: 1
  maxReplicaCount: 5
  triggers:
    - type: nats-jetstream
      metadata:
        natsServerMonitoringEndpoint: "http://nats-jetstream:8222"
        account: "$G"
        stream: "MARKET"
        consumer: "analytics-consumer"
        lagThreshold: "1000"  # scale-up при > 1000 необработанных сообщений
```

---

## Helm Chart структура

```
charts/trading-platform/
├── Chart.yaml
├── values.yaml          # дефолтные значения
├── values-prod.yaml     # production overrides
├── templates/
│   ├── _helpers.tpl
│   ├── market-data/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── hpa.yaml
│   ├── order-engine/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── portfolio/
│   ├── risk/
│   ├── analytics/
│   ├── nats/
│   │   └── statefulset.yaml
│   └── timescaledb/
│       └── statefulset.yaml
└── README.md
```

```yaml
# values.yaml
global:
  image:
    registry: registry.example.com
    tag: "1.0.0"
  natsUrl: "nats://nats-jetstream:4222"

marketData:
  replicas: 2
  resources:
    requests:
      cpu: 200m
      memory: 256Mi

orderEngine:
  replicas: 1  # всегда 1
  resources:
    requests:
      cpu: 500m
      memory: 512Mi

analytics:
  replicas: 1
  resources:
    requests:
      cpu: 200m
      memory: 512Mi
```

---

## Observability

### Prometheus + Grafana

```yaml
# k8s/monitoring/prometheus-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s

    scrape_configs:
      - job_name: 'trading-services'
        kubernetes_sd_configs:
          - role: pod
            namespaces:
              names: ['trading']
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            target_label: __metrics_path__
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_port]
            target_label: __address__
            regex: (.+)
            replacement: $1
```

### Ключевые дашборды Grafana

```
Trading Platform Dashboard:
┌─────────────────────────────────────────────────────┐
│ Market Data                                          │
│ • WebSocket connections (gauge)                     │
│ • Ticks/sec по символам (rate)                      │
│ • Dropped ticks % (alert если > 0.1%)               │
│                                                      │
│ Order Engine                                         │
│ • Orders/sec (rate)                                  │
│ • Match latency P50/P95/P99 (histogram)             │
│ • Queue depth (NATS pending msgs)                   │
│                                                      │
│ Infrastructure                                       │
│ • Go GC cycles/sec (alert если > 100/min)           │
│ • Heap usage % (alert если > 80%)                   │
│ • NATS message rate                                 │
│ • TimescaleDB write latency                         │
└─────────────────────────────────────────────────────┘
```

### Метрики в Go коде

```go
// internal/metrics/trading_metrics.go
package metrics

import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    // Order Engine метрики
    OrdersProcessed = promauto.NewCounterVec(prometheus.CounterOpts{
        Namespace: "trading",
        Subsystem: "order_engine",
        Name:      "orders_processed_total",
        Help:      "Total orders processed",
    }, []string{"symbol", "side", "type", "status"})

    MatchLatency = promauto.NewHistogramVec(prometheus.HistogramOpts{
        Namespace: "trading",
        Subsystem: "order_engine",
        Name:      "match_duration_seconds",
        Help:      "Order matching latency",
        Buckets:   []float64{0.0001, 0.0005, 0.001, 0.005, 0.01}, // 100µs - 10ms
    }, []string{"symbol"})

    TradesExecuted = promauto.NewCounterVec(prometheus.CounterOpts{
        Namespace: "trading",
        Subsystem: "order_engine",
        Name:      "trades_total",
        Help:      "Total trades executed",
    }, []string{"symbol"})

    OrderBookDepth = promauto.NewGaugeVec(prometheus.GaugeOpts{
        Namespace: "trading",
        Subsystem: "order_engine",
        Name:      "orderbook_depth",
        Help:      "Current order book depth",
    }, []string{"symbol", "side"})

    // GC метрики (экспортируем для алертов)
    GCPauseSeconds = promauto.NewHistogram(prometheus.HistogramOpts{
        Namespace: "trading",
        Subsystem: "runtime",
        Name:      "gc_pause_seconds",
        Help:      "Go GC stop-the-world pause duration",
        Buckets:   []float64{0.0001, 0.0005, 0.001, 0.005, 0.01},
    })
)

// Использование в Order Engine:
func (e *Engine) ProcessOrder(ctx context.Context, data []byte) error {
    start := time.Now()
    // ... логика матчинга
    trades := ob.Add(order)

    MatchLatency.WithLabelValues(string(order.Symbol)).
        Observe(time.Since(start).Seconds())

    OrdersProcessed.WithLabelValues(
        string(order.Symbol),
        order.Side.String(),
        order.Type.String(),
        order.Status.String(),
    ).Inc()

    TradesExecuted.WithLabelValues(string(order.Symbol)).
        Add(float64(len(trades)))

    return nil
}
```

---

## CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy Trading Platform

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      nats:
        image: nats:2.10-alpine
        ports: ["4222:4222"]
        options: --health-cmd "nats-server --version" --health-interval 10s
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.23'
      - name: Test all services
        run: |
          for svc in market-data order-engine portfolio risk analytics; do
            cd $svc && go test ./... -race -timeout 120s && cd ..
          done

  build-push:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build and push images
        run: |
          for svc in market-data order-engine portfolio risk analytics; do
            docker build \
              --build-arg SERVICE_DIR=$svc \
              -t ${{ env.REGISTRY }}/trading/$svc:${{ github.sha }} \
              -f Dockerfile .
            docker push ${{ env.REGISTRY }}/trading/$svc:${{ github.sha }}
          done

  deploy:
    needs: build-push
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Kubernetes
        run: |
          helm upgrade --install trading-platform charts/trading-platform \
            --namespace trading \
            --create-namespace \
            --values charts/trading-platform/values-prod.yaml \
            --set global.image.tag=${{ github.sha }} \
            --wait \
            --timeout 10m
```

---

## Production чеклист

```
Инфраструктура:
□ NATS JetStream в кластере (минимум 3 ноды для raft quorum)
□ TimescaleDB с репликой чтения
□ Redis Sentinel или Redis Cluster
□ Kubernetes RBAC для сервисных аккаунтов

Безопасность:
□ TLS для NATS (client certificates)
□ PostgreSQL SSL
□ Network Policies (ограничение pod-to-pod трафика)
□ Secrets в Kubernetes Secrets / Vault (не в ConfigMap!)
□ Non-root контейнеры (distroless/nonroot)

Надёжность:
□ PodDisruptionBudget для каждого сервиса
□ Readiness/Liveness probe настроены
□ Graceful shutdown (terminationGracePeriodSeconds ≥ таймаут завершения)
□ HPA настроен + протестирован
□ Retry + idempotency для NATS consumers

Мониторинг:
□ Prometheus scraping настроен
□ Grafana dashboards импортированы
□ Алерты: latency P99, error rate, GC pause, queue depth
□ Distributed tracing (OpenTelemetry → Jaeger/Tempo)

Go-специфично:
□ GOGC=200 + GOMEMLIMIT=<90% контейнерного лимита>
□ GOMAXPROCS равен числу CPU (или используем automaxprocs)
□ pprof endpoint доступен внутри кластера (не снаружи!)
□ go test -race проходит в CI
```

---

## Сравнение с .NET в Kubernetes

| Аспект | .NET 8 | Go |
|--------|--------|-----|
| Образ контейнера | ~200MB (mcr/aspnet) | ~15MB (distroless) |
| Время старта | 1-2 секунды | 50-100ms |
| Время до первого запроса | Дольше (JIT warmup) | Сразу |
| Memory footprint | ~150-300MB | ~50-100MB |
| GC tuning | ServerGC, LOH threshold, Gen2 | GOGC, GOMEMLIMIT |
| Health checks | built-in IHealthCheck | httpGet в probe |
| Rolling update | Отличная поддержка | Отличная поддержка |
| Graceful shutdown | `IHostApplicationLifetime` | signal.NotifyContext |

> **Главные преимущества Go для Kubernetes**: маленькие образы (быстрый pull при scale-out), мгновенный старт (быстрый rolling update), меньше памяти (больше подов на той же ноде).

---

## Итог проекта

Вы построили полноценную trading платформу на Go:

1. **Market Data Service** — WebSocket fan-out к тысячам клиентов через Hub + goroutines
2. **Order Matching Engine** — price-time priority matching с lock-free стаканом
3. **Portfolio Service** — real-time PnL tracking через события NATS
4. **Risk Service** — VaR расчёт + лимиты + алерты
5. **Analytics Service** — TimescaleDB гипертаблицы + continuous aggregates + HTTP API
6. **Performance tuning** — GC tuning, sync.Pool, профилирование
7. **Production deployment** — Kubernetes + HPA + Prometheus + CI/CD

### Ключевые паттерны, которые вы освоили

- **Event-driven через NATS JetStream** — at-least-once delivery, durable consumers
- **Fan-out через Hub goroutine** — нет race conditions, нет lock contention
- **Точная финансовая арифметика** — shopspring/decimal вместо float64
- **GC оптимизация** — GOGC, GOMEMLIMIT, sync.Pool
- **TimescaleDB** — гипертаблицы, continuous aggregates, time_bucket()
- **Минимальные контейнеры** — distroless + static Go binary

### Дополнительные задания

1. **Добавить FIX Protocol** — интеграция с реальной биржей через QuickFIX/Go
2. **Реализовать Circuit Breaker** — защита при деградации NATS/PostgreSQL
3. **Add WebSocket subscriptions** — клиент подписывается только на нужные символы
4. **Implement IOC/FOK orders** — дополнительные типы ордеров в Order Book
5. **Add backtesting** — исторические OHLCV данные для тестирования стратегий
6. **Distributed tracing** — OpenTelemetry spans через все сервисы
