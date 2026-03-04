# 5. Деплой: Docker Compose и Production

---

## Dockerfile

Go компилируется в единственный бинарный файл без зависимостей runtime.
Это делает Docker-образы минимальными.

### C# подход

```dockerfile
# Многостадийный build для ASP.NET Core
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app
COPY *.csproj .
RUN dotnet restore
COPY . .
RUN dotnet publish -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "MyApp.dll"]
# Итоговый размер: ~200-300 MB
```

### Go подход

```dockerfile
# ===== Стадия 1: Сборка =====
FROM golang:1.26-alpine AS builder

WORKDIR /app

# Кэшируем зависимости отдельным слоем
# Слой перестраивается только при изменении go.mod / go.sum
COPY go.mod go.sum ./
RUN go mod download

# Копируем исходники и собираем
COPY . .

# CGO_ENABLED=0 — статическая сборка, нет зависимостей от C-библиотек
# GOOS=linux GOARCH=amd64 — кросс-компиляция (если разрабатываем на macOS/Windows)
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build \
    -ldflags="-w -s" \  # убираем отладочную информацию (уменьшает размер)
    -o /app/server \
    ./cmd/server

# ===== Стадия 2: Минимальный образ =====
# scratch — пустой образ (0 байт). Только наш бинарник + CA сертификаты.
# Альтернатива: gcr.io/distroless/static-debian12 (чуть безопаснее)
FROM scratch

# CA сертификаты нужны для HTTPS-запросов из приложения (если есть)
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Копируем только бинарник
COPY --from=builder /app/server /server

# Миграции (если применяем при старте)
COPY migrations/ /migrations/

# Непривилегированный пользователь (security best practice)
# scratch не поддерживает USER инструкцию — используем числовой UID
USER 65534:65534

EXPOSE 8080

# Health check встроен в Docker
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["/server", "-health"] || exit 1

ENTRYPOINT ["/server"]
```

> 💡 **Размер образа**: Go scratch образ ~7-15 MB vs ASP.NET Core ~200 MB.
> Меньше образ = быстрее pull, меньше attack surface, ниже стоимость registry.

> ⚠️ **`-ldflags="-w -s"`**: `-w` убирает DWARF отладочную информацию, `-s` убирает
> символьную таблицу. Уменьшает размер бинарника на 30-40%. Без этих флагов
> `go build` включает всё необходимое для `dlv` отладчика.

---

## Docker Compose

```yaml
# docker-compose.yml
version: "3.9"

services:
  # ===== Приложение =====
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      # Конфигурация через переменные окружения
      - ADDR=:8080
      - DATABASE_URL=postgres://urlshortener:secret@postgres:5432/urlshortener?sslmode=disable
      - REDIS_URL=redis://redis:6379
      - BASE_URL=http://localhost:8080
      - RATE_LIMIT=100    # запросов/сек
      - RATE_BURST=20     # burst
    depends_on:
      postgres:
        condition: service_healthy  # ждём пока PG не скажет что готов
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:8080/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

  # ===== PostgreSQL =====
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: urlshortener
      POSTGRES_USER: urlshortener
      POSTGRES_PASSWORD: secret
    volumes:
      - postgres_data:/var/lib/postgresql/data
      # Автоматически применяем миграции при первом запуске
      - ./migrations:/docker-entrypoint-initdb.d:ro
    ports:
      - "5432:5432"   # только для локальной разработки
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U urlshortener -d urlshortener"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # ===== Redis =====
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"   # только для локальной разработки
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

**Команды**:

```bash
# Запуск всего стека
docker compose up -d

# Логи приложения
docker compose logs -f app

# Остановка
docker compose down

# Остановка с удалением данных (volumes)
docker compose down -v

# Перестройка образа при изменении кода
docker compose up -d --build app
```

> 💡 **`depends_on: condition: service_healthy`**: Приложение стартует только когда
> PostgreSQL и Redis прошли healthcheck. Без этого возможен race condition:
> приложение стартует раньше БД и падает при попытке подключиться.

---

## Конфигурация через переменные окружения

### C# подход

```json
// appsettings.json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Database=urlshortener;..."
  },
  "Redis": {
    "ConnectionString": "localhost:6379"
  },
  "RateLimit": {
    "RequestsPerSecond": 100
  }
}
```

```csharp
// Program.cs
builder.Services.Configure<RateLimitOptions>(
    builder.Configuration.GetSection("RateLimit"));
var connStr = builder.Configuration.GetConnectionString("DefaultConnection");
```

### Go подход

```go
// internal/config/config.go
package config

