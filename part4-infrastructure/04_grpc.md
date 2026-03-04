# gRPC

---

## Введение

В [разделе 3.4](../part3-web-api/04_validation_serialization.md) мы рассмотрели Protocol Buffers как формат сериализации — синтаксис `.proto` файлов, кодогенерацию через `protoc` и сравнение с JSON. Теперь мы используем protobuf как основу для **gRPC** — высокопроизводительного RPC-фреймворка, который стал стандартом межсервисного взаимодействия в микросервисных архитектурах.

gRPC передаёт данные в бинарном формате Protocol Buffers поверх HTTP/2, обеспечивая мультиплексирование, двунаправленный стриминг и сжатие заголовков. В отличие от REST API с JSON, gRPC предлагает строгую типизацию контрактов, автоматическую кодогенерацию клиентов и серверов, и значительно меньший размер сообщений.

> 💡 **Для C# разработчиков**: В .NET gRPC глубоко интегрирован в ASP.NET Core — вы добавляете `Grpc.AspNetCore`, описываете `.proto`, и `Grpc.Tools` автоматически генерирует код при сборке через MSBuild. Сервис регистрируется через `services.AddGrpc()`, DI работает из коробки, interceptors наследуют базовый класс `Interceptor`. В Go gRPC — **отдельная библиотека**, не привязанная к веб-фреймворку. Вы явно генерируете код через `protoc` (или `buf`), вручную создаёте сервер, регистрируете сервисы и управляете жизненным циклом. Это больше кода, но полный контроль и отсутствие скрытых абстракций.

### Что изменится в вашем подходе

**C# (ASP.NET Core gRPC)**:
```csharp
// Минимальная настройка — всё через DI и конвенции
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddGrpc();

var app = builder.Build();
app.MapGrpcService<UserService>(); // DI, interceptors, health — из коробки
app.Run();

// Сервис — обычный класс с DI
public class UserService : Users.UsersBase
{
    private readonly IUserRepository _repo;

    public UserService(IUserRepository repo) => _repo = repo;

    public override async Task<GetUserResponse> GetUser(
        GetUserRequest request, ServerCallContext context)
    {
        var user = await _repo.GetByIdAsync(request.Id);
        return new GetUserResponse { User = MapToProto(user) };
    }
}
```

**Go — явная реализация**:
```go
// Явное создание сервера, регистрация, управление lifecycle
func main() {
    lis, err := net.Listen("tcp", ":50051")
    if err != nil {
        log.Fatalf("не удалось слушать порт: %v", err)
    }

    // Зависимости передаются явно — никакого DI-контейнера
    repo := postgres.NewUserRepository(db)
    srv := grpc.NewServer()
    pb.RegisterUserServiceServer(srv, &userServer{repo: repo})

    log.Println("gRPC сервер запущен на :50051")
    if err := srv.Serve(lis); err != nil {
        log.Fatalf("ошибка сервера: %v", err)
    }
}

type userServer struct {
    pb.UnimplementedUserServiceServer
    repo UserRepository
}

func (s *userServer) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.GetUserResponse, error) {
    user, err := s.repo.GetByID(ctx, req.GetId())
    if err != nil {
        return nil, status.Errorf(codes.NotFound, "пользователь не найден: %v", err)
    }
    return &pb.GetUserResponse{User: toProtoUser(user)}, nil
}
```

---

## Экосистема: C# vs Go

| Аспект | C# (.NET) | Go |
|--------|-----------|-----|
| **Фреймворк** | `Grpc.AspNetCore` (часть ASP.NET Core) | `google.golang.org/grpc` (отдельная библиотека) |
| **Кодогенерация** | `Grpc.Tools` NuGet (MSBuild, автоматически при сборке) | `protoc` + плагины / `buf` (отдельный шаг) |
| **Регистрация сервиса** | `services.AddGrpc()` + `app.MapGrpcService<T>()` | `pb.RegisterXxxServer(s, &impl{})` |
| **DI в обработчиках** | Constructor injection из DI-контейнера | Передача зависимостей в структуру вручную |
| **Streaming** | `IAsyncStreamReader<T>` / `IServerStreamWriter<T>` | `stream.Recv()` / `stream.Send()` |
| **Interceptors** | Наследование `Interceptor` (virtual методы) | Функции с определённой сигнатурой |
| **Канал/подключение** | `GrpcChannel.ForAddress()` | `grpc.NewClient()` |
| **Дедлайны** | `CallOptions.Deadline` / `CancellationToken` | `context.WithTimeout()` / `context.WithDeadline()` |
| **Ошибки** | `RpcException` + `StatusCode` enum | `status.Error(codes.X, msg)` |
| **Health checks** | `Grpc.AspNetCore.HealthChecks` | `grpc/health/grpc_health_v1` |
| **REST прокси** | gRPC-Web middleware (`Grpc.AspNetCore.Web`) | gRPC-Gateway (reverse proxy) / ConnectRPC |
| **Тестирование** | `WebApplicationFactory` / `TestServer` | `bufconn` (in-memory listener) |
| **Линтинг proto** | Нет стандартного инструмента | `buf lint` |
| **Breaking changes** | Ручная проверка / SemVer | `buf breaking` |
| **Мониторинг** | Встроенные метрики .NET 8+ | go-grpc-middleware prometheus |
| **Трейсинг** | `Activity` / OTel .NET SDK | `otelgrpc` package |

> 💡 **Ключевое различие**: В C# gRPC — это часть платформы ASP.NET Core, и всё работает через привычные механизмы (DI, middleware pipeline, конфигурация). В Go gRPC — независимая библиотека, и вы собираете всё вручную. Это требует больше кода, но даёт явность и контроль — философия Go.

---

## Protocol Buffers для gRPC

> Базовый синтаксис Protocol Buffers рассмотрен в [разделе 3.4](../part3-web-api/04_validation_serialization.md). Здесь мы сфокусируемся на аспектах, специфичных для gRPC: проектирование API, сервисные определения и best practices.

### API Design: best practices для .proto

#### Naming conventions

```protobuf
syntax = "proto3";

// Пакет — всегда с версией для обратной совместимости
package myapp.user.v1;

// Go-специфичная опция (buf managed mode может генерировать автоматически)
option go_package = "github.com/myapp/gen/user/v1;userv1";

// Сервис: PascalCase, существительное + "Service"
service UserService {
    // Метод: PascalCase, глагол
    rpc GetUser(GetUserRequest) returns (GetUserResponse);
    rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
    rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
    rpc UpdateUser(UpdateUserRequest) returns (UpdateUserResponse);
    rpc DeleteUser(DeleteUserRequest) returns (DeleteUserResponse);
}

// Сообщения запросов/ответов: ИмяМетода + Request/Response
message GetUserRequest {
    // Поля: snake_case
    string user_id = 1;
}

message GetUserResponse {
    User user = 1;
}

// Ресурсные сообщения: существительное
message User {
    string id = 1;
    string email = 2;
    string display_name = 3;
    UserRole role = 4;
    google.protobuf.Timestamp created_at = 5;
    google.protobuf.Timestamp updated_at = 6;
}

// Enum: PascalCase, значения — UPPER_SNAKE_CASE с префиксом
enum UserRole {
    USER_ROLE_UNSPECIFIED = 0; // Нулевое значение всегда UNSPECIFIED
    USER_ROLE_ADMIN = 1;
    USER_ROLE_MEMBER = 2;
    USER_ROLE_VIEWER = 3;
}
```

> ⚠️ **Важно**: Нулевое значение enum **всегда** должно быть `UNSPECIFIED`. Это гарантирует, что отсутствие значения не будет интерпретировано как осмысленное. В C# enum по умолчанию тоже `0`, но в .NET принято давать ему осмысленное значение (например, `None`). В protobuf конвенция — именно `UNSPECIFIED`.

#### Версионирование API

```
proto/
├── myapp/
│   ├── user/
│   │   ├── v1/              # Стабильная версия
│   │   │   └── user.proto
│   │   └── v2/              # Новая версия с breaking changes
│   │       └── user.proto
│   └── order/
│       └── v1/
│           └── order.proto
```

> 💡 **Для C# разработчиков**: В .NET вы версионируете API через URL (`/api/v1/users`) или через заголовки (`api-version: 2.0`). В gRPC версия — часть **пакета protobuf** (`myapp.user.v1`). Это строже: разные версии — это разные сгенерированные типы, и компилятор гарантирует совместимость.

#### Паттерны пагинации и фильтрации

```protobuf
message ListUsersRequest {
    int32 page_size = 1;          // Сколько записей вернуть
    string page_token = 2;        // Токен следующей страницы (cursor)
    string filter = 3;            // Опциональный фильтр
    string order_by = 4;          // Сортировка: "created_at desc"
}

message ListUsersResponse {
    repeated User users = 1;
    string next_page_token = 2;   // Пустая строка = последняя страница
    int32 total_count = 3;        // Опционально: общее количество
}
```

### Well-Known Types

Google предоставляет набор стандартных типов, которые следует использовать вместо собственных:

```protobuf
import "google/protobuf/timestamp.proto";  // Время
import "google/protobuf/duration.proto";   // Длительность
import "google/protobuf/empty.proto";      // Пустое сообщение
import "google/protobuf/wrappers.proto";   // Nullable примитивы
import "google/protobuf/field_mask.proto"; // Частичное обновление
import "google/protobuf/struct.proto";     // Произвольный JSON
import "google/protobuf/any.proto";        // Любой protobuf-тип

message UpdateUserRequest {
    string user_id = 1;
    User user = 2;
    // FieldMask — указывает, какие поля обновлять (аналог PATCH)
    google.protobuf.FieldMask update_mask = 3;
}

message UserProfile {
    string name = 1;
    // Nullable int — отличие от обычного int32 (0 = не задано vs 0 = значение)
    google.protobuf.Int32Value age = 2;
    // Nullable string
    google.protobuf.StringValue bio = 3;
    // Произвольные метаданные
    google.protobuf.Struct metadata = 4;
}
```

**Сравнение Well-Known Types: C# vs Go**:

| Protobuf тип | C# маппинг | Go маппинг |
|--------------|------------|------------|
| `Timestamp` | `Google.Protobuf.WellKnownTypes.Timestamp` → `DateTime` через `.ToDateTime()` | `*timestamppb.Timestamp` → `time.Time` через `.AsTime()` |
| `Duration` | `Google.Protobuf.WellKnownTypes.Duration` → `TimeSpan` через `.ToTimeSpan()` | `*durationpb.Duration` → `time.Duration` через `.AsDuration()` |
| `Empty` | `Google.Protobuf.WellKnownTypes.Empty` | `*emptypb.Empty` |
| `FieldMask` | `Google.Protobuf.WellKnownTypes.FieldMask` | `*fieldmaskpb.FieldMask` |
| `StringValue` | `Google.Protobuf.WellKnownTypes.StringValue` → `string?` (nullable) | `*wrapperspb.StringValue` |

### Сервисные определения

Определим сервис, который будем использовать в примерах на протяжении всего раздела:

```protobuf
syntax = "proto3";

package myapp.user.v1;

option go_package = "github.com/myapp/gen/user/v1;userv1";

import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";
import "google/protobuf/field_mask.proto";

// UserService — CRUD операции и стриминг
service UserService {
    // Unary RPC — стандартный запрос-ответ
    rpc GetUser(GetUserRequest) returns (GetUserResponse);
    rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
    rpc UpdateUser(UpdateUserRequest) returns (UpdateUserResponse);
    rpc DeleteUser(DeleteUserRequest) returns (google.protobuf.Empty);
    rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);

    // Server Streaming — сервер отправляет поток данных
    rpc WatchUsers(WatchUsersRequest) returns (stream UserEvent);

    // Client Streaming — клиент отправляет поток, сервер — один ответ
    rpc ImportUsers(stream ImportUserRequest) returns (ImportUsersResponse);

    // Bidirectional Streaming — оба направления
    rpc Chat(stream ChatMessage) returns (stream ChatMessage);
}

message User {
    string id = 1;
    string email = 2;
    string display_name = 3;
    UserRole role = 4;
    google.protobuf.Timestamp created_at = 5;
    google.protobuf.Timestamp updated_at = 6;
}

enum UserRole {
    USER_ROLE_UNSPECIFIED = 0;
    USER_ROLE_ADMIN = 1;
    USER_ROLE_MEMBER = 2;
    USER_ROLE_VIEWER = 3;
}

message GetUserRequest {
    string user_id = 1;
}

message GetUserResponse {
    User user = 1;
}

message CreateUserRequest {
    string email = 1;
    string display_name = 2;
    UserRole role = 3;
}

message CreateUserResponse {
    User user = 1;
}

message UpdateUserRequest {
    string user_id = 1;
    User user = 2;
    google.protobuf.FieldMask update_mask = 3;
}

message UpdateUserResponse {
    User user = 1;
}

message ListUsersRequest {
    int32 page_size = 1;
    string page_token = 2;
}

message ListUsersResponse {
    repeated User users = 1;
    string next_page_token = 2;
}

// Server Streaming: события изменения пользователей
message WatchUsersRequest {
    // Фильтр по ролям (пустой = все)
    repeated UserRole roles = 1;
}

message UserEvent {
    enum EventType {
        EVENT_TYPE_UNSPECIFIED = 0;
        EVENT_TYPE_CREATED = 1;
        EVENT_TYPE_UPDATED = 2;
        EVENT_TYPE_DELETED = 3;
    }
    EventType type = 1;
    User user = 2;
    google.protobuf.Timestamp timestamp = 3;
}

// Client Streaming: импорт пользователей пакетом
message ImportUserRequest {
    string email = 1;
    string display_name = 2;
    UserRole role = 3;
}

message ImportUsersResponse {
    int32 imported_count = 1;
    int32 failed_count = 2;
    repeated string errors = 3;
}

// Bidirectional Streaming: чат
message ChatMessage {
    string user_id = 1;
    string text = 2;
    google.protobuf.Timestamp sent_at = 3;
}
```

