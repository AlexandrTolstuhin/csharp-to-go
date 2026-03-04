# 4.7 Контейнеризация: Docker, Compose и Kubernetes для Go

---

## Введение

В предыдущих разделах Части 4 мы создали полноценную инфраструктуру:
- **4.1**: PostgreSQL с connection pooling и миграциями
- **4.2**: Redis для кэширования
- **4.3**: Kafka/RabbitMQ для асинхронной обработки
- **4.4**: gRPC для межсервисного взаимодействия
- **4.5**: Observability — логирование, метрики, трейсинг
- **4.6**: Конфигурация через ENV и config-файлы

Теперь нужно упаковать всё это в контейнеры и развернуть. Go идеально подходит для контейнеризации: статическая компиляция позволяет создавать образы размером 5-15 MB без runtime-зависимостей.

> 💡 **Для C# разработчиков**: В .NET вам нужен `aspnet` runtime образ (~220 MB минимум). В Go финальный образ может быть **пустым** (`scratch`) — только ваш бинарник. Это радикально меняет подход к Docker.

**Что изучим:**
- Multi-stage Docker builds для минимальных образов
- Выбор базового образа: scratch, Alpine, Distroless
- Docker Compose для локальной разработки
- Kubernetes basics для production деплоя
- CI/CD пайплайны для автоматизации

---

## Экосистема: C# vs Go

| Концепция | C# (.NET) | Go |
|-----------|-----------|-----|
| Базовый образ для сборки | `mcr.microsoft.com/dotnet/sdk:8.0` (~900 MB) | `golang:1.23` (~850 MB) |
| Базовый образ для runtime | `mcr.microsoft.com/dotnet/aspnet:8.0` (~220 MB) | `scratch` / `distroless` (~2-20 MB) |
| Multi-stage паттерн | `sdk` → `aspnet` | `golang` → `scratch` |
| Runtime зависимости | CLR обязателен | Не нужны (статический бинарник) |
| Cold start | ~500ms - 2s | ~10-50ms |
| Memory footprint | ~100-300 MB | ~10-50 MB |
| Orchestration | .NET Aspire, Docker Compose | Docker Compose, Kubernetes |
| Health checks | `IHealthCheck` интерфейс | Ручная реализация HTTP endpoint |
| Конфигурация в контейнере | `appsettings.json` + ENV | ENV (12-Factor) |

> ⚠️ **Ключевое отличие**: В .NET runtime обязателен — CLR должен быть в образе. Go компилируется в нативный бинарник, который запускается напрямую на ядре Linux. Это позволяет использовать пустой базовый образ (`scratch`).

**Размеры типичных production образов:**

| Приложение | .NET 8 | Go |
|------------|--------|-----|
| Hello World API | ~220 MB | ~5 MB |
| REST API с PostgreSQL | ~250 MB | ~15 MB |
| Микросервис с gRPC | ~280 MB | ~20 MB |

---

## Docker для Go приложений

### Базовый Dockerfile: как НЕ надо

Начнём с примера, который **не следует** использовать в production:

```dockerfile
# ❌ Плохой пример — НЕ используйте в production
FROM golang:1.23

WORKDIR /app

# Копируем весь исходный код
COPY . .

# Скачиваем зависимости и собираем
RUN go mod download
RUN go build -o server ./cmd/server

# Запускаем
CMD ["./server"]
```

**Проблемы этого подхода:**

| Проблема | Последствие |
|----------|-------------|
| Финальный образ ~850 MB | Go SDK не нужен для запуска |
| Исходный код в образе | Утечка интеллектуальной собственности |
| Секреты в слоях | `.env`, конфиги могут попасть в образ |
| Нет кэширования слоёв | Каждое изменение кода перекачивает зависимости |
| Запуск от root | Уязвимость безопасности |
| CGO включен | Зависимость от libc в runtime |

**C# аналог той же ошибки:**

```dockerfile
# ❌ Плохой пример для .NET — НЕ используйте
FROM mcr.microsoft.com/dotnet/sdk:8.0
WORKDIR /app
COPY . .
RUN dotnet publish -c Release -o /app/publish
CMD ["dotnet", "/app/publish/MyApp.dll"]
# Размер: ~900 MB (SDK в финальном образе)
```

---

### Multi-stage builds

#### Почему multi-stage критичен для Go

Multi-stage build позволяет использовать несколько `FROM` инструкций в одном Dockerfile. Первый stage — для сборки (нужен компилятор), второй — для запуска (только бинарник).

**Преимущества:**

1. **Размер**: 850 MB → 5-15 MB
2. **Безопасность**: исходный код не попадает в финальный образ
3. **Кэширование**: зависимости и код в разных слоях
4. **Простота**: один Dockerfile для dev и prod

#### Базовый паттерн: builder + runtime

```dockerfile
# =============================================================================
# Stage 1: Builder — компиляция Go приложения
# =============================================================================
FROM golang:1.23-alpine AS builder

# Метаданные
LABEL maintainer="team@example.com"
LABEL stage="builder"

WORKDIR /build

# Копируем только файлы зависимостей (для кэширования)
COPY go.mod go.sum ./

# Скачиваем зависимости (кэшируется, если go.mod/go.sum не изменились)
RUN go mod download

# Копируем исходный код
COPY . .

# Собираем статический бинарник
# CGO_ENABLED=0 — отключаем CGO для статической линковки
# GOOS=linux — целевая ОС
# -ldflags="-s -w" — убираем debug info, уменьшаем размер
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-s -w" \
    -o /build/server \
    ./cmd/server

# =============================================================================
# Stage 2: Runtime — минимальный образ для запуска
# =============================================================================
FROM scratch

# Копируем CA сертификаты для HTTPS запросов
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Копируем бинарник из builder stage
COPY --from=builder /build/server /server

# Запускаем от непривилегированного пользователя
USER 65534:65534

# Точка входа
ENTRYPOINT ["/server"]
```

**Результат:**
- Builder stage: ~850 MB (не попадает в финальный образ)
- Runtime stage: ~5-10 MB (только бинарник + CA сертификаты)

**Сравнение с .NET multi-stage:**

```dockerfile
# .NET multi-stage build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY *.csproj .
RUN dotnet restore
COPY . .
RUN dotnet publish -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "MyApp.dll"]
# Финальный размер: ~220 MB (aspnet runtime обязателен)
```

> 💡 **Для C# разработчиков**: В .NET финальный образ минимум ~220 MB из-за CLR. В Go можно достичь ~5 MB, потому что runtime не нужен.

#### Кэширование зависимостей

Docker кэширует слои. Если слой не изменился, он берётся из кэша. Правильный порядок `COPY` критичен:

```dockerfile
# ✅ Правильный порядок — максимальное кэширование
FROM golang:1.23-alpine AS builder
WORKDIR /build

# 1. Сначала копируем только go.mod и go.sum
COPY go.mod go.sum ./

# 2. Скачиваем зависимости (кэшируется!)
RUN go mod download

# 3. Потом копируем исходный код
COPY . .

# 4. Собираем
RUN CGO_ENABLED=0 go build -o /app/server ./cmd/server
```

**Как это работает:**

1. `COPY go.mod go.sum` — редко меняется → слой кэшируется
2. `go mod download` — выполняется только если go.mod изменился
3. `COPY . .` — меняется часто (ваш код)
4. `go build` — выполняется при каждом изменении кода

**Без кэширования** (go.mod и код в одном слое):
- Каждое изменение кода → перекачивание всех зависимостей
- Время сборки: 2-5 минут

**С кэшированием**:
- Изменение кода → только компиляция
- Время сборки: 10-30 секунд

**BuildKit mount cache (ещё быстрее):**

```dockerfile
# syntax=docker/dockerfile:1

FROM golang:1.23-alpine AS builder
WORKDIR /build

COPY go.mod go.sum ./

# Mount cache для go modules и build cache
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    go mod download

COPY . .

RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 go build -o /app/server ./cmd/server
```

> 💡 **BuildKit cache mount**: Сохраняет кэш между сборками даже если слои инвалидируются. Требует `DOCKER_BUILDKIT=1` или Docker 23.0+.

#### CGO и Alpine

**CGO** (C Go) — механизм вызова C-кода из Go. По умолчанию включен.

**Когда нужен CGO:**
- SQLite (`mattn/go-sqlite3`)
- Некоторые криптографические библиотеки
- Биндинги к C-библиотекам

**Проблема CGO:**
- Бинарник зависит от libc
- Нужен совместимый runtime (glibc или musl)
- Нельзя использовать `scratch`

```dockerfile
# CGO_ENABLED=1 (по умолчанию) — динамическая линковка
# Бинарник зависит от libc

# CGO_ENABLED=0 — статическая линковка
# Бинарник автономный, работает в scratch
```

**Alpine использует musl, не glibc:**

```dockerfile
# ❌ Проблема: собрали с glibc, запускаем в musl
FROM golang:1.23 AS builder  # glibc
RUN go build -o /app/server

FROM alpine:3.20  # musl
COPY --from=builder /app/server /server
# Ошибка: "not found" (несовместимость libc)
```

**Решения:**

```dockerfile
# Вариант 1: CGO_ENABLED=0 (рекомендуется)
FROM golang:1.23-alpine AS builder
RUN CGO_ENABLED=0 go build -o /app/server

FROM scratch
COPY --from=builder /app/server /server

# Вариант 2: Собираем в alpine (musl)
FROM golang:1.23-alpine AS builder
RUN apk add --no-cache gcc musl-dev
RUN go build -o /app/server  # CGO с musl

FROM alpine:3.20
COPY --from=builder /app/server /server

# Вариант 3: Собираем в debian, запускаем в debian
FROM golang:1.23 AS builder  # glibc
RUN go build -o /app/server

FROM debian:bookworm-slim  # glibc
COPY --from=builder /app/server /server
```

> 💡 **Рекомендация**: Используйте `CGO_ENABLED=0` везде, где возможно. Это позволяет использовать `scratch` или `distroless` и избежать проблем с совместимостью libc.

---

### Scratch vs Alpine vs Distroless

#### FROM scratch: минимальный образ

`scratch` — это пустой образ. Буквально ничего: ни shell, ни libc, ни утилит.

