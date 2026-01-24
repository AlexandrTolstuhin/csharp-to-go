# 1.1 Установка и настройка окружения Go

## Цель
Настроить полноценное окружение для разработки на Go, которое позволит вам эффективно писать, тестировать и отлаживать код.

---

## Шаг 1: Установка Go (версия 1.22+)

### Windows

1. **Скачайте установщик**
   - Перейдите на официальный сайт: https://go.dev/dl/
   - Скачайте MSI-установщик для Windows (например, `go1.23.x.windows-amd64.msi`)

2. **Запустите установщик**
   - Запустите скачанный MSI-файл
   - Следуйте инструкциям мастера установки
   - По умолчанию Go устанавливается в `C:\Program Files\Go`

3. **Проверьте установку**
   ```bash
   go version
   ```
   Должно вывести что-то вроде: `go version go1.23.x windows/amd64`

### Альтернативный способ (через winget)
```bash
winget install GoLang.Go
```

### Linux

```bash
# Скачиваем последнюю версию
wget https://go.dev/dl/go1.23.x.linux-amd64.tar.gz

# Удаляем старую установку (если есть)
sudo rm -rf /usr/local/go

# Распаковываем в /usr/local
sudo tar -C /usr/local -xzf go1.23.x.linux-amd64.tar.gz

# Проверяем установку
go version
```

### macOS

```bash
# Через Homebrew
brew install go

# Или скачать PKG-установщик с https://go.dev/dl/
```

---

## Шаг 2: Настройка переменных окружения

### Основные переменные

#### GOROOT
**Что это**: Директория, где установлен Go
**Нужно ли настраивать**: Обычно **НЕТ** — устанавливается автоматически

**Проверка**:
```bash
go env GOROOT
```

**Когда нужно настраивать вручную**:
- Если вы используете несколько версий Go
- Если установили Go в нестандартную директорию

**Windows** (если нужно):
```cmd
setx GOROOT "C:\Program Files\Go"
```

**Linux/macOS** (добавить в `~/.bashrc` или `~/.zshrc`):
```bash
export GOROOT=/usr/local/go
export PATH=$PATH:$GOROOT/bin
```

---

#### GOPATH
**Что это**: Рабочая директория для вашего Go-кода (workspace)
**Значение по умолчанию**:
- Windows: `%USERPROFILE%\go` (например, `C:\Users\alext\go`)
- Linux/macOS: `$HOME/go`

**Структура GOPATH** (устаревшая для модулей, но полезна для понимания):
```
$GOPATH/
├── bin/        # Скомпилированные исполняемые файлы
├── pkg/        # Скомпилированные пакеты (кэш)
└── src/        # Исходный код (для legacy проектов без Go Modules)
```

**Рекомендация**: Оставьте значение по умолчанию. Go Modules (появились в Go 1.11) позволяют работать в любой директории.

**Проверка**:
```bash
go env GOPATH
```

**Добавление $GOPATH/bin в PATH** (важно для установленных утилит):

**Windows**:
```cmd
setx PATH "%PATH%;%USERPROFILE%\go\bin"
```

**Linux/macOS** (добавить в `~/.bashrc` или `~/.zshrc`):
```bash
export PATH=$PATH:$GOPATH/bin
```

---

#### GO111MODULE
**Что это**: Включение/выключение Go Modules
**Значение по умолчанию**: `on` (начиная с Go 1.16)

**Проверка**:
```bash
go env GO111MODULE
```

**Рекомендация**: Оставьте `on` или пустым (автоматический режим)

---

### Go Modules (современный подход)

**Что это**: Система управления зависимостями, появившаяся в Go 1.11

**Преимущества**:
- Работа вне GOPATH
- Версионирование зависимостей
- Reproducible builds
- Идиоматичный подход для современного Go

**Инициализация модуля**:
```bash
# В директории вашего проекта
go mod init github.com/yourusername/yourproject

# Для локального проекта (без GitHub)
go mod init myproject
```

**Файлы Go Modules**:
- `go.mod` — описание модуля и зависимостей
- `go.sum` — контрольные суммы зависимостей (для безопасности)

**Основные команды**:
```bash
go mod tidy        # Удалить неиспользуемые, добавить недостающие зависимости
go mod download    # Скачать зависимости
go mod vendor      # Создать vendor-директорию с зависимостями
go mod verify      # Проверить контрольные суммы
```

**Пример go.mod**:
```go
module github.com/yourusername/myapp

go 1.23

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/lib/pq v1.10.9
)
```

---

## Шаг 3: Настройка IDE

### Вариант 1: GoLand (JetBrains) — Рекомендуется для Senior разработчиков

**Преимущества**:
- Из коробки все работает
- Мощный отладчик
- Рефакторинг
- Интеграция с Go tools
- Знакомый интерфейс для пользователей Rider/IntelliJ

