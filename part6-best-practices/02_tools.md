# Инструменты

---

## Введение

В Go качество кода обеспечивается не только компилятором, но и богатой экосистемой инструментов статического анализа. В отличие от C#, где большинство инструментов интегрировано в Visual Studio или Rider, в Go принят модульный подход — множество специализированных инструментов, объединённых в единый workflow.

> 💡 **Для C# разработчиков**: Если в C# вы привыкли к Roslyn Analyzers, встроенным в IDE, то в Go вы столкнётесь с отдельными CLI-инструментами. Но не пугайтесь — golangci-lint объединяет 100+ линтеров в один инструмент с единой конфигурацией.

### Философия Go tooling

Go известен своей философией "batteries included" для базовых инструментов:

```bash
# Форматирование — НЕ обсуждается, один стиль для всех
go fmt ./...

# Базовый статический анализ — встроен
go vet ./...

# Тестирование — встроено
go test ./...

# Управление зависимостями — встроено
go mod tidy
```

Но для production-качества кода этого недостаточно. Здесь на помощь приходят сторонние инструменты, которые мы детально рассмотрим.

### Что мы изучим

1. **golangci-lint** — мета-линтер, объединяющий 100+ проверок
2. **staticcheck** — глубокий статический анализ
3. **govulncheck** — официальный инструмент проверки уязвимостей
4. **go mod** — продвинутое управление зависимостями
5. **air** — hot reload для разработки
6. **Дополнительные инструменты** — gofumpt, goimports, wire
7. **CI/CD интеграция** — GitHub Actions, GitLab CI, pre-commit hooks

---

## Экосистема инструментов: C# vs Go

### Сравнительная таблица

| Категория | C# (.NET) | Go | Комментарий |
|-----------|-----------|-----|-------------|
| **Форматирование** | `dotnet format`, EditorConfig | `go fmt`, `gofumpt` | Go: единый стиль, споры невозможны |
| **Линтеры** | Roslyn Analyzers, StyleCop, ReSharper | golangci-lint (100+ линтеров) | Go: один мета-линтер для всего |
| **Статический анализ** | SonarQube, NDepend, PVS-Studio | staticcheck, go vet | Go: бесплатные официальные инструменты |
| **Уязвимости** | `dotnet audit`, Dependabot, Snyk | govulncheck | Go: официальный инструмент от Go team |
| **Hot reload** | `dotnet watch run` | air | C#: встроен, Go: сторонний |
| **Зависимости** | NuGet, `dotnet restore` | go mod | Go: встроен в toolchain |
| **Code generation** | Source Generators, T4 | go generate | Go: команды в комментариях |
| **DI** | Microsoft.Extensions.DI | wire | C#: runtime, Go: compile-time |
| **Coverage** | coverlet, dotCover | go test -cover | Go: встроен |
| **Benchmarks** | BenchmarkDotNet | go test -bench | Go: встроен |

### Ключевые отличия

**В C#:**
- Большинство инструментов интегрировано в IDE
- Roslyn Analyzers работают в реальном времени при написании кода
- Много коммерческих решений (ReSharper, NDepend, PVS-Studio)
- Каждый инструмент настраивается отдельно

**В Go:**
- Инструменты — отдельные CLI-программы
- golangci-lint объединяет всё с единой конфигурацией
- Почти все инструменты бесплатные и open-source
- Официальные инструменты от Go team (govulncheck, go vet)

### Типичный workflow

**C# проект:**
```bash
# Сборка с анализаторами
dotnet build /p:TreatWarningsAsErrors=true

# Форматирование
dotnet format

# Тесты с покрытием
dotnet test --collect:"XPlat Code Coverage"

# Проверка уязвимостей
dotnet list package --vulnerable
```

**Go проект:**
```bash
# Линтинг (100+ проверок)
golangci-lint run

# Форматирование
gofumpt -l -w .

# Тесты с покрытием
go test -race -cover ./...

# Проверка уязвимостей
govulncheck ./...
```

---

## golangci-lint — мета-линтер

golangci-lint — это агрегатор линтеров, объединяющий более 100 проверок в один инструмент с единой конфигурацией, кэшированием и параллельным выполнением.

### Зачем нужен мета-линтер

**Проблема до golangci-lint:**
```bash
# Раньше запускали каждый линтер отдельно
golint ./...
go vet ./...
errcheck ./...
staticcheck ./...
ineffassign ./...
misspell ./...
# ... ещё 10-20 линтеров
```

Это было:
- Медленно (каждый парсит код заново)
- Неудобно (разные форматы конфигурации)
- Сложно поддерживать в CI/CD

**Решение — golangci-lint:**
```bash
# Один инструмент для всего
golangci-lint run
```

Преимущества:
- **Скорость**: кэширование и параллельное выполнение
- **Единая конфигурация**: один файл `.golangci.yml`
- **Единый формат вывода**: удобно для CI/CD
- **Автофикс**: некоторые проблемы исправляются автоматически

### Установка и базовое использование

> 💡 Базовая установка описана в [разделе 1.1](../part1-basics/01_setup_environment.md). Здесь — продвинутое использование.

```bash
# Установка (рекомендуемый способ)
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# Проверка версии
golangci-lint --version

# Базовый запуск
golangci-lint run

# С автоисправлением (где возможно)
golangci-lint run --fix

# Для конкретных директорий
golangci-lint run ./internal/... ./pkg/...

# С verbose output
golangci-lint run -v

# Показать, какие линтеры включены
golangci-lint linters
```

### Конфигурация .golangci.yml

Создайте файл `.golangci.yml` в корне проекта:

