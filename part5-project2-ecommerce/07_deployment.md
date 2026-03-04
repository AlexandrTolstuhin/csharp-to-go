# Деплой и наблюдаемость

---

## Docker Compose

### docker-compose.dev.yml — только инфраструктура (для разработки)

```yaml
# docker-compose.dev.yml
# Запустить: docker compose -f docker-compose.dev.yml up -d
name: ecommerce-dev

services:
  # PostgreSQL для каждого сервиса (отдельные БД, общий инстанс для dev)
  postgres:
    image: postgres:17-alpine
    environment:
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-databases.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s

  # Kafka + Zookeeper
  zookeeper:
    image: confluentinc/cp-zookeeper:7.7.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    healthcheck:
      test: ["CMD", "nc", "-z", "localhost", "2181"]

  kafka:
    image: confluentinc/cp-kafka:7.7.0
    depends_on:
      zookeeper:
        condition: service_healthy
    ports:
      - "9092:9092"
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092,PLAINTEXT_INTERNAL://kafka:29092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_INTERNAL:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT_INTERNAL
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
    healthcheck:
      test: ["CMD", "kafka-broker-api-versions", "--bootstrap-server", "localhost:9092"]
      interval: 10s

  # Jaeger для трейсинга
  jaeger:
    image: jaegertracing/all-in-one:1.62
    ports:
      - "16686:16686" # UI
      - "4317:4317"   # OTLP gRPC
      - "4318:4318"   # OTLP HTTP
    environment:
      COLLECTOR_OTLP_ENABLED: "true"

  # Kafka UI (удобно для отладки)
  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    ports:
      - "8090:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:29092
    depends_on:
      - kafka

volumes:
  postgres_data:
```

```sql
-- scripts/init-databases.sql
-- Создаём отдельные БД для каждого сервиса
CREATE DATABASE users_db;
CREATE DATABASE catalog_db;
CREATE DATABASE orders_db;
CREATE DATABASE payments_db;
```

### docker-compose.yml — все сервисы

```yaml
# docker-compose.yml
name: ecommerce

services:
  # === Инфраструктура ===
  postgres:
    image: postgres:17-alpine
    environment:
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-databases.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s

  kafka:
    image: confluentinc/cp-kafka:7.7.0
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
    depends_on:
      - zookeeper

  zookeeper:
    image: confluentinc/cp-zookeeper:7.7.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  otel-collector:
    image: otel/opentelemetry-collector-contrib:0.115.0
    volumes:
      - ./otel-collector-config.yaml:/etc/otelcol-contrib/config.yaml
    ports:
      - "4317:4317"

  jaeger:
    image: jaegertracing/all-in-one:1.62
    ports:
      - "16686:16686"

  # === Микросервисы ===
  user-service:
    build:
      context: ./services/user-service
      dockerfile: Dockerfile
    environment:
      SERVICE_NAME: user-service
      DATABASE_URL: postgres://postgres:postgres@postgres:5432/users_db?sslmode=disable
      JWT_SECRET: ${JWT_SECRET}
      GRPC_PORT: "9001"
      OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "grpc_health_probe", "-addr=:9001"]
      interval: 10s

  catalog-service:
    build:
      context: ./services/catalog-service
      dockerfile: Dockerfile
    environment:
      SERVICE_NAME: catalog-service
      DATABASE_URL: postgres://postgres:postgres@postgres:5432/catalog_db?sslmode=disable
      REDIS_URL: redis://redis:6379
      KAFKA_BROKERS: kafka:9092
      GRPC_PORT: "9002"
      OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  order-service:
    build:
      context: ./services/order-service
      dockerfile: Dockerfile
    environment:
      SERVICE_NAME: order-service
      DATABASE_URL: postgres://postgres:postgres@postgres:5432/orders_db?sslmode=disable
      KAFKA_BROKERS: kafka:9092
      KAFKA_CONSUMER_GROUP: order-service
      CATALOG_SERVICE_ADDR: catalog-service:9002
      GRPC_PORT: "9003"
      OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317
    depends_on:
      postgres:
        condition: service_healthy

  payment-service:
    build:
      context: ./services/payment-service
      dockerfile: Dockerfile
    environment:
      SERVICE_NAME: payment-service
      DATABASE_URL: postgres://postgres:postgres@postgres:5432/payments_db?sslmode=disable
      KAFKA_BROKERS: kafka:9092
      KAFKA_CONSUMER_GROUP: payment-service
      GRPC_PORT: "9004"
      OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317
    depends_on:
      postgres:
        condition: service_healthy

  notification-service:
    build:
      context: ./services/notification-service
      dockerfile: Dockerfile
    environment:
      SERVICE_NAME: notification-service
      KAFKA_BROKERS: kafka:9092
      KAFKA_CONSUMER_GROUP: notification-service
      OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317
      # SMTP_HOST: smtp.example.com # настроить для реальной отправки

  api-gateway:
    build:
      context: ./services/api-gateway
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      SERVICE_NAME: api-gateway
      HTTP_PORT: "8080"
      USER_SERVICE_ADDR: user-service:9001
      CATALOG_SERVICE_ADDR: catalog-service:9002
      ORDER_SERVICE_ADDR: order-service:9003
      PAYMENT_SERVICE_ADDR: payment-service:9004
      RATE_LIMIT_RPS: "100"
      OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317
    depends_on:
      - user-service
      - catalog-service
      - order-service
      - payment-service

volumes:
  postgres_data:
```

