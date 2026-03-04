# HTTP в Go: Создание веб-серверов

---

## Введение

HTTP-сервер — основа любого веб-приложения. В Go работа с HTTP принципиально отличается от ASP.NET Core. Вместо сложного фреймворка с DI-контейнерами, middleware pipeline и контроллерами, Go предлагает минималистичную стандартную библиотеку `net/http`, которая покрывает большинство потребностей.

> 💡 **Для C# разработчиков**: Забудьте про `Startup.cs`, `Program.cs` с `builder.Services`, атрибутные роуты и `IActionResult`. В Go всё проще: функция принимает `ResponseWriter` и `Request`, и вы сами решаете, что с ними делать.

### Что вы узнаете

- Как работает `net/http` и чем отличается от ASP.NET Core
- Паттерн middleware в Go (wrapping functions vs pipeline)
- Когда использовать стандартную библиотеку, а когда — роутеры
- Практические примеры production-ready HTTP серверов

---

## Философия: net/http vs ASP.NET Core

### Ключевые различия подходов

| Аспект | ASP.NET Core | Go (net/http) |
|--------|--------------|---------------|
| **Философия** | "Batteries included" фреймворк | Минималистичная библиотека |
| **Handler** | `ControllerBase`, Minimal APIs | `http.Handler` интерфейс |
| **Routing** | Атрибуты `[Route]`, `MapGet/Post` | `http.ServeMux` или роутеры |
| **Middleware** | `app.UseXxx()` pipeline | Wrapping functions |
| **DI** | Встроенный `IServiceCollection` | Manual / Wire / Fx |
| **Configuration** | `IConfiguration`, `appsettings.json` | `os.Getenv()`, viper |
| **Startup** | `Program.cs` + builder pattern | `main()` + композиция |

### ASP.NET Core подход

```csharp
// Program.cs в ASP.NET Core
var builder = WebApplication.CreateBuilder(args);

// Регистрация сервисов
builder.Services.AddControllers();
builder.Services.AddScoped<IUserService, UserService>();

var app = builder.Build();

// Middleware pipeline
app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

app.Run();
```

```csharp
// UserController.cs
[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    private readonly IUserService _userService;

    public UsersController(IUserService userService)
    {
        _userService = userService;
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<User>> GetUser(int id)
    {
        var user = await _userService.GetByIdAsync(id);
        if (user == null)
            return NotFound();
        return Ok(user);
    }
}
```

### Go подход

```go
// main.go в Go
package main

import (
    "encoding/json"
    "log"
    "net/http"
    "strconv"
    "strings"
)

type User struct {
    ID   int    `json:"id"`
    Name string `json:"name"`
}

// "Сервис" — просто структура с методами
type UserService struct {
    users map[int]User
}

func NewUserService() *UserService {
    return &UserService{
        users: map[int]User{
            1: {ID: 1, Name: "Alice"},
            2: {ID: 2, Name: "Bob"},
        },
    }
}

func (s *UserService) GetByID(id int) (User, bool) {
    user, ok := s.users[id]
    return user, ok
}

// Handler — просто функция
func (s *UserService) HandleGetUser(w http.ResponseWriter, r *http.Request) {
    // Извлекаем ID из пути вручную (в net/http нет параметров пути)
    path := strings.TrimPrefix(r.URL.Path, "/api/users/")
    id, err := strconv.Atoi(path)
    if err != nil {
        http.Error(w, "invalid id", http.StatusBadRequest)
        return
    }

    user, ok := s.GetByID(id)
    if !ok {
        http.Error(w, "user not found", http.StatusNotFound)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(user)
}

func main() {
    userService := NewUserService()

    mux := http.NewServeMux()
    mux.HandleFunc("/api/users/", userService.HandleGetUser)

    log.Println("Server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", mux))
}
```

> ⚠️ **Важно**: В чистом `net/http` нет встроенной поддержки параметров пути (`/users/{id}`). Это одна из причин использовать роутеры вроде chi.

### Почему Go проще?

1. **Нет магии** — всё явно, нет hidden conventions
2. **Нет DI-контейнера** — зависимости передаются через конструкторы
3. **Нет middleware pipeline** — просто wrapping функций
4. **Нет атрибутов** — роутинг в коде, а не в метаданных
5. **Быстрый старт** — один файл, минимум boilerplate

---

## net/http: основы

### Handler и HandlerFunc

В основе `net/http` лежит простой интерфейс:

```go
// Интерфейс Handler — всего один метод
type Handler interface {
    ServeHTTP(ResponseWriter, *Request)
}
```

Любой тип, реализующий этот интерфейс, может обрабатывать HTTP-запросы.

#### Способ 1: Реализация интерфейса

```go
type HelloHandler struct {
    greeting string
}

func (h *HelloHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "%s, World!", h.greeting)
}

func main() {
    handler := &HelloHandler{greeting: "Hello"}
    http.ListenAndServe(":8080", handler)
}
```

#### Способ 2: HandlerFunc (чаще используется)

```go
// HandlerFunc — это тип-адаптер для обычных функций
type HandlerFunc func(ResponseWriter, *Request)

// Реализует интерфейс Handler
func (f HandlerFunc) ServeHTTP(w ResponseWriter, r *Request) {
    f(w, r)
}
```

Это позволяет использовать обычные функции как handlers:

```go
func helloHandler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintln(w, "Hello, World!")
}

func main() {
    // http.HandleFunc автоматически оборачивает функцию в HandlerFunc
    http.HandleFunc("/hello", helloHandler)
    http.ListenAndServe(":8080", nil)
}
```

#### Сравнение с C#

| C# (ASP.NET Core) | Go (net/http) |
|-------------------|---------------|
| `IActionResult` | `http.ResponseWriter` + прямая запись |
| `ControllerBase` | Любой тип с `ServeHTTP` |
| `[HttpGet]` атрибут | `http.HandleFunc("/path", fn)` |
| `async Task<T>` | Синхронный код (горутины в фоне) |

### ServeMux: маршрутизация запросов

`ServeMux` — встроенный мультиплексор (роутер) в Go:

```go
func main() {
    mux := http.NewServeMux()

    // Точное совпадение
    mux.HandleFunc("/", homeHandler)
    mux.HandleFunc("/about", aboutHandler)

    // Префиксное совпадение (заканчивается на /)
    mux.HandleFunc("/api/", apiHandler) // /api/*, /api/users, etc.

    // Статические файлы
    fs := http.FileServer(http.Dir("./static"))
    mux.Handle("/static/", http.StripPrefix("/static/", fs))

    http.ListenAndServe(":8080", mux)
}
```

