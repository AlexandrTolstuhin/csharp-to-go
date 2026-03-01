# 2.6 Тестирование и бенчмаркинг

## Содержание

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Введение](#%D0%B2%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5)
  - [Сравнительная таблица: C# vs Go тестирование](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F-%D1%82%D0%B0%D0%B1%D0%BB%D0%B8%D1%86%D0%B0-c-vs-go-%D1%82%D0%B5%D1%81%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5)
- [1. testing package: основы](#1-testing-package-%D0%BE%D1%81%D0%BD%D0%BE%D0%B2%D1%8B)
  - [1.1 Структура тестов](#11-%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D1%83%D1%80%D0%B0-%D1%82%D0%B5%D1%81%D1%82%D0%BE%D0%B2)
    - [Сравнение: C# vs Go](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-c-vs-go)
    - [Ключевые различия](#%D0%BA%D0%BB%D1%8E%D1%87%D0%B5%D0%B2%D1%8B%D0%B5-%D1%80%D0%B0%D0%B7%D0%BB%D0%B8%D1%87%D0%B8%D1%8F)
    - [testing.T методы](#testingt-%D0%BC%D0%B5%D1%82%D0%BE%D0%B4%D1%8B)
  - [1.2 Запуск тестов](#12-%D0%B7%D0%B0%D0%BF%D1%83%D1%81%D0%BA-%D1%82%D0%B5%D1%81%D1%82%D0%BE%D0%B2)
    - [Базовые команды](#%D0%B1%D0%B0%D0%B7%D0%BE%D0%B2%D1%8B%D0%B5-%D0%BA%D0%BE%D0%BC%D0%B0%D0%BD%D0%B4%D1%8B)
    - [Сравнение: dotnet test vs go test](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-dotnet-test-vs-go-test)
    - [Пример вывода](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-%D0%B2%D1%8B%D0%B2%D0%BE%D0%B4%D0%B0)
  - [1.3 Setup/Teardown](#13-setupteardown)
    - [Способ 1: TestMain (package-level setup)](#%D1%81%D0%BF%D0%BE%D1%81%D0%BE%D0%B1-1-testmain-package-level-setup)
    - [Способ 2: defer (для простого cleanup)](#%D1%81%D0%BF%D0%BE%D1%81%D0%BE%D0%B1-2-defer-%D0%B4%D0%BB%D1%8F-%D0%BF%D1%80%D0%BE%D1%81%D1%82%D0%BE%D0%B3%D0%BE-cleanup)
    - [Способ 3: t.Cleanup() (Go 1.14+, идиоматично)](#%D1%81%D0%BF%D0%BE%D1%81%D0%BE%D0%B1-3-tcleanup-go-114-%D0%B8%D0%B4%D0%B8%D0%BE%D0%BC%D0%B0%D1%82%D0%B8%D1%87%D0%BD%D0%BE)
- [2. Table-Driven Tests (идиоматичный Go)](#2-table-driven-tests-%D0%B8%D0%B4%D0%B8%D0%BE%D0%BC%D0%B0%D1%82%D0%B8%D1%87%D0%BD%D1%8B%D0%B9-go)
  - [2.1 Паттерн Table-Driven](#21-%D0%BF%D0%B0%D1%82%D1%82%D0%B5%D1%80%D0%BD-table-driven)
    - [Сравнение: C# [Theory] vs Go table-driven](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-c-theory-vs-go-table-driven)
    - [Анатомия table-driven теста](#%D0%B0%D0%BD%D0%B0%D1%82%D0%BE%D0%BC%D0%B8%D1%8F-table-driven-%D1%82%D0%B5%D1%81%D1%82%D0%B0)
  - [2.2 Преимущества подхода](#22-%D0%BF%D1%80%D0%B5%D0%B8%D0%BC%D1%83%D1%89%D0%B5%D1%81%D1%82%D0%B2%D0%B0-%D0%BF%D0%BE%D0%B4%D1%85%D0%BE%D0%B4%D0%B0)
  - [2.3 Продвинутые техники](#23-%D0%BF%D1%80%D0%BE%D0%B4%D0%B2%D0%B8%D0%BD%D1%83%D1%82%D1%8B%D0%B5-%D1%82%D0%B5%D1%85%D0%BD%D0%B8%D0%BA%D0%B8)
    - [Техника 1: Именованные поля (описательность)](#%D1%82%D0%B5%D1%85%D0%BD%D0%B8%D0%BA%D0%B0-1-%D0%B8%D0%BC%D0%B5%D0%BD%D0%BE%D0%B2%D0%B0%D0%BD%D0%BD%D1%8B%D0%B5-%D0%BF%D0%BE%D0%BB%D1%8F-%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D0%BE%D1%81%D1%82%D1%8C)
    - [Техника 2: Setup/Teardown для каждого case](#%D1%82%D0%B5%D1%85%D0%BD%D0%B8%D0%BA%D0%B0-2-setupteardown-%D0%B4%D0%BB%D1%8F-%D0%BA%D0%B0%D0%B6%D0%B4%D0%BE%D0%B3%D0%BE-case)
    - [Техника 3: Параллелизация table tests](#%D1%82%D0%B5%D1%85%D0%BD%D0%B8%D0%BA%D0%B0-3-%D0%BF%D0%B0%D1%80%D0%B0%D0%BB%D0%BB%D0%B5%D0%BB%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-table-tests)
- [3. Subtests (t.Run)](#3-subtests-trun)
  - [3.1 Организация вложенных тестов](#31-%D0%BE%D1%80%D0%B3%D0%B0%D0%BD%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-%D0%B2%D0%BB%D0%BE%D0%B6%D0%B5%D0%BD%D0%BD%D1%8B%D1%85-%D1%82%D0%B5%D1%81%D1%82%D0%BE%D0%B2)
    - [Сравнение: C# Nested classes vs Go t.Run](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-c-nested-classes-vs-go-trun)
    - [Запуск конкретного subtest](#%D0%B7%D0%B0%D0%BF%D1%83%D1%81%D0%BA-%D0%BA%D0%BE%D0%BD%D0%BA%D1%80%D0%B5%D1%82%D0%BD%D0%BE%D0%B3%D0%BE-subtest)
  - [3.2 Parallel subtests](#32-parallel-subtests)
    - [Сравнение: C# [Theory] vs Go t.Parallel](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-c-theory-vs-go-tparallel)
    - [Важные правила t.Parallel()](#%D0%B2%D0%B0%D0%B6%D0%BD%D1%8B%D0%B5-%D0%BF%D1%80%D0%B0%D0%B2%D0%B8%D0%BB%D0%B0-tparallel)
  - [3.3 Интеграция с table-driven](#33-%D0%B8%D0%BD%D1%82%D0%B5%D0%B3%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D1%81-table-driven)
- [4. Мокирование и тестирование зависимостей](#4-%D0%BC%D0%BE%D0%BA%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5-%D0%B8-%D1%82%D0%B5%D1%81%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5-%D0%B7%D0%B0%D0%B2%D0%B8%D1%81%D0%B8%D0%BC%D0%BE%D1%81%D1%82%D0%B5%D0%B9)
  - [4.1 Интерфейсы для тестируемости](#41-%D0%B8%D0%BD%D1%82%D0%B5%D1%80%D1%84%D0%B5%D0%B9%D1%81%D1%8B-%D0%B4%D0%BB%D1%8F-%D1%82%D0%B5%D1%81%D1%82%D0%B8%D1%80%D1%83%D0%B5%D0%BC%D0%BE%D1%81%D1%82%D0%B8)
    - [Принцип: Accept interfaces, return structs](#%D0%BF%D1%80%D0%B8%D0%BD%D1%86%D0%B8%D0%BF-accept-interfaces-return-structs)
    - [Сравнение: C# Moq vs Go интерфейсы](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-c-moq-vs-go-%D0%B8%D0%BD%D1%82%D0%B5%D1%80%D1%84%D0%B5%D0%B9%D1%81%D1%8B)
  - [4.2 Ручные моки (идиоматично)](#42-%D1%80%D1%83%D1%87%D0%BD%D1%8B%D0%B5-%D0%BC%D0%BE%D0%BA%D0%B8-%D0%B8%D0%B4%D0%B8%D0%BE%D0%BC%D0%B0%D1%82%D0%B8%D1%87%D0%BD%D0%BE)
    - [Паттерн 1: Функциональный mock](#%D0%BF%D0%B0%D1%82%D1%82%D0%B5%D1%80%D0%BD-1-%D1%84%D1%83%D0%BD%D0%BA%D1%86%D0%B8%D0%BE%D0%BD%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9-mock)
    - [Паттерн 2: Mock с состоянием](#%D0%BF%D0%B0%D1%82%D1%82%D0%B5%D1%80%D0%BD-2-mock-%D1%81-%D1%81%D0%BE%D1%81%D1%82%D0%BE%D1%8F%D0%BD%D0%B8%D0%B5%D0%BC)
  - [4.3 gomock (code generation)](#43-gomock-code-generation)
    - [Установка](#%D1%83%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BA%D0%B0)
    - [Генерация моков](#%D0%B3%D0%B5%D0%BD%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D0%BC%D0%BE%D0%BA%D0%BE%D0%B2)
    - [Использование](#%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5)
  - [4.4 testify/mock](#44-testifymock)
- [5. Benchmarks: производительность](#5-benchmarks-%D0%BF%D1%80%D0%BE%D0%B8%D0%B7%D0%B2%D0%BE%D0%B4%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D0%BE%D1%81%D1%82%D1%8C)
  - [5.1 Основы бенчмаркинга](#51-%D0%BE%D1%81%D0%BD%D0%BE%D0%B2%D1%8B-%D0%B1%D0%B5%D0%BD%D1%87%D0%BC%D0%B0%D1%80%D0%BA%D0%B8%D0%BD%D0%B3%D0%B0)
    - [Сравнение: BenchmarkDotNet vs Go benchmarks](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-benchmarkdotnet-vs-go-benchmarks)
  - [5.2 Оптимизация benchmarks](#52-%D0%BE%D0%BF%D1%82%D0%B8%D0%BC%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-benchmarks)
    - [b.N iterations](#bn-iterations)
    - [b.ReportAllocs() — профилирование памяти](#breportallocs--%D0%BF%D1%80%D0%BE%D1%84%D0%B8%D0%BB%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5-%D0%BF%D0%B0%D0%BC%D1%8F%D1%82%D0%B8)
    - [Предотвращение оптимизаций компилятора](#%D0%BF%D1%80%D0%B5%D0%B4%D0%BE%D1%82%D0%B2%D1%80%D0%B0%D1%89%D0%B5%D0%BD%D0%B8%D0%B5-%D0%BE%D0%BF%D1%82%D0%B8%D0%BC%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D0%B9-%D0%BA%D0%BE%D0%BC%D0%BF%D0%B8%D0%BB%D1%8F%D1%82%D0%BE%D1%80%D0%B0)
  - [5.3 Анализ результатов](#53-%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7-%D1%80%D0%B5%D0%B7%D1%83%D0%BB%D1%8C%D1%82%D0%B0%D1%82%D0%BE%D0%B2)
    - [Метрики](#%D0%BC%D0%B5%D1%82%D1%80%D0%B8%D0%BA%D0%B8)
    - [benchstat — сравнение до/после](#benchstat--%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-%D0%B4%D0%BE%D0%BF%D0%BE%D1%81%D0%BB%D0%B5)
  - [5.4 Memory benchmarks](#54-memory-benchmarks)
    - [Связь с разделом 2.3 (GC)](#%D1%81%D0%B2%D1%8F%D0%B7%D1%8C-%D1%81-%D1%80%D0%B0%D0%B7%D0%B4%D0%B5%D0%BB%D0%BE%D0%BC-23-gc)
- [6. Fuzzing (Go 1.18+)](#6-fuzzing-go-118)
  - [6.1 Введение в fuzzing](#61-%D0%B2%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5-%D0%B2-fuzzing)
    - [Сигнатура fuzz-теста](#%D1%81%D0%B8%D0%B3%D0%BD%D0%B0%D1%82%D1%83%D1%80%D0%B0-fuzz-%D1%82%D0%B5%D1%81%D1%82%D0%B0)
  - [6.2 Написание fuzz-тестов](#62-%D0%BD%D0%B0%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B5-fuzz-%D1%82%D0%B5%D1%81%D1%82%D0%BE%D0%B2)
  - [6.3 Когда использовать](#63-%D0%BA%D0%BE%D0%B3%D0%B4%D0%B0-%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D1%8C)
- [7. Integration Tests](#7-integration-tests)
  - [7.1 httptest: тестирование HTTP handlers](#71-httptest-%D1%82%D0%B5%D1%81%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5-http-handlers)
    - [Сравнение: ASP.NET Core TestServer vs Go httptest](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-aspnet-core-testserver-vs-go-httptest)
  - [7.2 Тестирование БД](#72-%D1%82%D0%B5%D1%81%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5-%D0%B1%D0%B4)
    - [SQLite (in-memory)](#sqlite-in-memory)
    - [testcontainers-go (PostgreSQL в Docker)](#testcontainers-go-postgresql-%D0%B2-docker)
  - [7.3 Внешние зависимости](#73-%D0%B2%D0%BD%D0%B5%D1%88%D0%BD%D0%B8%D0%B5-%D0%B7%D0%B0%D0%B2%D0%B8%D1%81%D0%B8%D0%BC%D0%BE%D1%81%D1%82%D0%B8)
    - [TestMain для setup/teardown](#testmain-%D0%B4%D0%BB%D1%8F-setupteardown)
- [8. Race Detector](#8-race-detector)
  - [8.1 Что такое data race](#81-%D1%87%D1%82%D0%BE-%D1%82%D0%B0%D0%BA%D0%BE%D0%B5-data-race)
  - [8.2 go test -race](#82-go-test--race)
  - [8.3 Типичные race conditions](#83-%D1%82%D0%B8%D0%BF%D0%B8%D1%87%D0%BD%D1%8B%D0%B5-race-conditions)
    - [Race 1: Map без синхронизации](#race-1-map-%D0%B1%D0%B5%D0%B7-%D1%81%D0%B8%D0%BD%D1%85%D1%80%D0%BE%D0%BD%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D0%B8)
    - [Race 2: Loop variable в горутине (до Go 1.22)](#race-2-loop-variable-%D0%B2-%D0%B3%D0%BE%D1%80%D1%83%D1%82%D0%B8%D0%BD%D0%B5-%D0%B4%D0%BE-go-122)
- [9. Coverage (покрытие кода)](#9-coverage-%D0%BF%D0%BE%D0%BA%D1%80%D1%8B%D1%82%D0%B8%D0%B5-%D0%BA%D0%BE%D0%B4%D0%B0)
  - [9.1 go test -cover](#91-go-test--cover)
  - [9.2 Визуализация покрытия](#92-%D0%B2%D0%B8%D0%B7%D1%83%D0%B0%D0%BB%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-%D0%BF%D0%BE%D0%BA%D1%80%D1%8B%D1%82%D0%B8%D1%8F)
  - [9.3 Целевые метрики](#93-%D1%86%D0%B5%D0%BB%D0%B5%D0%B2%D1%8B%D0%B5-%D0%BC%D0%B5%D1%82%D1%80%D0%B8%D0%BA%D0%B8)
- [10. Идиоматичные паттерны тестирования](#10-%D0%B8%D0%B4%D0%B8%D0%BE%D0%BC%D0%B0%D1%82%D0%B8%D1%87%D0%BD%D1%8B%D0%B5-%D0%BF%D0%B0%D1%82%D1%82%D0%B5%D1%80%D0%BD%D1%8B-%D1%82%D0%B5%D1%81%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F)
  - [10.1 Helper functions](#101-helper-functions)
  - [10.2 Golden files](#102-golden-files)
  - [10.3 Testable Examples](#103-testable-examples)
  - [10.4 Build tags](#104-build-tags)
- [11. Тестирование конкурентного кода](#11-%D1%82%D0%B5%D1%81%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5-%D0%BA%D0%BE%D0%BD%D0%BA%D1%83%D1%80%D0%B5%D0%BD%D1%82%D0%BD%D0%BE%D0%B3%D0%BE-%D0%BA%D0%BE%D0%B4%D0%B0)
  - [11.1 Проблемы тестирования горутин](#111-%D0%BF%D1%80%D0%BE%D0%B1%D0%BB%D0%B5%D0%BC%D1%8B-%D1%82%D0%B5%D1%81%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F-%D0%B3%D0%BE%D1%80%D1%83%D1%82%D0%B8%D0%BD)
  - [11.2 Стратегии](#112-%D1%81%D1%82%D1%80%D0%B0%D1%82%D0%B5%D0%B3%D0%B8%D0%B8)
    - [WaitGroup для синхронизации](#waitgroup-%D0%B4%D0%BB%D1%8F-%D1%81%D0%B8%D0%BD%D1%85%D1%80%D0%BE%D0%BD%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D0%B8)
    - [Context для таймаутов](#context-%D0%B4%D0%BB%D1%8F-%D1%82%D0%B0%D0%B9%D0%BC%D0%B0%D1%83%D1%82%D0%BE%D0%B2)
  - [11.3 goleak: обнаружение утечек](#113-goleak-%D0%BE%D0%B1%D0%BD%D0%B0%D1%80%D1%83%D0%B6%D0%B5%D0%BD%D0%B8%D0%B5-%D1%83%D1%82%D0%B5%D1%87%D0%B5%D0%BA)
- [12. Новые возможности тестирования (Go 1.24-1.25)](#12-%D0%BD%D0%BE%D0%B2%D1%8B%D0%B5-%D0%B2%D0%BE%D0%B7%D0%BC%D0%BE%D0%B6%D0%BD%D0%BE%D1%81%D1%82%D0%B8-%D1%82%D0%B5%D1%81%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F-go-124-125)
  - [12.1 testing.T.Context() — контекст теста (Go 1.24)](#121-testingtcontext--%D0%BA%D0%BE%D0%BD%D1%82%D0%B5%D0%BA%D1%81%D1%82-%D1%82%D0%B5%D1%81%D1%82%D0%B0-go-124)
  - [12.2 testing.B.Loop() — надёжные бенчмарки (Go 1.24)](#122-testingbloop--%D0%BD%D0%B0%D0%B4%D1%91%D0%B6%D0%BD%D1%8B%D0%B5-%D0%B1%D0%B5%D0%BD%D1%87%D0%BC%D0%B0%D1%80%D0%BA%D0%B8-go-124)
  - [12.3 testing/synctest — детерминированное тестирование конкурентности (Go 1.25)](#123-testingsynctest--%D0%B4%D0%B5%D1%82%D0%B5%D1%80%D0%BC%D0%B8%D0%BD%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%BD%D0%BE%D0%B5-%D1%82%D0%B5%D1%81%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5-%D0%BA%D0%BE%D0%BD%D0%BA%D1%83%D1%80%D0%B5%D0%BD%D1%82%D0%BD%D0%BE%D1%81%D1%82%D0%B8-go-125)
- [Практические примеры](#%D0%BF%D1%80%D0%B0%D0%BA%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B5-%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80%D1%8B)
  - [Пример 1: UserService с полным покрытием](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-1-userservice-%D1%81-%D0%BF%D0%BE%D0%BB%D0%BD%D1%8B%D0%BC-%D0%BF%D0%BE%D0%BA%D1%80%D1%8B%D1%82%D0%B8%D0%B5%D0%BC)
  - [Пример 2: Rate Limiter с concurrent тестами](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-2-rate-limiter-%D1%81-concurrent-%D1%82%D0%B5%D1%81%D1%82%D0%B0%D0%BC%D0%B8)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

---

## Введение

В [разделе 1.4](../part1-basics/04_practice.md) мы писали практические проекты, но тестирование было минимальным. Теперь, когда мы изучили продвинутые темы ([горутины](./01_goroutines_channels.md), [GC](./03_gc.md), [синхронизацию](./04_sync_primitives.md), [обработку ошибок](./05_error_handling.md)), пришло время научиться тестировать сложный Go код на уровне production.

В этом разделе мы рассмотрим:
- **testing package** — минималистичный подход Go vs богатые фреймворки C# (xUnit, NUnit, MSTest)
- **Table-driven tests** — идиоматичный Go паттерн vs [Theory]/[InlineData]
- **Мокирование** — интерфейсы и code generation vs Moq/NSubstitute
- **Benchmarks** — встроенные бенчмарки vs BenchmarkDotNet
- **Fuzzing** — новая фича Go 1.18+ для обнаружения багов
- **Integration тесты** — httptest, testcontainers, БД
- **Race detector** — обнаружение data races (критично для конкурентного кода)
- **Coverage** — измерение покрытия кода

> 💡 **Для C# разработчиков**: В C# вы привыкли к богатым assertion библиотекам (FluentAssertions, Shouldly), атрибутам ([Test], [Theory]) и мощным фреймворкам (xUnit, NUnit). В Go философия другая: **простота и минимализм**. Стандартная библиотека `testing` предоставляет только базовые возможности (`t.Error()`, `t.Fatal()`), а идиоматичные паттерны (table-driven tests, subtests) заменяют многие фичи фреймворков. Это делает тесты более читаемыми и предсказуемыми.

### Сравнительная таблица: C# vs Go тестирование

| Аспект | C# (xUnit/NUnit/MSTest) | Go (testing) |
|--------|-------------------------|--------------|
| **Фреймворк** | Сторонние (xUnit, NUnit, MSTest) | Встроенный (`testing` package) |
| **Атрибуты** | `[Test]`, `[Theory]`, `[Fact]` | Соглашение по именованию: `func TestXxx(t *testing.T)` |
| **Параметризация** | `[InlineData]`, `[MemberData]` | **Table-driven tests** (идиома Go) |
| **Assertions** | Rich: `Assert.Equal()`, FluentAssertions | Минималистичные: `t.Error()`, `t.Fatal()` |
| **Setup/Teardown** | `IClassFixture`, `[SetUp]`, `[TearDown]` | `TestMain()`, `defer`, `t.Cleanup()` |
| **Subtests** | Nested classes | `t.Run(name, func)` |
| **Mocking** | Moq, NSubstitute (reflection-based) | Интерфейсы + `gomock`/`testify` (code gen) |
| **Benchmarks** | BenchmarkDotNet (отдельный пакет) | Встроенные: `func BenchmarkXxx(b *testing.B)` |
| **Fuzzing** | ❌ Нет в стандарте (сторонние) | ✅ Встроенный с Go 1.18+: `func FuzzXxx(f *testing.F)` |
| **Race detection** | Thread Sanitizer (LLVM, внешний) | ✅ Встроенный: `go test -race` |
| **Coverage** | Visual Studio, dotCover | ✅ Встроенный: `go test -cover` |
| **Parallel** | `[Theory]` автоматически | `t.Parallel()` (явно) |
| **Фильтрация** | `dotnet test --filter` | `go test -run TestName` |

---

## 1. testing package: основы

### 1.1 Структура тестов

В Go тесты — это обычные функции с определенной сигнатурой. Ключевые соглашения:

1. **Имя файла**: `*_test.go` (например, `user_test.go` для `user.go`)
2. **Имя функции**: `func TestXxx(t *testing.T)` (начинается с `Test`, затем заглавная буква)
3. **Расположение**: в том же пакете или в отдельном (`package xxx_test`)

#### Сравнение: C# vs Go

**C# (xUnit)**:
```csharp
// UserServiceTests.cs
using Xunit;

public class UserServiceTests
{
    [Fact]
    public void GetUser_ValidId_ReturnsUser()
    {
        // Arrange
        var service = new UserService();

        // Act
        var user = service.GetUser(1);

        // Assert
        Assert.NotNull(user);
        Assert.Equal("Alice", user.Name);
    }

    [Theory]
    [InlineData(1, "Alice")]
    [InlineData(2, "Bob")]
    public void GetUser_MultipleIds_ReturnsCorrectUser(int id, string expectedName)
    {
        var service = new UserService();
        var user = service.GetUser(id);
        Assert.Equal(expectedName, user.Name);
    }
}
```

**Go (идиоматично)**:
```go
// user_test.go
package user

import "testing"

// Simple unit test
func TestGetUser(t *testing.T) {
    service := NewUserService()

    user, err := service.GetUser(1)
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }

    if user.Name != "Alice" {
        t.Errorf("expected name %q, got %q", "Alice", user.Name)
    }
}

// Table-driven test (вместо [Theory])
func TestGetUser_TableDriven(t *testing.T) {
    service := NewUserService()

    tests := []struct {
        name         string
        id           int
        expectedName string
    }{
        {"Alice", 1, "Alice"},
        {"Bob", 2, "Bob"},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            user, err := service.GetUser(tt.id)
            if err != nil {
                t.Fatalf("unexpected error: %v", err)
            }
            if user.Name != tt.expectedName {
                t.Errorf("expected %q, got %q", tt.expectedName, user.Name)
            }
        })
    }
}
```

#### Ключевые различия

| Аспект | C# | Go |
|--------|----|----|
| **Атрибуты** | `[Fact]`, `[Theory]` | Соглашение: `func TestXxx(t *testing.T)` |
| **Файл** | `UserServiceTests.cs` | `user_test.go` (суффикс `_test`) |
| **Класс** | Требуется | ❌ Не нужен (пакетная функция) |
| **Assertions** | `Assert.Equal()`, `Assert.NotNull()` | `t.Error()`, `t.Errorf()`, `t.Fatal()` |
| **Параметризация** | `[InlineData]` | Table-driven pattern (struct slice) |

> 💡 **Идиома Go**: Тесты находятся в том же пакете (`package user`), что позволяет тестировать unexported функции. Для тестирования только публичного API используйте `package user_test`.

#### testing.T методы

```go
// t.Error / t.Errorf — помечает тест как failed, НО продолжает выполнение
t.Error("something went wrong")
t.Errorf("expected %d, got %d", 10, result)

// t.Fatal / t.Fatalf — помечает failed и НЕМЕДЛЕННО останавливает тест
t.Fatal("critical failure, stop test")
t.Fatalf("expected user, got nil")

// t.Log / t.Logf — выводит в консоль (только с флагом -v)
t.Logf("Processing user ID: %d", userID)

// t.Skip / t.Skipf — пропускает тест (например, если нет БД)
if testing.Short() {
    t.Skip("skipping integration test in short mode")
}

// t.Cleanup — регистрирует функцию cleanup (Go 1.14+)
t.Cleanup(func() {
    db.Close()
})
```

**Когда использовать `Error` vs `Fatal`?**

```go
func TestUser(t *testing.T) {
    user, err := GetUser(1)

    // Fatal: если ошибка критична и дальше тестировать нет смысла
    if err != nil {
        t.Fatalf("failed to get user: %v", err)
    }

    // Error: если можно продолжить проверки
    if user.Name != "Alice" {
        t.Errorf("expected name Alice, got %s", user.Name)
    }

    if user.Age != 30 {
        t.Errorf("expected age 30, got %d", user.Age)
    }
}
```

---

### 1.2 Запуск тестов

#### Базовые команды

```bash
# Запуск всех тестов в текущем пакете
go test

# Verbose output (показывает t.Log и имена тестов)
go test -v

# Запуск тестов рекурсивно во всех подпакетах
go test ./...

# Запуск конкретного теста (regex)
go test -run TestGetUser

# Запуск конкретного subtest
go test -run TestGetUser/Alice

# Запуск в "short mode" (пропускает медленные тесты)
go test -short

# Параллельный запуск
go test -parallel 4

# Запуск N раз (для проверки flaky tests)
go test -count=10
```

#### Сравнение: dotnet test vs go test

| Задача | C# (`dotnet test`) | Go (`go test`) |
|--------|-------------------|----------------|
| Все тесты | `dotnet test` | `go test` |
| Verbose | `dotnet test -v detailed` | `go test -v` |
| Фильтр | `dotnet test --filter FullyQualifiedName~GetUser` | `go test -run GetUser` |
| Параллельность | Автоматически | `go test -parallel N` |
| Coverage | `dotnet test --collect:"XPlat Code Coverage"` | `go test -cover` |
| Рекурсивно | `dotnet test` (ищет .csproj) | `go test ./...` |

#### Пример вывода

```bash
$ go test -v
=== RUN   TestGetUser
--- PASS: TestGetUser (0.00s)
=== RUN   TestGetUser_TableDriven
=== RUN   TestGetUser_TableDriven/Alice
=== RUN   TestGetUser_TableDriven/Bob
--- PASS: TestGetUser_TableDriven (0.00s)
    --- PASS: TestGetUser_TableDriven/Alice (0.00s)
    --- PASS: TestGetUser_TableDriven/Bob (0.00s)
PASS
ok      github.com/user/myapp    0.123s
```

---

### 1.3 Setup/Teardown

В C# вы используете `IClassFixture`, `[SetUp]`, `[TearDown]` для инициализации. В Go подход проще и явнее.

#### Способ 1: TestMain (package-level setup)

`TestMain` запускается **один раз** перед всеми тестами пакета. Используется для глобальной инициализации (БД, конфиги и т.д.).

**C# (xUnit)**:
```csharp
public class DatabaseFixture : IDisposable
{
    public Database DB { get; private set; }

    public DatabaseFixture()
    {
        DB = new Database("test_connection");
        DB.Migrate();
    }

    public void Dispose()
    {
        DB.Close();
    }
}

public class UserServiceTests : IClassFixture<DatabaseFixture>
{
    private readonly Database _db;

    public UserServiceTests(DatabaseFixture fixture)
    {
        _db = fixture.DB;
    }

    [Fact]
    public void Test1() { /* использует _db */ }
}
```

**Go (TestMain)**:
```go
package user

import (
    "testing"
    "os"
)

var testDB *Database

// TestMain запускается ПЕРЕД всеми тестами
func TestMain(m *testing.M) {
    // Setup
    testDB = setupTestDatabase()
    testDB.Migrate()

    // Запуск тестов
    code := m.Run()

    // Teardown (выполняется ВСЕГДА, даже если тесты упали)
    testDB.Close()

    // Выход с кодом (0 = success, 1 = failure)
    os.Exit(code)
}

func TestGetUser(t *testing.T) {
    // testDB доступен здесь
    user, err := GetUserFromDB(testDB, 1)
    if err != nil {
        t.Fatal(err)
    }
    // ...
}
```

> ⚠️ **Важно**: `TestMain` используется редко, только для тяжелой инициализации (БД, внешние сервисы). Для простых случаев используйте `t.Cleanup()` или `defer`.

#### Способ 2: defer (для простого cleanup)

```go
func TestWithCleanup(t *testing.T) {
    // Setup
    file, err := os.CreateTemp("", "test")
    if err != nil {
        t.Fatal(err)
    }
    defer os.Remove(file.Name()) // Cleanup через defer

    // Test logic
    _, err = file.WriteString("test data")
    if err != nil {
        t.Fatal(err)
    }

    // defer вызовется автоматически при выходе из функции
}
```

#### Способ 3: t.Cleanup() (Go 1.14+, идиоматично)

`t.Cleanup()` удобнее `defer`, так как cleanup запускается **после всех subtests**.

```go
func TestWithCleanup(t *testing.T) {
    // Setup
    db := setupDatabase()

    // Регистрируем cleanup (выполнится в конце теста)
    t.Cleanup(func() {
        db.Close()
    })

    // Test logic
    user, err := db.GetUser(1)
    if err != nil {
        t.Fatal(err)
    }

    // Можно вызвать t.Fatal() — cleanup всё равно выполнится
}
```

**Сравнение: defer vs t.Cleanup()**

```go
func TestDeferVsCleanup(t *testing.T) {
    // defer выполняется СРАЗУ при выходе из функции
    defer fmt.Println("defer cleanup")

    // t.Cleanup выполняется ПОСЛЕ всех subtests
    t.Cleanup(func() {
        fmt.Println("t.Cleanup cleanup")
    })

    t.Run("subtest1", func(t *testing.T) {
        fmt.Println("subtest1")
    })

    t.Run("subtest2", func(t *testing.T) {
        fmt.Println("subtest2")
    })
}

// Вывод:
// subtest1
// subtest2
// t.Cleanup cleanup
// defer cleanup
```

> 💡 **Идиома Go**: Предпочитайте `t.Cleanup()` для cleanup в тестах с subtests. Для простых случаев `defer` тоже подходит.

---

## 2. Table-Driven Tests (идиоматичный Go)

**Table-driven tests** — это **идиоматичный** паттерн тестирования в Go. Он заменяет атрибуты `[Theory]`/`[InlineData]` из C#.

### 2.1 Паттерн Table-Driven

Идея: создать **slice структур** с тестовыми случаями и прогнать их в цикле.

#### Сравнение: C# [Theory] vs Go table-driven

**C# (xUnit)**:
```csharp
[Theory]
[InlineData("user@example.com", true)]
[InlineData("invalid-email", false)]
[InlineData("", false)]
[InlineData("test@", false)]
public void IsValidEmail_VariousInputs_ReturnsExpected(string email, bool expected)
{
    var result = EmailValidator.IsValid(email);
    Assert.Equal(expected, result);
}
```

**Go (table-driven test)**:
```go
func TestIsValidEmail(t *testing.T) {
    // Таблица тестовых случаев
    tests := []struct {
        name     string // Описание case
        email    string // Входные данные
        expected bool   // Ожидаемый результат
    }{
        {"valid email", "user@example.com", true},
        {"missing @", "invalid-email", false},
        {"empty string", "", false},
        {"incomplete domain", "test@", false},
        {"no domain", "user@", false},
        {"unicode email", "пользователь@пример.рф", true}, // Go поддерживает unicode
    }

    // Прогоняем все cases
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := IsValidEmail(tt.email)
            if result != tt.expected {
                t.Errorf("IsValidEmail(%q) = %v, expected %v", tt.email, result, tt.expected)
            }
        })
    }
}
```

#### Анатомия table-driven теста

```go
tests := []struct {
    // 1. name — описание case (отображается в выводе)
    name string

    // 2. Входные параметры
    input  string
    userID int

    // 3. Ожидаемые результаты
    want      string
    wantError bool

    // 4. (Опционально) Setup функция для этого case
    setupFunc func()
}{
    {
        name:      "success case",
        input:     "valid",
        userID:    1,
        want:      "result",
        wantError: false,
    },
    // ...
}
```

---

### 2.2 Преимущества подхода

| Преимущество | C# [Theory] | Go table-driven |
|--------------|-------------|-----------------|
| **Читаемость** | Атрибуты могут быть далеко от кода | ✅ Все данные рядом с логикой |
| **Добавление случаев** | Новый `[InlineData]` | ✅ Новая строка в slice |
| **Именование** | Генерируется автоматически | ✅ Явное поле `name` |
| **Сложные структуры** | `[MemberData]` требует отдельный метод | ✅ Inline в slice |
| **Переиспользование** | Сложно | ✅ Можно вынести `tests` в переменную |
| **Отладка** | Атрибуты скрывают детали | ✅ Обычный Go код |

**Пример: сложные структуры**

```go
func TestProcessOrder(t *testing.T) {
    tests := []struct {
        name  string
        order Order
        want  OrderResult
    }{
        {
            name: "order with discount",
            order: Order{
                ID:    1,
                Items: []Item{{Name: "Book", Price: 100}},
                User:  User{ID: 1, HasDiscount: true},
            },
            want: OrderResult{
                Total:        90,
                DiscountUsed: true,
            },
        },
        {
            name: "order without items",
            order: Order{
                ID:    2,
                Items: []Item{},
                User:  User{ID: 2},
            },
            want: OrderResult{
                Total: 0,
                Error: ErrNoItems,
            },
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := ProcessOrder(tt.order)
            if result != tt.want {
                t.Errorf("got %+v, want %+v", result, tt.want)
            }
        })
    }
}
```

---

### 2.3 Продвинутые техники

#### Техника 1: Именованные поля (описательность)

Вместо позиционных параметров используйте **именованные поля**.

```go
// ❌ Плохо: непонятно, что означают параметры
tests := []struct {
    string
    int
    bool
}{
    {"test", 10, true},
}

// ✅ Хорошо: явные имена полей
tests := []struct {
    name     string
    input    int
    expected bool
}{
    {name: "positive", input: 10, expected: true},
}
```

#### Техника 2: Setup/Teardown для каждого case

```go
func TestWithPerCaseSetup(t *testing.T) {
    tests := []struct {
        name      string
        setupFunc func() *Database
        input     int
    }{
        {
            name: "with real DB",
            setupFunc: func() *Database {
                return setupRealDB()
            },
            input: 1,
        },
        {
            name: "with mock DB",
            setupFunc: func() *Database {
                return setupMockDB()
            },
            input: 2,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            db := tt.setupFunc()
            defer db.Close()

            result := db.Query(tt.input)
            // ...
        })
    }
}
```

#### Техника 3: Параллелизация table tests

```go
func TestParallel(t *testing.T) {
    tests := []struct {
        name  string
        input int
    }{
        {"case1", 1},
        {"case2", 2},
        {"case3", 3},
    }

    for _, tt := range tests {
        tt := tt // Копируем переменную цикла (до Go 1.22)

        t.Run(tt.name, func(t *testing.T) {
            t.Parallel() // Запускаем subtests параллельно

            result := SlowFunction(tt.input)
            // ...
        })
    }
}
```

> ⚠️ **Go 1.22+**: Начиная с Go 1.22, переменные цикла имеют область видимости внутри итерации, поэтому `tt := tt` больше не требуется. В более старых версиях это обязательно!

---

## 3. Subtests (t.Run)

### 3.1 Организация вложенных тестов

`t.Run()` позволяет создавать **иерархию тестов** и запускать их независимо. Это аналог nested classes в C#.

#### Сравнение: C# Nested classes vs Go t.Run

**C# (xUnit)**:
```csharp
public class UserServiceTests
{
    public class GetUserTests
    {
        [Fact]
        public void ValidId_ReturnsUser() { }

        [Fact]
        public void InvalidId_ReturnsNull() { }
    }

    public class CreateUserTests
    {
        [Fact]
        public void ValidData_CreatesUser() { }

        [Fact]
        public void DuplicateEmail_ThrowsException() { }
    }
}
```

**Go (t.Run)**:
```go
func TestUserService(t *testing.T) {
    t.Run("GetUser", func(t *testing.T) {
        t.Run("valid ID", func(t *testing.T) {
            user, err := GetUser(1)
            if err != nil {
                t.Fatal(err)
            }
            // ...
        })

        t.Run("invalid ID", func(t *testing.T) {
            user, err := GetUser(-1)
            if user != nil {
                t.Errorf("expected nil, got %v", user)
            }
        })
    })

    t.Run("CreateUser", func(t *testing.T) {
        t.Run("valid data", func(t *testing.T) {
            user, err := CreateUser("alice@example.com")
            if err != nil {
                t.Fatal(err)
            }
            // ...
        })

        t.Run("duplicate email", func(t *testing.T) {
            _, err := CreateUser("existing@example.com")
            if err == nil {
                t.Error("expected error for duplicate email")
            }
        })
    })
}
```

#### Запуск конкретного subtest

```bash
# Запустить весь тест
go test -run TestUserService

# Запустить только GetUser subtests
go test -run TestUserService/GetUser

# Запустить конкретный subtest
go test -run TestUserService/GetUser/valid

# Regex тоже работает
go test -run TestUserService/.*valid
```

> 💡 **Идиома Go**: Используйте `t.Run()` для группировки связанных тестов. Это удобнее, чем создавать отдельные `TestGetUser_ValidID`, `TestGetUser_InvalidID` и т.д.

---

### 3.2 Parallel subtests

`t.Parallel()` запускает subtests **параллельно**. Это ускоряет медленные тесты (I/O, network, БД).

#### Сравнение: C# [Theory] vs Go t.Parallel

**C# (xUnit)** — параллелизм автоматический:
```csharp
[Theory]
[InlineData(1)]
[InlineData(2)]
[InlineData(3)]
public async Task SlowTest(int id)
{
    // xUnit по умолчанию запускает каждый case параллельно
    await Task.Delay(1000);
}
```

**Go** — параллелизм явный:
```go
func TestSlow(t *testing.T) {
    tests := []int{1, 2, 3}

    for _, id := range tests {
        id := id // Копируем (до Go 1.22)

        t.Run(fmt.Sprintf("case_%d", id), func(t *testing.T) {
            t.Parallel() // Явно включаем параллелизм

            time.Sleep(1 * time.Second)
            // ...
        })
    }
}
```

#### Важные правила t.Parallel()

**Правило 1**: `t.Parallel()` блокирует выполнение до завершения родительского теста

```go
func TestParallelRules(t *testing.T) {
    fmt.Println("Parent start")

    t.Run("child1", func(t *testing.T) {
        t.Parallel()
        fmt.Println("Child1 start")
        time.Sleep(1 * time.Second)
        fmt.Println("Child1 end")
    })

    t.Run("child2", func(t *testing.T) {
        t.Parallel()
        fmt.Println("Child2 start")
        time.Sleep(1 * time.Second)
        fmt.Println("Child2 end")
    })

    fmt.Println("Parent end") // Выполнится ПОСЛЕ child1 и child2
}

// Вывод:
// Parent start
// Child1 start
// Child2 start
// (1 секунда, параллельно)
// Child1 end
// Child2 end
// Parent end
```

**Правило 2**: Изолируйте состояние между параллельными тестами

```go
// ❌ ПЛОХО: race condition
func TestRaceCondition(t *testing.T) {
    counter := 0

    for i := 0; i < 10; i++ {
        t.Run(fmt.Sprintf("case_%d", i), func(t *testing.T) {
            t.Parallel()
            counter++ // Race! Несколько горутин пишут в counter
        })
    }
}

// ✅ ХОРОШО: изолированное состояние
func TestIsolated(t *testing.T) {
    for i := 0; i < 10; i++ {
        i := i // Копируем переменную

        t.Run(fmt.Sprintf("case_%d", i), func(t *testing.T) {
            t.Parallel()

            // Каждый subtest имеет свою копию i
            result := ProcessItem(i)
            if result != i*2 {
                t.Errorf("expected %d, got %d", i*2, result)
            }
        })
    }
}
```

**Правило 3**: Контролируйте параллелизм через `-parallel`

```bash
# По умолчанию GOMAXPROCS (количество CPU)
go test -parallel 4

# Ограничить до 1 (последовательно)
go test -parallel 1
```

---

### 3.3 Интеграция с table-driven

Комбинация table-driven + t.Run + t.Parallel — **самый идиоматичный паттерн** в Go.

```go
func TestUserValidation(t *testing.T) {
    tests := []struct {
        name      string
        user      User
        wantError bool
    }{
        {
            name:      "valid user",
            user:      User{Name: "Alice", Email: "alice@example.com"},
            wantError: false,
        },
        {
            name:      "empty name",
            user:      User{Name: "", Email: "alice@example.com"},
            wantError: true,
        },
        {
            name:      "invalid email",
            user:      User{Name: "Bob", Email: "not-an-email"},
            wantError: true,
        },
    }

    for _, tt := range tests {
        tt := tt // Копируем (до Go 1.22)

        t.Run(tt.name, func(t *testing.T) {
            t.Parallel() // Параллельные subtests

            err := ValidateUser(tt.user)

            if tt.wantError && err == nil {
                t.Error("expected error, got nil")
            }
            if !tt.wantError && err != nil {
                t.Errorf("unexpected error: %v", err)
            }
        })
    }
}
```

**Вывод с `-v`:**
```
=== RUN   TestUserValidation
=== RUN   TestUserValidation/valid_user
=== RUN   TestUserValidation/empty_name
=== RUN   TestUserValidation/invalid_email
=== PAUSE TestUserValidation/valid_user
=== PAUSE TestUserValidation/empty_name
=== PAUSE TestUserValidation/invalid_email
=== CONT  TestUserValidation/valid_user
=== CONT  TestUserValidation/invalid_email
=== CONT  TestUserValidation/empty_name
--- PASS: TestUserValidation (0.00s)
    --- PASS: TestUserValidation/valid_user (0.00s)
    --- PASS: TestUserValidation/invalid_email (0.00s)
    --- PASS: TestUserValidation/empty_name (0.00s)
```

---

## 4. Мокирование и тестирование зависимостей

### 4.1 Интерфейсы для тестируемости

В C# мокирование основано на **reflection** (Moq, NSubstitute). В Go используются **интерфейсы** — более явный и type-safe подход.

#### Принцип: Accept interfaces, return structs

```go
// ❌ ПЛОХО: функция принимает конкретный тип
func ProcessUser(db *sql.DB, userID int) error {
    // Невозможно подставить mock без реальной БД
}

// ✅ ХОРОШО: функция принимает интерфейс
type UserRepository interface {
    GetUser(id int) (*User, error)
}

func ProcessUser(repo UserRepository, userID int) error {
    user, err := repo.GetUser(userID)
    // ...
}
```

Теперь можно легко подставить mock:

```go
type MockUserRepository struct {
    GetUserFunc func(id int) (*User, error)
}

func (m *MockUserRepository) GetUser(id int) (*User, error) {
    return m.GetUserFunc(id)
}

// В тесте
func TestProcessUser(t *testing.T) {
    mock := &MockUserRepository{
        GetUserFunc: func(id int) (*User, error) {
            return &User{ID: id, Name: "Alice"}, nil
        },
    }

    err := ProcessUser(mock, 1)
    if err != nil {
        t.Fatal(err)
    }
}
```

#### Сравнение: C# Moq vs Go интерфейсы

**C# (Moq)**:
```csharp
public interface IUserRepository
{
    User GetUser(int id);
}

public class UserService
{
    private readonly IUserRepository _repo;
    public UserService(IUserRepository repo) => _repo = repo;

    public void ProcessUser(int id)
    {
        var user = _repo.GetUser(id);
        // ...
    }
}

// Тест
[Fact]
public void ProcessUser_ValidId_Success()
{
    var mockRepo = new Mock<IUserRepository>();
    mockRepo.Setup(r => r.GetUser(1))
            .Returns(new User { Id = 1, Name = "Alice" });

    var service = new UserService(mockRepo.Object);
    service.ProcessUser(1);

    mockRepo.Verify(r => r.GetUser(1), Times.Once);
}
```

**Go (ручной mock)**:
```go
type UserRepository interface {
    GetUser(id int) (*User, error)
}

type UserService struct {
    repo UserRepository
}

func NewUserService(repo UserRepository) *UserService {
    return &UserService{repo: repo}
}

func (s *UserService) ProcessUser(id int) error {
    user, err := s.repo.GetUser(id)
    // ...
}

// Тест
type MockUserRepository struct {
    GetUserCalled int
    GetUserFunc   func(id int) (*User, error)
}

func (m *MockUserRepository) GetUser(id int) (*User, error) {
    m.GetUserCalled++
    return m.GetUserFunc(id)
}

func TestProcessUser(t *testing.T) {
    mock := &MockUserRepository{
        GetUserFunc: func(id int) (*User, error) {
            return &User{ID: id, Name: "Alice"}, nil
        },
    }

    service := NewUserService(mock)
    err := service.ProcessUser(1)

    if err != nil {
        t.Fatal(err)
    }

    if mock.GetUserCalled != 1 {
        t.Errorf("expected 1 call, got %d", mock.GetUserCalled)
    }
}
```

---

### 4.2 Ручные моки (идиоматично)

Для **простых случаев** ручные моки предпочтительнее генерации.

#### Паттерн 1: Функциональный mock

```go
type EmailSender interface {
    Send(to, subject, body string) error
}

type MockEmailSender struct {
    SendFunc func(to, subject, body string) error
}

func (m *MockEmailSender) Send(to, subject, body string) error {
    if m.SendFunc != nil {
        return m.SendFunc(to, subject, body)
    }
    return nil
}

// Использование
func TestNotifyUser(t *testing.T) {
    var sentTo string

    mock := &MockEmailSender{
        SendFunc: func(to, subject, body string) error {
            sentTo = to
            return nil
        },
    }

    NotifyUser(mock, "user@example.com", "Hello")

    if sentTo != "user@example.com" {
        t.Errorf("expected email to %q, sent to %q", "user@example.com", sentTo)
    }
}
```

#### Паттерн 2: Mock с состоянием

```go
type MockCache struct {
    Data  map[string]string
    Calls []string
}

func (m *MockCache) Get(key string) (string, bool) {
    m.Calls = append(m.Calls, "Get:"+key)
    val, ok := m.Data[key]
    return val, ok
}

func (m *MockCache) Set(key, value string) {
    m.Calls = append(m.Calls, "Set:"+key)
    if m.Data == nil {
        m.Data = make(map[string]string)
    }
    m.Data[key] = value
}
```

---

### 4.3 gomock (code generation)

Для сложных интерфейсов удобно использовать **gomock**.

#### Установка
```bash
go install github.com/golang/mock/mockgen@latest
```

#### Генерация моков
```go
//go:generate mockgen -destination=mocks/mock_repository.go -package=mocks . UserRepository

type UserRepository interface {
    GetUser(id int) (*User, error)
    CreateUser(user *User) error
}
```

```bash
go generate ./...
```

#### Использование
```go
import (
    "testing"
    "github.com/golang/mock/gomock"
    "myapp/mocks"
}

func TestUserService_GetUser(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockRepo := mocks.NewMockUserRepository(ctrl)

    mockRepo.EXPECT().
        GetUser(1).
        Return(&User{ID: 1, Name: "Alice"}, nil).
        Times(1)

    service := NewUserService(mockRepo)
    user, err := service.GetUser(1)

    if err != nil || user.Name != "Alice" {
        t.Fatal("test failed")
    }
}
```

| Аспект | C# Moq | Go gomock |
|--------|--------|-----------|
| **Генерация** | Runtime (reflection) | Code generation |
| **Type safety** | ❌ Runtime | ✅ Compile-time |
| **Setup** | `mock.Setup(...)` | `mock.EXPECT()...` |
| **Verification** | `mock.Verify(...)` | Автоматически |

---

### 4.4 testify/mock

Альтернатива gomock без code generation.

```bash
go get github.com/stretchr/testify
```

```go
import (
    "testing"
    "github.com/stretchr/testify/mock"
    "github.com/stretchr/testify/assert"
)

type MockUserRepository struct {
    mock.Mock
}

func (m *MockUserRepository) GetUser(id int) (*User, error) {
    args := m.Called(id)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*User), args.Error(1)
}

func TestUserService(t *testing.T) {
    mockRepo := new(MockUserRepository)
    mockRepo.On("GetUser", 1).Return(&User{ID: 1, Name: "Alice"}, nil)

    service := NewUserService(mockRepo)
    user, err := service.GetUser(1)

    assert.NoError(t, err)
    assert.Equal(t, "Alice", user.Name)
    mockRepo.AssertExpectations(t)
}
```

**testify/assert** (Rich assertions):
```go
assert.Equal(t, 10, result)
assert.NotNil(t, result)
assert.Contains(t, []int{1, 2, 3}, result)
```

| Подход | Когда использовать |
|--------|-------------------|
| **Ручные моки** | Простые интерфейсы (1-3 метода) |
| **gomock** | Сложные интерфейсы, compile-time safety |
| **testify/mock** | Средняя сложность |

> 💡 **Идиома Go**: Для большинства случаев **ручные моки** предпочтительнее.

---

## 5. Benchmarks: производительность

### 5.1 Основы бенчмаркинга

Benchmarks в Go встроены в `testing` package, в отличие от C# где нужен BenchmarkDotNet.

#### Сравнение: BenchmarkDotNet vs Go benchmarks

**C# (BenchmarkDotNet)**:
```csharp
using BenchmarkDotNet.Attributes;
using BenchmarkDotNet.Running;

[MemoryDiagnoser]
public class StringBenchmarks
{
    [Benchmark]
    public string Concatenation()
    {
        string result = "";
        for (int i = 0; i < 1000; i++)
            result += "a";
        return result;
    }

    [Benchmark]
    public string StringBuilder()
    {
        var sb = new StringBuilder();
        for (int i = 0; i < 1000; i++)
            sb.Append("a");
        return sb.ToString();
    }
}

// Program.cs
BenchmarkRunner.Run<StringBenchmarks>();
```

**Go (встроенный)**:
```go
// string_test.go
func BenchmarkConcatenation(b *testing.B) {
    for i := 0; i < b.N; i++ {
        result := ""
        for j := 0; j < 1000; j++ {
            result += "a"
        }
        _ = result // Предотвращаем оптимизацию
    }
}

func BenchmarkStringsBuilder(b *testing.B) {
    for i := 0; i < b.N; i++ {
        var builder strings.Builder
        for j := 0; j < 1000; j++ {
            builder.WriteString("a")
        }
        _ = builder.String()
    }
}
```

```bash
# Запуск benchmarks
go test -bench=.

# С выделением памяти
go test -bench=. -benchmem
```

**Вывод**:
```
BenchmarkConcatenation-8         1000    1234567 ns/op   500000 B/op    1000 allocs/op
BenchmarkStringsBuilder-8       50000      25678 ns/op     1024 B/op       1 allocs/op
```

| Аспект | C# BenchmarkDotNet | Go testing |
|--------|-------------------|------------|
| **Установка** | NuGet пакет | Встроенный |
| **Атрибуты** | `[Benchmark]` | `func BenchmarkXxx(b *testing.B)` |
| **Memory** | `[MemoryDiagnoser]` | `-benchmem` flag |
| **Запуск** | Отдельная программа | `go test -bench=.` |
| **b.N** | Автоматически | Автоматически (iterations) |

---

### 5.2 Оптимизация benchmarks

#### b.N iterations

`b.N` — автоматически подбирается для стабильных результатов (минимум 1 секунда).

```go
func BenchmarkExample(b *testing.B) {
    // Дорогая инициализация
    data := generateTestData()

    b.ResetTimer() // ⬅ Сбрасываем таймер после setup

    for i := 0; i < b.N; i++ {
        process(data)
    }
}
```

#### b.ReportAllocs() — профилирование памяти

```go
func BenchmarkJSON(b *testing.B) {
    b.ReportAllocs() // Включает детальную статистику аллокаций

    data := `{"name":"Alice","age":30}`

    for i := 0; i < b.N; i++ {
        var user User
        json.Unmarshal([]byte(data), &user)
    }
}
```

**Вывод**:
```
BenchmarkJSON-8    500000    2345 ns/op    384 B/op    7 allocs/op
                                           ↑           ↑
                                       bytes/op    allocs/op
```

#### Предотвращение оптимизаций компилятора

```go
var result int // Глобальная переменная

func BenchmarkSum(b *testing.B) {
    var r int

    for i := 0; i < b.N; i++ {
        r = Sum(1, 2, 3, 4, 5)
    }

    result = r // ⬅ Запись в глобальную предотвращает dead code elimination
}
```

---

### 5.3 Анализ результатов

#### Метрики

```
BenchmarkName-8    1000000    1234 ns/op    256 B/op    3 allocs/op
               ↑         ↑         ↑          ↑           ↑
             CPU      b.N     time/op   bytes/op    allocs/op
```

- **ns/op**: наносекунд на операцию
- **B/op**: байт выделено на операцию
- **allocs/op**: количество аллокаций на операцию

#### benchstat — сравнение до/после

```bash
# Запускаем до изменений
go test -bench=. -count=10 > old.txt

# Вносим изменения, запускаем снова
go test -bench=. -count=10 > new.txt

# Устанавливаем benchstat
go install golang.org/x/perf/cmd/benchstat@latest

# Сравниваем
benchstat old.txt new.txt
```

**Вывод**:
```
name        old time/op    new time/op    delta
Sum-8         245ns ± 2%     123ns ± 1%   -49.80%  (p=0.000)

name        old alloc/op   new alloc/op   delta
Sum-8          256B ± 0%       0B         -100.00%  (p=0.000)
```

---

### 5.4 Memory benchmarks

#### Связь с разделом 2.3 (GC)

Из [раздела 2.3](./03_gc.md#sync-pool-для-переиспользования-объектов) мы знаем про `sync.Pool`.

**Пример: JSON парсинг с/без sync.Pool**

```go
// Без sync.Pool
func BenchmarkJSONWithoutPool(b *testing.B) {
    b.ReportAllocs()

    data := []byte(`{"name":"Alice","age":30}`)

    for i := 0; i < b.N; i++ {
        var user User
        json.Unmarshal(data, &user)
    }
}

// С sync.Pool (из раздела 2.3)
var userPool = sync.Pool{
    New: func() interface{} {
        return new(User)
    },
}

func BenchmarkJSONWithPool(b *testing.B) {
    b.ReportAllocs()

    data := []byte(`{"name":"Alice","age":30}`)

    for i := 0; i < b.N; i++ {
        user := userPool.Get().(*User)
        json.Unmarshal(data, user)
        userPool.Put(user) // Возвращаем в pool
    }
}
```

**Результаты**:
```
BenchmarkJSONWithoutPool-8    500000    2345 ns/op    384 B/op    7 allocs/op
BenchmarkJSONWithPool-8       800000    1456 ns/op     48 B/op    2 allocs/op
```

> 💡 **Идиома Go**: Используйте benchmarks для проверки влияния оптимизаций. Связь с GC (раздел 2.3): меньше аллокаций → меньше работы для GC → меньше пауз.

---

## 6. Fuzzing (Go 1.18+)

### 6.1 Введение в fuzzing

**Fuzzing** — автоматическая генерация входных данных для поиска багов. Go 1.18+ имеет встроенный fuzzing.

> 💡 **Для C# разработчиков**: В C# нет встроенного fuzzing (есть сторонние: Microsoft.CodeAnalysis.FuzzTesting, SharpFuzz). В Go это часть стандартной библиотеки.

#### Сигнатура fuzz-теста

```go
func FuzzXxx(f *testing.F) {
    // ...
}
```

---

### 6.2 Написание fuzz-тестов

```go
func FuzzURLParse(f *testing.F) {
    // Seed corpus (начальные данные)
    f.Add("https://example.com/path?query=value")
    f.Add("http://localhost:8080")
    f.Add("ftp://ftp.example.com")

    // Fuzz callback
    f.Fuzz(func(t *testing.T, url string) {
        // Go будет генерировать различные строки
        parsed, err := ParseCustomURL(url)

        // Проверяем, что не было паники
        if err != nil {
            return // Ошибка — нормально
        }

        // Проверяем инварианты
        if parsed.Scheme == "" && parsed.Host != "" {
            t.Errorf("invalid state: host without scheme")
        }
    })
}
```

**Запуск fuzzing**:
```bash
# Fuzzing (запускается до первой ошибки или Ctrl+C)
go test -fuzz=FuzzURLParse

# Fuzzing 30 секунд
go test -fuzz=FuzzURLParse -fuzztime=30s

# Только unit-тесты (без fuzzing)
go test
```

**Corpus** (найденные inputs) сохраняется в `testdata/fuzz/FuzzURLParse/`:
```
testdata/fuzz/FuzzURLParse/
├── corpus
│   └── 8f3e... (hex-encoded inputs)
└── seed (начальные данные)
```

---

### 6.3 Когда использовать

| Задача | Использовать fuzzing? |
|--------|----------------------|
| **Парсеры** (JSON, XML, custom) | ✅ Да, находит edge cases |
| **Валидаторы** (email, URL) | ✅ Да, проверяет граничные случаи |
| **Криптография** | ✅ Да, находит уязвимости |
| **Бизнес-логика** | ⚠️ Редко (сложно проверять инварианты) |
| **CRUD операции** | ❌ Нет (лучше property-based testing) |

**Краткий пример**:
```go
func FuzzEmailValidator(f *testing.F) {
    f.Add("test@example.com")

    f.Fuzz(func(t *testing.T, email string) {
        valid := IsValidEmail(email)

        // Инвариант: если валидный, должен содержать @
        if valid && !strings.Contains(email, "@") {
            t.Errorf("email %q valid but no @", email)
        }
    })
}
```

---

## 7. Integration Tests

### 7.1 httptest: тестирование HTTP handlers

**httptest** — встроенный пакет для тестирования HTTP. Аналог TestServer в ASP.NET Core.

#### Сравнение: ASP.NET Core TestServer vs Go httptest

**C# (ASP.NET Core)**:
```csharp
public class UserControllerTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public UserControllerTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task GetUser_ValidId_ReturnsOk()
    {
        var response = await _client.GetAsync("/api/users/1");
        response.EnsureSuccessStatusCode();

        var user = await response.Content.ReadFromJsonAsync<User>();
        Assert.Equal("Alice", user.Name);
    }
}
```

**Go (httptest)**:
```go
func TestUserHandler(t *testing.T) {
    // Создаём handler
    handler := http.HandlerFunc(GetUserHandler)

    // Создаём request
    req := httptest.NewRequest("GET", "/api/users/1", nil)

    // ResponseRecorder для захвата ответа
    rr := httptest.NewRecorder()

    // Выполняем запрос
    handler.ServeHTTP(rr, req)

    // Проверки
    if rr.Code != http.StatusOK {
        t.Errorf("expected 200, got %d", rr.Code)
    }

    var user User
    json.Unmarshal(rr.Body.Bytes(), &user)

    if user.Name != "Alice" {
        t.Errorf("expected Alice, got %s", user.Name)
    }
}
```

**httptest.Server** (для реальных HTTP вызовов):
```go
func TestAPIIntegration(t *testing.T) {
    // Создаём тестовый сервер
    ts := httptest.NewServer(http.HandlerFunc(GetUserHandler))
    defer ts.Close()

    // Делаем реальный HTTP запрос
    resp, err := http.Get(ts.URL + "/api/users/1")
    if err != nil {
        t.Fatal(err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != 200 {
        t.Errorf("expected 200, got %d", resp.StatusCode)
    }
}
```

---

### 7.2 Тестирование БД

#### SQLite (in-memory)

```go
func setupTestDB(t *testing.T) *sql.DB {
    db, err := sql.Open("sqlite3", ":memory:")
    if err != nil {
        t.Fatal(err)
    }

    // Миграции
    _, err = db.Exec(`
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT
        )
    `)
    if err != nil {
        t.Fatal(err)
    }

    return db
}

func TestUserRepository(t *testing.T) {
    db := setupTestDB(t)
    defer db.Close()

    repo := NewUserRepository(db)

    // Test Create
    user := &User{Name: "Alice", Email: "alice@example.com"}
    err := repo.Create(user)
    if err != nil {
        t.Fatal(err)
    }

    // Test Get
    fetched, err := repo.GetByID(user.ID)
    if err != nil || fetched.Name != "Alice" {
        t.Error("failed to get user")
    }
}
```

#### testcontainers-go (PostgreSQL в Docker)

```bash
go get github.com/testcontainers/testcontainers-go
```

```go
//go:build integration

func TestWithPostgres(t *testing.T) {
    ctx := context.Background()

    // Запускаем PostgreSQL container
    postgres, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
        ContainerRequest: testcontainers.ContainerRequest{
            Image:        "postgres:15",
            ExposedPorts: []string{"5432/tcp"},
            Env: map[string]string{
                "POSTGRES_PASSWORD": "test",
                "POSTGRES_DB":       "testdb",
            },
            WaitingFor: wait.ForLog("database system is ready"),
        },
        Started: true,
    })
    if err != nil {
        t.Fatal(err)
    }
    defer postgres.Terminate(ctx)

    // Получаем DSN
    host, _ := postgres.Host(ctx)
    port, _ := postgres.MappedPort(ctx, "5432")
    dsn := fmt.Sprintf("host=%s port=%s user=postgres password=test dbname=testdb sslmode=disable",
        host, port.Port())

    // Подключаемся
    db, err := sql.Open("postgres", dsn)
    if err != nil {
        t.Fatal(err)
    }
    defer db.Close()

    // Тесты...
}
```

---

### 7.3 Внешние зависимости

#### TestMain для setup/teardown

```go
var testDB *sql.DB

func TestMain(m *testing.M) {
    // Setup
    var err error
    testDB, err = setupDatabase()
    if err != nil {
        log.Fatal(err)
    }

    // Run tests
    code := m.Run()

    // Teardown
    testDB.Close()

    os.Exit(code)
}
```

---

## 8. Race Detector

### 8.1 Что такое data race

**Data race** — когда несколько горутин одновременно обращаются к одной переменной, и хотя бы одна из них пишет.

```go
// ❌ Data race
var counter int

func increment() {
    counter++ // Не атомарно!
}

func main() {
    for i := 0; i < 1000; i++ {
        go increment()
    }
    time.Sleep(time.Second)
    fmt.Println(counter) // Undefined behavior!
}
```

---

### 8.2 go test -race

```bash
go test -race
```

**Вывод при race**:
```
==================
WARNING: DATA RACE
Write at 0x00c000100000 by goroutine 7:
  main.increment()
      /path/to/file.go:5 +0x3c

Previous write at 0x00c000100000 by goroutine 6:
  main.increment()
      /path/to/file.go:5 +0x3c
==================
```

**⚠️ Overhead**: 5-10x медленнее, 10x больше памяти. Используйте в CI/CD, но не в production.

---

### 8.3 Типичные race conditions

#### Race 1: Map без синхронизации

```go
// ❌ Race
var cache = make(map[string]string)

func Set(key, value string) {
    cache[key] = value // RACE!
}

// ✅ Исправление: sync.RWMutex или sync.Map
var (
    cache = make(map[string]string)
    mu    sync.RWMutex
)

func Set(key, value string) {
    mu.Lock()
    cache[key] = value
    mu.Unlock()
}
```

#### Race 2: Loop variable в горутине (до Go 1.22)

```go
// ❌ Race (до Go 1.22)
for i := 0; i < 10; i++ {
    go func() {
        fmt.Println(i) // Читает общую переменную i
    }()
}

// ✅ Исправление
for i := 0; i < 10; i++ {
    i := i // Копируем
    go func() {
        fmt.Println(i)
    }()
}

// ✅ Go 1.22+: автоматически
for i := 0; i < 10; i++ {
    go func() {
        fmt.Println(i) // Безопасно!
    }()
}
```

---

## 9. Coverage (покрытие кода)

### 9.1 go test -cover

```bash
# Процент покрытия
go test -cover

# Детальный отчёт
go test -coverprofile=coverage.out

# По пакетам
go test -cover ./...
```

**Вывод**:
```
ok      myapp/user    0.123s  coverage: 78.5% of statements
```

---

### 9.2 Визуализация покрытия

```bash
# HTML отчёт
go tool cover -html=coverage.out

# Открывается в браузере, показывает:
# - Зелёные строки: покрыты
# - Красные строки: не покрыты
# - Серые строки: не исполняемый код
```

**IDE интеграция**:
- **VS Code**: Go extension автоматически показывает покрытие
- **GoLand**: Run with Coverage

---

### 9.3 Целевые метрики

| Тип кода | Целевое покрытие |
|----------|------------------|
| **Business logic** | 80-90% |
| **Handlers** | 70-80% |
| **Utils** | 90%+ |
| **Generated code** | Не требуется |

> 💡 **Идиома Go**: Не гонитесь за 100%. Лучше 80% хорошо протестированного кода, чем 100% с бессмысленными тестами.

---

## 10. Идиоматичные паттерны тестирования

### 10.1 Helper functions

`t.Helper()` помечает функцию как вспомогательную. Ошибки будут указывать на вызывающий код, а не на helper.

```go
func assertNoError(t *testing.T, err error) {
    t.Helper() // ⬅ Важно!

    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
}

func TestExample(t *testing.T) {
    err := DoSomething()
    assertNoError(t, err) // Ошибка укажет на эту строку
}
```

---

### 10.2 Golden files

**Golden files** — сохранённые эталонные выводы для сложных структур.

```go
func TestRenderHTML(t *testing.T) {
    data := &Page{Title: "Test", Body: "Content"}
    output := RenderHTML(data)

    goldenFile := "testdata/golden/page.html"

    // Обновление golden file (при необходимости)
    if *update {
        os.WriteFile(goldenFile, []byte(output), 0644)
    }

    // Сравнение
    expected, _ := os.ReadFile(goldenFile)
    if output != string(expected) {
        t.Errorf("output mismatch")
    }
}
```

```bash
go test -update  # Обновить golden files
```

---

### 10.3 Testable Examples

`func ExampleXxx()` — примеры, которые компилируются и проверяются тестами.

```go
func ExampleSum() {
    result := Sum(1, 2, 3)
    fmt.Println(result)
    // Output: 6
}
```

Отображаются в `godoc` как примеры использования.

---

### 10.4 Build tags

Разделение unit/integration тестов:

```go
//go:build integration

package myapp

import "testing"

func TestDatabaseIntegration(t *testing.T) {
    // ...
}
```

```bash
# Только unit-тесты
go test

# С integration тестами
go test -tags=integration
```

---

## 11. Тестирование конкурентного кода

### 11.1 Проблемы тестирования горутин

- **Non-determinism**: порядок выполнения непредсказуем
- **Race conditions**: data races
- **Deadlocks**: взаимные блокировки

---

### 11.2 Стратегии

#### WaitGroup для синхронизации

```go
func TestConcurrentWorkers(t *testing.T) {
    var wg sync.WaitGroup
    results := make([]int, 0)
    mu := sync.Mutex{}

    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(val int) {
            defer wg.Done()

            result := Process(val)

            mu.Lock()
            results = append(results, result)
            mu.Unlock()
        }(i)
    }

    wg.Wait()

    if len(results) != 10 {
        t.Errorf("expected 10 results, got %d", len(results))
    }
}
```

#### Context для таймаутов

```go
func TestWithTimeout(t *testing.T) {
    ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
    defer cancel()

    result := make(chan int)

    go func() {
        result <- SlowOperation()
    }()

    select {
    case r := <-result:
        // OK
    case <-ctx.Done():
        t.Fatal("operation timed out")
    }
}
```

---

### 11.3 goleak: обнаружение утечек

```bash
go get go.uber.org/goleak
```

```go
import "go.uber.org/goleak"

func TestNoGoroutineLeak(t *testing.T) {
    defer goleak.VerifyNone(t) // Проверяет утечки в конце

    StartWorkers()
    StopWorkers() // Должен остановить все горутины
}
```

Связь с [разделом 2.1](./01_goroutines_channels.md#предотвращение-утечек-горутин).

---

## 12. Новые возможности тестирования (Go 1.24-1.25)

### 12.1 testing.T.Context() — контекст теста (Go 1.24)

> 💡 **Для C# разработчиков**: Аналог `CancellationToken`, автоматически отменяемый по завершении теста.

Go 1.24 добавил `t.Context()` — метод, возвращающий `context.Context`, который **автоматически отменяется** при завершении теста (успешном, провальном или с `t.Cleanup()`).

**До Go 1.24 (вручную):**
```go
func TestWithContext(t *testing.T) {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel() // Легко забыть!

    result, err := fetchData(ctx, "https://example.com")
    if err != nil {
        t.Fatal(err)
    }
    _ = result
}
```

**Go 1.24+ с `t.Context()` (идиоматично):**
```go
func TestWithContext(t *testing.T) {
    ctx := t.Context() // Отменяется автоматически при завершении теста

    result, err := fetchData(ctx, "https://example.com")
    if err != nil {
        t.Fatal(err)
    }
    _ = result
}
```

**Применение — integration тесты с БД:**
```go
func TestDatabase(t *testing.T) {
    ctx := t.Context() // Автоматически отменит in-flight запросы при t.Fatal

    db, err := sql.Open("postgres", testDSN)
    if err != nil {
        t.Fatal(err)
    }
    t.Cleanup(func() { db.Close() })

    // Если тест завершится (t.Fatal/t.FailNow), ctx отменяется,
    // прерывая зависшие запросы к БД
    rows, err := db.QueryContext(ctx, "SELECT id FROM users")
    if err != nil {
        t.Fatal(err)
    }
    defer rows.Close()
}
```

**Сравнение с C#:**
```csharp
// C# — CancellationTokenSource для тестов (xUnit/NUnit)
[Fact]
public async Task TestWithCancellation()
{
    using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(30));
    var result = await FetchDataAsync(cts.Token);
    Assert.NotNull(result);
}
```

```go
// Go 1.24 — t.Context() автоматически
func TestWithCancellation(t *testing.T) {
    ctx := t.Context() // Deadline можно добавить через context.WithTimeout
    result, err := fetchData(ctx, url)
    if err != nil {
        t.Fatal(err)
    }
}
```

---

### 12.2 testing.B.Loop() — надёжные бенчмарки (Go 1.24)

> 💡 **Для C# разработчиков**: Аналог `[Benchmark]` от BenchmarkDotNet с автоматической защитой от оптимизации компилятора.

Go 1.24 добавил `b.Loop()` — замену классическому `for i := 0; i < b.N; i++`. Новый метод решает проблему **оптимизации пустого цикла** компилятором.

**До Go 1.24 (проблема с оптимизацией):**
```go
var result int

func BenchmarkSum(b *testing.B) {
    for i := 0; i < b.N; i++ {
        // Компилятор может оптимизировать цикл, если result не используется
        result = computeSum(largeSlice)
    }
    _ = result // Попытка предотвратить оптимизацию (не всегда надёжно)
}
```

**Go 1.24+ с `b.Loop()` (надёжно):**
```go
func BenchmarkSum(b *testing.B) {
    for b.Loop() { // Компилятор не оптимизирует тело цикла
        result := computeSum(largeSlice)
        _ = result
    }
}
```

**Отличия `b.Loop()` от `for i < b.N`:**
| Аспект | `for i < b.N` | `b.Loop()` |
|--------|--------------|-----------|
| Защита от оптимизации | Ненадёжная (нужен `_ = result`) | Встроенная |
| Инициализация таймера | `b.ResetTimer()` вручную | Автоматически |
| Cleanup между итерациями | Невозможен | `b.Cleanup(func())` |
| Читаемость | Стандартная | Более явная |

```go
// Бенчмарк с setup per-iteration
func BenchmarkJSONEncode(b *testing.B) {
    data := &MyStruct{Name: "Alice", Age: 30}

    for b.Loop() {
        buf, err := json.Marshal(data)
        if err != nil {
            b.Fatal(err)
        }
        _ = buf
    }
}
```

---

### 12.3 testing/synctest — детерминированное тестирование конкурентности (Go 1.25)

> 💡 **Для C# разработчиков**: Аналог концепции Virtual Time в .NET тестировании — контролируемое время для воспроизводимых тестов горутин.

`testing/synctest` (экспериментальный в Go 1.24, стабильный в Go 1.25) позволяет тестировать конкурентный код **детерминированно**, используя виртуальные часы.

**Проблема тестирования кода с таймаутами:**
```go
// Функция с таймером — сложно тестировать
func ProcessWithTimeout(ctx context.Context, timeout time.Duration) error {
    timer := time.NewTimer(timeout)
    defer timer.Stop()

    select {
    case <-ctx.Done():
        return ctx.Err()
    case <-timer.C:
        return errors.New("timeout exceeded")
    }
}

// Тест без synctest — нужно реально ждать
func TestTimeout_Slow(t *testing.T) {
    ctx := context.Background()
    start := time.Now()
    err := ProcessWithTimeout(ctx, 100*time.Millisecond) // Реальное ожидание!
    t.Logf("elapsed: %v", time.Since(start))
    if err == nil {
        t.Error("expected timeout error")
    }
}
```

**С `testing/synctest` — мгновенно:**
```go
import "testing/synctest"

func TestTimeout_Fast(t *testing.T) {
    synctest.Run(func() {
        ctx := context.Background()

        // Запускаем тестируемую функцию в горутине
        var err error
        go func() {
            err = ProcessWithTimeout(ctx, 100*time.Millisecond)
        }()

        // Продвигаем виртуальное время на 200ms — мгновенно!
        synctest.Wait() // Ждём пока все горутины заблокируются
        // time.Sleep(200*time.Millisecond) в виртуальном времени

        // err теперь содержит "timeout exceeded"
    })
}
```

**Ключевые концепции `testing/synctest`:**
- `synctest.Run(func())` — запускает функцию в изолированном «bubble» с виртуальным временем
- `synctest.Wait()` — продвигает виртуальное время пока все горутины не заблокируются
- Горутины внутри bubble видят виртуальное время (`time.Now()`, `time.Sleep()`, таймеры)
- Горутины вне bubble работают с реальным временем

**Применение:**
```go
// Тестирование retry-логики без реальных задержек
func TestRetryPolicy(t *testing.T) {
    synctest.Run(func() {
        attempts := 0
        client := &Client{
            MaxRetries: 3,
            Backoff:    100 * time.Millisecond,
        }

        go func() {
            client.Do(func() error {
                attempts++
                if attempts < 3 {
                    return errors.New("temporary error")
                }
                return nil
            })
        }()

        synctest.Wait() // Время автоматически продвигается через backoff-паузы
        // attempts == 3, но тест завершился мгновенно
    })
}
```

> ⚠️ **Статус**: `testing/synctest` стабилен в Go 1.25. Для Go 1.24 требует `GOEXPERIMENT=synctest`.

---

## Практические примеры

> 💡 Примеры демонстрируют комбинацию изученных техник: table-driven tests, subtests, моки, benchmarks, integration tests.

### Пример 1: UserService с полным покрытием

**Задача**: Протестировать многослойное приложение (Repository → Service → HTTP Handler).

**Структура**:
```
user/
  user.go              // Модель
  repository.go        // Interface + реализация
  repository_test.go   // Unit-тесты repository
  service.go           // Бизнес-логика
  service_test.go      // Тесты с gomock
  handler.go           // HTTP handlers
  handler_test.go      // httptest
```

<details>
<summary>📄 Полный код (кликните чтобы развернуть)</summary>

```go
// user.go
package user

type User struct {
    ID    int
    Name  string
    Email string
}

// repository.go
type Repository interface {
    GetByID(id int) (*User, error)
    Create(user *User) error
}

// service.go
type Service struct {
    repo Repository
}

func NewService(repo Repository) *Service {
    return &Service{repo: repo}
}

func (s *Service) GetUser(id int) (*User, error) {
    if id <= 0 {
        return nil, errors.New("invalid ID")
    }
    return s.repo.GetByID(id)
}

// service_test.go (с gomock)
func TestService_GetUser(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockRepo := mocks.NewMockRepository(ctrl)

    tests := []struct {
        name      string
        id        int
        setupMock func()
        wantErr   bool
    }{
        {
            name: "valid ID",
            id:   1,
            setupMock: func() {
                mockRepo.EXPECT().
                    GetByID(1).
                    Return(&User{ID: 1, Name: "Alice"}, nil)
            },
            wantErr: false,
        },
        {
            name:      "invalid ID",
            id:        -1,
            setupMock: func() {},
            wantErr:   true,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            tt.setupMock()

            service := NewService(mockRepo)
            user, err := service.GetUser(tt.id)

            if (err != nil) != tt.wantErr {
                t.Errorf("wantErr=%v, got err=%v", tt.wantErr, err)
            }

            if !tt.wantErr && user == nil {
                t.Error("expected user, got nil")
            }
        })
    }
}

// handler_test.go (httptest)
func TestUserHandler(t *testing.T) {
    mockRepo := &MockRepository{
        GetByIDFunc: func(id int) (*User, error) {
            return &User{ID: id, Name: "Alice"}, nil
        },
    }

    service := NewService(mockRepo)
    handler := NewHandler(service)

    req := httptest.NewRequest("GET", "/users/1", nil)
    rr := httptest.NewRecorder()

    handler.ServeHTTP(rr, req)

    if rr.Code != 200 {
        t.Errorf("expected 200, got %d", rr.Code)
    }
}
```

</details>

**Выводы**:
- Table-driven tests для валидации
- gomock для изоляции слоёв
- httptest для HTTP endpoints
- Coverage: 85%+

---

### Пример 2: Rate Limiter с concurrent тестами

**Задача**: Протестировать thread-safe rate limiter с множеством горутин.

**Связь с разделами**: [2.1 (горутины)](./01_goroutines_channels.md), [2.4 (atomic/mutex)](./04_sync_primitives.md)

<details>
<summary>📄 Полный код (кликните чтобы развернуть)</summary>

```go
// ratelimiter.go
package ratelimiter

import (
    "sync"
    "time"
)

type RateLimiter struct {
    tokens    int
    capacity  int
    mu        sync.Mutex
    lastRefill time.Time
}

func New(capacity int) *RateLimiter {
    return &RateLimiter{
        tokens:     capacity,
        capacity:   capacity,
        lastRefill: time.Now(),
    }
}

func (r *RateLimiter) Allow() bool {
    r.mu.Lock()
    defer r.mu.Unlock()

    // Refill tokens
    now := time.Now()
    elapsed := now.Sub(r.lastRefill)
    tokensToAdd := int(elapsed.Seconds())

    if tokensToAdd > 0 {
        r.tokens = min(r.capacity, r.tokens+tokensToAdd)
        r.lastRefill = now
    }

    // Check and consume
    if r.tokens > 0 {
        r.tokens--
        return true
    }
    return false
}

// ratelimiter_test.go (unit tests)
func TestRateLimiter_Allow(t *testing.T) {
    tests := []struct {
        name     string
        capacity int
        calls    int
        want     int // Сколько должно пройти
    }{
        {"single", 5, 3, 3},
        {"exceeds capacity", 5, 10, 5},
        {"zero capacity", 0, 5, 0},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            rl := New(tt.capacity)

            allowed := 0
            for i := 0; i < tt.calls; i++ {
                if rl.Allow() {
                    allowed++
                }
            }

            if allowed != tt.want {
                t.Errorf("expected %d, got %d", tt.want, allowed)
            }
        })
    }
}

// ratelimiter_concurrent_test.go
func TestRateLimiter_Concurrent(t *testing.T) {
    rl := New(100)

    var wg sync.WaitGroup
    allowed := int32(0)

    // 1000 горутин пытаются взять токены
    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()

            if rl.Allow() {
                atomic.AddInt32(&allowed, 1)
            }
        }()
    }

    wg.Wait()

    // Должно пройти максимум 100
    if allowed > 100 {
        t.Errorf("expected <=100, got %d", allowed)
    }
}

// ratelimiter_bench_test.go
func BenchmarkRateLimiter(b *testing.B) {
    rl := New(1000000)

    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            rl.Allow()
        }
    })
}

// Test with race detector:
// go test -race
```

</details>

**Выводы**:
- Table-driven для unit тестов
- WaitGroup для синхронизации в concurrent тестах
- `go test -race` для обнаружения data races
- Benchmarks для производительности

---

**Вопросы?** Открой issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Назад: 2.5 Обработка ошибок](./05_error_handling.md) | [Вперёд: 2.7 Профилирование и оптимизация →](./07_profiling_optimization.md)
