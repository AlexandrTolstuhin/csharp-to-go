# Установка и настройка окружения Go

## Настройка инструментов

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

## Создание первого проекта

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

## Дополнительные инструменты

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
