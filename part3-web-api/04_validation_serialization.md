# Валидация и сериализация

---

## Введение

Сериализация и валидация — критически важные части любого API. В Go эти задачи решаются иначе, чем в C#: нет встроенных Data Annotations, нет System.Text.Json с source generators по умолчанию.

> 💡 **Для C# разработчиков**: Вместо `[Required]`, `[MaxLength]` используется библиотека validator со struct tags. Вместо System.Text.Json — `encoding/json` или альтернативы.

### Что вы узнаете

- Стандартный `encoding/json` и его ограничения
- json.Number и потоковая обработка больших JSON
- Быстрые альтернативы: easyjson, sonic, go-json
- gjson для быстрого извлечения полей без парсинга структуры
- Валидация с go-playground/validator
- Паттерны Request/Response DTO
- Protocol Buffers для высокопроизводительной сериализации

---

## JSON в Go

### encoding/json: основы

```go
import "encoding/json"

type User struct {
    ID        int       `json:"id"`
    Email     string    `json:"email"`
    Name      string    `json:"name"`
    CreatedAt time.Time `json:"created_at"`
}

// Marshal (Go → JSON)
func main() {
    user := User{
        ID:        1,
        Email:     "user@example.com",
        Name:      "John Doe",
        CreatedAt: time.Now(),
    }

    // В []byte
    data, err := json.Marshal(user)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println(string(data))
    // {"id":1,"email":"user@example.com","name":"John Doe","created_at":"2024-01-15T10:30:00Z"}

    // С отступами (для отладки)
    prettyData, _ := json.MarshalIndent(user, "", "  ")
    fmt.Println(string(prettyData))
}

// Unmarshal (JSON → Go)
func parseUser(jsonData []byte) (*User, error) {
    var user User
    if err := json.Unmarshal(jsonData, &user); err != nil {
        return nil, err
    }
    return &user, nil
}

// Encoder/Decoder для потоков (io.Reader/io.Writer)
func writeJSON(w http.ResponseWriter, data any) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(data)
}

func readJSON(r *http.Request, dst any) error {
    return json.NewDecoder(r.Body).Decode(dst)
}
```

### Struct Tags

```go
type User struct {
    // Базовые теги
    ID   int    `json:"id"`           // Переименование поля
    Name string `json:"name"`

    // omitempty — пропустить если zero value
    Email    string  `json:"email,omitempty"`
    Nickname *string `json:"nickname,omitempty"` // nil пропускается

    // Игнорировать поле
    Password string `json:"-"`

    // string — числа как строки (для JavaScript BigInt)
    Balance int64 `json:"balance,string"`

    // Вложенные структуры
    Address Address `json:"address"`

    // Inline embedding
    Metadata `json:",inline"` // Поля Metadata на верхнем уровне
}

type Address struct {
    City    string `json:"city"`
    Country string `json:"country"`
}

type Metadata struct {
    CreatedAt time.Time `json:"created_at"`
    UpdatedAt time.Time `json:"updated_at"`
}
```

### Сравнение с C#

| C# (System.Text.Json) | Go (encoding/json) |
|-----------------------|-------------------|
| `[JsonPropertyName("id")]` | `json:"id"` |
| `[JsonIgnore]` | `json:"-"` |
| `[JsonIgnore(Condition = WhenWritingNull)]` | `json:",omitempty"` |
| `JsonSerializer.Serialize()` | `json.Marshal()` |
| `JsonSerializer.Deserialize<T>()` | `json.Unmarshal()` |
| Nullable types | Pointers + omitempty |

### Custom Marshal/Unmarshal

```go
// Кастомная сериализация для enum
type Status int

const (
    StatusPending Status = iota
    StatusActive
    StatusBlocked
)

var statusNames = map[Status]string{
    StatusPending: "pending",
    StatusActive:  "active",
    StatusBlocked: "blocked",
}

var statusValues = map[string]Status{
    "pending": StatusPending,
    "active":  StatusActive,
    "blocked": StatusBlocked,
}

func (s Status) MarshalJSON() ([]byte, error) {
    name, ok := statusNames[s]
    if !ok {
        return nil, fmt.Errorf("unknown status: %d", s)
    }
    return json.Marshal(name)
}

func (s *Status) UnmarshalJSON(data []byte) error {
    var name string
    if err := json.Unmarshal(data, &name); err != nil {
        return err
    }

    status, ok := statusValues[name]
    if !ok {
        return fmt.Errorf("unknown status: %s", name)
    }
    *s = status
    return nil
}

// Использование
type User struct {
    ID     int    `json:"id"`
    Status Status `json:"status"`
}

// {"id": 1, "status": "active"}
```

```go
// Кастомный формат времени
type CustomTime time.Time

const customTimeLayout = "2006-01-02"

func (t CustomTime) MarshalJSON() ([]byte, error) {
    return json.Marshal(time.Time(t).Format(customTimeLayout))
}

func (t *CustomTime) UnmarshalJSON(data []byte) error {
    var s string
    if err := json.Unmarshal(data, &s); err != nil {
        return err
    }

    parsed, err := time.Parse(customTimeLayout, s)
    if err != nil {
        return err
    }
    *t = CustomTime(parsed)
    return nil
}

type Event struct {
    Name string     `json:"name"`
    Date CustomTime `json:"date"`
}

// {"name": "Conference", "date": "2024-06-15"}
```

