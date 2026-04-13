# CLI-приложения

---

## Введение

> 💡 **Для C# разработчиков**: Go — один из самых популярных языков для CLI-инструментов. Docker, Kubernetes (kubectl), Terraform, Hugo, gh (GitHub CLI) — всё написано на Go. Причины: быстрая компиляция в единый бинарник, кросс-компиляция на все платформы, мгновенный запуск (нет runtime). В C# CLI строятся через `System.CommandLine` (появился недавно) или `CommandLineParser`. В Go экосистема CLI зрелая и богатая.

### Что вы узнаете

- Стандартный пакет `flag` и его ограничения
- Cobra: стандарт индустрии для CLI
- Структура проекта CLI-приложения
- Подкоманды, флаги, аргументы, автодополнение
- Интерактивный ввод и форматированный вывод
- Кросс-компиляция и дистрибуция
- `go:embed` для встраивания ресурсов в бинарник

---

## Сравнительная таблица: C# vs Go CLI

| Аспект | C# | Go |
|--------|----|----|
| **Стандартная библиотека** | `System.CommandLine` (preview долго был) | `flag` (минималистичный) |
| **Основной фреймворк** | `System.CommandLine`, `CommandLineParser` | Cobra |
| **Бинарник** | Требует .NET Runtime или self-contained (~60MB) | Единый бинарник (~5-15MB) |
| **Запуск** | ~100-300ms (JIT / AOT) | ~1-5ms |
| **Кросс-компиляция** | `dotnet publish -r linux-x64` | `GOOS=linux go build` |
| **Автодополнение** | Ручная настройка | Cobra генерирует автоматически |
| **Man pages** | Нет стандартного | Cobra генерирует |

---

## Стандартный пакет flag

Для простых CLI без подкоманд.

```go
package main

import (
    "flag"
    "fmt"
)

func main() {
    // Определение флагов
    host := flag.String("host", "localhost", "адрес сервера")
    port := flag.Int("port", 8080, "порт сервера")
    verbose := flag.Bool("verbose", false, "подробный вывод")

    // Альтернатива: привязка к существующей переменной
    var timeout int
    flag.IntVar(&timeout, "timeout", 30, "таймаут в секундах")

    // Парсинг аргументов
    flag.Parse()

    // Позиционные аргументы (после флагов)
    args := flag.Args()

    fmt.Printf("host=%s port=%d verbose=%v timeout=%d args=%v\n",
        *host, *port, *verbose, timeout, args)
}
```

```bash
# Использование
myapp -host 0.0.0.0 -port 9090 -verbose file1.txt file2.txt
# host=0.0.0.0 port=9090 verbose=true timeout=30 args=[file1.txt file2.txt]

# Справка генерируется автоматически
myapp -help
```

**C# аналог**:
```csharp
// System.CommandLine
var hostOption = new Option<string>("--host", () => "localhost", "адрес сервера");
var portOption = new Option<int>("--port", () => 8080, "порт сервера");

var rootCommand = new RootCommand("My App");
rootCommand.AddOption(hostOption);
rootCommand.AddOption(portOption);

rootCommand.SetHandler((host, port) =>
{
    Console.WriteLine($"host={host} port={port}");
}, hostOption, portOption);

await rootCommand.InvokeAsync(args);
```

### Ограничения flag

- Нет подкоманд (`myapp serve`, `myapp migrate`)
- Только `-flag` (один дефис), нет `--flag` (GNU-style)
- Нет коротких флагов (`-v` = `--verbose`)
- Нет группировки, валидации, enum-значений
- Нет автодополнения

Для серьёзных CLI используйте Cobra.

---

## Cobra: стандарт индустрии

