# Дженерики (Generics)

---

## Введение

> 💡 **Для C# разработчиков**: Go получил дженерики в версии 1.18 (2022). Синтаксис и модель отличаются от C#: нет `where T : class`, нет `new()`, нет variance (`IEnumerable<out T>`), нет specialization. Зато есть `interface` как constraint — любой тип, включая встроенный.

Дженерики в Go решают ту же задачу, что и в C#: писать код, который работает с разными типами без дублирования. Но реализация другая.

**C#**:
```csharp
public T Max<T>(T a, T b) where T : IComparable<T>
    => a.CompareTo(b) >= 0 ? a : b;
```

**Go**:
```go
import "cmp"

func Max[T cmp.Ordered](a, b T) T {
    if a >= b {
        return a
    }
    return b
}
```

---

## Синтаксис type parameters

Type parameters объявляются в квадратных скобках `[T constraint]` сразу после имени функции или типа.

```go
// Функция с одним type parameter
func Identity[T any](v T) T {
    return v
}

// Функция с несколькими type parameters
func Map[T, U any](slice []T, fn func(T) U) []U {
    result := make([]U, len(slice))
    for i, v := range slice {
        result[i] = fn(v)
    }
    return result
}
```

### Вывод типов (Type Inference)

Go часто выводит тип автоматически — как `var x = 42` выводит `int`:

```go
// Явное указание типа
nums := Map[int, string]([]int{1, 2, 3}, strconv.Itoa)

// Вывод типа — компилятор сам определяет T=int, U=string
nums := Map([]int{1, 2, 3}, strconv.Itoa)
```

**Сравнение с C#:**
```csharp
// C# тоже выводит типы
var result = list.Select(x => x.ToString()); // T выведен из list

// Явное указание — редко нужно
var result = list.Select<int, string>(x => x.ToString());
```

---

## Constraints (ограничения типов)

Constraint — это интерфейс, который описывает, что умеет тип.

### Встроенные constraints

```go
// any — любой тип (псевдоним для interface{})
func Print[T any](v T) { fmt.Println(v) }

// comparable — типы, которые можно сравнивать через == и !=
// (числа, строки, указатели, массивы фиксированного размера, struct из comparable полей)
func Contains[T comparable](slice []T, target T) bool {
    for _, v := range slice {
        if v == target {
            return true
        }
    }
    return false
}
```

### Пакет constraints (устарел) и cmp.Ordered

До Go 1.21 использовался отдельный пакет `golang.org/x/exp/constraints`. Начиная с Go 1.21 встроен в stdlib пакет `cmp`:

```go
import "cmp"

// cmp.Ordered — числовые типы и строки (поддерживают <, >, <=, >=)
func Min[T cmp.Ordered](a, b T) T {
    if a < b {
        return a
    }
    return b
}

// Использование
fmt.Println(Min(3, 5))       // 3
fmt.Println(Min(3.14, 2.71)) // 2.71
fmt.Println(Min("b", "a"))   // "a"
```

Определение `cmp.Ordered` в stdlib:
```go
type Ordered interface {
    ~int | ~int8 | ~int16 | ~int32 | ~int64 |
    ~uint | ~uint8 | ~uint16 | ~uint32 | ~uint64 | ~uintptr |
    ~float32 | ~float64 |
    ~string
}
```

### Тильда `~` — тип-множество с underlying type

`~int` означает "любой тип, у которого underlying type — int":

```go
type UserID int
type ProductID int

func Double[T ~int](v T) T {
    return v * 2
}

var uid UserID = 42
var pid ProductID = 10

fmt.Println(Double(uid)) // 84 — работает, UserID underlying type = int
fmt.Println(Double(pid)) // 20 — работает
```

**Аналог в C#** — нет прямого аналога. Ближайшее: `where T : struct` или numeric interfaces из .NET 7+ (`INumber<T>`).

### Собственные constraints

```go
// Constraint через interface
type Stringer interface {
    String() string
}

func PrintAll[T Stringer](items []T) {
    for _, item := range items {
        fmt.Println(item.String())
    }
}

// Constraint с type set (union)
type Integer interface {
    ~int | ~int8 | ~int16 | ~int32 | ~int64
}

func Sum[T Integer](nums []T) T {
    var total T
    for _, n := range nums {
        total += n
    }
    return total
}

// Комбинированный constraint: и методы, и тип
type Numeric interface {
    ~int | ~float64
    String() string  // должен иметь метод String()
}
```