import (
    "fmt"
    "os"
    "strconv"
)

// Config — полная конфигурация приложения.
// Все значения из переменных окружения с дефолтами для разработки.
type Config struct {
    // Сервер
    Addr    string // :8080
    BaseURL string // http://localhost:8080

    // База данных
    DatabaseURL     string
    DatabaseMaxConns int

    // Redis
    RedisURL string

    // Rate limiting
    RateLimit float64 // запросов в секунду
    RateBurst int

    // Приложение
    ShutdownTimeout int // секунд для graceful shutdown
}

// Load читает конфигурацию из переменных окружения.
// Возвращает ошибку если обязательные поля отсутствуют.
func Load() (Config, error) {
    cfg := Config{
        // Значения по умолчанию (для локальной разработки)
        Addr:            getEnv("ADDR", ":8080"),
        BaseURL:         getEnv("BASE_URL", "http://localhost:8080"),
        DatabaseURL:     getEnv("DATABASE_URL", ""),
        DatabaseMaxConns: getEnvInt("DB_MAX_CONNS", 25),
        RedisURL:        getEnv("REDIS_URL", "redis://localhost:6379"),
        RateLimit:       getEnvFloat("RATE_LIMIT", 100),
        RateBurst:       getEnvInt("RATE_BURST", 20),
        ShutdownTimeout: getEnvInt("SHUTDOWN_TIMEOUT", 30),
    }

    // Проверяем обязательные поля
    if cfg.DatabaseURL == "" {
        return Config{}, fmt.Errorf("DATABASE_URL не задан")
    }

    return cfg, nil
}

func getEnv(key, defaultValue string) string {
    if v := os.Getenv(key); v != "" {
        return v
    }
    return defaultValue
}

func getEnvInt(key string, defaultValue int) int {
    if v := os.Getenv(key); v != "" {
        if n, err := strconv.Atoi(v); err == nil {
            return n
        }
    }
    return defaultValue
}

func getEnvFloat(key string, defaultValue float64) float64 {
    if v := os.Getenv(key); v != "" {
        if f, err := strconv.ParseFloat(v, 64); err == nil {
            return f
        }
    }
    return defaultValue
}
```

**.env.example** (для локальной разработки):

```bash
# .env.example — копируем в .env и настраиваем

# Сервер
ADDR=:8080
BASE_URL=http://localhost:8080

# База данных
DATABASE_URL=postgres://urlshortener:secret@localhost:5432/urlshortener?sslmode=disable
DB_MAX_CONNS=25

# Redis
REDIS_URL=redis://localhost:6379

# Rate limiting (запросов в секунду)
RATE_LIMIT=100
RATE_BURST=20

# Graceful shutdown (секунды)
SHUTDOWN_TIMEOUT=30
```

> ⚠️ **`.env` в `.gitignore`**: Никогда не коммитьте `.env` с реальными секретами.
> Только `.env.example` с заглушками. В production секреты хранятся в Vault,
> AWS Secrets Manager или Kubernetes Secrets.

---

## Graceful shutdown

Graceful shutdown позволяет завершить обработку текущих запросов перед остановкой.
В C# это встроено в `IHostedService`. В Go — реализуется вручную.

```go
// cmd/server/main.go (graceful shutdown блок)
func run(ctx context.Context, cfg config.Config) error {
    // ... инициализация ...

    srv := &http.Server{
        Addr:         cfg.Addr,
        Handler:      router,
        ReadTimeout:  15 * time.Second,
        WriteTimeout: 15 * time.Second,
        IdleTimeout:  60 * time.Second,
    }

    // Канал для ошибок сервера
    serverErr := make(chan error, 1)

    // Запускаем сервер в горутине
    go func() {
        slog.Info("сервер запущен", "addr", cfg.Addr)
        if err := srv.ListenAndServe(); err != http.ErrServerClosed {
            serverErr <- err
        }
    }()

    // Ожидаем сигнал ОС или ошибку сервера
    shutdown := make(chan os.Signal, 1)
    signal.Notify(shutdown, syscall.SIGINT, syscall.SIGTERM)

    select {
    case err := <-serverErr:
        return fmt.Errorf("ошибка сервера: %w", err)

    case sig := <-shutdown:
        slog.Info("получен сигнал завершения", "signal", sig.String())

        // Graceful shutdown с таймаутом
        shutdownCtx, cancel := context.WithTimeout(
            context.Background(),
            time.Duration(cfg.ShutdownTimeout)*time.Second,
        )
        defer cancel()

        // Shutdown ждёт завершения активных соединений
        if err := srv.Shutdown(shutdownCtx); err != nil {
            // Принудительно закрываем если не успели за таймаут
            srv.Close()
            return fmt.Errorf("graceful shutdown: %w", err)
        }
    }

    slog.Info("сервер остановлен")
    return nil
}
```

```mermaid
sequenceDiagram
    participant OS as ОС
    participant App as Приложение
    participant Srv as HTTP Server
    participant Req as Активные запросы

    OS->>App: SIGTERM
    App->>Srv: Shutdown(ctx, 30s)
    Srv->>Srv: Перестать принимать новые
    Srv->>Req: Ждём завершения
    Req-->>Srv: Запросы завершены
    Srv-->>App: nil (успех)
    App-->>OS: exit 0