#### Ограничения ServeMux (Go < 1.22)

```go
// ❌ НЕ поддерживается в старом ServeMux:
// - Параметры пути: /users/{id}
// - HTTP методы: GET /users vs POST /users
// - Регулярные выражения
// - Группировка роутов

// Приходится делать вручную:
func usersHandler(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case http.MethodGet:
        // GET /users
        getUsers(w, r)
    case http.MethodPost:
        // POST /users
        createUser(w, r)
    default:
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
    }
}
```

#### Новый ServeMux в Go 1.22+

Go 1.22 значительно улучшил `ServeMux`:

```go
func main() {
    mux := http.NewServeMux()

    // Теперь поддерживаются методы!
    mux.HandleFunc("GET /users", getUsers)
    mux.HandleFunc("POST /users", createUser)

    // И параметры пути!
    mux.HandleFunc("GET /users/{id}", getUser)
    mux.HandleFunc("PUT /users/{id}", updateUser)
    mux.HandleFunc("DELETE /users/{id}", deleteUser)

    // Доступ к параметрам
    // r.PathValue("id")

    http.ListenAndServe(":8080", mux)
}

func getUser(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id") // Новый метод в Go 1.22
    fmt.Fprintf(w, "User ID: %s", id)
}
```

> 💡 **Рекомендация**: Если ваш проект на Go 1.22+, стандартного `ServeMux` может быть достаточно для простых API. Для сложных проектов всё ещё рекомендуется chi.

#### Миграция с chi на stdlib (Go 1.22+)

**chi:**
```go
import "github.com/go-chi/chi/v5"

r := chi.NewRouter()

r.Use(middleware.Logger)
r.Use(middleware.Recoverer)

r.Get("/users/{id}", func(w http.ResponseWriter, r *http.Request) {
    id := chi.URLParam(r, "id")
    // ...
})

r.Route("/api", func(r chi.Router) {
    r.Get("/health", healthHandler)
})
```

**Go 1.22 stdlib:**
```go
mux := http.NewServeMux()

// Middleware через wrapping
handler := loggingMiddleware(recoveryMiddleware(mux))

mux.HandleFunc("GET /users/{id}", func(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id")  // Вместо chi.URLParam
    // ...
})

mux.HandleFunc("GET /api/health", healthHandler)

http.ListenAndServe(":8080", handler)

// Middleware — обёрточные функции
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        slog.Info("request",
            slog.String("method", r.Method),
            slog.String("path", r.URL.Path),
            slog.Duration("duration", time.Since(start)),
        )
    })
}
```

**Когда всё ещё нужен chi:**
- **Middleware ecosystem**: chi.Use() с готовыми middleware
- **Route groups**: Вложенные группы с общими middleware
- **Regex patterns**: Сложные паттерны маршрутизации
- **Существующая кодовая база**: Если проект уже на chi — миграция может не стоить усилий

### Работа с Request

`http.Request` содержит всю информацию о входящем запросе:

```go
func handler(w http.ResponseWriter, r *http.Request) {
    // Метод запроса
    method := r.Method // "GET", "POST", etc.

    // URL и путь
    fullURL := r.URL.String()    // "/api/users?page=1"
    path := r.URL.Path           // "/api/users"
    rawQuery := r.URL.RawQuery   // "page=1"

    // Query параметры
    page := r.URL.Query().Get("page")           // "1" или ""
    tags := r.URL.Query()["tags"]               // []string для множественных значений

    // Заголовки
    contentType := r.Header.Get("Content-Type")
    auth := r.Header.Get("Authorization")

    // Параметры пути (Go 1.22+)
    id := r.PathValue("id")

    // Cookies
    cookie, err := r.Cookie("session_id")
    if err == nil {
        sessionID := cookie.Value
    }

    // Тело запроса
    body, err := io.ReadAll(r.Body)
    defer r.Body.Close()

    // Парсинг JSON
    var user User
    if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
        http.Error(w, "Invalid JSON", http.StatusBadRequest)
        return
    }

    // Форма (application/x-www-form-urlencoded)
    if err := r.ParseForm(); err == nil {
        name := r.FormValue("name")
    }

    // Multipart форма (file upload)
    if err := r.ParseMultipartForm(10 << 20); err == nil { // 10 MB max
        file, header, err := r.FormFile("avatar")
        if err == nil {
            defer file.Close()
            // header.Filename, header.Size, header.Header
        }
    }

    // Контекст запроса
    ctx := r.Context()

    // IP клиента
    clientIP := r.RemoteAddr
    // Или через заголовки (за прокси)
    forwarded := r.Header.Get("X-Forwarded-For")
}
```

#### Сравнение с ASP.NET Core

| ASP.NET Core | Go |
|--------------|-----|
| `Request.Query["page"]` | `r.URL.Query().Get("page")` |
| `Request.Headers["Auth"]` | `r.Header.Get("Auth")` |
| `[FromBody] User user` | `json.NewDecoder(r.Body).Decode(&user)` |
| `Request.Form["name"]` | `r.FormValue("name")` |
| `Request.Cookies["session"]` | `r.Cookie("session")` |
| `HttpContext.RequestAborted` | `r.Context()` |

### Формирование Response

`http.ResponseWriter` — интерфейс для записи ответа:

```go
func handler(w http.ResponseWriter, r *http.Request) {
    // Установка заголовков (ДО записи тела!)
    w.Header().Set("Content-Type", "application/json")
    w.Header().Set("X-Custom-Header", "value")
    w.Header().Add("Set-Cookie", "session=abc123") // Add для множественных

    // Установка статус-кода (ДО записи тела!)
    w.WriteHeader(http.StatusCreated) // 201

    // Запись тела
    w.Write([]byte(`{"message": "created"}`))

    // Или через fmt
    fmt.Fprintf(w, "User %d created", userID)

    // Или через json.Encoder
    json.NewEncoder(w).Encode(map[string]string{
        "status": "ok",
    })
}
```

> ⚠️ **Важно**: После вызова `Write()` или `WriteHeader()` нельзя менять заголовки! Go отправит заголовки при первой записи в тело.

#### Helper-функции для ответов

Создайте вспомогательные функции для типичных ответов:

