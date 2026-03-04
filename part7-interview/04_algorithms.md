# 7.4 Алгоритмические задачи

## Содержание

- [Введение: специфика российских компаний](#%D0%B2%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81%D0%BF%D0%B5%D1%86%D0%B8%D1%84%D0%B8%D0%BA%D0%B0-%D1%80%D0%BE%D1%81%D1%81%D0%B8%D0%B9%D1%81%D0%BA%D0%B8%D1%85-%D0%BA%D0%BE%D0%BC%D0%BF%D0%B0%D0%BD%D0%B8%D0%B9)
  - [Яндекс](#%D1%8F%D0%BD%D0%B4%D0%B5%D0%BA%D1%81)
  - [Авито, Озон, Wildberries](#%D0%B0%D0%B2%D0%B8%D1%82%D0%BE-%D0%BE%D0%B7%D0%BE%D0%BD-wildberries)
  - [Тинькофф](#%D1%82%D0%B8%D0%BD%D1%8C%D0%BA%D0%BE%D1%84%D1%84)
  - [Сбер, МТС](#%D1%81%D0%B1%D0%B5%D1%80-%D0%BC%D1%82%D1%81)
- [Задача 1: LRU Cache](#%D0%B7%D0%B0%D0%B4%D0%B0%D1%87%D0%B0-1-lru-cache)
  - [Формулировка](#%D1%84%D0%BE%D1%80%D0%BC%D1%83%D0%BB%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D0%B0)
  - [Что проверяют](#%D1%87%D1%82%D0%BE-%D0%BF%D1%80%D0%BE%D0%B2%D0%B5%D1%80%D1%8F%D1%8E%D1%82)
  - [Go решение](#go-%D1%80%D0%B5%D1%88%D0%B5%D0%BD%D0%B8%D0%B5)
  - [Thread-safe версия](#thread-safe-%D0%B2%D0%B5%D1%80%D1%81%D0%B8%D1%8F)
  - [Дополнительные вопросы](#%D0%B4%D0%BE%D0%BF%D0%BE%D0%BB%D0%BD%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D1%8B%D0%B5-%D0%B2%D0%BE%D0%BF%D1%80%D0%BE%D1%81%D1%8B)
- [Задача 2: Two Sum](#%D0%B7%D0%B0%D0%B4%D0%B0%D1%87%D0%B0-2-two-sum)
  - [Формулировка](#%D1%84%D0%BE%D1%80%D0%BC%D1%83%D0%BB%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D0%B0-1)
  - [Что проверяют](#%D1%87%D1%82%D0%BE-%D0%BF%D1%80%D0%BE%D0%B2%D0%B5%D1%80%D1%8F%D1%8E%D1%82-1)
  - [Вариации (могут спросить следом)](#%D0%B2%D0%B0%D1%80%D0%B8%D0%B0%D1%86%D0%B8%D0%B8-%D0%BC%D0%BE%D0%B3%D1%83%D1%82-%D1%81%D0%BF%D1%80%D0%BE%D1%81%D0%B8%D1%82%D1%8C-%D1%81%D0%BB%D0%B5%D0%B4%D0%BE%D0%BC)
- [Задача 3: Валидация скобок](#%D0%B7%D0%B0%D0%B4%D0%B0%D1%87%D0%B0-3-%D0%B2%D0%B0%D0%BB%D0%B8%D0%B4%D0%B0%D1%86%D0%B8%D1%8F-%D1%81%D0%BA%D0%BE%D0%B1%D0%BE%D0%BA)
  - [Формулировка](#%D1%84%D0%BE%D1%80%D0%BC%D1%83%D0%BB%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D0%B0-2)
  - [Go решение](#go-%D1%80%D0%B5%D1%88%D0%B5%D0%BD%D0%B8%D0%B5-1)
  - [Вариация: генерация всех корректных скобочных выражений](#%D0%B2%D0%B0%D1%80%D0%B8%D0%B0%D1%86%D0%B8%D1%8F-%D0%B3%D0%B5%D0%BD%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D0%B2%D1%81%D0%B5%D1%85-%D0%BA%D0%BE%D1%80%D1%80%D0%B5%D0%BA%D1%82%D0%BD%D1%8B%D1%85-%D1%81%D0%BA%D0%BE%D0%B1%D0%BE%D1%87%D0%BD%D1%8B%D1%85-%D0%B2%D1%8B%D1%80%D0%B0%D0%B6%D0%B5%D0%BD%D0%B8%D0%B9)
- [Задача 4: Анаграммы](#%D0%B7%D0%B0%D0%B4%D0%B0%D1%87%D0%B0-4-%D0%B0%D0%BD%D0%B0%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D1%8B)
  - [Формулировка](#%D1%84%D0%BE%D1%80%D0%BC%D1%83%D0%BB%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D0%B0-3)
  - [Go решение](#go-%D1%80%D0%B5%D1%88%D0%B5%D0%BD%D0%B8%D0%B5-2)
- [Задача 5: Бинарный поиск](#%D0%B7%D0%B0%D0%B4%D0%B0%D1%87%D0%B0-5-%D0%B1%D0%B8%D0%BD%D0%B0%D1%80%D0%BD%D1%8B%D0%B9-%D0%BF%D0%BE%D0%B8%D1%81%D0%BA)
  - [Формулировка](#%D1%84%D0%BE%D1%80%D0%BC%D1%83%D0%BB%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D0%B0-4)
  - [Go решение](#go-%D1%80%D0%B5%D1%88%D0%B5%D0%BD%D0%B8%D0%B5-3)
  - [Вариация: поиск в повёрнутом отсортированном массиве](#%D0%B2%D0%B0%D1%80%D0%B8%D0%B0%D1%86%D0%B8%D1%8F-%D0%BF%D0%BE%D0%B8%D1%81%D0%BA-%D0%B2-%D0%BF%D0%BE%D0%B2%D1%91%D1%80%D0%BD%D1%83%D1%82%D0%BE%D0%BC-%D0%BE%D1%82%D1%81%D0%BE%D1%80%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%BD%D0%BE%D0%BC-%D0%BC%D0%B0%D1%81%D1%81%D0%B8%D0%B2%D0%B5)
- [Задача 6: Merge Sorted Arrays](#%D0%B7%D0%B0%D0%B4%D0%B0%D1%87%D0%B0-6-merge-sorted-arrays)
  - [Формулировка](#%D1%84%D0%BE%D1%80%D0%BC%D1%83%D0%BB%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D0%B0-5)
  - [Go решение](#go-%D1%80%D0%B5%D1%88%D0%B5%D0%BD%D0%B8%D0%B5-4)
- [Задача 7: Top K элементов](#%D0%B7%D0%B0%D0%B4%D0%B0%D1%87%D0%B0-7-top-k-%D1%8D%D0%BB%D0%B5%D0%BC%D0%B5%D0%BD%D1%82%D0%BE%D0%B2)
  - [Формулировка](#%D1%84%D0%BE%D1%80%D0%BC%D1%83%D0%BB%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D0%B0-6)
  - [Go решение](#go-%D1%80%D0%B5%D1%88%D0%B5%D0%BD%D0%B8%D0%B5-5)
- [Задача 8: Реализация стека и очереди](#%D0%B7%D0%B0%D0%B4%D0%B0%D1%87%D0%B0-8-%D1%80%D0%B5%D0%B0%D0%BB%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-%D1%81%D1%82%D0%B5%D0%BA%D0%B0-%D0%B8-%D0%BE%D1%87%D0%B5%D1%80%D0%B5%D0%B4%D0%B8)
  - [Формулировка](#%D1%84%D0%BE%D1%80%D0%BC%D1%83%D0%BB%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D0%B0-7)
  - [Go решение](#go-%D1%80%D0%B5%D1%88%D0%B5%D0%BD%D0%B8%D0%B5-6)
- [Шпаргалка: сложность задач](#%D1%88%D0%BF%D0%B0%D1%80%D0%B3%D0%B0%D0%BB%D0%BA%D0%B0-%D1%81%D0%BB%D0%BE%D0%B6%D0%BD%D0%BE%D1%81%D1%82%D1%8C-%D0%B7%D0%B0%D0%B4%D0%B0%D1%87)

---

## Введение: специфика российских компаний

### Яндекс

Яндекс — самый строгий работодатель по алгоритмам. Ожидается LeetCode Medium стабильно, LeetCode Hard на Senior уровне. Проводится 3-4 алгоритмических раунда.

**Популярные темы**: строки, sliding window, two pointers, dynamic programming, деревья, графы.

### Авито, Озон, Wildberries

Больше прагматики. Задачи уровня Medium, акцент на:
- Структуры данных (LRU cache — хит)
- Конкурентные задачи
- "Напиши рабочий код, объясни сложность"

### Тинькофф

Финтех-специфика: задачи на работу с числами, округления, денежная арифметика.

### Сбер, МТС

Задачи попроще, важнее объяснить ход мысли и подход к решению.

---

## Задача 1: LRU Cache

**Компания**: Яндекс, Авито, ВКонтакте (спрашивают почти везде!)
**Уровень**: Middle / Senior
**Время**: 25-30 минут

### Формулировка

> Реализуй LRU (Least Recently Used) кэш с операциями `Get(key int) int` и `Put(key, value int)`. Кэш имеет фиксированную ёмкость. Если кэш заполнен и нужно добавить новый элемент — удаляй наименее недавно использованный.
>
> `Get` должен возвращать -1 если ключ не найден. `Get` и `Put` должны работать за O(1).

### Что проверяют

- Понимание, что для O(1) нужна **doubly-linked list + hash map**
- Умение реализовать linked list на Go через `container/list`
- Аккуратность с указателями при удалении/добавлении узлов

**C# аналог**:
```csharp
// C# — нет готового LRU, но есть LinkedList<T> + Dictionary
// Или использовать MemoryCache с SlidingExpiration
```

### Go решение

```go
package lrucache

import "container/list"

type LRUCache struct {
    cap   int
    cache map[int]*list.Element
    list  *list.List // front = most recent, back = least recent
}

type entry struct {
    key   int
    value int
}

func NewLRUCache(capacity int) *LRUCache {
    return &LRUCache{
        cap:   capacity,
        cache: make(map[int]*list.Element, capacity),
        list:  list.New(),
    }
}

func (c *LRUCache) Get(key int) int {
    el, ok := c.cache[key]
    if !ok {
        return -1
    }
    // Перемещаем в начало (наиболее свежий)
    c.list.MoveToFront(el)
    return el.Value.(*entry).value
}

func (c *LRUCache) Put(key, value int) {
    // Если уже есть — обновляем и перемещаем в начало
    if el, ok := c.cache[key]; ok {
        el.Value.(*entry).value = value
        c.list.MoveToFront(el)
        return
    }

    // Если кэш заполнен — удаляем самый старый (из конца)
    if c.list.Len() == c.cap {
        oldest := c.list.Back()
        if oldest != nil {
            c.list.Remove(oldest)
            delete(c.cache, oldest.Value.(*entry).key)
        }
    }

    // Добавляем новый элемент в начало
    el := c.list.PushFront(&entry{key: key, value: value})
    c.cache[key] = el
}
```

**Пример использования**:
```go
cache := NewLRUCache(2)
cache.Put(1, 1)      // cache: {1=1}
cache.Put(2, 2)      // cache: {1=1, 2=2}
cache.Get(1)         // returns 1, cache: {2=2, 1=1}
cache.Put(3, 3)      // evicts key 2, cache: {1=1, 3=3}
cache.Get(2)         // returns -1 (not found)
cache.Put(4, 4)      // evicts key 1, cache: {3=3, 4=4}
cache.Get(1)         // returns -1
cache.Get(3)         // returns 3
cache.Get(4)         // returns 4
```

### Thread-safe версия

```go
// ✅ Для production добавляем mutex
type SafeLRUCache struct {
    mu sync.Mutex
    LRUCache
}

func (c *SafeLRUCache) Get(key int) int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.LRUCache.Get(key)
}

func (c *SafeLRUCache) Put(key, value int) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.LRUCache.Put(key, value)
}
```

### Дополнительные вопросы

- "Как реализовать без `container/list`, через собственный linked list?" → структура с полями prev/next
- "LFU (Least Frequently Used) — чем отличается от LRU?" → LFU учитывает частоту, не только время
- "Как добавить TTL?" → добавить поле `expiresAt` в entry, проверять при Get

---

## Задача 2: Two Sum

**Компания**: Яндекс, Авито (разогревочная задача)
**Уровень**: Junior / Middle
**Время**: 10 минут

### Формулировка

> Дан массив целых чисел и целевое значение `target`. Найди два числа в массиве, сумма которых равна `target`. Верни их индексы. Предполагается, что ровно одно решение существует.

```
twoSum([2, 7, 11, 15], 9) → [0, 1]  // 2 + 7 = 9
twoSum([3, 2, 4], 6) → [1, 2]        // 2 + 4 = 6
```

### Что проверяют

- Умение перейти от O(n²) к O(n) через map
- Правильное использование map для "комплемента"

```go
// ✅ O(n) через map: комплемент = target - current
func twoSum(nums []int, target int) []int {
    seen := make(map[int]int) // значение → индекс

    for i, n := range nums {
        complement := target - n
        if j, ok := seen[complement]; ok {
            return []int{j, i}
        }
        seen[n] = i
    }
    return nil // задача гарантирует, что решение есть
}
```

### Вариации (могут спросить следом)

```go
// Three Sum: три числа, сумма = 0
// Подход: sort + two pointers для O(n²)
func threeSum(nums []int) [][]int {
    slices.Sort(nums)
    var result [][]int

    for i := 0; i < len(nums)-2; i++ {
        if i > 0 && nums[i] == nums[i-1] {
            continue // пропускаем дубликаты
        }
        left, right := i+1, len(nums)-1
        for left < right {
            sum := nums[i] + nums[left] + nums[right]
            switch {
            case sum == 0:
                result = append(result, []int{nums[i], nums[left], nums[right]})
                for left < right && nums[left] == nums[left+1] { left++ }
                for left < right && nums[right] == nums[right-1] { right-- }
                left++
                right--
            case sum < 0:
                left++
            default:
                right--
            }
        }
    }
    return result
}
```

---

## Задача 3: Валидация скобок

**Компания**: Яндекс, Тинькофф, Авито
**Уровень**: Junior / Middle
**Время**: 10-15 минут

### Формулировка

> Напиши функцию `isValid(s string) bool`, которая проверяет, что строка из скобок `()`, `[]`, `{}` корректно вложена.

```
isValid("()")      → true
isValid("()[]{}")  → true
isValid("(]")      → false
isValid("([)]")    → false
isValid("{[]}")    → true
```

### Go решение

```go
// ✅ Классика: стек через слайс
func isValid(s string) bool {
    stack := make([]rune, 0, len(s))

    pairs := map[rune]rune{
        ')': '(',
        ']': '[',
        '}': '{',
    }

    for _, ch := range s {
        switch ch {
        case '(', '[', '{':
            stack = append(stack, ch) // push
        case ')', ']', '}':
            if len(stack) == 0 || stack[len(stack)-1] != pairs[ch] {
                return false
            }
            stack = stack[:len(stack)-1] // pop
        }
    }

    return len(stack) == 0 // стек должен быть пуст
}
```

### Вариация: генерация всех корректных скобочных выражений

```go
// "Generate Parentheses" — рекурсия с backtracking (Яндекс любит)
func generateParenthesis(n int) []string {
    var result []string
    var bt func(s string, open, close int)

    bt = func(s string, open, close int) {
        if len(s) == 2*n {
            result = append(result, s)
            return
        }
        if open < n {
            bt(s+"(", open+1, close)
        }
        if close < open {
            bt(s+")", open, close+1)
        }
    }

    bt("", 0, 0)
    return result
}
// generateParenthesis(3) → ["((()))", "(()())", "(())()", "()(())", "()()()"]
```

---

## Задача 4: Анаграммы

**Компания**: Яндекс, Авито, Озон
**Уровень**: Junior / Middle
**Время**: 10 минут

### Формулировка

> Напиши функцию `isAnagram(s, t string) bool`, которая возвращает true если `t` является анаграммой `s`.
>
> Затем: найди все группы анаграмм в массиве строк.

```
isAnagram("anagram", "nagaram") → true
isAnagram("rat", "car")         → false
```

### Go решение

```go
// ✅ Подсчёт частоты символов
func isAnagram(s, t string) bool {
    if len(s) != len(t) {
        return false
    }

    var freq [26]int // только латиница
    for i := range s {
        freq[s[i]-'a']++
        freq[t[i]-'a']--
    }

    for _, v := range freq {
        if v != 0 {
            return false
        }
    }
    return true
}

// ✅ Unicode версия (для русского языка!)
func isAnagramUnicode(s, t string) bool {
    if len(s) != len(t) {
        return false
    }
    freq := make(map[rune]int)
    for _, ch := range s {
        freq[ch]++
    }
    for _, ch := range t {
        freq[ch]--
        if freq[ch] < 0 {
            return false
        }
    }
    return true
}

// ✅ Группировка анаграмм
func groupAnagrams(strs []string) [][]string {
    groups := make(map[[26]int][]string)

    for _, s := range strs {
        var key [26]int
        for _, ch := range s {
            key[ch-'a']++
        }
        groups[key] = append(groups[key], s)
    }

    result := make([][]string, 0, len(groups))
    for _, group := range groups {
        result = append(result, group)
    }
    return result
}
```

> 💡 На интервью в российской компании уточни: "Работаем только с латиницей или нужна поддержка unicode (русский)?" Это покажет продуманность.

---

## Задача 5: Бинарный поиск

**Компания**: Яндекс, ВКонтакте
**Уровень**: Junior / Middle
**Время**: 10-15 минут

### Формулировка

> Реализуй бинарный поиск в отсортированном массиве. Верни индекс элемента или -1 если не найден.

### Go решение

```go
// ✅ Классический бинарный поиск
func binarySearch(arr []int, target int) int {
    left, right := 0, len(arr)-1

    for left <= right {
        mid := left + (right-left)/2 // избегаем переполнения: НЕ (left+right)/2

        switch {
        case arr[mid] == target:
            return mid
        case arr[mid] < target:
            left = mid + 1
        default:
            right = mid - 1
        }
    }
    return -1
}

// ✅ Или использовать стандартную библиотеку
import "slices"

idx, found := slices.BinarySearch(arr, target)

// ✅ Нижняя граница (first occurrence)
func lowerBound(arr []int, target int) int {
    left, right := 0, len(arr)
    for left < right {
        mid := left + (right-left)/2
        if arr[mid] < target {
            left = mid + 1
        } else {
            right = mid
        }
    }
    return left
}
```

> ⚠️ Классическая ошибка: `(left+right)/2` — может переполниться при большом массиве. Правильно: `left + (right-left)/2`.

### Вариация: поиск в повёрнутом отсортированном массиве

```go
// Сложнее: массив [3,4,5,6,7,0,1,2] (повёрнут на k позиций)
func searchRotated(nums []int, target int) int {
    left, right := 0, len(nums)-1

    for left <= right {
        mid := left + (right-left)/2
        if nums[mid] == target {
            return mid
        }

        // Определяем, какая половина отсортирована
        if nums[left] <= nums[mid] { // левая половина отсортирована
            if nums[left] <= target && target < nums[mid] {
                right = mid - 1
            } else {
                left = mid + 1
            }
        } else { // правая половина отсортирована
            if nums[mid] < target && target <= nums[right] {
                left = mid + 1
            } else {
                right = mid - 1
            }
        }
    }
    return -1
}
```

---

## Задача 6: Merge Sorted Arrays

**Компания**: Яндекс (классика), Тинькофф
**Уровень**: Junior / Middle
**Время**: 15 минут

### Формулировка

> Объедини два отсортированных слайса в один отсортированный слайс.

```
merge([1,3,5], [2,4,6]) → [1,2,3,4,5,6]
```

### Go решение

```go
// ✅ Two pointers — O(n+m) время, O(n+m) память
func mergeSorted(a, b []int) []int {
    result := make([]int, 0, len(a)+len(b))
    i, j := 0, 0

    for i < len(a) && j < len(b) {
        if a[i] <= b[j] {
            result = append(result, a[i])
            i++
        } else {
            result = append(result, b[j])
            j++
        }
    }

    // Добавляем оставшееся (только один из append выполнится)
    result = append(result, a[i:]...)
    result = append(result, b[j:]...)
    return result
}

// ✅ Merge K отсортированных массивов через heap (Яндекс Senior)
import "container/heap"

type Item struct {
    val, arrayIdx, elemIdx int
}

type MinHeap []Item

func (h MinHeap) Len() int            { return len(h) }
func (h MinHeap) Less(i, j int) bool  { return h[i].val < h[j].val }
func (h MinHeap) Swap(i, j int)       { h[i], h[j] = h[j], h[i] }
func (h *MinHeap) Push(x any)         { *h = append(*h, x.(Item)) }
func (h *MinHeap) Pop() any {
    old := *h
    n := len(old)
    x := old[n-1]
    *h = old[:n-1]
    return x
}

func mergeKSorted(arrays [][]int) []int {
    h := &MinHeap{}
    heap.Init(h)

    // Добавляем первые элементы каждого массива
    for i, arr := range arrays {
        if len(arr) > 0 {
            heap.Push(h, Item{arr[0], i, 0})
        }
    }

    var result []int
    for h.Len() > 0 {
        item := heap.Pop(h).(Item)
        result = append(result, item.val)

        // Добавляем следующий элемент из того же массива
        if next := item.elemIdx + 1; next < len(arrays[item.arrayIdx]) {
            heap.Push(h, Item{arrays[item.arrayIdx][next], item.arrayIdx, next})
        }
    }
    return result
}
```

---

## Задача 7: Top K элементов

**Компания**: Яндекс, Авито (аналитика, топ товаров)
**Уровень**: Middle
**Время**: 20 минут

### Формулировка

> Найди K наиболее часто встречающихся элементов в массиве.

```
topK([1,1,1,2,2,3], k=2) → [1, 2]
```

### Go решение

```go
// ✅ Bucket sort — O(n) время!
func topKFrequent(nums []int, k int) []int {
    // Подсчёт частот
    freq := make(map[int]int)
    for _, n := range nums {
        freq[n]++
    }

    // Bucket: индекс = частота, значение = список элементов
    buckets := make([][]int, len(nums)+1)
    for num, count := range freq {
        buckets[count] = append(buckets[count], num)
    }

    // Собираем K наиболее частых
    result := make([]int, 0, k)
    for i := len(buckets) - 1; i >= 0 && len(result) < k; i-- {
        result = append(result, buckets[i]...)
    }
    return result[:k]
}

// ✅ Через heap — O(n log k) — лучше при очень большом n и маленьком k
func topKFrequentHeap(nums []int, k int) []int {
    freq := make(map[int]int)
    for _, n := range nums {
        freq[n]++
    }

    type pair struct{ num, count int }
    h := make([]pair, 0)

    for num, count := range freq {
        h = append(h, pair{num, count})
    }
    // Сортируем по убыванию частоты
    slices.SortFunc(h, func(a, b pair) int {
        return b.count - a.count
    })

    result := make([]int, k)
    for i := range k {
        result[i] = h[i].num
    }
    return result
}
```

---

## Задача 8: Реализация стека и очереди

**Компания**: Wildberries, Авито, Тинькофф
**Уровень**: Junior
**Время**: 10-15 минут

### Формулировка

> Реализуй generic Stack и Queue через слайсы.

### Go решение

```go
// ✅ Generic Stack (LIFO)
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
    n := len(s.items) - 1
    v := s.items[n]
    s.items = s.items[:n]
    return v, true
}

func (s *Stack[T]) Peek() (T, bool) {
    if len(s.items) == 0 {
        var zero T
        return zero, false
    }
    return s.items[len(s.items)-1], true
}

func (s *Stack[T]) Len() int { return len(s.items) }

// ✅ Generic Queue (FIFO)
type Queue[T any] struct {
    items []T
}

func (q *Queue[T]) Enqueue(v T) {
    q.items = append(q.items, v)
}

func (q *Queue[T]) Dequeue() (T, bool) {
    if len(q.items) == 0 {
        var zero T
        return zero, false
    }
    v := q.items[0]
    q.items = q.items[1:] // ⚠️ утечка памяти при большом объёме!
    return v, true
}

func (q *Queue[T]) Len() int { return len(q.items) }
```

> ⚠️ Наивная Queue с `items[1:]` утекает память — backing array не уменьшается. Для production используй `container/ring` или два стека.

```go
// ✅ Queue через два стека — O(1) амортизированно
type EfficientQueue[T any] struct {
    in  []T // для добавления
    out []T // для извлечения
}

func (q *EfficientQueue[T]) Enqueue(v T) {
    q.in = append(q.in, v)
}

func (q *EfficientQueue[T]) Dequeue() (T, bool) {
    if len(q.out) == 0 {
        // Переворачиваем in → out
        for len(q.in) > 0 {
            n := len(q.in) - 1
            q.out = append(q.out, q.in[n])
            q.in = q.in[:n]
        }
    }
    if len(q.out) == 0 {
        var zero T
        return zero, false
    }
    n := len(q.out) - 1
    v := q.out[n]
    q.out = q.out[:n]
    return v, true
}
```

---

## Шпаргалка: сложность задач

| Задача | Время | Память | Ключевая идея |
|--------|-------|--------|---------------|
| LRU Cache | O(1) | O(n) | HashMap + DoublyLinkedList |
| Two Sum | O(n) | O(n) | Map комплементов |
| Valid Parentheses | O(n) | O(n) | Stack |
| Anagram | O(n) | O(1) | Массив частот [26] |
| Binary Search | O(log n) | O(1) | left + (right-left)/2 |
| Merge Sorted | O(n+m) | O(n+m) | Two pointers |
| Top K Frequent | O(n) | O(n) | Bucket sort |
| Stack/Queue | O(1) | O(n) | Slice + два стека |

---
