# 1.2 Синтаксис и базовые концепции (сравнение с C#)

## Содержание
- [Введение](#введение)
- [1. Базовый синтаксис](#1-базовый-синтаксис)
- [2. Типы данных](#2-типы-данных)
- [3. Коллекции](#3-коллекции)
  - [Массивы](#массивы)
  - [Слайсы](#слайсы-slices)
  - [Мапы](#мапы-maps)
  - [Пакеты slices, maps и cmp (Go 1.21+)](#пакеты-slices-maps-и-cmp-go-121)
  - [Современные встроенные функции (Go 1.21+)](#современные-встроенные-функции-go-121)
  - [Iterators (Go 1.23)](#iterators-go-123)
- [4. Управляющие конструкции](#4-управляющие-конструкции)
  - [Range over integers (Go 1.22)](#range-over-integers-go-122)
- [5. Функции и defer](#5-функции-и-defer)
- [6. Указатели](#6-указатели)
- [7. Структуры](#7-структуры-structs)
- [8. Интерфейсы](#8-интерфейсы)
- [9. Пакеты и импорты](#9-пакеты-и-импорты)
- [10. Сравнение с C#: Чего НЕТ в Go](#10-сравнение-с-c-чего-нет-в-go)
- [11. Практические примеры](#11-практические-примеры)
- [Задания для практики](#задания-для-практики)
- [Чек-лист](#чек-лист)

---

## Введение

Go — минималистичный язык с простым синтаксисом. Если вы приходите из C#, многие концепции покажутся знакомыми, но есть фундаментальные отличия в философии и подходах.

**Философия Go**:
- Простота > Сложность
- Explicit > Implicit
- Composition > Inheritance
- Меньше магии, больше ясности

> **📌 Важно для производительности**: В этом разделе вы найдете подробное описание работы коллекций (слайсы, мапы, строки) в контексте GC и производительности. Для быстрого справочника по оптимизации см. [02a_collections_performance_cheatsheet.md](02a_collections_performance_cheatsheet.md)

---

## 1. Базовый синтаксис

### Структура программы

**C#**:
```csharp
using System;

namespace MyApp
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Hello, World!");
        }
    }
}
```

**Go**:
```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
```

**Ключевые отличия**:
- В Go нет `namespace` — используются **пакеты** (packages)
- Точка входа — функция `main` в пакете `main`
- Нет классов — только функции и структуры
- Фигурные скобки `{` должны быть на той же строке
- Нет точки с запятой `;` в конце строк (добавляется автоматически)

---

### Объявление переменных

#### Полное объявление

**C#**:
```csharp
int age = 30;
string name = "Alice";
bool isActive = true;
```

**Go**:
```go
var age int = 30
var name string = "Alice"
var isActive bool = true
```

#### Краткое объявление (тип выводится автоматически)

**C#**:
```csharp
var age = 30;
var name = "Alice";
```

**Go**:
```go
age := 30
name := "Alice"
```

**Важно**: `:=` работает **только внутри функций**, не на уровне пакета.

#### Множественное объявление

**C#**:
```csharp
int x = 1, y = 2, z = 3;
```

**Go**:
```go
var x, y, z int = 1, 2, 3

// Или короче
x, y, z := 1, 2, 3

// Разные типы
var (
    age  int    = 30
    name string = "Bob"
    rate float64 = 99.5
)
```

#### Zero values (значения по умолчанию)

В Go все переменные инициализируются "нулевыми" значениями, в отличие от C# где могут быть неинициализированы.

**Go**:
```go
var i int       // 0
var f float64   // 0.0
var b bool      // false
var s string    // "" (пустая строка)
var p *int      // nil
```

**C#**:
```csharp
int i;          // Ошибка компиляции, если использовать без инициализации
int i = default; // 0
```

---

### Константы

**C#**:
```csharp
const int MaxUsers = 100;
const string AppName = "MyApp";
```

**Go**:
```go
const MaxUsers = 100
const AppName = "MyApp"

// Группировка констант
const (
    StatusOK       = 200
    StatusNotFound = 404
    StatusError    = 500
)
```

**Особенность Go**: константы вычисляются на этапе компиляции и могут быть типизированными или нетипизированными.

```go
const Pi = 3.14159 // Нетипизированная (может использоваться как float32 или float64)

const TypedPi float64 = 3.14159 // Типизированная
```

---

## 2. Типы данных

### Базовые типы

| Категория | C# | Go |
|-----------|-----|-----|
| **Целые числа** | `byte`, `int`, `long`, `uint` | `int8`, `int16`, `int32`, `int64`, `uint8`, `uint16`, `uint32`, `uint64`, `int`, `uint` |
| **Вещественные** | `float`, `double`, `decimal` | `float32`, `float64` |
| **Логические** | `bool` | `bool` |
| **Строки** | `string` | `string` |
| **Символы** | `char` | `rune` (alias для `int32`, Unicode code point) |
| **Байт** | `byte` | `byte` (alias для `uint8`) |

#### Важно про `int` и `uint`

В Go `int` и `uint` имеют размер **зависящий от платформы**:
- 32-битная система: `int` = `int32`
- 64-битная система: `int` = `int64`

**Рекомендация**: Используйте `int`, если нет явных требований к размеру.

---

### Строки

**C#**:
```csharp
string name = "Alice";
string multiline = @"Line 1
Line 2";
string interpolated = $"Hello, {name}!";
```

**Go**:
```go
name := "Alice"

// Многострочная строка (raw string literal)
multiline := `Line 1
Line 2`

// Интерполяция через fmt.Sprintf
greeting := fmt.Sprintf("Hello, %s!", name)
```

**Особенности Go строк**:
- Строки **иммутабельны** (как в C#)
- Строки — это **последовательность байтов** (UTF-8)
- Для работы с Unicode используйте **rune**

```go
s := "Hello, 世界"
fmt.Println(len(s))          // 13 (количество байтов, не символов!)

// Для подсчета символов
fmt.Println(utf8.RuneCountInString(s)) // 9

// Итерация по рунам
for i, r := range s {
    fmt.Printf("%d: %c\n", i, r)
}
```

---

### Массивы

**C#**:
```csharp
int[] numbers = new int[5];
int[] values = { 1, 2, 3, 4, 5 };
```

**Go**:
```go
var numbers [5]int              // [0 0 0 0 0]
values := [5]int{1, 2, 3, 4, 5}

// Размер выводится автоматически
auto := [...]int{1, 2, 3} // [3]int
```

**Важно**: В Go размер массива — **часть типа**!

```go
var a [5]int
var b [10]int

// a и b — РАЗНЫЕ типы! Нельзя присвоить друг другу
```

**Практический вывод**: Массивы в Go используются редко. Чаще используются **слайсы**.

---

### Слайсы (Slices) — динамические массивы

**C#**:
```csharp
List<int> numbers = new List<int> { 1, 2, 3 };
numbers.Add(4);
```

**Go**:
```go
numbers := []int{1, 2, 3}
numbers = append(numbers, 4)
```

**Создание слайсов**:

```go
// Литерал
s1 := []int{1, 2, 3}

// С помощью make (заданная длина и capacity)
s2 := make([]int, 5)      // len=5, cap=5, [0 0 0 0 0]
s3 := make([]int, 3, 10)  // len=3, cap=10, [0 0 0]

// Из массива
arr := [5]int{1, 2, 3, 4, 5}
s4 := arr[1:4] // [2 3 4] — срез от индекса 1 до 4 (не включая)
```

**Важные операции**:

```go
s := []int{1, 2, 3, 4, 5}

// Длина и вместимость
fmt.Println(len(s)) // 5
fmt.Println(cap(s)) // 5

// Добавление элементов
s = append(s, 6, 7, 8)

// Копирование
dest := make([]int, len(s))
copy(dest, s)

// Слайсинг
sub := s[1:3]  // [2 3]
first := s[:2] // [1 2]
last := s[3:]  // [4 5]
```

**Внимание**: Слайсы — это **ссылки** на массив!

```go
arr := [5]int{1, 2, 3, 4, 5}
s1 := arr[0:3] // [1 2 3]
s2 := arr[2:5] // [3 4 5]

s1[2] = 99 // Изменяет arr[2]!

fmt.Println(arr) // [1 2 99 4 5]
fmt.Println(s2)  // [99 4 5]
```

---

### Слайсы и производительность: GC, аллокации, capacity

#### Внутреннее устройство слайса

Слайс — это **дескриптор**, содержащий 3 поля:
```go
type slice struct {
    ptr    *array  // Указатель на базовый массив
    len    int     // Длина (количество элементов)
    cap    int     // Вместимость (capacity)
}
```

**Визуализация**:
```
Слайс: s := make([]int, 3, 5)

s.ptr  ──>  [10][20][30][0][0]  (базовый массив)
s.len  = 3  (можем обращаться к s[0], s[1], s[2])
s.cap  = 5  (можем расширить до 5 без реаллокации)
```

#### Аллокации и рост слайса

**Проблема**: `append` может вызывать аллокации на heap!

```go
// Плохо: множественные аллокации
s := []int{}
for i := 0; i < 1000; i++ {
    s = append(s, i) // Реаллокация при каждом превышении capacity!
}
```

**Как растет capacity**:
- Если `len < 256`: capacity удваивается
- Если `len >= 256`: capacity растет примерно на 25%

**Хорошо**: Предварительное выделение capacity

```go
// Если знаем размер заранее
s := make([]int, 0, 1000) // len=0, cap=1000
for i := 0; i < 1000; i++ {
    s = append(s, i) // Без реаллокаций!
}

// Или, если знаем точный размер
s := make([]int, 1000) // len=1000, cap=1000
for i := 0; i < 1000; i++ {
    s[i] = i // Прямое присваивание, нет append
}
```

**Сравнение производительности**:
```go
// Benchmark: без предвыделения
func BenchmarkWithoutCapacity(b *testing.B) {
    for i := 0; i < b.N; i++ {
        s := []int{}
        for j := 0; j < 10000; j++ {
            s = append(s, j) // Много аллокаций
        }
    }
}

// Benchmark: с предвыделением
func BenchmarkWithCapacity(b *testing.B) {
    for i := 0; i < b.N; i++ {
        s := make([]int, 0, 10000)
        for j := 0; j < 10000; j++ {
            s = append(s, j) // Одна аллокация
        }
    }
}

// Результат: разница ~10x в производительности!
```

#### Утечки памяти через слайсы

**Проблема 1**: Подслайсы удерживают весь базовый массив

```go
func processData() []byte {
    data := make([]byte, 1_000_000) // 1MB
    // ... заполнение данных ...

    // Возвращаем только первые 100 байт
    return data[:100] // ❌ УТЕЧКА: 1MB остается в памяти!
}
```

**Решение**: Копировать нужную часть

```go
func processData() []byte {
    data := make([]byte, 1_000_000)
    // ... заполнение данных ...

    result := make([]byte, 100)
    copy(result, data[:100]) // ✅ Копируем, data может быть освобожден GC
    return result
}
```

**Проблема 2**: "Мертвые" элементы в слайсе

```go
type BigStruct struct {
    Data [1024]byte
}

func removeElement(slice []*BigStruct, index int) []*BigStruct {
    // ❌ Плохо: последний элемент остается в памяти
    return append(slice[:index], slice[index+1:]...)
}

func removeElementCorrectly(slice []*BigStruct, index int) []*BigStruct {
    // ✅ Хорошо: очищаем ссылку
    copy(slice[index:], slice[index+1:])
    slice[len(slice)-1] = nil // Освобождаем ссылку для GC
    return slice[:len(slice)-1]
}
```

#### Stack vs Heap allocation (Escape Analysis)

**Критически важно**: Не все слайсы живут на heap!

```go
// Слайс на стеке (если компилятор определит, что он не "убегает")
func localSlice() {
    s := []int{1, 2, 3} // Может быть на стеке
    fmt.Println(s)
}

// Слайс на heap (возвращается из функции)
func heapSlice() []int {
    s := []int{1, 2, 3} // ТОЧНО на heap
    return s             // "Убегает" из функции
}
```

**Как проверить**:
```bash
go build -gcflags="-m" main.go

# Вывод:
# ./main.go:10:12: s escapes to heap
```

**Правила**:
- Если слайс возвращается из функции → heap
- Если слайс передается в другую горутину → heap
- Если слайс присваивается в структуру на heap → heap
- Иначе → может быть на стеке (быстрее, нет GC давления)

#### Советы по оптимизации слайсов

1. **Предвыделяйте capacity**, если знаете размер:
   ```go
   s := make([]int, 0, expectedSize)
   ```

2. **Переиспользуйте слайсы** вместо создания новых:
   ```go
   // Плохо
   for _, item := range items {
       temp := []int{} // Новая аллокация каждую итерацию!
       // ...
   }

   // Хорошо
   temp := make([]int, 0, maxSize)
   for _, item := range items {
       temp = temp[:0] // Переиспользуем
       // ...
   }
   ```

3. **Копируйте, когда нужен маленький подслайс** большого массива

4. **Очищайте ссылки** при удалении элементов с указателями

5. **Используйте массивы** для фиксированных размеров (если размер известен):
   ```go
   var buffer [4096]byte // На стеке, нет GC
   ```

---

### Мапы (Maps) — словари

**C#**:
```csharp
Dictionary<string, int> ages = new Dictionary<string, int>
{
    { "Alice", 30 },
    { "Bob", 25 }
};

ages["Charlie"] = 35;
int age = ages["Alice"];
```

**Go**:
```go
// Создание
ages := map[string]int{
    "Alice": 30,
    "Bob":   25,
}

// Или через make
ages := make(map[string]int)

// Добавление/обновление
ages["Charlie"] = 35

// Чтение
age := ages["Alice"]
```

**Проверка существования ключа**:

**C#**:
```csharp
if (ages.TryGetValue("Alice", out int age))
{
    Console.WriteLine(age);
}
```

**Go**:
```go
age, exists := ages["Alice"]
if exists {
    fmt.Println(age)
}

// Или короче (идиоматично)
if age, ok := ages["Alice"]; ok {
    fmt.Println(age)
}
```

**Удаление**:

```go
delete(ages, "Bob")
```

**Итерация**:

```go
for name, age := range ages {
    fmt.Printf("%s is %d years old\n", name, age)
}

// Только ключи
for name := range ages {
    fmt.Println(name)
}
```

**Важно**:
- Мапы — **ссылочный тип** (как слайсы)
- Порядок итерации **не гарантирован** (рандомизирован специально!)
- **Не потокобезопасны** (используйте `sync.Map` для concurrent доступа)

---

### Мапы и производительность: GC, аллокации, оптимизация

#### Внутреннее устройство мапы

Мапа в Go реализована как **hash table** с buckets:
```go
type hmap struct {
    count     int    // Количество элементов
    B         uint8  // log₂ количества buckets
    buckets   *[]bucket
    // ... другие поля
}
```

**Важно**: Мапа аллоцируется на **heap** (всегда!).

#### Предвыделение capacity для мап

Как и слайсы, мапы можно создавать с предварительным размером:

```go
// Плохо: множественные реаллокации
m := make(map[string]int)
for i := 0; i < 10000; i++ {
    m[fmt.Sprintf("key%d", i)] = i
}

// Хорошо: одна аллокация
m := make(map[string]int, 10000)
for i := 0; i < 10000; i++ {
    m[fmt.Sprintf("key%d", i)] = i
}
```

**Рост мапы**:
- Начальный размер: 8 buckets
- При заполнении ~6.5 элементов на bucket → удваивание buckets
- Процесс роста — **дорогая операция** (rehashing)

#### Удаление и память

**Проблема**: `delete` не освобождает память сразу!

```go
m := make(map[string]*BigStruct)
for i := 0; i < 1_000_000; i++ {
    m[fmt.Sprintf("key%d", i)] = &BigStruct{...}
}

// Удаляем все элементы
for k := range m {
    delete(m, k) // Buckets остаются аллоцированы!
}

// Мапа пустая, но память не освобождена полностью
```

**Решение**: Создать новую мапу

```go
// Если нужно очистить и переиспользовать
m = make(map[string]*BigStruct) // Старая мапа будет собрана GC
```

**Или** использовать `clear` (Go 1.21+):
```go
clear(m) // Очищает мапу, но сохраняет buckets
```

#### Ключи и значения: влияние на производительность

**Ключи мапы**:
- Должны быть **comparable** (int, string, struct без слайсов/мап/функций)
- String keys — дешевле, если строки уже интернированы
- Struct keys — можно, но каждое поле участвует в хешировании

```go
// Плохо: составной ключ через строку (аллокация!)
key := fmt.Sprintf("%d:%s", id, name) // Создает новую строку каждый раз
m[key] = value

// Хорошо: struct ключ (без аллокаций)
type Key struct {
    ID   int
    Name string
}
m[Key{id, name}] = value // Struct остается на стеке
```

**Значения мапы с указателями**:

```go
// Вариант 1: Мапа значений
m := make(map[int]BigStruct) // Копирование при вставке/извлечении

// Вариант 2: Мапа указателей
m := make(map[int]*BigStruct) // Хранение указателей (меньше копирований)
```

**Когда использовать указатели**:
- Большие структуры (> 100 байт)
- Нужна мутация значений в мапе
- Значения используются за пределами мапы

**Но**: Больше указателей = больше работы для GC (scan фаза)

#### Конкурентный доступ к мапам

**Проблема**: Обычные мапы **не потокобезопасны**!

```go
m := make(map[string]int)

// ❌ Race condition!
go func() {
    m["key"] = 1
}()
go func() {
    m["key"] = 2
}()
```

**Решение 1**: `sync.Mutex`

```go
type SafeMap struct {
    mu sync.RWMutex
    m  map[string]int
}

func (sm *SafeMap) Set(key string, value int) {
    sm.mu.Lock()
    defer sm.mu.Unlock()
    sm.m[key] = value
}

func (sm *SafeMap) Get(key string) (int, bool) {
    sm.mu.RLock()
    defer sm.mu.RUnlock()
    val, ok := sm.m[key]
    return val, ok
}
```

**Решение 2**: `sync.Map` (для специфичных случаев)

```go
var m sync.Map

m.Store("key", 42)
value, ok := m.Load("key")
m.Delete("key")

m.Range(func(key, value interface{}) bool {
    fmt.Println(key, value)
    return true // continue iteration
})
```

**Когда использовать `sync.Map`**:
- Ключи записываются раз, читаются много раз
- Множество горутин читают/пишут разные ключи
- Нет нужды в типобезопасности (interface{})

**Когда НЕ использовать `sync.Map`**:
- Частые записи одних и тех же ключей
- Нужна типобезопасность
- Большинство операций — чтение (используйте RWMutex)

#### Советы по оптимизации мап

1. **Предвыделяйте размер**, если известен:
   ```go
   m := make(map[string]int, expectedSize)
   ```

2. **Используйте примитивные ключи** (int, string) вместо составных:
   ```go
   // Вместо map[string]T используйте числовой ID
   m := make(map[int]T)
   ```

3. **Минимизируйте аллокации строковых ключей**:
   ```go
   // Плохо
   for i := 0; i < n; i++ {
       key := fmt.Sprintf("key%d", i) // Новая строка каждый раз
       m[key] = i
   }

   // Лучше
   var buf strings.Builder
   for i := 0; i < n; i++ {
       buf.Reset()
       buf.WriteString("key")
       buf.WriteString(strconv.Itoa(i))
       m[buf.String()] = i
   }
   ```

4. **Очищайте большие мапы** созданием новых:
   ```go
   m = make(map[K]V) // Вместо множественных delete
   ```

5. **Для read-heavy workload** используйте `sync.RWMutex` вместо `sync.Map`

6. **Переиспользуйте мапы** в пулах (`sync.Pool`) для hot paths:
   ```go
   var mapPool = sync.Pool{
       New: func() interface{} {
           return make(map[string]int)
       },
   }

   m := mapPool.Get().(map[string]int)
   // ... использование ...
   clear(m) // Go 1.21+
   mapPool.Put(m)
   ```

---

### Пакеты slices, maps и cmp (Go 1.21+)

До Go 1.21 любая операция с коллекциями требовала ручных циклов. Для C# разработчиков, привыкших к LINQ, это было болезненно. Пакеты `slices` и `maps` решают эту проблему.

#### Пакет slices

| C# LINQ | Go slices | Описание |
|---------|-----------|----------|
| `.Contains(x)` | `slices.Contains(s, x)` | Проверка наличия элемента |
| `.Any(predicate)` | `slices.ContainsFunc(s, fn)` | Есть ли элемент по условию |
| `.OrderBy()` | `slices.Sort(s)` | Сортировка (in-place!) |
| `.OrderByDescending()` | `slices.SortFunc(s, cmp)` | Сортировка с компаратором |
| `.Reverse()` | `slices.Reverse(s)` | Разворот (in-place!) |
| `.Distinct()` | `slices.Compact(s)` | Удаление последовательных дублей |
| Clone() | `slices.Clone(s)` | Копирование slice |
| `.Max()` | `slices.Max(s)` | Максимальный элемент |
| `.Min()` | `slices.Min(s)` | Минимальный элемент |
| `.SequenceEqual()` | `slices.Equal(s1, s2)` | Сравнение slices |
| `.Take(n)` | `s[:n]` | Взять первые N (нативный синтаксис) |
| `.Skip(n)` | `s[n:]` | Пропустить первые N |

> ⚠️ **Важно**: Многие функции `slices` работают **in-place** (изменяют исходный slice). В LINQ методы всегда возвращают новую коллекцию.

```go
import "slices"

numbers := []int{3, 1, 4, 1, 5, 9, 2, 6}

// Поиск
slices.Contains(numbers, 5)                    // true
slices.Index(numbers, 4)                       // 2
slices.IndexFunc(numbers, func(n int) bool {   // индекс первого > 4
    return n > 4
})

// Сортировка (in-place!)
slices.Sort(numbers)                           // [1, 1, 2, 3, 4, 5, 6, 9]
slices.SortFunc(numbers, func(a, b int) int {
    return b - a  // По убыванию
})

// Бинарный поиск (для отсортированных!)
idx, found := slices.BinarySearch(numbers, 5)

// Модификация
slices.Reverse(numbers)                        // In-place разворот
numbers = slices.Insert(numbers, 2, 100)       // Вставить 100 на позицию 2
numbers = slices.Delete(numbers, 2, 4)         // Удалить элементы [2:4)

// Удаление последовательных дубликатов (требует сортировки!)
sorted := []int{1, 1, 2, 2, 2, 3}
unique := slices.Compact(sorted)               // [1, 2, 3]

// Копия и сравнение
copy2 := slices.Clone(numbers)
slices.Equal(slice1, slice2)                   // Поэлементное сравнение

// Min/Max
slices.Min(numbers)
slices.Max(numbers)
```

> 💡 **Совет**: Для Filter, Map, Reduce — напишите свои generic-функции или используйте библиотеку `samber/lo`.

#### Пакет maps

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
maps.Copy(target, users)

// Equal — сравнение maps
maps.Equal(map1, map2)

// DeleteFunc — удаление по условию
maps.DeleteFunc(users, func(key string, user User) bool {
    return user.Age < 18
})

// Go 1.23+: итераторы для map
for key := range maps.Keys(users) {
    fmt.Println(key)
}

// Преобразование iterator в slice
keys := slices.Collect(maps.Keys(users))
values := slices.Collect(maps.Values(users))

// Сортированные ключи
keys = slices.Sorted(maps.Keys(users))
```

#### Пакет cmp

```go
import "cmp"

// cmp.Less — безопасное сравнение (обрабатывает NaN для float)
cmp.Less(1, 2)        // true
cmp.Compare(1, 2)     // -1, Compare(2, 2)=0, Compare(3, 2)=1

// cmp.Or — первое ненулевое значение (Go 1.22+)
// Аналог: name ?? config.Name ?? "default" в C#
name := cmp.Or(os.Getenv("NAME"), config.Name, "default")
port := cmp.Or(os.Getenv("PORT"), "8080")
```

> 💡 **Важно**: `cmp.Or` оценивает все аргументы сразу (не lazy). Если нужна lazy evaluation — используйте обычные if-цепочки.

---

### Современные встроенные функции (Go 1.21+)

#### clear() — очистка коллекций

```go
// Очистка map (очищает, но сохраняет buckets для переиспользования)
m := map[string]int{"a": 1, "b": 2, "c": 3}
clear(m)
fmt.Println(len(m))  // 0

// Очистка slice (заполняет zero values, длина не меняется!)
s := []int{1, 2, 3, 4, 5}
clear(s)
fmt.Println(s)    // [0 0 0 0 0]
fmt.Println(len(s))  // 5 — длина сохраняется!

// Для полной очистки slice используйте s[:0]
s = s[:0]
```

> ⚠️ **Внимание**: `clear(slice)` не меняет длину — только обнуляет элементы. Для очистки slice с нулевой длиной используйте `s = s[:0]`.

#### min/max — встроенные generic функции

```go
// Go 1.21+: встроенные generic функции
x := max(10, 20)             // 20
y := min(3.14, 2.71)         // 2.71
z := max("apple", "banana")  // "banana" (лексикографически)

// Множество аргументов
biggest := max(1, 5, 3, 9, 2)   // 9
smallest := min(1, 5, 3, 9, 2)  // 1

// Работают с любыми cmp.Ordered типами
type MyInt int
a, b := MyInt(10), MyInt(20)
result := max(a, b)  // MyInt(20)
```

**Сравнение с C#**:
```csharp
// C#: Math.Max, Math.Min (только один тип за раз)
int x = Math.Max(10, 20);
// C# 9+: Math.Clamp, но нет multi-arg max
```

---

### Iterators (Go 1.23)

Go 1.23 добавил поддержку user-defined iterators через `range over functions`:

```go
import "iter"

// Iterator — функция специального вида:
// iter.Seq[V]   = func(yield func(V) bool)
// iter.Seq2[K,V] = func(yield func(K, V) bool)

// Пример: итератор по числам Фибоначчи
func Fibonacci(n int) iter.Seq[int] {
    return func(yield func(int) bool) {
        a, b := 0, 1
        for i := 0; i < n; i++ {
            if !yield(a) {
                return  // break в range-цикле
            }
            a, b = b, a+b
        }
    }
}

// Использование — как обычный range
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
| `break` в foreach | `yield` вернул `false` |

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
```

---

### Строки и производительность

#### Строки иммутабельны, но это не всегда дешево

```go
// ❌ Плохо: O(n²) сложность из-за аллокаций
result := ""
for i := 0; i < 1000; i++ {
    result += "x" // Каждый раз создается новая строка!
}

// ✅ Хорошо: O(n) с strings.Builder
var builder strings.Builder
builder.Grow(1000) // Предвыделяем capacity
for i := 0; i < 1000; i++ {
    builder.WriteString("x")
}
result := builder.String()
```

**strings.Builder** — аналог `StringBuilder` в C#:
- Минимизирует аллокации
- Можно предвыделить capacity через `Grow()`
- **Не потокобезопасен**

#### Конвертация []byte ↔ string

**Проблема**: Конвертация создает копию!

```go
data := []byte("Hello, World!")
s := string(data) // Копирование всех байт!

str := "Hello"
b := []byte(str) // Снова копирование!
```

**Оптимизация** (небезопасная, используйте с осторожностью):
```go
import "unsafe"

// []byte -> string без копирования (read-only!)
func BytesToString(b []byte) string {
    return unsafe.String(unsafe.SliceData(b), len(b))
}

// string -> []byte без копирования (НЕ модифицируйте!)
func StringToBytes(s string) []byte {
    return unsafe.Slice(unsafe.StringData(s), len(s))
}
```

**Когда использовать**: Hot paths с гарантией immutability.

---

## 3. Управляющие конструкции

### If/Else

**C#**:
```csharp
if (x > 0)
{
    Console.WriteLine("Positive");
}
else if (x < 0)
{
    Console.WriteLine("Negative");
}
else
{
    Console.WriteLine("Zero");
}
```

**Go**:
```go
if x > 0 {
    fmt.Println("Positive")
} else if x < 0 {
    fmt.Println("Negative")
} else {
    fmt.Println("Zero")
}
```

**Особенность Go**: можно инициализировать переменную прямо в `if`:

```go
if age, ok := ages["Alice"]; ok {
    fmt.Printf("Alice is %d years old\n", age)
}
// age доступна только внутри if-блока
```

**Важно**: Скобки вокруг условия **не нужны** (и не рекомендуются).

---

### Switch

**C#**:
```csharp
switch (day)
{
    case "Monday":
        Console.WriteLine("Start of week");
        break;
    case "Friday":
        Console.WriteLine("End of week");
        break;
    default:
        Console.WriteLine("Midweek");
        break;
}
```

**Go**:
```go
switch day {
case "Monday":
    fmt.Println("Start of week")
case "Friday":
    fmt.Println("End of week")
default:
    fmt.Println("Midweek")
}
```

**Ключевые отличия**:
- **Нет `break`** — автоматический выход из case (!)
- Для продолжения используйте `fallthrough`
- Можно использовать без переменной (как цепочка if-else)

**Продвинутые примеры**:

```go
// Множественные значения в case
switch day {
case "Saturday", "Sunday":
    fmt.Println("Weekend!")
}

// Switch без переменной
switch {
case age < 18:
    fmt.Println("Minor")
case age < 65:
    fmt.Println("Adult")
default:
    fmt.Println("Senior")
}

// С инициализацией
switch age := getAge(); {
case age < 18:
    fmt.Println("Minor")
default:
    fmt.Println("Adult")
}

// Type switch (проверка типа интерфейса)
switch v := i.(type) {
case int:
    fmt.Printf("Integer: %d\n", v)
case string:
    fmt.Printf("String: %s\n", v)
default:
    fmt.Println("Unknown type")
}
```

---

### Циклы

**В Go есть только `for`!** Нет `while`, `do-while`, `foreach`.

#### Классический цикл

**C#**:
```csharp
for (int i = 0; i < 10; i++)
{
    Console.WriteLine(i);
}
```

**Go**:
```go
for i := 0; i < 10; i++ {
    fmt.Println(i)
}
```

#### While-подобный цикл

**C#**:
```csharp
while (condition)
{
    // code
}
```

**Go**:
```go
for condition {
    // code
}
```

#### Бесконечный цикл

**C#**:
```csharp
while (true)
{
    // code
}
```

**Go**:
```go
for {
    // code
}
```

#### Foreach-подобный цикл (range)

**C#**:
```csharp
foreach (var item in items)
{
    Console.WriteLine(item);
}
```

**Go**:
```go
for index, value := range items {
    fmt.Println(index, value)
}

// Если индекс не нужен
for _, value := range items {
    fmt.Println(value)
}

// Если нужен только индекс
for index := range items {
    fmt.Println(index)
}
```

**Range для разных типов**:

```go
// Слайс/массив
nums := []int{10, 20, 30}
for i, v := range nums {
    fmt.Printf("Index: %d, Value: %d\n", i, v)
}

// Мапа
ages := map[string]int{"Alice": 30, "Bob": 25}
for name, age := range ages {
    fmt.Printf("%s: %d\n", name, age)
}

// Строка (итерация по рунам!)
for i, r := range "Hello" {
    fmt.Printf("%d: %c\n", i, r)
}

// Канал (будем изучать позже)
for value := range channel {
    fmt.Println(value)
}
```

#### Range over integers (Go 1.22)

Одна из самых простых, но долгожданных возможностей:

```go
// До Go 1.22 — классический C-style цикл
for i := 0; i < 10; i++ {
    fmt.Println(i)
}

// Go 1.22+
for i := range 10 {
    fmt.Println(i)  // 0, 1, 2, ..., 9
}

// Когда индекс не нужен
for range 5 {
    doSomething()  // Выполнится 5 раз
}
```

**Сравнение с C#**:
```csharp
// C#: Enumerable.Range(0, 10)
foreach (var i in Enumerable.Range(0, 10))
    Console.WriteLine(i);
```

**Ограничения**: `range N` всегда начинается с 0. Для произвольного диапазона используйте классический цикл: `for i := 5; i < 10; i++`.

**Типичные use cases:**
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
    testUsers = append(testUsers, User{ID: i, Name: fmt.Sprintf("User %d", i)})
}
```

#### Break, Continue

Работают так же, как в C#:

```go
for i := 0; i < 10; i++ {
    if i == 5 {
        break // Выход из цикла
    }
    if i%2 == 0 {
        continue // Переход к следующей итерации
    }
    fmt.Println(i)
}
```

**Метки** (для вложенных циклов):

```go
outer:
for i := 0; i < 3; i++ {
    for j := 0; j < 3; j++ {
        if i == j {
            break outer // Выход из ВНЕШНЕГО цикла
        }
        fmt.Println(i, j)
    }
}
```

---

## 4. Функции

### Объявление функции

**C#**:
```csharp
public int Add(int a, int b)
{
    return a + b;
}
```

**Go**:
```go
func Add(a int, b int) int {
    return a + b
}

// Если параметры одного типа, можно сократить
func Add(a, b int) int {
    return a + b
}
```

**Видимость** в Go:
- Заглавная буква = **public** (экспортируется из пакета)
- Строчная буква = **private** (доступна только внутри пакета)

```go
func Add(a, b int) int { ... }       // Public
func calculateSum(a, b int) int { ... } // Private
```

---

### Множественные возвращаемые значения

**C# (через Tuple)**:
```csharp
public (int sum, int product) Calculate(int a, int b)
{
    return (a + b, a * b);
}

var (sum, product) = Calculate(3, 4);
```

**Go** (идиоматично!):
```go
func Calculate(a, b int) (int, int) {
    return a + b, a * b
}

sum, product := Calculate(3, 4)
```

**Именованные возвращаемые значения**:

```go
func Calculate(a, b int) (sum int, product int) {
    sum = a + b
    product = a * b
    return // "Naked return" — возвращает sum и product
}
```

**Предупреждение**: Naked return ухудшает читаемость, используйте с осторожностью.

---

### Обработка ошибок (Error handling)

**C#**:
```csharp
public int Divide(int a, int b)
{
    if (b == 0)
        throw new DivideByZeroException();
    return a / b;
}

try
{
    int result = Divide(10, 0);
}
catch (DivideByZeroException ex)
{
    Console.WriteLine(ex.Message);
}
```

**Go** (error как значение):
```go
func Divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

result, err := Divide(10, 0)
if err != nil {
    fmt.Println("Error:", err)
    return
}
fmt.Println(result)
```

**Идиома Go**: Проверять ошибки сразу после вызова функции.

```go
result, err := SomeFunction()
if err != nil {
    // Обработка ошибки
    return err
}
// Работа с result
```

**Подробнее об ошибках** — в разделе 2.5 плана обучения.

---

### Variadic функции (переменное количество аргументов)

**C#**:
```csharp
public int Sum(params int[] numbers)
{
    return numbers.Sum();
}

int total = Sum(1, 2, 3, 4, 5);
```

**Go**:
```go
func Sum(numbers ...int) int {
    total := 0
    for _, num := range numbers {
        total += num
    }
    return total
}

total := Sum(1, 2, 3, 4, 5)

// Или передать слайс
nums := []int{1, 2, 3, 4, 5}
total := Sum(nums...) // ... "распаковывает" слайс
```

---

### Анонимные функции и замыкания

**C#**:
```csharp
Func<int, int> double = x => x * 2;
Console.WriteLine(double(5)); // 10
```

**Go**:
```go
double := func(x int) int {
    return x * 2
}
fmt.Println(double(5)) // 10
```

**Замыкания**:

```go
func counter() func() int {
    count := 0
    return func() int {
        count++
        return count
    }
}

c := counter()
fmt.Println(c()) // 1
fmt.Println(c()) // 2
fmt.Println(c()) // 3
```

---

### Функции как параметры

**C#**:
```csharp
public void Apply(int[] numbers, Func<int, int> transform)
{
    for (int i = 0; i < numbers.Length; i++)
    {
        numbers[i] = transform(numbers[i]);
    }
}
```

**Go**:
```go
func Apply(numbers []int, transform func(int) int) {
    for i, num := range numbers {
        numbers[i] = transform(num)
    }
}

// Использование
nums := []int{1, 2, 3, 4}
Apply(nums, func(x int) int {
    return x * 2
})
fmt.Println(nums) // [2 4 6 8]
```

---

## 5. Defer (отложенное выполнение)

**Нет аналога в C#** (ближайшее — `using` или `finally`).

**Defer** откладывает выполнение функции до момента выхода из текущей функции.

```go
func ReadFile(filename string) {
    file, err := os.Open(filename)
    if err != nil {
        return
    }
    defer file.Close() // Закроется в конце функции

    // Работа с файлом
    // ...
}
```

**C# эквивалент**:
```csharp
using (var file = File.Open(filename, FileMode.Open))
{
    // Работа с файлом
} // file.Dispose() вызывается автоматически
```

**Множественные defer** выполняются в **обратном порядке** (LIFO):

```go
func example() {
    defer fmt.Println("1")
    defer fmt.Println("2")
    defer fmt.Println("3")
    fmt.Println("Function body")
}
// Вывод:
// Function body
// 3
// 2
// 1
```

**Практическое применение**:
- Закрытие файлов, соединений с БД
- Разблокировка мьютексов
- Логирование окончания функции
- Восстановление после panic (аналог catch)

```go
func SafeFunction() {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("Recovered from panic:", r)
        }
    }()

    // Код, который может вызвать panic
    panic("something went wrong")
}
```

---

## 6. Указатели

**C#**: Указатели есть, но используются редко (только в `unsafe` контексте).

**Go**: Указатели — обычная часть языка, но **без арифметики** (как в C/C++).

### Объявление и использование

```go
x := 10
p := &x     // p — указатель на x (тип *int)
fmt.Println(*p) // 10 (разыменование)

*p = 20     // Изменение значения x через указатель
fmt.Println(x)  // 20
```

**Синтаксис**:
- `&` — взятие адреса ("address of")
- `*` — разыменование ("dereference")

### Указатели в функциях

**Передача по значению**:
```go
func increment(x int) {
    x++
}

a := 5
increment(a)
fmt.Println(a) // 5 (не изменилось)
```

**Передача по указателю**:
```go
func increment(x *int) {
    *x++
}

a := 5
increment(&a)
fmt.Println(a) // 6
```

**Важно**: В Go **нет** автоматической конвертации значения ↔ указатель (как `ref` в C#).

**C# ref/out**:
```csharp
void Increment(ref int x)
{
    x++;
}

int a = 5;
Increment(ref a);
```

**Go**:
```go
func Increment(x *int) {
    *x++
}

a := 5
Increment(&a)
```

### Указатели vs значения: когда что использовать?

**Используйте указатели**:
- Когда нужно изменить переменную внутри функции
- Для больших структур (избежание копирования)
- Для опциональных значений (`nil` = отсутствие значения)

**Используйте значения**:
- Для маленьких типов (примитивы)
- Когда не нужно изменять данные
- Для иммутабельности

```go
// Плохо (лишнее копирование большой структуры)
func ProcessUser(u User) { ... }

// Хорошо
func ProcessUser(u *User) { ... }
```

---

## 7. Структуры (Structs)

**C# класс**:
```csharp
public class Person
{
    public string Name { get; set; }
    public int Age { get; set; }
}

var person = new Person { Name = "Alice", Age = 30 };
```

**Go структура**:
```go
type Person struct {
    Name string
    Age  int
}

person := Person{Name: "Alice", Age: 30}

// Или короче (по порядку полей)
person := Person{"Alice", 30}
```

### Методы на структурах

**C#**:
```csharp
public class Person
{
    public string Name { get; set; }

    public void Greet()
    {
        Console.WriteLine($"Hello, I'm {Name}");
    }
}
```

**Go**:
```go
type Person struct {
    Name string
}

func (p Person) Greet() {
    fmt.Printf("Hello, I'm %s\n", p.Name)
}

// Использование
person := Person{Name: "Alice"}
person.Greet()
```

**Методы с указателем** (для изменения структуры):

```go
type Counter struct {
    Value int
}

// Метод с receiver по значению (НЕ изменяет структуру)
func (c Counter) IncrementWrong() {
    c.Value++ // Изменяет КОПИЮ
}

// Метод с receiver по указателю (изменяет структуру)
func (c *Counter) Increment() {
    c.Value++
}

// Использование
counter := Counter{Value: 0}
counter.IncrementWrong()
fmt.Println(counter.Value) // 0

counter.Increment()
fmt.Println(counter.Value) // 1
```

**Правило**: Если хотя бы один метод использует pointer receiver, используйте pointer receiver для **всех** методов этого типа (консистентность).

---

### Встраивание (Embedding) — замена наследования

**C# наследование**:
```csharp
public class Animal
{
    public void Eat() { }
}

public class Dog : Animal
{
    public void Bark() { }
}
```

**Go композиция (embedding)**:
```go
type Animal struct {
    Name string
}

func (a Animal) Eat() {
    fmt.Println(a.Name, "is eating")
}

type Dog struct {
    Animal // Встраивание (анонимное поле)
    Breed  string
}

func (d Dog) Bark() {
    fmt.Println("Woof!")
}

// Использование
dog := Dog{
    Animal: Animal{Name: "Buddy"},
    Breed:  "Labrador",
}

dog.Eat()  // Вызов метода встроенного типа
dog.Bark()
fmt.Println(dog.Name) // Доступ к полю встроенного типа
```

**Ключевое отличие**: Это **не наследование**, а **композиция**. `Dog` — это не `Animal`, но имеет доступ к его полям и методам.

---

## 8. Интерфейсы

**C# интерфейс** (явная реализация):
```csharp
public interface IWriter
{
    void Write(string text);
}

public class ConsoleWriter : IWriter
{
    public void Write(string text)
    {
        Console.WriteLine(text);
    }
}
```

**Go интерфейс** (неявная реализация — **duck typing**):
```go
type Writer interface {
    Write(text string)
}

type ConsoleWriter struct{}

func (cw ConsoleWriter) Write(text string) {
    fmt.Println(text)
}

// Использование
var w Writer = ConsoleWriter{} // Автоматически удовлетворяет интерфейсу!
w.Write("Hello")
```

**Важно**: В Go **не нужно** явно указывать, что тип реализует интерфейс. Если у типа есть все нужные методы — он автоматически удовлетворяет интерфейсу.

### Пустой интерфейс (interface{})

**C# object**:
```csharp
object value = 42;
object value2 = "Hello";
```

**Go interface{}** (с Go 1.18+ можно использовать `any`):
```go
var value interface{} = 42
var value2 any = "Hello" // any — alias для interface{}
```

`interface{}` / `any` — может хранить **любое** значение.

### Type assertion (проверка типа)

```go
var i interface{} = "Hello"

// Type assertion
s := i.(string)
fmt.Println(s) // "Hello"

// Безопасная проверка
s, ok := i.(string)
if ok {
    fmt.Println("It's a string:", s)
}

// Type switch
switch v := i.(type) {
case string:
    fmt.Println("String:", v)
case int:
    fmt.Println("Int:", v)
default:
    fmt.Println("Unknown type")
}
```

---

## 9. Пакеты и импорты

### Создание пакета

**Структура проекта**:
```
myapp/
├── main.go
├── utils/
│   └── helper.go
```

**utils/helper.go**:
```go
package utils

// Экспортируемая функция (заглавная буква)
func Add(a, b int) int {
    return a + b
}

// Приватная функция
func subtract(a, b int) int {
    return a - b
}
```

**main.go**:
```go
package main

import (
    "fmt"
    "myapp/utils"
)

func main() {
    result := utils.Add(5, 3)
    fmt.Println(result)
}
```

### Импорты

```go
import "fmt"                    // Стандартная библиотека
import "github.com/pkg/errors"  // Внешний пакет

// Группированный импорт
import (
    "fmt"
    "os"
    "github.com/gin-gonic/gin"
)

// Алиас
import f "fmt"
f.Println("Hello")

// Импорт только для side-effects (init функции)
import _ "github.com/lib/pq"

// Импорт всех экспортируемых имен (НЕ рекомендуется!)
import . "fmt"
Println("No prefix needed")
```

---

## 10. Сравнение с C#: Чего НЕТ в Go

| Фича C# | Есть в Go? | Альтернатива |
|---------|-----------|--------------|
| Классы | ❌ | Структуры + методы |
| Наследование | ❌ | Композиция (embedding) |
| Перегрузка методов | ❌ | Разные имена функций |
| Исключения (try/catch) | ❌ | `error` как значение |
| LINQ | ❌ | Циклы или библиотеки (не идиоматично) |
| Nullable types (`int?`) | ❌ | Указатели (`*int`) |
| Properties | ❌ | Getter/Setter методы |
| Async/await | ❌ | Горутины и каналы |
| Attributes | ❌ | Struct tags (ограниченно) |
| Generics | ✅ (с Go 1.18) | Ограниченная версия |
| `null` | ❌ | `nil` (только для указателей, интерфейсов, слайсов, мап, каналов) |

---

## 11. Практические примеры

### Пример 1: Работа с JSON

**C#**:
```csharp
using System.Text.Json;

public class User
{
    public string Name { get; set; }
    public int Age { get; set; }
}

var user = new User { Name = "Alice", Age = 30 };
string json = JsonSerializer.Serialize(user);
```

**Go**:
```go
import "encoding/json"

type User struct {
    Name string `json:"name"`
    Age  int    `json:"age"`
}

user := User{Name: "Alice", Age: 30}
jsonData, err := json.Marshal(user)
if err != nil {
    log.Fatal(err)
}
fmt.Println(string(jsonData))

// Десериализация
var user2 User
err = json.Unmarshal(jsonData, &user2)
if err != nil {
    log.Fatal(err)
}
```

**Struct tags**: Метаданные для полей структуры.

---

### Пример 2: Чтение файла

**C#**:
```csharp
string content = File.ReadAllText("file.txt");
```

**Go**:
```go
import (
    "os"
    "io"
)

// Способ 1: Весь файл
content, err := os.ReadFile("file.txt")
if err != nil {
    log.Fatal(err)
}
fmt.Println(string(content))

// Способ 2: С defer
file, err := os.Open("file.txt")
if err != nil {
    log.Fatal(err)
}
defer file.Close()

data, err := io.ReadAll(file)
if err != nil {
    log.Fatal(err)
}
fmt.Println(string(data))
```

---

## Задания для практики

1. **Hello World с параметрами**
   - Создайте программу, которая принимает имя через аргументы командной строки и выводит приветствие

2. **Калькулятор**
   - Реализуйте функции `Add`, `Subtract`, `Multiply`, `Divide` с обработкой ошибок

3. **Работа со слайсами**
   - Напишите функцию `Filter`, которая фильтрует слайс по условию

4. **Структура Person**
   - Создайте структуру `Person` с методами `Greet()` и `HaveBirthday()` (увеличивает возраст)

5. **JSON парсер**
   - Прочитайте JSON из файла и выведите данные

---

## Следующие шаги

После изучения синтаксиса переходите к:
- **[1.3 Ключевые отличия от C#](03_key_differences.md)** — глубокое понимание философии Go
- **[1.4 Практика: мини-проекты](04_practice.md)** — закрепление на реальных задачах

---

## Чек-лист

- [ ] Понимаю объявление переменных (`:=` vs `var`)
- [ ] Знаю разницу между массивами и слайсами
- [ ] Умею работать с мапами
- [ ] Понимаю, как работают указатели
- [ ] Могу создавать структуры и методы
- [ ] Понимаю интерфейсы и duck typing
- [ ] Знаю, как обрабатывать ошибки (без exceptions)
- [ ] Понимаю `defer` и его применение
- [ ] Могу читать/писать JSON
- [ ] Знаю пакеты `slices`, `maps`, `cmp` (Go 1.21+) как замену LINQ-операциям
- [ ] Использую `for i := range N` вместо `for i := 0; i < N; i++` (Go 1.22)
- [ ] Понимаю `clear()`, `min()`, `max()` (Go 1.21)
- [ ] Знаю, что такое `iter.Seq[T]` и как создавать пользовательские итераторы (Go 1.23)
- [ ] Понимаю видимость (public/private через регистр)