### Работа с динамическим JSON

```go
// map[string]any для произвольного JSON
func parseDynamicJSON(data []byte) {
    var result map[string]any
    json.Unmarshal(data, &result)

    // Доступ к полям с type assertion
    if name, ok := result["name"].(string); ok {
        fmt.Println("Name:", name)
    }

    // Вложенные объекты
    if address, ok := result["address"].(map[string]any); ok {
        if city, ok := address["city"].(string); ok {
            fmt.Println("City:", city)
        }
    }
}

// json.RawMessage для отложенного парсинга
type Response struct {
    Type    string          `json:"type"`
    Payload json.RawMessage `json:"payload"` // Парсим позже
}

func handleResponse(data []byte) error {
    var resp Response
    if err := json.Unmarshal(data, &resp); err != nil {
        return err
    }

    switch resp.Type {
    case "user":
        var user User
        return json.Unmarshal(resp.Payload, &user)
    case "order":
        var order Order
        return json.Unmarshal(resp.Payload, &order)
    }
    return nil
}
```

### json.Number: точность для больших чисел

> 💡 **Для C# разработчиков**: `System.Text.Json` хранит числа в оригинальном виде через `JsonElement.GetInt64()`. В Go `encoding/json` по умолчанию конвертирует все числа в `float64` при десериализации в `any`, что ведёт к потере точности для больших `int64`.

`float64` имеет 53 бита мантиссы — точно хранит целые числа до 2^53 (≈9·10^15). Twitter ID, bank transaction ID, UUID-подобные `int64` легко превышают этот порог.

```go
// ❌ Ловушка: все числа в map[string]any → float64
data := []byte(`{"id":9223372036854775807}`) // math.MaxInt64

var result map[string]any
json.Unmarshal(data, &result)

id := result["id"].(float64)
fmt.Println(int64(id)) // 9223372036854775808 — НЕВЕРНО! (off-by-one)
```

```go
// ✅ Решение: json.Decoder.UseNumber()
dec := json.NewDecoder(bytes.NewReader(data))
dec.UseNumber() // числа остаются как строки — json.Number

var result map[string]any
dec.Decode(&result)

num := result["id"].(json.Number)
id, err := num.Int64()   // 9223372036854775807 — верно
f64, _ := num.Float64()  // → float64
str := num.String()      // → "9223372036854775807"
```

```go
// json.Number в структурах — явное поле
type Payload struct {
    ID      json.Number `json:"id"`
    Balance json.Number `json:"balance"`
    Name    string      `json:"name"`
}

var p Payload
json.Unmarshal(data, &p)
userID, _ := p.ID.Int64()
```

**Сравнение с C#:**

```csharp
// System.Text.Json — точные типы из коробки
using var doc = JsonDocument.Parse(json);
var id = doc.RootElement.GetProperty("id").GetInt64(); // точно, без float64

// Newtonsoft.Json — аналог json.Number
var token = JObject.Parse(json)["id"];
var id = token.Value<long>(); // точно
```

**Когда использовать:**
- Fintech: ID транзакций, номера счетов
- Социальные сети: user ID > 2^53 (Twitter/X использует 64-битные ID)
- Интеграция с внешними API без строгой схемы
- Обработка webhook-payload с числовыми ID

---

### Потоковая обработка больших JSON (Decoder.Token())

> 💡 **Для C# разработчиков**: Аналог `Utf8JsonReader` (System.Text.Json) и `JsonTextReader` (Newtonsoft.Json) — ручной low-level парсинг без загрузки всего документа в память.

**Когда использовать streaming:**
- Файлы > 10 MB
- Неограниченные массивы (пагинация недоступна)
- NDJSON-потоки (одна JSON-строка на событие)
- Ограниченная память (контейнеры с лимитом)

```go
// Паттерн: итерация по массиву без загрузки всего в память
func processOrdersStream(r io.Reader) (int, error) {
    dec := json.NewDecoder(r)

    // Читаем '[' — начало массива
    tok, err := dec.Token()
    if err != nil {
        return 0, fmt.Errorf("read open bracket: %w", err)
    }
    if tok != json.Delim('[') {
        return 0, fmt.Errorf("expected '[', got %v", tok)
    }

    count := 0
    for dec.More() { // есть ещё элементы?
        var order Order
        if err := dec.Decode(&order); err != nil {
            return count, fmt.Errorf("decode order %d: %w", count, err)
        }
        // Обрабатываем немедленно — предыдущий заказ уже GC-eligible
        if err := processOrder(order); err != nil {
            return count, err
        }
        count++
    }

    // Читаем ']' — конец массива
    if _, err := dec.Token(); err != nil {
        return count, fmt.Errorf("read close bracket: %w", err)
    }
    return count, nil
}
```

```go
// NDJSON (Newline-Delimited JSON) — популярный формат для логов и data export
// {"event":"click","user_id":1,"ts":1709812345}
// {"event":"view","user_id":2,"ts":1709812346}
func processNDJSON(r io.Reader) error {
    dec := json.NewDecoder(r)
    for dec.More() {
        var event AnalyticsEvent
        if err := dec.Decode(&event); err != nil {
            return fmt.Errorf("decode event: %w", err)
        }
        handleEvent(event)
    }
    return nil
}
```

**Сравнение подходов:**

