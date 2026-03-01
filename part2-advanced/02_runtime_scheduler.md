# 2.2 Go Runtime и планировщик

## Содержание

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Введение](#%D0%B2%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5)
  - [Почему это важно?](#%D0%BF%D0%BE%D1%87%D0%B5%D0%BC%D1%83-%D1%8D%D1%82%D0%BE-%D0%B2%D0%B0%D0%B6%D0%BD%D0%BE)
- [Архитектура GMP](#%D0%B0%D1%80%D1%85%D0%B8%D1%82%D0%B5%D0%BA%D1%82%D1%83%D1%80%D0%B0-gmp)
  - [Компоненты](#%D0%BA%D0%BE%D0%BC%D0%BF%D0%BE%D0%BD%D0%B5%D0%BD%D1%82%D1%8B)
    - [G - Goroutine](#g---goroutine)
    - [M - Machine (OS Thread)](#m---machine-os-thread)
    - [P - Processor (контекст выполнения)](#p---processor-%D0%BA%D0%BE%D0%BD%D1%82%D0%B5%D0%BA%D1%81%D1%82-%D0%B2%D1%8B%D0%BF%D0%BE%D0%BB%D0%BD%D0%B5%D0%BD%D0%B8%D1%8F)
  - [Взаимодействие GMP](#%D0%B2%D0%B7%D0%B0%D0%B8%D0%BC%D0%BE%D0%B4%D0%B5%D0%B9%D1%81%D1%82%D0%B2%D0%B8%D0%B5-gmp)
  - [Жизненный цикл](#%D0%B6%D0%B8%D0%B7%D0%BD%D0%B5%D0%BD%D0%BD%D1%8B%D0%B9-%D1%86%D0%B8%D0%BA%D0%BB)
  - [Сравнение с .NET ThreadPool](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81-net-threadpool)
- [Work-Stealing алгоритм](#work-stealing-%D0%B0%D0%BB%D0%B3%D0%BE%D1%80%D0%B8%D1%82%D0%BC)
  - [Как работает](#%D0%BA%D0%B0%D0%BA-%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%B0%D0%B5%D1%82)
  - [Реализация](#%D1%80%D0%B5%D0%B0%D0%BB%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F)
  - [C# аналог](#c-%D0%B0%D0%BD%D0%B0%D0%BB%D0%BE%D0%B3)
  - [Оптимизация для work-stealing](#%D0%BE%D0%BF%D1%82%D0%B8%D0%BC%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-%D0%B4%D0%BB%D1%8F-work-stealing)
- [Preemption (вытеснение)](#preemption-%D0%B2%D1%8B%D1%82%D0%B5%D1%81%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5)
  - [История](#%D0%B8%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F)
  - [Как работает preemption](#%D0%BA%D0%B0%D0%BA-%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%B0%D0%B5%D1%82-preemption)
  - [Cooperative vs Preemptive](#cooperative-vs-preemptive)
  - [Safe points](#safe-points)
- [GOMAXPROCS](#gomaxprocs)
  - [Значение по умолчанию](#%D0%B7%D0%BD%D0%B0%D1%87%D0%B5%D0%BD%D0%B8%D0%B5-%D0%BF%D0%BE-%D1%83%D0%BC%D0%BE%D0%BB%D1%87%D0%B0%D0%BD%D0%B8%D1%8E)
  - [Настройка](#%D0%BD%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0)
  - [Влияние на производительность](#%D0%B2%D0%BB%D0%B8%D1%8F%D0%BD%D0%B8%D0%B5-%D0%BD%D0%B0-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%B2%D0%BE%D0%B4%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D0%BE%D1%81%D1%82%D1%8C)
  - [Сравнение с .NET](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81-net)
  - [Рекомендации](#%D1%80%D0%B5%D0%BA%D0%BE%D0%BC%D0%B5%D0%BD%D0%B4%D0%B0%D1%86%D0%B8%D0%B8)
- [Сравнение с .NET ThreadPool](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81-net-threadpool-1)
  - [Архитектура](#%D0%B0%D1%80%D1%85%D0%B8%D1%82%D0%B5%D0%BA%D1%82%D1%83%D1%80%D0%B0)
  - [Ключевые различия](#%D0%BA%D0%BB%D1%8E%D1%87%D0%B5%D0%B2%D1%8B%D0%B5-%D1%80%D0%B0%D0%B7%D0%BB%D0%B8%D1%87%D0%B8%D1%8F)
  - [Пример: блокирующий syscall](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-%D0%B1%D0%BB%D0%BE%D0%BA%D0%B8%D1%80%D1%83%D1%8E%D1%89%D0%B8%D0%B9-syscall)
  - [Преимущества Go](#%D0%BF%D1%80%D0%B5%D0%B8%D0%BC%D1%83%D1%89%D0%B5%D1%81%D1%82%D0%B2%D0%B0-go)
- [Трассировка и диагностика](#%D1%82%D1%80%D0%B0%D1%81%D1%81%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D0%B0-%D0%B8-%D0%B4%D0%B8%D0%B0%D0%B3%D0%BD%D0%BE%D1%81%D1%82%D0%B8%D0%BA%D0%B0)
  - [go tool trace](#go-tool-trace)
  - [GODEBUG=schedtrace](#godebugschedtrace)
  - [runtime.NumGoroutine()](#runtimenumgoroutine)
  - [pprof goroutine profile](#pprof-goroutine-profile)
- [Оптимизация под планировщик](#%D0%BE%D0%BF%D1%82%D0%B8%D0%BC%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-%D0%BF%D0%BE%D0%B4-%D0%BF%D0%BB%D0%B0%D0%BD%D0%B8%D1%80%D0%BE%D0%B2%D1%89%D0%B8%D0%BA)
  - [1. Избегайте создания слишком многих горутин](#1-%D0%B8%D0%B7%D0%B1%D0%B5%D0%B3%D0%B0%D0%B9%D1%82%D0%B5-%D1%81%D0%BE%D0%B7%D0%B4%D0%B0%D0%BD%D0%B8%D1%8F-%D1%81%D0%BB%D0%B8%D1%88%D0%BA%D0%BE%D0%BC-%D0%BC%D0%BD%D0%BE%D0%B3%D0%B8%D1%85-%D0%B3%D0%BE%D1%80%D1%83%D1%82%D0%B8%D0%BD)
  - [2. Минимизируйте блокировки](#2-%D0%BC%D0%B8%D0%BD%D0%B8%D0%BC%D0%B8%D0%B7%D0%B8%D1%80%D1%83%D0%B9%D1%82%D0%B5-%D0%B1%D0%BB%D0%BE%D0%BA%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D0%B8)
  - [3. Используйте buffered channels правильно](#3-%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D1%83%D0%B9%D1%82%D0%B5-buffered-channels-%D0%BF%D1%80%D0%B0%D0%B2%D0%B8%D0%BB%D1%8C%D0%BD%D0%BE)
  - [4. Избегайте долгих вычислений без yield](#4-%D0%B8%D0%B7%D0%B1%D0%B5%D0%B3%D0%B0%D0%B9%D1%82%D0%B5-%D0%B4%D0%BE%D0%BB%D0%B3%D0%B8%D1%85-%D0%B2%D1%8B%D1%87%D0%B8%D1%81%D0%BB%D0%B5%D0%BD%D0%B8%D0%B9-%D0%B1%D0%B5%D0%B7-yield)
  - [5. GOMAXPROCS для контейнеров](#5-gomaxprocs-%D0%B4%D0%BB%D1%8F-%D0%BA%D0%BE%D0%BD%D1%82%D0%B5%D0%B9%D0%BD%D0%B5%D1%80%D0%BE%D0%B2)
- [Практические примеры](#%D0%BF%D1%80%D0%B0%D0%BA%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B5-%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80%D1%8B)
  - [Пример 1: Мониторинг планировщика](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-1-%D0%BC%D0%BE%D0%BD%D0%B8%D1%82%D0%BE%D1%80%D0%B8%D0%BD%D0%B3-%D0%BF%D0%BB%D0%B0%D0%BD%D0%B8%D1%80%D0%BE%D0%B2%D1%89%D0%B8%D0%BA%D0%B0)
  - [Пример 2: Оптимизация с worker pool](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-2-%D0%BE%D0%BF%D1%82%D0%B8%D0%BC%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-%D1%81-worker-pool)
  - [Пример 3: Сравнение GOMAXPROCS](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-3-%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-gomaxprocs)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

---

## Введение

Go runtime включает в себя **планировщик горутин** (goroutine scheduler), который эффективно мультиплексирует миллионы горутин на ограниченное количество OS threads.

### Почему это важно?

**C# разработчики** привыкли к тому, что:
- Task работает на ThreadPool
- ThreadPool управляет OS threads
- Async/await - это синтаксический сахар над callbacks

**В Go**:
- Горутины НЕ равны OS threads
- Go runtime сам управляет маппингом горутин на threads
- Понимание планировщика критично для производительности

> 💡 **Ключевое отличие**: В C# вы работаете с ThreadPool напрямую, в Go - через runtime планировщик, который намного эффективнее.

---

## Архитектура GMP

GMP - это модель планировщика Go:
- **G** (Goroutine) - горутина
- **M** (Machine) - OS thread
- **P** (Processor) - контекст выполнения

### Компоненты

#### G - Goroutine

Горутина - это легковесный поток выполнения.

**Характеристики**:
- Стек: начинается с 2KB (динамически растёт до 1GB)
- Состояние: running, runnable, waiting, dead
- Хранит: SP (stack pointer), PC (program counter), регистры

```go
type g struct {
    stack       stack   // Стек горутины
    stackguard0 uintptr // Защита от переполнения
    m           *m      // Текущий M (thread)
    sched       gobuf   // Контекст (SP, PC, регистры)
    // ... другие поля
}
```

**C# аналог**:
```csharp
// Task - это NOT thread, но высокоуровневая абстракция
var task = Task.Run(() => DoWork());

// Thread - это OS thread
var thread = new Thread(() => DoWork());
```

#### M - Machine (OS Thread)

Machine представляет реальный OS thread.

**Характеристики**:
- Соответствует OS thread (pthread на Linux, thread на Windows)
- Выполняет горутины
- Может блокироваться (syscall, cgo)
- Максимум: 10000 (ограничение runtime)

```go
type m struct {
    g0      *g    // Горутина для планировщика
    curg    *g    // Текущая выполняющаяся горутина
    p       *p    // Привязанный P
    nextp   *p    // P для следующего запуска
    // ... другие поля
}
```

**Важно**: M может существовать без P (заблокирован), но не может выполнять Go код.

#### P - Processor (контекст выполнения)

P представляет **логический процессор** - ресурс, необходимый для выполнения Go кода.

**Характеристики**:
- Количество: `GOMAXPROCS` (по умолчанию = количество CPU cores)
- Содержит local run queue горутин
- Кеш для аллокаций (mcache)
- Может быть передан между M

```go
type p struct {
    m           *m       // Текущий M
    runqhead    uint32   // Голова local run queue
    runqtail    uint32   // Хвост local run queue
    runq        [256]guintptr // Local run queue
    runnext     guintptr // Следующая горутина (приоритет)
    // ... другие поля
}
```

### Взаимодействие GMP

```
┌─────────────────────────────────────────────────┐
│              Global Run Queue                    │
│  (горутины, ожидающие выполнения)               │
└─────────────────────────────────────────────────┘
              ↓          ↓          ↓
    ┌─────────┐   ┌─────────┐   ┌─────────┐
    │    P0   │   │    P1   │   │    P2   │
    │ ┌─────┐ │   │ ┌─────┐ │   │ ┌─────┐ │
    │ │ LRQ │ │   │ │ LRQ │ │   │ │ LRQ │ │  Local Run Queues
    │ └─────┘ │   │ └─────┘ │   │ └─────┘ │
    └────┬────┘   └────┬────┘   └────┬────┘
         │             │             │
    ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
    │    M0   │   │    M1   │   │    M2   │  OS Threads
    └─────────┘   └─────────┘   └─────────┘
         │             │             │
    ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
    │    G1   │   │    G5   │   │    G9   │  Горутины
    │    G2   │   │    G6   │   │   G10   │
    │    G3   │   │    G7   │   │   G11   │
    │    G4   │   │    G8   │   │   G12   │
    └─────────┘   └─────────┘   └─────────┘
```

### Жизненный цикл

1. **Создание горутины** (`go func()`)
   - Создаётся структура G
   - Добавляется в run queue

2. **Планирование**
   - M берёт G из local run queue своего P
   - Если пусто - пытается украсть из других P (work-stealing)
   - Если везде пусто - берёт из global run queue

3. **Выполнение**
   - M выполняет G
   - При блокировке (channel, syscall) - G снимается с M

4. **Завершение**
   - G возвращается в pool для переиспользования
   - M ищет следующую G

### Сравнение с .NET ThreadPool

| Аспект | .NET ThreadPool | Go Scheduler |
|--------|-----------------|--------------|
| **Единица работы** | Task | Goroutine (G) |
| **Worker** | OS Thread | M (OS Thread) + P |
| **Очередь** | Global queue | Local (P) + Global |
| **Stealing** | Да (ограниченный) | Да (агрессивный) |
| **Контекст** | Нет | P (процессор) |
| **Preemption** | Cooperative (.NET < 6) | Cooperative + Signal-based |
| **Max workers** | ~1000-2000 threads | 10000 M, unlimited G |

---

## Work-Stealing алгоритм

Work-stealing - это механизм балансировки нагрузки между P.

### Как работает

```
P0 (занят)          P1 (простаивает)
┌────────┐          ┌────────┐
│ G1     │          │        │
│ G2     │   steal │        │
│ G3     │  ───────>  G3    │
│ G4     │          │        │
└────────┘          └────────┘
```

**Алгоритм**:
1. P проверяет свой local run queue
2. Если пусто → проверяет global run queue
3. Если пусто → **крадёт** половину горутин из другого P
4. Если везде пусто → переходит в режим ожидания

### Реализация

```go
// Упрощённая версия
func findrunnable() *g {
    // 1. Проверяем local run queue
    if gp := runqget(_p_); gp != nil {
        return gp
    }

    // 2. Проверяем global run queue
    if gp := globrunqget(_p_); gp != nil {
        return gp
    }

    // 3. Work-stealing: пробуем украсть из других P
    for i := 0; i < len(allp); i++ {
        p := allp[(i+offset)%len(allp)]
        if gp := runqsteal(_p_, p); gp != nil {
            return gp
        }
    }

    // 4. Ничего не нашли - засыпаем
    stopm()
}
```

### C# аналог

**.NET 6+ ThreadPool** также использует work-stealing, но:

```csharp
// .NET ThreadPool (упрощённо)
// - Каждый thread имеет local queue
// - Stealing происходит реже
// - Global queue имеет более высокий приоритет

ThreadPool.QueueUserWorkItem(_ => DoWork());
```

**Отличия**:
- Go stealing более агрессивный
- Go проверяет local queue чаще
- Go имеет два уровня: local (P) и global

### Оптимизация для work-stealing

```go
// ❌ Плохо: создаём дисбаланс
func bad() {
    for i := 0; i < 1000000; i++ {
        go func() {
            // Очень короткая работа
            _ = i * 2
        }()
    }
}

// ✅ Хорошо: используем worker pool
func good() {
    const numWorkers = 10
    jobs := make(chan int, 1000)

    for w := 0; w < numWorkers; w++ {
        go func() {
            for job := range jobs {
                _ = job * 2
            }
        }()
    }

    for i := 0; i < 1000000; i++ {
        jobs <- i
    }
    close(jobs)
}
```

---

## Preemption (вытеснение)

Preemption - это механизм, позволяющий планировщику **прерывать** выполняющуюся горутину.

### История

**Go 1.0-1.13**: Cooperative preemption
- Горутина вытеснялась только в safe points (function calls)
- Проблема: бесконечный цикл без вызовов функций блокировал P

```go
// Проблема в Go < 1.14
func loop() {
    for {
        // Нет function calls - не вытесняется
        i := 0
        i++
    }
}
```

**Go 1.14+**: Signal-based preemption (асинхронный)
- Runtime может прервать горутину в любой момент
- Использует OS signals (SIGURG на Unix)

### Как работает preemption

```
G выполняется > 10ms
         ↓
Планировщик отправляет signal
         ↓
G сохраняет контекст
         ↓
G перемещается в run queue
         ↓
M выполняет другую G
```

**Код планировщика**:
```go
// Упрощённо
const preemptionInterval = 10 * time.Millisecond

func sysmon() {
    for {
        // Проверяем все P
        for _, pp := range allp {
            if pp.m != nil && pp.m.curg != nil {
                gp := pp.m.curg

                // Если G выполняется > 10ms - вытесняем
                if now - gp.schedtime > preemptionInterval {
                    preemptone(pp)
                }
            }
        }

        time.Sleep(sysmonInterval)
    }
}
```

### Cooperative vs Preemptive

**C# (до .NET 6)**:
```csharp
// Cooperative - задача должна сама yield
async Task LongRunning()
{
    for (int i = 0; i < 1000000; i++)
    {
        // Явный yield
        if (i % 1000 == 0)
            await Task.Yield(); // Даём ThreadPool переключиться
    }
}
```

**Go (1.14+)**:
```go
// Планировщик сам прервёт через 10ms
func longRunning() {
    for i := 0; i < 1000000; i++ {
        // Не нужен явный yield
        _ = i * 2
    }
}
```

### Safe points

Несмотря на signal-based preemption, есть места, где вытеснение безопаснее:

```go
// Safe points:
// 1. Function calls
func work() {
    doSomething() // Safe point
}

// 2. Channel operations
ch := make(chan int)
ch <- 42 // Safe point
val := <-ch // Safe point

// 3. Memory allocations
data := make([]int, 1000) // Safe point
```

---

## GOMAXPROCS

`GOMAXPROCS` определяет количество P (логических процессоров).

### Значение по умолчанию

```go
import "runtime"

func main() {
    // По умолчанию = количество CPU cores
    fmt.Println(runtime.GOMAXPROCS(0)) // 8 (на 8-core машине)
}
```

### Настройка

```go
// Программно
runtime.GOMAXPROCS(4) // Установить 4 P

// Через переменную окружения
// GOMAXPROCS=4 go run main.go
```

### Влияние на производительность

**CPU-bound задачи**:
```go
// GOMAXPROCS = количество cores - оптимально
func cpuBound() {
    for i := 0; i < 1e9; i++ {
        _ = i * i
    }
}
```

**I/O-bound задачи**:
```go
// GOMAXPROCS может быть > cores
// Горутины блокируются на I/O, освобождая M
func ioBound() {
    resp, _ := http.Get("https://example.com")
    defer resp.Body.Close()
}
```

### Сравнение с .NET

**C#**:
```csharp
// .NET ThreadPool
ThreadPool.SetMinThreads(minWorker, minIO);
ThreadPool.SetMaxThreads(maxWorker, maxIO);

// По умолчанию:
// Min = количество cores
// Max = 32767 (теоретически)
```

**Go**:
```go
// GOMAXPROCS - количество параллельных исполнителей
// Не ограничивает количество M (threads)
// M создаются по необходимости (до 10000)
```

### Рекомендации

✅ **Оставьте по умолчанию** (= cores) для большинства случаев

⚠️ **Увеличьте**, если:
- Много I/O-bound операций
- Используете cgo (блокирует M)
- Запускаете в контейнере с CPU throttling

❌ **Не уменьшайте** без причины:
```go
// ❌ Плохо
runtime.GOMAXPROCS(1) // Только 1 P - нет параллелизма
```

---

## Сравнение с .NET ThreadPool

### Архитектура

**.NET ThreadPool** (упрощённо):
```
                Global Queue
                     ↓
    ┌────────────────┴────────────────┐
    ↓                ↓                ↓
Worker Thread 1  Worker Thread 2  Worker Thread N
    ↓                ↓                ↓
Local Queue      Local Queue      Local Queue
```

**Go Scheduler**:
```
                Global Queue
                     ↓
    ┌────────────────┴────────────────┐
    ↓                ↓                ↓
    P0               P1               P2
    ↓                ↓                ↓
    M0               M1               M2
    ↓                ↓                ↓
 Goroutines      Goroutines      Goroutines
```

### Ключевые различия

| Аспект | .NET ThreadPool | Go Scheduler |
|--------|-----------------|--------------|
| **Модель** | Thread Pool | M:N scheduler |
| **Единица** | Task на Thread | Goroutine на M через P |
| **Контекст** | Нет явного | P (процессор) |
| **Work-stealing** | Да (с .NET 4) | Да (агрессивный) |
| **Количество threads** | ~cores * 2-4 | Динамическое (до 10000 M) |
| **Блокировка** | Блокирует thread | M отсоединяется от P |
| **Preemption** | Cooperative | Signal-based (1.14+) |

### Пример: блокирующий syscall

**C#**:
```csharp
// Syscall блокирует worker thread
await Task.Run(() =>
{
    // Блокирующий I/O
    using var file = File.OpenRead("large.dat");
    var buffer = new byte[1024];
    file.Read(buffer, 0, buffer.Length); // Блокирует thread

    // ThreadPool создаст новый thread если нужно
});
```

**Go**:
```go
// Syscall блокирует M, но не P
go func() {
    // Блокирующий I/O
    file, _ := os.Open("large.dat")
    defer file.Close()

    buffer := make([]byte, 1024)
    file.Read(buffer) // Блокирует M

    // Runtime отсоединяет M от P
    // P берёт другой M и продолжает работу
}()
```

### Преимущества Go

1. **Лёгкость**: Горутины легче Task (нет boxing, меньше накладных расходов)
2. **Масштабируемость**: Миллионы горутин vs тысячи threads
3. **Контекст P**: Кеширование аллокаций, лучшая locality
4. **Адаптивность**: M создаются/уничтожаются по необходимости

---

## Трассировка и диагностика

### go tool trace

Визуализация работы планировщика.

```bash
# Запись trace
go test -trace=trace.out

# Или в коде
import "runtime/trace"

func main() {
    f, _ := os.Create("trace.out")
    defer f.Close()

    trace.Start(f)
    defer trace.Stop()

    // Ваш код
}

# Просмотр trace
go tool trace trace.out
```

**Что показывает trace**:
- Горутины по времени
- Переключения между G
- Блокировки на каналах
- GC события
- Syscalls

**Пример вывода**:
```
Goroutine analysis:
  Running: 4
  Runnable: 120
  Blocked: 0

Processor utilization:
  P0: 98%
  P1: 95%
  P2: 12%  ← Проблема: простаивает
  P3: 97%
```

### GODEBUG=schedtrace

Периодическая печать статистики планировщика.

```bash
GODEBUG=schedtrace=1000 ./myapp
```

**Вывод**:
```
SCHED 1000ms: gomaxprocs=4 idleprocs=0 threads=6 spinningthreads=0 idlethreads=1 runqueue=0 [0 0 0 0]
       ↑         ↑           ↑           ↑           ↑               ↑            ↑        ↑
     время   GOMAXPROCS   простаивающих  всего M   spinning M    idle M    global RQ  local RQ (по P)
```

**Расшифровка**:
- `gomaxprocs=4`: 4 процессора (P)
- `idleprocs=0`: все P заняты (хорошо)
- `threads=6`: 6 OS threads (M)
- `runqueue=0`: global run queue пуста
- `[0 0 0 0]`: local run queues (все пусты - хорошо)

### runtime.NumGoroutine()

```go
import "runtime"

func main() {
    // Количество активных горутин
    fmt.Println("Goroutines:", runtime.NumGoroutine())

    for i := 0; i < 1000; i++ {
        go func() {
            time.Sleep(time.Hour)
        }()
    }

    fmt.Println("Goroutines:", runtime.NumGoroutine()) // ~1001
}
```

### pprof goroutine profile

```go
import _ "net/http/pprof"

func main() {
    go func() {
        http.ListenAndServe("localhost:6060", nil)
    }()

    // Ваш код
}
```

```bash
# Просмотр горутин
go tool pprof http://localhost:6060/debug/pprof/goroutine

# В интерактивном режиме
(pprof) top
Showing nodes accounting for 1000, 100% of 1000 total
      flat  flat%   sum%        cum   cum%
      500 50.00% 50.00%       500 50.00%  main.worker
      300 30.00% 80.00%       300 30.00%  net/http.(*conn).serve
      200 20.00% 100.00%      200 20.00%  time.Sleep
```

---

## Оптимизация под планировщик

### 1. Избегайте создания слишком многих горутин

```go
// ❌ Плохо: 1 миллион горутин для trivial работы
func bad() {
    for i := 0; i < 1_000_000; i++ {
        go func(n int) {
            fmt.Println(n)
        }(i)
    }
}

// ✅ Хорошо: worker pool
func good() {
    const workers = 100
    jobs := make(chan int, 1000)

    var wg sync.WaitGroup
    for w := 0; w < workers; w++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobs {
                fmt.Println(job)
            }
        }()
    }

    for i := 0; i < 1_000_000; i++ {
        jobs <- i
    }
    close(jobs)
    wg.Wait()
}
```

### 2. Минимизируйте блокировки

```go
// ❌ Плохо: частые блокировки на mutex
type Counter struct {
    mu sync.Mutex
    value int
}

func (c *Counter) Inc() {
    c.mu.Lock()
    c.value++
    c.mu.Unlock() // Блокирует горутину, снимает с M
}

// ✅ Лучше: atomic операции
type Counter struct {
    value int64
}

func (c *Counter) Inc() {
    atomic.AddInt64(&c.value, 1) // Не блокирует
}
```

### 3. Используйте buffered channels правильно

```go
// ❌ Плохо: небуферизированный = блокировки
ch := make(chan int)

go func() {
    for i := 0; i < 1000; i++ {
        ch <- i // Блокируется на каждой отправке
    }
}()

for i := 0; i < 1000; i++ {
    <-ch // Блокируется на каждом получении
}

// ✅ Лучше: буферизированный
ch := make(chan int, 100) // Меньше блокировок

go func() {
    for i := 0; i < 1000; i++ {
        ch <- i // Блокируется только когда буфер полон
    }
    close(ch)
}()

for val := range ch {
    _ = val
}
```

### 4. Избегайте долгих вычислений без yield

```go
// ❌ Плохо (в Go < 1.14): монополизирует P
func compute() {
    sum := 0
    for i := 0; i < 1e9; i++ {
        sum += i
    }
    return sum
}

// ✅ Хорошо: периодически yield (для Go < 1.14)
func compute() {
    sum := 0
    for i := 0; i < 1e9; i++ {
        sum += i
        if i % 1e6 == 0 {
            runtime.Gosched() // Явный yield
        }
    }
    return sum
}

// ✅ Go 1.14+: не нужен явный yield (signal-based preemption)
func compute() {
    sum := 0
    for i := 0; i < 1e9; i++ {
        sum += i
    }
    return sum
}
```

### 5. GOMAXPROCS для контейнеров

```go
import _ "go.uber.org/automaxprocs"

// Автоматически устанавливает GOMAXPROCS
// на основе CPU limits в контейнере
func main() {
    // automaxprocs уже установил правильное значение
    // ...
}
```

---

## Практические примеры

### Пример 1: Мониторинг планировщика

```go
package main

import (
    "fmt"
    "runtime"
    "time"
)

func monitorScheduler(interval time.Duration) {
    ticker := time.NewTicker(interval)
    defer ticker.Stop()

    for range ticker.C {
        var stats runtime.MemStats
        runtime.ReadMemStats(&stats)

        fmt.Printf("Goroutines: %d, Threads: %d, GOMAXPROCS: %d\n",
            runtime.NumGoroutine(),
            runtime.NumCPU(),
            runtime.GOMAXPROCS(0))

        fmt.Printf("Heap: %.2f MB, Alloc: %.2f MB\n",
            float64(stats.HeapAlloc)/1024/1024,
            float64(stats.TotalAlloc)/1024/1024)

        fmt.Println("---")
    }
}

func main() {
    go monitorScheduler(2 * time.Second)

    // Симуляция работы
    for i := 0; i < 100; i++ {
        go func(n int) {
            time.Sleep(time.Duration(n) * time.Second)
        }(i % 10)
    }

    time.Sleep(20 * time.Second)
}
```

### Пример 2: Оптимизация с worker pool

```go
package main

import (
    "fmt"
    "runtime"
    "sync"
    "time"
)

type Job struct {
    ID   int
    Data int
}

type Result struct {
    JobID  int
    Result int
}

func worker(id int, jobs <-chan Job, results chan<- Result, wg *sync.WaitGroup) {
    defer wg.Done()

    for job := range jobs {
        // Симуляция CPU-intensive работы
        result := 0
        for i := 0; i < job.Data; i++ {
            result += i
        }

        results <- Result{
            JobID:  job.ID,
            Result: result,
        }
    }
}

func main() {
    numWorkers := runtime.GOMAXPROCS(0) // = количество P
    numJobs := 1000

    jobs := make(chan Job, 100)
    results := make(chan Result, 100)

    var wg sync.WaitGroup

    // Запускаем workers
    fmt.Printf("Starting %d workers (GOMAXPROCS=%d)\n", numWorkers, numWorkers)
    for w := 0; w < numWorkers; w++ {
        wg.Add(1)
        go worker(w, jobs, results, &wg)
    }

    // Закрываем results после завершения всех workers
    go func() {
        wg.Wait()
        close(results)
    }()

    // Отправляем jobs
    start := time.Now()
    go func() {
        for i := 0; i < numJobs; i++ {
            jobs <- Job{ID: i, Data: 10000}
        }
        close(jobs)
    }()

    // Собираем результаты
    count := 0
    for range results {
        count++
    }

    elapsed := time.Since(start)
    fmt.Printf("Processed %d jobs in %v\n", count, elapsed)
    fmt.Printf("Throughput: %.2f jobs/sec\n", float64(count)/elapsed.Seconds())
}
```

### Пример 3: Сравнение GOMAXPROCS

```go
package main

import (
    "fmt"
    "runtime"
    "sync"
    "time"
)

func cpuIntensiveWork(n int) int {
    result := 0
    for i := 0; i < n; i++ {
        result += i
    }
    return result
}

func benchmark(numGoroutines, gomaxprocs int) time.Duration {
    runtime.GOMAXPROCS(gomaxprocs)

    var wg sync.WaitGroup
    start := time.Now()

    for i := 0; i < numGoroutines; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            cpuIntensiveWork(1000000)
        }()
    }

    wg.Wait()
    return time.Since(start)
}

func main() {
    numCPU := runtime.NumCPU()
    fmt.Printf("CPU cores: %d\n\n", numCPU)

    goroutines := []int{10, 100, 1000}
    gomaxprocsValues := []int{1, numCPU / 2, numCPU, numCPU * 2}

    for _, g := range goroutines {
        fmt.Printf("=== %d goroutines ===\n", g)
        for _, p := range gomaxprocsValues {
            duration := benchmark(g, p)
            fmt.Printf("GOMAXPROCS=%d: %v\n", p, duration)
        }
        fmt.Println()
    }
}
```

---

**Вопросы?** Открой issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Назад: Горутины и каналы](01_goroutines_channels.md) | [Вперёд: Аллокатор памяти →](02a_memory_allocator.md)
