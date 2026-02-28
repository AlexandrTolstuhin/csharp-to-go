# План актуализации курса: Go 1.23 → Go 1.26

## Контекст

Курс "Переход с C# на Go" создан под Go 1.23+. Вышли версии Go 1.24, 1.25 и 1.26 с рядом
значимых изменений — новые API, улучшения GC, переработка стандартной библиотеки. Часть
изменений напрямую затрагивает темы, которые уже подробно описаны в курсе (синхронизация,
GC, тестирование, контейнеры). Цель — обновить существующие файлы без создания новых разделов,
обновить badge версии и context-summary.

---

## Ключевые изменения по версиям

### Go 1.24
- Generic type aliases (параметризованные псевдонимы типов)
- `strings.Lines()`, `strings.SplitSeq()`, `bytes.Lines()`, `bytes.SplitSeq()` — ленивые итераторы
- `sync.Map` — полностью переработан для высококонкурентных нагрузок (Swiss Tables)
- `runtime.AddCleanup()` — заменяет `SetFinalizer`, поддерживает несколько финализаторов на объект
- Новый пакет `weak` — слабые ссылки
- `testing.T.Context()` / `testing.B.Context()` — контекст, отменяемый по завершении теста
- `testing.B.Loop()` — новый идиоматичный способ написания бенчмарков
- `testing/synctest` (экспериментальный) — детерминированное тестирование конкурентного кода
- Алгоритм Swiss Tables для встроенных map — снижение CPU overhead на 2-3%

### Go 1.25
- `sync.WaitGroup.Go(func())` — новый метод, заменяет паттерн Add(1)+defer Done
- `testing/synctest` — переведён в stable
- JSON v2 как эксперимент (`GOEXPERIMENT=jsonv2`): `encoding/json/v2`, значительно быстрее decode
- `runtime/trace.FlightRecorder` — кольцевой буфер трассировки в памяти для редких событий
- Container-aware GOMAXPROCS — автоматически читает cgroup CPU limits (Kubernetes-critical)
- Green Tea GC (эксперимент, `GOEXPERIMENT=greenteagc`) — снижение GC overhead на 10-40%
- DWARF5 — уменьшение размера отладочной информации, ускорение линковки

### Go 1.26
- Self-referential generic types — тип может ссылаться на себя в constraint
- Enhanced `new()` — принимает выражение с начальным значением
- Green Tea GC — теперь включён по умолчанию (10-40% + ещё 10% на Ice Lake/Zen 4+)
- Post-quantum TLS по умолчанию (`SecP256r1MLKEM768`, `SecP384r1MLKEM1024`)
- `crypto/hpke` — Hybrid Public Key Encryption (RFC 9180)
- `io.ReadAll` — ~2x быстрее, ~50% меньше аллокаций
- `bytes.Buffer.Peek()` — неразрушающее чтение
- cgo — снижение базового overhead вызовов на ~30%
- Goroutine leak detection (экспериментальный) — находит заблокированные недостижимые горутины
- Новые runtime/metrics: состояния горутин, OS thread count, total goroutines created
- `go fix` переписан — поддерживает "modernizers" на базе go/analysis
- reflect: итераторные методы `Type.Fields()`, `Type.Methods()`, `Value.Fields()`

---

## Файлы для обновления

### Обязательные (высокий приоритет)

| Файл | Что добавить |
|------|-------------|
| `README.md` | Badge: `1.23+` → `1.26+` |
| `part2-advanced/04_sync_primitives.md` | `sync.Map` redesign (1.24), `WaitGroup.Go()` (1.25) |
| `part2-advanced/03_gc.md` | Green Tea GC: 1.25 эксперимент → 1.26 default, Swiss Tables map (1.24) |
| `part2-advanced/06_testing_benchmarking.md` | `T.Context()`, `B.Loop()` (1.24), `testing/synctest` stable (1.25) |
| `part4-infrastructure/07_containerization.md` | Container-aware GOMAXPROCS (1.25) |

### Средний приоритет

| Файл | Что добавить |
|------|-------------|
| `part6-best-practices/02_modern_go.md` | Итераторы strings/bytes (1.24), self-referential generics (1.26), `weak` package (1.24) |
| `part2-advanced/07_profiling_optimization.md` | `FlightRecorder` (1.25), goroutine leak detection (1.26), новые scheduler metrics (1.26) |
| `part3-web-api/04_validation_serialization.md` | JSON v2 (1.25 experimental), `io.ReadAll` 2x (1.26) |
| `part1-basics/02_syntax_basics.md` | Generic type aliases (1.24) |

