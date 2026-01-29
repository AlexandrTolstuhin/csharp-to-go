# 6.2 Современные возможности Go

## Содержание

- [Введение](#введение)
- [Generics (Go 1.18+)](#generics-go-118)
  - [Почему Go так долго ждал](#почему-go-так-долго-ждал)
  - [Синтаксис: C# vs Go](#синтаксис-c-vs-go)
  - [Type constraints](#type-constraints)
  - [Generic функции](#generic-функции)
  - [Generic типы](#generic-типы)
  - [Когда использовать generics](#когда-использовать-generics)
  - [Performance и GC](#performance-и-gc)
- [Пакеты slices и maps (Go 1.21+)](#пакеты-slices-и-maps-go-121)
  - [Пакет slices](#пакет-slices)
  - [Пакет maps](#пакет-maps)
  - [Пакет cmp](#пакет-cmp)
- [log/slog — структурированное логирование](#logslog--структурированное-логирование)
  - [Краткий обзор](#краткий-обзор)
  - [Миграция с других логгеров](#миграция-с-других-логгеров)
- [Улучшения net/http (Go 1.22+)](#улучшения-nethttp-go-122)
  - [Новый синтаксис маршрутизации](#новый-синтаксис-маршрутизации)
  - [Path parameters](#path-parameters)
  - [Сравнение с ASP.NET Core](#сравнение-с-aspnet-core)
  - [Миграция с chi/gorilla](#миграция-с-chigorilla)
- [Range over integers (Go 1.22)](#range-over-integers-go-122)
- [Другие современные возможности](#другие-современные-возможности)
  - [clear() — очистка коллекций (Go 1.21)](#clear--очистка-коллекций-go-121)
  - [min/max — встроенные функции (Go 1.21)](#minmax--встроенные-функции-go-121)
  - [cmp.Or — значения по умолчанию (Go 1.22)](#cmpor--значения-по-умолчанию-go-122)
  - [Iterators (Go 1.23)](#iterators-go-123)
- [Практические примеры](#практические-примеры)
  - [Пример 1: Generic Repository](#пример-1-generic-repository)
  - [Пример 2: Modern REST API](#пример-2-modern-rest-api)
  - [Пример 3: Миграционный чек-лист](#пример-3-миграционный-чек-лист)
- [Чек-лист](#чек-лист)

---

## Введение

Go известен своим консервативным подходом к добавлению новых возможностей. В отличие от C#, где каждая версия приносит десятки новых features (records, pattern matching, primary constructors), Go добавляет новое только после многолетнего обсуждения и когда польза очевидно перевешивает усложнение языка.

> 💡 **Для C# разработчиков**: Если в C# вы привыкли к ежегодным обновлениям с новыми синтаксическими конструкциями, в Go темп значительно медленнее. Но когда feature добавляется — она продумана до мелочей и остаётся стабильной годами.

### Эволюция: C# vs Go

| Feature | C# | Go | Комментарий |
|---------|----|----|-------------|
| **Generics** | C# 2.0 (2005) | Go 1.18 (2022) | Go ждал 13+ лет |
| **Structured logging** | Serilog (2013, 3rd party) | Go 1.21 (2023) | slog в stdlib |
| **Collection utilities** | LINQ (2007) | Go 1.21 (2023) | slices/maps пакеты |
| **Enhanced HTTP routing** | ASP.NET Core 1.0 (2016) | Go 1.22 (2024) | Method + path params в stdlib |
| **Range expressions** | C# 8.0 (2019) | Go 1.22 (2024) | `range 10` |

### Что мы рассмотрим

В этом разделе мы изучим ключевые возможности **Go 1.18-1.23**, которые делают современный Go значительно удобнее:

1. **Generics** — параметрический полиморфизм, наконец-то
2. **slices/maps пакеты** — утилиты для работы с коллекциями (прощай, LINQ-ностальгия)
3. **log/slog** — стандартное структурированное логирование
4. **net/http улучшения** — routing с методами и path parameters
5. **Range over integers** — `for i := range 10`
6. **Другие улучшения** — `clear()`, `min/max`, `cmp.Or`

---

## Generics (Go 1.18+)

Generics — самое значительное изменение в Go с момента создания языка. Они позволяют писать типобезопасный код, работающий с разными типами данных.

### Почему Go так долго ждал

Команда Go намеренно откладывала добавление generics, потому что:

1. **Простота важнее**: Generics усложняют язык и компилятор
2. **Интерфейсы работали**: Для большинства задач `interface{}` + type assertion было достаточно
3. **Не хотели повторять ошибки**: Java generics с type erasure, C++ templates с cryptic errors

> ⚠️ **Важно**: Generics в Go — это **не** замена интерфейсам. Это дополнительный инструмент для случаев, когда нужна **type safety без runtime overhead**.

### Синтаксис: C# vs Go

**C# generics:**
```csharp
// Generic класс
public class Stack<T>
{
    private List<T> _items = new();

    public void Push(T item) => _items.Add(item);
    public T Pop() => _items[^1];
}

// Generic метод
public T Max<T>(T a, T b) where T : IComparable<T>
{
    return a.CompareTo(b) > 0 ? a : b;
}

// Использование
var stack = new Stack<int>();
stack.Push(42);

var max = Max(10, 20); // Type inference
```

**Go generics:**
```go
// Generic структура
type Stack[T any] struct {
    items []T
}

func (s *Stack[T]) Push(item T) {
    s.items = append(s.items, item)
}

func (s *Stack[T]) Pop() T {
    item := s.items[len(s.items)-1]
    s.items = s.items[:len(s.items)-1]
    return item
}

// Generic функция
func Max[T cmp.Ordered](a, b T) T {
    if a > b {
        return a
    }
    return b
}

// Использование
stack := &Stack[int]{}
stack.Push(42)

max := Max(10, 20) // Type inference работает
```

### Type constraints

Constraints (ограничения) в Go определяют, какие типы могут использоваться как type parameters.

#### Встроенные constraints

```go
import "cmp"

// any — любой тип (аналог interface{})
func Print[T any](value T) {
    fmt.Println(value)
}

// comparable — типы, которые можно сравнивать через == и !=
func Contains[T comparable](slice []T, target T) bool {
    for _, item := range slice {
        if item == target {
            return true
        }
    }
    return false
}

// cmp.Ordered — типы с операторами <, >, <=, >= (Go 1.21+)
func Min[T cmp.Ordered](a, b T) T {
    if a < b {
        return a
    }
    return b
}
```

#### Сравнение constraints: C# vs Go

| C# Constraint | Go Equivalent | Пример |
|---------------|---------------|--------|
| `where T : class` | Нет прямого аналога | — |
| `where T : struct` | Нет прямого аналога | — |
| `where T : new()` | Нет прямого аналога | — |
| `where T : IComparable<T>` | `[T cmp.Ordered]` | `Max[T cmp.Ordered](a, b T)` |
| `where T : IEquatable<T>` | `[T comparable]` | `Contains[T comparable](...)` |
| `where T : SomeInterface` | `[T SomeInterface]` | `[T io.Reader]` |
| `where T : BaseClass` | Нет (нет наследования) | — |

#### Custom constraints

```go
// Constraint как интерфейс
type Number interface {
    ~int | ~int8 | ~int16 | ~int32 | ~int64 |
    ~uint | ~uint8 | ~uint16 | ~uint32 | ~uint64 |
    ~float32 | ~float64
}

func Sum[T Number](numbers []T) T {
    var total T
    for _, n := range numbers {
        total += n
    }
    return total
}

// ~ означает "underlying type" — включает type aliases
type MyInt int
numbers := []MyInt{1, 2, 3}
sum := Sum(numbers) // Работает благодаря ~int
```

#### Constraint с методами

```go
// Constraint, требующий наличия метода
type Stringer interface {
    String() string
}

func PrintAll[T Stringer](items []T) {
    for _, item := range items {
        fmt.Println(item.String())
    }
}

// Комбинированный constraint: тип + методы
type OrderedStringer interface {
    cmp.Ordered
    String() string
}
```

### Generic функции

#### Базовый синтаксис

```go
// Один type parameter
func Identity[T any](value T) T {
    return value
}

// Несколько type parameters
func Map[T, R any](slice []T, fn func(T) R) []R {
    result := make([]R, len(slice))
    for i, item := range slice {
        result[i] = fn(item)
    }
    return result
}

// Использование
doubled := Map([]int{1, 2, 3}, func(n int) int { return n * 2 })
// [2, 4, 6]

// С явным указанием типов (редко нужно)
result := Map[int, string]([]int{1, 2, 3}, strconv.Itoa)
// ["1", "2", "3"]
```

#### Полезные generic функции

```go
// Filter
func Filter[T any](slice []T, predicate func(T) bool) []T {
    var result []T
    for _, item := range slice {
        if predicate(item) {
            result = append(result, item)
        }
    }
    return result
}

// Reduce
func Reduce[T, R any](slice []T, initial R, fn func(R, T) R) R {
    result := initial
    for _, item := range slice {
        result = fn(result, item)
    }
    return result
}

// Find (возвращает pointer, nil если не найдено)
func Find[T any](slice []T, predicate func(T) bool) *T {
    for i := range slice {
        if predicate(slice[i]) {
            return &slice[i]
        }
    }
    return nil
}
```

### Generic типы

#### Generic структуры

```go
// Пара значений
type Pair[T, U any] struct {
    First  T
    Second U
}

func NewPair[T, U any](first T, second U) Pair[T, U] {
    return Pair[T, U]{First: first, Second: second}
}

// Optional/Maybe тип
type Optional[T any] struct {
    value *T
}

func Some[T any](value T) Optional[T] {
    return Optional[T]{value: &value}
}

func None[T any]() Optional[T] {
    return Optional[T]{value: nil}
}

func (o Optional[T]) IsPresent() bool {
    return o.value != nil
}

func (o Optional[T]) Get() (T, bool) {
    if o.value == nil {
        var zero T
        return zero, false
    }
    return *o.value, true
}

func (o Optional[T]) OrElse(defaultValue T) T {
    if o.value == nil {
        return defaultValue
    }
    return *o.value
}
```

#### Result тип (аналог C# Result<T, TError>)

```go
// Result — для функций, которые могут вернуть значение или ошибку
type Result[T any] struct {
    value T
    err   error
}

func Ok[T any](value T) Result[T] {
    return Result[T]{value: value}
}

func Err[T any](err error) Result[T] {
    return Result[T]{err: err}
}

func (r Result[T]) IsOk() bool {
    return r.err == nil
}

func (r Result[T]) Unwrap() (T, error) {
    return r.value, r.err
}

func (r Result[T]) UnwrapOr(defaultValue T) T {
    if r.err != nil {
        return defaultValue
    }
    return r.value
}

// Map для трансформации успешного результата
func MapResult[T, U any](r Result[T], fn func(T) U) Result[U] {
    if r.err != nil {
        return Err[U](r.err)
    }
    return Ok(fn(r.value))
}
```

### Когда использовать generics

#### ✅ Используйте generics для:

**1. Структур данных (контейнеров)**

```go
// Stack, Queue, Set, Tree — классические примеры
type Set[T comparable] struct {
    items map[T]struct{}
}

func NewSet[T comparable]() *Set[T] {
    return &Set[T]{items: make(map[T]struct{})}
}

func (s *Set[T]) Add(item T) {
    s.items[item] = struct{}{}
}

func (s *Set[T]) Contains(item T) bool {
    _, ok := s.items[item]
    return ok
}
```

**2. Утилит для работы с коллекциями**

```go
// Когда slices пакета недостаточно
func Chunk[T any](slice []T, size int) [][]T {
    var chunks [][]T
    for i := 0; i < len(slice); i += size {
        end := i + size
        if end > len(slice) {
            end = len(slice)
        }
        chunks = append(chunks, slice[i:end])
    }
    return chunks
}

func Unique[T comparable](slice []T) []T {
    seen := make(map[T]struct{})
    var result []T
    for _, item := range slice {
        if _, ok := seen[item]; !ok {
            seen[item] = struct{}{}
            result = append(result, item)
        }
    }
    return result
}
```

**3. Type-safe wrappers**

```go
// Sync.Map wrapper с типами
type SyncMap[K comparable, V any] struct {
    m sync.Map
}

func (m *SyncMap[K, V]) Store(key K, value V) {
    m.m.Store(key, value)
}

func (m *SyncMap[K, V]) Load(key K) (V, bool) {
    value, ok := m.m.Load(key)
    if !ok {
        var zero V
        return zero, false
    }
    return value.(V), true
}
```

#### ❌ НЕ используйте generics когда:

**1. Достаточно конкретного типа**

```go
// ❌ Избыточно
func ProcessUsers[T User](users []T) { ... }

// ✅ Проще
func ProcessUsers(users []User) { ... }
```

**2. Интерфейс понятнее**

```go
// ❌ Сложно читать
func Process[T interface{ Process() error }](item T) error {
    return item.Process()
}

// ✅ Классический Go-style
type Processor interface {
    Process() error
}

func Process(item Processor) error {
    return item.Process()
}
```

**3. Только 1-2 конкретных типа**

```go
// ❌ Over-engineering
func FormatID[T int | int64 | string](id T) string { ... }

// ✅ Два простых метода
func FormatIntID(id int) string { ... }
func FormatStringID(id string) string { ... }
```

> ⚠️ **Правило для C# разработчиков**: В Go простой код предпочтительнее clever-кода. Если не уверены — начните без generics. Добавите позже, если действительно понадобится.

### Performance и GC

Go использует **частичную мономорфизацию** (GCShape stenciling):

```go
// Компилятор создаёт отдельные версии для:
// - Pointer types (все указатели используют одну версию)
// - Non-pointer types (каждый размер отдельно)

func Process[T any](value T) T { return value }

// Process[int] и Process[int64] — разные версии
// Process[*User] и Process[*Order] — одна версия (оба pointer)
```

**Benchmark сравнение:**

```go
// Generic версия
func SumGeneric[T Number](slice []T) T {
    var total T
    for _, n := range slice {
        total += n
    }
    return total
}

// Конкретная версия
func SumInt(slice []int) int {
    var total int
    for _, n := range slice {
        total += n
    }
    return total
}

// Результаты benchmark (примерные):
// BenchmarkSumGeneric-8    1000000    1050 ns/op    0 B/op    0 allocs/op
// BenchmarkSumInt-8        1000000    1020 ns/op    0 B/op    0 allocs/op
// Разница ~3% — практически незаметна
```

> 💡 **Вывод**: Performance penalty от generics в Go минимален. Не избегайте generics из соображений производительности — используйте их там, где они улучшают читаемость и type safety.

---

## Пакеты slices и maps (Go 1.21+)

До Go 1.21 для любой операции с коллекциями приходилось писать ручные циклы. Для C# разработчиков, привыкших к LINQ, это было болезненно. Пакеты `slices` и `maps` решают эту проблему.

### Пакет slices

#### Сравнение с LINQ

| C# LINQ | Go slices | Описание |
|---------|-----------|----------|
| `.Contains(x)` | `slices.Contains(s, x)` | Проверка наличия элемента |
| `.Any(predicate)` | `slices.ContainsFunc(s, fn)` | Есть ли элемент, удовлетворяющий условию |
| `.First(predicate)` | `slices.IndexFunc(s, fn)` + доступ | Найти первый по условию |
| `.OrderBy()` | `slices.Sort(s)` | Сортировка (in-place!) |
| `.OrderByDescending()` | `slices.SortFunc(s, cmp)` | Сортировка с компаратором |
| `.Reverse()` | `slices.Reverse(s)` | Разворот (in-place!) |
| `.Distinct()` | `slices.Compact(s)` | Удаление дубликатов (требует сортировки!) |
| `.ToList()` / `Clone()` | `slices.Clone(s)` | Копирование slice |
| `.Max()` | `slices.Max(s)` | Максимальный элемент |
| `.Min()` | `slices.Min(s)` | Минимальный элемент |
| `.SequenceEqual()` | `slices.Equal(s1, s2)` | Сравнение slices |
| `.Take(n)` | `s[:n]` | Взять первые N (нативный синтаксис) |
| `.Skip(n)` | `s[n:]` | Пропустить первые N (нативный синтаксис) |

> ⚠️ **Важно**: Многие функции `slices` работают **in-place** (изменяют исходный slice). В LINQ методы всегда возвращают новую коллекцию. Будьте внимательны!

#### Основные функции slices

```go
import "slices"

// Поиск
numbers := []int{3, 1, 4, 1, 5, 9, 2, 6}

slices.Contains(numbers, 5)                    // true
slices.Index(numbers, 4)                       // 2 (индекс элемента)
slices.IndexFunc(numbers, func(n int) bool {   // 4 (индекс первого > 4)
    return n > 4
})

// Сортировка (in-place!)
slices.Sort(numbers)                           // [1, 1, 2, 3, 4, 5, 6, 9]
slices.SortFunc(numbers, func(a, b int) int {  // Кастомная сортировка
    return b - a  // По убыванию
})
slices.SortStableFunc(numbers, cmp)            // Стабильная сортировка

slices.IsSorted(numbers)                       // Проверка отсортированности

// Бинарный поиск (для отсортированных!)
slices.BinarySearch(numbers, 5)                // index, found

// Модификация
slices.Reverse(numbers)                        // In-place разворот
slices.Clip(numbers)                           // Обрезать capacity до length
slices.Grow(numbers, 10)                       // Увеличить capacity

// Вставка и удаление
numbers = slices.Insert(numbers, 2, 100)       // Вставить 100 на позицию 2
numbers = slices.Delete(numbers, 2, 4)         // Удалить элементы [2:4)
numbers = slices.Replace(numbers, 1, 3, 7, 8)  // Заменить [1:3) на 7, 8

// Compact — удаление последовательных дубликатов
sorted := []int{1, 1, 2, 2, 2, 3}
unique := slices.Compact(sorted)               // [1, 2, 3]

// Clone — копия slice
copy := slices.Clone(numbers)

// Сравнение
slices.Equal(slice1, slice2)                   // Поэлементное сравнение
slices.EqualFunc(slice1, slice2, equalFn)      // С кастомной функцией

// Min/Max
slices.Min(numbers)                            // Минимум
slices.Max(numbers)                            // Максимум
slices.MinFunc(items, cmpFn)                   // С компаратором
slices.MaxFunc(items, cmpFn)
```

#### Пример: обработка данных

**C# с LINQ:**
```csharp
var result = users
    .Where(u => u.IsActive)
    .OrderBy(u => u.Name)
    .Select(u => u.Email)
    .Distinct()
    .ToList();
```

**Go с slices:**
```go
// Шаг 1: Фильтрация (пока нет в slices, пишем вручную)
var activeUsers []User
for _, u := range users {
    if u.IsActive {
        activeUsers = append(activeUsers, u)
    }
}

// Шаг 2: Сортировка
slices.SortFunc(activeUsers, func(a, b User) int {
    return strings.Compare(a.Name, b.Name)
})

// Шаг 3: Извлечение emails
emails := make([]string, len(activeUsers))
for i, u := range activeUsers {
    emails[i] = u.Email
}

// Шаг 4: Удаление дубликатов (Compact требует сортировки!)
slices.Sort(emails)
emails = slices.Compact(emails)
```

> 💡 **Совет**: Для Filter, Map, Reduce — напишите свои generic-функции (см. раздел Generics) или используйте библиотеку `samber/lo`.

### Пакет maps

```go
import "maps"

users := map[string]User{
    "alice": {Name: "Alice", Age: 30},
    "bob":   {Name: "Bob", Age: 25},
}

// Clone — полная копия map
usersCopy := maps.Clone(users)

// Copy — копирование в существующую map
target := make(map[string]User)
maps.Copy(target, users)  // Добавит все пары из users в target

// Equal — сравнение maps
maps.Equal(map1, map2)
maps.EqualFunc(map1, map2, func(v1, v2 User) bool {
    return v1.Name == v2.Name
})

// DeleteFunc — удаление по условию
maps.DeleteFunc(users, func(key string, user User) bool {
    return user.Age < 18  // Удалить несовершеннолетних
})
```

#### Iterators в Go 1.23

Go 1.23 добавил поддержку iterators, включая `maps.Keys` и `maps.Values`:

```go
// Go 1.23+
import (
    "maps"
    "slices"
)

users := map[string]int{
    "alice": 30,
    "bob":   25,
    "carol": 35,
}

// Получение ключей как iterator
for key := range maps.Keys(users) {
    fmt.Println(key)
}

// Преобразование iterator в slice
keys := slices.Collect(maps.Keys(users))
values := slices.Collect(maps.Values(users))

// Сортированные ключи
keys = slices.Sorted(maps.Keys(users))
```

### Пакет cmp

```go
import "cmp"

// cmp.Ordered — constraint для упорядоченных типов
func Min[T cmp.Ordered](a, b T) T {
    if a < b {
        return a
    }
    return b
}

// cmp.Less — безопасное сравнение (обрабатывает NaN для float)
cmp.Less(1, 2)        // true
cmp.Less(2, 1)        // false
cmp.Less(1.0, math.NaN()) // true (NaN считается "больше" всего)

// cmp.Compare — возвращает -1, 0, 1
cmp.Compare(1, 2)     // -1
cmp.Compare(2, 2)     // 0
cmp.Compare(3, 2)     // 1

// cmp.Or — первое ненулевое значение (Go 1.22+)
name := cmp.Or(os.Getenv("NAME"), config.Name, "default")
// Эквивалент:
// name := os.Getenv("NAME")
// if name == "" { name = config.Name }
// if name == "" { name = "default" }
```

---

## log/slog — структурированное логирование

### Краткий обзор

Пакет `log/slog` добавлен в Go 1.21 и предоставляет стандартный интерфейс для structured logging. Полное описание с production patterns см. в [4.5 Observability](../part4-infrastructure/05_observability.md).

**Быстрое сравнение с C# ILogger:**

| Аспект | C# ILogger | Go slog |
|--------|------------|---------|
| Создание | DI injection | Явная передача через конструктор |
| Scoped logging | `_logger.BeginScope()` | `logger.With("key", "value")` |
| Structured data | `_logger.LogInformation("User {UserId}", id)` | `slog.Info("user", "id", id)` |
| Уровни | Trace, Debug, Info, Warning, Error, Critical | Debug, Info, Warn, Error |
| Output format | Через providers (Console, Serilog) | TextHandler, JSONHandler, custom |
| Context | `ILogger<T>` per class | Передача `*slog.Logger` |

**Базовое использование:**

```go
import "log/slog"

// Production setup (JSON)
logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
}))

// Использование
logger.Info("запрос обработан",
    slog.String("method", "GET"),
    slog.String("path", "/api/users"),
    slog.Int("status", 200),
    slog.Duration("latency", time.Millisecond*42),
)

// С контекстом (для tracing)
logger.InfoContext(ctx, "операция завершена",
    slog.String("operation", "create_user"),
)

// Scoped logger (как ILogger.BeginScope)
userLogger := logger.With(
    slog.String("component", "UserService"),
    slog.Int("user_id", 123),
)
userLogger.Info("профиль обновлён")
```

### Миграция с других логгеров

#### С logrus на slog

```go
// logrus (до)
import "github.com/sirupsen/logrus"

logrus.WithFields(logrus.Fields{
    "user_id": 123,
    "action":  "login",
}).Info("user logged in")

// slog (после)
import "log/slog"

slog.Info("user logged in",
    slog.Int("user_id", 123),
    slog.String("action", "login"),
)
```

#### С zerolog на slog

```go
// zerolog (до)
import "github.com/rs/zerolog/log"

log.Info().
    Int("user_id", 123).
    Str("action", "login").
    Msg("user logged in")

// slog (после)
slog.Info("user logged in",
    slog.Int("user_id", 123),
    slog.String("action", "login"),
)
```

#### С zap через zapslog

Если у вас большой проект на zap, можно использовать slog как интерфейс с zap backend:

```go
import (
    "log/slog"
    "go.uber.org/zap"
    "go.uber.org/zap/exp/zapslog"
)

// Создаём zap logger
zapLogger, _ := zap.NewProduction()

// Оборачиваем в slog.Handler
handler := zapslog.NewHandler(zapLogger.Core(), nil)
logger := slog.New(handler)

// Используем slog API, но backend — zap
logger.Info("message", slog.String("key", "value"))
```

> 💡 **Рекомендация**: Для новых проектов используйте чистый slog. Миграция существующих проектов на slog — хорошая идея для унификации.

---

## Улучшения net/http (Go 1.22+)

До Go 1.22 стандартный `http.ServeMux` был примитивным — только exact match путей, никаких методов, никаких path parameters. Все использовали сторонние роутеры (chi, gorilla/mux, gin). В Go 1.22 ситуация изменилась.

### Новый синтаксис маршрутизации

**До Go 1.22:**
```go
mux := http.NewServeMux()

// Только путь, метод проверяем вручную
mux.HandleFunc("/users/", func(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case http.MethodGet:
        // Парсим ID вручную
        id := strings.TrimPrefix(r.URL.Path, "/users/")
        getUser(w, r, id)
    case http.MethodPost:
        createUser(w, r)
    default:
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
    }
})
```

**Go 1.22+:**
```go
mux := http.NewServeMux()

// Метод + путь + path parameter
mux.HandleFunc("GET /users/{id}", getUser)
mux.HandleFunc("POST /users", createUser)
mux.HandleFunc("PUT /users/{id}", updateUser)
mux.HandleFunc("DELETE /users/{id}", deleteUser)

// Wildcard для оставшегося пути
mux.HandleFunc("GET /files/{path...}", serveFile)

// Host-based routing
mux.HandleFunc("api.example.com/", apiHandler)
```

### Path parameters

```go
func getUser(w http.ResponseWriter, r *http.Request) {
    // PathValue извлекает параметр из пути
    idStr := r.PathValue("id")

    id, err := strconv.Atoi(idStr)
    if err != nil {
        http.Error(w, "invalid user id", http.StatusBadRequest)
        return
    }

    // ... получить пользователя по id
}

func serveFile(w http.ResponseWriter, r *http.Request) {
    // {path...} захватывает весь оставшийся путь
    filePath := r.PathValue("path")
    // filePath = "documents/report.pdf" для /files/documents/report.pdf
}
```

### Сравнение с ASP.NET Core

| Feature | ASP.NET Core | Go 1.22 net/http |
|---------|--------------|------------------|
| Method routing | `[HttpGet]`, `[HttpPost]` | `"GET /path"`, `"POST /path"` |
| Path parameters | `{id}`, `{id:int}` | `{id}` (только string) |
| Type constraints | `{id:int}`, `{name:alpha}` | Нет (ручная валидация) |
| Catch-all | `{**path}` | `{path...}` |
| Query params | `[FromQuery]` автоматически | `r.URL.Query().Get("key")` |
| Body binding | `[FromBody]` автоматически | `json.Decoder` вручную |
| Model validation | `[Required]`, FluentValidation | Вручную / go-playground/validator |
| Middleware | `app.UseXxx()` pipeline | Wrapping functions |

**ASP.NET Core:**
```csharp
[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    [HttpGet("{id:int}")]
    public async Task<ActionResult<User>> GetUser(int id)
    {
        // id уже распарсен и провалидирован
        var user = await _userService.GetByIdAsync(id);
        return user is null ? NotFound() : Ok(user);
    }

    [HttpPost]
    public async Task<ActionResult<User>> CreateUser([FromBody] CreateUserRequest request)
    {
        // request уже десериализован и провалидирован
        var user = await _userService.CreateAsync(request);
        return CreatedAtAction(nameof(GetUser), new { id = user.Id }, user);
    }
}
```

**Go 1.22:**
```go
func main() {
    mux := http.NewServeMux()

    mux.HandleFunc("GET /api/users/{id}", getUser)
    mux.HandleFunc("POST /api/users", createUser)

    http.ListenAndServe(":8080", mux)
}

func getUser(w http.ResponseWriter, r *http.Request) {
    // Парсинг ID вручную
    idStr := r.PathValue("id")
    id, err := strconv.Atoi(idStr)
    if err != nil {
        http.Error(w, "invalid id", http.StatusBadRequest)
        return
    }

    user, err := userService.GetByID(r.Context(), id)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    if user == nil {
        http.NotFound(w, r)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(user)
}

func createUser(w http.ResponseWriter, r *http.Request) {
    // Десериализация body вручную
    var req CreateUserRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "invalid request body", http.StatusBadRequest)
        return
    }

    // Валидация вручную (или через validator)
    if req.Email == "" {
        http.Error(w, "email is required", http.StatusBadRequest)
        return
    }

    user, err := userService.Create(r.Context(), req)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    w.Header().Set("Location", fmt.Sprintf("/api/users/%d", user.ID))
    w.WriteHeader(http.StatusCreated)
    json.NewEncoder(w).Encode(user)
}
```

### Миграция с chi/gorilla

#### chi → stdlib

**chi:**
```go
import "github.com/go-chi/chi/v5"

r := chi.NewRouter()

r.Use(middleware.Logger)
r.Use(middleware.Recoverer)

r.Get("/users/{id}", func(w http.ResponseWriter, r *http.Request) {
    id := chi.URLParam(r, "id")
    // ...
})

r.Route("/api", func(r chi.Router) {
    r.Get("/health", healthHandler)
})
```

**Go 1.22 stdlib:**
```go
mux := http.NewServeMux()

// Middleware через wrapping
handler := loggingMiddleware(recoveryMiddleware(mux))

mux.HandleFunc("GET /users/{id}", func(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id")  // Вместо chi.URLParam
    // ...
})

mux.HandleFunc("GET /api/health", healthHandler)

http.ListenAndServe(":8080", handler)

// Middleware функции
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        slog.Info("request",
            slog.String("method", r.Method),
            slog.String("path", r.URL.Path),
            slog.Duration("duration", time.Since(start)),
        )
    })
}
```

#### Когда всё ещё нужен chi

- **Middleware ecosystem**: chi.Use() с готовыми middleware
- **Route groups**: Вложенные группы с общими middleware
- **Regex patterns**: Сложные паттерны маршрутизации
- **Существующая кодовая база**: Если проект уже на chi — миграция может не стоить усилий

> 💡 **Рекомендация**: Для новых проектов начните со stdlib Go 1.22+. Добавите chi позже, если действительно понадобятся его features.

---

## Range over integers (Go 1.22)

Одна из самых простых, но долгожданных возможностей.

### До и после

**До Go 1.22:**
```go
// Классический C-style цикл
for i := 0; i < 10; i++ {
    fmt.Println(i)
}

// Для обхода N раз
for i := 0; i < n; i++ {
    doSomething()
}
```

**Go 1.22+:**
```go
// Новый синтаксис
for i := range 10 {
    fmt.Println(i)  // 0, 1, 2, ..., 9
}

// Когда индекс не нужен
for range 5 {
    doSomething()  // Выполнится 5 раз
}
```

### Сравнение с C#

**C# Enumerable.Range:**
```csharp
// LINQ Range
foreach (var i in Enumerable.Range(0, 10))
{
    Console.WriteLine(i);
}

// С условием
foreach (var i in Enumerable.Range(0, 100).Where(x => x % 2 == 0))
{
    Console.WriteLine(i);  // Чётные числа
}
```

**Go:**
```go
// range integer
for i := range 10 {
    fmt.Println(i)
}

// С условием — обычный if внутри
for i := range 100 {
    if i%2 == 0 {
        fmt.Println(i)
    }
}
```

### Ограничения

```go
// ✅ Работает — начало с 0
for i := range 10 { }  // 0..9

// ❌ Не работает — произвольный диапазон
for i := range 5..10 { }  // Syntax error!

// Для произвольного диапазона — классический цикл
for i := 5; i < 10; i++ { }
```

### Use cases

```go
// Повторить действие N раз
for range 3 {
    retry()
}

// Инициализация slice
items := make([]Item, 10)
for i := range 10 {
    items[i] = Item{ID: i}
}

// Генерация тестовых данных
var testUsers []User
for i := range 100 {
    testUsers = append(testUsers, User{
        ID:   i,
        Name: fmt.Sprintf("User %d", i),
    })
}
```

---

## Другие современные возможности

### clear() — очистка коллекций (Go 1.21)

```go
// Очистка map
m := map[string]int{"a": 1, "b": 2, "c": 3}
clear(m)  // m теперь пустой, но capacity сохранён
fmt.Println(len(m))  // 0

// Очистка slice (заполняет zero values)
s := []int{1, 2, 3, 4, 5}
clear(s)  // [0, 0, 0, 0, 0]
fmt.Println(s)  // [0 0 0 0 0]
fmt.Println(len(s))  // 5 — длина не меняется!

// Для полной очистки slice
s = s[:0]  // Или s = nil
```

> ⚠️ **Внимание**: `clear(slice)` не меняет длину — только заполняет zero values. Для очистки slice используйте `s = s[:0]`.

### min/max — встроенные функции (Go 1.21)

```go
// До Go 1.21 — писали вручную или использовали math.Max (только float64)
func max(a, b int) int {
    if a > b {
        return a
    }
    return b
}

// Go 1.21+ — встроенные generic функции
x := max(10, 20)          // 20
y := min(3.14, 2.71)      // 2.71
z := max("apple", "banana")  // "banana" (лексикографически)

// Множество аргументов
biggest := max(1, 5, 3, 9, 2)  // 9
smallest := min(1, 5, 3, 9, 2)  // 1

// Работают с любыми cmp.Ordered типами
type MyInt int
a, b := MyInt(10), MyInt(20)
result := max(a, b)  // MyInt(20)
```

### cmp.Or — значения по умолчанию (Go 1.22)

Функция `cmp.Or` возвращает первое ненулевое значение:

```go
import "cmp"

// До Go 1.22
func getConfig() string {
    if env := os.Getenv("CONFIG"); env != "" {
        return env
    }
    if file := readConfigFile(); file != "" {
        return file
    }
    return "default"
}

// Go 1.22+
func getConfig() string {
    return cmp.Or(
        os.Getenv("CONFIG"),
        readConfigFile(),
        "default",
    )
}

// Примеры использования
name := cmp.Or(user.Nickname, user.Name, "Anonymous")
port := cmp.Or(os.Getenv("PORT"), "8080")
timeout := cmp.Or(config.Timeout, 30*time.Second)
```

> 💡 **Важно**: `cmp.Or` оценивает все аргументы сразу (не lazy). Если нужна lazy evaluation — используйте функции:

```go
// Eager (все вызовы выполняются)
value := cmp.Or(getFromCache(), getFromDB(), getDefault())

// Lazy (только необходимые вызовы)
func getValue() string {
    if v := getFromCache(); v != "" {
        return v
    }
    if v := getFromDB(); v != "" {
        return v
    }
    return getDefault()
}
```

### Iterators (Go 1.23)

Go 1.23 добавил поддержку user-defined iterators через `range over functions`:

```go
// Iterator — функция специального вида
// func(yield func(V) bool)           — для range с одним значением
// func(yield func(K, V) bool)        — для range с двумя значениями

// Пример: итератор по числам Фибоначчи
func Fibonacci(n int) iter.Seq[int] {
    return func(yield func(int) bool) {
        a, b := 0, 1
        for i := 0; i < n; i++ {
            if !yield(a) {
                return
            }
            a, b = b, a+b
        }
    }
}

// Использование
for num := range Fibonacci(10) {
    fmt.Println(num)  // 0, 1, 1, 2, 3, 5, 8, 13, 21, 34
}

// Преобразование в slice
fibs := slices.Collect(Fibonacci(10))
```

**Сравнение с C# IEnumerable:**

| C# | Go 1.23 |
|----|---------|
| `IEnumerable<T>` | `iter.Seq[T]` |
| `IEnumerator<T>` | `func(yield func(T) bool)` |
| `yield return x` | `yield(x)` |
| `yield break` | `return` |

```csharp
// C# iterator
public static IEnumerable<int> Fibonacci(int n)
{
    int a = 0, b = 1;
    for (int i = 0; i < n; i++)
    {
        yield return a;
        (a, b) = (b, a + b);
    }
}

foreach (var num in Fibonacci(10))
{
    Console.WriteLine(num);
}
```

```go
// Go 1.23 iterator
func Fibonacci(n int) iter.Seq[int] {
    return func(yield func(int) bool) {
        a, b := 0, 1
        for i := 0; i < n; i++ {
            if !yield(a) {
                return
            }
            a, b = b, a+b
        }
    }
}

for num := range Fibonacci(10) {
    fmt.Println(num)
}
```

---

## Практические примеры

### Пример 1: Generic Repository

Type-safe repository pattern с использованием generics:

```go
package repository

import (
    "context"
    "database/sql"
    "fmt"
)

// Entity — constraint для сущностей с ID
type Entity interface {
    GetID() int64
    TableName() string
}

// Repository — generic репозиторий
type Repository[T Entity] struct {
    db *sql.DB
}

// NewRepository создаёт новый репозиторий
func NewRepository[T Entity](db *sql.DB) *Repository[T] {
    return &Repository[T]{db: db}
}

// GetByID возвращает сущность по ID
func (r *Repository[T]) GetByID(ctx context.Context, id int64) (*T, error) {
    var entity T
    table := entity.TableName()

    query := fmt.Sprintf("SELECT * FROM %s WHERE id = $1", table)
    row := r.db.QueryRowContext(ctx, query, id)

    if err := scanEntity(row, &entity); err != nil {
        if err == sql.ErrNoRows {
            return nil, nil
        }
        return nil, err
    }

    return &entity, nil
}

// GetAll возвращает все сущности
func (r *Repository[T]) GetAll(ctx context.Context) ([]T, error) {
    var entity T
    table := entity.TableName()

    query := fmt.Sprintf("SELECT * FROM %s", table)
    rows, err := r.db.QueryContext(ctx, query)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var entities []T
    for rows.Next() {
        var e T
        if err := scanEntity(rows, &e); err != nil {
            return nil, err
        }
        entities = append(entities, e)
    }

    return entities, rows.Err()
}

// Delete удаляет сущность по ID
func (r *Repository[T]) Delete(ctx context.Context, id int64) error {
    var entity T
    table := entity.TableName()

    query := fmt.Sprintf("DELETE FROM %s WHERE id = $1", table)
    _, err := r.db.ExecContext(ctx, query, id)
    return err
}

// Использование
type User struct {
    ID    int64
    Name  string
    Email string
}

func (u User) GetID() int64     { return u.ID }
func (u User) TableName() string { return "users" }

type Product struct {
    ID    int64
    Name  string
    Price float64
}

func (p Product) GetID() int64     { return p.ID }
func (p Product) TableName() string { return "products" }

func main() {
    db, _ := sql.Open("postgres", "...")

    // Type-safe репозитории
    userRepo := NewRepository[User](db)
    productRepo := NewRepository[Product](db)

    // Компилятор проверяет типы
    user, _ := userRepo.GetByID(ctx, 1)     // *User
    product, _ := productRepo.GetByID(ctx, 1) // *Product

    users, _ := userRepo.GetAll(ctx)         // []User
    products, _ := productRepo.GetAll(ctx)   // []Product
}
```

### Пример 2: Modern REST API

Полноценное API на Go 1.22+ с использованием современных возможностей:

```go
package main

import (
    "cmp"
    "context"
    "encoding/json"
    "log/slog"
    "net/http"
    "os"
    "slices"
    "strconv"
    "sync"
    "time"
)

// --- Models ---

type User struct {
    ID        int       `json:"id"`
    Name      string    `json:"name"`
    Email     string    `json:"email"`
    CreatedAt time.Time `json:"created_at"`
}

// --- Storage (in-memory для примера) ---

type UserStorage struct {
    mu     sync.RWMutex
    users  map[int]User
    nextID int
}

func NewUserStorage() *UserStorage {
    return &UserStorage{
        users:  make(map[int]User),
        nextID: 1,
    }
}

func (s *UserStorage) Create(user User) User {
    s.mu.Lock()
    defer s.mu.Unlock()

    user.ID = s.nextID
    user.CreatedAt = time.Now()
    s.users[user.ID] = user
    s.nextID++
    return user
}

func (s *UserStorage) GetByID(id int) (User, bool) {
    s.mu.RLock()
    defer s.mu.RUnlock()

    user, ok := s.users[id]
    return user, ok
}

func (s *UserStorage) GetAll() []User {
    s.mu.RLock()
    defer s.mu.RUnlock()

    users := make([]User, 0, len(s.users))
    for _, user := range s.users {
        users = append(users, user)
    }

    // Сортировка с помощью slices (Go 1.21+)
    slices.SortFunc(users, func(a, b User) int {
        return cmp.Compare(a.ID, b.ID)
    })

    return users
}

func (s *UserStorage) Delete(id int) bool {
    s.mu.Lock()
    defer s.mu.Unlock()

    if _, ok := s.users[id]; !ok {
        return false
    }
    delete(s.users, id)
    return true
}

// --- Handlers ---

type UserHandler struct {
    storage *UserStorage
    logger  *slog.Logger
}

func NewUserHandler(storage *UserStorage, logger *slog.Logger) *UserHandler {
    return &UserHandler{
        storage: storage,
        logger:  logger.With("component", "UserHandler"),
    }
}

func (h *UserHandler) List(w http.ResponseWriter, r *http.Request) {
    users := h.storage.GetAll()

    h.logger.InfoContext(r.Context(), "listing users",
        slog.Int("count", len(users)),
    )

    writeJSON(w, http.StatusOK, users)
}

func (h *UserHandler) Get(w http.ResponseWriter, r *http.Request) {
    // Go 1.22: PathValue для извлечения параметров
    idStr := r.PathValue("id")
    id, err := strconv.Atoi(idStr)
    if err != nil {
        h.logger.WarnContext(r.Context(), "invalid user id",
            slog.String("id", idStr),
        )
        writeError(w, http.StatusBadRequest, "invalid user id")
        return
    }

    user, ok := h.storage.GetByID(id)
    if !ok {
        writeError(w, http.StatusNotFound, "user not found")
        return
    }

    h.logger.InfoContext(r.Context(), "user retrieved",
        slog.Int("user_id", id),
    )

    writeJSON(w, http.StatusOK, user)
}

func (h *UserHandler) Create(w http.ResponseWriter, r *http.Request) {
    var input struct {
        Name  string `json:"name"`
        Email string `json:"email"`
    }

    if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
        writeError(w, http.StatusBadRequest, "invalid request body")
        return
    }

    // Валидация с cmp.Or для default values
    name := cmp.Or(input.Name, "Anonymous")
    if input.Email == "" {
        writeError(w, http.StatusBadRequest, "email is required")
        return
    }

    user := h.storage.Create(User{
        Name:  name,
        Email: input.Email,
    })

    h.logger.InfoContext(r.Context(), "user created",
        slog.Int("user_id", user.ID),
        slog.String("email", user.Email),
    )

    w.Header().Set("Location", "/api/users/"+strconv.Itoa(user.ID))
    writeJSON(w, http.StatusCreated, user)
}

func (h *UserHandler) Delete(w http.ResponseWriter, r *http.Request) {
    idStr := r.PathValue("id")
    id, err := strconv.Atoi(idStr)
    if err != nil {
        writeError(w, http.StatusBadRequest, "invalid user id")
        return
    }

    if !h.storage.Delete(id) {
        writeError(w, http.StatusNotFound, "user not found")
        return
    }

    h.logger.InfoContext(r.Context(), "user deleted",
        slog.Int("user_id", id),
    )

    w.WriteHeader(http.StatusNoContent)
}

// --- Helpers ---

func writeJSON(w http.ResponseWriter, status int, data any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(data)
}

func writeError(w http.ResponseWriter, status int, message string) {
    writeJSON(w, status, map[string]string{"error": message})
}

// --- Middleware ---

func loggingMiddleware(logger *slog.Logger) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            start := time.Now()

            // Wrap ResponseWriter для захвата status code
            wrapped := &responseWriter{ResponseWriter: w, status: http.StatusOK}

            next.ServeHTTP(wrapped, r)

            logger.InfoContext(r.Context(), "request completed",
                slog.String("method", r.Method),
                slog.String("path", r.URL.Path),
                slog.Int("status", wrapped.status),
                slog.Duration("duration", time.Since(start)),
            )
        })
    }
}

type responseWriter struct {
    http.ResponseWriter
    status int
}

func (rw *responseWriter) WriteHeader(code int) {
    rw.status = code
    rw.ResponseWriter.WriteHeader(code)
}

func recoveryMiddleware(logger *slog.Logger) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            defer func() {
                if err := recover(); err != nil {
                    logger.ErrorContext(r.Context(), "panic recovered",
                        slog.Any("error", err),
                    )
                    writeError(w, http.StatusInternalServerError, "internal server error")
                }
            }()
            next.ServeHTTP(w, r)
        })
    }
}

// --- Main ---

func main() {
    // Настройка логгера (Go 1.21+)
    logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
        Level: slog.LevelInfo,
    }))

    // Инициализация
    storage := NewUserStorage()
    handler := NewUserHandler(storage, logger)

    // Маршрутизация (Go 1.22+)
    mux := http.NewServeMux()

    mux.HandleFunc("GET /api/users", handler.List)
    mux.HandleFunc("GET /api/users/{id}", handler.Get)
    mux.HandleFunc("POST /api/users", handler.Create)
    mux.HandleFunc("DELETE /api/users/{id}", handler.Delete)

    // Health check
    mux.HandleFunc("GET /health", func(w http.ResponseWriter, r *http.Request) {
        writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
    })

    // Middleware chain
    var h http.Handler = mux
    h = loggingMiddleware(logger)(h)
    h = recoveryMiddleware(logger)(h)

    // Запуск сервера
    addr := cmp.Or(os.Getenv("ADDR"), ":8080")
    logger.Info("starting server", slog.String("addr", addr))

    if err := http.ListenAndServe(addr, h); err != nil {
        logger.Error("server failed", slog.Any("error", err))
        os.Exit(1)
    }
}
```

### Пример 3: Миграционный чек-лист

Пошаговая миграция существующего Go-проекта на современные возможности:

```markdown
## Чек-лист модернизации Go-проекта

### Подготовка
- [ ] Обновить Go до версии 1.22+ (`go version`)
- [ ] Обновить go.mod: `go mod edit -go=1.22`
- [ ] Запустить `go mod tidy`

### Этап 1: Базовые улучшения (низкий риск)

#### min/max (Go 1.21)
- [ ] Найти: `if a > b { return a } return b`
- [ ] Заменить на: `return max(a, b)`
- [ ] Удалить самописные функции min/max

#### clear() (Go 1.21)
- [ ] Найти: `for k := range m { delete(m, k) }`
- [ ] Заменить на: `clear(m)`

#### range over int (Go 1.22)
- [ ] Найти: `for i := 0; i < n; i++` где используется только индекс
- [ ] Заменить на: `for i := range n`

### Этап 2: slices/maps пакеты (средний риск)

#### slices
- [ ] Найти ручные циклы сортировки
- [ ] Заменить на: `slices.Sort()` или `slices.SortFunc()`
- [ ] Найти: `for _, item := range slice { if item == target { return true } }`
- [ ] Заменить на: `slices.Contains(slice, target)`

#### maps
- [ ] Найти ручное копирование maps
- [ ] Заменить на: `maps.Clone()` или `maps.Copy()`

### Этап 3: slog (средний риск)

- [ ] Заменить `log.Printf` на `slog.Info`
- [ ] Если используется logrus/zerolog/zap:
  - [ ] Создать adapter или мигрировать постепенно
  - [ ] Обновить middleware логирования

### Этап 4: net/http 1.22 routing (высокий риск)

⚠️ Только для проектов, готовых к изменению HTTP-слоя

- [ ] Если используется chi:
  - [ ] Оценить необходимость (middleware, groups?)
  - [ ] Если можно — заменить на stdlib
  - [ ] `chi.URLParam(r, "id")` → `r.PathValue("id")`

- [ ] Если используется gorilla/mux:
  - [ ] gorilla/mux deprecated — миграция рекомендуется
  - [ ] `mux.Vars(r)["id"]` → `r.PathValue("id")`

### Этап 5: Generics (низкий-средний риск)

- [ ] Найти дублирующийся код для разных типов
- [ ] Оценить: упростят ли generics читаемость?
- [ ] Если да — рефакторинг с generic функциями/типами
- [ ] НЕ добавлять generics "на всякий случай"

### Верификация

- [ ] `go build ./...` — компиляция без ошибок
- [ ] `go test ./...` — все тесты проходят
- [ ] `go vet ./...` — нет warnings
- [ ] golangci-lint — нет новых issues
```

---

## Чек-лист

После изучения этого раздела вы должны уметь:

### Generics
- [ ] Писать generic функции с type parameters
- [ ] Использовать constraints: `any`, `comparable`, `cmp.Ordered`
- [ ] Создавать custom constraints с type sets и union types
- [ ] Понимать, когда использовать generics, а когда — нет
- [ ] Знать о performance implications (GCShape stenciling)

### slices/maps пакеты
- [ ] Использовать `slices.Sort`, `slices.SortFunc`, `slices.SortStableFunc`
- [ ] Использовать `slices.Contains`, `slices.Index`, `slices.IndexFunc`
- [ ] Использовать `slices.Clone`, `slices.Compact`, `slices.Reverse`
- [ ] Использовать `maps.Clone`, `maps.Copy`, `maps.Equal`
- [ ] Понимать различия с LINQ (in-place операции!)

### log/slog
- [ ] Настроить slog для production (JSONHandler)
- [ ] Использовать structured logging с типизированными атрибутами
- [ ] Интегрировать slog с context для tracing
- [ ] Знать, как мигрировать с logrus/zerolog/zap

### net/http (Go 1.22+)
- [ ] Использовать method routing: `"GET /path"`, `"POST /path"`
- [ ] Извлекать path parameters через `r.PathValue("param")`
- [ ] Использовать wildcards: `{path...}`
- [ ] Принять решение: stdlib vs chi для конкретного проекта
- [ ] Мигрировать с chi/gorilla если необходимо

### Range over integers
- [ ] Использовать `for i := range n` синтаксис
- [ ] Использовать `for range n` когда индекс не нужен
- [ ] Понимать ограничения (только с нуля)

### Другие возможности
- [ ] Использовать `clear()` для очистки maps
- [ ] Использовать `min/max` built-ins
- [ ] Использовать `cmp.Or` для значений по умолчанию
- [ ] Понимать основы iterators (Go 1.23)

---

## Следующие шаги

Переходите к [6.3 Инструменты](./03_tools.md), где рассмотрим:
- golangci-lint: обязательная настройка линтеров
- staticcheck: глубокий статический анализ
- govulncheck: проверка уязвимостей в зависимостях
- Профилирование и оптимизация

---

**Вопросы?** Открой issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Назад: 6.1 Код и архитектура](./01_code_architecture.md) | [Вперёд: 6.3 Инструменты →](./03_tools.md)
