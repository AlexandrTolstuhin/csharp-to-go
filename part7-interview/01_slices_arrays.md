# Задачи на слайсы и массивы

---

## Введение: что проверяют

Задачи на слайсы — самые частые на Go-интервью **любого уровня**. Они кажутся простыми, но именно здесь выявляются фундаментальные непонимания:

- Слайс — это **дескриптор** (pointer + len + cap), а не объект
- `append` может создать **новый backing array**, разорвав связь со старым
- Срез `s[a:b]` **разделяет память** с оригиналом
- `copy` копирует `min(len(dst), len(src))` элементов

### Типичные вопросы к кандидату

- "Чем слайс отличается от массива в Go?"
- "Что произойдёт при append за пределами capacity?"
- "Как безопасно скопировать слайс?"
- "Когда нужен make с capacity?"

---

## Задача 1: Reverse slice

**Компания**: Встречается повсеместно — Авито, Wildberries, Озон
**Уровень**: Junior
**Время**: 5 минут

### Формулировка

> Напиши функцию, которая переворачивает слайс целых чисел на месте (in-place).

```
Вход:  [1, 2, 3, 4, 5]
Выход: [5, 4, 3, 2, 1]
```

### Что проверяют

- Понимание in-place операций
- Нужна ли новая аллокация
- Идиоматичность кода (одновременное присваивание)

### Разбор

Классическое решение: два указателя с двух сторон, движутся навстречу. Никакой дополнительной памяти не нужно.

**C# аналог**:
```csharp
// C# — Array.Reverse работает in-place
Array.Reverse(arr);

// Или вручную
for (int i = 0, j = arr.Length - 1; i < j; i++, j--)
    (arr[i], arr[j]) = (arr[j], arr[i]);
```

**Go решение**:
```go
// ✅ Идиоматично: swap через множественное присваивание
func reverse(s []int) {
    for i, j := 0, len(s)-1; i < j; i, j = i+1, j-1 {
        s[i], s[j] = s[j], s[i]
    }
}

// Использование:
s := []int{1, 2, 3, 4, 5}
reverse(s)
fmt.Println(s) // [5 4 3 2 1]
```

### Типичные ошибки

```go
// ❌ Создают новый слайс — не in-place
func reverse(s []int) []int {
    result := make([]int, len(s))
    for i, v := range s {
        result[len(s)-1-i] = v
    }
    return result // нарушает требование "in-place"
}

// ❌ Временная переменная для swap — не нужна в Go
tmp := s[i]
s[i] = s[j]
s[j] = tmp
// В Go используем: s[i], s[j] = s[j], s[i]
```

### Дополнительные вопросы

- "Как написать обобщённую версию с generics?"
- "Как вернуть новый слайс, не трогая оригинал?"

**Generic версия (Go 1.21+)**:
```go
import "slices"

s := []int{1, 2, 3, 4, 5}
slices.Reverse(s)              // in-place (Go 1.21+)
rev := slices.Clone(s)
slices.Reverse(rev)            // новый слайс
```

---

## Задача 2: Удаление дубликатов

**Компания**: Яндекс, Авито, Озон
**Уровень**: Junior / Middle
**Время**: 10 минут

### Формулировка

> Напиши функцию, которая удаляет дубликаты из слайса, сохраняя порядок элементов. Слайс **не отсортирован**.

```
Вход:  [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
Выход: [3, 1, 4, 5, 9, 2, 6]
```

### Что проверяют

- Выбор структуры данных (map для O(1) поиска)
- Сохранение порядка
- Оценка сложности O(n) vs O(n²)

### Разбор

Наивное решение — вложенные циклы — O(n²). Правильное — map для трекинга посещённых элементов, O(n).

**C# аналог**:
```csharp
// C# — LINQ подход
var result = list.Distinct().ToList();

// Или вручную с HashSet
var seen = new HashSet<int>();
var result = list.Where(seen.Add).ToList();
```