**Сравнение с C#:**

| C# | Go |
|----|----|
| `where T : IComparable<T>` | `[T interface{ ... }]` или `[T cmp.Ordered]` |
| `where T : class` | нет аналога |
| `where T : struct` | нет прямого аналога |
| `where T : new()` | нет аналога |
| `where T : INumber<T>` (.NET 7+) | `[T cmp.Ordered]` или `[T Integer]` |
| Несколько: `where T : class, IFoo` | `[T interface{ ~int; Foo() }]` |

---

## Generic функции

### Стандартные паттерны

```go
// Map — преобразование элементов
func Map[T, U any](slice []T, fn func(T) U) []U {
    result := make([]U, len(slice))
    for i, v := range slice {
        result[i] = fn(v)
    }
    return result
}

// Filter — фильтрация
func Filter[T any](slice []T, pred func(T) bool) []T {
    var result []T
    for _, v := range slice {
        if pred(v) {
            result = append(result, v)
        }
    }
    return result
}

// Reduce — свёртка
func Reduce[T, U any](slice []T, initial U, fn func(U, T) U) U {
    acc := initial
    for _, v := range slice {
        acc = fn(acc, v)
    }
    return acc
}
```

```go
// Использование
nums := []int{1, 2, 3, 4, 5}

doubled := Map(nums, func(n int) int { return n * 2 })
// [2, 4, 6, 8, 10]

evens := Filter(nums, func(n int) bool { return n%2 == 0 })
// [2, 4]

sum := Reduce(nums, 0, func(acc, n int) int { return acc + n })
// 15

// Цепочка: сумма квадратов чётных чисел
result := Reduce(
    Map(
        Filter(nums, func(n int) bool { return n%2 == 0 }),
        func(n int) int { return n * n },
    ),
    0,
    func(acc, n int) int { return acc + n },
)
// 20 (= 4 + 16)
```

**Сравнение с C# LINQ:**
```csharp
var result = nums
    .Where(n => n % 2 == 0)
    .Select(n => n * n)
    .Sum();
// 20
```

> 💡 **Идиома Go**: В Go нет встроенного LINQ. Generic-хелперы пишутся вручную или берутся из библиотек (`samber/lo`). С Go 1.23 появились `slices.Collect` и iterators — паттерны меняются. Для простых случаев цикл `for` читается лучше, чем вложенные Map/Filter.

### Keys и Values для map

```go
func Keys[K comparable, V any](m map[K]V) []K {
    keys := make([]K, 0, len(m))
    for k := range m {
        keys = append(keys, k)
    }
    return keys
}

func Values[K comparable, V any](m map[K]V) []V {
    vals := make([]V, 0, len(m))
    for _, v := range m {
        vals = append(vals, v)
    }
    return vals
}

// Pointer
func Ptr[T any](v T) *T {
    return &v
}
```

### Must — panic wrapper для тестов

```go
// Must — для случаев, когда ошибка не ожидается (тесты, init)
func Must[T any](v T, err error) T {
    if err != nil {
        panic(err)
    }
    return v
}

// Использование
cfg := Must(config.Load("app.yaml"))  // паникует если ошибка
```

---

## Generic типы (параметризованные структуры)

```go
// Stack — типобезопасный стек
type Stack[T any] struct {
    items []T
}

func (s *Stack[T]) Push(v T) {
    s.items = append(s.items, v)
}

func (s *Stack[T]) Pop() (T, bool) {
    if len(s.items) == 0 {
        var zero T
        return zero, false
    }
    last := len(s.items) - 1
    v := s.items[last]
    s.items = s.items[:last]
    return v, true
}

func (s *Stack[T]) Len() int {
    return len(s.items)
}
```

```go
// Использование
s := Stack[int]{}
s.Push(1)
s.Push(2)
v, ok := s.Pop() // 2, true
```

**Сравнение с C#:**
```csharp
var stack = new Stack<int>();
stack.Push(1);
stack.Push(2);
var v = stack.Pop(); // 2
```

### Result — обёртка для возврата значения или ошибки

```go
// Альтернатива множественному возврату в API
type Result[T any] struct {
    value T
    err   error
}

func Ok[T any](v T) Result[T]       { return Result[T]{value: v} }
func Err[T any](err error) Result[T] { return Result[T]{err: err} }

func (r Result[T]) Unwrap() (T, error) { return r.value, r.err }
func (r Result[T]) IsOk() bool          { return r.err == nil }
```

