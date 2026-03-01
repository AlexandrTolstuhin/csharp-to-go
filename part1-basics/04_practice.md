# 1.4 Практика: Закрепление основ

## Содержание
- [Введение](#введение)
- [Проект 1: CLI-утилита для работы с файлами](#проект-1-cli-утилита-для-работы-с-файлами)
- [Проект 2: HTTP-сервер с JSON API](#проект-2-http-сервер-с-json-api)
- [Проект 3: Конкурентная обработка данных](#проект-3-конкурентная-обработка-данных)
- [Проект 4: Парсер логов](#проект-4-парсер-логов)
- [Дополнительные задачи](#дополнительные-задачи)
- [Решения и подсказки](#решения-и-подсказки)

---

## Введение

В этом разделе вы закрепите базовые знания Go через практические проекты. Каждый проект разбит на этапы с подсказками и решениями.

### Что вы отработаете

- ✅ Работа с файловой системой
- ✅ CLI аргументы и флаги
- ✅ HTTP серверы и роутинг
- ✅ JSON сериализация/десериализация
- ✅ Error handling
- ✅ Тестирование
- ✅ Goroutines и channels
- ✅ Работа с контекстом

### Требования

Перед началом убедитесь, что прошли:
- [01_setup_environment.md](01_setup_environment.md)
- [02_syntax_basics.md](02_syntax_basics.md)
- [03_key_differences.md](03_key_differences.md)

---

## Проект 1: CLI-утилита для работы с файлами

### Описание

Создайте утилиту `filetools` для работы с файлами и директориями. Это аналог базовых UNIX-команд.

### Функциональность

```bash
# Подсчёт строк в файле
filetools count lines file.txt

# Подсчёт слов
filetools count words file.txt

# Поиск текста в файлах
filetools search "pattern" *.txt

# Вывод структуры директории (как tree)
filetools tree ./src

# Копирование файлов с прогресс-баром
filetools copy source.bin dest.bin

# Генерация хеша файла (MD5, SHA256)
filetools hash sha256 file.bin
```

### Этап 1: Подсчёт строк и слов

**Задача**: Реализуйте команду `count lines` и `count words`.

**Требования**:
- Читайте файл построчно (не загружайте весь файл в память)
- Обрабатывайте ошибки (файл не найден, нет прав и т.д.)
- Поддержите флаг `--verbose` для вывода дополнительной информации

**Подсказка**:
```go
package main

import (
    "bufio"
    "flag"
    "fmt"
    "os"
    "strings"
)

func countLines(filename string) (int, error) {
    // TODO: открыть файл
    // TODO: создать bufio.Scanner
    // TODO: подсчитать строки
    return 0, nil
}

func countWords(filename string) (int, error) {
    // TODO: аналогично countLines, но считаем слова
    // Используйте strings.Fields() для разбиения строки
    return 0, nil
}

func main() {
    // TODO: парсинг аргументов командной строки
    // TODO: вызов нужной функции
}
```

**Проверка**:
```bash
go run main.go count lines test.txt
# Lines: 42

go run main.go count words test.txt
# Words: 256
```

<details>
<summary>📖 Решение этапа 1</summary>

```go
package main

import (
    "bufio"
    "flag"
    "fmt"
    "os"
    "strings"
)

func countLines(filename string, verbose bool) (int, error) {
    file, err := os.Open(filename)
    if err != nil {
        return 0, fmt.Errorf("open file: %w", err)
    }
    defer file.Close()

    scanner := bufio.NewScanner(file)
    count := 0

    for scanner.Scan() {
        count++
        if verbose && count%1000 == 0 {
            fmt.Printf("Processed %d lines...\n", count)
        }
    }

    if err := scanner.Err(); err != nil {
        return count, fmt.Errorf("scan file: %w", err)
    }

    return count, nil
}

func countWords(filename string, verbose bool) (int, error) {
    file, err := os.Open(filename)
    if err != nil {
        return 0, fmt.Errorf("open file: %w", err)
    }
    defer file.Close()

    scanner := bufio.NewScanner(file)
    count := 0

    for scanner.Scan() {
        line := scanner.Text()
        words := strings.Fields(line)
        count += len(words)
    }

    if err := scanner.Err(); err != nil {
        return count, fmt.Errorf("scan file: %w", err)
    }

    return count, nil
}

func main() {
    if len(os.Args) < 3 {
        fmt.Println("Usage: filetools count [lines|words] <filename>")
        os.Exit(1)
    }

    verbose := flag.Bool("verbose", false, "verbose output")
    flag.CommandLine.Parse(os.Args[3:])

    command := os.Args[1]
    subcommand := os.Args[2]
    filename := flag.Arg(0)

    if command != "count" {
        fmt.Printf("Unknown command: %s\n", command)
        os.Exit(1)
    }

    var count int
    var err error

    switch subcommand {
    case "lines":
        count, err = countLines(filename, *verbose)
    case "words":
        count, err = countWords(filename, *verbose)
    default:
        fmt.Printf("Unknown subcommand: %s\n", subcommand)
        os.Exit(1)
    }

    if err != nil {
        fmt.Printf("Error: %v\n", err)
        os.Exit(1)
    }

    fmt.Printf("%s: %d\n", strings.Title(subcommand), count)
}
```
</details>

### Этап 2: Поиск текста в файлах (grep)

**Задача**: Реализуйте команду `search` для поиска паттерна в файлах.

**Требования**:
- Поддержите wildcard паттерны (`*.txt`)
- Выводите имя файла, номер строки и саму строку
- Поддержите флаг `--ignore-case` для регистронезависимого поиска
- Используйте regexp для более сложных паттернов

**Подсказка**:
```go
import (
    "path/filepath"
    "regexp"
)

func searchInFile(filename, pattern string, ignoreCase bool) error {
    // TODO: откройте файл
    // TODO: скомпилируйте regexp
    // TODO: ищите совпадения построчно
    // TODO: выводите filename:lineNum:line
    return nil
}

func main() {
    // TODO: используйте filepath.Glob для wildcard
    // Пример: matches, err := filepath.Glob("*.txt")
}
```

<details>
<summary>📖 Решение этапа 2</summary>

```go
func searchInFile(filename, pattern string, ignoreCase bool) error {
    file, err := os.Open(filename)
    if err != nil {
        return fmt.Errorf("open file: %w", err)
    }
    defer file.Close()

    // Компилируем регулярное выражение
    var re *regexp.Regexp
    if ignoreCase {
        re, err = regexp.Compile("(?i)" + pattern)
    } else {
        re, err = regexp.Compile(pattern)
    }
    if err != nil {
        return fmt.Errorf("compile regex: %w", err)
    }

    scanner := bufio.NewScanner(file)
    lineNum := 0

    for scanner.Scan() {
        lineNum++
        line := scanner.Text()

        if re.MatchString(line) {
            // Выводим в формате grep: filename:lineNum:line
            fmt.Printf("%s:%d:%s\n", filename, lineNum, line)
        }
    }

    return scanner.Err()
}

func searchCommand(pattern string, filePattern string, ignoreCase bool) error {
    matches, err := filepath.Glob(filePattern)
    if err != nil {
        return fmt.Errorf("glob pattern: %w", err)
    }

    if len(matches) == 0 {
        return fmt.Errorf("no files match pattern: %s", filePattern)
    }

    for _, filename := range matches {
        if err := searchInFile(filename, pattern, ignoreCase); err != nil {
            fmt.Fprintf(os.Stderr, "Error searching %s: %v\n", filename, err)
        }
    }

    return nil
}
```
</details>

### Этап 3: Генерация хешей

**Задача**: Реализуйте команду `hash` для вычисления MD5/SHA256 хеша файла.

**Требования**:
- Поддержите алгоритмы: md5, sha1, sha256
- Читайте файл блоками для экономии памяти
- Выводите хеш в hex формате

**Проверка**:
```bash
go run main.go hash sha256 file.bin
# SHA256: a1b2c3d4...
```

<details>
<summary>📖 Решение этапа 3</summary>

```go
import (
    "crypto/md5"
    "crypto/sha1"
    "crypto/sha256"
    "encoding/hex"
    "hash"
    "io"
)

func hashFile(filename, algorithm string) (string, error) {
    file, err := os.Open(filename)
    if err != nil {
        return "", fmt.Errorf("open file: %w", err)
    }
    defer file.Close()

    var hasher hash.Hash

    switch algorithm {
    case "md5":
        hasher = md5.New()
    case "sha1":
        hasher = sha1.New()
    case "sha256":
        hasher = sha256.New()
    default:
        return "", fmt.Errorf("unsupported algorithm: %s", algorithm)
    }

    // Копируем файл в hasher блоками
    if _, err := io.Copy(hasher, file); err != nil {
        return "", fmt.Errorf("hash file: %w", err)
    }

    hashBytes := hasher.Sum(nil)
    return hex.EncodeToString(hashBytes), nil
}
```
</details>

### Полный код проекта

После реализации всех этапов структура проекта:

```
filetools/
├── go.mod
├── main.go
├── commands/
│   ├── count.go
│   ├── search.go
│   └── hash.go
├── internal/
│   └── utils/
│       └── file.go
└── main_test.go
```

### Задания для самостоятельной работы

1. Добавьте команду `tree` для вывода структуры директории
2. Реализуйте `copy` с прогресс-баром (используйте goroutine)
3. Добавьте поддержку `.gitignore` паттернов в `search`
4. Напишите unit-тесты для всех команд
5. Соберите бинарник с помощью `go build` и проверьте его размер

---

## Проект 2: HTTP-сервер с JSON API

### Описание

Создайте RESTful API для управления задачами (TODO list). Это типичный CRUD-сервис.

### API спецификация

```
GET    /api/tasks           - Получить все задачи
GET    /api/tasks/:id       - Получить задачу по ID
POST   /api/tasks           - Создать задачу
PUT    /api/tasks/:id       - Обновить задачу
DELETE /api/tasks/:id       - Удалить задачу
GET    /health              - Health check
```

### Модель данных

```go
type Task struct {
    ID          int       `json:"id"`
    Title       string    `json:"title"`
    Description string    `json:"description"`
    Completed   bool      `json:"completed"`
    CreatedAt   time.Time `json:"created_at"`
    UpdatedAt   time.Time `json:"updated_at"`
}
```

### Этап 1: Базовый HTTP сервер

**Задача**: Создайте HTTP сервер с роутингом.

**Требования**:
- Используйте стандартный `net/http` (без фреймворков)
- Реализуйте health check endpoint
- Логируйте все запросы
- Graceful shutdown

**Подсказка**:
```go
package main

import (
    "context"
    "encoding/json"
    "log"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"
)

func healthHandler(w http.ResponseWriter, r *http.Request) {
    // TODO: верните {"status": "ok"}
}

func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        // TODO: логируйте метод, путь, время выполнения
        next.ServeHTTP(w, r)
        log.Printf("%s %s - %v", r.Method, r.URL.Path, time.Since(start))
    })
}

func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("/health", healthHandler)

    // Оборачиваем в middleware
    handler := loggingMiddleware(mux)

    srv := &http.Server{
        Addr:         ":8080",
        Handler:      handler,
        ReadTimeout:  10 * time.Second,
        WriteTimeout: 10 * time.Second,
    }

    // TODO: запуск сервера в goroutine
    // TODO: graceful shutdown по сигналу
}
```

<details>
<summary>📖 Решение этапа 1</summary>

```go
package main

import (
    "context"
    "encoding/json"
    "log"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"
)

func healthHandler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]string{
        "status": "ok",
        "time":   time.Now().Format(time.RFC3339),
    })
}

func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s - %v", r.Method, r.URL.Path, time.Since(start))
    })
}

func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("/health", healthHandler)

    handler := loggingMiddleware(mux)

    srv := &http.Server{
        Addr:         ":8080",
        Handler:      handler,
        ReadTimeout:  10 * time.Second,
        WriteTimeout: 10 * time.Second,
        IdleTimeout:  60 * time.Second,
    }

    // Запускаем сервер в отдельной goroutine
    go func() {
        log.Printf("Starting server on %s", srv.Addr)
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatalf("Server failed: %v", err)
        }
    }()

    // Graceful shutdown
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    log.Println("Shutting down server...")

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := srv.Shutdown(ctx); err != nil {
        log.Fatalf("Server forced to shutdown: %v", err)
    }

    log.Println("Server stopped")
}
```
</details>

### Этап 2: In-memory хранилище

**Задача**: Реализуйте CRUD операции с хранением в памяти.

**Требования**:
- Thread-safe операции (используйте `sync.RWMutex`)
- Валидация входных данных
- Правильные HTTP коды ответов
- Обработка ошибок

**Подсказка**:
```go
type TaskStore struct {
    mu    sync.RWMutex
    tasks map[int]*Task
    nextID int
}

func NewTaskStore() *TaskStore {
    return &TaskStore{
        tasks: make(map[int]*Task),
        nextID: 1,
    }
}

func (s *TaskStore) Create(task *Task) (*Task, error) {
    s.mu.Lock()
    defer s.mu.Unlock()

    // TODO: валидация
    // TODO: установка ID, timestamps
    // TODO: сохранение в map

    return task, nil
}

func (s *TaskStore) GetAll() []*Task {
    // TODO: используйте s.mu.RLock()
    return nil
}

func (s *TaskStore) GetByID(id int) (*Task, error) {
    // TODO: реализуйте
    return nil, nil
}

func (s *TaskStore) Update(id int, task *Task) (*Task, error) {
    // TODO: реализуйте
    return nil, nil
}

func (s *TaskStore) Delete(id int) error {
    // TODO: реализуйте
    return nil
}
```

<details>
<summary>📖 Решение этапа 2</summary>

```go
import (
    "errors"
    "sync"
    "time"
)

var (
    ErrTaskNotFound = errors.New("task not found")
    ErrInvalidTask  = errors.New("invalid task")
)

type Task struct {
    ID          int       `json:"id"`
    Title       string    `json:"title"`
    Description string    `json:"description"`
    Completed   bool      `json:"completed"`
    CreatedAt   time.Time `json:"created_at"`
    UpdatedAt   time.Time `json:"updated_at"`
}

type TaskStore struct {
    mu     sync.RWMutex
    tasks  map[int]*Task
    nextID int
}

func NewTaskStore() *TaskStore {
    return &TaskStore{
        tasks:  make(map[int]*Task),
        nextID: 1,
    }
}

func (s *TaskStore) Create(task *Task) (*Task, error) {
    if task.Title == "" {
        return nil, ErrInvalidTask
    }

    s.mu.Lock()
    defer s.mu.Unlock()

    now := time.Now()
    task.ID = s.nextID
    s.nextID++
    task.CreatedAt = now
    task.UpdatedAt = now

    s.tasks[task.ID] = task

    return task, nil
}

func (s *TaskStore) GetAll() []*Task {
    s.mu.RLock()
    defer s.mu.RUnlock()

    tasks := make([]*Task, 0, len(s.tasks))
    for _, task := range s.tasks {
        tasks = append(tasks, task)
    }

    return tasks
}

func (s *TaskStore) GetByID(id int) (*Task, error) {
    s.mu.RLock()
    defer s.mu.RUnlock()

    task, exists := s.tasks[id]
    if !exists {
        return nil, ErrTaskNotFound
    }

    return task, nil
}

func (s *TaskStore) Update(id int, updatedTask *Task) (*Task, error) {
    if updatedTask.Title == "" {
        return nil, ErrInvalidTask
    }

    s.mu.Lock()
    defer s.mu.Unlock()

    task, exists := s.tasks[id]
    if !exists {
        return nil, ErrTaskNotFound
    }

    task.Title = updatedTask.Title
    task.Description = updatedTask.Description
    task.Completed = updatedTask.Completed
    task.UpdatedAt = time.Now()

    return task, nil
}

func (s *TaskStore) Delete(id int) error {
    s.mu.Lock()
    defer s.mu.Unlock()

    if _, exists := s.tasks[id]; !exists {
        return ErrTaskNotFound
    }

    delete(s.tasks, id)
    return nil
}
```
</details>

### Этап 3: HTTP handlers

**Задача**: Реализуйте HTTP handlers для всех endpoints.

**Требования**:
- Правильные HTTP статус коды
- JSON сериализация/десериализация
- Обработка ошибок
- Извлечение ID из URL

**Подсказка**:
```go
type TaskHandler struct {
    store *TaskStore
}

func (h *TaskHandler) handleGetTasks(w http.ResponseWriter, r *http.Request) {
    tasks := h.store.GetAll()
    respondJSON(w, http.StatusOK, tasks)
}

func (h *TaskHandler) handleGetTask(w http.ResponseWriter, r *http.Request) {
    // TODO: извлеките ID из URL
    // TODO: получите задачу из store
    // TODO: обработайте ошибки
}

func (h *TaskHandler) handleCreateTask(w http.ResponseWriter, r *http.Request) {
    var task Task
    if err := json.NewDecoder(r.Body).Decode(&task); err != nil {
        respondError(w, http.StatusBadRequest, "invalid request body")
        return
    }

    // TODO: создайте задачу через store
}

// Вспомогательные функции
func respondJSON(w http.ResponseWriter, status int, data interface{}) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(data)
}

func respondError(w http.ResponseWriter, status int, message string) {
    respondJSON(w, status, map[string]string{"error": message})
}
```

<details>
<summary>📖 Решение этапа 3</summary>

```go
import (
    "encoding/json"
    "net/http"
    "strconv"
    "strings"
)

type TaskHandler struct {
    store *TaskStore
}

func NewTaskHandler(store *TaskStore) *TaskHandler {
    return &TaskHandler{store: store}
}

func (h *TaskHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    // Роутинг (примитивный, можно использовать chi/gorilla/mux)
    path := strings.TrimPrefix(r.URL.Path, "/api/tasks")

    if path == "" || path == "/" {
        switch r.Method {
        case http.MethodGet:
            h.handleGetTasks(w, r)
        case http.MethodPost:
            h.handleCreateTask(w, r)
        default:
            respondError(w, http.StatusMethodNotAllowed, "method not allowed")
        }
        return
    }

    // Извлекаем ID: /api/tasks/123
    id, err := strconv.Atoi(strings.Trim(path, "/"))
    if err != nil {
        respondError(w, http.StatusBadRequest, "invalid task ID")
        return
    }

    switch r.Method {
    case http.MethodGet:
        h.handleGetTask(w, r, id)
    case http.MethodPut:
        h.handleUpdateTask(w, r, id)
    case http.MethodDelete:
        h.handleDeleteTask(w, r, id)
    default:
        respondError(w, http.StatusMethodNotAllowed, "method not allowed")
    }
}

func (h *TaskHandler) handleGetTasks(w http.ResponseWriter, r *http.Request) {
    tasks := h.store.GetAll()
    respondJSON(w, http.StatusOK, tasks)
}

func (h *TaskHandler) handleGetTask(w http.ResponseWriter, r *http.Request, id int) {
    task, err := h.store.GetByID(id)
    if err != nil {
        if errors.Is(err, ErrTaskNotFound) {
            respondError(w, http.StatusNotFound, "task not found")
            return
        }
        respondError(w, http.StatusInternalServerError, "internal error")
        return
    }

    respondJSON(w, http.StatusOK, task)
}

func (h *TaskHandler) handleCreateTask(w http.ResponseWriter, r *http.Request) {
    var task Task
    if err := json.NewDecoder(r.Body).Decode(&task); err != nil {
        respondError(w, http.StatusBadRequest, "invalid request body")
        return
    }

    created, err := h.store.Create(&task)
    if err != nil {
        if errors.Is(err, ErrInvalidTask) {
            respondError(w, http.StatusBadRequest, err.Error())
            return
        }
        respondError(w, http.StatusInternalServerError, "internal error")
        return
    }

    respondJSON(w, http.StatusCreated, created)
}

func (h *TaskHandler) handleUpdateTask(w http.ResponseWriter, r *http.Request, id int) {
    var task Task
    if err := json.NewDecoder(r.Body).Decode(&task); err != nil {
        respondError(w, http.StatusBadRequest, "invalid request body")
        return
    }

    updated, err := h.store.Update(id, &task)
    if err != nil {
        if errors.Is(err, ErrTaskNotFound) {
            respondError(w, http.StatusNotFound, "task not found")
            return
        }
        if errors.Is(err, ErrInvalidTask) {
            respondError(w, http.StatusBadRequest, err.Error())
            return
        }
        respondError(w, http.StatusInternalServerError, "internal error")
        return
    }

    respondJSON(w, http.StatusOK, updated)
}

func (h *TaskHandler) handleDeleteTask(w http.ResponseWriter, r *http.Request, id int) {
    if err := h.store.Delete(id); err != nil {
        if errors.Is(err, ErrTaskNotFound) {
            respondError(w, http.StatusNotFound, "task not found")
            return
        }
        respondError(w, http.StatusInternalServerError, "internal error")
        return
    }

    w.WriteHeader(http.StatusNoContent)
}

func respondJSON(w http.ResponseWriter, status int, data interface{}) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    if err := json.NewEncoder(w).Encode(data); err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
    }
}

func respondError(w http.ResponseWriter, status int, message string) {
    respondJSON(w, status, map[string]string{"error": message})
}
```
</details>

### Тестирование API

```bash
# Создание задачи
curl -X POST http://localhost:8080/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn Go","description":"Complete tutorial"}'

# Получение всех задач
curl http://localhost:8080/api/tasks

# Получение задачи по ID
curl http://localhost:8080/api/tasks/1

# Обновление задачи
curl -X PUT http://localhost:8080/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn Go","completed":true}'

# Удаление задачи
curl -X DELETE http://localhost:8080/api/tasks/1

# Health check
curl http://localhost:8080/health
```

### Задания для самостоятельной работы

1. Добавьте middleware для CORS
2. Реализуйте фильтрацию задач (GET /api/tasks?completed=true)
3. Добавьте пагинацию (GET /api/tasks?page=1&limit=10)
4. Сохраняйте задачи в JSON файл при shutdown
5. Добавьте метрики (количество запросов, время ответа)
6. Напишите интеграционные тесты с `httptest`

---

## Проект 3: Конкурентная обработка данных

### Описание

Создайте программу для параллельной обработки больших файлов с использованием goroutines и channels.

### Сценарий

Обработка CSV файла с миллионами записей:
- Чтение из файла
- Парсинг строк
- Валидация данных
- Агрегация результатов
- Запись в выходной файл

### Этап 1: Worker Pool Pattern

**Задача**: Реализуйте worker pool для обработки данных.

**Подсказка**:
```go
type Job struct {
    ID   int
    Data string
}

type Result struct {
    JobID int
    Value int
    Error error
}

func worker(id int, jobs <-chan Job, results chan<- Result) {
    for job := range jobs {
        // TODO: обработайте job
        // TODO: отправьте результат в results
    }
}

func main() {
    numWorkers := 5
    jobs := make(chan Job, 100)
    results := make(chan Result, 100)

    // Запускаем workers
    for w := 1; w <= numWorkers; w++ {
        go worker(w, jobs, results)
    }

    // TODO: отправляем jobs
    // TODO: собираем results
}
```

<details>
<summary>📖 Решение этапа 1</summary>

```go
package main

import (
    "bufio"
    "fmt"
    "log"
    "os"
    "strconv"
    "strings"
    "sync"
    "time"
)

type Job struct {
    LineNum int
    Line    string
}

type Result struct {
    LineNum int
    Value   int
    Error   error
}

// worker обрабатывает jobs из канала
func worker(id int, jobs <-chan Job, results chan<- Result, wg *sync.WaitGroup) {
    defer wg.Done()

    for job := range jobs {
        // Симуляция обработки: парсим число из строки
        parts := strings.Split(job.Line, ",")
        if len(parts) < 2 {
            results <- Result{
                LineNum: job.LineNum,
                Error:   fmt.Errorf("invalid format"),
            }
            continue
        }

        value, err := strconv.Atoi(strings.TrimSpace(parts[1]))
        if err != nil {
            results <- Result{
                LineNum: job.LineNum,
                Error:   fmt.Errorf("parse error: %w", err),
            }
            continue
        }

        // Симуляция тяжёлой работы
        time.Sleep(10 * time.Millisecond)

        results <- Result{
            LineNum: job.LineNum,
            Value:   value,
        }
    }
}

func processFile(filename string, numWorkers int) (int, error) {
    file, err := os.Open(filename)
    if err != nil {
        return 0, err
    }
    defer file.Close()

    jobs := make(chan Job, 100)
    results := make(chan Result, 100)

    // Запускаем workers
    var wg sync.WaitGroup
    for w := 1; w <= numWorkers; w++ {
        wg.Add(1)
        go worker(w, jobs, results, &wg)
    }

    // Goroutine для закрытия results после завершения всех workers
    go func() {
        wg.Wait()
        close(results)
    }()

    // Goroutine для отправки jobs
    go func() {
        defer close(jobs)

        scanner := bufio.NewScanner(file)
        lineNum := 0

        for scanner.Scan() {
            lineNum++
            jobs <- Job{
                LineNum: lineNum,
                Line:    scanner.Text(),
            }
        }

        if err := scanner.Err(); err != nil {
            log.Printf("Scanner error: %v", err)
        }
    }()

    // Собираем результаты
    var sum int
    var errorCount int

    for result := range results {
        if result.Error != nil {
            errorCount++
            log.Printf("Line %d error: %v", result.LineNum, result.Error)
            continue
        }
        sum += result.Value
    }

    log.Printf("Processed with %d errors", errorCount)
    return sum, nil
}

func main() {
    if len(os.Args) < 2 {
        fmt.Println("Usage: program <filename>")
        os.Exit(1)
    }

    filename := os.Args[1]
    numWorkers := 5

    start := time.Now()
    sum, err := processFile(filename, numWorkers)
    if err != nil {
        log.Fatalf("Error: %v", err)
    }

    fmt.Printf("Sum: %d\n", sum)
    fmt.Printf("Time: %v\n", time.Since(start))
}
```
</details>

### Этап 2: Pipeline Pattern

**Задача**: Реализуйте pipeline для последовательной обработки данных.

**Схема**:
```
Reader → Parser → Validator → Aggregator → Writer
```

**Подсказка**:
```go
func reader(filename string) <-chan string {
    out := make(chan string)
    go func() {
        defer close(out)
        // TODO: читайте файл построчно
        // TODO: отправляйте строки в out
    }()
    return out
}

func parser(in <-chan string) <-chan Record {
    out := make(chan Record)
    go func() {
        defer close(out)
        for line := range in {
            // TODO: парсите строку в Record
            // TODO: отправляйте в out
        }
    }()
    return out
}

func validator(in <-chan Record) <-chan Record {
    // TODO: валидируйте Record
    return out
}

func main() {
    lines := reader("data.csv")
    records := parser(lines)
    valid := validator(records)

    // TODO: агрегируйте результаты
}
```

<details>
<summary>📖 Решение этапа 2</summary>

```go
type Record struct {
    ID    int
    Name  string
    Value int
}

func reader(filename string) <-chan string {
    out := make(chan string, 100)

    go func() {
        defer close(out)

        file, err := os.Open(filename)
        if err != nil {
            log.Printf("Open file error: %v", err)
            return
        }
        defer file.Close()

        scanner := bufio.NewScanner(file)
        for scanner.Scan() {
            out <- scanner.Text()
        }

        if err := scanner.Err(); err != nil {
            log.Printf("Scanner error: %v", err)
        }
    }()

    return out
}

func parser(in <-chan string) <-chan Record {
    out := make(chan Record, 100)

    go func() {
        defer close(out)

        for line := range in {
            parts := strings.Split(line, ",")
            if len(parts) < 3 {
                continue
            }

            id, err := strconv.Atoi(strings.TrimSpace(parts[0]))
            if err != nil {
                continue
            }

            value, err := strconv.Atoi(strings.TrimSpace(parts[2]))
            if err != nil {
                continue
            }

            out <- Record{
                ID:    id,
                Name:  strings.TrimSpace(parts[1]),
                Value: value,
            }
        }
    }()

    return out
}

func validator(in <-chan Record) <-chan Record {
    out := make(chan Record, 100)

    go func() {
        defer close(out)

        for record := range in {
            // Валидация
            if record.ID <= 0 || record.Name == "" || record.Value < 0 {
                continue
            }

            out <- record
        }
    }()

    return out
}

func aggregator(in <-chan Record) <-chan int {
    out := make(chan int)

    go func() {
        defer close(out)

        sum := 0
        for record := range in {
            sum += record.Value
        }

        out <- sum
    }()

    return out
}

func main() {
    filename := "data.csv"

    // Pipeline
    lines := reader(filename)
    records := parser(lines)
    valid := validator(records)
    result := aggregator(valid)

    // Получаем результат
    sum := <-result
    fmt.Printf("Total sum: %d\n", sum)
}
```
</details>

### Задания для самостоятельной работы

1. Добавьте контекст для graceful cancellation
2. Реализуйте rate limiting для обработки
3. Добавьте метрики: throughput, latency
4. Реализуйте retry механизм для failed jobs
5. Добавьте прогресс-бар используя `github.com/schollz/progressbar`

---

## Проект 4: Парсер логов

### Описание

Создайте утилиту для анализа лог-файлов с агрегацией статистики.

### Функциональность

```bash
# Анализ лог-файла
logparser analyze access.log

# Вывод:
# Total requests: 100500
# Unique IPs: 1234
# Status codes:
#   200: 98000 (97.5%)
#   404: 1500 (1.5%)
#   500: 1000 (1.0%)
# Top URLs:
#   /api/users: 50000
#   /api/products: 30000
```

### Формат лога (Apache Combined)

```
127.0.0.1 - - [10/Oct/2024:13:55:36 +0000] "GET /api/users HTTP/1.1" 200 1234
```

### Задача

Реализуйте парсер с использованием:
- Регулярных выражений для парсинга
- Map для агрегации
- Goroutines для параллельной обработки
- Channels для сбора результатов

<details>
<summary>📖 Решение</summary>

```go
package main

import (
    "bufio"
    "flag"
    "fmt"
    "log"
    "os"
    "regexp"
    "sort"
    "sync"
)

type LogEntry struct {
    IP         string
    Timestamp  string
    Method     string
    URL        string
    StatusCode int
    Size       int
}

type Stats struct {
    mu          sync.Mutex
    totalReqs   int
    ips         map[string]int
    statusCodes map[int]int
    urls        map[string]int
}

func NewStats() *Stats {
    return &Stats{
        ips:         make(map[string]int),
        statusCodes: make(map[int]int),
        urls:        make(map[string]int),
    }
}

func (s *Stats) Add(entry LogEntry) {
    s.mu.Lock()
    defer s.mu.Unlock()

    s.totalReqs++
    s.ips[entry.IP]++
    s.statusCodes[entry.StatusCode]++
    s.urls[entry.URL]++
}

func (s *Stats) Print() {
    s.mu.Lock()
    defer s.mu.Unlock()

    fmt.Printf("\nLog Analysis Results\n")
    fmt.Printf("====================\n\n")

    fmt.Printf("Total requests: %d\n", s.totalReqs)
    fmt.Printf("Unique IPs: %d\n\n", len(s.ips))

    fmt.Println("Status codes:")
    for code, count := range s.statusCodes {
        pct := float64(count) / float64(s.totalReqs) * 100
        fmt.Printf("  %d: %d (%.1f%%)\n", code, count, pct)
    }

    // Топ-10 URLs
    type urlCount struct {
        url   string
        count int
    }

    urlCounts := make([]urlCount, 0, len(s.urls))
    for url, count := range s.urls {
        urlCounts = append(urlCounts, urlCount{url, count})
    }

    sort.Slice(urlCounts, func(i, j int) bool {
        return urlCounts[i].count > urlCounts[j].count
    })

    fmt.Println("\nTop 10 URLs:")
    for i := 0; i < 10 && i < len(urlCounts); i++ {
        fmt.Printf("  %s: %d\n", urlCounts[i].url, urlCounts[i].count)
    }
}

var logRegex = regexp.MustCompile(
    `^(\S+) \S+ \S+ \[([\w:/]+\s[+\-]\d{4})\] "(\S+)\s?(\S+)?\s?(\S+)?" (\d{3}|-) (\d+|-)`,
)

func parseLine(line string) (*LogEntry, error) {
    matches := logRegex.FindStringSubmatch(line)
    if len(matches) < 8 {
        return nil, fmt.Errorf("invalid format")
    }

    var statusCode int
    fmt.Sscanf(matches[6], "%d", &statusCode)

    var size int
    fmt.Sscanf(matches[7], "%d", &size)

    return &LogEntry{
        IP:         matches[1],
        Timestamp:  matches[2],
        Method:     matches[3],
        URL:        matches[4],
        StatusCode: statusCode,
        Size:       size,
    }, nil
}

func processFile(filename string) error {
    file, err := os.Open(filename)
    if err != nil {
        return err
    }
    defer file.Close()

    stats := NewStats()
    scanner := bufio.NewScanner(file)
    lineNum := 0

    for scanner.Scan() {
        lineNum++
        line := scanner.Text()

        entry, err := parseLine(line)
        if err != nil {
            log.Printf("Line %d: %v", lineNum, err)
            continue
        }

        stats.Add(*entry)
    }

    if err := scanner.Err(); err != nil {
        return err
    }

    stats.Print()
    return nil
}

func main() {
    flag.Parse()

    if flag.NArg() < 1 {
        fmt.Println("Usage: logparser <logfile>")
        os.Exit(1)
    }

    filename := flag.Arg(0)

    if err := processFile(filename); err != nil {
        log.Fatalf("Error: %v", err)
    }
}
```
</details>

---

## Дополнительные задачи

### 1. Rate Limiter

Реализуйте rate limiter с использованием каналов:

```go
type RateLimiter struct {
    rate  int           // requests per second
    burst int           // max burst size
    tokens chan struct{}
}

func NewRateLimiter(rate, burst int) *RateLimiter {
    // TODO: реализуйте
}

func (rl *RateLimiter) Allow() bool {
    // TODO: реализуйте
}
```

### 2. Cache с TTL

Реализуйте in-memory cache с expiration:

```go
type Cache struct {
    mu    sync.RWMutex
    items map[string]cacheItem
}

type cacheItem struct {
    value      interface{}
    expiration time.Time
}

func (c *Cache) Set(key string, value interface{}, ttl time.Duration) {
    // TODO: реализуйте
}

func (c *Cache) Get(key string) (interface{}, bool) {
    // TODO: реализуйте с проверкой expiration
}
```

### 3. Graceful Worker Pool

Реализуйте worker pool с graceful shutdown:

```go
type WorkerPool struct {
    workers   int
    jobQueue  chan Job
    wg        sync.WaitGroup
    ctx       context.Context
    cancel    context.CancelFunc
}

func (wp *WorkerPool) Start() {
    // TODO: запустите workers
}

func (wp *WorkerPool) Stop() {
    // TODO: graceful shutdown
}
```

---

## Решения и подсказки

### Общие рекомендации

1. **Error handling**:
   - Всегда проверяйте ошибки
   - Используйте `fmt.Errorf` с `%w` для wrapping
   - Логируйте ошибки с контекстом

2. **Тестирование**:
   - Пишите unit-тесты для каждого модуля
   - Используйте table-driven tests
   - Тестируйте граничные случаи

3. **Производительность**:
   - Используйте `pprof` для профилирования
   - Пишите benchmarks
   - Избегайте аллокаций в горячих путях

4. **Concurrency**:
   - Используйте `context.Context` для cancellation
   - Избегайте shared state
   - Предпочитайте channels для коммуникации

### Полезные пакеты

```go
// CLI
"flag"                                    // Флаги командной строки
"github.com/spf13/cobra"                  // Мощный CLI framework

// HTTP
"net/http"                                // Стандартный HTTP
"github.com/go-chi/chi"                   // Роутер
"github.com/gorilla/mux"                  // Роутер

// Логирование
"log/slog"                                // Структурированные логи (Go 1.21+)
"github.com/sirupsen/logrus"              // Популярный logger

// Тестирование
"testing"                                 // Стандартное тестирование
"github.com/stretchr/testify/assert"     // Assertions

// Concurrency
"context"                                 // Контексты
"golang.org/x/sync/errgroup"             // Групповые goroutines

// Файлы
"os"                                      // Файловая система
"path/filepath"                           // Пути к файлам
"io"                                      // I/O операции
```

---

**Вопросы?** Открой issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Назад: Ключевые отличия от C#](03_key_differences.md) | [Вперёд: Часть 2 →](../part2-advanced/README.md)