### Низкий приоритет (упомянуть вскользь)

| Файл | Что добавить |
|------|-------------|
| `part6-best-practices/03_tools.md` | `go fix` modernizers (1.26) |
| `part2-advanced/02_runtime_scheduler.md` | Новые scheduler metrics (1.26) |
| `part1-basics/01_setup_environment.md` | Версия установки: Go 1.26 |

---

## Детальный план по файлам

### 1. `README.md`
- Поменять badge: `Go-1.23+-00ADD8` → `Go-1.26+-00ADD8`
- В секции "Что нового" или footnote добавить строку об актуализации до 1.26

### 2. `part2-advanced/04_sync_primitives.md`
Раздел про `sync.Map`:
- Описать переработку в 1.24: Swiss Tables, без "прогрева" при низкой конкуренции, сниженная
  конкуренция для непересекающихся ключей
- Обновить benchmark-примеры (если есть) или добавить примечание с цифрами

Новый подраздел `WaitGroup.Go()` (Go 1.25):
```go
// ДО (Go 1.23)
var wg sync.WaitGroup
wg.Add(1)
go func() {
    defer wg.Done()
    doWork()
}()

// ПОСЛЕ (Go 1.25)
var wg sync.WaitGroup
wg.Go(func() {
    doWork()
})
```
Сравнение с C# `Task.WhenAll` + список задач.

### 3. `part2-advanced/03_gc.md`
Обновить раздел про Green Tea GC:
- В 1.25 появился как `GOEXPERIMENT=greenteagc`
- В 1.26 включён по умолчанию
- Цифры: 10-40% снижение GC overhead для малых объектов
- На Ice Lake / AMD Zen 4+ дополнительно ещё ~10% за счёт SIMD

Добавить упоминание Swiss Tables для встроенных map:
- Алгоритм с Go 1.24, снижение CPU overhead на 2-3% глобально

### 4. `part2-advanced/06_testing_benchmarking.md`
Три блока обновлений:

**`testing.T.Context()` (Go 1.24)**:
```go
func TestFoo(t *testing.T) {
    ctx := t.Context() // отменяется автоматически по завершении теста
    result, err := callWithContext(ctx)
    ...
}
```
Аналог: C# `CancellationToken` через `TestContext` в NUnit/xUnit.

**`testing.B.Loop()` (Go 1.24)**:
```go
// ДО
func BenchmarkFoo(b *testing.B) {
    for i := 0; i < b.N; i++ {
        doWork()
    }
}

// ПОСЛЕ (Go 1.24) — компилятор не оптимизирует тело
func BenchmarkFoo(b *testing.B) {
    for b.Loop() {
        doWork()
    }
}
```

**`testing/synctest` (experimental 1.24 → stable 1.25)**:
- Детерминированное тестирование горутин с виртуальными часами
- `synctest.Test()` + `synctest.Wait()` — изолированная "пузырь"-среда
- Аналог: `FakeTimeProvider` в тестах ASP.NET

### 5. `part4-infrastructure/07_containerization.md`
Раздел про GOMAXPROCS в Kubernetes:
- До Go 1.25 GOMAXPROCS игнорировал cgroup CPU limits → в K8s pod с `limits.cpu: 2`
  процесс использовал все ядра хоста
- С Go 1.25 — автоматически читает cgroup limits и обновляет при изменении
- Обновить секцию про `GOMAXPROCS` и убрать/отметить устаревшим рецепт с `uber-go/automaxprocs`
  (теперь встроено в runtime)

### 6. `part6-best-practices/02_modern_go.md`
**Lazy string/bytes iterators (Go 1.24)**:
```go
// Ленивый перебор строк — аналог C# LINQ lazy evaluation
for line := range strings.Lines(text) {
    process(line)
}

// vs старый подход
for _, line := range strings.Split(text, "\n") { ... }
```
Таблица новых итераторных функций: `Lines`, `SplitSeq`, `FieldsSeq`, `FieldsFuncSeq`.

**Self-referential generics (Go 1.26)**:
```go
// Теперь работает (раньше — ошибка компиляции)
type Adder[A Adder[A]] interface {
    Add(A) A
}
```
Сравнение с C# рекурсивными generic constraints (`where T : IComparable<T>`).

**Пакет `weak` (Go 1.24)**:
- Кратко: слабые ссылки через `weak.Pointer[T]`
- Аналог: `WeakReference<T>` в C#

