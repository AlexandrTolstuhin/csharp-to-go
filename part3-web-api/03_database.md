# 3.3 Работа с данными (PostgreSQL)

## Содержание

- [Введение](#введение)
- [Подходы к работе с БД в Go](#подходы-к-работе-с-бд-в-go)
- [database/sql: стандартная библиотека](#databasesql-стандартная-библиотека)
  - [Подключение и Connection Pool](#подключение-и-connection-pool)
  - [Выполнение запросов](#выполнение-запросов)
  - [Prepared Statements](#prepared-statements)
  - [Транзакции](#транзакции)
  - [Null значения](#null-значения)
- [pgx: Production PostgreSQL Driver](#pgx-production-postgresql-driver)
  - [Преимущества над database/sql](#преимущества-над-databasesql)
  - [Batch запросы](#batch-запросы)
  - [COPY Protocol](#copy-protocol)
  - [Listen/Notify](#listennotify)
- [sqlc: Type-Safe SQL](#sqlc-type-safe-sql)
  - [Установка и настройка](#установка-и-настройка)
  - [Написание запросов](#написание-запросов)
  - [Генерация кода](#генерация-кода)
- [GORM: когда нужен ORM](#gorm-когда-нужен-orm)
  - [Базовые операции](#базовые-операции)
  - [Миграции](#миграции-gorm)
  - [Associations](#associations)
- [Миграции базы данных](#миграции-базы-данных)
  - [golang-migrate](#golang-migrate)
  - [goose](#goose)
- [Repository Pattern](#repository-pattern)
- [Практические примеры](#практические-примеры)
  - [Пример 1: CRUD с pgx](#пример-1-crud-с-pgx)
  - [Пример 2: Type-safe queries с sqlc](#пример-2-type-safe-queries-с-sqlc)
  - [Пример 3: Repository с транзакциями](#пример-3-repository-с-транзакциями)
- [Чек-лист](#чек-лист)

---

## Введение

Работа с базами данных в Go существенно отличается от C#. Вместо мощного ORM (Entity Framework) Go-сообщество предпочитает более простые инструменты: чистый SQL или кодогенерацию.

> 💡 **Для C# разработчиков**: В Go нет LINQ, нет Change Tracker, нет Lazy Loading. Но есть простота, предсказуемость и полный контроль над SQL.

### Что вы узнаете

- Стандартную библиотеку `database/sql` и её ограничения
- pgx — production-ready PostgreSQL драйвер
- sqlc — генерация type-safe Go кода из SQL
- Когда использовать GORM
- Миграции и управление схемой БД
- Repository pattern в Go

---

## Подходы к работе с БД в Go

| Подход | Инструменты | Плюсы | Минусы |
|--------|-------------|-------|--------|
| **Raw SQL** | database/sql, pgx | Полный контроль, производительность | Нет type safety, много boilerplate |
| **Query Builder** | squirrel, goqu | Программное построение запросов | Сложнее читать, нет type safety |
| **Code Generation** | sqlc | Type safety, нет runtime overhead | Нужен шаг генерации |
| **ORM** | GORM, ent | Привычно для C# разработчиков | Magic, производительность, N+1 |

### Философия Go: SQL First

```
C# подход (EF Core):
1. Пишем C# классы (модели)
2. EF генерирует SQL
3. Change Tracker отслеживает изменения
4. LINQ транслируется в SQL

Go подход (sqlc):
1. Пишем SQL запросы
2. sqlc генерирует Go код
3. Работаем с type-safe функциями
4. Полный контроль над SQL
```

### Сравнение с C#

| EF Core | Go |
|---------|-----|
| `DbContext` | `*sql.DB` или `*pgxpool.Pool` |
| LINQ `Where(x => ...)` | Чистый SQL |
| `context.SaveChanges()` | Явные INSERT/UPDATE |
| `Include()` | JOIN в SQL |
| Migrations CLI | golang-migrate, goose |
| Code First | SQL First (sqlc) |

---

## database/sql: стандартная библиотека

`database/sql` — абстракция над SQL базами данных. Работает с любой БД через драйверы.

### Подключение и Connection Pool

```go
import (
    "database/sql"
    "log"
    "time"

    _ "github.com/lib/pq" // PostgreSQL драйвер
)

func NewDB(databaseURL string) (*sql.DB, error) {
    db, err := sql.Open("postgres", databaseURL)
    if err != nil {
        return nil, err
    }

    // Настройка connection pool
    db.SetMaxOpenConns(25)                 // Максимум открытых соединений
    db.SetMaxIdleConns(5)                  // Максимум idle соединений
    db.SetConnMaxLifetime(5 * time.Minute) // Время жизни соединения
    db.SetConnMaxIdleTime(1 * time.Minute) // Время простоя

    // Проверка подключения
    if err := db.Ping(); err != nil {
        return nil, err
    }

    return db, nil
}

func main() {
    db, err := NewDB("postgres://user:pass@localhost/mydb?sslmode=disable")
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    // Используем db...
}
```

> 💡 **Connection Pool**: `sql.DB` — это не одно соединение, а пул! Безопасен для concurrent использования.

### Выполнение запросов

```go
// SELECT один ряд
func GetUserByID(db *sql.DB, id int) (*User, error) {
    user := &User{}
    query := `SELECT id, email, name, created_at FROM users WHERE id = $1`

    err := db.QueryRow(query, id).Scan(
        &user.ID,
        &user.Email,
        &user.Name,
        &user.CreatedAt,
    )
    if err == sql.ErrNoRows {
        return nil, nil // Не найден
    }
    if err != nil {
        return nil, err
    }
    return user, nil
}

// SELECT несколько рядов
func GetAllUsers(db *sql.DB) ([]User, error) {
    query := `SELECT id, email, name, created_at FROM users ORDER BY id`

    rows, err := db.Query(query)
    if err != nil {
        return nil, err
    }
    defer rows.Close() // ВАЖНО: всегда закрывать!

    var users []User
    for rows.Next() {
        var user User
        if err := rows.Scan(&user.ID, &user.Email, &user.Name, &user.CreatedAt); err != nil {
            return nil, err
        }
        users = append(users, user)
    }

    // Проверяем ошибки итерации
    if err := rows.Err(); err != nil {
        return nil, err
    }

    return users, nil
}

// INSERT
func CreateUser(db *sql.DB, email, name string) (int, error) {
    query := `INSERT INTO users (email, name) VALUES ($1, $2) RETURNING id`

    var id int
    err := db.QueryRow(query, email, name).Scan(&id)
    return id, err
}

// UPDATE
func UpdateUser(db *sql.DB, id int, name string) error {
    query := `UPDATE users SET name = $1 WHERE id = $2`
    result, err := db.Exec(query, name, id)
    if err != nil {
        return err
    }

    rowsAffected, _ := result.RowsAffected()
    if rowsAffected == 0 {
        return sql.ErrNoRows
    }
    return nil
}

// DELETE
func DeleteUser(db *sql.DB, id int) error {
    query := `DELETE FROM users WHERE id = $1`
    _, err := db.Exec(query, id)
    return err
}
```

### Context для timeout и cancellation

```go
func GetUserByIDWithContext(ctx context.Context, db *sql.DB, id int) (*User, error) {
    user := &User{}
    query := `SELECT id, email, name, created_at FROM users WHERE id = $1`

    // Используем QueryRowContext
    err := db.QueryRowContext(ctx, query, id).Scan(
        &user.ID,
        &user.Email,
        &user.Name,
        &user.CreatedAt,
    )
    if err == sql.ErrNoRows {
        return nil, nil
    }
    return user, err
}

// В handler
func (h *Handler) GetUser(w http.ResponseWriter, r *http.Request) {
    // Контекст с timeout
    ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
    defer cancel()

    user, err := GetUserByIDWithContext(ctx, h.db, id)
    if err != nil {
        if ctx.Err() == context.DeadlineExceeded {
            http.Error(w, "Database timeout", http.StatusGatewayTimeout)
            return
        }
        // Другая ошибка...
    }
}
```

### Prepared Statements

```go
// Подготовленные запросы — оптимизация для повторяющихся запросов
func NewUserRepository(db *sql.DB) (*UserRepository, error) {
    getByID, err := db.Prepare(`SELECT id, email, name FROM users WHERE id = $1`)
    if err != nil {
        return nil, err
    }

    create, err := db.Prepare(`INSERT INTO users (email, name) VALUES ($1, $2) RETURNING id`)
    if err != nil {
        return nil, err
    }

    return &UserRepository{
        db:          db,
        getByIDStmt: getByID,
        createStmt:  create,
    }, nil
}

type UserRepository struct {
    db          *sql.DB
    getByIDStmt *sql.Stmt
    createStmt  *sql.Stmt
}

func (r *UserRepository) GetByID(ctx context.Context, id int) (*User, error) {
    user := &User{}
    err := r.getByIDStmt.QueryRowContext(ctx, id).Scan(&user.ID, &user.Email, &user.Name)
    if err == sql.ErrNoRows {
        return nil, nil
    }
    return user, err
}

func (r *UserRepository) Close() error {
    r.getByIDStmt.Close()
    r.createStmt.Close()
    return nil
}
```

### Транзакции

```go
func TransferMoney(db *sql.DB, fromID, toID int, amount float64) error {
    // Начинаем транзакцию
    tx, err := db.Begin()
    if err != nil {
        return err
    }
    // Откат при ошибке
    defer tx.Rollback()

    // Снимаем деньги
    _, err = tx.Exec(`UPDATE accounts SET balance = balance - $1 WHERE id = $2`, amount, fromID)
    if err != nil {
        return err
    }

    // Добавляем деньги
    _, err = tx.Exec(`UPDATE accounts SET balance = balance + $1 WHERE id = $2`, amount, toID)
    if err != nil {
        return err
    }

    // Коммитим
    return tx.Commit()
}

// С контекстом
func TransferMoneyWithContext(ctx context.Context, db *sql.DB, fromID, toID int, amount float64) error {
    tx, err := db.BeginTx(ctx, &sql.TxOptions{
        Isolation: sql.LevelSerializable, // Уровень изоляции
        ReadOnly:  false,
    })
    if err != nil {
        return err
    }
    defer tx.Rollback()

    // ... операции ...

    return tx.Commit()
}
```

### Null значения

```go
import "database/sql"

// Способ 1: sql.NullString, sql.NullInt64, etc.
type User struct {
    ID        int
    Email     string
    Name      sql.NullString // Может быть NULL
    DeletedAt sql.NullTime
}

func (r *Repository) GetUser(ctx context.Context, id int) (*User, error) {
    user := &User{}
    err := r.db.QueryRowContext(ctx, query, id).Scan(
        &user.ID,
        &user.Email,
        &user.Name,     // sql.NullString
        &user.DeletedAt, // sql.NullTime
    )
    // ...
}

// Проверка
if user.Name.Valid {
    fmt.Println(user.Name.String)
}

// Способ 2: Указатели
type User struct {
    ID        int
    Email     string
    Name      *string    // nil если NULL
    DeletedAt *time.Time // nil если NULL
}

// Способ 3: Значения по умолчанию с COALESCE в SQL
query := `SELECT id, email, COALESCE(name, '') FROM users WHERE id = $1`
```

---

## pgx: Production PostgreSQL Driver

[pgx](https://github.com/jackc/pgx) — рекомендуемый драйвер для PostgreSQL в Go.

### Преимущества над database/sql

| Функция | database/sql + lib/pq | pgx |
|---------|----------------------|-----|
| Производительность | Базовая | Выше на 30-50% |
| Batch запросы | Нет | Есть |
| COPY Protocol | Нет | Есть |
| Listen/Notify | Ограниченно | Полная поддержка |
| Prepared statements cache | Нет | Автоматически |
| Native types | Ограниченно | UUID, JSON, arrays |
| Connection Pool | Внешний | Встроенный (pgxpool) |

### Базовое использование

```go
import (
    "context"
    "github.com/jackc/pgx/v5"
    "github.com/jackc/pgx/v5/pgxpool"
)

func NewPool(ctx context.Context, databaseURL string) (*pgxpool.Pool, error) {
    config, err := pgxpool.ParseConfig(databaseURL)
    if err != nil {
        return nil, err
    }

    // Настройка пула
    config.MaxConns = 25
    config.MinConns = 5
    config.MaxConnLifetime = 5 * time.Minute
    config.MaxConnIdleTime = 1 * time.Minute

    pool, err := pgxpool.NewWithConfig(ctx, config)
    if err != nil {
        return nil, err
    }

    // Проверка подключения
    if err := pool.Ping(ctx); err != nil {
        return nil, err
    }

    return pool, nil
}

func main() {
    ctx := context.Background()

    pool, err := NewPool(ctx, "postgres://user:pass@localhost/mydb")
    if err != nil {
        log.Fatal(err)
    }
    defer pool.Close()

    // CRUD операции
    var id int
    err = pool.QueryRow(ctx,
        `INSERT INTO users (email, name) VALUES ($1, $2) RETURNING id`,
        "user@example.com", "John",
    ).Scan(&id)

    // Выборка
    rows, _ := pool.Query(ctx, `SELECT id, email, name FROM users`)
    defer rows.Close()

    for rows.Next() {
        var user User
        rows.Scan(&user.ID, &user.Email, &user.Name)
    }
}
```

### Batch запросы

Batch позволяет отправить несколько запросов за один round-trip:

```go
func InsertUsers(ctx context.Context, pool *pgxpool.Pool, users []User) error {
    batch := &pgx.Batch{}

    for _, user := range users {
        batch.Queue(
            `INSERT INTO users (email, name) VALUES ($1, $2)`,
            user.Email, user.Name,
        )
    }

    // Отправляем все запросы разом
    results := pool.SendBatch(ctx, batch)
    defer results.Close()

    // Проверяем результаты
    for range users {
        _, err := results.Exec()
        if err != nil {
            return err
        }
    }

    return nil
}

// Batch с разными типами запросов
func BatchOperations(ctx context.Context, pool *pgxpool.Pool) error {
    batch := &pgx.Batch{}

    // INSERT
    batch.Queue(`INSERT INTO logs (message) VALUES ($1)`, "Operation started")

    // UPDATE
    batch.Queue(`UPDATE counters SET value = value + 1 WHERE name = $1`, "operations")

    // SELECT
    batch.Queue(`SELECT COUNT(*) FROM users`)

    results := pool.SendBatch(ctx, batch)
    defer results.Close()

    // Обрабатываем INSERT
    _, err := results.Exec()
    if err != nil {
        return err
    }

    // Обрабатываем UPDATE
    _, err = results.Exec()
    if err != nil {
        return err
    }

    // Обрабатываем SELECT
    var count int
    err = results.QueryRow().Scan(&count)
    if err != nil {
        return err
    }

    log.Printf("Total users: %d", count)
    return nil
}
```

### COPY Protocol

Массовая вставка данных (в 10-100 раз быстрее INSERT):

```go
func BulkInsertUsers(ctx context.Context, pool *pgxpool.Pool, users []User) error {
    // Временная таблица для COPY
    _, err := pool.Exec(ctx, `
        CREATE TEMP TABLE temp_users (
            email TEXT,
            name TEXT
        ) ON COMMIT DROP
    `)
    if err != nil {
        return err
    }

    // COPY данные
    _, err = pool.CopyFrom(
        ctx,
        pgx.Identifier{"temp_users"},
        []string{"email", "name"},
        pgx.CopyFromSlice(len(users), func(i int) ([]any, error) {
            return []any{users[i].Email, users[i].Name}, nil
        }),
    )
    if err != nil {
        return err
    }

    // INSERT из временной таблицы
    _, err = pool.Exec(ctx, `
        INSERT INTO users (email, name)
        SELECT email, name FROM temp_users
        ON CONFLICT (email) DO NOTHING
    `)
    return err
}

// CopyFromRows для готовых данных
func BulkInsertSimple(ctx context.Context, pool *pgxpool.Pool) error {
    rows := [][]any{
        {"user1@example.com", "User 1"},
        {"user2@example.com", "User 2"},
        {"user3@example.com", "User 3"},
    }

    _, err := pool.CopyFrom(
        ctx,
        pgx.Identifier{"users"},
        []string{"email", "name"},
        pgx.CopyFromRows(rows),
    )
    return err
}
```

### Listen/Notify

PostgreSQL LISTEN/NOTIFY для real-time событий:

```go
func ListenForChanges(ctx context.Context, pool *pgxpool.Pool) error {
    conn, err := pool.Acquire(ctx)
    if err != nil {
        return err
    }
    defer conn.Release()

    // Подписываемся на канал
    _, err = conn.Exec(ctx, "LISTEN user_changes")
    if err != nil {
        return err
    }

    log.Println("Listening for user changes...")

    for {
        // Ждём уведомление
        notification, err := conn.Conn().WaitForNotification(ctx)
        if err != nil {
            return err
        }

        log.Printf("Received: channel=%s, payload=%s",
            notification.Channel, notification.Payload)

        // Обработка события...
    }
}

// Отправка уведомления (из другого соединения или триггера)
func NotifyChange(ctx context.Context, pool *pgxpool.Pool, userID int) error {
    payload := fmt.Sprintf(`{"user_id": %d, "action": "updated"}`, userID)
    _, err := pool.Exec(ctx, "SELECT pg_notify('user_changes', $1)", payload)
    return err
}
```

---

## sqlc: Type-Safe SQL

[sqlc](https://sqlc.dev/) генерирует Go код из SQL запросов. Это идиоматичный Go-подход: SQL First.

### Установка и настройка

```bash
# Установка
go install github.com/sqlc-dev/sqlc/cmd/sqlc@latest

# Или через brew
brew install sqlc
```

```yaml
# sqlc.yaml
version: "2"
sql:
  - engine: "postgresql"
    queries: "queries/"
    schema: "schema/"
    gen:
      go:
        package: "db"
        out: "internal/db"
        sql_package: "pgx/v5"
        emit_json_tags: true
        emit_empty_slices: true
```

### Написание запросов

```sql
-- schema/001_users.sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role) WHERE deleted_at IS NULL;
```

```sql
-- queries/users.sql

-- name: GetUser :one
SELECT id, email, name, role, created_at
FROM users
WHERE id = $1 AND deleted_at IS NULL;

-- name: GetUserByEmail :one
SELECT id, email, name, role, created_at
FROM users
WHERE email = $1 AND deleted_at IS NULL;

-- name: ListUsers :many
SELECT id, email, name, role, created_at
FROM users
WHERE deleted_at IS NULL
ORDER BY created_at DESC
LIMIT $1 OFFSET $2;

-- name: ListUsersByRole :many
SELECT id, email, name, role, created_at
FROM users
WHERE role = $1 AND deleted_at IS NULL
ORDER BY name;

-- name: CreateUser :one
INSERT INTO users (email, name, role)
VALUES ($1, $2, $3)
RETURNING id, email, name, role, created_at;

-- name: UpdateUser :one
UPDATE users
SET name = $2, role = $3
WHERE id = $1 AND deleted_at IS NULL
RETURNING id, email, name, role, created_at;

-- name: SoftDeleteUser :exec
UPDATE users
SET deleted_at = NOW()
WHERE id = $1;

-- name: CountUsersByRole :one
SELECT COUNT(*) FROM users
WHERE role = $1 AND deleted_at IS NULL;
```

### Генерация кода

```bash
sqlc generate
```

sqlc сгенерирует:

```go
// internal/db/models.go
package db

import "time"

type User struct {
    ID        int32     `json:"id"`
    Email     string    `json:"email"`
    Name      string    `json:"name"`
    Role      string    `json:"role"`
    CreatedAt time.Time `json:"created_at"`
}
```

```go
// internal/db/users.sql.go
package db

import (
    "context"
)

type CreateUserParams struct {
    Email string `json:"email"`
    Name  string `json:"name"`
    Role  string `json:"role"`
}

func (q *Queries) CreateUser(ctx context.Context, arg CreateUserParams) (User, error) {
    row := q.db.QueryRow(ctx, createUser, arg.Email, arg.Name, arg.Role)
    var i User
    err := row.Scan(
        &i.ID,
        &i.Email,
        &i.Name,
        &i.Role,
        &i.CreatedAt,
    )
    return i, err
}

func (q *Queries) GetUser(ctx context.Context, id int32) (User, error) {
    row := q.db.QueryRow(ctx, getUser, id)
    var i User
    err := row.Scan(&i.ID, &i.Email, &i.Name, &i.Role, &i.CreatedAt)
    return i, err
}

type ListUsersParams struct {
    Limit  int32 `json:"limit"`
    Offset int32 `json:"offset"`
}

func (q *Queries) ListUsers(ctx context.Context, arg ListUsersParams) ([]User, error) {
    rows, err := q.db.Query(ctx, listUsers, arg.Limit, arg.Offset)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    items := []User{}
    for rows.Next() {
        var i User
        if err := rows.Scan(&i.ID, &i.Email, &i.Name, &i.Role, &i.CreatedAt); err != nil {
            return nil, err
        }
        items = append(items, i)
    }
    return items, nil
}
```

### Использование

```go
package main

import (
    "context"
    "log"

    "github.com/jackc/pgx/v5/pgxpool"
    "myapp/internal/db"
)

func main() {
    ctx := context.Background()

    pool, err := pgxpool.New(ctx, "postgres://localhost/mydb")
    if err != nil {
        log.Fatal(err)
    }
    defer pool.Close()

    queries := db.New(pool)

    // Создание пользователя — type-safe!
    user, err := queries.CreateUser(ctx, db.CreateUserParams{
        Email: "user@example.com",
        Name:  "John Doe",
        Role:  "admin",
    })
    if err != nil {
        log.Fatal(err)
    }
    log.Printf("Created user: %+v", user)

    // Получение пользователя
    user, err = queries.GetUser(ctx, user.ID)
    if err != nil {
        log.Fatal(err)
    }

    // Список пользователей
    users, err := queries.ListUsers(ctx, db.ListUsersParams{
        Limit:  10,
        Offset: 0,
    })
    if err != nil {
        log.Fatal(err)
    }

    // Подсчёт
    count, err := queries.CountUsersByRole(ctx, "admin")
    if err != nil {
        log.Fatal(err)
    }
    log.Printf("Admin count: %d", count)
}
```

### Сравнение с Dapper (C#)

| Dapper | sqlc |
|--------|------|
| Runtime SQL → Object | Compile-time SQL → Go code |
| Reflection для маппинга | Генерация кода |
| Ошибки в runtime | Ошибки при генерации |
| Гибкий | Строгий |

```csharp
// Dapper (C#)
var user = connection.QuerySingleOrDefault<User>(
    "SELECT * FROM users WHERE id = @Id",
    new { Id = 1 }
);
```

```go
// sqlc (Go) — type-safe, compile-time проверка
user, err := queries.GetUser(ctx, 1)
```

---

## GORM: когда нужен ORM

[GORM](https://gorm.io/) — самый популярный ORM для Go. Похож на EF Core.

### Базовые операции

```go
import (
    "gorm.io/driver/postgres"
    "gorm.io/gorm"
)

type User struct {
    gorm.Model        // ID, CreatedAt, UpdatedAt, DeletedAt
    Email     string  `gorm:"uniqueIndex;not null"`
    Name      string  `gorm:"not null"`
    Role      string  `gorm:"default:user"`
    Posts     []Post  // Has Many
}

type Post struct {
    gorm.Model
    Title   string
    Content string
    UserID  uint
    User    User // Belongs To
}

func main() {
    dsn := "host=localhost user=postgres password=postgres dbname=mydb"
    db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
    if err != nil {
        log.Fatal(err)
    }

    // Автоматические миграции
    db.AutoMigrate(&User{}, &Post{})

    // CREATE
    user := User{Email: "user@example.com", Name: "John"}
    result := db.Create(&user)
    if result.Error != nil {
        log.Fatal(result.Error)
    }
    log.Printf("Created user ID: %d", user.ID)

    // READ
    var foundUser User
    db.First(&foundUser, user.ID)                          // по primary key
    db.First(&foundUser, "email = ?", "user@example.com")  // по условию

    // READ несколько
    var users []User
    db.Where("role = ?", "admin").Find(&users)

    // UPDATE
    db.Model(&user).Update("name", "John Doe")
    db.Model(&user).Updates(User{Name: "John", Role: "admin"})
    db.Model(&user).Updates(map[string]interface{}{"name": "John", "role": "admin"})

    // DELETE (soft delete по умолчанию)
    db.Delete(&user)

    // Hard delete
    db.Unscoped().Delete(&user)
}
```

### Миграции (GORM)

```go
// AutoMigrate — только добавляет колонки, не удаляет
db.AutoMigrate(&User{}, &Post{})

// Для production лучше использовать golang-migrate или goose
```

### Associations

```go
// Preload (аналог Include в EF)
var user User
db.Preload("Posts").First(&user, 1)

// Вложенный Preload
db.Preload("Posts.Comments").First(&user, 1)

// Условный Preload
db.Preload("Posts", "published = ?", true).First(&user, 1)

// Joins (более эффективно для single query)
db.Joins("Posts").First(&user, 1)
```

### Когда использовать GORM

```
✅ Используйте GORM если:
- Привыкли к EF Core / Hibernate
- Нужны быстрые CRUD операции
- Проект небольшой, производительность не критична
- Много связей между таблицами

❌ Не используйте GORM если:
- Критична производительность
- Сложные SQL запросы
- Нужен полный контроль над SQL
- Большие объёмы данных
```

---

## Миграции базы данных

### golang-migrate

[golang-migrate](https://github.com/golang-migrate/migrate) — популярный инструмент миграций.

```bash
# Установка
go install -tags 'postgres' github.com/golang-migrate/migrate/v4/cmd/migrate@latest

# Создание миграции
migrate create -ext sql -dir migrations -seq create_users

# Применение миграций
migrate -path migrations -database "postgres://localhost/mydb?sslmode=disable" up

# Откат
migrate -path migrations -database "postgres://localhost/mydb?sslmode=disable" down 1

# Статус
migrate -path migrations -database "postgres://localhost/mydb?sslmode=disable" version
```

```sql
-- migrations/000001_create_users.up.sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

```sql
-- migrations/000001_create_users.down.sql
DROP TABLE IF EXISTS users;
```

```go
// Программное применение миграций
import (
    "github.com/golang-migrate/migrate/v4"
    _ "github.com/golang-migrate/migrate/v4/database/postgres"
    _ "github.com/golang-migrate/migrate/v4/source/file"
)

func RunMigrations(databaseURL string) error {
    m, err := migrate.New(
        "file://migrations",
        databaseURL,
    )
    if err != nil {
        return err
    }

    if err := m.Up(); err != nil && err != migrate.ErrNoChange {
        return err
    }

    return nil
}
```

### goose

[goose](https://github.com/pressly/goose) — альтернатива с поддержкой Go-миграций.

```bash
# Установка
go install github.com/pressly/goose/v3/cmd/goose@latest

# Создание миграции
goose -dir migrations create create_users sql

# Применение
goose -dir migrations postgres "postgres://localhost/mydb" up

# Откат
goose -dir migrations postgres "postgres://localhost/mydb" down
```

```sql
-- migrations/20240101120000_create_users.sql

-- +goose Up
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL
);

-- +goose Down
DROP TABLE users;
```

```go
// Go-миграции (для сложных операций)
// migrations/20240102120000_seed_data.go

package migrations

import (
    "context"
    "database/sql"
    "github.com/pressly/goose/v3"
)

func init() {
    goose.AddMigrationContext(upSeedData, downSeedData)
}

func upSeedData(ctx context.Context, tx *sql.Tx) error {
    _, err := tx.ExecContext(ctx, `
        INSERT INTO users (email, name) VALUES
        ('admin@example.com', 'Admin'),
        ('user@example.com', 'User')
    `)
    return err
}

func downSeedData(ctx context.Context, tx *sql.Tx) error {
    _, err := tx.ExecContext(ctx, `DELETE FROM users WHERE email IN ('admin@example.com', 'user@example.com')`)
    return err
}
```

---

## Repository Pattern

Паттерн Repository инкапсулирует логику доступа к данным.

```go
// internal/domain/user.go
package domain

import (
    "context"
    "time"
)

type User struct {
    ID        int
    Email     string
    Name      string
    Role      string
    CreatedAt time.Time
}

type UserRepository interface {
    GetByID(ctx context.Context, id int) (*User, error)
    GetByEmail(ctx context.Context, email string) (*User, error)
    List(ctx context.Context, limit, offset int) ([]User, error)
    Create(ctx context.Context, user *User) error
    Update(ctx context.Context, user *User) error
    Delete(ctx context.Context, id int) error
}
```

```go
// internal/repository/postgres/user.go
package postgres

import (
    "context"
    "errors"

    "github.com/jackc/pgx/v5"
    "github.com/jackc/pgx/v5/pgxpool"

    "myapp/internal/domain"
)

type UserRepository struct {
    pool *pgxpool.Pool
}

func NewUserRepository(pool *pgxpool.Pool) *UserRepository {
    return &UserRepository{pool: pool}
}

// Проверяем реализацию интерфейса
var _ domain.UserRepository = (*UserRepository)(nil)

func (r *UserRepository) GetByID(ctx context.Context, id int) (*domain.User, error) {
    query := `
        SELECT id, email, name, role, created_at
        FROM users
        WHERE id = $1 AND deleted_at IS NULL
    `

    user := &domain.User{}
    err := r.pool.QueryRow(ctx, query, id).Scan(
        &user.ID,
        &user.Email,
        &user.Name,
        &user.Role,
        &user.CreatedAt,
    )
    if errors.Is(err, pgx.ErrNoRows) {
        return nil, nil
    }
    if err != nil {
        return nil, err
    }
    return user, nil
}

func (r *UserRepository) GetByEmail(ctx context.Context, email string) (*domain.User, error) {
    query := `
        SELECT id, email, name, role, created_at
        FROM users
        WHERE email = $1 AND deleted_at IS NULL
    `

    user := &domain.User{}
    err := r.pool.QueryRow(ctx, query, email).Scan(
        &user.ID,
        &user.Email,
        &user.Name,
        &user.Role,
        &user.CreatedAt,
    )
    if errors.Is(err, pgx.ErrNoRows) {
        return nil, nil
    }
    return user, err
}

func (r *UserRepository) List(ctx context.Context, limit, offset int) ([]domain.User, error) {
    query := `
        SELECT id, email, name, role, created_at
        FROM users
        WHERE deleted_at IS NULL
        ORDER BY created_at DESC
        LIMIT $1 OFFSET $2
    `

    rows, err := r.pool.Query(ctx, query, limit, offset)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var users []domain.User
    for rows.Next() {
        var user domain.User
        if err := rows.Scan(&user.ID, &user.Email, &user.Name, &user.Role, &user.CreatedAt); err != nil {
            return nil, err
        }
        users = append(users, user)
    }

    return users, rows.Err()
}

func (r *UserRepository) Create(ctx context.Context, user *domain.User) error {
    query := `
        INSERT INTO users (email, name, role)
        VALUES ($1, $2, $3)
        RETURNING id, created_at
    `

    return r.pool.QueryRow(ctx, query, user.Email, user.Name, user.Role).
        Scan(&user.ID, &user.CreatedAt)
}

func (r *UserRepository) Update(ctx context.Context, user *domain.User) error {
    query := `
        UPDATE users
        SET name = $2, role = $3
        WHERE id = $1 AND deleted_at IS NULL
    `

    result, err := r.pool.Exec(ctx, query, user.ID, user.Name, user.Role)
    if err != nil {
        return err
    }

    if result.RowsAffected() == 0 {
        return domain.ErrUserNotFound
    }
    return nil
}

func (r *UserRepository) Delete(ctx context.Context, id int) error {
    query := `UPDATE users SET deleted_at = NOW() WHERE id = $1`
    _, err := r.pool.Exec(ctx, query, id)
    return err
}
```

---

## Практические примеры

### Пример 1: CRUD с pgx

```go
// internal/repository/user_repository.go
package repository

import (
    "context"
    "errors"
    "time"

    "github.com/jackc/pgx/v5"
    "github.com/jackc/pgx/v5/pgxpool"
)

type User struct {
    ID        int       `json:"id"`
    Email     string    `json:"email"`
    Name      string    `json:"name"`
    CreatedAt time.Time `json:"created_at"`
}

var ErrNotFound = errors.New("not found")

type UserRepository struct {
    pool *pgxpool.Pool
}

func NewUserRepository(pool *pgxpool.Pool) *UserRepository {
    return &UserRepository{pool: pool}
}

func (r *UserRepository) Create(ctx context.Context, email, name string) (*User, error) {
    user := &User{}
    err := r.pool.QueryRow(ctx,
        `INSERT INTO users (email, name) VALUES ($1, $2)
         RETURNING id, email, name, created_at`,
        email, name,
    ).Scan(&user.ID, &user.Email, &user.Name, &user.CreatedAt)

    return user, err
}

func (r *UserRepository) GetByID(ctx context.Context, id int) (*User, error) {
    user := &User{}
    err := r.pool.QueryRow(ctx,
        `SELECT id, email, name, created_at FROM users WHERE id = $1`,
        id,
    ).Scan(&user.ID, &user.Email, &user.Name, &user.CreatedAt)

    if errors.Is(err, pgx.ErrNoRows) {
        return nil, ErrNotFound
    }
    return user, err
}

func (r *UserRepository) List(ctx context.Context, limit, offset int) ([]User, error) {
    rows, err := r.pool.Query(ctx,
        `SELECT id, email, name, created_at FROM users
         ORDER BY id LIMIT $1 OFFSET $2`,
        limit, offset,
    )
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var users []User
    for rows.Next() {
        var u User
        if err := rows.Scan(&u.ID, &u.Email, &u.Name, &u.CreatedAt); err != nil {
            return nil, err
        }
        users = append(users, u)
    }
    return users, rows.Err()
}

func (r *UserRepository) Update(ctx context.Context, id int, name string) error {
    result, err := r.pool.Exec(ctx,
        `UPDATE users SET name = $1 WHERE id = $2`,
        name, id,
    )
    if err != nil {
        return err
    }
    if result.RowsAffected() == 0 {
        return ErrNotFound
    }
    return nil
}

func (r *UserRepository) Delete(ctx context.Context, id int) error {
    result, err := r.pool.Exec(ctx, `DELETE FROM users WHERE id = $1`, id)
    if err != nil {
        return err
    }
    if result.RowsAffected() == 0 {
        return ErrNotFound
    }
    return nil
}
```

### Пример 2: Type-safe queries с sqlc

Полная структура проекта с sqlc:

```
myapp/
├── sqlc.yaml
├── schema/
│   └── 001_init.sql
├── queries/
│   ├── users.sql
│   └── posts.sql
├── internal/
│   └── db/           # Сгенерированный код
└── cmd/
    └── api/
        └── main.go
```

```yaml
# sqlc.yaml
version: "2"
sql:
  - engine: "postgresql"
    queries: "queries/"
    schema: "schema/"
    gen:
      go:
        package: "db"
        out: "internal/db"
        sql_package: "pgx/v5"
        emit_json_tags: true
        emit_empty_slices: true
        emit_result_struct_pointers: true
```

```sql
-- queries/users.sql

-- name: GetUser :one
SELECT * FROM users WHERE id = $1;

-- name: ListUsers :many
SELECT * FROM users ORDER BY created_at DESC LIMIT $1 OFFSET $2;

-- name: CreateUser :one
INSERT INTO users (email, name) VALUES ($1, $2) RETURNING *;

-- name: UpdateUserName :exec
UPDATE users SET name = $2 WHERE id = $1;

-- name: DeleteUser :exec
DELETE FROM users WHERE id = $1;

-- name: GetUserWithPosts :many
SELECT
    u.id, u.email, u.name, u.created_at,
    p.id as post_id, p.title, p.content
FROM users u
LEFT JOIN posts p ON p.user_id = u.id
WHERE u.id = $1;
```

### Пример 3: Repository с транзакциями

```go
// internal/repository/txmanager.go
package repository

import (
    "context"

    "github.com/jackc/pgx/v5"
    "github.com/jackc/pgx/v5/pgxpool"
)

type TxManager struct {
    pool *pgxpool.Pool
}

func NewTxManager(pool *pgxpool.Pool) *TxManager {
    return &TxManager{pool: pool}
}

type TxFunc func(ctx context.Context, tx pgx.Tx) error

func (m *TxManager) WithTx(ctx context.Context, fn TxFunc) error {
    tx, err := m.pool.Begin(ctx)
    if err != nil {
        return err
    }
    defer tx.Rollback(ctx)

    if err := fn(ctx, tx); err != nil {
        return err
    }

    return tx.Commit(ctx)
}

// Использование
type OrderService struct {
    txManager *TxManager
    orderRepo *OrderRepository
    stockRepo *StockRepository
}

func (s *OrderService) CreateOrder(ctx context.Context, order Order) error {
    return s.txManager.WithTx(ctx, func(ctx context.Context, tx pgx.Tx) error {
        // Создаём заказ
        if err := s.orderRepo.CreateWithTx(ctx, tx, &order); err != nil {
            return err
        }

        // Уменьшаем остатки
        for _, item := range order.Items {
            if err := s.stockRepo.DecrementWithTx(ctx, tx, item.ProductID, item.Quantity); err != nil {
                return err // Автоматический rollback
            }
        }

        return nil
    })
}
```

---

## Чек-лист

После изучения этого раздела вы должны уметь:

- [ ] Настроить connection pool в database/sql и pgx
- [ ] Выполнять CRUD операции с параметризованными запросами
- [ ] Работать с транзакциями и context
- [ ] Использовать pgx для batch запросов и COPY
- [ ] Настроить sqlc для генерации type-safe кода
- [ ] Писать SQL запросы для sqlc
- [ ] Применять миграции с golang-migrate или goose
- [ ] Реализовать Repository pattern
- [ ] Сравнить подходы Go и EF Core

---

## Следующие шаги

В следующем разделе мы рассмотрим [Валидацию и сериализацию](./04_validation_serialization.md) — JSON, validator и Protocol Buffers.

---

**Вопросы?** Открой issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Структура проекта](./02_project_structure.md) | [Вперёд: Валидация и сериализация →](./04_validation_serialization.md)