```

---

## Health checks

Health check нужен для:
- **Load balancer** (nginx, AWS ALB) — убирать нездоровые инстансы
- **Docker / Kubernetes** — перезапускать проблемные контейнеры
- **Мониторинг** — alerting при деградации

```go
// internal/handler/health.go
package handler

import (
    "context"
    "net/http"
    "time"

    "github.com/jackc/pgx/v5/pgxpool"
    "github.com/redis/go-redis/v9"
)

// HealthChecker содержит зависимости для проверки здоровья.
type HealthChecker struct {
    db    *pgxpool.Pool
    redis *redis.Client
}

func NewHealthChecker(db *pgxpool.Pool, redis *redis.Client) *HealthChecker {
    return &HealthChecker{db: db, redis: redis}
}

// healthStatus — статус компонентов.
type healthStatus struct {
    Status     string            `json:"status"`          // "ok" | "degraded"
    Components map[string]string `json:"components"`
}

// Check возвращает статус всех зависимостей.
// Если хотя бы одна зависимость недоступна — статус "degraded", код 503.
func (h *HealthChecker) Check(w http.ResponseWriter, r *http.Request) {
    ctx, cancel := context.WithTimeout(r.Context(), 3*time.Second)
    defer cancel()

    components := make(map[string]string)
    overall := "ok"

    // Проверяем PostgreSQL
    if err := h.db.Ping(ctx); err != nil {
        components["postgres"] = "unavailable: " + err.Error()
        overall = "degraded"
    } else {
        components["postgres"] = "ok"
    }

    // Проверяем Redis
    if err := h.redis.Ping(ctx).Err(); err != nil {
        components["redis"] = "unavailable: " + err.Error()
        overall = "degraded"
    } else {
        components["redis"] = "ok"
    }

    status := healthStatus{
        Status:     overall,
        Components: components,
    }

    // 200 если всё ок, 503 если что-то недоступно
    httpStatus := http.StatusOK
    if overall != "ok" {
        httpStatus = http.StatusServiceUnavailable
    }

    writeJSON(w, httpStatus, status)
}
```

**Пример ответов**:

```json
// GET /health — всё ок
{
  "status": "ok",
  "components": {
    "postgres": "ok",
    "redis": "ok"
  }
}

// GET /health — Redis недоступен
{
  "status": "degraded",
  "components": {
    "postgres": "ok",
    "redis": "unavailable: dial tcp: connection refused"
  }
}
```

---

## Структурированное логирование

`log/slog` — стандартный пакет Go 1.21+. Нет необходимости в Serilog/NLog.

```go
// cmd/server/main.go — инициализация логгера
logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
    // AddSource: true, // добавляет файл:строку в каждое сообщение
}))
slog.SetDefault(logger)

// В хэндлерах — структурированные атрибуты
slog.Info("создан URL",
    "code", result.Code,
    "original_url", req.URL,
    "remote_addr", r.RemoteAddr,
)