```dockerfile
FROM golang:1.23-alpine AS builder
WORKDIR /build

COPY go.mod go.sum ./
RUN go mod download
COPY . .

# Статический бинарник
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-s -w" \
    -o /app/server \
    ./cmd/server

FROM scratch

# CA сертификаты для HTTPS
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Timezone data (если нужны time.LoadLocation)
COPY --from=builder /usr/share/zoneinfo /usr/share/zoneinfo

# Наш бинарник
COPY --from=builder /app/server /server

# Non-root user (только UID, т.к. нет /etc/passwd)
USER 65534:65534

ENTRYPOINT ["/server"]
```

**Преимущества scratch:**
- Минимальный размер (~2-10 MB)
- Минимальная attack surface (нечего эксплуатировать)
- Нет CVE от ОС (нет ОС)

**Недостатки scratch:**
- Нет shell — нельзя `docker exec -it container sh`
- Нет утилит — нет `curl`, `wget`, `ls`
- Сложнее отлаживать
- Нужно явно копировать CA сертификаты и tzdata

**Когда использовать:**
- Production образы без необходимости отладки внутри контейнера
- Security-critical приложения

#### Alpine: баланс размера и утилит

Alpine Linux — минималистичный дистрибутив (~7 MB).

```dockerfile
FROM golang:1.23-alpine AS builder
WORKDIR /build

COPY go.mod go.sum ./
RUN go mod download
COPY . .

RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /app/server ./cmd/server

FROM alpine:3.20

# Установка необходимых пакетов
RUN apk add --no-cache \
    ca-certificates \
    tzdata

# Создание non-root пользователя
RUN adduser -D -H -u 10001 appuser

# Копирование бинарника
COPY --from=builder /app/server /server

# Переключение на non-root
USER appuser

ENTRYPOINT ["/server"]
```

**Преимущества Alpine:**
- Есть shell (`/bin/sh`)
- Есть package manager (`apk`)
- Можно установить утилиты для отладки
- Маленький размер (~7-15 MB финальный образ)

**Недостатки Alpine:**
- Использует musl вместо glibc (редко проблема для Go)
- Чуть больше attack surface чем scratch

**Когда использовать:**
- Нужна возможность отладки внутри контейнера
- Нужны дополнительные утилиты (curl, wget)
- Development и staging окружения

#### Distroless: безопасность Google

Distroless — образы от Google без shell и package manager, но с необходимыми runtime файлами.

```dockerfile
FROM golang:1.23-alpine AS builder
WORKDIR /build

COPY go.mod go.sum ./
RUN go mod download
COPY . .

RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /app/server ./cmd/server

# Distroless static — для Go приложений без CGO
FROM gcr.io/distroless/static-debian12:nonroot

# Копирование бинарника
COPY --from=builder /app/server /server

# nonroot tag уже запускает от непривилегированного пользователя
USER nonroot:nonroot

ENTRYPOINT ["/server"]
```

**Варианты distroless образов:**

| Образ | Размер | Содержит | Использование |
|-------|--------|----------|---------------|
| `gcr.io/distroless/static` | ~2 MB | CA certs, tzdata | Go без CGO |
| `gcr.io/distroless/base` | ~20 MB | + glibc | Go с CGO |
| `gcr.io/distroless/cc` | ~25 MB | + libgcc | C++ приложения |

**Теги для отладки:**

```dockerfile
# Production
FROM gcr.io/distroless/static-debian12:nonroot

# Debug (есть busybox shell)
FROM gcr.io/distroless/static-debian12:debug-nonroot
```

```bash
# Отладка с debug-образом
docker run -it --entrypoint=sh myapp:debug
```

**Преимущества Distroless:**
- Нет shell в production (безопасность)
- Есть debug-версия для отладки
- CA сертификаты и tzdata включены
- Non-root по умолчанию (тег `:nonroot`)

**Недостатки Distroless:**
- Зависимость от Google Container Registry
- Чуть больше scratch

**Когда использовать:**
- Production образы
- Security-critical приложения
- Когда scratch слишком минималистичен

#### Сравнительная таблица базовых образов

| Характеристика | scratch | distroless/static | alpine | debian-slim |
|----------------|---------|-------------------|--------|-------------|
| **Размер** | ~2 MB | ~2 MB | ~7 MB | ~80 MB |
| **Shell** | ❌ | ❌ (✅ в :debug) | ✅ | ✅ |
| **Package manager** | ❌ | ❌ | ✅ apk | ✅ apt |
| **CA certs** | ❌ (копировать) | ✅ | ✅ (apk add) | ✅ |
| **tzdata** | ❌ (копировать) | ✅ | ✅ (apk add) | ✅ |
| **glibc** | ❌ | ❌ (base: ✅) | ❌ (musl) | ✅ |
| **Security** | Максимум | Высокий | Средний | Низкий |
| **Debug** | Сложно | :debug tag | Легко | Легко |
| **CVE** | 0 (нет ОС) | Минимум | Редко | Часто |

#### Блок-схема выбора базового образа

```
Нужен CGO?
│
├─ ДА ──┬─► Какой libc?
│       │
│       ├─ glibc ──► distroless/base или debian-slim
│       │
│       └─ musl ───► alpine
│
└─ НЕТ ─┬─► Нужен shell в production?
        │
        ├─ ДА ──► alpine
        │
        └─ НЕТ ─┬─► Нужна максимальная безопасность?
                │
                ├─ ДА ──► scratch
                │
                └─ НЕТ ──► distroless/static (рекомендуется)
```

> 💡 **Рекомендация**: Для большинства Go приложений используйте `distroless/static:nonroot`. Это оптимальный баланс безопасности, размера и удобства.

---

### Безопасность Docker-образов

#### Non-root пользователь

По умолчанию контейнер запускается от root. Это опасно: если атакующий получит доступ к контейнеру, он будет root.

**scratch (нет /etc/passwd):**

```dockerfile
FROM scratch
COPY --from=builder /app/server /server

# Используем числовой UID/GID
# 65534 — стандартный "nobody" в Linux
USER 65534:65534

ENTRYPOINT ["/server"]
```

**Alpine (создаём пользователя):**

```dockerfile
FROM alpine:3.20

# Создаём пользователя без домашней директории
RUN adduser -D -H -u 10001 appuser

COPY --from=builder /app/server /server

# Переключаемся на созданного пользователя
USER appuser

ENTRYPOINT ["/server"]
```

**Distroless (уже есть nonroot):**

```dockerfile
FROM gcr.io/distroless/static-debian12:nonroot

COPY --from=builder /app/server /server

# Тег :nonroot уже настроен на user nonroot:nonroot
USER nonroot:nonroot

ENTRYPOINT ["/server"]
```

**Проверка:**

```bash
docker run myapp whoami
# Должен вернуть НЕ root

docker run myapp id
# uid=65534(nobody) gid=65534(nogroup) groups=65534(nogroup)
```

#### Сканирование уязвимостей (Trivy)

**Trivy** — сканер уязвимостей от Aqua Security.

```bash
# Установка (macOS)
brew install trivy

# Установка (Linux)
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Сканирование образа
trivy image myapp:latest

# Только критические и высокие уязвимости
trivy image --severity CRITICAL,HIGH myapp:latest

# JSON вывод для CI/CD
trivy image --format json --output results.json myapp:latest

# Fail если есть критические уязвимости
trivy image --exit-code 1 --severity CRITICAL myapp:latest
```

**Docker Scout (встроенный в Docker Desktop):**

```bash
# Анализ образа
docker scout cves myapp:latest

# Рекомендации по обновлению
docker scout recommendations myapp:latest
```

**Пример вывода Trivy:**

```
myapp:latest (alpine 3.20)
==========================
Total: 2 (UNKNOWN: 0, LOW: 1, MEDIUM: 1, HIGH: 0, CRITICAL: 0)

┌───────────────┬────────────────┬──────────┬─────────────────────────────────┐
│    Library    │ Vulnerability  │ Severity │          Fixed Version          │
├───────────────┼────────────────┼──────────┼─────────────────────────────────┤
│ libcrypto3    │ CVE-2024-XXXX  │ MEDIUM   │ 3.1.4-r6                        │
│ musl          │ CVE-2024-YYYY  │ LOW      │                                 │
└───────────────┴────────────────┴──────────┴─────────────────────────────────┘
```

> 💡 **Для scratch/distroless**: CVE от ОС будет 0, т.к. нет ОС. Сканер проверит только ваш Go бинарник на известные уязвимости в зависимостях.

#### .dockerignore

`.dockerignore` исключает файлы из контекста сборки:

```dockerignore
# Git
.git
.gitignore

# IDE
.idea
.vscode
*.swp

# Тесты и документация
*_test.go
**/*_test.go
docs/
*.md
!README.md

# Конфигурация разработки
.env
.env.*
*.local

# Docker
Dockerfile*
docker-compose*.yml
.dockerignore

# Build артефакты
bin/
dist/
coverage.out
*.exe

# Секреты (КРИТИЧНО!)
*.pem
*.key
secrets/
credentials/
```

**Почему это важно:**

1. **Безопасность**: секреты не попадут в образ
2. **Размер контекста**: быстрее передаётся в Docker daemon
3. **Кэширование**: меньше инвалидаций слоёв

```bash
# Проверить, что попадает в контекст
docker build --no-cache -t test . 2>&1 | head -5
# "Sending build context to Docker daemon  X.XXX MB"
```

#### Secrets в build-time

Иногда при сборке нужен доступ к секретам (private git repos, npm tokens).

**❌ Плохо — секрет в слое:**

```dockerfile
# НИКОГДА так не делайте!
ARG GITHUB_TOKEN
ENV GITHUB_TOKEN=$GITHUB_TOKEN
RUN git clone https://$GITHUB_TOKEN@github.com/private/repo.git
# Токен остаётся в истории слоёв!
```

**✅ Хорошо — BuildKit secrets:**

```dockerfile
# syntax=docker/dockerfile:1

FROM golang:1.23-alpine AS builder

# Секрет монтируется только на время выполнения команды
# Не сохраняется в слоях!
RUN --mount=type=secret,id=github_token \
    GITHUB_TOKEN=$(cat /run/secrets/github_token) && \
    git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"

COPY go.mod go.sum ./
RUN --mount=type=secret,id=github_token \
    GITHUB_TOKEN=$(cat /run/secrets/github_token) && \
    GOPRIVATE=github.com/myorg/* go mod download
```

