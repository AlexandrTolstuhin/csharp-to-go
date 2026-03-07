# Reflection в Go

---

## Введение

> 💡 **Для C# разработчиков**: Reflection в Go (`reflect` пакет) концептуально похож на C# Reflection, но значительно скромнее. Нет генерации кода в рантайме (Emit), нет dynamic-типов, нет Expression Trees. Зато есть принципиальное отличие: в Go reflection используется редко и считается последним средством — там, где C# разработчики привычно тянутся к `Type.GetProperties()`, идиоматичный Go предпочитает явный код или кодогенерацию.

### Что вы узнаете

- `reflect.Type` и `reflect.Value`: основы работы с типами в рантайме
- Инспекция struct-тегов — как `encoding/json` работает под капотом
- Динамический вызов методов через `Value.Call()`
- Создание и изменение значений через reflect
- Когда reflect оправдан: сериализаторы, DI, codegen
- Антипаттерны и альтернативы через кодогенерацию
- `reflect.Select`: динамический `select` по каналам
- `go/ast` как инструмент статического анализа для codegen

---

## reflect.Type и reflect.Value: основы

Пакет `reflect` работает через два центральных типа:

- `reflect.Type` — описание типа (структура, поля, методы)
- `reflect.Value` — конкретное значение с возможностью его читать и изменять

```go
import "reflect"

type User struct {
    ID    int64  `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email,omitempty"`
}

func main() {
    u := User{ID: 1, Name: "Alice", Email: "alice@example.com"}

    // reflect.TypeOf — тип значения
    t := reflect.TypeOf(u)
    fmt.Println(t.Name())    // User
    fmt.Println(t.Kind())    // struct
    fmt.Println(t.PkgPath()) // main (или полный путь пакета)

    // reflect.ValueOf — значение
    v := reflect.ValueOf(u)
    fmt.Println(v.Kind())         // struct
    fmt.Println(v.Field(0).Int()) // 1

    // Через указатель
    pt := reflect.TypeOf(&u)
    fmt.Println(pt.Kind())       // ptr
    fmt.Println(pt.Elem().Kind()) // struct
}
```

### Kind vs Type

`Kind` — категория типа (`struct`, `ptr`, `slice`, `map`, `int`, ...).
`Type` — конкретный именованный тип (`User`, `int64`, `[]string`).

```go
type MyInt int

var x MyInt = 42
t := reflect.TypeOf(x)

fmt.Println(t.Name()) // MyInt
fmt.Println(t.Kind()) // int  ← базовый вид, не MyInt
```

### Основные методы Type

```go
t := reflect.TypeOf(User{})

// Информация о типе
t.Name()        // "User"
t.Kind()        // reflect.Struct
t.PkgPath()     // "main"
t.Size()        // размер в байтах

// Поля struct
t.NumField()    // 3
f := t.Field(0)
f.Name          // "ID"
f.Type          // reflect.Type для int64
f.Tag           // reflect.StructTag (`json:"id"`)
f.Anonymous     // true для встроенных полей (embedding)
f.Index         // []int{0}

// Методы
t.NumMethod()   // количество методов на типе (не указателе)
m := t.Method(0)
m.Name          // имя метода
m.Type          // сигнатура метода

// Поиск
t.FieldByName("Name")    // (StructField, bool)
t.MethodByName("String") // (Method, bool)
```

### Основные методы Value

```go
v := reflect.ValueOf(u)

// Базовые
v.Type()  // reflect.Type
v.Kind()  // reflect.Kind

// Проверки
v.IsValid() // false если v == reflect.Value{}
v.IsNil()   // только для chan/func/interface/map/ptr/slice

// Получение Go-значения
v.Interface()      // any — универсально
v.String()         // для string
v.Int()            // для int*
v.Float()          // для float*
v.Bool()           // для bool
v.Bytes()          // для []byte

// Поля struct
v.NumField()
v.Field(0)
v.FieldByName("Name")

// Срезы и карты
v.Len()
v.Index(0)
v.MapKeys()
v.MapIndex(key)
```

### Сравнение с C#

**C#:**
```csharp
var type_ = typeof(User);
var properties = type_.GetProperties();
foreach (var prop in properties)
{
    Console.WriteLine($"{prop.Name}: {prop.PropertyType.Name}");
    var attr = prop.GetCustomAttribute<JsonPropertyNameAttribute>();
    if (attr != null)
        Console.WriteLine($"  JSON: {attr.Name}");
}