```yaml
# Версия конфигурации (для совместимости)
version: "2"

# Настройки запуска
run:
  # Таймаут (увеличьте для больших проектов)
  timeout: 5m

  # Код выхода при наличии issues
  issues-exit-code: 1

  # Проверять тесты
  tests: true

  # Build tags
  build-tags: []

  # Пропустить директории
  skip-dirs:
    - vendor
    - third_party
    - testdata
    - examples
    - .git

  # Пропустить файлы по паттерну
  skip-files:
    - ".*_mock\\.go$"
    - ".*_gen\\.go$"
    - ".*\\.pb\\.go$"

  # Режим загрузки модулей
  modules-download-mode: readonly

  # Разрешить параллельные запуски
  allow-parallel-runners: true

# Настройки вывода
output:
  # Формат: colored-line-number, tab, json, checkstyle, etc.
  formats:
    - format: colored-line-number

  # Печатать строки с ошибками
  print-issued-lines: true

  # Печатать имя линтера
  print-linter-name: true

  # Уникальные issues по строке
  uniq-by-line: true

  # Сортировать результаты
  sort-results: true

# Включенные линтеры
linters:
  # Отключить все по умолчанию
  disable-all: true

  # Включить конкретные
  enable:
    # Обязательные для production
    - errcheck      # Необработанные ошибки
    - gosimple      # Упрощение кода
    - govet         # Подозрительные конструкции
    - ineffassign   # Неэффективные присваивания
    - staticcheck   # Комплексный статический анализ
    - unused        # Неиспользуемый код

    # Рекомендуемые
    - bodyclose     # Незакрытые http.Response.Body
    - dupl          # Дублирование кода
    - errorlint     # Проверка работы с ошибками (Go 1.13+)
    - funlen        # Длина функций
    - gocognit      # Когнитивная сложность
    - goconst       # Повторяющиеся строки → константы
    - gocritic      # Опытные советы
    - gocyclo       # Цикломатическая сложность
    - gofmt         # Форматирование
    - goimports     # Импорты
    - gosec         # Безопасность
    - misspell      # Опечатки
    - nakedret      # Naked returns в длинных функциях
    - nilerr        # nil error возвращается с non-nil значением
    - prealloc      # Pre-allocation slices
    - revive        # Замена golint
    - unconvert     # Ненужные преобразования типов
    - unparam       # Неиспользуемые параметры
    - whitespace    # Лишние пробелы

# Настройки конкретных линтеров
linters-settings:
  errcheck:
    # Проверять type assertions
    check-type-assertions: true
    # Проверять blank identifier
    check-blank: true

  govet:
    # Включить shadow проверку
    enable:
      - shadow

  gocyclo:
    # Максимальная цикломатическая сложность
    min-complexity: 15

  gocognit:
    # Максимальная когнитивная сложность
    min-complexity: 20

  dupl:
    # Минимальное количество строк для дубликата
    threshold: 100

  funlen:
    # Максимальная длина функции
    lines: 100
    # Максимальное количество statements
    statements: 50

  goconst:
    # Минимальная длина строки
    min-len: 3
    # Минимальное количество вхождений
    min-occurrences: 3

  gocritic:
    # Включить все проверки
    enabled-tags:
      - diagnostic
      - style
      - performance
      - experimental
      - opinionated

  gosec:
    # Исключить определённые правила
    excludes:
      - G104  # Audit errors not checked (errcheck делает это лучше)

  revive:
    # Правила revive
    rules:
      - name: blank-imports
      - name: context-as-argument
      - name: context-keys-type
      - name: dot-imports
      - name: error-return
      - name: error-strings
      - name: error-naming
      - name: exported
      - name: if-return
      - name: increment-decrement
      - name: var-naming
      - name: var-declaration
      - name: package-comments
      - name: range
      - name: receiver-naming
      - name: time-naming
      - name: unexported-return
      - name: indent-error-flow
      - name: errorf
      - name: empty-block
      - name: superfluous-else
      - name: unreachable-code

  misspell:
    # Локаль (US или UK)
    locale: US

  nakedret:
    # Максимальная длина функции с naked return
    max-func-lines: 30

  prealloc:
    # Только simple loops
    simple: true
    # Проверять range loops
    range-loops: true
    # Проверять for loops
    for-loops: false

# Управление issues
issues:
  # Исключить по тексту
  exclude:
    # EXC0001 - errcheck: Almost all programs ignore errors on these functions
    - "Error return value of .((os\\.)?std(out|err)\\..*|.*Close|.*Flush|os\\.Remove(All)?|.*print(f|ln)?|os\\.(Un)?Setenv). is not checked"

  # Правила исключений
  exclude-rules:
    # Для тестов: разрешить больше
    - path: _test\.go
      linters:
        - errcheck
        - dupl
        - funlen
        - gocognit
        - gosec

    # Для main.go: разрешить длинные функции
    - path: main\.go
      linters:
        - funlen

    # Для generated кода: отключить всё
    - path: ".*_gen\\.go"
      linters:
        - all

    # Для proto: отключить всё
    - path: ".*\\.pb\\.go"
      linters:
        - all

    # Для wire: отключить
    - path: wire_gen\.go
      linters:
        - all

  # Показывать все issues (не группировать)
  max-issues-per-linter: 0
  max-same-issues: 0

  # Новый код: показывать issues только в новых строках
  # (полезно при внедрении в существующий проект)
  # new: true
  # new-from-rev: HEAD~1

# Severity (для интеграции с IDE)
severity:
  default-severity: error
  rules:
    - linters:
        - dupl
      severity: warning
    - linters:
        - goconst
      severity: warning
```

### Обязательные линтеры для production

| Линтер | Что проверяет | C# аналог | Пример ошибки |
|--------|---------------|-----------|---------------|
| **errcheck** | Необработанные ошибки | CA2000, CA1031 | `f.Close()` без проверки error |
| **staticcheck** | Комплексный анализ | Roslyn Analyzers | Deprecated API, dead code |
| **unused** | Неиспользуемый код | IDE0051, IDE0052 | Неиспользуемые функции/переменные |
| **gosimple** | Упрощение кода | IDE0003, IDE0004 | `if err != nil { return err }` в конце функции |
| **govet** | Подозрительные конструкции | Встроен в Roslyn | Printf с неправильными аргументами |
| **ineffassign** | Неэффективные присваивания | IDE0059 | `x := 1; x = 2` (первое присваивание не нужно) |

**Минимальная production конфигурация:**
```yaml
linters:
  enable:
    - errcheck
    - gosimple
    - govet
    - ineffassign
    - staticcheck
    - unused
```

### Дополнительные рекомендуемые линтеры

#### Для качества кода

| Линтер | Назначение | Настройка |
|--------|------------|-----------|
| **revive** | Замена golint, гибче | Много правил |
| **gocyclo** | Цикломатическая сложность | `min-complexity: 15` |
| **gocognit** | Когнитивная сложность | `min-complexity: 20` |
| **dupl** | Дублирование кода | `threshold: 100` |
| **funlen** | Длина функций | `lines: 100` |
| **goconst** | Магические строки | `min-len: 3, min-occurrences: 3` |
| **gocritic** | Опытные советы | `enabled-tags: all` |

#### Для безопасности

| Линтер | Назначение |
|--------|------------|
| **gosec** | Security issues (SQL injection, hardcoded credentials) |
| **bodyclose** | Незакрытые `http.Response.Body` |
| **nilerr** | `return nil, nil` когда должен быть error |
| **sqlclosecheck** | Незакрытые `sql.Rows` |

#### Для производительности

| Линтер | Назначение |
|--------|------------|
| **prealloc** | Pre-allocation slices в циклах |
| **unconvert** | Ненужные преобразования типов |

### Исключения и настройка severity

