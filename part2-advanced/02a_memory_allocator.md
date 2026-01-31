# 2.2a Аллокатор памяти Go (Memory Allocator Internals)

## Содержание

- [Введение](#введение)
- [1. Virtual Memory vs Physical Memory](#1-virtual-memory-vs-physical-memory)
  - [1.1 Основы виртуальной памяти](#11-основы-виртуальной-памяти)
  - [1.2 Сравнение с .NET CLR](#12-сравнение-с-net-clr)
  - [1.3 mmap и резервирование памяти](#13-mmap-и-резервирование-памяти)
- [2. Страницы памяти (Memory Pages)](#2-страницы-памяти-memory-pages)
  - [2.1 Page и page fault](#21-page-и-page-fault)
  - [2.2 Huge Pages в Go](#22-huge-pages-в-go)
  - [2.3 Сравнение с .NET GC Regions](#23-сравнение-с-net-gc-regions)
- [3. Архитектура аллокатора Go](#3-архитектура-аллокатора-go)
  - [3.1 Общая схема: mheap → mcentral → mcache](#31-общая-схема-mheap--mcentral--mcache)
  - [3.2 Сравнение с .NET SOH/LOH/POH](#32-сравнение-с-net-sohlohpoh)
- [4. mheap: Глобальная куча](#4-mheap-глобальная-куча)
  - [4.1 Структура и назначение](#41-структура-и-назначение)
  - [4.2 Arena и heap growth](#42-arena-и-heap-growth)
- [5. mspan: Единица управления памятью](#5-mspan-единица-управления-памятью)
  - [5.1 Структура mspan](#51-структура-mspan)
  - [5.2 Bitmap для отслеживания объектов](#52-bitmap-для-отслеживания-объектов)
  - [5.3 Состояния span](#53-состояния-span)
- [6. mcentral: Центральный кеш](#6-mcentral-центральный-кеш)
  - [6.1 Роль в многопоточной аллокации](#61-роль-в-многопоточной-аллокации)
  - [6.2 Partial и Full span списки](#62-partial-и-full-span-списки)
- [7. mcache: Per-P кеш](#7-mcache-per-p-кеш)
  - [7.1 Связь с P (Processor)](#71-связь-с-p-processor)
  - [7.2 Tiny allocator](#72-tiny-allocator)
  - [7.3 Сравнение с .NET Thread allocation context](#73-сравнение-с-net-thread-allocation-context)
- [8. Size Classes](#8-size-classes)
  - [8.1 Что такое size class](#81-что-такое-size-class)
  - [8.2 Таблица size classes в Go](#82-таблица-size-classes-в-go)
  - [8.3 Оптимизация структур под size classes](#83-оптимизация-структур-под-size-classes)
- [9. Путь аллокации: от new() до памяти](#9-путь-аллокации-от-new-до-памяти)
  - [9.1 mallocgc() пошагово](#91-mallocgc-пошагово)
  - [9.2 Fast path vs Slow path](#92-fast-path-vs-slow-path)
  - [9.3 Tiny, Small и Large аллокации](#93-tiny-small-и-large-аллокации)
- [10. Диагностика и мониторинг](#10-диагностика-и-мониторинг)
  - [10.1 runtime.MemStats детально](#101-runtimememstats-детально)
  - [10.2 GODEBUG флаги](#102-godebug-флаги)
  - [10.3 pprof визуализация](#103-pprof-визуализация)
- [Практические примеры](#практические-примеры)
- [Чек-лист](#чек-лист)

---

## Введение

Go runtime включает в себя **собственный аллокатор памяти**, который эффективно управляет выделением и освобождением памяти без обращения к системному malloc() для каждой аллокации.

### Почему это важно?

**C# разработчики** привыкли к тому, что:
- CLR управляет памятью через Managed Heap
- Есть разделение на SOH (Small Object Heap) и LOH (Large Object Heap)
- GC компактирует память (перемещает объекты)
- Аллокация — это просто сдвиг указателя (bump pointer)

**В Go**:
- Runtime использует **TCMalloc-подобный** аллокатор
- Память организована в **spans** фиксированных size classes
- GC **не компактирует** память (объекты не перемещаются)
- Каждый P (процессор) имеет **локальный кеш** (mcache) для быстрых аллокаций

> 💡 **Ключевое отличие**: В .NET аллокация — это bump pointer (сдвиг указателя). В Go — это выбор объекта из free list соответствующего size class.

### Что вы узнаете

После изучения этого раздела вы будете понимать:
- Как виртуальная память отображается на физическую
- Как Go организует heap через mheap, mcentral, mcache
- Что такое size classes и почему они важны
- Как оптимизировать структуры для минимизации потерь памяти

---

## 1. Virtual Memory vs Physical Memory

### 1.1 Основы виртуальной памяти

Современные операционные системы используют **виртуальную память** — абстракцию, которая даёт каждому процессу иллюзию собственного непрерывного адресного пространства.

```
┌─────────────────────────────────────────────────────────────┐
│                    Virtual Address Space                     │
│                    (процесс видит это)                       │
├─────────────────────────────────────────────────────────────┤
│  0x0000...  │  Stack  │  Heap  │  Data  │  Code  │  ...     │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ Page Table (MMU)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Physical Memory (RAM)                     │
│                    (реальная память)                         │
├─────────────────────────────────────────────────────────────┤
│  Frame 0  │  Frame 1  │  Frame 2  │  ...  │  Frame N        │
└─────────────────────────────────────────────────────────────┘
```

**Ключевые концепции**:

| Термин | Описание |
|--------|----------|
| **Virtual Address** | Адрес, который видит программа (0x00007fff...) |
| **Physical Address** | Реальный адрес в RAM |
| **Page** | Блок виртуальной памяти (обычно 4 KB) |
| **Frame** | Блок физической памяти (соответствует page) |
| **Page Table** | Таблица соответствия virtual → physical |
| **TLB** | Кеш page table для быстрого преобразования адресов |

**Преимущества виртуальной памяти**:
- **Изоляция**: процессы не видят память друг друга
- **Overcommit**: можно выделить больше памяти, чем есть физически
- **Ленивая аллокация**: физическая память выделяется при первом доступе
- **Memory-mapped files**: файлы отображаются в адресное пространство

### 1.2 Сравнение с .NET CLR

**.NET CLR** также работает с виртуальной памятью, но с важными отличиями:

| Аспект | .NET CLR | Go Runtime |
|--------|----------|------------|
| **Резервирование** | VirtualAlloc (Windows) | mmap (Unix) / VirtualAlloc (Windows) |
| **Heap структура** | Segments (SOH, LOH, POH) | Arenas и spans |
| **Компактирование** | Да (SOH) | Нет (объекты не перемещаются) |
| **Pinning** | Нужен для FFI | Не нужен (объекты не двигаются) |
| **Fragmentation** | Решается компактированием | Решается size classes |

**C# пример работы с памятью**:
```csharp
// C#: выделение памяти через CLR
var buffer = new byte[1024]; // CLR резервирует через VirtualAlloc

// Pinning для interop (объект не будет перемещён GC)
fixed (byte* ptr = buffer)
{
    // Передача указателя в native код
    NativeMethod(ptr);
}

// Unmanaged память (напрямую через ОС)
IntPtr unmanagedPtr = Marshal.AllocHGlobal(1024);
Marshal.FreeHGlobal(unmanagedPtr);
```

**Go эквивалент**:
```go
// Go: выделение памяти через runtime
buffer := make([]byte, 1024) // Go runtime выделяет через mmap

// Указатель можно передавать в cgo без pinning
// (объекты не перемещаются GC)
// #include <string.h>
// void process(void* ptr, int len);
import "C"
import "unsafe"

C.process(unsafe.Pointer(&buffer[0]), C.int(len(buffer)))
```

> ⚠️ **Важно**: В Go объекты **не перемещаются** GC, поэтому нет необходимости в `fixed` или `GCHandle.Alloc`.

### 1.3 mmap и резервирование памяти

Go runtime использует системные вызовы для работы с памятью:

**Linux/macOS**:
```go
// Упрощённо — как Go резервирует память
// runtime/mem_linux.go

func sysReserve(v unsafe.Pointer, n uintptr) unsafe.Pointer {
    // mmap с PROT_NONE — резервируем адресное пространство
    // без выделения физической памяти
    p, err := mmap(v, n, _PROT_NONE, _MAP_ANON|_MAP_PRIVATE, -1, 0)
    if err != 0 {
        return nil
    }
    return p
}

func sysMap(v unsafe.Pointer, n uintptr) {
    // mprotect — делаем память доступной для чтения/записи
    // Это вызывает выделение физических страниц при первом доступе
    mprotect(v, n, _PROT_READ|_PROT_WRITE)
}
```

**Windows**:
```go
// runtime/mem_windows.go (упрощённо)

func sysReserve(v unsafe.Pointer, n uintptr) unsafe.Pointer {
    // VirtualAlloc с MEM_RESERVE — резервируем адресное пространство
    return VirtualAlloc(v, n, _MEM_RESERVE, _PAGE_READWRITE)
}

func sysMap(v unsafe.Pointer, n uintptr) {
    // VirtualAlloc с MEM_COMMIT — выделяем физическую память
    VirtualAlloc(v, n, _MEM_COMMIT, _PAGE_READWRITE)
}
```

**Двухфазное выделение памяти**:

```
Фаза 1: Reserve (резервирование)
┌────────────────────────────────────────┐
│ Virtual Address Space                  │
│ ████████████████████ Reserved          │ ← Адреса заняты
│ (физическая память НЕ выделена)        │
└────────────────────────────────────────┘

Фаза 2: Commit (фиксация)
┌────────────────────────────────────────┐
│ Virtual Address Space                  │
│ ████████░░░░░░░░░░░░ Committed         │ ← Часть подкреплена RAM
│ ████████ = физическая память выделена  │
│ ░░░░░░░░ = только зарезервировано      │
└────────────────────────────────────────┘
```

> 💡 **Идиома Go**: Runtime резервирует большие блоки адресного пространства заранее, но физическую память выделяет лениво (при первом доступе через page fault).

---

## 2. Страницы памяти (Memory Pages)

### 2.1 Page и page fault

**Page (страница)** — минимальная единица управления памятью в ОС.

```
┌─────────────────────────────────────────────────────────────┐
│                    Virtual Memory                            │
├──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬─────┤
│ Page │ Page │ Page │ Page │ Page │ Page │ Page │ Page │ ... │
│  0   │  1   │  2   │  3   │  4   │  5   │  6   │  7   │     │
│ 4KB  │ 4KB  │ 4KB  │ 4KB  │ 4KB  │ 4KB  │ 4KB  │ 4KB  │     │
└──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴─────┘
```

**Стандартные размеры страниц**:

| Платформа | Стандартный размер | Huge Pages |
|-----------|-------------------|------------|
| x86-64 Linux | 4 KB | 2 MB, 1 GB |
| ARM64 Linux | 4 KB (или 16 KB, 64 KB) | 2 MB, 1 GB |
| Windows x64 | 4 KB | 2 MB |
| macOS | 4 KB (Intel), 16 KB (Apple Silicon) | — |

**Page Fault** — прерывание при доступе к странице, не загруженной в RAM:

```
Программа обращается к адресу 0x7fff1234
         │
         ▼
┌─────────────────────┐
│ MMU проверяет       │
│ Page Table          │
└─────────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
  Valid    Invalid
  (в RAM)  (Page Fault)
    │         │
    │         ▼
    │    ┌─────────────────┐
    │    │ Ядро ОС:        │
    │    │ 1. Выделяет     │
    │    │    физ. страницу│
    │    │ 2. Обновляет    │
    │    │    Page Table   │
    │    │ 3. Возвращает   │
    │    │    управление   │
    │    └─────────────────┘
    │         │
    ▼         ▼
  Доступ к данным
```

**Типы page fault**:
- **Minor (soft)**: страница в RAM, но не в page table (быстро)
- **Major (hard)**: нужно загрузить с диска (медленно — swap)

**Проверка page fault в Go**:
```go
package main

import (
    "fmt"
    "runtime"
    "syscall"
)

func main() {
    var rusage syscall.Rusage

    // Выделяем большой slice
    data := make([]byte, 100*1024*1024) // 100 MB

    // Читаем rusage до и после доступа к памяти
    syscall.Getrusage(syscall.RUSAGE_SELF, &rusage)
    minorBefore := rusage.Minflt
    majorBefore := rusage.Majflt

    // Трогаем каждую страницу (вызываем page faults)
    pageSize := 4096
    for i := 0; i < len(data); i += pageSize {
        data[i] = 1
    }

    syscall.Getrusage(syscall.RUSAGE_SELF, &rusage)
    fmt.Printf("Minor page faults: %d\n", rusage.Minflt-minorBefore)
    fmt.Printf("Major page faults: %d\n", rusage.Majflt-majorBefore)

    runtime.KeepAlive(data)
}
```

### 2.2 Huge Pages в Go

**Huge Pages** (Large Pages) — страницы большего размера (2 MB или 1 GB вместо 4 KB).

**Преимущества**:
- Меньше записей в Page Table
- Лучше TLB hit rate
- Меньше page faults

**Недостатки**:
- Больше внутренняя фрагментация
- Сложнее управление

**Go и Huge Pages** (Go 1.21+):

```bash
# Linux: включение transparent huge pages для Go
echo madvise > /sys/kernel/mm/transparent_hugepage/enabled

# Запуск Go программы с подсказкой для THP
GODEBUG=madvdontneed=0 ./myapp
```

```go
// Go runtime автоматически использует madvise(MADV_HUGEPAGE)
// для больших аллокаций на Linux

// Проверка размера страницы
import "os"

func getPageSize() int {
    return os.Getpagesize() // 4096 на x86-64 Linux
}
```

> 💡 **Для C# разработчиков**: В .NET Large Pages настраиваются через GC config (`GCLargePages`), в Go это происходит автоматически через transparent huge pages.

### 2.3 Сравнение с .NET GC Regions

**.NET 7+** представил **Regions** — новый способ организации heap:

| Аспект | .NET Regions | Go Spans |
|--------|--------------|----------|
| **Размер** | Переменный (обычно 4 MB) | Кратен 8 KB (Go page) |
| **Назначение** | Один регион = несколько объектов | Один span = объекты одного size class |
| **Освобождение** | Регион освобождается целиком | Span возвращается в mcentral |
| **Компактирование** | Да (внутри региона) | Нет |

**C# (концептуально)**:
```csharp
// .NET Regions (внутренняя реализация)
// Регион содержит объекты разных размеров
[Region: 4 MB]
├── Object 24 bytes
├── Object 128 bytes
├── Object 56 bytes
└── Object 1024 bytes
```

**Go**:
```go
// Go Spans — объекты одного размера
// Span для size class 32 bytes
[Span: 8 KB]
├── Object 32 bytes (slot 0)
├── Object 32 bytes (slot 1)
├── Object 32 bytes (slot 2)
├── ... (всего 256 slots)
└── Object 32 bytes (slot 255)
```

---

## 3. Архитектура аллокатора Go

### 3.1 Общая схема: mheap → mcentral → mcache

Go использует **иерархический аллокатор** на основе TCMalloc (Thread-Caching Malloc от Google):

```
┌─────────────────────────────────────────────────────────────────────┐
│                              mheap                                   │
│                    (глобальная куча, одна на процесс)               │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                         Arenas                               │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │    │
│  │  │ Arena 0 │ │ Arena 1 │ │ Arena 2 │ │ Arena N │           │    │
│  │  │  64 MB  │ │  64 MB  │ │  64 MB  │ │  64 MB  │           │    │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                       mcentral[67]                           │    │
│  │  (один mcentral на каждый size class)                        │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐      ┌──────────┐   │    │
│  │  │mcentral 0│ │mcentral 1│ │mcentral 2│ ... │mcentral 66│   │    │
│  │  │ 8 bytes  │ │ 16 bytes │ │ 24 bytes │     │ 32 KB    │   │    │
│  │  └──────────┘ └──────────┘ └──────────┘      └──────────┘   │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ spans
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           mcache (per-P)                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │    mcache P0     │  │    mcache P1     │  │    mcache P2     │   │
│  │  ┌────────────┐  │  │  ┌────────────┐  │  │  ┌────────────┐  │   │
│  │  │ alloc[67]  │  │  │  │ alloc[67]  │  │  │  │ alloc[67]  │  │   │
│  │  │ spans for  │  │  │  │ spans for  │  │  │  │ spans for  │  │   │
│  │  │ each class │  │  │  │ each class │  │  │  │ each class │  │   │
│  │  └────────────┘  │  │  └────────────┘  │  │  └────────────┘  │   │
│  │  ┌────────────┐  │  │  ┌────────────┐  │  │  ┌────────────┐  │   │
│  │  │   tiny     │  │  │  │   tiny     │  │  │  │   tiny     │  │   │
│  │  │ allocator  │  │  │  │ allocator  │  │  │  │ allocator  │  │   │
│  │  └────────────┘  │  │  └────────────┘  │  │  └────────────┘  │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ объекты
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Горутины (Goroutines)                         │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐        │
│  │ Goroutine │  │ Goroutine │  │ Goroutine │  │ Goroutine │        │
│  │     1     │  │     2     │  │     3     │  │     N     │        │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘        │
└─────────────────────────────────────────────────────────────────────┘
```

**Иерархия (от медленного к быстрому)**:

1. **mheap** — глобальный heap, обращение требует блокировки
2. **mcentral** — центральный кеш для каждого size class, частичная блокировка
3. **mcache** — локальный кеш на каждом P, **без блокировки** (lock-free)

### 3.2 Сравнение с .NET SOH/LOH/POH

| Компонент Go | Аналог .NET | Описание |
|--------------|-------------|----------|
| **mheap** | Managed Heap | Глобальное хранилище |
| **Arena (64 MB)** | GC Segment (~4 MB) | Единица резервирования у ОС |
| **mspan** | Region (.NET 7+) | Блок памяти для объектов |
| **mcache** | Thread Allocation Context | Быстрая аллокация без блокировок |
| **Size classes** | — | В .NET объекты любого размера |
| **Large objects (>32KB)** | LOH (>85KB) | Отдельная обработка больших объектов |

**C# аллокация**:
```csharp
// .NET: аллокация через bump pointer
// Внутри CLR (упрощённо):
// 1. Проверяем, есть ли место в allocation context
// 2. Если да — сдвигаем указатель (очень быстро)
// 3. Если нет — получаем новый сегмент от GC

var obj = new MyClass(); // Bump pointer allocation
```

**Go аллокация**:
```go
// Go: аллокация через free list
// Внутри runtime (упрощённо):
// 1. Определяем size class для размера объекта
// 2. Берём объект из mcache.alloc[sizeClass]
// 3. Если mcache пуст — пополняем из mcentral
// 4. Если mcentral пуст — запрашиваем span у mheap

obj := new(MyStruct) // Free list allocation
```

> 💡 **Ключевое отличие**: .NET использует **bump pointer** (простой, но требует компактирования). Go использует **segregated free lists** (сложнее, но не требует компактирования).

---

## 4. mheap: Глобальная куча

### 4.1 Структура и назначение

**mheap** — единственный глобальный объект, управляющий всей heap памятью в Go.

```go
// runtime/mheap.go (упрощённо)
type mheap struct {
    lock      mutex           // Глобальная блокировка

    // Arenas — блоки виртуальной памяти
    arenas    [1 << 22]*heapArena  // До 4 миллионов арен

    // Центральные кеши для каждого size class
    central   [numSpanClasses]mcentral

    // Свободные spans разных размеров
    free      mTreap          // Treap (tree + heap) свободных spans

    // Статистика
    pagesInUse    uint64      // Страницы, используемые для heap
    pagesSwept    uint64      // Страницы, просканированные GC

    // Для GC
    sweepgen      uint32      // Поколение sweep
    sweepers      uint32      // Количество активных sweepers
}
```

**Основные операции mheap**:

```go
// Выделение span (внутренний API runtime)
func (h *mheap) alloc(npages uintptr, spanclass spanClass) *mspan {
    // 1. Пробуем найти свободный span нужного размера
    // 2. Если нет — выделяем новые страницы через sysAlloc
    // 3. Создаём mspan и возвращаем
}

// Освобождение span
func (h *mheap) freeSpan(s *mspan) {
    // 1. Добавляем span в free treap
    // 2. Пробуем объединить со смежными свободными spans
    // 3. При достаточном размере — возвращаем ОС через madvise
}
```

### 4.2 Arena и heap growth

**Arena** — большой блок виртуальной памяти (64 MB на 64-bit системах).

```
┌─────────────────────────────────────────────────────────────┐
│                    heapArena (64 MB)                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Pages (8192 pages × 8 KB)          │   │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐         ┌─────┐     │   │
│  │  │ 8KB │ │ 8KB │ │ 8KB │ │ 8KB │   ...   │ 8KB │     │   │
│  │  └─────┘ └─────┘ └─────┘ └─────┘         └─────┘     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Bitmap                             │   │
│  │  (2 бита на каждый указатель — для GC)               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Spans table                        │   │
│  │  (указатель на mspan для каждой страницы)            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

```go
// runtime/mheap.go
type heapArena struct {
    // Bitmap для GC: каждый бит указывает, является ли слово указателем
    bitmap     [heapArenaBitmapBytes]byte

    // Spans: указатель на mspan для каждой страницы
    spans      [pagesPerArena]*mspan

    // Метаданные для GC
    pageInUse  [pagesPerArena / 8]uint8
    pageMarks  [pagesPerArena / 8]uint8
}

const (
    heapArenaBytes = 64 << 20  // 64 MB
    pagesPerArena  = heapArenaBytes / pageSize  // 8192 pages (pageSize = 8 KB)
)
```

**Рост heap**:

```go
// Как Go увеличивает heap (упрощённо)
func (h *mheap) grow(npage uintptr) bool {
    // 1. Вычисляем нужный размер (кратный arena)
    ask := alignUp(npage*pageSize, heapArenaBytes)

    // 2. Резервируем виртуальную память
    v := sysReserve(nil, ask)
    if v == nil {
        return false
    }

    // 3. Создаём heapArena
    arena := (*heapArena)(sysAlloc(unsafe.Sizeof(heapArena{})))

    // 4. Регистрируем в mheap.arenas
    h.arenas[arenaIndex(v)] = arena

    return true
}
```

> 💡 **Для C# разработчиков**: В .NET heap растёт сегментами (~4 MB для SOH). В Go — аренами по 64 MB, но физическая память выделяется лениво.

---

## 5. mspan: Единица управления памятью

### 5.1 Структура mspan

**mspan** — основная структура для управления блоком памяти.

```go
// runtime/mheap.go (упрощённо)
type mspan struct {
    next       *mspan     // Следующий span в списке
    prev       *mspan     // Предыдущий span в списке

    startAddr  uintptr    // Начальный адрес span
    npages     uintptr    // Количество страниц (× 8 KB)

    // Для управления объектами
    freeindex  uintptr    // Индекс первого возможно свободного объекта
    nelems     uintptr    // Количество объектов в span

    // Free list (bitmap свободных объектов)
    allocCache uint64     // Кеш для быстрого поиска
    allocBits  *gcBits    // Bitmap аллоцированных объектов
    gcmarkBits *gcBits    // Bitmap для GC marking

    // Size class
    spanclass  spanClass  // Size class + noscan flag
    elemsize   uintptr    // Размер одного объекта

    // Состояние
    state      mSpanState // free, in use, manual, etc.

    // Статистика
    allocCount uint16     // Количество аллоцированных объектов
}
```

**Визуализация mspan**:

```
mspan для size class 32 (elemsize = 32 bytes, npages = 1)
┌─────────────────────────────────────────────────────────────┐
│                        8 KB page                             │
├─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────────────┤
│  0  │  1  │  2  │  3  │  4  │  5  │  6  │ ... │    255      │
│ 32B │ 32B │ 32B │ 32B │ 32B │ 32B │ 32B │     │    32B      │
│     │ ███ │     │ ███ │     │ ███ │     │     │             │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────────────┘
  │     │     │     │     │     │
  ▼     ▼     ▼     ▼     ▼     ▼
 free  used  free  used  free  used

allocBits:  0 1 0 1 0 1 0 0 0 0 ... (1 = занят, 0 = свободен)
allocCount: 3 (три объекта аллоцировано)
freeindex:  0 (начинаем поиск с индекса 0)
```

### 5.2 Bitmap для отслеживания объектов

**allocBits** — bitmap, где каждый бит соответствует одному слоту в span:

```go
// Аллокация объекта из span (упрощённо)
func (s *mspan) nextFreeIndex() uintptr {
    // Используем allocCache для быстрого поиска
    // (64-битное слово из allocBits)

    for s.freeindex < s.nelems {
        // Ищем первый нулевой бит (свободный слот)
        if s.allocCache != 0 {
            // ctz (count trailing zeros) — находим первый свободный
            i := sys.Ctz64(s.allocCache)
            s.allocCache >>= (i + 1)
            s.freeindex += uintptr(i) + 1
            return s.freeindex - 1
        }

        // Загружаем следующее слово из allocBits
        s.refillAllocCache()
    }

    return s.nelems // Span полон
}
```

### 5.3 Состояния span

```go
type mSpanState uint8

const (
    mSpanDead   mSpanState = iota  // Не используется
    mSpanInUse                      // Содержит объекты
    mSpanManual                     // Ручное управление (стеки)
    mSpanFree                       // В свободном списке mheap
)
```

**Жизненный цикл span**:

```
                    ┌───────────┐
                    │  mSpanFree │◄────────────────────┐
                    │  (в mheap) │                     │
                    └─────┬─────┘                      │
                          │                            │
                          │ mheap.alloc()              │ mheap.freeSpan()
                          ▼                            │
                    ┌───────────┐                      │
              ┌────►│mSpanInUse │──────────────────────┘
              │     │(в mcache) │
              │     └─────┬─────┘
              │           │
              │           │ все объекты освобождены (GC sweep)
              │           │
              │           ▼
              │     ┌───────────┐
              │     │mSpanInUse │
              └─────│ (пустой)  │
   пополнение       └───────────┘
   из mcentral
```

---

## 6. mcentral: Центральный кеш

### 6.1 Роль в многопоточной аллокации

**mcentral** — промежуточный уровень между mheap и mcache. Один mcentral на каждый size class.

```go
// runtime/mcentral.go (упрощённо)
type mcentral struct {
    spanclass spanClass  // Size class этого mcentral

    // Spans с свободными объектами
    partial [2]spanSet   // [0] = swept, [1] = unswept

    // Полностью заполненные spans
    full    [2]spanSet   // [0] = swept, [1] = unswept
}
```

**Зачем нужен mcentral?**

Без mcentral:
```
mcache P0 ──┐
mcache P1 ──┼──► mheap (глобальная блокировка!)
mcache P2 ──┘
```

С mcentral:
```
mcache P0 ──► mcentral[class] ──┐
mcache P1 ──► mcentral[class] ──┼──► mheap
mcache P2 ──► mcentral[class] ──┘
                   ▲
            частичная блокировка
            (только для одного size class)
```

### 6.2 Partial и Full span списки

```
mcentral для size class 32
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  partial[swept]:     spans с свободными слотами             │
│  ┌─────┐   ┌─────┐   ┌─────┐                                │
│  │span1│──►│span2│──►│span3│                                │
│  │50%  │   │25%  │   │75%  │                                │
│  └─────┘   └─────┘   └─────┘                                │
│                                                              │
│  full[swept]:        полностью заполненные spans            │
│  ┌─────┐   ┌─────┐                                          │
│  │span4│──►│span5│                                          │
│  │100% │   │100% │                                          │
│  └─────┘   └─────┘                                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Операции mcentral**:

```go
// Получение span для mcache
func (c *mcentral) cacheSpan() *mspan {
    // 1. Пробуем взять из partial[swept]
    if s := c.partial[swept].pop(); s != nil {
        return s
    }

    // 2. Пробуем взять и sweep из partial[unswept]
    if s := c.partial[unswept].pop(); s != nil {
        s.sweep(true)  // Sweep перед использованием
        return s
    }

    // 3. Пробуем full[unswept] (могут освободиться объекты после sweep)
    if s := c.full[unswept].pop(); s != nil {
        s.sweep(true)
        if s.allocCount < s.nelems {
            return s  // После sweep появились свободные слоты
        }
        c.full[swept].push(s)  // Всё ещё полон
    }

    // 4. Запрашиваем новый span у mheap
    return c.grow()
}

// Возврат span от mcache
func (c *mcentral) uncacheSpan(s *mspan) {
    if s.allocCount == 0 {
        // Span пуст — возвращаем в mheap
        mheap_.freeSpan(s)
        return
    }

    if s.allocCount < s.nelems {
        // Есть свободные слоты
        c.partial[swept].push(s)
    } else {
        // Полностью заполнен
        c.full[swept].push(s)
    }
}
```

---

## 7. mcache: Per-P кеш

### 7.1 Связь с P (Processor)

**mcache** — локальный кеш, привязанный к P (не к потоку!). Аллокация из mcache не требует блокировок.

```go
// runtime/mcache.go (упрощённо)
type mcache struct {
    // Spans для каждого size class
    alloc [numSpanClasses]*mspan

    // Tiny allocator (для объектов < 16 bytes)
    tiny       uintptr  // Адрес текущего tiny block
    tinyoffset uintptr  // Смещение в tiny block
    tinyAllocs uintptr  // Количество tiny аллокаций

    // Статистика
    local_largefree  uintptr  // Освобождено large объектов
    local_nlargefree uintptr  // Количество освобождённых large
    local_nsmallfree [67]uintptr  // Освобождено small объектов по классам
}
```

**Связь P ↔ mcache**:

```go
// runtime/proc.go
type p struct {
    // ...
    mcache *mcache  // Локальный кеш памяти
    // ...
}

// Получение mcache для текущей горутины
func getMCache() *mcache {
    return getg().m.p.ptr().mcache
}
```

```
┌─────────────────────────────────────────────────────────────┐
│                         GMP Model                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Goroutine ──► M (OS Thread) ──► P (Processor)              │
│                                     │                        │
│                                     ▼                        │
│                              ┌──────────┐                   │
│                              │  mcache  │                   │
│                              │ alloc[67]│                   │
│                              │   tiny   │                   │
│                              └──────────┘                   │
│                                                              │
│  • mcache привязан к P, а не к M                            │
│  • Горутина на P аллоцирует из mcache этого P               │
│  • Нет блокировок — только один P имеет доступ              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Tiny allocator

**Tiny allocator** — специальная оптимизация для очень маленьких объектов (< 16 bytes), не содержащих указателей.

```go
// Примеры tiny объектов:
var a int8   // 1 byte
var b int16  // 2 bytes
var c bool   // 1 byte
// Все три могут быть упакованы в один 16-byte блок!
```

**Как работает tiny allocator**:

```
Без tiny allocator (каждый объект в своём слоте):
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│ 1B  │ 2B  │ 1B  │     │     │     │     │     │  ← 3 слота по 16B = 48B
│ ███ │ ███ │ ███ │     │     │     │     │     │     (потеря 44B!)
└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
  slot   slot   slot

С tiny allocator (объекты упакованы):
┌─────────────────────────────────────────────────┐
│ ███ ███ ███ │                                   │  ← 1 блок 16B
│ 1B  2B  1B  │      tiny block (16 bytes)        │     (потеря 12B)
└─────────────────────────────────────────────────┘
     offset: 0  1  3  4
```

```go
// Аллокация tiny объекта (упрощённо)
func mallocgc(size uintptr, typ *_type, needzero bool) unsafe.Pointer {
    if size <= maxTinySize && noscan(typ) {
        c := getMCache()

        // Пробуем упаковать в текущий tiny block
        off := c.tinyoffset
        if off+size <= maxTinySize {
            // Есть место — используем
            x := unsafe.Pointer(c.tiny + off)
            c.tinyoffset = alignUp(off+size, 2)  // Выравнивание на 2
            c.tinyAllocs++
            return x
        }

        // Нет места — аллоцируем новый tiny block
        s := c.alloc[tinySpanClass]
        // ... получаем новый слот из span ...
        c.tiny = uintptr(v)
        c.tinyoffset = size
    }

    // Обычная аллокация для больших объектов
    // ...
}
```

> 💡 **Оптимизация**: Tiny allocator экономит до 87.5% памяти для мелких объектов (1 byte в 16-byte слоте → 6.25% использования, но с tiny упаковкой несколько объектов делят один слот).

### 7.3 Сравнение с .NET Thread allocation context

| Аспект | Go mcache | .NET Thread Allocation Context |
|--------|-----------|-------------------------------|
| **Привязка** | К P (Processor) | К потоку |
| **Количество** | GOMAXPROCS штук | По количеству потоков |
| **Размер** | ~67 spans (по size class) | Один указатель + лимит |
| **Механизм** | Free list (выбор из span) | Bump pointer (сдвиг указателя) |
| **При исчерпании** | Пополнение из mcentral | Получение нового региона от GC |
| **Фрагментация** | Нет (size classes) | Решается компактированием |

**C# allocation context**:
```csharp
// .NET (концептуально)
// Каждый поток имеет:
class ThreadAllocationContext {
    IntPtr alloc_ptr;    // Текущий указатель
    IntPtr alloc_limit;  // Конец региона
}

// Аллокация:
if (alloc_ptr + size <= alloc_limit) {
    var result = alloc_ptr;
    alloc_ptr += size;  // Bump pointer
    return result;
} else {
    // Запрос нового региона у GC
}
```

**Go mcache**:
```go
// Go
// Каждый P имеет mcache с spans

// Аллокация:
span := c.alloc[sizeClass]
slot := span.nextFreeIndex()  // Поиск в free list
if slot < span.nelems {
    return span.base() + slot*span.elemsize
} else {
    // Получаем новый span из mcentral
}
```

---

## 8. Size Classes

### 8.1 Что такое size class

**Size class** — фиксированный размер слота в span. Go округляет размер объекта до ближайшего size class.

```
Запрошено: 20 bytes
Size class: 24 bytes (ближайший >= 20)
Потеря: 4 bytes (16.7%)

Запрошено: 100 bytes
Size class: 112 bytes
Потеря: 12 bytes (10.7%)
```

**Почему size classes?**

1. **Нет внешней фрагментации**: все слоты в span одинакового размера
2. **Быстрый поиск**: не нужно искать подходящий блок
3. **Простое освобождение**: слот просто помечается свободным

### 8.2 Таблица size classes в Go

Go использует **67 size classes** (+ 1 для больших объектов):

```go
// runtime/sizeclasses.go (сгенерировано)
// class  bytes/obj  bytes/span  objects  tail waste  max waste
//     1          8        8192     1024           0     87.50%
//     2         16        8192      512           0     43.75%
//     3         24        8192      341           8     29.24%
//     4         32        8192      256           0     21.88%
//     5         48        8192      170          32     31.52%
//     6         64        8192      128           0     23.44%
//     7         80        8192      102          32     19.07%
//     8         96        8192       85          32     15.95%
//     9        112        8192       73          16     13.56%
//    10        128        8192       64           0     11.72%
//    ...
//    66      28672       57344        2           0      4.91%
//    67      32768       32768        1           0     12.50%
```

**Визуализация size classes**:

```
Size class progression (первые 20):
┌────────────────────────────────────────────────────────────────────┐
│ Class │ Size    │ Class │ Size    │ Class │ Size    │ Class │ Size│
├───────┼─────────┼───────┼─────────┼───────┼─────────┼───────┼─────┤
│   1   │    8 B  │   6   │   64 B  │  11   │  144 B  │  16   │ 256B│
│   2   │   16 B  │   7   │   80 B  │  12   │  160 B  │  17   │ 288B│
│   3   │   24 B  │   8   │   96 B  │  13   │  176 B  │  18   │ 320B│
│   4   │   32 B  │   9   │  112 B  │  14   │  192 B  │  19   │ 352B│
│   5   │   48 B  │  10   │  128 B  │  15   │  224 B  │  20   │ 384B│
└────────────────────────────────────────────────────────────────────┘

Прогрессия: ~12.5% между соседними классами
Max waste: ~12.5% (в худшем случае объект 33B → класс 48B)
```

**Получение size class по размеру**:

```go
// runtime/msize.go
func roundupsize(size uintptr) uintptr {
    if size < _MaxSmallSize {
        if size <= smallSizeMax-8 {
            return uintptr(class_to_size[size_to_class8[divRoundUp(size, smallSizeDiv)]])
        } else {
            return uintptr(class_to_size[size_to_class128[divRoundUp(size-smallSizeMax, largeSizeDiv)]])
        }
    }
    // Large allocation (> 32KB)
    return alignUp(size, _PageSize)
}
```

### 8.3 Оптимизация структур под size classes

**Плохо** — структура попадает в больший size class:

```go
// 33 bytes → size class 48 (потеря 31%)
type Bad struct {
    ID        int64     // 8 bytes
    Timestamp int64     // 8 bytes
    Value     float64   // 8 bytes
    Flag      bool      // 1 byte
    Name      [8]byte   // 8 bytes
    // Total: 33 bytes → rounded to 48
}

func BenchmarkBadAlloc(b *testing.B) {
    for i := 0; i < b.N; i++ {
        _ = new(Bad)
    }
}
// BenchmarkBadAlloc-8    50000000    25.3 ns/op    48 B/op    1 allocs/op
```

**Хорошо** — структура точно попадает в size class:

```go
// 32 bytes → size class 32 (потеря 0%)
type Good struct {
    ID        int64     // 8 bytes
    Timestamp int64     // 8 bytes
    Value     float64   // 8 bytes
    Flag      bool      // 1 byte
    _         [7]byte   // 7 bytes padding (явный)
    // Total: 32 bytes → exact fit
}

// Или реорганизуем поля:
type Better struct {
    ID        int64     // 8 bytes
    Timestamp int64     // 8 bytes
    Value     float64   // 8 bytes
    Name      [7]byte   // 7 bytes
    Flag      bool      // 1 byte
    // Total: 32 bytes
}

func BenchmarkGoodAlloc(b *testing.B) {
    for i := 0; i < b.N; i++ {
        _ = new(Good)
    }
}
// BenchmarkGoodAlloc-8    50000000    24.1 ns/op    32 B/op    1 allocs/op
```

**Инструмент для анализа**:

```bash
# Установка fieldalignment
go install golang.org/x/tools/go/analysis/passes/fieldalignment/cmd/fieldalignment@latest

# Анализ структур
fieldalignment -fix ./...
```

```go
// fieldalignment подскажет оптимальный порядок полей
// До:
type Unoptimized struct {
    a bool    // 1 byte
    b int64   // 8 bytes (7 bytes padding перед b!)
    c bool    // 1 byte
    d int32   // 4 bytes (3 bytes padding перед d!)
}
// Размер: 24 bytes (много padding)

// После fieldalignment -fix:
type Optimized struct {
    b int64   // 8 bytes
    d int32   // 4 bytes
    a bool    // 1 byte
    c bool    // 1 byte
    // 2 bytes padding в конце
}
// Размер: 16 bytes
```

---

## 9. Путь аллокации: от new() до памяти

### 9.1 mallocgc() пошагово

**mallocgc** — центральная функция аллокации в Go runtime.

```go
// runtime/malloc.go (упрощённо)
func mallocgc(size uintptr, typ *_type, needzero bool) unsafe.Pointer {
    // 1. Проверка на нулевой размер
    if size == 0 {
        return unsafe.Pointer(&zerobase)
    }

    // 2. Получаем mcache текущего P
    c := getMCache()

    // 3. Выбираем путь аллокации
    var x unsafe.Pointer
    noscan := typ == nil || !typ.ptrdata

    if size <= maxSmallSize {
        if noscan && size < maxTinySize {
            // Tiny allocation (< 16 bytes, без указателей)
            x = tinyAlloc(c, size)
        } else {
            // Small allocation (16 bytes - 32 KB)
            x = smallAlloc(c, size, noscan)
        }
    } else {
        // Large allocation (> 32 KB)
        x = largeAlloc(size, noscan)
    }

    // 4. Зануление (если нужно)
    if needzero && x != nil {
        memclrNoHeapPointers(x, size)
    }

    // 5. Уведомление GC
    if gcphase != _GCoff {
        gcmarknewobject(x, size)
    }

    return x
}
```

### 9.2 Fast path vs Slow path

```
                        mallocgc(size)
                              │
                              ▼
                    ┌─────────────────────┐
                    │ size <= 32KB ?      │
                    └─────────────────────┘
                         │           │
                        Yes          No
                         │           │
                         ▼           ▼
              ┌──────────────┐  ┌──────────────┐
              │ Small/Tiny   │  │    Large     │
              │  allocation  │  │  allocation  │
              └──────────────┘  └──────────────┘
                    │                  │
                    ▼                  ▼
         ┌────────────────────┐  ┌──────────────┐
         │ mcache.alloc[class]│  │   mheap      │
         │ (FAST PATH)        │  │  (SLOW PATH) │
         └────────────────────┘  └──────────────┘
                    │
            есть свободный слот?
                 │        │
                Yes       No
                 │        │
                 ▼        ▼
         ┌──────────┐  ┌──────────────┐
         │ Готово!  │  │  mcentral    │
         │ (FAST)   │  │ cacheSpan() │
         └──────────┘  └──────────────┘
                              │
                       есть span?
                        │        │
                       Yes       No
                        │        │
                        ▼        ▼
                ┌──────────┐  ┌──────────┐
                │ Готово!  │  │  mheap   │
                │ (MEDIUM) │  │  grow()  │
                └──────────┘  └──────────┘
                                   │
                                   ▼
                            ┌──────────┐
                            │  sysMap  │
                            │  (SLOW)  │
                            └──────────┘
```

**Стоимость каждого пути**:

| Путь | Операция | Примерное время |
|------|----------|-----------------|
| **Fast** | mcache → span → slot | ~25 ns |
| **Medium** | + mcentral.cacheSpan | ~100 ns |
| **Slow** | + mheap.alloc | ~1 μs |
| **Very Slow** | + sysMap (mmap) | ~10 μs |

### 9.3 Tiny, Small и Large аллокации

**Tiny allocation (< 16 bytes, noscan)**:

```go
// Объекты упаковываются в один 16-byte блок
var a int8  = 1  // ─┐
var b int16 = 2  // ─┼─► один tiny block
var c bool  = true // ─┘
```

**Small allocation (16 bytes - 32 KB)**:

```go
// Стандартная аллокация через size classes
type User struct {
    ID   int64
    Name string
    Age  int
}
user := new(User)  // ~40 bytes → size class 48
```

**Large allocation (> 32 KB)**:

```go
// Напрямую из mheap, кратно размеру страницы
data := make([]byte, 100*1024)  // 100 KB → 13 pages (104 KB)
```

```go
// runtime/malloc.go
func largeAlloc(size uintptr, noscan bool) unsafe.Pointer {
    // Округляем до страницы
    npages := size >> pageShift
    if size&(pageSize-1) != 0 {
        npages++
    }

    // Выделяем span напрямую из mheap
    s := mheap_.alloc(npages, makeSpanClass(0, noscan))

    return unsafe.Pointer(s.base())
}
```

---

## 10. Диагностика и мониторинг

### 10.1 runtime.MemStats детально

**MemStats** — основной источник информации о памяти.

```go
package main

import (
    "fmt"
    "runtime"
)

func printMemStats() {
    var m runtime.MemStats
    runtime.ReadMemStats(&m)

    fmt.Println("=== Общая информация ===")
    fmt.Printf("Alloc:       %d MB (текущий heap)\n", m.Alloc/1024/1024)
    fmt.Printf("TotalAlloc:  %d MB (всего аллоцировано за время работы)\n", m.TotalAlloc/1024/1024)
    fmt.Printf("Sys:         %d MB (всего получено от ОС)\n", m.Sys/1024/1024)
    fmt.Printf("NumGC:       %d (количество GC циклов)\n", m.NumGC)

    fmt.Println("\n=== Heap ===")
    fmt.Printf("HeapAlloc:   %d MB (живые объекты)\n", m.HeapAlloc/1024/1024)
    fmt.Printf("HeapSys:     %d MB (получено от ОС для heap)\n", m.HeapSys/1024/1024)
    fmt.Printf("HeapIdle:    %d MB (неиспользуемые spans)\n", m.HeapIdle/1024/1024)
    fmt.Printf("HeapInuse:   %d MB (используемые spans)\n", m.HeapInuse/1024/1024)
    fmt.Printf("HeapReleased:%d MB (возвращено ОС)\n", m.HeapReleased/1024/1024)
    fmt.Printf("HeapObjects: %d (количество объектов)\n", m.HeapObjects)

    fmt.Println("\n=== Структуры аллокатора ===")
    fmt.Printf("MSpanInuse:  %d KB (память для mspan структур)\n", m.MSpanInuse/1024)
    fmt.Printf("MSpanSys:    %d KB (получено от ОС для mspan)\n", m.MSpanSys/1024)
    fmt.Printf("MCacheInuse: %d KB (память для mcache)\n", m.MCacheInuse/1024)
    fmt.Printf("MCacheSys:   %d KB (получено от ОС для mcache)\n", m.MCacheSys/1024)

    fmt.Println("\n=== Аллокации по размерам ===")
    for i, count := range m.BySize {
        if count.Mallocs > 0 {
            fmt.Printf("Size %5d: mallocs=%d, frees=%d, live=%d\n",
                m.BySize[i].Size,
                count.Mallocs,
                count.Frees,
                count.Mallocs-count.Frees)
        }
    }
}
```

**Ключевые метрики для мониторинга**:

| Метрика | Описание | Что смотреть |
|---------|----------|--------------|
| `HeapAlloc` | Живые объекты | Должно быть стабильным |
| `HeapSys` | Всего heap памяти | Рост = возможная утечка |
| `HeapIdle` | Неиспользуемые spans | Высокое значение = фрагментация |
| `HeapReleased` | Возвращено ОС | Должно расти при idle |
| `NumGC` | Количество GC | Частота GC |
| `PauseTotalNs` | Суммарные паузы GC | Влияние на latency |

### 10.2 GODEBUG флаги

**Отладка аллокатора**:

```bash
# Трассировка каждой аллокации и освобождения
GODEBUG=allocfreetrace=1 ./myapp

# Вывод:
# tracealloc(0xc0000a0000, 0x18, main.User)
# tracefree(0xc0000a0000, 0x18)

# Статистика планировщика и памяти каждые 5 секунд
GODEBUG=schedtrace=5000,gctrace=1 ./myapp

# Вывод GC:
# gc 1 @0.012s 2%: 0.018+1.2+0.019 ms clock, 0.14+0.25/1.0/0+0.15 ms cpu, 4->4->1 MB, 5 MB goal, 8 P
#    │    │    │   │                    │                           │           │         │
#    │    │    │   │                    │                           │           │         └─ P count
#    │    │    │   │                    │                           │           └─ Target heap
#    │    │    │   │                    │                           └─ Heap: before→after→live
#    │    │    │   │                    └─ CPU time (assist/bg/idle)
#    │    │    │   └─ Wall clock time (sweep+mark+mark term)
#    │    │    └─ CPU % spent in GC
#    │    └─ Time since start
#    └─ GC number
```

**Полезные GODEBUG флаги для памяти**:

```bash
# Проверка double-free
GODEBUG=invalidptr=1 ./myapp

# Отключение возврата памяти ОС (для отладки)
GODEBUG=madvdontneed=0 ./myapp

# Дополнительные проверки scavenger
GODEBUG=scavtrace=1 ./myapp
```

### 10.3 pprof визуализация

**Heap profile**:

```go
import (
    "net/http"
    _ "net/http/pprof"
)

func main() {
    go func() {
        http.ListenAndServe("localhost:6060", nil)
    }()

    // ... ваш код ...
}
```

```bash
# Heap в использовании
go tool pprof http://localhost:6060/debug/pprof/heap

# Все аллокации (включая освобождённые)
go tool pprof http://localhost:6060/debug/pprof/allocs

# Интерактивные команды:
(pprof) top          # Топ потребителей памяти
(pprof) list main.   # Построчный анализ функций main.*
(pprof) web          # Визуализация в браузере
(pprof) tree         # Дерево вызовов
```

**Сравнение с .NET**:

```csharp
// C#: аналогичный анализ через dotMemory или PerfView
// Heap snapshot
// Allocation recording
// Object retention graph
```

---

## Практические примеры

### Пример 1: Анализ size class через benchmark

```go
package main

import (
    "testing"
    "unsafe"
)

// Структуры разных размеров
type Size31 struct{ data [31]byte }   // 31 → class 32
type Size32 struct{ data [32]byte }   // 32 → class 32 (ideal)
type Size33 struct{ data [33]byte }   // 33 → class 48 (waste!)

func BenchmarkAlloc31(b *testing.B) {
    for i := 0; i < b.N; i++ {
        _ = new(Size31)
    }
}

func BenchmarkAlloc32(b *testing.B) {
    for i := 0; i < b.N; i++ {
        _ = new(Size32)
    }
}

func BenchmarkAlloc33(b *testing.B) {
    for i := 0; i < b.N; i++ {
        _ = new(Size33)
    }
}

func TestSizes(t *testing.T) {
    t.Logf("Size31: %d bytes", unsafe.Sizeof(Size31{}))
    t.Logf("Size32: %d bytes", unsafe.Sizeof(Size32{}))
    t.Logf("Size33: %d bytes", unsafe.Sizeof(Size33{}))
}
```

```bash
go test -bench=. -benchmem

# Результат:
# BenchmarkAlloc31-8    50000000    24.2 ns/op    32 B/op    1 allocs/op
# BenchmarkAlloc32-8    50000000    24.1 ns/op    32 B/op    1 allocs/op
# BenchmarkAlloc33-8    50000000    25.3 ns/op    48 B/op    1 allocs/op
#                                                  ^^
#                                     Size33 использует 48B вместо 33B!
```

### Пример 2: Мониторинг аллокатора в runtime

```go
package main

import (
    "fmt"
    "runtime"
    "time"
)

func monitorAllocator(interval time.Duration) {
    var prevStats runtime.MemStats
    runtime.ReadMemStats(&prevStats)

    ticker := time.NewTicker(interval)
    defer ticker.Stop()

    for range ticker.C {
        var m runtime.MemStats
        runtime.ReadMemStats(&m)

        // Дельта с предыдущим измерением
        allocRate := float64(m.TotalAlloc-prevStats.TotalAlloc) / interval.Seconds()

        fmt.Printf("[Allocator] HeapInuse: %d MB, HeapIdle: %d MB, "+
            "AllocRate: %.2f MB/s, Objects: %d\n",
            m.HeapInuse/1024/1024,
            m.HeapIdle/1024/1024,
            allocRate/1024/1024,
            m.HeapObjects)

        // Эффективность использования spans
        if m.HeapInuse > 0 {
            efficiency := float64(m.HeapAlloc) / float64(m.HeapInuse) * 100
            fmt.Printf("[Efficiency] %.1f%% (HeapAlloc/HeapInuse)\n", efficiency)
        }

        prevStats = m
    }
}

func main() {
    go monitorAllocator(2 * time.Second)

    // Симуляция нагрузки
    var data [][]byte
    for i := 0; i < 100; i++ {
        data = append(data, make([]byte, 1024*1024)) // 1 MB
        time.Sleep(100 * time.Millisecond)
    }

    // Освобождаем
    data = nil
    runtime.GC()

    time.Sleep(10 * time.Second)
}
```

### Пример 3: Prometheus метрики аллокатора

```go
package main

import (
    "net/http"
    "runtime"

    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
    heapAllocGauge = prometheus.NewGauge(prometheus.GaugeOpts{
        Name: "go_heap_alloc_bytes",
        Help: "Current heap allocation in bytes",
    })

    heapIdleGauge = prometheus.NewGauge(prometheus.GaugeOpts{
        Name: "go_heap_idle_bytes",
        Help: "Heap memory not in use",
    })

    heapInuseGauge = prometheus.NewGauge(prometheus.GaugeOpts{
        Name: "go_heap_inuse_bytes",
        Help: "Heap memory in use",
    })

    heapObjectsGauge = prometheus.NewGauge(prometheus.GaugeOpts{
        Name: "go_heap_objects",
        Help: "Number of heap objects",
    })

    mspanInuseGauge = prometheus.NewGauge(prometheus.GaugeOpts{
        Name: "go_mspan_inuse_bytes",
        Help: "Memory used by mspan structures",
    })

    mcacheInuseGauge = prometheus.NewGauge(prometheus.GaugeOpts{
        Name: "go_mcache_inuse_bytes",
        Help: "Memory used by mcache structures",
    })
)

func init() {
    prometheus.MustRegister(heapAllocGauge)
    prometheus.MustRegister(heapIdleGauge)
    prometheus.MustRegister(heapInuseGauge)
    prometheus.MustRegister(heapObjectsGauge)
    prometheus.MustRegister(mspanInuseGauge)
    prometheus.MustRegister(mcacheInuseGauge)
}

func updateMetrics() {
    var m runtime.MemStats
    runtime.ReadMemStats(&m)

    heapAllocGauge.Set(float64(m.HeapAlloc))
    heapIdleGauge.Set(float64(m.HeapIdle))
    heapInuseGauge.Set(float64(m.HeapInuse))
    heapObjectsGauge.Set(float64(m.HeapObjects))
    mspanInuseGauge.Set(float64(m.MSpanInuse))
    mcacheInuseGauge.Set(float64(m.MCacheInuse))
}

func main() {
    // Периодическое обновление метрик
    go func() {
        for {
            updateMetrics()
            time.Sleep(time.Second)
        }
    }()

    http.Handle("/metrics", promhttp.Handler())
    http.ListenAndServe(":9090", nil)
}
```

---

## Чек-лист

После изучения этого раздела вы должны понимать:

- [ ] Разницу между virtual memory и physical memory
- [ ] Что такое page и page fault
- [ ] Архитектуру Go аллокатора: mheap → mcentral → mcache
- [ ] Как работает mspan и что такое size class
- [ ] Роль mcache в lock-free аллокации
- [ ] Как tiny allocator экономит память
- [ ] Путь аллокации: fast path vs slow path
- [ ] Как оптимизировать структуры под size classes
- [ ] Как использовать runtime.MemStats для мониторинга
- [ ] Как применять GODEBUG флаги для отладки

---

## Следующие шаги

Переходите к [2.3 Сборка мусора (GC)](03_gc.md) для понимания того, как Go освобождает память.

---

**Вопросы?** Открой issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Назад: Go Runtime и планировщик](02_runtime_scheduler.md) | [Вперёд: Сборка мусора →](03_gc.md)