| Подход | Память | Когда |
|--------|--------|-------|
| `json.Unmarshal(data, &v)` | Весь JSON + структура | Файлы < 1 MB |
| `Decoder.Decode(&v)` | Буфер + структура | HTTP body, io.Reader |
| `Decoder.Token()` | Минимум (один объект) | Файлы > 10 MB, NDJSON |

```csharp
// C# аналог — JsonSerializer.DeserializeAsyncEnumerable
await foreach (var order in JsonSerializer.DeserializeAsyncEnumerable<Order>(stream))
{
    await ProcessOrder(order);
}

// C# низкоуровневый — Utf8JsonReader
var reader = new Utf8JsonReader(jsonBytes);
while (reader.Read())
{
    if (reader.TokenType == JsonTokenType.StartObject) { /* ... */ }
}
```

---

## Быстрые JSON библиотеки

Стандартный `encoding/json` использует reflection, что медленно. Для production рекомендуются альтернативы.

### easyjson

[easyjson](https://github.com/mailru/easyjson) генерирует код сериализации без reflection.

```bash
go install github.com/mailru/easyjson/...@latest
```

```go
//go:generate easyjson -all user.go

package models

type User struct {
    ID    int    `json:"id"`
    Email string `json:"email"`
    Name  string `json:"name"`
}
```

```bash
go generate ./...
```

easyjson сгенерирует `user_easyjson.go`:

```go
// Сгенерированные методы
func (v *User) MarshalJSON() ([]byte, error) { ... }
func (v *User) UnmarshalJSON(data []byte) error { ... }

// Быстрые методы (без []byte allocation)
func (v *User) MarshalEasyJSON(w *jwriter.Writer) { ... }
func (v *User) UnmarshalEasyJSON(l *jlexer.Lexer) { ... }
```

### sonic

[sonic](https://github.com/bytedance/sonic) — JIT-компилируемая библиотека от ByteDance (TikTok).

```go
import "github.com/bytedance/sonic"

// Drop-in replacement для encoding/json
data, err := sonic.Marshal(user)
err = sonic.Unmarshal(data, &user)

// Streaming
sonic.NewEncoder(w).Encode(user)
sonic.NewDecoder(r).Decode(&user)

// Конфигурация
api := sonic.Config{
    EscapeHTML:       false,
    SortMapKeys:      false,
    UseInt64:         true,
    CopyString:       true,
}.Froze()

data, _ = api.Marshal(user)
```

### go-json

[go-json](https://github.com/goccy/go-json) — drop-in замена без кодогенерации. Единственная быстрая библиотека, которая работает на всех платформах включая 32-bit и WASM.

```go
import "github.com/goccy/go-json"

// API идентичен encoding/json — замена одним import
data, err := json.Marshal(user)
err = json.Unmarshal(data, &user)

// Streaming — то же
json.NewEncoder(w).Encode(user)
json.NewDecoder(r).Decode(&user)
```

**Преимущества перед sonic и easyjson:**
- Не требует кодогенерации (в отличие от easyjson)
- Работает на arm32, MIPS, WASM (sonic требует x86/arm64)
- Активно используется в production: Grafana, consul, многие k8s-утилиты

### Benchmarks

| Библиотека | Marshal (ns/op) | Unmarshal (ns/op) | Allocs | Кодогенерация | Платформы |
|------------|-----------------|-------------------|--------|---------------|-----------|
| encoding/json | 1500 | 2800 | 8 | Нет | Все |
| go-json | 650 | 1100 | 3 | Нет | Все |
| easyjson | 300 | 450 | 1 | Да | Все |
| sonic | 200 | 350 | 1 | Нет (JIT) | x86/arm64 |

> 💡 **Выбор библиотеки:**
> - **encoding/json** — дефолт, нет требований к производительности
> - **go-json** — нужна скорость без codegen, любые платформы
> - **easyjson** — максимальная скорость + кросс-платформенность, OK с codegen
> - **sonic** — абсолютный максимум на x86/arm64 (ByteDance, TikTok backend)

### gjson — быстрое извлечение полей

[gjson](https://github.com/tidwall/gjson) — парсит только нужные поля, не декодирует весь JSON. Аналог `JObject.SelectToken()` / JsonPath в Newtonsoft.Json.

```go
import "github.com/tidwall/gjson"

payload := `{
    "user": {
        "id": 12345,
        "name": "Alice",
        "roles": ["admin", "editor"],
        "address": {"city": "Moscow"}
    },
    "event": "login",
    "timestamp": 1709812345
}`

// Точечная нотация — как JPath
name := gjson.Get(payload, "user.name").String()         // "Alice"
id   := gjson.Get(payload, "user.id").Int()              // 12345
city := gjson.Get(payload, "user.address.city").String() // "Moscow"

// Массивы
role0 := gjson.Get(payload, "user.roles.0").String() // "admin"
count := gjson.Get(payload, "user.roles.#").Int()    // 2

// Множественное извлечение — один проход по JSON
results := gjson.GetMany(payload, "user.id", "user.name", "event")
// results[0].Int()    == 12345
// results[1].String() == "Alice"
// results[2].String() == "login"

// Итерация по массиву
gjson.Get(payload, "user.roles").ForEach(func(_, val gjson.Result) bool {
    fmt.Println(val.String()) // "admin", "editor"
    return true               // продолжить итерацию
})
```

```csharp
// C# Newtonsoft.Json — ближайший аналог
var obj = JObject.Parse(json);
var name = obj.SelectToken("user.name")?.Value<string>(); // "Alice"

// C# System.Text.Json — нет SelectToken, только путь через GetProperty
using var doc = JsonDocument.Parse(json);
var name = doc.RootElement
    .GetProperty("user")
    .GetProperty("name")
    .GetString(); // "Alice"
```

**Когда уместно:**
- Middleware: извлечь `user_id` для логирования/трейсинга до полного парсинга
- Webhook: обработать payload с переменной схемой без определения struct
- Feature flags: быстро прочитать значение из config-JSON
- Логирование: вытащить несколько полей из большого события

**Когда не использовать:**
- Полная десериализация в struct (используйте encoding/json / easyjson)
- Изменение JSON (используйте [sjson](https://github.com/tidwall/sjson) — сиблинг-библиотека)
- Схемная валидация

---

## Валидация: go-playground/validator

[go-playground/validator](https://github.com/go-playground/validator) — стандартная библиотека валидации в Go.

```bash
go get github.com/go-playground/validator/v10
```

### Базовые валидаторы

```go
import (
    "github.com/go-playground/validator/v10"
)

type CreateUserRequest struct {
    // required — обязательное поле
    Email string `json:"email" validate:"required,email"`

    // min/max — длина строки
    Name string `json:"name" validate:"required,min=2,max=100"`

    // gte/lte — числовые ограничения
    Age int `json:"age" validate:"gte=18,lte=120"`

    // oneof — enum
    Role string `json:"role" validate:"required,oneof=user admin moderator"`

    // len — точная длина
    CountryCode string `json:"country_code" validate:"len=2"`

    // url, uri
    Website string `json:"website" validate:"omitempty,url"`

    // uuid
    ReferralCode string `json:"referral_code" validate:"omitempty,uuid"`

    // Регулярное выражение
    Username string `json:"username" validate:"required,alphanum,min=3,max=20"`

    // Пароль: минимум 8 символов, содержит цифру
    Password string `json:"password" validate:"required,min=8,containsany=0123456789"`
}

func main() {
    validate := validator.New()

    req := CreateUserRequest{
        Email:    "invalid-email",
        Name:     "J", // Слишком короткое
        Age:      15,  // Меньше 18
        Role:     "superadmin", // Не в списке
    }

    err := validate.Struct(req)
    if err != nil {
        for _, e := range err.(validator.ValidationErrors) {
            fmt.Printf("Field: %s, Tag: %s, Value: %v\n",
                e.Field(), e.Tag(), e.Value())
        }
    }
}
```

### Полный список популярных тегов

| Тег | Описание | Пример |
|-----|----------|--------|
| `required` | Обязательное поле | `validate:"required"` |
| `email` | Email формат | `validate:"email"` |
| `url` | URL формат | `validate:"url"` |
| `uuid` | UUID формат | `validate:"uuid"` |
| `min` | Минимальная длина/значение | `validate:"min=3"` |
| `max` | Максимальная длина/значение | `validate:"max=100"` |
| `len` | Точная длина | `validate:"len=10"` |
| `gte` | >= (числа) | `validate:"gte=0"` |
| `lte` | <= (числа) | `validate:"lte=100"` |
| `oneof` | Одно из значений | `validate:"oneof=a b c"` |
| `alphanum` | Только буквы и цифры | `validate:"alphanum"` |
| `numeric` | Только цифры | `validate:"numeric"` |
| `omitempty` | Пропустить если пустое | `validate:"omitempty,email"` |
| `dive` | Валидация элементов слайса | `validate:"dive,required"` |
| `eqfield` | Равно другому полю | `validate:"eqfield=Password"` |

### Кастомные валидаторы

```go
import (
    "regexp"
    "github.com/go-playground/validator/v10"
)

// Валидатор для российского телефона
func validateRuPhone(fl validator.FieldLevel) bool {
    phone := fl.Field().String()
    matched, _ := regexp.MatchString(`^\+7[0-9]{10}$`, phone)
    return matched
}

// Валидатор для slug
func validateSlug(fl validator.FieldLevel) bool {
    slug := fl.Field().String()
    matched, _ := regexp.MatchString(`^[a-z0-9]+(?:-[a-z0-9]+)*$`, slug)
    return matched
}

// Структурный валидатор (сравнение полей)
func validatePasswordMatch(sl validator.StructLevel) {
    req := sl.Current().Interface().(CreateUserRequest)
    if req.Password != req.ConfirmPassword {
        sl.ReportError(req.ConfirmPassword, "ConfirmPassword", "confirm_password", "eqfield", "Password")
    }
}

func main() {
    validate := validator.New()

    // Регистрация кастомных валидаторов
    validate.RegisterValidation("ruphone", validateRuPhone)
    validate.RegisterValidation("slug", validateSlug)
    validate.RegisterStructValidation(validatePasswordMatch, CreateUserRequest{})

    // Использование
    type Profile struct {
        Phone string `validate:"required,ruphone"`
        Slug  string `validate:"required,slug"`
    }
}
```

### Вложенные структуры

```go
type Address struct {
    Street  string `json:"street" validate:"required,min=5"`
    City    string `json:"city" validate:"required"`
    ZipCode string `json:"zip_code" validate:"required,len=6,numeric"`
}

type CreateOrderRequest struct {
    // Вложенная структура — валидируется автоматически
    ShippingAddress Address `json:"shipping_address" validate:"required"`

    // Слайс структур
    Items []OrderItem `json:"items" validate:"required,min=1,dive"`
}

type OrderItem struct {
    ProductID int `json:"product_id" validate:"required,gt=0"`
    Quantity  int `json:"quantity" validate:"required,gte=1,lte=100"`
}

// `dive` — валидирует каждый элемент слайса
```

### Локализация ошибок

```go
import (
    "github.com/go-playground/validator/v10"
    "github.com/go-playground/locales/ru"
    ut "github.com/go-playground/universal-translator"
    ru_translations "github.com/go-playground/validator/v10/translations/ru"
)

func NewValidator() (*validator.Validate, ut.Translator) {
    validate := validator.New()

    // Русская локаль
    ruLocale := ru.New()
    uni := ut.New(ruLocale, ruLocale)
    trans, _ := uni.GetTranslator("ru")

    // Регистрация переводов
    ru_translations.RegisterDefaultTranslations(validate, trans)

    return validate, trans
}

func ValidateRequest(validate *validator.Validate, trans ut.Translator, req any) map[string]string {
    err := validate.Struct(req)
    if err == nil {
        return nil
    }

    errors := make(map[string]string)
    for _, e := range err.(validator.ValidationErrors) {
        errors[e.Field()] = e.Translate(trans)
    }
    return errors
}

// Результат:
// {
//   "Email": "Email должен быть действительным email адресом",
//   "Name": "Name должен содержать минимум 2 символов"
// }
```

### Сравнение с C# Data Annotations

| C# | Go (validator) |
|----|----------------|
| `[Required]` | `validate:"required"` |
| `[EmailAddress]` | `validate:"email"` |
| `[StringLength(100)]` | `validate:"max=100"` |
| `[MinLength(3)]` | `validate:"min=3"` |
| `[Range(1, 100)]` | `validate:"gte=1,lte=100"` |
| `[RegularExpression]` | `validate:"regex=..."` |
| `[Compare("Password")]` | `validate:"eqfield=Password"` |
| Custom `IValidatableObject` | `RegisterStructValidation` |

---

## Request/Response DTO

Разделение моделей API и доменных моделей.

```go
// internal/handler/dto/user.go
package dto

import "time"

// Request DTOs
type CreateUserRequest struct {
    Email    string `json:"email" validate:"required,email"`
    Name     string `json:"name" validate:"required,min=2,max=100"`
    Password string `json:"password" validate:"required,min=8"`
}

type UpdateUserRequest struct {
    Name *string `json:"name" validate:"omitempty,min=2,max=100"`
    Bio  *string `json:"bio" validate:"omitempty,max=500"`
}

// Response DTOs
type UserResponse struct {
    ID        int       `json:"id"`
    Email     string    `json:"email"`
    Name      string    `json:"name"`
    Bio       string    `json:"bio,omitempty"`
    CreatedAt time.Time `json:"created_at"`
}

type UsersListResponse struct {
    Users      []UserResponse `json:"users"`
    TotalCount int            `json:"total_count"`
    Page       int            `json:"page"`
    PageSize   int            `json:"page_size"`
}

type ErrorResponse struct {
    Error   string            `json:"error"`
    Details map[string]string `json:"details,omitempty"`
}

// Маппинг Domain → DTO
func UserToResponse(user *domain.User) UserResponse {
    return UserResponse{
        ID:        user.ID,
        Email:     user.Email,
        Name:      user.Name,
        Bio:       user.Bio,
        CreatedAt: user.CreatedAt,
    }
}

func UsersToResponse(users []domain.User) []UserResponse {
    result := make([]UserResponse, len(users))
    for i, u := range users {
        result[i] = UserToResponse(&u)
    }
    return result
}
```

```go
// internal/handler/user_handler.go
package handler

import (
    "encoding/json"
    "net/http"

    "github.com/go-playground/validator/v10"
    "myapp/internal/handler/dto"
)

type UserHandler struct {
    service  *usecase.UserService
    validate *validator.Validate
}

func (h *UserHandler) Create(w http.ResponseWriter, r *http.Request) {
    var req dto.CreateUserRequest

    // Декодирование
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        respondError(w, http.StatusBadRequest, "Invalid JSON", nil)
        return
    }

    // Валидация
    if err := h.validate.Struct(req); err != nil {
        errors := make(map[string]string)
        for _, e := range err.(validator.ValidationErrors) {
            errors[e.Field()] = e.Tag()
        }
        respondError(w, http.StatusBadRequest, "Validation failed", errors)
        return
    }

    // Бизнес-логика
    user, err := h.service.CreateUser(r.Context(), usecase.CreateUserInput{
        Email:    req.Email,
        Name:     req.Name,
        Password: req.Password,
    })
    if err != nil {
        handleServiceError(w, err)
        return
    }

    // Ответ
    respondJSON(w, http.StatusCreated, dto.UserToResponse(user))
}

func respondJSON(w http.ResponseWriter, status int, data any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(data)
}

func respondError(w http.ResponseWriter, status int, message string, details map[string]string) {
    respondJSON(w, status, dto.ErrorResponse{
        Error:   message,
        Details: details,
    })
}
```

---

## Protocol Buffers

Protocol Buffers (protobuf) — бинарный формат сериализации от Google. Быстрее и компактнее JSON.

### Основы protobuf

```protobuf
// api/proto/user.proto
syntax = "proto3";

package api.v1;

option go_package = "myapp/internal/pb";

import "google/protobuf/timestamp.proto";

message User {
  int32 id = 1;
  string email = 2;
  string name = 3;
  UserStatus status = 4;
  google.protobuf.Timestamp created_at = 5;
}

enum UserStatus {
  USER_STATUS_UNSPECIFIED = 0;
  USER_STATUS_ACTIVE = 1;
  USER_STATUS_BLOCKED = 2;
}

message CreateUserRequest {
  string email = 1;
  string name = 2;
  string password = 3;
}

message CreateUserResponse {
  User user = 1;
}

message GetUserRequest {
  int32 id = 1;
}

message ListUsersRequest {
  int32 page = 1;
  int32 page_size = 2;
}

message ListUsersResponse {
  repeated User users = 1;
  int32 total_count = 2;
}
```

### Генерация Go кода

```bash
# Установка protoc
# macOS: brew install protobuf
# Linux: apt install protobuf-compiler

# Установка Go плагинов
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# Генерация
protoc --go_out=. --go_opt=paths=source_relative \
       --go-grpc_out=. --go-grpc_opt=paths=source_relative \
       api/proto/user.proto
```

Сгенерированный код:

```go
// internal/pb/user.pb.go
type User struct {
    Id        int32                  `protobuf:"varint,1,opt,name=id,proto3" json:"id,omitempty"`
    Email     string                 `protobuf:"bytes,2,opt,name=email,proto3" json:"email,omitempty"`
    Name      string                 `protobuf:"bytes,3,opt,name=name,proto3" json:"name,omitempty"`
    Status    UserStatus             `protobuf:"varint,4,opt,name=status,proto3,enum=api.v1.UserStatus" json:"status,omitempty"`
    CreatedAt *timestamppb.Timestamp `protobuf:"bytes,5,opt,name=created_at,json=createdAt,proto3" json:"created_at,omitempty"`
}

// Методы сериализации генерируются автоматически
func (x *User) ProtoReflect() protoreflect.Message { ... }
func (x *User) GetId() int32 { ... }
func (x *User) GetEmail() string { ... }
```

### Использование

```go
import (
    "google.golang.org/protobuf/proto"
    "myapp/internal/pb"
)

func main() {
    user := &pb.User{
        Id:    1,
        Email: "user@example.com",
        Name:  "John Doe",
        Status: pb.UserStatus_USER_STATUS_ACTIVE,
    }

    // Сериализация (Go → bytes)
    data, err := proto.Marshal(user)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Protobuf size: %d bytes\n", len(data))

    // Десериализация (bytes → Go)
    var parsed pb.User
    if err := proto.Unmarshal(data, &parsed); err != nil {
        log.Fatal(err)
    }
    fmt.Printf("User: %+v\n", parsed)
}
```

### Сравнение с JSON

| Аспект | JSON | Protobuf |
|--------|------|----------|
| **Размер** | ~100 bytes | ~30 bytes |
| **Скорость** | Медленно (text parsing) | Быстро (binary) |
| **Schema** | Нет (dynamic) | Строгая (.proto) |
| **Читаемость** | Человекочитаемый | Бинарный |
| **Эволюция** | Хрупкая | Backward/Forward compatible |
| **Использование** | Public API, REST | Internal API, gRPC, storage |

```go
// Benchmark сравнение
// JSON:     Marshal: 1500ns, Size: 89 bytes
// Protobuf: Marshal: 150ns,  Size: 28 bytes
// Разница: ~10x быстрее, ~3x компактнее
```

---

## encoding/json/v2 и производительность io.ReadAll (Go 1.25-1.26)

### encoding/json/v2 — статус на март 2026

> 💡 **Для C# разработчиков**: Аналог миграции с `Newtonsoft.Json` на `System.Text.Json` — новый, более быстрый и строгий JSON API.

**Два способа использования v2:**

1. **Standalone пакет** `github.com/go-json-experiment/json` — доступен прямо сейчас, без флагов
2. **В stdlib** — `GOEXPERIMENT=jsonv2` в Go 1.25/1.26, пока нестабилен в стандартной библиотеке

```bash
# Установка standalone пакета (март 2026)
go get github.com/go-json-experiment/json
```

```go
import jsonv2 "github.com/go-json-experiment/json"

type User struct {
    Name  string `json:"name"`
    Email string `json:"email"`
    Age   int    `json:"age"`
}

user := User{Name: "Alice", Email: "alice@example.com", Age: 30}

// Marshal — совместимый API
data, err := jsonv2.Marshal(user)

// Unmarshal — строже по умолчанию (unknown fields → ошибка)
var parsed User
if err := jsonv2.Unmarshal(data, &parsed); err != nil {
    return err
}

// Разрешить unknown fields явно
if err := jsonv2.UnmarshalOptions{RejectUnknownMembers: false}.Unmarshal(data, &parsed); err != nil {
    return err
}
```

**Новые теги v2:**

```go
type Config struct {
    // omitzero — omit если IsZero() возвращает true (или == zero value)
    // Работает без указателя, в отличие от omitempty для struct
    Timeout time.Duration `json:"timeout,omitzero"`

    // format — подсказка формата для кастомных типов
    StartDate time.Time `json:"start_date,format:date"`        // "2024-01-15"
    CreatedAt time.Time `json:"created_at,format:RFC3339Nano"` // полный timestamp

    // unknown — поле для захвата неизвестных полей (вместо map или RawMessage)
    Extra jsonv2.RawValue `json:",unknown"`
}

type Response struct {
    Status string `json:"status"`
    // Все неизвестные поля попадут в Extra
    Extra  map[string]jsonv2.RawValue `json:",unknown"`
}
```

**Ключевые отличия от v1:**

```go
// v1: тихо игнорирует unknown fields
json.Unmarshal([]byte(`{"name":"Alice","newField":"value"}`), &User{})
// OK, newField проигнорирован

// v2: ошибка при unknown fields по умолчанию — безопаснее для API
jsonv2.Unmarshal([]byte(`{"name":"Alice","newField":"value"}`), &User{})
// Error: unknown name "newField"

// v2: различие null и absent field
// null → pointer = nil
// absent → pointer не тронут (сохраняет предыдущее значение)
```

**Benchmarks v1 vs v2:**

| Операция | json v1 | json v2 | Улучшение |
|----------|---------|---------|-----------|
| Marshal 1KB | 1500 ns | 900 ns | ~1.7x |
| Unmarshal 1KB | 2800 ns | 1400 ns | ~2x |
| Allocations | 8 | 4 | ~2x меньше |

**Рекомендация (март 2026):**

| Сценарий | Выбор |
|----------|-------|
| Стабильный production | encoding/json + easyjson/sonic |
| Новый сервис, можно обновить зависимость | `github.com/go-json-experiment/json` |
| Нужен `omitzero`, `format`, `unknown` тег | `github.com/go-json-experiment/json` |
| Ждёте стабилизации в stdlib | Следите за Go 1.27+ |

```go
// Сейчас (стабильно, без кодогенерации)
import "encoding/json"

// Уже можно (standalone, API может корректироваться)
import jsonv2 "github.com/go-json-experiment/json"

// Будущее (в stdlib, ожидается Go 1.27+)
// import "encoding/json/v2"
```

---

### io.ReadAll — 2x быстрее (Go 1.26)

> 💡 Это **бесплатное улучшение** — никакого изменения кода не требуется.

Go 1.26 оптимизировал `io.ReadAll` — функцию для чтения всего содержимого Reader:
- **~2x быстрее** в типичных сценариях
- **~50% меньше аллокаций** за счёт более умного предвыделения буфера

```go
// Ваш существующий код работает быстрее «бесплатно»
func readRequestBody(r *http.Request) ([]byte, error) {
    // В Go 1.26: ~2x быстрее, ~50% меньше аллокаций
    body, err := io.ReadAll(r.Body)
    if err != nil {
        return nil, fmt.Errorf("read body: %w", err)
    }
    return body, nil
}

func loadConfig(path string) ([]byte, error) {
    f, err := os.Open(path)
    if err != nil {
        return nil, err
    }
    defer f.Close()

    // В Go 1.26: умное предвыделение на основе os.File.Stat()
    return io.ReadAll(f) // Быстрее в Go 1.26
}
```

**Детали оптимизации (для понимания):**
```
Go 1.25 и ранее:
- io.ReadAll начинает с буфера 512 bytes
- Каждый раз удваивает при переполнении
- Много промежуточных аллокаций

Go 1.26:
- Для os.File: читает размер через Stat() заранее
- Для bytes.Buffer и strings.Reader: предвыделяет точный размер
- Для http.Response.Body: использует Content-Length если доступен
- Значительно меньше re-allocation
```

---

## Практические примеры

### Пример 1: REST API с валидацией

```go
// internal/handler/product_handler.go
package handler

import (
    "encoding/json"
    "net/http"

    "github.com/go-chi/chi/v5"
    "github.com/go-playground/validator/v10"
)

type CreateProductRequest struct {
    Name        string   `json:"name" validate:"required,min=2,max=200"`
    Description string   `json:"description" validate:"max=5000"`
    Price       float64  `json:"price" validate:"required,gt=0"`
    Currency    string   `json:"currency" validate:"required,oneof=USD EUR RUB"`
    Categories  []string `json:"categories" validate:"required,min=1,max=5,dive,required"`
    Stock       int      `json:"stock" validate:"gte=0"`
}

type ProductResponse struct {
    ID          int      `json:"id"`
    Name        string   `json:"name"`
    Description string   `json:"description,omitempty"`
    Price       float64  `json:"price"`
    Currency    string   `json:"currency"`
    Categories  []string `json:"categories"`
    Stock       int      `json:"stock"`
}

type ProductHandler struct {
    service  ProductService
    validate *validator.Validate
}

func NewProductHandler(service ProductService) *ProductHandler {
    v := validator.New()
    return &ProductHandler{
        service:  service,
        validate: v,
    }
}

func (h *ProductHandler) Routes() chi.Router {
    r := chi.NewRouter()
    r.Post("/", h.Create)
    r.Get("/{id}", h.Get)
    r.Put("/{id}", h.Update)
    r.Delete("/{id}", h.Delete)
    return r
}

func (h *ProductHandler) Create(w http.ResponseWriter, r *http.Request) {
    var req CreateProductRequest

    // 1. Decode JSON
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        h.respondError(w, http.StatusBadRequest, "Invalid JSON format")
        return
    }

    // 2. Validate
    if err := h.validate.Struct(req); err != nil {
        h.respondValidationError(w, err)
        return
    }

    // 3. Business logic
    product, err := h.service.Create(r.Context(), req)
    if err != nil {
        h.handleServiceError(w, err)
        return
    }

    // 4. Response
    h.respondJSON(w, http.StatusCreated, ProductResponse{
        ID:          product.ID,
        Name:        product.Name,
        Description: product.Description,
        Price:       product.Price,
        Currency:    product.Currency,
        Categories:  product.Categories,
        Stock:       product.Stock,
    })
}

func (h *ProductHandler) respondJSON(w http.ResponseWriter, status int, data any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(data)
}

func (h *ProductHandler) respondError(w http.ResponseWriter, status int, message string) {
    h.respondJSON(w, status, map[string]string{"error": message})
}

func (h *ProductHandler) respondValidationError(w http.ResponseWriter, err error) {
    errors := make(map[string]string)

    for _, e := range err.(validator.ValidationErrors) {
        field := e.Field()
        switch e.Tag() {
        case "required":
            errors[field] = field + " is required"
        case "min":
            errors[field] = field + " is too short"
        case "max":
            errors[field] = field + " is too long"
        case "gt":
            errors[field] = field + " must be greater than " + e.Param()
        case "oneof":
            errors[field] = field + " must be one of: " + e.Param()
        default:
            errors[field] = field + " is invalid"
        }
    }

    h.respondJSON(w, http.StatusBadRequest, map[string]any{
        "error":   "Validation failed",
        "details": errors,
    })
}

func (h *ProductHandler) handleServiceError(w http.ResponseWriter, err error) {
    switch {
    case errors.Is(err, ErrProductNotFound):
        h.respondError(w, http.StatusNotFound, "Product not found")
    case errors.Is(err, ErrDuplicateName):
        h.respondError(w, http.StatusConflict, "Product with this name already exists")
    default:
        h.respondError(w, http.StatusInternalServerError, "Internal server error")
    }
}
```

### Пример 2: Оптимизация JSON

```go
// internal/model/user_easyjson.go
//go:generate easyjson -all user.go

package model

type User struct {
    ID        int       `json:"id"`
    Email     string    `json:"email"`
    Name      string    `json:"name"`
    Role      string    `json:"role"`
    CreatedAt time.Time `json:"created_at"`
}

type UsersResponse struct {
    Users []User `json:"users"`
    Total int    `json:"total"`
}
```

```bash
# Генерация
go generate ./internal/model/...
```

```go
// Использование в handler
package handler

import (
    "net/http"

    "github.com/mailru/easyjson"
    "myapp/internal/model"
)

func (h *Handler) ListUsers(w http.ResponseWriter, r *http.Request) {
    users, total, err := h.service.List(r.Context())
    if err != nil {
        // ...
    }

    response := &model.UsersResponse{
        Users: users,
        Total: total,
    }

    w.Header().Set("Content-Type", "application/json")

    // easyjson — в 5x быстрее стандартного encoding/json
    data, err := easyjson.Marshal(response)
    if err != nil {
        http.Error(w, "Serialization error", http.StatusInternalServerError)
        return
    }

    w.Write(data)
}

// Или через Writer (без аллокации []byte)
func (h *Handler) ListUsersOptimized(w http.ResponseWriter, r *http.Request) {
    users, total, _ := h.service.List(r.Context())

    response := &model.UsersResponse{
        Users: users,
        Total: total,
    }

    w.Header().Set("Content-Type", "application/json")

    // Пишем напрямую в ResponseWriter
    _, _, err := easyjson.MarshalToHTTPResponseWriter(response, w)
    if err != nil {
        // Уже поздно менять статус, логируем
        log.Printf("Failed to write response: %v", err)
    }
}
```

### Пример 3: Protobuf для микросервисов

```protobuf
// api/proto/product.proto
syntax = "proto3";

package api.v1;

option go_package = "myapp/internal/pb";

message Product {
  int32 id = 1;
  string name = 2;
  string description = 3;
  double price = 4;
  string currency = 5;
  int32 stock = 6;
}

message GetProductRequest {
  int32 id = 1;
}

message GetProductResponse {
  Product product = 1;
}

service ProductService {
  rpc GetProduct(GetProductRequest) returns (GetProductResponse);
}
```

```go
// internal/client/product_client.go
package client

import (
    "context"
    "net/http"

    "google.golang.org/protobuf/proto"
    "myapp/internal/pb"
)

type ProductClient struct {
    baseURL string
    client  *http.Client
}

func NewProductClient(baseURL string) *ProductClient {
    return &ProductClient{
        baseURL: baseURL,
        client:  &http.Client{Timeout: 10 * time.Second},
    }
}

func (c *ProductClient) GetProduct(ctx context.Context, id int) (*pb.Product, error) {
    req := &pb.GetProductRequest{Id: int32(id)}

    // Сериализация запроса
    body, err := proto.Marshal(req)
    if err != nil {
        return nil, err
    }

    // HTTP запрос
    httpReq, _ := http.NewRequestWithContext(ctx, "POST",
        c.baseURL+"/api/v1/products/get",
        bytes.NewReader(body))
    httpReq.Header.Set("Content-Type", "application/x-protobuf")

    resp, err := c.client.Do(httpReq)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    // Десериализация ответа
    respBody, _ := io.ReadAll(resp.Body)

    var response pb.GetProductResponse
    if err := proto.Unmarshal(respBody, &response); err != nil {
        return nil, err
    }

    return response.Product, nil
}
```

---