**Использование:**

```bash
# Передача секрета при сборке
echo "ghp_xxxxxxxxxxxx" > github_token.txt
docker build --secret id=github_token,src=github_token.txt -t myapp .

# Или через stdin
docker build --secret id=github_token,env=GITHUB_TOKEN -t myapp .
```

---

### Оптимизация размера образа

#### Флаги компиляции: ldflags

```dockerfile
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags="-s -w" \
    -o /app/server \
    ./cmd/server
```

**Флаги:**

| Флаг | Действие | Экономия |
|------|----------|----------|
| `-s` | Удалить symbol table | ~20% |
| `-w` | Удалить DWARF debug info | ~10% |
| `-X main.Version=1.0.0` | Внедрить версию при компиляции | 0 |

**Пример с версионированием:**

```dockerfile
ARG VERSION=dev
ARG COMMIT=unknown
ARG BUILD_TIME=unknown

RUN CGO_ENABLED=0 go build \
    -ldflags="-s -w \
        -X main.Version=${VERSION} \
        -X main.Commit=${COMMIT} \
        -X main.BuildTime=${BUILD_TIME}" \
    -o /app/server \
    ./cmd/server
```

```go
// main.go
package main

var (
    Version   = "dev"
    Commit    = "unknown"
    BuildTime = "unknown"
)

func main() {
    log.Printf("Version: %s, Commit: %s, Built: %s", Version, Commit, BuildTime)
    // ...
}
```

**Сборка:**

```bash
docker build \
    --build-arg VERSION=$(git describe --tags) \
    --build-arg COMMIT=$(git rev-parse --short HEAD) \
    --build-arg BUILD_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
    -t myapp:$(git describe --tags) .
```

#### UPX компрессия

**UPX** (Ultimate Packer for eXecutables) — сжимает бинарники.

```dockerfile
FROM golang:1.23-alpine AS builder

RUN apk add --no-cache upx

WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download
COPY . .

# Собираем
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /app/server ./cmd/server

# Сжимаем (--best — максимальное сжатие)
RUN upx --best --lzma /app/server

FROM scratch
COPY --from=builder /app/server /server
ENTRYPOINT ["/server"]
```

**Результат:**

| Этап | Размер |
|------|--------|
| После go build | ~15 MB |
| После -ldflags="-s -w" | ~10 MB |
| После UPX | ~3-4 MB |

**Предостережения:**

- **Время запуска**: UPX распаковывает при старте (+50-100ms)
- **Memory**: Нужна память для распаковки
- **Отладка**: Сложнее дебажить (нет символов + сжатие)
- **Security**: Некоторые сканеры считают UPX подозрительным

> 💡 **Рекомендация**: Используйте UPX только если размер критичен (edge computing, serverless). Для обычных серверов `-ldflags="-s -w"` достаточно.

---

## Production Docker Patterns

### Health Checks в Dockerfile

Docker поддерживает `HEALTHCHECK` инструкцию для проверки здоровья контейнера.

**Для scratch (бинарник с флагом --health):**

```go
// cmd/server/main.go
package main

import (
    "flag"
    "fmt"
    "net/http"
    "os"
    "time"
)

func main() {
    healthCheck := flag.Bool("health", false, "выполнить health check и выйти")
    flag.Parse()

    if *healthCheck {
        // Health check режим — проверяем сервис и выходим
        client := &http.Client{Timeout: 3 * time.Second}
        resp, err := client.Get("http://localhost:8080/health")
        if err != nil || resp.StatusCode != http.StatusOK {
            os.Exit(1)
        }
        os.Exit(0)
    }

    // Обычный режим — запускаем сервер
    http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        fmt.Fprintln(w, "OK")
    })

    http.ListenAndServe(":8080", nil)
}
```

```dockerfile
FROM scratch

COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /app/server /server

USER 65534:65534

# Health check использует сам бинарник
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["/server", "-health"]

ENTRYPOINT ["/server"]
```

**Для Alpine (с wget):**

```dockerfile
FROM alpine:3.20

RUN apk add --no-cache ca-certificates

COPY --from=builder /app/server /server

RUN adduser -D -H -u 10001 appuser
USER appuser

# Используем wget для health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:8080/health || exit 1

ENTRYPOINT ["/server"]
```

**Параметры HEALTHCHECK:**

| Параметр | Описание | Рекомендация |
|----------|----------|--------------|
| `--interval` | Интервал между проверками | 30s для production |
| `--timeout` | Таймаут одной проверки | 3-5s |
| `--start-period` | Время на инициализацию (игнорирует failures) | 5-30s |
| `--retries` | Количество неудач до unhealthy | 3 |

**Состояния контейнера:**

```bash
docker ps
# CONTAINER ID   IMAGE    STATUS
# abc123         myapp    Up 5 minutes (healthy)
# def456         myapp    Up 2 minutes (health: starting)
# ghi789         myapp    Up 10 minutes (unhealthy)
```

> 💡 **Для C# разработчиков**: В ASP.NET Core вы используете `IHealthCheck` интерфейс и middleware. В Go нужно реализовать HTTP endpoint самостоятельно. См. раздел [4.5 Observability](./05_observability.md#health-checks) для детальной реализации.

### Graceful Shutdown

Когда Docker останавливает контейнер, он отправляет `SIGTERM`, ждёт (по умолчанию 10 секунд), затем `SIGKILL`.

```go
// cmd/server/main.go
package main

import (
    "context"
    "log/slog"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"
)

func main() {
    logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

    // Создаём сервер
    srv := &http.Server{
        Addr:         ":8080",
        Handler:      routes(),
        ReadTimeout:  5 * time.Second,
        WriteTimeout: 10 * time.Second,
        IdleTimeout:  120 * time.Second,
    }

    // Канал для получения сигналов
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

    // Запускаем сервер в горутине
    go func() {
        logger.Info("сервер запущен", "addr", srv.Addr)
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            logger.Error("ошибка сервера", "error", err)
            os.Exit(1)
        }
    }()

    // Ждём сигнал завершения
    sig := <-quit
    logger.Info("получен сигнал завершения", "signal", sig)

    // Контекст с таймаутом для graceful shutdown
    // Должен быть меньше, чем docker stop timeout (10s по умолчанию)
    ctx, cancel := context.WithTimeout(context.Background(), 8*time.Second)
    defer cancel()

    // Graceful shutdown — ждём завершения активных запросов
    if err := srv.Shutdown(ctx); err != nil {
        logger.Error("ошибка graceful shutdown", "error", err)
        os.Exit(1)
    }

    logger.Info("сервер остановлен корректно")
}
```

**Таймауты:**

```
Docker SIGTERM ─────────────────────────────────────────► Docker SIGKILL
                    |◄────── 10s по умолчанию ──────►|

Приложение:         |◄── Shutdown ctx 8s ──►|
                    └─ Завершение запросов ─┘
```

**Dockerfile с увеличенным stop timeout:**

```dockerfile
# Увеличиваем таймаут для приложений с долгими операциями
STOPSIGNAL SIGTERM
# docker stop --time=30 или docker-compose stop_grace_period: 30s
```

**C# аналог:**

```csharp
// Program.cs в ASP.NET Core
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

// IHostApplicationLifetime — встроенный механизм
var lifetime = app.Services.GetRequiredService<IHostApplicationLifetime>();

lifetime.ApplicationStopping.Register(() =>
{
    Console.WriteLine("Получен сигнал завершения...");
    // Cleanup logic
});

app.Run();
```

### Логирование в контейнере

**12-Factor App**: Логи в stdout/stderr, агрегация внешними средствами.

```go
// ✅ Правильно — логи в stdout
logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
logger.Info("запрос обработан", "method", "GET", "path", "/users")

// ❌ Неправильно — логи в файл
file, _ := os.OpenFile("/var/log/app.log", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
logger := slog.New(slog.NewJSONHandler(file, nil))
```

**JSON формат для агрегаторов:**

```go
// slog с JSON handler
logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
}))

logger.Info("запрос обработан",
    "method", "GET",
    "path", "/api/users",
    "status", 200,
    "duration_ms", 45,
    "trace_id", "abc123",
)
```

**Вывод:**

```json
{"time":"2024-01-15T10:30:00Z","level":"INFO","msg":"запрос обработан","method":"GET","path":"/api/users","status":200,"duration_ms":45,"trace_id":"abc123"}
```

**Docker logging drivers:**

```bash
# Просмотр логов контейнера
docker logs -f myapp

# С timestamp
docker logs -f --timestamps myapp

# Последние 100 строк
docker logs --tail 100 myapp
```

**Compose с logging:**

```yaml
services:
  app:
    image: myapp:latest
    logging:
      driver: "json-file"
      options:
        max-size: "10m"    # Ротация по размеру
        max-file: "3"      # Максимум 3 файла
```

### Сигналы и PID 1

В контейнере ваш процесс запускается как PID 1. Это особый процесс в Linux с особым поведением сигналов.

**Проблема с shell формой:**

```dockerfile
# ❌ Shell форма — запускает через /bin/sh
CMD ./server
# PID 1: /bin/sh -c "./server"
# PID 2: ./server
# SIGTERM идёт к shell, не к приложению!
```

```dockerfile
# ✅ Exec форма — запускает напрямую
CMD ["./server"]
# PID 1: ./server
# SIGTERM идёт напрямую к приложению
```

**ENTRYPOINT vs CMD:**

```dockerfile
# ENTRYPOINT — основная команда (не переопределяется без --entrypoint)
# CMD — аргументы по умолчанию (переопределяются)

ENTRYPOINT ["/server"]
CMD ["--port=8080"]

# docker run myapp → /server --port=8080
# docker run myapp --port=9090 → /server --port=9090
```

**Zombie processes:**

Если ваше приложение создаёт дочерние процессы, они могут стать "зомби" после завершения (PID 1 не делает reaping автоматически).

**Решение с tini (для Alpine с shell скриптами):**

```dockerfile
FROM alpine:3.20

RUN apk add --no-cache tini

COPY --from=builder /app/server /server

# tini как init system — корректно обрабатывает сигналы и reaping
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/server"]
```

> 💡 **Для Go приложений**: Если не создаёте дочерние процессы — tini не нужен. Go корректно обрабатывает сигналы, когда используете exec форму.

---

## Docker Compose