// Получить значение
var user = new User { ID = 1, Name = "Alice" };
var nameValue = type_.GetProperty("Name")?.GetValue(user);
```

**Go:**
```go
t := reflect.TypeOf(User{})
v := reflect.ValueOf(u)

for i := 0; i < t.NumField(); i++ {
    field := t.Field(i)
    value := v.Field(i)
    fmt.Printf("%s (%s) = %v\n", field.Name, field.Type.Name(), value.Interface())

    jsonTag := field.Tag.Get("json")
    if jsonTag != "" {
        fmt.Printf("  JSON: %s\n", jsonTag)
    }
}
```

---

## Инспекция struct-тегов

Struct tags — это строковые метаданные полей, доступные через `reflect.StructTag`. Именно так работают `encoding/json`, `validate`, `db` и другие библиотеки.

```go
type Product struct {
    ID       int64   `json:"id"                  db:"product_id" validate:"required"`
    Name     string  `json:"name"                db:"name"       validate:"required,min=1,max=255"`
    Price    float64 `json:"price"               db:"price"      validate:"gte=0"`
    Internal string  `json:"-"`                                   // игнорировать в JSON
    Optional *string `json:"description,omitempty" db:"description"`
}
```

### Чтение тегов

```go
func inspectTags(v any) {
    t := reflect.TypeOf(v)
    if t.Kind() == reflect.Ptr {
        t = t.Elem()
    }
    if t.Kind() != reflect.Struct {
        return
    }

    for i := 0; i < t.NumField(); i++ {
        field := t.Field(i)
        tag := field.Tag

        // Get — возвращает "" если тег отсутствует
        jsonName := tag.Get("json")
        dbName   := tag.Get("db")
        validate := tag.Get("validate")

        // Lookup — различает "" и отсутствие тега
        val, ok := tag.Lookup("json")
        if !ok {
            fmt.Printf("Поле %s не имеет json-тега\n", field.Name)
        }
        _ = val

        fmt.Printf("%-12s json:%-20s db:%-15s validate:%s\n",
            field.Name, jsonName, dbName, validate)
    }
}
```

### Парсинг json-тега с опциями

`encoding/json` парсит теги вида `"name,omitempty"` — можно воспроизвести:

```go
// parseJSONTag разбирает тег вида "name,omitempty" или "-"
func parseJSONTag(field reflect.StructField) (name string, omitempty bool, skip bool) {
    tag := field.Tag.Get("json")
    if tag == "-" {
        return "", false, true
    }

    parts := strings.SplitN(tag, ",", 2)
    name = parts[0]
    if name == "" {
        name = field.Name // по умолчанию — имя поля
    }

    if len(parts) > 1 {
        for _, opt := range strings.Split(parts[1], ",") {
            if opt == "omitempty" {
                omitempty = true
            }
        }
    }
    return name, omitempty, false
}
```

### Мини-сериализатор: как работает encoding/json

```go
// Упрощённый JSON-сериализатор через reflect
// Только для понимания — в production используйте encoding/json
func marshalSimple(v any) (string, error) {
    val := reflect.ValueOf(v)
    if val.Kind() == reflect.Ptr {
        if val.IsNil() {
            return "null", nil
        }
        val = val.Elem()
    }

    switch val.Kind() {
    case reflect.Struct:
        return marshalStruct(val)
    case reflect.String:
        return fmt.Sprintf("%q", val.String()), nil
    case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
        return fmt.Sprintf("%d", val.Int()), nil
    case reflect.Float32, reflect.Float64:
        return fmt.Sprintf("%g", val.Float()), nil
    case reflect.Bool:
        return fmt.Sprintf("%t", val.Bool()), nil
    default:
        return "null", nil
    }
}

func marshalStruct(val reflect.Value) (string, error) {
    t := val.Type()
    var parts []string

    for i := 0; i < t.NumField(); i++ {
        field := t.Field(i)
        fieldVal := val.Field(i)

        // Пропустить неэкспортированные
        if !field.IsExported() {
            continue
        }

        jsonName, omitempty, skip := parseJSONTag(field)
        if skip {
            continue
        }

        // omitempty: пропустить zero-value
        if omitempty && fieldVal.IsZero() {
            continue
        }

        valueStr, err := marshalSimple(fieldVal.Interface())
        if err != nil {
            return "", err
        }

        parts = append(parts, fmt.Sprintf("%q:%s", jsonName, valueStr))
    }

    return "{" + strings.Join(parts, ",") + "}", nil
}
```

---

## Динамический вызов методов

### MethodByName и Call

```go
type Calculator struct {
    value float64
}