> 💡 **Обратите внимание**: Каждый RPC использует **отдельные типы** Request/Response, даже если они кажутся похожими. Это позволяет развивать API без breaking changes — каждый метод эволюционирует независимо. В C# это аналогично паттерну CQRS с отдельными command/query объектами.

---

## buf: современный Protobuf tooling

### Проблемы protoc

Традиционный `protoc` — мощный инструмент, но у него ряд проблем, знакомых C# разработчикам, которые привыкли к удобству NuGet:

```bash
# Типичная команда protoc — сложно запомнить и поддерживать
protoc \
  --go_out=. --go_opt=paths=source_relative \
  --go-grpc_out=. --go-grpc_opt=paths=source_relative \
  -I proto \
  -I third_party/googleapis \
  -I third_party/grpc-gateway \
  proto/myapp/user/v1/user.proto
```

**Проблемы**:
- Ручное управление зависимостями (нужно скачивать `googleapis`, `grpc-gateway` proto-файлы)
- Длинные команды с множеством флагов
- Нет линтинга — ошибки проектирования API обнаруживаются поздно
- Нет обнаружения breaking changes — можно случайно сломать клиентов
- Каждый разработчик должен установить `protoc` и плагины нужных версий

> 💡 **Для C# разработчиков**: В .NET всё это скрыто — `Grpc.Tools` NuGet пакет включает `protoc` и плагины, MSBuild автоматически запускает генерацию при сборке, а зависимости управляются через NuGet. `buf` приближает Go-экосистему к этому уровню удобства.

### Установка и настройка buf

```bash
# Установка buf
go install github.com/bufbuild/buf/cmd/buf@latest

# Или через Homebrew (macOS/Linux)
brew install bufbuild/buf/buf

# Проверка
buf --version
```

#### buf.yaml — конфигурация модуля

```yaml
# buf.yaml — в корне вашего proto-проекта
version: v2
modules:
  - path: proto
    name: buf.build/mycompany/myapp
lint:
  use:
    - STANDARD           # Стандартный набор правил
  except:
    - PACKAGE_VERSION_SUFFIX  # Не требовать v1 суффикс (опционально)
breaking:
  use:
    - FILE                # Проверка breaking changes на уровне файлов
deps:
  - buf.build/googleapis/googleapis      # Google API annotations
  - buf.build/grpc-ecosystem/grpc-gateway # gRPC-Gateway
```

#### buf.gen.yaml — конфигурация кодогенерации

```yaml
# buf.gen.yaml
version: v2
plugins:
  # Go protobuf код
  - remote: buf.build/protocolbuffers/go
    out: gen
    opt:
      - paths=source_relative
  # Go gRPC код
  - remote: buf.build/grpc/go
    out: gen
    opt:
      - paths=source_relative
      - require_unimplemented_servers=true
  # gRPC-Gateway (REST прокси)
  - remote: buf.build/grpc-ecosystem/gateway
    out: gen
    opt:
      - paths=source_relative
  # OpenAPI/Swagger документация
  - remote: buf.build/grpc-ecosystem/openapiv2
    out: gen/openapiv2
managed:
  enabled: true
  override:
    - file_option: go_package_prefix
      value: github.com/mycompany/myapp/gen
```

> 💡 **managed mode** автоматически устанавливает `go_package` для всех proto-файлов на основе пути. Больше не нужно вручную прописывать `option go_package` в каждом файле — buf вычислит его из структуры директорий.

### buf lint — линтинг proto файлов

```bash
# Запуск линтера
buf lint

# Пример ошибок:
# proto/myapp/user/v1/user.proto:15:1:
#   Enum value name "ADMIN" should be prefixed with "USER_ROLE_".
# proto/myapp/user/v1/user.proto:8:3:
#   RPC request type "UserRequest" should be named "GetUserRequest".
```

**Категории правил buf lint**:

| Категория | Правило | Пример нарушения |
|-----------|---------|------------------|
| **NAMING** | Naming conventions | `getUserRequest` вместо `GetUserRequest` |
| **PACKAGE** | Package structure | Отсутствие version suffix в пакете |
| **ENUM** | Enum best practices | Нет `UNSPECIFIED` нулевого значения |
| **SERVICE** | Service design | Request/Response не по конвенции |
| **FIELD** | Field naming | `UserName` вместо `user_name` |
| **COMMENT** | Documentation | Отсутствие комментариев к сервисам |

**Сравнение с C#**: `buf lint` — это аналог **Roslyn analyzers** или `.editorconfig` для proto-файлов. Как StyleCop проверяет C# код на соответствие конвенциям, так `buf lint` проверяет proto-файлы.

### buf breaking — обнаружение несовместимых изменений

```bash
# Проверка против предыдущего коммита в git
buf breaking --against '.git#branch=main'

# Проверка против определённого тега
buf breaking --against '.git#tag=v1.0.0'

# Проверка против BSR (Buf Schema Registry)
buf breaking --against 'buf.build/mycompany/myapp'
```

**Что обнаруживает**:

```bash
# Примеры breaking changes:
# ❌ Удаление поля
#   proto/user.proto:10: Previously present field "3" with name
#   "display_name" on message "User" was deleted.
#
# ❌ Изменение типа поля
#   proto/user.proto:8: Field "2" on message "User" changed type
#   from "string" to "int32".
#
# ❌ Удаление RPC метода
#   proto/user.proto:5: Previously present RPC "DeleteUser" on
#   service "UserService" was deleted.
```

**Уровни проверки**:

| Уровень | Что проверяет | Когда использовать |
|---------|---------------|-------------------|
| `FILE` | Breaking changes на уровне файлов | По умолчанию, подходит для большинства |
| `PACKAGE` | Breaking changes на уровне пакетов | Если перемещаете файлы между директориями |
| `WIRE` | Только wire-совместимость (бинарная) | Если важна только бинарная совместимость |
| `WIRE_JSON` | Wire + JSON совместимость | Если используете JSON сериализацию |

> 💡 **Для C# разработчиков**: Это аналог проверки обратной совместимости NuGet-пакетов. Как `Microsoft.DotNet.ApiCompat` проверяет, что новая версия библиотеки не ломает существующих потребителей, так `buf breaking` проверяет proto API.

### buf generate — генерация кода

```bash
# Генерация кода из всех proto-файлов
buf generate

# Генерация только для конкретного модуля
buf generate proto/myapp/user/v1

# Результат (в директории gen/):
# gen/
# ├── myapp/user/v1/
# │   ├── user.pb.go           # Protobuf messages
# │   ├── user_grpc.pb.go      # gRPC server/client код
# │   └── user.pb.gw.go        # gRPC-Gateway reverse proxy
# └── openapiv2/
#     └── myapp/user/v1/
#         └── user.swagger.json # OpenAPI документация
```

**Сравнение workflow: C# vs Go**:

```csharp
// C# — генерация автоматическая при сборке
// .csproj:
// <Protobuf Include="Protos\user.proto" GrpcServices="Both" />
// dotnet build → автоматически вызывает protoc через MSBuild

// Сгенерированный код в obj/ — не коммитится в git
```

```bash
# Go — генерация явная, отдельный шаг
buf generate

# Сгенерированный код в gen/ — обычно коммитится в git
# (или генерируется в CI)
```

### Buf Schema Registry (BSR)

BSR — это реестр proto-модулей, аналог **NuGet** для protobuf:

```bash
# Авторизация
buf registry login

# Публикация модуля
buf push

# Использование чужого модуля (в buf.yaml):
# deps:
#   - buf.build/googleapis/googleapis
#   - buf.build/envoyproxy/protoc-gen-validate

# Обновление зависимостей (аналог go mod tidy)
buf dep update
```

**Преимущества BSR**:
- Централизованное хранение proto-определений
- Версионирование и breaking change detection
- Автоматическая генерация SDK для Go, TypeScript, Java, и др.
- Документация API из комментариев в proto

### buf в CI/CD

```yaml
# .github/workflows/proto.yml
name: Proto CI

on:
  push:
    paths: ['proto/**']

jobs:
  proto:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: bufbuild/buf-setup-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}

      # Линтинг
      - uses: bufbuild/buf-lint-action@v1
        with:
          input: proto

      # Проверка breaking changes (относительно main)
      - uses: bufbuild/buf-breaking-action@v1
        with:
          input: proto
          against: 'https://github.com/${{ github.repository }}.git#branch=main,subdir=proto'

      # Генерация и проверка актуальности
      - run: buf generate
      - run: |
          if ! git diff --exit-code gen/; then
            echo "Сгенерированный код устарел. Запустите 'buf generate' и закоммитьте."
            exit 1
          fi
```

> 💡 **Для C# разработчиков**: Этот CI pipeline — аналог того, что делает `dotnet build` + `Microsoft.DotNet.ApiCompat` + StyleCop в одном шаге. В .NET проекте подобные проверки обычно интегрированы в MSBuild, в Go — это отдельные шаги CI.

---

## Сервер gRPC

### Создание сервера

```go
package main

import (
    "log"
    "net"

    "google.golang.org/grpc"
    pb "github.com/myapp/gen/user/v1"
)

func main() {
    // 1. Создаём TCP listener
    lis, err := net.Listen("tcp", ":50051")
    if err != nil {
        log.Fatalf("не удалось слушать порт: %v", err)
    }

    // 2. Создаём gRPC сервер с опциями
    srv := grpc.NewServer(
        // Опции добавляются здесь (interceptors, TLS, etc.)
    )

    // 3. Регистрируем реализацию сервиса
    pb.RegisterUserServiceServer(srv, NewUserServer(repo))

    // 4. Запускаем
    log.Printf("gRPC сервер запущен на %s", lis.Addr())
    if err := srv.Serve(lis); err != nil {
        log.Fatalf("ошибка сервера: %v", err)
    }
}
```

**Сравнение создания сервера**:

```csharp
// C# — сервер создаётся через WebApplication builder
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddGrpc(options =>
{
    options.MaxReceiveMessageSize = 16 * 1024 * 1024; // 16 MB
    options.EnableDetailedErrors = true;
});

var app = builder.Build();
app.MapGrpcService<UserService>();
app.Run("https://localhost:5001");
```

```go
// Go — всё явно
srv := grpc.NewServer(
    grpc.MaxRecvMsgSize(16 * 1024 * 1024), // 16 MB
)
pb.RegisterUserServiceServer(srv, &userServer{})
srv.Serve(lis)
```

### Структура реализации сервиса

При генерации кода `protoc-gen-go-grpc` создаёт интерфейс и **Unimplemented** структуру:

```go
// Сгенерированный код (user_grpc.pb.go):

// Интерфейс, который нужно реализовать
type UserServiceServer interface {
    GetUser(context.Context, *GetUserRequest) (*GetUserResponse, error)
    CreateUser(context.Context, *CreateUserRequest) (*CreateUserResponse, error)
    UpdateUser(context.Context, *UpdateUserRequest) (*UpdateUserResponse, error)
    DeleteUser(context.Context, *DeleteUserRequest) (*emptypb.Empty, error)
    ListUsers(context.Context, *ListUsersRequest) (*ListUsersResponse, error)
    WatchUsers(*WatchUsersRequest, grpc.ServerStreamingServer[UserEvent]) error
    ImportUsers(grpc.ClientStreamingServer[ImportUserRequest, ImportUsersResponse]) error
    Chat(grpc.BidiStreamingServer[ChatMessage, ChatMessage]) error
    mustEmbedUnimplementedUserServiceServer()
}

// Встроить для forward compatibility
type UnimplementedUserServiceServer struct{}
```

```go
// Ваша реализация
type userServer struct {
    pb.UnimplementedUserServiceServer // Встраиваем для forward compatibility
    repo UserRepository
}

// Конструктор — передаём зависимости явно (не через DI)
func NewUserServer(repo UserRepository) *userServer {
    return &userServer{repo: repo}
}
```

> ⚠️ **Важно**: Всегда встраивайте `UnimplementedUserServiceServer`. Если в proto добавится новый метод, сервер продолжит работать — новый метод вернёт `codes.Unimplemented`. Без встраивания код перестанет компилироваться при добавлении нового RPC. Это аналог наследования `UsersBase` в C#.

### Unary RPC

Самый простой тип — один запрос, один ответ:

```go
func (s *userServer) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.GetUserResponse, error) {
    // Валидация
    if req.GetUserId() == "" {
        return nil, status.Error(codes.InvalidArgument, "user_id обязателен")
    }

    // Бизнес-логика
    user, err := s.repo.GetByID(ctx, req.GetUserId())
    if err != nil {
        if errors.Is(err, ErrNotFound) {
            return nil, status.Errorf(codes.NotFound, "пользователь %s не найден", req.GetUserId())
        }
        return nil, status.Errorf(codes.Internal, "ошибка базы данных: %v", err)
    }

    return &pb.GetUserResponse{
        User: toProtoUser(user),
    }, nil
}

func (s *userServer) CreateUser(ctx context.Context, req *pb.CreateUserRequest) (*pb.CreateUserResponse, error) {
    user := &User{
        Email:       req.GetEmail(),
        DisplayName: req.GetDisplayName(),
        Role:        fromProtoRole(req.GetRole()),
    }

    created, err := s.repo.Create(ctx, user)
    if err != nil {
        if errors.Is(err, ErrDuplicate) {
            return nil, status.Errorf(codes.AlreadyExists, "email %s уже используется", req.GetEmail())
        }
        return nil, status.Errorf(codes.Internal, "не удалось создать пользователя: %v", err)
    }

    return &pb.CreateUserResponse{
        User: toProtoUser(created),
    }, nil
}
```

**Сравнение Unary RPC: C# vs Go**:

```csharp
// C# — async Task, DI, исключения
public override async Task<GetUserResponse> GetUser(
    GetUserRequest request, ServerCallContext context)
{
    if (string.IsNullOrEmpty(request.UserId))
        throw new RpcException(new Status(StatusCode.InvalidArgument, "user_id обязателен"));

    var user = await _repo.GetByIdAsync(request.UserId, context.CancellationToken);
    if (user == null)
        throw new RpcException(new Status(StatusCode.NotFound, $"Пользователь {request.UserId} не найден"));

    return new GetUserResponse { User = MapToProto(user) };
}
```