**Исключения для тестов:**
```yaml
issues:
  exclude-rules:
    - path: _test\.go
      linters:
        - errcheck    # В тестах часто игнорируют ошибки
        - dupl        # Тесты могут повторяться
        - funlen      # Тесты могут быть длинными
        - gosec       # Security не критична в тестах
```

**Исключение конкретной ошибки:**
```yaml
issues:
  exclude-rules:
    - linters:
        - staticcheck
      text: "SA1019:"  # Игнорировать deprecated warnings
```

**Директивы в коде:**
```go
// Отключить для строки
result, _ := SomeFunc() //nolint:errcheck

// Отключить для строки с причиной
result, _ := SomeFunc() //nolint:errcheck // error handled elsewhere

// Отключить для блока
//nolint:gocyclo
func complexFunction() {
    // ...
}

// Отключить несколько линтеров
//nolint:errcheck,gosec
```

> ⚠️ **Важно**: Используйте `//nolint` осторожно. Каждое использование должно быть обосновано.

---

## staticcheck — глубокий статический анализ

staticcheck — один из самых мощных статических анализаторов для Go, разработанный Dominik Honnef. Он включён в golangci-lint, но может использоваться и отдельно.

### Категории проверок

| Категория | Prefix | Описание | Количество |
|-----------|--------|----------|------------|
| **SA** | SA1xxx-SA9xxx | Статический анализ (основной) | ~90 проверок |
| **S** | S1xxx | Упрощения кода (simplifications) | ~40 проверок |
| **ST** | ST1xxx | Стилистические проверки | ~20 проверок |
| **QF** | QF1xxx | Quick fixes (автоисправления) | ~15 проверок |

### Важные проверки

**SA (Статический анализ) — критические:**

```go
// SA1019: Using deprecated API
import "io/ioutil"  // Deprecated в Go 1.16
data, _ := ioutil.ReadFile("file.txt")
// Исправление: использовать os.ReadFile

// SA4006: Value assigned but never used
x := 1
x = 2  // x = 1 никогда не используется
fmt.Println(x)

// SA5001: Inefficient use of time.After in select
for {
    select {
    case <-time.After(time.Second): // Создаёт новый timer каждую итерацию!
        // ...
    }
}
// Исправление: использовать time.NewTimer + Reset

// SA9003: Empty branch
if condition {
    // Пустая ветка — подозрительно
}

// SA4017: Pure function with unused return
strings.ToLower(s) // Результат не используется!
```

**S (Упрощения) — улучшают читаемость:**

```go
// S1000: Use plain channel send/receive
select {
case x := <-ch:
    return x
}
// Упрощение:
return <-ch

// S1002: Omit comparison to bool
if b == true {  // Лишнее сравнение
    // ...
}
// Упрощение:
if b {
    // ...
}

// S1009: Omit redundant nil check
if x != nil && len(x) > 0 {  // len(nil slice) = 0, проверка не нужна
    // ...
}
// Упрощение:
if len(x) > 0 {
    // ...
}
```

**ST (Стиль) — соглашения Go:**

```go
// ST1003: Poorly chosen identifier
const MAX_VALUE = 100  // В Go используют camelCase
// Исправление:
const maxValue = 100

// ST1005: Error strings should not be capitalized
return errors.New("User not found")  // Неправильно
// Исправление:
return errors.New("user not found")

// ST1006: Poorly chosen receiver name
func (this *User) GetName() string {  // "this" — не Go-way
    return this.Name
}
// Исправление:
func (u *User) GetName() string {
    return u.Name
}
```

### staticcheck в golangci-lint vs standalone

**В golangci-lint (рекомендуется):**
```yaml
# .golangci.yml
linters:
  enable:
    - staticcheck

linters-settings:
  staticcheck:
    # Включить все категории
    checks:
      - all
      # Исключить стилистические (опционально)
      # - "-ST1000"
```

**Standalone:**
```bash
# Установка
go install honnef.co/go/tools/cmd/staticcheck@latest

# Запуск
staticcheck ./...

# С конфигурацией
staticcheck -checks="all,-ST1000" ./...
```

**Конфигурация staticcheck.conf (для standalone):**
```toml
checks = ["all", "-ST1000", "-ST1003"]

[[analyzers]]
name = "SA1019"
enabled = false  # Отключить deprecated warnings
```

**Когда использовать standalone:**
- Нужны все возможности staticcheck (некоторые не доступны через golangci-lint)
- Отладка конкретных проверок
- В остальных случаях — golangci-lint удобнее

---

## govulncheck — проверка уязвимостей

govulncheck — официальный инструмент от Go team для проверки уязвимостей в зависимостях. В отличие от большинства аналогов, он анализирует **фактически используемый код**, а не просто список зависимостей.

### Как работает govulncheck

```
┌─────────────────────────────────────────────────────────────────┐
│                        govulncheck                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Читает go.mod и go.sum                                      │
│              ↓                                                   │
│  2. Строит call graph вашего кода                               │
│              ↓                                                   │
│  3. Проверяет против vuln.go.dev database                       │
│              ↓                                                   │
│  4. Показывает ТОЛЬКО уязвимости, которые реально используются  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Ключевое отличие от других инструментов:**

| Инструмент | Анализирует | False positives |
|------------|-------------|-----------------|
| Dependabot | Все зависимости | Много |
| `dotnet audit` | Все зависимости | Много |
| **govulncheck** | Только используемый код | Мало |

### Использование

```bash
# Установка
go install golang.org/x/vuln/cmd/govulncheck@latest

# Проверка исходного кода
govulncheck ./...

# JSON output (для CI/CD)
govulncheck -json ./... > vulns.json

# Проверка скомпилированного бинарника
govulncheck -mode=binary ./myapp

# Проверка конкретного модуля
govulncheck -C ./cmd/server ./...
```

**Пример вывода:**
```
Scanning your code and 47 packages across 12 dependent modules for known vulnerabilities...

Vulnerability #1: GO-2024-2687
    Incorrect forwarding of sensitive headers and cookies on HTTP redirect in net/http

    More info: https://pkg.go.dev/vuln/GO-2024-2687

    Module: stdlib
    Found in: stdlib@go1.21.0
    Fixed in: stdlib@go1.21.8

    Example call found:
      main.go:45:12: myapp.FetchData calls
        net/http.(*Client).Do, which eventually calls
        net/http.shouldCopyHeaderOnRedirect

Vulnerability #2: GO-2024-1234
    SQL injection in github.com/example/sqlutil

    Module: github.com/example/sqlutil
    Found in: github.com/example/sqlutil@v1.2.0
    Fixed in: github.com/example/sqlutil@v1.2.5

    Example call found:
      internal/db/queries.go:23:8: db.GetUser calls
        github.com/example/sqlutil.Query