slog.Error("ошибка базы данных",
    "operation", "GetByCode",
    "code", code,
    "err", err,
)
```

**Пример вывода JSON**:

```json
{"time":"2024-01-15T10:23:45Z","level":"INFO","msg":"сервер запущен","addr":":8080"}
{"time":"2024-01-15T10:23:50Z","level":"INFO","msg":"http request","method":"POST","path":"/api/urls","status":201,"duration_ms":3}
{"time":"2024-01-15T10:23:51Z","level":"INFO","msg":"http request","method":"GET","path":"/aB3xY9","status":302,"duration_ms":1}
{"time":"2024-01-15T10:23:52Z","level":"ERROR","msg":"ошибка базы данных","operation":"GetByCode","code":"xyz","err":"connection refused"}
```

> 💡 **Для C# разработчиков**: `slog` ≈ `ILogger<T>` из Microsoft.Extensions.Logging
> со структурированным выводом. Не нужна внешняя библиотека для базовых нужд.

---

## Production чек-лист

```mermaid
graph LR
    subgraph Security["Безопасность"]
        S1["Непривилег. пользователь<br/>USER 65534"]
        S2["Нет секретов в образе"]
        S3["Read-only filesystem"]
    end

    subgraph Reliability["Надёжность"]
        R1["Graceful shutdown"]
        R2["Health checks"]
        R3["Restart policy"]
    end

    subgraph Observability["Наблюдаемость"]
        O1["JSON логи"]
        O2["Метрики (Prometheus)"]
        O3["Трейсинг (OpenTelemetry)"]
    end

    subgraph Performance["Производительность"]
        P1["Connection pool tuning"]
        P2["Redis maxmemory policy"]
        P3["HTTP timeouts"]
    end
```

### Чек-лист

**Безопасность**:
- [ ] Непривилегированный пользователь в контейнере (не root)
- [ ] Секреты не в образе, не в git (только env vars / secrets manager)
- [ ] `.env` в `.gitignore`
- [ ] HTTPS (TLS termination на load balancer или nginx)
- [ ] Rate limiting настроен для production нагрузки
- [ ] SQL-параметризованные запросы (нет конкатенации строк)

**Надёжность**:
- [ ] Graceful shutdown обрабатывает SIGTERM
- [ ] Health check endpoint возвращает 503 при деградации
- [ ] `restart: unless-stopped` в docker-compose
- [ ] `depends_on: condition: service_healthy` для зависимостей
- [ ] Таймауты на все операции (HTTP, DB, Redis)

**Наблюдаемость**:
- [ ] Структурированные JSON-логи
- [ ] Логируется: метод, путь, статус, latency
- [ ] Ошибки логируются с контекстом (code, err)
- [ ] Prometheus метрики (опционально для этого проекта)

**Производительность**:
- [ ] `pgxpool` настроен: MaxConns, MinConns, MaxConnLifetime
- [ ] Redis `maxmemory` и политика вытеснения (`allkeys-lru`)
- [ ] HTTP таймауты: ReadTimeout, WriteTimeout, IdleTimeout
- [ ] `CGO_ENABLED=0` для статической сборки

---

## Сравнительная таблица

| Аспект | C# / ASP.NET Core | Go |
|--------|------------------|----|
| Dockerfile base | `mcr.microsoft.com/dotnet/aspnet:8.0` (~200 MB) | `scratch` (~7 MB) |
| Runtime | .NET runtime (нужен в образе) | Нет (статический бинарник) |
| Graceful shutdown | `IHostedService` / `IHostApplicationLifetime` | `server.Shutdown(ctx)` вручную |
| Health checks | `IHealthCheck` + `AddHealthChecks()` | Обычный HTTP хэндлер |
| Конфигурация | `appsettings.json` + `IConfiguration` | `os.Getenv` / env-пакеты |
| Секреты | Azure Key Vault / User Secrets | Vault / AWS Secrets Manager / env |
| Логирование | Serilog / NLog / `ILogger<T>` | `log/slog` (stdlib) |
| Сигналы ОС | `IHostApplicationLifetime` | `signal.Notify(chan, SIGTERM)` |
| Docker Compose | Аналогично | Аналогично |

---

## Итоги проекта

Поздравляем! Вы построили полноценный production-ready URL Shortener на Go:

| Компонент | Реализован |
|-----------|-----------|
| Доменная модель + ошибки | ✅ |
| PostgreSQL репозиторий (pgx) | ✅ |
| Redis кэш (cache-aside) | ✅ |
| HTTP API (net/http) | ✅ |
| Миграция на chi | ✅ |
| Middleware (logging, recovery, rate limit) | ✅ |
| Unit + handler тесты | ✅ |
| Integration тесты (testcontainers-go) | ✅ |
| Бенчмарки | ✅ |
| Docker + Docker Compose | ✅ |
| Graceful shutdown | ✅ |
| Health checks | ✅ |
| Структурированное логирование | ✅ |

**Что изучили**:
- Идиоматичный Go: структуры, интерфейсы, ошибки
- Работа с PostgreSQL без ORM (pgx)
- Кэширование в Redis (cache-aside паттерн)
- HTTP сервер: net/http → chi
- Тестирование без mock-библиотек
- Docker для Go приложений

---