```go
// Go — синхронный стиль, явные ошибки, context
func (s *userServer) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.GetUserResponse, error) {
    if req.GetUserId() == "" {
        return nil, status.Error(codes.InvalidArgument, "user_id обязателен")
    }

    user, err := s.repo.GetByID(ctx, req.GetUserId())
    if err != nil {
        return nil, status.Errorf(codes.NotFound, "пользователь %s не найден", req.GetUserId())
    }

    return &pb.GetUserResponse{User: toProtoUser(user)}, nil
}
```

| Аспект | C# | Go |
|--------|----|----|
| Возврат ошибки | `throw new RpcException(...)` | `return nil, status.Error(...)` |
| Async | `async Task<T>` + `await` | Синхронный стиль (context для отмены) |
| Отмена | `context.CancellationToken` | `ctx.Done()` / `ctx.Err()` |
| DI | Constructor injection | Поля структуры |
| Null safety | `user == null` | `errors.Is(err, ...)` |

### Server Streaming RPC

Сервер отправляет поток сообщений клиенту:

```go
func (s *userServer) WatchUsers(
    req *pb.WatchUsersRequest,
    stream grpc.ServerStreamingServer[pb.UserEvent],
) error {
    // Подписываемся на изменения (например, через канал)
    events := s.repo.Subscribe(stream.Context(), req.GetRoles())

    for {
        select {
        case <-stream.Context().Done():
            // Клиент отключился или дедлайн истёк
            return stream.Context().Err()

        case event, ok := <-events:
            if !ok {
                // Канал закрыт — завершаем стрим
                return nil
            }

            if err := stream.Send(toProtoEvent(event)); err != nil {
                return err
            }
        }
    }
}
```

**Сравнение Server Streaming: C# vs Go**:

```csharp
// C# — IServerStreamWriter<T> + await foreach
public override async Task WatchUsers(
    WatchUsersRequest request,
    IServerStreamWriter<UserEvent> responseStream,
    ServerCallContext context)
{
    await foreach (var evt in _repo.SubscribeAsync(request.Roles, context.CancellationToken))
    {
        await responseStream.WriteAsync(MapToProto(evt));
    }
}
```

```go
// Go — for + select + stream.Send()
func (s *userServer) WatchUsers(
    req *pb.WatchUsersRequest,
    stream grpc.ServerStreamingServer[pb.UserEvent],
) error {
    events := s.repo.Subscribe(stream.Context(), req.GetRoles())
    for event := range events {
        if err := stream.Send(toProtoEvent(event)); err != nil {
            return err
        }
    }
    return nil
}
```

> 💡 Обратите внимание: в Go Server Streaming метод **не получает** `context.Context` как отдельный параметр — контекст доступен через `stream.Context()`. Также метод не получает `*Request` и `stream` одновременно как в C# (где 3 параметра) — в Go request и stream передаются как 2 параметра.

### Client Streaming RPC

Клиент отправляет поток сообщений, сервер возвращает один ответ:

```go
func (s *userServer) ImportUsers(
    stream grpc.ClientStreamingServer[pb.ImportUserRequest, pb.ImportUsersResponse],
) error {
    var imported, failed int32
    var errs []string

    for {
        req, err := stream.Recv()
        if err == io.EOF {
            // Клиент завершил отправку — возвращаем результат
            return stream.SendAndClose(&pb.ImportUsersResponse{
                ImportedCount: imported,
                FailedCount:   failed,
                Errors:        errs,
            })
        }
        if err != nil {
            return err
        }

        // Обрабатываем каждого пользователя
        if err := s.repo.Create(stream.Context(), &User{
            Email:       req.GetEmail(),
            DisplayName: req.GetDisplayName(),
            Role:        fromProtoRole(req.GetRole()),
        }); err != nil {
            failed++
            errs = append(errs, fmt.Sprintf("email %s: %v", req.GetEmail(), err))
        } else {
            imported++
        }
    }
}
```

**Сравнение Client Streaming: C# vs Go**:

```csharp
// C# — IAsyncStreamReader<T> + MoveNext()
public override async Task<ImportUsersResponse> ImportUsers(
    IAsyncStreamReader<ImportUserRequest> requestStream,
    ServerCallContext context)
{
    int imported = 0, failed = 0;
    var errors = new List<string>();

    await foreach (var req in requestStream.ReadAllAsync(context.CancellationToken))
    {
        try
        {
            await _repo.CreateAsync(new User { Email = req.Email });
            imported++;
        }
        catch (Exception ex)
        {
            failed++;
            errors.Add($"email {req.Email}: {ex.Message}");
        }
    }

    return new ImportUsersResponse
    {
        ImportedCount = imported,
        FailedCount = failed,
        Errors = { errors }
    };
}
```

| Аспект | C# | Go |
|--------|----|----|
| Чтение потока | `await foreach (ReadAllAsync())` | `for { stream.Recv() }` |
| Конец потока | Итерация завершается | `err == io.EOF` |
| Отправка ответа | `return new Response(...)` | `stream.SendAndClose(...)` |

### Bidirectional Streaming RPC

Оба направления работают одновременно:

```go
func (s *userServer) Chat(
    stream grpc.BidiStreamingServer[pb.ChatMessage, pb.ChatMessage],
) error {
    for {
        msg, err := stream.Recv()
        if err == io.EOF {
            return nil
        }
        if err != nil {
            return err
        }

        // Обрабатываем сообщение и отвечаем
        reply := &pb.ChatMessage{
            UserId: "system",
            Text:   fmt.Sprintf("Получено от %s: %s", msg.GetUserId(), msg.GetText()),
            SentAt: timestamppb.Now(),
        }

        if err := stream.Send(reply); err != nil {
            return err
        }
    }
}
```

Для более сложных сценариев (например, чат-комната), приём и отправка разделяются в горутины:

```go
func (s *userServer) Chat(
    stream grpc.BidiStreamingServer[pb.ChatMessage, pb.ChatMessage],
) error {
    // Канал для сообщений на отправку
    outgoing := make(chan *pb.ChatMessage, 100)
    defer close(outgoing)

    // Горутина для отправки сообщений
    var sendErr error
    var wg sync.WaitGroup
    wg.Add(1)
    go func() {
        defer wg.Done()
        for msg := range outgoing {
            if err := stream.Send(msg); err != nil {
                sendErr = err
                return
            }
        }
    }()

    // Основной цикл — чтение сообщений
    for {
        msg, err := stream.Recv()
        if err == io.EOF {
            break
        }
        if err != nil {
            return err
        }

        // Рассылка всем подписчикам (через chat room)
        s.chatRoom.Broadcast(msg, outgoing)
    }

    wg.Wait()
    return sendErr
}
```

> 💡 **Для C# разработчиков**: В C# bidirectional streaming обычно тоже разделяют на чтение и запись, но используют `Task.WhenAll` или `Channel<T>`:
> ```csharp
> var readTask = Task.Run(async () => {
>     await foreach (var msg in requestStream.ReadAllAsync(ct)) { ... }
> });
> var writeTask = WriteMessagesAsync(responseStream, ct);
> await Task.WhenAll(readTask, writeTask);
> ```
> В Go аналогичная структура, но с горутинами и каналами вместо `Task` и `Channel<T>`.

### Graceful Shutdown

```go
func main() {
    lis, err := net.Listen("tcp", ":50051")
    if err != nil {
        log.Fatalf("не удалось слушать порт: %v", err)
    }

    srv := grpc.NewServer()
    pb.RegisterUserServiceServer(srv, NewUserServer(repo))

    // Запускаем сервер в горутине
    go func() {
        log.Printf("gRPC сервер запущен на %s", lis.Addr())
        if err := srv.Serve(lis); err != nil {
            log.Fatalf("ошибка сервера: %v", err)
        }
    }()

    // Ожидаем сигнал завершения
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    log.Println("Завершение работы сервера...")

    // GracefulStop ждёт завершения активных RPC
    // Stop() завершает немедленно
    srv.GracefulStop()

    log.Println("Сервер остановлен")
}
```

**Сравнение Graceful Shutdown: C# vs Go**:

| Аспект | C# | Go |
|--------|----|----|
| Механизм | `IHostApplicationLifetime` / `WebApplication.StopAsync()` | `srv.GracefulStop()` |
| Сигнал | `Console.CancelKeyPress` / `IHostedService` | `signal.Notify(quit, SIGTERM)` |
| Таймаут | `HostOptions.ShutdownTimeout` | Вручную через `context.WithTimeout` + `srv.Stop()` |

---

## Клиент gRPC

### Подключение

```go
import (
    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"
    pb "github.com/myapp/gen/user/v1"
)

func main() {
    // grpc.NewClient — современный API (Go gRPC v1.63+)
    // Заменяет устаревший grpc.Dial / grpc.DialContext
    conn, err := grpc.NewClient(
        "localhost:50051",
        grpc.WithTransportCredentials(insecure.NewCredentials()), // Без TLS (dev)
    )
    if err != nil {
        log.Fatalf("не удалось подключиться: %v", err)
    }
    defer conn.Close()

    // Создаём типизированный клиент
    client := pb.NewUserServiceClient(conn)

    // Используем клиент...
}
```

> ⚠️ **Важно**: `grpc.Dial` и `grpc.DialContext` помечены как deprecated начиная с gRPC Go v1.63. Используйте `grpc.NewClient` — он не создаёт соединение сразу (lazy connect), а подключается при первом вызове.

**Сравнение подключения: C# vs Go**:

```csharp
// C# — GrpcChannel (обёртка над HttpClient)
using var channel = GrpcChannel.ForAddress("https://localhost:5001");
var client = new UserService.UserServiceClient(channel);
```

```go
// Go — grpc.NewClient + ClientConn
conn, err := grpc.NewClient("localhost:50051",
    grpc.WithTransportCredentials(insecure.NewCredentials()),
)
defer conn.Close()
client := pb.NewUserServiceClient(conn)
```

### Вызов Unary RPC

```go
func getUser(ctx context.Context, client pb.UserServiceClient, userID string) (*pb.User, error) {
    // Дедлайн через контекст
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()

    resp, err := client.GetUser(ctx, &pb.GetUserRequest{
        UserId: userID,
    })
    if err != nil {
        // Извлекаем gRPC статус из ошибки
        st, ok := status.FromError(err)
        if ok {
            switch st.Code() {
            case codes.NotFound:
                return nil, fmt.Errorf("пользователь не найден: %s", userID)
            case codes.DeadlineExceeded:
                return nil, fmt.Errorf("таймаут запроса")
            default:
                return nil, fmt.Errorf("gRPC ошибка [%s]: %s", st.Code(), st.Message())
            }
        }
        return nil, err
    }

    return resp.GetUser(), nil
}
```

### Работа со стримами

#### Чтение Server Stream

```go
func watchUsers(ctx context.Context, client pb.UserServiceClient) error {
    stream, err := client.WatchUsers(ctx, &pb.WatchUsersRequest{
        Roles: []pb.UserRole{pb.UserRole_USER_ROLE_ADMIN},
    })
    if err != nil {
        return fmt.Errorf("не удалось начать watch: %w", err)
    }

    for {
        event, err := stream.Recv()
        if err == io.EOF {
            log.Println("Стрим завершён сервером")
            return nil
        }
        if err != nil {
            return fmt.Errorf("ошибка чтения стрима: %w", err)
        }

        log.Printf("Событие: %s, пользователь: %s",
            event.GetType(), event.GetUser().GetDisplayName())
    }
}
```

#### Отправка Client Stream

```go
func importUsers(ctx context.Context, client pb.UserServiceClient, users []*User) (*pb.ImportUsersResponse, error) {
    stream, err := client.ImportUsers(ctx)
    if err != nil {
        return nil, err
    }

    for _, u := range users {
        if err := stream.Send(&pb.ImportUserRequest{
            Email:       u.Email,
            DisplayName: u.DisplayName,
            Role:        toProtoRole(u.Role),
        }); err != nil {
            return nil, fmt.Errorf("ошибка отправки: %w", err)
        }
    }

    // Закрываем стрим и получаем ответ
    return stream.CloseAndRecv()
}
```

#### Bidirectional Stream на клиенте

```go
func chat(ctx context.Context, client pb.UserServiceClient, userID string) error {
    stream, err := client.Chat(ctx)
    if err != nil {
        return err
    }

    // Горутина для получения сообщений
    go func() {
        for {
            msg, err := stream.Recv()
            if err == io.EOF {
                return
            }
            if err != nil {
                log.Printf("ошибка получения: %v", err)
                return
            }
            fmt.Printf("[%s]: %s\n", msg.GetUserId(), msg.GetText())
        }
    }()

    // Отправка сообщений из stdin
    scanner := bufio.NewScanner(os.Stdin)
    for scanner.Scan() {
        if err := stream.Send(&pb.ChatMessage{
            UserId: userID,
            Text:   scanner.Text(),
            SentAt: timestamppb.Now(),
        }); err != nil {
            return fmt.Errorf("ошибка отправки: %w", err)
        }
    }

    // Закрываем сторону отправки
    return stream.CloseSend()
}
```

### Connection Management

```go
// Production-конфигурация клиента
conn, err := grpc.NewClient(
    "dns:///user-service.default.svc.cluster.local:50051",
    grpc.WithTransportCredentials(credentials.NewTLS(tlsConfig)),
    // Балансировка нагрузки (round-robin между эндпоинтами)
    grpc.WithDefaultServiceConfig(`{"loadBalancingConfig": [{"round_robin":{}}]}`),
    // Keepalive — поддержание соединения
    grpc.WithKeepaliveParams(keepalive.ClientParameters{
        Time:                10 * time.Second, // Пинг каждые 10 секунд при idle
        Timeout:             3 * time.Second,  // Таймаут ожидания pong
        PermitWithoutStream: true,             // Пинговать даже без активных стримов
    }),
)
```

