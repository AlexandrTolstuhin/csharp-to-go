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

## Задача 0: Упразднение раздела 6.2 и распределение контента

### Проблема

`part6-best-practices/02_modern_go.md` является сборником "современных возможностей" Go 1.18-1.23,
но эти темы уже частично раскрыты в соответствующих разделах курса или должны быть там.
Держать их отдельно создаёт дублирование и разрывает тематический контекст.

### Карта распределения контента

| Блок из 6.2 | Куда переносится |
|---|---|
| **Generics (1.18+)**: constraints, type params, generic functions/types, когда использовать, performance | `part1-basics/03_key_differences.md` — в раздел про систему типов |
| **slices/maps/cmp пакеты (1.21+)** | `part1-basics/02_syntax_basics.md` — в раздел про коллекции |
| **log/slog (1.21)** | `part4-infrastructure/05_observability.md` — в раздел структурированного логирования |
| **net/http улучшения (1.22+)**: метод-маршруты, PathValue, wildcards | `part3-web-api/01_http_server.md` — в раздел роутинга |
| **Range over integers (1.22)** | `part1-basics/02_syntax_basics.md` — в раздел про циклы |
| **clear(), min/max, cmp.Or (1.21-1.22)** | `part1-basics/02_syntax_basics.md` — в раздел встроенных функций |
| **Iterators (1.23)** | `part1-basics/02_syntax_basics.md` — в раздел про range |
| **Практические примеры** (Generic Repository, REST API) | Удаляются: Generic Repository частично войдёт в generics-блок в 1.3, REST API уже есть в части 3 |

### Что удаляется
- Файл `part6-best-practices/02_modern_go.md` — удалить полностью после переноса контента.

### Что меняется в структуре part6
После удаления 02_modern_go.md файлы часть 6 перенумеровываются:

| Было | Станет |
|---|---|
| `02_modern_go.md` | удалён |
| `03_tools.md` | `02_tools.md` |
| `04_performance.md` | `03_performance.md` |
| `05_production_checklist.md` | `04_production_checklist.md` |

### Что нужно обновить после удаления

- `part6-best-practices/README.md` — убрать раздел 6.2, обновить нумерацию и ссылки
- Нижняя навигация в `part6-best-practices/01_code_architecture.md` — ссылка "вперёд" меняется на `02_tools.md`
- Нижняя навигация в `02_tools.md` (бывший 03) — ссылка "назад" меняется на `01_code_architecture.md`
- Нижняя навигация в `03_performance.md` (бывший 04) — ссылка "назад" меняется на `02_tools.md`
- Нижняя навигация в `04_production_checklist.md` (бывший 05) — ссылка "назад" меняется на `03_performance.md`
- Корневой `README.md` — обновить ссылки на файлы части 6

### Примечание по контенту 1.24-1.26

Запланированный новый контент из Go 1.24-1.26, который планировался для `02_modern_go.md`,
теперь распределяется так:
- Итераторы `strings.Lines`, `strings.SplitSeq` (1.24) → `part1-basics/02_syntax_basics.md`
- `weak.Pointer[T]` (1.24) → `part2-advanced/03_gc.md` (тема управления памятью и GC)
- Self-referential generics (1.26) → `part1-basics/03_key_differences.md` (раздел generics)

---

## Файлы для обновления

### Обязательные (высокий приоритет)

