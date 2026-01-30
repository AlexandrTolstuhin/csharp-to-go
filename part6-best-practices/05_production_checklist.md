# 6.5 Production Checklist

## Содержание

- [Введение](#введение)
- [1. Graceful Shutdown](#1-graceful-shutdown)
  - [1.1 Зачем нужен graceful shutdown](#11-зачем-нужен-graceful-shutdown)
  - [1.2 Сигналы ОС](#12-сигналы-ос)
  - [1.3 Паттерн реализации](#13-паттерн-реализации)
  - [1.4 Shutdown order](#14-shutdown-order)
  - [1.5 Kubernetes интеграция](#15-kubernetes-интеграция)
- [2. Health Checks](#2-health-checks)
  - [2.1 Типы проверок](#21-типы-проверок)
  - [2.2 Реализация endpoints](#22-реализация-endpoints)
  - [2.3 Проверка зависимостей](#23-проверка-зависимостей)
  - [2.4 Kubernetes probes](#24-kubernetes-probes)
- [3. Structured Logging](#3-structured-logging)
  - [3.1 Production requirements](#31-production-requirements)
  - [3.2 slog конфигурация](#32-slog-конфигурация)
  - [3.3 Уровни логирования](#33-уровни-логирования)
  - [3.4 Маскирование sensitive data](#34-маскирование-sensitive-data)
  - [3.5 Request ID и correlation](#35-request-id-и-correlation)
- [4. Metrics и Monitoring](#4-metrics-и-monitoring)
  - [4.1 RED metrics](#41-red-metrics)
  - [4.2 Prometheus экспорт](#42-prometheus-экспорт)
  - [4.3 Бизнес-метрики](#43-бизнес-метрики)
  - [4.4 Alerting](#44-alerting)
- [5. Distributed Tracing](#5-distributed-tracing)
  - [5.1 Когда tracing необходим](#51-когда-tracing-необходим)
  - [5.2 OpenTelemetry setup](#52-opentelemetry-setup)
  - [5.3 Sampling strategies](#53-sampling-strategies)
- [6. Resilience Patterns](#6-resilience-patterns)
  - [6.1 Rate Limiting](#61-rate-limiting)
  - [6.2 Circuit Breaker](#62-circuit-breaker)
  - [6.3 Retry с Exponential Backoff](#63-retry-с-exponential-backoff)
  - [6.4 Timeouts и Deadlines](#64-timeouts-и-deadlines)
  - [6.5 Bulkhead pattern](#65-bulkhead-pattern)
- [7. Error Handling в Production](#7-error-handling-в-production)
  - [7.1 Классификация ошибок](#71-классификация-ошибок)
  - [7.2 RFC 7807 Problem Details](#72-rfc-7807-problem-details)
  - [7.3 Panic recovery](#73-panic-recovery)
  - [7.4 Error tracking](#74-error-tracking)
- [8. Configuration](#8-configuration)
  - [8.1 12-Factor App](#81-12-factor-app)
  - [8.2 Environment variables](#82-environment-variables)
  - [8.3 Secrets management](#83-secrets-management)
  - [8.4 Fail fast validation](#84-fail-fast-validation)
- [9. Docker Images](#9-docker-images)
  - [9.1 Multi-stage build](#91-multi-stage-build)
  - [9.2 Base images](#92-base-images)
  - [9.3 Security scanning](#93-security-scanning)
  - [9.4 Non-root user](#94-non-root-user)
- [10. Security Checklist](#10-security-checklist)
  - [10.1 Input validation](#101-input-validation)
  - [10.2 SQL injection prevention](#102-sql-injection-prevention)
  - [10.3 Security headers](#103-security-headers)
  - [10.4 Dependency scanning](#104-dependency-scanning)
- [Практические примеры](#практические-примеры)
  - [Пример 1: Production-Ready HTTP Server](#пример-1-production-ready-http-server)
  - [Пример 2: Complete main.go Template](#пример-2-complete-maingo-template)
  - [Пример 3: Kubernetes Manifests](#пример-3-kubernetes-manifests)
- [Master Checklist](#master-checklist)
- [Чек-лист](#чек-лист)

---

## Введение

Этот раздел — **финальный чек-лист** для подготовки Go-приложения к production. Он объединяет best practices из всего курса в единый практический документ.

> **Для C# разработчиков**: ASP.NET Core предоставляет многое "из коробки" (health checks, graceful shutdown, DI). В Go вы собираете эти компоненты самостоятельно, что даёт больше контроля, но требует понимания каждой части.

### C# vs Go: Production-Ready "из коробки"

| Компонент | ASP.NET Core | Go |
|-----------|--------------|-----|
| **Graceful shutdown** | `IHostApplicationLifetime` (встроен) | `signal.NotifyContext` (ручная реализация) |
| **Health checks** | `Microsoft.Extensions.Diagnostics.HealthChecks` | Ручная реализация endpoints |
| **Structured logging** | `ILogger<T>` + Serilog/NLog | `log/slog` (Go 1.21+) |
| **Metrics** | OpenTelemetry.Exporter.Prometheus | `prometheus/client_golang` |
| **Configuration** | `IConfiguration` + appsettings.json | `os.Getenv` + библиотеки (envconfig, viper) |
| **Rate limiting** | `Microsoft.AspNetCore.RateLimiting` | `golang.org/x/time/rate` |
| **Circuit breaker** | Polly | `sony/gobreaker` |

**Философское различие**:

```
┌─────────────────────────────────────────────────────────────────┐
│                 PRODUCTION READINESS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ASP.NET Core:                                                  │
│   ─────────────                                                  │
│   • Batteries included — многое работает из коробки             │
│   • Стандартизированные паттерны (middleware, DI, IHost)        │
│   • Обширная документация Microsoft                              │
│   • Интеграция с Azure "в один клик"                            │
│                                                                  │
│   Go:                                                            │
│   ────                                                           │
│   • Minimal by design — собираешь сам                           │
│   • Простота > магия                                             │
│   • Каждый компонент явный и понятный                           │
│   • Полный контроль над поведением                              │
│                                                                  │
│   Вывод:                                                         │
│   ──────                                                         │
│   • В Go production-ready = явно реализованные паттерны         │
│   • Этот чек-лист = аналог того, что ASP.NET Core делает сам    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Связь с другими разделами курса

Этот раздел **не дублирует**, а **интегрирует** материалы:

| Тема | Детальный материал |
|------|-------------------|
| HTTP Server basics | [3.1 HTTP в Go](../part3-web-api/01_http_server.md) |
| Observability (подробно) | [4.5 Observability](../part4-infrastructure/05_observability.md) |
| Контейнеризация | [4.7 Контейнеризация](../part4-infrastructure/07_containerization.md) |
| Error handling | [2.5 Обработка ошибок](../part2-advanced/05_error_handling.md) |
| Конфигурация | [4.6 Конфигурация](../part4-infrastructure/06_configuration.md) |
| Производительность | [6.4 Производительность](./04_performance.md) |

---

## 1. Graceful Shutdown

### 1.1 Зачем нужен graceful shutdown

**Graceful shutdown** — корректное завершение работы приложения:
- Завершение текущих запросов (не обрывать на середине)
- Закрытие соединений с БД
- Flush буферов логов и метрик
- Освобождение ресурсов

**Без graceful shutdown**:
```
┌─────────────────────────────────────────────────────────────────┐
│   Клиент отправляет запрос                                      │
│        ↓                                                         │
│   Kubernetes отправляет SIGTERM                                  │
│        ↓                                                         │
│   Pod НЕМЕДЛЕННО убит (SIGKILL)                                 │
│        ↓                                                         │
│   Клиент получает "connection reset" или таймаут                │
│        ↓                                                         │
│   Данные не сохранены, транзакция откачена                      │
└─────────────────────────────────────────────────────────────────┘
```

**С graceful shutdown**:
```
┌─────────────────────────────────────────────────────────────────┐
│   Клиент отправляет запрос                                      │
│        ↓                                                         │
│   Kubernetes отправляет SIGTERM                                  │
│        ↓                                                         │
│   Приложение ПРЕКРАЩАЕТ принимать новые запросы                 │
│        ↓                                                         │
│   Текущий запрос ЗАВЕРШАЕТСЯ нормально                          │
│        ↓                                                         │
│   Соединения закрываются, логи flush'атся                       │
│        ↓                                                         │
│   Приложение завершается с exit code 0                          │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Сигналы ОС

**Основные сигналы**:

| Сигнал | Код | Описание | Kubernetes |
|--------|-----|----------|------------|
| `SIGINT` | 2 | Ctrl+C (интерактивное завершение) | — |
| `SIGTERM` | 15 | Запрос на завершение | preStop hook, по умолчанию |
| `SIGKILL` | 9 | Принудительное завершение | После `terminationGracePeriodSeconds` |
| `SIGHUP` | 1 | Перезагрузка конфигурации | — |

> **C# разработчикам**: В .NET вы используете `IHostApplicationLifetime.ApplicationStopping`. В Go — напрямую работаете с сигналами ОС через `os/signal`.

**Важно**: `SIGKILL` нельзя перехватить — процесс убивается мгновенно. Поэтому критично обрабатывать `SIGTERM`.

### 1.3 Паттерн реализации

**Базовый паттерн** (Go 1.16+):

```go
package main

import (
    "context"
    "errors"
    "log/slog"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"
)

func main() {
    logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

    // Создаём context, который отменится при получении сигнала
    ctx, stop := signal.NotifyContext(context.Background(),
        syscall.SIGINT,  // Ctrl+C
        syscall.SIGTERM, // Kubernetes
    )
    defer stop()

    // HTTP server
    server := &http.Server{
        Addr:    ":8080",
        Handler: http.HandlerFunc(handleRequest),
    }

    // Запускаем сервер в горутине
    go func() {
        logger.Info("starting server", "addr", server.Addr)
        if err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
            logger.Error("server error", "error", err)
            os.Exit(1)
        }
    }()

    // Ждём сигнала завершения
    <-ctx.Done()
    logger.Info("shutdown signal received")

    // Graceful shutdown с таймаутом
    shutdownCtx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := server.Shutdown(shutdownCtx); err != nil {
        logger.Error("server shutdown error", "error", err)
        os.Exit(1)
    }

    logger.Info("server stopped gracefully")
}

func handleRequest(w http.ResponseWriter, r *http.Request) {
    // Симуляция долгой операции
    time.Sleep(5 * time.Second)
    w.Write([]byte("OK"))
}
```

**Сравнение с C#**:

```csharp
// C#: IHostApplicationLifetime
public class Worker : BackgroundService
{
    private readonly IHostApplicationLifetime _lifetime;

    public Worker(IHostApplicationLifetime lifetime)
    {
        _lifetime = lifetime;
        _lifetime.ApplicationStopping.Register(OnStopping);
    }

    private void OnStopping()
    {
        // Graceful shutdown logic
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            // Work
        }
    }
}
```

```go
// Go: signal.NotifyContext — более явный контроль
ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGTERM)
defer stop()

// Передаём ctx во все компоненты
worker := NewWorker(ctx, logger)
go worker.Run()

<-ctx.Done() // Ждём сигнала
worker.Stop() // Явный вызов остановки
```

### 1.4 Shutdown order

**Правильный порядок завершения**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SHUTDOWN ORDER                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. STOP ACCEPTING NEW REQUESTS                                 │
│      └── Health check возвращает "not ready"                    │
│      └── Load balancer перестаёт направлять трафик              │
│                                                                  │
│   2. COMPLETE IN-FLIGHT REQUESTS                                 │
│      └── Ждём завершения текущих HTTP запросов                  │
│      └── server.Shutdown() делает это автоматически             │
│                                                                  │
│   3. STOP BACKGROUND WORKERS                                     │
│      └── Отменяем context для воркеров                          │
│      └── Ждём завершения горутин (WaitGroup или errgroup)       │
│                                                                  │
│   4. CLOSE EXTERNAL CONNECTIONS                                  │
│      └── Database connections                                    │
│      └── Redis, message queues                                   │
│      └── gRPC connections                                        │
│                                                                  │
│   5. FLUSH BUFFERS                                               │
│      └── Логи (slog с буферизацией)                             │
│      └── Метрики                                                 │
│      └── Tracing spans                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Реализация с несколькими компонентами**:

```go
package main

import (
    "context"
    "database/sql"
    "errors"
    "log/slog"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "golang.org/x/sync/errgroup"
)

type App struct {
    server     *http.Server
    db         *sql.DB
    logger     *slog.Logger
    shutdownCh chan struct{}
}

func NewApp(db *sql.DB, logger *slog.Logger) *App {
    app := &App{
        db:         db,
        logger:     logger,
        shutdownCh: make(chan struct{}),
    }

    mux := http.NewServeMux()
    mux.HandleFunc("/healthz", app.healthzHandler)
    mux.HandleFunc("/ready", app.readyHandler)
    mux.HandleFunc("/", app.mainHandler)

    app.server = &http.Server{
        Addr:         ":8080",
        Handler:      mux,
        ReadTimeout:  5 * time.Second,
        WriteTimeout: 10 * time.Second,
        IdleTimeout:  120 * time.Second,
    }

    return app
}

func (a *App) Run(ctx context.Context) error {
    g, gCtx := errgroup.WithContext(ctx)

    // HTTP server
    g.Go(func() error {
        a.logger.Info("starting HTTP server", "addr", a.server.Addr)
        if err := a.server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
            return err
        }
        return nil
    })

    // Graceful shutdown при отмене context
    g.Go(func() error {
        <-gCtx.Done()
        a.logger.Info("initiating graceful shutdown")

        // Помечаем приложение как "not ready"
        close(a.shutdownCh)

        // Даём время load balancer'у перенаправить трафик
        a.logger.Info("waiting for load balancer drain")
        time.Sleep(5 * time.Second)

        // Shutdown HTTP server
        shutdownCtx, cancel := context.WithTimeout(context.Background(), 25*time.Second)
        defer cancel()

        if err := a.server.Shutdown(shutdownCtx); err != nil {
            a.logger.Error("HTTP server shutdown error", "error", err)
            return err
        }
        a.logger.Info("HTTP server stopped")

        // Close database
        if err := a.db.Close(); err != nil {
            a.logger.Error("database close error", "error", err)
            return err
        }
        a.logger.Info("database connection closed")

        return nil
    })

    return g.Wait()
}

func (a *App) healthzHandler(w http.ResponseWriter, r *http.Request) {
    // Liveness: процесс жив
    w.WriteHeader(http.StatusOK)
    w.Write([]byte(`{"status":"ok"}`))
}

func (a *App) readyHandler(w http.ResponseWriter, r *http.Request) {
    // Readiness: готов принимать трафик
    select {
    case <-a.shutdownCh:
        // Shutdown в процессе — не готовы
        w.WriteHeader(http.StatusServiceUnavailable)
        w.Write([]byte(`{"status":"shutting_down"}`))
        return
    default:
    }

    // Проверяем зависимости
    ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
    defer cancel()

    if err := a.db.PingContext(ctx); err != nil {
        w.WriteHeader(http.StatusServiceUnavailable)
        w.Write([]byte(`{"status":"database_unavailable"}`))
        return
    }

    w.WriteHeader(http.StatusOK)
    w.Write([]byte(`{"status":"ready"}`))
}

func (a *App) mainHandler(w http.ResponseWriter, r *http.Request) {
    time.Sleep(2 * time.Second) // Симуляция работы
    w.Write([]byte("Hello, World!"))
}

func main() {
    logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

    // Database connection (пример)
    db, err := sql.Open("postgres", os.Getenv("DATABASE_URL"))
    if err != nil {
        logger.Error("failed to connect to database", "error", err)
        os.Exit(1)
    }

    app := NewApp(db, logger)

    // Signal handling
    ctx, stop := signal.NotifyContext(context.Background(),
        syscall.SIGINT,
        syscall.SIGTERM,
    )
    defer stop()

    if err := app.Run(ctx); err != nil {
        logger.Error("application error", "error", err)
        os.Exit(1)
    }

    logger.Info("application stopped gracefully")
}
```

### 1.5 Kubernetes интеграция

**Kubernetes Deployment**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  template:
    spec:
      # Время на graceful shutdown (по умолчанию 30s)
      terminationGracePeriodSeconds: 45
      containers:
        - name: app
          image: myapp:latest
          ports:
            - containerPort: 8080
          # Readiness probe — когда pod готов принимать трафик
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
            failureThreshold: 3
          # Liveness probe — когда pod нужно перезапустить
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 10
            failureThreshold: 3
          lifecycle:
            # preStop hook — выполняется ПЕРЕД отправкой SIGTERM
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 5"]
```

**Почему `preStop: sleep 5`?**

```
┌─────────────────────────────────────────────────────────────────┐
│                KUBERNETES SHUTDOWN SEQUENCE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. Pod помечается для удаления                                │
│      ↓                                                           │
│   2. Endpoints controller УДАЛЯЕТ pod из Service endpoints      │
│      (ПАРАЛЛЕЛЬНО с шагом 3!)                                   │
│      ↓                                                           │
│   3. preStop hook ВЫПОЛНЯЕТСЯ                                    │
│      └── sleep 5 даёт время endpoints controller'у              │
│      ↓                                                           │
│   4. SIGTERM отправляется контейнеру                            │
│      ↓                                                           │
│   5. Приложение начинает graceful shutdown                      │
│      ↓                                                           │
│   6. После terminationGracePeriodSeconds — SIGKILL              │
│                                                                  │
│   ПРОБЛЕМА БЕЗ preStop:                                          │
│   ─────────────────────                                          │
│   • SIGTERM может прийти ДО того, как kube-proxy обновится      │
│   • Новые запросы всё ещё идут на pod, который уже shutdown     │
│   • Результат: connection errors для клиентов                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Расчёт terminationGracePeriodSeconds**:

```
terminationGracePeriodSeconds >=
    preStop duration +
    request drain time +
    worker shutdown time +
    connection close time +
    buffer

Пример:
    5s (preStop) +
    10s (drain) +
    10s (workers) +
    5s (connections) +
    5s (buffer) = 35s → округляем до 45s
```

> **Идиома Go**: Всегда задавайте `terminationGracePeriodSeconds` больше, чем ваш shutdown timeout в коде. Иначе SIGKILL придёт раньше, чем приложение завершится.

---

## 2. Health Checks

### 2.1 Типы проверок

**Три типа health checks в Kubernetes**:

| Тип | Вопрос | Когда неуспешен | Действие K8s |
|-----|--------|-----------------|--------------|
| **Liveness** | "Процесс жив?" | Deadlock, hang | Перезапуск контейнера |
| **Readiness** | "Готов принимать трафик?" | Загрузка, warm-up, shutdown | Убрать из Service endpoints |
| **Startup** | "Приложение запустилось?" | Долгий старт | Отложить liveness/readiness |

> **Для C# разработчиков**: В ASP.NET Core есть `AddHealthChecks()` с `IHealthCheck`. В Go реализуем endpoints вручную, что даёт больше контроля.

**Типичные ошибки**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    РАСПРОСТРАНЁННЫЕ ОШИБКИ                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ❌ Liveness проверяет БД                                       │
│      └── БД упала → все pods перезапускаются → каскадный сбой   │
│      └── Правильно: liveness проверяет только процесс           │
│                                                                  │
│   ❌ Readiness не проверяет зависимости                          │
│      └── Pod "ready", но БД недоступна → 500 ошибки             │
│      └── Правильно: readiness проверяет критичные зависимости   │
│                                                                  │
│   ❌ Одинаковые liveness и readiness                             │
│      └── Readiness fail → pod убивается из endpoints            │
│      └── Liveness fail → pod ПЕРЕЗАПУСКАЕТСЯ                    │
│      └── Это разные вещи!                                        │
│                                                                  │
│   ❌ Слишком агрессивные thresholds                              │
│      └── failureThreshold: 1 → любой spike = перезапуск         │
│      └── Правильно: failureThreshold: 3, periodSeconds: 10      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Реализация endpoints

**Базовая реализация**:

```go
package health

import (
    "context"
    "encoding/json"
    "net/http"
    "sync/atomic"
    "time"
)

// Status представляет статус компонента
type Status string

const (
    StatusOK      Status = "ok"
    StatusDegraded Status = "degraded"
    StatusDown    Status = "down"
)

// Response — ответ health check endpoint
type Response struct {
    Status     Status            `json:"status"`
    Components map[string]Status `json:"components,omitempty"`
    Timestamp  time.Time         `json:"timestamp"`
}

// Checker проверяет здоровье приложения
type Checker struct {
    ready      atomic.Bool
    checks     map[string]CheckFunc
}

// CheckFunc — функция проверки компонента
type CheckFunc func(ctx context.Context) Status

// New создаёт новый Checker
func New() *Checker {
    c := &Checker{
        checks: make(map[string]CheckFunc),
    }
    c.ready.Store(true)
    return c
}

// Register добавляет проверку компонента
func (c *Checker) Register(name string, check CheckFunc) {
    c.checks[name] = check
}

// SetReady устанавливает флаг готовности
func (c *Checker) SetReady(ready bool) {
    c.ready.Store(ready)
}

// LivenessHandler — /healthz
// Проверяет только: процесс жив и отвечает
func (c *Checker) LivenessHandler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusOK)
    json.NewEncoder(w).Encode(Response{
        Status:    StatusOK,
        Timestamp: time.Now(),
    })
}

// ReadinessHandler — /ready
// Проверяет: готов принимать трафик
func (c *Checker) ReadinessHandler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")

    // Проверяем флаг готовности (для graceful shutdown)
    if !c.ready.Load() {
        w.WriteHeader(http.StatusServiceUnavailable)
        json.NewEncoder(w).Encode(Response{
            Status:    StatusDown,
            Timestamp: time.Now(),
        })
        return
    }

    // Проверяем все зависимости
    ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
    defer cancel()

    components := make(map[string]Status)
    overallStatus := StatusOK

    for name, check := range c.checks {
        status := check(ctx)
        components[name] = status
        if status != StatusOK {
            overallStatus = StatusDegraded
        }
        if status == StatusDown {
            overallStatus = StatusDown
        }
    }

    httpStatus := http.StatusOK
    if overallStatus == StatusDown {
        httpStatus = http.StatusServiceUnavailable
    }

    w.WriteHeader(httpStatus)
    json.NewEncoder(w).Encode(Response{
        Status:     overallStatus,
        Components: components,
        Timestamp:  time.Now(),
    })
}
```

**Использование**:

```go
func main() {
    checker := health.New()

    // Регистрируем проверки
    checker.Register("database", func(ctx context.Context) health.Status {
        if err := db.PingContext(ctx); err != nil {
            return health.StatusDown
        }
        return health.StatusOK
    })

    checker.Register("redis", func(ctx context.Context) health.Status {
        if err := redisClient.Ping(ctx).Err(); err != nil {
            return health.StatusDown
        }
        return health.StatusOK
    })

    checker.Register("external_api", func(ctx context.Context) health.Status {
        // Внешний API — degraded если недоступен, но не down
        resp, err := http.Get("https://api.example.com/health")
        if err != nil || resp.StatusCode != http.StatusOK {
            return health.StatusDegraded
        }
        return health.StatusOK
    })

    mux := http.NewServeMux()
    mux.HandleFunc("/healthz", checker.LivenessHandler)
    mux.HandleFunc("/ready", checker.ReadinessHandler)

    // При shutdown
    // checker.SetReady(false)
}
```

### 2.3 Проверка зависимостей

**Что проверять в readiness**:

| Зависимость | Проверка | Таймаут |
|-------------|----------|---------|
| PostgreSQL | `db.PingContext(ctx)` | 2s |
| Redis | `client.Ping(ctx)` | 1s |
| Kafka | Проверка метаданных | 3s |
| External API | `GET /health` | 5s |
| File storage | `os.Stat(path)` | 1s |

**Пример с несколькими БД**:

```go
// DatabaseChecker проверяет подключение к БД
type DatabaseChecker struct {
    db      *sql.DB
    name    string
    timeout time.Duration
}

func NewDatabaseChecker(db *sql.DB, name string) *DatabaseChecker {
    return &DatabaseChecker{
        db:      db,
        name:    name,
        timeout: 2 * time.Second,
    }
}

func (c *DatabaseChecker) Check(ctx context.Context) health.Status {
    ctx, cancel := context.WithTimeout(ctx, c.timeout)
    defer cancel()

    if err := c.db.PingContext(ctx); err != nil {
        slog.Warn("database health check failed",
            "database", c.name,
            "error", err,
        )
        return health.StatusDown
    }
    return health.StatusOK
}

// Использование
checker.Register("postgres_primary",
    NewDatabaseChecker(primaryDB, "primary").Check)
checker.Register("postgres_replica",
    NewDatabaseChecker(replicaDB, "replica").Check)
```

### 2.4 Kubernetes probes

**Полный пример конфигурации**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
        - name: app
          image: myapp:latest
          ports:
            - containerPort: 8080
              name: http

          # Startup probe: для приложений с долгим стартом
          # Пока startup не пройдёт — liveness/readiness не проверяются
          startupProbe:
            httpGet:
              path: /healthz
              port: http
            # 30 попыток × 10 сек = 5 минут на старт
            failureThreshold: 30
            periodSeconds: 10

          # Liveness: процесс жив?
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
            # Начинаем проверять через 0 сек (startup уже прошёл)
            initialDelaySeconds: 0
            periodSeconds: 10
            timeoutSeconds: 5
            # 3 неудачи подряд → перезапуск
            failureThreshold: 3
            successThreshold: 1

          # Readiness: готов к трафику?
          readinessProbe:
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 0
            periodSeconds: 5
            timeoutSeconds: 5
            # 3 неудачи → убираем из Service
            failureThreshold: 3
            # 1 успех → возвращаем в Service
            successThreshold: 1
```

**Сравнение с C#**:

```csharp
// C#: Microsoft.Extensions.Diagnostics.HealthChecks
services.AddHealthChecks()
    .AddDbContextCheck<AppDbContext>("database")
    .AddRedis(connectionString, "redis")
    .AddCheck<ExternalApiHealthCheck>("external_api");

app.MapHealthChecks("/healthz", new HealthCheckOptions
{
    Predicate = _ => false // Только process check
});

app.MapHealthChecks("/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")
});
```

```go
// Go: явная реализация (больше контроля)
checker := health.New()
checker.Register("database", dbChecker.Check)
checker.Register("redis", redisChecker.Check)
checker.Register("external_api", apiChecker.Check)

mux.HandleFunc("/healthz", checker.LivenessHandler)
mux.HandleFunc("/ready", checker.ReadinessHandler)
```

---

## 3. Structured Logging

### 3.1 Production requirements

**Требования к production логированию**:

```
┌─────────────────────────────────────────────────────────────────┐
│               PRODUCTION LOGGING REQUIREMENTS                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   FORMAT:                                                        │
│   • JSON (для ELK, Loki, CloudWatch)                            │
│   • Единый формат для всех сервисов                              │
│                                                                  │
│   FIELDS:                                                        │
│   • timestamp (ISO 8601)                                         │
│   • level (debug, info, warn, error)                            │
│   • message                                                      │
│   • service_name                                                 │
│   • request_id / trace_id / correlation_id                      │
│   • error (если есть)                                            │
│   • source (file:line) — для debug                              │
│                                                                  │
│   PERFORMANCE:                                                   │
│   • Минимум аллокаций на hot path                               │
│   • Async write с буферизацией                                  │
│   • Sampling для debug логов в production                       │
│                                                                  │
│   SECURITY:                                                      │
│   • Маскирование PII (emails, phones, cards)                    │
│   • Маскирование secrets (tokens, passwords, API keys)          │
│   • Не логировать request/response bodies с sensitive data      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 slog конфигурация

**Production setup с slog** (Go 1.21+):

```go
package logging

import (
    "context"
    "io"
    "log/slog"
    "os"
    "runtime"
    "strings"
)

// Config конфигурация логгера
type Config struct {
    Level       string `env:"LOG_LEVEL" envDefault:"info"`
    Format      string `env:"LOG_FORMAT" envDefault:"json"` // json или text
    ServiceName string `env:"SERVICE_NAME" envDefault:"app"`
    AddSource   bool   `env:"LOG_ADD_SOURCE" envDefault:"false"`
}

// New создаёт production-ready логгер
func New(cfg Config) *slog.Logger {
    var level slog.Level
    switch strings.ToLower(cfg.Level) {
    case "debug":
        level = slog.LevelDebug
    case "info":
        level = slog.LevelInfo
    case "warn", "warning":
        level = slog.LevelWarn
    case "error":
        level = slog.LevelError
    default:
        level = slog.LevelInfo
    }

    opts := &slog.HandlerOptions{
        Level:     level,
        AddSource: cfg.AddSource,
        ReplaceAttr: func(groups []string, a slog.Attr) slog.Attr {
            // Стандартизируем имена полей
            switch a.Key {
            case slog.TimeKey:
                // ISO 8601 формат
                return a
            case slog.LevelKey:
                // Lowercase level
                if level, ok := a.Value.Any().(slog.Level); ok {
                    return slog.String("level", strings.ToLower(level.String()))
                }
            case slog.MessageKey:
                return slog.String("msg", a.Value.String())
            }

            // Маскирование sensitive data
            return maskSensitiveData(a)
        },
    }

    var handler slog.Handler
    var output io.Writer = os.Stdout

    if cfg.Format == "json" {
        handler = slog.NewJSONHandler(output, opts)
    } else {
        handler = slog.NewTextHandler(output, opts)
    }

    // Добавляем service_name ко всем записям
    logger := slog.New(handler).With(
        slog.String("service", cfg.ServiceName),
    )

    return logger
}

// maskSensitiveData маскирует конфиденциальные данные
func maskSensitiveData(a slog.Attr) slog.Attr {
    key := strings.ToLower(a.Key)

    // Полная маскировка
    sensitiveKeys := []string{
        "password", "secret", "token", "api_key", "apikey",
        "authorization", "auth", "credential", "private_key",
    }
    for _, k := range sensitiveKeys {
        if strings.Contains(key, k) {
            return slog.String(a.Key, "[REDACTED]")
        }
    }

    // Частичная маскировка для PII
    piiKeys := []string{"email", "phone", "card", "ssn"}
    for _, k := range piiKeys {
        if strings.Contains(key, k) {
            value := a.Value.String()
            if len(value) > 4 {
                masked := value[:2] + strings.Repeat("*", len(value)-4) + value[len(value)-2:]
                return slog.String(a.Key, masked)
            }
            return slog.String(a.Key, "**")
        }
    }

    return a
}

// SetDefault устанавливает логгер по умолчанию
func SetDefault(logger *slog.Logger) {
    slog.SetDefault(logger)
}
```

**Использование**:

```go
func main() {
    cfg := logging.Config{
        Level:       os.Getenv("LOG_LEVEL"),
        Format:      "json",
        ServiceName: "user-service",
        AddSource:   os.Getenv("ENV") != "production",
    }

    logger := logging.New(cfg)
    logging.SetDefault(logger)

    // Теперь можно использовать slog напрямую
    slog.Info("application started", "port", 8080)

    // С context (для request_id)
    ctx := context.Background()
    slog.InfoContext(ctx, "processing request",
        "user_id", 123,
        "email", "user@example.com", // будет замаскирован
    )
}
```

**Пример вывода**:

```json
{
  "time": "2024-01-15T10:30:00.000Z",
  "level": "info",
  "msg": "processing request",
  "service": "user-service",
  "user_id": 123,
  "email": "us**********om"
}
```

### 3.3 Уровни логирования

**Когда использовать каждый уровень**:

| Уровень | Когда использовать | Примеры |
|---------|-------------------|---------|
| **DEBUG** | Детали для разработки | SQL queries, request/response bodies |
| **INFO** | Важные события | Request started/completed, user actions |
| **WARN** | Потенциальные проблемы | Slow queries, retry attempts, deprecation |
| **ERROR** | Ошибки требующие внимания | Failed requests, external service errors |

**Правила**:

```go
// ❌ Плохо: слишком много INFO
slog.Info("entering function processUser")
slog.Info("user found in database")
slog.Info("user validated")
slog.Info("returning response")

// ✅ Хорошо: INFO для бизнес-событий
slog.Info("user registered", "user_id", user.ID)
slog.Info("order placed", "order_id", order.ID, "amount", order.Total)

// ❌ Плохо: ERROR для ожидаемых случаев
if user == nil {
    slog.Error("user not found") // Это не ошибка системы!
}

// ✅ Хорошо: WARN для ожидаемых проблем, ERROR для неожиданных
if user == nil {
    slog.Debug("user not found", "user_id", userID)
    return ErrUserNotFound
}

if err := db.Save(user); err != nil {
    slog.Error("failed to save user", "error", err, "user_id", user.ID)
    return err
}
```

### 3.4 Маскирование sensitive data

**Расширенная реализация**:

```go
package logging

import (
    "log/slog"
    "regexp"
    "strings"
)

var (
    // Регулярки для маскирования
    emailRegex    = regexp.MustCompile(`[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`)
    phoneRegex    = regexp.MustCompile(`\+?[0-9]{10,15}`)
    cardRegex     = regexp.MustCompile(`[0-9]{13,19}`)
    uuidRegex     = regexp.MustCompile(`[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}`)
)

// SensitiveHandler оборачивает handler для маскирования
type SensitiveHandler struct {
    slog.Handler
}

func NewSensitiveHandler(h slog.Handler) *SensitiveHandler {
    return &SensitiveHandler{Handler: h}
}

func (h *SensitiveHandler) Handle(ctx context.Context, r slog.Record) error {
    // Создаём копию записи с замаскированными атрибутами
    newRecord := slog.NewRecord(r.Time, r.Level, r.Message, r.PC)

    r.Attrs(func(a slog.Attr) bool {
        newRecord.AddAttrs(maskAttr(a))
        return true
    })

    return h.Handler.Handle(ctx, newRecord)
}

func maskAttr(a slog.Attr) slog.Attr {
    // Для групп — рекурсивно
    if a.Value.Kind() == slog.KindGroup {
        attrs := a.Value.Group()
        masked := make([]slog.Attr, 0, len(attrs))
        for _, attr := range attrs {
            masked = append(masked, maskAttr(attr))
        }
        return slog.Group(a.Key, masked...)
    }

    // Маскируем по имени поля
    key := strings.ToLower(a.Key)

    // Полное скрытие
    fullMaskKeys := []string{
        "password", "secret", "token", "api_key", "apikey",
        "authorization", "bearer", "credential", "private",
    }
    for _, k := range fullMaskKeys {
        if strings.Contains(key, k) {
            return slog.String(a.Key, "[REDACTED]")
        }
    }

    // Строковые значения — проверяем содержимое
    if a.Value.Kind() == slog.KindString {
        value := a.Value.String()

        // Маскируем email
        if emailRegex.MatchString(value) {
            return slog.String(a.Key, maskEmail(value))
        }

        // Маскируем номера карт
        if cardRegex.MatchString(value) {
            return slog.String(a.Key, maskCard(value))
        }

        // Маскируем телефоны (но не port numbers и т.п.)
        if len(value) >= 10 && phoneRegex.MatchString(value) {
            return slog.String(a.Key, maskPhone(value))
        }
    }

    return a
}

func maskEmail(email string) string {
    parts := strings.Split(email, "@")
    if len(parts) != 2 {
        return "***@***"
    }
    name := parts[0]
    if len(name) <= 2 {
        return "**@" + parts[1]
    }
    return name[:2] + strings.Repeat("*", len(name)-2) + "@" + parts[1]
}

func maskCard(card string) string {
    digits := regexp.MustCompile(`[0-9]`).FindAllString(card, -1)
    if len(digits) < 4 {
        return "****"
    }
    return strings.Repeat("*", len(digits)-4) + strings.Join(digits[len(digits)-4:], "")
}

func maskPhone(phone string) string {
    digits := regexp.MustCompile(`[0-9]`).FindAllString(phone, -1)
    if len(digits) < 4 {
        return "****"
    }
    return strings.Repeat("*", len(digits)-4) + strings.Join(digits[len(digits)-4:], "")
}
```

### 3.5 Request ID и correlation

**Middleware для request ID**:

```go
package middleware

import (
    "context"
    "log/slog"
    "net/http"

    "github.com/google/uuid"
)

type contextKey string

const (
    RequestIDKey contextKey = "request_id"
    TraceIDKey   contextKey = "trace_id"
)

// RequestID добавляет request_id к каждому запросу
func RequestID(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Проверяем входящий header (от API Gateway, трассировки)
        requestID := r.Header.Get("X-Request-ID")
        if requestID == "" {
            requestID = uuid.New().String()
        }

        // Добавляем в context
        ctx := context.WithValue(r.Context(), RequestIDKey, requestID)

        // Добавляем в response header
        w.Header().Set("X-Request-ID", requestID)

        // Продолжаем цепочку
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

// GetRequestID извлекает request_id из context
func GetRequestID(ctx context.Context) string {
    if id, ok := ctx.Value(RequestIDKey).(string); ok {
        return id
    }
    return ""
}

// LoggerFromContext создаёт логгер с request_id
func LoggerFromContext(ctx context.Context) *slog.Logger {
    logger := slog.Default()

    if requestID := GetRequestID(ctx); requestID != "" {
        logger = logger.With("request_id", requestID)
    }

    if traceID, ok := ctx.Value(TraceIDKey).(string); ok && traceID != "" {
        logger = logger.With("trace_id", traceID)
    }

    return logger
}

// Logging middleware с structured logging
func Logging(logger *slog.Logger) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            start := time.Now()

            // Wrap ResponseWriter для получения status code
            ww := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}

            // Логгер с request context
            reqLogger := LoggerFromContext(r.Context())

            reqLogger.Info("request started",
                "method", r.Method,
                "path", r.URL.Path,
                "remote_addr", r.RemoteAddr,
                "user_agent", r.UserAgent(),
            )

            defer func() {
                reqLogger.Info("request completed",
                    "method", r.Method,
                    "path", r.URL.Path,
                    "status", ww.statusCode,
                    "duration_ms", time.Since(start).Milliseconds(),
                    "bytes", ww.bytesWritten,
                )
            }()

            next.ServeHTTP(ww, r)
        })
    }
}

type responseWriter struct {
    http.ResponseWriter
    statusCode   int
    bytesWritten int
}

func (w *responseWriter) WriteHeader(code int) {
    w.statusCode = code
    w.ResponseWriter.WriteHeader(code)
}

func (w *responseWriter) Write(b []byte) (int, error) {
    n, err := w.ResponseWriter.Write(b)
    w.bytesWritten += n
    return n, err
}
```

**Использование**:

```go
func main() {
    logger := logging.New(cfg)

    mux := http.NewServeMux()
    mux.HandleFunc("/users/{id}", getUserHandler)

    // Применяем middleware
    handler := middleware.RequestID(
        middleware.Logging(logger)(mux),
    )

    http.ListenAndServe(":8080", handler)
}

func getUserHandler(w http.ResponseWriter, r *http.Request) {
    // Получаем логгер с request_id
    logger := middleware.LoggerFromContext(r.Context())

    userID := r.PathValue("id")
    logger.Debug("fetching user", "user_id", userID)

    // ... бизнес-логика
}
```

**Пример вывода**:

```json
{"time":"2024-01-15T10:30:00Z","level":"info","msg":"request started","service":"user-service","request_id":"550e8400-e29b-41d4-a716-446655440000","method":"GET","path":"/users/123","remote_addr":"10.0.0.1:54321","user_agent":"curl/7.79.1"}
{"time":"2024-01-15T10:30:00Z","level":"debug","msg":"fetching user","service":"user-service","request_id":"550e8400-e29b-41d4-a716-446655440000","user_id":"123"}
{"time":"2024-01-15T10:30:00Z","level":"info","msg":"request completed","service":"user-service","request_id":"550e8400-e29b-41d4-a716-446655440000","method":"GET","path":"/users/123","status":200,"duration_ms":15,"bytes":256}
```

---

## 4. Metrics и Monitoring

### 4.1 RED metrics

**RED методология** — три главные метрики для любого сервиса:

| Метрика | Что измеряет | Prometheus тип |
|---------|--------------|----------------|
| **R**ate | Количество запросов в секунду | Counter |
| **E**rrors | Процент ошибок | Counter (вычисляется) |
| **D**uration | Время обработки | Histogram |

```
┌─────────────────────────────────────────────────────────────────┐
│                        RED METRICS                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Rate (RPS):                                                    │
│   ───────────                                                    │
│   • Сколько запросов обрабатывается                             │
│   • rate(http_requests_total[5m])                               │
│   • Alert: резкое падение = проблемы upstream                   │
│                                                                  │
│   Errors (%):                                                    │
│   ───────────                                                    │
│   • Какой процент запросов неуспешен                            │
│   • rate(http_requests_total{status=~"5.."}[5m]) /              │
│     rate(http_requests_total[5m])                               │
│   • Alert: > 1% = SLO под угрозой                               │
│                                                                  │
│   Duration (latency):                                            │
│   ───────────────────                                            │
│   • Как быстро обрабатываются запросы                           │
│   • histogram_quantile(0.99, http_request_duration_bucket)      │
│   • Alert: P99 > SLO = деградация                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Prometheus экспорт

**Базовая настройка**:

```go
package metrics

import (
    "net/http"
    "strconv"
    "time"

    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
    // RED: Rate
    httpRequestsTotal = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total number of HTTP requests",
        },
        []string{"method", "path", "status"},
    )

    // RED: Duration
    httpRequestDuration = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "http_request_duration_seconds",
            Help: "HTTP request duration in seconds",
            // Buckets для типичных latency API
            Buckets: []float64{.001, .005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10},
        },
        []string{"method", "path"},
    )

    // Дополнительно: размер ответа
    httpResponseSize = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "http_response_size_bytes",
            Help:    "HTTP response size in bytes",
            Buckets: prometheus.ExponentialBuckets(100, 10, 8), // 100, 1K, 10K, 100K...
        },
        []string{"method", "path"},
    )

    // Дополнительно: активные запросы
    httpRequestsInFlight = promauto.NewGauge(
        prometheus.GaugeOpts{
            Name: "http_requests_in_flight",
            Help: "Number of HTTP requests currently being processed",
        },
    )
)

// Handler возвращает handler для /metrics endpoint
func Handler() http.Handler {
    return promhttp.Handler()
}

// Middleware добавляет метрики к HTTP запросам
func Middleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Увеличиваем счётчик активных запросов
        httpRequestsInFlight.Inc()
        defer httpRequestsInFlight.Dec()

        start := time.Now()

        // Wrap ResponseWriter
        ww := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}

        // Обрабатываем запрос
        next.ServeHTTP(ww, r)

        // Записываем метрики
        duration := time.Since(start).Seconds()
        status := strconv.Itoa(ww.statusCode)
        path := normalizePath(r.URL.Path) // Нормализуем path

        httpRequestsTotal.WithLabelValues(r.Method, path, status).Inc()
        httpRequestDuration.WithLabelValues(r.Method, path).Observe(duration)
        httpResponseSize.WithLabelValues(r.Method, path).Observe(float64(ww.bytesWritten))
    })
}

// normalizePath заменяет динамические части пути на плейсхолдеры
// Это предотвращает cardinality explosion
func normalizePath(path string) string {
    // Пример: /users/123 -> /users/{id}
    // В реальности используйте router для получения pattern
    // или regexp для замены
    return path
}

type responseWriter struct {
    http.ResponseWriter
    statusCode   int
    bytesWritten int
}

func (w *responseWriter) WriteHeader(code int) {
    w.statusCode = code
    w.ResponseWriter.WriteHeader(code)
}

func (w *responseWriter) Write(b []byte) (int, error) {
    n, err := w.ResponseWriter.Write(b)
    w.bytesWritten += n
    return n, err
}
```

**Использование с chi router** (для нормализации путей):

```go
package main

import (
    "net/http"

    "github.com/go-chi/chi/v5"
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

// Middleware с нормализацией пути через chi
func MetricsMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        ww := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}

        next.ServeHTTP(ww, r)

        // chi RouteContext содержит pattern маршрута
        rctx := chi.RouteContext(r.Context())
        pattern := rctx.RoutePattern()
        if pattern == "" {
            pattern = "unknown"
        }

        duration := time.Since(start).Seconds()
        status := strconv.Itoa(ww.statusCode)

        httpRequestsTotal.WithLabelValues(r.Method, pattern, status).Inc()
        httpRequestDuration.WithLabelValues(r.Method, pattern).Observe(duration)
    })
}

func main() {
    r := chi.NewRouter()

    // Middleware
    r.Use(MetricsMiddleware)

    // Metrics endpoint на отдельном порту (рекомендуется)
    go func() {
        mux := http.NewServeMux()
        mux.Handle("/metrics", metrics.Handler())
        http.ListenAndServe(":9090", mux)
    }()

    // Application routes
    r.Get("/users/{id}", getUserHandler)
    r.Post("/users", createUserHandler)

    http.ListenAndServe(":8080", r)
}
```

### 4.3 Бизнес-метрики

**Примеры бизнес-метрик**:

```go
package metrics

import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    // Бизнес-метрики: пользователи
    usersRegistered = promauto.NewCounter(
        prometheus.CounterOpts{
            Name: "business_users_registered_total",
            Help: "Total number of registered users",
        },
    )

    usersActive = promauto.NewGauge(
        prometheus.GaugeOpts{
            Name: "business_users_active",
            Help: "Number of currently active users",
        },
    )

    // Бизнес-метрики: заказы
    ordersPlaced = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "business_orders_placed_total",
            Help: "Total number of orders placed",
        },
        []string{"status", "payment_method"},
    )

    orderValue = promauto.NewHistogram(
        prometheus.HistogramOpts{
            Name:    "business_order_value_dollars",
            Help:    "Order value in dollars",
            Buckets: []float64{10, 25, 50, 100, 250, 500, 1000, 2500, 5000},
        },
    )

    // Бизнес-метрики: внешние сервисы
    externalAPILatency = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "external_api_duration_seconds",
            Help:    "External API call duration",
            Buckets: []float64{.05, .1, .25, .5, 1, 2.5, 5, 10},
        },
        []string{"service", "endpoint"},
    )

    externalAPIErrors = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "external_api_errors_total",
            Help: "External API errors",
        },
        []string{"service", "endpoint", "error_type"},
    )
)

// RecordUserRegistered записывает регистрацию пользователя
func RecordUserRegistered() {
    usersRegistered.Inc()
}

// RecordOrder записывает заказ
func RecordOrder(status, paymentMethod string, value float64) {
    ordersPlaced.WithLabelValues(status, paymentMethod).Inc()
    orderValue.Observe(value)
}

// RecordExternalCall записывает вызов внешнего API
func RecordExternalCall(service, endpoint string, duration time.Duration, err error) {
    externalAPILatency.WithLabelValues(service, endpoint).Observe(duration.Seconds())
    if err != nil {
        errorType := classifyError(err)
        externalAPIErrors.WithLabelValues(service, endpoint, errorType).Inc()
    }
}

func classifyError(err error) string {
    // Классификация ошибок
    if errors.Is(err, context.DeadlineExceeded) {
        return "timeout"
    }
    if errors.Is(err, context.Canceled) {
        return "canceled"
    }
    return "unknown"
}
```

### 4.4 Alerting

**Prometheus alerting rules**:

```yaml
# prometheus/alerts.yml
groups:
  - name: http_alerts
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          /
          sum(rate(http_requests_total[5m]))
          > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High HTTP error rate"
          description: "Error rate is {{ $value | humanizePercentage }} (> 1%)"

      # High latency
      - alert: HighLatency
        expr: |
          histogram_quantile(0.99,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          ) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High P99 latency"
          description: "P99 latency is {{ $value | humanizeDuration }}"

      # No traffic (potential issue)
      - alert: NoTraffic
        expr: |
          sum(rate(http_requests_total[5m])) == 0
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "No HTTP traffic"
          description: "Service has received no requests for 10 minutes"

  - name: resource_alerts
    rules:
      # High memory usage
      - alert: HighMemoryUsage
        expr: |
          go_memstats_alloc_bytes / go_memstats_sys_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is above 90%"

      # Too many goroutines
      - alert: TooManyGoroutines
        expr: |
          go_goroutines > 10000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Too many goroutines"
          description: "{{ $value }} goroutines running"
```

---

## 5. Distributed Tracing

### 5.1 Когда tracing необходим

```
┌─────────────────────────────────────────────────────────────────┐
│                    КОГДА НУЖЕН TRACING                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ✅ НУЖЕН:                                                      │
│   • Микросервисная архитектура (> 3 сервисов)                   │
│   • Запрос проходит через несколько сервисов                    │
│   • Сложно понять, где "тормозит" запрос                        │
│   • Асинхронная обработка (очереди, события)                    │
│                                                                  │
│   ❌ НЕ НУЖЕН:                                                   │
│   • Монолит или 1-2 сервиса                                     │
│   • Простые CRUD API                                             │
│   • Достаточно request_id для correlation                       │
│                                                                  │
│   ⚠️ OVERHEAD:                                                   │
│   • CPU: 1-5% дополнительной нагрузки                           │
│   • Memory: буферы для spans                                     │
│   • Network: отправка spans в collector                         │
│   • Storage: хранение traces (может быть дорого)                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 OpenTelemetry setup

**Минимальная конфигурация**:

```go
package tracing

import (
    "context"
    "log/slog"

    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    "go.opentelemetry.io/otel/propagation"
    "go.opentelemetry.io/otel/sdk/resource"
    "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.24.0"
)

// Config конфигурация трейсинга
type Config struct {
    ServiceName    string  `env:"SERVICE_NAME" envDefault:"app"`
    ServiceVersion string  `env:"SERVICE_VERSION" envDefault:"unknown"`
    OTLPEndpoint   string  `env:"OTEL_EXPORTER_OTLP_ENDPOINT" envDefault:"localhost:4317"`
    SampleRate     float64 `env:"OTEL_SAMPLE_RATE" envDefault:"0.1"` // 10% по умолчанию
    Enabled        bool    `env:"OTEL_ENABLED" envDefault:"false"`
}

// Init инициализирует OpenTelemetry tracing
func Init(ctx context.Context, cfg Config) (func(context.Context) error, error) {
    if !cfg.Enabled {
        slog.Info("tracing disabled")
        return func(context.Context) error { return nil }, nil
    }

    // Создаём exporter
    exporter, err := otlptracegrpc.New(ctx,
        otlptracegrpc.WithEndpoint(cfg.OTLPEndpoint),
        otlptracegrpc.WithInsecure(), // Для локальной разработки
    )
    if err != nil {
        return nil, err
    }

    // Resource описывает сервис
    res, err := resource.Merge(
        resource.Default(),
        resource.NewWithAttributes(
            semconv.SchemaURL,
            semconv.ServiceName(cfg.ServiceName),
            semconv.ServiceVersion(cfg.ServiceVersion),
        ),
    )
    if err != nil {
        return nil, err
    }

    // Sampler — какой процент запросов трейсить
    var sampler trace.Sampler
    if cfg.SampleRate >= 1.0 {
        sampler = trace.AlwaysSample()
    } else if cfg.SampleRate <= 0 {
        sampler = trace.NeverSample()
    } else {
        sampler = trace.ParentBased(
            trace.TraceIDRatioBased(cfg.SampleRate),
        )
    }

    // Создаём TracerProvider
    tp := trace.NewTracerProvider(
        trace.WithBatcher(exporter),
        trace.WithResource(res),
        trace.WithSampler(sampler),
    )

    // Регистрируем глобально
    otel.SetTracerProvider(tp)

    // Propagation для передачи trace context между сервисами
    otel.SetTextMapPropagator(
        propagation.NewCompositeTextMapPropagator(
            propagation.TraceContext{}, // W3C Trace Context
            propagation.Baggage{},      // W3C Baggage
        ),
    )

    slog.Info("tracing initialized",
        "service", cfg.ServiceName,
        "endpoint", cfg.OTLPEndpoint,
        "sample_rate", cfg.SampleRate,
    )

    // Возвращаем shutdown функцию
    return tp.Shutdown, nil
}
```

**HTTP middleware**:

```go
package middleware

import (
    "net/http"

    "go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/trace"
)

// Tracing добавляет OpenTelemetry tracing к HTTP handlers
func Tracing(serviceName string) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        // otelhttp автоматически создаёт spans и propagates context
        return otelhttp.NewHandler(next, serviceName,
            otelhttp.WithSpanNameFormatter(func(operation string, r *http.Request) string {
                return r.Method + " " + r.URL.Path
            }),
        )
    }
}

// AddSpanAttributes добавляет атрибуты к текущему span
func AddSpanAttributes(ctx context.Context, attrs ...attribute.KeyValue) {
    span := trace.SpanFromContext(ctx)
    span.SetAttributes(attrs...)
}

// StartSpan создаёт новый span для операции
func StartSpan(ctx context.Context, name string, attrs ...attribute.KeyValue) (context.Context, trace.Span) {
    tracer := otel.Tracer("")
    ctx, span := tracer.Start(ctx, name)
    span.SetAttributes(attrs...)
    return ctx, span
}
```

**Использование в коде**:

```go
func getUserHandler(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()

    // Создаём span для database query
    ctx, span := middleware.StartSpan(ctx, "db.query",
        attribute.String("db.system", "postgresql"),
        attribute.String("db.operation", "SELECT"),
    )
    defer span.End()

    user, err := db.GetUser(ctx, userID)
    if err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, err.Error())
        // ...
    }

    // Добавляем атрибуты результата
    span.SetAttributes(
        attribute.Int64("user.id", user.ID),
        attribute.String("user.role", user.Role),
    )

    // ...
}
```

### 5.3 Sampling strategies

**Стратегии семплирования**:

| Стратегия | Когда использовать | Пример |
|-----------|-------------------|--------|
| **Always** | Development, debugging | 100% запросов |
| **Ratio** | Production (типично) | 1-10% запросов |
| **Parent-based** | Микросервисы | Следует решению родителя |
| **Rate-limiting** | High-traffic | Макс N spans/sec |

```go
// Разные sampler'ы
sampler := trace.ParentBased(
    // Root span: 10% трейсим
    trace.TraceIDRatioBased(0.1),
    // Если родитель трейсится — трейсим тоже
    trace.WithRemoteParentSampled(trace.AlwaysSample()),
    // Если родитель не трейсится — не трейсим
    trace.WithRemoteParentNotSampled(trace.NeverSample()),
)
```

**Рекомендации**:

```
┌─────────────────────────────────────────────────────────────────┐
│                  SAMPLING RECOMMENDATIONS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Development:                                                   │
│   • SampleRate: 1.0 (100%)                                      │
│   • Видим все traces для отладки                                │
│                                                                  │
│   Staging:                                                       │
│   • SampleRate: 0.5 (50%)                                       │
│   • Достаточно для тестирования                                 │
│                                                                  │
│   Production (low traffic, < 1000 RPS):                         │
│   • SampleRate: 0.1 (10%)                                       │
│   • Баланс между visibility и cost                              │
│                                                                  │
│   Production (high traffic, > 10000 RPS):                       │
│   • SampleRate: 0.01 (1%)                                       │
│   • Или rate-limiting sampler                                   │
│                                                                  │
│   ВАЖНО:                                                         │
│   • Всегда трейсить errors (error sampling)                     │
│   • Head-based vs Tail-based sampling                           │
│   • Storage costs растут линейно с sample rate                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Resilience Patterns

### 6.1 Rate Limiting

**Rate limiting** защищает сервис от перегрузки.

> **Для C# разработчиков**: В ASP.NET Core есть `Microsoft.AspNetCore.RateLimiting`. В Go используем `golang.org/x/time/rate` — стандартную библиотеку.

**Token Bucket алгоритм**:

```go
package ratelimit

import (
    "net/http"
    "sync"

    "golang.org/x/time/rate"
)

// Limiter ограничивает количество запросов
type Limiter struct {
    // Global limiter
    global *rate.Limiter

    // Per-IP limiters
    ips     map[string]*rate.Limiter
    mu      sync.RWMutex
    rps     rate.Limit
    burst   int
}

// New создаёт новый rate limiter
// rps — requests per second, burst — maximum burst size
func New(rps float64, burst int) *Limiter {
    return &Limiter{
        global: rate.NewLimiter(rate.Limit(rps*10), burst*10), // Global limit
        ips:    make(map[string]*rate.Limiter),
        rps:    rate.Limit(rps),
        burst:  burst,
    }
}

// getLimiter возвращает limiter для IP
func (l *Limiter) getLimiter(ip string) *rate.Limiter {
    l.mu.RLock()
    limiter, exists := l.ips[ip]
    l.mu.RUnlock()

    if exists {
        return limiter
    }

    l.mu.Lock()
    defer l.mu.Unlock()

    // Double-check после получения write lock
    if limiter, exists = l.ips[ip]; exists {
        return limiter
    }

    limiter = rate.NewLimiter(l.rps, l.burst)
    l.ips[ip] = limiter
    return limiter
}

// Allow проверяет, разрешён ли запрос
func (l *Limiter) Allow(ip string) bool {
    // Проверяем global limit
    if !l.global.Allow() {
        return false
    }

    // Проверяем per-IP limit
    return l.getLimiter(ip).Allow()
}

// Middleware создаёт HTTP middleware для rate limiting
func (l *Limiter) Middleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        ip := getIP(r)

        if !l.Allow(ip) {
            w.Header().Set("Retry-After", "1")
            http.Error(w, "Too Many Requests", http.StatusTooManyRequests)
            return
        }

        next.ServeHTTP(w, r)
    })
}

func getIP(r *http.Request) string {
    // Проверяем X-Forwarded-For (за reverse proxy)
    if xff := r.Header.Get("X-Forwarded-For"); xff != "" {
        // Берём первый IP (клиентский)
        if idx := strings.Index(xff, ","); idx != -1 {
            return strings.TrimSpace(xff[:idx])
        }
        return strings.TrimSpace(xff)
    }

    // X-Real-IP
    if xri := r.Header.Get("X-Real-IP"); xri != "" {
        return xri
    }

    // Fallback: RemoteAddr
    ip, _, _ := net.SplitHostPort(r.RemoteAddr)
    return ip
}
```

**Использование**:

```go
func main() {
    // 100 RPS per IP, burst 10
    limiter := ratelimit.New(100, 10)

    mux := http.NewServeMux()
    mux.HandleFunc("/api/", apiHandler)

    // Применяем rate limiting
    handler := limiter.Middleware(mux)

    http.ListenAndServe(":8080", handler)
}
```

**Сравнение с C#**:

```csharp
// C#: Microsoft.AspNetCore.RateLimiting
builder.Services.AddRateLimiter(options =>
{
    options.AddFixedWindowLimiter("fixed", config =>
    {
        config.PermitLimit = 100;
        config.Window = TimeSpan.FromSeconds(1);
        config.QueueLimit = 0;
    });
});

app.UseRateLimiter();

app.MapGet("/api", () => "Hello")
    .RequireRateLimiting("fixed");
```

### 6.2 Circuit Breaker

**Circuit Breaker** защищает от каскадных сбоев.

```
┌─────────────────────────────────────────────────────────────────┐
│                   CIRCUIT BREAKER STATES                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   CLOSED (нормальное состояние)                                  │
│   ├── Запросы проходят нормально                                │
│   ├── Считаем ошибки                                            │
│   └── При превышении порога → OPEN                              │
│                                                                  │
│   OPEN (защита активна)                                          │
│   ├── Все запросы отклоняются сразу                             │
│   ├── Не нагружаем падающий сервис                              │
│   └── После таймаута → HALF-OPEN                                 │
│                                                                  │
│   HALF-OPEN (проверка)                                           │
│   ├── Пропускаем несколько запросов                             │
│   ├── Если успех → CLOSED                                        │
│   └── Если ошибка → OPEN                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Реализация с sony/gobreaker**:

```go
package resilience

import (
    "context"
    "errors"
    "net/http"
    "time"

    "github.com/sony/gobreaker/v2"
)

var (
    ErrCircuitOpen = errors.New("circuit breaker is open")
)

// HTTPClient с circuit breaker
type HTTPClient struct {
    client  *http.Client
    breaker *gobreaker.CircuitBreaker[*http.Response]
}

// NewHTTPClient создаёт HTTP клиент с circuit breaker
func NewHTTPClient(name string) *HTTPClient {
    settings := gobreaker.Settings{
        Name:        name,
        MaxRequests: 5, // Запросов в half-open для проверки
        Interval:    10 * time.Second, // Интервал сброса счётчиков
        Timeout:     30 * time.Second, // Время в open перед переходом в half-open

        // Когда открывать circuit
        ReadyToTrip: func(counts gobreaker.Counts) bool {
            // Открываем после 5 последовательных ошибок
            // ИЛИ если > 50% запросов неуспешны (минимум 10 запросов)
            if counts.ConsecutiveFailures >= 5 {
                return true
            }
            if counts.Requests >= 10 {
                failureRatio := float64(counts.TotalFailures) / float64(counts.Requests)
                return failureRatio > 0.5
            }
            return false
        },

        // Callback при смене состояния
        OnStateChange: func(name string, from, to gobreaker.State) {
            slog.Warn("circuit breaker state changed",
                "name", name,
                "from", from.String(),
                "to", to.String(),
            )
        },

        // Что считать успехом
        IsSuccessful: func(err error) bool {
            if err == nil {
                return true
            }
            // Некоторые ошибки не должны влиять на circuit
            // (например, 4xx клиентские ошибки)
            return false
        },
    }

    return &HTTPClient{
        client:  &http.Client{Timeout: 10 * time.Second},
        breaker: gobreaker.NewCircuitBreaker[*http.Response](settings),
    }
}

// Do выполняет HTTP запрос через circuit breaker
func (c *HTTPClient) Do(req *http.Request) (*http.Response, error) {
    resp, err := c.breaker.Execute(func() (*http.Response, error) {
        resp, err := c.client.Do(req)
        if err != nil {
            return nil, err
        }

        // 5xx считаем ошибкой для circuit breaker
        if resp.StatusCode >= 500 {
            return resp, errors.New("server error")
        }

        return resp, nil
    })

    if err != nil {
        if errors.Is(err, gobreaker.ErrOpenState) {
            return nil, ErrCircuitOpen
        }
        return nil, err
    }

    return resp, nil
}

// State возвращает текущее состояние circuit breaker
func (c *HTTPClient) State() gobreaker.State {
    return c.breaker.State()
}
```

**Использование**:

```go
// Создаём клиент для каждого внешнего сервиса
var (
    paymentClient = resilience.NewHTTPClient("payment-service")
    emailClient   = resilience.NewHTTPClient("email-service")
)

func processPayment(ctx context.Context, orderID string) error {
    req, _ := http.NewRequestWithContext(ctx, "POST",
        "https://payment.example.com/charge",
        bytes.NewReader(payload))

    resp, err := paymentClient.Do(req)
    if err != nil {
        if errors.Is(err, resilience.ErrCircuitOpen) {
            // Circuit открыт — используем fallback
            return enqueueForRetry(orderID)
        }
        return err
    }
    defer resp.Body.Close()

    // ...
}
```

### 6.3 Retry с Exponential Backoff

**Retry** — повторные попытки при временных сбоях.

```go
package resilience

import (
    "context"
    "math"
    "math/rand"
    "time"
)

// RetryConfig конфигурация retry
type RetryConfig struct {
    MaxAttempts int           // Максимум попыток
    InitialWait time.Duration // Начальная задержка
    MaxWait     time.Duration // Максимальная задержка
    Multiplier  float64       // Множитель для backoff
    Jitter      float64       // Случайный разброс (0-1)
}

// DefaultRetryConfig возвращает стандартную конфигурацию
func DefaultRetryConfig() RetryConfig {
    return RetryConfig{
        MaxAttempts: 3,
        InitialWait: 100 * time.Millisecond,
        MaxWait:     10 * time.Second,
        Multiplier:  2.0,
        Jitter:      0.1,
    }
}

// RetryableFunc функция, которую можно повторять
type RetryableFunc func(ctx context.Context) error

// IsRetryable определяет, нужно ли повторять
type IsRetryable func(error) bool

// Retry выполняет функцию с повторными попытками
func Retry(ctx context.Context, cfg RetryConfig, isRetryable IsRetryable, fn RetryableFunc) error {
    var lastErr error

    for attempt := 1; attempt <= cfg.MaxAttempts; attempt++ {
        // Проверяем context
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
        }

        // Выполняем функцию
        err := fn(ctx)
        if err == nil {
            return nil // Успех
        }

        lastErr = err

        // Проверяем, нужно ли повторять
        if !isRetryable(err) {
            return err // Не retriable ошибка
        }

        // Последняя попытка — не ждём
        if attempt == cfg.MaxAttempts {
            break
        }

        // Вычисляем задержку с exponential backoff + jitter
        wait := calculateBackoff(cfg, attempt)

        slog.Debug("retrying after error",
            "attempt", attempt,
            "max_attempts", cfg.MaxAttempts,
            "wait", wait,
            "error", err,
        )

        // Ждём или отменяем
        select {
        case <-ctx.Done():
            return ctx.Err()
        case <-time.After(wait):
        }
    }

    return lastErr
}

func calculateBackoff(cfg RetryConfig, attempt int) time.Duration {
    // Exponential: initialWait * multiplier^(attempt-1)
    wait := float64(cfg.InitialWait) * math.Pow(cfg.Multiplier, float64(attempt-1))

    // Ограничиваем максимумом
    if wait > float64(cfg.MaxWait) {
        wait = float64(cfg.MaxWait)
    }

    // Добавляем jitter
    if cfg.Jitter > 0 {
        jitter := wait * cfg.Jitter * (rand.Float64()*2 - 1) // -jitter to +jitter
        wait += jitter
    }

    return time.Duration(wait)
}

// DefaultIsRetryable — стандартная проверка retriable ошибок
func DefaultIsRetryable(err error) bool {
    // Временные ошибки
    if errors.Is(err, context.DeadlineExceeded) {
        return true
    }

    // Network ошибки обычно временные
    var netErr net.Error
    if errors.As(err, &netErr) && netErr.Temporary() {
        return true
    }

    // HTTP 5xx и 429 (rate limit)
    var httpErr *HTTPError
    if errors.As(err, &httpErr) {
        return httpErr.StatusCode >= 500 || httpErr.StatusCode == 429
    }

    return false
}

// HTTPError ошибка HTTP запроса
type HTTPError struct {
    StatusCode int
    Message    string
}

func (e *HTTPError) Error() string {
    return fmt.Sprintf("HTTP %d: %s", e.StatusCode, e.Message)
}
```

**Использование**:

```go
func fetchUser(ctx context.Context, userID string) (*User, error) {
    var user *User

    err := resilience.Retry(ctx,
        resilience.DefaultRetryConfig(),
        resilience.DefaultIsRetryable,
        func(ctx context.Context) error {
            resp, err := httpClient.Get(ctx, "/users/"+userID)
            if err != nil {
                return err
            }
            user = resp
            return nil
        },
    )

    return user, err
}
```

### 6.4 Timeouts и Deadlines

**Timeouts** на всех уровнях:

```go
package main

import (
    "context"
    "database/sql"
    "net/http"
    "time"
)

// Timeouts configuration
type Timeouts struct {
    // HTTP Server
    ServerRead  time.Duration `env:"SERVER_READ_TIMEOUT" envDefault:"5s"`
    ServerWrite time.Duration `env:"SERVER_WRITE_TIMEOUT" envDefault:"10s"`
    ServerIdle  time.Duration `env:"SERVER_IDLE_TIMEOUT" envDefault:"120s"`

    // HTTP Client
    ClientRequest time.Duration `env:"CLIENT_REQUEST_TIMEOUT" envDefault:"30s"`
    ClientDial    time.Duration `env:"CLIENT_DIAL_TIMEOUT" envDefault:"5s"`

    // Database
    DBConnect time.Duration `env:"DB_CONNECT_TIMEOUT" envDefault:"5s"`
    DBQuery   time.Duration `env:"DB_QUERY_TIMEOUT" envDefault:"30s"`

    // External services
    ExternalAPI time.Duration `env:"EXTERNAL_API_TIMEOUT" envDefault:"10s"`
}

func setupHTTPServer(cfg Timeouts) *http.Server {
    return &http.Server{
        ReadTimeout:       cfg.ServerRead,
        ReadHeaderTimeout: cfg.ServerRead,
        WriteTimeout:      cfg.ServerWrite,
        IdleTimeout:       cfg.ServerIdle,
    }
}

func setupHTTPClient(cfg Timeouts) *http.Client {
    return &http.Client{
        Timeout: cfg.ClientRequest,
        Transport: &http.Transport{
            DialContext: (&net.Dialer{
                Timeout:   cfg.ClientDial,
                KeepAlive: 30 * time.Second,
            }).DialContext,
            TLSHandshakeTimeout:   10 * time.Second,
            ResponseHeaderTimeout: cfg.ClientRequest,
            ExpectContinueTimeout: 1 * time.Second,
            MaxIdleConns:          100,
            MaxIdleConnsPerHost:   10,
            IdleConnTimeout:       90 * time.Second,
        },
    }
}

func setupDatabase(cfg Timeouts, dsn string) (*sql.DB, error) {
    db, err := sql.Open("postgres", dsn)
    if err != nil {
        return nil, err
    }

    // Connection pool settings
    db.SetMaxOpenConns(25)
    db.SetMaxIdleConns(5)
    db.SetConnMaxLifetime(5 * time.Minute)
    db.SetConnMaxIdleTime(1 * time.Minute)

    // Проверяем подключение с таймаутом
    ctx, cancel := context.WithTimeout(context.Background(), cfg.DBConnect)
    defer cancel()

    if err := db.PingContext(ctx); err != nil {
        return nil, fmt.Errorf("database ping: %w", err)
    }

    return db, nil
}

// Запрос к БД с таймаутом
func getUser(ctx context.Context, db *sql.DB, cfg Timeouts, id int64) (*User, error) {
    // Создаём context с таймаутом
    ctx, cancel := context.WithTimeout(ctx, cfg.DBQuery)
    defer cancel()

    var user User
    err := db.QueryRowContext(ctx,
        "SELECT id, name, email FROM users WHERE id = $1", id,
    ).Scan(&user.ID, &user.Name, &user.Email)

    if err != nil {
        return nil, err
    }
    return &user, nil
}
```

### 6.5 Bulkhead pattern

**Bulkhead** (отсеки) изолирует компоненты друг от друга.

```go
package resilience

import (
    "context"
    "errors"

    "golang.org/x/sync/semaphore"
)

var ErrBulkheadFull = errors.New("bulkhead is full")

// Bulkhead ограничивает concurrency
type Bulkhead struct {
    sem     *semaphore.Weighted
    maxSize int64
}

// NewBulkhead создаёт bulkhead с указанным размером
func NewBulkhead(maxConcurrent int64) *Bulkhead {
    return &Bulkhead{
        sem:     semaphore.NewWeighted(maxConcurrent),
        maxSize: maxConcurrent,
    }
}

// Execute выполняет функцию в bulkhead
func (b *Bulkhead) Execute(ctx context.Context, fn func() error) error {
    // Пытаемся захватить slot
    if err := b.sem.Acquire(ctx, 1); err != nil {
        return err
    }
    defer b.sem.Release(1)

    return fn()
}

// TryExecute пытается выполнить без ожидания
func (b *Bulkhead) TryExecute(fn func() error) error {
    if !b.sem.TryAcquire(1) {
        return ErrBulkheadFull
    }
    defer b.sem.Release(1)

    return fn()
}
```

**Использование для изоляции внешних сервисов**:

```go
var (
    // Разные bulkhead'ы для разных сервисов
    paymentBulkhead = resilience.NewBulkhead(10) // Макс 10 concurrent запросов
    emailBulkhead   = resilience.NewBulkhead(5)  // Макс 5 concurrent запросов
    searchBulkhead  = resilience.NewBulkhead(20) // Макс 20 concurrent запросов
)

func chargePayment(ctx context.Context, amount float64) error {
    return paymentBulkhead.Execute(ctx, func() error {
        // Запрос к payment service
        return paymentClient.Charge(ctx, amount)
    })
}

func sendEmail(ctx context.Context, to, subject, body string) error {
    // Без ожидания — если bulkhead полон, сразу ошибка
    err := emailBulkhead.TryExecute(func() error {
        return emailClient.Send(ctx, to, subject, body)
    })

    if errors.Is(err, resilience.ErrBulkheadFull) {
        // Fallback: ставим в очередь
        return enqueueEmail(to, subject, body)
    }
    return err
}
```

**Сравнение с C# Polly**:

```csharp
// C#: Polly Bulkhead
var bulkhead = Policy.Bulkhead(
    maxParallelization: 10,
    maxQueuingActions: 20
);

await bulkhead.ExecuteAsync(async () =>
{
    await paymentService.ChargeAsync(amount);
});
```

```go
// Go: простой и явный подход с semaphore
bulkhead := resilience.NewBulkhead(10)

err := bulkhead.Execute(ctx, func() error {
    return paymentService.Charge(ctx, amount)
})
```

---

## 7. Error Handling в Production

### 7.1 Классификация ошибок

**Классификация по типу реакции**:

| Тип | Описание | Действие | Пример |
|-----|----------|----------|--------|
| **Operational** | Ожидаемые ошибки | Graceful handling | Not found, validation error |
| **Transient** | Временные сбои | Retry | Network timeout, DB connection |
| **Fatal** | Критические | Shutdown | Config missing, panic |
| **Bug** | Ошибки в коде | Log + fix | Nil pointer, index out of range |

```go
package apperror

import (
    "errors"
    "net/http"
)

// ErrorType тип ошибки
type ErrorType string

const (
    ErrorTypeValidation   ErrorType = "VALIDATION"
    ErrorTypeNotFound     ErrorType = "NOT_FOUND"
    ErrorTypeConflict     ErrorType = "CONFLICT"
    ErrorTypeUnauthorized ErrorType = "UNAUTHORIZED"
    ErrorTypeForbidden    ErrorType = "FORBIDDEN"
    ErrorTypeInternal     ErrorType = "INTERNAL"
    ErrorTypeUnavailable  ErrorType = "UNAVAILABLE"
)

// AppError структурированная ошибка приложения
type AppError struct {
    Type       ErrorType `json:"type"`
    Message    string    `json:"message"`
    Detail     string    `json:"detail,omitempty"`
    Field      string    `json:"field,omitempty"`      // Для validation errors
    Code       string    `json:"code,omitempty"`       // Внутренний код ошибки
    StatusCode int       `json:"-"`                    // HTTP status code
    Err        error     `json:"-"`                    // Wrapped error
}

func (e *AppError) Error() string {
    if e.Err != nil {
        return e.Message + ": " + e.Err.Error()
    }
    return e.Message
}

func (e *AppError) Unwrap() error {
    return e.Err
}

// Конструкторы для типичных ошибок
func ValidationError(field, message string) *AppError {
    return &AppError{
        Type:       ErrorTypeValidation,
        Message:    "Validation failed",
        Detail:     message,
        Field:      field,
        StatusCode: http.StatusBadRequest,
    }
}

func NotFoundError(resource string) *AppError {
    return &AppError{
        Type:       ErrorTypeNotFound,
        Message:    resource + " not found",
        StatusCode: http.StatusNotFound,
    }
}

func ConflictError(message string) *AppError {
    return &AppError{
        Type:       ErrorTypeConflict,
        Message:    message,
        StatusCode: http.StatusConflict,
    }
}

func UnauthorizedError() *AppError {
    return &AppError{
        Type:       ErrorTypeUnauthorized,
        Message:    "Authentication required",
        StatusCode: http.StatusUnauthorized,
    }
}

func ForbiddenError() *AppError {
    return &AppError{
        Type:       ErrorTypeForbidden,
        Message:    "Access denied",
        StatusCode: http.StatusForbidden,
    }
}

func InternalError(err error) *AppError {
    return &AppError{
        Type:       ErrorTypeInternal,
        Message:    "Internal server error",
        StatusCode: http.StatusInternalServerError,
        Err:        err,
    }
}

func UnavailableError(service string, err error) *AppError {
    return &AppError{
        Type:       ErrorTypeUnavailable,
        Message:    service + " is temporarily unavailable",
        StatusCode: http.StatusServiceUnavailable,
        Err:        err,
    }
}

// IsRetryable определяет, можно ли повторить запрос
func (e *AppError) IsRetryable() bool {
    return e.Type == ErrorTypeUnavailable
}
```

### 7.2 RFC 7807 Problem Details

**Problem Details** — стандартный формат ошибок HTTP API.

```go
package apperror

import (
    "encoding/json"
    "net/http"
)

// ProblemDetails RFC 7807 Problem Details
type ProblemDetails struct {
    Type     string `json:"type"`               // URI идентифицирующий тип ошибки
    Title    string `json:"title"`              // Краткое описание
    Status   int    `json:"status"`             // HTTP status code
    Detail   string `json:"detail,omitempty"`   // Детальное описание
    Instance string `json:"instance,omitempty"` // URI конкретного случая ошибки

    // Extensions
    Code   string            `json:"code,omitempty"`   // Код ошибки
    Errors []ValidationError `json:"errors,omitempty"` // Для validation errors
}

type ValidationError struct {
    Field   string `json:"field"`
    Message string `json:"message"`
}

// ToProblemDetails конвертирует AppError в ProblemDetails
func ToProblemDetails(err *AppError, requestID string) ProblemDetails {
    pd := ProblemDetails{
        Type:     "https://api.example.com/errors/" + string(err.Type),
        Title:    err.Message,
        Status:   err.StatusCode,
        Detail:   err.Detail,
        Code:     err.Code,
    }

    if requestID != "" {
        pd.Instance = "/errors/" + requestID
    }

    return pd
}

// ErrorHandler middleware для обработки ошибок
func ErrorHandler(logger *slog.Logger) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            // Создаём custom ResponseWriter для перехвата ошибок
            ww := &errorResponseWriter{
                ResponseWriter: w,
                request:        r,
                logger:         logger,
            }

            next.ServeHTTP(ww, r)
        })
    }
}

// WriteError записывает ошибку в response
func WriteError(w http.ResponseWriter, r *http.Request, err error, logger *slog.Logger) {
    var appErr *AppError
    if !errors.As(err, &appErr) {
        // Неизвестная ошибка — internal error
        appErr = InternalError(err)
    }

    requestID := middleware.GetRequestID(r.Context())

    // Логируем
    logLevel := slog.LevelWarn
    if appErr.StatusCode >= 500 {
        logLevel = slog.LevelError
    }

    logger.Log(r.Context(), logLevel, "request error",
        "error_type", appErr.Type,
        "status", appErr.StatusCode,
        "message", appErr.Message,
        "request_id", requestID,
        "path", r.URL.Path,
        "method", r.Method,
        "error", appErr.Err,
    )

    // Формируем response
    pd := ToProblemDetails(appErr, requestID)

    w.Header().Set("Content-Type", "application/problem+json")
    w.WriteHeader(appErr.StatusCode)
    json.NewEncoder(w).Encode(pd)
}
```

**Пример ответа**:

```json
{
  "type": "https://api.example.com/errors/VALIDATION",
  "title": "Validation failed",
  "status": 400,
  "detail": "Email format is invalid",
  "instance": "/errors/550e8400-e29b-41d4-a716-446655440000",
  "code": "INVALID_EMAIL",
  "errors": [
    {"field": "email", "message": "must be a valid email address"}
  ]
}
```

### 7.3 Panic recovery

**Recovery middleware**:

```go
package middleware

import (
    "log/slog"
    "net/http"
    "runtime/debug"
)

// Recovery middleware восстанавливается после panic
func Recovery(logger *slog.Logger) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            defer func() {
                if err := recover(); err != nil {
                    // Получаем stack trace
                    stack := debug.Stack()

                    // Логируем panic
                    logger.Error("panic recovered",
                        "error", err,
                        "stack", string(stack),
                        "path", r.URL.Path,
                        "method", r.Method,
                        "request_id", GetRequestID(r.Context()),
                    )

                    // Отправляем 500 клиенту
                    w.Header().Set("Content-Type", "application/problem+json")
                    w.WriteHeader(http.StatusInternalServerError)
                    w.Write([]byte(`{"type":"INTERNAL","title":"Internal server error","status":500}`))
                }
            }()

            next.ServeHTTP(w, r)
        })
    }
}
```

### 7.4 Error tracking

**Интеграция с Sentry**:

```go
package errortracking

import (
    "context"
    "time"

    "github.com/getsentry/sentry-go"
)

// Config конфигурация error tracking
type Config struct {
    DSN         string  `env:"SENTRY_DSN"`
    Environment string  `env:"ENVIRONMENT" envDefault:"development"`
    Release     string  `env:"RELEASE" envDefault:"unknown"`
    SampleRate  float64 `env:"SENTRY_SAMPLE_RATE" envDefault:"1.0"`
}

// Init инициализирует Sentry
func Init(cfg Config) error {
    if cfg.DSN == "" {
        return nil // Sentry отключен
    }

    return sentry.Init(sentry.ClientOptions{
        Dsn:              cfg.DSN,
        Environment:      cfg.Environment,
        Release:          cfg.Release,
        SampleRate:       cfg.SampleRate,
        AttachStacktrace: true,
        BeforeSend: func(event *sentry.Event, hint *sentry.EventHint) *sentry.Event {
            // Фильтруем или модифицируем события
            // Например, убираем sensitive data
            return event
        },
    })
}

// Flush отправляет все события перед shutdown
func Flush(timeout time.Duration) {
    sentry.Flush(timeout)
}

// CaptureError отправляет ошибку в Sentry
func CaptureError(ctx context.Context, err error) {
    hub := sentry.GetHubFromContext(ctx)
    if hub == nil {
        hub = sentry.CurrentHub().Clone()
    }

    hub.CaptureException(err)
}

// Middleware добавляет Sentry hub в context
func Middleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        hub := sentry.CurrentHub().Clone()
        hub.Scope().SetRequest(r)

        ctx := sentry.SetHubOnContext(r.Context(), hub)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

---

## 8. Configuration

### 8.1 12-Factor App

**Принципы конфигурации 12-Factor App**:

```
┌─────────────────────────────────────────────────────────────────┐
│               12-FACTOR APP: CONFIGURATION                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   III. Config — храни конфигурацию в окружении                  │
│   ─────────────────────────────────────────────────────────────  │
│                                                                  │
│   ✅ DO:                                                         │
│   • Используй environment variables                              │
│   • Разделяй config от code                                     │
│   • Одна кодовая база → разные окружения                        │
│   • Fail fast при невалидном конфиге                            │
│                                                                  │
│   ❌ DON'T:                                                      │
│   • Хардкодить значения                                         │
│   • Хранить secrets в коде/git                                  │
│   • Использовать config files в production                      │
│   • Допускать разный код для разных окружений                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Environment variables

**Рекомендуемый подход с env**:

```go
package config

import (
    "fmt"
    "time"

    "github.com/caarlos0/env/v10"
    "github.com/go-playground/validator/v10"
)

// Config корневая конфигурация приложения
type Config struct {
    App      AppConfig      `envPrefix:"APP_"`
    Server   ServerConfig   `envPrefix:"SERVER_"`
    Database DatabaseConfig `envPrefix:"DB_"`
    Redis    RedisConfig    `envPrefix:"REDIS_"`
    Logging  LoggingConfig  `envPrefix:"LOG_"`
    Tracing  TracingConfig  `envPrefix:"OTEL_"`
}

type AppConfig struct {
    Name        string `env:"NAME" envDefault:"myapp" validate:"required"`
    Environment string `env:"ENV" envDefault:"development" validate:"oneof=development staging production"`
    Version     string `env:"VERSION" envDefault:"unknown"`
    Debug       bool   `env:"DEBUG" envDefault:"false"`
}

type ServerConfig struct {
    Host            string        `env:"HOST" envDefault:"0.0.0.0"`
    Port            int           `env:"PORT" envDefault:"8080" validate:"min=1,max=65535"`
    ReadTimeout     time.Duration `env:"READ_TIMEOUT" envDefault:"5s"`
    WriteTimeout    time.Duration `env:"WRITE_TIMEOUT" envDefault:"10s"`
    ShutdownTimeout time.Duration `env:"SHUTDOWN_TIMEOUT" envDefault:"30s"`
}

type DatabaseConfig struct {
    Host            string        `env:"HOST" envDefault:"localhost" validate:"required"`
    Port            int           `env:"PORT" envDefault:"5432" validate:"min=1,max=65535"`
    User            string        `env:"USER" envDefault:"postgres" validate:"required"`
    Password        string        `env:"PASSWORD" validate:"required"` // No default!
    Name            string        `env:"NAME" envDefault:"app" validate:"required"`
    SSLMode         string        `env:"SSL_MODE" envDefault:"disable" validate:"oneof=disable require verify-ca verify-full"`
    MaxOpenConns    int           `env:"MAX_OPEN_CONNS" envDefault:"25"`
    MaxIdleConns    int           `env:"MAX_IDLE_CONNS" envDefault:"5"`
    ConnMaxLifetime time.Duration `env:"CONN_MAX_LIFETIME" envDefault:"5m"`
}

func (c DatabaseConfig) DSN() string {
    return fmt.Sprintf(
        "host=%s port=%d user=%s password=%s dbname=%s sslmode=%s",
        c.Host, c.Port, c.User, c.Password, c.Name, c.SSLMode,
    )
}

type RedisConfig struct {
    Host     string `env:"HOST" envDefault:"localhost"`
    Port     int    `env:"PORT" envDefault:"6379"`
    Password string `env:"PASSWORD"`
    DB       int    `env:"DB" envDefault:"0"`
}

func (c RedisConfig) Addr() string {
    return fmt.Sprintf("%s:%d", c.Host, c.Port)
}

type LoggingConfig struct {
    Level     string `env:"LEVEL" envDefault:"info" validate:"oneof=debug info warn error"`
    Format    string `env:"FORMAT" envDefault:"json" validate:"oneof=json text"`
    AddSource bool   `env:"ADD_SOURCE" envDefault:"false"`
}

type TracingConfig struct {
    Enabled    bool    `env:"ENABLED" envDefault:"false"`
    Endpoint   string  `env:"EXPORTER_OTLP_ENDPOINT" envDefault:"localhost:4317"`
    SampleRate float64 `env:"SAMPLE_RATE" envDefault:"0.1" validate:"min=0,max=1"`
}

// Load загружает конфигурацию из environment variables
func Load() (*Config, error) {
    var cfg Config

    // Парсим environment variables
    if err := env.Parse(&cfg); err != nil {
        return nil, fmt.Errorf("parse config: %w", err)
    }

    // Валидируем
    validate := validator.New()
    if err := validate.Struct(&cfg); err != nil {
        return nil, fmt.Errorf("validate config: %w", err)
    }

    return &cfg, nil
}

// MustLoad загружает конфигурацию или паникует
func MustLoad() *Config {
    cfg, err := Load()
    if err != nil {
        panic(fmt.Sprintf("failed to load config: %v", err))
    }
    return cfg
}
```

**Использование**:

```go
func main() {
    // Fail fast при невалидном конфиге
    cfg := config.MustLoad()

    // Используем конфиг
    logger := logging.New(cfg.Logging)
    db, err := database.Connect(cfg.Database.DSN())
    // ...
}
```

### 8.3 Secrets management

**Принципы работы с secrets**:

```
┌─────────────────────────────────────────────────────────────────┐
│                   SECRETS MANAGEMENT                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ❌ НЕ ДЕЛАТЬ:                                                  │
│   • Хранить secrets в коде                                      │
│   • Хранить secrets в git (даже в .env файлах)                  │
│   • Логировать secrets                                          │
│   • Передавать secrets в URL parameters                         │
│                                                                  │
│   ✅ ДЕЛАТЬ:                                                     │
│   • Environment variables (для простых случаев)                 │
│   • Kubernetes Secrets                                           │
│   • HashiCorp Vault / AWS Secrets Manager / GCP Secret Manager  │
│   • Sidecar injection (Vault Agent, External Secrets Operator)  │
│                                                                  │
│   KUBERNETES:                                                    │
│   • Secret → env var или volume mount                           │
│   • External Secrets Operator для sync с Vault/AWS/GCP          │
│   • Sealed Secrets для GitOps                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Kubernetes Secret как env var**:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secrets
type: Opaque
stringData:
  DB_PASSWORD: "super-secret-password"
  API_KEY: "sk-1234567890"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
        - name: app
          envFrom:
            - secretRef:
                name: myapp-secrets
          env:
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: myapp-secrets
                  key: DB_PASSWORD
```

### 8.4 Fail fast validation

**Валидация при старте**:

```go
package config

import (
    "context"
    "database/sql"
    "fmt"
    "net"
    "time"
)

// Validator валидирует конфигурацию
type Validator struct {
    cfg    *Config
    errors []error
}

// NewValidator создаёт валидатор
func NewValidator(cfg *Config) *Validator {
    return &Validator{cfg: cfg}
}

// Validate выполняет все проверки
func (v *Validator) Validate(ctx context.Context) error {
    // Проверяем подключение к БД
    v.validateDatabase(ctx)

    // Проверяем Redis
    v.validateRedis(ctx)

    // Проверяем внешние сервисы (опционально)
    if v.cfg.App.Environment == "production" {
        v.validateExternalServices(ctx)
    }

    if len(v.errors) > 0 {
        return fmt.Errorf("configuration validation failed: %v", v.errors)
    }

    return nil
}

func (v *Validator) validateDatabase(ctx context.Context) {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()

    db, err := sql.Open("postgres", v.cfg.Database.DSN())
    if err != nil {
        v.errors = append(v.errors, fmt.Errorf("database config: %w", err))
        return
    }
    defer db.Close()

    if err := db.PingContext(ctx); err != nil {
        v.errors = append(v.errors, fmt.Errorf("database connection: %w", err))
    }
}

func (v *Validator) validateRedis(ctx context.Context) {
    ctx, cancel := context.WithTimeout(ctx, 2*time.Second)
    defer cancel()

    conn, err := net.DialTimeout("tcp", v.cfg.Redis.Addr(), 2*time.Second)
    if err != nil {
        v.errors = append(v.errors, fmt.Errorf("redis connection: %w", err))
        return
    }
    conn.Close()
}

func (v *Validator) validateExternalServices(ctx context.Context) {
    // Проверяем доступность внешних API
    // ...
}
```

**Использование в main**:

```go
func main() {
    cfg := config.MustLoad()

    // Валидируем подключения
    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    validator := config.NewValidator(cfg)
    if err := validator.Validate(ctx); err != nil {
        slog.Error("configuration validation failed", "error", err)
        os.Exit(1) // Fail fast!
    }

    slog.Info("configuration validated successfully")
    // ... продолжаем запуск
}
```

---

## 9. Docker Images

### 9.1 Multi-stage build

**Оптимальный Dockerfile для Go**:

```dockerfile
# Build stage
FROM golang:1.23-alpine AS builder

# Устанавливаем необходимые пакеты
RUN apk add --no-cache ca-certificates git

WORKDIR /app

# Кэшируем зависимости
COPY go.mod go.sum ./
RUN go mod download

# Копируем исходники
COPY . .

# Собираем бинарник
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build -ldflags="-s -w -X main.version=${VERSION:-unknown}" \
    -o /server ./cmd/server

# Runtime stage
FROM gcr.io/distroless/static-debian12:nonroot

# Копируем бинарник
COPY --from=builder /server /server

# Копируем CA certificates (для HTTPS)
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Non-root user (distroless уже имеет nonroot user)
USER nonroot:nonroot

# Expose port
EXPOSE 8080

# Health check (если нужен без Kubernetes)
# HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
#     CMD ["/server", "-health"]

ENTRYPOINT ["/server"]
```

**Ключевые оптимизации**:

| Оптимизация | Описание | Эффект |
|-------------|----------|--------|
| `CGO_ENABLED=0` | Статическая линковка | Работает в scratch/distroless |
| `-ldflags="-s -w"` | Убирает debug info | -30% размера бинарника |
| Multi-stage | Отдельные build/runtime | Image < 20MB |
| Distroless | Минимальный runtime | Меньше attack surface |
| Non-root | Запуск не от root | Security best practice |

### 9.2 Base images

**Сравнение base images**:

| Image | Размер | Shell | Security | Когда использовать |
|-------|--------|-------|----------|-------------------|
| `scratch` | 0 MB | Нет | Максимальная | Статические бинарники |
| `distroless/static` | ~2 MB | Нет | Высокая | Production (рекомендуется) |
| `alpine` | ~5 MB | Есть | Средняя | Если нужен shell для debug |
| `debian-slim` | ~80 MB | Есть | Средняя | CGO, специфические библиотеки |

**Scratch** (минимальный):

```dockerfile
FROM scratch
COPY --from=builder /server /server
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
USER 65532:65532
ENTRYPOINT ["/server"]
```

**Distroless** (рекомендуется):

```dockerfile
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /server /server
USER nonroot:nonroot
ENTRYPOINT ["/server"]
```

**Alpine** (для debug):

```dockerfile
FROM alpine:3.19
RUN apk --no-cache add ca-certificates
COPY --from=builder /server /server
RUN adduser -D -u 1000 appuser
USER appuser
ENTRYPOINT ["/server"]
```

### 9.3 Security scanning

**Trivy** — сканер уязвимостей:

```yaml
# .github/workflows/docker-security.yml
name: Docker Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:${{ github.sha }}'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1' # Fail on HIGH/CRITICAL

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'
```

**Локальный скан**:

```bash
# Установка Trivy
brew install trivy  # macOS
# или
sudo apt install trivy  # Ubuntu

# Сканирование образа
trivy image myapp:latest

# Сканирование с CI-friendly output
trivy image --exit-code 1 --severity HIGH,CRITICAL myapp:latest

# Сканирование Dockerfile
trivy config Dockerfile
```

### 9.4 Non-root user

**Почему non-root важен**:

```
┌─────────────────────────────────────────────────────────────────┐
│                     NON-ROOT CONTAINER                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ❌ Root (UID 0):                                               │
│   • Полный доступ к файловой системе контейнера                 │
│   • При escape из контейнера = root на хосте                    │
│   • Может модифицировать system files                           │
│   • Нарушает принцип least privilege                            │
│                                                                  │
│   ✅ Non-root (UID 65532, 1000, etc.):                          │
│   • Ограниченные права                                          │
│   • При escape = обычный пользователь                           │
│   • Не может bind к портам < 1024                               │
│   • Соответствует security best practices                       │
│                                                                  │
│   KUBERNETES:                                                    │
│   • PodSecurityPolicy / PodSecurityStandards                    │
│   • runAsNonRoot: true                                          │
│   • readOnlyRootFilesystem: true                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Kubernetes SecurityContext**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 65532
        runAsGroup: 65532
        fsGroup: 65532
      containers:
        - name: app
          image: myapp:latest
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          # Если нужна запись (логи, tmp):
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir: {}
```

---

## 10. Security Checklist

### 10.1 Input validation

**Валидация входных данных**:

```go
package validation

import (
    "regexp"
    "unicode/utf8"

    "github.com/go-playground/validator/v10"
)

var validate = validator.New()

// ValidateStruct валидирует структуру
func ValidateStruct(s interface{}) error {
    return validate.Struct(s)
}

// Пример структуры с валидацией
type CreateUserRequest struct {
    Email    string `json:"email" validate:"required,email,max=255"`
    Username string `json:"username" validate:"required,min=3,max=50,alphanum"`
    Password string `json:"password" validate:"required,min=8,max=72"`
    Age      int    `json:"age" validate:"omitempty,min=13,max=150"`
}

// SanitizeString очищает строку от потенциально опасных символов
func SanitizeString(s string) string {
    // Убираем null bytes
    s = strings.ReplaceAll(s, "\x00", "")

    // Ограничиваем длину
    if len(s) > 10000 {
        s = s[:10000]
    }

    // Проверяем валидность UTF-8
    if !utf8.ValidString(s) {
        s = strings.ToValidUTF8(s, "")
    }

    return strings.TrimSpace(s)
}

// ValidateEmail проверяет email
func ValidateEmail(email string) bool {
    // Простая проверка формата
    emailRegex := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
    return emailRegex.MatchString(email) && len(email) <= 255
}

// ValidateUUID проверяет UUID формат
func ValidateUUID(id string) bool {
    uuidRegex := regexp.MustCompile(`^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`)
    return uuidRegex.MatchString(strings.ToLower(id))
}
```

### 10.2 SQL injection prevention

**Параметризованные запросы** — единственный правильный способ:

```go
// ❌ НИКОГДА ТАК НЕ ДЕЛАТЬ — SQL Injection
func getUserBAD(db *sql.DB, userID string) (*User, error) {
    query := "SELECT * FROM users WHERE id = '" + userID + "'"
    // userID = "1' OR '1'='1" → SELECT * FROM users WHERE id = '1' OR '1'='1'
    return db.Query(query)
}

// ✅ Параметризованный запрос
func getUser(ctx context.Context, db *sql.DB, userID string) (*User, error) {
    var user User
    err := db.QueryRowContext(ctx,
        "SELECT id, name, email FROM users WHERE id = $1",
        userID, // Параметр безопасно экранируется драйвером
    ).Scan(&user.ID, &user.Name, &user.Email)
    return &user, err
}

// ✅ С ORM (sqlx)
func getUserSQLX(ctx context.Context, db *sqlx.DB, userID string) (*User, error) {
    var user User
    err := db.GetContext(ctx, &user, "SELECT * FROM users WHERE id = $1", userID)
    return &user, err
}

// ✅ Динамические запросы безопасно
func searchUsers(ctx context.Context, db *sql.DB, filters map[string]string) ([]*User, error) {
    query := strings.Builder{}
    query.WriteString("SELECT id, name, email FROM users WHERE 1=1")

    args := []interface{}{}
    argNum := 1

    if name, ok := filters["name"]; ok {
        query.WriteString(fmt.Sprintf(" AND name ILIKE $%d", argNum))
        args = append(args, "%"+name+"%")
        argNum++
    }

    if email, ok := filters["email"]; ok {
        query.WriteString(fmt.Sprintf(" AND email = $%d", argNum))
        args = append(args, email)
        argNum++
    }

    rows, err := db.QueryContext(ctx, query.String(), args...)
    // ...
}
```

### 10.3 Security headers

**Middleware для security headers**:

```go
package middleware

import "net/http"

// SecurityHeaders добавляет security headers к ответам
func SecurityHeaders(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Предотвращает MIME type sniffing
        w.Header().Set("X-Content-Type-Options", "nosniff")

        // Предотвращает clickjacking
        w.Header().Set("X-Frame-Options", "DENY")

        // XSS protection (устаревший, но не вредит)
        w.Header().Set("X-XSS-Protection", "1; mode=block")

        // HTTPS enforcement
        w.Header().Set("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload")

        // Referrer policy
        w.Header().Set("Referrer-Policy", "strict-origin-when-cross-origin")

        // Content Security Policy (настройте под ваше приложение)
        // w.Header().Set("Content-Security-Policy", "default-src 'self'")

        // Permissions Policy (бывший Feature-Policy)
        w.Header().Set("Permissions-Policy", "geolocation=(), microphone=(), camera=()")

        next.ServeHTTP(w, r)
    })
}

// CORS middleware
func CORS(allowedOrigins []string) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            origin := r.Header.Get("Origin")

            // Проверяем, разрешён ли origin
            allowed := false
            for _, o := range allowedOrigins {
                if o == "*" || o == origin {
                    allowed = true
                    break
                }
            }

            if allowed {
                w.Header().Set("Access-Control-Allow-Origin", origin)
                w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
                w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
                w.Header().Set("Access-Control-Max-Age", "86400")
            }

            // Preflight request
            if r.Method == "OPTIONS" {
                w.WriteHeader(http.StatusNoContent)
                return
            }

            next.ServeHTTP(w, r)
        })
    }
}
```

### 10.4 Dependency scanning

**govulncheck** — официальный сканер уязвимостей Go:

```bash
# Установка
go install golang.org/x/vuln/cmd/govulncheck@latest

# Сканирование проекта
govulncheck ./...

# Сканирование бинарника
govulncheck -mode=binary ./myapp
```

**CI интеграция**:

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 0 * * *' # Ежедневно

jobs:
  govulncheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: '1.23'

      - name: Install govulncheck
        run: go install golang.org/x/vuln/cmd/govulncheck@latest

      - name: Run govulncheck
        run: govulncheck ./...

  gosec:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run gosec
        uses: securego/gosec@master
        with:
          args: ./...
```

**Makefile**:

```makefile
.PHONY: security vuln gosec

security: vuln gosec

vuln:
	govulncheck ./...

gosec:
	gosec -quiet ./...

# Обновление зависимостей с проверкой уязвимостей
update-deps:
	go get -u ./...
	go mod tidy
	govulncheck ./...
```

---

## Практические примеры

### Пример 1: Production-Ready HTTP Server

Полный пример с graceful shutdown, health checks, metrics, logging.

```go
// cmd/server/main.go
package main

import (
    "context"
    "database/sql"
    "errors"
    "fmt"
    "log/slog"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "github.com/prometheus/client_golang/prometheus/promhttp"
    "golang.org/x/sync/errgroup"

    _ "github.com/lib/pq"
    _ "go.uber.org/automaxprocs"
)

func main() {
    // Загружаем конфигурацию
    cfg, err := loadConfig()
    if err != nil {
        fmt.Fprintf(os.Stderr, "failed to load config: %v\n", err)
        os.Exit(1)
    }

    // Инициализируем логгер
    logger := setupLogger(cfg)
    slog.SetDefault(logger)

    // Context для graceful shutdown
    ctx, stop := signal.NotifyContext(context.Background(),
        syscall.SIGINT,
        syscall.SIGTERM,
    )
    defer stop()

    // Запускаем приложение
    if err := run(ctx, cfg, logger); err != nil {
        logger.Error("application error", "error", err)
        os.Exit(1)
    }

    logger.Info("application stopped gracefully")
}

func run(ctx context.Context, cfg *Config, logger *slog.Logger) error {
    // Подключаемся к БД
    db, err := setupDatabase(ctx, cfg)
    if err != nil {
        return fmt.Errorf("database: %w", err)
    }
    defer db.Close()

    // Health checker
    healthChecker := newHealthChecker(db)

    // HTTP handlers
    mux := http.NewServeMux()

    // Health endpoints
    mux.HandleFunc("GET /healthz", healthChecker.liveness)
    mux.HandleFunc("GET /ready", healthChecker.readiness)

    // Metrics endpoint
    mux.Handle("GET /metrics", promhttp.Handler())

    // API endpoints
    mux.HandleFunc("GET /api/v1/users/{id}", getUserHandler(db, logger))
    mux.HandleFunc("POST /api/v1/users", createUserHandler(db, logger))

    // Middleware stack
    handler := chainMiddleware(mux,
        recoveryMiddleware(logger),
        requestIDMiddleware(),
        loggingMiddleware(logger),
        metricsMiddleware(),
    )

    // HTTP server
    server := &http.Server{
        Addr:         cfg.Server.Addr(),
        Handler:      handler,
        ReadTimeout:  cfg.Server.ReadTimeout,
        WriteTimeout: cfg.Server.WriteTimeout,
        IdleTimeout:  cfg.Server.IdleTimeout,
    }

    // Metrics server (отдельный порт)
    metricsServer := &http.Server{
        Addr:    ":9090",
        Handler: promhttp.Handler(),
    }

    g, gCtx := errgroup.WithContext(ctx)

    // Main server
    g.Go(func() error {
        logger.Info("starting HTTP server", "addr", server.Addr)
        if err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
            return err
        }
        return nil
    })

    // Metrics server
    g.Go(func() error {
        logger.Info("starting metrics server", "addr", metricsServer.Addr)
        if err := metricsServer.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
            return err
        }
        return nil
    })

    // Graceful shutdown
    g.Go(func() error {
        <-gCtx.Done()
        logger.Info("shutdown signal received")

        // Помечаем как not ready
        healthChecker.setReady(false)

        // Даём время load balancer'у
        logger.Info("waiting for load balancer drain")
        time.Sleep(5 * time.Second)

        // Shutdown servers
        shutdownCtx, cancel := context.WithTimeout(context.Background(), 25*time.Second)
        defer cancel()

        // Сначала main server
        if err := server.Shutdown(shutdownCtx); err != nil {
            logger.Error("main server shutdown error", "error", err)
        }
        logger.Info("main server stopped")

        // Затем metrics server
        if err := metricsServer.Shutdown(shutdownCtx); err != nil {
            logger.Error("metrics server shutdown error", "error", err)
        }
        logger.Info("metrics server stopped")

        return nil
    })

    return g.Wait()
}

// Health checker
type healthChecker struct {
    db    *sql.DB
    ready bool
}

func newHealthChecker(db *sql.DB) *healthChecker {
    return &healthChecker{db: db, ready: true}
}

func (h *healthChecker) setReady(ready bool) {
    h.ready = ready
}

func (h *healthChecker) liveness(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusOK)
    w.Write([]byte(`{"status":"ok"}`))
}

func (h *healthChecker) readiness(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")

    if !h.ready {
        w.WriteHeader(http.StatusServiceUnavailable)
        w.Write([]byte(`{"status":"shutting_down"}`))
        return
    }

    ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
    defer cancel()

    if err := h.db.PingContext(ctx); err != nil {
        w.WriteHeader(http.StatusServiceUnavailable)
        w.Write([]byte(`{"status":"database_unavailable"}`))
        return
    }

    w.WriteHeader(http.StatusOK)
    w.Write([]byte(`{"status":"ready"}`))
}

// Middleware helpers
func chainMiddleware(h http.Handler, middlewares ...func(http.Handler) http.Handler) http.Handler {
    for i := len(middlewares) - 1; i >= 0; i-- {
        h = middlewares[i](h)
    }
    return h
}

// Config и другие вспомогательные функции опущены для краткости
```

### Пример 2: Complete main.go Template

Шаблон для новых проектов — скопируйте и настройте.

```go
// main.go template
package main

import (
    "context"
    "errors"
    "fmt"
    "log/slog"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "golang.org/x/sync/errgroup"
    _ "go.uber.org/automaxprocs" // Автоматическая настройка GOMAXPROCS
)

// ============================================================================
// CONFIGURATION
// ============================================================================

type Config struct {
    // Server
    ServerAddr            string        `env:"SERVER_ADDR" envDefault:":8080"`
    ServerReadTimeout     time.Duration `env:"SERVER_READ_TIMEOUT" envDefault:"5s"`
    ServerWriteTimeout    time.Duration `env:"SERVER_WRITE_TIMEOUT" envDefault:"10s"`
    ServerShutdownTimeout time.Duration `env:"SERVER_SHUTDOWN_TIMEOUT" envDefault:"30s"`

    // Logging
    LogLevel  string `env:"LOG_LEVEL" envDefault:"info"`
    LogFormat string `env:"LOG_FORMAT" envDefault:"json"`

    // TODO: Добавьте свои настройки
    // DatabaseURL string `env:"DATABASE_URL" validate:"required"`
}

func loadConfig() (*Config, error) {
    // TODO: Используйте github.com/caarlos0/env/v10
    return &Config{
        ServerAddr:            getEnv("SERVER_ADDR", ":8080"),
        ServerReadTimeout:     5 * time.Second,
        ServerWriteTimeout:    10 * time.Second,
        ServerShutdownTimeout: 30 * time.Second,
        LogLevel:              getEnv("LOG_LEVEL", "info"),
        LogFormat:             getEnv("LOG_FORMAT", "json"),
    }, nil
}

func getEnv(key, defaultValue string) string {
    if value := os.Getenv(key); value != "" {
        return value
    }
    return defaultValue
}

// ============================================================================
// MAIN
// ============================================================================

func main() {
    if err := run(); err != nil {
        fmt.Fprintf(os.Stderr, "error: %v\n", err)
        os.Exit(1)
    }
}

func run() error {
    // Load config
    cfg, err := loadConfig()
    if err != nil {
        return fmt.Errorf("load config: %w", err)
    }

    // Setup logger
    logger := setupLogger(cfg.LogLevel, cfg.LogFormat)
    slog.SetDefault(logger)

    // Signal handling
    ctx, stop := signal.NotifyContext(context.Background(),
        syscall.SIGINT,
        syscall.SIGTERM,
    )
    defer stop()

    // TODO: Initialize dependencies
    // db, err := setupDatabase(ctx, cfg)
    // if err != nil {
    //     return fmt.Errorf("database: %w", err)
    // }
    // defer db.Close()

    // Setup HTTP server
    mux := setupRoutes(logger)
    server := &http.Server{
        Addr:         cfg.ServerAddr,
        Handler:      mux,
        ReadTimeout:  cfg.ServerReadTimeout,
        WriteTimeout: cfg.ServerWriteTimeout,
    }

    // Run with graceful shutdown
    g, gCtx := errgroup.WithContext(ctx)

    // HTTP server
    g.Go(func() error {
        logger.Info("starting server", "addr", cfg.ServerAddr)
        if err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
            return err
        }
        return nil
    })

    // Graceful shutdown
    g.Go(func() error {
        <-gCtx.Done()
        logger.Info("shutting down")

        shutdownCtx, cancel := context.WithTimeout(context.Background(), cfg.ServerShutdownTimeout)
        defer cancel()

        return server.Shutdown(shutdownCtx)
    })

    if err := g.Wait(); err != nil {
        return err
    }

    logger.Info("server stopped")
    return nil
}

// ============================================================================
// ROUTES
// ============================================================================

func setupRoutes(logger *slog.Logger) http.Handler {
    mux := http.NewServeMux()

    // Health endpoints
    mux.HandleFunc("GET /healthz", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        w.Write([]byte(`{"status":"ok"}`))
    })

    mux.HandleFunc("GET /ready", func(w http.ResponseWriter, r *http.Request) {
        // TODO: Check dependencies
        w.WriteHeader(http.StatusOK)
        w.Write([]byte(`{"status":"ready"}`))
    })

    // API endpoints
    // TODO: Add your routes
    mux.HandleFunc("GET /api/v1/hello", func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        w.Write([]byte(`{"message":"Hello, World!"}`))
    })

    // Wrap with middleware
    return recoveryMiddleware(logger)(
        loggingMiddleware(logger)(mux),
    )
}

// ============================================================================
// LOGGING
// ============================================================================

func setupLogger(level, format string) *slog.Logger {
    var lvl slog.Level
    switch level {
    case "debug":
        lvl = slog.LevelDebug
    case "warn":
        lvl = slog.LevelWarn
    case "error":
        lvl = slog.LevelError
    default:
        lvl = slog.LevelInfo
    }

    opts := &slog.HandlerOptions{Level: lvl}

    var handler slog.Handler
    if format == "json" {
        handler = slog.NewJSONHandler(os.Stdout, opts)
    } else {
        handler = slog.NewTextHandler(os.Stdout, opts)
    }

    return slog.New(handler)
}

// ============================================================================
// MIDDLEWARE
// ============================================================================

func recoveryMiddleware(logger *slog.Logger) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            defer func() {
                if err := recover(); err != nil {
                    logger.Error("panic recovered", "error", err)
                    http.Error(w, "Internal Server Error", http.StatusInternalServerError)
                }
            }()
            next.ServeHTTP(w, r)
        })
    }
}

func loggingMiddleware(logger *slog.Logger) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            start := time.Now()
            next.ServeHTTP(w, r)
            logger.Info("request",
                "method", r.Method,
                "path", r.URL.Path,
                "duration", time.Since(start),
            )
        })
    }
}
```

### Пример 3: Kubernetes Manifests

Полный набор манифестов для деплоя.

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  labels:
    app: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/metrics"
    spec:
      terminationGracePeriodSeconds: 45
      securityContext:
        runAsNonRoot: true
        runAsUser: 65532
        fsGroup: 65532
      containers:
        - name: app
          image: myapp:latest
          ports:
            - name: http
              containerPort: 8080
            - name: metrics
              containerPort: 9090
          env:
            - name: SERVER_ADDR
              value: ":8080"
            - name: LOG_LEVEL
              value: "info"
            - name: LOG_FORMAT
              value: "json"
          envFrom:
            - configMapRef:
                name: myapp-config
            - secretRef:
                name: myapp-secrets
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          startupProbe:
            httpGet:
              path: /healthz
              port: http
            failureThreshold: 30
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
            initialDelaySeconds: 0
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 0
            periodSeconds: 5
            timeoutSeconds: 5
            failureThreshold: 3
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 5"]
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir: {}
---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
  labels:
    app: myapp
spec:
  type: ClusterIP
  ports:
    - name: http
      port: 80
      targetPort: http
    - name: metrics
      port: 9090
      targetPort: metrics
  selector:
    app: myapp
---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
data:
  SERVER_READ_TIMEOUT: "5s"
  SERVER_WRITE_TIMEOUT: "10s"
  SERVER_SHUTDOWN_TIMEOUT: "30s"
---
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 3
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
---
# k8s/pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: myapp
```

---

## Master Checklist

Визуальный чек-лист для быстрой проверки production-readiness.

### Infrastructure

```
[ ] Graceful shutdown реализован
    [ ] signal.NotifyContext для SIGTERM/SIGINT
    [ ] server.Shutdown() с таймаутом
    [ ] Правильный shutdown order
    [ ] preStop hook в Kubernetes

[ ] Health endpoints
    [ ] /healthz (liveness) — только процесс
    [ ] /ready (readiness) — с проверкой зависимостей
    [ ] Kubernetes probes настроены

[ ] Structured logging
    [ ] JSON формат для production
    [ ] Уровни логов (debug/info/warn/error)
    [ ] Request ID в каждом запросе
    [ ] Sensitive data замаскированы

[ ] Configuration
    [ ] Environment variables
    [ ] Validation при старте
    [ ] Secrets не в коде
```

### Observability

```
[ ] Metrics
    [ ] RED metrics (Rate, Errors, Duration)
    [ ] /metrics endpoint
    [ ] Prometheus annotations в K8s

[ ] Tracing (если микросервисы)
    [ ] OpenTelemetry настроен
    [ ] Sampling strategy выбран
    [ ] Correlation IDs

[ ] Alerting
    [ ] High error rate alert
    [ ] High latency alert
    [ ] No traffic alert
```

### Resilience

```
[ ] Timeouts
    [ ] HTTP server timeouts
    [ ] HTTP client timeouts
    [ ] Database query timeouts

[ ] Rate limiting
    [ ] Global rate limit
    [ ] Per-IP/user rate limit

[ ] Circuit breaker
    [ ] Для внешних сервисов
    [ ] Fallback стратегия

[ ] Retry
    [ ] Exponential backoff
    [ ] Jitter
    [ ] Max attempts
```

### Security

```
[ ] Input validation
    [ ] Все входные данные валидируются
    [ ] Sanitization строк

[ ] SQL injection prevention
    [ ] Только параметризованные запросы

[ ] Security headers
    [ ] X-Content-Type-Options
    [ ] X-Frame-Options
    [ ] Strict-Transport-Security

[ ] Dependencies
    [ ] govulncheck в CI
    [ ] Регулярное обновление
```

### Docker & Kubernetes

```
[ ] Docker image
    [ ] Multi-stage build
    [ ] Distroless/scratch base
    [ ] Non-root user
    [ ] Security scanning

[ ] Kubernetes
    [ ] Resource limits
    [ ] SecurityContext
    [ ] PodDisruptionBudget
    [ ] HPA настроен
```

---

## Чек-лист

После изучения этого раздела вы должны:

### Graceful Shutdown
- [ ] Понимать важность graceful shutdown в production
- [ ] Использовать `signal.NotifyContext` для обработки сигналов
- [ ] Реализовывать правильный shutdown order
- [ ] Настраивать `terminationGracePeriodSeconds` и `preStop` в Kubernetes

### Health Checks
- [ ] Различать liveness, readiness и startup probes
- [ ] Реализовывать health endpoints с проверкой зависимостей
- [ ] Настраивать Kubernetes probes с правильными thresholds
- [ ] Понимать, когда возвращать "not ready" (shutdown, warmup)

### Logging & Metrics
- [ ] Настраивать structured logging с slog
- [ ] Маскировать sensitive data в логах
- [ ] Реализовывать RED metrics (Rate, Errors, Duration)
- [ ] Экспортировать метрики для Prometheus

### Distributed Tracing
- [ ] Понимать, когда tracing необходим
- [ ] Настраивать OpenTelemetry с sampling
- [ ] Передавать trace context между сервисами

### Resilience Patterns
- [ ] Реализовывать rate limiting с `golang.org/x/time/rate`
- [ ] Использовать circuit breaker (sony/gobreaker)
- [ ] Применять retry с exponential backoff и jitter
- [ ] Устанавливать timeouts на всех уровнях (server, client, DB)
- [ ] Применять bulkhead pattern для изоляции

### Error Handling
- [ ] Классифицировать ошибки (operational, transient, fatal)
- [ ] Возвращать ошибки в формате RFC 7807 Problem Details
- [ ] Реализовывать panic recovery middleware
- [ ] Интегрировать error tracking (Sentry)

### Configuration
- [ ] Загружать конфигурацию из environment variables
- [ ] Валидировать конфигурацию при старте (fail fast)
- [ ] Управлять secrets через Kubernetes Secrets или Vault

### Docker & Security
- [ ] Создавать минимальные Docker images (multi-stage, distroless)
- [ ] Запускать контейнеры от non-root пользователя
- [ ] Сканировать images и зависимости на уязвимости
- [ ] Добавлять security headers к HTTP ответам
- [ ] Использовать только параметризованные SQL запросы

---

## Следующие шаги

Поздравляем! Вы завершили **Часть 6: Best Practices**.

Теперь у вас есть полный набор знаний для написания production-ready Go приложений:
- Идиоматичный код и архитектура
- Современные возможности Go
- Инструменты разработки
- Оптимизация производительности
- Production checklist

Переходите к **Части 5: Практические проекты** для закрепления знаний на реальных примерах:
- CLI приложение
- REST API сервис
- Микросервисная архитектура
- Интеграция с очередями сообщений

---

**Вопросы?** Открой issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Назад: 6.4 Производительность](./04_performance.md) | [К оглавлению](../README.md)