> 💡 **Для C# разработчиков**: В .NET `GrpcChannel` — обёртка над `HttpClient`, и connection management наследует настройки `SocketsHttpHandler`. В Go `grpc.ClientConn` управляет соединениями самостоятельно через механизм resolvers и balancers. Одного `ClientConn` обычно достаточно для всех вызовов — он мультиплексирует запросы через HTTP/2.

---

## Контекст, дедлайны и метаданные

### Deadlines и Timeouts

В gRPC дедлайн — это абсолютное время, после которого RPC считается неуспешным. Дедлайны **пропагируются** через цепочку сервисов: если Service A вызывает Service B с дедлайном 5 секунд, и 2 секунды уже потрачены — Service B получит оставшиеся 3 секунды.

```go
// Клиент: установка дедлайна
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

resp, err := client.GetUser(ctx, &pb.GetUserRequest{UserId: "123"})
if err != nil {
    st, _ := status.FromError(err)
    if st.Code() == codes.DeadlineExceeded {
        log.Println("Запрос превысил дедлайн")
    }
}

// Сервер: проверка дедлайна
func (s *userServer) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.GetUserResponse, error) {
    // Проверяем, не истёк ли дедлайн до начала работы
    if ctx.Err() == context.DeadlineExceeded {
        return nil, status.Error(codes.DeadlineExceeded, "дедлайн истёк")
    }

    // Передаём context дальше — дедлайн пропагируется автоматически
    user, err := s.repo.GetByID(ctx, req.GetUserId())
    // ...
}
```

**Сравнение дедлайнов: C# vs Go**:

```csharp
// C# — через CallOptions или CancellationToken
var deadline = DateTime.UtcNow.AddSeconds(5);
var response = await client.GetUserAsync(
    request,
    deadline: deadline,
    cancellationToken: ct);

// Или через GrpcChannelOptions (глобально)
var channel = GrpcChannel.ForAddress("https://localhost:5001", new GrpcChannelOptions
{
    HttpHandler = new SocketsHttpHandler
    {
        // Общий таймаут на уровне HTTP
        ConnectTimeout = TimeSpan.FromSeconds(5)
    }
});
```

```go
// Go — через context (единый механизм)
ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
defer cancel()
resp, err := client.GetUser(ctx, req)
```

> 💡 **Ключевое отличие**: В C# есть два механизма — `Deadline` (gRPC-специфичный) и `CancellationToken` (универсальный .NET). В Go — единый `context.Context`, который обслуживает и дедлайны, и отмену, и передачу метаданных. Это проще и согласованнее.

### Metadata (заголовки)

Metadata — это key-value пары, аналог HTTP заголовков. Передаются в начале и конце RPC:

```go
import "google.golang.org/grpc/metadata"

// === Клиент: отправка metadata ===
func callWithMetadata(ctx context.Context, client pb.UserServiceClient) {
    // Создаём metadata
    md := metadata.Pairs(
        "authorization", "Bearer eyJhbG...",
        "x-request-id", uuid.New().String(),
        "x-client-version", "1.2.0",
    )

    // Добавляем к контексту
    ctx = metadata.NewOutgoingContext(ctx, md)

    // Вызываем RPC — metadata отправится автоматически
    resp, err := client.GetUser(ctx, &pb.GetUserRequest{UserId: "123"})
    // ...

    // Чтение metadata из ответа (headers и trailers)
    var header, trailer metadata.MD
    resp, err = client.GetUser(ctx, req,
        grpc.Header(&header),   // Заголовки ответа
        grpc.Trailer(&trailer), // Трейлеры ответа
    )
    log.Printf("Server version: %s", header.Get("x-server-version"))
}

// === Сервер: чтение и отправка metadata ===
func (s *userServer) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.GetUserResponse, error) {
    // Чтение входящих metadata
    md, ok := metadata.FromIncomingContext(ctx)
    if !ok {
        return nil, status.Error(codes.Internal, "нет metadata")
    }

    // Извлекаем значения
    requestID := ""
    if vals := md.Get("x-request-id"); len(vals) > 0 {
        requestID = vals[0]
    }

    authHeader := ""
    if vals := md.Get("authorization"); len(vals) > 0 {
        authHeader = vals[0]
    }

    log.Printf("request_id=%s, auth=%s", requestID, authHeader)

    // Отправляем metadata в ответе
    header := metadata.Pairs("x-server-version", "2.1.0")
    if err := grpc.SendHeader(ctx, header); err != nil {
        return nil, err
    }

    // Трейлеры — отправляются после ответа
    trailer := metadata.Pairs("x-processing-time-ms", "42")
    if err := grpc.SetTrailer(ctx, trailer); err != nil {
        return nil, err
    }

    // ...
    return &pb.GetUserResponse{User: toProtoUser(user)}, nil
}
```

**Сравнение Metadata: C# vs Go**:

```csharp
// C# — Metadata класс + ServerCallContext
public override async Task<GetUserResponse> GetUser(
    GetUserRequest request, ServerCallContext context)
{
    // Чтение
    var requestId = context.RequestHeaders.GetValue("x-request-id");
    var auth = context.RequestHeaders.GetValue("authorization");

    // Отправка
    await context.WriteResponseHeadersAsync(new Metadata
    {
        { "x-server-version", "2.1.0" }
    });

    context.ResponseTrailers.Add("x-processing-time-ms", "42");
    // ...
}
```

| Аспект | C# | Go |
|--------|----|----|
| Входящие | `context.RequestHeaders` | `metadata.FromIncomingContext(ctx)` |
| Исходящие (клиент) | `new CallOptions(headers: md)` | `metadata.NewOutgoingContext(ctx, md)` |
| Ответ (сервер) | `context.WriteResponseHeadersAsync()` | `grpc.SendHeader(ctx, md)` |
| Трейлеры | `context.ResponseTrailers.Add()` | `grpc.SetTrailer(ctx, md)` |

### Коды ошибок gRPC

gRPC определяет 16 стандартных кодов ошибок. Правильный выбор кода критически важен для корректной работы retry и мониторинга:

```go
import (
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"
)

// Создание ошибки с кодом
err := status.Error(codes.NotFound, "пользователь не найден")
err = status.Errorf(codes.InvalidArgument, "email '%s' невалиден", email)

// Извлечение кода из ошибки
st, ok := status.FromError(err)
if ok {
    fmt.Println(st.Code())    // codes.NotFound
    fmt.Println(st.Message()) // "пользователь не найден"
}
```

**Сопоставление кодов gRPC с HTTP и типичными сценариями**:

| gRPC Code | HTTP | Когда использовать | C# StatusCode |
|-----------|------|--------------------|---------------|
| `OK` | 200 | Успех | `StatusCode.OK` |
| `InvalidArgument` | 400 | Невалидные входные данные | `StatusCode.InvalidArgument` |
| `NotFound` | 404 | Ресурс не найден | `StatusCode.NotFound` |
| `AlreadyExists` | 409 | Ресурс уже существует | `StatusCode.AlreadyExists` |
| `PermissionDenied` | 403 | Нет прав (аутентифицирован, но нет доступа) | `StatusCode.PermissionDenied` |
| `Unauthenticated` | 401 | Не аутентифицирован | `StatusCode.Unauthenticated` |
| `ResourceExhausted` | 429 | Rate limit, квота исчерпана | `StatusCode.ResourceExhausted` |
| `FailedPrecondition` | 400 | Нарушено предусловие (например, optimistic lock) | `StatusCode.FailedPrecondition` |
| `Aborted` | 409 | Конфликт (concurrency, transaction abort) | `StatusCode.Aborted` |
| `DeadlineExceeded` | 504 | Таймаут | `StatusCode.DeadlineExceeded` |
| `Unavailable` | 503 | Сервис недоступен (retry имеет смысл) | `StatusCode.Unavailable` |
| `Internal` | 500 | Внутренняя ошибка сервера | `StatusCode.Internal` |
| `Unimplemented` | 501 | Метод не реализован | `StatusCode.Unimplemented` |
| `Cancelled` | 499 | Клиент отменил запрос | `StatusCode.Cancelled` |
| `DataLoss` | 500 | Потеря данных | `StatusCode.DataLoss` |
| `Unknown` | 500 | Неизвестная ошибка | `StatusCode.Unknown` |

> ⚠️ **Распространённая ошибка**: Не используйте `Internal` для всех ошибок. `InvalidArgument` для плохих входных данных, `NotFound` для отсутствующих ресурсов, `Unavailable` для временной недоступности (клиент может retry). Правильные коды позволяют клиентам принимать верные решения о retry.

### Rich Error Model

Стандартный `status.Error` передаёт только код и текст. Для структурированных деталей используйте **Rich Error Model**:

```go
import (
    "google.golang.org/genproto/googleapis/rpc/errdetails"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"
)

func (s *userServer) CreateUser(ctx context.Context, req *pb.CreateUserRequest) (*pb.CreateUserResponse, error) {
    // Валидация с подробными ошибками
    var violations []*errdetails.BadRequest_FieldViolation

    if req.GetEmail() == "" {
        violations = append(violations, &errdetails.BadRequest_FieldViolation{
            Field:       "email",
            Description: "Email обязателен",
        })
    }
    if !isValidEmail(req.GetEmail()) {
        violations = append(violations, &errdetails.BadRequest_FieldViolation{
            Field:       "email",
            Description: "Некорректный формат email",
        })
    }

    if len(violations) > 0 {
        st := status.New(codes.InvalidArgument, "ошибка валидации")
        detailed, err := st.WithDetails(&errdetails.BadRequest{
            FieldViolations: violations,
        })
        if err != nil {
            return nil, st.Err() // Fallback без деталей
        }
        return nil, detailed.Err()
    }

    // ...
}

// Клиент: извлечение деталей
func handleError(err error) {
    st := status.Convert(err)
    for _, detail := range st.Details() {
        switch d := detail.(type) {
        case *errdetails.BadRequest:
            for _, v := range d.GetFieldViolations() {
                fmt.Printf("Поле %s: %s\n", v.GetField(), v.GetDescription())
            }
        case *errdetails.RetryInfo:
            fmt.Printf("Повторите через: %s\n", d.GetRetryDelay().AsDuration())
        case *errdetails.ErrorInfo:
            fmt.Printf("Причина: %s, домен: %s\n", d.GetReason(), d.GetDomain())
        }
    }
}
```

> 💡 **Для C# разработчиков**: В .NET rich errors доступны через `Google.Rpc.Status` и `Grpc.StatusProto`. Но на практике в C# чаще используют `RpcException` с простым текстом или custom metadata. В Go rich error model более распространён, особенно в Google-style API.

---

## Interceptors (Middleware для gRPC)

Interceptors — аналог middleware в HTTP-серверах и `Interceptor` базового класса в C# gRPC. Они перехватывают RPC вызовы для добавления cross-cutting concerns: логирование, аутентификация, метрики, recovery.

### Типы interceptors

В gRPC Go существует 4 типа interceptors:

| Тип | Сторона | Сигнатура |
|-----|---------|-----------|
| **Unary Server** | Сервер | `func(ctx, req, info, handler) (resp, err)` |
| **Stream Server** | Сервер | `func(srv, stream, info, handler) err` |
| **Unary Client** | Клиент | `func(ctx, method, req, reply, cc, invoker, opts) err` |
| **Stream Client** | Клиент | `func(ctx, desc, cc, method, streamer, opts) (stream, err)` |

**Сравнение с C#**:

```csharp
// C# — один базовый класс с virtual методами
public class LoggingInterceptor : Interceptor
{
    // Server Unary
    public override async Task<TResponse> UnaryServerHandler<TRequest, TResponse>(
        TRequest request, ServerCallContext context,
        UnaryServerMethod<TRequest, TResponse> continuation) { ... }

    // Server Streaming
    public override async Task ServerStreamingServerHandler<TRequest, TResponse>(
        TRequest request, IServerStreamWriter<TResponse> responseStream,
        ServerCallContext context,
        ServerStreamingServerMethod<TRequest, TResponse> continuation) { ... }

    // Client Unary
    public override AsyncUnaryCall<TResponse> AsyncUnaryCall<TRequest, TResponse>(
        TRequest request, ClientInterceptorContext<TRequest, TResponse> context,
        AsyncUnaryCallContinuation<TRequest, TResponse> continuation) { ... }
}
```

```go
// Go — отдельные функции для каждого типа
type UnaryServerInterceptor func(
    ctx context.Context,
    req any,
    info *grpc.UnaryServerInfo,
    handler grpc.UnaryHandler,
) (any, error)

type StreamServerInterceptor func(
    srv any,
    ss grpc.ServerStream,
    info *grpc.StreamServerInfo,
    handler grpc.StreamHandler,
) error
```

### Server Unary Interceptor

```go
// Логирование
func loggingInterceptor(
    ctx context.Context,
    req any,
    info *grpc.UnaryServerInfo,
    handler grpc.UnaryHandler,
) (any, error) {
    start := time.Now()

    // Вызываем следующий interceptor / handler
    resp, err := handler(ctx, req)

    // Логируем результат
    duration := time.Since(start)
    code := status.Code(err)

    slog.Info("gRPC вызов",
        "method", info.FullMethod,
        "code", code.String(),
        "duration", duration,
        "error", err,
    )

    return resp, err
}

// Recovery (перехват panic)
func recoveryInterceptor(
    ctx context.Context,
    req any,
    info *grpc.UnaryServerInfo,
    handler grpc.UnaryHandler,
) (resp any, err error) {
    defer func() {
        if r := recover(); r != nil {
            slog.Error("panic в gRPC handler",
                "method", info.FullMethod,
                "panic", r,
                "stack", string(debug.Stack()),
            )
            err = status.Errorf(codes.Internal, "внутренняя ошибка сервера")
        }
    }()

    return handler(ctx, req)
}

// Аутентификация
func authInterceptor(
    ctx context.Context,
    req any,
    info *grpc.UnaryServerInfo,
    handler grpc.UnaryHandler,
) (any, error) {
    // Пропускаем health check и reflection
    if info.FullMethod == "/grpc.health.v1.Health/Check" {
        return handler(ctx, req)
    }

    md, ok := metadata.FromIncomingContext(ctx)
    if !ok {
        return nil, status.Error(codes.Unauthenticated, "нет metadata")
    }

    tokens := md.Get("authorization")
    if len(tokens) == 0 {
        return nil, status.Error(codes.Unauthenticated, "нет токена авторизации")
    }

    // Валидация токена
    claims, err := validateToken(tokens[0])
    if err != nil {
        return nil, status.Errorf(codes.Unauthenticated, "невалидный токен: %v", err)
    }

    // Добавляем claims в context для использования в handlers
    ctx = context.WithValue(ctx, claimsKey{}, claims)

    return handler(ctx, req)
}
```