Docker Compose — инструмент для определения и запуска multi-container приложений.

### Структура compose.yaml

```yaml
# compose.yaml (или docker-compose.yml)
name: myapp  # Имя проекта (опционально)

services:
  # Определение сервисов
  app:
    # ...

  postgres:
    # ...

  redis:
    # ...

networks:
  # Определение сетей
  backend:
    driver: bridge

volumes:
  # Определение volumes
  postgres-data:
```

### Сервис Go приложения

```yaml
services:
  app:
    # Сборка из Dockerfile
    build:
      context: .
      dockerfile: Dockerfile
      target: production  # Multi-stage target
      args:
        - VERSION=${VERSION:-dev}
        - COMMIT=${COMMIT:-unknown}

    # Или готовый образ
    # image: ghcr.io/myorg/myapp:latest

    # Имя контейнера (опционально)
    container_name: myapp

    # Порты: хост:контейнер
    ports:
      - "8080:8080"
      - "9090:9090"  # gRPC

    # Переменные окружения
    environment:
      - ENV=production
      - LOG_LEVEL=info
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_USER=myapp
      - DB_PASSWORD=${DB_PASSWORD}  # Из .env файла
      - DB_NAME=myapp
      - REDIS_ADDR=redis:6379

    # Или из файла
    env_file:
      - .env
      - .env.local

    # Зависимости
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started

    # Health check
    healthcheck:
      test: ["CMD", "/app/server", "-health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

    # Перезапуск
    restart: unless-stopped

    # Ресурсы (опционально)
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M

    # Сети
    networks:
      - backend
```

### Зависимости: PostgreSQL, Redis

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: myapp-postgres

    environment:
      POSTGRES_USER: myapp
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: myapp

    # Инициализация базы
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql:ro

    # Health check для PostgreSQL
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U myapp -d myapp"]
      interval: 5s
      timeout: 5s
      retries: 5

    ports:
      - "5432:5432"  # Для локальной разработки

    networks:
      - backend

  redis:
    image: redis:7-alpine
    container_name: myapp-redis

    # Команда с настройками
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru

    volumes:
      - redis-data:/data

    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

    ports:
      - "6379:6379"

    networks:
      - backend

volumes:
  postgres-data:
  redis-data:

networks:
  backend:
    driver: bridge
```

### Networking и service discovery

В Docker Compose сервисы автоматически доступны по имени в одной сети.

```yaml
services:
  app:
    environment:
      # Имя сервиса = hostname в сети
      - DB_HOST=postgres    # НЕ localhost!
      - REDIS_ADDR=redis:6379
    networks:
      - backend

  postgres:
    networks:
      - backend

  redis:
    networks:
      - backend

networks:
  backend:
    driver: bridge
```

```go
// В коде Go
cfg := &Config{
    DBHost:    os.Getenv("DB_HOST"),    // "postgres"
    RedisAddr: os.Getenv("REDIS_ADDR"), // "redis:6379"
}

// Подключение к PostgreSQL
dsn := fmt.Sprintf("host=%s port=5432 user=myapp password=secret dbname=myapp",
    cfg.DBHost) // host=postgres

// Подключение к Redis
rdb := redis.NewClient(&redis.Options{
    Addr: cfg.RedisAddr, // redis:6379
})
```

**DNS resolution внутри сети:**

```bash
# Из контейнера app
docker exec myapp nslookup postgres
# Server:    127.0.0.11
# Address:   127.0.0.11:53
# Name:      postgres
# Address:   172.20.0.2
```

### Volumes: данные и конфигурация

```yaml
services:
  app:
    volumes:
      # Named volume для персистентных данных
      - app-data:/app/data

      # Bind mount для конфигурации (только чтение)
      - ./config:/app/config:ro

      # Bind mount для разработки (hot reload)
      - .:/app:cached

  postgres:
    volumes:
      # Named volume — данные переживают перезапуск
      - postgres-data:/var/lib/postgresql/data

      # Init скрипты
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql:ro

volumes:
  app-data:
  postgres-data:
    # Внешний volume (создан отдельно)
    # external: true