**Установка**:
1. Скачайте с https://www.jetbrains.com/go/
2. Запустите установщик
3. Укажите путь к Go SDK (обычно определяется автоматически)

**Настройка**:
- **Settings → Go → GOROOT**: должен быть установлен автоматически
- **Settings → Go → Go Modules**: включено по умолчанию
- **Settings → Tools → File Watchers**: можно настроить автоматический `go fmt`

**Плагины** (опционально):
- `Protocol Buffers` — для работы с protobuf
- `Docker` — для контейнеризации

---

### Вариант 2: Visual Studio Code + Go Extension

**Установка VS Code**:
1. Скачайте с https://code.visualstudio.com/
2. Установите

**Установка Go Extension**:
1. Откройте VS Code
2. Перейдите в Extensions (`Ctrl+Shift+X`)
3. Найдите и установите **"Go"** (от Go Team at Google)

**Первая настройка**:
При открытии первого `.go` файла VS Code предложит установить Go tools:
- Нажмите **"Install All"**

**Альтернативно** (вручную):
```bash
# Откройте Command Palette (Ctrl+Shift+P)
# Введите: Go: Install/Update Tools
# Выберите все тулы и нажмите OK
```

**Устанавливаемые инструменты**:
- `gopls` — Language Server Protocol (автодополнение, навигация)
- `dlv` — Delve debugger
- `staticcheck` — статический анализ
- `golangci-lint` — мета-линтер
- И другие...

**Рекомендуемые настройки** (`settings.json`):
```json
{
  "go.useLanguageServer": true,
  "go.lintOnSave": "workspace",
  "go.formatTool": "gofmt",
  "go.lintTool": "golangci-lint",
  "editor.formatOnSave": true,
  "[go]": {
    "editor.defaultFormatter": "golang.go",
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "go.testFlags": ["-v", "-race"],
  "go.coverOnSave": true
}
```

**Полезные расширения для VS Code**:
- **Go** (обязательно)
- **Error Lens** — показывает ошибки inline
- **GitLens** — Git интеграция
- **REST Client** — тестирование HTTP API
- **Thunder Client** — альтернатива Postman

---

## Шаг 4: Настройка инструментов

### go fmt — Форматирование кода

**Что делает**: Автоматически форматирует код по стандарту Go

**Использование**:
```bash
# Форматировать один файл
go fmt main.go

# Форматировать все файлы в текущей директории
go fmt ./...
```

**Рекомендация**: Настройте автоформатирование при сохранении в вашей IDE

---

### go vet — Статический анализ

**Что делает**: Проверяет код на распространенные ошибки

**Примеры проверок**:
- Printf с неправильными аргументами
- Недостижимый код
- Неправильное использование sync
- И др.

**Использование**:
```bash
go vet ./...
```

**Пример вывода**:
```
./main.go:10:2: Printf format %d has arg name of wrong type string
```

---

### golangci-lint — Мета-линтер (обязательно!)

**Что это**: Агрегатор множества линтеров в одном инструменте

**Установка**:

**Windows**:
```bash
# Через winget
winget install golangci.golangci-lint

# Или через Go
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
```

**Linux/macOS**:
```bash
# Через скрипт
curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(go env GOPATH)/bin

# Или через Go
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
```

**Проверка установки**:
```bash
golangci-lint --version
```

**Использование**:
```bash
# Запуск с конфигурацией по умолчанию
golangci-lint run

# Запуск для всех пакетов
golangci-lint run ./...
```

**Рекомендуемая конфигурация** (`.golangci.yml` в корне проекта):
```yaml
run:
  timeout: 5m
  tests: true

linters:
  enable:
    - errcheck      # Проверка необработанных ошибок
    - gosimple      # Упрощение кода
    - govet         # Стандартный go vet
    - ineffassign   # Неиспользуемые присваивания
    - staticcheck   # Статический анализ
    - unused        # Неиспользуемый код
    - gofmt         # Форматирование
    - goimports     # Импорты
    - misspell      # Опечатки
    - revive        # Быстрая замена golint
    - gosec         # Безопасность
    - gocritic      # Всесторонние проверки
    - gocyclo       # Цикломатическая сложность
    - errorlint     # Обработка ошибок
    - bodyclose     # HTTP body закрыт
    - contextcheck  # Правильное использование context

linters-settings:
  gocyclo:
    min-complexity: 15

  govet:
    check-shadowing: true

  errcheck:
    check-type-assertions: true
    check-blank: true

issues:
  exclude-use-default: false
  max-issues-per-linter: 0
  max-same-issues: 0
```

**Интеграция с CI/CD**:
```bash
# В GitHub Actions или GitLab CI
golangci-lint run --out-format=github-actions
```

---

## Шаг 5: Создание первого проекта

### Структура простого проекта

```bash
# Создайте директорию проекта (можно где угодно, не обязательно в GOPATH)
mkdir hello-go
cd hello-go

# Инициализируйте Go модуль
go mod init hello-go
```

