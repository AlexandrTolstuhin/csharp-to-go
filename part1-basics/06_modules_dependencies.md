# Модули и управление зависимостями

---

## Введение

> 💡 **Для C# разработчиков**: В .NET управление зависимостями строится на NuGet — централизованном реестре пакетов. Файл `.csproj` описывает зависимости, `dotnet restore` скачивает их. В Go нет центрального реестра. Модули загружаются напрямую из Git-репозиториев по URL, версионирование привязано к Git-тегам, а прокси-серверы обеспечивают кеширование и доступность. Это принципиально другая модель, и она влияет на структуру проектов, версионирование и публикацию библиотек.

### Что вы узнаете

- Модульная система Go: `go.mod`, `go.sum` и их роль
- Семантическое версионирование и Major Version Suffix
- Управление зависимостями: `go get`, `go mod tidy`, `go mod vendor`
- Директивы `replace`, `retract`, `exclude`
- Workspace mode (`go work`) для мультимодульных проектов
- Приватные модули и `GOPRIVATE`
- Прокси и зеркала: `GOPROXY`, `GONOSUMCHECK`

---

## Сравнительная таблица: NuGet vs Go Modules

| Аспект | C# (NuGet) | Go (Modules) |
|--------|-----------|---------------|
| **Реестр** | nuget.org (централизованный) | Нет реестра, загрузка из VCS (GitHub, GitLab...) |
| **Файл зависимостей** | `.csproj` / `packages.config` | `go.mod` |
| **Lock-файл** | `packages.lock.json` (опциональный) | `go.sum` (обязательный) |
| **Установка** | `dotnet add package Foo` | `go get example.com/foo` |
| **Очистка** | `dotnet restore` | `go mod tidy` |
| **Vendoring** | Нет стандартного | `go mod vendor` |
| **Версионирование** | SemVer (мажорные ломают совместимость) | SemVer + Major Version Suffix в пути |
| **Публикация** | `dotnet nuget push` | `git tag v1.2.3 && git push --tags` |
| **Приватные пакеты** | NuGet feed + auth | `GOPRIVATE` + Git credentials |
| **Мультипроект** | `.sln` (solution) | `go.work` (workspace) |
| **Кеш** | `~/.nuget/packages` | `$GOPATH/pkg/mod` (по умолчанию `~/go/pkg/mod`) |

---

## go.mod: анатомия файла

```
module github.com/username/myapp

go 1.26

require (
    github.com/go-chi/chi/v5 v5.2.1
    github.com/jackc/pgx/v5 v5.7.4
    go.uber.org/zap v1.27.0
)

require (
    // indirect — транзитивные зависимости (зависимости зависимостей)
    github.com/jackc/pgpassfile v1.0.0 // indirect
    github.com/jackc/pgservicefile v0.0.0-20240725223059-51e0843b621d // indirect
    go.uber.org/multierr v1.11.0 // indirect
)
```

### Поля go.mod

| Поле | Описание | Аналог в C# |
|------|----------|-------------|
| `module` | Путь модуля (import path) | `<RootNamespace>` + `<PackageId>` |
| `go` | Минимальная версия Go | `<TargetFramework>` |
| `require` | Прямые зависимости | `<PackageReference>` |
| `require // indirect` | Транзитивные зависимости | Авто-resolved в NuGet |
| `replace` | Замена модуля (локальный путь или форк) | Нет прямого аналога |
| `exclude` | Исключение версии | Нет прямого аналога |
| `retract` | Пометка своей версии как отозванной | `dotnet nuget delete` (но не аналог) |

### Путь модуля: это важно

```
module github.com/username/myapp
```

Путь модуля — это **уникальный идентификатор** и одновременно **URL**, откуда Go будет скачивать код. В C# имя пакета и его расположение — разные вещи (пакет `Newtonsoft.Json` лежит на nuget.org). В Go — одно и то же.

```go
// Путь модуля определяет import path для всех пакетов внутри
import "github.com/username/myapp/internal/service"
//      ^^^^^^^^^^^^^^^^^^^^^^^^^ - путь модуля
//                                 ^^^^^^^^^^^^^^^^ - пакет внутри модуля
```

---

## go.sum: контрольные суммы

`go.sum` — файл с хешами всех зависимостей (прямых и транзитивных). Гарантирует, что при повторной загрузке код не изменился.

```
github.com/go-chi/chi/v5 v5.2.1 h1:KOIHODQj5PL...
github.com/go-chi/chi/v5 v5.2.1/go.mod h1:DslCQbL2O...
```

Каждая строка содержит:
- Путь модуля + версия
- Хеш содержимого (`h1:...` — SHA-256 в base64)

**Обязательно коммитить `go.sum` в Git** — это эквивалент lock-файла.