### Server Stream Interceptor

```go
// Обёртка для стрима — добавляет функциональность
type wrappedStream struct {
    grpc.ServerStream
    ctx context.Context
}

func (w *wrappedStream) Context() context.Context {
    return w.ctx
}

func streamLoggingInterceptor(
    srv any,
    ss grpc.ServerStream,
    info *grpc.StreamServerInfo,
    handler grpc.StreamHandler,
) error {
    start := time.Now()

    err := handler(srv, ss)

    slog.Info("gRPC stream завершён",
        "method", info.FullMethod,
        "duration", time.Since(start),
        "error", err,
    )

    return err
}

func streamAuthInterceptor(
    srv any,
    ss grpc.ServerStream,
    info *grpc.StreamServerInfo,
    handler grpc.StreamHandler,
) error {
    md, ok := metadata.FromIncomingContext(ss.Context())
    if !ok {
        return status.Error(codes.Unauthenticated, "нет metadata")
    }

    tokens := md.Get("authorization")
    if len(tokens) == 0 {
        return status.Error(codes.Unauthenticated, "нет токена")
    }

    claims, err := validateToken(tokens[0])
    if err != nil {
        return status.Errorf(codes.Unauthenticated, "невалидный токен: %v", err)
    }

    // Оборачиваем стрим с новым контекстом
    ctx := context.WithValue(ss.Context(), claimsKey{}, claims)
    wrapped := &wrappedStream{ServerStream: ss, ctx: ctx}

    return handler(srv, wrapped)
}
```

### Client Interceptors

```go
// Клиентский interceptor — добавляет auth токен ко всем запросам
func clientAuthInterceptor(
    ctx context.Context,
    method string,
    req, reply any,
    cc *grpc.ClientConn,
    invoker grpc.UnaryInvoker,
    opts ...grpc.CallOption,
) error {
    // Добавляем токен в metadata
    ctx = metadata.AppendToOutgoingContext(ctx,
        "authorization", "Bearer "+getAccessToken(),
    )

    return invoker(ctx, method, req, reply, cc, opts...)
}

// Клиентский interceptor — retry при Unavailable
func clientRetryInterceptor(
    ctx context.Context,
    method string,
    req, reply any,
    cc *grpc.ClientConn,
    invoker grpc.UnaryInvoker,
    opts ...grpc.CallOption,
) error {
    var lastErr error
    for attempt := 0; attempt < 3; attempt++ {
        lastErr = invoker(ctx, method, req, reply, cc, opts...)
        if lastErr == nil {
            return nil
        }

        st, ok := status.FromError(lastErr)
        if !ok || st.Code() != codes.Unavailable {
            return lastErr // Не retryable
        }

        // Exponential backoff
        delay := time.Duration(1<<attempt) * 100 * time.Millisecond
        select {
        case <-ctx.Done():
            return ctx.Err()
        case <-time.After(delay):
        }
    }
    return lastErr
}
```

### Chaining interceptors

```go
// Сервер — порядок имеет значение: первый interceptor вызывается первым
srv := grpc.NewServer(
    grpc.ChainUnaryInterceptor(
        recoveryInterceptor,     // 1. Recovery (обёртка вокруг всего)
        loggingInterceptor,      // 2. Логирование (замер времени)
        authInterceptor,         // 3. Аутентификация
    ),
    grpc.ChainStreamInterceptor(
        streamLoggingInterceptor,
        streamAuthInterceptor,
    ),
)

// Клиент — аналогично
conn, err := grpc.NewClient(
    "localhost:50051",
    grpc.WithChainUnaryInterceptor(
        clientAuthInterceptor,
        clientRetryInterceptor,
    ),
    grpc.WithTransportCredentials(insecure.NewCredentials()),
)
```

**Сравнение chaining: C# vs Go**:

```csharp
// C# — добавление через options
services.AddGrpc(options =>
{
    options.Interceptors.Add<RecoveryInterceptor>();
    options.Interceptors.Add<LoggingInterceptor>();
    options.Interceptors.Add<AuthInterceptor>();
});
```

```go
// Go — через ChainUnaryInterceptor
grpc.ChainUnaryInterceptor(
    recoveryInterceptor,
    loggingInterceptor,
    authInterceptor,
)
```

### go-grpc-middleware v2

Библиотека `github.com/grpc-ecosystem/go-grpc-middleware/v2` предоставляет готовые interceptors:

```go
import (
    "github.com/grpc-ecosystem/go-grpc-middleware/v2/interceptors/logging"
    "github.com/grpc-ecosystem/go-grpc-middleware/v2/interceptors/recovery"
    "github.com/grpc-ecosystem/go-grpc-middleware/v2/interceptors/auth"
    "github.com/grpc-ecosystem/go-grpc-middleware/v2/interceptors/ratelimit"
    "github.com/grpc-ecosystem/go-grpc-middleware/v2/interceptors/validator"
    "github.com/grpc-ecosystem/go-grpc-middleware/v2/interceptors/retry"
)

// Сервер с полным набором middleware
srv := grpc.NewServer(
    grpc.ChainUnaryInterceptor(
        // Recovery — перехват паников
        recovery.UnaryServerInterceptor(
            recovery.WithRecoveryHandler(func(p any) error {
                slog.Error("panic перехвачен", "panic", p)
                return status.Errorf(codes.Internal, "внутренняя ошибка")
            }),
        ),
        // Логирование
        logging.UnaryServerInterceptor(
            interceptorLogger(slog.Default()),
            logging.WithLogOnEvents(logging.StartCall, logging.FinishCall),
        ),
        // Аутентификация
        auth.UnaryServerInterceptor(authFunc),
        // Rate limiting
        ratelimit.UnaryServerInterceptor(limiter),
        // Валидация (если используете protovalidate)
        validator.UnaryServerInterceptor(),
    ),
    grpc.ChainStreamInterceptor(
        recovery.StreamServerInterceptor(),
        logging.StreamServerInterceptor(interceptorLogger(slog.Default())),
        auth.StreamServerInterceptor(authFunc),
    ),
)

// Функция аутентификации для auth middleware
func authFunc(ctx context.Context) (context.Context, error) {
    token, err := auth.AuthFromMD(ctx, "bearer")
    if err != nil {
        return nil, err
    }

    claims, err := validateJWT(token)
    if err != nil {
        return nil, status.Errorf(codes.Unauthenticated, "невалидный токен: %v", err)
    }

    return context.WithValue(ctx, claimsKey{}, claims), nil
}

// Адаптер slog для logging middleware
func interceptorLogger(l *slog.Logger) logging.Logger {
    return logging.LoggerFunc(func(ctx context.Context, lvl logging.Level, msg string, fields ...any) {
        l.Log(ctx, slog.Level(lvl), msg, fields...)
    })
}

// Клиент с retry middleware
conn, err := grpc.NewClient(
    "localhost:50051",
    grpc.WithChainUnaryInterceptor(
        retry.UnaryClientInterceptor(
            retry.WithMax(3),
            retry.WithBackoff(retry.BackoffExponential(100*time.Millisecond)),
            retry.WithCodes(codes.Unavailable, codes.ResourceExhausted),
        ),
    ),
    grpc.WithTransportCredentials(insecure.NewCredentials()),
)
```

> 💡 **Для C# разработчиков**: `go-grpc-middleware` — это аналог того, что ASP.NET Core предоставляет из коробки: logging, auth, rate limiting, error handling. В .NET эти concerns встроены в middleware pipeline и DI. В Go вы явно собираете pipeline из отдельных interceptors — больше контроля, но и больше кода настройки.

---

## gRPC-Gateway: REST API из gRPC

### Зачем нужен gRPC-Gateway

Не все клиенты могут использовать gRPC напрямую: браузеры, мобильные приложения, сторонние интеграции часто ожидают REST API с JSON. gRPC-Gateway автоматически генерирует reverse proxy, который транслирует REST-запросы в gRPC-вызовы.

```
             ┌──────────────────────────────┐
  REST/JSON  │      gRPC-Gateway            │  gRPC/Protobuf
  ─────────► │  (HTTP reverse proxy)        │ ──────────────►  gRPC Server
  GET /users │  JSON ↔ Protobuf conversion  │  ListUsers()
             └──────────────────────────────┘
```

**Сравнение подходов: C# vs Go**:

| Подход | C# | Go |
|--------|----|----|
| gRPC из браузера | `Grpc.AspNetCore.Web` (gRPC-Web middleware) | gRPC-Gateway (reverse proxy) |
| Один сервер REST+gRPC | Kestrel обслуживает оба протокола | Два listener или mux |
| Swagger | Swashbuckle / NSwag (из контроллеров) | `protoc-gen-openapiv2` (из proto) |

### HTTP annotations в .proto

Для gRPC-Gateway нужно добавить HTTP маппинг в proto-файлы:

```protobuf
syntax = "proto3";

package myapp.user.v1;

import "google/api/annotations.proto"; // HTTP annotations

service UserService {
    rpc GetUser(GetUserRequest) returns (GetUserResponse) {
        option (google.api.http) = {
            get: "/api/v1/users/{user_id}"
        };
    }

    rpc ListUsers(ListUsersRequest) returns (ListUsersResponse) {
        option (google.api.http) = {
            get: "/api/v1/users"
        };
    }

    rpc CreateUser(CreateUserRequest) returns (CreateUserResponse) {
        option (google.api.http) = {
            post: "/api/v1/users"
            body: "*"  // Всё тело запроса маппится на CreateUserRequest
        };
    }

    rpc UpdateUser(UpdateUserRequest) returns (UpdateUserResponse) {
        option (google.api.http) = {
            patch: "/api/v1/users/{user_id}"
            body: "user"  // Только поле "user" маппится из тела
        };
    }

    rpc DeleteUser(DeleteUserRequest) returns (google.protobuf.Empty) {
        option (google.api.http) = {
            delete: "/api/v1/users/{user_id}"
        };
    }
}
```

**Правила маппинга**:
- Поля из URL path (`{user_id}`) → поля запроса
- Query parameters → оставшиеся поля запроса (для GET)
- `body: "*"` → всё тело JSON маппится на запрос
- `body: "field"` → тело маппится на конкретное поле

### Реализация Gateway

```go
package main

import (
    "context"
    "log"
    "net"
    "net/http"

    "github.com/grpc-ecosystem/grpc-gateway/v2/runtime"
    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"

    pb "github.com/myapp/gen/user/v1"
)

func main() {
    ctx := context.Background()

    // === 1. Запускаем gRPC сервер ===
    lis, err := net.Listen("tcp", ":50051")
    if err != nil {
        log.Fatalf("не удалось слушать: %v", err)
    }

    grpcServer := grpc.NewServer()
    pb.RegisterUserServiceServer(grpcServer, NewUserServer(repo))

    go func() {
        log.Println("gRPC сервер на :50051")
        if err := grpcServer.Serve(lis); err != nil {
            log.Fatalf("ошибка gRPC: %v", err)
        }
    }()

    // === 2. Настраиваем gRPC-Gateway ===
    mux := runtime.NewServeMux(
        // Маппинг ошибок gRPC → HTTP
        runtime.WithErrorHandler(customErrorHandler),
        // Формат JSON (используем оригинальные имена полей из proto)
        runtime.WithMarshalerOption(runtime.MIMEWildcard, &runtime.JSONPb{
            MarshalOptions: protojson.MarshalOptions{
                UseProtoNames:   true,   // snake_case вместо camelCase
                EmitUnpopulated: false,  // Не выводить пустые поля
            },
            UnmarshalOptions: protojson.UnmarshalOptions{
                DiscardUnknown: true, // Игнорировать неизвестные поля
            },
        }),
    )

    opts := []grpc.DialOption{
        grpc.WithTransportCredentials(insecure.NewCredentials()),
    }

    // Регистрируем gateway handler (подключается к gRPC серверу)
    if err := pb.RegisterUserServiceHandlerFromEndpoint(ctx, mux, "localhost:50051", opts); err != nil {
        log.Fatalf("не удалось зарегистрировать gateway: %v", err)
    }

    // === 3. Запускаем HTTP сервер ===
    httpServer := &http.Server{
        Addr:    ":8080",
        Handler: mux,
    }

    log.Println("gRPC-Gateway (REST) на :8080")
    if err := httpServer.ListenAndServe(); err != nil {
        log.Fatalf("ошибка HTTP: %v", err)
    }
}

// Кастомная обработка ошибок — маппинг gRPC кодов в HTTP
func customErrorHandler(
    ctx context.Context,
    mux *runtime.ServeMux,
    marshaler runtime.Marshaler,
    w http.ResponseWriter,
    r *http.Request,
    err error,
) {
    // Используем стандартный обработчик (gRPC коды → HTTP коды автоматически)
    runtime.DefaultHTTPErrorHandler(ctx, mux, marshaler, w, r, err)
}
```

**Использование REST API**:
```bash
# GET /api/v1/users/123 → GetUser(user_id: "123")
curl http://localhost:8080/api/v1/users/123

# POST /api/v1/users → CreateUser({...})
curl -X POST http://localhost:8080/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "display_name": "John"}'

# GET /api/v1/users?page_size=10 → ListUsers(page_size: 10)
curl "http://localhost:8080/api/v1/users?page_size=10"
```

### Swagger/OpenAPI генерация

При использовании `protoc-gen-openapiv2` (или через buf) автоматически генерируется OpenAPI spec:

```yaml
# buf.gen.yaml — добавляем плагин
plugins:
  - remote: buf.build/grpc-ecosystem/openapiv2
    out: gen/openapiv2
```

