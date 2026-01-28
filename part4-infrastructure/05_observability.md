# 4.5 Observability: Логирование, Метрики, Трейсинг

## Содержание

- [Введение](#введение)
- [Экосистема: C# vs Go](#экосистема-c-vs-go)
- [Столп 1: Structured Logging](#столп-1-structured-logging)
  - [log/slog — стандартная библиотека (Go 1.21+)](#logslog--стандартная-библиотека-go-121)
    - [Основные концепции](#основные-концепции)
    - [TextHandler и JSONHandler](#texthandler-и-jsonhandler)
    - [Контекстное логирование: With() и WithGroup()](#контекстное-логирование-with-и-withgroup)
    - [Уровни логирования](#уровни-логирования)
    - [Интеграция с context.Context](#интеграция-с-contextcontext)
    - [Custom Handler](#custom-handler)
    - [HandlerOptions: тонкая настройка](#handleroptions-тонкая-настройка)
  - [uber-go/zap — высокопроизводительное логирование](#uber-gozap--высокопроизводительное-логирование)
    - [Два API: Logger и SugaredLogger](#два-api-logger-и-sugaredlogger)
    - [Конфигурация и настройка](#конфигурация-и-настройка)
    - [Sampling](#sampling)
    - [Интеграция с slog через zapslog](#интеграция-с-slog-через-zapslog)
  - [rs/zerolog — zero-allocation JSON logger](#rszerolog--zero-allocation-json-logger)
    - [API и использование](#api-и-использование)
    - [Интеграция с context и slog](#интеграция-с-context-и-slog)
  - [Сравнительная таблица: slog vs zap vs zerolog](#сравнительная-таблица-slog-vs-zap-vs-zerolog)
  - [Production Logging Patterns](#production-logging-patterns)
    - [Log rotation с lumberjack](#log-rotation-с-lumberjack)
    - [HTTP Request Logging Middleware](#http-request-logging-middleware)
    - [Маскирование чувствительных данных](#маскирование-чувствительных-данных)
    - [Динамическое управление уровнем логов](#динамическое-управление-уровнем-логов)
- [Столп 2: Метрики с Prometheus](#столп-2-метрики-с-prometheus)
  - [Архитектура Prometheus](#архитектура-prometheus)
  - [prometheus/client_golang](#prometheusclient_golang)
    - [Подключение и /metrics endpoint](#подключение-и-metrics-endpoint)
    - [Типы метрик](#типы-метрик)
    - [Labels и dimensions](#labels-и-dimensions)
    - [Регистрация метрик](#регистрация-метрик)
  - [HTTP Metrics Middleware](#http-metrics-middleware)
  - [Бизнес-метрики](#бизнес-метрики)
  - [VictoriaMetrics как альтернатива](#victoriametrics-как-альтернатива)
  - [PromQL: полезные запросы](#promql-полезные-запросы)
  - [Grafana дашборды](#grafana-дашборды)
- [Столп 3: Distributed Tracing с OpenTelemetry](#столп-3-distributed-tracing-с-opentelemetry)
  - [Концепции трейсинга](#концепции-трейсинга)
  - [OpenTelemetry Go SDK Setup](#opentelemetry-go-sdk-setup)
    - [TracerProvider и Resource](#tracerprovider-и-resource)
    - [Exporters](#exporters)
    - [Sampler и Propagator](#sampler-и-propagator)
    - [Production-ready инициализация](#production-ready-инициализация)
  - [Manual Instrumentation](#manual-instrumentation)
    - [Создание spans](#создание-spans)
    - [Атрибуты, события, ошибки](#атрибуты-события-ошибки)
    - [Вложенные spans](#вложенные-spans)
  - [Auto-Instrumentation](#auto-instrumentation)
    - [otelhttp: HTTP сервер и клиент](#otelhttp-http-сервер-и-клиент)
    - [otelgrpc, otelsql, redisotel](#otelgrpc-otelsql-redisotel)
  - [Jaeger и Zipkin](#jaeger-и-zipkin)
  - [OpenTelemetry Collector](#opentelemetry-collector)
- [Интеграция трёх столпов](#интеграция-трёх-столпов)
  - [Корреляция логов и трейсов](#корреляция-логов-и-трейсов)
  - [Exemplars: связь метрик с трейсами](#exemplars-связь-метрик-с-трейсами)
  - [Context Propagation между сервисами](#context-propagation-между-сервисами)
  - [Агрегация логов](#агрегация-логов)
- [Health Checks и Readiness Probes](#health-checks-и-readiness-probes)
  - [Liveness vs Readiness vs Startup](#liveness-vs-readiness-vs-startup)
  - [Реализация в Go](#реализация-в-go)
  - [Kubernetes интеграция](#kubernetes-интеграция)
- [SLI/SLO](#slislo)
  - [Service Level Indicators](#service-level-indicators)
  - [Service Level Objectives и Error Budgets](#service-level-objectives-и-error-budgets)
  - [Реализация SLI метрик в Go](#реализация-sli-метрик-в-go)
- [Production Concerns](#production-concerns)
  - [Влияние на производительность](#влияние-на-производительность)
  - [Graceful Shutdown](#graceful-shutdown)
  - [Тестирование observability](#тестирование-observability)
  - [Безопасность](#безопасность)
- [Практические примеры](#практические-примеры)
  - [Пример 1: Full Observability Setup для HTTP сервиса](#пример-1-full-observability-setup-для-http-сервиса)
  - [Пример 2: Distributed Tracing между микросервисами](#пример-2-distributed-tracing-между-микросервисами)
  - [Пример 3: Grafana Stack с Docker Compose](#пример-3-grafana-stack-с-docker-compose)
- [Чек-лист](#чек-лист)

---

## Введение

Observability — это способность понять внутреннее состояние системы по её внешним сигналам. В отличие от мониторинга, который отвечает на заранее известные вопросы ("работает ли сервис?", "какая нагрузка на CPU?"), observability позволяет исследовать **неизвестные проблемы** — те, которые вы не предвидели при проектировании.

В предыдущих разделах мы уже добавляли элементы observability фрагментарно: Prometheus метрики в [4.1 PostgreSQL](./01_production_postgresql.md), [4.2 Кэширование](./02_caching.md), [4.3 Очереди сообщений](./03_message_queues.md) и OpenTelemetry tracing в [4.4 gRPC](./04_grpc.md). Теперь мы соберём полную картину и построим observability как единую систему.

**Три столпа observability**:

| Столп | Что даёт | Пример |
|-------|----------|--------|
| **Логирование** | Детальные события с контекстом | `"заказ 12345 не прошёл валидацию: недостаточно средств"` |
| **Метрики** | Агрегированные числовые показатели | `http_requests_total{status="500"} = 42` |
| **Трейсинг** | Путь запроса через все сервисы | `API Gateway → User Service → Payment Service → DB` |

> 💡 **Для C# разработчиков**: В .NET экосистеме observability часто строится вокруг единого решения — **Application Insights** или **Datadog .NET**. Они предоставляют логирование (`ILogger<T>`), метрики (`System.Diagnostics.Metrics`) и трейсинг (`Activity`/`DiagnosticSource`) "из коробки". В Go нет all-in-one решения — вы **явно собираете** стек из отдельных библиотек: `log/slog` для логов, `prometheus/client_golang` для метрик, `go.opentelemetry.io/otel` для трейсинга. Больше кода, но полная прозрачность и vendor-нейтральность.

**C#** — всё через DI и middleware:
```csharp
// C#: одна строка подключает всё
builder.Services.AddOpenTelemetry()
    .WithTracing(b => b
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddOtlpExporter())
    .WithMetrics(b => b
        .AddAspNetCoreInstrumentation()
        .AddPrometheusExporter());

builder.Host.UseSerilog((ctx, lc) => lc
    .WriteTo.Console()
    .WriteTo.OpenTelemetry());
```

**Go** — явная инициализация каждого компонента:
```go
// Go: каждый компонент настраивается явно
func main() {
    // 1. Логирование
    logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
    slog.SetDefault(logger)

    // 2. Трейсинг
    tp, err := initTracer()
    if err != nil {
        log.Fatal(err)
    }
    defer tp.Shutdown(context.Background())

    // 3. Метрики
    reg := prometheus.NewRegistry()
    reg.MustRegister(collectors.NewGoCollector())

    // 4. HTTP сервер с middleware
    mux := http.NewServeMux()
    mux.Handle("/metrics", promhttp.HandlerFor(reg, promhttp.HandlerOpts{}))
    // ... обработчики с otelhttp обёрткой
}
```

---

## Экосистема: C# vs Go

| Концепция | C# (.NET) | Go |
|-----------|-----------|-----|
| Стандартное логирование | `Microsoft.Extensions.Logging` + `ILogger<T>` | `log/slog` (Go 1.21+) |
| Популярные логгеры | Serilog, NLog | zap (Uber), zerolog |
| Structured logging | Serilog message templates | slog, zap, zerolog — JSON нативно |
| Log abstraction | `ILoggerFactory`, DI injection | `slog.Logger` передаётся явно |
| Метрики (стандарт) | `System.Diagnostics.Metrics` (.NET 8+) | `prometheus/client_golang` |
| Метрики (Prometheus) | `prometheus-net` | `prometheus/client_golang` (официальный) |
| Метрики (OTel) | `OpenTelemetry.Metrics` | `go.opentelemetry.io/otel/metric` |
| Трейсинг (стандарт) | `System.Diagnostics.Activity` | `go.opentelemetry.io/otel/trace` |
| OTel SDK | `OpenTelemetry .NET` (NuGet) | `go.opentelemetry.io/otel` |
| Context propagation | `Activity.Current` (ambient) | `context.Context` (explicit) |
| Health checks | `Microsoft.Extensions.Diagnostics.HealthChecks` | Ручная реализация / `alexliesenfeld/health` |
| Middleware | `app.UseHttpLogging()` | Явные middleware функции |
| All-in-one платформа | Application Insights, Datadog | Нет аналога — собирается из компонентов |
| Log aggregation | ELK, Application Insights | ELK, Grafana Loki |
| Dashboards | Azure Monitor, Kibana | Grafana |
| Correlation ID | `Activity.TraceId` (автоматически) | `trace.SpanFromContext(ctx)` (вручную) |
| Auto-instrumentation | `AddAspNetCoreInstrumentation()` | `otelhttp.NewHandler()` (явно) |

> 💡 **Ключевое отличие**: В Go **context propagation всегда явный** через `context.Context`. Нет ambient `Activity.Current` как в .NET. Это значит: каждый метод в цепочке вызовов должен принимать `ctx context.Context` как первый параметр. Это выглядит как boilerplate, но даёт полный контроль и прозрачность.

---

## Столп 1: Structured Logging

### log/slog — стандартная библиотека (Go 1.21+)

До Go 1.21 стандартный пакет `log` предоставлял только текстовое логирование без структуры. Каждый проект выбирал между `zap`, `zerolog`, `logrus` — что приводило к несовместимости между библиотеками. Пакет `log/slog`, добавленный в Go 1.21, решил эту проблему — он стал **стандартным интерфейсом** для structured logging в Go.

> 💡 **Для C# разработчиков**: `slog` — это аналог `Microsoft.Extensions.Logging.ILogger<T>`. Как `ILogger<T>` абстрагирует конкретный провайдер (Console, Serilog, NLog), так `slog.Handler` абстрагирует backend логирования. Разница: в Go нет DI — логгер передаётся явно.

#### Основные концепции

```go
package main

import (
    "context"
    "log/slog"
    "os"
)

func main() {
    // Создание логгера с JSON выводом (production)
    logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

    // Установка как default (аналог ILoggerFactory в C#)
    slog.SetDefault(logger)

    // Логирование с structured данными
    slog.Info("сервер запущен",
        slog.String("addr", ":8080"),
        slog.Int("workers", 4),
    )
    // Вывод: {"time":"2026-01-27T10:00:00Z","level":"INFO","msg":"сервер запущен","addr":":8080","workers":4}

    // Логирование с контекстом (для интеграции с tracing)
    ctx := context.Background()
    slog.InfoContext(ctx, "обработка запроса",
        slog.String("method", "GET"),
        slog.String("path", "/api/users"),
    )
}
```

**Ключевые типы slog**:

| Тип | Описание | Аналог в C# |
|-----|----------|--------------|
| `slog.Logger` | Экземпляр логгера | `ILogger<T>` |
| `slog.Handler` | Backend (куда и как писать) | `ILoggerProvider` |
| `slog.Record` | Одна запись лога | `LogEntry` |
| `slog.Attr` | Пара ключ-значение | `KeyValuePair` в scope |
| `slog.Level` | Уровень логирования | `LogLevel` |

Два способа передачи атрибутов:

```go
// Способ 1: Alternating key-value (быстрый, но нет type-safety)
slog.Info("запрос", "method", "GET", "path", "/api/users", "status", 200)

// Способ 2: Typed attrs (предпочтительный — type-safe, нет ошибок с парностью)
slog.Info("запрос",
    slog.String("method", "GET"),
    slog.String("path", "/api/users"),
    slog.Int("status", 200),
)
```

> ⚠️ **Не используйте строковую конкатенацию**: `slog.Info("user " + id)` — это медленнее (аллокация строки) и ломает structured logging. Всегда передавайте данные как атрибуты: `slog.Info("user", slog.String("id", id))`.

#### TextHandler и JSONHandler

```go
// TextHandler — для разработки (human-readable)
textHandler := slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelDebug,
})
textLogger := slog.New(textHandler)
textLogger.Info("запрос обработан", slog.String("path", "/api"), slog.Int("status", 200))
// Вывод: time=2026-01-27T10:00:00.000Z level=INFO msg="запрос обработан" path=/api status=200

// JSONHandler — для production (машиночитаемый)
jsonHandler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
})
jsonLogger := slog.New(jsonHandler)
jsonLogger.Info("запрос обработан", slog.String("path", "/api"), slog.Int("status", 200))
// Вывод: {"time":"2026-01-27T10:00:00Z","level":"INFO","msg":"запрос обработан","path":"/api","status":200}
```

**Сравнение с C#**:

```csharp
// C#: Serilog с разными форматами
Log.Logger = new LoggerConfiguration()
    .WriteTo.Console() // text для разработки
    // .WriteTo.Console(new JsonFormatter()) // JSON для production
    .CreateLogger();

Log.Information("Запрос обработан: {Path} {Status}", "/api", 200);
// Serilog: message template с destructuring
```

```go
// Go: slog — явный выбор handler
// В Go нет message templates — всегда key-value пары
slog.Info("запрос обработан",
    slog.String("path", "/api"),
    slog.Int("status", 200),
)
```

> 💡 **Идиома Go**: В C# Serilog использует **message templates** (`"Processing {OrderId}"`), где имя свойства извлекается из шаблона. В Go slog — всегда явные **key-value пары**. Это обеспечивает type-safety без рефлексии и исключает ошибки несоответствия параметров шаблону.

#### Контекстное логирование: With() и WithGroup()

```go
// With() — добавление постоянных атрибутов (аналог Serilog.ForContext<T>())
func NewOrderService(logger *slog.Logger) *OrderService {
    return &OrderService{
        // Все логи этого сервиса будут содержать "component"
        logger: logger.With(slog.String("component", "order_service")),
    }
}

type OrderService struct {
    logger *slog.Logger
}

func (s *OrderService) ProcessOrder(ctx context.Context, order Order) error {
    // Добавляем контекст заказа
    log := s.logger.With(
        slog.String("order_id", order.ID),
        slog.String("customer_id", order.CustomerID),
    )

    log.InfoContext(ctx, "начало обработки заказа")

    if err := s.validateOrder(order); err != nil {
        log.ErrorContext(ctx, "валидация заказа не пройдена",
            slog.String("error", err.Error()),
        )
        return fmt.Errorf("валидация: %w", err)
    }

    log.InfoContext(ctx, "заказ успешно обработан",
        slog.Float64("total", order.Total),
    )
    return nil
}
```

```go
// WithGroup() — группировка атрибутов (вложенный JSON)
logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

requestLogger := logger.WithGroup("request").With(
    slog.String("method", "POST"),
    slog.String("path", "/api/orders"),
)

requestLogger.Info("получен запрос", slog.Int("body_size", 1024))
// Вывод:
// {
//   "time": "2026-01-27T10:00:00Z",
//   "level": "INFO",
//   "msg": "получен запрос",
//   "request": {
//     "method": "POST",
//     "path": "/api/orders",
//     "body_size": 1024
//   }
// }
```

**Сравнение с C#** (ILogger scope):

```csharp
// C#: ILogger с BeginScope
using (_logger.BeginScope(new Dictionary<string, object>
{
    ["OrderId"] = order.Id,
    ["CustomerId"] = order.CustomerId
}))
{
    _logger.LogInformation("Начало обработки заказа");
    // ... все логи в scope содержат OrderId и CustomerId
}
```

```go
// Go: slog.With() — без using/Dispose, просто новый логгер
log := s.logger.With(
    slog.String("order_id", order.ID),
    slog.String("customer_id", order.CustomerID),
)
log.Info("начало обработки заказа")
// log можно передавать дальше по цепочке вызовов
```

#### Уровни логирования

```go
// Стандартные уровни slog
const (
    LevelDebug = slog.Level(-4)  // подробная отладка
    LevelInfo  = slog.Level(0)   // информационные сообщения
    LevelWarn  = slog.Level(4)   // предупреждения
    LevelError = slog.Level(8)   // ошибки
)

// Использование
slog.Debug("детали отладки", slog.Any("payload", data))
slog.Info("операция выполнена")
slog.Warn("высокая нагрузка", slog.Int("goroutines", runtime.NumGoroutine()))
slog.Error("ошибка подключения к БД", slog.String("error", err.Error()))

// Пользовательские уровни (между стандартными)
const (
    LevelTrace  = slog.Level(-8)  // ещё подробнее чем Debug
    LevelNotice = slog.Level(2)   // между Info и Warn
    LevelFatal  = slog.Level(12)  // критическая ошибка
)
```

| slog Level | C# LogLevel | Числовое значение |
|------------|-------------|-------------------|
| `LevelDebug` | `Debug` | -4 |
| `LevelInfo` | `Information` | 0 |
| `LevelWarn` | `Warning` | 4 |
| `LevelError` | `Error` | 8 |
| _(custom)_ | `Critical` | _(12)_ |

#### Интеграция с context.Context

```go
// slog поддерживает context для интеграции с tracing
func handleRequest(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()

    // InfoContext передаёт ctx в Handler — тот может извлечь trace_id
    slog.InfoContext(ctx, "обработка запроса",
        slog.String("method", r.Method),
        slog.String("path", r.URL.Path),
    )

    user, err := getUserFromDB(ctx, r.URL.Query().Get("id"))
    if err != nil {
        slog.ErrorContext(ctx, "не удалось получить пользователя",
            slog.String("error", err.Error()),
        )
        http.Error(w, "internal error", http.StatusInternalServerError)
        return
    }

    slog.InfoContext(ctx, "пользователь найден",
        slog.String("user_id", user.ID),
        slog.String("email", user.Email),
    )
}
```

> 💡 **Всегда используйте `InfoContext`/`ErrorContext`/etc. вместо `Info`/`Error`** в production-коде. Это позволит custom handler извлечь trace_id и span_id из контекста и добавить их в каждую запись лога. Мы реализуем такой handler в разделе [Корреляция логов и трейсов](#корреляция-логов-и-трейсов).

#### Custom Handler

Интерфейс `slog.Handler` позволяет создавать кастомные обработчики — аналогично `ILoggerProvider` в C#:

```go
// slog.Handler — интерфейс (4 метода)
type Handler interface {
    Enabled(context.Context, Level) bool
    Handle(context.Context, Record) error
    WithAttrs(attrs []Attr) Handler
    WithGroup(name string) Handler
}
```

Пример: handler, который добавляет trace_id из OpenTelemetry context в каждую запись:

```go
package logging

import (
    "context"
    "log/slog"

    "go.opentelemetry.io/otel/trace"
)

// OTelHandler оборачивает любой slog.Handler и добавляет trace_id/span_id
type OTelHandler struct {
    inner slog.Handler
}

func NewOTelHandler(inner slog.Handler) *OTelHandler {
    return &OTelHandler{inner: inner}
}

func (h *OTelHandler) Enabled(ctx context.Context, level slog.Level) bool {
    return h.inner.Enabled(ctx, level)
}

func (h *OTelHandler) Handle(ctx context.Context, r slog.Record) error {
    // Извлекаем span из context
    span := trace.SpanFromContext(ctx)
    if span.SpanContext().IsValid() {
        r.AddAttrs(
            slog.String("trace_id", span.SpanContext().TraceID().String()),
            slog.String("span_id", span.SpanContext().SpanID().String()),
        )
    }
    return h.inner.Handle(ctx, r)
}

func (h *OTelHandler) WithAttrs(attrs []slog.Attr) slog.Handler {
    return &OTelHandler{inner: h.inner.WithAttrs(attrs)}
}

func (h *OTelHandler) WithGroup(name string) slog.Handler {
    return &OTelHandler{inner: h.inner.WithGroup(name)}
}
```

Использование:

```go
func main() {
    // Обычный JSON handler
    jsonHandler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
        Level: slog.LevelInfo,
    })

    // Оборачиваем в OTel handler
    otelHandler := logging.NewOTelHandler(jsonHandler)
    logger := slog.New(otelHandler)
    slog.SetDefault(logger)

    // Теперь каждый лог с контекстом будет содержать trace_id и span_id:
    // {"time":"...","level":"INFO","msg":"запрос","trace_id":"abc123","span_id":"def456"}
}
```

> 💡 **Для C# разработчиков**: В .NET `Activity.Current.TraceId` **автоматически** попадает в логи через `Microsoft.Extensions.Logging`. В Go это нужно сделать **вручную** — но зато вы полностью контролируете формат и какие данные включать.

#### HandlerOptions: тонкая настройка

```go
opts := &slog.HandlerOptions{
    // Добавлять source code location (файл:строка)
    AddSource: true,

    // Минимальный уровень логирования
    Level: slog.LevelInfo,

    // Кастомизация атрибутов (аналог Serilog Enricher)
    ReplaceAttr: func(groups []string, a slog.Attr) slog.Attr {
        // Переименовать "time" → "timestamp" (для совместимости с ELK)
        if a.Key == slog.TimeKey {
            a.Key = "timestamp"
        }

        // Переименовать "level" → "severity" (для GCP Cloud Logging)
        if a.Key == slog.LevelKey {
            a.Key = "severity"
        }

        // Маскировать чувствительные данные
        if a.Key == "password" || a.Key == "token" || a.Key == "card_number" {
            a.Value = slog.StringValue("***REDACTED***")
        }

        return a
    },
}

logger := slog.New(slog.NewJSONHandler(os.Stdout, opts))
logger.Info("пользователь авторизован",
    slog.String("user_id", "123"),
    slog.String("password", "secret123"), // → "***REDACTED***"
)
// {"timestamp":"...","severity":"INFO","source":{"function":"main.main","file":"main.go","line":42},
//  "msg":"пользователь авторизован","user_id":"123","password":"***REDACTED***"}
```

> ⚠️ **Никогда не логируйте пароли, токены, номера карт.** Реализуйте redaction через `ReplaceAttr` или custom handler — заменяйте значения полей `"password"`, `"token"`, `"card_number"`, `"secret"` на `"***REDACTED***"`. Это должно быть настроено **на уровне handler**, а не в каждом вызове лога.

---

### uber-go/zap — высокопроизводительное логирование

[zap](https://github.com/uber-go/zap) — библиотека от Uber, созданная задолго до `slog` (2016 год). Главное преимущество — **zero-allocation** дизайн: в hot paths не происходит аллокаций в heap, что минимизирует нагрузку на GC. В эпоху до `slog` (Go <1.21) `zap` был де-факто стандартом для production-логирования в Go.

> 💡 **Для C# разработчиков**: `zap` — это ближайший аналог **Serilog** в Go-мире: высокопроизводительный structured logging с гибкой конфигурацией. Разница: Serilog использует message templates, zap — типизированные поля.

#### Два API: Logger и SugaredLogger

```go
package main

import (
    "go.uber.org/zap"
)

func main() {
    // === Production Logger (typed, zero-alloc) ===
    logger, _ := zap.NewProduction()
    defer logger.Sync() // flushes buffer

    // Typed fields — НУЛЕВЫЕ аллокации
    logger.Info("запрос обработан",
        zap.String("method", "GET"),
        zap.String("path", "/api/users"),
        zap.Int("status", 200),
        zap.Duration("latency", 42*time.Millisecond),
    )
    // {"level":"info","ts":1706349600,"caller":"main.go:15",
    //  "msg":"запрос обработан","method":"GET","path":"/api/users",
    //  "status":200,"latency":0.042}

    // === Sugared Logger (printf-like, удобнее но медленнее) ===
    sugar := logger.Sugar()

    // printf-style (аллокации из-за interface{})
    sugar.Infof("запрос %s %s → %d", "GET", "/api/users", 200)

    // Alternating key-value (похоже на slog)
    sugar.Infow("запрос обработан",
        "method", "GET",
        "path", "/api/users",
        "status", 200,
    )
}
```

> ⚠️ **Не используйте SugaredLogger в production hot paths** — он в 4-10x медленнее обычного Logger из-за `interface{}` аллокаций. SugaredLogger удобен для прототипирования и low-frequency логирования (запуск, shutdown), а для hot paths всегда используйте typed Logger.

| API | Аллокации | Скорость | Удобство | Использование |
|-----|-----------|----------|----------|---------------|
| `zap.Logger` | 0 (zero-alloc) | Максимальная | Typed fields | Production hot paths |
| `zap.SugaredLogger` | Есть (interface{}) | 4-10x медленнее | printf/key-value | Startup/shutdown, dev |

#### Конфигурация и настройка

```go
// Production конфигурация с кастомизацией
cfg := zap.Config{
    Level:       zap.NewAtomicLevelAt(zap.InfoLevel),
    Development: false,
    Encoding:    "json", // "json" или "console"
    EncoderConfig: zapcore.EncoderConfig{
        TimeKey:        "timestamp",
        LevelKey:       "severity",
        NameKey:        "logger",
        CallerKey:      "caller",
        FunctionKey:    zapcore.OmitKey,
        MessageKey:     "message",
        StacktraceKey:  "stacktrace",
        LineEnding:     zapcore.DefaultLineEnding,
        EncodeLevel:    zapcore.CapitalLevelEncoder,    // INFO, WARN, ERROR
        EncodeTime:     zapcore.ISO8601TimeEncoder,     // 2026-01-27T10:00:00Z
        EncodeDuration: zapcore.MillisDurationEncoder,  // 42.5
        EncodeCaller:   zapcore.ShortCallerEncoder,     // main.go:42
    },
    OutputPaths:      []string{"stdout"},
    ErrorOutputPaths: []string{"stderr"},
    InitialFields: map[string]interface{}{
        "service": "order-service",
        "version": "1.2.3",
    },
}

logger, err := cfg.Build()
if err != nil {
    log.Fatalf("не удалось создать логгер: %v", err)
}
defer logger.Sync()
```

Запись с log rotation через [lumberjack](https://github.com/natefinch/lumberjack):

```go
import (
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
    "gopkg.in/natefinch/lumberjack.v2"
)

func newProductionLogger() *zap.Logger {
    // Log rotation
    writer := &lumberjack.Logger{
        Filename:   "/var/log/app/service.log",
        MaxSize:    100, // MB
        MaxBackups: 5,
        MaxAge:     30, // дней
        Compress:   true,
    }

    // Encoder для JSON
    encoderCfg := zap.NewProductionEncoderConfig()
    encoderCfg.TimeKey = "timestamp"
    encoderCfg.EncodeTime = zapcore.ISO8601TimeEncoder

    core := zapcore.NewCore(
        zapcore.NewJSONEncoder(encoderCfg),
        zapcore.AddSync(writer),
        zap.InfoLevel,
    )

    return zap.New(core,
        zap.AddCaller(),
        zap.AddStacktrace(zap.ErrorLevel), // stacktrace для Error+
    )
}
```

#### Sampling

zap поддерживает sampling — пропуск повторяющихся сообщений для снижения нагрузки:

```go
// Sampling: после первых 100 одинаковых сообщений, логировать каждое 100-е
logger, _ := zap.NewProduction(zap.WrapCore(func(core zapcore.Core) zapcore.Core {
    return zapcore.NewSamplerWithOptions(core,
        time.Second,  // интервал
        100,          // первых N сообщений логировать все
        100,          // потом — каждое N-е
    )
}))

// Или через Config
cfg := zap.NewProductionConfig()
cfg.Sampling = &zap.SamplingConfig{
    Initial:    100,
    Thereafter: 100,
}
```

> 💡 **Sampling** полезен для high-throughput сервисов, где один и тот же лог может генерироваться тысячи раз в секунду (например, "получен запрос"). Без sampling такие логи забивают диск и Loki/ELK. В `slog` встроенного sampling нет — нужно реализовать через custom handler.

#### Интеграция с slog через zapslog

Начиная с Go 1.21, можно использовать `zap` как backend для `slog`:

```go
import (
    "log/slog"

    "go.uber.org/zap"
    "go.uber.org/zap/exp/zapslog"
)

func main() {
    // Создаём zap logger
    zapLogger, _ := zap.NewProduction()
    defer zapLogger.Sync()

    // Используем zap как backend для slog
    slogHandler := zapslog.NewHandler(zapLogger.Core(), &zapslog.HandlerOptions{
        AddSource: true,
    })
    slogLogger := slog.New(slogHandler)
    slog.SetDefault(slogLogger)

    // Теперь slog.Info() использует zap под капотом
    slog.Info("сервер запущен", slog.String("addr", ":8080"))

    // А zap logger можно использовать напрямую для hot paths
    zapLogger.Info("hot path операция",
        zap.String("key", "value"),
    )
}
```

> 💡 **Рекомендация**: В новых проектах используйте `slog` как **публичный интерфейс** (API сервиса), а `zap` — как **backend** через `zapslog`. Это даёт стандартный интерфейс + производительность zap. Внешние библиотеки видят `slog.Logger`, внутри работает `zap`.

---

### rs/zerolog — zero-allocation JSON logger

[zerolog](https://github.com/rs/zerolog) — ещё более минималистичный zero-allocation логгер. Его философия: **JSON-first, minimum overhead**. zerolog изначально генерирует только JSON, что делает его самым быстрым логгером в бенчмарках.

#### API и использование

```go
package main

import (
    "os"
    "time"

    "github.com/rs/zerolog"
    "github.com/rs/zerolog/log"
)

func main() {
    // === Development: human-readable вывод ===
    log.Logger = zerolog.New(zerolog.ConsoleWriter{
        Out:        os.Stderr,
        TimeFormat: time.Kitchen,
    }).With().Timestamp().Caller().Logger()

    log.Info().
        Str("method", "GET").
        Str("path", "/api/users").
        Int("status", 200).
        Dur("latency", 42*time.Millisecond).
        Msg("запрос обработан")
    // 10:00AM INF main.go:20 > запрос обработан method=GET path=/api/users status=200 latency=42ms

    // === Production: JSON вывод ===
    logger := zerolog.New(os.Stdout).With().
        Timestamp().
        Str("service", "order-service").
        Logger()

    logger.Info().
        Str("order_id", "12345").
        Float64("total", 99.99).
        Msg("заказ создан")
    // {"level":"info","service":"order-service","order_id":"12345","total":99.99,
    //  "time":"2026-01-27T10:00:00Z","message":"заказ создан"}
}
```

**Отличие от zap**: zerolog использует **method chaining** (builder pattern), что даёт более fluent API:

```go
// zerolog: chaining
logger.Info().
    Str("key", "value").
    Int("count", 42).
    Msg("сообщение")

// zap: typed fields в конструкторе
logger.Info("сообщение",
    zap.String("key", "value"),
    zap.Int("count", 42),
)

// slog: key-value пары
slog.Info("сообщение",
    slog.String("key", "value"),
    slog.Int("count", 42),
)
```

**Контекстное логирование**:

```go
// zerolog хранит логгер в context.Context
func middleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Добавляем логгер с request_id в контекст
        logger := log.With().
            Str("request_id", r.Header.Get("X-Request-ID")).
            Str("method", r.Method).
            Str("path", r.URL.Path).
            Logger()

        ctx := logger.WithContext(r.Context())
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

func handler(w http.ResponseWriter, r *http.Request) {
    // Извлекаем логгер из контекста
    logger := zerolog.Ctx(r.Context())
    logger.Info().Msg("обработка запроса")
    // Автоматически содержит request_id, method, path
}
```

#### Интеграция с context и slog

```go
import (
    "log/slog"

    "github.com/rs/zerolog"
    slogzerolog "github.com/samber/slog-zerolog/v2"
)

func main() {
    // zerolog как backend для slog
    zerologLogger := zerolog.New(os.Stdout).With().Timestamp().Logger()

    slogHandler := slogzerolog.Option{
        Logger: &zerologLogger,
    }.NewZerologHandler()

    slog.SetDefault(slog.New(slogHandler))

    // slog API → zerolog backend
    slog.Info("сервер запущен", slog.String("addr", ":8080"))
}
```

---

### Сравнительная таблица: slog vs zap vs zerolog

| Аспект | log/slog | zap | zerolog |
|--------|----------|-----|---------|
| **Тип** | Стандартная библиотека | Сторонняя (Uber) | Сторонняя |
| **Появился** | Go 1.21 (2023) | 2016 | 2017 |
| **Аллокации** | Минимальные | Zero-allocation | Zero-allocation |
| **API стиль** | Key-value пары | Typed fields | Method chaining |
| **JSON output** | JSONHandler | Встроено | Нативно (только JSON) |
| **Text output** | TextHandler | Console encoder | ConsoleWriter |
| **Sampling** | Нет (custom handler) | Встроено | Нет |
| **Log rotation** | Нет (через io.Writer) | lumberjack | lumberjack |
| **slog совместимость** | Нативно | zapslog adapter | slog-zerolog adapter |
| **Context support** | InfoContext(ctx, ...) | Нет (через middleware) | zerolog.Ctx(ctx) |
| **Caller info** | AddSource: true | AddCaller() | Caller() |
| **Stack traces** | Нет | AddStacktrace() | Stack() |
| **DI/injection** | Передаётся явно | Передаётся явно + Global | Передаётся явно + Global |
| **Экосистема** | Растёт (новый стандарт) | Большая | Средняя |
| **Рекомендация** | Новые проекты | Enterprise, существующие | Макс. производительность |

**Бенчмарки** (типичные значения, сообщение с 10 полями):

| Логгер | ns/op | B/op | allocs/op |
|--------|-------|------|-----------|
| **zerolog** | ~180 | 0 | 0 |
| **zap** | ~200 | 0 | 0 |
| **slog (JSONHandler)** | ~350 | ~120 | ~3 |
| **slog (zap backend)** | ~250 | ~40 | ~1 |

> 💡 **Когда что выбирать**:
> - **Новый проект** → `slog` (стандарт, все библиотеки будут его поддерживать)
> - **Новый проект + нужна макс. производительность** → `slog` + `zap` backend (через `zapslog`)
> - **Существующий проект с zap** → оставить `zap`, при необходимости добавить `slog` интерфейс
> - **Микросервис с минимальным overhead** → `zerolog` (самый быстрый)
> - **Нужен sampling** → `zap` (встроенный) или `slog` + custom handler

---

### Production Logging Patterns

#### Log rotation с lumberjack

В production-среде с контейнерами (Docker, Kubernetes) **лучше логировать в stdout** и позволить платформе управлять логами. Но если вы деплоите на bare metal / VM — нужна ротация файлов:

```go
import (
    "io"
    "log/slog"
    "os"

    "gopkg.in/natefinch/lumberjack.v2"
)

func newProductionLogger() *slog.Logger {
    // Ротация файлов
    fileWriter := &lumberjack.Logger{
        Filename:   "/var/log/app/service.log",
        MaxSize:    100, // максимальный размер файла (MB)
        MaxBackups: 5,   // сколько старых файлов хранить
        MaxAge:     30,  // сколько дней хранить
        Compress:   true, // gzip для старых файлов
    }

    // Пишем и в файл, и в stdout (для Docker logs)
    multiWriter := io.MultiWriter(os.Stdout, fileWriter)

    opts := &slog.HandlerOptions{
        Level:     slog.LevelInfo,
        AddSource: true,
    }

    return slog.New(slog.NewJSONHandler(multiWriter, opts))
}
```

> 💡 **Идиома Go**: Логируйте в **stdout в JSON-формате**. Не пишите в файлы напрямую в контейнерной среде — пусть Docker/Kubernetes управляет сбором логов через Fluentd, Promtail или Vector. `lumberjack` нужен только для bare metal / VM деплоя.

#### HTTP Request Logging Middleware

```go
// Middleware для логирования HTTP запросов (аналог ASP.NET Core UseHttpLogging)
func LoggingMiddleware(logger *slog.Logger) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            start := time.Now()

            // Обёртка для захвата status code и размера ответа
            wrapped := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}

            // Логируем начало запроса
            requestID := r.Header.Get("X-Request-ID")
            if requestID == "" {
                requestID = uuid.NewString()
            }

            log := logger.With(
                slog.String("request_id", requestID),
                slog.String("method", r.Method),
                slog.String("path", r.URL.Path),
                slog.String("remote_addr", r.RemoteAddr),
                slog.String("user_agent", r.UserAgent()),
            )

            // Добавляем логгер в контекст
            ctx := context.WithValue(r.Context(), loggerKey{}, log)
            r = r.WithContext(ctx)

            // Выполняем запрос
            next.ServeHTTP(wrapped, r)

            // Логируем результат
            duration := time.Since(start)
            level := slog.LevelInfo
            if wrapped.statusCode >= 500 {
                level = slog.LevelError
            } else if wrapped.statusCode >= 400 {
                level = slog.LevelWarn
            }

            log.Log(r.Context(), level, "запрос обработан",
                slog.Int("status", wrapped.statusCode),
                slog.Int64("bytes", wrapped.bytesWritten),
                slog.Duration("duration", duration),
            )
        })
    }
}

type responseWriter struct {
    http.ResponseWriter
    statusCode   int
    bytesWritten int64
}

func (rw *responseWriter) WriteHeader(code int) {
    rw.statusCode = code
    rw.ResponseWriter.WriteHeader(code)
}

func (rw *responseWriter) Write(b []byte) (int, error) {
    n, err := rw.ResponseWriter.Write(b)
    rw.bytesWritten += int64(n)
    return n, err
}
```

**Сравнение с C#**:

```csharp
// C#: одна строка
app.UseHttpLogging();

// Или с Serilog
app.UseSerilogRequestLogging();
```

```go
// Go: явный middleware (больше кода, но полный контроль)
mux.Handle("/api/", LoggingMiddleware(logger)(apiHandler))
```

#### Маскирование чувствительных данных

```go
// PII Redaction Handler — оборачивает любой slog.Handler
type RedactHandler struct {
    inner      slog.Handler
    redactKeys map[string]bool
}

func NewRedactHandler(inner slog.Handler, keys ...string) *RedactHandler {
    redactKeys := make(map[string]bool, len(keys))
    for _, k := range keys {
        redactKeys[k] = true
    }
    return &RedactHandler{inner: inner, redactKeys: redactKeys}
}

func (h *RedactHandler) Enabled(ctx context.Context, level slog.Level) bool {
    return h.inner.Enabled(ctx, level)
}

func (h *RedactHandler) Handle(ctx context.Context, r slog.Record) error {
    // Фильтруем атрибуты
    var filtered []slog.Attr
    r.Attrs(func(a slog.Attr) bool {
        if h.redactKeys[a.Key] {
            filtered = append(filtered, slog.String(a.Key, "***REDACTED***"))
        } else {
            filtered = append(filtered, a)
        }
        return true
    })

    // Создаём новую запись с отфильтрованными атрибутами
    newRecord := slog.NewRecord(r.Time, r.Level, r.Message, r.PC)
    newRecord.AddAttrs(filtered...)
    return h.inner.Handle(ctx, newRecord)
}

func (h *RedactHandler) WithAttrs(attrs []slog.Attr) slog.Handler {
    return &RedactHandler{inner: h.inner.WithAttrs(attrs), redactKeys: h.redactKeys}
}

func (h *RedactHandler) WithGroup(name string) slog.Handler {
    return &RedactHandler{inner: h.inner.WithGroup(name), redactKeys: h.redactKeys}
}

// Использование
func main() {
    jsonHandler := slog.NewJSONHandler(os.Stdout, nil)
    redactHandler := NewRedactHandler(jsonHandler,
        "password", "token", "card_number", "secret", "ssn",
    )
    slog.SetDefault(slog.New(redactHandler))

    slog.Info("авторизация",
        slog.String("user", "john"),
        slog.String("password", "s3cret!"),   // → "***REDACTED***"
        slog.String("token", "eyJhbGci..."),  // → "***REDACTED***"
    )
}
```

#### Динамическое управление уровнем логов

```go
// slog: через slog.LevelVar (потокобезопасный)
var logLevel = new(slog.LevelVar)

func main() {
    logLevel.Set(slog.LevelInfo) // начальный уровень

    handler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
        Level: logLevel, // динамический уровень
    })
    slog.SetDefault(slog.New(handler))

    // HTTP endpoint для изменения уровня в runtime
    http.HandleFunc("PUT /admin/log-level", func(w http.ResponseWriter, r *http.Request) {
        level := r.URL.Query().Get("level")
        switch level {
        case "debug":
            logLevel.Set(slog.LevelDebug)
        case "info":
            logLevel.Set(slog.LevelInfo)
        case "warn":
            logLevel.Set(slog.LevelWarn)
        case "error":
            logLevel.Set(slog.LevelError)
        default:
            http.Error(w, "unknown level", http.StatusBadRequest)
            return
        }
        slog.Info("уровень логирования изменён", slog.String("level", level))
        w.WriteHeader(http.StatusOK)
    })
}

// zap: через zap.AtomicLevel
atomicLevel := zap.NewAtomicLevel()
atomicLevel.SetLevel(zap.InfoLevel)

// zap предоставляет готовый HTTP handler
http.Handle("PUT /admin/log-level", atomicLevel) // принимает JSON: {"level":"debug"}
```

> 💡 **Динамическое изменение уровня логов** — критическая возможность для production. Когда возникает проблема, вы включаете `DEBUG` через API, собираете данные, и возвращаете `INFO`. В C# это делается через `IOptionsMonitor<LoggerFilterOptions>` или reloadable Serilog config. В Go — через `slog.LevelVar` или `zap.AtomicLevel`.

---

## Столп 2: Метрики с Prometheus

### Архитектура Prometheus

Prometheus — система мониторинга с **pull-моделью**: Prometheus-сервер периодически опрашивает (scrape) HTTP endpoint `/metrics` каждого сервиса. Данные хранятся как **time series** — имя метрики + набор labels + значение + timestamp.

```
┌──────────┐    scrape /metrics    ┌──────────────┐
│Prometheus │───────────────────────│  Go Service   │
│  Server   │   каждые 15s          │  :8080/metrics│
└──────┬───┘                       └──────────────┘
       │
       │  PromQL queries
       ▼
┌──────────┐
│  Grafana  │
│ Dashboard │
└──────────┘
```

> 💡 **Для C# разработчиков**: Prometheus pull-модель работает так же, как `prometheus-net` в .NET: вы регистрируете метрики, экспонируете `/metrics` endpoint, и Prometheus забирает данные. Альтернатива — push-модель (StatsD, Datadog Agent), где приложение отправляет метрики на сервер. В Kubernetes pull-модель предпочтительна — Prometheus автоматически находит сервисы через Service Discovery.

**Модель данных Prometheus**:

```
# Метрика с labels
http_requests_total{method="GET", path="/api/users", status="200"} 1542

# Структура: <metric_name>{<label_name>=<label_value>, ...} <value> [<timestamp>]
```

| Компонент | Описание | Пример |
|-----------|----------|--------|
| metric_name | Имя метрики (snake_case) | `http_requests_total` |
| labels | Dimensions (ключ-значение) | `method="GET"` |
| value | Числовое значение (float64) | `1542` |
| timestamp | Время (опционально) | `1706349600000` |

**Naming conventions**:
- `_total` — суффикс для counters (`http_requests_total`)
- `_seconds` — суффикс для duration (`request_duration_seconds`)
- `_bytes` — суффикс для размеров (`response_size_bytes`)
- `_info` — суффикс для информационных метрик (`build_info`)

---

### prometheus/client_golang

[prometheus/client_golang](https://github.com/prometheus/client_golang) — **официальная** Go-библиотека для работы с Prometheus. В отличие от .NET, где `prometheus-net` — сторонняя библиотека, в Go клиент от самих разработчиков Prometheus.

#### Подключение и /metrics endpoint

```go
package main

import (
    "log"
    "net/http"

    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/collectors"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

func main() {
    // Создаём registry (вместо default, для изоляции в тестах)
    reg := prometheus.NewRegistry()

    // Регистрируем стандартные Go метрики
    reg.MustRegister(collectors.NewGoCollector())       // go_goroutines, go_gc_*, go_memstats_*
    reg.MustRegister(collectors.NewProcessCollector(     // process_cpu_seconds, process_open_fds
        collectors.ProcessCollectorOpts{},
    ))

    // Экспонируем /metrics
    mux := http.NewServeMux()
    mux.Handle("GET /metrics", promhttp.HandlerFor(reg, promhttp.HandlerOpts{
        Registry:          reg,
        EnableOpenMetrics: true, // OpenMetrics формат (поддерживает exemplars)
    }))

    log.Println("метрики доступны на :9090/metrics")
    log.Fatal(http.ListenAndServe(":9090", mux))
}
```

**Сравнение с C#**:

```csharp
// C#: prometheus-net
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

// Одна строка — и /metrics доступен
app.UseMetricServer(); // prometheus-net.AspNetCore
app.MapMetrics();      // или через mapping

// Метрики регистрируются глобально
var counter = Metrics.CreateCounter("my_counter", "Description");
```

```go
// Go: явная настройка registry и handler
reg := prometheus.NewRegistry()
reg.MustRegister(collectors.NewGoCollector())
mux.Handle("GET /metrics", promhttp.HandlerFor(reg, promhttp.HandlerOpts{}))
```

#### Типы метрик

Prometheus определяет 4 типа метрик:

| Тип | Описание | Когда использовать | Пример |
|-----|----------|-------------------|--------|
| **Counter** | Монотонно растущее значение | Подсчёт событий | `http_requests_total` |
| **Gauge** | Значение, которое растёт и падает | Текущее состояние | `active_connections` |
| **Histogram** | Распределение значений по bucket'ам | Latency, размеры | `request_duration_seconds` |
| **Summary** | Квантили (percentiles) | Latency (редко) | `request_duration_quantile` |

```go
import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

// === Counter: монотонно растёт (нельзя уменьшать!) ===
var httpRequestsTotal = promauto.NewCounterVec(
    prometheus.CounterOpts{
        Namespace: "myapp",
        Subsystem: "http",
        Name:      "requests_total",
        Help:      "Общее количество HTTP запросов",
    },
    []string{"method", "path", "status"}, // labels
)

// Использование: httpRequestsTotal.WithLabelValues("GET", "/api/users", "200").Inc()

// === Gauge: текущее значение (может расти и падать) ===
var activeConnections = promauto.NewGauge(
    prometheus.GaugeOpts{
        Namespace: "myapp",
        Name:      "active_connections",
        Help:      "Количество активных соединений",
    },
)

// Использование:
// activeConnections.Inc()  // +1
// activeConnections.Dec()  // -1
// activeConnections.Set(42) // установить конкретное значение

// === Histogram: распределение значений ===
var requestDuration = promauto.NewHistogramVec(
    prometheus.HistogramOpts{
        Namespace: "myapp",
        Subsystem: "http",
        Name:      "request_duration_seconds",
        Help:      "Длительность HTTP запросов в секундах",
        // Кастомные buckets для вашего SLA
        Buckets: []float64{0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5},
    },
    []string{"method", "path"},
)

// Использование: requestDuration.WithLabelValues("GET", "/api/users").Observe(0.042)

// === Summary: квантили (используйте Histogram вместо Summary!) ===
var requestDurationSummary = promauto.NewSummary(
    prometheus.SummaryOpts{
        Name:       "request_duration_summary",
        Help:       "Квантили длительности запросов",
        Objectives: map[float64]float64{0.5: 0.05, 0.9: 0.01, 0.99: 0.001},
    },
)
```

> ⚠️ **Используйте Histogram вместо Summary** в большинстве случаев. Histogram позволяет вычислять произвольные percentiles через PromQL (`histogram_quantile()`), агрегировать по нескольким инстансам и настраивать alerting. Summary вычисляет квантили на стороне клиента и **не может агрегироваться** между инстансами.

> ⚠️ **Настройте Histogram buckets под ваш SLA!** Дефолтные buckets `DefBuckets` (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10) могут не подходить. Если ваш SLA — "99% запросов < 100ms", вам нужны гранулярные buckets в диапазоне 1-100ms.

#### Labels и dimensions

```go
// Labels добавляют dimensions к метрике
var dbQueryDuration = promauto.NewHistogramVec(
    prometheus.HistogramOpts{
        Name:    "db_query_duration_seconds",
        Help:    "Длительность запросов к БД",
        Buckets: prometheus.ExponentialBuckets(0.001, 2, 15), // от 1ms, x2, 15 buckets
    },
    []string{"query_name", "table", "status"}, // label names
)

// Использование с labels
func queryUsers(ctx context.Context) ([]User, error) {
    timer := prometheus.NewTimer(
        dbQueryDuration.WithLabelValues("get_users", "users", "success"),
    )
    defer timer.ObserveDuration()

    // ... выполнение запроса
}
```

> ⚠️ **Не создавайте метрики с высокой кардинальностью (high cardinality)!** Каждая уникальная комбинация labels — это отдельная time series в Prometheus. Не используйте `user_id`, `order_id`, `request_id`, IP-адрес как labels. Это быстро исчерпает память Prometheus и замедлит запросы.

**Хорошие labels**:
- `method` (GET, POST, PUT, DELETE — ~5 значений)
- `status` (200, 400, 500 — ~10 значений)
- `endpoint` (/api/users, /api/orders — ~20 значений)

**Плохие labels**:
- `user_id` (миллионы значений!)
- `request_id` (уникальный для каждого запроса!)
- `timestamp` (бесконечное количество!)

#### Регистрация метрик

```go
// Способ 1: promauto — автоматическая регистрация в default registry
// Удобно, но плохо для тестов (глобальное состояние)
var counter = promauto.NewCounter(prometheus.CounterOpts{
    Name: "my_counter",
    Help: "Описание",
})

// Способ 2: Явная регистрация в custom registry (рекомендуется)
func NewMetrics(reg prometheus.Registerer) *Metrics {
    m := &Metrics{
        RequestsTotal: prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "http_requests_total",
                Help: "Общее количество HTTP запросов",
            },
            []string{"method", "path", "status"},
        ),
        RequestDuration: prometheus.NewHistogramVec(
            prometheus.HistogramOpts{
                Name:    "http_request_duration_seconds",
                Help:    "Длительность HTTP запросов",
                Buckets: []float64{0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5},
            },
            []string{"method", "path"},
        ),
    }

    reg.MustRegister(m.RequestsTotal, m.RequestDuration)
    return m
}

type Metrics struct {
    RequestsTotal   *prometheus.CounterVec
    RequestDuration *prometheus.HistogramVec
}
```

> 💡 **Для тестов используйте custom registry**: `prometheus.NewRegistry()`. Это изолирует метрики теста от глобального состояния и позволяет проверять конкретные значения.

---

### HTTP Metrics Middleware

Полноценный middleware для сбора RED-метрик (Rate, Errors, Duration):

```go
// metricsMiddleware собирает RED-метрики для HTTP сервера
type metricsMiddleware struct {
    requestsTotal   *prometheus.CounterVec
    requestDuration *prometheus.HistogramVec
    requestSize     *prometheus.HistogramVec
    responseSize    *prometheus.HistogramVec
    requestsInFlight prometheus.Gauge
}

func NewMetricsMiddleware(reg prometheus.Registerer) *metricsMiddleware {
    m := &metricsMiddleware{
        requestsTotal: prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Name: "http_requests_total",
                Help: "Общее количество HTTP запросов",
            },
            []string{"method", "path", "status"},
        ),
        requestDuration: prometheus.NewHistogramVec(
            prometheus.HistogramOpts{
                Name:    "http_request_duration_seconds",
                Help:    "Длительность HTTP запросов",
                Buckets: []float64{0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5},
            },
            []string{"method", "path"},
        ),
        requestSize: prometheus.NewHistogramVec(
            prometheus.HistogramOpts{
                Name:    "http_request_size_bytes",
                Help:    "Размер HTTP запросов в байтах",
                Buckets: prometheus.ExponentialBuckets(100, 10, 7), // 100B, 1KB, 10KB, ...
            },
            []string{"method", "path"},
        ),
        responseSize: prometheus.NewHistogramVec(
            prometheus.HistogramOpts{
                Name:    "http_response_size_bytes",
                Help:    "Размер HTTP ответов в байтах",
                Buckets: prometheus.ExponentialBuckets(100, 10, 7),
            },
            []string{"method", "path"},
        ),
        requestsInFlight: prometheus.NewGauge(
            prometheus.GaugeOpts{
                Name: "http_requests_in_flight",
                Help: "Количество запросов в обработке",
            },
        ),
    }

    reg.MustRegister(
        m.requestsTotal, m.requestDuration,
        m.requestSize, m.responseSize,
        m.requestsInFlight,
    )
    return m
}

func (m *metricsMiddleware) Handler(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()

        m.requestsInFlight.Inc()
        defer m.requestsInFlight.Dec()

        // Нормализация пути (чтобы /api/users/123 → /api/users/:id)
        path := normalizePath(r.URL.Path)

        // Размер запроса
        m.requestSize.WithLabelValues(r.Method, path).
            Observe(float64(r.ContentLength))

        // Обёртка для захвата status и размера ответа
        wrapped := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}
        next.ServeHTTP(wrapped, r)

        // Записываем метрики
        status := strconv.Itoa(wrapped.statusCode)
        duration := time.Since(start).Seconds()

        m.requestsTotal.WithLabelValues(r.Method, path, status).Inc()
        m.requestDuration.WithLabelValues(r.Method, path).Observe(duration)
        m.responseSize.WithLabelValues(r.Method, path).
            Observe(float64(wrapped.bytesWritten))
    })
}

// normalizePath заменяет динамические сегменты на :param
// чтобы избежать high cardinality labels
func normalizePath(path string) string {
    // /api/users/550e8400-e29b-41d4-a716-446655440000 → /api/users/:id
    // /api/orders/12345 → /api/orders/:id
    // Реализация зависит от вашего роутера
    // Для chi: chi.RouteContext(ctx).RoutePattern()
    return path
}
```

**Сравнение с C#**:

```csharp
// C#: prometheus-net одна строка
app.UseHttpMetrics(); // собирает все RED метрики автоматически
```

```go
// Go: явный middleware (полный контроль над метриками и labels)
metrics := NewMetricsMiddleware(reg)
mux.Handle("/api/", metrics.Handler(apiHandler))
```

> 💡 **Нормализация путей** — критически важна. Без неё каждый уникальный URL (`/api/users/1`, `/api/users/2`, ...) создаёт отдельную time series, что приводит к cardinality explosion. Используйте шаблон маршрута (route pattern) вместо фактического URL.

---

### Бизнес-метрики

Помимо инфраструктурных метрик (HTTP, DB), важно отслеживать **бизнес-показатели**:

```go
type BusinessMetrics struct {
    OrdersCreated    *prometheus.CounterVec
    OrdersCompleted  *prometheus.CounterVec
    OrdersFailed     *prometheus.CounterVec
    OrderAmount      prometheus.Histogram
    ActiveUsers      prometheus.Gauge
    PaymentsTotal    *prometheus.CounterVec
    PaymentsAmount   *prometheus.CounterVec
    InventoryLevel   *prometheus.GaugeVec
}

func NewBusinessMetrics(reg prometheus.Registerer) *BusinessMetrics {
    m := &BusinessMetrics{
        OrdersCreated: prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Namespace: "business",
                Name:      "orders_created_total",
                Help:      "Количество созданных заказов",
            },
            []string{"type"}, // "standard", "express", "subscription"
        ),
        OrdersCompleted: prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Namespace: "business",
                Name:      "orders_completed_total",
                Help:      "Количество выполненных заказов",
            },
            []string{"type"},
        ),
        OrdersFailed: prometheus.NewCounterVec(
            prometheus.CounterOpts{
                Namespace: "business",
                Name:      "orders_failed_total",
                Help:      "Количество неудачных заказов",
            },
            []string{"type", "reason"}, // reason: "payment_declined", "out_of_stock"
        ),
        OrderAmount: prometheus.NewHistogram(
            prometheus.HistogramOpts{
                Namespace: "business",
                Name:      "order_amount_rub",
                Help:      "Сумма заказа в рублях",
                Buckets:   []float64{100, 500, 1000, 5000, 10000, 50000, 100000},
            },
        ),
        ActiveUsers: prometheus.NewGauge(
            prometheus.GaugeOpts{
                Namespace: "business",
                Name:      "active_users",
                Help:      "Количество активных пользователей (за последние 5 минут)",
            },
        ),
    }

    reg.MustRegister(
        m.OrdersCreated, m.OrdersCompleted, m.OrdersFailed,
        m.OrderAmount, m.ActiveUsers,
    )
    return m
}

// Использование в бизнес-логике
func (s *OrderService) CreateOrder(ctx context.Context, order Order) error {
    // ... создание заказа

    s.metrics.OrdersCreated.WithLabelValues(order.Type).Inc()
    s.metrics.OrderAmount.Observe(order.Total)

    return nil
}
```

> 💡 **Бизнес-метрики** — самые ценные для product-команды. Они показывают, как система работает **с точки зрения бизнеса**: сколько заказов, какая конверсия, сколько денег обрабатывается. Техническим метрикам (CPU, memory) не хватает этого контекста.

---

### VictoriaMetrics как альтернатива

[VictoriaMetrics](https://github.com/VictoriaMetrics/metrics) предлагает более простой Go-клиент для метрик, совместимый с Prometheus format:

```go
import "github.com/VictoriaMetrics/metrics"

// Counter
var requestsTotal = metrics.NewCounter("http_requests_total")
requestsTotal.Inc()

// Counter с labels (формируются через строку)
metrics.GetOrCreateCounter(`http_requests_total{method="GET",status="200"}`).Inc()

// Histogram
var duration = metrics.NewHistogram("http_request_duration_seconds")
duration.Update(0.042)

// Gauge
var goroutines = metrics.NewGauge("go_goroutines", func() float64 {
    return float64(runtime.NumGoroutine())
})

// Экспонирование метрик
http.HandleFunc("/metrics", func(w http.ResponseWriter, r *http.Request) {
    metrics.WritePrometheus(w, true) // true = с go runtime метриками
})
```

**Когда использовать VictoriaMetrics клиент**:
- Минимальный overhead и размер бинарника
- Простой API без registry/collector абстракций
- Совместимость с Prometheus format
- Не нужна полная мощь `prometheus/client_golang`

**Когда оставаться на `prometheus/client_golang`**:
- Нужны Exemplars (для связи с трейсами)
- Нужен custom registry для тестов
- Используете OpenMetrics формат
- Нужны collectors (GoCollector, ProcessCollector)

---

### PromQL: полезные запросы

PromQL (Prometheus Query Language) — язык запросов для анализа time series данных. Основные паттерны для Go-сервисов:

#### Rate и throughput

```promql
# Запросов в секунду (RPS) за последние 5 минут
rate(http_requests_total[5m])

# RPS по методу и пути
sum(rate(http_requests_total[5m])) by (method, path)

# Общий RPS сервиса
sum(rate(http_requests_total[5m]))
```

#### Error rate

```promql
# Процент ошибок (5xx)
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
* 100

# Error rate по endpoint
sum(rate(http_requests_total{status=~"5.."}[5m])) by (path)
/
sum(rate(http_requests_total[5m])) by (path)
```

#### Latency (percentiles)

```promql
# p50 (медиана) latency
histogram_quantile(0.5, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# p95 latency
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# p99 latency
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# p99 latency по endpoint
histogram_quantile(0.99,
    sum(rate(http_request_duration_seconds_bucket[5m])) by (le, path)
)
```

#### Go runtime метрики

```promql
# Количество горутин
go_goroutines

# Использование памяти (heap alloc)
go_memstats_heap_alloc_bytes

# GC pause duration (p99)
histogram_quantile(0.99, rate(go_gc_duration_seconds_bucket[5m]))

# Количество GC циклов в секунду
rate(go_gc_duration_seconds_count[5m])
```

#### Alerting rules (примеры)

```yaml
# prometheus-alerts.yml
groups:
  - name: go-service
    rules:
      # Высокий error rate
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          / sum(rate(http_requests_total[5m]))
          > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Error rate > 5%"

      # Высокая latency
      - alert: HighLatency
        expr: |
          histogram_quantile(0.99,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          ) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "p99 latency > 1s"

      # Слишком много горутин
      - alert: TooManyGoroutines
        expr: go_goroutines > 10000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Goroutine count > 10000 (possible leak)"
```

**Полезные PromQL паттерны**:

| Паттерн | PromQL | Применение |
|---------|--------|------------|
| RPS | `rate(counter[5m])` | Throughput |
| Error rate | `rate(errors[5m]) / rate(total[5m])` | Reliability |
| p95 latency | `histogram_quantile(0.95, rate(bucket[5m]))` | Performance |
| Saturation | `gauge / max_capacity` | Capacity |
| Increase | `increase(counter[1h])` | Абсолютные числа за период |

---

### Grafana дашборды

#### RED Method — для сервисов

**R**ate (запросов в секунду), **E**rrors (процент ошибок), **D**uration (latency) — три ключевые метрики для любого сервиса:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Order Service Dashboard                       │
├──────────────────┬──────────────────┬───────────────────────────┤
│  Request Rate    │  Error Rate (%)  │  p95 Latency              │
│  ████████ 250/s  │  ░░░░░█ 1.2%    │  ████░░ 45ms              │
├──────────────────┴──────────────────┴───────────────────────────┤
│  Request Rate by Endpoint                                        │
│  /api/orders  ████████████ 150/s                                │
│  /api/users   ██████ 80/s                                       │
│  /api/health  ██ 20/s                                           │
├─────────────────────────────────────────────────────────────────┤
│  Latency Distribution (Heatmap)                                  │
│  99%  ░░░░░░░░░░░░░░░░░░░█                                     │
│  95%  ░░░░░░░░░░░░████████                                      │
│  50%  ████████████                                               │
├─────────────────────────────────────────────────────────────────┤
│  Go Runtime                                                      │
│  Goroutines: 142  │  Heap: 45MB  │  GC Pause p99: 0.8ms        │
└─────────────────────────────────────────────────────────────────┘
```

#### USE Method — для инфраструктуры

**U**tilization, **S**aturation, **E**rrors — для ресурсов (CPU, Memory, Disk, Network, Connection Pool):

```promql
# Utilization: % использования пула соединений БД
pgx_pool_acquired_connections / pgx_pool_max_connections * 100

# Saturation: очередь ожидания пула
pgx_pool_pending_acquires

# Errors: ошибки при получении соединения
rate(pgx_pool_acquire_errors_total[5m])
```

#### Go Runtime Dashboard

Стандартные Go метрики, которые автоматически экспортируются `collectors.NewGoCollector()`:

| Метрика | Описание | Полезный PromQL |
|---------|----------|-----------------|
| `go_goroutines` | Кол-во горутин | `go_goroutines` — goroutine leak detection |
| `go_memstats_heap_alloc_bytes` | Heap memory | Trend analysis |
| `go_gc_duration_seconds` | GC pause time | `histogram_quantile(0.99, ...)` |
| `go_memstats_alloc_bytes_total` | Total allocations | `rate(...)` — alloc rate |
| `go_threads` | OS threads | Thread leak detection |
| `process_open_fds` | Open file descriptors | Approaching ulimit |
| `process_resident_memory_bytes` | RSS memory | OOM risk |

> 💡 **Grafana Dashboard ID 14061** — популярный готовый дашборд для Go-сервисов. Импортируйте его через Grafana UI → Import Dashboard → ID 14061. Он включает горутины, GC, memory, HTTP метрики.

---

## Столп 3: Distributed Tracing с OpenTelemetry

### Концепции трейсинга

Distributed tracing позволяет проследить путь запроса через все микросервисы — от входящего HTTP-запроса до последнего SQL-запроса к базе данных. Каждый "шаг" в пути — это **span**.

```
Trace: abc-123
├── [HTTP Server] GET /api/orders/42        (span 1, 150ms)
│   ├── [DB] SELECT * FROM orders WHERE id=42  (span 2, 5ms)
│   ├── [gRPC Client] GetUser(user_id=7)       (span 3, 30ms)
│   │   └── [gRPC Server] GetUser              (span 4, 25ms)
│   │       └── [DB] SELECT * FROM users       (span 5, 3ms)
│   └── [HTTP Client] GET payment-service/...  (span 6, 80ms)
│       └── [HTTP Server] GET /payments/42     (span 7, 75ms)
│           └── [DB] SELECT * FROM payments    (span 8, 2ms)
```

**Ключевые концепции**:

| Концепция | Описание | Аналог в C# |
|-----------|----------|--------------|
| **Trace** | Весь путь запроса (дерево spans) | Trace (Activity tree) |
| **Span** | Одна операция (с временем начала/конца) | `Activity` |
| **SpanContext** | TraceID + SpanID + Flags | `ActivityContext` |
| **Tracer** | Фабрика для создания spans | `ActivitySource` |
| **TracerProvider** | Фабрика для Tracer'ов + настройка export | `TracerProvider` |
| **Attributes** | Key-value пары на span | `Activity.Tags` |
| **Events** | Временные метки внутри span | `Activity.Events` |
| **Status** | OK / Error / Unset | `Activity.Status` |
| **SpanKind** | Client / Server / Producer / Consumer / Internal | `ActivityKind` |
| **Baggage** | Данные, пропагируемые через все сервисы | `Baggage` |

> 💡 **Для C# разработчиков**: В .NET трейсинг основан на `System.Diagnostics.Activity`. Ключевое отличие: `Activity.Current` — это **ambient context** (хранится в `AsyncLocal<T>`), который автоматически доступен в любом месте кода без передачи. В Go аналога нет — `context.Context` нужно **явно передавать** в каждый вызов. Это означает, что каждая функция в цепочке должна принимать `ctx context.Context`.

**Стратегии сэмплирования (sampling)**:

| Стратегия | Описание | Когда использовать |
|-----------|----------|--------------------|
| `AlwaysOn` | Записывать 100% трейсов | Development, staging |
| `AlwaysOff` | Не записывать | Отключение трейсинга |
| `TraceIDRatioBased(0.1)` | 10% трейсов | Production (low traffic) |
| `ParentBased(root)` | Наследовать от родителя | Production (рекомендуется) |

> ⚠️ **В production всегда настраивайте sampling!** `AlwaysOn` (100% трейсов) приводит к огромному потреблению памяти и нагрузке на Jaeger/Zipkin backend. Типичный production sampling: 1-10% (`TraceIDRatioBased(0.01)` - `TraceIDRatioBased(0.1)`).

---

### OpenTelemetry Go SDK Setup

#### TracerProvider и Resource

```go
package telemetry

import (
    "context"
    "fmt"

    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    "go.opentelemetry.io/otel/propagation"
    "go.opentelemetry.io/otel/sdk/resource"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.26.0"
)

// InitTracer создаёт и настраивает TracerProvider
func InitTracer(ctx context.Context, serviceName, serviceVersion, env string) (*sdktrace.TracerProvider, error) {
    // 1. Resource — описание сервиса
    res, err := resource.Merge(
        resource.Default(),
        resource.NewWithAttributes(
            semconv.SchemaURL,
            semconv.ServiceName(serviceName),
            semconv.ServiceVersion(serviceVersion),
            semconv.DeploymentEnvironmentName(env),
        ),
    )
    if err != nil {
        return nil, fmt.Errorf("создание resource: %w", err)
    }

    // 2. Exporter — куда отправлять трейсы (OTLP gRPC)
    exporter, err := otlptracegrpc.New(ctx,
        otlptracegrpc.WithEndpoint("otel-collector:4317"),
        otlptracegrpc.WithInsecure(), // для dev; в production — TLS
    )
    if err != nil {
        return nil, fmt.Errorf("создание exporter: %w", err)
    }

    // 3. TracerProvider — собираем всё вместе
    tp := sdktrace.NewTracerProvider(
        sdktrace.WithResource(res),
        sdktrace.WithBatcher(exporter), // BatchSpanProcessor для production
        sdktrace.WithSampler(
            sdktrace.ParentBased(
                sdktrace.TraceIDRatioBased(0.1), // 10% в production
            ),
        ),
    )

    // 4. Глобальная регистрация
    otel.SetTracerProvider(tp)
    otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
        propagation.TraceContext{}, // W3C Trace Context
        propagation.Baggage{},     // W3C Baggage
    ))

    return tp, nil
}
```

**Сравнение с C#**:

```csharp
// C#: через builder pattern и DI
builder.Services.AddOpenTelemetry()
    .ConfigureResource(r => r
        .AddService("order-service", serviceVersion: "1.0.0"))
    .WithTracing(b => b
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddOtlpExporter(opts => opts.Endpoint = new Uri("http://otel-collector:4317")));
```

```go
// Go: явная инициализация в main()
tp, err := telemetry.InitTracer(ctx, "order-service", "1.0.0", "production")
if err != nil {
    log.Fatalf("не удалось инициализировать трейсинг: %v", err)
}
defer tp.Shutdown(ctx) // ОБЯЗАТЕЛЬНО: flush оставшихся spans
```

> ⚠️ **Всегда вызывайте `tp.Shutdown(ctx)` при остановке сервиса!** Без этого последние spans из BatchSpanProcessor не будут отправлены и потеряются. Используйте `defer` в `main()`.

#### Exporters

| Exporter | Пакет | Назначение |
|----------|-------|------------|
| **OTLP gRPC** | `otlptracegrpc` | OTel Collector (рекомендуется) |
| **OTLP HTTP** | `otlptracehttp` | OTel Collector через HTTP |
| **stdout** | `stdouttrace` | Development (вывод в консоль) |
| **Zipkin** | `otlptrace/zipkin` | Напрямую в Zipkin |

```go
// Development: вывод в stdout
import "go.opentelemetry.io/otel/exporters/stdout/stdouttrace"

exporter, _ := stdouttrace.New(stdouttrace.WithPrettyPrint())

// Production: OTLP через HTTP (если gRPC недоступен)
import "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"

exporter, _ := otlptracehttp.New(ctx,
    otlptracehttp.WithEndpoint("otel-collector:4318"),
    otlptracehttp.WithInsecure(),
)
```

> 💡 **OTLP (OpenTelemetry Protocol)** — рекомендуемый способ экспорта. Прямые Jaeger/Zipkin exporters устарели (deprecated). Вместо этого отправляйте через OTLP в OTel Collector, который маршрутизирует данные в Jaeger, Zipkin, Grafana Tempo и т.д.

#### Sampler и Propagator

```go
// Sampler: контролирует, какие трейсы записывать
sdktrace.NewTracerProvider(
    // Вариант 1: Фиксированный процент
    sdktrace.WithSampler(sdktrace.TraceIDRatioBased(0.1)), // 10%

    // Вариант 2: ParentBased (рекомендуется)
    // - Если родительский span sampled → sample
    // - Если нет родителя → используй root sampler
    sdktrace.WithSampler(
        sdktrace.ParentBased(sdktrace.TraceIDRatioBased(0.1)),
    ),

    // Вариант 3: Всегда (для dev/staging)
    sdktrace.WithSampler(sdktrace.AlwaysSample()),
)

// Propagator: как передавать trace context между сервисами
otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
    propagation.TraceContext{}, // W3C: traceparent, tracestate headers
    propagation.Baggage{},     // W3C: baggage header
))
```

#### Production-ready инициализация

Полная функция инициализации с поддержкой разных окружений:

```go
func InitTelemetry(ctx context.Context, cfg Config) (*sdktrace.TracerProvider, error) {
    res, err := resource.Merge(
        resource.Default(),
        resource.NewWithAttributes(
            semconv.SchemaURL,
            semconv.ServiceName(cfg.ServiceName),
            semconv.ServiceVersion(cfg.ServiceVersion),
            semconv.DeploymentEnvironmentName(cfg.Environment),
        ),
    )
    if err != nil {
        return nil, fmt.Errorf("resource: %w", err)
    }

    // Выбор exporter по окружению
    var exporter sdktrace.SpanExporter
    switch cfg.Environment {
    case "development":
        exporter, err = stdouttrace.New(stdouttrace.WithPrettyPrint())
    default:
        opts := []otlptracegrpc.Option{
            otlptracegrpc.WithEndpoint(cfg.OTLPEndpoint),
        }
        if cfg.OTLPInsecure {
            opts = append(opts, otlptracegrpc.WithInsecure())
        }
        exporter, err = otlptracegrpc.New(ctx, opts...)
    }
    if err != nil {
        return nil, fmt.Errorf("exporter: %w", err)
    }

    // Выбор sampler
    var sampler sdktrace.Sampler
    switch cfg.Environment {
    case "development", "staging":
        sampler = sdktrace.AlwaysSample()
    default:
        sampler = sdktrace.ParentBased(
            sdktrace.TraceIDRatioBased(cfg.SampleRate), // обычно 0.01-0.1
        )
    }

    // Выбор processor
    var processor sdktrace.SpanProcessor
    switch cfg.Environment {
    case "development":
        processor = sdktrace.NewSimpleSpanProcessor(exporter) // синхронный (для dev)
    default:
        processor = sdktrace.NewBatchSpanProcessor(exporter) // батчинг (для production)
    }

    tp := sdktrace.NewTracerProvider(
        sdktrace.WithResource(res),
        sdktrace.WithSpanProcessor(processor),
        sdktrace.WithSampler(sampler),
    )

    otel.SetTracerProvider(tp)
    otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
        propagation.TraceContext{},
        propagation.Baggage{},
    ))

    return tp, nil
}

type Config struct {
    ServiceName    string
    ServiceVersion string
    Environment    string  // "development", "staging", "production"
    OTLPEndpoint   string  // "otel-collector:4317"
    OTLPInsecure   bool
    SampleRate     float64 // 0.0-1.0
}
```

---

### Manual Instrumentation

#### Создание spans

```go
import (
    "context"

    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/codes"
    "go.opentelemetry.io/otel/trace"
)

// Tracer — обычно создаётся один на пакет
var tracer = otel.Tracer("myapp/order-service")

func (s *OrderService) CreateOrder(ctx context.Context, req CreateOrderRequest) (*Order, error) {
    // Создаём span — ВСЕГДА используйте defer span.End()!
    ctx, span := tracer.Start(ctx, "OrderService.CreateOrder",
        trace.WithSpanKind(trace.SpanKindInternal), // внутренняя операция
    )
    defer span.End()

    // Добавляем атрибуты
    span.SetAttributes(
        attribute.String("order.customer_id", req.CustomerID),
        attribute.Int("order.items_count", len(req.Items)),
        attribute.Float64("order.total", req.Total),
    )

    // Валидация (вложенный span)
    if err := s.validateOrder(ctx, req); err != nil {
        span.RecordError(err) // записываем ошибку как event
        span.SetStatus(codes.Error, "валидация не пройдена")
        return nil, fmt.Errorf("валидация: %w", err)
    }

    // Создание заказа в БД
    order, err := s.repo.Create(ctx, req)
    if err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, "ошибка создания в БД")
        return nil, fmt.Errorf("создание: %w", err)
    }

    span.SetAttributes(attribute.String("order.id", order.ID))
    span.SetStatus(codes.Ok, "")

    return order, nil
}
```

> 💡 **Всегда вызывайте `defer span.End()`** сразу после `tracer.Start()`. Без `End()` span не будет отправлен и "зависнет" в памяти. Паттерн `ctx, span := tracer.Start(ctx, "name"); defer span.End()` — идиома Go для трейсинга.

#### Атрибуты, события, ошибки

```go
func (s *OrderService) processPayment(ctx context.Context, order *Order) error {
    ctx, span := tracer.Start(ctx, "OrderService.processPayment",
        trace.WithSpanKind(trace.SpanKindClient), // вызываем внешний сервис
    )
    defer span.End()

    // Атрибуты — статическая информация о span
    span.SetAttributes(
        attribute.String("payment.method", order.PaymentMethod),
        attribute.String("payment.currency", "RUB"),
        attribute.Float64("payment.amount", order.Total),
    )

    // Событие — временная метка внутри span
    span.AddEvent("начало обращения к платёжному шлюзу")

    result, err := s.paymentClient.Charge(ctx, order)
    if err != nil {
        // RecordError добавляет event с exception details
        span.RecordError(err, trace.WithAttributes(
            attribute.String("payment.gateway", "stripe"),
        ))
        span.SetStatus(codes.Error, err.Error())
        return fmt.Errorf("платёж: %w", err)
    }

    // Событие об успешном завершении
    span.AddEvent("платёж подтверждён", trace.WithAttributes(
        attribute.String("payment.transaction_id", result.TransactionID),
    ))

    span.SetStatus(codes.Ok, "")
    return nil
}
```

**SpanKind** — указывает роль span в trace:

| SpanKind | Описание | Пример |
|----------|----------|--------|
| `SpanKindClient` | Исходящий вызов | HTTP client, gRPC client |
| `SpanKindServer` | Входящий вызов | HTTP server, gRPC server |
| `SpanKindProducer` | Отправка сообщения | Kafka producer |
| `SpanKindConsumer` | Получение сообщения | Kafka consumer |
| `SpanKindInternal` | Внутренняя операция (default) | Бизнес-логика |

#### Вложенные spans

```go
func (s *OrderService) CreateOrder(ctx context.Context, req CreateOrderRequest) (*Order, error) {
    ctx, span := tracer.Start(ctx, "OrderService.CreateOrder")
    defer span.End()

    // Каждый вызов с ctx создаёт дочерний span
    if err := s.validateOrder(ctx, req); err != nil { // ← child span
        return nil, err
    }

    order, err := s.repo.Create(ctx, req) // ← child span
    if err != nil {
        return nil, err
    }

    if err := s.processPayment(ctx, order); err != nil { // ← child span
        return nil, err
    }

    s.notifyUser(ctx, order) // ← child span
    return order, nil
}

func (s *OrderService) validateOrder(ctx context.Context, req CreateOrderRequest) error {
    // Этот span будет дочерним для CreateOrder
    ctx, span := tracer.Start(ctx, "OrderService.validateOrder")
    defer span.End()

    // ... валидация
    return nil
}
```

Результат в Jaeger:
```
CreateOrder (150ms)
├── validateOrder (2ms)
├── repo.Create (15ms)
│   └── pgx.Query (10ms)  — auto-instrumented
├── processPayment (100ms)
│   └── HTTP POST /payments (95ms)  — auto-instrumented
└── notifyUser (5ms)
    └── NATS Publish (2ms)  — auto-instrumented
```

---

### Auto-Instrumentation

В Go нет "магической" auto-instrumentation как в .NET (где `.AddAspNetCoreInstrumentation()` подключается к DiagnosticSource). Вместо этого вы **явно оборачиваете** handlers и транспорты библиотеками-обёртками.

#### otelhttp: HTTP сервер и клиент

```go
import (
    "net/http"

    "go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
)

// === HTTP Server: оборачиваем handler ===
func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("GET /api/users", getUsers)
    mux.HandleFunc("GET /api/orders/{id}", getOrder)

    // otelhttp.NewHandler создаёт span для каждого входящего запроса
    handler := otelhttp.NewHandler(mux, "http-server",
        otelhttp.WithMessageEvents(otelhttp.ReadEvents, otelhttp.WriteEvents),
    )

    http.ListenAndServe(":8080", handler)
}

// === HTTP Client: оборачиваем Transport ===
func newHTTPClient() *http.Client {
    return &http.Client{
        Transport: otelhttp.NewTransport(http.DefaultTransport),
        Timeout:   10 * time.Second,
    }
}

// Каждый исходящий запрос автоматически:
// 1. Создаёт span с kind=Client
// 2. Пропагирует trace context через W3C headers (traceparent)
// 3. Записывает status code, размер тела
func callPaymentService(ctx context.Context, orderID string) error {
    client := newHTTPClient()

    req, _ := http.NewRequestWithContext(ctx, "GET",
        "http://payment-service:8081/payments/"+orderID, nil)

    // trace context автоматически добавится в headers
    resp, err := client.Do(req)
    if err != nil {
        return err
    }
    defer resp.Body.Close()
    return nil
}
```

**Сравнение с C#**:

```csharp
// C#: одна строка для всех HTTP
builder.Services.AddOpenTelemetry()
    .WithTracing(b => b
        .AddAspNetCoreInstrumentation()      // входящие
        .AddHttpClientInstrumentation());     // исходящие
```

```go
// Go: явная обёртка каждого handler и client
handler := otelhttp.NewHandler(mux, "server")               // входящие
transport := otelhttp.NewTransport(http.DefaultTransport)    // исходящие
```

#### otelgrpc, otelsql, redisotel

Для других протоколов и библиотек существуют аналогичные обёртки:

```go
// gRPC Server (подробнее в разделе 4.4)
import "go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc"

grpcServer := grpc.NewServer(
    grpc.StatsHandler(otelgrpc.NewServerHandler()),
)

// gRPC Client
conn, _ := grpc.NewClient("localhost:50051",
    grpc.WithStatsHandler(otelgrpc.NewClientHandler()),
)

// database/sql
import "github.com/XSAM/otelsql"

db, _ := otelsql.Open("postgres", dsn,
    otelsql.WithAttributes(semconv.DBSystemPostgreSQL),
)

// pgx (подробнее в разделе 4.1)
// pgx поддерживает QueryTracer — трейсинг встроен
poolCfg, _ := pgxpool.ParseConfig(dsn)
poolCfg.ConnConfig.Tracer = otelpgx.NewTracer()

// Redis (подробнее в разделе 4.2)
import "github.com/redis/go-redis/extra/redisotel/v9"

rdb := redis.NewClient(&redis.Options{Addr: "localhost:6379"})
redisotel.InstrumentTracing(rdb)
redisotel.InstrumentMetrics(rdb)
```

**Таблица доступных instrumentation библиотек**:

| Библиотека | OTel пакет | Что инструментирует |
|------------|-----------|---------------------|
| `net/http` | `otelhttp` | HTTP server/client |
| `google.golang.org/grpc` | `otelgrpc` | gRPC server/client |
| `database/sql` | `otelsql` | SQL queries |
| `pgx` | `otelpgx` / QueryTracer | PostgreSQL |
| `go-redis` | `redisotel` | Redis operations |
| `segmentio/kafka-go` | Manual propagation | Kafka produce/consume |
| `nats.go` | Manual propagation | NATS publish/subscribe |

> 💡 **Для Kafka и NATS** нет готовых OTel-обёрток — trace context нужно пропагировать вручную через message headers. Примеры этого показаны в разделе [4.3 Очереди сообщений](./03_message_queues.md).

---

### Jaeger и Zipkin

**Jaeger** (от Uber) и **Zipkin** (от Twitter) — два наиболее популярных backend'а для хранения и визуализации трейсов.

#### Docker Compose для локальной разработки

```yaml
# docker-compose.yml — минимальный стек для трейсинга
services:
  # Jaeger all-in-one (UI + Collector + Storage)
  jaeger:
    image: jaegertracing/all-in-one:1.55
    ports:
      - "16686:16686"  # Jaeger UI
      - "4317:4317"    # OTLP gRPC receiver
      - "4318:4318"    # OTLP HTTP receiver
    environment:
      - COLLECTOR_OTLP_ENABLED=true

  # Альтернатива: Zipkin
  # zipkin:
  #   image: openzipkin/zipkin:3
  #   ports:
  #     - "9411:9411"  # Zipkin UI + API
```

С Jaeger all-in-one ваш Go-сервис может отправлять трейсы напрямую через OTLP:

```go
exporter, _ := otlptracegrpc.New(ctx,
    otlptracegrpc.WithEndpoint("localhost:4317"),
    otlptracegrpc.WithInsecure(),
)
```

Трейсы доступны в UI: `http://localhost:16686`

#### Jaeger vs Zipkin

| Аспект | Jaeger | Zipkin |
|--------|--------|--------|
| Разработчик | Uber → CNCF | Twitter |
| UI | Богатый (service map, comparison) | Простой |
| Storage | Cassandra, Elasticsearch, Kafka, Memory | MySQL, Cassandra, Elasticsearch, Memory |
| OTLP поддержка | Встроена | Через OTel Collector |
| Production-ready | Да (graduated CNCF) | Да |
| Deployment | Сложнее (несколько компонентов) | Проще (single binary) |

> 💡 **Рекомендация**: Для production используйте **Grafana Tempo** — он интегрируется с Grafana, Loki и Prometheus, обеспечивая единую платформу для всех трёх столпов. Jaeger отлично подходит для локальной разработки (all-in-one Docker image).

---

### OpenTelemetry Collector

OTel Collector — промежуточный компонент между вашими сервисами и backend'ами (Jaeger, Prometheus, Loki). Он **декаплит** сервисы от конкретных backend'ов.

```
┌──────────┐   OTLP   ┌───────────────┐   Jaeger    ┌──────────┐
│ Service A │─────────→│               │────────────→│  Jaeger  │
└──────────┘          │  OTel         │             └──────────┘
                      │  Collector    │   Prometheus  ┌──────────┐
┌──────────┐   OTLP   │               │────────────→│Prometheus│
│ Service B │─────────→│               │             └──────────┘
└──────────┘          │               │   Loki       ┌──────────┐
                      │               │────────────→│  Loki    │
                      └───────────────┘             └──────────┘
```

**Зачем нужен Collector**:
- Сервисы знают только про OTLP — не зависят от Jaeger/Zipkin/Datadog
- Centralised processing: batching, retry, sampling
- Легко сменить backend без изменения кода сервисов
- Может обогащать данные (добавлять labels, фильтровать)

#### Конфигурация

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
    timeout: 5s
    send_batch_size: 1024

  # Фильтрация: убрать health check трейсы
  filter:
    traces:
      span:
        - 'attributes["http.target"] == "/healthz"'
        - 'attributes["http.target"] == "/readyz"'

  # Добавление атрибутов
  attributes:
    actions:
      - key: environment
        value: production
        action: upsert

exporters:
  # Трейсы → Jaeger
  otlp/jaeger:
    endpoint: jaeger:4317
    tls:
      insecure: true

  # Метрики → Prometheus (Collector экспонирует /metrics)
  prometheus:
    endpoint: 0.0.0.0:8889

  # Логи → Loki (через OTLP)
  otlphttp/loki:
    endpoint: http://loki:3100/otlp

  # Debug: вывод в консоль
  debug:
    verbosity: detailed

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [filter, attributes, batch]
      exporters: [otlp/jaeger]

    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]

    logs:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlphttp/loki]
```

**Паттерны деплоя**:

| Паттерн | Описание | Когда использовать |
|---------|----------|--------------------|
| **Agent** (sidecar) | Collector рядом с каждым сервисом | Kubernetes (DaemonSet/Sidecar) |
| **Gateway** | Централизованный Collector | Небольшие деплои, dev/staging |
| **Agent + Gateway** | Два уровня | Крупные production системы |

```yaml
# Kubernetes: Collector как DaemonSet
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: otel-collector-agent
spec:
  template:
    spec:
      containers:
        - name: otel-collector
          image: otel/opentelemetry-collector-contrib:0.96.0
          args: ["--config=/conf/otel-collector-config.yaml"]
          ports:
            - containerPort: 4317  # OTLP gRPC
            - containerPort: 4318  # OTLP HTTP
```

---

## Интеграция трёх столпов

Настоящая сила observability проявляется, когда логи, метрики и трейсы **связаны между собой**. Увидели аномалию на графике метрик → перешли к трейсу → нашли конкретные логи с ошибкой.

### Корреляция логов и трейсов

Добавление `trace_id` и `span_id` в каждую запись лога позволяет искать все логи конкретного запроса:

```go
// OTelHandler — уже был показан в разделе slog, здесь полная версия
package logging

import (
    "context"
    "log/slog"

    "go.opentelemetry.io/otel/trace"
)

// NewCorrelatedLogger создаёт slog.Logger с автоматической корреляцией
func NewCorrelatedLogger(baseHandler slog.Handler) *slog.Logger {
    return slog.New(&correlationHandler{inner: baseHandler})
}

type correlationHandler struct {
    inner slog.Handler
}

func (h *correlationHandler) Enabled(ctx context.Context, level slog.Level) bool {
    return h.inner.Enabled(ctx, level)
}

func (h *correlationHandler) Handle(ctx context.Context, r slog.Record) error {
    span := trace.SpanFromContext(ctx)
    if span.SpanContext().IsValid() {
        r.AddAttrs(
            slog.String("trace_id", span.SpanContext().TraceID().String()),
            slog.String("span_id", span.SpanContext().SpanID().String()),
            slog.Bool("trace_sampled", span.SpanContext().IsSampled()),
        )
    }
    return h.inner.Handle(ctx, r)
}

func (h *correlationHandler) WithAttrs(attrs []slog.Attr) slog.Handler {
    return &correlationHandler{inner: h.inner.WithAttrs(attrs)}
}

func (h *correlationHandler) WithGroup(name string) slog.Handler {
    return &correlationHandler{inner: h.inner.WithGroup(name)}
}
```

Использование:

```go
func main() {
    // JSON handler + корреляция с трейсами
    baseHandler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
        Level: slog.LevelInfo,
    })
    logger := logging.NewCorrelatedLogger(baseHandler)
    slog.SetDefault(logger)
}

// Теперь все логи содержат trace_id:
// {"time":"...","level":"INFO","msg":"заказ создан","order_id":"123",
//  "trace_id":"abc123def456","span_id":"789ghi","trace_sampled":true}
```

**Workflow поиска проблемы**:
1. В Grafana видим spike error rate на графике метрик
2. Кликаем на exemplar → открывается трейс в Jaeger
3. В трейсе видим span с ошибкой
4. Копируем `trace_id` из span
5. В Loki/Kibana ищем: `{trace_id="abc123def456"}`
6. Находим все логи этого запроса — с полным контекстом

> 💡 **Для C# разработчиков**: В .NET `Activity.Current.TraceId` автоматически попадает в логи через scope `Microsoft.Extensions.Logging`. В Go нужно создать custom handler (как выше), но результат тот же — `trace_id` в каждом логе.

---

### Exemplars: связь метрик с трейсами

**Exemplars** — механизм Prometheus, позволяющий прикрепить `trace_id` к конкретной точке данных метрики. В Grafana при наведении на график вы видите ссылку на конкретный трейс.

```go
import (
    "github.com/prometheus/client_golang/prometheus"
    "go.opentelemetry.io/otel/trace"
)

// Middleware с exemplars
func (m *metricsMiddleware) HandlerWithExemplars(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()

        wrapped := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}
        next.ServeHTTP(wrapped, r)

        duration := time.Since(start).Seconds()
        path := normalizePath(r.URL.Path)

        // Извлекаем trace_id для exemplar
        span := trace.SpanFromContext(r.Context())
        if span.SpanContext().IsValid() {
            traceID := span.SpanContext().TraceID().String()

            // Histogram с exemplar
            m.requestDuration.WithLabelValues(r.Method, path).(prometheus.ExemplarObserver).
                ObserveWithExemplar(duration, prometheus.Labels{
                    "trace_id": traceID,
                })

            // Counter с exemplar
            status := strconv.Itoa(wrapped.statusCode)
            m.requestsTotal.WithLabelValues(r.Method, path, status).(prometheus.ExemplarAdder).
                AddWithExemplar(1, prometheus.Labels{
                    "trace_id": traceID,
                })
        } else {
            m.requestDuration.WithLabelValues(r.Method, path).Observe(duration)
            status := strconv.Itoa(wrapped.statusCode)
            m.requestsTotal.WithLabelValues(r.Method, path, status).Inc()
        }
    })
}
```

> 💡 Для работы exemplars в Grafana нужно: (1) Prometheus с `--enable-feature=exemplar-storage`, (2) endpoint `/metrics` с `EnableOpenMetrics: true`, (3) Grafana data source с включенной опцией Exemplars и ссылкой на Jaeger/Tempo.

---

### Context Propagation между сервисами

Trace context пропагируется между сервисами через стандартные механизмы:

```
┌──────────────┐  traceparent header  ┌──────────────┐  metadata   ┌──────────────┐
│  API Gateway │────────────────────→│ Order Service │───────────→│ User Service │
│  (HTTP)      │                      │  (HTTP→gRPC)  │  (gRPC)    │  (gRPC)      │
└──────────────┘                      └──────┬───────┘            └──────────────┘
                                             │
                                    kafka headers
                                             │
                                      ┌──────▼───────┐
                                      │Notification  │
                                      │Service (Kafka)│
                                      └──────────────┘
```

**HTTP**: W3C `traceparent` header (автоматически через `otelhttp`)
```
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
```

**gRPC**: `traceparent` в metadata (автоматически через `otelgrpc`)

**Kafka**: Через message headers (вручную):

```go
// Producer: инжектим trace context в kafka headers
import "go.opentelemetry.io/otel/propagation"

type kafkaHeaderCarrier []kafka.Header

func (c *kafkaHeaderCarrier) Get(key string) string {
    for _, h := range *c {
        if h.Key == key {
            return string(h.Value)
        }
    }
    return ""
}

func (c *kafkaHeaderCarrier) Set(key, value string) {
    *c = append(*c, kafka.Header{Key: key, Value: []byte(value)})
}

func (c *kafkaHeaderCarrier) Keys() []string {
    keys := make([]string, len(*c))
    for i, h := range *c {
        keys[i] = h.Key
    }
    return keys
}

// При отправке сообщения
func publishEvent(ctx context.Context, writer *kafka.Writer, event Event) error {
    headers := kafkaHeaderCarrier{}
    otel.GetTextMapPropagator().Inject(ctx, &headers)

    return writer.WriteMessages(ctx, kafka.Message{
        Key:     []byte(event.Key),
        Value:   event.Payload,
        Headers: headers,
    })
}

// Consumer: извлекаем trace context из kafka headers
func processMessage(msg kafka.Message) {
    headers := kafkaHeaderCarrier(msg.Headers)
    ctx := otel.GetTextMapPropagator().Extract(context.Background(), &headers)

    // ctx теперь содержит parent span → новые spans будут дочерними
    ctx, span := tracer.Start(ctx, "process-order-event",
        trace.WithSpanKind(trace.SpanKindConsumer),
    )
    defer span.End()

    // ... обработка сообщения
}
```

---

### Агрегация логов

В production логи должны собираться централизованно для поиска и анализа.

#### Grafana Loki

**Loki** — система агрегации логов от Grafana Labs. В отличие от ELK, Loki **не индексирует содержимое логов** — только labels. Это делает его значительно легче и дешевле.

```
┌──────────┐  stdout   ┌───────────┐  push    ┌──────────┐
│ Go App   │──────────→│ Promtail  │────────→│  Loki    │
│ (JSON)   │           │ (agent)   │          │          │
└──────────┘           └───────────┘          └────┬─────┘
                                                   │ LogQL
                                              ┌────▼─────┐
                                              │ Grafana  │
                                              └──────────┘
```

```yaml
# promtail-config.yaml
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
    relabel_configs:
      - source_labels: ['__meta_docker_container_name']
        target_label: 'container'
    pipeline_stages:
      - json:
          expressions:
            level: level
            trace_id: trace_id
      - labels:
          level:
          trace_id:
```

**LogQL запросы**:

```logql
# Все ошибки сервиса
{container="order-service"} |= "ERROR"

# JSON парсинг + фильтрация
{container="order-service"} | json | level="ERROR" | line_format "{{.msg}}"

# Поиск по trace_id
{container=~".*service.*"} | json | trace_id="abc123def456"

# Rate ошибок (metric from logs)
sum(rate({container="order-service"} | json | level="ERROR" [5m]))
```

#### ELK Stack (Elasticsearch + Logstash + Kibana)

Более тяжёлое решение, но с полнотекстовым поиском по содержимому логов:

```
Go App (stdout JSON) → Filebeat/Fluentd → Logstash → Elasticsearch → Kibana
```

> 💡 **Идиома Go**: Всегда логируйте в **stdout в JSON-формате**. Не пишите в файлы — контейнерная платформа (Docker, K8s) управляет логами. Promtail/Filebeat/Fluentd собирают логи из stdout контейнера и отправляют в Loki/ELK. Это стандартный подход [12-Factor App](https://12factor.net/logs).

**Сравнение Loki vs ELK**:

| Аспект | Grafana Loki | ELK Stack |
|--------|-------------|-----------|
| Индексация | Только labels | Полнотекстовая |
| Ресурсы | Лёгкий | Тяжёлый (Elasticsearch) |
| Стоимость | Дешевле | Дороже |
| Поиск | LogQL (по labels) | KQL (полнотекстовый) |
| Интеграция | Grafana (native) | Kibana |
| Масштабирование | Простое | Сложное |
| Рекомендация | Новые проекты с Grafana | Enterprise с существующим ELK |

---

## Health Checks и Readiness Probes

### Liveness vs Readiness vs Startup

В Kubernetes (и не только) сервисы должны отвечать на вопросы о своём состоянии через HTTP endpoints:

| Проба | Endpoint | Вопрос | При неудаче |
|-------|----------|--------|-------------|
| **Liveness** | `/healthz` | "Жив ли процесс?" | K8s перезапускает контейнер |
| **Readiness** | `/readyz` | "Готов принимать трафик?" | K8s убирает из Service endpoints |
| **Startup** | `/healthz` | "Запустился ли?" | K8s ждёт (не убивает) |

> 💡 **Для C# разработчиков**: В .NET это `builder.Services.AddHealthChecks().AddNpgsql().AddRedis()` + `app.MapHealthChecks("/healthz")`. В Go нет встроенного фреймворка — реализуем вручную или используем библиотеку.

### Реализация в Go

```go
package health

import (
    "context"
    "encoding/json"
    "net/http"
    "sync"
    "time"
)

// Checker проверяет здоровье зависимости
type Checker interface {
    Check(ctx context.Context) error
}

// CheckerFunc — адаптер для функций
type CheckerFunc func(ctx context.Context) error

func (f CheckerFunc) Check(ctx context.Context) error { return f(ctx) }

// Health — агрегатор health checks
type Health struct {
    mu       sync.RWMutex
    checkers map[string]Checker
    timeout  time.Duration
}

func New(timeout time.Duration) *Health {
    return &Health{
        checkers: make(map[string]Checker),
        timeout:  timeout,
    }
}

func (h *Health) Register(name string, checker Checker) {
    h.mu.Lock()
    defer h.mu.Unlock()
    h.checkers[name] = checker
}

type Status struct {
    Status  string            `json:"status"` // "healthy" или "unhealthy"
    Details map[string]Detail `json:"details,omitempty"`
}

type Detail struct {
    Status string `json:"status"`
    Error  string `json:"error,omitempty"`
}

func (h *Health) Check(ctx context.Context) Status {
    h.mu.RLock()
    defer h.mu.RUnlock()

    ctx, cancel := context.WithTimeout(ctx, h.timeout)
    defer cancel()

    status := Status{
        Status:  "healthy",
        Details: make(map[string]Detail, len(h.checkers)),
    }

    var wg sync.WaitGroup
    var mu sync.Mutex

    for name, checker := range h.checkers {
        wg.Add(1)
        go func(name string, checker Checker) {
            defer wg.Done()

            err := checker.Check(ctx)

            mu.Lock()
            defer mu.Unlock()

            if err != nil {
                status.Status = "unhealthy"
                status.Details[name] = Detail{Status: "unhealthy", Error: err.Error()}
            } else {
                status.Details[name] = Detail{Status: "healthy"}
            }
        }(name, checker)
    }

    wg.Wait()
    return status
}

// LivenessHandler — жив ли процесс (минимальная проверка)
func (h *Health) LivenessHandler() http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        w.WriteHeader(http.StatusOK)
        json.NewEncoder(w).Encode(map[string]string{"status": "alive"})
    })
}

// ReadinessHandler — готов ли принимать трафик
func (h *Health) ReadinessHandler() http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        status := h.Check(r.Context())

        w.Header().Set("Content-Type", "application/json")
        if status.Status == "healthy" {
            w.WriteHeader(http.StatusOK)
        } else {
            w.WriteHeader(http.StatusServiceUnavailable)
        }
        json.NewEncoder(w).Encode(status)
    })
}
```

Регистрация проверок:

```go
func main() {
    h := health.New(5 * time.Second)

    // PostgreSQL
    h.Register("postgresql", health.CheckerFunc(func(ctx context.Context) error {
        return db.PingContext(ctx)
    }))

    // Redis
    h.Register("redis", health.CheckerFunc(func(ctx context.Context) error {
        return rdb.Ping(ctx).Err()
    }))

    // Kafka
    h.Register("kafka", health.CheckerFunc(func(ctx context.Context) error {
        conn, err := kafka.DialContext(ctx, "tcp", "kafka:9092")
        if err != nil {
            return err
        }
        return conn.Close()
    }))

    mux := http.NewServeMux()
    mux.Handle("GET /healthz", h.LivenessHandler())
    mux.Handle("GET /readyz", h.ReadinessHandler())

    http.ListenAndServe(":8080", mux)
}
```

Ответ `/readyz`:
```json
{
    "status": "healthy",
    "details": {
        "postgresql": { "status": "healthy" },
        "redis": { "status": "healthy" },
        "kafka": { "status": "unhealthy", "error": "dial tcp: connection refused" }
    }
}
```

### Kubernetes интеграция

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
        - name: order-service
          image: order-service:latest
          ports:
            - containerPort: 8080
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /readyz
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 5
            failureThreshold: 3
          startupProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 0
            periodSeconds: 5
            failureThreshold: 30  # 30 * 5s = 2.5 минуты на запуск
```

> 💡 **Liveness vs Readiness**: Liveness проверяет "не завис ли процесс" (минимальная проверка). Readiness проверяет "готов ли принимать трафик" (все зависимости доступны). Если PostgreSQL недоступен — readiness = false (перестаём получать трафик), но liveness = true (не нужно перезапускать).

---

## SLI/SLO

### Service Level Indicators

**SLI** (Service Level Indicator) — количественная метрика, описывающая аспект качества сервиса.

| SLI | Формула | Пример |
|-----|---------|--------|
| **Availability** | Успешные запросы / Все запросы | 99.95% |
| **Latency** | % запросов < порога | 95% запросов < 200ms |
| **Throughput** | Запросов в секунду | > 1000 RPS |
| **Error rate** | Ошибочные запросы / Все запросы | < 0.1% |

### Service Level Objectives и Error Budgets

**SLO** (Service Level Objective) — целевое значение SLI.

| SLO | Допустимый downtime/month | Error budget |
|-----|--------------------------|--------------|
| 99% | 7.3 часа | 1% |
| 99.9% | 43.8 минуты | 0.1% |
| 99.95% | 21.9 минуты | 0.05% |
| 99.99% | 4.38 минуты | 0.01% |

**Error budget** — "бюджет ошибок". Если SLO = 99.9%, то 0.1% запросов могут быть неуспешными. Когда error budget исчерпан — приоритет на reliability, а не на новые фичи.

### Реализация SLI метрик в Go

```go
// SLI метрики для HTTP сервиса
var (
    sliRequestsTotal = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Namespace: "sli",
            Name:      "requests_total",
            Help:      "Все запросы (для расчёта availability SLI)",
        },
        []string{"status_class"}, // "2xx", "3xx", "4xx", "5xx"
    )

    sliRequestDuration = promauto.NewHistogram(
        prometheus.HistogramOpts{
            Namespace: "sli",
            Name:      "request_duration_seconds",
            Help:      "Длительность запросов (для расчёта latency SLI)",
            Buckets:   []float64{0.01, 0.025, 0.05, 0.1, 0.2, 0.5, 1},
        },
    )
)

// SLI middleware
func SLIMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        wrapped := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}

        next.ServeHTTP(wrapped, r)

        duration := time.Since(start).Seconds()
        statusClass := fmt.Sprintf("%dxx", wrapped.statusCode/100)

        sliRequestsTotal.WithLabelValues(statusClass).Inc()
        sliRequestDuration.Observe(duration)
    })
}
```

**PromQL запросы для SLO дашборда**:

```promql
# Availability SLI (% успешных запросов за 30 дней)
1 - (
  sum(increase(sli_requests_total{status_class=~"5xx"}[30d]))
  /
  sum(increase(sli_requests_total[30d]))
)

# Latency SLI (% запросов < 200ms за 30 дней)
sum(increase(sli_request_duration_seconds_bucket{le="0.2"}[30d]))
/
sum(increase(sli_request_duration_seconds_count[30d]))

# Error budget remaining (SLO = 99.9%)
1 - (
  sum(increase(sli_requests_total{status_class="5xx"}[30d]))
  / sum(increase(sli_requests_total[30d]))
  / (1 - 0.999)
)
# 1.0 = бюджет полный, 0.0 = бюджет исчерпан, < 0 = SLO нарушен

# Burn rate (скорость расходования бюджета)
sum(rate(sli_requests_total{status_class="5xx"}[1h]))
/ sum(rate(sli_requests_total[1h]))
/ (1 - 0.999)
# > 1 = расходуем бюджет быстрее, чем восполняем
```

---

## Production Concerns

### Влияние на производительность

Observability добавляет overhead. Важно понимать его масштаб:

| Компонент | Overhead | Память | Примечание |
|-----------|----------|--------|------------|
| slog (JSONHandler) | ~350 ns/op, ~3 allocs | Минимально | Основной overhead — I/O (запись в stdout) |
| zap (Logger) | ~200 ns/op, 0 allocs | Минимально | Zero-allocation design |
| Prometheus Counter/Gauge | ~20 ns/op | ~200 bytes/metric | Пренебрежимо мало |
| Prometheus Histogram | ~200 ns/op | ~1 KB/metric | Зависит от количества buckets |
| OTel span (sampled) | ~500 ns | ~2-5 KB/span | BatchProcessor буферизирует |
| OTel span (not sampled) | ~50 ns | ~0 | Только проверка sampling decision |
| otelhttp middleware | ~1-2 μs | ~5 KB/request | Создание span + attributes |

```go
// Benchmark: overhead observability middleware
func BenchmarkHandler(b *testing.B) {
    // Без observability
    b.Run("plain", func(b *testing.B) {
        handler := http.HandlerFunc(plainHandler)
        // ...
    })

    // С логированием + метриками + трейсингом
    b.Run("full-observability", func(b *testing.B) {
        handler := otelhttp.NewHandler(
            metricsMiddleware(
                loggingMiddleware(
                    http.HandlerFunc(plainHandler),
                ),
            ),
            "server",
        )
        // ...
    })
}

// Типичные результаты:
// BenchmarkHandler/plain-8              500000    2400 ns/op    512 B/op    4 allocs/op
// BenchmarkHandler/full-observability-8  300000    5100 ns/op   2048 B/op   18 allocs/op
// Overhead: ~2.7 μs/request (~0.003ms) — пренебрежимо для network-bound сервисов
```

> 💡 **Для сетевых сервисов** (HTTP, gRPC) overhead observability ничтожен по сравнению с latency сети (1-100ms). Но для CPU-intensive hot paths (обработка миллионов событий в секунду) — стоит профилировать и оптимизировать.

> ⚠️ **Трейсинг без sampling в production** может потреблять 50-200 MB RAM на сервис и генерировать терабайты данных в день. Всегда настраивайте sampling: `TraceIDRatioBased(0.01)` (1%) для high-traffic сервисов, `TraceIDRatioBased(0.1)` (10%) для low-traffic.

### Graceful Shutdown

При остановке сервиса необходимо **flush** все буферизированные данные:

```go
func main() {
    ctx, cancel := context.WithCancel(context.Background())

    // Инициализация
    tp, err := telemetry.InitTracer(ctx, "order-service", "1.0.0", "production")
    if err != nil {
        log.Fatal(err)
    }

    logger := logging.NewCorrelatedLogger(
        slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}),
    )
    slog.SetDefault(logger)

    // HTTP server
    srv := &http.Server{Addr: ":8080", Handler: mux}

    // Graceful shutdown
    go func() {
        sigCh := make(chan os.Signal, 1)
        signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
        <-sigCh

        slog.Info("получен сигнал завершения, начинаем graceful shutdown")

        // 1. Прекращаем принимать новые запросы
        shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 30*time.Second)
        defer shutdownCancel()

        if err := srv.Shutdown(shutdownCtx); err != nil {
            slog.Error("ошибка shutdown HTTP сервера", slog.String("error", err.Error()))
        }

        // 2. Flush оставшихся spans
        if err := tp.Shutdown(shutdownCtx); err != nil {
            slog.Error("ошибка shutdown TracerProvider", slog.String("error", err.Error()))
        }

        // 3. Финальный лог
        slog.Info("сервис остановлен")

        cancel()
    }()

    slog.Info("сервис запущен", slog.String("addr", ":8080"))
    if err := srv.ListenAndServe(); err != http.ErrServerClosed {
        log.Fatal(err)
    }

    <-ctx.Done()
}
```

> ⚠️ **Порядок shutdown важен**: сначала HTTP сервер (прекратить принимать запросы), затем TracerProvider (flush spans), затем остальные ресурсы (DB, Redis). Без `tp.Shutdown()` последние spans потеряются.

### Тестирование observability

#### Тестирование метрик

```go
func TestMetricsMiddleware(t *testing.T) {
    // Custom registry для изоляции теста
    reg := prometheus.NewRegistry()
    middleware := NewMetricsMiddleware(reg)

    handler := middleware.Handler(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        w.Write([]byte("ok"))
    }))

    // Выполняем запрос
    req := httptest.NewRequest("GET", "/api/users", nil)
    rec := httptest.NewRecorder()
    handler.ServeHTTP(rec, req)

    // Проверяем метрики
    metrics, err := reg.Gather()
    require.NoError(t, err)

    // Ищем http_requests_total
    var found bool
    for _, mf := range metrics {
        if mf.GetName() == "http_requests_total" {
            found = true
            require.Len(t, mf.GetMetric(), 1)
            require.Equal(t, float64(1), mf.GetMetric()[0].GetCounter().GetValue())
        }
    }
    require.True(t, found, "метрика http_requests_total не найдена")
}
```

#### Тестирование spans

```go
import (
    "go.opentelemetry.io/otel/sdk/trace/tracetest"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
)

func TestCreateOrder_TracesSpans(t *testing.T) {
    // In-memory exporter
    exporter := tracetest.NewInMemoryExporter()

    tp := sdktrace.NewTracerProvider(
        sdktrace.WithSyncer(exporter), // синхронный для тестов
        sdktrace.WithSampler(sdktrace.AlwaysSample()),
    )
    defer tp.Shutdown(context.Background())

    otel.SetTracerProvider(tp)

    // Выполняем операцию
    svc := NewOrderService(/* ... */)
    _, err := svc.CreateOrder(context.Background(), CreateOrderRequest{
        CustomerID: "user-1",
        Items:      []Item{{Name: "Widget", Qty: 1}},
    })
    require.NoError(t, err)

    // Проверяем spans
    spans := exporter.GetSpans()
    require.GreaterOrEqual(t, len(spans), 1)

    // Ищем root span
    var rootSpan tracetest.SpanStub
    for _, s := range spans {
        if s.Name == "OrderService.CreateOrder" {
            rootSpan = s
            break
        }
    }

    require.Equal(t, "OrderService.CreateOrder", rootSpan.Name)
    require.Equal(t, codes.Ok, rootSpan.Status.Code)

    // Проверяем атрибуты
    attrs := rootSpan.Attributes
    require.Contains(t, attrs, attribute.String("order.customer_id", "user-1"))
}
```

#### Тестирование slog handlers

```go
func TestOTelHandler_AddsTraceID(t *testing.T) {
    // Создаём буфер для захвата логов
    var buf bytes.Buffer
    baseHandler := slog.NewJSONHandler(&buf, nil)
    handler := logging.NewOTelHandler(baseHandler)
    logger := slog.New(handler)

    // Создаём span для получения trace context
    tp := sdktrace.NewTracerProvider()
    tracer := tp.Tracer("test")
    ctx, span := tracer.Start(context.Background(), "test-span")
    defer span.End()

    expectedTraceID := span.SpanContext().TraceID().String()

    // Логируем с контекстом
    logger.InfoContext(ctx, "тестовое сообщение")

    // Парсим JSON
    var logEntry map[string]interface{}
    err := json.Unmarshal(buf.Bytes(), &logEntry)
    require.NoError(t, err)

    // Проверяем trace_id
    assert.Equal(t, expectedTraceID, logEntry["trace_id"])
    assert.NotEmpty(t, logEntry["span_id"])
}
```

### Безопасность

```go
// 1. Не выставляйте /metrics публично
func main() {
    // Public API
    publicMux := http.NewServeMux()
    publicMux.Handle("/api/", apiHandler)

    // Internal endpoints (метрики, health, pprof)
    internalMux := http.NewServeMux()
    internalMux.Handle("GET /metrics", promhttp.Handler())
    internalMux.Handle("GET /healthz", healthHandler)
    internalMux.Handle("GET /debug/pprof/", http.DefaultServeMux)

    // Запускаем на разных портах
    go http.ListenAndServe(":8080", publicMux)    // public
    go http.ListenAndServe(":9090", internalMux)  // internal only
}
```

**Чек-лист безопасности observability**:

- ❌ Не логируйте пароли, токены, API keys, номера карт
- ❌ Не добавляйте PII (email, телефон, адрес) в span attributes
- ❌ Не выставляйте `/metrics` и `/debug/pprof/` публично
- ❌ Не используйте user ID как Prometheus label (high cardinality)
- ✅ Используйте redaction handler для чувствительных данных
- ✅ Разделяйте public и internal порты
- ✅ Используйте TLS для OTLP exporter в production
- ✅ Настройте аутентификацию для Grafana, Jaeger, Prometheus

---

## Практические примеры

### Пример 1: Full Observability Setup для HTTP сервиса

Полная инициализация всех трёх столпов observability для production HTTP-сервиса:

```go
package main

import (
    "context"
    "fmt"
    "log"
    "log/slog"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/collectors"
    "github.com/prometheus/client_golang/prometheus/promhttp"
    "go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    "go.opentelemetry.io/otel/propagation"
    "go.opentelemetry.io/otel/sdk/resource"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.26.0"
    "go.opentelemetry.io/otel/trace"
)

func main() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    // === 1. Логирование с корреляцией трейсов ===
    logger := initLogger()
    slog.SetDefault(logger)
    slog.Info("инициализация сервиса")

    // === 2. Трейсинг (OpenTelemetry) ===
    tp, err := initTracer(ctx)
    if err != nil {
        log.Fatalf("не удалось инициализировать трейсинг: %v", err)
    }

    // === 3. Метрики (Prometheus) ===
    reg := prometheus.NewRegistry()
    reg.MustRegister(collectors.NewGoCollector())
    reg.MustRegister(collectors.NewProcessCollector(collectors.ProcessCollectorOpts{}))
    metrics := initMetrics(reg)

    // === 4. Health checks ===
    health := initHealthChecks()

    // === 5. HTTP роутер ===
    mux := http.NewServeMux()

    // API endpoints (с трейсингом через otelhttp)
    mux.Handle("GET /api/orders", otelhttp.WithRouteTag("/api/orders",
        http.HandlerFunc(listOrders)))
    mux.Handle("GET /api/orders/{id}", otelhttp.WithRouteTag("/api/orders/{id}",
        http.HandlerFunc(getOrder)))
    mux.Handle("POST /api/orders", otelhttp.WithRouteTag("/api/orders",
        http.HandlerFunc(createOrder)))

    // Observability middleware stack
    handler := otelhttp.NewHandler(           // трейсинг
        metrics.Handler(                       // метрики
            LoggingMiddleware(logger)(mux),     // логирование
        ),
        "order-service",
    )

    // === 6. Internal endpoints (на отдельном порту) ===
    internalMux := http.NewServeMux()
    internalMux.Handle("GET /metrics", promhttp.HandlerFor(reg, promhttp.HandlerOpts{
        EnableOpenMetrics: true,
    }))
    internalMux.Handle("GET /healthz", health.LivenessHandler())
    internalMux.Handle("GET /readyz", health.ReadinessHandler())

    // === 7. Запуск серверов ===
    publicSrv := &http.Server{Addr: ":8080", Handler: handler}
    internalSrv := &http.Server{Addr: ":9090", Handler: internalMux}

    go func() {
        slog.Info("internal endpoints запущены", slog.String("addr", ":9090"))
        if err := internalSrv.ListenAndServe(); err != http.ErrServerClosed {
            log.Fatal(err)
        }
    }()

    go func() {
        slog.Info("API сервер запущен", slog.String("addr", ":8080"))
        if err := publicSrv.ListenAndServe(); err != http.ErrServerClosed {
            log.Fatal(err)
        }
    }()

    // === 8. Graceful shutdown ===
    sigCh := make(chan os.Signal, 1)
    signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
    <-sigCh

    slog.Info("получен сигнал завершения")

    shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer shutdownCancel()

    // Порядок shutdown:
    // 1. HTTP серверы (прекратить принимать запросы)
    publicSrv.Shutdown(shutdownCtx)
    internalSrv.Shutdown(shutdownCtx)

    // 2. TracerProvider (flush оставшихся spans)
    if err := tp.Shutdown(shutdownCtx); err != nil {
        slog.Error("ошибка shutdown TracerProvider", slog.String("error", err.Error()))
    }

    slog.Info("сервис остановлен")
}

// initLogger создаёт slog.Logger с JSON output и корреляцией трейсов
func initLogger() *slog.Logger {
    jsonHandler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
        Level:     slog.LevelInfo,
        AddSource: true,
        ReplaceAttr: func(groups []string, a slog.Attr) slog.Attr {
            if a.Key == slog.TimeKey {
                a.Key = "timestamp"
            }
            if a.Key == "password" || a.Key == "token" || a.Key == "secret" {
                a.Value = slog.StringValue("***REDACTED***")
            }
            return a
        },
    })

    // Обёртка для корреляции с trace_id/span_id
    return slog.New(&correlationHandler{inner: jsonHandler})
}

type correlationHandler struct{ inner slog.Handler }

func (h *correlationHandler) Enabled(ctx context.Context, l slog.Level) bool {
    return h.inner.Enabled(ctx, l)
}
func (h *correlationHandler) Handle(ctx context.Context, r slog.Record) error {
    span := trace.SpanFromContext(ctx)
    if span.SpanContext().IsValid() {
        r.AddAttrs(
            slog.String("trace_id", span.SpanContext().TraceID().String()),
            slog.String("span_id", span.SpanContext().SpanID().String()),
        )
    }
    return h.inner.Handle(ctx, r)
}
func (h *correlationHandler) WithAttrs(attrs []slog.Attr) slog.Handler {
    return &correlationHandler{inner: h.inner.WithAttrs(attrs)}
}
func (h *correlationHandler) WithGroup(name string) slog.Handler {
    return &correlationHandler{inner: h.inner.WithGroup(name)}
}

// initTracer создаёт OpenTelemetry TracerProvider
func initTracer(ctx context.Context) (*sdktrace.TracerProvider, error) {
    res, err := resource.Merge(resource.Default(), resource.NewWithAttributes(
        semconv.SchemaURL,
        semconv.ServiceName("order-service"),
        semconv.ServiceVersion("1.0.0"),
        semconv.DeploymentEnvironmentName(os.Getenv("ENV")),
    ))
    if err != nil {
        return nil, fmt.Errorf("resource: %w", err)
    }

    exporter, err := otlptracegrpc.New(ctx,
        otlptracegrpc.WithEndpoint(getEnv("OTEL_ENDPOINT", "localhost:4317")),
        otlptracegrpc.WithInsecure(),
    )
    if err != nil {
        return nil, fmt.Errorf("exporter: %w", err)
    }

    tp := sdktrace.NewTracerProvider(
        sdktrace.WithResource(res),
        sdktrace.WithBatcher(exporter),
        sdktrace.WithSampler(sdktrace.ParentBased(sdktrace.TraceIDRatioBased(0.1))),
    )

    otel.SetTracerProvider(tp)
    otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
        propagation.TraceContext{},
        propagation.Baggage{},
    ))

    return tp, nil
}

func getEnv(key, fallback string) string {
    if v := os.Getenv(key); v != "" {
        return v
    }
    return fallback
}
```

> 💡 **Для C# разработчиков**: Это аналог `Program.cs` с `builder.Services.AddOpenTelemetry()` + `builder.Services.AddHealthChecks()` + `builder.Host.UseSerilog()`. В Go больше кода, но каждый шаг явный и прозрачный.

---

### Пример 2: Distributed Tracing между микросервисами

Два сервиса с пропагацией trace context через gRPC:

```go
// === Service A: API Gateway (HTTP → gRPC) ===
package main

import (
    "context"
    "log/slog"

    "go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc"
    "go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/codes"
    "google.golang.org/grpc"

    userpb "example.com/proto/user"
)

var tracer = otel.Tracer("api-gateway")

func getOrderHandler(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()

    // Span создан автоматически otelhttp (parent)
    orderID := r.PathValue("id")

    // 1. Бизнес-логика span
    ctx, span := tracer.Start(ctx, "getOrder.business-logic")
    span.SetAttributes(attribute.String("order.id", orderID))

    // 2. gRPC вызов к User Service (trace context пропагируется автоматически)
    userConn, _ := grpc.NewClient("user-service:50051",
        grpc.WithStatsHandler(otelgrpc.NewClientHandler()), // auto-instrumentation
        grpc.WithInsecure(),
    )
    defer userConn.Close()

    userClient := userpb.NewUserServiceClient(userConn)
    user, err := userClient.GetUser(ctx, &userpb.GetUserRequest{Id: "user-123"})
    if err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, "ошибка получения пользователя")
        slog.ErrorContext(ctx, "не удалось получить пользователя",
            slog.String("error", err.Error()))
        http.Error(w, "internal error", 500)
        span.End()
        return
    }

    slog.InfoContext(ctx, "заказ получен",
        slog.String("order_id", orderID),
        slog.String("user_name", user.GetName()),
    )
    // Лог будет содержать: trace_id, span_id, order_id, user_name

    span.SetStatus(codes.Ok, "")
    span.End()

    // ... формирование ответа
}
```

```go
// === Service B: User Service (gRPC Server) ===
package main

import (
    "context"
    "log/slog"

    "go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "google.golang.org/grpc"

    userpb "example.com/proto/user"
)

var tracer = otel.Tracer("user-service")

type userServer struct {
    userpb.UnimplementedUserServiceServer
    db     *pgxpool.Pool
    logger *slog.Logger
}

func (s *userServer) GetUser(ctx context.Context, req *userpb.GetUserRequest) (*userpb.GetUserResponse, error) {
    // Span создан автоматически otelgrpc (parent span от API Gateway)
    s.logger.InfoContext(ctx, "получение пользователя",
        slog.String("user_id", req.GetId()),
    )
    // Лог содержит тот же trace_id, что и в API Gateway!

    // Вложенный span для DB запроса
    ctx, span := tracer.Start(ctx, "db.GetUser")
    defer span.End()

    span.SetAttributes(attribute.String("db.statement", "SELECT * FROM users WHERE id = $1"))

    var user User
    err := s.db.QueryRow(ctx,
        "SELECT id, name, email FROM users WHERE id = $1", req.GetId(),
    ).Scan(&user.ID, &user.Name, &user.Email)
    if err != nil {
        span.RecordError(err)
        return nil, status.Errorf(codes.NotFound, "пользователь не найден")
    }

    return &userpb.GetUserResponse{
        Id:    user.ID,
        Name:  user.Name,
        Email: user.Email,
    }, nil
}

func main() {
    // ... init tracer, logger

    grpcServer := grpc.NewServer(
        grpc.StatsHandler(otelgrpc.NewServerHandler()), // auto-instrumentation
    )
    userpb.RegisterUserServiceServer(grpcServer, &userServer{db: pool, logger: logger})

    // ...
}
```

Результат в Jaeger UI:
```
Trace: abc-123-def-456
├── [api-gateway] GET /api/orders/42              (120ms)
│   ├── [api-gateway] getOrder.business-logic      (115ms)
│   │   └── [user-service] /user.UserService/GetUser (30ms)  ← gRPC propagation
│   │       └── [user-service] db.GetUser              (5ms)
```

Все логи обоих сервисов содержат `trace_id: "abc-123-def-456"` → можно найти в Loki одним запросом.

---

### Пример 3: Grafana Stack с Docker Compose

Полная observability инфраструктура для локальной разработки:

```yaml
# docker-compose.yml
services:
  # === Ваш Go сервис ===
  app:
    build: .
    ports:
      - "8080:8080"   # API
      - "9090:9090"   # metrics + health
    environment:
      - ENV=development
      - OTEL_ENDPOINT=otel-collector:4317
      - DB_URL=postgres://user:pass@postgres:5432/app?sslmode=disable
      - REDIS_URL=redis:6379
    depends_on:
      - postgres
      - redis
      - otel-collector

  # === OpenTelemetry Collector ===
  otel-collector:
    image: otel/opentelemetry-collector-contrib:0.96.0
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./configs/otel-collector-config.yaml:/etc/otel-collector-config.yaml
    ports:
      - "4317:4317"   # OTLP gRPC
      - "4318:4318"   # OTLP HTTP
      - "8889:8889"   # Prometheus exporter

  # === Jaeger (трейсы) ===
  jaeger:
    image: jaegertracing/all-in-one:1.55
    ports:
      - "16686:16686" # UI
    environment:
      - COLLECTOR_OTLP_ENABLED=true

  # === Prometheus (метрики) ===
  prometheus:
    image: prom/prometheus:v2.50.0
    volumes:
      - ./configs/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9091:9090"   # UI (9091 чтобы не конфликтовать с app)

  # === Loki (логи) ===
  loki:
    image: grafana/loki:2.9.4
    ports:
      - "3100:3100"

  # === Promtail (сбор логов из Docker) ===
  promtail:
    image: grafana/promtail:2.9.4
    volumes:
      - ./configs/promtail.yaml:/etc/promtail/config.yaml
      - /var/run/docker.sock:/var/run/docker.sock:ro
    command: -config.file=/etc/promtail/config.yaml

  # === Grafana (дашборды) ===
  grafana:
    image: grafana/grafana:10.3.1
    ports:
      - "3000:3000"   # UI
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_FEATURE_TOGGLES_ENABLE=traceqlEditor
    volumes:
      - ./configs/grafana/provisioning:/etc/grafana/provisioning

  # === Инфраструктура ===
  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=app

  redis:
    image: redis:7-alpine
```

```yaml
# configs/otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 5s
    send_batch_size: 1024

exporters:
  otlp/jaeger:
    endpoint: jaeger:4317
    tls:
      insecure: true
  prometheus:
    endpoint: 0.0.0.0:8889

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/jaeger]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]
```

```yaml
# configs/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  # Метрики Go-сервиса
  - job_name: 'app'
    static_configs:
      - targets: ['app:9090']

  # Метрики из OTel Collector
  - job_name: 'otel-collector'
    static_configs:
      - targets: ['otel-collector:8889']
```

```yaml
# configs/grafana/provisioning/datasources/datasources.yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    isDefault: true

  - name: Jaeger
    type: jaeger
    url: http://jaeger:16686

  - name: Loki
    type: loki
    url: http://loki:3100
    jsonData:
      derivedFields:
        - datasourceUid: jaeger
          matcherRegex: '"trace_id":"(\w+)"'
          name: TraceID
          url: '$${__value.raw}'
```

После `docker compose up`:
- **API**: http://localhost:8080
- **Grafana**: http://localhost:3000 (admin/admin)
- **Jaeger UI**: http://localhost:16686
- **Prometheus**: http://localhost:9091

В Grafana настроен автоматический переход из логов (Loki) в трейсы (Jaeger) по `trace_id`.

---

## Чек-лист

После изучения этого раздела вы должны уметь:

### Логирование
- [ ] Настроить `slog` с `JSONHandler` для production
- [ ] Понимать разницу между `slog`, `zap` и `zerolog` и выбрать подходящий
- [ ] Использовать typed attributes (`slog.String`, `slog.Int`) вместо `any`
- [ ] Настроить корреляцию логов с трейсами (trace_id, span_id) через custom handler
- [ ] Реализовать HTTP request logging middleware
- [ ] Настроить log rotation через `lumberjack` или вывод в stdout для контейнеров
- [ ] Реализовать маскирование чувствительных данных (PII redaction)
- [ ] Подключить zap или zerolog как backend для slog (через `zapslog` / `slog-zerolog`)
- [ ] Настроить динамическое управление уровнем логов (`slog.LevelVar`, `zap.AtomicLevel`)

### Метрики
- [ ] Настроить `prometheus/client_golang` с endpoint `/metrics`
- [ ] Использовать правильные типы метрик: Counter, Gauge, Histogram (не Summary)
- [ ] Реализовать HTTP middleware для RED-метрик (Rate, Errors, Duration)
- [ ] Добавить бизнес-метрики (orders_total, payments_amount)
- [ ] Настроить custom Histogram buckets под ваш SLA
- [ ] Избегать high cardinality labels (не использовать user_id, order_id)
- [ ] Написать PromQL запросы для rate, error rate, percentiles
- [ ] Настроить alerting rules в Prometheus
- [ ] Создать Grafana дашборд для Go-сервиса (RED + Go runtime)

### Трейсинг
- [ ] Настроить OpenTelemetry TracerProvider с OTLP exporter
- [ ] Инструментировать HTTP сервер через `otelhttp.NewHandler()`
- [ ] Инструментировать HTTP клиент через `otelhttp.NewTransport()`
- [ ] Инструментировать gRPC через `otelgrpc` StatsHandler
- [ ] Создавать вручную spans для бизнес-операций (`tracer.Start()`)
- [ ] Записывать ошибки в spans (`span.RecordError()`, `span.SetStatus()`)
- [ ] Настроить sampling для production (`ParentBased` + `TraceIDRatioBased`)
- [ ] Настроить W3C Trace Context propagation

### Интеграция трёх столпов
- [ ] Реализовать корреляцию логов и трейсов через trace_id в каждом логе
- [ ] Настроить Exemplars в Prometheus (связь метрик с трейсами)
- [ ] Пропагировать trace context через HTTP, gRPC и Kafka headers
- [ ] Настроить OpenTelemetry Collector (receivers → processors → exporters)
- [ ] Настроить Grafana с data sources: Prometheus, Jaeger/Tempo, Loki
- [ ] Обеспечить end-to-end trace через несколько микросервисов

### Health Checks
- [ ] Реализовать `/healthz` (liveness) и `/readyz` (readiness) endpoints
- [ ] Проверять зависимости (PostgreSQL, Redis, Kafka) в readiness
- [ ] Интегрировать health checks с Kubernetes probes
- [ ] Разделять liveness (процесс жив) и readiness (готов к трафику)

### SLI/SLO
- [ ] Определить SLI для сервиса (availability, latency, error rate)
- [ ] Установить SLO и вычислять error budget
- [ ] Реализовать SLI recording middleware
- [ ] Написать PromQL для SLO дашборда (error budget remaining, burn rate)

### Production
- [ ] Логировать в stdout в JSON формате
- [ ] Не логировать чувствительные данные (пароли, токены)
- [ ] Не выставлять `/metrics` и `/debug/pprof/` публично
- [ ] Настроить graceful shutdown для OTel TracerProvider (`tp.Shutdown()`)
- [ ] Тестировать метрики через custom registry
- [ ] Тестировать spans через `tracetest.NewInMemoryExporter()`
- [ ] Понимать overhead observability и профилировать при необходимости
- [ ] Настроить Docker Compose стек для локальной разработки (Jaeger + Prometheus + Grafana + Loki)

---

## Следующие шаги

Переходите к [4.6 Конфигурация](./06_config.md) — viper, envconfig, caarlos0/env, управление конфигурацией в production Go-приложениях.

---

**Вопросы?** Откройте issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Назад: 4.4 gRPC](./04_grpc.md) | [Вперёд: 4.6 Конфигурация →](./06_config.md)