> 💡 **Для C# разработчиков**: в .NET `packages.lock.json` опционален и часто игнорируется. В Go `go.sum` генерируется автоматически и **обязателен** — без него сборка непредсказуема.

---

## Команды: ежедневная работа

### go get: добавление и обновление зависимостей

```bash
# Добавить зависимость (последняя версия)
go get github.com/go-chi/chi/v5

# Конкретная версия
go get github.com/go-chi/chi/v5@v5.2.1

# Последняя минорная версия
go get github.com/go-chi/chi/v5@v5

# Обновить до последнего патча
go get -u=patch github.com/go-chi/chi/v5

# Обновить зависимость и все транзитивные
go get -u github.com/go-chi/chi/v5

# Удалить зависимость
go get github.com/go-chi/chi/v5@none
```

**C# аналог**:
```bash
dotnet add package Newtonsoft.Json --version 13.0.1
dotnet remove package Newtonsoft.Json
```

### go mod tidy: очистка

```bash
# Добавляет недостающие и удаляет неиспользуемые зависимости
go mod tidy
```

Запускайте после каждого изменения import-ов. Аналог `dotnet restore`, но умнее — сам убирает мусор.

### go mod download: скачивание в кеш

```bash
# Скачать все зависимости в $GOPATH/pkg/mod
go mod download

# Полезно в Docker для кеширования слоя зависимостей
# (аналог dotnet restore в отдельном слое)
```

### go mod graph: дерево зависимостей

```bash
# Показать граф зависимостей
go mod graph

# Найти, кто тянет конкретную зависимость
go mod graph | grep pgx
```

**C# аналог**: `dotnet list package --include-transitive`

### go mod why: зачем нужна зависимость

```bash
# Показать цепочку зависимостей до модуля
go mod why github.com/jackc/pgpassfile
# github.com/username/myapp
# github.com/jackc/pgx/v5
# github.com/jackc/pgpassfile
```

---

## Семантическое версионирование (SemVer)

Go строго следует SemVer: `vMAJOR.MINOR.PATCH`

```
v1.2.3
│ │ └── PATCH: исправления багов, обратно совместимые
│ └──── MINOR: новая функциональность, обратно совместимая
└────── MAJOR: ломающие изменения
```

### Major Version Suffix: главное отличие от NuGet

В Go **мажорная версия >= 2 кодируется в пути модуля**:

```
// v0 и v1 — обычный путь
github.com/go-chi/chi          // v0.x.x или v1.x.x

// v2+ — суффикс /v2, /v3 и т.д.
github.com/go-chi/chi/v5       // v5.x.x
github.com/jackc/pgx/v5        // v5.x.x
```

Это означает, что **v1 и v5 — разные модули** и могут использоваться одновременно:

```go
import (
    chi_v1 "github.com/go-chi/chi"     // v1 (legacy)
    chi_v5 "github.com/go-chi/chi/v5"  // v5 (актуальная)
)
```

> 💡 **Для C# разработчиков**: в NuGet обновление с `Newtonsoft.Json 12.x` на `13.x` — просто смена версии в `.csproj`. В Go переход с `chi` на `chi/v5` — это **смена всех import path** в коде. Поэтому мажорные обновления в Go — более осознанное действие.

### Pre-release и псевдо-версии

```bash
# Pre-release тег
go get example.com/foo@v1.2.3-beta.1

# Псевдо-версия (конкретный коммит без тега)
go get example.com/foo@v0.0.0-20240101120000-abcdef123456
#                        │           │              │
#                        │           │              └── хеш коммита (12 символов)
#                        │           └── timestamp коммита (UTC)
#                        └── версия-заглушка

# По хешу коммита (Go сам сгенерирует псевдо-версию)
go get example.com/foo@abc1234
```

---

## Директива replace: локальная разработка и форки

### Работа с локальным модулем

```
// go.mod
module github.com/username/myapp

require github.com/username/mylib v1.2.3

// Подменяем на локальную копию для разработки
replace github.com/username/mylib => ../mylib
```

Локальный путь должен содержать `go.mod`.

**C# аналог**: `<ProjectReference>` вместо `<PackageReference>` — но в Go это не требует изменения кода, только `go.mod`.

### Использование форка

```
// Подменяем оригинальный модуль на свой форк
replace github.com/original/lib => github.com/myfork/lib v1.2.3-patched
```

Import path в коде **не меняется** — replace прозрачна для кода:

```go
import "github.com/original/lib" // код использует оригинальный путь
// но Go подставит github.com/myfork/lib при сборке
```

### Фиксация уязвимой версии транзитивной зависимости

```
// Транзитивная зависимость foo v1.2.3 содержит CVE
// Принудительно обновляем до v1.2.4
replace github.com/vulnerable/foo v1.2.3 => github.com/vulnerable/foo v1.2.4
```