```go
// Раздача Swagger UI вместе с gateway
import "github.com/grpc-ecosystem/grpc-gateway/v2/runtime"

func main() {
    mux := runtime.NewServeMux()
    // ... регистрация gateway

    // Swagger JSON
    httpMux := http.NewServeMux()
    httpMux.Handle("/", mux) // gRPC-Gateway
    httpMux.HandleFunc("/swagger/", func(w http.ResponseWriter, r *http.Request) {
        http.ServeFile(w, r, "gen/openapiv2/user.swagger.json")
    })

    http.ListenAndServe(":8080", httpMux)
}
```

---

## ConnectRPC: современная альтернатива

### Что такое ConnectRPC

ConnectRPC — это современная реализация RPC от команды Buf, которая решает основные проблемы classic gRPC:

| Проблема classic gRPC | Решение ConnectRPC |
|----------------------|-------------------|
| Требует HTTP/2 | Работает поверх HTTP/1.1 и HTTP/2 |
| Не работает из браузера | Нативная поддержка браузеров |
| Сложный binary протокол | Три протокола: Connect, gRPC, gRPC-Web |
| Нестандартные HTTP заголовки | Стандартные HTTP заголовки и коды |
| Сложная отладка | `curl`-friendly (JSON over HTTP) |

### connect-go: сервер и клиент

```go
// go get connectrpc.com/connect

// === Сервер ===
package main

import (
    "context"
    "log"
    "net/http"

    "connectrpc.com/connect"
    "golang.org/x/net/http2"
    "golang.org/x/net/http2/h2c"

    userv1 "github.com/myapp/gen/user/v1"
    "github.com/myapp/gen/user/v1/userv1connect" // Сгенерированный connect-код
)

type userServer struct {
    repo UserRepository
}

// Реализация — обычная функция, возвращающая connect.Response
func (s *userServer) GetUser(
    ctx context.Context,
    req *connect.Request[userv1.GetUserRequest],
) (*connect.Response[userv1.GetUserResponse], error) {
    // req.Msg — protobuf сообщение
    // req.Header() — HTTP заголовки (не gRPC metadata!)
    log.Printf("Authorization: %s", req.Header().Get("Authorization"))

    user, err := s.repo.GetByID(ctx, req.Msg.GetUserId())
    if err != nil {
        return nil, connect.NewError(connect.CodeNotFound, err)
    }

    resp := connect.NewResponse(&userv1.GetUserResponse{
        User: toProtoUser(user),
    })
    resp.Header().Set("X-Server-Version", "2.0")

    return resp, nil
}

func main() {
    srv := &userServer{repo: repo}

    // Регистрация — возвращает path и handler
    path, handler := userv1connect.NewUserServiceHandler(srv)

    mux := http.NewServeMux()
    mux.Handle(path, handler)

    // h2c — HTTP/2 без TLS (для development)
    log.Println("ConnectRPC сервер на :8080")
    http.ListenAndServe(":8080",
        h2c.NewHandler(mux, &http2.Server{}),
    )
}

// === Клиент ===
func connectClient() {
    client := userv1connect.NewUserServiceClient(
        http.DefaultClient,
        "http://localhost:8080",
    )

    resp, err := client.GetUser(
        context.Background(),
        connect.NewRequest(&userv1.GetUserRequest{UserId: "123"}),
    )
    if err != nil {
        // connect.CodeOf(err) возвращает код ошибки
        log.Fatalf("ошибка: %v (код: %s)", err, connect.CodeOf(err))
    }

    fmt.Printf("Пользователь: %s\n", resp.Msg.GetUser().GetDisplayName())
}
```

**Тестирование через curl** (невозможно с classic gRPC):
```bash
# ConnectRPC поддерживает JSON через обычный HTTP POST
curl -X POST http://localhost:8080/myapp.user.v1.UserService/GetUser \
  -H "Content-Type: application/json" \
  -d '{"userId": "123"}'
```

### Когда выбрать ConnectRPC vs classic gRPC

| Критерий | classic gRPC | ConnectRPC |
|----------|-------------|------------|
| **Зрелость** | Зрелый, proven (Google, CNCF) | Новый, быстро растёт |
| **Экосистема** | Огромная (middleware, tools, infra) | Растущая, но меньше |
| **Браузеры** | Нужен gRPC-Web proxy | Нативная поддержка |
| **curl/отладка** | Нет (бинарный протокол) | Да (JSON over HTTP) |
| **Interop** | gRPC стандарт | Совместим с gRPC серверами |
| **HTTP/1.1** | Нет | Да |
| **Streaming** | Все 4 типа | Все 4 типа |
| **Когда выбрать** | Инфраструктура уже на gRPC, нужна максимальная совместимость | Новый проект, нужна простота, browser clients |

> 💡 **Рекомендация**: Для внутренних микросервисов classic gRPC по-прежнему стандарт. Для public API или проектов, где нужна простота отладки и работа из браузера — рассмотрите ConnectRPC. Оба используют одни и те же `.proto` файлы.

---

## Health Checking и Reflection

### gRPC Health Checking Protocol

Стандартный протокол для проверки здоровья gRPC сервисов, критически важный для Kubernetes и load balancers:

```go
import (
    "google.golang.org/grpc/health"
    "google.golang.org/grpc/health/grpc_health_v1"
)

func main() {
    srv := grpc.NewServer()

    // Регистрируем бизнес-сервисы
    pb.RegisterUserServiceServer(srv, NewUserServer(repo))

    // Регистрируем health check сервис
    healthServer := health.NewServer()
    grpc_health_v1.RegisterHealthServer(srv, healthServer)

    // Устанавливаем статус для конкретного сервиса
    healthServer.SetServingStatus(
        "myapp.user.v1.UserService",
        grpc_health_v1.HealthCheckResponse_SERVING,
    )

    // Устанавливаем общий статус (пустая строка = весь сервер)
    healthServer.SetServingStatus(
        "",
        grpc_health_v1.HealthCheckResponse_SERVING,
    )

    // При shutdown
    go func() {
        <-quit
        healthServer.Shutdown() // Все сервисы → NOT_SERVING
        srv.GracefulStop()
    }()

    srv.Serve(lis)
}
```

**Kubernetes integration**:
```yaml
# Kubernetes pod spec
containers:
  - name: user-service
    ports:
      - containerPort: 50051
    livenessProbe:
      grpc:
        port: 50051
      initialDelaySeconds: 10
      periodSeconds: 10
    readinessProbe:
      grpc:
        port: 50051
        service: "myapp.user.v1.UserService"
      initialDelaySeconds: 5
      periodSeconds: 5
```

**Проверка через grpcurl**:
```bash
# Проверка здоровья
grpcurl -plaintext localhost:50051 grpc.health.v1.Health/Check

# Проверка конкретного сервиса
grpcurl -plaintext -d '{"service": "myapp.user.v1.UserService"}' \
  localhost:50051 grpc.health.v1.Health/Check
```

**Сравнение с C#**:

```csharp
// C# — через Grpc.AspNetCore.HealthChecks
services.AddGrpcHealthChecks()
    .AddCheck("database", () => /* ... */);

app.MapGrpcHealthChecksService();
```

```go
// Go — явная регистрация и управление статусом
healthServer := health.NewServer()
grpc_health_v1.RegisterHealthServer(srv, healthServer)
healthServer.SetServingStatus("service", grpc_health_v1.HealthCheckResponse_SERVING)
```

### Server Reflection

Reflection позволяет клиентам динамически обнаруживать сервисы и методы без `.proto` файлов. Незаменимо для отладки:

```go
import "google.golang.org/grpc/reflection"

func main() {
    srv := grpc.NewServer()
    pb.RegisterUserServiceServer(srv, NewUserServer(repo))

    // Включаем reflection (только для development!)
    reflection.Register(srv)

    srv.Serve(lis)
}
```

**Использование с grpcurl**:
```bash
# Список сервисов
grpcurl -plaintext localhost:50051 list
# myapp.user.v1.UserService
# grpc.health.v1.Health
# grpc.reflection.v1alpha.ServerReflection

# Список методов сервиса
grpcurl -plaintext localhost:50051 list myapp.user.v1.UserService
# myapp.user.v1.UserService.GetUser
# myapp.user.v1.UserService.CreateUser
# ...

# Описание метода
grpcurl -plaintext localhost:50051 describe myapp.user.v1.UserService.GetUser

# Вызов метода
grpcurl -plaintext \
  -d '{"user_id": "123"}' \
  localhost:50051 myapp.user.v1.UserService/GetUser
```

> ⚠️ **Важно**: Не включайте reflection в production без аутентификации — это раскрывает API surface атакующим. Либо отключайте в prod, либо защищайте interceptor-ом аутентификации.

---

## Безопасность

### TLS

```go
// === Сервер с TLS ===
import "google.golang.org/grpc/credentials"

func main() {
    // Загружаем серверный сертификат и ключ
    creds, err := credentials.NewServerTLSFromFile("server.crt", "server.key")
    if err != nil {
        log.Fatalf("не удалось загрузить TLS: %v", err)
    }

    srv := grpc.NewServer(
        grpc.Creds(creds),
    )
    pb.RegisterUserServiceServer(srv, NewUserServer(repo))

    lis, _ := net.Listen("tcp", ":50051")
    srv.Serve(lis)
}

// === Клиент с TLS ===
func main() {
    creds, err := credentials.NewClientTLSFromFile("ca.crt", "server.example.com")
    if err != nil {
        log.Fatalf("не удалось загрузить CA: %v", err)
    }

    conn, err := grpc.NewClient(
        "server.example.com:50051",
        grpc.WithTransportCredentials(creds),
    )
    // ...
}
```

### mTLS (Mutual TLS)

Mutual TLS — обе стороны аутентифицируют друг друга сертификатами. Стандарт для service-to-service коммуникации:

```go
import (
    "crypto/tls"
    "crypto/x509"
)

// === Сервер с mTLS ===
func newMTLSServer() *grpc.Server {
    // Загружаем серверный сертификат
    cert, err := tls.LoadX509KeyPair("server.crt", "server.key")
    if err != nil {
        log.Fatal(err)
    }

    // Загружаем CA для верификации клиентских сертификатов
    caCert, err := os.ReadFile("ca.crt")
    if err != nil {
        log.Fatal(err)
    }
    caPool := x509.NewCertPool()
    caPool.AppendCertsFromPEM(caCert)

    tlsConfig := &tls.Config{
        Certificates: []tls.Certificate{cert},
        ClientAuth:   tls.RequireAndVerifyClientCert,
        ClientCAs:    caPool,
        MinVersion:   tls.VersionTLS13,
    }

    return grpc.NewServer(
        grpc.Creds(credentials.NewTLS(tlsConfig)),
    )
}

// === Клиент с mTLS ===
func newMTLSClient() (*grpc.ClientConn, error) {
    // Клиентский сертификат
    cert, err := tls.LoadX509KeyPair("client.crt", "client.key")
    if err != nil {
        return nil, err
    }

    // CA сервера
    caCert, err := os.ReadFile("ca.crt")
    if err != nil {
        return nil, err
    }
    caPool := x509.NewCertPool()
    caPool.AppendCertsFromPEM(caCert)

    tlsConfig := &tls.Config{
        Certificates: []tls.Certificate{cert},
        RootCAs:      caPool,
        MinVersion:   tls.VersionTLS13,
    }

    return grpc.NewClient(
        "server.example.com:50051",
        grpc.WithTransportCredentials(credentials.NewTLS(tlsConfig)),
    )
}
```

### JWT аутентификация через metadata

Самый распространённый подход для аутентификации пользователей (не сервисов):

```go
// Per-RPC credentials — автоматически добавляют токен к каждому вызову
type tokenAuth struct {
    token string
}

func (t *tokenAuth) GetRequestMetadata(ctx context.Context, uri ...string) (map[string]string, error) {
    return map[string]string{
        "authorization": "Bearer " + t.token,
    }, nil
}

func (t *tokenAuth) RequireTransportSecurity() bool {
    return true // Требовать TLS
}

// Использование
conn, err := grpc.NewClient(
    "server.example.com:50051",
    grpc.WithTransportCredentials(creds),
    grpc.WithPerRPCCredentials(&tokenAuth{token: "eyJhbG..."}),
)
```

**Сравнение аутентификации: C# vs Go**:

```csharp
// C# — через CallCredentials
var credentials = CallCredentials.FromInterceptor(async (context, metadata) =>
{
    var token = await GetTokenAsync();
    metadata.Add("Authorization", $"Bearer {token}");
});

var channel = GrpcChannel.ForAddress("https://server:5001", new GrpcChannelOptions
{
    Credentials = ChannelCredentials.Create(
        new SslCredentials(), credentials)
});
```

```go
// Go — через PerRPCCredentials или interceptor
conn, err := grpc.NewClient("server:50051",
    grpc.WithTransportCredentials(creds),
    grpc.WithPerRPCCredentials(&tokenAuth{token: token}),
)
```

---

## Тестирование gRPC

### bufconn: in-memory тестирование

`bufconn` создаёт in-memory listener, позволяя тестировать gRPC сервер без реального сетевого соединения. Это аналог `WebApplicationFactory` в ASP.NET Core:

