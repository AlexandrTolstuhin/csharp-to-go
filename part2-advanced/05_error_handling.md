# 2.5 Обработка ошибок (продвинутый уровень)

## Содержание
- [Введение](#введение)
- [Sentinel Errors vs Typed Errors](#sentinel-errors-vs-typed-errors)
  - [Sentinel Errors (экспортируемые переменные)](#sentinel-errors-экспортируемые-переменные)
  - [Typed Errors (кастомные типы)](#typed-errors-кастомные-типы)
  - [Сравнительная таблица](#сравнительная-таблица-sentinel-vs-typed)
  - [Hybrid подход (best practice)](#hybrid-подход-best-practice)
- [Custom Error Types с метаданными](#custom-error-types-с-метаданными)
  - [Коды ошибок](#коды-ошибок-для-grpcвнутренних-api)
  - [Fluent API для метаданных](#fluent-api-для-метаданных)
  - [HTTP status маппинг](#http-status-маппинг)
- [Panic/Recover: когда и как использовать](#panicrecover-когда-и-как-использовать)
  - [Сравнение Panic vs Exceptions](#сравнение-panic-vs-exceptions)
  - [Когда использовать panic](#когда-использовать-panic)
  - [Recover в middleware](#recover-в-middleware-защита-httpgrpc-сервера)
  - [Defer и panic](#defer-и-panic-порядок-выполнения)
- [Error Wrapping Chains](#error-wrapping-chains)
  - [Построение контекста](#построение-контекста-через-wrapping)
  - [Unwrapping цепочки](#unwrapping-цепочки)
  - [Stack traces с pkg/errors](#stack-traces-с-pkgerrors-опционально)
- [Стратегии обработки ошибок по слоям](#стратегии-обработки-ошибок-по-слоям)
  - [Repository слой](#repository-слой)
  - [Service слой](#service-слой)
  - [Handler слой](#handler-слой)
  - [Таблица: Где обрабатывать ошибки](#таблица-где-обрабатывать-ошибки)
- [Логирование ошибок](#логирование-ошибок)
  - [Где логировать](#где-логировать)
  - [Структурированное логирование (slog)](#структурированное-логирование-slog)
  - [Expected vs Unexpected errors](#expected-vs-unexpected-errors)
- [Идиоматичные паттерны для production](#идиоматичные-паттерны-для-production)
  - [Retry с exponential backoff](#retry-с-exponential-backoff)
  - [Error aggregation](#error-aggregation-несколько-горутин)
  - [Context для cancellation](#context-для-cancellation-cascading-errors)
- [Практические примеры](#практические-примеры)
  - [Пример 1: REST API с централизованной обработкой ошибок](#пример-1-rest-api-с-централизованной-обработкой-ошибок)
  - [Пример 2: Background Job с retry и DLQ](#пример-2-background-job-с-retry-и-dlq)
  - [Пример 3: gRPC сервис с error details](#пример-3-grpc-сервис-с-error-details)
  - [Пример 4: Observability — distributed tracing](#пример-4-observability--distributed-tracing)
- [Чек-лист](#чек-лист)

---

## Введение

В [разделе 1.3](../part1-basics/03_key_differences.md#error-handling-vs-exceptions) мы познакомились с базовой философией обработки ошибок в Go: **errors are values**, явные проверки, early return. Этот подход кардинально отличается от C# exceptions, но его простота — это только начало.

В продвинутом уровне мы рассмотрим:
- **Архитектурные паттерны**: как правильно обрабатывать ошибки в многослойных приложениях (Repository → Service → Handler)
- **Production-ready практики**: retry, dead letter queue, circuit breaker, observability
- **Типизированные vs sentinel ошибки**: когда какой подход использовать
- **Panic/recover**: правила безопасного использования
- **Логирование и метрики**: structured logging, error tracking

> 💡 **Для C# разработчиков**: В C# вы привыкли к автоматическим stack traces и глобальным exception handlers. В Go вы строите контекст вручную через error wrapping, но получаете **нулевую стоимость для happy path** и полный контроль над потоком выполнения. Для Senior разработчика важно понимать, как масштабировать этот подход на enterprise приложения.

### Сравнительная таблица: C# Enterprise vs Go Production-ready

| Аспект | C# (Enterprise) | Go (Production-ready) |
|--------|-----------------|----------------------|
| **Stack traces** | ✅ Автоматические (дорого) | ⚠️ Ручные через wrapping (дешево) |
| **Контекст ошибок** | Exception.Data (Dictionary) | Custom error types с полями |
| **Иерархия** | Наследование (InvalidOperationException : SystemException) | Композиция (errors.Is/As) |
| **HTTP маппинг** | Глобальный exception filter | Явный маппинг в handler/middleware |
| **Observability** | Exception telemetry (автоматически) | Structured logging + wrapping |
| **Стоимость (happy path)** | ✅ Нулевая | ✅ Нулевая (if err == nil) |
| **Стоимость (error path)** | ❌ Высокая (stack unwinding) | ✅ Низкая (return value) |
| **Явность** | ❌ Не видны в сигнатуре метода | ✅ Часть API (func() error) |
| **Retry логика** | Polly, exception filters | Явный код, exponential backoff |

---

## Sentinel Errors vs Typed Errors

В Go существует два основных подхода к созданию ошибок: **sentinel errors** (предопределенные переменные) и **typed errors** (кастомные типы). Понимание того, когда использовать каждый подход, критически важно для проектирования стабильного API.

### Sentinel Errors (экспортируемые переменные)

**Sentinel errors** — это глобальные переменные типа `error`, объявленные на уровне пакета. Они используются для представления **константных ошибок без дополнительного контекста**.

**Когда использовать**:
- Ошибки без дополнительных данных (просто факт ошибки)
- Публичный API пакета (стабильность)
- Сравнение через `errors.Is()`

**C# аналог**:
```csharp
// C#: Типизированные исключения без данных
public class UserNotFoundException : Exception
{
    public UserNotFoundException() : base("User not found") { }
}

// Использование
throw new UserNotFoundException();

// Проверка
catch (UserNotFoundException ex)
{
    return NotFound("User not found");
}
```

**Go идиоматично**:
```go
// Sentinel errors объявляются на уровне пакета
var (
    ErrUserNotFound    = errors.New("user not found")
    ErrInvalidPassword = errors.New("invalid password")
    ErrDuplicateEmail  = errors.New("email already exists")
)

// Использование
func GetUser(id int) (*User, error) {
    user := db.Find(id)
    if user == nil {
        return nil, ErrUserNotFound  // Без wrapping — это конечная ошибка
    }
    return user, nil
}

// Проверка в вызывающем коде
user, err := repo.GetUser(42)
if errors.Is(err, ErrUserNotFound) {
    return http.StatusNotFound, "user not found"
}
```

> 💡 **Идиома Go**: Экспортируй sentinel errors с префиксом `Err` (например, `ErrNotFound`). Это позволяет клиентам пакета проверять конкретные ошибки через `errors.Is()`.

**⚠️ Ограничения sentinel errors**:
1. **Нет дополнительного контекста**: Вы не знаете, какой именно пользователь не найден
2. **Сложно добавлять данные**: Изменение с `var ErrNotFound = errors.New("...")` на структуру — breaking change
3. **Один instance**: Все места кода возвращают одну и ту же переменную

### Typed Errors (кастомные типы)

**Typed errors** — это пользовательские типы, реализующие интерфейс `error`. Они позволяют добавлять **метаданные** (ID, код ошибки, HTTP статус и т.д.).

**Когда использовать**:
- Нужны метаданные (ID, код, поля)
- Внутренние ошибки пакета (гибкость)
- Сложная логика обработки на основе полей

**C# аналог**:
```csharp
// C#: Exception с полями
public class ValidationException : Exception
{
    public Dictionary<string, string[]> Errors { get; }

    public ValidationException(Dictionary<string, string[]> errors)
        : base("Validation failed")
    {
        Errors = errors;
    }
}

// Использование
var errors = new Dictionary<string, string[]>
{
    ["email"] = new[] { "Invalid format" },
    ["password"] = new[] { "Too short" }
};
throw new ValidationException(errors);

// Обработка
catch (ValidationException ex)
{
    return BadRequest(new { errors = ex.Errors });
}
```

**Go идиоматично**:
```go
// Typed error с метаданными
type ValidationError struct {
    Field   string
    Message string
    Value   interface{}
}

// Реализация интерфейса error
func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed: %s: %s", e.Field, e.Message)
}

// Использование
func ValidateEmail(email string) error {
    if !isValidEmail(email) {
        return &ValidationError{
            Field:   "email",
            Message: "invalid format",
            Value:   email,
        }
    }
    return nil
}

// Проверка с errors.As() — извлекает данные
func HandleError(err error) Response {
    var validationErr *ValidationError
    if errors.As(err, &validationErr) {
        return Response{
            Status: http.StatusBadRequest,
            Field:  validationErr.Field,
            Error:  validationErr.Message,
        }
    }

    return Response{
        Status: http.StatusInternalServerError,
        Error:  "internal error",
    }
}
```

> 💡 **Идиома Go**: Используй указатели для custom error types (`*ValidationError`), чтобы избежать лишних копирований. `errors.As()` требует указатель на указатель (`var e *ValidationError`).

### Сравнительная таблица: Sentinel vs Typed

| Критерий | Sentinel Errors | Typed Errors |
|----------|----------------|--------------|
| **Контекст** | ❌ Нет | ✅ Есть (поля структуры) |
| **Производительность** | ✅ Быстрее (одна аллокация при создании) | ⚠️ Аллокация на каждую ошибку |
| **Проверка** | `errors.Is(err, ErrNotFound)` | `errors.As(err, &validErr)` |
| **Wrapping** | ✅ Хорошо работает с fmt.Errorf | ⚠️ Требует внимания (Unwrap метод) |
| **API стабильность** | ✅ Легко добавлять новые | ⚠️ Изменение полей = breaking change |
| **Когда использовать** | Публичный API, простые случаи | Внутри пакета, нужны метаданные |
| **Примеры** | io.EOF, sql.ErrNoRows | net.OpError, os.PathError |

### Hybrid подход (best practice)

В production коде часто используется **комбинация**: sentinel errors для публичного API + typed errors для внутренней гибкости.

**Идиоматичный паттерн**:
```go
// Sentinel для публичного API (стабильность)
var ErrValidationFailed = errors.New("validation failed")

// Typed для внутреннего использования (гибкость)
type ValidationError struct {
    Errors map[string]string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed: %v", e.Errors)
}

// Функция возвращает wrapped sentinel + typed
func ValidateUser(user *User) error {
    errs := make(map[string]string)

    if user.Email == "" {
        errs["email"] = "required"
    }
    if len(user.Password) < 8 {
        errs["password"] = "must be at least 8 characters"
    }

    if len(errs) > 0 {
        // Wrapping: клиент проверяет sentinel, но может извлечь детали
        return fmt.Errorf("%w: %w", ErrValidationFailed, &ValidationError{Errors: errs})
    }

    return nil
}

// Клиентский код
func CreateUser(user *User) error {
    if err := ValidateUser(user); err != nil {
        // Проверяем sentinel (стабильный API)
        if errors.Is(err, ErrValidationFailed) {
            // Извлекаем детали (опционально)
            var validErr *ValidationError
            if errors.As(err, &validErr) {
                return BadRequest(validErr.Errors)
            }
        }
        return err
    }
    return nil
}
```

> 💡 **Идиома Go**: Экспортируй sentinel errors для стабильного API, используй typed errors внутри для гибкости. Клиенты пакета зависят от sentinel (стабильные), но могут извлечь детали через `errors.As()` (опционально).

---

## Custom Error Types с метаданными

Для enterprise приложений часто требуются ошибки с дополнительными данными: коды ошибок (для gRPC/внутренних API), HTTP статусы, метаданные для логирования. Рассмотрим, как проектировать такие типы идиоматично.

### Коды ошибок для gRPC/внутренних API

**C# подход**:
```csharp
// C#: Enum для кодов ошибок
public enum ErrorCode
{
    UserNotFound = 1001,
    InvalidPassword = 1002,
    DatabaseError = 2001
}

public class DomainException : Exception
{
    public ErrorCode Code { get; }
    public Dictionary<string, object> Metadata { get; }

    public DomainException(ErrorCode code, string message,
                          Dictionary<string, object> metadata = null)
        : base(message)
    {
        Code = code;
        Metadata = metadata ?? new Dictionary<string, object>();
    }
}

// Использование
throw new DomainException(
    ErrorCode.UserNotFound,
    "User not found",
    new Dictionary<string, object> { ["userId"] = 42 }
);

// Обработка
catch (DomainException ex)
{
    switch (ex.Code)
    {
        case ErrorCode.UserNotFound:
            return NotFound(ex.Message);
        case ErrorCode.DatabaseError:
            return StatusCode(500, "Database error");
    }
}
```

**Go подход**:
```go
// Определяем коды ошибок
type ErrorCode int

const (
    CodeUserNotFound ErrorCode = 1001
    CodeInvalidPassword ErrorCode = 1002
    CodeDatabaseError ErrorCode = 2001
)

// Кастомный тип ошибки
type DomainError struct {
    Code     ErrorCode
    Message  string
    Metadata map[string]interface{}
    Wrapped  error  // Вложенная ошибка для wrapping
}

func (e *DomainError) Error() string {
    if e.Wrapped != nil {
        return fmt.Sprintf("[%d] %s: %v", e.Code, e.Message, e.Wrapped)
    }
    return fmt.Sprintf("[%d] %s", e.Code, e.Message)
}

// Реализуем Unwrap для поддержки errors.Is/As
func (e *DomainError) Unwrap() error {
    return e.Wrapped
}

// Helper функция для создания
func NewDomainError(code ErrorCode, message string, wrapped error) *DomainError {
    return &DomainError{
        Code:     code,
        Message:  message,
        Wrapped:  wrapped,
        Metadata: make(map[string]interface{}),
    }
}

// Использование в repository
func (r *UserRepository) GetByID(id int) (*User, error) {
    user, err := r.db.QueryUser(id)
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, NewDomainError(CodeUserNotFound, "user not found", err).
                WithMetadata("user_id", id)
        }
        return nil, NewDomainError(CodeDatabaseError, "query failed", err).
            WithMetadata("user_id", id)
    }
    return user, nil
}

// Обработка в handler
func (h *Handler) GetUser(w http.ResponseWriter, r *http.Request) {
    user, err := h.service.GetUser(id)
    if err != nil {
        var domainErr *DomainError
        if errors.As(err, &domainErr) {
            switch domainErr.Code {
            case CodeUserNotFound:
                respondJSON(w, http.StatusNotFound, map[string]interface{}{
                    "code":    domainErr.Code,
                    "message": domainErr.Message,
                })
                return
            case CodeDatabaseError:
                h.logger.Error("database error", "metadata", domainErr.Metadata)
                respondJSON(w, http.StatusInternalServerError, map[string]interface{}{
                    "code":    domainErr.Code,
                    "message": "internal error",
                })
                return
            }
        }

        // Неизвестная ошибка
        respondJSON(w, http.StatusInternalServerError, map[string]interface{}{
            "message": "internal error",
        })
    }
}
```

### Fluent API для метаданных

**Идиома Go (builder pattern)**:
```go
// Метод для добавления метаданных (chainable)
func (e *DomainError) WithMetadata(key string, value interface{}) *DomainError {
    e.Metadata[key] = value
    return e
}

// Использование (chaining)
return NewDomainError(CodeUserNotFound, "user not found", err).
    WithMetadata("user_id", id).
    WithMetadata("requested_by", currentUser.ID).
    WithMetadata("timestamp", time.Now())
```

> 💡 **Идиома Go**: Методы, возвращающие `*T`, позволяют строить fluent API. Это удобно для конфигурирования объектов.

### HTTP status маппинг

Часто требуется мапить доменные ошибки на HTTP статусы. Добавим метод в `DomainError`:

```go
// Метод для получения HTTP статуса
func (e *DomainError) HTTPStatus() int {
    switch e.Code {
    case CodeUserNotFound:
        return http.StatusNotFound
    case CodeInvalidPassword:
        return http.StatusUnauthorized
    case CodeDatabaseError:
        return http.StatusInternalServerError
    default:
        return http.StatusInternalServerError
    }
}

// Middleware для автоматического маппинга
func ErrorToHTTP(err error) (int, map[string]interface{}) {
    var domainErr *DomainError
    if errors.As(err, &domainErr) {
        return domainErr.HTTPStatus(), map[string]interface{}{
            "code":     domainErr.Code,
            "message":  domainErr.Message,
            "metadata": domainErr.Metadata,
        }
    }

    // Неизвестная ошибка
    return http.StatusInternalServerError, map[string]interface{}{
        "message": "internal server error",
    }
}

// Использование в handler
func (h *Handler) GetUser(w http.ResponseWriter, r *http.Request) {
    user, err := h.service.GetUser(id)
    if err != nil {
        status, body := ErrorToHTTP(err)
        respondJSON(w, status, body)
        return
    }
    respondJSON(w, http.StatusOK, user)
}
```

---

## Panic/Recover: когда и как использовать

**Критически важно**: Panic в Go — это **НЕ exceptions**. Использовать panic следует только для невосстановимых ошибок.

### Сравнение Panic vs Exceptions

**C# exceptions (норма для контроля потока)**:
```csharp
// C#: Исключения — обычный механизм контроля потока
public User GetUser(int id)
{
    if (id <= 0)
        throw new ArgumentException("Invalid ID");

    var user = _db.Users.Find(id);
    if (user == null)
        throw new NotFoundException($"User {id} not found");

    return user;
}

// Использование
try
{
    var user = service.GetUser(id);
    return Ok(user);
}
catch (ArgumentException ex)
{
    return BadRequest(ex.Message);
}
catch (NotFoundException ex)
{
    return NotFound(ex.Message);
}
```

**Go panic (ТОЛЬКО для критических ошибок)**:
```go
// ❌ ПЛОХО: паника для бизнес-логики
func GetUser(id int) *User {
    if id <= 0 {
        panic("invalid ID")  // НЕТ! Это не критическая ошибка
    }

    user := db.Find(id)
    if user == nil {
        panic("user not found")  // НЕТ! Это ожидаемая ситуация
    }

    return user
}

// ✅ ХОРОШО: явные ошибки
func GetUser(id int) (*User, error) {
    if id <= 0 {
        return nil, fmt.Errorf("invalid ID: %d", id)
    }

    user := db.Find(id)
    if user == nil {
        return nil, fmt.Errorf("%w: id=%d", ErrUserNotFound, id)
    }

    return user, nil
}
```

> ⚠️ **Важно**: В C# exceptions дешевые для happy path, но дорогие при выбросе. В Go panic **всегда дорогая** (stack unwinding, восстановление состояния). Используйте panic только для программных ошибок (bugs), а не для ожидаемых ситуаций.

### Когда использовать panic

| Сценарий | Panic? | Решение | Почему |
|----------|--------|---------|--------|
| Невалидные аргументы | ❌ | Вернуть `error` | Ожидаемая ситуация |
| Бизнес-логика (запись не найдена) | ❌ | Вернуть `error` | Ожидаемая ситуация |
| Ошибка сети, БД | ❌ | Вернуть `error` | Ожидаемая ситуация |
| Невозможная ситуация (assertion) | ✅ | `panic("unreachable")` | Программная ошибка |
| Критическая ошибка инициализации | ✅ | `log.Fatal()` или `panic()` | Приложение не может работать |
| Nil dereference (баг в коде) | ✅ | Автоматически | Программная ошибка |
| Out of memory | ✅ | Автоматически | Система не может продолжить |

**Примеры правильного использования panic**:
```go
// ✅ Assertion (unreachable code)
func ProcessStatus(status Status) {
    switch status {
    case StatusActive, StatusInactive:
        // handle
    default:
        panic(fmt.Sprintf("unreachable: unknown status %v", status))
    }
}

// ✅ Критическая инициализация (обычно в init())
func init() {
    config, err := LoadConfig()
    if err != nil {
        panic(fmt.Sprintf("failed to load config: %v", err))
        // Или log.Fatal(err) — более явно
    }
    globalConfig = config
}

// ✅ Regexp compilation (compile-time check)
var emailRegex = regexp.MustCompile(`^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$`)
// MustCompile паникует если regex невалидный — это OK, т.к. это баг в коде
```

### Recover в middleware (защита HTTP/gRPC сервера)

Даже если вы не используете panic в своем коде, третьесторонние библиотеки или программные ошибки могут вызвать панику. Для защиты сервера используйте `recover` в middleware.

**C# аналог (global exception handler)**:
```csharp
// C#: Middleware для перехвата всех исключений
public class ExceptionMiddleware
{
    public async Task InvokeAsync(HttpContext context, RequestDelegate next)
    {
        try
        {
            await next(context);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unhandled exception");
            context.Response.StatusCode = 500;
            await context.Response.WriteAsJsonAsync(new { error = "Internal error" });
        }
    }
}
```

**Go паттерн (recover в HTTP middleware)**:
```go
func RecoverMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if rec := recover(); rec != nil {
                // Логируем stack trace
                stack := debug.Stack()
                log.Printf("PANIC recovered: %v\n%s", rec, stack)

                // Возвращаем 500
                w.Header().Set("Content-Type", "application/json")
                w.WriteHeader(http.StatusInternalServerError)
                json.NewEncoder(w).Encode(map[string]string{
                    "error": "internal server error",
                })
            }
        }()

        // Вызываем следующий handler
        next.ServeHTTP(w, r)
    })
}

// Использование
func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("/users", GetUsersHandler)

    // Оборачиваем в recover middleware
    http.ListenAndServe(":8080", RecoverMiddleware(mux))
}
```

> 💡 **Идиома Go**: Всегда защищай HTTP/gRPC серверы через recover middleware. Даже если твой код не паникует, third-party библиотеки могут.

### Defer и panic: порядок выполнения

**Механика**:
```go
func Example() {
    defer fmt.Println("defer 1")
    defer fmt.Println("defer 2")
    panic("error")
    defer fmt.Println("defer 3")  // Никогда не выполнится
}

// Вывод (defer выполняются в обратном порядке):
// defer 2
// defer 1
// panic: error
```

**Идиома: recover только в defer**:
```go
func SafeOperation() (err error) {
    defer func() {
        if r := recover(); r != nil {
            // Преобразуем panic в error
            err = fmt.Errorf("panic recovered: %v", r)
        }
    }()

    // Код, который может паниковать
    riskyCode()

    return nil
}
```

**⚠️ КРИТИЧЕСКИ ВАЖНО: Recover работает только в текущей горутине!**

```go
// ❌ НЕ РАБОТАЕТ
func Bad() {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("recovered")  // Никогда не выполнится!
        }
    }()

    go func() {
        panic("error")  // Упадет вся программа!
    }()

    time.Sleep(time.Second)
}

// ✅ ПРАВИЛЬНО: recover в каждой горутине
func Good() {
    go func() {
        defer func() {
            if r := recover(); r != nil {
                log.Printf("recovered in goroutine: %v", r)
            }
        }()

        panic("error")  // Будет пойман
    }()
}
```

> ⚠️ **Важно**: Если горутина паникует и нет recover, **вся программа упадет**. Всегда добавляй defer+recover в горутины, которые могут паниковать.

---

## Error Wrapping Chains

### Построение контекста через wrapping

В C# stack trace строится автоматически при выбросе exception. В Go вы **вручную строите контекст** через error wrapping, но это **дешево** и дает полный контроль.

**C# stack trace (автоматически)**:
```csharp
// C#: Автоматический stack trace
public User GetUser(int id)
{
    throw new Exception("Database error");
}

// Вывод:
// System.Exception: Database error
//    at UserRepository.GetUser(Int32 id) in UserRepository.cs:line 42
//    at UserService.FindUser(Int32 id) in UserService.cs:line 23
//    at UserController.GetUser(Int32 id) in UserController.cs:line 15
```

**Go wrapping (вручную, но дешево)**:
```go
// Repository слой
func (r *UserRepository) GetUser(id int) (*User, error) {
    row := r.db.QueryRow("SELECT * FROM users WHERE id = $1", id)
    var user User
    if err := row.Scan(&user); err != nil {
        // Добавляем контекст: что делали, с каким ID
        return nil, fmt.Errorf("scan user %d: %w", id, err)
    }
    return &user, nil
}

// Service слой
func (s *UserService) FindUser(id int) (*User, error) {
    user, err := s.repo.GetUser(id)
    if err != nil {
        // Добавляем контекст: на каком уровне
        return nil, fmt.Errorf("find user: %w", err)
    }
    return user, nil
}

// Handler слой
func (h *UserController) GetUser(w http.ResponseWriter, r *http.Request) {
    user, err := h.service.FindUser(id)
    if err != nil {
        // Ошибка содержит всю цепочку
        log.Printf("get user failed: %v", err)
        // Вывод: get user failed: find user: scan user 42: sql: no rows in result set

        // Проверяем конкретную ошибку
        if errors.Is(err, sql.ErrNoRows) {
            http.Error(w, "User not found", http.StatusNotFound)
            return
        }

        http.Error(w, "Internal error", http.StatusInternalServerError)
        return
    }
    json.NewEncoder(w).Encode(user)
}
```

> 💡 **Идиома Go**: Используй `fmt.Errorf("context: %w", err)` для wrapping. Флаг `%w` сохраняет возможность проверки через `errors.Is()` и `errors.As()`.

### Unwrapping цепочки

**Ручное unwrapping**:
```go
func PrintErrorChain(err error) {
    for err != nil {
        fmt.Println(err)
        err = errors.Unwrap(err)
    }
}

// Пример:
// find user: scan user 42: sql: no rows in result set
// scan user 42: sql: no rows in result set
// sql: no rows in result set
```

**Проверка вложенных ошибок**:
```go
// errors.Is проходит по всей цепочке
if errors.Is(err, sql.ErrNoRows) {
    // Сработает даже если ошибка обернута несколько раз
}

// errors.As извлекает typed error из цепочки
var netErr *net.OpError
if errors.As(err, &netErr) {
    // netErr теперь содержит конкретную сетевую ошибку
    fmt.Println("Network operation:", netErr.Op)
    fmt.Println("Network address:", netErr.Addr)
}
```

### Stack traces с pkg/errors (опционально)

Стандартная библиотека `errors` не добавляет stack traces. Для debugging можно использовать `github.com/pkg/errors`:

```go
import "github.com/pkg/errors"

func GetUser(id int) (*User, error) {
    user, err := db.Query(id)
    if err != nil {
        // errors.Wrap добавляет stack trace
        return nil, errors.Wrap(err, "query user")
    }
    return user, nil
}

// Вывод с stack trace (используй fmt %+v)
fmt.Printf("%+v", err)
// Вывод:
// query user
// main.GetUser
//     /path/to/file.go:42
// main.main
//     /path/to/main.go:15
// sql: no rows in result set
```

**⚠️ Trade-off**: Stack traces полезны для debugging, но:
- **Дороги**: каждая ошибка аллоцирует stack trace (heap allocation)
- **Избыточны** для production: structured logging с контекстом обычно лучше

> 💡 **Рекомендация для production**: Используй stdlib `errors` + structured logging с метаданными. pkg/errors полезен для локальной разработки и debugging.

---

## Стратегии обработки ошибок по слоям

В многослойных приложениях (Clean Architecture, Hexagonal Architecture) важно понимать, **где** и **как** обрабатывать ошибки на каждом уровне.

**Архитектура** (типичная):
```
Handler/Controller (HTTP/gRPC) — маппинг на статусы, логирование
       ↓
Service (бизнес-логика) — валидация, координация
       ↓
Repository (доступ к данным) — маппинг БД ошибок на доменные
```

### Repository слой

**Ответственность**:
- Мапить ошибки БД/внешних сервисов на **доменные ошибки**
- Добавлять контекст (ID, таблица, операция)
- **НЕ логировать** (логирование на краях системы)
- **НЕ мапить на HTTP** (repository не должен знать про HTTP)

**❌ ПЛОХО: пробрасываем сырые ошибки БД**:
```go
func (r *UserRepository) GetByID(id int) (*User, error) {
    return r.db.QueryUser(id)  // sql.ErrNoRows утечет наружу!
}

// Проблема: клиент зависит от деталей реализации (SQL)
// Если позже заменишь БД на MongoDB, клиентский код сломается
```

**✅ ХОРОШО: мапим на доменные ошибки**:
```go
// Доменные ошибки (объявлены на уровне пакета domain/repository)
var (
    ErrUserNotFound = errors.New("user not found")
    ErrDuplicateEmail = errors.New("email already exists")
)

func (r *UserRepository) GetByID(id int) (*User, error) {
    user, err := r.db.QueryUser(id)
    if err != nil {
        // Мапим SQL ошибку на доменную
        if errors.Is(err, sql.ErrNoRows) {
            return nil, fmt.Errorf("%w (id=%d)", ErrUserNotFound, id)
        }
        // Неизвестная ошибка — wrapping с контекстом
        return nil, fmt.Errorf("query user %d: %w", id, err)
    }
    return user, nil
}

func (r *UserRepository) Create(user *User) error {
    err := r.db.Insert(user)
    if err != nil {
        // Мапим constraint violation на доменную ошибку
        if isPgUniqueViolation(err, "users_email_key") {
            return fmt.Errorf("%w: %s", ErrDuplicateEmail, user.Email)
        }
        return fmt.Errorf("insert user: %w", err)
    }
    return nil
}

// Helper для проверки PostgreSQL ошибок
func isPgUniqueViolation(err error, constraint string) bool {
    var pgErr *pgconn.PgError
    if errors.As(err, &pgErr) {
        return pgErr.Code == "23505" && pgErr.ConstraintName == constraint
    }
    return false
}
```

**C# аналог**:
```csharp
// C#: Repository мапит EF исключения на доменные
public class UserRepository
{
    public async Task<User> GetByIdAsync(int id)
    {
        try
        {
            return await _context.Users.FindAsync(id);
        }
        catch (SqlException ex) when (ex.Number == 2627) // Unique constraint
        {
            throw new DuplicateEmailException("Email already exists", ex);
        }
        catch (SqlException ex)
        {
            throw new DatabaseException($"Failed to query user {id}", ex);
        }
    }
}
```

### Service слой

**Ответственность**:
- Бизнес-валидация
- Координация нескольких репозиториев/внешних сервисов
- Обогащение ошибок **бизнес-контекстом**
- **НЕ мапить на HTTP** (service не знает про HTTP)
- **НЕ логировать** (кроме критических случаев)

**Паттерн**:
```go
func (s *UserService) UpdateProfile(ctx context.Context, userID int, req UpdateProfileRequest) error {
    // 1. Валидация (бизнес-правила)
    if err := s.validator.Validate(req); err != nil {
        return fmt.Errorf("validation failed: %w", err)
    }

    // 2. Получение пользователя
    user, err := s.repo.GetByID(userID)
    if err != nil {
        // Обогащаем контекстом: кто пытался обновить
        return fmt.Errorf("get user for update (requested_by=%d): %w", userID, err)
    }

    // 3. Проверка бизнес-правил
    if user.IsBlocked {
        return fmt.Errorf("user %d is blocked and cannot update profile", userID)
    }

    // 4. Обновление
    user.Name = req.Name
    user.Email = req.Email

    if err := s.repo.Update(user); err != nil {
        return fmt.Errorf("update user %d: %w", userID, err)
    }

    // 5. Побочные эффекты (не критично)
    if err := s.emailService.SendUpdateNotification(user); err != nil {
        // НЕ возвращаем ошибку — профиль обновлен успешно
        // Но логируем на уровне WARNING
        s.logger.Warn("failed to send notification",
            "user_id", userID,
            "error", err)
    }

    return nil
}
```

**C# аналог**:
```csharp
// C#: Service координирует и валидирует
public class UserService
{
    public async Task UpdateProfileAsync(int userId, UpdateProfileRequest request)
    {
        // Валидация
        var validationResult = await _validator.ValidateAsync(request);
        if (!validationResult.IsValid)
            throw new ValidationException(validationResult.Errors);

        // Получение пользователя
        var user = await _repo.GetByIdAsync(userId);
        if (user == null)
            throw new UserNotFoundException(userId);

        // Бизнес-правила
        if (user.IsBlocked)
            throw new BusinessException("User is blocked");

        // Обновление
        user.Name = request.Name;
        user.Email = request.Email;
        await _repo.UpdateAsync(user);

        // Побочные эффекты (не критично)
        try
        {
            await _emailService.SendNotificationAsync(user);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to send notification");
            // Не пробрасываем
        }
    }
}
```

### Handler слой

**Ответственность**:
- Мапить доменные ошибки на **HTTP/gRPC статусы**
- **Логировать unexpected ошибки** (unknown errors)
- Возвращать клиенту **безопасные сообщения** (не раскрывать внутренние детали)
- Добавлять метрики (error counters)

**Паттерн (HTTP)**:
```go
type ErrorResponse struct {
    Error   string                 `json:"error"`
    Code    string                 `json:"code,omitempty"`
    Details map[string]interface{} `json:"details,omitempty"`
}

func (h *UserHandler) UpdateProfile(w http.ResponseWriter, r *http.Request) {
    var req UpdateProfileRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        h.respondError(w, http.StatusBadRequest, "invalid request body", nil)
        return
    }

    userID := getUserIDFromContext(r.Context())

    err := h.service.UpdateProfile(r.Context(), userID, req)
    if err != nil {
        h.handleServiceError(w, r, err)
        return
    }

    w.WriteHeader(http.StatusNoContent)
}

func (h *UserHandler) handleServiceError(w http.ResponseWriter, r *http.Request, err error) {
    // 1. Проверяем известные доменные ошибки
    switch {
    case errors.Is(err, ErrUserNotFound):
        h.respondError(w, http.StatusNotFound, "user not found", nil)
        return

    case errors.Is(err, ErrValidationFailed):
        var validErr *ValidationError
        if errors.As(err, &validErr) {
            h.respondError(w, http.StatusBadRequest, "validation failed", validErr.Errors)
            return
        }

    case errors.Is(err, ErrUnauthorized):
        h.respondError(w, http.StatusUnauthorized, "unauthorized", nil)
        return

    case errors.Is(err, ErrDuplicateEmail):
        h.respondError(w, http.StatusConflict, "email already exists", nil)
        return
    }

    // 2. Неизвестная ошибка — логируем детали, клиенту Generic message
    h.logger.Error("unexpected error",
        "path", r.URL.Path,
        "method", r.Method,
        "user_id", getUserIDFromContext(r.Context()),
        "error", fmt.Sprintf("%+v", err),  // Полная цепочка
    )

    // Метрики
    h.metrics.ErrorCounter.WithLabelValues("unexpected", r.URL.Path).Inc()

    h.respondError(w, http.StatusInternalServerError, "internal server error", nil)
}

func (h *UserHandler) respondError(w http.ResponseWriter, status int, message string, details map[string]interface{}) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(ErrorResponse{
        Error:   message,
        Details: details,
    })
}
```

**C# аналог (global exception filter)**:
```csharp
// C#: Централизованная обработка ошибок
public class GlobalExceptionFilter : IExceptionFilter
{
    public void OnException(ExceptionContext context)
    {
        var status = context.Exception switch
        {
            NotFoundException => 404,
            ValidationException => 400,
            UnauthorizedException => 401,
            DuplicateEmailException => 409,
            _ => 500
        };

        if (status == 500)
        {
            _logger.LogError(context.Exception, "Unhandled exception");
            context.Result = new ObjectResult(new { error = "Internal error" })
            {
                StatusCode = 500
            };
        }
        else
        {
            context.Result = new ObjectResult(new { error = context.Exception.Message })
            {
                StatusCode = status
            };
        }
    }
}
```

### Таблица: Где обрабатывать ошибки

| Слой | Что делать | Что НЕ делать |
|------|-----------|---------------|
| **Repository** | • Мапить БД ошибки на доменные<br>• Добавлять контекст (ID, таблица)<br>• Wrapping с fmt.Errorf | ❌ Логировать<br>❌ Мапить на HTTP статусы<br>❌ Знать про HTTP |
| **Service** | • Бизнес-валидация<br>• Координация репозиториев<br>• Обогащение бизнес-контекстом<br>• Wrapping ошибок | ❌ Мапить на HTTP<br>❌ Логировать (кроме критического)<br>❌ Знать про HTTP |
| **Handler** | • Мапить на HTTP/gRPC статусы<br>• Логировать unexpected errors<br>• Безопасные сообщения клиенту<br>• Метрики (error counters) | ❌ Бизнес-логика<br>❌ Прямой доступ к БД<br>❌ Раскрывать внутренние детали |

---

## Логирование ошибок

### Где логировать

**Правило**: Логировать на **краях системы** (handlers, background jobs), а не в середине.

**❌ ПЛОХО: логирование на каждом уровне**:
```go
// Repository
func (r *Repo) GetUser(id int) (*User, error) {
    user, err := r.db.Query(id)
    if err != nil {
        log.Printf("ERROR: query user %d: %v", id, err)  // НЕТ!
        return nil, err
    }
    return user, nil
}

// Service
func (s *Service) FindUser(id int) (*User, error) {
    user, err := s.repo.GetUser(id)
    if err != nil {
        log.Printf("ERROR: find user %d: %v", id, err)  // Дублирование!
        return nil, err
    }
    return user, nil
}

// Handler
func (h *Handler) GetUser(w http.ResponseWriter, r *http.Request) {
    user, err := h.service.FindUser(id)
    if err != nil {
        log.Printf("ERROR: get user %d: %v", id, err)  // Третий раз!
        http.Error(w, "error", 500)
    }
}

// Результат: 3 дубликата в логах для одной ошибки!
// ERROR: query user 42: sql: no rows in result set
// ERROR: find user 42: query user 42: sql: no rows in result set
// ERROR: get user 42: find user: query user 42: sql: no rows in result set
```

**✅ ХОРОШО: логирование на краю**:
```go
// Repository — только wrapping
func (r *Repo) GetUser(id int) (*User, error) {
    user, err := r.db.Query(id)
    if err != nil {
        return nil, fmt.Errorf("query user %d: %w", id, err)
    }
    return user, nil
}

// Service — только wrapping
func (s *Service) FindUser(id int) (*User, error) {
    user, err := s.repo.GetUser(id)
    if err != nil {
        return nil, fmt.Errorf("find user: %w", err)
    }
    return user, nil
}

// Handler — логируем ОДИН РАЗ
func (h *Handler) GetUser(w http.ResponseWriter, r *http.Request) {
    user, err := h.service.FindUser(id)
    if err != nil {
        // Логируем только неизвестные ошибки
        if !errors.Is(err, ErrUserNotFound) {
            h.logger.Error("unexpected error",
                "path", r.URL.Path,
                "user_id", id,
                "error", err,  // Вся цепочка: find user: query user 42: sql: no rows
            )
        }

        handleError(w, err)
    }
}
```

> 💡 **Идиома Go**: Repository и Service не логируют — только wrapping. Handler логирует unexpected errors один раз.

### Структурированное логирование (slog)

С Go 1.21+ в стандартной библиотеке появился `log/slog` — structured logger.

**Go 1.21+ (stdlib slog)**:
```go
import "log/slog"

// Настройка (в main)
logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
}))

// Использование
func (h *Handler) GetUser(w http.ResponseWriter, r *http.Request) {
    user, err := h.service.FindUser(id)
    if err != nil {
        logger.Error("get user failed",
            "error", err,
            "user_id", id,
            "path", r.URL.Path,
            "method", r.Method,
            "request_id", r.Header.Get("X-Request-ID"),
        )
        return
    }
}

// Вывод (JSON):
// {
//   "time": "2026-01-24T12:00:00Z",
//   "level": "ERROR",
//   "msg": "get user failed",
//   "error": "find user: query user 42: sql: no rows",
//   "user_id": 42,
//   "path": "/users/42",
//   "method": "GET",
//   "request_id": "abc123"
// }
```

**C# аналог (Serilog)**:
```csharp
// C#: Structured logging
Log.Error(ex, "Get user failed {UserId} {Path}", userId, path);

// Вывод (JSON):
// {
//   "Timestamp": "2026-01-24T12:00:00Z",
//   "Level": "Error",
//   "MessageTemplate": "Get user failed {UserId} {Path}",
//   "UserId": 42,
//   "Path": "/users/42",
//   "Exception": "..."
// }
```

> 💡 **Рекомендация**: Используй structured logging (slog, zap, zerolog) вместо fmt.Printf для production. Это позволяет фильтровать и анализировать логи в системах мониторинга (ELK, Grafana Loki).

### Expected vs Unexpected errors

**Правило**: Не логировать **expected errors** (404, 400) как ERROR. Используй INFO или не логируй вообще.

```go
func (h *Handler) GetUser(w http.ResponseWriter, r *http.Request) {
    user, err := h.service.FindUser(id)
    if err != nil {
        switch {
        case errors.Is(err, ErrUserNotFound):
            // Expected — логируем как INFO или не логируем
            logger.Info("user not found", "user_id", id)
            http.Error(w, "not found", 404)
            return

        case errors.Is(err, ErrUnauthorized):
            // Expected — логируем как WARN
            logger.Warn("unauthorized access attempt",
                "user_id", id,
                "ip", r.RemoteAddr)
            http.Error(w, "unauthorized", 401)
            return

        default:
            // Unexpected — логируем как ERROR
            logger.Error("unexpected error", "error", err, "user_id", id)
            http.Error(w, "internal error", 500)
            return
        }
    }
}
```

**Таблица: Уровни логирования**:

| HTTP Status | Тип ошибки | Уровень логирования | Почему |
|-------------|-----------|---------------------|--------|
| 400 Bad Request | Валидация | INFO или не логировать | Ожидаемая ситуация |
| 401 Unauthorized | Аутентификация | WARN | Потенциальная атака |
| 403 Forbidden | Авторизация | WARN | Потенциальная атака |
| 404 Not Found | Запись не найдена | INFO или не логировать | Ожидаемая ситуация |
| 409 Conflict | Дубликат | INFO | Ожидаемая ситуация |
| 500 Internal Error | Неизвестная ошибка | **ERROR** | Требует расследования |

---

## Идиоматичные паттерны для production

### Retry с exponential backoff

**C# (Polly)**:
```csharp
var policy = Policy
    .Handle<HttpRequestException>()
    .WaitAndRetryAsync(3, retryAttempt =>
        TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)));

await policy.ExecuteAsync(async () =>
    await httpClient.GetAsync(url));
```

**Go паттерн**:
```go
func RetryWithBackoff(ctx context.Context, maxRetries int, fn func() error) error {
    backoff := time.Second

    for i := 0; i < maxRetries; i++ {
        err := fn()
        if err == nil {
            return nil
        }

        // Проверяем, можно ли retry
        if !IsRetryable(err) {
            return fmt.Errorf("non-retryable error: %w", err)
        }

        if i == maxRetries-1 {
            return fmt.Errorf("max retries exceeded: %w", err)
        }

        select {
        case <-time.After(backoff):
            backoff *= 2  // Exponential backoff
        case <-ctx.Done():
            return ctx.Err()
        }
    }

    return errors.New("unreachable")
}

// Классификация ошибок
func IsRetryable(err error) bool {
    // Сетевые временные ошибки
    var netErr net.Error
    if errors.As(err, &netErr) && netErr.Temporary() {
        return true
    }

    // Timeout — retry
    if errors.Is(err, context.DeadlineExceeded) {
        return true
    }

    // Cancelled — НЕ retry
    if errors.Is(err, context.Canceled) {
        return false
    }

    return false
}

// Использование
err := RetryWithBackoff(ctx, 3, func() error {
    return httpClient.Get(url)
})
```

### Error aggregation (несколько горутин)

**C# (Task.WhenAll + AggregateException)**:
```csharp
try
{
    await Task.WhenAll(
        Task.Run(() => Operation1()),
        Task.Run(() => Operation2()),
        Task.Run(() => Operation3())
    );
}
catch (AggregateException ex)
{
    foreach (var inner in ex.InnerExceptions)
    {
        Console.WriteLine(inner.Message);
    }
}
```

**Go (errgroup — возвращает первую ошибку)**:
```go
import "golang.org/x/sync/errgroup"

func ProcessMultiple(ctx context.Context, items []Item) error {
    g, ctx := errgroup.WithContext(ctx)

    for _, item := range items {
        item := item  // Capture
        g.Go(func() error {
            return processItem(ctx, item)
        })
    }

    // Возвращает первую ошибку, отменяет контекст
    return g.Wait()
}
```

**Go (собираем все ошибки — MultiError helper)**:
```go
type MultiError struct {
    Errors []error
}

func (m *MultiError) Error() string {
    if len(m.Errors) == 0 {
        return "no errors"
    }

    var buf strings.Builder
    buf.WriteString(fmt.Sprintf("%d errors occurred:", len(m.Errors)))
    for i, err := range m.Errors {
        buf.WriteString(fmt.Sprintf("\n\t%d: %v", i+1, err))
    }
    return buf.String()
}

func (m *MultiError) Add(err error) {
    if err != nil {
        m.Errors = append(m.Errors, err)
    }
}

func (m *MultiError) ErrorOrNil() error {
    if len(m.Errors) == 0 {
        return nil
    }
    return m
}

// Использование
func ProcessAll(items []Item) error {
    var wg sync.WaitGroup
    var mu sync.Mutex
    var multiErr MultiError

    for _, item := range items {
        wg.Add(1)
        go func(item Item) {
            defer wg.Done()
            if err := processItem(item); err != nil {
                mu.Lock()
                multiErr.Add(fmt.Errorf("process item %d: %w", item.ID, err))
                mu.Unlock()
            }
        }(item)
    }

    wg.Wait()
    return multiErr.ErrorOrNil()
}
```

### Context для cancellation (cascading errors)

**Паттерн**: Отмена всех операций при первой ошибке.

```go
func ProcessPipeline(ctx context.Context) error {
    // Создаем контекст с отменой
    ctx, cancel := context.WithCancel(ctx)
    defer cancel()

    // Если любая горутина упадет — отменим остальные
    errCh := make(chan error, 3)

    go func() {
        if err := step1(ctx); err != nil {
            errCh <- fmt.Errorf("step1: %w", err)
        } else {
            errCh <- nil
        }
    }()

    go func() {
        if err := step2(ctx); err != nil {
            errCh <- fmt.Errorf("step2: %w", err)
        } else {
            errCh <- nil
        }
    }()

    go func() {
        if err := step3(ctx); err != nil {
            errCh <- fmt.Errorf("step3: %w", err)
        } else {
            errCh <- nil
        }
    }()

    // Ждем результатов
    for i := 0; i < 3; i++ {
        if err := <-errCh; err != nil {
            cancel()  // Отменяем остальные
            return err
        }
    }

    return nil
}
```

---

## Практические примеры

### Пример 1: REST API с централизованной обработкой ошибок

**Задача**: Реализовать CRUD API для пользователей с правильной обработкой ошибок на всех слоях.

**Архитектура**:
```
errors.go          — Доменные ошибки
repository.go      — Маппинг БД ошибок
service.go         — Бизнес-логика
handler.go         — HTTP маппинг
middleware.go      — Recover + logging
```

<details>
<summary>Полный код (кликните чтобы развернуть)</summary>

```go
// ========== errors.go ==========
package domain

import "errors"

// Доменные ошибки (публичный API)
var (
    ErrUserNotFound    = errors.New("user not found")
    ErrDuplicateEmail  = errors.New("email already exists")
    ErrValidationFailed = errors.New("validation failed")
)

// Typed error для валидации
type ValidationError struct {
    Errors map[string]string
}

func (e *ValidationError) Error() string {
    return "validation failed"
}

// ========== repository.go ==========
package repository

import (
    "database/sql"
    "errors"
    "fmt"

    "github.com/jackc/pgconn"
    "myapp/domain"
)

type UserRepository struct {
    db *sql.DB
}

func (r *UserRepository) GetByID(id int) (*domain.User, error) {
    var user domain.User
    err := r.db.QueryRow("SELECT id, email, name FROM users WHERE id = $1", id).
        Scan(&user.ID, &user.Email, &user.Name)

    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, fmt.Errorf("%w (id=%d)", domain.ErrUserNotFound, id)
        }
        return nil, fmt.Errorf("query user %d: %w", id, err)
    }

    return &user, nil
}

func (r *UserRepository) Create(user *domain.User) error {
    _, err := r.db.Exec("INSERT INTO users (email, name) VALUES ($1, $2)",
        user.Email, user.Name)

    if err != nil {
        var pgErr *pgconn.PgError
        if errors.As(err, &pgErr) && pgErr.Code == "23505" {
            return fmt.Errorf("%w: %s", domain.ErrDuplicateEmail, user.Email)
        }
        return fmt.Errorf("insert user: %w", err)
    }

    return nil
}

// ========== service.go ==========
package service

import (
    "context"
    "fmt"
    "myapp/domain"
)

type UserService struct {
    repo UserRepository
}

func (s *UserService) GetUser(ctx context.Context, id int) (*domain.User, error) {
    user, err := s.repo.GetByID(id)
    if err != nil {
        return nil, fmt.Errorf("get user: %w", err)
    }
    return user, nil
}

func (s *UserService) CreateUser(ctx context.Context, req domain.CreateUserRequest) (*domain.User, error) {
    // Валидация
    errs := make(map[string]string)
    if req.Email == "" {
        errs["email"] = "required"
    }
    if req.Name == "" {
        errs["name"] = "required"
    }

    if len(errs) > 0 {
        return nil, fmt.Errorf("%w: %w", domain.ErrValidationFailed, &domain.ValidationError{Errors: errs})
    }

    // Создание
    user := &domain.User{Email: req.Email, Name: req.Name}
    if err := s.repo.Create(user); err != nil {
        return nil, fmt.Errorf("create user: %w", err)
    }

    return user, nil
}

// ========== handler.go ==========
package handler

import (
    "encoding/json"
    "errors"
    "log/slog"
    "net/http"

    "myapp/domain"
    "myapp/service"
)

type UserHandler struct {
    service *service.UserService
    logger  *slog.Logger
}

func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
    id := getIDFromPath(r.URL.Path)

    user, err := h.service.GetUser(r.Context(), id)
    if err != nil {
        h.handleError(w, r, err)
        return
    }

    respondJSON(w, http.StatusOK, user)
}

func (h *UserHandler) CreateUser(w http.ResponseWriter, r *http.Request) {
    var req domain.CreateUserRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        respondJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid request"})
        return
    }

    user, err := h.service.CreateUser(r.Context(), req)
    if err != nil {
        h.handleError(w, r, err)
        return
    }

    respondJSON(w, http.StatusCreated, user)
}

func (h *UserHandler) handleError(w http.ResponseWriter, r *http.Request, err error) {
    switch {
    case errors.Is(err, domain.ErrUserNotFound):
        respondJSON(w, http.StatusNotFound, map[string]string{"error": "user not found"})

    case errors.Is(err, domain.ErrDuplicateEmail):
        respondJSON(w, http.StatusConflict, map[string]string{"error": "email already exists"})

    case errors.Is(err, domain.ErrValidationFailed):
        var validErr *domain.ValidationError
        if errors.As(err, &validErr) {
            respondJSON(w, http.StatusBadRequest, map[string]interface{}{
                "error": "validation failed",
                "fields": validErr.Errors,
            })
            return
        }

    default:
        h.logger.Error("unexpected error",
            "path", r.URL.Path,
            "method", r.Method,
            "error", err,
        )
        respondJSON(w, http.StatusInternalServerError, map[string]string{"error": "internal error"})
    }
}

func respondJSON(w http.ResponseWriter, status int, data interface{}) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(data)
}

// ========== middleware.go ==========
package middleware

import (
    "log"
    "net/http"
    "runtime/debug"
)

func RecoverMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if rec := recover(); rec != nil {
                log.Printf("PANIC: %v\n%s", rec, debug.Stack())
                w.WriteHeader(http.StatusInternalServerError)
                w.Write([]byte(`{"error":"internal server error"}`))
            }
        }()

        next.ServeHTTP(w, r)
    })
}
```

</details>

---

### Пример 2: Background Job с retry и DLQ

**Задача**: Обработка сообщений из Kafka с классификацией ошибок (transient vs permanent), retry и dead letter queue.

<details>
<summary>Полный код (кликните чтобы развернуть)</summary>

```go
package worker

import (
    "context"
    "errors"
    "fmt"
    "log"
    "time"
)

// Классификация ошибок
var (
    ErrTransient = errors.New("transient error")  // Можно retry
    ErrPermanent = errors.New("permanent error")  // Отправить в DLQ
)

type Message struct {
    ID   string
    Data []byte
}

type Worker struct {
    kafka     KafkaConsumer
    dlq       DLQPublisher
    maxRetries int
}

func (w *Worker) ProcessMessage(ctx context.Context, msg Message) error {
    backoff := time.Second

    for i := 0; i < w.maxRetries; i++ {
        err := w.processMessageOnce(ctx, msg)
        if err == nil {
            return nil
        }

        // Классификация ошибки
        if errors.Is(err, ErrPermanent) {
            log.Printf("permanent error, sending to DLQ: %v", err)
            return w.dlq.Publish(msg, err.Error())
        }

        if !errors.Is(err, ErrTransient) {
            // Неизвестная ошибка — считаем transient
            log.Printf("unknown error (treating as transient): %v", err)
        }

        // Retry с exponential backoff
        if i < w.maxRetries-1 {
            log.Printf("retry %d/%d after %v: %v", i+1, w.maxRetries, backoff, err)

            select {
            case <-time.After(backoff):
                backoff *= 2
            case <-ctx.Done():
                return ctx.Err()
            }
        }
    }

    // Превышено количество попыток — отправляем в DLQ
    log.Printf("max retries exceeded, sending to DLQ")
    return w.dlq.Publish(msg, "max retries exceeded")
}

func (w *Worker) processMessageOnce(ctx context.Context, msg Message) error {
    // Парсинг сообщения
    order, err := parseOrder(msg.Data)
    if err != nil {
        return fmt.Errorf("%w: invalid message format: %v", ErrPermanent, err)
    }

    // Валидация
    if err := validateOrder(order); err != nil {
        return fmt.Errorf("%w: validation failed: %v", ErrPermanent, err)
    }

    // Сохранение в БД
    if err := saveOrder(ctx, order); err != nil {
        if isDeadlock(err) || isConnectionError(err) {
            return fmt.Errorf("%w: database error: %v", ErrTransient, err)
        }
        return fmt.Errorf("database error: %v", err)
    }

    return nil
}

func isDeadlock(err error) bool {
    // Проверка PostgreSQL deadlock
    return false // Упрощено
}

func isConnectionError(err error) bool {
    // Проверка сетевых ошибок
    return false // Упрощено
}
```

</details>

---

### Пример 3: gRPC сервис с error details

**Задача**: gRPC API с детальными ошибками (Google API error model).

<details>
<summary>Полный код (кликните чтобы развернуть)</summary>

```go
package grpc

import (
    "context"
    "errors"

    "google.golang.org/genproto/googleapis/rpc/errdetails"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"

    pb "myapp/proto"
    "myapp/domain"
)

type Server struct {
    service UserService
}

func (s *Server) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.User, error) {
    user, err := s.service.GetUser(ctx, int(req.Id))
    if err != nil {
        return nil, toGRPCError(err)
    }

    return &pb.User{
        Id:    int64(user.ID),
        Email: user.Email,
        Name:  user.Name,
    }, nil
}

func toGRPCError(err error) error {
    switch {
    case errors.Is(err, domain.ErrUserNotFound):
        st := status.New(codes.NotFound, "user not found")

        // Добавляем детали
        st, _ = st.WithDetails(&errdetails.ResourceInfo{
            ResourceType: "User",
            Description:  "The requested user was not found",
        })
        return st.Err()

    case errors.Is(err, domain.ErrValidationFailed):
        var validErr *domain.ValidationError
        if errors.As(err, &validErr) {
            st := status.New(codes.InvalidArgument, "validation failed")

            br := &errdetails.BadRequest{}
            for field, msg := range validErr.Errors {
                br.FieldViolations = append(br.FieldViolations, &errdetails.BadRequest_FieldViolation{
                    Field:       field,
                    Description: msg,
                })
            }

            st, _ = st.WithDetails(br)
            return st.Err()
        }
    }

    return status.Error(codes.Internal, "internal error")
}

// ========== Client ==========
func (c *Client) GetUser(id int) (*pb.User, error) {
    user, err := c.client.GetUser(ctx, &pb.GetUserRequest{Id: int64(id)})
    if err != nil {
        // Извлекаем детали
        st := status.Convert(err)

        for _, detail := range st.Details() {
            switch t := detail.(type) {
            case *errdetails.BadRequest:
                fmt.Println("Validation errors:")
                for _, v := range t.FieldViolations {
                    fmt.Printf("  %s: %s\n", v.Field, v.Description)
                }
            }
        }

        return nil, err
    }

    return user, nil
}
```

</details>

---

### Пример 4: Observability — distributed tracing

**Задача**: Трассировка ошибок через микросервисы с OpenTelemetry.

<details>
<summary>Краткий пример</summary>

```go
package tracing

import (
    "context"
    "fmt"

    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/codes"
)

func ProcessOrder(ctx context.Context, orderID int) error {
    tracer := otel.Tracer("order-service")
    ctx, span := tracer.Start(ctx, "ProcessOrder")
    defer span.End()

    span.SetAttributes(attribute.Int("order.id", orderID))

    // Вызов другого сервиса
    user, err := getUserFromService(ctx, userID)
    if err != nil {
        // Записываем ошибку в span
        span.RecordError(err)
        span.SetStatus(codes.Error, "failed to get user")
        return fmt.Errorf("get user: %w", err)
    }

    span.SetAttributes(attribute.String("user.email", user.Email))

    // Success
    span.SetStatus(codes.Ok, "")
    return nil
}
```

</details>

---

## Чек-лист

После изучения этого раздела вы должны:

**Базовые концепции:**
- [ ] Понимать разницу между sentinel и typed errors
- [ ] Выбирать между sentinel/typed в зависимости от сценария
- [ ] Создавать custom error types с метаданными
- [ ] Использовать fluent API для построения ошибок (`WithMetadata`)
- [ ] Знать, когда использовать panic (почти никогда для бизнес-логики)
- [ ] Использовать recover только в defer и на краях системы
- [ ] Помнить, что recover не ловит панику из другой горутины

**Wrapping и unwrapping:**
- [ ] Строить контекст через `fmt.Errorf("context: %w", err)`
- [ ] Проверять ошибки через `errors.Is()` и `errors.As()`
- [ ] Понимать trade-off между stdlib errors и pkg/errors (stack traces)

**Архитектурные паттерны:**
- [ ] Мапить БД ошибки на доменные в repository
- [ ] Обогащать контекстом в service
- [ ] Мапить на HTTP/gRPC в handler
- [ ] Логировать один раз на краю системы (handler)
- [ ] Различать expected и unexpected errors (404 vs 500)
- [ ] Использовать structured logging (log/slog)

**Production практики:**
- [ ] Реализовывать retry с exponential backoff
- [ ] Собирать ошибки из множества горутин (MultiError)
- [ ] Использовать context для cascading cancellation
- [ ] Добавлять метрики для ошибок (Prometheus counters)
- [ ] Защищать HTTP/gRPC сервер через recover middleware

**gRPC и rich errors:**
- [ ] Мапить доменные ошибки на gRPC codes
- [ ] Использовать error details (errdetails.BadRequest)
- [ ] Извлекать details на клиенте через `status.Convert()`

---

## Следующие шаги

Переходите к [2.6 Тестирование и бенчмаркинг](06_testing_benchmarking.md)

---

**Вопросы?** Открой issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Назад: 2.4 Примитивы синхронизации](04_sync_primitives.md) | [Вперёд: 2.6 Тестирование →](06_testing_benchmarking.md)