| Файл | Что добавить |
|------|-------------|
| `README.md` | Badge: `1.23+` → `1.26+`; обновить ссылки части 6 |
| `part2-advanced/04_sync_primitives.md` | `sync.Map` redesign (1.24), `WaitGroup.Go()` (1.25) |
| `part2-advanced/03_gc.md` | Green Tea GC: 1.25 эксперимент → 1.26 default, Swiss Tables map (1.24), `weak.Pointer` (1.24) |
| `part2-advanced/06_testing_benchmarking.md` | `T.Context()`, `B.Loop()` (1.24), `testing/synctest` stable (1.25) |
| `part4-infrastructure/07_containerization.md` | Container-aware GOMAXPROCS (1.25) |
| `part1-basics/02_syntax_basics.md` | Контент из 6.2: slices/maps/cmp, range-over-int, clear/min/max, iterators; + generic type aliases (1.24), strings.Lines/SplitSeq (1.24) |
| `part1-basics/03_key_differences.md` | Контент из 6.2: generics; + self-referential generics (1.26) |
| `part3-web-api/01_http_server.md` | Контент из 6.2: net/http 1.22 routing |
| `part4-infrastructure/05_observability.md` | Контент из 6.2: log/slog |
| `part6-best-practices/README.md` | Удалить п.6.2, обновить нумерацию и ссылки |

### Средний приоритет

| Файл | Что сделать |
|------|-------------|
| `part6-best-practices/02_modern_go.md` | Удалить файл после переноса контента |
| `part6-best-practices/03_tools.md` → `02_tools.md` | Переименовать, обновить навигацию, добавить `go fix` modernizers (1.26) |
| `part6-best-practices/04_performance.md` → `03_performance.md` | Переименовать, обновить навигацию |
| `part6-best-practices/05_production_checklist.md` → `04_production_checklist.md` | Переименовать, обновить навигацию |
| `part6-best-practices/01_code_architecture.md` | Обновить навигацию: ссылка "вперёд" → `02_tools.md` |
| `part2-advanced/07_profiling_optimization.md` | `FlightRecorder` (1.25), goroutine leak detection (1.26), новые scheduler metrics (1.26) |
| `part3-web-api/04_validation_serialization.md` | JSON v2 (1.25 experimental), `io.ReadAll` 2x (1.26) |

### Низкий приоритет (упомянуть вскользь)

| Файл | Что добавить |
|------|-------------|
| `part6-best-practices/02_tools.md` | `go fix` modernizers (1.26) |
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

### 6. `part1-basics/02_syntax_basics.md` (основной приёмник контента из 6.2)
Перенести из `02_modern_go.md`:
- Раздел про `slices`/`maps`/`cmp` пакеты (Go 1.21+) — добавить в секцию коллекций
- Range over integers (`for i := range 10`) — добавить в секцию циклов
- `clear()`, `min/max`, `cmp.Or` — добавить в секцию встроенных функций
- Iterators (Go 1.23) — добавить после range-over-integers

Добавить новый контент (Go 1.24):
- Generic type aliases: `type MyMap[K comparable, V any] = map[K]V`
- Итераторы `strings.Lines`, `strings.SplitSeq`, `bytes.Lines`, `bytes.SplitSeq` — аналог LINQ lazy evaluation

### 6а. `part1-basics/03_key_differences.md`
Перенести из `02_modern_go.md`:
- Весь блок Generics (Go 1.18+): философия, синтаксис C# vs Go, type constraints,
  generic functions/types, когда использовать, performance/GC

Добавить новый контент (Go 1.26):
```go
// Self-referential generics — теперь работает (раньше — ошибка компиляции)
type Adder[A Adder[A]] interface {
    Add(A) A
}
```
Сравнение с C# рекурсивными generic constraints (`where T : IComparable<T>`).

### 6б. `part3-web-api/01_http_server.md`
Перенести из `02_modern_go.md`:
- Улучшения net/http (Go 1.22+): метод-маршруты `GET /path`, `PathValue()`, wildcards
- Сравнение с ASP.NET Core, миграция с chi/gorilla
(Проверить, что не дублирует уже существующий контент в этом файле — по TOC файл уже
должен покрывать ServeMux 1.22, при дубле — объединить, не добавлять второй раз)

### 6в. `part4-infrastructure/05_observability.md`
Перенести из `02_modern_go.md`:
- Раздел log/slog: обзор API, Handler интерфейс, миграция с других логгеров
(Аналогично — проверить на дублирование с существующим контентом про slog в файле)