```go
import (
    "net"
    "testing"

    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"
    "google.golang.org/grpc/test/bufconn"

    pb "github.com/myapp/gen/user/v1"
)

const bufSize = 1024 * 1024

// setupTest создаёт in-memory gRPC сервер и клиент
func setupTest(t *testing.T) pb.UserServiceClient {
    t.Helper()

    // In-memory listener
    lis := bufconn.Listen(bufSize)

    // Создаём сервер
    srv := grpc.NewServer()
    repo := NewInMemoryUserRepository() // Тестовый репозиторий
    pb.RegisterUserServiceServer(srv, NewUserServer(repo))

    go func() {
        if err := srv.Serve(lis); err != nil {
            t.Errorf("ошибка сервера: %v", err)
        }
    }()

    // Создаём клиент через bufconn
    conn, err := grpc.NewClient(
        "passthrough://bufnet",
        grpc.WithContextDialer(func(ctx context.Context, s string) (net.Conn, error) {
            return lis.DialContext(ctx)
        }),
        grpc.WithTransportCredentials(insecure.NewCredentials()),
    )
    if err != nil {
        t.Fatalf("не удалось подключиться: %v", err)
    }

    t.Cleanup(func() {
        conn.Close()
        srv.Stop()
        lis.Close()
    })

    return pb.NewUserServiceClient(conn)
}

func TestGetUser(t *testing.T) {
    client := setupTest(t)

    // Создаём пользователя
    createResp, err := client.CreateUser(context.Background(), &pb.CreateUserRequest{
        Email:       "test@example.com",
        DisplayName: "Test User",
        Role:        pb.UserRole_USER_ROLE_MEMBER,
    })
    if err != nil {
        t.Fatalf("CreateUser: %v", err)
    }

    // Получаем пользователя
    getResp, err := client.GetUser(context.Background(), &pb.GetUserRequest{
        UserId: createResp.GetUser().GetId(),
    })
    if err != nil {
        t.Fatalf("GetUser: %v", err)
    }

    if getResp.GetUser().GetEmail() != "test@example.com" {
        t.Errorf("email = %s, want test@example.com", getResp.GetUser().GetEmail())
    }
}

func TestGetUser_NotFound(t *testing.T) {
    client := setupTest(t)

    _, err := client.GetUser(context.Background(), &pb.GetUserRequest{
        UserId: "nonexistent",
    })

    // Проверяем gRPC код ошибки
    st, ok := status.FromError(err)
    if !ok {
        t.Fatalf("ожидалась gRPC ошибка, получено: %v", err)
    }
    if st.Code() != codes.NotFound {
        t.Errorf("code = %s, want NotFound", st.Code())
    }
}

func TestCreateUser_Validation(t *testing.T) {
    client := setupTest(t)

    _, err := client.CreateUser(context.Background(), &pb.CreateUserRequest{
        Email: "", // Пустой email
    })

    st, _ := status.FromError(err)
    if st.Code() != codes.InvalidArgument {
        t.Errorf("code = %s, want InvalidArgument", st.Code())
    }
}
```

**Сравнение тестирования: C# vs Go**:

```csharp
// C# — WebApplicationFactory
public class UserServiceTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly UserService.UserServiceClient _client;

    public UserServiceTests(WebApplicationFactory<Program> factory)
    {
        var channel = GrpcChannel.ForAddress(
            factory.CreateClient().BaseAddress!,
            new GrpcChannelOptions { HttpHandler = factory.Server.CreateHandler() });
        _client = new UserService.UserServiceClient(channel);
    }

    [Fact]
    public async Task GetUser_ReturnsUser()
    {
        var response = await _client.GetUserAsync(new GetUserRequest { UserId = "123" });
        Assert.Equal("test@example.com", response.User.Email);
    }
}
```

```go
// Go — bufconn (in-memory listener)
func TestGetUser(t *testing.T) {
    client := setupTest(t) // Вся настройка в helper
    resp, err := client.GetUser(ctx, &pb.GetUserRequest{UserId: "123"})
    // ...
}
```

### Тестирование стримов

```go
func TestWatchUsers(t *testing.T) {
    client := setupTest(t)

    // Создаём несколько пользователей для генерации событий
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    stream, err := client.WatchUsers(ctx, &pb.WatchUsersRequest{})
    if err != nil {
        t.Fatalf("WatchUsers: %v", err)
    }

    // В отдельной горутине создаём пользователя (генерирует событие)
    go func() {
        time.Sleep(100 * time.Millisecond)
        _, _ = client.CreateUser(context.Background(), &pb.CreateUserRequest{
            Email:       "stream-test@example.com",
            DisplayName: "Stream Test",
        })
    }()

    // Читаем событие
    event, err := stream.Recv()
    if err != nil {
        t.Fatalf("Recv: %v", err)
    }

    if event.GetType() != pb.UserEvent_EVENT_TYPE_CREATED {
        t.Errorf("type = %s, want CREATED", event.GetType())
    }
}

func TestImportUsers(t *testing.T) {
    client := setupTest(t)

    stream, err := client.ImportUsers(context.Background())
    if err != nil {
        t.Fatalf("ImportUsers: %v", err)
    }

    // Отправляем 3 пользователей
    users := []struct{ email, name string }{
        {"a@test.com", "User A"},
        {"b@test.com", "User B"},
        {"c@test.com", "User C"},
    }

    for _, u := range users {
        if err := stream.Send(&pb.ImportUserRequest{
            Email:       u.email,
            DisplayName: u.name,
            Role:        pb.UserRole_USER_ROLE_MEMBER,
        }); err != nil {
            t.Fatalf("Send: %v", err)
        }
    }

    resp, err := stream.CloseAndRecv()
    if err != nil {
        t.Fatalf("CloseAndRecv: %v", err)
    }

    if resp.GetImportedCount() != 3 {
        t.Errorf("imported = %d, want 3", resp.GetImportedCount())
    }
}
```

### grpcurl для ручного тестирования

```bash
# Установка
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

# Список сервисов (нужен reflection)
grpcurl -plaintext localhost:50051 list

# Вызов метода с JSON
grpcurl -plaintext \
  -d '{"user_id": "123"}' \
  localhost:50051 myapp.user.v1.UserService/GetUser

# Вызов с metadata (заголовками)
grpcurl -plaintext \
  -H "Authorization: Bearer eyJhbG..." \
  -d '{"email": "new@test.com", "display_name": "New User"}' \
  localhost:50051 myapp.user.v1.UserService/CreateUser

# Server streaming — выводит все сообщения
grpcurl -plaintext \
  -d '{}' \
  localhost:50051 myapp.user.v1.UserService/WatchUsers

# Без reflection — указываем proto файл
grpcurl -plaintext \
  -import-path ./proto \
  -proto myapp/user/v1/user.proto \
  -d '{"user_id": "123"}' \
  localhost:50051 myapp.user.v1.UserService/GetUser
```

> 💡 **Для C# разработчиков**: `grpcurl` — это аналог **Postman** или **curl** для gRPC. В .NET мире также доступны **Postman** (поддерживает gRPC), **BloomRPC** и **grpcui** (веб-интерфейс). `grpcui` запускается как `grpcui -plaintext localhost:50051` и открывает браузер с интерактивным UI.

---

## Production Concerns

### Мониторинг с Prometheus

```go
import (
    grpcprom "github.com/grpc-ecosystem/go-grpc-middleware/providers/prometheus"
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

func main() {
    // Создаём метрики
    srvMetrics := grpcprom.NewServerMetrics(
        grpcprom.WithServerHandlingTimeHistogram(
            grpcprom.WithHistogramBuckets([]float64{0.001, 0.01, 0.1, 0.3, 0.6, 1, 3, 6, 9, 20}),
        ),
    )

    // Регистрируем в Prometheus
    reg := prometheus.NewRegistry()
    reg.MustRegister(srvMetrics)

    // gRPC сервер с метриками
    srv := grpc.NewServer(
        grpc.ChainUnaryInterceptor(
            srvMetrics.UnaryServerInterceptor(),
        ),
        grpc.ChainStreamInterceptor(
            srvMetrics.StreamServerInterceptor(),
        ),
    )

    pb.RegisterUserServiceServer(srv, NewUserServer(repo))
    srvMetrics.InitializeMetrics(srv) // Инициализация нулевых метрик

    // HTTP сервер для /metrics
    httpMux := http.NewServeMux()
    httpMux.Handle("/metrics", promhttp.HandlerFor(reg, promhttp.HandlerOpts{}))

    go http.ListenAndServe(":9090", httpMux)

    lis, _ := net.Listen("tcp", ":50051")
    srv.Serve(lis)
}
```

**Ключевые метрики**:

| Метрика | Тип | Описание |
|---------|-----|----------|
| `grpc_server_started_total` | Counter | Количество начатых RPC |
| `grpc_server_handled_total` | Counter | Количество завершённых RPC (с кодом) |
| `grpc_server_handling_seconds` | Histogram | Длительность обработки RPC |
| `grpc_server_msg_received_total` | Counter | Количество полученных сообщений (streaming) |
| `grpc_server_msg_sent_total` | Counter | Количество отправленных сообщений (streaming) |

**Полезные PromQL запросы**:
```promql
# Error rate по сервисам
sum(rate(grpc_server_handled_total{grpc_code!="OK"}[5m])) by (grpc_service, grpc_method)
/
sum(rate(grpc_server_handled_total[5m])) by (grpc_service, grpc_method)

# p99 latency
histogram_quantile(0.99, rate(grpc_server_handling_seconds_bucket[5m]))

# RPS по методам
sum(rate(grpc_server_started_total[1m])) by (grpc_method)
```

### OpenTelemetry Instrumentation

```go
import (
    "go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc"
    "go.opentelemetry.io/otel"
)

func main() {
    // Инициализация OTel (trace provider, exporter) — см. раздел 4.5

    // gRPC сервер с OTel
    srv := grpc.NewServer(
        grpc.StatsHandler(otelgrpc.NewServerHandler()),
    )

    // gRPC клиент с OTel
    conn, err := grpc.NewClient(
        "localhost:50051",
        grpc.WithStatsHandler(otelgrpc.NewClientHandler()),
        grpc.WithTransportCredentials(insecure.NewCredentials()),
    )
}
```

> 💡 `otelgrpc` использует `StatsHandler` вместо interceptors — это более точный механизм для сбора метрик и трейсов, работающий на уровне транспорта gRPC. Подробнее об OpenTelemetry — в [разделе 4.5](./05_observability.md).

### Load Balancing

```go
// Client-side load balancing — round robin
conn, err := grpc.NewClient(
    // dns:/// resolver — обнаруживает все IP адреса
    "dns:///user-service.default.svc.cluster.local:50051",
    grpc.WithDefaultServiceConfig(`{
        "loadBalancingConfig": [{"round_robin": {}}]
    }`),
    grpc.WithTransportCredentials(creds),
)

// Или pick_first (по умолчанию) — одно соединение
conn, err := grpc.NewClient(
    "dns:///user-service:50051",
    grpc.WithDefaultServiceConfig(`{
        "loadBalancingConfig": [{"pick_first": {"shuffleAddressList": true}}]
    }`),
    grpc.WithTransportCredentials(creds),
)
```

**Виды балансировки**:

| Тип | Описание | Когда использовать |
|-----|----------|-------------------|
| `pick_first` | Одно соединение к первому доступному адресу | По умолчанию, простые случаи |
| `round_robin` | Распределение по всем адресам | Kubernetes, множество реплик |
| Proxy (Envoy, Nginx) | Внешний балансировщик | Service mesh, сложная маршрутизация |

> 💡 **Для C# разработчиков**: В .NET `HttpClient` управляет DNS resolution и может использовать `SocketsHttpHandler` для connection pooling. В Go gRPC имеет собственную систему resolvers и balancers, независимую от `net/http`.

### Retry Policy и Keepalive

```go
// Retry policy через service config
serviceConfig := `{
    "methodConfig": [{
        "name": [{"service": "myapp.user.v1.UserService"}],
        "timeout": "5s",
        "retryPolicy": {
            "maxAttempts": 3,
            "initialBackoff": "0.1s",
            "maxBackoff": "1s",
            "backoffMultiplier": 2,
            "retryableStatusCodes": ["UNAVAILABLE", "RESOURCE_EXHAUSTED"]
        }
    }]
}`

conn, err := grpc.NewClient(
    "dns:///user-service:50051",
    grpc.WithDefaultServiceConfig(serviceConfig),
    grpc.WithTransportCredentials(creds),
)

// Keepalive — поддержание соединения
import "google.golang.org/grpc/keepalive"

// Серверная сторона
srv := grpc.NewServer(
    grpc.KeepaliveParams(keepalive.ServerParameters{
        MaxConnectionIdle:     15 * time.Minute, // Закрыть idle соединение
        MaxConnectionAge:      30 * time.Minute, // Максимальный возраст соединения
        MaxConnectionAgeGrace: 5 * time.Second,  // Время на завершение RPC после MaxConnectionAge
        Time:                  5 * time.Minute,  // Пинг каждые 5 минут
        Timeout:               1 * time.Second,  // Таймаут пинга
    }),
    grpc.KeepaliveEnforcementPolicy(keepalive.EnforcementPolicy{
        MinTime:             5 * time.Second, // Минимальный интервал пинга от клиента
        PermitWithoutStream: true,
    }),
)

// Клиентская сторона
conn, err := grpc.NewClient(
    "localhost:50051",
    grpc.WithKeepaliveParams(keepalive.ClientParameters{
        Time:                10 * time.Second,
        Timeout:             3 * time.Second,
        PermitWithoutStream: true,
    }),
    grpc.WithTransportCredentials(creds),
)
```

---

## Практические примеры

### Пример 1: CRUD User Service

Полный пример gRPC сервиса с interceptors, error handling и тестами.

<details>
<summary>Структура проекта</summary>

```
user-service/
├── proto/
│   └── user/v1/
│       └── user.proto
├── buf.yaml
├── buf.gen.yaml
├── gen/                    # Сгенерированный код
│   └── user/v1/
│       ├── user.pb.go
│       └── user_grpc.pb.go
├── internal/
│   ├── server/
│   │   └── user.go         # Реализация gRPC сервиса
│   └── repository/
│       ├── memory.go        # In-memory репозиторий
│       └── repository.go    # Интерфейс
├── cmd/
│   └── server/
│       └── main.go          # Точка входа
└── server_test.go           # Тесты
```
</details>

**Интерфейс репозитория**:

```go
// internal/repository/repository.go
package repository

import (
    "context"
    "time"
)

type User struct {
    ID          string
    Email       string
    DisplayName string
    Role        string
    CreatedAt   time.Time
    UpdatedAt   time.Time
}

type UserRepository interface {
    GetByID(ctx context.Context, id string) (*User, error)
    Create(ctx context.Context, user *User) (*User, error)
    Update(ctx context.Context, user *User) (*User, error)
    Delete(ctx context.Context, id string) error
    List(ctx context.Context, pageSize int, pageToken string) ([]*User, string, error)
}
```