```

**Типы volumes:**

| Тип | Синтаксис | Использование |
|-----|-----------|---------------|
| Named | `volume-name:/path` | Персистентные данные |
| Bind | `./host/path:/container/path` | Разработка, конфиги |
| tmpfs | `tmpfs:/path` | Временные данные (в памяти) |

### Health checks и depends_on

```yaml
services:
  app:
    depends_on:
      postgres:
        condition: service_healthy  # Ждём healthcheck
      redis:
        condition: service_healthy
      kafka:
        condition: service_started  # Просто запуск (нет healthcheck)

    healthcheck:
      test: ["CMD", "/app/server", "-health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

  postgres:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U myapp"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s

  redis:
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
```

**Условия depends_on:**

| Условие | Описание |
|---------|----------|
| `service_started` | Контейнер запущен (по умолчанию) |
| `service_healthy` | Healthcheck прошёл |
| `service_completed_successfully` | Контейнер завершился с кодом 0 |

> ⚠️ **Важно**: `depends_on` гарантирует порядок запуска, но не готовность сервиса. Используйте `condition: service_healthy` для зависимостей.

### Profiles для разных окружений

```yaml
services:
  app:
    profiles: ["dev", "prod"]
    # ...

  postgres:
    profiles: ["dev", "prod"]
    # ...

  # Только для development
  adminer:
    image: adminer
    ports:
      - "8081:8080"
    profiles: ["dev"]
    depends_on:
      - postgres

  # Только для monitoring
  prometheus:
    image: prom/prometheus:latest
    profiles: ["monitoring", "prod"]
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
    ports:
      - "9091:9090"

  grafana:
    image: grafana/grafana:latest
    profiles: ["monitoring", "prod"]
    ports:
      - "3000:3000"
    depends_on:
      - prometheus

  # Только для production
  jaeger:
    image: jaegertracing/all-in-one:latest
    profiles: ["monitoring", "prod"]
    ports:
      - "16686:16686"
      - "4317:4317"
```

**Использование profiles:**

```bash
# Development (app + postgres + adminer)
docker compose --profile dev up

# Production (app + postgres + monitoring)
docker compose --profile prod up

# Development + monitoring
docker compose --profile dev --profile monitoring up

# Конкретные сервисы
docker compose up app postgres
```

### Горячая перезагрузка в development (air)

[air](https://github.com/air-verse/air) — hot reload для Go.

**Установка:**

```bash
go install github.com/air-verse/air@latest
```

**.air.toml:**

```toml
root = "."
tmp_dir = "tmp"

[build]
  # Команда сборки
  cmd = "go build -o ./tmp/main ./cmd/server"
  # Бинарник
  bin = "./tmp/main"
  # Задержка перед перезапуском
  delay = 500
  # Исключения
  exclude_dir = ["assets", "tmp", "vendor", "testdata", "node_modules"]
  exclude_file = []
  exclude_regex = ["_test.go"]
  exclude_unchanged = false
  follow_symlink = false
  # Расширения для отслеживания
  include_ext = ["go", "tpl", "tmpl", "html", "yaml", "yml", "toml"]
  # Аргументы
  args_bin = []
  # Kill delay
  kill_delay = 500

[log]
  time = true
  main_only = false

[color]
  main = "magenta"
  watcher = "cyan"
  build = "yellow"
  runner = "green"

[misc]
  clean_on_exit = true
```

**compose.yaml для development:**

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      # Mount исходного кода для hot reload
      - .:/app:cached
      # Кэш Go modules
      - go-mod-cache:/go/pkg/mod
      # Кэш сборки
      - go-build-cache:/root/.cache/go-build
    command: ["air", "-c", ".air.toml"]
    ports:
      - "8080:8080"
    environment:
      - ENV=development
      - DB_HOST=postgres
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  go-mod-cache:
  go-build-cache:
```

**Dockerfile.dev:**

```dockerfile
FROM golang:1.23-alpine

# Установка air
RUN go install github.com/air-verse/air@latest

WORKDIR /app

# Копируем go.mod для начальной загрузки зависимостей
COPY go.mod go.sum ./
RUN go mod download

# Исходный код будет mount'иться через volume
# COPY . .

# Air следит за изменениями и перезапускает
CMD ["air", "-c", ".air.toml"]
```

**Запуск:**

```bash
# Development с hot reload
docker compose -f compose.yaml -f compose.dev.yaml up

# Или с profile
docker compose --profile dev up
```

> 💡 **Для C# разработчиков**: Это аналог `dotnet watch run` в ASP.NET Core. Air отслеживает изменения .go файлов и автоматически пересобирает/перезапускает приложение.

---

## Kubernetes Basics

### Зачем Kubernetes: когда Docker Compose недостаточно

Docker Compose подходит для:
- Локальной разработки
- Простых production-сценариев (один сервер)
- CI/CD тестирования

**Kubernetes нужен когда:**

| Требование | Docker Compose | Kubernetes |
|------------|----------------|------------|
| Автоскейлинг | ❌ Ручной | ✅ HPA, VPA |
| High Availability | ❌ Один хост | ✅ Multi-node |
| Zero-downtime deploy | ⚠️ Сложно | ✅ Rolling update |
| Service mesh | ❌ | ✅ Istio, Linkerd |
| Self-healing | ❌ | ✅ Liveness probes |
| Secrets management | ⚠️ .env файлы | ✅ K8s Secrets, Vault |
| Multi-cluster | ❌ | ✅ Federation |

> 💡 **Для C# разработчиков**: Kubernetes — это как Azure App Service на стероидах. Вы описываете желаемое состояние, K8s его поддерживает. Похоже на IaC (Infrastructure as Code).

### Основные концепции: Pod, Deployment, Service

**Pod** — минимальная единица деплоя. Один или несколько контейнеров с общим network namespace.

```yaml
# Пример Pod (обычно не создаётся напрямую)
apiVersion: v1
kind: Pod
metadata:
  name: myapp
  labels:
    app: myapp
spec:
  containers:
    - name: myapp
      image: myapp:v1.0.0
      ports:
        - containerPort: 8080
```

**Deployment** — управляет ReplicaSets и обеспечивает декларативные обновления.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  labels:
    app: myapp
spec:
  replicas: 3  # Количество Pod'ов
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: myapp
          image: myapp:v1.0.0
          ports:
            - containerPort: 8080
```

**Service** — стабильный endpoint для доступа к Pod'ам.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp  # Выбирает Pod'ы с этим label
  ports:
    - port: 80        # Порт Service
      targetPort: 8080 # Порт контейнера
  type: ClusterIP  # Внутренний IP в кластере
```

**Взаимосвязь:**

```
                    ┌─────────────────────────────────────────────┐
                    │              Deployment                      │
                    │  ┌─────────────────────────────────────┐    │
                    │  │           ReplicaSet                 │    │
                    │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐│    │
User → Service ────►│  │  │  Pod 1  │ │  Pod 2  │ │  Pod 3  ││    │
       (myapp)      │  │  │ :8080   │ │ :8080   │ │ :8080   ││    │
                    │  │  └─────────┘ └─────────┘ └─────────┘│    │
                    │  └─────────────────────────────────────┘    │
                    └─────────────────────────────────────────────┘
```

### Deployment манифест для Go сервиса

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: production
  labels:
    app: myapp
    version: v1.0.0
spec:
  replicas: 3

  # Стратегия обновления
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Макс. дополнительных Pod'ов при обновлении
      maxUnavailable: 0  # Мин. доступных Pod'ов (zero-downtime)

  selector:
    matchLabels:
      app: myapp

  template:
    metadata:
      labels:
        app: myapp
        version: v1.0.0
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/metrics"

    spec:
      # Security context для Pod
      securityContext:
        runAsNonRoot: true
        runAsUser: 65534
        runAsGroup: 65534
        fsGroup: 65534

      containers:
        - name: myapp
          image: ghcr.io/myorg/myapp:v1.0.0
          imagePullPolicy: IfNotPresent

          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
            - name: metrics
              containerPort: 9090
              protocol: TCP

          # Переменные из ConfigMap и Secret
          env:
            - name: ENV
              value: "production"
            - name: LOG_LEVEL
              value: "info"
            - name: DB_HOST
              valueFrom:
                configMapKeyRef:
                  name: myapp-config
                  key: db-host
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: myapp-secrets
                  key: db-password

          # Или из envFrom
          envFrom:
            - configMapRef:
                name: myapp-config
            - secretRef:
                name: myapp-secrets

          # Health checks (подробнее ниже)
          livenessProbe:
            httpGet:
              path: /health/live
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3

          readinessProbe:
            httpGet:
              path: /health/ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3

          startupProbe:
            httpGet:
              path: /health/live
              port: http
            initialDelaySeconds: 0
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 30  # 30 * 5s = 2.5 минуты на старт

          # Ресурсы (подробнее ниже)
          resources:
            requests:
              memory: "64Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "500m"

          # Security context для контейнера
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL

      # Распределение по нодам
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchLabels:
                    app: myapp
                topologyKey: kubernetes.io/hostname

      # Graceful shutdown
      terminationGracePeriodSeconds: 30
```

### Service и Ingress

**ClusterIP Service (внутренний):**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
  namespace: production
spec:
  type: ClusterIP  # Доступен только внутри кластера
  selector:
    app: myapp
  ports:
    - name: http
      port: 80
      targetPort: 8080
    - name: grpc
      port: 9090
      targetPort: 9090
```

**NodePort Service (внешний через порт ноды):**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-nodeport
spec:
  type: NodePort
  selector:
    app: myapp
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080  # 30000-32767
```

**LoadBalancer Service (облачный LB):**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-lb
spec:
  type: LoadBalancer  # AWS ELB, GCP GLB, Azure LB
  selector:
    app: myapp
  ports:
    - port: 80
      targetPort: 8080
```

**Ingress (HTTP маршрутизация):**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  namespace: production
  annotations:
    # Для nginx ingress controller
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    # Rate limiting
    nginx.ingress.kubernetes.io/limit-rps: "100"

spec:
  ingressClassName: nginx

  # TLS
  tls:
    - hosts:
        - api.example.com
      secretName: api-tls-secret

  rules:
    - host: api.example.com
      http:
        paths:
          - path: /api/v1
            pathType: Prefix
            backend:
              service:
                name: myapp
                port:
                  number: 80

          - path: /health
            pathType: Exact
            backend:
              service:
                name: myapp
                port:
                  number: 80
```

### ConfigMaps и Secrets

**ConfigMap:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
  namespace: production
data:
  # Простые значения
  db-host: "postgres.production.svc.cluster.local"
  db-port: "5432"
  db-name: "myapp"
  log-level: "info"

  # Файл конфигурации
  config.yaml: |
    server:
      port: 8080
      read_timeout: 5s
      write_timeout: 10s
    database:
      max_connections: 25
      max_idle: 5
```

**Secret:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secrets
  namespace: production
type: Opaque
data:
  # Значения в base64
  db-password: cGFzc3dvcmQxMjM=  # echo -n 'password123' | base64
  api-key: c2VjcmV0LWFwaS1rZXk=
stringData:
  # Или plain text (K8s закодирует)
  jwt-secret: "my-super-secret-jwt-key"
```

**Использование в Pod:**

```yaml
spec:
  containers:
    - name: myapp
      # Как переменные окружения
      env:
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: myapp-config
              key: db-host
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: myapp-secrets
              key: db-password

      # Или все значения из ConfigMap/Secret
      envFrom:
        - configMapRef:
            name: myapp-config
        - secretRef:
            name: myapp-secrets

      # Как файлы (volume mount)
      volumeMounts:
        - name: config-volume
          mountPath: /app/config
          readOnly: true

  volumes:
    - name: config-volume
      configMap:
        name: myapp-config
        items:
          - key: config.yaml
            path: config.yaml
```

> ⚠️ **Безопасность Secrets**: K8s Secrets хранятся в etcd в base64 (не шифрование!). Для production используйте:
> - Sealed Secrets (Bitnami)
> - External Secrets Operator + Vault/AWS SM
> - SOPS + GitOps

### Health Probes: liveness, readiness, startup

**Три типа проверок:**

| Probe | Назначение | При неудаче |
|-------|------------|-------------|
| **Liveness** | Приложение живо? | Перезапуск контейнера |
| **Readiness** | Готов принимать трафик? | Исключение из Service |
| **Startup** | Завершена инициализация? | Блокирует liveness/readiness |

**Go endpoints:**

```go
// internal/health/health.go
package health

import (
    "context"
    "database/sql"
    "encoding/json"
    "net/http"
    "sync"
    "time"

    "github.com/redis/go-redis/v9"
)

type Checker struct {
    db    *sql.DB
    redis *redis.Client
}

type Status struct {
    Status    string            `json:"status"`
    Checks    map[string]string `json:"checks,omitempty"`
    Timestamp time.Time         `json:"timestamp"`
}

// Liveness — приложение работает?
// Не проверяет внешние зависимости
func (c *Checker) LivenessHandler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(Status{
        Status:    "ok",
        Timestamp: time.Now(),
    })
}

// Readiness — готов принимать трафик?
// Проверяет все зависимости
func (c *Checker) ReadinessHandler(w http.ResponseWriter, r *http.Request) {
    ctx, cancel := context.WithTimeout(r.Context(), 3*time.Second)
    defer cancel()

    checks := make(map[string]string)
    var mu sync.Mutex
    var wg sync.WaitGroup
    allHealthy := true

    // Параллельная проверка зависимостей
    wg.Add(2)

    // Проверка PostgreSQL
    go func() {
        defer wg.Done()
        status := "ok"
        if err := c.db.PingContext(ctx); err != nil {
            status = "error: " + err.Error()
            allHealthy = false
        }
        mu.Lock()
        checks["postgres"] = status
        mu.Unlock()
    }()

    // Проверка Redis
    go func() {
        defer wg.Done()
        status := "ok"
        if err := c.redis.Ping(ctx).Err(); err != nil {
            status = "error: " + err.Error()
            allHealthy = false
        }
        mu.Lock()
        checks["redis"] = status
        mu.Unlock()
    }()

    wg.Wait()

    w.Header().Set("Content-Type", "application/json")
    status := Status{
        Status:    "ok",
        Checks:    checks,
        Timestamp: time.Now(),
    }

    if !allHealthy {
        status.Status = "degraded"
        w.WriteHeader(http.StatusServiceUnavailable)
    }

    json.NewEncoder(w).Encode(status)
}
```

**Kubernetes манифест:**

```yaml
spec:
  containers:
    - name: myapp
      # Liveness — перезапуск при зависании
      livenessProbe:
        httpGet:
          path: /health/live
          port: 8080
        initialDelaySeconds: 5    # Ждём перед первой проверкой
        periodSeconds: 10         # Интервал проверок
        timeoutSeconds: 3         # Таймаут одной проверки
        failureThreshold: 3       # Сколько неудач до перезапуска

      # Readiness — исключение из балансировки
      readinessProbe:
        httpGet:
          path: /health/ready
          port: 8080
        initialDelaySeconds: 5
        periodSeconds: 5
        timeoutSeconds: 3
        failureThreshold: 3
        successThreshold: 1       # Сколько успехов до ready

      # Startup — для медленного старта
      startupProbe:
        httpGet:
          path: /health/live
          port: 8080
        periodSeconds: 5
        failureThreshold: 30      # 30 * 5s = 2.5 мин на старт
        # После успеха startup, включаются liveness/readiness
```

> 💡 **Для C# разработчиков**: В ASP.NET Core вы используете `services.AddHealthChecks()` и `.AddCheck<T>()`. В Go реализуете HTTP endpoints вручную, но логика та же: liveness для "жив ли процесс", readiness для "готов ли к трафику".

### Resource Limits и Requests

**Go-специфичные настройки:**

```yaml
spec:
  containers:
    - name: myapp
      resources:
        # Requests — гарантированные ресурсы (scheduling)
        requests:
          memory: "64Mi"   # Go приложение стартует с ~10-20 MB
          cpu: "100m"      # 0.1 CPU core

        # Limits — максимум (throttling/OOM kill)
        limits:
          memory: "256Mi"  # Go GC учитывает лимит (GOMEMLIMIT)
          cpu: "500m"      # 0.5 CPU core

      env:
        # GOMEMLIMIT (Go 1.19+) — мягкий лимит для GC
        # Должен быть ~80-90% от memory limit
        - name: GOMEMLIMIT
          value: "200MiB"

        # GOMAXPROCS — количество потоков (P в GMP)
        # По умолчанию = все CPU, но в K8s видит все CPU ноды!
        - name: GOMAXPROCS
          value: "2"  # Или используйте automaxprocs