> 💡 **Идиома Go**: В реальном коде этот паттерн не распространён — идиоматично возвращать `(T, error)` напрямую. `Result[T]` уместен как тип в канале или слайсе результатов параллельных операций.

### Pair и Optional

```go
type Pair[A, B any] struct {
    First  A
    Second B
}

func Zip[A, B any](as []A, bs []B) []Pair[A, B] {
    n := min(len(as), len(bs))
    result := make([]Pair[A, B], n)
    for i := range n {
        result[i] = Pair[A, B]{as[i], bs[i]}
    }
    return result
}

// Optional — для случаев когда нужно отличить "нет значения" от zero value
type Optional[T any] struct {
    value    T
    hasValue bool
}

func Some[T any](v T) Optional[T]    { return Optional[T]{value: v, hasValue: true} }
func None[T any]() Optional[T]       { return Optional[T]{} }
func (o Optional[T]) Get() (T, bool) { return o.value, o.hasValue }
```

### Typed Set

```go
type Set[T comparable] struct {
    items map[T]struct{}
}

func NewSet[T comparable](items ...T) Set[T] {
    s := Set[T]{items: make(map[T]struct{}, len(items))}
    for _, item := range items {
        s.items[item] = struct{}{}
    }
    return s
}

func (s *Set[T]) Add(v T)          { s.items[v] = struct{}{} }
func (s *Set[T]) Remove(v T)       { delete(s.items, v) }
func (s *Set[T]) Contains(v T) bool { _, ok := s.items[v]; return ok }
func (s *Set[T]) Len() int          { return len(s.items) }

func (s *Set[T]) Intersect(other Set[T]) Set[T] {
    result := NewSet[T]()
    for k := range s.items {
        if other.Contains(k) {
            result.Add(k)
        }
    }
    return result
}
```

```go
// Использование
roles := NewSet("admin", "editor")
roles.Add("viewer")
fmt.Println(roles.Contains("admin")) // true
fmt.Println(roles.Len())             // 3
```

**Сравнение с C#:**
```csharp
var roles = new HashSet<string> { "admin", "editor" };
roles.Add("viewer");
Console.WriteLine(roles.Contains("admin")); // True

var intersection = roles.Intersect(otherRoles).ToHashSet();
```

---

## Ограничения Go generics

### Нет specialization

В C# компилятор может генерировать специализированный IL для value types. В Go дженерики работают через GC Shape Stenciling — типы с одинаковым "shape" (указатель vs не-указатель) используют одну реализацию.

```csharp
// C# — JIT создаёт отдельный код для List<int> и List<string>
var ints = new List<int>();    // specialized for int
var strs = new List<string>(); // specialized for string
```

```go
// Go — нет гарантии отдельной реализации для каждого типа
// Производительность: могут быть небольшие накладные расходы
s1 := Stack[int]{}
s2 := Stack[string]{}
```

> 💡 На практике разница в производительности минимальна. Для hot path с primitive types лучше написать конкретную реализацию вручную.

### Нет variance (ковариантность / контравариантность)

```csharp
// C# — IEnumerable<T> ковариантен (out T)
IEnumerable<Animal> animals = new List<Dog>(); // OK

// C# — Action<T> контравариантен (in T)
Action<Animal> act = (Dog d) => { };  // OK
```

```go
// Go — нет variance
// Stack[Dog] нельзя присвоить Stack[Animal], даже если Dog реализует Animal
type Animal interface{ Sound() string }
type Dog struct{}
func (d Dog) Sound() string { return "Woof" }

var dogs Stack[Dog]
// var animals Stack[Animal] = dogs  // ❌ не компилируется
```

Обходной путь — явное преобразование или использование `[]Animal`:

```go
func ToAnimalSlice[T Animal](items []T) []Animal {
    result := make([]Animal, len(items))
    for i, v := range items {
        result[i] = v
    }
    return result
}
```

### Нет `new()` constraint и дженерик-методов с доп. параметрами

```csharp
// C# — можно создать экземпляр T
T Create<T>() where T : new() => new T();
```

```go
// Go — нет способа вызвать "конструктор" T напрямую
// Решение: принять фабричную функцию
func Create[T any](factory func() T) T {
    return factory()
}

user := Create(func() User { return User{Name: "Alice"} })
```

### Нет дженерик-методов на типах

В Go нельзя добавить type parameter к методу (только к функции или типу):

