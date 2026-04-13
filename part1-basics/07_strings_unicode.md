# Строки и Unicode

---

## Введение

> 💡 **Для C# разработчиков**: в C# строки (`System.String`) хранятся как последовательность `char` (UTF-16, по 2 или 4 байта на символ). В Go строки — это **неизменяемые последовательности байтов** в кодировке UTF-8. Это фундаментальное отличие влияет на индексацию, длину, итерацию и работу с кириллицей, иероглифами и эмодзи. Если привыкли к `string[i]` в C# — в Go вас ждут сюрпризы.

### Что вы узнаете

- Внутреннее представление строк в Go vs C#
- `byte` vs `rune`: когда какой тип использовать
- Итерация по строкам: байты vs символы
- Пакеты `strings`, `strconv`, `unicode/utf8`
- `strings.Builder` vs конкатенация: производительность
- Типичные ошибки при работе с кириллицей и мультибайтовыми символами

---

## Внутреннее представление

### C#: UTF-16

```csharp
string s = "Привет";
Console.WriteLine(s.Length);    // 6 (количество char, каждый char = 2 байта)
Console.WriteLine(s[0]);        // 'П' (правильный символ)

// Внутри: П=0x041F, р=0x0440, и=0x0438, в=0x0432, е=0x0435, т=0x0442
// Каждый символ занимает ровно 2 байта (BMP символы)

// Но эмодзи ломают Length:
string emoji = "Hello 🌍";
Console.WriteLine(emoji.Length); // 8 (не 7!) — эмодзи = surrogate pair = 2 char
```

### Go: UTF-8

```go
s := "Привет"
fmt.Println(len(s))    // 12 (количество БАЙТОВ, не символов!)
fmt.Println(s[0])      // 208 (первый байт буквы 'П', не символ)

// Внутри: П = 0xD0 0x9F (2 байта), р = 0xD1 0x80 (2 байта), ...
// Каждая кириллическая буква занимает 2 байта в UTF-8

emoji := "Hello 🌍"
fmt.Println(len(emoji))                    // 10 байт (5 ASCII + 4 байта на 🌍 + 1 пробел)
fmt.Println(utf8.RuneCountInString(emoji)) // 7 символов (правильно)
```

### Сравнительная таблица кодировок

| Символ | C# (`char[]`, UTF-16) | Go (`[]byte`, UTF-8) |
|--------|----------------------|---------------------|
| `A` (ASCII) | 2 байта (`0x0041`) | 1 байт (`0x41`) |
| `П` (кириллица) | 2 байта (`0x041F`) | 2 байта (`0xD0 0x9F`) |
| `中` (иероглиф) | 2 байта (`0x4E2D`) | 3 байта (`0xE4 0xB8 0xAD`) |
| `🌍` (эмодзи) | 4 байта (surrogate pair) | 4 байта (`0xF0 0x9F 0x8C 0x8D`) |

**Вывод**: UTF-8 экономнее для ASCII и кириллицы, UTF-16 — для CJK (китайский, японский, корейский).

---

## byte и rune

### byte = uint8 (один байт)

```go
var b byte = 'A'     // ASCII символ — 1 байт
fmt.Println(b)       // 65
fmt.Printf("%c\n", b) // A

s := "hello"
fmt.Println(s[0])    // 104 (код 'h')
```

### rune = int32 (Unicode code point)

```go
var r rune = 'П'        // rune — любой Unicode символ
fmt.Println(r)           // 1055 (U+041F)
fmt.Printf("%c\n", r)   // П
fmt.Printf("U+%04X\n", r) // U+041F

r2 := '🌍'
fmt.Println(r2)          // 127757 (U+1F30D)
```

> 💡 **Для C# разработчиков**: `rune` в Go — аналог `System.Text.Rune` (.NET Core 3.0+), а не `char`. `char` в C# — это UTF-16 code unit (может быть половиной surrogate pair). `rune` в Go — полный Unicode code point, всегда один символ.

### Конвертация

```go
s := "Привет"

// string → []byte (копирование данных)
bytes := []byte(s)
fmt.Println(bytes) // [208 159 209 128 208 184 208 178 208 181 209 130]

// string → []rune (декодирование UTF-8 → Unicode code points)
runes := []rune(s)
fmt.Println(runes) // [1055 1088 1080 1074 1077 1090]
fmt.Println(len(runes)) // 6 — количество символов

// []byte → string
s2 := string(bytes)

// []rune → string
s3 := string(runes)

// rune → string
s4 := string('П') // "П"

// int → string — НЕ то, что вы ожидаете!
s5 := string(65)   // "A" (символ с кодом 65), НЕ строка "65"
s6 := strconv.Itoa(65) // "65" — правильный способ
```

