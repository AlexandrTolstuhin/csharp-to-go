# Часть 2: Продвинутые темы

## Описание

Глубокое погружение в concurrency, runtime, GC и производительность Go. Эта часть критически важна для понимания отличий от C# async/await.

<!-- AUTO: MATERIALS -->
## Материалы

### 1. [2.1 Горутины и каналы](./01_goroutines_channels.md)

- Введение
- Горутины vs C# Task/Thread
- Каналы: основы
- Буферизированные каналы
- Select statement
- Context и cancellation
- Паттерны конкурентности
- Утечки горутин
- Практические примеры

### 2. [2.2 Go Runtime и планировщик](./02_runtime_scheduler.md)

- Введение
- Архитектура GMP
- Work-Stealing алгоритм
- Preemption (вытеснение)
- GOMAXPROCS
- Сравнение с .NET ThreadPool
- Трассировка и диагностика
- Оптимизация под планировщик
- Практические примеры

### 3. [2.2a Аллокатор памяти Go (Memory Allocator Internals)](./02a_memory_allocator.md)

- Введение
- 1. Virtual Memory vs Physical Memory
- 2. Страницы памяти (Memory Pages)
- 3. Архитектура аллокатора Go
- 4. mheap: Глобальная куча
- 5. mspan: Единица управления памятью
- 6. mcentral: Центральный кеш
- 7. mcache: Per-P кеш
- 8. Size Classes
- 9. Путь аллокации: от new() до памяти
- 10. Диагностика и мониторинг
- Практические примеры

### 4. [2.3 Сборка мусора (GC)](./03_gc.md)

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

### 5. [2.4 Примитивы синхронизации](./04_sync_primitives.md)

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

### 6. [2.5 Обработка ошибок (продвинутый уровень)](./05_error_handling.md)

- Введение
- Sentinel Errors vs Typed Errors
- Custom Error Types с метаданными
- Panic/Recover: когда и как использовать
- Error Wrapping Chains
- Стратегии обработки ошибок по слоям
- Логирование ошибок
- Идиоматичные паттерны для production
- Практические примеры

### 7. [2.6 Тестирование и бенчмаркинг](./06_testing_benchmarking.md)

- Введение
- 1. testing package: основы
- 2. Table-Driven Tests (идиоматичный Go)
- 3. Subtests (t.Run)
- 4. Мокирование и тестирование зависимостей
- 5. Benchmarks: производительность
- 6. Fuzzing (Go 1.18+)
- 7. Integration Tests
- 8. Race Detector
- 9. Coverage (покрытие кода)
- 10. Идиоматичные паттерны тестирования
- 11. Тестирование конкурентного кода
- 12. Новые возможности тестирования (Go 1.24-1.25)
- Практические примеры

### 8. [2.7 Профилирование и оптимизация](./07_profiling_optimization.md)

- Введение
- 1. pprof: CPU профилирование
- 2. go tool trace: расширенный анализ
- 3. Комплексный workflow профилирования
- 4. Оптимизация production-кода
- 5. Continuous Profiling
- 5. Новые инструменты профилирования (Go 1.25-1.26)
- Практические примеры
<!-- /AUTO: MATERIALS -->

---

<!-- AUTO: NAV -->
[← Назад к оглавлению](../README.md) | [Предыдущая часть: Часть 1: Основы Go](../part1-basics/) | [Следующая часть: Часть 3: Web & API →](../part3-web-api/)
<!-- /AUTO: NAV -->