func (c *Calculator) Add(x float64) float64 { return c.value + x }
func (c *Calculator) Mul(x float64) float64 { return c.value * x }
func (c *Calculator) String() string          { return fmt.Sprintf("%.2f", c.value) }

func callMethod(obj any, methodName string, args ...any) ([]any, error) {
    v := reflect.ValueOf(obj)

    method := v.MethodByName(methodName)
    if !method.IsValid() {
        return nil, fmt.Errorf("метод %s не найден", methodName)
    }

    // Подготовить аргументы
    in := make([]reflect.Value, len(args))
    for i, arg := range args {
        in[i] = reflect.ValueOf(arg)
    }

    // Вызов
    results := method.Call(in)

    // Извлечь результаты
    out := make([]any, len(results))
    for i, r := range results {
        out[i] = r.Interface()
    }
    return out, nil
}

func main() {
    calc := &Calculator{value: 10}

    result, err := callMethod(calc, "Add", 5.0)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println(result[0]) // 15

    // Метод без аргументов
    result, _ = callMethod(calc, "String")
    fmt.Println(result[0]) // 10.00
}
```

### Проверка сигнатуры метода

```go
// Перед вызовом — проверить сигнатуру
func validateMethod(t reflect.Type, methodName string, numIn, numOut int) error {
    method, ok := t.MethodByName(methodName)
    if !ok {
        return fmt.Errorf("метод %s не найден в %s", methodName, t.Name())
    }

    mt := method.Type
    // Для методов на значении: первый параметр — receiver
    // Для методов на указателе через interface: receiver уже не считается
    if mt.NumIn() != numIn {
        return fmt.Errorf("ожидается %d аргументов, есть %d", numIn, mt.NumIn())
    }
    if mt.NumOut() != numOut {
        return fmt.Errorf("ожидается %d возвращаемых значений, есть %d", numOut, mt.NumOut())
    }
    return nil
}
```

### Сравнение с C#

**C#:**
```csharp
var obj = new Calculator(10);
var method = obj.GetType().GetMethod("Add")!;
var result = method.Invoke(obj, new object[] { 5.0 });
Console.WriteLine(result); // 15

// Проверка сигнатуры
var parameters = method.GetParameters();
Console.WriteLine(parameters[0].ParameterType.Name); // Double
```

**Go:**
```go
v := reflect.ValueOf(&calc)
method := v.MethodByName("Add")
mt := method.Type()

// Проверка типа аргумента
fmt.Println(mt.In(0)) // float64

result := method.Call([]reflect.Value{reflect.ValueOf(5.0)})
fmt.Println(result[0].Float()) // 15
```

---

## Создание значений и изменение через reflect

### reflect.New и адресуемые значения

```go
// reflect.New аналогичен new(T)
t := reflect.TypeOf(User{})
ptr := reflect.New(t)       // *User, инициализированный zero-value
elem := ptr.Elem()          // User — адресуемый, можно Set

// Установка полей
elem.FieldByName("ID").SetInt(42)
elem.FieldByName("Name").SetString("Bob")
elem.FieldByName("Email").SetString("bob@example.com")

user := elem.Interface().(User)
fmt.Println(user) // {42 Bob bob@example.com}
```

### CanSet — когда можно изменять

```go
u := User{ID: 1}

// Неадресуемое значение — нельзя изменить
v := reflect.ValueOf(u)
fmt.Println(v.Field(0).CanSet()) // false

// Через указатель — можно
pv := reflect.ValueOf(&u).Elem()
fmt.Println(pv.Field(0).CanSet()) // true
pv.Field(0).SetInt(99)
fmt.Println(u.ID) // 99