---

## Итерация по строкам

### По байтам (for с индексом)

```go
s := "Привет"
for i := 0; i < len(s); i++ {
    fmt.Printf("byte[%d] = %d\n", i, s[i])
}
// byte[0] = 208, byte[1] = 159, byte[2] = 209, byte[3] = 128, ...
// 12 байтов, не 6 символов!
```

### По символам (for range)

```go
s := "Привет"
for i, r := range s {
    fmt.Printf("rune[%d] = %c (U+%04X)\n", i, r, r)
}
// rune[0] = П (U+041F)
// rune[2] = р (U+0440)   ← индекс 2, не 1! (это байтовое смещение)
// rune[4] = и (U+0438)
// rune[6] = в (U+0432)
// rune[8] = е (U+0435)
// rune[10] = т (U+0442)
```

`for range` по строке автоматически декодирует UTF-8 → rune. Индекс `i` — это **байтовое смещение**, не порядковый номер символа.

**C# аналог**:
```csharp
string s = "Привет";
// Поэлементно — char (UTF-16 code unit)
foreach (char c in s) { ... }

// По rune (.NET 5+)
foreach (Rune r in s.EnumerateRunes()) { ... }
```

### Невалидный UTF-8

```go
// Если строка содержит невалидный UTF-8, for range заменяет на U+FFFD
s := string([]byte{0xFF, 0xFE})
for _, r := range s {
    fmt.Printf("%U ", r) // U+FFFD U+FFFD
}
```

---

## Длина строки: len vs RuneCount

```go
s := "Привет, мир! 🌍"

// Количество БАЙТОВ
fmt.Println(len(s)) // 27

// Количество СИМВОЛОВ (rune)
fmt.Println(utf8.RuneCountInString(s)) // 14

// Альтернатива (менее эффективная — аллокация []rune)
fmt.Println(len([]rune(s))) // 14
```

**C# аналог**:
```csharp
string s = "Привет, мир! 🌍";
Console.WriteLine(s.Length);                          // 15 (UTF-16 code units, 🌍 = 2)
Console.WriteLine(s.EnumerateRunes().Count());        // 14 (Unicode code points)
```

---

## Индексация и срезы

### Индексация — по байтам

```go
s := "Привет"

// ❌ Получаем байт, а не символ
fmt.Println(s[0]) // 208 (первый байт буквы 'П')

// ✅ Получаем первый символ
r, size := utf8.DecodeRuneInString(s)
fmt.Printf("%c (размер: %d байта)\n", r, size) // П (размер: 2 байта)

// ✅ Получаем N-й символ (через []rune — с аллокацией)
runes := []rune(s)
fmt.Println(string(runes[0])) // П
fmt.Println(string(runes[3])) // в
```

### Срезы строк — по байтам

```go
s := "Привет"

// ❌ Срез по байтам может разрезать символ пополам
fmt.Println(s[:1]) // невалидный UTF-8 (только первый байт буквы 'П')

// ✅ Срез по правильным границам
fmt.Println(s[:2])  // "П" (первые 2 байта = первый символ)
fmt.Println(s[:4])  // "Пр" (4 байта = 2 символа)

// ✅ Срез через []rune (безопасно, но с аллокацией)
runes := []rune(s)
fmt.Println(string(runes[:3])) // "При"
```

> 💡 **Для C# разработчиков**: в C# `s[..3]` (range) всегда даёт первые 3 символа. В Go `s[:3]` даёт первые 3 **байта** — для кириллицы это 1.5 символа и невалидная строка. Это самая частая ошибка при миграции с C#.

---

## Пакет strings

### Основные функции

```go
import "strings"

s := "Hello, World!"

// Поиск
strings.Contains(s, "World")        // true
strings.HasPrefix(s, "Hello")       // true
strings.HasSuffix(s, "!")           // true
strings.Index(s, "World")          // 7 (байтовое смещение)
strings.Count(s, "l")              // 3

// Трансформация
strings.ToUpper(s)                 // "HELLO, WORLD!"
strings.ToLower(s)                 // "hello, world!"
strings.TrimSpace("  hello  ")     // "hello"
strings.Trim("***hello***", "*")   // "hello"
strings.ReplaceAll(s, "World", "Go") // "Hello, Go!"
strings.Repeat("Go ", 3)           // "Go Go Go "

// Разбиение и объединение
parts := strings.Split("a,b,c", ",")   // ["a", "b", "c"]
joined := strings.Join(parts, " | ")    // "a | b | c"
fields := strings.Fields("  foo  bar  ") // ["foo", "bar"] (по пробелам)
```

