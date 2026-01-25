# Часть 2: Продвинутые темы

## Описание

Глубокое погружение в concurrency, runtime, GC и производительность Go. Эта часть критически важна для понимания отличий от C# async/await.

## Статус

✅ **Завершено** - 100% (7 из 7 разделов)

## Материалы

### ✅ Завершено

1. **[01_goroutines_channels.md](./01_goroutines_channels.md)** — Горутины и каналы
   - Goroutines vs C# Task/Thread
   - Каналы vs C# Channel<T>
   - Буферизированные и небуферизированные каналы
   - Select statement
   - Context и cancellation (vs CancellationToken)
   - Паттерны: Worker Pool, Fan-Out/Fan-In, Pipeline, Semaphore
   - errgroup для обработки ошибок
   - Утечки горутин и их предотвращение
   - 3 практических примера

2. **[02_runtime_scheduler.md](./02_runtime_scheduler.md)** — Go Runtime и планировщик
   - Архитектура GMP (Goroutine, Machine, Processor)
   - Work-stealing алгоритм
   - Cooperative vs Signal-based preemption
   - GOMAXPROCS и его влияние
   - Сравнение с .NET ThreadPool
   - Трассировка: go tool trace, GODEBUG=schedtrace
   - Оптимизация под планировщик
   - 3 практических примера

3. **[03_gc.md](./03_gc.md)** — Сборка мусора (GC)
   - Архитектура Go GC vs .NET GC (concurrent vs generational)
   - Tri-color mark-and-sweep алгоритм
   - Write barriers и concurrent GC
   - GOGC и GOMEMLIMIT — настройка памяти
   - Escape Analysis: Stack vs Heap
   - Профилирование: pprof, GODEBUG=gctrace, runtime.MemStats
   - Оптимизация под GC (избегание аллокаций)
   - sync.Pool для переиспользования объектов
   - 3 практических примера

4. **[04_sync_primitives.md](./04_sync_primitives.md)** — Примитивы синхронизации
   - Mutex vs C# lock (defer для разблокировки)
   - RWMutex vs ReaderWriterLockSlim
   - Deadlock и как его избежать
   - WaitGroup vs Task.WhenAll (с errgroup)
   - Once vs Lazy<T> (singleton инициализация)
   - Cond vs Monitor.Wait/Pulse (предпочтение каналам)
   - Atomic операции: atomic.Int64, atomic.Value
   - sync.Map vs ConcurrentDictionary (write-once сценарии)
   - Выбор правильного примитива (блок-схема)
   - **golang.org/x/sync**: errgroup, semaphore, singleflight
   - 3 практических примера: Rate Limiter, метрики, Connection Pool

5. **[05_error_handling.md](./05_error_handling.md)** — Обработка ошибок (продвинутый уровень)
   - Sentinel errors vs Typed errors (когда что использовать)
   - Custom error types с метаданными (коды, HTTP маппинг)
   - Fluent API для построения ошибок
   - Panic/recover: правила безопасного использования
   - Error wrapping chains (построение контекста)
   - Стратегии по слоям: Repository/Service/Handler
   - Логирование: где и как (structured logging с slog)
   - Expected vs Unexpected errors
   - Production паттерны: retry, MultiError, context cancellation
   - 4 практических примера: REST API, Background Job, gRPC, tracing

6. **[06_testing_benchmarking.md](./06_testing_benchmarking.md)** — Тестирование и бенчмаркинг
   - testing package: func TestXxx(t *testing.T) vs xUnit/NUnit
   - Table-driven tests (идиоматичный Go паттерн)
   - Subtests: t.Run() и t.Parallel()
   - Мокирование: ручные моки, gomock, testify
   - Benchmarks: func BenchmarkXxx(b *testing.B) vs BenchmarkDotNet
   - Fuzzing (Go 1.18+): автогенерация входных данных
   - Integration tests: httptest, testcontainers
   - Race detector: go test -race
   - Coverage: go test -cover
   - Идиоматичные паттерны: t.Helper(), golden files, build tags
   - 2 практических примера: UserService, Rate Limiter

7. **[07_profiling_optimization.md](./07_profiling_optimization.md)** — Профилирование и оптимизация
   - pprof: CPU профилирование (sampling, анализ, flame graphs)
   - go tool trace: расширенный анализ (latency spikes, goroutine analysis)
   - Комплексный workflow: Measure → Identify → Optimize → Verify
   - Оптимизация production-кода (строки, JSON, interface{}, preallocation)
   - Continuous Profiling (Pyroscope, Cloud Profiler, Datadog)
   - CI/CD интеграция для отслеживания регрессий
   - 4 практических примера: HTTP сервис, memory leak, latency spikes, CI/CD

## Время изучения

**Примерно**: 3-4 недели интенсивного обучения

## Проверка знаний

После изучения этой части вы должны уметь:

- [x] Создавать конкурентные приложения с горутинами
- [x] Использовать каналы для коммуникации
- [x] Понимать работу планировщика Go
- [x] Оптимизировать код с учетом GC
- [x] Профилировать приложения
- [x] Писать эффективные тесты и benchmarks
- [x] Обрабатывать ошибки идиоматично

---

[← Назад к оглавлению](../README.md) | [Предыдущая часть](../part1-basics/) | [Следующая часть →](../part3-web-api/)