[Cobra](https://github.com/spf13/cobra) — фреймворк для CLI, используемый в kubectl, hugo, gh, docker compose и сотнях других проектов.

### Установка

```bash
go get github.com/spf13/cobra@latest

# Генератор проекта (опционально)
go install github.com/spf13/cobra-cli@latest
```

### Структура проекта

```
myctl/
├── cmd/
│   ├── root.go         # корневая команда
│   ├── serve.go        # myctl serve
│   ├── migrate.go      # myctl migrate
│   └── version.go      # myctl version
├── internal/
│   ├── config/         # конфигурация
│   └── runner/         # бизнес-логика
├── main.go
├── go.mod
└── go.sum
```

### main.go: точка входа

```go
package main

import "github.com/username/myctl/cmd"

func main() {
    cmd.Execute()
}
```

### cmd/root.go: корневая команда

```go
package cmd

import (
    "fmt"
    "os"

    "github.com/spf13/cobra"
)

// Глобальные флаги
var (
    cfgFile string
    verbose bool
)

var rootCmd = &cobra.Command{
    Use:   "myctl",
    Short: "Утилита управления сервисом",
    Long: `myctl — CLI для управления, миграций и мониторинга.

Примеры:
  myctl serve --port 8080
  myctl migrate up
  myctl config show`,
}

func Execute() {
    if err := rootCmd.Execute(); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
}

func init() {
    // Persistent flags — доступны во ВСЕХ подкомандах
    rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "путь к конфигу")
    rootCmd.PersistentFlags().BoolVarP(&verbose, "verbose", "v", false, "подробный вывод")
}
```

### cmd/serve.go: подкоманда

```go
package cmd

import (
    "fmt"
    "github.com/spf13/cobra"
)

var (
    serveHost string
    servePort int
)

var serveCmd = &cobra.Command{
    Use:   "serve",
    Short: "Запустить HTTP-сервер",
    Long:  "Запустить HTTP-сервер с указанным адресом и портом",
    Example: `  myctl serve
  myctl serve --host 0.0.0.0 --port 9090
  myctl serve -p 9090`,
    RunE: func(cmd *cobra.Command, args []string) error {
        fmt.Printf("Запуск сервера на %s:%d\n", serveHost, servePort)
        // Здесь реальная логика запуска
        return nil
    },
}

func init() {
    // Локальные флаги — только для этой команды
    serveCmd.Flags().StringVar(&serveHost, "host", "localhost", "адрес")
    serveCmd.Flags().IntVarP(&servePort, "port", "p", 8080, "порт")

    // Регистрация подкоманды
    rootCmd.AddCommand(serveCmd)
}
```

### cmd/migrate.go: вложенные подкоманды

```go
package cmd

import (
    "fmt"
    "github.com/spf13/cobra"
)

var migrateCmd = &cobra.Command{
    Use:   "migrate",
    Short: "Управление миграциями БД",
}

var migrateUpCmd = &cobra.Command{
    Use:   "up [steps]",
    Short: "Применить миграции",
    Args:  cobra.MaximumNArgs(1), // 0 или 1 аргумент
    RunE: func(cmd *cobra.Command, args []string) error {
        steps := "all"
        if len(args) > 0 {
            steps = args[0]
        }
        fmt.Printf("Применение миграций: %s\n", steps)
        return nil
    },
}

var migrateDownCmd = &cobra.Command{
    Use:   "down [steps]",
    Short: "Откатить миграции",
    Args:  cobra.MaximumNArgs(1),
    RunE: func(cmd *cobra.Command, args []string) error {
        steps := "1"
        if len(args) > 0 {
            steps = args[0]
        }
        fmt.Printf("Откат миграций: %s\n", steps)
        return nil
    },
}

func init() {
    migrateCmd.AddCommand(migrateUpCmd)
    migrateCmd.AddCommand(migrateDownCmd)
    rootCmd.AddCommand(migrateCmd)
}
```

```bash
# Использование
myctl migrate up
myctl migrate up 3
myctl migrate down 1
myctl migrate --help
```

---

## Флаги и аргументы: детали

### Типы флагов

```go
// Persistent — наследуются всеми подкомандами
cmd.PersistentFlags().StringVar(&cfgFile, "config", "", "конфиг")

// Local — только для текущей команды
cmd.Flags().IntVarP(&port, "port", "p", 8080, "порт")

// Required — обязательный флаг
cmd.Flags().StringVar(&name, "name", "", "имя сервиса")
cmd.MarkFlagRequired("name")

// Deprecated
cmd.Flags().StringVar(&old, "old-flag", "", "deprecated")
cmd.Flags().MarkDeprecated("old-flag", "используйте --new-flag")

// Hidden — скрытый (не показывается в help)
cmd.Flags().BoolVar(&debug, "debug", false, "debug mode")
cmd.Flags().MarkHidden("debug")

// Enum-подобный с валидацией
var format string
cmd.Flags().StringVar(&format, "format", "json", "формат вывода")
cmd.RegisterFlagCompletionFunc("format", func(cmd *cobra.Command, args []string, toComplete string) ([]string, cobra.ShellCompDirective) {
    return []string{"json", "yaml", "table"}, cobra.ShellCompDirectiveDefault
})
```

### Валидация аргументов

```go
// Ровно 1 аргумент
cmd.Args = cobra.ExactArgs(1)

// От 1 до 3
cmd.Args = cobra.RangeArgs(1, 3)

// Без аргументов
cmd.Args = cobra.NoArgs

// Минимум 1
cmd.Args = cobra.MinimumNArgs(1)

// Пользовательская валидация
cmd.Args = func(cmd *cobra.Command, args []string) error {
    for _, arg := range args {
        if !isValidName(arg) {
            return fmt.Errorf("невалидное имя: %q", arg)
        }
    }
    return nil
}
```

---

## Cobra + Viper: конфигурация

Cobra часто используется вместе с [Viper](https://github.com/spf13/viper) для объединения конфигурации из файлов, переменных окружения и флагов CLI.

```go
import (
    "github.com/spf13/cobra"
    "github.com/spf13/viper"
)

func init() {
    cobra.OnInitialize(initConfig)

    rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "конфиг файл")
    rootCmd.PersistentFlags().IntVar(&port, "port", 8080, "порт")

    // Привязка флага CLI к Viper
    viper.BindPFlag("port", rootCmd.PersistentFlags().Lookup("port"))
}

func initConfig() {
    if cfgFile != "" {
        viper.SetConfigFile(cfgFile)
    } else {
        viper.SetConfigName("config")
        viper.SetConfigType("yaml")
        viper.AddConfigPath(".")
        viper.AddConfigPath("$HOME/.myctl")
    }

    viper.AutomaticEnv()        // читать переменные окружения
    viper.SetEnvPrefix("MYCTL") // MYCTL_PORT → port

    if err := viper.ReadInConfig(); err == nil {
        fmt.Println("Конфиг:", viper.ConfigFileUsed())
    }
}
```

Приоритет значений (от высшего к низшему):
1. Флаги CLI (`--port 9090`)
2. Переменные окружения (`MYCTL_PORT=9090`)
3. Файл конфигурации (`config.yaml`)
4. Значения по умолчанию

---

## Автодополнение (Shell Completion)

Cobra генерирует скрипты автодополнения для всех популярных оболочек.

```go
// cmd/completion.go
var completionCmd = &cobra.Command{
    Use:   "completion [bash|zsh|fish|powershell]",
    Short: "Генерация скрипта автодополнения",
    Long: `Загрузка автодополнения:

  # Bash
  source <(myctl completion bash)

  # Zsh
  myctl completion zsh > "${fpath[1]}/_myctl"

  # Fish
  myctl completion fish | source

  # PowerShell
  myctl completion powershell | Out-String | Invoke-Expression`,
    Args:      cobra.ExactValidArgs(1),
    ValidArgs: []string{"bash", "zsh", "fish", "powershell"},
    RunE: func(cmd *cobra.Command, args []string) error {
        switch args[0] {
        case "bash":
            return rootCmd.GenBashCompletion(os.Stdout)
        case "zsh":
            return rootCmd.GenZshCompletion(os.Stdout)
        case "fish":
            return rootCmd.GenFishCompletion(os.Stdout, true)
        case "powershell":
            return rootCmd.GenPowerShellCompletionWithDesc(os.Stdout)
        }
        return nil
    },
}

func init() {
    rootCmd.AddCommand(completionCmd)
}
```

---

## Интерактивный ввод и вывод

### Форматированный вывод: таблицы

```go
import "text/tabwriter"

func printTable(users []User) {
    w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
    fmt.Fprintln(w, "ID\tИМЯ\tEMAIL\tСТАТУС")
    fmt.Fprintln(w, "──\t───\t─────\t──────")
    for _, u := range users {
        fmt.Fprintf(w, "%d\t%s\t%s\t%s\n", u.ID, u.Name, u.Email, u.Status)
    }
    w.Flush()
}

// Вывод:
// ID  ИМЯ      EMAIL              СТАТУС
// ──  ───      ─────              ──────
// 1   Alice    alice@mail.com     active
// 2   Bob      bob@mail.com       inactive
```

### Вывод в JSON/YAML

```go
import "encoding/json"

func printJSON(v any) error {
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    return enc.Encode(v)
}

// Выбор формата по флагу
func printOutput(v any, format string) error {
    switch format {
    case "json":
        return printJSON(v)
    case "yaml":
        data, err := yaml.Marshal(v)
        if err != nil { return err }
        _, err = os.Stdout.Write(data)
        return err
    case "table":
        printTable(v)
        return nil
    default:
        return fmt.Errorf("неизвестный формат: %s", format)
    }
}
```

### Прогресс-бар

```go
import "github.com/schollz/progressbar/v3"

func downloadFile(url, dest string) error {
    resp, err := http.Get(url)
    if err != nil { return err }
    defer resp.Body.Close()

    f, err := os.Create(dest)
    if err != nil { return err }
    defer f.Close()

    bar := progressbar.DefaultBytes(
        resp.ContentLength,
        "Загрузка",
    )

    _, err = io.Copy(io.MultiWriter(f, bar), resp.Body)
    return err
}
```

### Цветной вывод

```go
import "github.com/fatih/color"

// Простой вывод
color.Red("Ошибка: файл не найден")
color.Green("Готово!")
color.Yellow("Предупреждение: устаревший формат")

// Форматированный
info := color.New(color.FgCyan, color.Bold)
info.Printf("Версия: %s\n", version)

// Автоматическое отключение цветов при перенаправлении
// color.NoColor = true (или через os.Getenv("NO_COLOR"))
```

### Интерактивные промпты

```go
import "github.com/AlecAivazis/survey/v2"

// Ввод текста
var name string
survey.AskOne(&survey.Input{
    Message: "Имя сервиса:",
    Default: "my-service",
}, &name)

// Подтверждение
var confirm bool
survey.AskOne(&survey.Confirm{
    Message: "Удалить все данные?",
    Default: false,
}, &confirm)

// Выбор из списка
var env string
survey.AskOne(&survey.Select{
    Message: "Окружение:",
    Options: []string{"development", "staging", "production"},
    Default: "development",
}, &env)
```

---

## go:embed — встраивание файлов

Директива `go:embed` (Go 1.16+) позволяет встраивать файлы и директории прямо в бинарник.

```go
import "embed"

// Один файл как строка
//go:embed version.txt
var version string

// Один файл как байты
//go:embed config.default.yaml
var defaultConfig []byte

// Целая директория
//go:embed templates/*
var templates embed.FS

// Несколько паттернов
//go:embed static/* templates/*
var assets embed.FS

// Использование embed.FS
func loadTemplate(name string) (string, error) {
    data, err := templates.ReadFile("templates/" + name)
    if err != nil {
        return "", err
    }
    return string(data), nil
}
```

**C# аналог**:
```csharp
// Embedded resources в .csproj
// <EmbeddedResource Include="templates\**\*" />

var assembly = Assembly.GetExecutingAssembly();
using var stream = assembly.GetManifestResourceStream("MyApp.templates.index.html");
```

В Go `//go:embed` — одна строка и встроенная файловая система. В C# — конфигурация `.csproj` + Reflection для доступа.

### Типичные применения go:embed

```go
// 1. SQL-миграции в бинарнике
//go:embed migrations/*.sql
var migrationsFS embed.FS

// 2. Шаблоны HTML
//go:embed templates/*.html
var templateFS embed.FS

tmpl, _ := template.ParseFS(templateFS, "templates/*.html")

// 3. Статические файлы для HTTP
//go:embed static/*
var staticFS embed.FS

http.Handle("/static/", http.FileServer(http.FS(staticFS)))

// 4. Версия из файла
//go:embed VERSION
var version string

var versionCmd = &cobra.Command{
    Use:   "version",
    Short: "Показать версию",
    Run: func(cmd *cobra.Command, args []string) {
        fmt.Printf("myctl %s\n", strings.TrimSpace(version))
    },
}
```

---

## Кросс-компиляция

Одно из главных преимуществ Go — сборка бинарников для любой платформы на любой машине.

```bash
# Linux (amd64)
GOOS=linux GOARCH=amd64 go build -o myctl-linux-amd64

# Linux (ARM64 — Raspberry Pi, AWS Graviton)
GOOS=linux GOARCH=arm64 go build -o myctl-linux-arm64

# macOS (Apple Silicon)
GOOS=darwin GOARCH=arm64 go build -o myctl-darwin-arm64

# Windows
GOOS=windows GOARCH=amd64 go build -o myctl-windows-amd64.exe

# Без CGO (чистый Go — статическая линковка)
CGO_ENABLED=0 GOOS=linux go build -o myctl-linux-static
```

**C# аналог**:
```bash
dotnet publish -r linux-x64 --self-contained  # ~60-80MB бинарник
dotnet publish -r linux-x64 /p:PublishAot=true # AOT: ~10-30MB, но ограничения
```

### Скрипт релиза

```bash
#!/bin/bash
VERSION=$(git describe --tags --always)
LDFLAGS="-s -w -X main.version=${VERSION}"

for GOOS in linux darwin windows; do
    for GOARCH in amd64 arm64; do
        output="myctl-${GOOS}-${GOARCH}"
        if [ "$GOOS" = "windows" ]; then
            output="${output}.exe"
        fi
        echo "Сборка: ${output}"
        GOOS=$GOOS GOARCH=$GOARCH go build -ldflags "$LDFLAGS" -o "dist/${output}" .
    done
done
```

### ldflags: внедрение переменных при сборке

```go
// main.go
package main

var (
    version = "dev"      // переопределяется при сборке
    commit  = "unknown"
    date    = "unknown"
)
```

```bash
go build -ldflags "-X main.version=1.2.3 -X main.commit=$(git rev-parse HEAD) -X main.date=$(date -u +%Y-%m-%dT%H:%M:%SZ)" -o myctl
```

```bash
# -s -w — убрать отладочные символы (уменьшает бинарник на ~30%)
go build -ldflags "-s -w" -o myctl
```

---

## Goreleaser: автоматизация релизов

[Goreleaser](https://goreleaser.com) автоматизирует сборку, подпись и публикацию CLI-инструментов.

```yaml
# .goreleaser.yml
version: 2
project_name: myctl

builds:
  - main: .
    binary: myctl
    goos: [linux, darwin, windows]
    goarch: [amd64, arm64]
    ldflags:
      - -s -w
      - -X main.version={{.Version}}
      - -X main.commit={{.Commit}}
      - -X main.date={{.Date}}

archives:
  - formats: [tar.gz]
    format_overrides:
      - goos: windows
        formats: [zip]
    name_template: "{{ .ProjectName }}_{{ .Os }}_{{ .Arch }}"

brews:
  - repository:
      owner: username
      name: homebrew-tap
    homepage: https://github.com/username/myctl
    description: "Утилита управления сервисом"

changelog:
  sort: asc
  filters:
    exclude:
      - "^docs:"
      - "^test:"
```

```bash
# Локальная сборка (без публикации)
goreleaser release --snapshot --clean

# Релиз при пуше тега
git tag v1.0.0
git push origin v1.0.0
# GitHub Actions запустит goreleaser
```

---

## Тестирование CLI

```go
func TestServeCommand(t *testing.T) {
    // Создаём новую корневую команду для изоляции
    cmd := newRootCmd()

    // Захватываем stdout
    var buf bytes.Buffer
    cmd.SetOut(&buf)
    cmd.SetErr(&buf)

    // Устанавливаем аргументы
    cmd.SetArgs([]string{"serve", "--port", "9090"})

    // Выполняем
    err := cmd.Execute()
    if err != nil {
        t.Fatalf("ошибка выполнения: %v", err)
    }

    output := buf.String()
    if !strings.Contains(output, "9090") {
        t.Errorf("ожидалось упоминание порта 9090, получено: %s", output)
    }
}

func TestMigrateUpArgs(t *testing.T) {
    cmd := newRootCmd()
    cmd.SetArgs([]string{"migrate", "up", "3"})

    err := cmd.Execute()
    if err != nil {
        t.Fatalf("ошибка: %v", err)
    }
}

func TestInvalidCommand(t *testing.T) {
    cmd := newRootCmd()
    cmd.SetArgs([]string{"nonexistent"})

    err := cmd.Execute()
    if err == nil {
        t.Fatal("ожидалась ошибка для несуществующей команды")
    }
}
```

---

## Практический пример: dbctl

Минимальный CLI для управления базой данных:

<details>
<summary>Полный код dbctl</summary>

```go
package main

import (
    "embed"
    "fmt"
    "os"
    "strings"
    "text/tabwriter"

    "github.com/spf13/cobra"
)

//go:embed VERSION
var version string

var (
    dsn     string
    verbose bool
)

func main() {
    if err := rootCmd.Execute(); err != nil {
        os.Exit(1)
    }
}

var rootCmd = &cobra.Command{
    Use:   "dbctl",
    Short: "Утилита управления базой данных",
}

var statusCmd = &cobra.Command{
    Use:   "status",
    Short: "Показать статус подключения",
    RunE: func(cmd *cobra.Command, args []string) error {
        fmt.Fprintf(cmd.OutOrStdout(), "DSN: %s\n", dsn)
        fmt.Fprintf(cmd.OutOrStdout(), "Статус: подключено\n")
        return nil
    },
}

var tablesCmd = &cobra.Command{
    Use:   "tables",
    Short: "Список таблиц",
    RunE: func(cmd *cobra.Command, args []string) error {
        // Пример вывода — в реальности запрос к БД
        tables := []struct {
            Name  string
            Rows  int
            Size  string
        }{
            {"users", 15420, "2.1 MB"},
            {"orders", 89301, "12.4 MB"},
            {"products", 3200, "0.8 MB"},
        }

        w := tabwriter.NewWriter(cmd.OutOrStdout(), 0, 0, 2, ' ', 0)
        fmt.Fprintln(w, "ТАБЛИЦА\tСТРОК\tРАЗМЕР")
        fmt.Fprintln(w, "───────\t─────\t──────")
        for _, t := range tables {
            fmt.Fprintf(w, "%s\t%d\t%s\n", t.Name, t.Rows, t.Size)
        }
        return w.Flush()
    },
}

var migrateCmd = &cobra.Command{
    Use:   "migrate",
    Short: "Управление миграциями",
}

var migrateUpCmd = &cobra.Command{
    Use:   "up",
    Short: "Применить миграции",
    RunE: func(cmd *cobra.Command, args []string) error {
        fmt.Fprintln(cmd.OutOrStdout(), "Применение миграций...")
        fmt.Fprintln(cmd.OutOrStdout(), "  001_create_users.sql  OK")
        fmt.Fprintln(cmd.OutOrStdout(), "  002_create_orders.sql OK")
        fmt.Fprintln(cmd.OutOrStdout(), "Готово: 2 миграции применены")
        return nil
    },
}

var versionCmd = &cobra.Command{
    Use:   "version",
    Short: "Версия программы",
    Run: func(cmd *cobra.Command, args []string) {
        fmt.Fprintf(cmd.OutOrStdout(), "dbctl %s\n", strings.TrimSpace(version))
    },
}

func init() {
    rootCmd.PersistentFlags().StringVar(&dsn, "dsn", "", "строка подключения к БД")
    rootCmd.PersistentFlags().BoolVarP(&verbose, "verbose", "v", false, "подробный вывод")

    rootCmd.MarkPersistentFlagRequired("dsn")

    migrateCmd.AddCommand(migrateUpCmd)
    rootCmd.AddCommand(statusCmd, tablesCmd, migrateCmd, versionCmd)
}
```

</details>

```bash
# Использование
dbctl --dsn "postgres://localhost/mydb" status
dbctl --dsn "postgres://localhost/mydb" tables
dbctl --dsn "postgres://localhost/mydb" migrate up
dbctl version
dbctl --help
```

---

## Шпаргалка: экосистема CLI в Go

| Задача | Пакет / инструмент |
|--------|-------------------|
| Парсинг флагов (простой) | `flag` (stdlib) |
| CLI-фреймворк | [Cobra](https://github.com/spf13/cobra) |
| Конфигурация | [Viper](https://github.com/spf13/viper) |
| Прогресс-бар | [progressbar](https://github.com/schollz/progressbar) |
| Цвета | [color](https://github.com/fatih/color) |
| Интерактивные промпты | [survey](https://github.com/AlecAivazis/survey) |
| TUI (терминальный UI) | [bubbletea](https://github.com/charmbracelet/bubbletea) |
| Таблицы | `text/tabwriter` (stdlib), [tablewriter](https://github.com/olekukonez/tablewriter) |
| Логирование CLI | [slog](https://pkg.go.dev/log/slog) (stdlib) |
| Кросс-компиляция + релиз | [Goreleaser](https://goreleaser.com) |
| Встраивание файлов | `go:embed` (stdlib) |