// Неэкспортированное поле — нельзя даже через указатель
type secret struct{ hidden string }
s := secret{hidden: "private"}
sv := reflect.ValueOf(&s).Elem()
fmt.Println(sv.Field(0).CanSet()) // false — неэкспортированное
```

### Паттерн: универсальный mapper struct → map

```go
// StructToMap конвертирует struct в map[string]any по json-тегам
func StructToMap(v any) map[string]any {
    val := reflect.ValueOf(v)
    if val.Kind() == reflect.Ptr {
        val = val.Elem()
    }
    if val.Kind() != reflect.Struct {
        return nil
    }

    t := val.Type()
    result := make(map[string]any, t.NumField())

    for i := 0; i < t.NumField(); i++ {
        field := t.Field(i)
        if !field.IsExported() {
            continue
        }

        key := field.Tag.Get("json")
        if key == "" || key == "-" {
            key = field.Name
        } else {
            key = strings.SplitN(key, ",", 2)[0]
        }

        result[key] = val.Field(i).Interface()
    }
    return result
}
```

---

## reflect.Select: динамический select

`reflect.Select` позволяет построить `select` с набором каналов, известным только в рантайме. В статическом Go количество каналов в `select` фиксировано на этапе компиляции.

### Базовый пример

```go
func fanIn(channels ...<-chan int) <-chan int {
    out := make(chan int)

    go func() {
        defer close(out)

        // Строим набор SelectCase динамически
        cases := make([]reflect.SelectCase, len(channels)+1)

        // Канал завершения (первый)
        done := make(chan struct{})
        cases[0] = reflect.SelectCase{
            Dir:  reflect.SelectRecv,
            Chan: reflect.ValueOf(done),
        }

        for i, ch := range channels {
            cases[i+1] = reflect.SelectCase{
                Dir:  reflect.SelectRecv,
                Chan: reflect.ValueOf(ch),
            }
        }

        remaining := len(channels)
        for remaining > 0 {
            chosen, value, ok := reflect.Select(cases)
            if chosen == 0 {
                return // done-канал
            }
            if !ok {
                // Канал закрыт — убрать его из набора
                cases[chosen] = reflect.SelectCase{Dir: reflect.SelectDefault}
                remaining--
                continue
            }
            out <- int(value.Int())
        }
    }()

    return out
}
```

### Мультиплексор с таймаутом

```go
// SelectFirst читает из нескольких каналов, возвращает первое значение
func SelectFirst[T any](timeout time.Duration, channels ...<-chan T) (T, bool) {
    cases := make([]reflect.SelectCase, len(channels)+1)

    // Таймаут через time.After
    cases[0] = reflect.SelectCase{
        Dir:  reflect.SelectRecv,
        Chan: reflect.ValueOf(time.After(timeout)),
    }
    for i, ch := range channels {
        cases[i+1] = reflect.SelectCase{
            Dir:  reflect.SelectRecv,
            Chan: reflect.ValueOf(ch),
        }
    }

    chosen, value, ok := reflect.Select(cases)
    if chosen == 0 || !ok {
        var zero T
        return zero, false
    }
    return value.Interface().(T), true
}
```

### reflect.SelectCase поля

```go
// Отправка в канал
reflect.SelectCase{
    Dir:  reflect.SelectSend,
    Chan: reflect.ValueOf(ch),    // chan T
    Send: reflect.ValueOf(value), // значение T
}

// Получение из канала
reflect.SelectCase{
    Dir:  reflect.SelectRecv,
    Chan: reflect.ValueOf(ch), // <-chan T или chan T
}

// Default ветка (non-blocking)
reflect.SelectCase{
    Dir: reflect.SelectDefault,
}
```

> 💡 **Когда нужен reflect.Select**: динамическое количество источников данных — например, агрегатор данных с переменным числом upstream-сервисов, или fan-in для N каналов где N неизвестно на этапе компиляции.

---

## Когда reflect оправдан

### 1. Сериализаторы и ORM

```go
// encoding/json, encoding/xml, encoding/gob — все используют reflect
// GORM, sqlx, ent (до кодогенерации) — тоже

// Пример: sqlx Scan в struct через reflect
// sqlx читает теги `db:"column_name"` и маппит результат запроса
type Order struct {
    ID         int64     `db:"id"`
    UserID     int64     `db:"user_id"`
    TotalPrice float64   `db:"total_price"`
    CreatedAt  time.Time `db:"created_at"`
}

// sqlx.Get автоматически маппит через reflect
var order Order
err := db.Get(&order, "SELECT * FROM orders WHERE id = $1", orderID)
```

### 2. Универсальные DI-контейнеры

```go
// Упрощённый DI: регистрация и резолвинг зависимостей
type Container struct {
    factories map[reflect.Type]any
}