**C# аналог**:
```csharp
// Большинство методов — на самом объекте string
s.Contains("World");
s.StartsWith("Hello");
s.ToUpper();
s.Trim();
s.Replace("World", "Go");
s.Split(',');
string.Join(" | ", parts);
```

В Go строковые функции — **в пакете `strings`**, а не методы на строке. Причина: строка — базовый тип, методы к ней не добавить.

### strings.Map: трансформация по символам

```go
// Удалить все non-ASCII символы
clean := strings.Map(func(r rune) rune {
    if r > 127 {
        return -1 // -1 = удалить символ
    }
    return r
}, "Hello, Мир!")
fmt.Println(clean) // "Hello, !"
```

### strings.NewReplacer: множественная замена

```go
// Эффективная множественная замена (один проход)
r := strings.NewReplacer(
    "&", "&amp;",
    "<", "&lt;",
    ">", "&gt;",
    `"`, "&quot;",
)
escaped := r.Replace(`<a href="url">link</a>`)
// &lt;a href=&quot;url&quot;&gt;link&lt;/a&gt;
```

### strings.Cut: разбиение на две части (Go 1.18+)

```go
// Разбить строку по первому вхождению разделителя
before, after, found := strings.Cut("user:password:extra", ":")
// before="user", after="password:extra", found=true

// Полезно для парсинга key=value
key, value, _ := strings.Cut("Content-Type=application/json", "=")
```

**C# аналог**: нет прямого — обычно `IndexOf` + `Substring` или `Split` с `count: 2`.

---

## Пакет strconv: конвертация

```go
import "strconv"

// Число → строка
s := strconv.Itoa(42)           // "42"
s = strconv.FormatFloat(3.14, 'f', 2, 64) // "3.14"
s = strconv.FormatBool(true)    // "true"

// Строка → число
n, err := strconv.Atoi("42")          // 42, nil
f, err := strconv.ParseFloat("3.14", 64) // 3.14, nil
b, err := strconv.ParseBool("true")   // true, nil

// Ошибка парсинга
_, err = strconv.Atoi("abc")
// err: strconv.Atoi: parsing "abc": invalid syntax
```

**C# аналог**:
```csharp
int.Parse("42");           // исключение при ошибке
int.TryParse("42", out n); // false при ошибке
42.ToString();
```

В Go нет исключений — всегда `(value, error)`.

### fmt.Sprintf vs strconv

```go
// fmt.Sprintf — универсальный, но медленнее
s := fmt.Sprintf("%d", 42)      // "42"
s = fmt.Sprintf("%.2f", 3.14)   // "3.14"

// strconv — быстрее (без парсинга формат-строки)
s = strconv.Itoa(42)             // "42"
s = strconv.FormatFloat(3.14, 'f', 2, 64) // "3.14"

// Бенчмарк (типичные цифры):
// BenchmarkSprintf    15_000_000 ns/op    2 allocs/op
// BenchmarkItoa       50_000_000 ns/op    0 allocs/op
```

---

## strings.Builder: эффективная конкатенация

### Проблема конкатенации

```go
// ❌ Каждая конкатенация создаёт новую строку (O(n^2) по памяти)
var s string
for i := 0; i < 10000; i++ {
    s += strconv.Itoa(i) + ","  // 10000 аллокаций!
}

// ✅ strings.Builder — аналог StringBuilder в C#
var sb strings.Builder
for i := 0; i < 10000; i++ {
    sb.WriteString(strconv.Itoa(i))
    sb.WriteByte(',')
}
result := sb.String()
```

**C# аналог**:
```csharp
var sb = new StringBuilder();
for (int i = 0; i < 10000; i++)
{
    sb.Append(i);
    sb.Append(',');
}
string result = sb.ToString();
```

### Предаллокация Builder

```go
var sb strings.Builder
sb.Grow(1024) // предаллокация 1024 байт — уменьшает реаллокации