```go
// Успешный JSON ответ
func respondJSON(w http.ResponseWriter, status int, data any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(data)
}

// Ответ с ошибкой
func respondError(w http.ResponseWriter, status int, message string) {
    respondJSON(w, status, map[string]string{
        "error": message,
    })
}

// Использование
func getUser(w http.ResponseWriter, r *http.Request) {
    user, ok := findUser(id)
    if !ok {
        respondError(w, http.StatusNotFound, "user not found")
        return
    }
    respondJSON(w, http.StatusOK, user)
}
```

### Graceful Shutdown

Корректное завершение сервера — критически важно для production:

```go
package main

import (
    "context"
    "log"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"
)

func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        // Имитация долгой обработки
        time.Sleep(5 * time.Second)
        w.Write([]byte("Hello!"))
    })

    server := &http.Server{
        Addr:         ":8080",
        Handler:      mux,
        ReadTimeout:  15 * time.Second,
        WriteTimeout: 15 * time.Second,
        IdleTimeout:  60 * time.Second,
    }

    // Канал для получения сигналов ОС
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

    // Запуск сервера в горутине
    go func() {
        log.Println("Server starting on :8080")
        if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatalf("Server error: %v", err)
        }
    }()

    // Ожидание сигнала завершения
    <-quit
    log.Println("Shutting down server...")

    // Контекст с таймаутом для graceful shutdown
    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    // Shutdown ждёт завершения активных запросов
    if err := server.Shutdown(ctx); err != nil {
        log.Fatalf("Server forced to shutdown: %v", err)
    }

    log.Println("Server stopped gracefully")
}
```

#### Сравнение с ASP.NET Core

```csharp
// ASP.NET Core — graceful shutdown встроен
var app = builder.Build();
app.Lifetime.ApplicationStopping.Register(() => {
    // Cleanup
});
await app.RunAsync();
```

```go
// Go — явное управление жизненным циклом
// + Больше контроля
// + Понятно, что происходит
// - Больше кода
```

---

## Middleware Pattern

### Концепция middleware в Go

Middleware в Go — это функции, которые оборачивают handler, добавляя дополнительную логику до и/или после обработки запроса.

```go
// Тип middleware — функция, принимающая и возвращающая Handler
type Middleware func(http.Handler) http.Handler

// Пример: логирование
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()

        // До обработки
        log.Printf("Started %s %s", r.Method, r.URL.Path)

        // Вызов следующего handler
        next.ServeHTTP(w, r)

        // После обработки
        log.Printf("Completed in %v", time.Since(start))
    })
}
```

#### Сравнение с ASP.NET Core

```csharp
// ASP.NET Core middleware
public class LoggingMiddleware
{
    private readonly RequestDelegate _next;

    public LoggingMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var start = DateTime.UtcNow;
        Console.WriteLine($"Started {context.Request.Method} {context.Request.Path}");

        await _next(context);

        Console.WriteLine($"Completed in {DateTime.UtcNow - start}");
    }
}

// Регистрация
app.UseMiddleware<LoggingMiddleware>();
```

```go
// Go middleware — просто функция
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        log.Printf("Started %s %s", r.Method, r.URL.Path)

        next.ServeHTTP(w, r)

        log.Printf("Completed in %v", time.Since(start))
    })
}

// Применение — просто оборачивание
handler = loggingMiddleware(handler)
```

### Цепочка middleware

Middleware можно комбинировать, создавая цепочку обработки:

```go
// Способ 1: Ручное оборачивание
func main() {
    var handler http.Handler = http.HandlerFunc(finalHandler)

    // Порядок: снизу вверх (последний применённый — первый в цепочке)
    handler = authMiddleware(handler)
    handler = loggingMiddleware(handler)
    handler = recoveryMiddleware(handler)

    // Результат: recovery -> logging -> auth -> finalHandler
    http.ListenAndServe(":8080", handler)
}
```

```go
// Способ 2: Функция-композитор
func chain(h http.Handler, middlewares ...Middleware) http.Handler {
    // Применяем в обратном порядке
    for i := len(middlewares) - 1; i >= 0; i-- {
        h = middlewares[i](h)
    }
    return h
}

func main() {
    handler := chain(
        http.HandlerFunc(finalHandler),
        recoveryMiddleware,  // 1-й в цепочке
        loggingMiddleware,   // 2-й
        authMiddleware,      // 3-й, ближе к handler
    )
    http.ListenAndServe(":8080", handler)
}
```

```go
// Способ 3: Использовать роутер (chi) — рекомендуется
import "github.com/go-chi/chi/v5"
import "github.com/go-chi/chi/v5/middleware"

func main() {
    r := chi.NewRouter()

    // Middleware применяются в порядке добавления
    r.Use(middleware.Recoverer)
    r.Use(middleware.Logger)
    r.Use(authMiddleware)

    r.Get("/", finalHandler)

    http.ListenAndServe(":8080", r)
}
```

### Типичные middleware

#### Recovery (обработка паники)

```go
func recoveryMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if err := recover(); err != nil {
                log.Printf("Panic recovered: %v\n%s", err, debug.Stack())
                http.Error(w, "Internal Server Error", http.StatusInternalServerError)
            }
        }()
        next.ServeHTTP(w, r)
    })
}
```

#### Logging

```go
// ResponseWriter wrapper для захвата статус-кода
type responseWriter struct {
    http.ResponseWriter
    status int
    size   int
}

func (rw *responseWriter) WriteHeader(status int) {
    rw.status = status
    rw.ResponseWriter.WriteHeader(status)
}

func (rw *responseWriter) Write(b []byte) (int, error) {
    size, err := rw.ResponseWriter.Write(b)
    rw.size += size
    return size, err
}

func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()

        wrapped := &responseWriter{ResponseWriter: w, status: http.StatusOK}
        next.ServeHTTP(wrapped, r)

        log.Printf(
            "%s %s %d %d %v",
            r.Method,
            r.URL.Path,
            wrapped.status,
            wrapped.size,
            time.Since(start),
        )
    })
}
```

#### CORS

```go
func corsMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Access-Control-Allow-Origin", "*")
        w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

        // Preflight request
        if r.Method == http.MethodOptions {
            w.WriteHeader(http.StatusNoContent)
            return
        }

        next.ServeHTTP(w, r)
    })
}
```

#### Authentication