func (c *Container) Register(factory any) {
    ft := reflect.TypeOf(factory)
    // factory: func() T или func(deps...) T
    returnType := ft.Out(0)
    c.factories[returnType] = factory
}

func (c *Container) Resolve(target any) error {
    t := reflect.TypeOf(target)
    if t.Kind() != reflect.Ptr {
        return fmt.Errorf("target должен быть указателем")
    }
    elemType := t.Elem()

    factory, ok := c.factories[elemType]
    if !ok {
        return fmt.Errorf("нет регистрации для %s", elemType)
    }

    result := reflect.ValueOf(factory).Call(nil)
    reflect.ValueOf(target).Elem().Set(result[0])
    return nil
}
```

### 3. Валидаторы

```go
// go-playground/validator использует reflect для проверки тегов
// Упрощённый валидатор required-полей
func ValidateRequired(v any) []string {
    val := reflect.ValueOf(v)
    if val.Kind() == reflect.Ptr {
        val = val.Elem()
    }
    t := val.Type()

    var errors []string
    for i := 0; i < t.NumField(); i++ {
        field := t.Field(i)
        tag := field.Tag.Get("validate")
        if !strings.Contains(tag, "required") {
            continue
        }
        if val.Field(i).IsZero() {
            errors = append(errors, fmt.Sprintf("поле %s обязательно", field.Name))
        }
    }
    return errors
}
```

### 4. Инструменты разработки

```go
// fmt.Printf("%v", x) — reflect под капотом
// testing.DeepEqual — reflect.DeepEqual
// text/template — reflect для доступа к полям

// Типичный паттерн в инструментах: инспекция без изменения
func PrintStruct(v any) {
    val := reflect.ValueOf(v)
    if val.Kind() == reflect.Ptr {
        val = val.Elem()
    }
    t := val.Type()

    fmt.Printf("=== %s ===\n", t.Name())
    for i := 0; i < t.NumField(); i++ {
        field := t.Field(i)
        value := val.Field(i)
        fmt.Printf("  %-15s = %v\n", field.Name, value.Interface())
    }
}
```

---

## Антипаттерны и альтернативы

### reflect в hot path

```go
// ❌ Медленно: reflect в цикле обработки запросов
func SerializeUserSlow(u User) string {
    val := reflect.ValueOf(u)
    t := val.Type()
    // ... reflection каждый раз
    return result
}

// ✅ Быстро: кодогенерация (easyjson, jsoniter)
// Или явный маршалинг:
func SerializeUser(u User) string {
    return fmt.Sprintf(`{"id":%d,"name":%q}`, u.ID, u.Name)
}
```

**Бенчмарк:**

```go
func BenchmarkReflectMarshal(b *testing.B) {
    u := User{ID: 1, Name: "Alice", Email: "alice@example.com"}
    b.ReportAllocs()
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        _ = reflectMarshal(u) // ~2000 ns/op, 8 allocs/op
    }
}

func BenchmarkDirectMarshal(b *testing.B) {
    u := User{ID: 1, Name: "Alice", Email: "alice@example.com"}
    b.ReportAllocs()
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        _ = fmt.Sprintf(`{"id":%d,"name":%q,"email":%q}`, u.ID, u.Name, u.Email)
    }
    // ~400 ns/op, 1 alloc/op
}
```

### sync.Map вместо reflect для type registry

```go
// ❌ Не нужен reflect для реестра типов
type HandlerRegistry struct{}
func (r *HandlerRegistry) Register(name string, handler any) { ... }
func (r *HandlerRegistry) Call(name string, args ...any)     { ... }

// ✅ Явный реестр с конкретными типами
type HandlerFunc func(ctx context.Context, payload []byte) error

type HandlerRegistry struct {
    handlers map[string]HandlerFunc
}
func (r *HandlerRegistry) Register(name string, handler HandlerFunc) {
    r.handlers[name] = handler
}
func (r *HandlerRegistry) Call(ctx context.Context, name string, payload []byte) error {
    h, ok := r.handlers[name]
    if !ok {
        return fmt.Errorf("обработчик %s не найден", name)
    }
    return h(ctx, payload)
}
```

### Кэширование reflect-информации

```go
// Если reflect необходим — кэшировать TypeOf результаты
var (
    typeCache   sync.Map // map[reflect.Type]*typeInfo
)

type typeInfo struct {
    fields []fieldInfo
}