> 💡 **Для C# разработчиков**: в NuGet аналог — `<PackageReference>` с `PrivateAssets` и ручная фиксация версии транзитивной зависимости. В Go — одна строка `replace`.

---

## Директива retract: отзыв своих версий

Если вы опубликовали сломанную версию своей библиотеки:

```
// go.mod вашей библиотеки
module github.com/username/mylib

go 1.26

// Отзываем сломанную версию
retract (
    v1.3.0 // содержит data race в Cache.Get
    [v1.1.0, v1.2.0] // диапазон сломанных версий
)
```

После `retract` пользователи, запускающие `go get -u`, не получат отозванную версию. Но те, кто уже используют её — продолжат работать (в отличие от `dotnet nuget delete`, который удаляет пакет).

---

## Директива exclude

```
// Запрещаем использование конкретной версии
exclude github.com/buggy/lib v1.5.0
```

Используется редко. Обычно `replace` более гибок.

---

## Vendoring: зависимости в репозитории

```bash
# Копировать все зависимости в vendor/
go mod vendor

# Сборка из vendor (без обращения к сети)
go build -mod=vendor ./...
```

**Когда использовать vendor:**
- CI/CD без доступа к интернету
- Аудит зависимостей (весь код в репозитории)
- Защита от удаления зависимости автором (left-pad problem)

**Когда НЕ использовать:**
- Обычная разработка (прокси `proxy.golang.org` кеширует модули)
- Маленькие проекты

> 💡 **Для C# разработчиков**: в NuGet нет стандартного vendoring. Ближайший аналог — коммит папки `packages/` в репозиторий, что считается антипаттерном. В Go vendor — официально поддерживаемый механизм.

---

## Go Workspace: мультимодульные проекты

Для проектов с несколькими модулями в одном репозитории (monorepo):

```bash
# Создать workspace
go work init ./api ./worker ./shared

# Добавить модуль в workspace
go work use ./new-service
```

Генерирует `go.work`:

```
go 1.26

use (
    ./api
    ./worker
    ./shared
)
```

### Когда использовать workspace

```
myproject/
├── go.work           # workspace file
├── api/
│   ├── go.mod        # module github.com/user/myproject/api
│   └── main.go
├── worker/
│   ├── go.mod        # module github.com/user/myproject/worker
│   └── main.go
└── shared/
    ├── go.mod        # module github.com/user/myproject/shared
    └── models.go
```

Без `go.work` каждый модуль потребовал бы `replace ../shared` в `go.mod`. С workspace все модули видят друг друга автоматически.

**C# аналог**: `.sln` файл, который объединяет несколько `.csproj`.

> **Не коммитить `go.work`** в репозиторий библиотеки — он нужен только для локальной разработки. Для приложений (не библиотек) — можно коммитить.

---

## Приватные модули

### Настройка GOPRIVATE

```bash
# Модули, которые НЕ должны проходить через прокси и checksum DB
export GOPRIVATE="github.com/mycompany/*,gitlab.internal.com/*"

# Или в конфиге Go (персистентно)
go env -w GOPRIVATE="github.com/mycompany/*"
```

### Git credentials

```bash
# HTTPS (через .netrc или credential helper)
git config --global url."https://oauth2:${TOKEN}@github.com/mycompany/".insteadOf "https://github.com/mycompany/"

# SSH
git config --global url."git@github.com:mycompany/".insteadOf "https://github.com/mycompany/"
```

**C# аналог**: настройка приватного NuGet feed в `nuget.config` с credentials.

---

## Прокси и зеркала

### Как работает загрузка модулей

```mermaid
graph LR
    A[go get] --> B{GOPROXY}
    B --> C[proxy.golang.org]
    C --> D{Найден?}
    D -->|Да| E[Скачать + проверить checksum]
    D -->|Нет| F[direct: обращение к VCS]
    E --> G[sum.golang.org: проверка хеша]
    G --> H[Сохранить в $GOPATH/pkg/mod]
    F --> H
```

### Переменные окружения

```bash
# Прокси (по умолчанию: proxy.golang.org)
GOPROXY=https://proxy.golang.org,direct

# Приватные модули (обходят прокси и checksum DB)
GOPRIVATE=github.com/mycompany/*

# Отключить checksum DB для определённых модулей
GONOSUMCHECK=github.com/mycompany/*

# Запретить прямое обращение к VCS (только через прокси)
GONOSUMDB=...

# Корпоративный прокси
GOPROXY=https://goproxy.mycompany.com,https://proxy.golang.org,direct
```

### Зачем нужен прокси