### 7. `part2-advanced/07_profiling_optimization.md`
**`runtime/trace.FlightRecorder` (Go 1.25)**:
```go
fr := trace.NewFlightRecorder()
fr.Start()
// ... в обработчике сигнала или при обнаружении аномалии:
var buf bytes.Buffer
fr.WriteTo(&buf)
```
Аналог: Event Tracing for Windows (ETW) ring buffer в .NET.

**Goroutine leak detection (Go 1.26, experimental)**:
- Детектирует заблокированные горутины без внешних ссылок
- Как включить, что сообщает

**Новые scheduler metrics (Go 1.26)**:
- Добавить в таблицу `runtime/metrics`: `goroutine states`, `os thread count`,
  `total goroutines created`

### 8. `part3-web-api/04_validation_serialization.md`
**JSON v2 (Go 1.25 experimental)**:
- Доступен через `encoding/json/v2` при `GOEXPERIMENT=jsonv2`
- Значительно быстрее decode, encoding на уровне v1
- Предупреждение: ещё экспериментальный, не для продакшна без тестирования

**`io.ReadAll` (Go 1.26)**:
- ~2x быстрее, ~50% меньше аллокаций — без изменений в коде

### 9. `part1-basics/02_syntax_basics.md`
Подраздел про generic type aliases (Go 1.24):
```go
// Теперь можно
type MyMap[K comparable, V any] = map[K]V

// Аналог C#
// using MyDict<K, V> = Dictionary<K, V>; (C# 12 global using aliases)
```

### 10. `part1-basics/01_setup_environment.md`
- Обновить версию в инструкциях установки: `go1.23.x` → `go1.26.x`
- Обновить ссылку на загрузку

### 11. `part6-best-practices/03_tools.md`
**`go fix` modernizers (Go 1.26)**:
- `go fix` теперь поддерживает автоматические миграции кода через go/analysis
- Встроенные modernizers: автоматическое применение новых идиом
- Директива `//go:fix inline` для source-level inlining

### 12. `.context-summary.md`
- Обновить раздел "Целевая версия Go": `1.23+` → `1.26+`
- Добавить запись об актуализации в историю изменений

---

## Порядок выполнения

Рекомендуемая последовательность (по убыванию impact/сложности):

1. `README.md` — badge (5 мин)
2. `04_sync_primitives.md` — WaitGroup.Go() + sync.Map (30 мин)
3. `03_gc.md` — Green Tea GC default (20 мин)
4. `06_testing_benchmarking.md` — T.Context(), B.Loop(), synctest (40 мин)
5. `07_containerization.md` — GOMAXPROCS (20 мин)
6. `02_modern_go.md` — итераторы, self-referential generics, weak (30 мин)
7. `07_profiling_optimization.md` — FlightRecorder, leak detection (25 мин)
8. `04_validation_serialization.md` — JSON v2, io.ReadAll (15 мин)
9. `02_syntax_basics.md` — generic type aliases (15 мин)
10. `01_setup_environment.md` — версия установки (5 мин)
11. `03_tools.md` — go fix (10 мин)
12. `.context-summary.md` — финальное обновление (10 мин)

**Итого**: ~3.5 часа чистой работы по написанию.

---

## Что НЕ включать

- Криптографические пакеты (`crypto/hpke`, `crypto/mlkem`) — вне scope курса для C# разработчиков
- SIMD эксперимент (`GOEXPERIMENT=simd`) — слишком low-level, нестабильно
- DWARF5 — детали линковки не нужны курсу
- `runtime/secret` эксперимент — узкоспециализировано
- cgo improvements — cgo не входит в курс
- S390X, RISC-V изменения — платформо-специфично

---

## Проверка после обновления

- [ ] Badge в README.md показывает 1.26+
- [ ] Все примеры кода скомпилированы мысленно (или проверены в go playground) для Go 1.26
- [ ] WaitGroup.Go() пример корректен (метод добавлен именно в 1.25, не 1.24)
- [ ] Секция GOMAXPROCS не вводит в заблуждение: automaxprocs всё ещё может быть полезен для Go < 1.25
- [ ] Green Tea GC: чётко разделены — эксперимент в 1.25 vs default в 1.26
- [ ] testing/synctest: чётко указано — experimental в 1.24, stable в 1.25
- [ ] Создан коммит по завершении каждого файла (согласно CLAUDE.md)
- [ ] Push на GitHub в конце сессии