type fieldInfo struct {
    index   int
    name    string
    jsonKey string
    kind    reflect.Kind
}

func getTypeInfo(t reflect.Type) *typeInfo {
    if cached, ok := typeCache.Load(t); ok {
        return cached.(*typeInfo)
    }

    info := buildTypeInfo(t) // reflect вызывается один раз
    typeCache.Store(t, info)
    return info
}

// buildTypeInfo вызывается при первом обращении к типу
// Последующие вызовы используют кэш — reflect только при инициализации
func buildTypeInfo(t reflect.Type) *typeInfo {
    fields := make([]fieldInfo, 0, t.NumField())
    for i := 0; i < t.NumField(); i++ {
        f := t.Field(i)
        if !f.IsExported() {
            continue
        }
        key := f.Tag.Get("json")
        if key == "-" {
            continue
        }
        if key == "" {
            key = f.Name
        } else {
            key = strings.SplitN(key, ",", 2)[0]
        }
        fields = append(fields, fieldInfo{
            index:   i,
            name:    f.Name,
            jsonKey: key,
            kind:    f.Type.Kind(),
        })
    }
    return &typeInfo{fields: fields}
}
```

> 💡 **Правило**: Если reflect нужен в hot path — кэшируй `typeInfo` при запуске. `encoding/json` делает именно это через внутренний кэш кодировщиков.

---

## go/ast: статический анализ как альтернатива reflect

`go/ast` — анализ исходного кода на этапе компиляции / генерации. Не требует рантайма, не влияет на производительность.

### Разбор файла

```go
import (
    "go/ast"
    "go/parser"
    "go/token"
)

func parseFile(filename string) (*ast.File, *token.FileSet) {
    fset := token.NewFileSet()
    file, err := parser.ParseFile(fset, filename, nil, parser.ParseComments)
    if err != nil {
        log.Fatal(err)
    }
    return file, fset
}
```

### Поиск всех struct-типов в файле

```go
func findStructs(file *ast.File) []string {
    var structs []string

    // ast.Inspect обходит AST в глубину
    ast.Inspect(file, func(n ast.Node) bool {
        // TypeSpec — объявление типа: type Foo struct{}
        ts, ok := n.(*ast.TypeSpec)
        if !ok {
            return true // продолжить обход
        }

        // Проверить, что это struct
        if _, isStruct := ts.Type.(*ast.StructType); isStruct {
            structs = append(structs, ts.Name.Name)
        }
        return true
    })

    return structs
}

// Использование
func main() {
    file, _ := parseFile("models.go")
    structs := findStructs(file)
    fmt.Println(structs) // [User Order Product ...]
}
```

### Извлечение полей struct с тегами

```go
type FieldMeta struct {
    Name    string
    Type    string
    JSONTag string
    DBTag   string
}

func extractFields(file *ast.File, structName string) []FieldMeta {
    var fields []FieldMeta

    ast.Inspect(file, func(n ast.Node) bool {
        ts, ok := n.(*ast.TypeSpec)
        if !ok || ts.Name.Name != structName {
            return true
        }

        st, ok := ts.Type.(*ast.StructType)
        if !ok {
            return false
        }

        for _, field := range st.Fields.List {
            for _, name := range field.Names {
                meta := FieldMeta{Name: name.Name}

                // Тип поля — может быть *ast.Ident или *ast.StarExpr (указатель)
                switch ft := field.Type.(type) {
                case *ast.Ident:
                    meta.Type = ft.Name
                case *ast.StarExpr:
                    if id, ok := ft.X.(*ast.Ident); ok {
                        meta.Type = "*" + id.Name
                    }
                }

                // Теги
                if field.Tag != nil {
                    tag := reflect.StructTag(
                        strings.Trim(field.Tag.Value, "`"),
                    )
                    meta.JSONTag = tag.Get("json")
                    meta.DBTag = tag.Get("db")
                }

                fields = append(fields, meta)
            }
        }
        return false
    })

    return fields
}
```

### Генерация кода через go/ast + text/template

```go
// go generate: нет рантайм-reflect, генерируем код один раз
// Типичный workflow:
//
// 1. Читаем исходный Go-файл через go/ast
// 2. Извлекаем метаданные (типы, поля, теги)
// 3. Генерируем код через text/template
// 4. Форматируем через go/format
// 5. Пишем в *_gen.go файл