**Реализация сервера** (ключевые части):

```go
// internal/server/user.go
package server

import (
    "context"
    "errors"

    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"
    "google.golang.org/protobuf/types/known/emptypb"
    "google.golang.org/protobuf/types/known/timestamppb"

    pb "github.com/myapp/gen/user/v1"
    "github.com/myapp/internal/repository"
)

type UserServer struct {
    pb.UnimplementedUserServiceServer
    repo repository.UserRepository
}

func NewUserServer(repo repository.UserRepository) *UserServer {
    return &UserServer{repo: repo}
}

func (s *UserServer) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.GetUserResponse, error) {
    if req.GetUserId() == "" {
        return nil, status.Error(codes.InvalidArgument, "user_id обязателен")
    }

    user, err := s.repo.GetByID(ctx, req.GetUserId())
    if err != nil {
        if errors.Is(err, repository.ErrNotFound) {
            return nil, status.Errorf(codes.NotFound, "пользователь %s не найден", req.GetUserId())
        }
        return nil, status.Errorf(codes.Internal, "ошибка получения пользователя: %v", err)
    }

    return &pb.GetUserResponse{User: toProto(user)}, nil
}

func (s *UserServer) CreateUser(ctx context.Context, req *pb.CreateUserRequest) (*pb.CreateUserResponse, error) {
    if req.GetEmail() == "" {
        return nil, status.Error(codes.InvalidArgument, "email обязателен")
    }

    user, err := s.repo.Create(ctx, &repository.User{
        Email:       req.GetEmail(),
        DisplayName: req.GetDisplayName(),
        Role:        req.GetRole().String(),
    })
    if err != nil {
        if errors.Is(err, repository.ErrDuplicate) {
            return nil, status.Errorf(codes.AlreadyExists, "email %s уже используется", req.GetEmail())
        }
        return nil, status.Errorf(codes.Internal, "ошибка создания: %v", err)
    }

    return &pb.CreateUserResponse{User: toProto(user)}, nil
}

func (s *UserServer) DeleteUser(ctx context.Context, req *pb.DeleteUserRequest) (*emptypb.Empty, error) {
    if req.GetUserId() == "" {
        return nil, status.Error(codes.InvalidArgument, "user_id обязателен")
    }

    if err := s.repo.Delete(ctx, req.GetUserId()); err != nil {
        if errors.Is(err, repository.ErrNotFound) {
            return nil, status.Errorf(codes.NotFound, "пользователь %s не найден", req.GetUserId())
        }
        return nil, status.Errorf(codes.Internal, "ошибка удаления: %v", err)
    }

    return &emptypb.Empty{}, nil
}

func (s *UserServer) ListUsers(ctx context.Context, req *pb.ListUsersRequest) (*pb.ListUsersResponse, error) {
    pageSize := int(req.GetPageSize())
    if pageSize <= 0 || pageSize > 100 {
        pageSize = 20
    }

    users, nextToken, err := s.repo.List(ctx, pageSize, req.GetPageToken())
    if err != nil {
        return nil, status.Errorf(codes.Internal, "ошибка списка: %v", err)
    }

    pbUsers := make([]*pb.User, 0, len(users))
    for _, u := range users {
        pbUsers = append(pbUsers, toProto(u))
    }

    return &pb.ListUsersResponse{
        Users:         pbUsers,
        NextPageToken: nextToken,
    }, nil
}

// Конвертация domain → proto
func toProto(u *repository.User) *pb.User {
    return &pb.User{
        Id:          u.ID,
        Email:       u.Email,
        DisplayName: u.DisplayName,
        CreatedAt:   timestamppb.New(u.CreatedAt),
        UpdatedAt:   timestamppb.New(u.UpdatedAt),
    }
}
```

**Точка входа с interceptors**:

```go
// cmd/server/main.go
package main

import (
    "log/slog"
    "net"
    "os"
    "os/signal"
    "syscall"

    "github.com/grpc-ecosystem/go-grpc-middleware/v2/interceptors/logging"
    "github.com/grpc-ecosystem/go-grpc-middleware/v2/interceptors/recovery"
    "google.golang.org/grpc"
    "google.golang.org/grpc/health"
    "google.golang.org/grpc/health/grpc_health_v1"
    "google.golang.org/grpc/reflection"

    pb "github.com/myapp/gen/user/v1"
    "github.com/myapp/internal/repository"
    "github.com/myapp/internal/server"
)

func main() {
    logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

    repo := repository.NewInMemory()
    userServer := server.NewUserServer(repo)

    srv := grpc.NewServer(
        grpc.ChainUnaryInterceptor(
            recovery.UnaryServerInterceptor(),
            logging.UnaryServerInterceptor(interceptorLogger(logger)),
        ),
        grpc.ChainStreamInterceptor(
            recovery.StreamServerInterceptor(),
            logging.StreamServerInterceptor(interceptorLogger(logger)),
        ),
    )

    pb.RegisterUserServiceServer(srv, userServer)

    // Health checking
    healthSrv := health.NewServer()
    grpc_health_v1.RegisterHealthServer(srv, healthSrv)
    healthSrv.SetServingStatus("", grpc_health_v1.HealthCheckResponse_SERVING)

    // Reflection (development only)
    reflection.Register(srv)

    lis, err := net.Listen("tcp", ":50051")
    if err != nil {
        logger.Error("не удалось слушать порт", "error", err)
        os.Exit(1)
    }

    go func() {
        logger.Info("gRPC сервер запущен", "addr", lis.Addr())
        if err := srv.Serve(lis); err != nil {
            logger.Error("ошибка сервера", "error", err)
        }
    }()

    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    logger.Info("завершение работы...")
    healthSrv.Shutdown()
    srv.GracefulStop()
    logger.Info("сервер остановлен")
}
```

### Пример 2: Real-Time стриминг цен

Server streaming для отправки обновлений цен в реальном времени. Типичный сценарий для финансовых приложений и маркетплейсов.

**Proto**:
```protobuf
service PriceService {
    // Server streaming — поток обновлений цен
    rpc WatchPrices(WatchPricesRequest) returns (stream PriceUpdate);
}

message WatchPricesRequest {
    repeated string symbols = 1;  // Список символов (например, ["BTC", "ETH"])
}

message PriceUpdate {
    string symbol = 1;
    double price = 2;
    double change_percent = 3;
    google.protobuf.Timestamp timestamp = 4;
}
```

**Сервер**:
```go
type priceServer struct {
    pb.UnimplementedPriceServiceServer
    priceFeed *PriceFeed // Источник данных
}

func (s *priceServer) WatchPrices(
    req *pb.WatchPricesRequest,
    stream grpc.ServerStreamingServer[pb.PriceUpdate],
) error {
    symbols := req.GetSymbols()
    if len(symbols) == 0 {
        return status.Error(codes.InvalidArgument, "укажите хотя бы один символ")
    }

    // Подписываемся на обновления цен
    updates := s.priceFeed.Subscribe(stream.Context(), symbols)

    for {
        select {
        case <-stream.Context().Done():
            return stream.Context().Err()

        case update, ok := <-updates:
            if !ok {
                return nil // Канал закрыт
            }

            if err := stream.Send(&pb.PriceUpdate{
                Symbol:        update.Symbol,
                Price:         update.Price,
                ChangePercent: update.ChangePercent,
                Timestamp:     timestamppb.Now(),
            }); err != nil {
                return err
            }
        }
    }
}
```

**Клиент с reconnection**:
```go
func watchPricesWithReconnect(ctx context.Context, client pb.PriceServiceClient, symbols []string) {
    backoff := 100 * time.Millisecond
    maxBackoff := 30 * time.Second

    for {
        err := watchPrices(ctx, client, symbols)
        if err == nil || ctx.Err() != nil {
            return // Завершение по контексту
        }

        slog.Warn("стрим прервался, переподключение...",
            "error", err,
            "backoff", backoff,
        )

        select {
        case <-ctx.Done():
            return
        case <-time.After(backoff):
        }

        // Exponential backoff с cap
        backoff = min(backoff*2, maxBackoff)
    }
}

func watchPrices(ctx context.Context, client pb.PriceServiceClient, symbols []string) error {
    stream, err := client.WatchPrices(ctx, &pb.WatchPricesRequest{
        Symbols: symbols,
    })
    if err != nil {
        return fmt.Errorf("не удалось начать watch: %w", err)
    }

    for {
        update, err := stream.Recv()
        if err == io.EOF {
            return nil
        }
        if err != nil {
            return fmt.Errorf("ошибка чтения: %w", err)
        }

        fmt.Printf("%s: $%.2f (%+.2f%%)\n",
            update.GetSymbol(),
            update.GetPrice(),
            update.GetChangePercent(),
        )
    }
}
```

### Пример 3: gRPC-Gateway + REST

Полный пример совмещения gRPC и REST API через gRPC-Gateway.

**Proto с HTTP annotations**:
```protobuf
syntax = "proto3";

package myapp.product.v1;

import "google/api/annotations.proto";
import "google/protobuf/timestamp.proto";
import "protoc-gen-openapiv2/options/annotations.proto";

option go_package = "github.com/myapp/gen/product/v1;productv1";

// Swagger metadata
option (grpc.gateway.protoc_gen_openapiv2.options.openapiv2_swagger) = {
    info: {
        title: "Product API"
        version: "1.0"
        description: "API для управления продуктами"
    }
    schemes: HTTPS
};

service ProductService {
    rpc GetProduct(GetProductRequest) returns (GetProductResponse) {
        option (google.api.http) = {
            get: "/api/v1/products/{product_id}"
        };
    }

    rpc ListProducts(ListProductsRequest) returns (ListProductsResponse) {
        option (google.api.http) = {
            get: "/api/v1/products"
        };
    }

    rpc CreateProduct(CreateProductRequest) returns (CreateProductResponse) {
        option (google.api.http) = {
            post: "/api/v1/products"
            body: "*"
        };
    }
}

message Product {
    string id = 1;
    string name = 2;
    string description = 3;
    int64 price_cents = 4;      // Цена в центах (не float!)
    string currency = 5;
    int32 stock = 6;
    google.protobuf.Timestamp created_at = 7;
}

message GetProductRequest { string product_id = 1; }
message GetProductResponse { Product product = 1; }

message ListProductsRequest {
    int32 page_size = 1;
    string page_token = 2;
    string category = 3;       // Фильтр по категории (query param)
}
message ListProductsResponse {
    repeated Product products = 1;
    string next_page_token = 2;
}

message CreateProductRequest {
    string name = 1;
    string description = 2;
    int64 price_cents = 3;
    string currency = 4;
    int32 stock = 5;
}
message CreateProductResponse { Product product = 1; }
```

**Сервер с gRPC + REST gateway**:
```go
package main

import (
    "context"
    "log/slog"
    "net"
    "net/http"
    "os"
    "os/signal"
    "syscall"

    "github.com/grpc-ecosystem/grpc-gateway/v2/runtime"
    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"
    "google.golang.org/grpc/reflection"
    "google.golang.org/protobuf/encoding/protojson"

    pb "github.com/myapp/gen/product/v1"
)

func main() {
    logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    // === gRPC сервер ===
    grpcLis, err := net.Listen("tcp", ":50051")
    if err != nil {
        logger.Error("не удалось слушать gRPC порт", "error", err)
        os.Exit(1)
    }

    grpcServer := grpc.NewServer()
    pb.RegisterProductServiceServer(grpcServer, NewProductServer(repo))
    reflection.Register(grpcServer)

    go func() {
        logger.Info("gRPC сервер запущен", "addr", ":50051")
        if err := grpcServer.Serve(grpcLis); err != nil {
            logger.Error("ошибка gRPC сервера", "error", err)
        }
    }()

    // === gRPC-Gateway (REST) ===
    gwMux := runtime.NewServeMux(
        runtime.WithMarshalerOption(runtime.MIMEWildcard, &runtime.JSONPb{
            MarshalOptions: protojson.MarshalOptions{
                UseProtoNames:   true,
                EmitUnpopulated: false,
            },
            UnmarshalOptions: protojson.UnmarshalOptions{
                DiscardUnknown: true,
            },
        }),
    )

    opts := []grpc.DialOption{
        grpc.WithTransportCredentials(insecure.NewCredentials()),
    }
    if err := pb.RegisterProductServiceHandlerFromEndpoint(ctx, gwMux, ":50051", opts); err != nil {
        logger.Error("не удалось зарегистрировать gateway", "error", err)
        os.Exit(1)
    }

    // HTTP mux для gateway + swagger + health
    httpMux := http.NewServeMux()
    httpMux.Handle("/", gwMux)
    httpMux.HandleFunc("/swagger.json", func(w http.ResponseWriter, r *http.Request) {
        http.ServeFile(w, r, "gen/openapiv2/product.swagger.json")
    })

    httpServer := &http.Server{Addr: ":8080", Handler: httpMux}

    go func() {
        logger.Info("REST gateway запущен", "addr", ":8080")
        if err := httpServer.ListenAndServe(); err != http.ErrServerClosed {
            logger.Error("ошибка HTTP сервера", "error", err)
        }
    }()

    // === Graceful shutdown ===
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    logger.Info("завершение работы...")
    httpServer.Shutdown(ctx)
    grpcServer.GracefulStop()
    logger.Info("серверы остановлены")
}
```

**Использование**:
```bash
# gRPC (через grpcurl)
grpcurl -plaintext \
  -d '{"product_id": "prod-1"}' \
  localhost:50051 myapp.product.v1.ProductService/GetProduct

# REST (через curl) — тот же сервис, другой протокол
curl http://localhost:8080/api/v1/products/prod-1

# Создание через REST
curl -X POST http://localhost:8080/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Go книга", "description": "Продвинутый Go", "price_cents": 4999, "currency": "USD", "stock": 100}'

# Список с фильтрацией (query params → proto fields)
curl "http://localhost:8080/api/v1/products?page_size=10&category=books"

# Swagger документация
curl http://localhost:8080/swagger.json
```

---