---

## Dockerfiles

### Типичный Dockerfile (одинаков для всех сервисов)

```dockerfile
# services/user-service/Dockerfile
# Этап 1: сборка
FROM golang:1.26-alpine AS builder

WORKDIR /app

# Копируем go.mod/go.sum отдельно для кэширования зависимостей
COPY go.mod go.sum ./
RUN go mod download

COPY . .

# Собираем бинарник с отключённой отладочной информацией
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build \
    -ldflags="-s -w" \
    -o /bin/server \
    ./cmd/server

# Этап 2: минимальный runtime образ
FROM gcr.io/distroless/static-debian12:nonroot

COPY --from=builder /bin/server /server

# distroless nonroot: UID=65532 по умолчанию — безопасно
USER nonroot:nonroot

EXPOSE 9001

ENTRYPOINT ["/server"]
```

> 💡 **Distroless vs scratch**: distroless включает CA certificates и timezone data —
> нужно для HTTPS запросов и правильных timestamp. scratch — абсолютный минимум,
> нужно добавлять CA вручную.

---

## Makefile

```makefile
# Makefile

.PHONY: help proto migrate-all dev test lint build docker-up docker-down

help: ## Показать список команд
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Proto
proto: ## Сгенерировать gRPC код из proto файлов
	cd proto && buf generate
	@echo "Proto generated successfully"

proto-lint: ## Проверить proto файлы на соответствие стандартам
	cd proto && buf lint

proto-breaking: ## Проверить на breaking changes
	cd proto && buf breaking --against '.git#branch=main'

# Миграции
migrate-all: ## Применить миграции всех сервисов
	@for svc in user-service catalog-service order-service payment-service; do \
		echo "Migrating $$svc..."; \
		for f in services/$$svc/migrations/*.sql; do \
			psql "$$($$(echo $${svc^^} | tr '-' '_')_DATABASE_URL)" < $$f; \
		done; \
	done

# Разработка
dev: ## Запустить все сервисы (требует docker-compose.dev.yml запущен)
	@echo "Starting all services..."
	@for svc in user-service catalog-service order-service payment-service notification-service api-gateway; do \
		(cd services/$$svc && go run ./cmd/...) & \
	done
	@wait

# Тесты
test: ## Запустить unit тесты всех сервисов
	@for svc in user-service catalog-service order-service payment-service api-gateway; do \
		echo "Testing $$svc..."; \
		(cd services/$$svc && go test ./...); \
	done

test-integration: ## Запустить интеграционные тесты (требует Docker)
	@for svc in user-service catalog-service order-service payment-service; do \
		echo "Integration testing $$svc..."; \
		(cd services/$$svc && go test -tags=integration ./...); \
	done

test-coverage: ## Тесты с покрытием
	@mkdir -p coverage
	@for svc in user-service catalog-service order-service payment-service api-gateway; do \
		(cd services/$$svc && go test -coverprofile=../../coverage/$$svc.out ./...); \
	done
	@go tool cover -html=coverage/user-service.out -o coverage/user-service.html

# Качество кода
lint: ## Запустить golangci-lint для всех сервисов
	@for svc in user-service catalog-service order-service payment-service notification-service api-gateway; do \
		echo "Linting $$svc..."; \
		(cd services/$$svc && golangci-lint run ./...); \
	done

vuln: ## Проверка уязвимостей
	@for svc in services/*/; do \
		(cd $$svc && govulncheck ./...); \
	done

# Docker
docker-up: ## Запустить всё через Docker Compose
	docker compose up -d --build

docker-down: ## Остановить все контейнеры
	docker compose down

docker-logs: ## Посмотреть логи (make docker-logs SVC=api-gateway)
	docker compose logs -f $(SVC)

# Сборка
build: ## Собрать все бинарники
	@mkdir -p bin
	@for svc in user-service catalog-service order-service payment-service notification-service api-gateway; do \
		echo "Building $$svc..."; \
		(cd services/$$svc && \
			CGO_ENABLED=0 go build -ldflags="-s -w" -o ../../bin/$$svc ./cmd/...); \
	done

# Инструменты
install-tools: ## Установить все dev инструменты
	go install github.com/bufbuild/buf/cmd/buf@latest
	go install github.com/sqlc-dev/sqlc/cmd/sqlc@latest
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
	go install golang.org/x/vuln/cmd/govulncheck@latest
	go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest
	go install github.com/grpc-ecosystem/grpc-health-probe@latest
```