**Go решение**:
```go
// ✅ Идиоматично: map как set + slice для порядка
func deduplicate(s []int) []int {
    seen := make(map[int]struct{}, len(s))
    result := make([]int, 0, len(s))

    for _, v := range s {
        if _, ok := seen[v]; !ok {
            seen[v] = struct{}{}
            result = append(result, v)
        }
    }
    return result
}

// Тест:
fmt.Println(deduplicate([]int{3, 1, 4, 1, 5, 9, 2, 6, 5, 3}))
// [3 1 4 5 9 2 6]
```

> 💡 `struct{}{}` — пустая структура для имитации set. Занимает 0 байт. Это идиома Go.

### Generic версия

```go
// Go 1.21+ — уже есть в стандартной библиотеке
import "slices"

s := []int{3, 1, 4, 1, 5, 9, 2, 6, 5, 3}
slices.Sort(s)
s = slices.Compact(s) // удаляет соседние дубликаты
// НО: меняет порядок! Для сохранения порядка — только map-подход
```

**Generic функция**:
```go
func deduplicate[T comparable](s []T) []T {
    seen := make(map[T]struct{}, len(s))
    result := make([]T, 0, len(s))
    for _, v := range s {
        if _, ok := seen[v]; !ok {
            seen[v] = struct{}{}
            result = append(result, v)
        }
    }
    return result
}
```

### Дополнительные вопросы

- "Как изменить решение, если слайс отсортирован?" → два указателя, O(n) без map
- "Как сделать in-place?" → тот же two-pointer trick
- "Какая сложность по памяти?" → O(n) на map

**In-place для отсортированного слайса**:
```go
// Если слайс отсортирован — O(n) времени, O(1) памяти
func deduplicateSorted(s []int) []int {
    if len(s) == 0 {
        return s
    }
    i := 0
    for j := 1; j < len(s); j++ {
        if s[j] != s[i] {
            i++
            s[i] = s[j]
        }
    }
    return s[:i+1]
}
```

---

## Задача 3: Rotate slice

**Компания**: Яндекс, ВКонтакте
**Уровень**: Middle
**Время**: 15 минут

### Формулировка

> Реализуй функцию `rotate(s []int, k int)`, которая сдвигает слайс на `k` позиций влево. Операция должна быть in-place.

```
rotate([1,2,3,4,5], 2) → [3,4,5,1,2]
rotate([1,2,3,4,5], 7) → [3,4,5,1,2]  // k > len(s), k % len
```

### Что проверяют

- Обработка граничных случаев (`k > len`, `k < 0`, пустой слайс)
- Знание трюка с тройным переворотом (O(n) время, O(1) память)
- Умение рассуждать о сложности

### Разбор

**Наивное решение**: скопировать во временный слайс — O(n) памяти.

**Оптимальное решение**: трёхкратный reverse — O(n) время, O(1) память:

```
rotate([1,2,3,4,5], k=2):
1. reverse([1,2])    → [2,1,3,4,5]
2. reverse([3,4,5])  → [2,1,5,4,3]
3. reverse всего     → [3,4,5,1,2]
```

**Go решение**:
```go
func reverse(s []int) {
    for i, j := 0, len(s)-1; i < j; i, j = i+1, j-1 {
        s[i], s[j] = s[j], s[i]
    }
}

// ✅ Тройной reverse — in-place, O(n) время, O(1) память
func rotateLeft(s []int, k int) {
    n := len(s)
    if n == 0 {
        return
    }
    k = k % n // обработка k > n и k < 0
    if k < 0 {
        k += n
    }
    if k == 0 {
        return
    }

    reverse(s[:k])
    reverse(s[k:])
    reverse(s)
}

// Тест:
s := []int{1, 2, 3, 4, 5}
rotateLeft(s, 2)
fmt.Println(s) // [3 4 5 1 2]

rotateLeft(s, 7) // k=7%5=2
// [3 4 5 1 2] → [5 1 2 3 4]... нет, применяем к текущему состоянию
```