1. **Скорость** — кеширует модули рядом с вами
2. **Доступность** — автор удалил репозиторий, но прокси сохранил копию
3. **Иммутабельность** — опубликованная версия не может измениться
4. **Безопасность** — `sum.golang.org` проверяет хеши (supply chain protection)

---

## Публикация своего модуля

### Пошаговый процесс

```bash
# 1. Инициализировать модуль с правильным путём
go mod init github.com/username/mylib

# 2. Написать код, тесты
# 3. Убедиться, что всё работает
go test ./...
go vet ./...

# 4. Тегировать версию
git tag v1.0.0
git push origin v1.0.0

# 5. Готово! Пользователи могут: go get github.com/username/mylib@v1.0.0
```

### Публикация мажорной версии (v2+)

Два подхода:

**Подход 1: отдельная директория** (рекомендуется для библиотек):
```
mylib/
├── go.mod          # module github.com/username/mylib (v0/v1)
├── lib.go
└── v2/
    ├── go.mod      # module github.com/username/mylib/v2
    └── lib.go
```

**Подход 2: ветка major** (проще для приложений):
```bash
# В go.mod меняем путь модуля
# module github.com/username/mylib/v2

# Обновляем все внутренние import
# Тегируем: git tag v2.0.0
```

> 💡 **Для C# разработчиков**: в NuGet публикация — `dotnet pack` + `dotnet nuget push` + API key. В Go публикация — просто `git tag` + `git push`. Прокси подхватит автоматически. Никаких API ключей, никакой сборки пакета.

---

## Типичные ошибки C# разработчиков

### 1. Зависимость без версии

```bash
# ❌ Без версии — непредсказуемо
go get github.com/some/lib

# ✅ Явная версия
go get github.com/some/lib@v1.2.3
```

### 2. Забытый go mod tidy

```bash
# ❌ Добавили import, но не обновили go.mod
# Сборка упадёт: "missing go.sum entry"

# ✅ После изменения import — всегда
go mod tidy
```

### 3. replace в go.mod библиотеки

```
// ❌ replace в библиотеке ИГНОРИРУЕТСЯ при импорте другими модулями
// Работает только в go.mod основного приложения (main module)
module github.com/username/mylib

replace github.com/foo/bar => ../bar // не будет работать у пользователей!
```

### 4. Коммит go.work в библиотеку

```bash
# ❌ go.work в репозитории библиотеки
# Пользователи получат ошибки при go get

# ✅ Добавить go.work в .gitignore
echo "go.work" >> .gitignore
echo "go.work.sum" >> .gitignore
```

### 5. Игнорирование go.sum

```bash
# ❌ go.sum в .gitignore
# Сборка будет недетерминированной

# ✅ Всегда коммитить go.sum
git add go.sum
```

---

## Практика: Dockerfile с кешированием зависимостей

```dockerfile
FROM golang:1.26-alpine AS builder

WORKDIR /app

# Слой 1: зависимости (кешируется, пока go.mod/go.sum не изменятся)
COPY go.mod go.sum ./
RUN go mod download

# Слой 2: сборка (пересобирается при изменении кода)
COPY . .
RUN CGO_ENABLED=0 go build -o /app/server ./cmd/server

FROM alpine:3.21
COPY --from=builder /app/server /server
ENTRYPOINT ["/server"]
```

**C# аналог**:
```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS builder
WORKDIR /app
COPY *.csproj ./
RUN dotnet restore          # аналог go mod download
COPY . .
RUN dotnet publish -c Release -o /out
```

Та же стратегия: сначала зависимости (кешируются Docker), потом код.

---

## Шпаргалка команд

| Команда | Описание | C# аналог |
|---------|----------|-----------|
| `go mod init <path>` | Создать модуль | `dotnet new` |
| `go get <pkg>@<ver>` | Добавить/обновить зависимость | `dotnet add package` |
| `go get <pkg>@none` | Удалить зависимость | `dotnet remove package` |
| `go mod tidy` | Синхронизировать зависимости | `dotnet restore` (частично) |
| `go mod download` | Скачать зависимости в кеш | `dotnet restore` |
| `go mod vendor` | Вендорить зависимости | нет аналога |
| `go mod graph` | Граф зависимостей | `dotnet list package --include-transitive` |
| `go mod why <pkg>` | Зачем нужна зависимость | нет аналога |
| `go mod verify` | Проверить целостность | нет аналога |
| `go work init` | Создать workspace | Создать `.sln` |
| `go work use <dir>` | Добавить модуль в workspace | `dotnet sln add` |
| `go clean -modcache` | Очистить кеш модулей | `dotnet nuget locals all --clear` |
| `go list -m all` | Все зависимости (прямые + транзитивные) | `dotnet list package --include-transitive` |
| `go list -m -u all` | Доступные обновления | `dotnet list package --outdated` |