```go
func authMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        token := r.Header.Get("Authorization")
        if token == "" {
            http.Error(w, "Unauthorized", http.StatusUnauthorized)
            return
        }

        // Валидация токена
        userID, err := validateToken(token)
        if err != nil {
            http.Error(w, "Invalid token", http.StatusUnauthorized)
            return
        }

        // Добавляем userID в контекст
        ctx := context.WithValue(r.Context(), userIDKey, userID)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

#### Rate Limiting

```go
import "golang.org/x/time/rate"

func rateLimitMiddleware(rps int) Middleware {
    limiter := rate.NewLimiter(rate.Limit(rps), rps)

    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            if !limiter.Allow() {
                http.Error(w, "Too Many Requests", http.StatusTooManyRequests)
                return
            }
            next.ServeHTTP(w, r)
        })
    }
}

// Использование
handler = rateLimitMiddleware(100)(handler) // 100 RPS
```

### Передача данных через context

Context — стандартный способ передачи request-scoped данных:

```go
// Определяем типизированные ключи (избегаем коллизий)
type contextKey string

const (
    userIDKey    contextKey = "userID"
    requestIDKey contextKey = "requestID"
)

// Middleware добавляет данные в context
func requestIDMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        requestID := uuid.New().String()
        ctx := context.WithValue(r.Context(), requestIDKey, requestID)

        // Добавляем в заголовок ответа
        w.Header().Set("X-Request-ID", requestID)

        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

// Handler извлекает данные из context
func handler(w http.ResponseWriter, r *http.Request) {
    requestID, ok := r.Context().Value(requestIDKey).(string)
    if !ok {
        requestID = "unknown"
    }

    userID, ok := r.Context().Value(userIDKey).(int)
    if !ok {
        http.Error(w, "Unauthorized", http.StatusUnauthorized)
        return
    }

    log.Printf("[%s] User %d accessed endpoint", requestID, userID)
}
```

> ⚠️ **Важно**: Используйте типизированные ключи (`type contextKey string`), а не строки напрямую. Это предотвращает коллизии между разными пакетами.

---

## Популярные роутеры

Стандартный `ServeMux` подходит для простых случаев, но для production часто используют сторонние роутеры.

### chi — идиоматичный выбор

[chi](https://github.com/go-chi/chi) — минималистичный роутер, полностью совместимый с `net/http`.

```go
import (
    "github.com/go-chi/chi/v5"
    "github.com/go-chi/chi/v5/middleware"
)

func main() {
    r := chi.NewRouter()

    // Встроенные middleware
    r.Use(middleware.RequestID)
    r.Use(middleware.RealIP)
    r.Use(middleware.Logger)
    r.Use(middleware.Recoverer)
    r.Use(middleware.Timeout(60 * time.Second))

    // Простые роуты
    r.Get("/", homeHandler)
    r.Post("/users", createUser)

    // Параметры пути
    r.Get("/users/{id}", getUser)

    // Группировка
    r.Route("/api/v1", func(r chi.Router) {
        r.Use(authMiddleware) // Middleware только для этой группы

        r.Get("/users", listUsers)
        r.Post("/users", createUser)

        r.Route("/users/{userID}", func(r chi.Router) {
            r.Get("/", getUser)
            r.Put("/", updateUser)
            r.Delete("/", deleteUser)
            r.Get("/posts", getUserPosts)
        })
    })

    // Статические файлы
    fs := http.FileServer(http.Dir("./static"))
    r.Handle("/static/*", http.StripPrefix("/static/", fs))

    http.ListenAndServe(":8080", r)
}

func getUser(w http.ResponseWriter, r *http.Request) {
    userID := chi.URLParam(r, "id")
    // ...
}
```

#### Преимущества chi

- **100% совместим с net/http** — все middleware и handlers работают
- **Нет лишних зависимостей** — только stdlib
- **Идиоматичный Go** — использует стандартные паттерны
- **Отличные встроенные middleware** — logger, recoverer, timeout и др.
- **Поддержка вложенных роутеров** — группировка и подроуты

### gin — самый популярный

[gin](https://github.com/gin-gonic/gin) — самый популярный веб-фреймворк Go (75k+ stars).

```go
import "github.com/gin-gonic/gin"

func main() {
    r := gin.Default() // Включает Logger и Recovery

    // Простые роуты
    r.GET("/", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "Hello"})
    })

    // Параметры
    r.GET("/users/:id", func(c *gin.Context) {
        id := c.Param("id")
        c.JSON(200, gin.H{"id": id})
    })

    // Query параметры
    r.GET("/search", func(c *gin.Context) {
        query := c.DefaultQuery("q", "")
        page := c.Query("page")
        c.JSON(200, gin.H{"query": query, "page": page})
    })

    // Binding JSON
    r.POST("/users", func(c *gin.Context) {
        var user User
        if err := c.ShouldBindJSON(&user); err != nil {
            c.JSON(400, gin.H{"error": err.Error()})
            return
        }
        c.JSON(201, user)
    })

    // Группы
    api := r.Group("/api/v1")
    api.Use(authMiddleware())
    {
        api.GET("/users", listUsers)
        api.POST("/users", createUser)
    }

    r.Run(":8080")
}
```

#### Особенности gin

- **Свой Context** — `*gin.Context` вместо `http.ResponseWriter` + `*http.Request`
- **Высокая производительность** — radix tree routing
- **Binding и валидация** — встроенная поддержка
- **Большое сообщество** — много примеров и middleware

> ⚠️ **Компромисс**: gin быстрый и популярный, но менее "идиоматичный" — его `*gin.Context` не совместим напрямую с `net/http`.

### echo — элегантный API

[echo](https://github.com/labstack/echo) — высокопроизводительный фреймворк с элегантным API.

```go
import (
    "github.com/labstack/echo/v4"
    "github.com/labstack/echo/v4/middleware"
)