### Наивное решение (с объяснением)

```go
// ✅ Простое, читаемое, O(n) память — вполне приемлемо на интервью
func rotateLeftSimple(s []int, k int) []int {
    n := len(s)
    if n == 0 {
        return s
    }
    k = ((k % n) + n) % n // нормализация, работает и для отрицательных
    return append(s[k:], s[:k]...)
}
```

> 💡 На интервью сначала покажи простое решение, потом предложи оптимизацию — это правильная стратегия.

### Дополнительные вопросы

- "Как сделать rotate вправо?" → `rotateLeft(s, n-k)`
- "Можно ли без аллокации вообще?" → трёхкратный reverse
- "Что такое `s[k:]` и `s[:k]`? Они копируют данные?" → нет, это срезы с shared backing array

---

## Задача 4: Пересечение двух слайсов

**Компания**: Авито, Озон, Тинькофф
**Уровень**: Junior / Middle
**Время**: 10 минут

### Формулировка

> Напиши функцию `intersection(a, b []int) []int`, которая возвращает элементы, присутствующие в обоих слайсах. Дубликаты в результате не допускаются.

```
intersection([1,2,3,4], [3,4,5,6]) → [3,4]
intersection([1,1,2], [1,1,3])     → [1]
```

### Go решение

```go
// ✅ O(n+m) через map
func intersection(a, b []int) []int {
    // Строим set из меньшего слайса
    set := make(map[int]struct{}, len(a))
    for _, v := range a {
        set[v] = struct{}{}
    }

    result := make([]int, 0)
    seen := make(map[int]struct{}) // чтобы не добавлять дубликаты

    for _, v := range b {
        if _, ok := set[v]; ok {
            if _, dup := seen[v]; !dup {
                result = append(result, v)
                seen[v] = struct{}{}
            }
        }
    }
    return result
}
```

### Дополнительные вопросы

- "Как найти объединение?" → собрать оба в set
- "Как найти разность A\B?" → элементы из A, которых нет в B
- "Как оптимизировать по памяти?" → если один из слайсов отсортирован — two pointers

---

## Задача 5: Flatten вложенных слайсов

**Компания**: ВКонтакте, Яндекс
**Уровень**: Middle
**Время**: 10 минут

### Формулировка

> Напиши функцию, которая "выпрямляет" слайс слайсов в одномерный слайс.

```
flatten([[1,2], [3,4], [5]]) → [1,2,3,4,5]
```

### Go решение

```go
// ✅ Вариант 1: с предварительным подсчётом размера (одна аллокация)
func flatten(s [][]int) []int {
    total := 0
    for _, sub := range s {
        total += len(sub)
    }

    result := make([]int, 0, total) // pre-allocate — важно для производительности
    for _, sub := range s {
        result = append(result, sub...)
    }
    return result
}

// ✅ Вариант 2: использование стандартной библиотеки (Go 1.22+)
import "slices"

func flattenStdlib(s [][]int) []int {
    return slices.Concat(s...)
}
```

> 💡 Упоминание `slices.Concat` показывает знание стандартной библиотеки — плюс на интервью.

### Generic версия

```go
func flatten[T any](s [][]T) []T {
    total := 0
    for _, sub := range s {
        total += len(sub)
    }
    result := make([]T, 0, total)
    for _, sub := range s {
        result = append(result, sub...)
    }
    return result
}
```

---

## Задача 6: Chunk — разбивка на части

**Компания**: Wildberries, Авито (batch-обработка)
**Уровень**: Middle
**Время**: 10 минут

### Формулировка

> Напиши функцию `chunk(s []int, size int) [][]int`, которая разбивает слайс на чанки заданного размера.