```go
type Container struct{}

// ❌ Не компилируется — методы не могут иметь свои type parameters
// func (c *Container) Get[T any]() T { ... }

// ✅ Решение 1: вынести в функцию
func Get[T any](c *Container) T { ... }

// ✅ Решение 2: параметризовать тип
type TypedContainer[T any] struct{ value T }
func (c *TypedContainer[T]) Get() T { return c.value }
```

---

## Когда generics, когда `interface{}`

| Ситуация | Выбор |
|----------|-------|
| Типобезопасная коллекция (`Stack[int]`) | Generics |
| Алгоритм над разными типами (`Sort`, `Map`) | Generics |
| Поведение через интерфейс (`io.Writer`, `http.Handler`) | Interface |
| Разнородные типы в runtime (`any`, reflection) | `interface{}` / `any` |
| Конвертация типов в compile time | Generics |
| Plugin-архитектура, динамическая диспетчеризация | Interface |

```go
// ✅ Generics — compile-time safety, нет boxing
func Sum[T cmp.Ordered](nums []T) T {
    var total T
    for _, n := range nums {
        total += n
    }
    return total
}

// ✅ Interface — поведенческий полиморфизм
type Writer interface {
    Write([]byte) (int, error)
}

func WriteAll(w Writer, data [][]byte) error {
    for _, chunk := range data {
        if _, err := w.Write(chunk); err != nil {
            return err
        }
    }
    return nil
}

// ❌ Не стоит — interface{} теряет типы, дешевле написать конкретный тип
func BadSum(nums []interface{}) interface{} { ... }
```

> 💡 **Идиома Go**: Предпочитай конкретные типы. Используй generics, если алгоритм действительно не зависит от типа. Используй interface, если важно поведение. Избегай `any` там, где можно получить compile-time safety.

---

## Паттерны: пакет `slices` и `maps` (Go 1.21+)

С Go 1.21 в stdlib добавлены generic-пакеты, которые заменяют ручные хелперы:

```go
import (
    "slices"
    "maps"
)

nums := []int{3, 1, 4, 1, 5, 9, 2, 6}

// Сортировка
slices.Sort(nums)                          // [1, 1, 2, 3, 4, 5, 6, 9]
slices.SortFunc(nums, func(a, b int) int { return b - a }) // убывание

// Поиск
idx, found := slices.BinarySearch(nums, 5) // индекс и наличие
has := slices.Contains(nums, 4)             // true
idx2 := slices.Index(nums, 4)              // первый индекс

// Трансформации
unique := slices.Compact(nums)             // убрать соседние дубликаты
reversed := slices.Clone(nums)
slices.Reverse(reversed)

// maps
m := map[string]int{"a": 1, "b": 2}
keys := slices.Collect(maps.Keys(m))       // []string (порядок не гарантирован)
vals := slices.Collect(maps.Values(m))     // []int
maps.Copy(dst, src)                        // скопировать все пары
maps.DeleteFunc(m, func(k string, v int) bool { return v == 0 }) // удалить по условию
```

**Сравнение с C# LINQ:**

| C# LINQ | Go (slices/maps) |
|---------|-----------------|
| `list.Sort()` | `slices.Sort(s)` |
| `list.OrderBy(x => x.Name)` | `slices.SortFunc(s, cmp.Compare)` |
| `list.Contains(x)` | `slices.Contains(s, x)` |
| `list.IndexOf(x)` | `slices.Index(s, x)` |
| `list.Distinct()` | `slices.Compact(slices.Sorted(...))` |
| `dict.Keys` | `maps.Keys(m)` (iterator) |
| `dict.Values` | `maps.Values(m)` (iterator) |

---

## Итераторы и range функции (Go 1.23+)

Go 1.23 добавил поддержку кастомных функций в `range`:

```go
// iter.Seq — функция, которую можно использовать в range
import "iter"

func Fibonacci() iter.Seq[int] {
    return func(yield func(int) bool) {
        a, b := 0, 1
        for {
            if !yield(a) {
                return
            }
            a, b = b, a+b
        }
    }
}

// Использование
for n := range Fibonacci() {
    if n > 100 {
        break
    }
    fmt.Println(n)
}
```

```go
// iter.Seq2 — пары ключ-значение
func Enumerate[T any](s []T) iter.Seq2[int, T] {
    return func(yield func(int, T) bool) {
        for i, v := range s {
            if !yield(i, v) {
                return
            }
        }
    }
}

for i, v := range Enumerate([]string{"a", "b", "c"}) {
    fmt.Printf("%d: %s\n", i, v) // 0: a, 1: b, 2: c
}
```