func main() {
    e := echo.New()

    // Middleware
    e.Use(middleware.Logger())
    e.Use(middleware.Recover())
    e.Use(middleware.CORS())

    // Роуты
    e.GET("/", func(c echo.Context) error {
        return c.JSON(200, map[string]string{"message": "Hello"})
    })

    e.GET("/users/:id", func(c echo.Context) error {
        id := c.Param("id")
        return c.JSON(200, map[string]string{"id": id})
    })

    // Binding
    e.POST("/users", func(c echo.Context) error {
        var user User
        if err := c.Bind(&user); err != nil {
            return echo.NewHTTPError(400, err.Error())
        }
        return c.JSON(201, user)
    })

    // Группы
    api := e.Group("/api/v1")
    api.Use(authMiddleware)
    api.GET("/users", listUsers)

    e.Start(":8080")
}
```

#### Особенности echo

- **Возврат error** — handlers возвращают `error`, удобно для обработки
- **Автоматическая обработка ошибок** — централизованный error handler
- **Отличная документация**
- **Встроенная поддержка Swagger**

### fiber — максимальная производительность

[fiber](https://github.com/gofiber/fiber) — Express-inspired фреймворк на основе fasthttp.

```go
import "github.com/gofiber/fiber/v2"

func main() {
    app := fiber.New()

    // Middleware
    app.Use(logger.New())
    app.Use(recover.New())

    // Роуты (Express-like API)
    app.Get("/", func(c *fiber.Ctx) error {
        return c.JSON(fiber.Map{"message": "Hello"})
    })

    app.Get("/users/:id", func(c *fiber.Ctx) error {
        id := c.Params("id")
        return c.JSON(fiber.Map{"id": id})
    })

    app.Post("/users", func(c *fiber.Ctx) error {
        var user User
        if err := c.BodyParser(&user); err != nil {
            return c.Status(400).JSON(fiber.Map{"error": err.Error()})
        }
        return c.Status(201).JSON(user)
    })

    app.Listen(":8080")
}
```

#### Особенности fiber

- **Самый быстрый** — использует fasthttp вместо net/http
- **Express-like API** — знакомо для Node.js разработчиков
- **Zero memory allocation** — оптимизирован для производительности

> ⚠️ **Важно**: fiber использует fasthttp, который **не совместим с net/http**. Стандартные middleware не будут работать.

### Сравнительная таблица роутеров

| Характеристика | chi | gin | echo | fiber |
|----------------|-----|-----|------|-------|
| **GitHub Stars** | 18k | 79k | 30k | 34k |
| **Совместимость с net/http** | ✅ 100% | ❌ Свой Context | ❌ Свой Context | ❌ fasthttp |
| **Производительность** | Высокая | Очень высокая | Очень высокая | Максимальная |
| **Идиоматичность Go** | ✅ Отлично | ⚠️ Средне | ⚠️ Средне | ⚠️ Средне |
| **Встроенные middleware** | ✅ Много | ✅ Много | ✅ Много | ✅ Много |
| **Binding/Validation** | ❌ Нет | ✅ Есть | ✅ Есть | ✅ Есть |
| **Кривая обучения** | Низкая | Низкая | Низкая | Низкая |
| **Зависимости** | Нет | Много | Средне | Много |

### Когда что использовать?

```
┌─────────────────────────────────────────────────────────────┐
│ Нужна максимальная производительность?                      │
│                                                              │
│   Да → fiber (fasthttp)                                     │
│   Нет ↓                                                     │
├─────────────────────────────────────────────────────────────┤
│ Важна совместимость с net/http?                             │
│                                                              │
│   Да → chi                                                  │
│   Нет ↓                                                     │
├─────────────────────────────────────────────────────────────┤
│ Нужен встроенный binding/validation?                        │
│                                                              │
│   Да → gin или echo                                         │
│   Нет → chi                                                 │
├─────────────────────────────────────────────────────────────┤
│ Предпочитаете идиоматичный Go?                              │
│                                                              │
│   Да → chi                                                  │
│   Нет → gin (самый популярный)                              │
└─────────────────────────────────────────────────────────────┘
```

> 💡 **Рекомендация для курса**: Мы используем **chi** как основной роутер, потому что:
> 1. 100% совместим с `net/http`
> 2. Идиоматичный Go код
> 3. Легко понять после изучения стандартной библиотеки
> 4. Отличные встроенные middleware

---

## Context в HTTP handlers

### Request Context

Каждый HTTP запрос имеет связанный `context.Context`:

```go
func handler(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()

    // Context отменяется когда:
    // 1. Клиент закрыл соединение
    // 2. Сработал timeout
    // 3. Сервер начал shutdown

    // Проверка отмены
    select {
    case <-ctx.Done():
        log.Println("Request cancelled:", ctx.Err())
        return
    default:
        // Продолжаем обработку
    }

    // Передача контекста в downstream сервисы
    result, err := fetchData(ctx)
    if err != nil {
        if ctx.Err() != nil {
            // Клиент отключился, не отправляем ответ
            return
        }
        http.Error(w, err.Error(), 500)
        return
    }
}

func fetchData(ctx context.Context) (Data, error) {
    // Создаём запрос с контекстом
    req, _ := http.NewRequestWithContext(ctx, "GET", "https://api.example.com/data", nil)

    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return Data{}, err
    }
    defer resp.Body.Close()

    // ...
}
```

### Timeout middleware

```go
func timeoutMiddleware(timeout time.Duration) Middleware {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            ctx, cancel := context.WithTimeout(r.Context(), timeout)
            defer cancel()

            // Важно: передаём новый контекст в запрос
            r = r.WithContext(ctx)

            done := make(chan struct{})
            go func() {
                next.ServeHTTP(w, r)
                close(done)
            }()

            select {
            case <-done:
                // Обработка завершена
            case <-ctx.Done():
                // Timeout
                http.Error(w, "Request timeout", http.StatusGatewayTimeout)
            }
        })
    }
}
```

### Сравнение с ASP.NET Core

| ASP.NET Core | Go |
|--------------|-----|
| `HttpContext.RequestAborted` | `r.Context()` |
| `CancellationToken` | `context.Context` |
| `HttpContext.Items` | `context.WithValue()` |
| Automatic timeout via Kestrel | `context.WithTimeout()` |

---

## Практические примеры

### Пример 1: REST API с net/http

Полноценный REST API для управления задачами (todo list):

```go
package main

import (
    "encoding/json"
    "log"
    "net/http"
    "strconv"
    "strings"
    "sync"
    "time"
)

// Модель
type Task struct {
    ID        int       `json:"id"`
    Title     string    `json:"title"`
    Completed bool      `json:"completed"`
    CreatedAt time.Time `json:"created_at"`
}

// In-memory хранилище
type TaskStore struct {
    mu     sync.RWMutex
    tasks  map[int]Task
    nextID int
}

func NewTaskStore() *TaskStore {
    return &TaskStore{
        tasks:  make(map[int]Task),
        nextID: 1,
    }
}