const tmpl = `// Code generated by mycodegen. DO NOT EDIT.
package {{ .Package }}

{{ range .Structs }}
func (s {{ .Name }}) ToMap() map[string]any {
    return map[string]any{
        {{ range .Fields }}"{{ .JSONKey }}": s.{{ .Name }},
        {{ end }}
    }
}
{{ end }}`

type TemplateData struct {
    Package string
    Structs []StructData
}

type StructData struct {
    Name   string
    Fields []FieldData
}

type FieldData struct {
    Name    string
    JSONKey string
}

func generate(data TemplateData) ([]byte, error) {
    t := template.Must(template.New("").Parse(tmpl))

    var buf bytes.Buffer
    if err := t.Execute(&buf, data); err != nil {
        return nil, err
    }

    // Форматирование — как gofmt
    formatted, err := format.Source(buf.Bytes())
    if err != nil {
        return nil, fmt.Errorf("ошибка форматирования: %w\n%s", err, buf.String())
    }
    return formatted, nil
}
```

### Сравнение reflect vs go/ast

| Аспект | `reflect` | `go/ast` |
|--------|-----------|----------|
| Когда работает | Рантайм | Compile time / go generate |
| Производительность | Медленнее (рантайм-проверки) | Нет влияния на рантайм |
| Доступ к информации | Значения + типы | Только синтаксис, не значения |
| Изменение данных | Да (`CanSet`) | Нет |
| Использование | Общий код для любых типов | Кодогенерация |
| Примеры | encoding/json, validator | stringer, mockgen, sqlc |

---

## Полное сравнение с C# Reflection

| Аспект | C# | Go |
|--------|----|----|
| Получить тип | `typeof(T)`, `obj.GetType()` | `reflect.TypeOf(v)` |
| Список полей | `Type.GetProperties()`, `GetFields()` | `Type.NumField()`, `Type.Field(i)` |
| Список методов | `Type.GetMethods()` | `Type.NumMethod()`, `Type.Method(i)` |
| Вызов метода | `MethodInfo.Invoke(obj, args)` | `Value.MethodByName(name).Call(args)` |
| Создание экземпляра | `Activator.CreateInstance(type)` | `reflect.New(type)` |
| Чтение атрибутов | `MemberInfo.GetCustomAttributes()` | `StructField.Tag.Get("key")` |
| Установка поля | `PropertyInfo.SetValue(obj, val)` | `Value.Field(i).SetInt(v)` |
| Генерация кода в рантайме | `System.Reflection.Emit` | Не поддерживается |
| Expression Trees | `Expression<Func<T,R>>` | Нет |
| Source Generators | `ISourceGenerator` (Roslyn) | `go/ast` + `go generate` |
| Атрибуты/теги | `[JsonPropertyName("x")]` | `` `json:"x"` `` в struct |

**Ключевые отличия:**

1. **Теги vs атрибуты**: Go-теги — строки, читаемые через `StructTag.Get()`. C# атрибуты — типизированные классы с параметрами.

2. **Нет Emit**: В Go нельзя генерировать IL/байткод в рантайме. Для динамического поведения — `reflect.Call()` или кодогенерация.

3. **Нет dynamic**: Тип `dynamic` в C# компилятор преобразует в вызовы через DLR. В Go аналог — `any` (`interface{}`), но без автоматической диспетчеризации.

4. **Generics vs reflect**: Многие паттерны, требовавшие reflect до Go 1.18, теперь решаются через дженерики без рантайм-затрат.

---

## Практические примеры

### Пример 1: Реестр обработчиков событий

**Задача**: Диспетчер событий — разные типы событий в одной очереди, обработчики регистрируются по типу.

```go
type EventDispatcher struct {
    handlers map[reflect.Type][]reflect.Value
}

func NewEventDispatcher() *EventDispatcher {
    return &EventDispatcher{handlers: make(map[reflect.Type][]reflect.Value)}
}

// Register принимает func(EventT) — тип события определяется через reflect
func (d *EventDispatcher) Register(handler any) {
    ht := reflect.TypeOf(handler)
    if ht.Kind() != reflect.Func || ht.NumIn() != 1 {
        panic("обработчик должен быть func(T)")
    }
    eventType := ht.In(0)
    d.handlers[eventType] = append(d.handlers[eventType], reflect.ValueOf(handler))
}