**Сравнение с C# IEnumerable / yield return:**
```csharp
IEnumerable<int> Fibonacci()
{
    int a = 0, b = 1;
    while (true)
    {
        yield return a;
        (a, b) = (b, a + b);
    }
}

foreach (var n in Fibonacci().TakeWhile(n => n <= 100))
    Console.WriteLine(n);
```

---

## Сравнительная таблица: C# generics vs Go generics

| Аспект | C# | Go |
|--------|----|----|
| Синтаксис | `List<T>`, `Func<T, TResult>` | `[]T`, `func(T) U` |
| Constraints | `where T : IComparable<T>` | `[T cmp.Ordered]` |
| Type union | нет (до C# 9) | `~int \| ~string` |
| Variance | `IEnumerable<out T>`, `Action<in T>` | нет |
| Specialization | есть (JIT для value types) | GC Shape Stenciling |
| `new()` constraint | `where T : new()` | нет, нужна фабрика |
| Generic методы | `T Foo<T>(...)` на любом классе | только функции и типы |
| Stdlib generics | `List<T>`, `Dictionary<K,V>`, LINQ | `slices`, `maps`, `cmp` |
| Inference | полный вывод в большинстве случаев | вывод из аргументов функции |

---

## Практические примеры

### Пример 1: Типобезопасный кэш

```go
type Cache[K comparable, V any] struct {
    mu    sync.RWMutex
    items map[K]V
}

func NewCache[K comparable, V any]() *Cache[K, V] {
    return &Cache[K, V]{items: make(map[K]V)}
}

func (c *Cache[K, V]) Set(key K, val V) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.items[key] = val
}

func (c *Cache[K, V]) Get(key K) (V, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    v, ok := c.items[key]
    return v, ok
}

func (c *Cache[K, V]) GetOrSet(key K, factory func() V) V {
    c.mu.Lock()
    defer c.mu.Unlock()
    if v, ok := c.items[key]; ok {
        return v
    }
    v := factory()
    c.items[key] = v
    return v
}
```

```go
// Использование
userCache := NewCache[int, User]()
userCache.Set(1, User{Name: "Alice"})

user, ok := userCache.Get(1) // User{Name: "Alice"}, true
```

### Пример 2: Batch processor

```go
// Обработка элементов пачками — частый паттерн при работе с БД/API
func Batch[T any](items []T, size int, fn func([]T) error) error {
    for i := 0; i < len(items); i += size {
        end := min(i+size, len(items))
        if err := fn(items[i:end]); err != nil {
            return fmt.Errorf("batch starting at %d: %w", i, err)
        }
    }
    return nil
}

// Использование: вставка в БД пачками по 100
users := fetchUsers()
err := Batch(users, 100, func(batch []User) error {
    return db.InsertUsers(ctx, batch)
})
```

**C# аналог:**
```csharp
// C# — через Chunk (LINQ, .NET 6+)
foreach (var batch in users.Chunk(100))
{
    await db.InsertUsersAsync(batch);
}
```

### Пример 3: Pipeline с каналами

```go
// Типобезопасный pipeline через каналы
func Generate[T any](ctx context.Context, items ...T) <-chan T {
    out := make(chan T)
    go func() {
        defer close(out)
        for _, item := range items {
            select {
            case out <- item:
            case <-ctx.Done():
                return
            }
        }
    }()
    return out
}

func Transform[T, U any](ctx context.Context, in <-chan T, fn func(T) U) <-chan U {
    out := make(chan U)
    go func() {
        defer close(out)
        for v := range in {
            select {
            case out <- fn(v):
            case <-ctx.Done():
                return
            }
        }
    }()
    return out
}

// Использование
ctx := context.Background()
nums := Generate(ctx, 1, 2, 3, 4, 5)
doubled := Transform(ctx, nums, func(n int) int { return n * 2 })
for v := range doubled {
    fmt.Println(v) // 2, 4, 6, 8, 10
}
```

---

## Ссылки

- [Go Blog: An Introduction to Generics](https://go.dev/blog/intro-generics)
- [Go Blog: When To Use Generics](https://go.dev/blog/when-generics)
- [Пакет cmp](https://pkg.go.dev/cmp)
- [Пакет slices](https://pkg.go.dev/slices)
- [Пакет maps](https://pkg.go.dev/maps)
- [Пакет iter (Go 1.23+)](https://pkg.go.dev/iter)
