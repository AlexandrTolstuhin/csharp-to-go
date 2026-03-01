# 3.2 Структура проекта Go

## Содержание

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Введение](#%D0%B2%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5)
  - [Что вы узнаете](#%D1%87%D1%82%D0%BE-%D0%B2%D1%8B-%D1%83%D0%B7%D0%BD%D0%B0%D0%B5%D1%82%D0%B5)
- [Философия структуры в Go](#%D1%84%D0%B8%D0%BB%D0%BE%D1%81%D0%BE%D1%84%D0%B8%D1%8F-%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D1%83%D1%80%D1%8B-%D0%B2-go)
  - [Ключевые принципы](#%D0%BA%D0%BB%D1%8E%D1%87%D0%B5%D0%B2%D1%8B%D0%B5-%D0%BF%D1%80%D0%B8%D0%BD%D1%86%D0%B8%D0%BF%D1%8B)
  - [C# vs Go: организация кода](#c-vs-go-%D0%BE%D1%80%D0%B3%D0%B0%D0%BD%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-%D0%BA%D0%BE%D0%B4%D0%B0)
  - [Правило: усложняй только когда нужно](#%D0%BF%D1%80%D0%B0%D0%B2%D0%B8%D0%BB%D0%BE-%D1%83%D1%81%D0%BB%D0%BE%D0%B6%D0%BD%D1%8F%D0%B9-%D1%82%D0%BE%D0%BB%D1%8C%D0%BA%D0%BE-%D0%BA%D0%BE%D0%B3%D0%B4%D0%B0-%D0%BD%D1%83%D0%B6%D0%BD%D0%BE)
- [Flat Structure (плоская структура)](#flat-structure-%D0%BF%D0%BB%D0%BE%D1%81%D0%BA%D0%B0%D1%8F-%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D1%83%D1%80%D0%B0)
  - [Когда использовать](#%D0%BA%D0%BE%D0%B3%D0%B4%D0%B0-%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D1%8C)
  - [Пример структуры](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D1%83%D1%80%D1%8B)
  - [Преимущества](#%D0%BF%D1%80%D0%B5%D0%B8%D0%BC%D1%83%D1%89%D0%B5%D1%81%D1%82%D0%B2%D0%B0)
  - [Недостатки](#%D0%BD%D0%B5%D0%B4%D0%BE%D1%81%D1%82%D0%B0%D1%82%D0%BA%D0%B8)
  - [Пример кода (flat structure)](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-%D0%BA%D0%BE%D0%B4%D0%B0-flat-structure)
- [Standard Go Project Layout](#standard-go-project-layout)
  - [Основные директории](#%D0%BE%D1%81%D0%BD%D0%BE%D0%B2%D0%BD%D1%8B%D0%B5-%D0%B4%D0%B8%D1%80%D0%B5%D0%BA%D1%82%D0%BE%D1%80%D0%B8%D0%B8)
  - [Описание директорий](#%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B5-%D0%B4%D0%B8%D1%80%D0%B5%D0%BA%D1%82%D0%BE%D1%80%D0%B8%D0%B9)
  - [internal/ — ваш лучший друг](#internal--%D0%B2%D0%B0%D1%88-%D0%BB%D1%83%D1%87%D1%88%D0%B8%D0%B9-%D0%B4%D1%80%D1%83%D0%B3)
  - [Когда НЕ нужен этот layout](#%D0%BA%D0%BE%D0%B3%D0%B4%D0%B0-%D0%BD%D0%B5-%D0%BD%D1%83%D0%B6%D0%B5%D0%BD-%D1%8D%D1%82%D0%BE%D1%82-layout)
- [Clean Architecture в Go](#clean-architecture-%D0%B2-go)
  - [Слои и зависимости](#%D1%81%D0%BB%D0%BE%D0%B8-%D0%B8-%D0%B7%D0%B0%D0%B2%D0%B8%D1%81%D0%B8%D0%BC%D0%BE%D1%81%D1%82%D0%B8)
  - [Реализация в Go](#%D1%80%D0%B5%D0%B0%D0%BB%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-%D0%B2-go)
  - [Пример кода (Clean Architecture)](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-%D0%BA%D0%BE%D0%B4%D0%B0-clean-architecture)
    - [Domain Layer](#domain-layer)
    - [Application Layer (Use Cases)](#application-layer-use-cases)
    - [Adapter Layer (HTTP Handler)](#adapter-layer-http-handler)
    - [Adapter Layer (Repository)](#adapter-layer-repository)
  - [Сравнение с C#](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81-c)
- [Dependency Injection](#dependency-injection)
  - [Manual DI (идиоматичный Go)](#manual-di-%D0%B8%D0%B4%D0%B8%D0%BE%D0%BC%D0%B0%D1%82%D0%B8%D1%87%D0%BD%D1%8B%D0%B9-go)
  - [Wire (Google)](#wire-google)
  - [Fx (Uber)](#fx-uber)
  - [Сравнение подходов](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-%D0%BF%D0%BE%D0%B4%D1%85%D0%BE%D0%B4%D0%BE%D0%B2)
  - [Рекомендации](#%D1%80%D0%B5%D0%BA%D0%BE%D0%BC%D0%B5%D0%BD%D0%B4%D0%B0%D1%86%D0%B8%D0%B8)
- [Configuration](#configuration)
  - [Environment variables](#environment-variables)
  - [Viper для сложных конфигов](#viper-%D0%B4%D0%BB%D1%8F-%D1%81%D0%BB%D0%BE%D0%B6%D0%BD%D1%8B%D1%85-%D0%BA%D0%BE%D0%BD%D1%84%D0%B8%D0%B3%D0%BE%D0%B2)
  - [Сравнение с C#](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81-c-1)
- [Практические примеры](#%D0%BF%D1%80%D0%B0%D0%BA%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B5-%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80%D1%8B)
  - [Пример 1: Flat structure для микросервиса](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-1-flat-structure-%D0%B4%D0%BB%D1%8F-%D0%BC%D0%B8%D0%BA%D1%80%D0%BE%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D0%B0)
  - [Пример 2: Clean Architecture](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-2-clean-architecture)
  - [Пример 3: DI с Wire](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-3-di-%D1%81-wire)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

---

## Введение

Структура проекта в Go кардинально отличается от C#. Нет Solution/Project файлов, нет жёсткой иерархии namespace'ов, нет требования "один класс — один файл". Go продвигает простоту и практичность.

> 💡 **Для C# разработчиков**: Забудьте про `.sln`, `.csproj`, вложенные папки по namespace'ам. В Go структура проекта — это просто папки с файлами `.go`. Один пакет = одна папка.

### Что вы узнаете

- Когда использовать плоскую структуру, а когда — сложную
- Standard Go Project Layout и его директории
- Clean Architecture в контексте Go
- Dependency Injection: от manual до Wire/Fx
- Работа с конфигурацией

---

## Философия структуры в Go

### Ключевые принципы

| Принцип | Описание |
|---------|----------|
| **Начинай просто** | Не создавай сложную структуру "на вырост" |
| **Пакет = директория** | Один пакет живёт в одной папке |
| **internal/** | Код недоступный извне модуля |
| **Минимум зависимостей** | Пакеты должны быть слабо связаны |
| **Явность** | Структура должна быть понятна без документации |

### C# vs Go: организация кода

```
# C# Solution
MySolution/
├── MySolution.sln
├── MyApp.Api/
│   ├── MyApp.Api.csproj
│   ├── Controllers/
│   │   └── UsersController.cs
│   ├── Services/
│   │   └── UserService.cs
│   └── Program.cs
├── MyApp.Domain/
│   ├── MyApp.Domain.csproj
│   └── Entities/
│       └── User.cs
└── MyApp.Infrastructure/
    ├── MyApp.Infrastructure.csproj
    └── Repositories/
        └── UserRepository.cs
```

```
# Go Module (простой вариант)
myapp/
├── go.mod
├── go.sum
├── main.go
├── handler.go
├── service.go
├── repository.go
└── model.go
```

```
# Go Module (сложный вариант)
myapp/
├── go.mod
├── go.sum
├── cmd/
│   └── api/
│       └── main.go
├── internal/
│   ├── handler/
│   ├── service/
│   └── repository/
└── pkg/
    └── validator/
```

### Правило: усложняй только когда нужно

```
Маленький проект (< 5 файлов)     → Flat structure
Средний проект (5-20 файлов)      → Группировка по назначению
Большой проект / команда          → Standard Layout + Clean Architecture
Библиотека для переиспользования  → pkg/ структура
```

---

## Flat Structure (плоская структура)

Простейший подход — все файлы в корне пакета.

### Когда использовать

- Микросервисы с ограниченной ответственностью
- CLI утилиты
- Небольшие API (< 10 endpoints)
- Прототипы и MVP

### Пример структуры

```
user-service/
├── go.mod
├── go.sum
├── main.go          # Entry point, инициализация
├── config.go        # Конфигурация
├── handler.go       # HTTP handlers
├── service.go       # Бизнес-логика
├── repository.go    # Работа с БД
├── model.go         # Структуры данных
├── middleware.go    # HTTP middleware
└── errors.go        # Кастомные ошибки
```

### Преимущества

- **Простота** — нет вложенности, всё на виду
- **Быстрый старт** — минимум boilerplate
- **Легко навигировать** — мало файлов
- **Нет циклических зависимостей** — всё в одном пакете

### Недостатки

- **Не масштабируется** — при росте становится messy
- **Всё public** — нет инкапсуляции между слоями
- **Сложно тестировать** — нет изоляции

### Пример кода (flat structure)

```go
// main.go
package main

import (
    "log"
    "net/http"
)

func main() {
    cfg := LoadConfig()

    repo := NewUserRepository(cfg.DatabaseURL)
    svc := NewUserService(repo)
    handler := NewUserHandler(svc)

    router := SetupRouter(handler)

    log.Printf("Starting server on %s", cfg.ServerAddr)
    log.Fatal(http.ListenAndServe(cfg.ServerAddr, router))
}
```

```go
// config.go
package main

import "os"

type Config struct {
    ServerAddr  string
    DatabaseURL string
}

func LoadConfig() Config {
    return Config{
        ServerAddr:  getEnv("SERVER_ADDR", ":8080"),
        DatabaseURL: getEnv("DATABASE_URL", "postgres://localhost/mydb"),
    }
}

func getEnv(key, defaultValue string) string {
    if value := os.Getenv(key); value != "" {
        return value
    }
    return defaultValue
}
```

```go
// model.go
package main

import "time"

type User struct {
    ID        int       `json:"id"`
    Email     string    `json:"email"`
    Name      string    `json:"name"`
    CreatedAt time.Time `json:"created_at"`
}

type CreateUserRequest struct {
    Email string `json:"email"`
    Name  string `json:"name"`
}
```

```go
// repository.go
package main

import (
    "context"
    "database/sql"
)

type UserRepository struct {
    db *sql.DB
}

func NewUserRepository(databaseURL string) *UserRepository {
    db, err := sql.Open("postgres", databaseURL)
    if err != nil {
        panic(err)
    }
    return &UserRepository{db: db}
}

func (r *UserRepository) Create(ctx context.Context, user *User) error {
    query := `INSERT INTO users (email, name) VALUES ($1, $2) RETURNING id, created_at`
    return r.db.QueryRowContext(ctx, query, user.Email, user.Name).
        Scan(&user.ID, &user.CreatedAt)
}

func (r *UserRepository) GetByID(ctx context.Context, id int) (*User, error) {
    user := &User{}
    query := `SELECT id, email, name, created_at FROM users WHERE id = $1`
    err := r.db.QueryRowContext(ctx, query, id).
        Scan(&user.ID, &user.Email, &user.Name, &user.CreatedAt)
    if err == sql.ErrNoRows {
        return nil, nil
    }
    return user, err
}
```

```go
// service.go
package main

import (
    "context"
    "errors"
)

var ErrUserNotFound = errors.New("user not found")

type UserService struct {
    repo *UserRepository
}

func NewUserService(repo *UserRepository) *UserService {
    return &UserService{repo: repo}
}

func (s *UserService) CreateUser(ctx context.Context, req CreateUserRequest) (*User, error) {
    user := &User{
        Email: req.Email,
        Name:  req.Name,
    }

    if err := s.repo.Create(ctx, user); err != nil {
        return nil, err
    }

    return user, nil
}

func (s *UserService) GetUser(ctx context.Context, id int) (*User, error) {
    user, err := s.repo.GetByID(ctx, id)
    if err != nil {
        return nil, err
    }
    if user == nil {
        return nil, ErrUserNotFound
    }
    return user, nil
}
```

---

## Standard Go Project Layout

[Standard Go Project Layout](https://github.com/golang-standards/project-layout) — популярный (но не официальный) шаблон структуры.

> ⚠️ **Важно**: Это НЕ официальный стандарт Go. Это набор общепринятых практик. Не копируйте все директории — используйте только нужные.

### Основные директории

```
myproject/
├── cmd/                    # Entry points (main packages)
│   ├── api/
│   │   └── main.go         # API сервер
│   ├── worker/
│   │   └── main.go         # Background worker
│   └── migrate/
│       └── main.go         # CLI для миграций
│
├── internal/               # Приватный код (не импортируется извне)
│   ├── config/             # Конфигурация
│   ├── handler/            # HTTP handlers
│   ├── service/            # Бизнес-логика
│   ├── repository/         # Работа с БД
│   ├── model/              # Domain models
│   └── pkg/                # Внутренние shared пакеты
│
├── pkg/                    # Публичные библиотеки (можно импортировать)
│   ├── logger/
│   └── validator/
│
├── api/                    # API спецификации
│   ├── openapi.yaml
│   └── proto/
│       └── user.proto
│
├── configs/                # Конфигурационные файлы
│   ├── config.yaml
│   └── config.example.yaml
│
├── deployments/            # Docker, k8s, etc.
│   ├── Dockerfile
│   └── docker-compose.yaml
│
├── scripts/                # Скрипты для разработки
│   ├── setup.sh
│   └── migrate.sh
│
├── migrations/             # SQL миграции
│   ├── 001_init.up.sql
│   └── 001_init.down.sql
│
├── go.mod
├── go.sum
├── Makefile
└── README.md
```

### Описание директорий

| Директория | Назначение |
|------------|------------|
| `cmd/` | Entry points. Каждая поддиректория — отдельный binary |
| `internal/` | **Приватный код**. Go compiler запрещает импорт извне модуля |
| `pkg/` | Публичные библиотеки. Можно импортировать из других проектов |
| `api/` | OpenAPI, gRPC proto, JSON schemas |
| `configs/` | Примеры конфигов, templates |
| `deployments/` | Docker, Kubernetes, CI/CD |
| `scripts/` | Build, install, analysis скрипты |
| `migrations/` | Database migrations |

### internal/ — ваш лучший друг

Директория `internal/` имеет особое значение в Go:

```go
// ✅ Можно импортировать из того же модуля
// myproject/cmd/api/main.go
import "myproject/internal/service"

// ❌ НЕЛЬЗЯ импортировать из другого модуля
// other-project/main.go
import "myproject/internal/service" // Ошибка компиляции!
```

Это даёт **гарантию инкапсуляции** на уровне компилятора.

### Когда НЕ нужен этот layout

```
❌ Не используйте для:
- Маленьких проектов (< 1000 строк)
- Библиотек (только pkg/ структура)
- Учебных проектов

✅ Используйте для:
- Больших приложений
- Командных проектов
- Микросервисов в монорепо
```

---

## Clean Architecture в Go

Clean Architecture помогает разделить concerns и сделать код тестируемым.

### Слои и зависимости

```
┌─────────────────────────────────────────────┐
│              Frameworks & Drivers           │  ← HTTP, DB, External APIs
│  (handlers, repositories, external clients) │
├─────────────────────────────────────────────┤
│              Interface Adapters             │  ← Controllers, Presenters
│         (DTOs, mappers, validators)         │
├─────────────────────────────────────────────┤
│              Application Layer              │  ← Use Cases
│         (services, business logic)          │
├─────────────────────────────────────────────┤
│                 Domain Layer                │  ← Entities, Value Objects
│            (models, interfaces)             │
└─────────────────────────────────────────────┘

Зависимости направлены ВНУТРЬ (от внешнего к внутреннему)
```

### Реализация в Go

```
myproject/
├── cmd/
│   └── api/
│       └── main.go
├── internal/
│   ├── domain/           # Domain Layer
│   │   ├── user.go       # Entities
│   │   └── repository.go # Interfaces
│   │
│   ├── usecase/          # Application Layer (Use Cases)
│   │   ├── user_service.go
│   │   └── user_service_test.go
│   │
│   ├── adapter/          # Interface Adapters
│   │   ├── http/         # HTTP handlers
│   │   │   ├── user_handler.go
│   │   │   └── dto.go    # Request/Response DTOs
│   │   └── postgres/     # PostgreSQL repositories
│   │       └── user_repository.go
│   │
│   └── infrastructure/   # Frameworks & Drivers
│       ├── config/
│       └── database/
└── go.mod
```

### Пример кода (Clean Architecture)

#### Domain Layer

```go
// internal/domain/user.go
package domain

import "time"

// Entity — чистая бизнес-модель
type User struct {
    ID        int
    Email     string
    Name      string
    CreatedAt time.Time
}

// Value Object
type Email string

func NewEmail(email string) (Email, error) {
    // Валидация
    if email == "" {
        return "", ErrInvalidEmail
    }
    return Email(email), nil
}
```

```go
// internal/domain/repository.go
package domain

import "context"

// Repository interface — определяется в domain, реализуется в adapter
type UserRepository interface {
    Create(ctx context.Context, user *User) error
    GetByID(ctx context.Context, id int) (*User, error)
    GetByEmail(ctx context.Context, email string) (*User, error)
    Update(ctx context.Context, user *User) error
    Delete(ctx context.Context, id int) error
}
```

```go
// internal/domain/errors.go
package domain

import "errors"

var (
    ErrUserNotFound  = errors.New("user not found")
    ErrUserExists    = errors.New("user already exists")
    ErrInvalidEmail  = errors.New("invalid email")
)
```

#### Application Layer (Use Cases)

```go
// internal/usecase/user_service.go
package usecase

import (
    "context"
    "myproject/internal/domain"
)

type UserService struct {
    repo domain.UserRepository
}

func NewUserService(repo domain.UserRepository) *UserService {
    return &UserService{repo: repo}
}

type CreateUserInput struct {
    Email string
    Name  string
}

type CreateUserOutput struct {
    ID int
}

func (s *UserService) CreateUser(ctx context.Context, input CreateUserInput) (*CreateUserOutput, error) {
    // Проверяем, не существует ли пользователь
    existing, err := s.repo.GetByEmail(ctx, input.Email)
    if err != nil {
        return nil, err
    }
    if existing != nil {
        return nil, domain.ErrUserExists
    }

    // Создаём пользователя
    user := &domain.User{
        Email: input.Email,
        Name:  input.Name,
    }

    if err := s.repo.Create(ctx, user); err != nil {
        return nil, err
    }

    return &CreateUserOutput{ID: user.ID}, nil
}

func (s *UserService) GetUser(ctx context.Context, id int) (*domain.User, error) {
    user, err := s.repo.GetByID(ctx, id)
    if err != nil {
        return nil, err
    }
    if user == nil {
        return nil, domain.ErrUserNotFound
    }
    return user, nil
}
```

#### Adapter Layer (HTTP Handler)

```go
// internal/adapter/http/dto.go
package http

// Request DTOs
type CreateUserRequest struct {
    Email string `json:"email"`
    Name  string `json:"name"`
}

// Response DTOs
type UserResponse struct {
    ID        int    `json:"id"`
    Email     string `json:"email"`
    Name      string `json:"name"`
    CreatedAt string `json:"created_at"`
}

type ErrorResponse struct {
    Error string `json:"error"`
}
```

```go
// internal/adapter/http/user_handler.go
package http

import (
    "encoding/json"
    "errors"
    "net/http"
    "strconv"

    "github.com/go-chi/chi/v5"
    "myproject/internal/domain"
    "myproject/internal/usecase"
)

type UserHandler struct {
    service *usecase.UserService
}

func NewUserHandler(service *usecase.UserService) *UserHandler {
    return &UserHandler{service: service}
}

func (h *UserHandler) Routes() chi.Router {
    r := chi.NewRouter()
    r.Post("/", h.Create)
    r.Get("/{id}", h.Get)
    return r
}

func (h *UserHandler) Create(w http.ResponseWriter, r *http.Request) {
    var req CreateUserRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        respondError(w, http.StatusBadRequest, "Invalid JSON")
        return
    }

    output, err := h.service.CreateUser(r.Context(), usecase.CreateUserInput{
        Email: req.Email,
        Name:  req.Name,
    })
    if err != nil {
        handleServiceError(w, err)
        return
    }

    respondJSON(w, http.StatusCreated, map[string]int{"id": output.ID})
}

func (h *UserHandler) Get(w http.ResponseWriter, r *http.Request) {
    idStr := chi.URLParam(r, "id")
    id, err := strconv.Atoi(idStr)
    if err != nil {
        respondError(w, http.StatusBadRequest, "Invalid user ID")
        return
    }

    user, err := h.service.GetUser(r.Context(), id)
    if err != nil {
        handleServiceError(w, err)
        return
    }

    respondJSON(w, http.StatusOK, UserResponse{
        ID:        user.ID,
        Email:     user.Email,
        Name:      user.Name,
        CreatedAt: user.CreatedAt.Format("2006-01-02T15:04:05Z"),
    })
}

func handleServiceError(w http.ResponseWriter, err error) {
    switch {
    case errors.Is(err, domain.ErrUserNotFound):
        respondError(w, http.StatusNotFound, "User not found")
    case errors.Is(err, domain.ErrUserExists):
        respondError(w, http.StatusConflict, "User already exists")
    default:
        respondError(w, http.StatusInternalServerError, "Internal server error")
    }
}

func respondJSON(w http.ResponseWriter, status int, data any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(data)
}

func respondError(w http.ResponseWriter, status int, message string) {
    respondJSON(w, status, ErrorResponse{Error: message})
}
```

#### Adapter Layer (Repository)

```go
// internal/adapter/postgres/user_repository.go
package postgres

import (
    "context"
    "database/sql"

    "myproject/internal/domain"
)

type UserRepository struct {
    db *sql.DB
}

func NewUserRepository(db *sql.DB) *UserRepository {
    return &UserRepository{db: db}
}

// Проверяем, что реализуем интерфейс
var _ domain.UserRepository = (*UserRepository)(nil)

func (r *UserRepository) Create(ctx context.Context, user *domain.User) error {
    query := `
        INSERT INTO users (email, name, created_at)
        VALUES ($1, $2, NOW())
        RETURNING id, created_at
    `
    return r.db.QueryRowContext(ctx, query, user.Email, user.Name).
        Scan(&user.ID, &user.CreatedAt)
}

func (r *UserRepository) GetByID(ctx context.Context, id int) (*domain.User, error) {
    query := `SELECT id, email, name, created_at FROM users WHERE id = $1`

    user := &domain.User{}
    err := r.db.QueryRowContext(ctx, query, id).
        Scan(&user.ID, &user.Email, &user.Name, &user.CreatedAt)

    if err == sql.ErrNoRows {
        return nil, nil
    }
    if err != nil {
        return nil, err
    }
    return user, nil
}

func (r *UserRepository) GetByEmail(ctx context.Context, email string) (*domain.User, error) {
    query := `SELECT id, email, name, created_at FROM users WHERE email = $1`

    user := &domain.User{}
    err := r.db.QueryRowContext(ctx, query, email).
        Scan(&user.ID, &user.Email, &user.Name, &user.CreatedAt)

    if err == sql.ErrNoRows {
        return nil, nil
    }
    if err != nil {
        return nil, err
    }
    return user, nil
}

func (r *UserRepository) Update(ctx context.Context, user *domain.User) error {
    query := `UPDATE users SET email = $1, name = $2 WHERE id = $3`
    _, err := r.db.ExecContext(ctx, query, user.Email, user.Name, user.ID)
    return err
}

func (r *UserRepository) Delete(ctx context.Context, id int) error {
    query := `DELETE FROM users WHERE id = $1`
    _, err := r.db.ExecContext(ctx, query, id)
    return err
}
```

### Сравнение с C#

| Аспект | C# Clean Architecture | Go Clean Architecture |
|--------|----------------------|----------------------|
| **Entities** | Отдельные .cs файлы в Domain проекте | Структуры в `internal/domain/` |
| **Use Cases** | Классы в Application проекте | Функции/методы в `internal/usecase/` |
| **Controllers** | Отдельные Controller классы | Handler структуры в `internal/adapter/http/` |
| **Repositories** | Interface + Implementation | Interface в domain, реализация в adapter |
| **DI** | `IServiceCollection` | Manual или Wire/Fx |
| **Проекты** | Отдельные .csproj | Пакеты (директории) |

---

## Dependency Injection

### Manual DI (идиоматичный Go)

В Go предпочтительный подход — ручная инъекция зависимостей через конструкторы.

```go
// cmd/api/main.go
package main

import (
    "database/sql"
    "log"
    "net/http"

    "github.com/go-chi/chi/v5"
    _ "github.com/lib/pq"

    "myproject/internal/adapter/postgres"
    httpAdapter "myproject/internal/adapter/http"
    "myproject/internal/usecase"
)

func main() {
    // 1. Загружаем конфигурацию
    cfg := LoadConfig()

    // 2. Создаём подключение к БД
    db, err := sql.Open("postgres", cfg.DatabaseURL)
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    // 3. Создаём зависимости (снизу вверх)
    userRepo := postgres.NewUserRepository(db)
    userService := usecase.NewUserService(userRepo)
    userHandler := httpAdapter.NewUserHandler(userService)

    // 4. Настраиваем роутер
    r := chi.NewRouter()
    r.Mount("/users", userHandler.Routes())

    // 5. Запускаем сервер
    log.Printf("Starting server on %s", cfg.ServerAddr)
    log.Fatal(http.ListenAndServe(cfg.ServerAddr, r))
}
```

**Преимущества:**
- Простота и понятность
- Нет магии
- Легко отследить зависимости
- Отличная поддержка IDE

**Недостатки:**
- Много boilerplate при большом количестве зависимостей
- Нужно следить за порядком инициализации

### Wire (Google)

[Wire](https://github.com/google/wire) — compile-time dependency injection.

```bash
go install github.com/google/wire/cmd/wire@latest
```

```go
// cmd/api/wire.go
//go:build wireinject
// +build wireinject

package main

import (
    "database/sql"

    "github.com/google/wire"

    "myproject/internal/adapter/postgres"
    httpAdapter "myproject/internal/adapter/http"
    "myproject/internal/usecase"
)

func InitializeApp(db *sql.DB) (*httpAdapter.UserHandler, error) {
    wire.Build(
        postgres.NewUserRepository,
        usecase.NewUserService,
        httpAdapter.NewUserHandler,
    )
    return nil, nil // Wire заполнит это
}
```

```go
// cmd/api/main.go
package main

import (
    "database/sql"
    "log"
    "net/http"

    "github.com/go-chi/chi/v5"
)

func main() {
    cfg := LoadConfig()

    db, err := sql.Open("postgres", cfg.DatabaseURL)
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    // Wire сгенерирует wire_gen.go с реализацией
    handler, err := InitializeApp(db)
    if err != nil {
        log.Fatal(err)
    }

    r := chi.NewRouter()
    r.Mount("/users", handler.Routes())

    log.Fatal(http.ListenAndServe(cfg.ServerAddr, r))
}
```

```bash
# Генерация кода
wire ./cmd/api/...
```

Wire сгенерирует `wire_gen.go`:

```go
// Code generated by Wire. DO NOT EDIT.
//go:generate go run github.com/google/wire/cmd/wire
//go:build !wireinject
// +build !wireinject

package main

import (
    "database/sql"

    "myproject/internal/adapter/postgres"
    httpAdapter "myproject/internal/adapter/http"
    "myproject/internal/usecase"
)

func InitializeApp(db *sql.DB) (*httpAdapter.UserHandler, error) {
    userRepository := postgres.NewUserRepository(db)
    userService := usecase.NewUserService(userRepository)
    userHandler := httpAdapter.NewUserHandler(userService)
    return userHandler, nil
}
```

**Преимущества Wire:**
- Compile-time проверка зависимостей
- Автоматическое разрешение графа зависимостей
- Нет runtime overhead

**Недостатки:**
- Нужен отдельный шаг генерации
- Сложнее для понимания новичкам

### Fx (Uber)

[Fx](https://github.com/uber-go/fx) — runtime dependency injection framework.

```go
// cmd/api/main.go
package main

import (
    "context"
    "database/sql"
    "net/http"

    "github.com/go-chi/chi/v5"
    "go.uber.org/fx"

    "myproject/internal/adapter/postgres"
    httpAdapter "myproject/internal/adapter/http"
    "myproject/internal/usecase"
)

func main() {
    fx.New(
        fx.Provide(
            LoadConfig,
            NewDatabase,
            postgres.NewUserRepository,
            usecase.NewUserService,
            httpAdapter.NewUserHandler,
            NewRouter,
        ),
        fx.Invoke(StartServer),
    ).Run()
}

func NewDatabase(cfg Config) (*sql.DB, error) {
    return sql.Open("postgres", cfg.DatabaseURL)
}

func NewRouter(handler *httpAdapter.UserHandler) *chi.Mux {
    r := chi.NewRouter()
    r.Mount("/users", handler.Routes())
    return r
}

func StartServer(lc fx.Lifecycle, cfg Config, router *chi.Mux) {
    server := &http.Server{
        Addr:    cfg.ServerAddr,
        Handler: router,
    }

    lc.Append(fx.Hook{
        OnStart: func(ctx context.Context) error {
            go server.ListenAndServe()
            return nil
        },
        OnStop: func(ctx context.Context) error {
            return server.Shutdown(ctx)
        },
    })
}
```

**Преимущества Fx:**
- Автоматическое управление lifecycle
- Graceful shutdown из коробки
- Гибкая конфигурация

**Недостатки:**
- Runtime overhead
- Сложнее дебажить
- "Магия" в разрешении зависимостей

### Сравнение подходов

| Аспект | Manual DI | Wire | Fx |
|--------|-----------|------|----|
| **Тип** | Ручной | Compile-time | Runtime |
| **Сложность** | Низкая | Средняя | Высокая |
| **Производительность** | Лучшая | Лучшая | Хорошая |
| **Boilerplate** | Много | Мало | Мало |
| **Lifecycle** | Ручной | Ручной | Автоматический |
| **Отладка** | Простая | Средняя | Сложная |
| **Идиоматичность** | ✅ Go-way | ⚠️ Приемлемо | ⚠️ Java-like |

### Рекомендации

```
Маленький проект (< 10 зависимостей)  → Manual DI
Средний проект (10-50 зависимостей)   → Wire
Большой проект с lifecycle            → Fx
```

---

## Configuration

### Environment variables

12-factor app рекомендует использовать переменные окружения:

```go
// internal/config/config.go
package config

import (
    "os"
    "strconv"
    "time"
)

type Config struct {
    Server   ServerConfig
    Database DatabaseConfig
    Redis    RedisConfig
}

type ServerConfig struct {
    Addr         string
    ReadTimeout  time.Duration
    WriteTimeout time.Duration
}

type DatabaseConfig struct {
    URL             string
    MaxOpenConns    int
    MaxIdleConns    int
    ConnMaxLifetime time.Duration
}

type RedisConfig struct {
    Addr     string
    Password string
    DB       int
}

func Load() Config {
    return Config{
        Server: ServerConfig{
            Addr:         getEnv("SERVER_ADDR", ":8080"),
            ReadTimeout:  getDuration("SERVER_READ_TIMEOUT", 15*time.Second),
            WriteTimeout: getDuration("SERVER_WRITE_TIMEOUT", 15*time.Second),
        },
        Database: DatabaseConfig{
            URL:             mustGetEnv("DATABASE_URL"),
            MaxOpenConns:    getInt("DATABASE_MAX_OPEN_CONNS", 25),
            MaxIdleConns:    getInt("DATABASE_MAX_IDLE_CONNS", 5),
            ConnMaxLifetime: getDuration("DATABASE_CONN_MAX_LIFETIME", 5*time.Minute),
        },
        Redis: RedisConfig{
            Addr:     getEnv("REDIS_ADDR", "localhost:6379"),
            Password: getEnv("REDIS_PASSWORD", ""),
            DB:       getInt("REDIS_DB", 0),
        },
    }
}

func getEnv(key, defaultValue string) string {
    if value := os.Getenv(key); value != "" {
        return value
    }
    return defaultValue
}

func mustGetEnv(key string) string {
    value := os.Getenv(key)
    if value == "" {
        panic("required environment variable not set: " + key)
    }
    return value
}

func getInt(key string, defaultValue int) int {
    if value := os.Getenv(key); value != "" {
        if i, err := strconv.Atoi(value); err == nil {
            return i
        }
    }
    return defaultValue
}

func getDuration(key string, defaultValue time.Duration) time.Duration {
    if value := os.Getenv(key); value != "" {
        if d, err := time.ParseDuration(value); err == nil {
            return d
        }
    }
    return defaultValue
}
```

### Viper для сложных конфигов

[Viper](https://github.com/spf13/viper) — популярная библиотека для конфигурации.

```go
// internal/config/config.go
package config

import (
    "github.com/spf13/viper"
)

type Config struct {
    Server   ServerConfig   `mapstructure:"server"`
    Database DatabaseConfig `mapstructure:"database"`
    Redis    RedisConfig    `mapstructure:"redis"`
}

type ServerConfig struct {
    Addr         string `mapstructure:"addr"`
    ReadTimeout  string `mapstructure:"read_timeout"`
    WriteTimeout string `mapstructure:"write_timeout"`
}

type DatabaseConfig struct {
    URL             string `mapstructure:"url"`
    MaxOpenConns    int    `mapstructure:"max_open_conns"`
    MaxIdleConns    int    `mapstructure:"max_idle_conns"`
    ConnMaxLifetime string `mapstructure:"conn_max_lifetime"`
}

type RedisConfig struct {
    Addr     string `mapstructure:"addr"`
    Password string `mapstructure:"password"`
    DB       int    `mapstructure:"db"`
}

func Load(configPath string) (*Config, error) {
    viper.SetConfigFile(configPath)

    // Переменные окружения переопределяют файл
    viper.AutomaticEnv()
    viper.SetEnvPrefix("APP")

    if err := viper.ReadInConfig(); err != nil {
        return nil, err
    }

    var cfg Config
    if err := viper.Unmarshal(&cfg); err != nil {
        return nil, err
    }

    return &cfg, nil
}
```

```yaml
# configs/config.yaml
server:
  addr: ":8080"
  read_timeout: "15s"
  write_timeout: "15s"

database:
  url: "postgres://localhost/mydb"
  max_open_conns: 25
  max_idle_conns: 5
  conn_max_lifetime: "5m"

redis:
  addr: "localhost:6379"
  password: ""
  db: 0
```

### Сравнение с C#

| C# | Go |
|----|----|
| `appsettings.json` | `config.yaml` + viper |
| `IConfiguration` | Struct + viper |
| `IOptions<T>` | Struct fields |
| `User secrets` | `.env` файлы |
| `Azure Key Vault` | Vault, AWS Secrets Manager |

---

## Практические примеры

### Пример 1: Flat structure для микросервиса

Простой сервис аутентификации:

```
auth-service/
├── go.mod
├── go.sum
├── main.go
├── config.go
├── handler.go
├── service.go
├── repository.go
├── model.go
├── token.go
├── middleware.go
└── Dockerfile
```

```go
// main.go
package main

import (
    "log"
    "net/http"

    "github.com/go-chi/chi/v5"
    "github.com/go-chi/chi/v5/middleware"
)

func main() {
    cfg := LoadConfig()

    db := NewDB(cfg.DatabaseURL)
    defer db.Close()

    repo := NewUserRepository(db)
    tokenSvc := NewTokenService(cfg.JWTSecret)
    authSvc := NewAuthService(repo, tokenSvc)
    handler := NewAuthHandler(authSvc)

    r := chi.NewRouter()
    r.Use(middleware.Logger)
    r.Use(middleware.Recoverer)

    r.Post("/register", handler.Register)
    r.Post("/login", handler.Login)
    r.Post("/refresh", handler.Refresh)

    // Protected routes
    r.Group(func(r chi.Router) {
        r.Use(AuthMiddleware(tokenSvc))
        r.Get("/me", handler.Me)
        r.Post("/logout", handler.Logout)
    })

    log.Printf("Auth service starting on %s", cfg.Addr)
    log.Fatal(http.ListenAndServe(cfg.Addr, r))
}
```

### Пример 2: Clean Architecture

Полная структура для среднего проекта:

```
user-api/
├── cmd/
│   └── api/
│       ├── main.go
│       └── wire.go
├── internal/
│   ├── domain/
│   │   ├── user.go
│   │   ├── repository.go
│   │   └── errors.go
│   ├── usecase/
│   │   ├── user_service.go
│   │   └── user_service_test.go
│   ├── adapter/
│   │   ├── http/
│   │   │   ├── handler.go
│   │   │   ├── dto.go
│   │   │   ├── router.go
│   │   │   └── middleware.go
│   │   └── postgres/
│   │       ├── user_repository.go
│   │       └── user_repository_test.go
│   └── infrastructure/
│       ├── config/
│       │   └── config.go
│       └── database/
│           └── postgres.go
├── migrations/
│   ├── 001_create_users.up.sql
│   └── 001_create_users.down.sql
├── api/
│   └── openapi.yaml
├── deployments/
│   ├── Dockerfile
│   └── docker-compose.yaml
├── go.mod
├── go.sum
├── Makefile
└── README.md
```

### Пример 3: DI с Wire

```go
// cmd/api/wire.go
//go:build wireinject

package main

import (
    "github.com/google/wire"

    "user-api/internal/adapter/http"
    "user-api/internal/adapter/postgres"
    "user-api/internal/infrastructure/config"
    "user-api/internal/infrastructure/database"
    "user-api/internal/usecase"
)

func InitializeApp() (*App, func(), error) {
    wire.Build(
        config.Load,
        database.NewPostgres,

        // Repository
        postgres.NewUserRepository,

        // Use Cases
        usecase.NewUserService,

        // HTTP
        http.NewUserHandler,
        http.NewRouter,

        // App
        NewApp,
    )
    return nil, nil, nil
}
```

```go
// cmd/api/app.go
package main

import (
    "context"
    "log"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "github.com/go-chi/chi/v5"

    "user-api/internal/infrastructure/config"
)

type App struct {
    config *config.Config
    router *chi.Mux
}

func NewApp(cfg *config.Config, router *chi.Mux) *App {
    return &App{
        config: cfg,
        router: router,
    }
}

func (a *App) Run() error {
    server := &http.Server{
        Addr:         a.config.Server.Addr,
        Handler:      a.router,
        ReadTimeout:  a.config.Server.ReadTimeout,
        WriteTimeout: a.config.Server.WriteTimeout,
    }

    // Graceful shutdown
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

    go func() {
        log.Printf("Server starting on %s", a.config.Server.Addr)
        if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatalf("Server error: %v", err)
        }
    }()

    <-quit
    log.Println("Shutting down server...")

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    return server.Shutdown(ctx)
}
```

```go
// cmd/api/main.go
package main

import "log"

func main() {
    app, cleanup, err := InitializeApp()
    if err != nil {
        log.Fatal(err)
    }
    defer cleanup()

    if err := app.Run(); err != nil {
        log.Fatal(err)
    }
}
```

---

<!-- AUTO: NAV -->
**Вопросы?** Открой issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Назад: HTTP в Go: Создание веб-серверов](./01_http_server.md) | [Вперёд: Работа с данными (PostgreSQL) →](./03_database.md)
<!-- /AUTO: NAV -->