---

## OpenTelemetry

### otel-collector-config.yaml

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024
  memory_limiter:
    limit_mib: 512
    check_interval: 5s

exporters:
  jaeger:
    endpoint: jaeger:14250
    tls:
      insecure: true
  logging:
    verbosity: normal

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [jaeger, logging]
```

### Инициализация трейсера (общая для всех сервисов)

```go
// shared/telemetry/tracer.go
package telemetry

import (
    "context"
    "fmt"

    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    "go.opentelemetry.io/otel/sdk/resource"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.26.0"
)

// InitTracer инициализирует OpenTelemetry TracerProvider.
// Возвращает shutdown функцию, которую нужно вызвать перед завершением.
func InitTracer(otlpEndpoint, serviceName string) (func(context.Context) error, error) {
    exporter, err := otlptracegrpc.New(context.Background(),
        otlptracegrpc.WithEndpoint(otlpEndpoint),
        otlptracegrpc.WithInsecure(),
    )
    if err != nil {
        return nil, fmt.Errorf("create exporter: %w", err)
    }

    res, err := resource.New(context.Background(),
        resource.WithAttributes(
            semconv.ServiceNameKey.String(serviceName),
        ),
    )
    if err != nil {
        return nil, fmt.Errorf("create resource: %w", err)
    }

    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exporter),
        sdktrace.WithResource(res),
        sdktrace.WithSampler(sdktrace.AlwaysSample()), // в prod: ParentBased(TraceIDRatioBased(0.1))
    )

    otel.SetTracerProvider(tp)

    return tp.Shutdown, nil
}
```

---

## Health Checks

```go
// internal/handler/health.go (в api-gateway)
package handler

import (
    "context"
    "encoding/json"
    "net/http"
    "sync"
    "time"

    "google.golang.org/grpc"
    "google.golang.org/grpc/health/grpc_health_v1"
)

type HealthHandler struct {
    // Адреса upstream сервисов для проверки
    upstreams map[string]string
}

func NewHealthHandler(upstreams map[string]string) *HealthHandler {
    return &HealthHandler{upstreams: upstreams}
}

type healthResponse struct {
    Status   string            `json:"status"`
    Services map[string]string `json:"services,omitempty"`
}

// Health — liveness probe. Возвращает 200 если сам Gateway жив.
func (h *HealthHandler) Health(w http.ResponseWriter, r *http.Request) {
    writeJSON(w, http.StatusOK, healthResponse{Status: "ok"})
}