func (s *TaskStore) Create(title string) Task {
    s.mu.Lock()
    defer s.mu.Unlock()

    task := Task{
        ID:        s.nextID,
        Title:     title,
        Completed: false,
        CreatedAt: time.Now(),
    }
    s.tasks[task.ID] = task
    s.nextID++
    return task
}

func (s *TaskStore) GetAll() []Task {
    s.mu.RLock()
    defer s.mu.RUnlock()

    tasks := make([]Task, 0, len(s.tasks))
    for _, t := range s.tasks {
        tasks = append(tasks, t)
    }
    return tasks
}

func (s *TaskStore) GetByID(id int) (Task, bool) {
    s.mu.RLock()
    defer s.mu.RUnlock()

    task, ok := s.tasks[id]
    return task, ok
}

func (s *TaskStore) Update(id int, title string, completed bool) (Task, bool) {
    s.mu.Lock()
    defer s.mu.Unlock()

    task, ok := s.tasks[id]
    if !ok {
        return Task{}, false
    }

    task.Title = title
    task.Completed = completed
    s.tasks[id] = task
    return task, true
}

func (s *TaskStore) Delete(id int) bool {
    s.mu.Lock()
    defer s.mu.Unlock()

    _, ok := s.tasks[id]
    if ok {
        delete(s.tasks, id)
    }
    return ok
}

// HTTP Handlers
type TaskHandler struct {
    store *TaskStore
}

func (h *TaskHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    // Роутинг вручную (недостаток чистого net/http)
    path := strings.TrimPrefix(r.URL.Path, "/api/tasks")

    switch {
    case path == "" || path == "/":
        h.handleTasks(w, r)
    case strings.HasPrefix(path, "/"):
        h.handleTask(w, r, strings.TrimPrefix(path, "/"))
    default:
        http.NotFound(w, r)
    }
}

func (h *TaskHandler) handleTasks(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case http.MethodGet:
        h.listTasks(w, r)
    case http.MethodPost:
        h.createTask(w, r)
    default:
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
    }
}

func (h *TaskHandler) handleTask(w http.ResponseWriter, r *http.Request, idStr string) {
    id, err := strconv.Atoi(idStr)
    if err != nil {
        http.Error(w, "Invalid task ID", http.StatusBadRequest)
        return
    }

    switch r.Method {
    case http.MethodGet:
        h.getTask(w, r, id)
    case http.MethodPut:
        h.updateTask(w, r, id)
    case http.MethodDelete:
        h.deleteTask(w, r, id)
    default:
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
    }
}

func (h *TaskHandler) listTasks(w http.ResponseWriter, r *http.Request) {
    tasks := h.store.GetAll()
    respondJSON(w, http.StatusOK, tasks)
}

func (h *TaskHandler) createTask(w http.ResponseWriter, r *http.Request) {
    var input struct {
        Title string `json:"title"`
    }

    if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
        respondError(w, http.StatusBadRequest, "Invalid JSON")
        return
    }

    if input.Title == "" {
        respondError(w, http.StatusBadRequest, "Title is required")
        return
    }

    task := h.store.Create(input.Title)
    respondJSON(w, http.StatusCreated, task)
}

func (h *TaskHandler) getTask(w http.ResponseWriter, r *http.Request, id int) {
    task, ok := h.store.GetByID(id)
    if !ok {
        respondError(w, http.StatusNotFound, "Task not found")
        return
    }
    respondJSON(w, http.StatusOK, task)
}

func (h *TaskHandler) updateTask(w http.ResponseWriter, r *http.Request, id int) {
    var input struct {
        Title     string `json:"title"`
        Completed bool   `json:"completed"`
    }

    if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
        respondError(w, http.StatusBadRequest, "Invalid JSON")
        return
    }

    task, ok := h.store.Update(id, input.Title, input.Completed)
    if !ok {
        respondError(w, http.StatusNotFound, "Task not found")
        return
    }
    respondJSON(w, http.StatusOK, task)
}

func (h *TaskHandler) deleteTask(w http.ResponseWriter, r *http.Request, id int) {
    if !h.store.Delete(id) {
        respondError(w, http.StatusNotFound, "Task not found")
        return
    }
    w.WriteHeader(http.StatusNoContent)
}

// Helper функции
func respondJSON(w http.ResponseWriter, status int, data any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(data)
}

func respondError(w http.ResponseWriter, status int, message string) {
    respondJSON(w, status, map[string]string{"error": message})
}

func main() {
    store := NewTaskStore()
    taskHandler := &TaskHandler{store: store}

    mux := http.NewServeMux()
    mux.Handle("/api/tasks", taskHandler)
    mux.Handle("/api/tasks/", taskHandler)

    // Добавляем простые middleware
    var handler http.Handler = mux
    handler = loggingMiddleware(handler)
    handler = recoveryMiddleware(handler)

    log.Println("Server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", handler))
}

func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        log.Printf("Started %s %s", r.Method, r.URL.Path)
        next.ServeHTTP(w, r)
        log.Printf("Completed in %v", time.Since(start))
    })
}

func recoveryMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if err := recover(); err != nil {
                log.Printf("Panic: %v", err)
                http.Error(w, "Internal Server Error", http.StatusInternalServerError)
            }
        }()
        next.ServeHTTP(w, r)
    })
}
```

**Тестирование:**
```bash
# Создание задачи
curl -X POST http://localhost:8080/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn Go"}'

# Получение всех задач
curl http://localhost:8080/api/tasks

# Получение конкретной задачи
curl http://localhost:8080/api/tasks/1

# Обновление задачи
curl -X PUT http://localhost:8080/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn Go", "completed": true}'

# Удаление задачи
curl -X DELETE http://localhost:8080/api/tasks/1
```

### Пример 2: REST API с chi

Тот же API, но с использованием chi — обратите внимание, насколько код становится чище:

```go
package main

import (
    "encoding/json"
    "log"
    "net/http"
    "strconv"
    "sync"
    "time"

    "github.com/go-chi/chi/v5"
    "github.com/go-chi/chi/v5/middleware"
)

// Модель и Store — такие же как в примере 1

type Task struct {
    ID        int       `json:"id"`
    Title     string    `json:"title"`
    Completed bool      `json:"completed"`
    CreatedAt time.Time `json:"created_at"`
}

type TaskStore struct {
    mu     sync.RWMutex
    tasks  map[int]Task
    nextID int
}

