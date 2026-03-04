# 2.7 Профилирование и оптимизация

## Содержание

- [Введение](#%D0%B2%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5)
  - [Сравнительная таблица: .NET Profiling vs Go Profiling](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F-%D1%82%D0%B0%D0%B1%D0%BB%D0%B8%D1%86%D0%B0-net-profiling-vs-go-profiling)
  - [Золотое правило профилирования](#%D0%B7%D0%BE%D0%BB%D0%BE%D1%82%D0%BE%D0%B5-%D0%BF%D1%80%D0%B0%D0%B2%D0%B8%D0%BB%D0%BE-%D0%BF%D1%80%D0%BE%D1%84%D0%B8%D0%BB%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F)
- [1. pprof: CPU профилирование](#1-pprof-cpu-%D0%BF%D1%80%D0%BE%D1%84%D0%B8%D0%BB%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5)
  - [1.1 Как работает CPU sampling](#11-%D0%BA%D0%B0%D0%BA-%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%B0%D0%B5%D1%82-cpu-sampling)
  - [1.2 Подключение pprof к приложению](#12-%D0%BF%D0%BE%D0%B4%D0%BA%D0%BB%D1%8E%D1%87%D0%B5%D0%BD%D0%B8%D0%B5-pprof-%D0%BA-%D0%BF%D1%80%D0%B8%D0%BB%D0%BE%D0%B6%D0%B5%D0%BD%D0%B8%D1%8E)
    - [Способ 1: HTTP endpoint (рекомендуется для серверов)](#%D1%81%D0%BF%D0%BE%D1%81%D0%BE%D0%B1-1-http-endpoint-%D1%80%D0%B5%D0%BA%D0%BE%D0%BC%D0%B5%D0%BD%D0%B4%D1%83%D0%B5%D1%82%D1%81%D1%8F-%D0%B4%D0%BB%D1%8F-%D1%81%D0%B5%D1%80%D0%B2%D0%B5%D1%80%D0%BE%D0%B2)
    - [Способ 2: Программный сбор (для CLI, benchmarks)](#%D1%81%D0%BF%D0%BE%D1%81%D0%BE%D0%B1-2-%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%BD%D1%8B%D0%B9-%D1%81%D0%B1%D0%BE%D1%80-%D0%B4%D0%BB%D1%8F-cli-benchmarks)
    - [Способ 3: Профилирование benchmarks (самый простой)](#%D1%81%D0%BF%D0%BE%D1%81%D0%BE%D0%B1-3-%D0%BF%D1%80%D0%BE%D1%84%D0%B8%D0%BB%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5-benchmarks-%D1%81%D0%B0%D0%BC%D1%8B%D0%B9-%D0%BF%D1%80%D0%BE%D1%81%D1%82%D0%BE%D0%B9)
  - [1.3 Сбор CPU профиля](#13-%D1%81%D0%B1%D0%BE%D1%80-cpu-%D0%BF%D1%80%D0%BE%D1%84%D0%B8%D0%BB%D1%8F)
    - [Через HTTP endpoint](#%D1%87%D0%B5%D1%80%D0%B5%D0%B7-http-endpoint)
    - [Минимальное время сбора](#%D0%BC%D0%B8%D0%BD%D0%B8%D0%BC%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE%D0%B5-%D0%B2%D1%80%D0%B5%D0%BC%D1%8F-%D1%81%D0%B1%D0%BE%D1%80%D0%B0)
  - [1.4 Анализ профиля: интерактивный режим](#14-%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7-%D0%BF%D1%80%D0%BE%D1%84%D0%B8%D0%BB%D1%8F-%D0%B8%D0%BD%D1%82%D0%B5%D1%80%D0%B0%D0%BA%D1%82%D0%B8%D0%B2%D0%BD%D1%8B%D0%B9-%D1%80%D0%B5%D0%B6%D0%B8%D0%BC)
    - [`top` — топ функций по времени](#top--%D1%82%D0%BE%D0%BF-%D1%84%D1%83%D0%BD%D0%BA%D1%86%D0%B8%D0%B9-%D0%BF%D0%BE-%D0%B2%D1%80%D0%B5%D0%BC%D0%B5%D0%BD%D0%B8)
    - [`top -cum` — топ по cumulative time](#top--cum--%D1%82%D0%BE%D0%BF-%D0%BF%D0%BE-cumulative-time)
    - [`list` — исходный код с аннотациями](#list--%D0%B8%D1%81%D1%85%D0%BE%D0%B4%D0%BD%D1%8B%D0%B9-%D0%BA%D0%BE%D0%B4-%D1%81-%D0%B0%D0%BD%D0%BD%D0%BE%D1%82%D0%B0%D1%86%D0%B8%D1%8F%D0%BC%D0%B8)
    - [`web` — визуализация в браузере](#web--%D0%B2%D0%B8%D0%B7%D1%83%D0%B0%D0%BB%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-%D0%B2-%D0%B1%D1%80%D0%B0%D1%83%D0%B7%D0%B5%D1%80%D0%B5)
  - [1.5 Flame Graphs](#15-flame-graphs)
  - [1.6 Типичные CPU bottlenecks](#16-%D1%82%D0%B8%D0%BF%D0%B8%D1%87%D0%BD%D1%8B%D0%B5-cpu-bottlenecks)
    - [1. Избыточные аллокации (GC pressure)](#1-%D0%B8%D0%B7%D0%B1%D1%8B%D1%82%D0%BE%D1%87%D0%BD%D1%8B%D0%B5-%D0%B0%D0%BB%D0%BB%D0%BE%D0%BA%D0%B0%D1%86%D0%B8%D0%B8-gc-pressure)
    - [2. Конкатенация строк](#2-%D0%BA%D0%BE%D0%BD%D0%BA%D0%B0%D1%82%D0%B5%D0%BD%D0%B0%D1%86%D0%B8%D1%8F-%D1%81%D1%82%D1%80%D0%BE%D0%BA)
    - [3. JSON marshaling/unmarshaling](#3-json-marshalingunmarshaling)
    - [4. Reflection](#4-reflection)
    - [5. Mutex contention](#5-mutex-contention)
    - [6. Регулярные выражения](#6-%D1%80%D0%B5%D0%B3%D1%83%D0%BB%D1%8F%D1%80%D0%BD%D1%8B%D0%B5-%D0%B2%D1%8B%D1%80%D0%B0%D0%B6%D0%B5%D0%BD%D0%B8%D1%8F)
- [2. go tool trace: расширенный анализ](#2-go-tool-trace-%D1%80%D0%B0%D1%81%D1%88%D0%B8%D1%80%D0%B5%D0%BD%D0%BD%D1%8B%D0%B9-%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7)
  - [2.1 Когда использовать trace vs pprof](#21-%D0%BA%D0%BE%D0%B3%D0%B4%D0%B0-%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D1%8C-trace-vs-pprof)
  - [2.2 Сбор и визуализация trace](#22-%D1%81%D0%B1%D0%BE%D1%80-%D0%B8-%D0%B2%D0%B8%D0%B7%D1%83%D0%B0%D0%BB%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-trace)
    - [Способ 1: Через тесты](#%D1%81%D0%BF%D0%BE%D1%81%D0%BE%D0%B1-1-%D1%87%D0%B5%D1%80%D0%B5%D0%B7-%D1%82%D0%B5%D1%81%D1%82%D1%8B)
    - [Способ 2: Программно](#%D1%81%D0%BF%D0%BE%D1%81%D0%BE%D0%B1-2-%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%BD%D0%BE)
    - [Способ 3: Через HTTP endpoint](#%D1%81%D0%BF%D0%BE%D1%81%D0%BE%D0%B1-3-%D1%87%D0%B5%D1%80%D0%B5%D0%B7-http-endpoint)
    - [Способ 4: User-defined tasks и regions (Go 1.11+)](#%D1%81%D0%BF%D0%BE%D1%81%D0%BE%D0%B1-4-user-defined-tasks-%D0%B8-regions-go-111)
  - [2.3 Анализ Goroutine Analysis](#23-%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7-goroutine-analysis)
  - [2.4 Диагностика latency spikes](#24-%D0%B4%D0%B8%D0%B0%D0%B3%D0%BD%D0%BE%D1%81%D1%82%D0%B8%D0%BA%D0%B0-latency-spikes)
    - [Причина 1: GC паузы (STW)](#%D0%BF%D1%80%D0%B8%D1%87%D0%B8%D0%BD%D0%B0-1-gc-%D0%BF%D0%B0%D1%83%D0%B7%D1%8B-stw)
    - [Причина 2: Блокировка на mutex](#%D0%BF%D1%80%D0%B8%D1%87%D0%B8%D0%BD%D0%B0-2-%D0%B1%D0%BB%D0%BE%D0%BA%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D0%B0-%D0%BD%D0%B0-mutex)
    - [Причина 3: Медленные syscalls (I/O)](#%D0%BF%D1%80%D0%B8%D1%87%D0%B8%D0%BD%D0%B0-3-%D0%BC%D0%B5%D0%B4%D0%BB%D0%B5%D0%BD%D0%BD%D1%8B%D0%B5-syscalls-io)
    - [Причина 4: Scheduler latency](#%D0%BF%D1%80%D0%B8%D1%87%D0%B8%D0%BD%D0%B0-4-scheduler-latency)
- [3. Комплексный workflow профилирования](#3-%D0%BA%D0%BE%D0%BC%D0%BF%D0%BB%D0%B5%D0%BA%D1%81%D0%BD%D1%8B%D0%B9-workflow-%D0%BF%D1%80%D0%BE%D1%84%D0%B8%D0%BB%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F)
  - [3.1 Методология: Measure → Identify → Optimize → Verify](#31-%D0%BC%D0%B5%D1%82%D0%BE%D0%B4%D0%BE%D0%BB%D0%BE%D0%B3%D0%B8%D1%8F-measure-%E2%86%92-identify-%E2%86%92-optimize-%E2%86%92-verify)
    - [Шаг 1: Measure (Измерение)](#%D1%88%D0%B0%D0%B3-1-measure-%D0%B8%D0%B7%D0%BC%D0%B5%D1%80%D0%B5%D0%BD%D0%B8%D0%B5)
    - [Шаг 2: Identify (Идентификация)](#%D1%88%D0%B0%D0%B3-2-identify-%D0%B8%D0%B4%D0%B5%D0%BD%D1%82%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%86%D0%B8%D1%8F)
    - [Шаг 3: Optimize (Оптимизация)](#%D1%88%D0%B0%D0%B3-3-optimize-%D0%BE%D0%BF%D1%82%D0%B8%D0%BC%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F)
    - [Шаг 4: Verify (Верификация)](#%D1%88%D0%B0%D0%B3-4-verify-%D0%B2%D0%B5%D1%80%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%86%D0%B8%D1%8F)
  - [3.2 Выбор инструмента по типу проблемы](#32-%D0%B2%D1%8B%D0%B1%D0%BE%D1%80-%D0%B8%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D0%B0-%D0%BF%D0%BE-%D1%82%D0%B8%D0%BF%D1%83-%D0%BF%D1%80%D0%BE%D0%B1%D0%BB%D0%B5%D0%BC%D1%8B)
  - [3.3 Интеграция с CI/CD](#33-%D0%B8%D0%BD%D1%82%D0%B5%D0%B3%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D1%81-cicd)
    - [GitHub Actions: Benchmark на каждый PR](#github-actions-benchmark-%D0%BD%D0%B0-%D0%BA%D0%B0%D0%B6%D0%B4%D1%8B%D0%B9-pr)
    - [Пример с регрессией:](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-%D1%81-%D1%80%D0%B5%D0%B3%D1%80%D0%B5%D1%81%D1%81%D0%B8%D0%B5%D0%B9)
    - [Сбор профилей в production (опционально)](#%D1%81%D0%B1%D0%BE%D1%80-%D0%BF%D1%80%D0%BE%D1%84%D0%B8%D0%BB%D0%B5%D0%B9-%D0%B2-production-%D0%BE%D0%BF%D1%86%D0%B8%D0%BE%D0%BD%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE)
- [4. Оптимизация production-кода](#4-%D0%BE%D0%BF%D1%82%D0%B8%D0%BC%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-production-%D0%BA%D0%BE%D0%B4%D0%B0)
  - [4.1 Hot paths и закон Амдала](#41-hot-paths-%D0%B8-%D0%B7%D0%B0%D0%BA%D0%BE%D0%BD-%D0%B0%D0%BC%D0%B4%D0%B0%D0%BB%D0%B0)
  - [4.2 Оптимизация строковых операций](#42-%D0%BE%D0%BF%D1%82%D0%B8%D0%BC%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-%D1%81%D1%82%D1%80%D0%BE%D0%BA%D0%BE%D0%B2%D1%8B%D1%85-%D0%BE%D0%BF%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D0%B9)
    - [Конкатенация строк](#%D0%BA%D0%BE%D0%BD%D0%BA%D0%B0%D1%82%D0%B5%D0%BD%D0%B0%D1%86%D0%B8%D1%8F-%D1%81%D1%82%D1%80%D0%BE%D0%BA)
    - [Сравнение с C#](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81-c)
  - [4.3 Оптимизация JSON](#43-%D0%BE%D0%BF%D1%82%D0%B8%D0%BC%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-json)
    - [Стандартная библиотека](#%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D0%B0%D1%8F-%D0%B1%D0%B8%D0%B1%D0%BB%D0%B8%D0%BE%D1%82%D0%B5%D0%BA%D0%B0)
    - [Альтернативы (по скорости)](#%D0%B0%D0%BB%D1%8C%D1%82%D0%B5%D1%80%D0%BD%D0%B0%D1%82%D0%B8%D0%B2%D1%8B-%D0%BF%D0%BE-%D1%81%D0%BA%D0%BE%D1%80%D0%BE%D1%81%D1%82%D0%B8)
    - [easyjson — code generation](#easyjson--code-generation)
    - [Сравнение с C#](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81-c-1)
  - [4.4 Избегание interface{} в hot paths](#44-%D0%B8%D0%B7%D0%B1%D0%B5%D0%B3%D0%B0%D0%BD%D0%B8%D0%B5-interface-%D0%B2-hot-paths)
    - [Type switch как альтернатива](#type-switch-%D0%BA%D0%B0%D0%BA-%D0%B0%D0%BB%D1%8C%D1%82%D0%B5%D1%80%D0%BD%D0%B0%D1%82%D0%B8%D0%B2%D0%B0)
  - [4.5 Preallocations и переиспользование](#45-preallocations-%D0%B8-%D0%BF%D0%B5%D1%80%D0%B5%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5)
    - [Preallocation слайсов](#preallocation-%D1%81%D0%BB%D0%B0%D0%B9%D1%81%D0%BE%D0%B2)
    - [Preallocation maps](#preallocation-maps)
    - [sync.Pool для переиспользования](#syncpool-%D0%B4%D0%BB%D1%8F-%D0%BF%D0%B5%D1%80%D0%B5%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F)
    - [Сравнение с C#](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81-c-2)
- [5. Continuous Profiling](#5-continuous-profiling)
  - [5.1 Концепция](#51-%D0%BA%D0%BE%D0%BD%D1%86%D0%B5%D0%BF%D1%86%D0%B8%D1%8F)
  - [5.2 Инструменты](#52-%D0%B8%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D1%8B)
  - [5.3 Интеграция с Go приложением](#53-%D0%B8%D0%BD%D1%82%D0%B5%D0%B3%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D1%81-go-%D0%BF%D1%80%D0%B8%D0%BB%D0%BE%D0%B6%D0%B5%D0%BD%D0%B8%D0%B5%D0%BC)
    - [Pyroscope (Open Source)](#pyroscope-open-source)
    - [Google Cloud Profiler](#google-cloud-profiler)
    - [Datadog Continuous Profiler](#datadog-continuous-profiler)
    - [Low-overhead профилирование](#low-overhead-%D0%BF%D1%80%D0%BE%D1%84%D0%B8%D0%BB%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5)
- [5. Новые инструменты профилирования (Go 1.25-1.26)](#5-%D0%BD%D0%BE%D0%B2%D1%8B%D0%B5-%D0%B8%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D1%8B-%D0%BF%D1%80%D0%BE%D1%84%D0%B8%D0%BB%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F-go-125-126)
  - [5.1 runtime/trace.FlightRecorder (Go 1.25)](#51-runtimetraceflightrecorder-go-125)
  - [5.2 Обнаружение утечек горутин (Go 1.26, экспериментально)](#52-%D0%BE%D0%B1%D0%BD%D0%B0%D1%80%D1%83%D0%B6%D0%B5%D0%BD%D0%B8%D0%B5-%D1%83%D1%82%D0%B5%D1%87%D0%B5%D0%BA-%D0%B3%D0%BE%D1%80%D1%83%D1%82%D0%B8%D0%BD-go-126-%D1%8D%D0%BA%D1%81%D0%BF%D0%B5%D1%80%D0%B8%D0%BC%D0%B5%D0%BD%D1%82%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE)
  - [5.3 Новые runtime/metrics в Go 1.26](#53-%D0%BD%D0%BE%D0%B2%D1%8B%D0%B5-runtimemetrics-%D0%B2-go-126)
- [Практические примеры](#%D0%BF%D1%80%D0%B0%D0%BA%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B5-%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80%D1%8B)
  - [Пример 1: Оптимизация HTTP сервиса (end-to-end)](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-1-%D0%BE%D0%BF%D1%82%D0%B8%D0%BC%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-http-%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D0%B0-end-to-end)
    - [Шаг 1: Воспроизвести проблему](#%D1%88%D0%B0%D0%B3-1-%D0%B2%D0%BE%D1%81%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%B2%D0%B5%D1%81%D1%82%D0%B8-%D0%BF%D1%80%D0%BE%D0%B1%D0%BB%D0%B5%D0%BC%D1%83)
    - [Шаг 2: Benchmark](#%D1%88%D0%B0%D0%B3-2-benchmark)
    - [Шаг 3: Анализ профиля](#%D1%88%D0%B0%D0%B3-3-%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7-%D0%BF%D1%80%D0%BE%D1%84%D0%B8%D0%BB%D1%8F)
    - [Шаг 4: Оптимизация](#%D1%88%D0%B0%D0%B3-4-%D0%BE%D0%BF%D1%82%D0%B8%D0%BC%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F)
    - [Шаг 5: Верификация](#%D1%88%D0%B0%D0%B3-5-%D0%B2%D0%B5%D1%80%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%86%D0%B8%D1%8F)
  - [Пример 2: Диагностика memory leak через goroutine leak](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-2-%D0%B4%D0%B8%D0%B0%D0%B3%D0%BD%D0%BE%D1%81%D1%82%D0%B8%D0%BA%D0%B0-memory-leak-%D1%87%D0%B5%D1%80%D0%B5%D0%B7-goroutine-leak)
    - [Симптомы](#%D1%81%D0%B8%D0%BC%D0%BF%D1%82%D0%BE%D0%BC%D1%8B)
    - [Шаг 1: Проверка горутин](#%D1%88%D0%B0%D0%B3-1-%D0%BF%D1%80%D0%BE%D0%B2%D0%B5%D1%80%D0%BA%D0%B0-%D0%B3%D0%BE%D1%80%D1%83%D1%82%D0%B8%D0%BD)
    - [Шаг 2: Анализ кода](#%D1%88%D0%B0%D0%B3-2-%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7-%D0%BA%D0%BE%D0%B4%D0%B0)
    - [Шаг 3: Исправление](#%D1%88%D0%B0%D0%B3-3-%D0%B8%D1%81%D0%BF%D1%80%D0%B0%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5)
    - [Шаг 4: Использование goleak в тестах](#%D1%88%D0%B0%D0%B3-4-%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5-goleak-%D0%B2-%D1%82%D0%B5%D1%81%D1%82%D0%B0%D1%85)
  - [Пример 3: Latency spikes в микросервисе](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-3-latency-spikes-%D0%B2-%D0%BC%D0%B8%D0%BA%D1%80%D0%BE%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D0%B5)
    - [Шаг 1: Сбор trace](#%D1%88%D0%B0%D0%B3-1-%D1%81%D0%B1%D0%BE%D1%80-trace)
    - [Шаг 2: Анализ](#%D1%88%D0%B0%D0%B3-2-%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7)
    - [Шаг 3: Диагностика mutex contention](#%D1%88%D0%B0%D0%B3-3-%D0%B4%D0%B8%D0%B0%D0%B3%D0%BD%D0%BE%D1%81%D1%82%D0%B8%D0%BA%D0%B0-mutex-contention)
    - [Шаг 4: Оптимизация](#%D1%88%D0%B0%D0%B3-4-%D0%BE%D0%BF%D1%82%D0%B8%D0%BC%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-1)
    - [Шаг 5: Диагностика GC](#%D1%88%D0%B0%D0%B3-5-%D0%B4%D0%B8%D0%B0%D0%B3%D0%BD%D0%BE%D1%81%D1%82%D0%B8%D0%BA%D0%B0-gc)
  - [Пример 4: CI/CD pipeline для производительности](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-4-cicd-pipeline-%D0%B4%D0%BB%D1%8F-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%B2%D0%BE%D0%B4%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D0%BE%D1%81%D1%82%D0%B8)
    - [GitHub Actions workflow](#github-actions-workflow)
    - [Результат в PR](#%D1%80%D0%B5%D0%B7%D1%83%D0%BB%D1%8C%D1%82%D0%B0%D1%82-%D0%B2-pr)

---

## Введение

В предыдущих разделах мы изучили отдельные аспекты производительности Go:
- [Раздел 2.3 (GC)](./03_gc.md) — pprof для memory profiling, escape analysis, `GOGC`/`GOMEMLIMIT`
- [Раздел 2.6 (Тестирование)](./06_testing_benchmarking.md) — benchmarks, `benchstat`, race detector

Этот раздел объединяет все инструменты в **единый workflow профилирования** и фокусируется на:
- **CPU профилирование** (основной фокус — не рассматривалось ранее)
- **Комплексная методология** "от симптома к решению"
- **Практические паттерны оптимизации** production-кода
- **Continuous Profiling** для мониторинга в production

> 💡 **Для C# разработчиков**: В .NET экосистеме профилирование обычно требует платных инструментов (dotTrace, dotMemory, ANTS Profiler) или сложной настройки (PerfView, ETW). В Go все инструменты встроены и бесплатны — `pprof`, `go tool trace`, `go test -bench`. Философия та же: **не оптимизируй без данных профилировщика**.

### Сравнительная таблица: .NET Profiling vs Go Profiling

| Аспект | .NET | Go |
|--------|------|-----|
| **CPU Profiling** | Visual Studio Profiler, dotTrace, PerfView | `pprof` CPU profile |
| **Memory Profiling** | dotMemory, PerfView, VS Diagnostic Tools | `pprof` heap/allocs ([раздел 2.3](./03_gc.md)) |
| **Concurrency** | Concurrency Visualizer (VS Enterprise) | `go tool trace` |
| **Benchmarks** | BenchmarkDotNet (NuGet) | `go test -bench` (встроенный) |
| **Race Detection** | Thread Sanitizer (LLVM, внешний) | `go test -race` (встроенный) |
| **Flame Graphs** | PerfView, speedscope | `pprof -http` (встроенный) |
| **Production Profiling** | Application Insights, Datadog | Pyroscope, Cloud Profiler |
| **Стоимость** | Часто платные (dotTrace ~$400/год) | Бесплатно |
| **Интеграция с IDE** | Отличная (VS, Rider) | Базовая (GoLand), CLI-first |

### Золотое правило профилирования

```
╔═══════════════════════════════════════════════════════════════╗
║   "Premature optimization is the root of all evil"           ║
║                                    — Donald Knuth             ║
║                                                               ║
║   НО:                                                         ║
║   "Измерение без оптимизации — потеря времени"               ║
║   "Оптимизация без измерения — гадание на кофейной гуще"     ║
╚═══════════════════════════════════════════════════════════════╝
```

**Правильный подход:**
1. **Measure** — собери данные профилировщика
2. **Identify** — найди bottleneck
3. **Optimize** — измени код
4. **Verify** — подтверди улучшение через benchstat

---

## 1. pprof: CPU профилирование

CPU профилирование — это основной инструмент для ответа на вопрос **"Где моё приложение тратит процессорное время?"**

> 💡 **Связь с другими разделами**: Memory profiling через pprof подробно описан в [разделе 2.3 (GC)](./03_gc.md). Здесь фокусируемся на CPU.

### 1.1 Как работает CPU sampling

Go использует **sampling-based профилирование**:

```
┌─────────────────────────────────────────────────────────────┐
│                   CPU SAMPLING                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Время ──────────────────────────────────────────────►     │
│                                                              │
│   Программа:  ████████░░░░████████████░░░░░░████████        │
│                  ▲         ▲           ▲        ▲           │
│                  │         │           │        │           │
│   Samples:      [1]       [2]         [3]      [4]          │
│                  │         │           │        │           │
│                  ▼         ▼           ▼        ▼           │
│   Stack:     main()   process()   process()   main()        │
│              parse()   compute()  compute()   write()       │
│              read()    math()     math()      flush()       │
│                                                              │
│   Частота: 100 samples/sec (каждые 10ms)                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Как это работает:**
1. Профилировщик каждые ~10ms останавливает выполнение
2. Записывает текущий call stack всех горутин
3. После завершения агрегирует: какие функции чаще всего были на стеке

**Преимущества sampling:**
- Низкий overhead (~5-10%)
- Не искажает поведение программы
- Статистически точен при достаточном времени сбора

**Сравнение с .NET:**

| Аспект | .NET (dotTrace) | Go (pprof) |
|--------|-----------------|------------|
| Метод | Sampling + Tracing | Sampling only |
| Частота | Настраиваемая | 100 Hz (фиксированная) |
| Overhead | 5-50% (зависит от режима) | ~5-10% |
| Line-level | Да (в tracing mode) | Да |

### 1.2 Подключение pprof к приложению

#### Способ 1: HTTP endpoint (рекомендуется для серверов)

```go
package main

import (
    "log"
    "net/http"
    _ "net/http/pprof" // Важно: blank import!
)

func main() {
    // Регистрирует endpoints:
    // /debug/pprof/
    // /debug/pprof/profile     <- CPU profile
    // /debug/pprof/heap        <- Memory profile
    // /debug/pprof/goroutine   <- Goroutine stacks
    // /debug/pprof/block       <- Block profile
    // /debug/pprof/mutex       <- Mutex profile
    // /debug/pprof/trace       <- Execution trace

    // Опция 1: Отдельный порт для pprof (рекомендуется для production)
    go func() {
        log.Println("pprof server: http://localhost:6060/debug/pprof/")
        log.Println(http.ListenAndServe("localhost:6060", nil))
    }()

    // Ваш основной сервер
    mux := http.NewServeMux()
    mux.HandleFunc("/api/users", handleUsers)

    log.Fatal(http.ListenAndServe(":8080", mux))
}
```

> ⚠️ **Безопасность**: Никогда не экспонируйте pprof endpoint в публичный интернет! Он раскрывает внутреннюю структуру приложения и может содержать чувствительные данные в stack traces.

**Защита pprof в production:**

```go
// Вариант 1: Только localhost
http.ListenAndServe("localhost:6060", nil)

// Вариант 2: Middleware с авторизацией
func pprofAuth(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        token := r.Header.Get("X-Pprof-Token")
        if token != os.Getenv("PPROF_TOKEN") {
            http.Error(w, "Unauthorized", http.StatusUnauthorized)
            return
        }
        next.ServeHTTP(w, r)
    })
}
```

#### Способ 2: Программный сбор (для CLI, benchmarks)

```go
package main

import (
    "os"
    "runtime/pprof"
)

func main() {
    // Создаём файл для профиля
    f, err := os.Create("cpu.prof")
    if err != nil {
        panic(err)
    }
    defer f.Close()

    // Начинаем профилирование
    if err := pprof.StartCPUProfile(f); err != nil {
        panic(err)
    }
    defer pprof.StopCPUProfile()

    // Выполняем код, который хотим профилировать
    runExpensiveOperation()
}
```

#### Способ 3: Профилирование benchmarks (самый простой)

```bash
# Запустить benchmark и сохранить CPU профиль
go test -bench=BenchmarkProcess -cpuprofile=cpu.prof

# Также можно собрать memory профиль
go test -bench=BenchmarkProcess -memprofile=mem.prof
```

### 1.3 Сбор CPU профиля

#### Через HTTP endpoint

```bash
# Собрать 30-секундный CPU профиль
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

# Или сохранить в файл
curl -o cpu.prof "http://localhost:6060/debug/pprof/profile?seconds=30"
```

#### Минимальное время сбора

```
┌────────────────────────────────────────────────────────────┐
│              РЕКОМЕНДУЕМОЕ ВРЕМЯ СБОРА                      │
├────────────────────────────────────────────────────────────┤
│                                                             │
│   Сценарий                    │ Время                      │
│   ─────────────────────────────────────────────────        │
│   Benchmark, микро-тест       │ 5-10 секунд                │
│   Типичный production         │ 30 секунд                  │
│   Редкие события              │ 60-120 секунд              │
│   Поиск intermittent issues   │ 5-10 минут                 │
│                                                             │
│   Правило: минимум 1000 samples для статистики             │
│   100 Hz × 30 sec = 3000 samples ✓                         │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### 1.4 Анализ профиля: интерактивный режим

```bash
# Открыть интерактивный режим
go tool pprof cpu.prof
```

**Основные команды:**

#### `top` — топ функций по времени

```
(pprof) top
Showing nodes accounting for 4.5s, 90% of 5s total
      flat  flat%   sum%        cum   cum%
     2.0s 40.00% 40.00%      2.5s 50.00%  main.processData
     1.5s 30.00% 70.00%      1.5s 30.00%  runtime.mallocgc
     0.5s 10.00% 80.00%      3.0s 60.00%  main.handleRequest
     0.3s  6.00% 86.00%      0.3s  6.00%  encoding/json.Marshal
     0.2s  4.00% 90.00%      0.2s  4.00%  runtime.memmove
```

**Что означают колонки:**
- **flat** — время только в этой функции (без вызовов)
- **cum** (cumulative) — общее время (включая вызовы других функций)

```
┌─────────────────────────────────────────────────────────────┐
│                FLAT vs CUM (CUMULATIVE)                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   func A() {           │   flat(A) = 1s (время в самой A)   │
│       // 1s работы     │   cum(A)  = 4s (A + B + C)         │
│       B()              │                                     │
│   }                    │   flat(B) = 2s                      │
│                        │   cum(B)  = 3s (B + C)              │
│   func B() {           │                                     │
│       // 2s работы     │   flat(C) = 1s                      │
│       C()              │   cum(C)  = 1s                      │
│   }                    │                                     │
│                        │                                     │
│   func C() {           │   ⚠️ Высокий flat = код функции     │
│       // 1s работы     │   ⚠️ Высокий cum = функция или      │
│   }                    │      её дочерние вызовы             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### `top -cum` — топ по cumulative time

```
(pprof) top -cum
Showing nodes accounting for 4.5s, 90% of 5s total
      flat  flat%   sum%        cum   cum%
     0.1s  2.00%  2.00%      5.0s   100%  main.main
     0.5s 10.00% 12.00%      3.0s 60.00%  main.handleRequest
     2.0s 40.00% 52.00%      2.5s 50.00%  main.processData
```

#### `list` — исходный код с аннотациями

```
(pprof) list processData
Total: 5s
ROUTINE ======================== main.processData
     2.0s      2.5s (flat, cum) 50.00% of Total
         .          .     15:func processData(data []byte) Result {
         .          .     16:    var result Result
     0.5s      0.5s     17:    for _, b := range data {        // ← 0.5s здесь
     1.0s      1.0s     18:        result.Sum += int(b)        // ← 1.0s здесь
     0.5s      0.5s     19:        result.Count++              // ← 0.5s здесь
         .          .     20:    }
         .      0.5s     21:    result.Normalize()             // ← 0.5s в Normalize
         .          .     22:    return result
         .          .     23:}
```

#### `web` — визуализация в браузере

```bash
(pprof) web
# Открывает граф в браузере (требует graphviz)
```

### 1.5 Flame Graphs

Flame Graph — это самый эффективный способ визуализации CPU профиля.

```bash
# Встроенный веб-интерфейс с flame graph
go tool pprof -http=:8080 cpu.prof
```

**Как читать Flame Graph:**

```
┌─────────────────────────────────────────────────────────────┐
│                      FLAME GRAPH                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                    main.main                         │   │
│   └─────────────────────────────────────────────────────┘   │
│   ┌───────────────────────────┐┌────────────────────────┐   │
│   │     main.handleRequest    ││    main.loadConfig     │   │
│   └───────────────────────────┘└────────────────────────┘   │
│   ┌─────────────┐┌────────────┐                             │
│   │main.process ││ json.Marshal│                            │
│   └─────────────┘└────────────┘                             │
│   ┌───────┐                                                  │
│   │compute│                                                  │
│   └───────┘                                                  │
│                                                              │
│   Ширина = время CPU                                        │
│   Высота = глубина стека                                    │
│   ↑ Кликни на блок = zoom in                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Интерпретация:**
- **Широкие блоки** — много CPU времени, потенциальные bottlenecks
- **Глубокие стеки** — много вызовов функций (возможно, рекурсия)
- **Плоские широкие блоки** — функции с тяжёлыми вычислениями внутри

### 1.6 Типичные CPU bottlenecks

#### 1. Избыточные аллокации (GC pressure)

```go
// ❌ Плохо: аллокация в каждой итерации
func processBad(items []string) []string {
    var result []string  // len=0, cap=0
    for _, item := range items {
        result = append(result, transform(item))  // Grow → allocate
    }
    return result
}

// ✅ Хорошо: preallocation
func processGood(items []string) []string {
    result := make([]string, 0, len(items))  // Preallocate capacity
    for _, item := range items {
        result = append(result, transform(item))  // No reallocation
    }
    return result
}
```

> 💡 **Связь с GC**: Подробнее об аллокациях и escape analysis — [раздел 2.3](./03_gc.md).

#### 2. Конкатенация строк

```go
// ❌ Плохо: O(n²) по памяти
func joinBad(items []string) string {
    result := ""
    for _, s := range items {
        result += s  // Каждый раз новая аллокация!
    }
    return result
}

// ✅ Хорошо: O(n) с strings.Builder
func joinGood(items []string) string {
    var b strings.Builder
    b.Grow(estimatedSize)  // Опционально: preallocate
    for _, s := range items {
        b.WriteString(s)
    }
    return b.String()
}
```

**Сравнение производительности:**

```
BenchmarkJoinBad-8      1000000    15234 ns/op    58320 B/op   999 allocs/op
BenchmarkJoinGood-8    10000000      234 ns/op      512 B/op     1 allocs/op
```

#### 3. JSON marshaling/unmarshaling

```go
// ❌ Плохо: encoding/json использует reflection
import "encoding/json"

func handleRequest(w http.ResponseWriter, r *http.Request) {
    var req Request
    json.NewDecoder(r.Body).Decode(&req)  // Reflection + allocations

    resp := process(req)
    json.NewEncoder(w).Encode(resp)  // Reflection + allocations
}
```

**Альтернативы (по скорости):**

| Библиотека | Скорость vs encoding/json | Особенности |
|------------|---------------------------|-------------|
| `encoding/json` | 1x (baseline) | Стандартная библиотека |
| `json-iterator` | ~3-5x | Drop-in replacement |
| `easyjson` | ~5-7x | Code generation |
| `sonic` | ~10x | SIMD, code gen |
| `goccy/go-json` | ~3-5x | Drop-in, zero-alloc |

```go
// ✅ С easyjson (code generation)
//go:generate easyjson -all types.go

func handleRequestFast(w http.ResponseWriter, r *http.Request) {
    var req Request
    easyjson.UnmarshalFromReader(r.Body, &req)

    resp := process(req)
    easyjson.MarshalToWriter(resp, w)
}
```

#### 4. Reflection

```go
// ❌ Плохо: reflection в hot path
func processBad(v interface{}) {
    rv := reflect.ValueOf(v)
    for i := 0; i < rv.NumField(); i++ {
        field := rv.Field(i)
        // ...
    }
}

// ✅ Хорошо: generics (Go 1.18+)
func processGood[T any](v T) {
    // Type-safe, no reflection
}

// ✅ Или: type switch для известных типов
func processSwitch(v interface{}) {
    switch x := v.(type) {
    case *User:
        processUser(x)
    case *Order:
        processOrder(x)
    }
}
```

#### 5. Mutex contention

```go
// ❌ Плохо: глобальный mutex
var (
    mu    sync.Mutex
    cache = make(map[string]Value)
)

func Get(key string) Value {
    mu.Lock()
    defer mu.Unlock()
    return cache[key]  // Read-only, но блокирует всех
}

// ✅ Хорошо: RWMutex для read-heavy workloads
var (
    mu    sync.RWMutex
    cache = make(map[string]Value)
)

func Get(key string) Value {
    mu.RLock()
    defer mu.RUnlock()
    return cache[key]  // Параллельные чтения
}

// ✅ Ещё лучше: sharded cache
type ShardedCache struct {
    shards [256]struct {
        sync.RWMutex
        data map[string]Value
    }
}

func (c *ShardedCache) getShard(key string) *shard {
    h := fnv.New32a()
    h.Write([]byte(key))
    return &c.shards[h.Sum32()%256]
}
```

> 💡 **Связь с sync**: Подробнее о mutex и contention — [раздел 2.4](./04_sync_primitives.md).

#### 6. Регулярные выражения

```go
// ❌ Плохо: компиляция regex в каждом вызове
func validateBad(email string) bool {
    re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
    return re.MatchString(email)
}

// ✅ Хорошо: компиляция один раз
var emailRegex = regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)

func validateGood(email string) bool {
    return emailRegex.MatchString(email)
}

// ✅ Ещё лучше для простых случаев: strings functions
func validateFast(email string) bool {
    at := strings.Index(email, "@")
    if at == -1 || at == 0 {
        return false
    }
    dot := strings.LastIndex(email[at:], ".")
    return dot > 1 && dot < len(email[at:])-2
}
```

---

## 2. go tool trace: расширенный анализ

`go tool trace` — это инструмент для детального анализа выполнения программы во времени. В отличие от pprof (который показывает агрегированную статистику), trace показывает **что происходило в каждый момент времени**.

> 💡 **Связь с разделом 2.2**: Базовое описание trace для анализа планировщика — в [разделе 2.2 (Runtime)](./02_runtime_scheduler.md). Здесь фокусируемся на практическом применении для диагностики проблем.

### 2.1 Когда использовать trace vs pprof

```
┌─────────────────────────────────────────────────────────────┐
│              PPROF vs TRACE: КОГДА ЧТО ИСПОЛЬЗОВАТЬ         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ВОПРОС                          │ ИНСТРУМЕНТ              │
│   ────────────────────────────────────────────────────────  │
│   "Где тратится CPU время?"       │ pprof CPU               │
│   "Где выделяется память?"        │ pprof heap/allocs       │
│   "Почему горутины блокируются?"  │ go tool trace ✓         │
│   "Почему есть latency spikes?"   │ go tool trace ✓         │
│   "Что делал планировщик?"        │ go tool trace ✓         │
│   "Где mutex contention?"         │ pprof mutex + trace     │
│   "Когда были GC паузы?"          │ go tool trace ✓         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Ключевое отличие:**

| Аспект | pprof | go tool trace |
|--------|-------|---------------|
| **Тип данных** | Агрегированная статистика | Timeline событий |
| **Вопрос** | "Сколько времени в функции X?" | "Что происходило в момент T?" |
| **Overhead** | ~5-10% | ~10-25% |
| **Размер данных** | Килобайты | Мегабайты (10MB/sec) |
| **Визуализация** | Flame graph, text | Timeline в браузере |

**Сравнение с .NET:**

| Go | .NET |
|----|------|
| `go tool trace` | Concurrency Visualizer (VS Enterprise) |
| Бесплатный | $5000+/год (Enterprise лицензия) |
| CLI + браузер | Visual Studio only |

### 2.2 Сбор и визуализация trace

#### Способ 1: Через тесты

```bash
# Запустить тесты и собрать trace
go test -trace=trace.out ./...

# Запустить конкретный benchmark с trace
go test -bench=BenchmarkProcess -trace=trace.out

# Открыть trace в браузере
go tool trace trace.out
```

#### Способ 2: Программно

```go
package main

import (
    "os"
    "runtime/trace"
)

func main() {
    // Создаём файл для trace
    f, err := os.Create("trace.out")
    if err != nil {
        panic(err)
    }
    defer f.Close()

    // Начинаем трассировку
    if err := trace.Start(f); err != nil {
        panic(err)
    }
    defer trace.Stop()

    // Выполняем код
    runApplication()
}
```

#### Способ 3: Через HTTP endpoint

```bash
# Собрать 5-секундный trace
curl -o trace.out "http://localhost:6060/debug/pprof/trace?seconds=5"

# Открыть в браузере
go tool trace trace.out
```

#### Способ 4: User-defined tasks и regions (Go 1.11+)

```go
import "runtime/trace"

func processOrder(ctx context.Context, order Order) error {
    // Создаём task для группировки связанных событий
    ctx, task := trace.NewTask(ctx, "processOrder")
    defer task.End()

    // Region для отдельной фазы
    trace.WithRegion(ctx, "validation", func() {
        validateOrder(order)
    })

    trace.WithRegion(ctx, "payment", func() {
        processPayment(order)
    })

    trace.WithRegion(ctx, "notification", func() {
        sendNotification(order)
    })

    return nil
}
```

### 2.3 Анализ Goroutine Analysis

После открытия `go tool trace trace.out` в браузере, ключевые секции:

```
┌─────────────────────────────────────────────────────────────┐
│                  GO TOOL TRACE: ОСНОВНЫЕ VIEWS              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. View trace                                               │
│     └── Timeline всех событий (горутины, GC, syscalls)      │
│                                                              │
│  2. Goroutine analysis                                       │
│     └── Статистика по горутинам:                            │
│         • Execution time (время выполнения)                 │
│         • Network wait (ожидание сети)                      │
│         • Sync block (блокировка на mutex/channel)          │
│         • Syscall (системные вызовы)                        │
│         • Scheduler wait (ожидание планировщика)            │
│                                                              │
│  3. Network blocking profile                                 │
│     └── Где горутины ждут сеть                              │
│                                                              │
│  4. Synchronization blocking profile                         │
│     └── Где горутины ждут mutex/channel                     │
│                                                              │
│  5. Syscall blocking profile                                 │
│     └── Где горутины ждут syscalls (file I/O, etc.)         │
│                                                              │
│  6. User-defined tasks                                       │
│     └── Ваши trace.NewTask и trace.WithRegion               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Goroutine analysis — ключевые метрики:**

```
Goroutine analysis:
─────────────────────────────────────────────────────────────
Goroutine Name             Count   Total Time   Execution   Network   Sync Block
─────────────────────────────────────────────────────────────
main.handleRequest           100     10.5s        2.1s       5.2s      3.2s
main.processData              50      5.2s        4.8s       0.1s      0.3s
runtime.gcBgMarkWorker         4      1.2s        1.2s       0s        0s
```

**Интерпретация:**
- **High Network wait** → Медленные внешние сервисы, БД
- **High Sync block** → Contention на mutex или переполненные каналы
- **High Syscall** → Много disk I/O
- **High Scheduler wait** → Слишком много горутин, не хватает P

### 2.4 Диагностика latency spikes

Latency spikes — это когда P99 latency значительно выше P50. Типичные причины:

#### Причина 1: GC паузы (STW)

```
┌─────────────────────────────────────────────────────────────┐
│                     GC PAUSE В TRACE                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Timeline:                                                   │
│                                                              │
│  Goroutine 1: ████████░░░░░░░░████████████                  │
│  Goroutine 2: ██████░░░░░░░░░░██████████████                │
│  Goroutine 3: ████░░░░░░░░░░░░████████████████              │
│                     ▲                                        │
│                     │                                        │
│               GC STW (stop-the-world)                       │
│               Все горутины остановлены                      │
│                                                              │
│  ⚠️ STW > 1ms = проблема для low-latency систем            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Диагностика:**
1. Открыть trace, найти "GC" события
2. Посмотреть на длительность STW фаз
3. Если STW > 1ms, оптимизировать аллокации

**Решение:**
- Уменьшить аллокации (escape analysis, sync.Pool)
- Увеличить GOGC (больше памяти, реже GC)
- Использовать GOMEMLIMIT

> 💡 **Подробнее**: [Раздел 2.3 (GC)](./03_gc.md)

#### Причина 2: Блокировка на mutex

```go
// Симптом в trace: высокий "Sync block" для многих горутин

// Проблемный код
var globalMu sync.Mutex
var cache = make(map[string]Value)

func handleRequest(key string) Value {
    globalMu.Lock()  // ← Все запросы сериализуются здесь
    defer globalMu.Unlock()

    if v, ok := cache[key]; ok {
        return v
    }
    v := computeExpensive(key)
    cache[key] = v
    return v
}
```

**Как выглядит в trace:**
```
Goroutine 1: ████████████████████████████████  (executing)
Goroutine 2: ░░░░░░░░░░░░████████████████████  (blocked on mutex)
Goroutine 3: ░░░░░░░░░░░░░░░░░░░░░████████████  (blocked on mutex)
```

**Решение:**
- RWMutex для read-heavy workloads
- Sharding (несколько locks)
- Lock-free структуры (sync/atomic)

> 💡 **Подробнее**: [Раздел 2.4 (Синхронизация)](./04_sync_primitives.md)

#### Причина 3: Медленные syscalls (I/O)

```go
// Симптом в trace: высокий "Syscall" time

func handleRequest(w http.ResponseWriter, r *http.Request) {
    // Синхронное чтение файла — блокирует горутину
    data, _ := os.ReadFile("/var/log/large.log")  // ← Syscall blocking

    // Синхронный запрос к внешнему сервису
    resp, _ := http.Get("http://slow-service/api")  // ← Network blocking
    defer resp.Body.Close()

    // ...
}
```

**Решение:**
- Асинхронная обработка через горутины
- Кэширование результатов
- Connection pooling

#### Причина 4: Scheduler latency

```
Симптом: горутины долго ждут в "Runnable" состоянии
(ждут пока планировщик назначит их на P)
```

**Диагностика:**
```bash
GODEBUG=schedtrace=1000 ./myapp
```

**Причины:**
- Слишком много горутин (> 10K активных)
- GOMAXPROCS слишком низкий
- Горутины не yielding (нет I/O, нет runtime.Gosched())

---

## 3. Комплексный workflow профилирования

Этот раздел объединяет все инструменты в единую методологию решения проблем производительности.

### 3.1 Методология: Measure → Identify → Optimize → Verify

```
┌─────────────────────────────────────────────────────────────────┐
│                 WORKFLOW ПРОФИЛИРОВАНИЯ                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐                                               │
│  │  1. MEASURE  │ ← Воспроизвести проблему, собрать данные      │
│  └──────┬───────┘                                               │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────┐                                               │
│  │  2. IDENTIFY │ ← Проанализировать профиль, найти bottleneck  │
│  └──────┬───────┘                                               │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────┐                                               │
│  │  3. OPTIMIZE │ ← Изменить код                                │
│  └──────┬───────┘                                               │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────┐                                               │
│  │  4. VERIFY   │ ← Подтвердить улучшение (benchstat)           │
│  └──────┬───────┘                                               │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Улучшение достаточно?  ──No──►  Вернуться к шагу 1      │   │
│  │         │                                                 │   │
│  │        Yes                                                │   │
│  │         ▼                                                 │   │
│  │      ГОТОВО                                               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Шаг 1: Measure (Измерение)

```bash
# 1. Создать воспроизводимый benchmark
go test -bench=BenchmarkHandler -count=10 > before.txt

# 2. Собрать профиль CPU
go test -bench=BenchmarkHandler -cpuprofile=cpu.prof

# 3. Или для running сервиса
curl -o cpu.prof "http://localhost:6060/debug/pprof/profile?seconds=30"
```

**Важно:**
- Тестировать на **реалистичных данных**
- Использовать **production-like нагрузку**
- Собирать **достаточно samples** (минимум 30 секунд для production)

#### Шаг 2: Identify (Идентификация)

```bash
# Открыть профиль
go tool pprof -http=:8080 cpu.prof

# В браузере:
# 1. Посмотреть Flame Graph — найти широкие блоки
# 2. top -cum — найти функции с высоким cumulative time
# 3. list <function> — посмотреть код с аннотациями
```

**Типичные находки:**
```
Находка                          │ Возможная причина
─────────────────────────────────────────────────────────
runtime.mallocgc занимает >20%   │ Много аллокаций, GC pressure
encoding/json.* занимает много   │ Медленный JSON
runtime.lock/unlock много        │ Mutex contention
syscall.* много                  │ I/O bottleneck
runtime.memmove много            │ Копирование данных
```

#### Шаг 3: Optimize (Оптимизация)

После идентификации bottleneck — изменить код:

```go
// Пример: нашли что strings concat медленный
// До:
func process(items []string) string {
    result := ""
    for _, s := range items {
        result += s  // ← Bottleneck найден в профиле
    }
    return result
}

// После:
func process(items []string) string {
    var b strings.Builder
    b.Grow(estimatedSize)
    for _, s := range items {
        b.WriteString(s)
    }
    return b.String()
}
```

#### Шаг 4: Verify (Верификация)

```bash
# Запустить тот же benchmark после изменений
go test -bench=BenchmarkHandler -count=10 > after.txt

# Сравнить результаты с помощью benchstat
benchstat before.txt after.txt
```

**Пример вывода benchstat:**

```
name              old time/op    new time/op    delta
Handler-8           1.25ms ± 2%    0.42ms ± 3%   -66.4%  (p=0.000 n=10+10)

name              old alloc/op   new alloc/op   delta
Handler-8           48.2kB ± 0%    12.1kB ± 0%   -74.9%  (p=0.000 n=10+10)

name              old allocs/op  new allocs/op  delta
Handler-8              125 ± 0%        32 ± 0%   -74.4%  (p=0.000 n=10+10)
```

> 💡 **Подробнее о benchstat**: [Раздел 2.6 (Тестирование)](./06_testing_benchmarking.md)

### 3.2 Выбор инструмента по типу проблемы

```
┌─────────────────────────────────────────────────────────────────┐
│              МАТРИЦА ВЫБОРА ИНСТРУМЕНТА                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   СИМПТОМ                      │ ПЕРВЫЙ ИНСТРУМЕНТ              │
│   ─────────────────────────────────────────────────────────     │
│   Высокий CPU usage            │ pprof CPU + flame graph        │
│   Высокое потребление RAM      │ pprof heap                     │
│   Частые GC паузы              │ GODEBUG=gctrace + pprof allocs │
│   Latency spikes (P99 >> P50)  │ go tool trace                  │
│   Data races                   │ go test -race                  │
│   Goroutine leaks              │ pprof goroutine                │
│   Медленный throughput         │ benchmarks + pprof CPU         │
│   Mutex contention             │ pprof mutex + trace            │
│   I/O bottleneck               │ go tool trace (syscall)        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Блок-схема выбора:**

```
                    ┌─────────────────┐
                    │  Какая проблема? │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
   ┌───────────┐       ┌───────────┐       ┌───────────┐
   │   CPU %   │       │  Memory   │       │  Latency  │
   │   высокий │       │  растёт   │       │  спайки   │
   └─────┬─────┘       └─────┬─────┘       └─────┬─────┘
         │                   │                   │
         ▼                   ▼                   ▼
   ┌───────────┐       ┌───────────┐       ┌───────────┐
   │pprof CPU  │       │pprof heap │       │ go tool   │
   │flame graph│       │+ allocs   │       │   trace   │
   └───────────┘       └───────────┘       └───────────┘
```

### 3.3 Интеграция с CI/CD

Автоматическое отслеживание регрессий производительности.

#### GitHub Actions: Benchmark на каждый PR

```yaml
# .github/workflows/benchmark.yml
name: Benchmark

on:
  pull_request:
    branches: [main]

jobs:
  benchmark:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Go
        uses: actions/setup-go@v5
        with:
          go-version: '1.22'

      - name: Run benchmarks
        run: |
          go test -bench=. -count=10 -benchmem ./... > new.txt

      - name: Download baseline
        uses: actions/download-artifact@v4
        with:
          name: benchmark-baseline
        continue-on-error: true  # Первый запуск

      - name: Compare with baseline
        run: |
          if [ -f old.txt ]; then
            go install golang.org/x/perf/cmd/benchstat@latest
            benchstat old.txt new.txt | tee comparison.txt

            # Проверить на регрессии > 10%
            if grep -E '\+[0-9]{2,}\.[0-9]+%' comparison.txt; then
              echo "::warning::Performance regression detected!"
            fi
          fi

      - name: Save as baseline (main only)
        if: github.ref == 'refs/heads/main'
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-baseline
          path: new.txt
```

#### Пример с регрессией:

```
                                   PR #123
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  benchstat old.txt new.txt                                       │
│                                                                  │
│  name              old time/op    new time/op    delta          │
│  Handler-8           1.25ms ± 2%    1.89ms ± 3%   +51.2%  ⚠️     │
│                                                                  │
│  ::warning:: Performance regression detected!                   │
│  PR blocked until regression is fixed or approved               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Сбор профилей в production (опционально)

```yaml
# Периодический сбор профилей
- name: Collect production profile
  run: |
    curl -o cpu.prof "http://prod-service:6060/debug/pprof/profile?seconds=30"
    # Отправить в S3 / GCS для анализа
    aws s3 cp cpu.prof s3://profiles/$(date +%Y-%m-%d)/cpu.prof
```

---

## 4. Оптимизация production-кода

После профилирования — практические паттерны оптимизации.

### 4.1 Hot paths и закон Амдала

**Закон Амдала** определяет максимальное ускорение при оптимизации части программы:

```
                    1
Speedup = ──────────────────────────
          (1 - P) + P/S

P = доля времени в оптимизируемой части
S = ускорение этой части
```

**Практический вывод:**

```
┌─────────────────────────────────────────────────────────────┐
│              ЗАКОН АМДАЛА: ПРАКТИКА                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Если функция занимает 50% времени:                        │
│   - Ускорить в 2x → общее ускорение 1.33x                   │
│   - Ускорить в 10x → общее ускорение 1.82x                  │
│   - Ускорить в ∞x → общее ускорение 2x (максимум!)          │
│                                                              │
│   Если функция занимает 10% времени:                        │
│   - Ускорить в 10x → общее ускорение 1.1x                   │
│   - Не стоит тратить время на эту функцию!                  │
│                                                              │
│   ⚠️ Вывод: Оптимизируй только hot paths (>20% времени)     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Как найти hot paths:**

```bash
go tool pprof -http=:8080 cpu.prof
# В Flame Graph: самые широкие блоки = hot paths
```

### 4.2 Оптимизация строковых операций

#### Конкатенация строк

```go
// ❌ Очень плохо: O(n²) — каждая итерация создаёт новую строку
func buildSlow(items []string) string {
    result := ""
    for _, s := range items {
        result += s  // Новая аллокация каждый раз!
    }
    return result
}

// ✅ Хорошо: strings.Builder (O(n), amortized)
func buildFast(items []string) string {
    var b strings.Builder

    // Опционально: предварительный расчёт размера
    size := 0
    for _, s := range items {
        size += len(s)
    }
    b.Grow(size)  // Одна аллокация

    for _, s := range items {
        b.WriteString(s)
    }
    return b.String()
}

// ✅ Альтернатива: strings.Join (если просто конкатенация)
func buildJoin(items []string) string {
    return strings.Join(items, "")
}
```

**Benchmark:**
```
BenchmarkBuildSlow-8     10000     150234 ns/op    530192 B/op    999 allocs/op
BenchmarkBuildFast-8   1000000       1234 ns/op      4096 B/op      1 allocs/op
BenchmarkBuildJoin-8   1000000       1156 ns/op      4096 B/op      1 allocs/op
```

#### Сравнение с C#

```csharp
// C# — аналогичная проблема
string result = "";
foreach (var s in items)
{
    result += s;  // ❌ Плохо
}

// C# — StringBuilder
var sb = new StringBuilder();
foreach (var s in items)
{
    sb.Append(s);  // ✅ Хорошо
}
return sb.ToString();
```

**Сравнение:**
| Go | C# |
|----|-----|
| `strings.Builder` | `StringBuilder` |
| `.WriteString()` | `.Append()` |
| `.Grow(n)` | `.EnsureCapacity(n)` |
| `.String()` | `.ToString()` |

### 4.3 Оптимизация JSON

JSON serialization — частый bottleneck в HTTP сервисах.

#### Стандартная библиотека

```go
import "encoding/json"

// Работает, но использует reflection
func handleRequest(w http.ResponseWriter, r *http.Request) {
    var req Request
    json.NewDecoder(r.Body).Decode(&req)  // Reflection

    resp := process(req)
    json.NewEncoder(w).Encode(resp)  // Reflection
}
```

#### Альтернативы (по скорости)

```
┌─────────────────────────────────────────────────────────────┐
│           СРАВНЕНИЕ JSON БИБЛИОТЕК                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Библиотека       │ Скорость │ Аллокации │ Особенности     │
│   ─────────────────────────────────────────────────────     │
│   encoding/json    │    1x    │  Много    │ Стандартная     │
│   json-iterator    │   3-5x   │  Меньше   │ Drop-in         │
│   goccy/go-json    │   3-5x   │  Меньше   │ Drop-in         │
│   easyjson         │   5-7x   │  Мало     │ Code generation │
│   sonic            │  10-15x  │  Минимум  │ SIMD, code gen  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### easyjson — code generation

```bash
# Установка
go install github.com/mailru/easyjson/...@latest

# Генерация (для файла с типами)
easyjson -all types.go
```

```go
// types.go
type Request struct {
    UserID   int64  `json:"user_id"`
    Action   string `json:"action"`
    Payload  []byte `json:"payload"`
}

// После easyjson -all types.go создаётся types_easyjson.go
// с методами MarshalEasyJSON / UnmarshalEasyJSON
```

```go
// Использование
import "github.com/mailru/easyjson"

func handleRequestFast(w http.ResponseWriter, r *http.Request) {
    var req Request
    easyjson.UnmarshalFromReader(r.Body, &req)  // Без reflection

    resp := process(req)
    easyjson.MarshalToWriter(resp, w)  // Без reflection
}
```

#### Сравнение с C#

```csharp
// C# — System.Text.Json (с source generators)
[JsonSerializable(typeof(Request))]
public partial class JsonContext : JsonSerializerContext { }

// Использование (без reflection)
var req = JsonSerializer.Deserialize(json, JsonContext.Default.Request);
```

| Go | C# |
|----|-----|
| `easyjson` (code gen) | `System.Text.Json` + source generators |
| `encoding/json` (reflection) | `Newtonsoft.Json` (reflection) |

### 4.4 Избегание interface{} в hot paths

`interface{}` (или `any` в Go 1.18+) требует boxing/unboxing и не позволяет компилятору оптимизировать.

```go
// ❌ Плохо: interface{} в hot path
func processSlow(items []interface{}) int {
    sum := 0
    for _, item := range items {
        // Type assertion в каждой итерации
        if v, ok := item.(int); ok {
            sum += v
        }
    }
    return sum
}

// ✅ Хорошо: generics (Go 1.18+)
func processFast[T constraints.Integer](items []T) T {
    var sum T
    for _, item := range items {
        sum += item  // Без type assertion
    }
    return sum
}

// ✅ Или: конкретный тип
func processInts(items []int) int {
    sum := 0
    for _, item := range items {
        sum += item
    }
    return sum
}
```

**Benchmark:**
```
BenchmarkProcessInterface-8    5000000    312 ns/op    80 B/op    5 allocs/op
BenchmarkProcessGeneric-8     50000000     24 ns/op     0 B/op    0 allocs/op
BenchmarkProcessInts-8        50000000     23 ns/op     0 B/op    0 allocs/op
```

#### Type switch как альтернатива

```go
// Когда типов немного и они известны заранее
func processKnownTypes(v interface{}) int {
    switch x := v.(type) {
    case int:
        return x * 2
    case int64:
        return int(x * 2)
    case string:
        return len(x)
    default:
        return 0
    }
}
```

### 4.5 Preallocations и переиспользование

#### Preallocation слайсов

```go
// ❌ Плохо: много reallocations
func collectBad(n int) []int {
    var result []int  // len=0, cap=0
    for i := 0; i < n; i++ {
        result = append(result, compute(i))  // Grow: 0→1→2→4→8→16→...
    }
    return result
}

// ✅ Хорошо: одна аллокация
func collectGood(n int) []int {
    result := make([]int, 0, n)  // len=0, cap=n
    for i := 0; i < n; i++ {
        result = append(result, compute(i))  // No reallocation
    }
    return result
}

// ✅ Ещё лучше, если индекс известен
func collectBest(n int) []int {
    result := make([]int, n)  // len=n, cap=n
    for i := 0; i < n; i++ {
        result[i] = compute(i)  // Direct assignment
    }
    return result
}
```

#### Preallocation maps

```go
// ❌ Плохо: много rehashing
func buildMapBad(items []Item) map[string]Item {
    result := make(map[string]Item)  // Начальный размер по умолчанию
    for _, item := range items {
        result[item.ID] = item  // Rehash при росте
    }
    return result
}

// ✅ Хорошо: одна аллокация
func buildMapGood(items []Item) map[string]Item {
    result := make(map[string]Item, len(items))  // Точный размер
    for _, item := range items {
        result[item.ID] = item  // No rehashing
    }
    return result
}
```

#### sync.Pool для переиспользования

```go
// Пул буферов для JSON encoding
var bufferPool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

func encodeJSON(v interface{}) ([]byte, error) {
    buf := bufferPool.Get().(*bytes.Buffer)
    buf.Reset()  // Важно: очистить перед использованием
    defer bufferPool.Put(buf)

    err := json.NewEncoder(buf).Encode(v)
    if err != nil {
        return nil, err
    }

    // Копируем, потому что буфер вернётся в пул
    result := make([]byte, buf.Len())
    copy(result, buf.Bytes())
    return result, nil
}
```

> 💡 **Подробнее о sync.Pool**: [Раздел 2.3 (GC)](./03_gc.md)

#### Сравнение с C#

| Go | C# |
|----|-----|
| `make([]T, 0, n)` | `new List<T>(capacity: n)` |
| `make(map[K]V, n)` | `new Dictionary<K,V>(capacity: n)` |
| `sync.Pool` | `ObjectPool<T>` (Microsoft.Extensions.ObjectPool) |
| `[]byte` buffer reuse | `ArrayPool<byte>.Shared` |

```csharp
// C# эквивалент sync.Pool
var pool = ArrayPool<byte>.Shared;
byte[] buffer = pool.Rent(1024);
try
{
    // Использовать buffer
}
finally
{
    pool.Return(buffer);
}
```

---

## 5. Continuous Profiling

Continuous Profiling — это постоянный сбор профилей в production для отслеживания производительности во времени.

### 5.1 Концепция

```
┌─────────────────────────────────────────────────────────────────┐
│              CONTINUOUS PROFILING: КОНЦЕПЦИЯ                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Традиционное профилирование:                                  │
│   ────────────────────────────                                  │
│   1. Заметили проблему                                          │
│   2. Подключились к production                                  │
│   3. Собрали профиль                                            │
│   4. Проблема уже прошла... 😞                                  │
│                                                                  │
│   Continuous Profiling:                                         │
│   ─────────────────────                                         │
│   • Постоянный сбор профилей (CPU, memory, goroutines)          │
│   • Агрегация и хранение во времени                             │
│   • Можно "вернуться в прошлое" и увидеть, что происходило      │
│   • Сравнение версий: v1.2.3 vs v1.2.4                          │
│   • Alerts на аномалии                                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Преимущества:**
- **Ретроспективный анализ** — посмотреть профиль на момент инцидента
- **Сравнение версий** — новая версия стала медленнее?
- **Тренды** — производительность деградирует со временем?
- **Корреляция** — связать профиль с метриками и логами

### 5.2 Инструменты

```
┌─────────────────────────────────────────────────────────────────┐
│           ИНСТРУМЕНТЫ CONTINUOUS PROFILING                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Инструмент          │ Тип          │ Стоимость                │
│   ────────────────────────────────────────────────────────────  │
│   Pyroscope           │ Open-source  │ Бесплатно (self-hosted)  │
│   Grafana Phlare      │ Open-source  │ Бесплатно (self-hosted)  │
│   Google Cloud        │ Cloud        │ $5/agent/month           │
│     Profiler          │              │                          │
│   Datadog             │ Cloud        │ Включено в APM план      │
│     Profiler          │              │                          │
│   Polar Signals       │ Cloud/OSS    │ Free tier + paid         │
│   Parca               │ Open-source  │ Бесплатно (self-hosted)  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Сравнение с .NET:**
| Go | .NET |
|----|------|
| Pyroscope | Application Insights Profiler |
| Datadog Profiler | Datadog .NET Profiler |
| Google Cloud Profiler | Azure Application Insights |

### 5.3 Интеграция с Go приложением

#### Pyroscope (Open Source)

```go
package main

import (
    "github.com/grafana/pyroscope-go"
)

func main() {
    // Инициализация Pyroscope
    pyroscope.Start(pyroscope.Config{
        ApplicationName: "my-service",
        ServerAddress:   "http://pyroscope:4040",

        // Типы профилей для сбора
        ProfileTypes: []pyroscope.ProfileType{
            pyroscope.ProfileCPU,
            pyroscope.ProfileAllocObjects,
            pyroscope.ProfileAllocSpace,
            pyroscope.ProfileInuseObjects,
            pyroscope.ProfileInuseSpace,
            pyroscope.ProfileGoroutines,
        },

        // Теги для фильтрации
        Tags: map[string]string{
            "env":     "production",
            "version": "1.2.3",
            "region":  "us-east-1",
        },
    })

    // Запуск приложения
    runApp()
}
```

**Dockerfile для Pyroscope:**

```dockerfile
FROM golang:1.22 AS builder
WORKDIR /app
COPY . .
RUN go build -o /app/myservice

FROM gcr.io/distroless/base
COPY --from=builder /app/myservice /myservice
CMD ["/myservice"]
```

**Docker Compose:**

```yaml
version: "3.8"
services:
  pyroscope:
    image: grafana/pyroscope:latest
    ports:
      - "4040:4040"
    volumes:
      - pyroscope-data:/var/lib/pyroscope

  myservice:
    build: .
    environment:
      - PYROSCOPE_SERVER=http://pyroscope:4040
    depends_on:
      - pyroscope

volumes:
  pyroscope-data:
```

#### Google Cloud Profiler

```go
package main

import (
    "cloud.google.com/go/profiler"
    "log"
)

func main() {
    // Инициализация Cloud Profiler
    cfg := profiler.Config{
        Service:        "my-service",
        ServiceVersion: "1.2.3",
        ProjectID:      "my-gcp-project",  // Опционально, если в GCP

        // Не нужно указывать MutexProfiling, он включён по умолчанию
    }

    if err := profiler.Start(cfg); err != nil {
        log.Fatalf("Failed to start profiler: %v", err)
    }

    // Запуск приложения
    runApp()
}
```

#### Datadog Continuous Profiler

```go
package main

import (
    "gopkg.in/DataDog/dd-trace-go.v1/profiler"
    "log"
)

func main() {
    // Инициализация Datadog Profiler
    err := profiler.Start(
        profiler.WithService("my-service"),
        profiler.WithEnv("production"),
        profiler.WithVersion("1.2.3"),
        profiler.WithProfileTypes(
            profiler.CPUProfile,
            profiler.HeapProfile,
            profiler.GoroutineProfile,
            profiler.MutexProfile,
            profiler.BlockProfile,
        ),
    )
    if err != nil {
        log.Fatalf("Failed to start profiler: %v", err)
    }
    defer profiler.Stop()

    // Запуск приложения
    runApp()
}
```

#### Low-overhead профилирование

Continuous profiling работает с низким overhead (~1-5%):

```
┌─────────────────────────────────────────────────────────────────┐
│              OVERHEAD CONTINUOUS PROFILING                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Профиль         │ Overhead │ Частота сбора                    │
│   ────────────────────────────────────────────────────────────  │
│   CPU             │  ~1-2%   │ Постоянно (sampling 100 Hz)      │
│   Heap            │  ~1%     │ Каждые 10 секунд                 │
│   Goroutines      │  ~0.5%   │ Каждые 10 секунд                 │
│   Mutex           │  ~0.5%   │ Постоянно (sampling)             │
│   Block           │  ~1%     │ Постоянно (sampling)             │
│   ────────────────────────────────────────────────────────────  │
│   ИТОГО           │  ~3-5%   │ Приемлемо для production         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Новые инструменты профилирования (Go 1.25-1.26)

### 5.1 runtime/trace.FlightRecorder (Go 1.25)

> 💡 **Для C# разработчиков**: Аналог .NET ETW (Event Tracing for Windows) или Application Insights Snapshot Debugger — кольцевой буфер событий для диагностики редких проблем в продакшне.

Go 1.25 добавил `runtime/trace.FlightRecorder` — **непрерывную запись trace-событий** в кольцевой буфер. В отличие от `go tool trace`, FlightRecorder работает **всегда в фоне** и сохраняет только последние N секунд. Полезен для захвата редких ошибок (latency spike раз в несколько часов).

**Проблема классического trace:**
```go
// Классический подход: trace нужно включить заранее
// Если latency spike произошёл до включения — данных нет
f, _ := os.Create("trace.out")
trace.Start(f)
defer trace.Stop()
// Ждём проблему... которая уже произошла
```

**FlightRecorder — всегда пишет, сохраняет по событию:**
```go
import (
    "os"
    "runtime/trace"
)

func startFlightRecorder() {
    // Создаём recorder с буфером на 30 секунд
    recorder := &trace.FlightRecorder{}
    recorder.Start()

    // В отдельной горутине следим за latency
    go func() {
        for {
            start := time.Now()
            checkLatency()
            elapsed := time.Since(start)

            // При latency spike — сохраняем последние 30 сек
            if elapsed > 500*time.Millisecond {
                f, err := os.Create("flight-" + time.Now().Format("150405") + ".trace")
                if err == nil {
                    recorder.WriteTo(f) // Сохраняем буфер
                    f.Close()
                    log.Printf("latency spike detected: %v, trace saved", elapsed)
                }
            }
            time.Sleep(100 * time.Millisecond)
        }
    }()
}
```

**Интеграция с HTTP handler для on-demand дампа:**
```go
// Endpoint для получения trace по требованию
http.HandleFunc("/debug/flight-trace", func(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/octet-stream")
    w.Header().Set("Content-Disposition", `attachment; filename="flight.trace"`)
    recorder.WriteTo(w) // Отдаём trace клиенту
})
```

**Сравнение с .NET:**
| Аспект | .NET ETW / Snapshot | Go FlightRecorder |
|--------|---------------------|------------------|
| Всегда активен | Да (ETW) | Да |
| Кольцевой буфер | Да | Да |
| Накладные расходы | ~1-3% CPU | ~1-2% CPU |
| Размер буфера | Настраиваемый | По времени (N сек) |
| Инструмент анализа | PerfView, dotnet-trace | go tool trace |

---

### 5.2 Обнаружение утечек горутин (Go 1.26, экспериментально)

Go 1.26 добавил **экспериментальный** детектор утечек горутин в runtime. Включается через `GOEXPERIMENT=goroutineleak`.

```go
// При сборке с GOEXPERIMENT=goroutineleak
// runtime отслеживает горутины без владельцев

// go build -gcflags="-e" -tags goroutineleak ./...

func processOrders(ctx context.Context) {
    for order := range orderChan {
        go func(o Order) { // ← Если ctx отменён до завершения горутины —
            result := processOrder(ctx, o) // ← детектор зафиксирует утечку
            resultChan <- result
        }(order)
    }
}
```

```bash
# Включение детектора при тестировании
GOEXPERIMENT=goroutineleak go test ./... -v

# В логах увидите:
# GOROUTINE LEAK: goroutine 42 started at main.processOrders:45
# still running after context cancellation
```

> ⚠️ **Статус**: Экспериментальный в Go 1.26. Не рекомендуется для продакшна. Для стабильного обнаружения утечек используйте [goleak](https://github.com/uber-go/goleak) (см. раздел 11.3 в 06_testing_benchmarking.md).

---

### 5.3 Новые runtime/metrics в Go 1.26

Go 1.26 добавил новые метрики в `runtime/metrics` (доступны через Prometheus и OpenTelemetry):

```go
import "runtime/metrics"

// Новые метрики Go 1.26
samples := []metrics.Sample{
    // Состояния горутин
    {Name: "/sched/goroutines:goroutines"},        // Текущее количество
    {Name: "/sched/goroutines/created:goroutines"}, // Создано всего (новая!)
    {Name: "/sched/goroutines/runnable:goroutines"}, // В очереди (новая!)
    {Name: "/sched/goroutines/blocked:goroutines"},   // Заблокированных (новая!)

    // OS потоки
    {Name: "/sched/latencies:seconds"},            // Latency планировщика
    {Name: "/os/threads:threads"},                 // OS потоки (новая!)
}

metrics.Read(samples)

for _, s := range samples {
    fmt.Printf("%s = %v\n", s.Name, s.Value)
}
```

**Prometheus: экспорт новых метрик:**
```go
// go.opencensus.io/stats или prometheus/client_golang
// Автоматически подхватывает новые runtime/metrics через
// collectors.NewGoCollector(collectors.WithGoCollectorRuntimeMetrics(...))

import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/collectors"
)

func initMetrics() *prometheus.Registry {
    reg := prometheus.NewRegistry()
    reg.MustRegister(
        collectors.NewGoCollector(
            // Go 1.26: включаем все runtime метрики включая новые
            collectors.WithGoCollectorRuntimeMetrics(
                collectors.GoRuntimeMetricsRuleAny,
            ),
        ),
    )
    return reg
}
```

**Что отслеживают новые метрики:**
| Метрика | Что показывает | Применение |
|---------|----------------|-----------|
| `goroutines/created` | Темп создания горутин | Утечки горутин |
| `goroutines/runnable` | Очередь планировщика | Overload планировщика |
| `goroutines/blocked` | Ожидание channel/mutex | Deadlock-риски |
| `os/threads` | OS потоки (M в GMP) | Thread pool bloat |

---

## Практические примеры

### Пример 1: Оптимизация HTTP сервиса (end-to-end)

**Сценарий:** HTTP сервис с высоким latency на endpoint `/api/users`.

#### Шаг 1: Воспроизвести проблему

```go
// main.go
package main

import (
    "encoding/json"
    "net/http"
    _ "net/http/pprof"  // Добавляем pprof
)

type User struct {
    ID       int64    `json:"id"`
    Name     string   `json:"name"`
    Email    string   `json:"email"`
    Tags     []string `json:"tags"`
    Metadata string   `json:"metadata"`
}

func getUsers(w http.ResponseWriter, r *http.Request) {
    users := loadUsers()  // Загрузка из БД

    // Проблемный код: строим JSON ответ неэффективно
    var result string
    for _, u := range users {
        data, _ := json.Marshal(u)
        result += string(data) + ","  // ❌ Конкатенация строк
    }
    result = "[" + result[:len(result)-1] + "]"

    w.Header().Set("Content-Type", "application/json")
    w.Write([]byte(result))
}

func main() {
    // pprof на отдельном порту
    go func() {
        http.ListenAndServe("localhost:6060", nil)
    }()

    mux := http.NewServeMux()
    mux.HandleFunc("/api/users", getUsers)
    http.ListenAndServe(":8080", mux)
}
```

#### Шаг 2: Benchmark

```go
// main_test.go
package main

import (
    "net/http"
    "net/http/httptest"
    "testing"
)

func BenchmarkGetUsers(b *testing.B) {
    req := httptest.NewRequest("GET", "/api/users", nil)

    for i := 0; i < b.N; i++ {
        w := httptest.NewRecorder()
        getUsers(w, req)
    }
}
```

```bash
# Запуск benchmark с CPU профилем
go test -bench=BenchmarkGetUsers -count=10 -cpuprofile=cpu.prof > before.txt
```

#### Шаг 3: Анализ профиля

```bash
go tool pprof -http=:8080 cpu.prof
```

**Результат анализа:**

```
Showing top 10 nodes out of 43
      flat  flat%   sum%        cum   cum%
     2.5s 35.00% 35.00%      2.5s 35.00%  runtime.mallocgc      ← Много аллокаций!
     1.5s 21.00% 56.00%      1.5s 21.00%  runtime.memmove       ← Копирование данных
     1.0s 14.00% 70.00%      4.0s 56.00%  main.getUsers         ← Наш handler
     0.5s  7.00% 77.00%      0.5s  7.00%  encoding/json.Marshal
```

**Вывод:** Много аллокаций (`mallocgc`) и копирование (`memmove`) — типично для конкатенации строк.

#### Шаг 4: Оптимизация

```go
func getUsersOptimized(w http.ResponseWriter, r *http.Request) {
    users := loadUsers()

    w.Header().Set("Content-Type", "application/json")

    // ✅ Используем json.Encoder напрямую — никакой конкатенации
    json.NewEncoder(w).Encode(users)
}
```

**Ещё лучше с easyjson:**

```go
//go:generate easyjson -all main.go

func getUsersFast(w http.ResponseWriter, r *http.Request) {
    users := loadUsers()

    w.Header().Set("Content-Type", "application/json")

    // ✅ easyjson — без reflection
    out, _ := easyjson.Marshal(users)
    w.Write(out)
}
```

#### Шаг 5: Верификация

```bash
go test -bench=BenchmarkGetUsers -count=10 > after.txt
benchstat before.txt after.txt
```

**Результат:**
```
name          old time/op    new time/op    delta
GetUsers-8      15.2ms ± 2%     1.2ms ± 3%   -92.1%  (p=0.000 n=10+10)

name          old alloc/op   new alloc/op   delta
GetUsers-8      4.52MB ± 0%    0.12MB ± 0%   -97.3%  (p=0.000 n=10+10)

name          old allocs/op  new allocs/op  delta
GetUsers-8       45.2k ± 0%      0.5k ± 0%   -98.9%  (p=0.000 n=10+10)
```

---

### Пример 2: Диагностика memory leak через goroutine leak

**Сценарий:** Память приложения постоянно растёт.

#### Симптомы

```bash
# Мониторинг памяти
watch -n 5 'curl -s localhost:6060/debug/pprof/heap | head -20'

# Результат: память растёт на ~10MB каждую минуту
```

#### Шаг 1: Проверка горутин

```bash
# Количество горутин
curl -s localhost:6060/debug/pprof/goroutine | head -1
# goroutine profile: total 15234  ← Подозрительно много!

# Детальный профиль
go tool pprof http://localhost:6060/debug/pprof/goroutine
```

```
(pprof) top
Showing nodes accounting for 15000, 98.5% of 15234 total
      flat  flat%   sum%        cum   cum%
     15000 98.5% 98.5%      15000 98.5%  main.processRequest
```

#### Шаг 2: Анализ кода

```go
// Проблемный код
func processRequest(ctx context.Context, data Data) {
    // Горутина запускается, но никогда не завершается
    go func() {
        for {
            result := heavyComputation(data)
            sendToChannel(result)  // ← Канал заполнен, горутина блокируется
        }
    }()
}

// Канал никогда не читается после первых N элементов
var resultChan = make(chan Result, 100)

func init() {
    go func() {
        for i := 0; i < 100; i++ {
            <-resultChan  // Читаем только 100 элементов
        }
        // Больше не читаем — все горутины блокируются на send
    }()
}
```

#### Шаг 3: Исправление

```go
func processRequestFixed(ctx context.Context, data Data) {
    go func() {
        for {
            select {
            case <-ctx.Done():
                return  // ✅ Выход при отмене контекста
            default:
                result := heavyComputation(data)
                select {
                case resultChan <- result:
                    // Отправлено успешно
                case <-ctx.Done():
                    return  // ✅ Выход если контекст отменён
                case <-time.After(time.Second):
                    // ✅ Таймаут — не блокируемся навечно
                    log.Warn("channel full, dropping result")
                }
            }
        }
    }()
}
```

#### Шаг 4: Использование goleak в тестах

```go
import "go.uber.org/goleak"

func TestMain(m *testing.M) {
    goleak.VerifyTestMain(m)
}

func TestProcessRequest(t *testing.T) {
    ctx, cancel := context.WithTimeout(context.Background(), time.Second)
    defer cancel()

    processRequestFixed(ctx, testData)

    // goleak автоматически проверит утечки горутин
}
```

---

### Пример 3: Latency spikes в микросервисе

**Сценарий:** P99 latency = 500ms, P50 = 10ms. Огромный разброс.

#### Шаг 1: Сбор trace

```bash
curl -o trace.out "http://localhost:6060/debug/pprof/trace?seconds=60"
go tool trace trace.out
```

#### Шаг 2: Анализ

В браузере открываем "Goroutine analysis":

```
Goroutine analysis:
────────────────────────────────────────────────────────────────
Goroutine Name           Count   Execution   Sync Block   GC Wait
────────────────────────────────────────────────────────────────
main.handleRequest        1000     100ms       350ms       50ms
                                               ↑            ↑
                                         Mutex/Channel   GC паузы
```

**Вывод:**
- 350ms в "Sync Block" — блокировка на mutex или channel
- 50ms в "GC Wait" — ожидание GC

#### Шаг 3: Диагностика mutex contention

```bash
# Профиль mutex contention
go tool pprof http://localhost:6060/debug/pprof/mutex
```

```
(pprof) top
Showing nodes accounting for 8.5s, 85% of 10s total
      flat  flat%   sum%        cum   cum%
     8.5s 85.00% 85.00%      8.5s 85.00%  sync.(*Mutex).Lock
                                           main.getCache
```

**Проблемный код:**

```go
var (
    cacheMu sync.Mutex
    cache   = make(map[string]Value)
)

func getCache(key string) Value {
    cacheMu.Lock()  // ← Все запросы сериализуются здесь
    defer cacheMu.Unlock()
    return cache[key]
}
```

#### Шаг 4: Оптимизация

```go
// Решение 1: RWMutex для read-heavy workload
var (
    cacheMu sync.RWMutex
    cache   = make(map[string]Value)
)

func getCacheRW(key string) Value {
    cacheMu.RLock()  // ✅ Параллельные чтения
    defer cacheMu.RUnlock()
    return cache[key]
}

// Решение 2: Sharded cache для high contention
type ShardedCache struct {
    shards [256]struct {
        sync.RWMutex
        data map[string]Value
    }
}

func (c *ShardedCache) Get(key string) Value {
    shard := &c.shards[hash(key)%256]
    shard.RLock()
    defer shard.RUnlock()
    return shard.data[key]
}
```

#### Шаг 5: Диагностика GC

```bash
GODEBUG=gctrace=1 ./myapp 2>&1 | grep gc
```

```
gc 1 @0.012s 2%: 0.5+15+0.5 ms clock, 4+0/12/0+4 ms cpu, 100->105->50 MB
gc 2 @0.034s 3%: 0.6+18+0.6 ms clock, 5+0/15/0+5 ms cpu, 100->110->55 MB
                      ↑
                 STW pause = 18ms — слишком долго!
```

**Решение:**

```go
// Увеличить GOGC (меньше GC циклов, больше памяти)
// В production или через переменную окружения
import "runtime/debug"

func init() {
    debug.SetGCPercent(200)  // Дефолт 100, увеличиваем в 2 раза
}
```

---

### Пример 4: CI/CD pipeline для производительности

**Цель:** Автоматически ловить регрессии производительности в PR.

#### GitHub Actions workflow

```yaml
# .github/workflows/performance.yml
name: Performance Tests

on:
  pull_request:
    branches: [main]

jobs:
  benchmark:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Для сравнения с main

      - name: Setup Go
        uses: actions/setup-go@v5
        with:
          go-version: '1.22'

      - name: Install benchstat
        run: go install golang.org/x/perf/cmd/benchstat@latest

      - name: Run benchmarks on PR
        run: |
          go test -bench=. -count=10 -benchmem ./... > new.txt

      - name: Checkout main branch
        run: |
          git checkout main
          go test -bench=. -count=10 -benchmem ./... > old.txt
          git checkout -

      - name: Compare benchmarks
        id: compare
        run: |
          benchstat old.txt new.txt > comparison.txt
          cat comparison.txt

          # Проверка на регрессии > 10%
          if grep -E '\+[1-9][0-9]+\.[0-9]+%' comparison.txt; then
            echo "regression=true" >> $GITHUB_OUTPUT
          else
            echo "regression=false" >> $GITHUB_OUTPUT
          fi

      - name: Comment on PR
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const comparison = fs.readFileSync('comparison.txt', 'utf8');

            const body = `## Benchmark Results

            \`\`\`
            ${comparison}
            \`\`\`

            ${process.env.REGRESSION === 'true' ? '⚠️ **Performance regression detected!**' : '✅ No significant regressions'}
            `;

            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: body
            });
        env:
          REGRESSION: ${{ steps.compare.outputs.regression }}

      - name: Fail on regression
        if: steps.compare.outputs.regression == 'true'
        run: |
          echo "Performance regression detected!"
          exit 1
```

#### Результат в PR

```
## Benchmark Results

name              old time/op    new time/op    delta
Handler-8           1.25ms ± 2%    1.89ms ± 3%   +51.2%  ⚠️

name              old alloc/op   new alloc/op   delta
Handler-8           48.2kB ± 0%    72.1kB ± 0%   +49.6%  ⚠️

⚠️ **Performance regression detected!**
```

---