### 6г. Удаление `part6-best-practices/02_modern_go.md`
После переноса всего контента:
- Удалить файл
- Переименовать оставшиеся файлы part6 (03→02, 04→03, 05→04)
- Обновить навигацию во всех файлах части 6
- Обновить `part6-best-practices/README.md`
- Обновить корневой `README.md` (ссылки на файлы части 6)

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

Рекомендуемая последовательность. Сначала — распределение контента 6.2, затем — актуализация под 1.26.

**Фаза 1: Распределение контента 6.2 по разделам**

1. Прочитать `02_modern_go.md` целиком, зафиксировать все блоки
2. `part1-basics/02_syntax_basics.md` — перенести slices/maps/cmp, range-over-int, clear/min/max, iterators (60 мин)
3. `part1-basics/03_key_differences.md` — перенести generics-блок (45 мин)
4. `part3-web-api/01_http_server.md` — перенести net/http 1.22 (проверить дубли, 20 мин)
5. `part4-infrastructure/05_observability.md` — перенести log/slog (проверить дубли, 15 мин)
6. Удалить `part6-best-practices/02_modern_go.md`
7. Переименовать файлы part6: 03→02, 04→03, 05→04
8. Обновить навигацию во всех файлах part6 (01, 02, 03, 04) + `part6/README.md`
9. Обновить корневой `README.md` (ссылки части 6)

**Фаза 2: Актуализация Go 1.24-1.26**

10. `README.md` — badge `1.26+` (5 мин)
11. `part2-advanced/04_sync_primitives.md` — WaitGroup.Go() + sync.Map (30 мин)
12. `part2-advanced/03_gc.md` — Green Tea GC default + weak.Pointer (25 мин)
13. `part2-advanced/06_testing_benchmarking.md` — T.Context(), B.Loop(), synctest (40 мин)
14. `part4-infrastructure/07_containerization.md` — GOMAXPROCS (20 мин)
15. `part1-basics/02_syntax_basics.md` — generic type aliases, strings.Lines/SplitSeq (20 мин)
16. `part1-basics/03_key_differences.md` — self-referential generics (15 мин)
17. `part2-advanced/07_profiling_optimization.md` — FlightRecorder, leak detection (25 мин)
18. `part3-web-api/04_validation_serialization.md` — JSON v2, io.ReadAll (15 мин)
19. `part6-best-practices/02_tools.md` — go fix modernizers (10 мин)
20. `part1-basics/01_setup_environment.md` — версия установки (5 мин)
21. `.context-summary.md` — финальное обновление (10 мин)

**Итого**: ~5.5 часов чистой работы (Фаза 1 ~2 ч + Фаза 2 ~3.5 ч).

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

**Распределение 6.2:**
- [ ] Файл `02_modern_go.md` удалён
- [ ] Контент generics есть в `03_key_differences.md`, не дублируется
- [ ] Контент slices/maps/range/iterators есть в `02_syntax_basics.md`, не дублируется
- [ ] net/http 1.22 есть в `01_http_server.md`, не дублируется
- [ ] log/slog есть в `05_observability.md`, не дублируется
- [ ] Файлы part6 переименованы (нет пробелов в нумерации)
- [ ] Все ссылки навигации в part6 ведут на правильные файлы
- [ ] Корневой README.md не ссылается на удалённый `02_modern_go.md`

**Актуализация 1.26:**
- [ ] Badge в README.md показывает 1.26+
- [ ] WaitGroup.Go() помечен как Go 1.25, не 1.24
- [ ] Секция GOMAXPROCS не вводит в заблуждение: automaxprocs ещё актуален для Go < 1.25
- [ ] Green Tea GC: эксперимент в 1.25 vs default в 1.26 — чётко разделены
- [ ] testing/synctest: experimental в 1.24, stable в 1.25 — чётко указано
- [ ] weak.Pointer размещён в GC-разделе, не в syntax-разделе
- [ ] Создан коммит по завершении каждого файла (согласно CLAUDE.md)
- [ ] Push на GitHub в конце сессии