func NewTaskStore() *TaskStore {
    return &TaskStore{
        tasks:  make(map[int]Task),
        nextID: 1,
    }
}

func (s *TaskStore) Create(title string) Task {
    s.mu.Lock()
    defer s.mu.Unlock()

    task := Task{
        ID:        s.nextID,
        Title:     title,
        Completed: false,
        CreatedAt: time.Now(),
    }
    s.tasks[task.ID] = task
    s.nextID++
    return task
}

func (s *TaskStore) GetAll() []Task {
    s.mu.RLock()
    defer s.mu.RUnlock()

    tasks := make([]Task, 0, len(s.tasks))
    for _, t := range s.tasks {
        tasks = append(tasks, t)
    }
    return tasks
}

func (s *TaskStore) GetByID(id int) (Task, bool) {
    s.mu.RLock()
    defer s.mu.RUnlock()

    task, ok := s.tasks[id]
    return task, ok
}

func (s *TaskStore) Update(id int, title string, completed bool) (Task, bool) {
    s.mu.Lock()
    defer s.mu.Unlock()

    task, ok := s.tasks[id]
    if !ok {
        return Task{}, false
    }

    task.Title = title
    task.Completed = completed
    s.tasks[id] = task
    return task, true
}

func (s *TaskStore) Delete(id int) bool {
    s.mu.Lock()
    defer s.mu.Unlock()

    _, ok := s.tasks[id]
    if ok {
        delete(s.tasks, id)
    }
    return ok
}

// HTTP Handlers — теперь простые функции!
type TaskHandler struct {
    store *TaskStore
}

func (h *TaskHandler) List(w http.ResponseWriter, r *http.Request) {
    tasks := h.store.GetAll()
    respondJSON(w, http.StatusOK, tasks)
}

func (h *TaskHandler) Create(w http.ResponseWriter, r *http.Request) {
    var input struct {
        Title string `json:"title"`
    }

    if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
        respondError(w, http.StatusBadRequest, "Invalid JSON")
        return
    }

    if input.Title == "" {
        respondError(w, http.StatusBadRequest, "Title is required")
        return
    }

    task := h.store.Create(input.Title)
    respondJSON(w, http.StatusCreated, task)
}

func (h *TaskHandler) Get(w http.ResponseWriter, r *http.Request) {
    // chi.URLParam — удобно получаем параметр пути!
    id, err := strconv.Atoi(chi.URLParam(r, "id"))
    if err != nil {
        respondError(w, http.StatusBadRequest, "Invalid task ID")
        return
    }

    task, ok := h.store.GetByID(id)
    if !ok {
        respondError(w, http.StatusNotFound, "Task not found")
        return
    }
    respondJSON(w, http.StatusOK, task)
}

func (h *TaskHandler) Update(w http.ResponseWriter, r *http.Request) {
    id, err := strconv.Atoi(chi.URLParam(r, "id"))
    if err != nil {
        respondError(w, http.StatusBadRequest, "Invalid task ID")
        return
    }

    var input struct {
        Title     string `json:"title"`
        Completed bool   `json:"completed"`
    }

    if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
        respondError(w, http.StatusBadRequest, "Invalid JSON")
        return
    }

    task, ok := h.store.Update(id, input.Title, input.Completed)
    if !ok {
        respondError(w, http.StatusNotFound, "Task not found")
        return
    }
    respondJSON(w, http.StatusOK, task)
}

func (h *TaskHandler) Delete(w http.ResponseWriter, r *http.Request) {
    id, err := strconv.Atoi(chi.URLParam(r, "id"))
    if err != nil {
        respondError(w, http.StatusBadRequest, "Invalid task ID")
        return
    }

    if !h.store.Delete(id) {
        respondError(w, http.StatusNotFound, "Task not found")
        return
    }
    w.WriteHeader(http.StatusNoContent)
}

func respondJSON(w http.ResponseWriter, status int, data any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(data)
}

func respondError(w http.ResponseWriter, status int, message string) {
    respondJSON(w, status, map[string]string{"error": message})
}

func main() {
    store := NewTaskStore()
    handler := &TaskHandler{store: store}

    r := chi.NewRouter()

    // Встроенные middleware chi — всё что нужно!
    r.Use(middleware.RequestID)
    r.Use(middleware.RealIP)
    r.Use(middleware.Logger)
    r.Use(middleware.Recoverer)
    r.Use(middleware.Timeout(60 * time.Second))

    // RESTful роуты — чисто и понятно
    r.Route("/api/tasks", func(r chi.Router) {
        r.Get("/", handler.List)
        r.Post("/", handler.Create)

        r.Route("/{id}", func(r chi.Router) {
            r.Get("/", handler.Get)
            r.Put("/", handler.Update)
            r.Delete("/", handler.Delete)
        })
    })

    log.Println("Server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", r))
}
```

**Сравните с первым примером:**

| Аспект | net/http | chi |
|--------|----------|-----|
| Роутинг | Ручной парсинг path | `chi.URLParam(r, "id")` |
| HTTP методы | `switch r.Method` | `r.Get()`, `r.Post()`, etc. |
| Middleware | Ручное оборачивание | `r.Use(middleware.Logger)` |
| Группировка | Нет | `r.Route("/api", ...)` |
| Количество кода | Больше | Меньше |
| Читаемость | Средняя | Высокая |

### Пример 3: Middleware chain

Production-ready набор middleware с chi:

```go
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "runtime/debug"
    "strings"
    "time"

    "github.com/go-chi/chi/v5"
    "github.com/google/uuid"
)

// ========== Кастомные типы для Context ==========

type contextKey string

const (
    requestIDKey contextKey = "requestID"
    userIDKey    contextKey = "userID"
)

// ========== Middleware ==========

// RequestID — добавляет уникальный ID к каждому запросу
func RequestIDMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        requestID := r.Header.Get("X-Request-ID")
        if requestID == "" {
            requestID = uuid.New().String()
        }

        ctx := context.WithValue(r.Context(), requestIDKey, requestID)
        w.Header().Set("X-Request-ID", requestID)

        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

// GetRequestID — хелпер для получения request ID
func GetRequestID(ctx context.Context) string {
    if id, ok := ctx.Value(requestIDKey).(string); ok {
        return id
    }
    return "unknown"
}