// Dispatch вызывает все обработчики для типа события
func (d *EventDispatcher) Dispatch(event any) {
    et := reflect.TypeOf(event)
    handlers, ok := d.handlers[et]
    if !ok {
        return
    }
    args := []reflect.Value{reflect.ValueOf(event)}
    for _, h := range handlers {
        h.Call(args)
    }
}

// Использование
type OrderCreated struct{ OrderID int64 }
type UserRegistered struct{ Email string }

func main() {
    d := NewEventDispatcher()

    d.Register(func(e OrderCreated) {
        fmt.Printf("Новый заказ: %d\n", e.OrderID)
    })
    d.Register(func(e UserRegistered) {
        fmt.Printf("Новый пользователь: %s\n", e.Email)
    })

    d.Dispatch(OrderCreated{OrderID: 42})
    d.Dispatch(UserRegistered{Email: "alice@example.com"})
}
```

### Пример 2: Копирование полей между структурами

**Задача**: Скопировать поля с совпадающими именами из DTO в доменную модель.

```go
// CopyFields копирует поля с совпадающими именами из src в dst
// dst должен быть указателем
func CopyFields(dst, src any) {
    dstVal := reflect.ValueOf(dst)
    if dstVal.Kind() != reflect.Ptr {
        panic("dst должен быть указателем")
    }
    dstVal = dstVal.Elem()
    srcVal := reflect.ValueOf(src)
    if srcVal.Kind() == reflect.Ptr {
        srcVal = srcVal.Elem()
    }

    srcType := srcVal.Type()
    for i := 0; i < srcType.NumField(); i++ {
        srcField := srcType.Field(i)
        if !srcField.IsExported() {
            continue
        }

        dstField := dstVal.FieldByName(srcField.Name)
        if !dstField.IsValid() || !dstField.CanSet() {
            continue
        }

        srcValue := srcVal.Field(i)
        // Проверить совместимость типов
        if srcValue.Type().AssignableTo(dstField.Type()) {
            dstField.Set(srcValue)
        }
    }
}

// Использование
type CreateUserRequest struct {
    Name  string
    Email string
    Age   int
}

type User struct {
    ID    int64  // нет в Request — не тронем
    Name  string
    Email string
    Age   int
}

func main() {
    req := CreateUserRequest{Name: "Alice", Email: "alice@example.com", Age: 30}
    var user User
    user.ID = 99 // установим вручную

    CopyFields(&user, req)
    fmt.Println(user) // {99 Alice alice@example.com 30}
}
```

### Пример 3: Инспектор конфигурации

**Задача**: Вывести все поля конфигурации с их текущими значениями и тегами.

```go
type Config struct {
    Host     string        `env:"HOST"     default:"localhost"`
    Port     int           `env:"PORT"     default:"8080"`
    Debug    bool          `env:"DEBUG"    default:"false"`
    Timeout  time.Duration `env:"TIMEOUT"  default:"30s"`
    LogLevel string        `env:"LOG_LEVEL" default:"info"`
}

func PrintConfig(cfg any) {
    val := reflect.ValueOf(cfg)
    if val.Kind() == reflect.Ptr {
        val = val.Elem()
    }
    t := val.Type()

    fmt.Printf("%-15s %-15s %-20s %s\n", "Field", "EnvVar", "Default", "Current")
    fmt.Println(strings.Repeat("-", 65))

    for i := 0; i < t.NumField(); i++ {
        field := t.Field(i)
        value := val.Field(i)

        envVar  := field.Tag.Get("env")
        defVal  := field.Tag.Get("default")
        current := fmt.Sprintf("%v", value.Interface())

        fmt.Printf("%-15s %-15s %-20s %s\n", field.Name, envVar, defVal, current)
    }
}
```

---

## Итоговые рекомендации

```
reflect оправдан:             reflect НЕ нужен:
─────────────────────────     ─────────────────────────
Сериализаторы/десериализаторы Конкретные типы известны
Универсальные маппперы        Дженерики решают задачу
DI-контейнеры                 Явная регистрация типов
Валидаторы по тегам           Ручная валидация полей
Инструменты/CLI               Бизнес-логика
Тестовые утилиты              Hot path (> 10K req/s)
```

**Принцип выбора**:
1. Может ли задача быть решена дженериками? → Используй дженерики
2. Нужен ли код один раз при генерации? → Используй `go/ast` + `go generate`
3. Нужна динамичность в рантайме для общего кода? → Используй `reflect` с кэшем
4. Всё остальное → Пиши явный код