// Ready — readiness probe. Проверяет доступность всех upstream сервисов.
func (h *HealthHandler) Ready(w http.ResponseWriter, r *http.Request) {
    ctx, cancel := context.WithTimeout(r.Context(), 3*time.Second)
    defer cancel()

    statuses := make(map[string]string, len(h.upstreams))
    var mu sync.Mutex
    var wg sync.WaitGroup

    for name, addr := range h.upstreams {
        wg.Add(1)
        go func(name, addr string) {
            defer wg.Done()

            conn, err := grpc.NewClient(addr, grpc.WithInsecure())
            if err != nil {
                mu.Lock()
                statuses[name] = "unreachable"
                mu.Unlock()
                return
            }
            defer conn.Close()

            client := grpc_health_v1.NewHealthClient(conn)
            resp, err := client.Check(ctx, &grpc_health_v1.HealthCheckRequest{})

            mu.Lock()
            if err != nil || resp.Status != grpc_health_v1.HealthCheckResponse_SERVING {
                statuses[name] = "unhealthy"
            } else {
                statuses[name] = "healthy"
            }
            mu.Unlock()
        }(name, addr)
    }

    wg.Wait()

    // Если хоть один сервис нездоров — возвращаем 503
    allHealthy := true
    for _, s := range statuses {
        if s != "healthy" {
            allHealthy = false
            break
        }
    }

    if allHealthy {
        writeJSON(w, http.StatusOK, healthResponse{Status: "ready", Services: statuses})
    } else {
        writeJSON(w, http.StatusServiceUnavailable, healthResponse{Status: "not ready", Services: statuses})
    }
}
```

---

## Kubernetes

### Deployment для User Service

```yaml
# k8s/user-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  labels:
    app: user-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
        - name: user-service
          image: ghcr.io/yourname/ecommerce/user-service:latest
          ports:
            - containerPort: 9001
              name: grpc
          env:
            - name: SERVICE_NAME
              value: user-service
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: user-service-secrets
                  key: database-url
            - name: JWT_SECRET
              valueFrom:
                secretKeyRef:
                  name: user-service-secrets
                  key: jwt-secret
            - name: GRPC_PORT
              value: "9001"
            - name: OTEL_EXPORTER_OTLP_ENDPOINT
              value: http://otel-collector:4317
          livenessProbe:
            grpc:
              port: 9001
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            grpc:
              port: 9001
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            requests:
              cpu: 100m
              memory: 64Mi
            limits:
              cpu: 500m
              memory: 128Mi
          # Go 1.25+: container-aware GOMAXPROCS встроен в runtime
          # Явная установка не нужна

---
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  selector:
    app: user-service
  ports:
    - port: 9001
      targetPort: 9001
      name: grpc
  type: ClusterIP
```

### HPA для API Gateway

```yaml
# k8s/api-gateway-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

---

## Итоги проекта

### Чеклист production-readiness

```
Функциональность:
- [x] Регистрация и аутентификация (JWT)
- [x] Каталог товаров с кэшированием (Redis)
- [x] Создание заказов с резервированием склада
- [x] Асинхронная оплата через Kafka (Saga)
- [x] Email уведомления

Качество:
- [x] Unit тесты для всех сервисов
- [x] Интеграционные тесты (testcontainers)
- [x] gRPC Health Checks
- [x] Graceful Shutdown
- [x] Структурированное логирование (slog)

Надёжность:
- [x] Circuit Breaker (gobreaker)
- [x] Rate Limiting (token bucket)
- [x] Идемпотентность (Payment Service)
- [x] State machine для статусов заказа
- [x] Saga Pattern (хореография)
- [x] CQRS (Catalog Service)

Наблюдаемость:
- [x] Distributed Tracing (OpenTelemetry + Jaeger)
- [x] Structured Logging (slog JSON)
- [x] Health/Readiness проверки

Инфраструктура:
- [x] Distroless Docker образы
- [x] Docker Compose для dev
- [x] Kubernetes манифесты (Deployment + Service + HPA)
- [x] Makefile для автоматизации
```

### Технологический стек

| Слой | Технология | Аналог в C# |
|------|-----------|-------------|
| HTTP | chi | ASP.NET Core |
| gRPC | google.golang.org/grpc | Grpc.AspNetCore |
| Proto | buf | Grpc.Tools |
| База данных | pgx/v5 | EF Core / Npgsql |
| Кэш | go-redis/v9 | StackExchange.Redis |
| Очереди | kafka-go | MassTransit + Kafka |
| JWT | golang-jwt/jwt/v5 | System.IdentityModel.Tokens.Jwt |
| Circuit Breaker | gobreaker | Polly |
| Трейсинг | OpenTelemetry | OpenTelemetry .NET |
| Тесты | testify + testcontainers | xUnit + TestContainers.NET |
| DI | нет — явная инициализация | Microsoft.Extensions.DI |

### Дополнительные задания

1. **Поиск товаров**: добавить полнотекстовый поиск через PostgreSQL `tsvector` или Elasticsearch
2. **Refresh Token**: реализовать `POST /auth/refresh` в User Service
3. **Admin API**: отдельный сервис для управления товарами с RBAC
4. **Prometheus метрики**: добавить RED метрики в каждый сервис
5. **Outbox Pattern**: надёжная публикация событий в Order Service через транзакционный Outbox
6. **gRPC-Gateway**: добавить REST/gRPC gateway вместо кастомного API Gateway
7. **E2E тесты**: написать end-to-end тесты с реальными Kafka и PostgreSQL

---
