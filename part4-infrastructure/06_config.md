# 4.6 Конфигурация: Управление настройками в Go

## Содержание

- [Введение](#введение)
- [Экосистема: C# vs Go](#экосистема-c-vs-go)
- [Стандартная библиотека: os и flag](#стандартная-библиотека-os-и-flag)
  - [os.Getenv и os.LookupEnv](#osgetenv-и-oslookupenv)
  - [Типизированная обёртка над env](#типизированная-обёртка-над-env)
  - [flag: аргументы командной строки](#flag-аргументы-командной-строки)
  - [Комбинирование flag и env](#комбинирование-flag-и-env)
- [caarlos0/env: struct-based ENV парсинг](#caarlos0env-struct-based-env-парсинг)
  - [Основы и struct tags](#основы-и-struct-tags)
  - [Поддерживаемые типы и custom parsers](#поддерживаемые-типы-и-custom-parsers)
  - [Вложенные структуры и prefix](#вложенные-структуры-и-prefix)
  - [Required, defaults, expand](#required-defaults-expand)
  - [Интеграция с .env файлами (godotenv)](#интеграция-с-env-файлами-godotenv)
- [kelseyhightower/envconfig](#kelseyhightowerenvconfig)
  - [Основы и отличия от caarlos0/env](#основы-и-отличия-от-caarlos0env)
  - [Struct tags и naming conventions](#struct-tags-и-naming-conventions)
  - [Usage и help output](#usage-и-help-output)
- [Сравнение env-библиотек](#сравнение-env-библиотек)
- [Viper: полнофункциональная конфигурация](#viper-полнофункциональная-конфигурация)
  - [Установка и базовое использование](#установка-и-базовое-использование)
  - [Источники конфигурации и приоритеты](#источники-конфигурации-и-приоритеты)
  - [Файлы конфигурации (YAML, TOML, JSON)](#файлы-конфигурации-yaml-toml-json)
  - [Переменные окружения и AutomaticEnv](#переменные-окружения-и-automaticenv)
  - [Unmarshal в структуры](#unmarshal-в-структуры)
  - [WatchConfig: горячая перезагрузка](#watchconfig-горячая-перезагрузка)
  - [Remote Config (etcd, Consul)](#remote-config-etcd-consul)
  - [Проблемы Viper и когда НЕ использовать](#проблемы-viper-и-когда-не-использовать)
- [koanf: современная альтернатива Viper](#koanf-современная-альтернатива-viper)
  - [Архитектура: Providers и Parsers](#архитектура-providers-и-parsers)
  - [Файлы, ENV, flags](#файлы-env-flags)
  - [Unmarshal и struct tags](#unmarshal-и-struct-tags)
  - [Watch и reload](#watch-и-reload)
  - [Viper vs koanf](#viper-vs-koanf)
- [cleanenv: лёгкая альтернатива](#cleanenv-лёгкая-альтернатива)
- [Сравнительная таблица всех библиотек](#сравнительная-таблица-всех-библиотек)
- [Блок-схема выбора библиотеки](#блок-схема-выбора-библиотеки)
- [Валидация конфигурации](#валидация-конфигурации)
  - [Fail fast при запуске](#fail-fast-при-запуске)
  - [go-playground/validator для конфигов](#go-playgroundvalidator-для-конфигов)
  - [Custom validation logic](#custom-validation-logic)
- [Паттерны конфигурации](#паттерны-конфигурации)
  - [12-Factor App: конфигурация через ENV](#12-factor-app-конфигурация-через-env)
  - [Multi-environment (dev/staging/prod)](#multi-environment-devstagingprod)
  - [Immutable config vs hot reload](#immutable-config-vs-hot-reload)
  - [Functional Options для конфигурации](#functional-options-для-конфигурации)
- [Секреты и безопасность](#секреты-и-безопасность)
  - [Почему НЕ хранить секреты в config-файлах](#почему-не-хранить-секреты-в-config-файлах)
  - [HashiCorp Vault](#hashicorp-vault)
  - [AWS Secrets Manager](#aws-secrets-manager)
  - [Kubernetes Secrets и ConfigMaps](#kubernetes-secrets-и-configmaps)
  - [Маскирование секретов в логах](#маскирование-секретов-в-логах)
- [Feature Flags](#feature-flags)
  - [Простая реализация через конфигурацию](#простая-реализация-через-конфигурацию)
  - [OpenFeature SDK](#openfeature-sdk)
  - [Сторонние сервисы](#сторонние-сервисы)
- [Production Concerns](#production-concerns)
  - [Порядок инициализации](#порядок-инициализации)
  - [Graceful reload](#graceful-reload)
  - [Тестирование конфигурации](#тестирование-конфигурации)
  - [Observability для конфигурации](#observability-для-конфигурации)
- [Типичные ошибки C# разработчиков](#типичные-ошибки-c-разработчиков)
- [Практические примеры](#практические-примеры)
  - [Пример 1: Production-ready config с caarlos0/env](#пример-1-production-ready-config-с-caarlos0env)
  - [Пример 2: Multi-source config с koanf и hot reload](#пример-2-multi-source-config-с-koanf-и-hot-reload)
  - [Пример 3: Config с секретами и feature flags](#пример-3-config-с-секретами-и-feature-flags)

---

## Введение

В [разделе 3.2](../part3-web-api/02_project_structure.md) мы познакомились с базовым подходом к конфигурации — `os.Getenv` и простая структура `Config`. Этого достаточно для учебного проекта, но в production-системах конфигурация — это целая инфраструктура: типизация, валидация, секреты, горячая перезагрузка, мультисреды.

В предыдущих разделах Части 4 мы уже сталкивались с конфигурацией:
- **4.1**: `os.Getenv("DB_HOST")` для подключения к PostgreSQL
- **4.2**: строка подключения Redis, TTL кэша
- **4.3**: адреса брокеров Kafka/RabbitMQ
- **4.4**: порты и TLS-настройки gRPC
- **4.5**: уровни логирования, адреса коллекторов

Каждый раз мы использовали ad-hoc подход. Теперь систематизируем.

> 💡 **Для C# разработчиков**: В .NET конфигурация — часть фреймворка. `IConfiguration`, `appsettings.json`, `IOptions<T>` — всё это встроено в DI-контейнер и работает "из коробки". В Go нет фреймворка — конфигурация это **просто структура**, которую вы заполняете и передаёте явно. Никакого DI, никакого `IOptions<T>` — только struct и конструкторы.

---

## Экосистема: C# vs Go

| Концепция | C# (.NET) | Go |
|-----------|-----------|-----|
| Стандартная конфигурация | `IConfiguration` + `ConfigurationBuilder` | `os.Getenv` / `flag` |
| Файлы настроек | `appsettings.json` (JSON) | YAML/TOML через viper/koanf |
| Строгая типизация | `IOptions<T>` паттерн | Struct + tags |
| Переменные окружения | `AddEnvironmentVariables()` | `os.Getenv` / caarlos0/env |
| Перезагрузка | `IOptionsMonitor<T>` | viper.WatchConfig / atomic.Pointer |
| Снимок на запрос | `IOptionsSnapshot<T>` | Immutable struct (перезагрузка = новая структура) |
| Валидация | Data Annotations / `IValidateOptions<T>` | go-playground/validator / custom |
| Секреты | User Secrets, Azure Key Vault | Vault, AWS SM, K8s Secrets |
| DI-интеграция | `services.Configure<T>()` | Нет — передаём struct явно |
| Feature flags | `Microsoft.FeatureManagement` | Manual / OpenFeature / LaunchDarkly |

> ⚠️ **Ключевое отличие**: В C# конфигурация пронизывает весь фреймворк через DI. В Go конфигурация — это **данные**, которые вы загружаете при старте и передаёте через конструкторы. Нет магии, нет скрытых зависимостей.

**C# подход**:
```csharp
// Program.cs — конфигурация встроена в фреймворк
var builder = WebApplication.CreateBuilder(args);

// Автоматически загружает: appsettings.json → appsettings.{Env}.json → env vars → secrets
builder.Configuration
    .AddJsonFile("appsettings.json")
    .AddEnvironmentVariables()
    .AddUserSecrets<Program>();

// Регистрация типизированной конфигурации через DI
builder.Services.Configure<DatabaseOptions>(
    builder.Configuration.GetSection("Database"));

builder.Services.AddScoped<IUserRepository, UserRepository>();

// Использование — через DI
public class UserRepository : IUserRepository
{
    public UserRepository(IOptions<DatabaseOptions> options)
    {
        _connectionString = options.Value.ConnectionString;
    }
}
```

**Go подход**:
```go
// main.go — конфигурация загружается явно
func main() {
    // Загрузка конфигурации — явный вызов
    cfg, err := config.Load()
    if err != nil {
        log.Fatal("ошибка загрузки конфигурации", "error", err)
    }

    // Передача через конструкторы — никакого DI
    repo := postgres.NewUserRepository(cfg.Database)
    svc := service.NewUserService(repo)
    handler := api.NewHandler(svc)

    srv := &http.Server{
        Addr:    cfg.Server.Address(),
        Handler: handler.Routes(),
    }
    log.Fatal(srv.ListenAndServe())
}
```

Простота и явность — философия Go. Конфигурация не исключение.

---

## Стандартная библиотека: os и flag

### os.Getenv и os.LookupEnv

Go предоставляет два способа чтения переменных окружения:

```go
package main

import (
    "fmt"
    "os"
)

func main() {
    // os.Getenv — возвращает значение или пустую строку
    // Невозможно отличить "не задана" от "задана пустой"
    host := os.Getenv("DB_HOST")
    fmt.Println(host) // "" — не задана? или задана пустой?

    // os.LookupEnv — возвращает значение и флаг наличия
    host, ok := os.LookupEnv("DB_HOST")
    if !ok {
        fmt.Println("DB_HOST не задана")
    } else {
        fmt.Printf("DB_HOST = %q\n", host) // может быть пустой строкой
    }
}
```

**C# аналог**:
```csharp
// Environment.GetEnvironmentVariable — аналог os.LookupEnv
// Возвращает null, если переменная не задана
string? host = Environment.GetEnvironmentVariable("DB_HOST");
if (host is null)
    Console.WriteLine("DB_HOST не задана");
```

> 💡 **Идиома Go**: Используйте `os.LookupEnv`, когда нужно отличить "не задана" от "пустая". Для обязательных переменных — `os.Getenv` с проверкой на пустоту.

### Типизированная обёртка над env

Разбросанные вызовы `os.Getenv` — путь к хаосу. Идиоматичный подход — собрать конфигурацию в структуру:

```go
package config

import (
    "fmt"
    "os"
    "strconv"
    "time"
)

type Config struct {
    Server   ServerConfig
    Database DatabaseConfig
}

type ServerConfig struct {
    Host         string
    Port         int
    ReadTimeout  time.Duration
    WriteTimeout time.Duration
}

type DatabaseConfig struct {
    Host     string
    Port     int
    User     string
    Password string
    Name     string
    SSLMode  string
}

func Load() (*Config, error) {
    port, err := getEnvInt("SERVER_PORT", 8080)
    if err != nil {
        return nil, fmt.Errorf("SERVER_PORT: %w", err)
    }

    dbPort, err := getEnvInt("DB_PORT", 5432)
    if err != nil {
        return nil, fmt.Errorf("DB_PORT: %w", err)
    }

    readTimeout, err := getEnvDuration("SERVER_READ_TIMEOUT", 5*time.Second)
    if err != nil {
        return nil, fmt.Errorf("SERVER_READ_TIMEOUT: %w", err)
    }

    writeTimeout, err := getEnvDuration("SERVER_WRITE_TIMEOUT", 10*time.Second)
    if err != nil {
        return nil, fmt.Errorf("SERVER_WRITE_TIMEOUT: %w", err)
    }

    return &Config{
        Server: ServerConfig{
            Host:         getEnv("SERVER_HOST", "0.0.0.0"),
            Port:         port,
            ReadTimeout:  readTimeout,
            WriteTimeout: writeTimeout,
        },
        Database: DatabaseConfig{
            Host:     getEnv("DB_HOST", "localhost"),
            Port:     dbPort,
            User:     mustGetEnv("DB_USER"),     // обязательная — паникует
            Password: mustGetEnv("DB_PASSWORD"), // обязательная — паникует
            Name:     getEnv("DB_NAME", "myapp"),
            SSLMode:  getEnv("DB_SSLMODE", "disable"),
        },
    }, nil
}

// getEnv — возвращает значение переменной или default
func getEnv(key, defaultValue string) string {
    if value, ok := os.LookupEnv(key); ok {
        return value
    }
    return defaultValue
}

// mustGetEnv — паникует, если переменная не задана
func mustGetEnv(key string) string {
    value, ok := os.LookupEnv(key)
    if !ok || value == "" {
        panic(fmt.Sprintf("обязательная переменная окружения %s не задана", key))
    }
    return value
}

// getEnvInt — читает int из env с default
func getEnvInt(key string, defaultValue int) (int, error) {
    str, ok := os.LookupEnv(key)
    if !ok {
        return defaultValue, nil
    }
    return strconv.Atoi(str)
}

// getEnvDuration — читает time.Duration из env с default
func getEnvDuration(key string, defaultValue time.Duration) (time.Duration, error) {
    str, ok := os.LookupEnv(key)
    if !ok {
        return defaultValue, nil
    }
    return time.ParseDuration(str)
}
```

Этот подход **работает**, но у него есть недостатки:
- Каждое новое поле требует отдельной helper-функции
- Нет автоматической документации доступных переменных
- Нет валидации (min/max, формат, зависимости)
- Много boilerplate-кода

> ⚠️ **Проблема масштабирования**: При 20+ переменных окружения этот подход становится трудно поддерживать. Именно для этого существуют библиотеки — caarlos0/env, envconfig и другие.

### flag: аргументы командной строки

Пакет `flag` — встроенный способ работы с CLI-аргументами:

```go
package main

import (
    "flag"
    "fmt"
    "time"
)

func main() {
    // Определение флагов
    host := flag.String("host", "0.0.0.0", "адрес сервера")
    port := flag.Int("port", 8080, "порт сервера")
    debug := flag.Bool("debug", false, "режим отладки")
    timeout := flag.Duration("timeout", 30*time.Second, "таймаут запросов")

    // Парсинг аргументов (обязательно до использования)
    flag.Parse()

    fmt.Printf("Сервер: %s:%d (debug=%v, timeout=%v)\n",
        *host, *port, *debug, *timeout)
}
```

```bash
# Использование
go run main.go -host localhost -port 9090 -debug -timeout 1m

# Автоматический help
go run main.go -h
# Output:
#   -debug
#         режим отладки
#   -host string
#         адрес сервера (default "0.0.0.0")
#   -port int
#         порт сервера (default 8080)
#   -timeout duration
#         таймаут запросов (default 30s)
```

**C# аналог**:
```csharp
// В C# нет встроенной работы с CLI-аргументами в ASP.NET
// Обычно используют CommandLineConfigurationProvider или System.CommandLine
builder.Configuration.AddCommandLine(args);

// Или библиотеку System.CommandLine
var rootCommand = new RootCommand("My App");
var portOption = new Option<int>("--port", () => 8080, "порт сервера");
rootCommand.AddOption(portOption);
```

> 💡 **Когда использовать flag**: Для CLI-утилит и инструментов. Для серверных приложений предпочтительнее переменные окружения (12-Factor App). `flag` удобен для dev-переопределений: `go run main.go -debug`.

### Комбинирование flag и env

В production часто нужен приоритет: **flag > env > default**. Стандартная библиотека `pflag` (POSIX-совместимые флаги) упрощает это:

```go
package main

import (
    "fmt"
    "os"

    "github.com/spf13/pflag"
)

func main() {
    // pflag поддерживает длинные и короткие флаги
    host := pflag.StringP("host", "H", "0.0.0.0", "адрес сервера")
    port := pflag.IntP("port", "p", 8080, "порт сервера")
    debug := pflag.BoolP("debug", "d", false, "режим отладки")

    pflag.Parse()

    // Проверяем, был ли флаг явно задан
    // Если нет — проверяем env
    if !pflag.CommandLine.Changed("host") {
        if envHost := os.Getenv("SERVER_HOST"); envHost != "" {
            *host = envHost
        }
    }
    if !pflag.CommandLine.Changed("port") {
        if envPort := os.Getenv("SERVER_PORT"); envPort != "" {
            fmt.Sscanf(envPort, "%d", port)
        }
    }

    fmt.Printf("Сервер: %s:%d (debug=%v)\n", *host, *port, *debug)
}
```

```bash
# POSIX-стиль флагов
go run main.go --host localhost --port 9090 --debug
go run main.go -H localhost -p 9090 -d

# Через env
SERVER_HOST=10.0.0.1 SERVER_PORT=3000 go run main.go

# Flag перебивает env
SERVER_HOST=10.0.0.1 go run main.go --host localhost
# Результат: host = localhost (flag приоритетнее)
```

> ⚠️ **Для серверных приложений** этот подход — чрезмерно сложный boilerplate. Используйте caarlos0/env или viper, которые решают эту задачу декларативно.

---

## caarlos0/env: struct-based ENV парсинг

[github.com/caarlos0/env](https://github.com/caarlos0/env) — самая популярная библиотека для парсинга переменных окружения в Go. Философия: **определи структуру с тегами, получи конфигурацию**.

```bash
go get github.com/caarlos0/env/v11
```

### Основы и struct tags

```go
package config

import (
    "fmt"
    "time"

    "github.com/caarlos0/env/v11"
)

type Config struct {
    Server   ServerConfig
    Database DatabaseConfig
    Redis    RedisConfig
    Log      LogConfig
}

type ServerConfig struct {
    Host         string        `env:"SERVER_HOST" envDefault:"0.0.0.0"`
    Port         int           `env:"SERVER_PORT" envDefault:"8080"`
    ReadTimeout  time.Duration `env:"SERVER_READ_TIMEOUT" envDefault:"5s"`
    WriteTimeout time.Duration `env:"SERVER_WRITE_TIMEOUT" envDefault:"10s"`
}

type DatabaseConfig struct {
    Host     string `env:"DB_HOST" envDefault:"localhost"`
    Port     int    `env:"DB_PORT" envDefault:"5432"`
    User     string `env:"DB_USER,required"`     // обязательная — ошибка если не задана
    Password string `env:"DB_PASSWORD,required"`
    Name     string `env:"DB_NAME" envDefault:"myapp"`
    SSLMode  string `env:"DB_SSLMODE" envDefault:"disable"`
    MaxConns int    `env:"DB_MAX_CONNS" envDefault:"25"`
}

type RedisConfig struct {
    Addr     string `env:"REDIS_ADDR" envDefault:"localhost:6379"`
    Password string `env:"REDIS_PASSWORD"`
    DB       int    `env:"REDIS_DB" envDefault:"0"`
}

type LogConfig struct {
    Level  string `env:"LOG_LEVEL" envDefault:"info"`
    Format string `env:"LOG_FORMAT" envDefault:"json"` // json или text
}

func Load() (*Config, error) {
    cfg := &Config{}
    if err := env.Parse(cfg); err != nil {
        return nil, fmt.Errorf("парсинг конфигурации: %w", err)
    }
    return cfg, nil
}
```

Использование:
```bash
# Задаём обязательные переменные, остальное — defaults
export DB_USER=admin
export DB_PASSWORD=secret123
export SERVER_PORT=9090

# Запускаем приложение
go run main.go
```

**Сравнение с C#**:
```csharp
// C# — нужен DI, IOptions<T>, builder.Services.Configure<T>()
public class DatabaseOptions
{
    [Required]
    public string User { get; set; } = default!;

    [Required]
    public string Password { get; set; } = default!;

    public string Host { get; set; } = "localhost";
    public int Port { get; set; } = 5432;
}

// Регистрация
services.Configure<DatabaseOptions>(config.GetSection("Database"));

// Использование через DI
public class Repository(IOptions<DatabaseOptions> opts) { }
```

```go
// Go — просто структура, никакого DI
cfg, err := config.Load()
if err != nil {
    log.Fatal(err)
}
repo := postgres.NewRepository(cfg.Database)
```

> 💡 **Для C# разработчиков**: `env:"DB_USER,required"` — аналог `[Required]` атрибута на свойстве класса `IOptions<T>`. Только без DI — парсинг и валидация происходят в момент вызова `env.Parse`.

### Поддерживаемые типы и custom parsers

caarlos0/env поддерживает множество типов "из коробки":

```go
type AllTypesExample struct {
    // Примитивы
    String  string  `env:"STR"`
    Int     int     `env:"INT"`
    Int64   int64   `env:"INT64"`
    Float64 float64 `env:"FLOAT"`
    Bool    bool    `env:"BOOL"` // true, false, 1, 0

    // Стандартные типы
    Duration time.Duration `env:"DUR"`    // "5s", "1m30s", "2h"
    URL      url.URL       `env:"URL"`    // "https://example.com"

    // Срезы (разделитель по умолчанию — запятая)
    Hosts []string `env:"HOSTS" envSeparator:":"` // HOST1:HOST2:HOST3
    Ports []int    `env:"PORTS"`                   // 8080,8081,8082

    // Map
    Labels map[string]string `env:"LABELS"` // key=val,key2=val2
}
```

Для нестандартных типов — custom parsers:

```go
import (
    "log/slog"
    "github.com/caarlos0/env/v11"
)

// Собственный тип для уровня логирования
type LogLevel slog.Level

// Реализуем интерфейс env.ParserFunc не нужен —
// достаточно encoding.TextUnmarshaler
func (l *LogLevel) UnmarshalText(text []byte) error {
    switch string(text) {
    case "debug":
        *l = LogLevel(slog.LevelDebug)
    case "info":
        *l = LogLevel(slog.LevelInfo)
    case "warn":
        *l = LogLevel(slog.LevelWarn)
    case "error":
        *l = LogLevel(slog.LevelError)
    default:
        return fmt.Errorf("неизвестный уровень логирования: %s", text)
    }
    return nil
}

type Config struct {
    LogLevel LogLevel `env:"LOG_LEVEL" envDefault:"info"`
}
```

Альтернативный способ — через `env.WithTypeCast`:

```go
// Глобальный парсер для типа через опции
cfg := &Config{}
err := env.ParseWithOptions(cfg, env.Options{
    FuncMap: map[reflect.Type]env.ParserFunc{
        reflect.TypeOf(slog.LevelInfo): func(v string) (interface{}, error) {
            var level slog.Level
            err := level.UnmarshalText([]byte(v))
            return level, err
        },
    },
})
```

### Вложенные структуры и prefix

Для группировки связанных настроек используйте `envPrefix`:

```go
type Config struct {
    // envPrefix добавляет префикс ко всем полям вложенной структуры
    Primary  DatabaseConfig `envPrefix:"PRIMARY_DB_"`
    Replica  DatabaseConfig `envPrefix:"REPLICA_DB_"`
    Cache    RedisConfig    `envPrefix:"CACHE_"`
    Session  RedisConfig    `envPrefix:"SESSION_"`
}

type DatabaseConfig struct {
    Host     string `env:"HOST" envDefault:"localhost"`
    Port     int    `env:"PORT" envDefault:"5432"`
    User     string `env:"USER,required"`
    Password string `env:"PASSWORD,required"`
}

type RedisConfig struct {
    Addr     string `env:"ADDR" envDefault:"localhost:6379"`
    Password string `env:"PASSWORD"`
    DB       int    `env:"DB" envDefault:"0"`
}
```

```bash
# Результирующие переменные:
# PRIMARY_DB_HOST, PRIMARY_DB_PORT, PRIMARY_DB_USER, PRIMARY_DB_PASSWORD
# REPLICA_DB_HOST, REPLICA_DB_PORT, REPLICA_DB_USER, REPLICA_DB_PASSWORD
# CACHE_ADDR, CACHE_PASSWORD, CACHE_DB
# SESSION_ADDR, SESSION_PASSWORD, SESSION_DB

export PRIMARY_DB_USER=admin
export PRIMARY_DB_PASSWORD=secret
export REPLICA_DB_USER=reader
export REPLICA_DB_PASSWORD=readonly
```

**C# аналог**:
```csharp
// В C# — секции конфигурации
services.Configure<DatabaseOptions>(config.GetSection("PrimaryDb"));
services.Configure<DatabaseOptions>("Replica", config.GetSection("ReplicaDb"));
```

### Required, defaults, expand

```go
type Config struct {
    // required — ошибка парсинга, если переменная не задана
    APIKey string `env:"API_KEY,required"`

    // envDefault — значение по умолчанию
    Port int `env:"PORT" envDefault:"8080"`

    // notEmpty — переменная должна быть задана и не быть пустой
    DatabaseURL string `env:"DATABASE_URL,notEmpty"`

    // expand — раскрывает ссылки на другие переменные ($VAR или ${VAR})
    // DATABASE_URL=postgres://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME
    ExpandedURL string `env:"DATABASE_URL,expand"`

    // file — читает значение из файла (путь в переменной)
    // DB_PASSWORD_FILE=/run/secrets/db_password (Docker secrets)
    PasswordFromFile string `env:"DB_PASSWORD_FILE,file"`

    // unset — удаляет переменную из окружения после парсинга (безопасность)
    Secret string `env:"SECRET_TOKEN,required,unset"`
}
```

> 💡 **`file` — для Docker secrets**: Docker Swarm и Kubernetes монтируют секреты как файлы в `/run/secrets/`. Тег `file` читает содержимое файла, путь к которому указан в переменной.

```bash
# Docker secret монтируется как файл
echo "supersecret" > /run/secrets/db_password

# Переменная содержит путь к файлу
export DB_PASSWORD_FILE=/run/secrets/db_password

# caarlos0/env прочитает содержимое файла ("supersecret")
```

### Интеграция с .env файлами (godotenv)

В development удобно хранить настройки в `.env` файле:

```go
package config

import (
    "fmt"

    "github.com/caarlos0/env/v11"
    "github.com/joho/godotenv"
)

func Load() (*Config, error) {
    // В development загружаем .env файл
    // В production файл просто не существует — ошибка игнорируется
    _ = godotenv.Load() // .env в текущей директории
    // godotenv.Load(".env.local", ".env") — несколько файлов, приоритет слева направо

    cfg := &Config{}
    if err := env.Parse(cfg); err != nil {
        return nil, fmt.Errorf("парсинг конфигурации: %w", err)
    }
    return cfg, nil
}
```

Файл `.env`:
```bash
# .env — НЕ коммитить в git!
DB_USER=developer
DB_PASSWORD=devpassword
DB_HOST=localhost
DB_PORT=5432

SERVER_PORT=8080
LOG_LEVEL=debug
```

`.env.example` — коммитить в git как документацию:
```bash
# .env.example — шаблон для разработчиков
DB_USER=
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

SERVER_PORT=8080
LOG_LEVEL=info
```

`.gitignore`:
```
.env
.env.local
.env.*.local
```

**C# аналог**:
```csharp
// Встроенный механизм User Secrets для development
// dotnet user-secrets set "Database:Password" "devpassword"
builder.Configuration.AddUserSecrets<Program>(optional: true);

// В production — через переменные окружения или Azure Key Vault
```

> ⚠️ **Никогда не коммитьте `.env` файлы с реальными секретами!** Используйте `.env.example` как шаблон.

---

## kelseyhightower/envconfig

[github.com/kelseyhightower/envconfig](https://github.com/kelseyhightower/envconfig) — ещё одна популярная библиотека для парсинга env. Отличается **prefix-based подходом**: все переменные группируются общим префиксом.

```bash
go get github.com/kelseyhightower/envconfig
```

### Основы и отличия от caarlos0/env

```go
package config

import (
    "time"

    "github.com/kelseyhightower/envconfig"
)

type Config struct {
    Host         string        `envconfig:"HOST" default:"0.0.0.0"`
    Port         int           `envconfig:"PORT" default:"8080"`
    Debug        bool          `envconfig:"DEBUG"`
    ReadTimeout  time.Duration `envconfig:"READ_TIMEOUT" default:"5s"`
    DatabaseURL  string        `envconfig:"DATABASE_URL" required:"true"`
    AllowedHosts []string      `envconfig:"ALLOWED_HOSTS" default:"localhost"`
}

func Load() (*Config, error) {
    var cfg Config
    // "myapp" — префикс. Все переменные: MYAPP_HOST, MYAPP_PORT и т.д.
    if err := envconfig.Process("myapp", &cfg); err != nil {
        return nil, err
    }
    return &cfg, nil
}
```

```bash
# Все переменные имеют префикс MYAPP_
export MYAPP_HOST=0.0.0.0
export MYAPP_PORT=9090
export MYAPP_DEBUG=true
export MYAPP_DATABASE_URL=postgres://user:pass@localhost/db
export MYAPP_ALLOWED_HOSTS=example.com,api.example.com
```

**Ключевое отличие от caarlos0/env**: envconfig использует **prefix** для namespace всех переменных. Это удобно когда несколько сервисов запущены в одном окружении.

### Struct tags и naming conventions

envconfig автоматически генерирует имена переменных из имён полей:

```go
type Config struct {
    // Автоматическое именование: CamelCase → SCREAMING_SNAKE
    DatabaseURL  string // → MYAPP_DATABASE_URL
    MaxOpenConns int    // → MYAPP_MAX_OPEN_CONNS
    EnableSSL    bool   // → MYAPP_ENABLE_SSL

    // Явное имя через тег
    DBHost string `envconfig:"DB_HOST"` // → MYAPP_DB_HOST

    // Вложенные структуры "сплющиваются"
    DB struct {
        Host string // → MYAPP_DB_HOST
        Port int    // → MYAPP_DB_PORT
    }

    // Игнорирование поля
    Internal string `envconfig:"-" ignored:"true"`
}
```

### Usage и help output

Уникальная фича envconfig — автоматическая генерация документации:

```go
func main() {
    var cfg Config
    err := envconfig.Process("myapp", &cfg)
    if err != nil {
        // Печатаем документацию по переменным
        envconfig.Usage("myapp", &cfg)
        os.Exit(1)
    }
}
```

Вывод `Usage`:
```
This application is configured via the environment. The following environment
variables can be used:

KEY                     TYPE        DEFAULT      REQUIRED    DESCRIPTION
MYAPP_HOST              String      0.0.0.0
MYAPP_PORT              Integer     8080
MYAPP_DEBUG             True/False
MYAPP_READ_TIMEOUT      Duration    5s
MYAPP_DATABASE_URL      String                   true
MYAPP_ALLOWED_HOSTS     Comma-separated list     localhost
```

Можно добавить описания через тег `desc`:

```go
type Config struct {
    Port        int    `envconfig:"PORT" default:"8080" desc:"порт HTTP-сервера"`
    DatabaseURL string `envconfig:"DATABASE_URL" required:"true" desc:"строка подключения к PostgreSQL"`
}
```

> 💡 **Usage() — килер-фича envconfig**. Ни caarlos0/env, ни viper не генерируют документацию автоматически. Это особенно ценно для DevOps-команды, которая деплоит ваш сервис.

---

## Сравнение env-библиотек

| Аспект | caarlos0/env | envconfig | Ручной os.Getenv |
|--------|-------------|-----------|-----------------|
| **Подход** | Struct tags | Prefix + struct | Helper-функции |
| **Именование** | Явное `env:"NAME"` | Авто из имени поля | Ручное |
| **Prefix** | `envPrefix` на вложенных | Глобальный prefix | Ручной |
| **Required** | `env:"...,required"` | `required:"true"` | `mustGetEnv()` |
| **Defaults** | `envDefault:"..."` | `default:"..."` | Второй аргумент |
| **File secrets** | `env:"...,file"` | Нет | Ручное чтение |
| **Expand $VAR** | `env:"...,expand"` | Нет | `os.ExpandEnv()` |
| **Usage/Help** | Нет | `Usage()` | Нет |
| **Custom типы** | `TextUnmarshaler` | `Decoder` interface | Ручной парсинг |
| **Популярность** | ~5K stars, активно | ~5K stars, стабильно | N/A |
| **Зависимости** | 0 | 0 | 0 |
| **Рекомендация** | **Новые проекты** | Проекты с prefix-конвенцией | Простые сервисы |

> 💡 **Рекомендация**: Для новых проектов используйте **caarlos0/env** — более гибкий, поддерживает file secrets, expand, активно развивается. **envconfig** — хороший выбор если вам нужен auto-generated usage или prefix-конвенция.

---

## Viper: полнофункциональная конфигурация

[github.com/spf13/viper](https://github.com/spf13/viper) — самая известная библиотека конфигурации в Go (~27K stars). Поддерживает файлы, env, flags, remote config и hot reload.

```bash
go get github.com/spf13/viper
```

### Установка и базовое использование

В [разделе 3.2](../part3-web-api/02_project_structure.md) мы видели базовый пример Viper. Теперь разберём все возможности.

```go
package main

import (
    "fmt"
    "log"

    "github.com/spf13/viper"
)

func main() {
    // Установка значений по умолчанию
    viper.SetDefault("server.host", "0.0.0.0")
    viper.SetDefault("server.port", 8080)
    viper.SetDefault("database.sslmode", "disable")

    // Чтение конфигурационного файла
    viper.SetConfigName("config")  // имя файла без расширения
    viper.SetConfigType("yaml")    // формат
    viper.AddConfigPath(".")       // путь поиска
    viper.AddConfigPath("./config")
    viper.AddConfigPath("$HOME/.myapp")

    if err := viper.ReadInConfig(); err != nil {
        if _, ok := err.(viper.ConfigFileNotFoundError); ok {
            log.Println("конфиг-файл не найден, используем defaults и env")
        } else {
            log.Fatalf("ошибка чтения конфига: %v", err)
        }
    }

    // Включаем автоматическое чтение env
    viper.AutomaticEnv()

    // Чтение значений
    host := viper.GetString("server.host")
    port := viper.GetInt("server.port")
    debug := viper.GetBool("debug")

    fmt.Printf("Сервер: %s:%d (debug=%v)\n", host, port, debug)
}
```

### Источники конфигурации и приоритеты

Viper поддерживает множество источников с чётким приоритетом (первый побеждает):

```
1. viper.Set()           — явно заданные значения (высший приоритет)
2. Флаги командной строки (pflag)
3. Переменные окружения
4. Конфигурационный файл
5. Key/Value store (etcd, Consul)
6. viper.SetDefault()    — значения по умолчанию (низший приоритет)
```

**C# аналог** — `ConfigurationBuilder`, но приоритет **обратный** (последний побеждает):
```csharp
// C# — последний AddXxx перезаписывает предыдущие
builder.Configuration
    .AddJsonFile("appsettings.json")           // 1. Базовый (низший)
    .AddJsonFile($"appsettings.{env}.json")    // 2. Перезаписывает
    .AddEnvironmentVariables()                  // 3. Перезаписывает
    .AddCommandLine(args);                      // 4. Высший приоритет
```

> ⚠️ **Разный порядок приоритетов!** В C# последний источник побеждает. В Viper — первый. При миграции с C# на Go это частый источник путаницы.

### Файлы конфигурации (YAML, TOML, JSON)

Viper поддерживает YAML, TOML, JSON, HCL, envfile и Java properties. YAML — самый популярный формат в Go-экосистеме.

`config.yaml`:
```yaml
server:
  host: 0.0.0.0
  port: 8080
  read_timeout: 5s
  write_timeout: 10s

database:
  host: localhost
  port: 5432
  user: admin
  password: "" # Лучше через env!
  name: myapp
  sslmode: disable
  max_open_conns: 25
  max_idle_conns: 5
  conn_max_lifetime: 5m

redis:
  addr: localhost:6379
  password: ""
  db: 0

log:
  level: info
  format: json
```

```go
// Чтение вложенных ключей — через точку
host := viper.GetString("database.host")
port := viper.GetInt("database.port")
timeout := viper.GetDuration("server.read_timeout")
```

**C# аналог**:
```csharp
// appsettings.json — JSON вместо YAML
{
    "Database": {
        "Host": "localhost",
        "Port": 5432
    }
}

// Доступ через секции
var host = config.GetSection("Database")["Host"];
// Или через IOptions<T>
var host = options.Value.Host;
```

### Переменные окружения и AutomaticEnv

```go
// AutomaticEnv — viper автоматически ищет env для каждого ключа
viper.AutomaticEnv()

// Prefix — все env-переменные должны начинаться с MYAPP_
viper.SetEnvPrefix("MYAPP")

// server.host → MYAPP_SERVER_HOST
// Но точки в ключах не совпадают с подчёркиваниями в env!
// Нужен replacer:
viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))

// Теперь:
// viper.GetString("server.host") → ищет MYAPP_SERVER_HOST

// Явная привязка env к ключу (для нестандартных имён)
viper.BindEnv("database.password", "DB_PASSWORD") // без prefix
```

> ⚠️ **Главный подводный камень Viper**: `AutomaticEnv()` работает **только с `Get*()`**, но **НЕ работает с `Unmarshal()`**. Это самый частый баг при использовании Viper:

```go
// ❌ AutomaticEnv НЕ заполнит поля при Unmarshal
viper.AutomaticEnv()
var cfg Config
viper.Unmarshal(&cfg) // env-переменные НЕ попадут в структуру!

// ✅ Нужно явно привязывать env к каждому ключу
viper.BindEnv("server.host", "SERVER_HOST")
viper.BindEnv("server.port", "SERVER_PORT")
// ... для каждого поля

// Или использовать viper.Get*() вместо Unmarshal
host := viper.GetString("server.host") // ✅ AutomaticEnv работает
```

Это **серьёзное архитектурное ограничение** Viper, из-за которого многие команды переходят на koanf или caarlos0/env.

### Unmarshal в структуры

Viper использует `mapstructure` для десериализации в структуры:

```go
type Config struct {
    Server   ServerConfig   `mapstructure:"server"`
    Database DatabaseConfig `mapstructure:"database"`
    Redis    RedisConfig    `mapstructure:"redis"`
    Log      LogConfig      `mapstructure:"log"`
}

type ServerConfig struct {
    Host         string        `mapstructure:"host"`
    Port         int           `mapstructure:"port"`
    ReadTimeout  time.Duration `mapstructure:"read_timeout"`
    WriteTimeout time.Duration `mapstructure:"write_timeout"`
}

type DatabaseConfig struct {
    Host           string        `mapstructure:"host"`
    Port           int           `mapstructure:"port"`
    User           string        `mapstructure:"user"`
    Password       string        `mapstructure:"password"`
    Name           string        `mapstructure:"name"`
    SSLMode        string        `mapstructure:"sslmode"`
    MaxOpenConns   int           `mapstructure:"max_open_conns"`
    MaxIdleConns   int           `mapstructure:"max_idle_conns"`
    ConnMaxLifetime time.Duration `mapstructure:"conn_max_lifetime"`
}

func LoadConfig() (*Config, error) {
    viper.SetConfigName("config")
    viper.SetConfigType("yaml")
    viper.AddConfigPath(".")

    if err := viper.ReadInConfig(); err != nil {
        return nil, fmt.Errorf("чтение конфига: %w", err)
    }

    var cfg Config
    // DecoderConfigOption для корректной обработки time.Duration
    if err := viper.Unmarshal(&cfg, viper.DecodeHook(
        mapstructure.ComposeDecodeHookFunc(
            mapstructure.StringToTimeDurationHookFunc(),
            mapstructure.StringToSliceHookFunc(","),
        ),
    )); err != nil {
        return nil, fmt.Errorf("десериализация конфига: %w", err)
    }

    return &cfg, nil
}
```

**C# аналог**:
```csharp
// C# — привязка секции к классу через DI
services.Configure<ServerConfig>(config.GetSection("Server"));
services.Configure<DatabaseConfig>(config.GetSection("Database"));

// Или напрямую
var serverConfig = config.GetSection("Server").Get<ServerConfig>();
```

> 💡 **mapstructure теги**: Viper использует `mapstructure` (не `json` или `yaml`) для десериализации. Это отдельная библиотека с собственными тегами. Если забыть `mapstructure:"..."` тег — поля не заполнятся.

### WatchConfig: горячая перезагрузка

```go
import (
    "log"
    "sync"

    "github.com/fsnotify/fsnotify"
    "github.com/spf13/viper"
)

var (
    cfg    *Config
    cfgMu  sync.RWMutex
)

func initConfig() {
    viper.SetConfigName("config")
    viper.SetConfigType("yaml")
    viper.AddConfigPath(".")

    if err := viper.ReadInConfig(); err != nil {
        log.Fatalf("ошибка чтения конфига: %v", err)
    }

    // Первоначальная загрузка
    cfgMu.Lock()
    cfg = mustUnmarshalConfig()
    cfgMu.Unlock()

    // Горячая перезагрузка при изменении файла
    viper.WatchConfig()
    viper.OnConfigChange(func(e fsnotify.Event) {
        log.Printf("конфиг изменён: %s", e.Name)

        newCfg := mustUnmarshalConfig()

        cfgMu.Lock()
        cfg = newCfg
        cfgMu.Unlock()

        log.Println("конфигурация перезагружена")
    })
}

func GetConfig() *Config {
    cfgMu.RLock()
    defer cfgMu.RUnlock()
    return cfg
}
```

**C# аналог**:
```csharp
// IOptionsMonitor<T> — автоматический reload при изменении файла
public class MyService(IOptionsMonitor<ServerConfig> monitor)
{
    public void DoWork()
    {
        var current = monitor.CurrentValue; // всегда актуальное значение
    }
}

// IOptionsSnapshot<T> — снимок на время запроса (scoped)
public class MyController(IOptionsSnapshot<ServerConfig> snapshot)
{
    public IActionResult Get() => Ok(snapshot.Value);
}
```

> ⚠️ **Thread safety**: Viper сам по себе **не потокобезопасен** при записи + чтении. `WatchConfig` вызывает callback в отдельной горутине. Обязательно используйте `sync.RWMutex` или `atomic.Pointer` для защиты конфига.

### Remote Config (etcd, Consul)

Viper поддерживает удалённые хранилища конфигурации:

```go
import (
    "github.com/spf13/viper"
    _ "github.com/spf13/viper/remote" // подключение remote provider
)

func loadFromConsul() error {
    viper.AddRemoteProvider("consul", "localhost:8500", "myapp/config")
    viper.SetConfigType("yaml")

    if err := viper.ReadRemoteConfig(); err != nil {
        return fmt.Errorf("чтение remote config: %w", err)
    }

    // Периодическое обновление (polling)
    go func() {
        for {
            time.Sleep(5 * time.Second)
            if err := viper.WatchRemoteConfig(); err != nil {
                log.Printf("ошибка обновления remote config: %v", err)
            }
        }
    }()

    return nil
}
```

> 💡 **Remote config** полезен для централизованного управления настройками множества сервисов. Но для секретов лучше использовать HashiCorp Vault (раздел [Секреты и безопасность](#секреты-и-безопасность)).

### Проблемы Viper и когда НЕ использовать

**Проблемы Viper** (о которых важно знать):

1. **Глобальный state по умолчанию**: `viper.Get*()` работает с глобальным синглтоном. Это затрудняет тестирование и создаёт скрытые зависимости.

```go
// ❌ Глобальный Viper — скрытая зависимость
func NewServer() *Server {
    port := viper.GetInt("server.port") // откуда взялось?
    return &Server{port: port}
}

// ✅ Явная зависимость — передача Config через конструктор
func NewServer(cfg ServerConfig) *Server {
    return &Server{port: cfg.Port}
}
```

2. **Тяжёлое дерево зависимостей**: spf13/pflag, fsnotify, mapstructure, и многое другое. Для простого микросервиса — чрезмерно.

3. **AutomaticEnv не работает с Unmarshal**: Как показано выше — это фундаментальная проблема дизайна.

4. **Thread safety**: Нет встроенной защиты от concurrent access.

5. **Медленная рефлексия**: mapstructure использует рефлексию. Для конфигурации это несущественно (загрузка однократная), но стоит знать.

**Когда НЕ использовать Viper**:

| Ситуация | Альтернатива |
|----------|-------------|
| Только env-переменные (12-Factor) | caarlos0/env |
| Простой микросервис | caarlos0/env или cleanenv |
| Нужна модульность и чистая архитектура | koanf |
| Только CLI-утилита | cobra + pflag |

**Когда Viper оправдан**:
- Сложное приложение с файлами + env + flags + remote config
- Легаси-проект, уже использующий Viper
- Нужен WatchConfig из коробки

---

## koanf: современная альтернатива Viper

[github.com/knadh/koanf](https://github.com/knadh/koanf) — модульная библиотека конфигурации без глобального state. Решает основные проблемы Viper: модульность, чистая архитектура, минимальные зависимости.

```bash
go get github.com/knadh/koanf/v2
# Провайдеры и парсеры устанавливаются отдельно
go get github.com/knadh/koanf/providers/file
go get github.com/knadh/koanf/providers/env
go get github.com/knadh/koanf/parsers/yaml
```

### Архитектура: Providers и Parsers

koanf построен на двух абстракциях:
- **Provider** — источник данных (файл, env, flags, remote)
- **Parser** — формат данных (YAML, JSON, TOML)

Вы импортируете **только то, что используете**:

```go
import (
    "github.com/knadh/koanf/v2"
    "github.com/knadh/koanf/providers/file"
    "github.com/knadh/koanf/providers/env"
    "github.com/knadh/koanf/parsers/yaml"
)

// Создание экземпляра — никакого глобального state
var k = koanf.New(".")
```

**Сравнение с Viper**:
```go
// Viper — глобальный синглтон
viper.GetString("database.host") // откуда взялось?

// koanf — явный экземпляр
k := koanf.New(".")
k.String("database.host") // k передаётся явно
```

### Файлы, ENV, flags

```go
package config

import (
    "fmt"
    "log"
    "strings"

    "github.com/knadh/koanf/v2"
    "github.com/knadh/koanf/parsers/yaml"
    "github.com/knadh/koanf/providers/env"
    "github.com/knadh/koanf/providers/file"
)

func Load(configPath string) (*koanf.Koanf, error) {
    k := koanf.New(".")

    // 1. Загрузка из YAML-файла (низший приоритет)
    if err := k.Load(file.Provider(configPath), yaml.Parser()); err != nil {
        // Файл необязателен
        log.Printf("конфиг-файл не найден: %v", err)
    }

    // 2. Загрузка из env (перезаписывает файл)
    // APP_SERVER_HOST → server.host
    err := k.Load(env.Provider("APP_", ".", func(s string) string {
        return strings.Replace(
            strings.ToLower(strings.TrimPrefix(s, "APP_")),
            "_", ".", -1)
    }), nil)
    if err != nil {
        return nil, fmt.Errorf("загрузка env: %w", err)
    }

    return k, nil
}
```

```bash
# Env-переменные перезаписывают значения из файла
export APP_SERVER_HOST=10.0.0.1
export APP_SERVER_PORT=9090
export APP_DATABASE_HOST=db.production.internal
```

Интеграция с **pflag** (CLI-аргументы):

```go
import (
    "github.com/knadh/koanf/providers/posflag"
    "github.com/spf13/pflag"
)

func Load() (*koanf.Koanf, error) {
    k := koanf.New(".")

    // 1. Файл (низший приоритет)
    k.Load(file.Provider("config.yaml"), yaml.Parser())

    // 2. ENV
    k.Load(env.Provider("APP_", ".", transformer), nil)

    // 3. CLI flags (высший приоритет)
    f := pflag.NewFlagSet("app", pflag.ExitOnError)
    f.String("server.host", "", "адрес сервера")
    f.Int("server.port", 0, "порт сервера")
    f.Parse(os.Args[1:])

    // Загружаем только явно заданные флаги
    k.Load(posflag.Provider(f, ".", k), nil)

    return k, nil
}
```

### Unmarshal и struct tags

```go
type Config struct {
    Server   ServerConfig   `koanf:"server"`
    Database DatabaseConfig `koanf:"database"`
    Redis    RedisConfig    `koanf:"redis"`
}

type ServerConfig struct {
    Host         string        `koanf:"host"`
    Port         int           `koanf:"port"`
    ReadTimeout  time.Duration `koanf:"read_timeout"`
    WriteTimeout time.Duration `koanf:"write_timeout"`
}

type DatabaseConfig struct {
    Host     string `koanf:"host"`
    Port     int    `koanf:"port"`
    User     string `koanf:"user"`
    Password string `koanf:"password"`
    Name     string `koanf:"name"`
}

func LoadConfig(path string) (*Config, error) {
    k, err := Load(path)
    if err != nil {
        return nil, err
    }

    var cfg Config
    if err := k.Unmarshal("", &cfg); err != nil {
        return nil, fmt.Errorf("десериализация: %w", err)
    }

    // Unmarshal подсекции
    // var dbCfg DatabaseConfig
    // k.Unmarshal("database", &dbCfg)

    return &cfg, nil
}
```

> 💡 **koanf vs viper теги**: koanf использует тег `koanf:"..."`, viper — `mapstructure:"..."`. При миграции нужно заменить теги.

### Watch и reload

koanf поддерживает наблюдение за файлами через callback:

```go
import (
    "sync/atomic"

    "github.com/knadh/koanf/v2"
    "github.com/knadh/koanf/parsers/yaml"
    "github.com/knadh/koanf/providers/file"
)

type ConfigManager struct {
    config atomic.Pointer[Config]
    k      *koanf.Koanf
}

func NewConfigManager(path string) (*ConfigManager, error) {
    cm := &ConfigManager{
        k: koanf.New("."),
    }

    // Первоначальная загрузка
    if err := cm.reload(path); err != nil {
        return nil, err
    }

    // Наблюдение за файлом (polling)
    f := file.Provider(path)
    f.Watch(func(event interface{}, err error) {
        if err != nil {
            log.Printf("ошибка watch: %v", err)
            return
        }

        log.Println("конфиг-файл изменён, перезагрузка...")
        if err := cm.reload(path); err != nil {
            log.Printf("ошибка перезагрузки: %v", err)
            return
        }
        log.Println("конфигурация обновлена")
    })

    return cm, nil
}

func (cm *ConfigManager) reload(path string) error {
    // Создаём новый koanf для чистой загрузки
    k := koanf.New(".")
    if err := k.Load(file.Provider(path), yaml.Parser()); err != nil {
        return fmt.Errorf("загрузка файла: %w", err)
    }

    var cfg Config
    if err := k.Unmarshal("", &cfg); err != nil {
        return fmt.Errorf("десериализация: %w", err)
    }

    // Атомарная замена конфигурации
    cm.config.Store(&cfg)
    return nil
}

func (cm *ConfigManager) Get() *Config {
    return cm.config.Load()
}
```

### Viper vs koanf

| Аспект | Viper | koanf |
|--------|-------|-------|
| **Глобальный state** | Да (по умолчанию) | Нет |
| **Зависимости** | Тяжёлые (~20 deps) | Модульные (по выбору) |
| **Struct tags** | `mapstructure:"..."` | `koanf:"..."` |
| **ENV + Unmarshal** | ❌ AutomaticEnv не работает | ✅ Работает корректно |
| **Thread safety** | ❌ Нет встроенной | ❌ Нет встроенной |
| **Модульность** | Монолит | Provider + Parser |
| **Remote config** | Встроенный | Через провайдеры |
| **Сообщество** | ~27K stars, стабильно | ~3K stars, растёт |
| **API** | Широкий (Get*, Set, Sub) | Минималистичный |
| **Рекомендация** | Легаси, сложные проекты | **Новые проекты** |

> 💡 **Рекомендация**: Для новых проектов с файлами конфигурации выбирайте **koanf**. Для env-only проектов — **caarlos0/env**.

---

## cleanenv: лёгкая альтернатива

[github.com/ilyakaznacheev/cleanenv](https://github.com/ilyakaznacheev/cleanenv) — простая библиотека, которая объединяет файл и env в одной структуре. Идеальна для небольших и средних проектов.

```bash
go get github.com/ilyakaznacheev/cleanenv
```

```go
package config

import (
    "github.com/ilyakaznacheev/cleanenv"
)

type Config struct {
    Server struct {
        Host string `yaml:"host" env:"SERVER_HOST" env-default:"0.0.0.0"`
        Port int    `yaml:"port" env:"SERVER_PORT" env-default:"8080"`
    } `yaml:"server"`

    Database struct {
        Host     string `yaml:"host" env:"DB_HOST" env-default:"localhost"`
        Port     int    `yaml:"port" env:"DB_PORT" env-default:"5432"`
        User     string `yaml:"user" env:"DB_USER" env-required:"true"`
        Password string `yaml:"password" env:"DB_PASSWORD" env-required:"true"`
        Name     string `yaml:"name" env:"DB_NAME" env-default:"myapp"`
    } `yaml:"database"`

    Log struct {
        Level string `yaml:"level" env:"LOG_LEVEL" env-default:"info"`
    } `yaml:"log"`
}

func Load(path string) (*Config, error) {
    var cfg Config

    // Читает файл, затем накладывает env-переменные
    if err := cleanenv.ReadConfig(path, &cfg); err != nil {
        return nil, err
    }

    return &cfg, nil
}
```

`config.yaml`:
```yaml
server:
  host: 0.0.0.0
  port: 8080

database:
  host: localhost
  port: 5432
  name: myapp

log:
  level: info
```

```bash
# env перезаписывает значения из файла
export DB_USER=admin
export DB_PASSWORD=secret
export LOG_LEVEL=debug
```

**Автоматический help output** (аналог envconfig.Usage):

```go
func main() {
    var cfg Config
    help, _ := cleanenv.GetDescription(&cfg, nil)
    fmt.Println(help)
}
```

Вывод:
```
Environment variables:
  SERVER_HOST string (default: "0.0.0.0")
  SERVER_PORT int (default: "8080")
  DB_HOST string (default: "localhost")
  DB_USER string (required)
  DB_PASSWORD string (required)
  ...
```

> 💡 **cleanenv — золотая середина**: проще Viper, мощнее caarlos0/env. Файл + ENV в одной структуре с одними тегами. Идеальна для проектов, где нужен конфиг-файл, но не нужна сложность Viper.

---

## Сравнительная таблица всех библиотек

| Аспект | os.Getenv | caarlos0/env | envconfig | cleanenv | Viper | koanf |
|--------|-----------|-------------|-----------|----------|-------|-------|
| **Config файлы** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **ENV** | Ручной | Tags | Tags | Tags | Auto/Bind | Provider |
| **CLI flags** | flag | ❌ | ❌ | ❌ | pflag | pflag |
| **Hot reload** | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Remote config** | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Зависимости** | 0 | 0 | 0 | Минимум | Много | Модульные |
| **Struct-first** | ❌ | ✅ | ✅ | ✅ | Опционально | Опционально |
| **Глобальный state** | ❌ | ❌ | ❌ | ❌ | ✅ (default) | ❌ |
| **Usage/Help** | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| **File secrets** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **GitHub stars** | N/A | ~5K | ~5K | ~1K | ~27K | ~3K |

---

## Блок-схема выбора библиотеки

```
Нужны ли config-файлы (YAML/TOML/JSON)?
│
├─ НЕТ (только env) ──────────────────────┐
│   │                                       │
│   └─ Нужна автоматическая документация? ──┤
│       │                                   │
│       ├─ ДА → envconfig                   │
│       └─ НЕТ → caarlos0/env ★            │
│                                           │
└─ ДА (файлы + env) ──────────────────────┐│
    │                                      ││
    ├─ Простой проект (файл + env)?        ││
    │   └─ ДА → cleanenv                   ││
    │                                      ││
    ├─ Нужен hot reload / remote config?   ││
    │   │                                  ││
    │   ├─ Новый проект → koanf ★          ││
    │   └─ Легаси / сложный → Viper        ││
    │                                      ││
    └─ Скрипт / утилита?                   ││
        └─ os.Getenv + flag                ││
                                           ││
★ = рекомендуемый выбор                    ││
```

> 💡 **Для большинства Go-микросервисов** достаточно **caarlos0/env**. 12-Factor App рекомендует env-переменные, а config-файлы — это рудимент десктопных приложений. Файлы конфигурации оправданы для сложных систем с большим количеством настроек.

---

## Валидация конфигурации

### Fail fast при запуске

Главный принцип: **если конфигурация невалидна — приложение не должно запускаться**. Лучше упасть при старте с понятной ошибкой, чем через час в production с непонятной.

```go
func main() {
    cfg, err := config.Load()
    if err != nil {
        // Приложение НЕ запускается с невалидным конфигом
        log.Fatalf("невалидная конфигурация: %v", err)
    }

    // Дополнительная валидация бизнес-правил
    if err := cfg.Validate(); err != nil {
        log.Fatalf("ошибка валидации конфигурации: %v", err)
    }

    // Только после успешной валидации — запуск сервера
    run(cfg)
}
```

**C# аналог**:
```csharp
// .NET 8 — ValidateOnStart
builder.Services
    .AddOptions<DatabaseOptions>()
    .Bind(config.GetSection("Database"))
    .ValidateDataAnnotations()  // [Required], [Range], etc.
    .ValidateOnStart();          // Проверка при запуске!
```

> ⚠️ **Распространённая ошибка**: Валидация конфигурации "по запросу" — когда сервис узнаёт о невалидном конфиге только при первом использовании. В Go нет `ValidateOnStart()` из коробки — реализуйте это явно.

### go-playground/validator для конфигов

```bash
go get github.com/go-playground/validator/v10
```

```go
package config

import (
    "fmt"
    "time"

    "github.com/caarlos0/env/v11"
    "github.com/go-playground/validator/v10"
)

type Config struct {
    Server   ServerConfig   `validate:"required"`
    Database DatabaseConfig `validate:"required"`
    Redis    RedisConfig    `validate:"required"`
}

type ServerConfig struct {
    Host         string        `env:"SERVER_HOST" envDefault:"0.0.0.0" validate:"required,ip|hostname"`
    Port         int           `env:"SERVER_PORT" envDefault:"8080" validate:"required,min=1,max=65535"`
    ReadTimeout  time.Duration `env:"SERVER_READ_TIMEOUT" envDefault:"5s" validate:"required,min=1000000000"`  // min 1s
    WriteTimeout time.Duration `env:"SERVER_WRITE_TIMEOUT" envDefault:"10s" validate:"required,min=1000000000"` // min 1s
}

type DatabaseConfig struct {
    Host     string `env:"DB_HOST" envDefault:"localhost" validate:"required,hostname|ip"`
    Port     int    `env:"DB_PORT" envDefault:"5432" validate:"required,min=1,max=65535"`
    User     string `env:"DB_USER,required" validate:"required,min=1"`
    Password string `env:"DB_PASSWORD,required" validate:"required,min=8"` // минимум 8 символов
    Name     string `env:"DB_NAME" envDefault:"myapp" validate:"required,min=1,max=63"`
    SSLMode  string `env:"DB_SSLMODE" envDefault:"disable" validate:"required,oneof=disable allow prefer require verify-ca verify-full"`
    MaxConns int    `env:"DB_MAX_CONNS" envDefault:"25" validate:"min=1,max=1000"`
}

type RedisConfig struct {
    Addr     string `env:"REDIS_ADDR" envDefault:"localhost:6379" validate:"required"`
    Password string `env:"REDIS_PASSWORD"`
    DB       int    `env:"REDIS_DB" envDefault:"0" validate:"min=0,max=15"`
}

var validate = validator.New()

func Load() (*Config, error) {
    cfg := &Config{}

    // 1. Парсинг env
    if err := env.Parse(cfg); err != nil {
        return nil, fmt.Errorf("парсинг env: %w", err)
    }

    // 2. Валидация структуры
    if err := validate.Struct(cfg); err != nil {
        return nil, fmt.Errorf("валидация: %w", formatValidationErrors(err))
    }

    return cfg, nil
}

// formatValidationErrors — человекочитаемые ошибки валидации
func formatValidationErrors(err error) error {
    validationErrors, ok := err.(validator.ValidationErrors)
    if !ok {
        return err
    }

    var messages []string
    for _, e := range validationErrors {
        switch e.Tag() {
        case "required":
            messages = append(messages, fmt.Sprintf("%s: обязательное поле", e.Namespace()))
        case "min":
            messages = append(messages, fmt.Sprintf("%s: минимальное значение %s", e.Namespace(), e.Param()))
        case "max":
            messages = append(messages, fmt.Sprintf("%s: максимальное значение %s", e.Namespace(), e.Param()))
        case "oneof":
            messages = append(messages, fmt.Sprintf("%s: допустимые значения: %s", e.Namespace(), e.Param()))
        default:
            messages = append(messages, fmt.Sprintf("%s: не прошло проверку '%s'", e.Namespace(), e.Tag()))
        }
    }

    return fmt.Errorf("ошибки валидации:\n  - %s", strings.Join(messages, "\n  - "))
}
```

Пример вывода при невалидном конфиге:
```
FATAL: валидация: ошибки валидации:
  - Config.Database.Password: минимальное значение 8
  - Config.Database.SSLMode: допустимые значения: disable allow prefer require verify-ca verify-full
  - Config.Server.Port: максимальное значение 65535
```

### Custom validation logic

Для сложных бизнес-правил — метод `Validate()` на структуре:

```go
func (c *Config) Validate() error {
    var errs []error

    // Бизнес-правило: WriteTimeout > ReadTimeout
    if c.Server.WriteTimeout <= c.Server.ReadTimeout {
        errs = append(errs, fmt.Errorf(
            "server.write_timeout (%v) должен быть больше server.read_timeout (%v)",
            c.Server.WriteTimeout, c.Server.ReadTimeout,
        ))
    }

    // Бизнес-правило: в production обязателен SSL
    if c.Database.SSLMode == "disable" {
        if env := os.Getenv("APP_ENV"); env == "production" {
            errs = append(errs, fmt.Errorf(
                "database.sslmode=disable запрещён в production",
            ))
        }
    }

    // Бизнес-правило: MaxConns >= MaxIdleConns
    if c.Database.MaxConns > 0 && c.Database.MaxIdleConns > c.Database.MaxConns {
        errs = append(errs, fmt.Errorf(
            "database.max_idle_conns (%d) не может превышать max_conns (%d)",
            c.Database.MaxIdleConns, c.Database.MaxConns,
        ))
    }

    return errors.Join(errs...)
}
```

> 💡 **`errors.Join` (Go 1.20+)** — идеальный способ собрать множественные ошибки валидации. В C# аналог — `AggregateException` или `ValidationResult` коллекция.

---

## Паттерны конфигурации

### 12-Factor App: конфигурация через ENV

[12-Factor App](https://12factor.net/config) (Factor III) гласит: **конфигурация хранится в переменных окружения**. Это де-факто стандарт для облачных приложений.

**Почему ENV**:
- Языконезависимы (работают с Go, C#, Python, Java)
- Не попадают в git (в отличие от config-файлов)
- Легко менять между средами (dev/staging/prod)
- Нативная поддержка в Docker, Kubernetes, CI/CD
- Одинаково работают на всех ОС

**Когда файлы конфигурации оправданы**:
- Сложная вложенная структура (>50 параметров)
- Конфигурация, которую удобнее редактировать в YAML/TOML
- Локальная разработка без Docker
- Конфиг, который должен быть под версионным контролем

```go
// ✅ 12-Factor подход: только env
type Config struct {
    Port        int           `env:"PORT" envDefault:"8080"`
    DatabaseURL string        `env:"DATABASE_URL,required"`
    RedisURL    string        `env:"REDIS_URL,required"`
    LogLevel    string        `env:"LOG_LEVEL" envDefault:"info"`
    Timeout     time.Duration `env:"TIMEOUT" envDefault:"30s"`
}

// ❌ Не 12-Factor: хардкод путей к файлам
// config := LoadFromFile("/etc/myapp/config.yaml")
```

### Multi-environment (dev/staging/prod)

Паттерн: **одинаковый код, разная конфигурация**:

```go
type Config struct {
    Env string `env:"APP_ENV" envDefault:"development"` // development, staging, production

    Server   ServerConfig
    Database DatabaseConfig
    Log      LogConfig
}

func Load() (*Config, error) {
    cfg := &Config{}

    // В development загружаем .env файл
    if os.Getenv("APP_ENV") == "" || os.Getenv("APP_ENV") == "development" {
        _ = godotenv.Load(".env.development")
    }

    if err := env.Parse(cfg); err != nil {
        return nil, err
    }

    // Среда влияет на defaults
    if cfg.Env == "production" {
        if cfg.Log.Level == "" {
            cfg.Log.Level = "warn"
        }
        if cfg.Database.SSLMode == "" {
            cfg.Database.SSLMode = "require"
        }
    }

    return cfg, nil
}
```

```bash
# .env.development
APP_ENV=development
DB_HOST=localhost
DB_USER=developer
DB_PASSWORD=devpass
DB_SSLMODE=disable
LOG_LEVEL=debug

# Production — через оркестратор (K8s, Docker Compose)
# APP_ENV=production
# DB_HOST=db.internal
# DB_USER=app_user
# DB_PASSWORD=<из Vault>
# DB_SSLMODE=verify-full
# LOG_LEVEL=warn
```

**C# аналог**:
```csharp
// Автоматический выбор файла по ASPNETCORE_ENVIRONMENT
builder.Configuration
    .AddJsonFile("appsettings.json")
    .AddJsonFile($"appsettings.{env.EnvironmentName}.json", optional: true);
```

### Immutable config vs hot reload

**Immutable config** (рекомендуемый подход):
```go
// Загружаем один раз при старте — Config неизменяем
func main() {
    cfg, err := config.Load()
    if err != nil {
        log.Fatal(err)
    }

    // Передаём по значению или указателю — никто не может изменить
    server := api.NewServer(cfg.Server)
    repo := postgres.NewRepository(cfg.Database)
}
```

**Hot reload** (когда действительно нужен):
```go
// Сценарии для hot reload:
// - Уровень логирования (переключить на debug в production без рестарта)
// - Rate limiting (изменить лимиты без даунтайма)
// - Feature flags (включить/выключить функции)

type ConfigManager struct {
    config atomic.Pointer[Config]
}

func (cm *ConfigManager) Get() *Config {
    return cm.config.Load()
}

func (cm *ConfigManager) Update(newCfg *Config) {
    cm.config.Store(newCfg)
}
```

**C# аналог**:
```csharp
// IOptions<T>        — immutable, создаётся один раз (Singleton)
// IOptionsSnapshot<T> — обновляется каждый запрос (Scoped)
// IOptionsMonitor<T>  — уведомляет об изменениях (Singleton, live reload)
```

> 💡 **Правило**: Используйте immutable config по умолчанию. Hot reload — только для параметров, которые **действительно** нужно менять без рестарта. Чем меньше mutable state — тем проще отладка.

### Functional Options для конфигурации

Functional Options — Go-паттерн для конфигурирования библиотек и компонентов:

```go
// Определение компонента с Options
type Server struct {
    host         string
    port         int
    readTimeout  time.Duration
    writeTimeout time.Duration
    logger       *slog.Logger
}

type Option func(*Server)

func WithHost(host string) Option {
    return func(s *Server) { s.host = host }
}

func WithPort(port int) Option {
    return func(s *Server) { s.port = port }
}

func WithTimeouts(read, write time.Duration) Option {
    return func(s *Server) {
        s.readTimeout = read
        s.writeTimeout = write
    }
}

func WithLogger(logger *slog.Logger) Option {
    return func(s *Server) { s.logger = logger }
}

func NewServer(opts ...Option) *Server {
    // Defaults
    s := &Server{
        host:         "0.0.0.0",
        port:         8080,
        readTimeout:  5 * time.Second,
        writeTimeout: 10 * time.Second,
        logger:       slog.Default(),
    }

    for _, opt := range opts {
        opt(s)
    }

    return s
}

// Использование
func main() {
    cfg, _ := config.Load()

    srv := NewServer(
        WithHost(cfg.Server.Host),
        WithPort(cfg.Server.Port),
        WithTimeouts(cfg.Server.ReadTimeout, cfg.Server.WriteTimeout),
    )
}
```

> 💡 **Functional Options vs Config struct**: Для внутренних компонентов приложения предпочтительнее Config struct (проще, явнее). Functional Options — для публичных библиотек, где нужна обратная совместимость и необязательные параметры.

---

## Секреты и безопасность

### Почему НЕ хранить секреты в config-файлах

```yaml
# ❌ НИКОГДА не делайте так!
database:
  password: "my-super-secret-password"

redis:
  password: "redis-password-123"

api_key: "sk-1234567890abcdef"
```

**Проблемы**:
1. **Git history** — даже после удаления, секрет остаётся в истории коммитов
2. **Логи** — config-файлы могут попасть в логи при отладке
3. **Shared access** — доступ к репозиторию = доступ к секретам
4. **Нет ротации** — смена секрета требует коммита и деплоя

**Правильный подход**: секреты через env-переменные или secret manager.

### HashiCorp Vault

```bash
go get github.com/hashicorp/vault/api
```

```go
package secrets

import (
    "context"
    "fmt"

    vault "github.com/hashicorp/vault/api"
)

type VaultClient struct {
    client *vault.Client
}

func NewVaultClient(addr, token string) (*VaultClient, error) {
    config := vault.DefaultConfig()
    config.Address = addr

    client, err := vault.NewClient(config)
    if err != nil {
        return nil, fmt.Errorf("создание vault клиента: %w", err)
    }

    client.SetToken(token)

    return &VaultClient{client: client}, nil
}

// GetSecret читает секрет из Vault KV v2
func (vc *VaultClient) GetSecret(ctx context.Context, path, key string) (string, error) {
    secret, err := vc.client.KVv2("secret").Get(ctx, path)
    if err != nil {
        return "", fmt.Errorf("чтение секрета %s: %w", path, err)
    }

    value, ok := secret.Data[key].(string)
    if !ok {
        return "", fmt.Errorf("секрет %s/%s не найден или не строка", path, key)
    }

    return value, nil
}

// Использование в загрузке конфигурации
func LoadWithSecrets() (*Config, error) {
    cfg := &Config{}
    if err := env.Parse(cfg); err != nil {
        return nil, err
    }

    // Загрузка секретов из Vault (если настроен)
    vaultAddr := os.Getenv("VAULT_ADDR")
    vaultToken := os.Getenv("VAULT_TOKEN")

    if vaultAddr != "" && vaultToken != "" {
        vc, err := NewVaultClient(vaultAddr, vaultToken)
        if err != nil {
            return nil, fmt.Errorf("подключение к vault: %w", err)
        }

        ctx := context.Background()

        // Перезаписываем секреты из Vault
        if dbPass, err := vc.GetSecret(ctx, "myapp/database", "password"); err == nil {
            cfg.Database.Password = dbPass
        }

        if redisPass, err := vc.GetSecret(ctx, "myapp/redis", "password"); err == nil {
            cfg.Redis.Password = redisPass
        }
    }

    return cfg, nil
}
```

**C# аналог**:
```csharp
// Azure Key Vault
builder.Configuration.AddAzureKeyVault(
    new Uri("https://myapp-vault.vault.azure.net/"),
    new DefaultAzureCredential());

// Секреты автоматически становятся частью IConfiguration
var dbPassword = config["Database:Password"]; // из Key Vault
```

### AWS Secrets Manager

```go
package secrets

import (
    "context"
    "encoding/json"
    "fmt"

    "github.com/aws/aws-sdk-go-v2/config"
    "github.com/aws/aws-sdk-go-v2/service/secretsmanager"
)

type AWSSecrets struct {
    client *secretsmanager.Client
}

func NewAWSSecrets(ctx context.Context) (*AWSSecrets, error) {
    cfg, err := config.LoadDefaultConfig(ctx)
    if err != nil {
        return nil, fmt.Errorf("загрузка AWS config: %w", err)
    }

    return &AWSSecrets{
        client: secretsmanager.NewFromConfig(cfg),
    }, nil
}

// GetSecretJSON читает JSON-секрет из AWS Secrets Manager
func (as *AWSSecrets) GetSecretJSON(ctx context.Context, name string) (map[string]string, error) {
    result, err := as.client.GetSecretValue(ctx, &secretsmanager.GetSecretValueInput{
        SecretId: &name,
    })
    if err != nil {
        return nil, fmt.Errorf("чтение секрета %s: %w", name, err)
    }

    var data map[string]string
    if err := json.Unmarshal([]byte(*result.SecretString), &data); err != nil {
        return nil, fmt.Errorf("парсинг секрета %s: %w", name, err)
    }

    return data, nil
}
```

### Kubernetes Secrets и ConfigMaps

В Kubernetes секреты монтируются как файлы или env-переменные:

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
        - name: myapp
          env:
            # Из ConfigMap
            - name: SERVER_PORT
              valueFrom:
                configMapKeyRef:
                  name: myapp-config
                  key: server-port

            # Из Secret
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: myapp-secrets
                  key: db-password

          # Или монтирование как файлы
          volumeMounts:
            - name: secrets
              mountPath: /run/secrets
              readOnly: true

      volumes:
        - name: secrets
          secret:
            secretName: myapp-secrets
```

```go
// Чтение секрета из файла (Docker/K8s secrets)
type Config struct {
    // Переменная содержит путь к файлу с секретом
    DBPassword string `env:"DB_PASSWORD_FILE,file"` // caarlos0/env

    // Или обычная переменная (K8s secretKeyRef)
    DBPasswordEnv string `env:"DB_PASSWORD"`
}
```

### Маскирование секретов в логах

```go
// Secret — тип для секретных значений, маскируется при логировании
type Secret string

// String — маскирует значение при выводе
func (s Secret) String() string {
    if len(s) == 0 {
        return ""
    }
    return "***"
}

// MarshalJSON — маскирует в JSON
func (s Secret) MarshalJSON() ([]byte, error) {
    return []byte(`"***"`), nil
}

// MarshalText — маскирует в текстовом формате (используется slog)
func (s Secret) MarshalText() ([]byte, error) {
    return []byte("***"), nil
}

// Value — получение реального значения (явный вызов)
func (s Secret) Value() string {
    return string(s)
}

// Использование в конфигурации
type DatabaseConfig struct {
    Host     string `env:"DB_HOST" envDefault:"localhost"`
    Port     int    `env:"DB_PORT" envDefault:"5432"`
    User     string `env:"DB_USER,required"`
    Password Secret `env:"DB_PASSWORD,required"` // маскируется при логировании
    Name     string `env:"DB_NAME" envDefault:"myapp"`
}

// Логирование — секреты замаскированы
func main() {
    cfg, _ := config.Load()

    slog.Info("конфигурация загружена",
        "db_host", cfg.Database.Host,
        "db_user", cfg.Database.User,
        "db_password", cfg.Database.Password, // выведет: ***
    )

    // Для реального использования — явный вызов .Value()
    dsn := fmt.Sprintf("postgres://%s:%s@%s:%d/%s",
        cfg.Database.User,
        cfg.Database.Password.Value(), // реальное значение
        cfg.Database.Host,
        cfg.Database.Port,
        cfg.Database.Name,
    )
}
```

> 💡 **Тип `Secret`** — простой, но эффективный приём. Он предотвращает случайное попадание паролей в логи, JSON-ответы и отладочный вывод. См. также раздел [4.5 Observability](./05_observability.md) — PII-маскирование в логах.

---

## Feature Flags

### Простая реализация через конфигурацию

Для базовых сценариев feature flags — это просто поля в конфиге:

```go
type FeatureFlags struct {
    EnableNewUI      bool `env:"FF_ENABLE_NEW_UI" envDefault:"false"`
    EnableV2API      bool `env:"FF_ENABLE_V2_API" envDefault:"false"`
    EnableAnalytics  bool `env:"FF_ENABLE_ANALYTICS" envDefault:"true"`
    MaxUploadSizeMB  int  `env:"FF_MAX_UPLOAD_SIZE_MB" envDefault:"10"`
}

type Config struct {
    Server   ServerConfig
    Database DatabaseConfig
    Features FeatureFlags
}

// Использование в handler
func (h *Handler) Upload(w http.ResponseWriter, r *http.Request) {
    maxSize := int64(h.cfg.Features.MaxUploadSizeMB) * 1024 * 1024
    r.Body = http.MaxBytesReader(w, r.Body, maxSize)

    if !h.cfg.Features.EnableV2API {
        h.uploadV1(w, r)
        return
    }
    h.uploadV2(w, r)
}

// Middleware для feature flags
func FeatureGate(flag bool) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            if !flag {
                http.Error(w, "feature not available", http.StatusNotFound)
                return
            }
            next.ServeHTTP(w, r)
        })
    }
}

// Использование
mux.Handle("/api/v2/", FeatureGate(cfg.Features.EnableV2API)(v2Handler))
```

**C# аналог**:
```csharp
// Microsoft.FeatureManagement
services.AddFeatureManagement(config.GetSection("FeatureFlags"));

// Использование
[FeatureGate("EnableV2API")]
public class V2Controller : ControllerBase { }

// Или в коде
if (await featureManager.IsEnabledAsync("EnableNewUI"))
    return View("NewUI");
```

### OpenFeature SDK

[OpenFeature](https://openfeature.dev/) — вендор-нейтральный стандарт для feature flags:

```bash
go get github.com/open-feature/go-sdk
```

```go
import (
    "context"

    "github.com/open-feature/go-sdk/openfeature"
)

func setupFeatureFlags() {
    // Провайдер — можно заменить на LaunchDarkly, Flagd и др.
    openfeature.SetProvider(myProvider)

    client := openfeature.NewClient("myapp")

    ctx := context.Background()

    // Оценка флага с контекстом пользователя
    value, err := client.BooleanValue(ctx, "enable-new-ui", false,
        openfeature.NewEvaluationContext("", map[string]interface{}{
            "user-id":    "user-123",
            "user-role":  "admin",
            "user-region": "eu",
        }),
    )
    if err != nil {
        log.Printf("ошибка оценки флага: %v", err)
    }

    if value {
        // Новый UI
    }
}
```

### Сторонние сервисы

Для сложных сценариев (A/B тестирование, постепенный rollout, таргетинг) — используйте специализированные сервисы:

| Сервис | Особенности | Go SDK |
|--------|------------|--------|
| **LaunchDarkly** | Лидер рынка, rich targeting | `github.com/launchdarkly/go-server-sdk` |
| **Unleash** | Open-source, self-hosted | `github.com/Unleash/unleash-client-go` |
| **Flagsmith** | Open-source, SaaS и self-hosted | `github.com/Flagsmith/flagsmith-go-client` |
| **flagd** | CNCF, OpenFeature-native | Через OpenFeature SDK |

> 💡 **Рекомендация**: Начните с config-based флагов. Переходите на OpenFeature / внешний сервис, когда появится потребность в A/B тестировании, постепенном rollout или таргетинге по пользователям.

---

## Production Concerns

### Порядок инициализации

В Go нет автоматической инициализации как в ASP.NET `WebApplicationBuilder`. Порядок важен:

```go
func main() {
    // 1. Загрузка конфигурации (ПЕРВЫМ!)
    cfg, err := config.Load()
    if err != nil {
        // На этом этапе логгер ещё не инициализирован — используем стандартный
        log.Fatalf("ошибка загрузки конфигурации: %v", err)
    }

    // 2. Валидация конфигурации
    if err := cfg.Validate(); err != nil {
        log.Fatalf("невалидная конфигурация: %v", err)
    }

    // 3. Инициализация логгера (зависит от cfg.Log)
    logger := setupLogger(cfg.Log)
    logger.Info("конфигурация загружена",
        "env", cfg.Env,
        "server_port", cfg.Server.Port,
    )

    // 4. Инициализация трейсинга (зависит от cfg и logger)
    shutdown, err := setupTracing(cfg.Telemetry)
    if err != nil {
        logger.Error("ошибка инициализации трейсинга", "error", err)
    }
    defer shutdown(context.Background())

    // 5. Подключение к базам данных (зависит от cfg)
    db, err := setupDatabase(cfg.Database)
    if err != nil {
        logger.Error("ошибка подключения к БД", "error", err)
        os.Exit(1)
    }
    defer db.Close()

    // 6. Создание сервисов
    repo := postgres.NewRepository(db)
    svc := service.NewService(repo, logger)
    handler := api.NewHandler(svc, logger)

    // 7. Запуск сервера
    srv := &http.Server{
        Addr:         cfg.Server.Address(),
        Handler:      handler.Routes(),
        ReadTimeout:  cfg.Server.ReadTimeout,
        WriteTimeout: cfg.Server.WriteTimeout,
    }

    // 8. Graceful shutdown
    go func() {
        sigCh := make(chan os.Signal, 1)
        signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
        <-sigCh

        logger.Info("получен сигнал завершения")
        ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
        defer cancel()
        srv.Shutdown(ctx)
    }()

    logger.Info("сервер запущен", "addr", cfg.Server.Address())
    if err := srv.ListenAndServe(); err != http.ErrServerClosed {
        logger.Error("ошибка сервера", "error", err)
        os.Exit(1)
    }
}
```

**C# аналог** — порядок автоматизирован:
```csharp
var builder = WebApplication.CreateBuilder(args);
// builder сам управляет порядком: config → logging → DI → middleware → endpoints
```

### Graceful reload

Перезагрузка конфигурации по сигналу SIGHUP:

```go
func setupConfigReload(cm *config.Manager, logger *slog.Logger) {
    sigCh := make(chan os.Signal, 1)
    signal.Notify(sigCh, syscall.SIGHUP)

    go func() {
        for range sigCh {
            logger.Info("SIGHUP получен, перезагрузка конфигурации...")

            newCfg, err := config.Load()
            if err != nil {
                logger.Error("ошибка перезагрузки конфигурации", "error", err)
                continue
            }

            if err := newCfg.Validate(); err != nil {
                logger.Error("невалидная новая конфигурация", "error", err)
                continue
            }

            cm.Update(newCfg)
            logger.Info("конфигурация обновлена")
        }
    }()
}
```

```bash
# Перезагрузка конфигурации без рестарта
kill -SIGHUP $(pidof myapp)
```

> ⚠️ **Что можно перезагружать**: уровень логирования, feature flags, rate limits. **Что нельзя**: порт сервера, строку подключения к БД (требует переподключения).

### Тестирование конфигурации

```go
package config_test

import (
    "testing"

    "myapp/config"
)

func TestLoad_Defaults(t *testing.T) {
    // t.Setenv устанавливает переменные только для этого теста
    // и автоматически восстанавливает исходные значения
    t.Setenv("DB_USER", "testuser")
    t.Setenv("DB_PASSWORD", "testpass123")

    cfg, err := config.Load()
    if err != nil {
        t.Fatalf("неожиданная ошибка: %v", err)
    }

    // Проверка defaults
    if cfg.Server.Port != 8080 {
        t.Errorf("ожидали порт 8080, получили %d", cfg.Server.Port)
    }
    if cfg.Server.Host != "0.0.0.0" {
        t.Errorf("ожидали host 0.0.0.0, получили %s", cfg.Server.Host)
    }
}

func TestLoad_RequiredFields(t *testing.T) {
    // Не задаём обязательные поля — ожидаем ошибку
    cfg, err := config.Load()
    if err == nil {
        t.Fatal("ожидали ошибку для отсутствующих обязательных полей")
    }
    if cfg != nil {
        t.Fatal("конфиг должен быть nil при ошибке")
    }
}

func TestValidate_WriteTimeoutGreaterThanRead(t *testing.T) {
    cfg := &config.Config{
        Server: config.ServerConfig{
            ReadTimeout:  10 * time.Second,
            WriteTimeout: 5 * time.Second, // меньше ReadTimeout — невалидно
        },
    }

    err := cfg.Validate()
    if err == nil {
        t.Fatal("ожидали ошибку валидации: WriteTimeout < ReadTimeout")
    }
}

func TestLoad_CustomValues(t *testing.T) {
    t.Setenv("DB_USER", "admin")
    t.Setenv("DB_PASSWORD", "supersecret")
    t.Setenv("SERVER_PORT", "9090")
    t.Setenv("LOG_LEVEL", "debug")

    cfg, err := config.Load()
    if err != nil {
        t.Fatalf("неожиданная ошибка: %v", err)
    }

    if cfg.Server.Port != 9090 {
        t.Errorf("ожидали порт 9090, получили %d", cfg.Server.Port)
    }
    if cfg.Log.Level != "debug" {
        t.Errorf("ожидали log level debug, получили %s", cfg.Log.Level)
    }
}
```

> 💡 **`t.Setenv` (Go 1.17+)** — устанавливает переменную окружения только для текущего теста и автоматически восстанавливает значение после завершения. Безопасен для параллельных тестов (вызывает `t.Parallel()` panic — по дизайну).

### Observability для конфигурации

Логируйте конфигурацию при старте и отслеживайте перезагрузки:

```go
// Логирование конфигурации при запуске (без секретов!)
func logConfig(logger *slog.Logger, cfg *Config) {
    logger.Info("конфигурация загружена",
        "env", cfg.Env,
        "server.host", cfg.Server.Host,
        "server.port", cfg.Server.Port,
        "server.read_timeout", cfg.Server.ReadTimeout,
        "database.host", cfg.Database.Host,
        "database.port", cfg.Database.Port,
        "database.name", cfg.Database.Name,
        "database.sslmode", cfg.Database.SSLMode,
        "database.max_conns", cfg.Database.MaxConns,
        "database.password", cfg.Database.Password, // тип Secret — выведет ***
        "redis.addr", cfg.Redis.Addr,
        "log.level", cfg.Log.Level,
        "features", cfg.Features,
    )
}

// Prometheus-метрики для конфигурации
var (
    configReloadTotal = prometheus.NewCounter(prometheus.CounterOpts{
        Name: "config_reload_total",
        Help: "Количество перезагрузок конфигурации",
    })
    configReloadErrors = prometheus.NewCounter(prometheus.CounterOpts{
        Name: "config_reload_errors_total",
        Help: "Количество ошибок при перезагрузке конфигурации",
    })
    configInfo = prometheus.NewGaugeVec(prometheus.GaugeOpts{
        Name: "config_info",
        Help: "Информация о текущей конфигурации",
    }, []string{"env", "log_level"})
)

func init() {
    prometheus.MustRegister(configReloadTotal, configReloadErrors, configInfo)
}

func updateConfigMetrics(cfg *Config) {
    configInfo.Reset()
    configInfo.WithLabelValues(cfg.Env, cfg.Log.Level).Set(1)
}

---

## Типичные ошибки C# разработчиков

### 1. Over-engineering: DI-based config providers

```go
// ❌ C# привычка — создание интерфейсов и DI для конфигурации
type ConfigProvider interface {
    GetConfig() *Config
}

type envConfigProvider struct{}

func (p *envConfigProvider) GetConfig() *Config {
    cfg, _ := config.Load()
    return cfg
}

// Инъекция через конструктор
func NewService(cp ConfigProvider) *Service {
    return &Service{config: cp.GetConfig()}
}

// ✅ Go-way — просто передайте структуру
func NewService(cfg ServiceConfig) *Service {
    return &Service{cfg: cfg}
}
```

### 2. Не валидируют конфигурацию при запуске

```go
// ❌ Ленивая валидация — узнаём о проблеме через час в production
func (r *Repository) Connect() error {
    if r.cfg.Host == "" {
        return errors.New("database host не задан") // поздно!
    }
    // ...
}

// ✅ Fail fast — валидация при старте
func main() {
    cfg, err := config.Load()
    if err != nil {
        log.Fatal(err) // ← сразу при запуске
    }
    if err := cfg.Validate(); err != nil {
        log.Fatal(err) // ← сразу при запуске
    }
}
```

### 3. Секреты в config-файлах и коде

```go
// ❌ Привычка от appsettings.json
const defaultPassword = "admin123" // никогда!

// ❌ Коммит .env с реальными паролями
// .env: DB_PASSWORD=production-secret-123

// ✅ Секреты через env или secret manager
type Config struct {
    Password Secret `env:"DB_PASSWORD,required"` // обязательная, без default
}
```

### 4. Глобальный mutable state

```go
// ❌ Глобальный Viper — скрытая зависимость
func GetDatabaseHost() string {
    return viper.GetString("database.host") // кто инициализировал? когда?
}

// ✅ Явная передача конфигурации
type Repository struct {
    cfg DatabaseConfig
}

func NewRepository(cfg DatabaseConfig) *Repository {
    return &Repository{cfg: cfg}
}
```

### 5. Игнорирование 12-Factor

```go
// ❌ Зависимость от config-файла в production
func Load() (*Config, error) {
    return LoadFromFile("/etc/myapp/config.yaml") // а если файла нет?
}

// ✅ ENV-first, файл — опционально
func Load() (*Config, error) {
    _ = godotenv.Load() // опционально для dev
    cfg := &Config{}
    return cfg, env.Parse(cfg)
}
```

### 6. Перечитывание конфига на каждый запрос

```go
// ❌ Парсинг конфигурации на каждый HTTP-запрос
func (h *Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    cfg, _ := config.Load() // парсинг env на КАЖДЫЙ запрос!
    // ...
}

// ✅ Загрузка один раз, передача через замыкание/поле
func NewHandler(cfg *Config) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // cfg уже загружен
    })
}
```

### 7. Смешение конфигурации и бизнес-логики

```go
// ❌ Бизнес-логика читает env напрямую
func CalculateDiscount(price float64) float64 {
    maxDiscount, _ := strconv.ParseFloat(os.Getenv("MAX_DISCOUNT"), 64)
    return price * maxDiscount
}

// ✅ Бизнес-логика принимает параметры
func CalculateDiscount(price, maxDiscount float64) float64 {
    return price * maxDiscount
}

// Конфигурация — на уровне инициализации
svc := NewPricingService(cfg.Pricing.MaxDiscount)
```

---

## Практические примеры

### Пример 1: Production-ready config с caarlos0/env

Полный пакет конфигурации для production-микросервиса:

```go
// internal/config/config.go
package config

import (
    "errors"
    "fmt"
    "strings"
    "time"

    "github.com/caarlos0/env/v11"
    "github.com/go-playground/validator/v10"
    "github.com/joho/godotenv"
)

// Secret — тип для секретных значений
type Secret string

func (s Secret) String() string {
    if len(s) == 0 {
        return ""
    }
    return "***"
}

func (s Secret) MarshalText() ([]byte, error) { return []byte("***"), nil }
func (s Secret) Value() string                 { return string(s) }

// Config — корневая структура конфигурации
type Config struct {
    Env    string `env:"APP_ENV" envDefault:"development" validate:"required,oneof=development staging production"`
    Server ServerConfig
    DB     DatabaseConfig
    Redis  RedisConfig
    Log    LogConfig
}

type ServerConfig struct {
    Host         string        `env:"SERVER_HOST" envDefault:"0.0.0.0" validate:"required"`
    Port         int           `env:"SERVER_PORT" envDefault:"8080" validate:"required,min=1,max=65535"`
    ReadTimeout  time.Duration `env:"SERVER_READ_TIMEOUT" envDefault:"5s" validate:"required"`
    WriteTimeout time.Duration `env:"SERVER_WRITE_TIMEOUT" envDefault:"10s" validate:"required"`
    IdleTimeout  time.Duration `env:"SERVER_IDLE_TIMEOUT" envDefault:"120s"`
}

func (s ServerConfig) Address() string {
    return fmt.Sprintf("%s:%d", s.Host, s.Port)
}

type DatabaseConfig struct {
    Host            string        `env:"DB_HOST" envDefault:"localhost" validate:"required"`
    Port            int           `env:"DB_PORT" envDefault:"5432" validate:"required,min=1,max=65535"`
    User            string        `env:"DB_USER,required" validate:"required"`
    Password        Secret        `env:"DB_PASSWORD,required" validate:"required"`
    Name            string        `env:"DB_NAME" envDefault:"myapp" validate:"required"`
    SSLMode         string        `env:"DB_SSLMODE" envDefault:"disable" validate:"required,oneof=disable allow prefer require verify-ca verify-full"`
    MaxOpenConns    int           `env:"DB_MAX_OPEN_CONNS" envDefault:"25" validate:"min=1,max=1000"`
    MaxIdleConns    int           `env:"DB_MAX_IDLE_CONNS" envDefault:"5" validate:"min=0"`
    ConnMaxLifetime time.Duration `env:"DB_CONN_MAX_LIFETIME" envDefault:"5m"`
}

func (d DatabaseConfig) DSN() string {
    return fmt.Sprintf("postgres://%s:%s@%s:%d/%s?sslmode=%s",
        d.User, d.Password.Value(), d.Host, d.Port, d.Name, d.SSLMode)
}

type RedisConfig struct {
    Addr     string `env:"REDIS_ADDR" envDefault:"localhost:6379" validate:"required"`
    Password Secret `env:"REDIS_PASSWORD"`
    DB       int    `env:"REDIS_DB" envDefault:"0" validate:"min=0,max=15"`
}

type LogConfig struct {
    Level  string `env:"LOG_LEVEL" envDefault:"info" validate:"required,oneof=debug info warn error"`
    Format string `env:"LOG_FORMAT" envDefault:"json" validate:"required,oneof=json text"`
}

var validate = validator.New()

// Load загружает и валидирует конфигурацию
func Load() (*Config, error) {
    // В development загружаем .env
    _ = godotenv.Load()

    cfg := &Config{}

    // Парсинг env-переменных
    if err := env.Parse(cfg); err != nil {
        return nil, fmt.Errorf("парсинг env: %w", err)
    }

    // Структурная валидация
    if err := validate.Struct(cfg); err != nil {
        return nil, fmt.Errorf("валидация: %w", err)
    }

    // Бизнес-валидация
    if err := cfg.validate(); err != nil {
        return nil, fmt.Errorf("бизнес-валидация: %w", err)
    }

    return cfg, nil
}

func (c *Config) validate() error {
    var errs []error

    if c.Server.WriteTimeout <= c.Server.ReadTimeout {
        errs = append(errs, fmt.Errorf(
            "write_timeout (%v) должен быть > read_timeout (%v)",
            c.Server.WriteTimeout, c.Server.ReadTimeout))
    }

    if c.DB.MaxIdleConns > c.DB.MaxOpenConns {
        errs = append(errs, fmt.Errorf(
            "max_idle_conns (%d) не может быть > max_open_conns (%d)",
            c.DB.MaxIdleConns, c.DB.MaxOpenConns))
    }

    if c.Env == "production" && c.DB.SSLMode == "disable" {
        errs = append(errs, fmt.Errorf("SSL обязателен в production"))
    }

    return errors.Join(errs...)
}
```

```go
// cmd/server/main.go
package main

import (
    "log"
    "log/slog"
    "os"

    "myapp/internal/config"
)

func main() {
    cfg, err := config.Load()
    if err != nil {
        log.Fatalf("FATAL: конфигурация: %v", err)
    }

    logger := setupLogger(cfg.Log)
    logger.Info("приложение запущено",
        "env", cfg.Env,
        "server", cfg.Server.Address(),
        "db_host", cfg.DB.Host,
        "db_password", cfg.DB.Password, // выведет ***
    )

    // ... инициализация и запуск
}

func setupLogger(cfg config.LogConfig) *slog.Logger {
    var level slog.Level
    switch cfg.Level {
    case "debug":
        level = slog.LevelDebug
    case "warn":
        level = slog.LevelWarn
    case "error":
        level = slog.LevelError
    default:
        level = slog.LevelInfo
    }

    opts := &slog.HandlerOptions{Level: level}

    var handler slog.Handler
    if cfg.Format == "text" {
        handler = slog.NewTextHandler(os.Stdout, opts)
    } else {
        handler = slog.NewJSONHandler(os.Stdout, opts)
    }

    return slog.New(handler)
}
```

### Пример 2: Multi-source config с koanf и hot reload

```go
// internal/config/manager.go
package config

import (
    "fmt"
    "log/slog"
    "strings"
    "sync/atomic"
    "time"

    "github.com/knadh/koanf/v2"
    "github.com/knadh/koanf/parsers/yaml"
    "github.com/knadh/koanf/providers/env"
    "github.com/knadh/koanf/providers/file"
)

type Config struct {
    Server struct {
        Host         string        `koanf:"host"`
        Port         int           `koanf:"port"`
        ReadTimeout  time.Duration `koanf:"read_timeout"`
        WriteTimeout time.Duration `koanf:"write_timeout"`
    } `koanf:"server"`

    Database struct {
        Host     string `koanf:"host"`
        Port     int    `koanf:"port"`
        User     string `koanf:"user"`
        Password string `koanf:"password"`
        Name     string `koanf:"name"`
    } `koanf:"database"`

    Log struct {
        Level string `koanf:"level"`
    } `koanf:"log"`

    Features struct {
        EnableNewUI bool `koanf:"enable_new_ui"`
        EnableV2API bool `koanf:"enable_v2_api"`
    } `koanf:"features"`
}

// Manager управляет конфигурацией с поддержкой hot reload
type Manager struct {
    config    atomic.Pointer[Config]
    logger    *slog.Logger
    configPath string
    reloadCount atomic.Int64
}

func NewManager(configPath string, logger *slog.Logger) (*Manager, error) {
    m := &Manager{
        logger:     logger,
        configPath: configPath,
    }

    // Первоначальная загрузка
    cfg, err := m.load()
    if err != nil {
        return nil, fmt.Errorf("первоначальная загрузка: %w", err)
    }
    m.config.Store(cfg)

    // Запуск наблюдения за файлом
    m.watchConfig()

    return m, nil
}

func (m *Manager) load() (*Config, error) {
    k := koanf.New(".")

    // 1. Файл (низший приоритет)
    if err := k.Load(file.Provider(m.configPath), yaml.Parser()); err != nil {
        m.logger.Warn("конфиг-файл не найден", "path", m.configPath, "error", err)
    }

    // 2. ENV (высший приоритет) — перезаписывает файл
    err := k.Load(env.Provider("APP_", ".", func(s string) string {
        return strings.Replace(
            strings.ToLower(strings.TrimPrefix(s, "APP_")),
            "_", ".", -1)
    }), nil)
    if err != nil {
        return nil, fmt.Errorf("загрузка env: %w", err)
    }

    var cfg Config
    if err := k.Unmarshal("", &cfg); err != nil {
        return nil, fmt.Errorf("десериализация: %w", err)
    }

    return &cfg, nil
}

func (m *Manager) watchConfig() {
    f := file.Provider(m.configPath)

    f.Watch(func(event interface{}, err error) {
        if err != nil {
            m.logger.Error("ошибка watch", "error", err)
            return
        }

        m.logger.Info("обнаружено изменение конфиг-файла")

        cfg, err := m.load()
        if err != nil {
            m.logger.Error("ошибка перезагрузки", "error", err)
            return
        }

        m.config.Store(cfg)
        m.reloadCount.Add(1)

        m.logger.Info("конфигурация обновлена",
            "reload_count", m.reloadCount.Load(),
            "log_level", cfg.Log.Level,
        )
    })
}

// Get возвращает текущую конфигурацию (thread-safe)
func (m *Manager) Get() *Config {
    return m.config.Load()
}

// ReloadCount возвращает количество перезагрузок
func (m *Manager) ReloadCount() int64 {
    return m.reloadCount.Load()
}
```

```go
// Использование в main.go
func main() {
    logger := slog.Default()

    mgr, err := config.NewManager("config.yaml", logger)
    if err != nil {
        log.Fatal(err)
    }

    // HTTP handler с hot-reloadable конфигом
    http.HandleFunc("/api/features", func(w http.ResponseWriter, r *http.Request) {
        cfg := mgr.Get() // всегда актуальная конфигурация
        json.NewEncoder(w).Encode(cfg.Features)
    })

    cfg := mgr.Get()
    addr := fmt.Sprintf("%s:%d", cfg.Server.Host, cfg.Server.Port)
    log.Fatal(http.ListenAndServe(addr, nil))
}
```

### Пример 3: Config с секретами и feature flags

```go
// internal/config/loader.go
package config

import (
    "context"
    "fmt"
    "log/slog"
    "os"
    "time"

    "github.com/caarlos0/env/v11"
    vault "github.com/hashicorp/vault/api"
    "github.com/joho/godotenv"
)

type Config struct {
    Env      string `env:"APP_ENV" envDefault:"development"`
    Server   ServerConfig
    DB       DatabaseConfig
    Redis    RedisConfig
    Log      LogConfig
    Features FeatureFlags
    Vault    VaultConfig
}

type VaultConfig struct {
    Addr  string `env:"VAULT_ADDR"`
    Token Secret `env:"VAULT_TOKEN"`
    Path  string `env:"VAULT_SECRET_PATH" envDefault:"secret/data/myapp"`
}

type FeatureFlags struct {
    EnableNewUI     bool `env:"FF_ENABLE_NEW_UI" envDefault:"false"`
    EnableV2API     bool `env:"FF_ENABLE_V2_API" envDefault:"false"`
    EnableAnalytics bool `env:"FF_ENABLE_ANALYTICS" envDefault:"true"`
}

// Load загружает конфигурацию из env и Vault
func Load(ctx context.Context, logger *slog.Logger) (*Config, error) {
    // 1. Загрузка .env в development
    _ = godotenv.Load()

    // 2. Парсинг env-переменных
    cfg := &Config{}
    if err := env.Parse(cfg); err != nil {
        return nil, fmt.Errorf("парсинг env: %w", err)
    }

    // 3. Загрузка секретов из Vault (если настроен)
    if cfg.Vault.Addr != "" {
        if err := loadVaultSecrets(ctx, cfg, logger); err != nil {
            // В development — предупреждение, в production — ошибка
            if cfg.Env == "production" {
                return nil, fmt.Errorf("загрузка секретов: %w", err)
            }
            logger.Warn("Vault недоступен, используем env-переменные", "error", err)
        }
    }

    // 4. Валидация
    if err := cfg.Validate(); err != nil {
        return nil, fmt.Errorf("валидация: %w", err)
    }

    return cfg, nil
}

func loadVaultSecrets(ctx context.Context, cfg *Config, logger *slog.Logger) error {
    vaultCfg := vault.DefaultConfig()
    vaultCfg.Address = cfg.Vault.Addr

    client, err := vault.NewClient(vaultCfg)
    if err != nil {
        return fmt.Errorf("создание vault клиента: %w", err)
    }

    client.SetToken(cfg.Vault.Token.Value())

    // Чтение секретов
    secret, err := client.KVv2("secret").Get(ctx, "myapp")
    if err != nil {
        return fmt.Errorf("чтение секретов: %w", err)
    }

    // Перезаписываем секреты из Vault
    if dbPass, ok := secret.Data["db_password"].(string); ok {
        cfg.DB.Password = Secret(dbPass)
        logger.Debug("секрет db_password загружен из Vault")
    }

    if redisPass, ok := secret.Data["redis_password"].(string); ok {
        cfg.Redis.Password = Secret(redisPass)
        logger.Debug("секрет redis_password загружен из Vault")
    }

    logger.Info("секреты загружены из Vault")
    return nil
}

func (c *Config) Validate() error {
    // ... валидация как в Примере 1
    return nil
}
```

```go
// cmd/server/main.go
package main

import (
    "context"
    "log"
    "log/slog"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "myapp/internal/config"
)

func main() {
    ctx := context.Background()

    // Базовый логгер для инициализации
    initLogger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

    // 1. Загрузка конфигурации (с секретами из Vault)
    cfg, err := config.Load(ctx, initLogger)
    if err != nil {
        log.Fatalf("FATAL: %v", err)
    }

    // 2. Production логгер (с уровнем из конфигурации)
    logger := setupLogger(cfg.Log)
    logger.Info("приложение запускается",
        "env", cfg.Env,
        "features.new_ui", cfg.Features.EnableNewUI,
        "features.v2_api", cfg.Features.EnableV2API,
    )

    // 3. Инициализация инфраструктуры
    // db := setupDB(cfg.DB)
    // cache := setupRedis(cfg.Redis)
    // handler := setupHandler(db, cache, cfg, logger)

    // 4. HTTP-сервер
    srv := &http.Server{
        Addr:         cfg.Server.Address(),
        // Handler:   handler,
        ReadTimeout:  cfg.Server.ReadTimeout,
        WriteTimeout: cfg.Server.WriteTimeout,
    }

    // 5. Graceful shutdown
    done := make(chan struct{})
    go func() {
        sigCh := make(chan os.Signal, 1)
        signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
        sig := <-sigCh

        logger.Info("получен сигнал завершения", "signal", sig)

        shutdownCtx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
        defer cancel()

        if err := srv.Shutdown(shutdownCtx); err != nil {
            logger.Error("ошибка graceful shutdown", "error", err)
        }
        close(done)
    }()

    logger.Info("сервер запущен", "addr", cfg.Server.Address())
    if err := srv.ListenAndServe(); err != http.ErrServerClosed {
        logger.Error("ошибка сервера", "error", err)
        os.Exit(1)
    }

    <-done
    logger.Info("приложение завершено")
}
```

---

**Вопросы?** Откройте issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Назад: 4.5 Observability](./05_observability.md) | [Вперёд: 4.7 Контейнеризация →](./07_containerization.md)