Your code is affected by 2 vulnerabilities.
```

### Сравнение с C# инструментами

| Аспект | govulncheck | dotnet audit | Dependabot |
|--------|-------------|--------------|------------|
| **Анализ использования** | Да (call graph) | Нет | Нет |
| **False positives** | Минимум | Много | Много |
| **База уязвимостей** | vuln.go.dev | NuGet advisories | GitHub Advisory |
| **Официальный** | Да (Go team) | Да (Microsoft) | Да (GitHub) |
| **Автоматический fix** | Нет | Нет | Да (создаёт PR) |
| **CI/CD интеграция** | CLI, JSON output | CLI | GitHub native |

**Интеграция в CI/CD:**
```yaml
# GitHub Actions
- name: Check vulnerabilities
  run: |
    go install golang.org/x/vuln/cmd/govulncheck@latest
    govulncheck ./...
```

---

## go mod — управление зависимостями

go mod — встроенная система управления зависимостями в Go. В отличие от NuGet, она минималистична, но предоставляет мощные возможности для безопасности и воспроизводимости сборок.

### Основные команды

```bash
# Инициализация модуля
go mod init github.com/user/project

# Добавить/обновить зависимости, удалить неиспользуемые
go mod tidy

# Проверить целостность зависимостей
go mod verify
# all modules verified

# Скачать зависимости в кэш
go mod download

# Создать vendor директорию
go mod vendor

# Показать граф зависимостей
go mod graph

# Почему нужна зависимость?
go mod why -m github.com/some/module

# Редактировать go.mod программно
go mod edit -require github.com/some/module@v1.2.3
go mod edit -go=1.23

# Показать текущие зависимости
go list -m all

# Показать доступные версии модуля
go list -m -versions github.com/some/module
```

**Проверка в CI (go mod tidy):**
```bash
# Если есть изменения — кто-то забыл go mod tidy
go mod tidy
git diff --exit-code go.mod go.sum
```

**Анализ зависимостей:**
```bash
# Найти, кто тянет проблемную зависимость
go mod graph | grep "problematic-module"

# Найти все версии модуля в дереве
go mod graph | grep "github.com/some/module@"