// Logger — структурированное логирование запросов
func LoggerMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()

        // Оборачиваем ResponseWriter для захвата статуса
        wrapped := &statusResponseWriter{ResponseWriter: w, status: 200}

        next.ServeHTTP(wrapped, r)

        log.Printf(
            "[%s] %s %s %s %d %v",
            GetRequestID(r.Context()),
            r.RemoteAddr,
            r.Method,
            r.URL.Path,
            wrapped.status,
            time.Since(start),
        )
    })
}

type statusResponseWriter struct {
    http.ResponseWriter
    status int
}

func (w *statusResponseWriter) WriteHeader(status int) {
    w.status = status
    w.ResponseWriter.WriteHeader(status)
}

// Recoverer — обработка паники с логированием stack trace
func RecovererMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if err := recover(); err != nil {
                requestID := GetRequestID(r.Context())
                log.Printf(
                    "[%s] PANIC: %v\n%s",
                    requestID,
                    err,
                    string(debug.Stack()),
                )

                w.Header().Set("Content-Type", "application/json")
                w.WriteHeader(http.StatusInternalServerError)
                json.NewEncoder(w).Encode(map[string]string{
                    "error":      "Internal Server Error",
                    "request_id": requestID,
                })
            }
        }()

        next.ServeHTTP(w, r)
    })
}

// CORS — Cross-Origin Resource Sharing
func CORSMiddleware(allowedOrigins []string) func(http.Handler) http.Handler {
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
                w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Request-ID")
                w.Header().Set("Access-Control-Allow-Credentials", "true")
                w.Header().Set("Access-Control-Max-Age", "86400")
            }

            // Preflight request
            if r.Method == http.MethodOptions {
                w.WriteHeader(http.StatusNoContent)
                return
            }

            next.ServeHTTP(w, r)
        })
    }
}

// Auth — проверка JWT токена
func AuthMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        authHeader := r.Header.Get("Authorization")
        if authHeader == "" {
            respondError(w, http.StatusUnauthorized, "Missing authorization header")
            return
        }

        // Формат: "Bearer <token>"
        parts := strings.SplitN(authHeader, " ", 2)
        if len(parts) != 2 || parts[0] != "Bearer" {
            respondError(w, http.StatusUnauthorized, "Invalid authorization format")
            return
        }

        token := parts[1]

        // Валидация токена (упрощённо)
        userID, err := validateToken(token)
        if err != nil {
            respondError(w, http.StatusUnauthorized, "Invalid token")
            return
        }

        // Добавляем userID в контекст
        ctx := context.WithValue(r.Context(), userIDKey, userID)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

// GetUserID — хелпер для получения user ID
func GetUserID(ctx context.Context) (int, bool) {
    id, ok := ctx.Value(userIDKey).(int)
    return id, ok
}

func validateToken(token string) (int, error) {
    // Упрощённая валидация для примера
    // В реальности здесь JWT парсинг
    if token == "valid-token" {
        return 1, nil
    }
    return 0, fmt.Errorf("invalid token")
}

// Timeout — ограничение времени обработки запроса
func TimeoutMiddleware(timeout time.Duration) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            ctx, cancel := context.WithTimeout(r.Context(), timeout)
            defer cancel()

            done := make(chan struct{})

            go func() {
                next.ServeHTTP(w, r.WithContext(ctx))
                close(done)
            }()

            select {
            case <-done:
                return
            case <-ctx.Done():
                requestID := GetRequestID(r.Context())
                log.Printf("[%s] Request timeout after %v", requestID, timeout)

                w.Header().Set("Content-Type", "application/json")
                w.WriteHeader(http.StatusGatewayTimeout)
                json.NewEncoder(w).Encode(map[string]string{
                    "error":      "Request timeout",
                    "request_id": requestID,
                })
            }
        })
    }
}

func respondError(w http.ResponseWriter, status int, message string) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(map[string]string{"error": message})
}

// ========== Handlers ==========

func publicHandler(w http.ResponseWriter, r *http.Request) {
    requestID := GetRequestID(r.Context())
    json.NewEncoder(w).Encode(map[string]string{
        "message":    "Hello, public!",
        "request_id": requestID,
    })
}

func protectedHandler(w http.ResponseWriter, r *http.Request) {
    requestID := GetRequestID(r.Context())
    userID, _ := GetUserID(r.Context())

    json.NewEncoder(w).Encode(map[string]any{
        "message":    "Hello, authenticated user!",
        "user_id":    userID,
        "request_id": requestID,
    })
}

func slowHandler(w http.ResponseWriter, r *http.Request) {
    // Проверяем отмену контекста
    select {
    case <-time.After(10 * time.Second):
        json.NewEncoder(w).Encode(map[string]string{"message": "Done!"})
    case <-r.Context().Done():
        // Клиент отключился или timeout
        return
    }
}

func panicHandler(w http.ResponseWriter, r *http.Request) {
    panic("intentional panic for testing")
}

// ========== Main ==========

func main() {
    r := chi.NewRouter()

    // Глобальные middleware — применяются ко всем роутам
    r.Use(RequestIDMiddleware)
    r.Use(LoggerMiddleware)
    r.Use(RecovererMiddleware)
    r.Use(CORSMiddleware([]string{"http://localhost:3000", "https://myapp.com"}))
    r.Use(TimeoutMiddleware(30 * time.Second))

    // Публичные роуты
    r.Get("/", publicHandler)
    r.Get("/health", func(w http.ResponseWriter, r *http.Request) {
        w.Write([]byte("OK"))
    })

    // Тестовые роуты
    r.Get("/slow", slowHandler)   // Для тестирования timeout
    r.Get("/panic", panicHandler) // Для тестирования recovery

    // Защищённые роуты
    r.Route("/api", func(r chi.Router) {
        r.Use(AuthMiddleware) // Auth только для /api/*

        r.Get("/me", protectedHandler)
        r.Get("/profile", protectedHandler)
    })

    log.Println("Server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", r))
}
```

**Тестирование:**
```bash
# Публичный endpoint (без auth)
curl http://localhost:8080/

# С кастомным Request ID
curl -H "X-Request-ID: my-custom-id" http://localhost:8080/

# Защищённый endpoint (без токена — 401)
curl http://localhost:8080/api/me

# Защищённый endpoint (с токеном)
curl -H "Authorization: Bearer valid-token" http://localhost:8080/api/me

# Тест timeout (отменится через 30 сек)
curl http://localhost:8080/slow

# Тест panic recovery
curl http://localhost:8080/panic
```

---