### Создайте файл main.go

```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, Go!")
}
```

### Запустите программу

```bash
# Запуск без компиляции
go run main.go

# Компиляция в исполняемый файл
go build

# Запуск скомпилированного файла
./hello-go         # Linux/macOS
hello-go.exe       # Windows
```

### Проверьте инструменты

```bash
# Форматирование
go fmt ./...

# Статический анализ
go vet ./...

# Линтинг
golangci-lint run
```

---

## Шаг 6: Дополнительные инструменты (опционально, но рекомендуется)

### staticcheck — Мощный статический анализатор

```bash
go install honnef.co/go/tools/cmd/staticcheck@latest

# Использование
staticcheck ./...
```

### govulncheck — Проверка уязвимостей

```bash
go install golang.org/x/vuln/cmd/govulncheck@latest

# Использование
govulncheck ./...
```

### air — Hot reload для разработки

**Установка**:
```bash
go install github.com/cosmtrek/air@latest
```

**Создайте .air.toml** (опционально):
```toml
root = "."
tmp_dir = "tmp"

[build]
cmd = "go build -o ./tmp/main ."
bin = "tmp/main"
include_ext = ["go", "tpl", "tmpl", "html"]
exclude_dir = ["assets", "tmp", "vendor"]
delay = 1000
```

**Использование**:
```bash
air
```

Теперь при изменении `.go` файлов приложение автоматически перезапустится.

---

## Проверка готовности окружения

Выполните эти команды, чтобы убедиться, что все настроено корректно:

```bash
# 1. Версия Go (должна быть 1.22+)
go version

# 2. Переменные окружения
go env GOROOT
go env GOPATH
go env GOMODCACHE

# 3. Форматирование
go fmt ./...

# 4. Vet
go vet ./...

# 5. golangci-lint
golangci-lint --version
golangci-lint run

# 6. Тесты (если есть)
go test ./...

# 7. Сборка
go build
```

---

## Полезные команды Go

```bash
# Управление модулями
go mod init <module-name>    # Создать go.mod
go mod tidy                  # Очистить зависимости
go mod download              # Скачать зависимости
go mod vendor                # Создать vendor/
go mod verify                # Проверить зависимости

# Сборка и запуск
go run main.go               # Запустить без компиляции
go build                     # Скомпилировать
go build -o myapp            # Скомпилировать с именем
go install                   # Установить в $GOPATH/bin

# Тестирование
go test                      # Запустить тесты
go test -v                   # Verbose
go test -race                # С детектором гонок
go test -cover               # С покрытием
go test ./...                # Все пакеты

# Очистка
go clean                     # Удалить скомпилированные файлы
go clean -modcache           # Очистить кэш модулей

# Получение пакетов
go get github.com/pkg/name   # Добавить зависимость
go get -u                    # Обновить зависимости

# Информация
go list -m all               # Список всех зависимостей
go doc package.Function      # Документация
```

---

## Типичные проблемы и решения

### 1. "go: command not found"

**Причина**: Go не добавлен в PATH

**Решение Windows**:
```cmd
setx PATH "%PATH%;C:\Program Files\Go\bin"
```

**Решение Linux/macOS**:
Добавьте в `~/.bashrc` или `~/.zshrc`:
```bash
export PATH=$PATH:/usr/local/go/bin
```
Затем:
```bash
source ~/.bashrc
```

### 2. "cannot find package"

**Причина**: Зависимость не скачана

**Решение**:
```bash
go mod tidy
go mod download
```

### 3. Проблемы с GOPATH

**Решение**: С Go Modules вам не нужен GOPATH для проектов. Работайте в любой директории:
```bash
mkdir ~/projects/myapp
cd ~/projects/myapp
go mod init myapp
```

### 4. Проблемы с прокси (в корпоративной сети)

**Решение**:
```bash
# Отключить Go proxy
go env -w GOPROXY=direct

# Или использовать свой proxy
go env -w GOPROXY=https://yourproxy.com
```

---

## Следующие шаги

После настройки окружения переходите к:
- **1.2 Синтаксис и базовые концепции** — изучение основ языка
- **1.3 Ключевые отличия от C#** — понимание философии Go
- **1.4 Практика: мини-проекты** — закрепление навыков

---

## Чек-лист готовности

- [ ] Go установлен (версия 1.22+)
- [ ] `go version` работает
- [ ] `go env` показывает корректные GOROOT и GOPATH
- [ ] `$GOPATH/bin` добавлен в PATH
- [ ] IDE настроена (GoLand или VS Code с Go extension)
- [ ] `golangci-lint` установлен и работает
- [ ] Создан и запущен первый проект
- [ ] `go fmt`, `go vet` работают корректно
- [ ] Понимаете, как работают Go Modules

**Если все пункты выполнены — окружение настроено! Можно переходить к изучению языка.**