# Визуализация (требует graphviz)
go mod graph | modgraphviz | dot -Tpng -o deps.png
```

### Private modules и GOPROXY

```bash
# Для приватных репозиториев — не использовать proxy
export GOPRIVATE=github.com/mycompany/*,gitlab.mycompany.com/*

# Не проверять checksum для приватных модулей
export GONOSUMDB=github.com/mycompany/*

# Приватный proxy (для enterprise)
export GOPROXY=https://proxy.mycompany.com,https://proxy.golang.org,direct

# Отключить proxy полностью (не рекомендуется)
export GOPROXY=direct
```

**Git credentials для приватных репозиториев:**
```bash
# .gitconfig
[url "git@github.com:"]
    insteadOf = https://github.com/

# Или через HTTPS с токеном
git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"
```

### Сравнение с NuGet

| Аспект | go mod | NuGet |
|--------|--------|-------|
| **Lock file** | go.sum (checksums) | packages.lock.json |
| **Manifest** | go.mod | .csproj / Directory.Packages.props |
| **Версионирование** | MVS (Minimal Version Selection) | NuGet resolver (newest) |
| **Private feed** | GOPRIVATE / GOPROXY | NuGet.config |
| **Централизация** | go.work (workspaces) | Directory.Packages.props |
| **Vendoring** | `go mod vendor` | Нет встроенного |
| **Checksum DB** | sum.golang.org | Нет |
| **Кэш** | `$GOPATH/pkg/mod` | `~/.nuget/packages` |

**MVS vs NuGet resolver:**

```
Зависимости:
  A → B v1.1
  A → C
  C → B v1.2

NuGet (newest wins):
  B v1.2 (берёт новейшую)

Go MVS (minimal version):
  B v1.2 (минимальная, удовлетворяющая всем требованиям)
```

MVS гарантирует воспроизводимость: одинаковые go.mod → одинаковые версии.

---

## air — hot reload для разработки

air — инструмент для автоматической перезагрузки Go-приложения при изменении файлов. Аналог `dotnet watch run` для C#.

> 💡 Базовая настройка air описана в [разделе 4.7](../part4-infrastructure/07_containerization.md). Здесь — продвинутая конфигурация.

### Конфигурация

**Установка:**
```bash
go install github.com/air-verse/air@latest
```

**Полная конфигурация .air.toml:**
```toml
# Корневая директория проекта
root = "."
# Директория для временных файлов
tmp_dir = "tmp"

[build]
  # Команда сборки с флагами отладки
  cmd = "go build -gcflags='all=-N -l' -o ./tmp/main ./cmd/server"
  # Путь к бинарнику
  bin = "./tmp/main"
  # Аргументы при запуске
  args_bin = ["-config", "./config/local.yaml"]
  # Перед сборкой
  pre_cmd = []
  # После сборки
  post_cmd = []
  # Задержка перед сборкой (мс)
  delay = 500
  # Остановить при ошибке сборки
  stop_on_error = true
  # Логировать ошибки сборки
  log = "build-errors.log"
  # Отправить interrupt сигнал (для graceful shutdown)
  send_interrupt = true
  # Задержка перед kill (мс)
  kill_delay = 500
  # Перезапускать при ошибке
  rerun = false
  # Задержка перезапуска при ошибке (мс)
  rerun_delay = 500

  # Исключить директории
  exclude_dir = [
    "assets",
    "tmp",
    "vendor",
    "testdata",
    "node_modules",
    ".git",
    ".idea",
    ".vscode",
  ]

  # Исключить файлы по regex
  exclude_regex = [
    "_test\\.go$",
    "_mock\\.go$",
    "\\.pb\\.go$",
  ]

  # Включить только эти директории (пусто = все)
  include_dir = []

  # Расширения для отслеживания
  include_ext = ["go", "yaml", "yml", "toml", "json", "html", "tmpl", "tpl"]

  # Исключить файлы без изменений
  exclude_unchanged = true

  # Следить за символическими ссылками
  follow_symlink = false

[log]
  # Показывать время
  time = true
  # Показывать только main output
  main_only = false

[color]
  main = "magenta"
  watcher = "cyan"
  build = "yellow"
  runner = "green"

[misc]
  # Очистить tmp при выходе
  clean_on_exit = true

[screen]
  # Очищать экран при перезагрузке
  clear_on_rebuild = true
  # Оставить scroll history
  keep_scroll = true
```

**Запуск:**
```bash
# С конфигурацией
air -c .air.toml

# Или просто (ищет .air.toml автоматически)
air
```

### Интеграция с Docker

**Dockerfile.dev:**
```dockerfile
FROM golang:1.23-alpine

WORKDIR /app

# Установить air
RUN go install github.com/air-verse/air@latest

# Копировать go.mod для кэширования зависимостей
COPY go.mod go.sum ./
RUN go mod download

# Не копируем код — он будет в volume

CMD ["air", "-c", ".air.toml"]
```

**docker-compose.yml:**
```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      # Код проекта
      - .:/app
      # Кэш Go modules (для скорости)
      - go-mod-cache:/go/pkg/mod
      # Кэш сборки
      - go-build-cache:/root/.cache/go-build
    ports:
      - "8080:8080"
    environment:
      - ENV=development
    # Graceful shutdown
    stop_grace_period: 5s

volumes:
  go-mod-cache:
  go-build-cache:
```

### Сравнение с dotnet watch

| Аспект | air | dotnet watch |
|--------|-----|--------------|
| **Установка** | `go install` | Встроен в SDK |
| **Конфигурация** | `.air.toml` | `launchSettings.json` |
| **Механизм** | Перезапуск процесса | Hot reload (runtime patching) |
| **Скорость** | 1-5 секунд (компиляция) | Мгновенно (patching) |
| **Отладка** | Delve attachment | Встроен |
| **Docker** | Требует настройки | Работает из коробки |

> 💡 **Почему Go перекомпилирует?** Go компилируется очень быстро (секунды), поэтому hot reload на уровне runtime не нужен. Перекомпиляция гарантирует, что код всегда актуален.

---

## Дополнительные инструменты

### gofumpt — строгое форматирование

gofumpt — форк gofmt с более строгими правилами форматирования.

```bash
# Установка
go install mvdan.cc/gofumpt@latest

# Форматирование
gofumpt -l -w .

# Проверка без изменений
gofumpt -d .
```

**Отличия от gofmt:**
```go
// gofmt (допустимо):
func foo() {

    x := 1

}

// gofumpt (убирает лишние пустые строки):
func foo() {
    x := 1
}
```

**Интеграция с golangci-lint:**
```yaml
linters:
  enable:
    - gofumpt

linters-settings:
  gofumpt:
    extra-rules: true
```

### goimports — автоимпорты

goimports добавляет отсутствующие импорты и удаляет неиспользуемые.

```bash
# Установка
go install golang.org/x/tools/cmd/goimports@latest

# Форматирование + импорты
goimports -w .

# С группировкой локальных импортов
goimports -local github.com/mycompany -w .
```

**Группировка импортов:**
```go
import (
    // Стандартная библиотека
    "context"
    "fmt"
    "net/http"

    // Внешние зависимости
    "github.com/gin-gonic/gin"
    "go.uber.org/zap"

    // Локальные пакеты (отделены blank line)
    "github.com/mycompany/myproject/internal/config"
    "github.com/mycompany/myproject/pkg/utils"
)
```

### go generate

go generate запускает команды, указанные в специальных комментариях.

```go
// В начале файла или перед типом
//go:generate stringer -type=Status
//go:generate mockgen -source=service.go -destination=mocks/service_mock.go
//go:generate sqlc generate

type Status int

const (
    StatusPending Status = iota
    StatusActive
    StatusCompleted
)
```

**Запуск:**
```bash
# Все go:generate в проекте
go generate ./...

# В конкретной директории
go generate ./internal/...

# С verbose output
go generate -v ./...
```

**Популярные генераторы:**
| Инструмент | Назначение |
|------------|------------|
| `stringer` | Метод `String()` для enum |
| `mockgen` | Моки для тестирования |
| `sqlc` | Типобезопасные SQL-запросы |
| `oapi-codegen` | Код из OpenAPI spec |
| `protoc` | Код из .proto файлов |

### wire — compile-time DI

wire — инструмент для dependency injection на этапе компиляции от Google.

```bash
# Установка
go install github.com/google/wire/cmd/wire@latest
```

**Определение провайдеров:**
```go
// providers.go
package main

func NewConfig() *Config {
    return &Config{...}
}

func NewDatabase(cfg *Config) (*Database, error) {
    return sql.Open("postgres", cfg.DatabaseURL)
}

func NewUserRepository(db *Database) *UserRepository {
    return &UserRepository{db: db}
}

func NewUserService(repo *UserRepository) *UserService {
    return &UserService{repo: repo}
}

func NewApp(svc *UserService) *App {
    return &App{userService: svc}
}
```

**wire.go (build tag wireinject):**
```go
//go:build wireinject
// +build wireinject

package main

import "github.com/google/wire"

func InitializeApp() (*App, error) {
    wire.Build(
        NewConfig,
        NewDatabase,
        NewUserRepository,
        NewUserService,
        NewApp,
    )
    return nil, nil
}
```

**Генерация:**
```bash
wire ./...
# Создаёт wire_gen.go
```

**Сгенерированный wire_gen.go:**
```go
// Code generated by Wire. DO NOT EDIT.

package main

func InitializeApp() (*App, error) {
    config := NewConfig()
    database, err := NewDatabase(config)
    if err != nil {
        return nil, err
    }
    userRepository := NewUserRepository(database)
    userService := NewUserService(userRepository)
    app := NewApp(userService)
    return app, nil
}
```

**Сравнение с Microsoft.Extensions.DI:**

| Аспект | wire | Microsoft.Extensions.DI |
|--------|------|------------------------|
| **Время** | Compile-time | Runtime |
| **Ошибки** | При компиляции | При запуске |
| **Performance** | Нет overhead | Reflection overhead |
| **Сложность** | Простой | Feature-rich (scopes, lifetimes) |
| **Debugging** | Сгенерированный код читаем | Stack trace через DI |

### go fix — автоматические миграции кода (Go 1.26)

> 💡 **Для C# разработчиков**: Аналог `dotnet-upgrade-assistant` или Roslyn code fixes, но встроенный в инструментарий Go.

`go fix` теперь поддерживает автоматические миграции кода на основе `go/analysis`. В Go 1.26 команда получила набор встроенных «модернизаторов» и директиву для библиотек.

#### Встроенные модернизаторы Go 1.26

```bash
# Применить все доступные fix-ы к пакету
go fix ./...

# Применить конкретный fix
go fix -fix=stdversion ./...

# Посмотреть доступные fix-ы
go fix -list
```

**Что умеет `go fix` в 1.26:**
- Автоматически обновляет использование устаревших API на актуальные альтернативы
- Заменяет deprecated функции в стандартной библиотеке
- Адаптирует код к изменениям в языке (например, новые constraints в generics)

#### Директива `//go:fix inline` для библиотек

Библиотеки теперь могут помечать устаревшие функции для автоматической замены:

```go
// Старый API (deprecated)
//
// Deprecated: используйте NewClientV2.
//go:fix inline
func NewClient(addr string) *Client {
    return NewClientV2(addr, DefaultOptions())
}

// Новый API
func NewClientV2(addr string, opts Options) *Client {
    return &Client{addr: addr, opts: opts}
}
```

После `go fix ./...` все вызовы `NewClient("localhost")` автоматически заменятся на `NewClientV2("localhost", DefaultOptions())`.

#### Сравнение с C#

| Аспект | C# (Roslyn / dotnet-upgrade-assistant) | Go (go fix) |
|--------|----------------------------------------|-------------|
| **Механизм** | Roslyn analyzer + code fix | go/analysis + built-in fixes |
| **Запуск** | IDE или CLI | `go fix ./...` |
| **Для библиотек** | `[Obsolete]` + diagnostic | `//go:fix inline` directive |
| **Проверка CI** | `dotnet format --verify-no-changes` | `go fix -list` + diff |

```bash
# CI: проверить что fix-ы применены
git diff --exit-code  # после go fix ./... не должно быть изменений
```

---

## Интеграция в IDE

### VS Code

**Установка Go extension:**
1. Extensions → Go (golang.go)
2. Cmd+Shift+P → Go: Install/Update Tools → выбрать все

**settings.json для проекта (.vscode/settings.json):**
```json
{
  // Использовать gopls
  "go.useLanguageServer": true,

  // Линтер
  "go.lintTool": "golangci-lint",
  "go.lintFlags": ["--fast", "--config", ".golangci.yml"],
  "go.lintOnSave": "workspace",

  // Форматирование
  "go.formatTool": "gofumpt",

  // Тесты
  "go.testFlags": ["-v", "-race"],
  "go.coverOnSave": true,
  "go.coverageDecorator": {
    "type": "gutter"
  },

  // gopls настройки
  "gopls": {
    "ui.semanticTokens": true,
    "ui.completion.usePlaceholders": true,
    "analyses": {
      "unusedparams": true,
      "shadow": true,
      "fieldalignment": true,
      "nilness": true,
      "unusedwrite": true
    },
    "staticcheck": true,
    "gofumpt": true
  },

  // Автоформатирование при сохранении
  "[go]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    },
    "editor.suggest.snippetsPreventQuickSuggestions": false
  },

  "[go.mod]": {
    "editor.formatOnSave": true
  }
}
```

**extensions.json (рекомендуемые расширения):**
```json
{
  "recommendations": [
    "golang.go",
    "zxh404.vscode-proto3",
    "redhat.vscode-yaml",
    "tamasfe.even-better-toml"
  ]
}
```

### GoLand

GoLand имеет встроенную поддержку Go инструментов:

1. **Settings → Go → Go Modules** — включить support
2. **Settings → Tools → File Watchers** — добавить gofumpt
3. **Settings → Editor → Inspections** — настроить проверки
4. **Settings → Tools → golangci-lint** — указать путь к конфигурации

**File Watcher для gofumpt:**
- Name: gofumpt
- File type: Go files
- Program: `$GOPATH$/bin/gofumpt` (или путь к gofumpt)
- Arguments: `-w $FilePath$`
- Output paths to refresh: `$FilePath$`

### Настройка для команды

**Структура конфигурационных файлов:**
```
project/
├── .vscode/
│   ├── settings.json      # VS Code настройки
│   └── extensions.json    # Рекомендуемые расширения
├── .editorconfig          # Общие настройки редактора
├── .golangci.yml          # Конфигурация линтера
├── .air.toml              # Hot reload
└── Makefile               # Команды сборки
```

**.editorconfig:**
```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = tab

[*.go]
indent_size = 4

[*.{yaml,yml,json,toml}]
indent_style = space
indent_size = 2

[Makefile]
indent_style = tab
```

---

## CI/CD Pipeline

### GitHub Actions

**Полный workflow (.github/workflows/ci.yml):**
```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  GO_VERSION: '1.23'

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: ${{ env.GO_VERSION }}
          cache: true

      - name: golangci-lint
        uses: golangci/golangci-lint-action@v6
        with:
          version: latest
          args: --timeout=5m

  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: ${{ env.GO_VERSION }}
          cache: true

      - name: Run tests
        run: go test -race -coverprofile=coverage.out -covermode=atomic ./...

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage.out
          fail_ci_if_error: true

  security:
    name: Security
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: ${{ env.GO_VERSION }}
          cache: true

      - name: govulncheck
        run: |
          go install golang.org/x/vuln/cmd/govulncheck@latest
          govulncheck ./...

      - name: gosec
        uses: securego/gosec@master
        with:
          args: -no-fail -fmt sarif -out results.sarif ./...

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif

  build:
    name: Build
    needs: [lint, test, security]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: ${{ env.GO_VERSION }}
          cache: true

      - name: Build
        run: go build -v ./...

      - name: Verify go.mod is tidy
        run: |
          go mod tidy
          git diff --exit-code go.mod go.sum
```

### GitLab CI

**.gitlab-ci.yml:**
```yaml
stages:
  - lint
  - test
  - security
  - build

variables:
  GO_VERSION: "1.23"

.go-cache: &go-cache
  variables:
    GOPATH: $CI_PROJECT_DIR/.go
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - .go/pkg/mod/

lint:
  stage: lint
  image: golangci/golangci-lint:latest
  <<: *go-cache
  script:
    - golangci-lint run --timeout=5m
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == "main"

test:
  stage: test
  image: golang:${GO_VERSION}
  <<: *go-cache
  script:
    - go test -race -coverprofile=coverage.out ./...
    - go tool cover -func=coverage.out
  coverage: '/total:\s+\(statements\)\s+(\d+.\d+)%/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == "main"

security:
  stage: security
  image: golang:${GO_VERSION}
  <<: *go-cache
  script:
    - go install golang.org/x/vuln/cmd/govulncheck@latest
    - govulncheck ./...
  allow_failure: true
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == "main"

build:
  stage: build
  image: golang:${GO_VERSION}
  <<: *go-cache
  script:
    - go build -v ./...
    - go mod tidy
    - git diff --exit-code go.mod go.sum
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == "main"
```

### Pre-commit hooks

**.pre-commit-config.yaml:**
```yaml
repos:
  - repo: local
    hooks:
      - id: go-fmt
        name: go fmt
        entry: gofmt -l -w
        language: system
        types: [go]

      - id: gofumpt
        name: gofumpt
        entry: gofumpt -l -w
        language: system
        types: [go]

      - id: go-vet
        name: go vet
        entry: go vet
        language: system
        types: [go]
        pass_filenames: false

      - id: golangci-lint
        name: golangci-lint
        entry: golangci-lint run --fix
        language: system
        types: [go]
        pass_filenames: false

      - id: go-mod-tidy
        name: go mod tidy
        entry: go mod tidy
        language: system
        pass_filenames: false

      - id: go-mod-verify
        name: go mod verify
        entry: go mod verify
        language: system
        pass_filenames: false
```

**Установка:**
```bash
# Установить pre-commit
pip install pre-commit
# или
brew install pre-commit

# Установить hooks
pre-commit install

# Запустить вручную
pre-commit run --all-files
```

---

## Практические примеры

### Пример 1: Production-ready .golangci.yml

<details>
<summary>Полная конфигурация (раскрыть)</summary>

```yaml
# .golangci.yml
# Production-ready конфигурация для Go 1.23+
# Версия: 2.0

version: "2"

run:
  timeout: 5m
  issues-exit-code: 1
  tests: true

  skip-dirs:
    - vendor
    - third_party
    - testdata
    - examples
    - .git

  skip-files:
    - ".*_mock\\.go$"
    - ".*_gen\\.go$"
    - ".*\\.pb\\.go$"
    - "wire_gen\\.go$"

  modules-download-mode: readonly
  allow-parallel-runners: true

output:
  formats:
    - format: colored-line-number
  print-issued-lines: true
  print-linter-name: true
  uniq-by-line: true
  sort-results: true

linters:
  disable-all: true
  enable:
    # Tier 1: Обязательные (ошибки = блокер)
    - errcheck
    - gosimple
    - govet
    - ineffassign
    - staticcheck
    - unused

    # Tier 2: Безопасность
    - bodyclose
    - gosec
    - nilerr
    - sqlclosecheck

    # Tier 3: Качество кода
    - dupl
    - errorlint
    - funlen
    - gocognit
    - goconst
    - gocritic
    - gocyclo
    - nakedret
    - prealloc
    - revive
    - unconvert
    - unparam

    # Tier 4: Форматирование
    - gofmt
    - gofumpt
    - goimports
    - misspell
    - whitespace

linters-settings:
  errcheck:
    check-type-assertions: true
    check-blank: true
    exclude-functions:
      - (io.Closer).Close
      - (net/http.ResponseWriter).Write

  govet:
    enable:
      - shadow
      - fieldalignment

  staticcheck:
    checks:
      - all

  gocyclo:
    min-complexity: 15

  gocognit:
    min-complexity: 20

  dupl:
    threshold: 100

  funlen:
    lines: 100
    statements: 50

  goconst:
    min-len: 3
    min-occurrences: 3
    ignore-tests: true

  gocritic:
    enabled-tags:
      - diagnostic
      - style
      - performance
      - experimental
      - opinionated
    disabled-checks:
      - whyNoLint
      - hugeParam

  gosec:
    excludes:
      - G104
    config:
      G301: "0750"
      G302: "0600"
      G306: "0600"

  revive:
    enable-all-rules: false
    rules:
      - name: blank-imports
      - name: context-as-argument
      - name: context-keys-type
      - name: dot-imports
      - name: error-return
      - name: error-strings
      - name: error-naming
      - name: exported
      - name: if-return
      - name: increment-decrement
      - name: var-naming
      - name: var-declaration
      - name: package-comments
      - name: range
      - name: receiver-naming
      - name: time-naming
      - name: unexported-return
      - name: indent-error-flow
      - name: errorf
      - name: empty-block
      - name: superfluous-else
      - name: unreachable-code

  misspell:
    locale: US

  nakedret:
    max-func-lines: 30

  prealloc:
    simple: true
    range-loops: true
    for-loops: false

  gofumpt:
    extra-rules: true

  goimports:
    local-prefixes: github.com/mycompany

issues:
  exclude:
    - "Error return value of .((os\\.)?std(out|err)\\..*|.*Close|.*Flush|os\\.Remove(All)?|.*print(f|ln)?|os\\.(Un)?Setenv). is not checked"

  exclude-rules:
    # Тесты: разрешить больше
    - path: _test\.go
      linters:
        - errcheck
        - dupl
        - funlen
        - gocognit
        - gocyclo
        - gosec
        - goconst

    # main.go: разрешить длинные функции
    - path: main\.go
      linters:
        - funlen

    # Generated код: отключить всё
    - path: ".*_gen\\.go"
      linters:
        - all

    # Proto: отключить всё
    - path: ".*\\.pb\\.go"
      linters:
        - all

    # Wire: отключить
    - path: wire_gen\.go
      linters:
        - all

    # Migrations: отключить
    - path: "migrations/"
      linters:
        - all

  max-issues-per-linter: 0
  max-same-issues: 0

severity:
  default-severity: error
  rules:
    - linters:
        - dupl
        - goconst
      severity: warning
```

</details>

### Пример 2: CI/CD Pipeline

<details>
<summary>GitHub Actions с matrix builds (раскрыть)</summary>

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  GO_VERSION_STABLE: '1.23'

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: ${{ env.GO_VERSION_STABLE }}
          cache: true

      - name: golangci-lint
        uses: golangci/golangci-lint-action@v6
        with:
          version: latest
          args: --timeout=5m --config=.golangci.yml

  test:
    name: Test (Go ${{ matrix.go-version }})
    runs-on: ubuntu-latest
    strategy:
      matrix:
        go-version: ['1.22', '1.23']

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: ${{ matrix.go-version }}
          cache: true

      - name: Run tests
        run: |
          go test -race -coverprofile=coverage.out -covermode=atomic ./...
        env:
          DATABASE_URL: postgres://test:test@localhost:5432/test?sslmode=disable

      - name: Upload coverage
        if: matrix.go-version == env.GO_VERSION_STABLE
        uses: codecov/codecov-action@v4
        with:
          files: coverage.out
          fail_ci_if_error: true

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: ${{ env.GO_VERSION_STABLE }}
          cache: true

      - name: govulncheck
        run: |
          go install golang.org/x/vuln/cmd/govulncheck@latest
          govulncheck ./...

      - name: gosec
        uses: securego/gosec@master
        with:
          args: -no-fail -fmt sarif -out results.sarif ./...

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: results.sarif

  build:
    name: Build
    needs: [lint, test, security]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: ${{ env.GO_VERSION_STABLE }}
          cache: true

      - name: Verify dependencies
        run: |
          go mod tidy
          go mod verify
          git diff --exit-code go.mod go.sum

      - name: Build
        run: |
          CGO_ENABLED=0 go build -ldflags="-s -w" -o bin/app ./cmd/server

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: app
          path: bin/app
```

</details>

### Пример 3: Makefile для Go проекта

<details>
<summary>Полный Makefile (раскрыть)</summary>

```makefile
# Makefile для Go проекта
# Использование: make [target]

.PHONY: all build test lint fmt vet vuln clean run dev help install-tools

# ============================================================================
# VARIABLES
# ============================================================================

# Имя приложения
BINARY_NAME := myapp
# Путь к main пакету
MAIN_PACKAGE := ./cmd/server
# Go команда
GO := go
# golangci-lint
GOLANGCI_LINT := golangci-lint

# Build info
VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
BUILD_TIME := $(shell date -u '+%Y-%m-%d_%H:%M:%S')

# Ldflags для injection версии
LDFLAGS := -ldflags "-s -w \
	-X main.Version=$(VERSION) \
	-X main.Commit=$(COMMIT) \
	-X main.BuildTime=$(BUILD_TIME)"

# ============================================================================
# TARGETS
# ============================================================================

## help: Показать эту справку
help:
	@echo "Использование: make [target]"
	@echo ""
	@echo "Targets:"
	@sed -n 's/^##//p' $(MAKEFILE_LIST) | column -t -s ':' | sed -e 's/^/ /'

## all: Запустить все проверки и собрать
all: fmt vet lint test build

# ----------------------------------------------------------------------------
# BUILD
# ----------------------------------------------------------------------------

## build: Собрать бинарник
build:
	CGO_ENABLED=0 $(GO) build $(LDFLAGS) -o bin/$(BINARY_NAME) $(MAIN_PACKAGE)

## build-linux: Собрать для Linux
build-linux:
	GOOS=linux GOARCH=amd64 CGO_ENABLED=0 $(GO) build $(LDFLAGS) -o bin/$(BINARY_NAME)-linux-amd64 $(MAIN_PACKAGE)

## build-darwin: Собрать для macOS
build-darwin:
	GOOS=darwin GOARCH=arm64 CGO_ENABLED=0 $(GO) build $(LDFLAGS) -o bin/$(BINARY_NAME)-darwin-arm64 $(MAIN_PACKAGE)

## build-all: Собрать для всех платформ
build-all: build-linux build-darwin

# ----------------------------------------------------------------------------
# RUN
# ----------------------------------------------------------------------------

## run: Запустить приложение
run:
	$(GO) run $(MAIN_PACKAGE)

## dev: Запустить с hot reload (air)
dev:
	air -c .air.toml

# ----------------------------------------------------------------------------
# TEST
# ----------------------------------------------------------------------------

## test: Запустить тесты
test:
	$(GO) test -race -coverprofile=coverage.out ./...

## test-v: Запустить тесты с verbose output
test-v:
	$(GO) test -race -v -coverprofile=coverage.out ./...

## test-short: Запустить быстрые тесты
test-short:
	$(GO) test -short ./...

## coverage: Показать отчёт о покрытии
coverage: test
	$(GO) tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report: coverage.html"

## bench: Запустить бенчмарки
bench:
	$(GO) test -bench=. -benchmem ./...

# ----------------------------------------------------------------------------
# LINT
# ----------------------------------------------------------------------------

## lint: Запустить линтеры
lint:
	$(GOLANGCI_LINT) run --timeout=5m

## lint-fix: Запустить линтеры с автоисправлением
lint-fix:
	$(GOLANGCI_LINT) run --fix

## fmt: Отформатировать код
fmt:
	$(GO) fmt ./...
	gofumpt -l -w .

## vet: Запустить go vet
vet:
	$(GO) vet ./...

# ----------------------------------------------------------------------------
# SECURITY
# ----------------------------------------------------------------------------

## vuln: Проверить уязвимости
vuln:
	govulncheck ./...

## gosec: Запустить gosec
gosec:
	gosec -quiet ./...

# ----------------------------------------------------------------------------
# DEPENDENCIES
# ----------------------------------------------------------------------------

## tidy: Очистить зависимости
tidy:
	$(GO) mod tidy
	$(GO) mod verify

## deps: Скачать зависимости
deps:
	$(GO) mod download

## deps-update: Обновить зависимости
deps-update:
	$(GO) get -u ./...
	$(GO) mod tidy

# ----------------------------------------------------------------------------
# CODE GENERATION
# ----------------------------------------------------------------------------

## generate: Запустить go generate
generate:
	$(GO) generate ./...

## mocks: Сгенерировать моки
mocks:
	mockgen -source=internal/service/user.go -destination=internal/service/mocks/user_mock.go

# ----------------------------------------------------------------------------
# DOCKER
# ----------------------------------------------------------------------------

## docker-build: Собрать Docker образ
docker-build:
	docker build -t $(BINARY_NAME):$(VERSION) .

## docker-run: Запустить в Docker
docker-run:
	docker run --rm -p 8080:8080 $(BINARY_NAME):$(VERSION)

## docker-compose-up: Запустить docker-compose
docker-compose-up:
	docker-compose up -d

## docker-compose-down: Остановить docker-compose
docker-compose-down:
	docker-compose down

# ----------------------------------------------------------------------------
# CLEAN
# ----------------------------------------------------------------------------

## clean: Удалить артефакты сборки
clean:
	rm -rf bin/
	rm -rf tmp/
	rm -f coverage.out coverage.html

# ----------------------------------------------------------------------------
# TOOLS
# ----------------------------------------------------------------------------

## install-tools: Установить инструменты разработки
install-tools:
	$(GO) install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
	$(GO) install golang.org/x/vuln/cmd/govulncheck@latest
	$(GO) install mvdan.cc/gofumpt@latest
	$(GO) install github.com/air-verse/air@latest
	$(GO) install github.com/google/wire/cmd/wire@latest
	$(GO) install github.com/securego/gosec/v2/cmd/gosec@latest
	$(GO) install go.uber.org/mock/mockgen@latest

## check-tools: Проверить установленные инструменты
check-tools:
	@which golangci-lint > /dev/null || (echo "golangci-lint not found" && exit 1)
	@which govulncheck > /dev/null || (echo "govulncheck not found" && exit 1)
	@which gofumpt > /dev/null || (echo "gofumpt not found" && exit 1)
	@which air > /dev/null || (echo "air not found" && exit 1)
	@echo "All tools installed"

# ----------------------------------------------------------------------------
# CI
# ----------------------------------------------------------------------------

## ci: Запустить все CI проверки
ci: fmt vet lint test vuln build
	@echo "CI checks passed"

## ci-quick: Быстрые CI проверки (без vuln)
ci-quick: fmt vet lint test-short build
	@echo "Quick CI checks passed"
```

</details>

**Использование:**
```bash
# Показать справку
make help

# Полный CI цикл
make ci

# Разработка с hot reload
make dev

# Установить все инструменты
make install-tools
```

---