```

#### Go 1.25+: container-aware GOMAXPROCS встроен в runtime

> 🚀 **Go 1.25** (август 2025): Go runtime **автоматически** читает cgroup CPU limits. `uber-go/automaxprocs` больше **не нужен** для Go 1.25+.

```go
// Go 1.25+ — GOMAXPROCS устанавливается автоматически
// из cgroup CPU limits при запуске в контейнере.
// Ничего дополнительно не нужно!
func main() {
    // runtime сам прочитает /sys/fs/cgroup/cpu.max
    // и установит GOMAXPROCS = ceil(quota / period)
    startServer()
}
```

**Для Go < 1.25 используйте `automaxprocs` (рекомендуется):**

```go
import _ "go.uber.org/automaxprocs"

func main() {
    // automaxprocs автоматически устанавливает GOMAXPROCS
    // на основе CPU limits в Kubernetes
}
```

```bash
go get go.uber.org/automaxprocs
```

| Версия Go | Решение |
|-----------|---------|
| Go 1.25+ | Встроено в runtime автоматически |
| Go < 1.25 | `go.uber.org/automaxprocs` |
| Все версии | `GOMAXPROCS=N` env var (явно) |

**Почему это важно:**

```
Без GOMAXPROCS/automaxprocs:
┌─────────────────────────────────────────────────────────────┐
│ Node с 32 CPU                                                │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Pod с limits.cpu: 500m                                  │ │
│ │ GOMAXPROCS = 32 (видит все CPU ноды!)                   │ │
│ │ → Создаёт 32 P, но получает только 0.5 CPU              │ │
│ │ → Постоянное переключение контекста                     │ │
│ │ → Деградация производительности                         │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

С automaxprocs:
┌─────────────────────────────────────────────────────────────┐
│ Node с 32 CPU                                                │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Pod с limits.cpu: 500m                                  │ │
│ │ GOMAXPROCS = 1 (автоматически из cgroup)                │ │
│ │ → Оптимальная работа с выделенными ресурсами            │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### HPA: автоскейлинг

**Horizontal Pod Autoscaler** автоматически масштабирует количество Pod'ов.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp

  minReplicas: 2   # Минимум для HA
  maxReplicas: 10  # Максимум

  metrics:
    # По CPU
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70  # 70% от requests.cpu

    # По памяти
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80

    # По custom метрике (требует Prometheus Adapter)
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "1000"

  # Поведение масштабирования
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Ждём 5 мин перед scale down
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0  # Scale up сразу
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
        - type: Pods
          value: 4
          periodSeconds: 15
      selectPolicy: Max
```

**Проверка:**

```bash
# Статус HPA
kubectl get hpa myapp-hpa

# Детали
kubectl describe hpa myapp-hpa

# Нагрузочное тестирование
kubectl run -it --rm load-generator --image=busybox -- sh
# while true; do wget -qO- http://myapp/api/users; done
```

---

## CI/CD интеграция

### GitHub Actions для Go + Docker

```yaml
# .github/workflows/build.yml
name: Build and Push

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Go
        uses: actions/setup-go@v5
        with:
          go-version: '1.23'
          cache: true

      - name: Run tests
        run: go test -race -coverprofile=coverage.out ./...

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage.out

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            VERSION=${{ github.ref_name }}
            COMMIT=${{ github.sha }}
            BUILD_TIME=${{ github.event.head_commit.timestamp }}

      - name: Scan for vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload scan results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'
```

### Multi-platform builds

```dockerfile
# syntax=docker/dockerfile:1

# Поддержка multi-platform через BUILDPLATFORM/TARGETPLATFORM
FROM --platform=$BUILDPLATFORM golang:1.23-alpine AS builder

# Целевая платформа
ARG TARGETOS
ARG TARGETARCH

WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download
COPY . .

# Кросс-компиляция для целевой платформы
RUN CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH \
    go build -ldflags="-s -w" -o /app/server ./cmd/server

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /app/server /server
USER nonroot:nonroot
ENTRYPOINT ["/server"]
```

**Сборка:**

```bash
# Сборка для нескольких платформ
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --tag myapp:latest \
    --push \
    .

# Локальная сборка для текущей платформы
docker buildx build \
    --load \
    --tag myapp:local \
    .
```

### Container Registry

**GitHub Container Registry (GHCR):**

```bash
# Логин
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Push
docker push ghcr.io/myorg/myapp:v1.0.0
```

**Docker Hub:**

```bash
docker login
docker push myorg/myapp:v1.0.0
```

**AWS ECR:**

```bash
# Получение токена
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Push
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:v1.0.0
```

### Версионирование образов

**Рекомендуемая стратегия:**

| Тег | Использование | Пример |
|-----|---------------|--------|
| `v1.0.0` | Релизы (SemVer) | Immutable, production |
| `v1.0` | Major.Minor | Patch updates |
| `v1` | Major only | Minor updates |
| `sha-abc123` | Конкретный коммит | CI/CD, debugging |
| `main` | Ветка | Development |
| `latest` | Последний релиз | Не рекомендуется в prod |

```bash
# Теги из Git
VERSION=$(git describe --tags --always)
COMMIT=$(git rev-parse --short HEAD)

docker build \
    --tag myapp:$VERSION \
    --tag myapp:$COMMIT \
    --tag myapp:latest \
    .
```

---

## Сравнение с .NET

### ASP.NET Core Docker vs Go Docker

**ASP.NET Core:**

```dockerfile
# ASP.NET Core multi-stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY *.csproj .
RUN dotnet restore
COPY . .
RUN dotnet publish -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "MyApp.dll"]
```

**Go:**

```dockerfile
# Go multi-stage
FROM golang:1.23-alpine AS builder
WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /app/server ./cmd/server

FROM scratch
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /app/server /server
USER 65534:65534
ENTRYPOINT ["/server"]
```

**Сравнение:**

| Аспект | ASP.NET Core 8 | Go 1.23 |
|--------|----------------|---------|
| SDK образ | ~900 MB | ~850 MB |
| Runtime образ | ~220 MB (aspnet) | ~2 MB (scratch) |
| Финальный образ | ~250-300 MB | ~5-15 MB |
| Runtime в образе | CLR обязателен | Не нужен |
| Cold start | ~500ms - 2s | ~10-50ms |
| Memory footprint | ~100-300 MB | ~10-50 MB |
| Self-contained | ❌ (нужен aspnet) | ✅ (статический бинарник) |

### .NET Aspire vs Go + Compose

**.NET Aspire** (появился в .NET 8):

```csharp
// Program.cs
var builder = DistributedApplication.CreateBuilder(args);

var cache = builder.AddRedis("cache");
var postgres = builder.AddPostgres("postgres")
    .AddDatabase("mydb");

builder.AddProject<Projects.MyApp>("myapp")
    .WithReference(cache)
    .WithReference(postgres);

builder.Build().Run();
```

**Преимущества Aspire:**
- Интегрирован в Visual Studio
- Типизированные ресурсы
- Автоматический service discovery
- Dashboard из коробки
- Dev/Prod конфигурация

**Go + Docker Compose:**

```yaml
# compose.yaml
services:
  app:
    build: .
    environment:
      - REDIS_ADDR=redis:6379
      - DB_HOST=postgres
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started

  postgres:
    image: postgres:16-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]

  redis:
    image: redis:7-alpine
```

**Преимущества Go + Compose:**
- Полный контроль
- Работает везде (не только Visual Studio)
- Прозрачность конфигурации
- Легко расширять

> 💡 **Для C# разработчиков**: .NET Aspire — это higher-level абстракция над Docker Compose. В Go нет аналога — вы работаете напрямую с Compose/K8s манифестами. Это требует больше работы, но даёт полный контроль.

### Размеры образов

| Приложение | .NET 8 | Go | Разница |
|------------|--------|-----|---------|
| Hello World | ~220 MB | ~2 MB | 110x |
| REST API | ~250 MB | ~8 MB | 31x |
| API + DB driver | ~270 MB | ~12 MB | 22x |
| Микросервис | ~300 MB | ~15 MB | 20x |

**Влияние на:**

| Аспект | Большой образ | Маленький образ |
|--------|---------------|-----------------|
| Pull time | Минуты | Секунды |
| Registry storage | $$$$ | $ |
| Cold start (serverless) | Медленный | Быстрый |
| Network transfer | Много | Мало |
| Attack surface | Большая | Минимальная |

---

## Типичные ошибки C# разработчиков

### 1. Использование runtime-образов как базовых

```dockerfile
# ❌ Ошибка: думают, что Go нужен runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0  # Зачем??
COPY myapp /myapp
# Лишние 220 MB

# ✅ Правильно: Go — статический бинарник
FROM scratch
COPY myapp /myapp
# 0 MB базового образа
```

### 2. Не используют multi-stage builds

```dockerfile
# ❌ Ошибка: Go SDK в финальном образе
FROM golang:1.23
COPY . .
RUN go build -o /app/server
CMD ["/app/server"]
# Размер: ~850 MB

# ✅ Правильно: multi-stage
FROM golang:1.23 AS builder
# ...build...

FROM scratch
COPY --from=builder /app/server /server
# Размер: ~5 MB
```

### 3. CGO_ENABLED=1 по умолчанию

```dockerfile
# ❌ Ошибка: динамическая линковка
FROM golang:1.23-alpine AS builder
RUN go build -o /app/server

FROM scratch
COPY --from=builder /app/server /server
# Ошибка: "not found" — бинарник зависит от libc

# ✅ Правильно: статическая линковка
RUN CGO_ENABLED=0 go build -o /app/server
```

### 4. Файловое логирование в контейнере

```go
// ❌ Ошибка: логи в файл
file, _ := os.OpenFile("/var/log/app.log", os.O_CREATE|os.O_WRONLY, 0666)
logger := slog.New(slog.NewJSONHandler(file, nil))

// ✅ Правильно: stdout/stderr (12-Factor)
logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
```

### 5. Игнорирование graceful shutdown

```go
// ❌ Ошибка: нет обработки SIGTERM
func main() {
    http.ListenAndServe(":8080", nil) // Docker kill через 10s
}