```
chunk([1,2,3,4,5,6,7], 3) → [[1,2,3], [4,5,6], [7]]
chunk([1,2], 5)            → [[1,2]]
chunk([], 3)               → []
```

### Что проверяют

- Обработка граничных случаев
- Понимание, что срезы делят память (нужно ли копировать?)
- Практическая применимость (batch обработка в API)

### Go решение

```go
// ✅ Через срезы (shared memory — экономно, но осторожно)
func chunk(s []int, size int) [][]int {
    if size <= 0 || len(s) == 0 {
        return nil
    }

    result := make([][]int, 0, (len(s)+size-1)/size)
    for len(s) > 0 {
        n := size
        if n > len(s) {
            n = len(s)
        }
        result = append(result, s[:n])
        s = s[n:]
    }
    return result
}
```

> ⚠️ Чанки разделяют память с оригинальным слайсом! Если планируется модифицировать — нужно `copy`.

```go
// ✅ С копированием (безопаснее для долгоживущих данных)
func chunkCopy(s []int, size int) [][]int {
    if size <= 0 || len(s) == 0 {
        return nil
    }

    result := make([][]int, 0, (len(s)+size-1)/size)
    for i := 0; i < len(s); i += size {
        end := i + size
        if end > len(s) {
            end = len(s)
        }
        chunk := make([]int, end-i)
        copy(chunk, s[i:end])
        result = append(result, chunk)
    }
    return result
}
```

### Применение в реальных задачах

```go
// Батч-вставка в БД — реальная задача из Wildberries/Авито
func insertBatch(ctx context.Context, ids []int64) error {
    for _, batch := range chunk(ids, 1000) { // PostgreSQL лимит параметров
        if err := db.InsertMany(ctx, batch); err != nil {
            return err
        }
    }
    return nil
}
```

---

## Задача 7: Что выведет код — gotchas

**Компания**: Яндекс, ВКонтакте (проверка глубины знания)
**Уровень**: Middle / Senior
**Время**: 5 минут на каждый пример

### Что проверяют

Понимание внутренней работы слайсов — header (pointer + len + cap) и shared backing array.

---

### Gotcha 1: Append и shared memory

```go
a := []int{1, 2, 3, 4, 5}
b := a[:3]    // b = [1 2 3], cap(b) = 5 — shared!

b = append(b, 99)  // cap не превышен → пишем в shared array

fmt.Println(a) // ?
fmt.Println(b) // ?
```

<details>
<summary>Ответ</summary>

```
a: [1 2 99 4 5]  ← a[3] изменился!
b: [1 2 3 99]
```

`b` и `a` делят backing array. `append(b, 99)` записывает 99 в `a[3]`, потому что `cap(b) = 5` и места хватает.

**Защита через full slice expression**:
```go
b := a[:3:3] // cap(b) = 3, следующий append создаст новый array
b = append(b, 99) // теперь a не тронут
```

</details>

---

### Gotcha 2: Loop variable capture (до Go 1.22)

```go
// Go до 1.22
s := []int{1, 2, 3}
funcs := make([]func(), len(s))

for i, v := range s {
    funcs[i] = func() { fmt.Println(v) }
}

for _, f := range funcs {
    f()
}
```

<details>
<summary>Ответ</summary>

**Go < 1.22**:
```
3
3
3
```
Все замыкания захватывают одну переменную `v`, которая после цикла равна 3.

**Go 1.22+** (изменение семантики): каждая итерация создаёт новую переменную — вывод будет `1 2 3`.

Правильное решение для старых версий:
```go
for i, v := range s {
    v := v // новая переменная в области цикла
    funcs[i] = func() { fmt.Println(v) }
}
```

> 💡 Упомяни версию Go — интервьюер оценит знание истории изменения семантики.

</details>

---

### Gotcha 3: Nil slice vs Empty slice