for _, item := range items {
    sb.WriteString(item)
}
```

### bytes.Buffer vs strings.Builder

| Аспект | `strings.Builder` | `bytes.Buffer` |
|--------|-------------------|----------------|
| Результат | `string` (без копирования) | `[]byte` или `string` (с копированием) |
| Запись | `WriteString`, `Write`, `WriteByte`, `WriteRune` | То же + `ReadFrom`, `WriteTo` |
| Чтение | Нет (только `String()`) | `Read`, `ReadByte`, `ReadString` |
| io.Writer | Да | Да |
| io.Reader | Нет | Да |
| Копировать нельзя | Да (panic при копировании) | Можно |
| Когда использовать | Сборка строк | Буфер для I/O |

---

## Пакет unicode/utf8

```go
import "unicode/utf8"

s := "Привет 🌍"

// Количество символов
utf8.RuneCountInString(s)          // 8

// Проверка валидности UTF-8
utf8.ValidString(s)                // true
utf8.ValidString(string([]byte{0xFF})) // false

// Декодирование первого символа
r, size := utf8.DecodeRuneInString(s)
// r = 'П', size = 2

// Декодирование последнего символа
r, size = utf8.DecodeLastRuneInString(s)
// r = '🌍', size = 4

// Размер символа в байтах
utf8.RuneLen('A')  // 1
utf8.RuneLen('П')  // 2
utf8.RuneLen('中')  // 3
utf8.RuneLen('🌍') // 4

// Кодирование rune в байты
buf := make([]byte, 4)
n := utf8.EncodeRune(buf, 'П')
// buf[:n] = [208, 159], n = 2

// Проверка: является ли байт началом rune
utf8.RuneStart(s[0]) // true (первый байт 'П')
utf8.RuneStart(s[1]) // false (продолжение 'П')
```

---

## Пакет unicode: классификация символов

```go
import "unicode"

unicode.IsLetter('A')    // true
unicode.IsLetter('5')    // false
unicode.IsDigit('5')     // true
unicode.IsSpace(' ')     // true
unicode.IsUpper('A')     // true
unicode.IsLower('a')     // true
unicode.IsPunct('!')     // true

// Проверка кириллицы
unicode.Is(unicode.Cyrillic, 'П') // true
unicode.Is(unicode.Cyrillic, 'A') // false

// Преобразование
unicode.ToUpper('a') // 'A'
unicode.ToLower('A') // 'a'
unicode.ToTitle('a') // 'A' (title case)
```

---

## Сравнение строк

```go
// == сравнивает побайтово (быстро)
"hello" == "hello" // true
"hello" == "Hello" // false

// Case-insensitive сравнение
strings.EqualFold("hello", "Hello") // true
strings.EqualFold("Привет", "привет") // true — корректно для Unicode

// ❌ Не используйте ToLower для сравнения — медленнее и некорректно для некоторых языков
strings.ToLower("Hello") == strings.ToLower("hello") // работает, но хуже

// Лексикографическое сравнение
strings.Compare("a", "b") // -1 (a < b)
// Но проще: if a < b { ... } — оператор < работает со строками
```

**C# аналог**:
```csharp
string.Equals("hello", "Hello", StringComparison.OrdinalIgnoreCase);
// В Go нет StringComparison — только EqualFold для case-insensitive
```

---

## Типичные ошибки C# разработчиков

### 1. len() возвращает байты, не символы

```go
// ❌ Ожидание: длина кириллической строки = количество букв
s := "Привет"
if len(s) == 6 { // false! len(s) == 12
    // ...
}

// ✅ Для символов
if utf8.RuneCountInString(s) == 6 { // true
    // ...
}
```

### 2. Индексация разрезает символ

```go
// ❌ Отрезаем "первые 3 символа" кириллицы
s := "Привет"
first3 := s[:3] // "П" + первый байт 'р' = невалидный UTF-8!

// ✅ Через []rune
first3 = string([]rune(s)[:3]) // "При"
```

### 3. Конкатенация в цикле

```go
// ❌ O(n^2) по памяти
result := ""
for _, s := range items {
    result += s
}

// ✅ strings.Builder
var sb strings.Builder
for _, s := range items {
    sb.WriteString(s)
}
result := sb.String()

// ✅ strings.Join (если элементы уже в слайсе)
result := strings.Join(items, "")
```

### 4. string(int) — не то, что ожидается

```go
// ❌ Ожидание: число → строка "65"
s := string(65)  // "A" (символ с кодом 65)