// ✅ Правильно: graceful shutdown
quit := make(chan os.Signal, 1)
signal.Notify(quit, syscall.SIGTERM)
go func() {
    <-quit
    srv.Shutdown(ctx)
}()
```

### 6. Запуск от root

```dockerfile
# ❌ Ошибка: по умолчанию root
FROM alpine
COPY server /server
ENTRYPOINT ["/server"]

# ✅ Правильно: non-root
FROM alpine
RUN adduser -D -H -u 10001 appuser
USER appuser
COPY server /server
ENTRYPOINT ["/server"]
```

### 7. Хранение состояния в контейнере

```go
// ❌ Ошибка: данные в локальном файле
os.WriteFile("/app/data/users.json", data, 0644)
// При перезапуске контейнера данные потеряются!

// ✅ Правильно: внешнее хранилище
db.Exec("INSERT INTO users ...")
redis.Set(ctx, "user:1", data, 0)
```

### 8. depends_on без healthcheck

```yaml
# ❌ Ошибка: depends_on без condition
services:
  app:
    depends_on:
      - postgres  # Postgres может быть не готов!

# ✅ Правильно: ждём healthcheck
services:
  app:
    depends_on:
      postgres:
        condition: service_healthy
  postgres:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
```

### 9. Отсутствие .dockerignore

```
# ❌ Без .dockerignore:
# - .git попадает в контекст (~100 MB)
# - .env с секретами в образе
# - node_modules, vendor

# ✅ Создайте .dockerignore:
.git
.env
*.md
Dockerfile
```

### 10. Shell форма вместо exec

```dockerfile
# ❌ Ошибка: shell форма
CMD ./server
# SIGTERM не доходит до приложения!

# ✅ Правильно: exec форма
CMD ["./server"]
# SIGTERM напрямую к приложению
```

---

## Практические примеры

### Пример 1: Production Dockerfile с multi-stage и distroless

**Задача**: Создать production-ready Dockerfile для Go микросервиса с:
- Multi-stage build
- Distroless runtime
- Версионирование через build args
- Health check
- Безопасность (non-root, minimal image)

**Структура проекта:**

```
myapp/
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── config/
│   │   └── config.go
│   ├── health/
│   │   └── health.go
│   └── handler/
│       └── handler.go
├── go.mod
├── go.sum
├── Dockerfile
└── .dockerignore
```

**cmd/server/main.go:**

```go
package main

import (
    "context"
    "flag"
    "fmt"
    "log/slog"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "myapp/internal/config"
    "myapp/internal/handler"
    "myapp/internal/health"
)

// Версия, внедряется при компиляции через ldflags
var (
    Version   = "dev"
    Commit    = "unknown"
    BuildTime = "unknown"
)

func main() {
    // Health check режим для Docker HEALTHCHECK
    healthCheck := flag.Bool("health", false, "выполнить health check")
    flag.Parse()

    if *healthCheck {
        if err := health.Check("http://localhost:8080/health/live"); err != nil {
            os.Exit(1)
        }
        os.Exit(0)
    }

    // Настройка логгера
    logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
        Level: slog.LevelInfo,
    }))
    slog.SetDefault(logger)

    logger.Info("запуск приложения",
        "version", Version,
        "commit", Commit,
        "build_time", BuildTime,
    )

    // Загрузка конфигурации
    cfg, err := config.Load()
    if err != nil {
        logger.Error("ошибка загрузки конфигурации", "error", err)
        os.Exit(1)
    }

    // Создание обработчиков
    h := handler.New(logger)
    healthHandler := health.NewHandler()

    // Настройка роутера
    mux := http.NewServeMux()
    mux.HandleFunc("/api/v1/users", h.Users)
    mux.HandleFunc("/health/live", healthHandler.Live)
    mux.HandleFunc("/health/ready", healthHandler.Ready)
    mux.HandleFunc("/version", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, `{"version":"%s","commit":"%s","build_time":"%s"}`,
            Version, Commit, BuildTime)
    })

    // Настройка сервера
    srv := &http.Server{
        Addr:         fmt.Sprintf(":%d", cfg.Port),
        Handler:      mux,
        ReadTimeout:  cfg.ReadTimeout,
        WriteTimeout: cfg.WriteTimeout,
        IdleTimeout:  120 * time.Second,
    }

    // Graceful shutdown
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

    go func() {
        logger.Info("сервер запущен", "port", cfg.Port)
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            logger.Error("ошибка сервера", "error", err)
            os.Exit(1)
        }
    }()

    <-quit
    logger.Info("получен сигнал завершения, начинаем graceful shutdown")

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := srv.Shutdown(ctx); err != nil {
        logger.Error("ошибка shutdown", "error", err)
        os.Exit(1)
    }

    logger.Info("сервер остановлен корректно")
}
```

**internal/health/health.go:**

```go
package health

import (
    "encoding/json"
    "net/http"
    "time"
)

type Handler struct{}

func NewHandler() *Handler {
    return &Handler{}
}

type response struct {
    Status    string `json:"status"`
    Timestamp string `json:"timestamp"`
}

// Live — проверка жизнеспособности (для liveness probe)
func (h *Handler) Live(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response{
        Status:    "ok",
        Timestamp: time.Now().UTC().Format(time.RFC3339),
    })
}

// Ready — проверка готовности (для readiness probe)
func (h *Handler) Ready(w http.ResponseWriter, r *http.Request) {
    // TODO: добавить проверку зависимостей (DB, Redis)
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response{
        Status:    "ok",
        Timestamp: time.Now().UTC().Format(time.RFC3339),
    })
}

// Check — клиент для health check (используется в Docker HEALTHCHECK)
func Check(url string) error {
    client := &http.Client{Timeout: 3 * time.Second}
    resp, err := client.Get(url)
    if err != nil {
        return err
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return http.ErrAbortHandler
    }
    return nil
}
```

**Dockerfile:**

```dockerfile
# syntax=docker/dockerfile:1

# =============================================================================
# Stage 1: Builder
# =============================================================================
FROM --platform=$BUILDPLATFORM golang:1.23-alpine AS builder

# Аргументы для версионирования
ARG VERSION=dev
ARG COMMIT=unknown
ARG BUILD_TIME=unknown

# Аргументы для кросс-компиляции
ARG TARGETOS
ARG TARGETARCH

# Метаданные
LABEL maintainer="team@example.com"
LABEL stage="builder"

WORKDIR /build

# Копируем зависимости (для кэширования)
COPY go.mod go.sum ./

# Скачиваем зависимости с кэшированием
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download

# Копируем исходный код
COPY . .

# Собираем статический бинарник для целевой платформы
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=${TARGETOS} GOARCH=${TARGETARCH} \
    go build \
        -ldflags="-s -w \
            -X main.Version=${VERSION} \
            -X main.Commit=${COMMIT} \
            -X main.BuildTime=${BUILD_TIME}" \
        -o /build/server \
        ./cmd/server

# =============================================================================
# Stage 2: Runtime (Distroless)
# =============================================================================
FROM gcr.io/distroless/static-debian12:nonroot

# Метаданные
LABEL maintainer="team@example.com"
LABEL org.opencontainers.image.title="MyApp"
LABEL org.opencontainers.image.description="Production Go microservice"
LABEL org.opencontainers.image.source="https://github.com/myorg/myapp"

# Копируем бинарник из builder
COPY --from=builder /build/server /server

# Используем non-root пользователя (уже настроен в :nonroot)
USER nonroot:nonroot

# Порт приложения
EXPOSE 8080

# Health check (использует сам бинарник)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["/server", "-health"]

# Точка входа
ENTRYPOINT ["/server"]
```

**.dockerignore:**

```dockerignore
# Git
.git
.gitignore
.github

# IDE
.idea
.vscode
*.swp
*.swo

# Документация
*.md
!README.md
docs/