```go
var a []int        // nil slice
b := []int{}       // empty slice
c := make([]int, 0) // empty slice

fmt.Println(a == nil) // ?
fmt.Println(b == nil) // ?
fmt.Println(len(a), len(b)) // ?

a = append(a, 1) // работает?
```

<details>
<summary>Ответ</summary>

```
true
false
0 0
```

`append` к nil-слайсу — **корректная операция**, Go создаёт backing array.

Практические выводы:
- `json.Marshal(nil)` → `"null"`, `json.Marshal([]int{})` → `"[]"` — важно для API!
- Для функций, возвращающих слайс: возвращай `nil` если нечего вернуть, не `[]T{}`
- `len(nil)` → 0, `range nil` → 0 итераций — всё безопасно

</details>

---

### Gotcha 4: Copy и длина

```go
src := []int{1, 2, 3, 4, 5}
dst := make([]int, 3)

n := copy(dst, src)

fmt.Println(dst, n) // ?
```

<details>
<summary>Ответ</summary>

```
[1 2 3] 3
```

`copy` копирует `min(len(dst), len(src))` элементов. Возвращает количество скопированных.

**Частая ошибка**:
```go
dst := make([]int, 0, 5) // cap=5, но len=0!
copy(dst, src)            // скопирует 0 элементов!

// Правильно:
dst := make([]int, len(src))
copy(dst, src)
```

</details>

---

## Задача 8: Фильтрация без аллокаций

**Компания**: Авито, Яндекс (оптимизационные задачи)
**Уровень**: Senior
**Время**: 15 минут

### Формулировка

> Напиши функцию `filter`, которая удаляет из слайса элементы, не удовлетворяющие предикату. Без создания нового слайса (in-place), O(1) дополнительной памяти.

### Что проверяют

- Понимание трюка "write pointer"
- Рассуждение об аллокациях
- Generic код

### Go решение

```go
// ✅ In-place filter через write pointer
func filter(s []int, keep func(int) bool) []int {
    write := 0
    for _, v := range s {
        if keep(v) {
            s[write] = v
            write++
        }
    }
    return s[:write] // trim хвост
}

// Использование:
nums := []int{1, 2, 3, 4, 5, 6, 7, 8}
evens := filter(nums, func(n int) bool { return n%2 == 0 })
fmt.Println(evens) // [2 4 6 8]
// nums до write pointer: [2 4 6 8 5 6 7 8] — хвост не важен
```

**Generic версия**:
```go
func filter[T any](s []T, keep func(T) bool) []T {
    write := 0
    for _, v := range s {
        if keep(v) {
            s[write] = v
            write++
        }
    }
    return s[:write]
}
```

### Почему это важно

```go
// ❌ C#-стиль — LINQ создаёт новый IEnumerable, потом ToList → 2 аллокации
var result = list.Where(x => x % 2 == 0).ToList();

// ✅ Go-стиль — zero allocation, работаем с тем же backing array
nums = filter(nums, func(n int) bool { return n%2 == 0 })
```

---

## Итоги: что запомнить

| Задача | Ключевая идея | Сложность |
|--------|---------------|-----------|
| Reverse | Two pointers + swap in-place | O(n) / O(1) |
| Deduplicate | Map как set для O(1) поиска | O(n) / O(n) |
| Rotate | Тройной reverse или срез+append | O(n) / O(1) или O(n) |
| Intersection | Map из меньшего + проход по большему | O(n+m) / O(n) |
| Flatten | Предварительный подсчёт → одна аллокация | O(n) / O(n) |
| Chunk | Срезы с shared memory или copy | O(n) / O(n) |
| Filter in-place | Write pointer | O(n) / O(1) |

### Чеклист перед ответом

- [ ] Проверил граничные случаи: nil, пустой слайс, один элемент
- [ ] Оценил сложность по времени и памяти
- [ ] Упомянул про shared memory там, где это важно
- [ ] Предложил generic версию, если это уместно
- [ ] Проверил граничное условие `k % n` для rotate

---
