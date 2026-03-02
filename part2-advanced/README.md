# Часть 2: Продвинутые темы

## Описание

Глубокое погружение в concurrency, runtime, GC и производительность Go. Эта часть критически важна для понимания отличий от C# async/await.

<!-- AUTO: MATERIALS -->
## Материалы

### 1. [Горутины и каналы](./01_goroutines_channels.md)

- Введение
- Горутины vs C# Task/Thread
- Каналы: основы
- Буферизированные каналы
- Select statement
- Context и cancellation
- Паттерны конкурентности
- Утечки горутин
- Практические примеры

### 2. [Go Runtime и планировщик](./02_runtime_scheduler.md)

- Введение
- Архитектура GMP
- Work-Stealing алгоритм
- Preemption (вытеснение)
- GOMAXPROCS
- Сравнение с .NET ThreadPool
- Трассировка и диагностика
- Оптимизация под планировщик
- Практические примеры

### 3. [Аллокатор памяти Go (Memory Allocator Internals)](./02a_memory_allocator.md)

- Введение
- Virtual Memory vs Physical Memory
- Страницы памяти (Memory Pages)
- Архитектура аллокатора Go
- mheap: Глобальная куча
- mspan: Единица управления памятью
- mcentral: Центральный кеш
- mcache: Per-P кеш
- Size Classes
- Путь аллокации: от new() до памяти
- Диагностика и мониторинг
- Практические примеры

### 4. [Сборка мусора (GC)](./03_gc.md)

- Введение
- Архитектура GC в Go vs .NET
- Tri-Color Mark-and-Sweep алгоритм
- Write Barriers и concurrent GC
- GOGC и GOMEMLIMIT
- Escape Analysis: Stack vs Heap
- Профилирование и диагностика
- Оптимизация под GC
- sync.Pool и переиспользование объектов
- Практические примеры

### 5. [Примитивы синхронизации](./04_sync_primitives.md)

- Введение
- Mutex: взаимное исключение
- WaitGroup: ожидание завершения горутин
- Once: однократное выполнение
- Cond: условные переменные
- Atomic операции
- sync.Map: потокобезопасная карта
- Выбор правильного примитива
- Практические примеры
- golang.org/x/sync: расширенные примитивы

### 6. [Обработка ошибок (продвинутый уровень)](./05_error_handling.md)

- Введение
- Sentinel Errors vs Typed Errors
- Custom Error Types с метаданными
- Panic/Recover: когда и как использовать
- Error Wrapping Chains
- Стратегии обработки ошибок по слоям
- Логирование ошибок
- Идиоматичные паттерны для production
- Практические примеры

### 7. [Тестирование и бенчмаркинг](./06_testing_benchmarking.md)

- Введение
- testing package: основы
- Table-Driven Tests (идиоматичный Go)
- Subtests (t.Run)
- Мокирование и тестирование зависимостей
- Benchmarks: производительность
- Fuzzing (Go 1.18+)
- Integration Tests
- Race Detector
- Coverage (покрытие кода)
- Идиоматичные паттерны тестирования
- Тестирование конкурентного кода
- Новые возможности тестирования (Go 1.24-1.25)
- Практические примеры

### 8. [Профилирование и оптимизация](./07_profiling_optimization.md)

- Введение
- pprof: CPU профилирование
- go tool trace: расширенный анализ
- Комплексный workflow профилирования
- Оптимизация production-кода
- Continuous Profiling
- Новые инструменты профилирования (Go 1.25-1.26)
- Практические примеры
<!-- /AUTO: MATERIALS -->

---

<!-- AUTO: NAV -->
[← Назад к оглавлению](../README.md) | [Предыдущая часть: Часть 1: Основы Go (Быстрый старт)](../part1-basics/) | [Следующая часть: Часть 3: Web API разработка →](../part3-web-api/)
<!-- /AUTO: NAV -->