// ✅ Число → строка
s = strconv.Itoa(65) // "65"
s = fmt.Sprintf("%d", 65) // "65"
```

### 5. Мутация строк

```go
// ❌ Строки иммутабельны — нельзя менять отдельные символы
s := "hello"
// s[0] = 'H' // ошибка компиляции

// ✅ Через []byte (для ASCII)
b := []byte(s)
b[0] = 'H'
s = string(b) // "Hello"

// ✅ Через []rune (для Unicode)
r := []rune("Привет")
r[0] = 'п' // 'П' → 'п'
s = string(r) // "привет"
```

---

## Производительность

### Бенчмарк: конкатенация

```go
// Сборка строки из 10000 элементов
func BenchmarkConcat(b *testing.B) {
    for b.Loop() {
        var s string
        for i := 0; i < 10000; i++ {
            s += "x"
        }
    }
}

func BenchmarkBuilder(b *testing.B) {
    for b.Loop() {
        var sb strings.Builder
        for i := 0; i < 10000; i++ {
            sb.WriteString("x")
        }
        _ = sb.String()
    }
}

func BenchmarkBuilderGrow(b *testing.B) {
    for b.Loop() {
        var sb strings.Builder
        sb.Grow(10000)
        for i := 0; i < 10000; i++ {
            sb.WriteString("x")
        }
        _ = sb.String()
    }
}

// Результат (типичный):
// BenchmarkConcat-8          100    52_000_000 ns/op    53_000_000 B/op    10000 allocs/op
// BenchmarkBuilder-8       20000        55_000 ns/op        40960 B/op       12 allocs/op
// BenchmarkBuilderGrow-8   30000        35_000 ns/op        10240 B/op        1 allocs/op
//
// Builder в ~1000x быстрее конкатенации, Grow ещё ускоряет
```

### Конвертация string ↔ []byte: скрытые копии

```go
s := "hello"

// Каждая конвертация — копирование данных
b := []byte(s) // аллокация + копия 5 байт
s2 := string(b) // аллокация + копия 5 байт

// Компилятор Go оптимизирует некоторые случаи (без копирования):
// 1. for range []byte(s) — не копирует
// 2. string(b) в сравнении: if string(b) == "hello" — не копирует
// 3. map lookup: m[string(b)] — не копирует
// 4. Конкатенация: "prefix" + string(b) — может не копировать
```

### unsafe-конвертация (только если критически важна производительность)

```go
import "unsafe"

// ⚠️ Без копирования, но опасно: изменение b сломает s
func unsafeString(b []byte) string {
    return unsafe.String(unsafe.SliceData(b), len(b))
}

func unsafeBytes(s string) []byte {
    return unsafe.Slice(unsafe.StringData(s), len(s))
}

// Используйте только после профилирования, если конвертация — bottleneck
```

---

## Шпаргалка

| Задача | Go | C# |
|--------|----|----|
| Длина в символах | `utf8.RuneCountInString(s)` | `s.Length` (но не для surrogate pairs) |
| Длина в байтах | `len(s)` | `Encoding.UTF8.GetByteCount(s)` |
| N-й символ | `[]rune(s)[n]` | `s[n]` |
| Итерация по символам | `for _, r := range s` | `foreach (var r in s.EnumerateRunes())` |
| Конкатенация | `strings.Builder` / `strings.Join` | `StringBuilder` / `string.Join` |
| Содержит подстроку | `strings.Contains(s, sub)` | `s.Contains(sub)` |
| Начинается с | `strings.HasPrefix(s, prefix)` | `s.StartsWith(prefix)` |
| Разбиение | `strings.Split(s, sep)` | `s.Split(sep)` |
| Замена | `strings.ReplaceAll(s, old, new)` | `s.Replace(old, new)` |
| Trim | `strings.TrimSpace(s)` | `s.Trim()` |
| Upper/Lower | `strings.ToUpper(s)` | `s.ToUpper()` |
| Case-insensitive = | `strings.EqualFold(a, b)` | `string.Equals(a, b, OrdinalIgnoreCase)` |
| int → string | `strconv.Itoa(n)` | `n.ToString()` |
| string → int | `strconv.Atoi(s)` | `int.Parse(s)` / `int.TryParse(s)` |
| Форматирование | `fmt.Sprintf(...)` | `string.Format(...)` / `$"..."` |
| Интерполяция | Нет (только `fmt.Sprintf`) | `$"Hello, {name}!"` |
