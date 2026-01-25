# 3.5 Документация API

## Содержание

- [Введение](#введение)
- [Подходы к документации](#подходы-к-документации)
- [OpenAPI Specification](#openapi-specification)
- [swaggo: документация из кода](#swaggo-документация-из-кода)
  - [Установка и настройка](#установка-и-настройка)
  - [Аннотации](#аннотации)
  - [Документирование endpoints](#документирование-endpoints)
  - [Модели и схемы](#модели-и-схемы)
  - [Swagger UI](#swagger-ui)
- [OpenAPI-first подход](#openapi-first-подход)
  - [oapi-codegen](#oapi-codegen)
  - [Преимущества и недостатки](#преимущества-и-недостатки)
- [Практические аспекты](#практические-аспекты)
  - [Версионирование API](#версионирование-api)
  - [Authentication в документации](#authentication-в-документации)
  - [CI/CD интеграция](#cicd-интеграция)
- [Практические примеры](#практические-примеры)
  - [Пример 1: REST API с swaggo](#пример-1-rest-api-с-swaggo)
  - [Пример 2: OpenAPI-first с генерацией](#пример-2-openapi-first-с-генерацией)
- [Чек-лист](#чек-лист)

---

## Введение

Документация API критически важна для разработчиков, использующих ваш сервис. В Go есть два основных подхода: Code-first (генерация спецификации из кода) и API-first (генерация кода из спецификации).

> 💡 **Для C# разработчиков**: Вместо Swashbuckle с атрибутами `[ProducesResponseType]` в Go используется swaggo с комментариями. Концепция та же — автогенерация OpenAPI из кода.

### Что вы узнаете

- OpenAPI/Swagger спецификацию
- swaggo для генерации документации из кода
- oapi-codegen для генерации кода из OpenAPI
- Интеграцию Swagger UI
- Версионирование и аутентификацию в документации

---

## Подходы к документации

| Подход | Инструменты | Плюсы | Минусы |
|--------|-------------|-------|--------|
| **Code-first** | swaggo | Документация рядом с кодом, не рассинхронизируется | Комментарии загромождают код |
| **API-first** | oapi-codegen | Контракт определяется заранее, строгая типизация | Дополнительный шаг, сложнее рефакторить |
| **Ручной** | OpenAPI YAML | Полный контроль | Быстро устаревает |

### Сравнение с C#

| C# (ASP.NET Core) | Go |
|-------------------|-----|
| Swashbuckle | swaggo |
| NSwag | oapi-codegen |
| `[ProducesResponseType]` | `// @Success 200` |
| `[ApiExplorerSettings]` | `// @Tags` |

---

## OpenAPI Specification

OpenAPI (бывший Swagger) — стандарт описания REST API.

```yaml
# api/openapi.yaml
openapi: "3.0.3"
info:
  title: User API
  description: API для управления пользователями
  version: "1.0.0"
  contact:
    name: API Support
    email: support@example.com

servers:
  - url: http://localhost:8080/api/v1
    description: Development server
  - url: https://api.example.com/v1
    description: Production server

paths:
  /users:
    get:
      summary: Список пользователей
      description: Возвращает список всех пользователей с пагинацией
      operationId: listUsers
      tags:
        - users
      parameters:
        - name: page
          in: query
          description: Номер страницы
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          description: Количество на странице
          schema:
            type: integer
            default: 20
            maximum: 100
      responses:
        "200":
          description: Успешный ответ
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/UsersListResponse"
        "401":
          $ref: "#/components/responses/Unauthorized"

    post:
      summary: Создание пользователя
      operationId: createUser
      tags:
        - users
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CreateUserRequest"
      responses:
        "201":
          description: Пользователь создан
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/User"
        "400":
          $ref: "#/components/responses/BadRequest"
        "409":
          description: Пользователь уже существует

  /users/{id}:
    get:
      summary: Получение пользователя
      operationId: getUser
      tags:
        - users
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        "200":
          description: Успешный ответ
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/User"
        "404":
          $ref: "#/components/responses/NotFound"

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
          example: 1
        email:
          type: string
          format: email
          example: user@example.com
        name:
          type: string
          example: John Doe
        role:
          type: string
          enum: [user, admin, moderator]
        created_at:
          type: string
          format: date-time
      required:
        - id
        - email
        - name
        - role
        - created_at

    CreateUserRequest:
      type: object
      properties:
        email:
          type: string
          format: email
        name:
          type: string
          minLength: 2
          maxLength: 100
        password:
          type: string
          minLength: 8
      required:
        - email
        - name
        - password

    UsersListResponse:
      type: object
      properties:
        users:
          type: array
          items:
            $ref: "#/components/schemas/User"
        total:
          type: integer
        page:
          type: integer
        limit:
          type: integer

    Error:
      type: object
      properties:
        error:
          type: string
        details:
          type: object
          additionalProperties:
            type: string

  responses:
    BadRequest:
      description: Некорректный запрос
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"
    Unauthorized:
      description: Требуется аутентификация
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"
    NotFound:
      description: Ресурс не найден
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

---

## swaggo: документация из кода

[swaggo](https://github.com/swaggo/swag) генерирует OpenAPI спецификацию из комментариев в коде.

### Установка и настройка

```bash
# Установка CLI
go install github.com/swaggo/swag/cmd/swag@latest

# Зависимости для проекта
go get github.com/swaggo/http-swagger
go get github.com/swaggo/swag
```

### Аннотации

Главные аннотации размещаются в `main.go`:

```go
// main.go
package main

import (
    "log"
    "net/http"

    "github.com/go-chi/chi/v5"
    httpSwagger "github.com/swaggo/http-swagger"

    _ "myapp/docs" // Сгенерированная документация
    "myapp/internal/handler"
)

// @title           User API
// @version         1.0
// @description     API для управления пользователями
// @termsOfService  http://example.com/terms/

// @contact.name   API Support
// @contact.url    http://example.com/support
// @contact.email  support@example.com

// @license.name  MIT
// @license.url   https://opensource.org/licenses/MIT

// @host      localhost:8080
// @BasePath  /api/v1

// @securityDefinitions.apikey BearerAuth
// @in header
// @name Authorization
// @description Введите токен в формате: Bearer <token>

// @externalDocs.description  OpenAPI
// @externalDocs.url          https://swagger.io/resources/open-api/
func main() {
    r := chi.NewRouter()

    // API routes
    r.Route("/api/v1", func(r chi.Router) {
        r.Mount("/users", handler.NewUserHandler().Routes())
    })

    // Swagger UI
    r.Get("/swagger/*", httpSwagger.Handler(
        httpSwagger.URL("http://localhost:8080/swagger/doc.json"),
    ))

    log.Println("Server starting on :8080")
    log.Println("Swagger UI: http://localhost:8080/swagger/index.html")
    log.Fatal(http.ListenAndServe(":8080", r))
}
```

### Документирование endpoints

```go
// internal/handler/user_handler.go
package handler

import (
    "encoding/json"
    "net/http"
    "strconv"

    "github.com/go-chi/chi/v5"
)

type UserHandler struct {
    service UserService
}

func NewUserHandler() *UserHandler {
    return &UserHandler{}
}

func (h *UserHandler) Routes() chi.Router {
    r := chi.NewRouter()

    r.Get("/", h.List)
    r.Post("/", h.Create)
    r.Get("/{id}", h.Get)
    r.Put("/{id}", h.Update)
    r.Delete("/{id}", h.Delete)

    return r
}

// List godoc
// @Summary      Список пользователей
// @Description  Возвращает список всех пользователей с пагинацией
// @Tags         users
// @Accept       json
// @Produce      json
// @Param        page   query     int  false  "Номер страницы"  default(1)
// @Param        limit  query     int  false  "Количество на странице"  default(20) maximum(100)
// @Success      200    {object}  UsersListResponse
// @Failure      500    {object}  ErrorResponse
// @Router       /users [get]
func (h *UserHandler) List(w http.ResponseWriter, r *http.Request) {
    page, _ := strconv.Atoi(r.URL.Query().Get("page"))
    if page < 1 {
        page = 1
    }
    limit, _ := strconv.Atoi(r.URL.Query().Get("limit"))
    if limit < 1 || limit > 100 {
        limit = 20
    }

    // Бизнес-логика...
    users := []User{} // Получаем из сервиса

    respondJSON(w, http.StatusOK, UsersListResponse{
        Users: users,
        Total: len(users),
        Page:  page,
        Limit: limit,
    })
}

// Create godoc
// @Summary      Создание пользователя
// @Description  Создаёт нового пользователя
// @Tags         users
// @Accept       json
// @Produce      json
// @Param        request  body      CreateUserRequest  true  "Данные пользователя"
// @Success      201      {object}  User
// @Failure      400      {object}  ErrorResponse
// @Failure      409      {object}  ErrorResponse  "Пользователь уже существует"
// @Security     BearerAuth
// @Router       /users [post]
func (h *UserHandler) Create(w http.ResponseWriter, r *http.Request) {
    var req CreateUserRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        respondError(w, http.StatusBadRequest, "Invalid JSON")
        return
    }

    // Валидация и создание...
    user := User{ID: 1, Email: req.Email, Name: req.Name}

    respondJSON(w, http.StatusCreated, user)
}

// Get godoc
// @Summary      Получение пользователя
// @Description  Возвращает пользователя по ID
// @Tags         users
// @Accept       json
// @Produce      json
// @Param        id   path      int  true  "User ID"
// @Success      200  {object}  User
// @Failure      404  {object}  ErrorResponse
// @Router       /users/{id} [get]
func (h *UserHandler) Get(w http.ResponseWriter, r *http.Request) {
    id, err := strconv.Atoi(chi.URLParam(r, "id"))
    if err != nil {
        respondError(w, http.StatusBadRequest, "Invalid ID")
        return
    }

    // Получаем пользователя...
    user := User{ID: id, Email: "user@example.com", Name: "John"}

    respondJSON(w, http.StatusOK, user)
}

// Update godoc
// @Summary      Обновление пользователя
// @Description  Обновляет данные пользователя
// @Tags         users
// @Accept       json
// @Produce      json
// @Param        id       path      int                true  "User ID"
// @Param        request  body      UpdateUserRequest  true  "Новые данные"
// @Success      200      {object}  User
// @Failure      400      {object}  ErrorResponse
// @Failure      404      {object}  ErrorResponse
// @Security     BearerAuth
// @Router       /users/{id} [put]
func (h *UserHandler) Update(w http.ResponseWriter, r *http.Request) {
    // Реализация...
}

// Delete godoc
// @Summary      Удаление пользователя
// @Description  Удаляет пользователя по ID
// @Tags         users
// @Accept       json
// @Produce      json
// @Param        id   path      int  true  "User ID"
// @Success      204  "Пользователь удалён"
// @Failure      404  {object}  ErrorResponse
// @Security     BearerAuth
// @Router       /users/{id} [delete]
func (h *UserHandler) Delete(w http.ResponseWriter, r *http.Request) {
    // Реализация...
    w.WriteHeader(http.StatusNoContent)
}
```

### Модели и схемы

```go
// internal/handler/dto.go
package handler

import "time"

// User представляет пользователя
// @Description Модель пользователя
type User struct {
    ID        int       `json:"id" example:"1"`
    Email     string    `json:"email" example:"user@example.com"`
    Name      string    `json:"name" example:"John Doe"`
    Role      string    `json:"role" example:"user" enums:"user,admin,moderator"`
    CreatedAt time.Time `json:"created_at" example:"2024-01-15T10:30:00Z"`
}

// CreateUserRequest запрос на создание пользователя
// @Description Данные для создания пользователя
type CreateUserRequest struct {
    Email    string `json:"email" example:"user@example.com" validate:"required,email"`
    Name     string `json:"name" example:"John Doe" validate:"required,min=2,max=100"`
    Password string `json:"password" example:"secretpass123" validate:"required,min=8"`
}

// UpdateUserRequest запрос на обновление пользователя
type UpdateUserRequest struct {
    Name *string `json:"name,omitempty" example:"John Doe"`
    Role *string `json:"role,omitempty" example:"admin" enums:"user,admin,moderator"`
}

// UsersListResponse ответ со списком пользователей
type UsersListResponse struct {
    Users []User `json:"users"`
    Total int    `json:"total" example:"100"`
    Page  int    `json:"page" example:"1"`
    Limit int    `json:"limit" example:"20"`
}

// ErrorResponse ответ с ошибкой
// @Description Стандартный ответ с ошибкой
type ErrorResponse struct {
    Error   string            `json:"error" example:"Validation failed"`
    Details map[string]string `json:"details,omitempty"`
}
```

### Генерация документации

```bash
# Генерация docs/
swag init -g cmd/api/main.go -o docs

# Или с указанием папок для парсинга
swag init -g cmd/api/main.go -o docs --parseDependency --parseInternal

# Форматирование комментариев
swag fmt
```

Сгенерированные файлы:

```
docs/
├── docs.go       # Go код для импорта
├── swagger.json  # OpenAPI спецификация (JSON)
└── swagger.yaml  # OpenAPI спецификация (YAML)
```

### Swagger UI

```go
import (
    httpSwagger "github.com/swaggo/http-swagger"
    _ "myapp/docs"
)

// Подключение Swagger UI
r.Get("/swagger/*", httpSwagger.Handler(
    httpSwagger.URL("/swagger/doc.json"),
    httpSwagger.DeepLinking(true),
    httpSwagger.DocExpansion("none"),
    httpSwagger.DomID("swagger-ui"),
))

// Или с кастомными настройками
r.Get("/swagger/*", httpSwagger.WrapHandler)
```

Теперь Swagger UI доступен по адресу: `http://localhost:8080/swagger/index.html`

---

## OpenAPI-first подход

При OpenAPI-first подходе сначала пишется спецификация, затем генерируется код.

### oapi-codegen

[oapi-codegen](https://github.com/deepmap/oapi-codegen) генерирует Go код из OpenAPI спецификации.

```bash
go install github.com/deepmap/oapi-codegen/v2/cmd/oapi-codegen@latest
```

```yaml
# oapi-codegen.yaml
package: api
output: internal/api/api.gen.go
generate:
  models: true
  chi-server: true
  strict-server: true
```

```bash
# Генерация
oapi-codegen -config oapi-codegen.yaml api/openapi.yaml
```

Сгенерированный код:

```go
// internal/api/api.gen.go (сгенерировано)
package api

import (
    "context"
    "net/http"

    "github.com/go-chi/chi/v5"
)

// User defines model for User.
type User struct {
    Id        int       `json:"id"`
    Email     string    `json:"email"`
    Name      string    `json:"name"`
    Role      string    `json:"role"`
    CreatedAt time.Time `json:"created_at"`
}

// CreateUserRequest defines model for CreateUserRequest.
type CreateUserRequest struct {
    Email    string `json:"email"`
    Name     string `json:"name"`
    Password string `json:"password"`
}

// StrictServerInterface — интерфейс, который нужно реализовать
type StrictServerInterface interface {
    // Список пользователей
    // (GET /users)
    ListUsers(ctx context.Context, request ListUsersRequestObject) (ListUsersResponseObject, error)

    // Создание пользователя
    // (POST /users)
    CreateUser(ctx context.Context, request CreateUserRequestObject) (CreateUserResponseObject, error)

    // Получение пользователя
    // (GET /users/{id})
    GetUser(ctx context.Context, request GetUserRequestObject) (GetUserResponseObject, error)
}

// Типизированные request/response
type ListUsersRequestObject struct {
    Params ListUsersParams
}

type ListUsersResponseObject interface {
    VisitListUsersResponse(w http.ResponseWriter) error
}

type ListUsers200JSONResponse UsersListResponse

func (response ListUsers200JSONResponse) VisitListUsersResponse(w http.ResponseWriter) error {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(200)
    return json.NewEncoder(w).Encode(response)
}

// Handler — подключение к chi
func Handler(si StrictServerInterface) http.Handler {
    return HandlerWithOptions(si, ChiServerOptions{})
}
```

### Реализация сервера

```go
// internal/api/server.go
package api

import (
    "context"

    "myapp/internal/service"
)

type Server struct {
    userService *service.UserService
}

func NewServer(userService *service.UserService) *Server {
    return &Server{userService: userService}
}

// Проверка реализации интерфейса
var _ StrictServerInterface = (*Server)(nil)

func (s *Server) ListUsers(ctx context.Context, request ListUsersRequestObject) (ListUsersResponseObject, error) {
    page := 1
    if request.Params.Page != nil {
        page = *request.Params.Page
    }
    limit := 20
    if request.Params.Limit != nil {
        limit = *request.Params.Limit
    }

    users, total, err := s.userService.List(ctx, page, limit)
    if err != nil {
        return nil, err
    }

    // Маппинг domain -> API модели
    apiUsers := make([]User, len(users))
    for i, u := range users {
        apiUsers[i] = User{
            Id:        u.ID,
            Email:     u.Email,
            Name:      u.Name,
            Role:      u.Role,
            CreatedAt: u.CreatedAt,
        }
    }

    return ListUsers200JSONResponse{
        Users: apiUsers,
        Total: total,
        Page:  page,
        Limit: limit,
    }, nil
}

func (s *Server) CreateUser(ctx context.Context, request CreateUserRequestObject) (CreateUserResponseObject, error) {
    user, err := s.userService.Create(ctx, service.CreateUserInput{
        Email:    request.Body.Email,
        Name:     request.Body.Name,
        Password: request.Body.Password,
    })
    if err != nil {
        // Обработка ошибок...
        return nil, err
    }

    return CreateUser201JSONResponse{
        Id:        user.ID,
        Email:     user.Email,
        Name:      user.Name,
        Role:      user.Role,
        CreatedAt: user.CreatedAt,
    }, nil
}

func (s *Server) GetUser(ctx context.Context, request GetUserRequestObject) (GetUserResponseObject, error) {
    user, err := s.userService.GetByID(ctx, request.Id)
    if err != nil {
        return nil, err
    }
    if user == nil {
        return GetUser404JSONResponse{Error: "User not found"}, nil
    }

    return GetUser200JSONResponse{
        Id:        user.ID,
        Email:     user.Email,
        Name:      user.Name,
        Role:      user.Role,
        CreatedAt: user.CreatedAt,
    }, nil
}
```

```go
// cmd/api/main.go
package main

import (
    "log"
    "net/http"

    "github.com/go-chi/chi/v5"

    "myapp/internal/api"
    "myapp/internal/service"
)

func main() {
    userService := service.NewUserService()
    server := api.NewServer(userService)

    r := chi.NewRouter()

    // Подключение сгенерированного handler
    r.Mount("/api/v1", api.Handler(api.NewStrictHandler(server, nil)))

    log.Println("Server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", r))
}
```

### Преимущества и недостатки

| Подход | Плюсы | Минусы |
|--------|-------|--------|
| **Code-first (swaggo)** | Документация рядом с кодом, быстро начать | Комментарии загромождают, нет строгой типизации |
| **API-first (oapi-codegen)** | Строгий контракт, type-safe, сложнее сломать API | Дополнительный шаг генерации, сложнее рефакторить |

### Когда что использовать

```
Code-first (swaggo):
- Быстрая разработка MVP
- API эволюционирует вместе с кодом
- Небольшая команда

API-first (oapi-codegen):
- API — контракт между командами
- Важна обратная совместимость
- Параллельная разработка frontend/backend
- Микросервисы с чётким API
```

---

## Практические аспекты

### Версионирование API

```go
// Способ 1: В URL path
// @BasePath /api/v1
r.Route("/api/v1", func(r chi.Router) {
    r.Mount("/users", userHandlerV1.Routes())
})

r.Route("/api/v2", func(r chi.Router) {
    r.Mount("/users", userHandlerV2.Routes())
})

// Способ 2: В заголовке
// @Param X-API-Version header string false "API Version" default(1)
func versionMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        version := r.Header.Get("X-API-Version")
        if version == "" {
            version = "1"
        }
        ctx := context.WithValue(r.Context(), "api_version", version)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

// Способ 3: Accept header (Content Negotiation)
// Accept: application/vnd.myapp.v2+json
```

### Authentication в документации

```go
// main.go

// @securityDefinitions.apikey BearerAuth
// @in header
// @name Authorization
// @description JWT токен в формате: Bearer <token>

// @securityDefinitions.oauth2.password OAuth2Password
// @tokenUrl /api/v1/auth/token
// @scope.read Read access
// @scope.write Write access

// @securityDefinitions.basic BasicAuth
```

```go
// В handler

// @Security BearerAuth
// @Security OAuth2Password[read, write]
func (h *Handler) ProtectedEndpoint(w http.ResponseWriter, r *http.Request) {
    // ...
}
```

### CI/CD интеграция

```yaml
# .github/workflows/api-docs.yml
name: API Documentation

on:
  push:
    branches: [main]
    paths:
      - 'internal/handler/**'
      - 'cmd/api/**'

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Go
        uses: actions/setup-go@v5
        with:
          go-version: '1.23'

      - name: Install swag
        run: go install github.com/swaggo/swag/cmd/swag@latest

      - name: Generate Swagger docs
        run: swag init -g cmd/api/main.go -o docs

      - name: Check for changes
        run: |
          if [[ -n $(git status --porcelain docs/) ]]; then
            echo "Documentation is out of date!"
            git diff docs/
            exit 1
          fi

      - name: Upload OpenAPI spec
        uses: actions/upload-artifact@v4
        with:
          name: openapi-spec
          path: docs/swagger.yaml

  validate-spec:
    runs-on: ubuntu-latest
    needs: generate-docs
    steps:
      - name: Download spec
        uses: actions/download-artifact@v4
        with:
          name: openapi-spec

      - name: Validate OpenAPI
        uses: char0n/swagger-editor-validate@v1
        with:
          definition-file: swagger.yaml
```

```makefile
# Makefile
.PHONY: swagger
swagger:
	swag init -g cmd/api/main.go -o docs
	swag fmt

.PHONY: swagger-check
swagger-check:
	swag init -g cmd/api/main.go -o docs --outputTypes yaml
	@if [ -n "$$(git status --porcelain docs/)" ]; then \
		echo "Swagger docs are out of date. Run 'make swagger'"; \
		exit 1; \
	fi
```

---

## Практические примеры

### Пример 1: REST API с swaggo

Полный пример API с документацией:

```go
// cmd/api/main.go
package main

import (
    "log"
    "net/http"

    "github.com/go-chi/chi/v5"
    "github.com/go-chi/chi/v5/middleware"
    httpSwagger "github.com/swaggo/http-swagger"

    _ "myapp/docs"
    "myapp/internal/handler"
)

// @title           Product API
// @version         1.0
// @description     API для управления продуктами интернет-магазина

// @contact.name   API Support
// @contact.email  api@example.com

// @license.name  MIT

// @host      localhost:8080
// @BasePath  /api/v1

// @securityDefinitions.apikey BearerAuth
// @in header
// @name Authorization
func main() {
    r := chi.NewRouter()

    r.Use(middleware.Logger)
    r.Use(middleware.Recoverer)

    r.Route("/api/v1", func(r chi.Router) {
        r.Mount("/products", handler.NewProductHandler().Routes())
        r.Mount("/categories", handler.NewCategoryHandler().Routes())
    })

    r.Get("/swagger/*", httpSwagger.Handler(
        httpSwagger.URL("/swagger/doc.json"),
    ))

    r.Get("/health", func(w http.ResponseWriter, r *http.Request) {
        w.Write([]byte("OK"))
    })

    log.Println("Server: http://localhost:8080")
    log.Println("Swagger: http://localhost:8080/swagger/index.html")
    log.Fatal(http.ListenAndServe(":8080", r))
}
```

```go
// internal/handler/product_handler.go
package handler

import (
    "encoding/json"
    "net/http"
    "strconv"

    "github.com/go-chi/chi/v5"
)

// Product модель продукта
// @Description Продукт в каталоге
type Product struct {
    ID          int      `json:"id" example:"1"`
    Name        string   `json:"name" example:"iPhone 15 Pro"`
    Description string   `json:"description" example:"Смартфон Apple"`
    Price       float64  `json:"price" example:"999.99"`
    Currency    string   `json:"currency" example:"USD"`
    CategoryID  int      `json:"category_id" example:"1"`
    Stock       int      `json:"stock" example:"100"`
    Tags        []string `json:"tags" example:"smartphone,apple,new"`
}

// CreateProductRequest запрос на создание продукта
type CreateProductRequest struct {
    Name        string   `json:"name" example:"iPhone 15 Pro" validate:"required,min=2,max=200"`
    Description string   `json:"description" example:"Смартфон Apple" validate:"max=5000"`
    Price       float64  `json:"price" example:"999.99" validate:"required,gt=0"`
    Currency    string   `json:"currency" example:"USD" validate:"required,oneof=USD EUR RUB"`
    CategoryID  int      `json:"category_id" example:"1" validate:"required,gt=0"`
    Stock       int      `json:"stock" example:"100" validate:"gte=0"`
    Tags        []string `json:"tags" example:"smartphone,apple" validate:"max=10"`
}

// ProductsListResponse ответ со списком продуктов
type ProductsListResponse struct {
    Products []Product `json:"products"`
    Total    int       `json:"total" example:"150"`
    Page     int       `json:"page" example:"1"`
    Limit    int       `json:"limit" example:"20"`
}

type ProductHandler struct{}

func NewProductHandler() *ProductHandler {
    return &ProductHandler{}
}

func (h *ProductHandler) Routes() chi.Router {
    r := chi.NewRouter()

    r.Get("/", h.List)
    r.Post("/", h.Create)
    r.Get("/{id}", h.Get)
    r.Put("/{id}", h.Update)
    r.Delete("/{id}", h.Delete)
    r.Get("/search", h.Search)

    return r
}

// List godoc
// @Summary      Список продуктов
// @Description  Возвращает список продуктов с пагинацией и фильтрацией
// @Tags         products
// @Accept       json
// @Produce      json
// @Param        page        query     int     false  "Номер страницы"        default(1)
// @Param        limit       query     int     false  "Количество на странице" default(20) maximum(100)
// @Param        category_id query     int     false  "Фильтр по категории"
// @Param        min_price   query     number  false  "Минимальная цена"
// @Param        max_price   query     number  false  "Максимальная цена"
// @Success      200         {object}  ProductsListResponse
// @Failure      500         {object}  ErrorResponse
// @Router       /products [get]
func (h *ProductHandler) List(w http.ResponseWriter, r *http.Request) {
    // Парсинг параметров...
    products := []Product{
        {ID: 1, Name: "iPhone 15 Pro", Price: 999.99, Currency: "USD", Stock: 50},
        {ID: 2, Name: "MacBook Pro", Price: 1999.99, Currency: "USD", Stock: 30},
    }

    respondJSON(w, http.StatusOK, ProductsListResponse{
        Products: products,
        Total:    2,
        Page:     1,
        Limit:    20,
    })
}

// Create godoc
// @Summary      Создание продукта
// @Description  Создаёт новый продукт в каталоге
// @Tags         products
// @Accept       json
// @Produce      json
// @Param        request  body      CreateProductRequest  true  "Данные продукта"
// @Success      201      {object}  Product
// @Failure      400      {object}  ErrorResponse
// @Failure      401      {object}  ErrorResponse
// @Security     BearerAuth
// @Router       /products [post]
func (h *ProductHandler) Create(w http.ResponseWriter, r *http.Request) {
    var req CreateProductRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        respondError(w, http.StatusBadRequest, "Invalid JSON")
        return
    }

    product := Product{
        ID:          1,
        Name:        req.Name,
        Description: req.Description,
        Price:       req.Price,
        Currency:    req.Currency,
        CategoryID:  req.CategoryID,
        Stock:       req.Stock,
        Tags:        req.Tags,
    }

    respondJSON(w, http.StatusCreated, product)
}

// Get godoc
// @Summary      Получение продукта
// @Description  Возвращает продукт по ID
// @Tags         products
// @Accept       json
// @Produce      json
// @Param        id   path      int  true  "Product ID"
// @Success      200  {object}  Product
// @Failure      404  {object}  ErrorResponse
// @Router       /products/{id} [get]
func (h *ProductHandler) Get(w http.ResponseWriter, r *http.Request) {
    id, _ := strconv.Atoi(chi.URLParam(r, "id"))

    product := Product{
        ID:       id,
        Name:     "iPhone 15 Pro",
        Price:    999.99,
        Currency: "USD",
        Stock:    50,
    }

    respondJSON(w, http.StatusOK, product)
}

// Update godoc
// @Summary      Обновление продукта
// @Description  Обновляет данные продукта
// @Tags         products
// @Accept       json
// @Produce      json
// @Param        id       path      int                   true  "Product ID"
// @Param        request  body      CreateProductRequest  true  "Новые данные"
// @Success      200      {object}  Product
// @Failure      400      {object}  ErrorResponse
// @Failure      404      {object}  ErrorResponse
// @Security     BearerAuth
// @Router       /products/{id} [put]
func (h *ProductHandler) Update(w http.ResponseWriter, r *http.Request) {
    // Реализация...
    w.WriteHeader(http.StatusOK)
}

// Delete godoc
// @Summary      Удаление продукта
// @Description  Удаляет продукт по ID
// @Tags         products
// @Param        id   path      int  true  "Product ID"
// @Success      204  "Продукт удалён"
// @Failure      404  {object}  ErrorResponse
// @Security     BearerAuth
// @Router       /products/{id} [delete]
func (h *ProductHandler) Delete(w http.ResponseWriter, r *http.Request) {
    w.WriteHeader(http.StatusNoContent)
}

// Search godoc
// @Summary      Поиск продуктов
// @Description  Полнотекстовый поиск по продуктам
// @Tags         products
// @Accept       json
// @Produce      json
// @Param        q      query     string  true   "Поисковый запрос" minLength(2)
// @Param        limit  query     int     false  "Лимит результатов" default(10) maximum(50)
// @Success      200    {object}  ProductsListResponse
// @Failure      400    {object}  ErrorResponse
// @Router       /products/search [get]
func (h *ProductHandler) Search(w http.ResponseWriter, r *http.Request) {
    query := r.URL.Query().Get("q")
    if len(query) < 2 {
        respondError(w, http.StatusBadRequest, "Query must be at least 2 characters")
        return
    }

    // Поиск...
    respondJSON(w, http.StatusOK, ProductsListResponse{
        Products: []Product{},
        Total:    0,
    })
}

// Helpers
func respondJSON(w http.ResponseWriter, status int, data any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(data)
}

func respondError(w http.ResponseWriter, status int, message string) {
    respondJSON(w, status, ErrorResponse{Error: message})
}

type ErrorResponse struct {
    Error   string            `json:"error" example:"Validation failed"`
    Details map[string]string `json:"details,omitempty"`
}
```

### Пример 2: OpenAPI-first с генерацией

Структура проекта:

```
myapp/
├── api/
│   └── openapi.yaml          # OpenAPI спецификация
├── oapi-codegen.yaml         # Конфигурация генератора
├── internal/
│   ├── api/
│   │   ├── api.gen.go        # Сгенерированный код
│   │   └── server.go         # Реализация
│   └── service/
│       └── user_service.go
├── cmd/
│   └── api/
│       └── main.go
└── Makefile
```

```yaml
# oapi-codegen.yaml
package: api
output: internal/api/api.gen.go
generate:
  models: true
  chi-server: true
  strict-server: true
  embedded-spec: true
```

```makefile
# Makefile
.PHONY: generate
generate:
	oapi-codegen -config oapi-codegen.yaml api/openapi.yaml

.PHONY: validate
validate:
	swagger-cli validate api/openapi.yaml

.PHONY: serve-docs
serve-docs:
	swagger-ui-watcher api/openapi.yaml
```

---

## Чек-лист

После изучения этого раздела вы должны уметь:

- [ ] Писать OpenAPI спецификацию
- [ ] Настроить swaggo для генерации документации
- [ ] Документировать endpoints с помощью аннотаций
- [ ] Описывать модели и схемы данных
- [ ] Интегрировать Swagger UI
- [ ] Использовать oapi-codegen для API-first подхода
- [ ] Настроить аутентификацию в документации
- [ ] Версионировать API
- [ ] Интегрировать генерацию документации в CI/CD

---

## Итоги Части 3

Вы изучили основы web-разработки на Go:

1. **HTTP в Go** — net/http, middleware, роутеры (chi)
2. **Структура проекта** — Standard Layout, Clean Architecture, DI
3. **Работа с данными** — pgx, sqlc, миграции, Repository
4. **Валидация** — validator, JSON, Protocol Buffers
5. **Документация** — swaggo, OpenAPI, Swagger UI

### Следующие шаги

Переходите к [Части 4: Инфраструктура](../part4-infrastructure/) — Redis, Kafka, gRPC, Observability.

---

**Вопросы?** Открой issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Валидация и сериализация](./04_validation_serialization.md) | [Часть 4: Инфраструктура →](../part4-infrastructure/)