# Тесты
*_test.go
**/*_test.go
testdata/
coverage.out

# Конфигурация разработки
.env
.env.*
*.local
.air.toml

# Docker
Dockerfile*
docker-compose*.yml
.dockerignore

# Build артефакты
bin/
dist/
tmp/
*.exe

# Секреты
*.pem
*.key
secrets/
credentials/
```

**Сборка и запуск:**

```bash
# Сборка с версионированием
docker build \
    --build-arg VERSION=$(git describe --tags --always) \
    --build-arg COMMIT=$(git rev-parse --short HEAD) \
    --build-arg BUILD_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
    -t myapp:$(git describe --tags --always) \
    .

# Запуск
docker run -d \
    --name myapp \
    -p 8080:8080 \
    -e LOG_LEVEL=info \
    myapp:latest

# Проверка
curl http://localhost:8080/version
curl http://localhost:8080/health/live
docker inspect --format='{{.State.Health.Status}}' myapp

# Размер образа
docker images myapp
# REPOSITORY   TAG       SIZE
# myapp        v1.0.0    12.3MB
```

---

### Пример 2: Docker Compose для микросервисов

**Задача**: Создать полное локальное окружение для разработки с:
- Go API сервис
- PostgreSQL с инициализацией
- Redis для кэширования
- Prometheus + Grafana для мониторинга
- Hot reload для разработки

**Структура проекта:**

```
myapp/
├── cmd/server/main.go
├── internal/...
├── scripts/
│   └── init.sql
├── config/
│   └── prometheus.yml
├── Dockerfile
├── Dockerfile.dev
├── compose.yaml
├── compose.override.yaml
├── .air.toml
└── .env.example
```

**compose.yaml (база):**

```yaml
# compose.yaml — базовая конфигурация
name: myapp

services:
  # ==========================================================================
  # Go API сервис
  # ==========================================================================
  app:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        - VERSION=${VERSION:-dev}
    image: myapp:${VERSION:-dev}
    container_name: myapp-api
    ports:
      - "8080:8080"
      - "9090:9090"  # Metrics
    environment:
      - ENV=production
      - LOG_LEVEL=info
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_USER=myapp
      - DB_PASSWORD=${DB_PASSWORD:-secret}
      - DB_NAME=myapp
      - DB_SSLMODE=disable
      - REDIS_ADDR=redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["/server", "-health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    restart: unless-stopped
    networks:
      - backend

  # ==========================================================================
  # PostgreSQL
  # ==========================================================================
  postgres:
    image: postgres:16-alpine
    container_name: myapp-postgres
    environment:
      POSTGRES_USER: myapp
      POSTGRES_PASSWORD: ${DB_PASSWORD:-secret}
      POSTGRES_DB: myapp
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U myapp -d myapp"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s
    restart: unless-stopped
    networks:
      - backend

  # ==========================================================================
  # Redis
  # ==========================================================================
  redis:
    image: redis:7-alpine
    container_name: myapp-redis
    command: >
      redis-server
      --appendonly yes
      --maxmemory 256mb
      --maxmemory-policy allkeys-lru
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    restart: unless-stopped
    networks:
      - backend

# ==========================================================================
# Volumes
# ==========================================================================
volumes:
  postgres-data:
  redis-data:

# ==========================================================================
# Networks
# ==========================================================================
networks:
  backend:
    driver: bridge
```

**compose.override.yaml (development):**

```yaml
# compose.override.yaml — автоматически применяется к compose.yaml
# Переопределения для разработки
services:
  app:
    build:
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app:cached
      - go-mod-cache:/go/pkg/mod
      - go-build-cache:/root/.cache/go-build
    command: ["air", "-c", ".air.toml"]
    environment:
      - ENV=development
      - LOG_LEVEL=debug

  # Adminer для работы с БД
  adminer:
    image: adminer
    container_name: myapp-adminer
    ports:
      - "8081:8080"
    depends_on:
      - postgres
    networks:
      - backend

  # Redis Commander
  redis-commander:
    image: rediscommander/redis-commander:latest
    container_name: myapp-redis-commander
    environment:
      - REDIS_HOSTS=local:redis:6379
    ports:
      - "8082:8081"
    depends_on:
      - redis
    networks:
      - backend

volumes:
  go-mod-cache:
  go-build-cache:
```

**compose.monitoring.yaml (мониторинг):**

```yaml
# compose.monitoring.yaml — для production/staging с мониторингом
# Использование: docker compose -f compose.yaml -f compose.monitoring.yaml up

services:
  # ==========================================================================
  # Prometheus
  # ==========================================================================
  prometheus:
    image: prom/prometheus:latest
    container_name: myapp-prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.enable-lifecycle'
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    ports:
      - "9091:9090"
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:9090/-/healthy"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    networks:
      - backend

  # ==========================================================================
  # Grafana
  # ==========================================================================
  grafana:
    image: grafana/grafana:latest
    container_name: myapp-grafana
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-data:/var/lib/grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    restart: unless-stopped
    networks:
      - backend

  # ==========================================================================
  # Jaeger (Tracing)
  # ==========================================================================
  jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: myapp-jaeger
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    ports:
      - "16686:16686"  # UI
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP
    restart: unless-stopped
    networks:
      - backend

volumes:
  prometheus-data:
  grafana-data:
```

**config/prometheus.yml:**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'myapp'
    static_configs:
      - targets: ['app:9090']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

**scripts/init.sql:**

```sql
-- Инициализация базы данных
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Тестовые данные
INSERT INTO users (email, name) VALUES
    ('alice@example.com', 'Alice'),
    ('bob@example.com', 'Bob')
ON CONFLICT (email) DO NOTHING;
```

**Dockerfile.dev:**

```dockerfile
FROM golang:1.23-alpine

# Установка air для hot reload
RUN go install github.com/air-verse/air@latest

# Установка утилит для отладки
RUN apk add --no-cache git curl

WORKDIR /app

# Копируем go.mod для начальной загрузки
COPY go.mod go.sum ./
RUN go mod download

# Исходный код будет смонтирован через volume
CMD ["air", "-c", ".air.toml"]
```

**.air.toml:**

```toml
root = "."
tmp_dir = "tmp"

[build]
  cmd = "go build -o ./tmp/main ./cmd/server"
  bin = "./tmp/main"
  delay = 500
  exclude_dir = ["assets", "tmp", "vendor", "testdata"]
  exclude_regex = ["_test.go"]
  include_ext = ["go", "yaml", "yml", "toml"]
  kill_delay = 500

[log]
  time = true
  main_only = false

[color]
  main = "magenta"
  watcher = "cyan"
  build = "yellow"
  runner = "green"

[misc]
  clean_on_exit = true
```

**.env.example:**

```bash
# Копировать в .env и заполнить

# Database
DB_PASSWORD=your-secure-password

# Monitoring
GRAFANA_PASSWORD=your-grafana-password

# App
VERSION=dev
```

**Использование:**

```bash
# Development (с hot reload, adminer, redis-commander)
docker compose up

# Production (только app + deps)
docker compose -f compose.yaml up

# Production с мониторингом
docker compose -f compose.yaml -f compose.monitoring.yaml up

# Сборка и запуск
docker compose build
docker compose up -d

# Логи
docker compose logs -f app

# Остановка
docker compose down

# Очистка (включая volumes)
docker compose down -v
```

---

### Пример 3: Kubernetes Deployment с health checks и HPA

**Задача**: Создать полный набор K8s манифестов для production деплоя Go сервиса.

**Структура:**

```
k8s/
├── namespace.yaml
├── configmap.yaml
├── secret.yaml
├── deployment.yaml
├── service.yaml
├── ingress.yaml
├── hpa.yaml
└── kustomization.yaml
```

**k8s/namespace.yaml:**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: myapp
  labels:
    name: myapp
    environment: production
```

**k8s/configmap.yaml:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
  namespace: myapp
data:
  # Конфигурация приложения
  LOG_LEVEL: "info"
  DB_HOST: "postgres.database.svc.cluster.local"
  DB_PORT: "5432"
  DB_NAME: "myapp"
  DB_SSLMODE: "require"
  REDIS_ADDR: "redis.cache.svc.cluster.local:6379"

  # Конфигурационный файл (монтируется как volume)
  config.yaml: |
    server:
      port: 8080
      read_timeout: 5s
      write_timeout: 10s
    metrics:
      port: 9090
      path: /metrics
```

**k8s/secret.yaml:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secrets
  namespace: myapp
type: Opaque
stringData:
  # В реальности используйте Sealed Secrets или External Secrets
  DB_PASSWORD: "super-secret-password"
  API_KEY: "secret-api-key"
```

**k8s/deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: myapp
  labels:
    app: myapp
    version: v1.0.0
spec:
  replicas: 3

  # Стратегия обновления
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0

  selector:
    matchLabels:
      app: myapp

  template:
    metadata:
      labels:
        app: myapp
        version: v1.0.0
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/metrics"

    spec:
      # Security context для Pod
      securityContext:
        runAsNonRoot: true
        runAsUser: 65534
        runAsGroup: 65534
        fsGroup: 65534
        seccompProfile:
          type: RuntimeDefault

      # Service Account
      serviceAccountName: myapp

      containers:
        - name: myapp
          image: ghcr.io/myorg/myapp:v1.0.0
          imagePullPolicy: IfNotPresent

          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
            - name: metrics
              containerPort: 9090
              protocol: TCP

          # Переменные окружения
          env:
            - name: ENV
              value: "production"
            # GOMEMLIMIT для Go GC (80% от limits.memory)
            - name: GOMEMLIMIT
              value: "200MiB"
            # Pod info
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace

          # Переменные из ConfigMap и Secret
          envFrom:
            - configMapRef:
                name: myapp-config
            - secretRef:
                name: myapp-secrets

          # Volume mounts
          volumeMounts:
            - name: config
              mountPath: /app/config
              readOnly: true
            - name: tmp
              mountPath: /tmp

          # Liveness probe — приложение живо?
          livenessProbe:
            httpGet:
              path: /health/live
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3

          # Readiness probe — готов к трафику?
          readinessProbe:
            httpGet:
              path: /health/ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
            successThreshold: 1

          # Startup probe — для медленного старта
          startupProbe:
            httpGet:
              path: /health/live
              port: http
            periodSeconds: 5
            failureThreshold: 30

          # Resources
          resources:
            requests:
              memory: "64Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "500m"

          # Security context для контейнера
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL

      # Volumes
      volumes:
        - name: config
          configMap:
            name: myapp-config
            items:
              - key: config.yaml
                path: config.yaml
        - name: tmp
          emptyDir: {}

      # Anti-affinity — распределение по нодам
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchLabels:
                    app: myapp
                topologyKey: kubernetes.io/hostname

      # Graceful shutdown
      terminationGracePeriodSeconds: 30

      # Image pull secrets (если private registry)
      # imagePullSecrets:
      #   - name: ghcr-secret
```

**k8s/service.yaml:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
  namespace: myapp
  labels:
    app: myapp
spec:
  type: ClusterIP
  selector:
    app: myapp
  ports:
    - name: http
      port: 80
      targetPort: 8080
      protocol: TCP
    - name: metrics
      port: 9090
      targetPort: 9090
      protocol: TCP
```

**k8s/ingress.yaml:**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp
  namespace: myapp
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.example.com
      secretName: myapp-tls
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: myapp
                port:
                  number: 80
```

**k8s/hpa.yaml:**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp
  namespace: myapp
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp

  minReplicas: 2
  maxReplicas: 10

  metrics:
    # CPU utilization
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70

    # Memory utilization
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80

  # Поведение масштабирования
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
        - type: Pods
          value: 4
          periodSeconds: 15
      selectPolicy: Max
```

**k8s/kustomization.yaml:**

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: myapp

resources:
  - namespace.yaml
  - configmap.yaml
  - secret.yaml
  - deployment.yaml
  - service.yaml
  - ingress.yaml
  - hpa.yaml

commonLabels:
  app.kubernetes.io/name: myapp
  app.kubernetes.io/part-of: myapp-system

images:
  - name: ghcr.io/myorg/myapp
    newTag: v1.0.0
```

**Деплой:**

```bash
# Применение всех манифестов
kubectl apply -k k8s/

# Или по отдельности
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

# Проверка статуса
kubectl -n myapp get pods
kubectl -n myapp get svc
kubectl -n myapp get hpa

# Логи
kubectl -n myapp logs -f deployment/myapp

# Port forward для тестирования
kubectl -n myapp port-forward svc/myapp 8080:80

# Масштабирование
kubectl -n myapp scale deployment/myapp --replicas=5

# Обновление образа
kubectl -n myapp set image deployment/myapp myapp=ghcr.io/myorg/myapp:v1.1.0

# Rollout статус
kubectl -n myapp rollout status deployment/myapp

# Откат
kubectl -n myapp rollout undo deployment/myapp
```

---
