# 4.3 Очереди сообщений

## Содержание

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Введение](#%D0%B2%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5)
  - [Что изменится в вашем подходе](#%D1%87%D1%82%D0%BE-%D0%B8%D0%B7%D0%BC%D0%B5%D0%BD%D0%B8%D1%82%D1%81%D1%8F-%D0%B2-%D0%B2%D0%B0%D1%88%D0%B5%D0%BC-%D0%BF%D0%BE%D0%B4%D1%85%D0%BE%D0%B4%D0%B5)
- [Экосистема: C# vs Go](#%D1%8D%D0%BA%D0%BE%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%B0-c-vs-go)
  - [Ключевое отличие](#%D0%BA%D0%BB%D1%8E%D1%87%D0%B5%D0%B2%D0%BE%D0%B5-%D0%BE%D1%82%D0%BB%D0%B8%D1%87%D0%B8%D0%B5)
  - [В этом разделе вы научитесь](#%D0%B2-%D1%8D%D1%82%D0%BE%D0%BC-%D1%80%D0%B0%D0%B7%D0%B4%D0%B5%D0%BB%D0%B5-%D0%B2%D1%8B-%D0%BD%D0%B0%D1%83%D1%87%D0%B8%D1%82%D0%B5%D1%81%D1%8C)
- [Apache Kafka (segmentio/kafka-go)](#apache-kafka-segmentiokafka-go)
  - [Почему kafka-go](#%D0%BF%D0%BE%D1%87%D0%B5%D0%BC%D1%83-kafka-go)
  - [Подключение и конфигурация](#%D0%BF%D0%BE%D0%B4%D0%BA%D0%BB%D1%8E%D1%87%D0%B5%D0%BD%D0%B8%D0%B5-%D0%B8-%D0%BA%D0%BE%D0%BD%D1%84%D0%B8%D0%B3%D1%83%D1%80%D0%B0%D1%86%D0%B8%D1%8F)
  - [Producer: отправка сообщений](#producer-%D0%BE%D1%82%D0%BF%D1%80%D0%B0%D0%B2%D0%BA%D0%B0-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D0%B9)
    - [Синхронная отправка](#%D1%81%D0%B8%D0%BD%D1%85%D1%80%D0%BE%D0%BD%D0%BD%D0%B0%D1%8F-%D0%BE%D1%82%D0%BF%D1%80%D0%B0%D0%B2%D0%BA%D0%B0)
    - [Батчевая отправка](#%D0%B1%D0%B0%D1%82%D1%87%D0%B5%D0%B2%D0%B0%D1%8F-%D0%BE%D1%82%D0%BF%D1%80%D0%B0%D0%B2%D0%BA%D0%B0)
    - [Стратегии партиционирования](#%D1%81%D1%82%D1%80%D0%B0%D1%82%D0%B5%D0%B3%D0%B8%D0%B8-%D0%BF%D0%B0%D1%80%D1%82%D0%B8%D1%86%D0%B8%D0%BE%D0%BD%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F)
    - [Асинхронный producer через горутины](#%D0%B0%D1%81%D0%B8%D0%BD%D1%85%D1%80%D0%BE%D0%BD%D0%BD%D1%8B%D0%B9-producer-%D1%87%D0%B5%D1%80%D0%B5%D0%B7-%D0%B3%D0%BE%D1%80%D1%83%D1%82%D0%B8%D0%BD%D1%8B)
  - [Consumer: потребление сообщений](#consumer-%D0%BF%D0%BE%D1%82%D1%80%D0%B5%D0%B1%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D0%B9)
    - [Базовый consumer](#%D0%B1%D0%B0%D0%B7%D0%BE%D0%B2%D1%8B%D0%B9-consumer)
    - [Manual commit vs Auto commit](#manual-commit-vs-auto-commit)
    - [Параллельная обработка с worker pool](#%D0%BF%D0%B0%D1%80%D0%B0%D0%BB%D0%BB%D0%B5%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F-%D0%BE%D0%B1%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%BA%D0%B0-%D1%81-worker-pool)
  - [Consumer Groups](#consumer-groups)
  - [Production конфигурация Kafka](#production-%D0%BA%D0%BE%D0%BD%D1%84%D0%B8%D0%B3%D1%83%D1%80%D0%B0%D1%86%D0%B8%D1%8F-kafka)
    - [Production Writer (Producer)](#production-writer-producer)
    - [Production Reader (Consumer)](#production-reader-consumer)
    - [TLS и SASL аутентификация](#tls-%D0%B8-sasl-%D0%B0%D1%83%D1%82%D0%B5%D0%BD%D1%82%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%86%D0%B8%D1%8F)
  - [Error Handling и Dead Letter Topics](#error-handling-%D0%B8-dead-letter-topics)
    - [Классификация ошибок](#%D0%BA%D0%BB%D0%B0%D1%81%D1%81%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%86%D0%B8%D1%8F-%D0%BE%D1%88%D0%B8%D0%B1%D0%BE%D0%BA)
    - [Dead Letter Topic реализация](#dead-letter-topic-%D1%80%D0%B5%D0%B0%D0%BB%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F)
- [RabbitMQ (amqp091-go)](#rabbitmq-amqp091-go)
  - [Подключение и управление каналами](#%D0%BF%D0%BE%D0%B4%D0%BA%D0%BB%D1%8E%D1%87%D0%B5%D0%BD%D0%B8%D0%B5-%D0%B8-%D1%83%D0%BF%D1%80%D0%B0%D0%B2%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5-%D0%BA%D0%B0%D0%BD%D0%B0%D0%BB%D0%B0%D0%BC%D0%B8)
    - [Базовое подключение](#%D0%B1%D0%B0%D0%B7%D0%BE%D0%B2%D0%BE%D0%B5-%D0%BF%D0%BE%D0%B4%D0%BA%D0%BB%D1%8E%D1%87%D0%B5%D0%BD%D0%B8%D0%B5)
    - [Пул каналов](#%D0%BF%D1%83%D0%BB-%D0%BA%D0%B0%D0%BD%D0%B0%D0%BB%D0%BE%D0%B2)
  - [Exchanges, Queues, Bindings](#exchanges-queues-bindings)
    - [Типы exchange](#%D1%82%D0%B8%D0%BF%D1%8B-exchange)
  - [Publishing: подтверждения и гарантии](#publishing-%D0%BF%D0%BE%D0%B4%D1%82%D0%B2%D0%B5%D1%80%D0%B6%D0%B4%D0%B5%D0%BD%D0%B8%D1%8F-%D0%B8-%D0%B3%D0%B0%D1%80%D0%B0%D0%BD%D1%82%D0%B8%D0%B8)
    - [Базовая публикация](#%D0%B1%D0%B0%D0%B7%D0%BE%D0%B2%D0%B0%D1%8F-%D0%BF%D1%83%D0%B1%D0%BB%D0%B8%D0%BA%D0%B0%D1%86%D0%B8%D1%8F)
    - [Publisher Confirms](#publisher-confirms)
  - [Consuming: prefetch, ack/nack](#consuming-prefetch-acknack)
    - [Worker Pool для параллельной обработки](#worker-pool-%D0%B4%D0%BB%D1%8F-%D0%BF%D0%B0%D1%80%D0%B0%D0%BB%D0%BB%D0%B5%D0%BB%D1%8C%D0%BD%D0%BE%D0%B9-%D0%BE%D0%B1%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%BA%D0%B8)
  - [Connection Recovery и Reconnection](#connection-recovery-%D0%B8-reconnection)
  - [Dead Letter Exchanges (DLX)](#dead-letter-exchanges-dlx)
    - [Настройка DLX](#%D0%BD%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0-dlx)
    - [Retry через цепочку DLX + TTL](#retry-%D1%87%D0%B5%D1%80%D0%B5%D0%B7-%D1%86%D0%B5%D0%BF%D0%BE%D1%87%D0%BA%D1%83-dlx--ttl)
- [NATS (nats.go)](#nats-natsgo)
  - [Core NATS: Pub/Sub и Request/Reply](#core-nats-pubsub-%D0%B8-requestreply)
    - [Pub/Sub](#pubsub)
    - [Queue Groups (балансировка нагрузки)](#queue-groups-%D0%B1%D0%B0%D0%BB%D0%B0%D0%BD%D1%81%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D0%B0-%D0%BD%D0%B0%D0%B3%D1%80%D1%83%D0%B7%D0%BA%D0%B8)
    - [Request/Reply (синхронный RPC)](#requestreply-%D1%81%D0%B8%D0%BD%D1%85%D1%80%D0%BE%D0%BD%D0%BD%D1%8B%D0%B9-rpc)
  - [JetStream: персистентный обмен сообщениями](#jetstream-%D0%BF%D0%B5%D1%80%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BD%D1%82%D0%BD%D1%8B%D0%B9-%D0%BE%D0%B1%D0%BC%D0%B5%D0%BD-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D1%8F%D0%BC%D0%B8)
    - [Consumer: получение сообщений из JetStream](#consumer-%D0%BF%D0%BE%D0%BB%D1%83%D1%87%D0%B5%D0%BD%D0%B8%D0%B5-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D0%B9-%D0%B8%D0%B7-jetstream)
  - [Push vs Pull Consumers](#push-vs-pull-consumers)
  - [Key-Value Store и Object Store](#key-value-store-%D0%B8-object-store)
- [Redis Streams](#redis-streams)
  - [Основные операции (XADD, XREAD)](#%D0%BE%D1%81%D0%BD%D0%BE%D0%B2%D0%BD%D1%8B%D0%B5-%D0%BE%D0%BF%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D0%B8-xadd-xread)
  - [Consumer Groups (Redis)](#consumer-groups-redis)
  - [Acknowledgment и Claiming](#acknowledgment-%D0%B8-claiming)
  - [Когда использовать Redis Streams](#%D0%BA%D0%BE%D0%B3%D0%B4%D0%B0-%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D1%8C-redis-streams)
- [Сравнение технологий](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5-%D1%82%D0%B5%D1%85%D0%BD%D0%BE%D0%BB%D0%BE%D0%B3%D0%B8%D0%B9)
  - [Сводная таблица](#%D1%81%D0%B2%D0%BE%D0%B4%D0%BD%D0%B0%D1%8F-%D1%82%D0%B0%D0%B1%D0%BB%D0%B8%D1%86%D0%B0)
  - [Блок-схема выбора](#%D0%B1%D0%BB%D0%BE%D0%BA-%D1%81%D1%85%D0%B5%D0%BC%D0%B0-%D0%B2%D1%8B%D0%B1%D0%BE%D1%80%D0%B0)
- [Паттерны и Best Practices](#%D0%BF%D0%B0%D1%82%D1%82%D0%B5%D1%80%D0%BD%D1%8B-%D0%B8-best-practices)
  - [Идемпотентность (Exactly-Once Processing)](#%D0%B8%D0%B4%D0%B5%D0%BC%D0%BF%D0%BE%D1%82%D0%B5%D0%BD%D1%82%D0%BD%D0%BE%D1%81%D1%82%D1%8C-exactly-once-processing)
  - [Graceful Shutdown](#graceful-shutdown)
  - [Retry с Exponential Backoff](#retry-%D1%81-exponential-backoff)
  - [Dead Letter Queue](#dead-letter-queue)
  - [Сериализация сообщений](#%D1%81%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D0%B9)
  - [Outbox Pattern](#outbox-pattern)
  - [Saga Pattern](#saga-pattern)
- [Production Concerns](#production-concerns)
  - [Мониторинг с Prometheus](#%D0%BC%D0%BE%D0%BD%D0%B8%D1%82%D0%BE%D1%80%D0%B8%D0%BD%D0%B3-%D1%81-prometheus)
    - [Kafka Consumer Lag](#kafka-consumer-lag)
  - [OpenTelemetry Instrumentation](#opentelemetry-instrumentation)
  - [Health Checks](#health-checks)
- [Практические примеры](#%D0%BF%D1%80%D0%B0%D0%BA%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B5-%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80%D1%8B)
  - [Пример 1: Event-Driven Order Processing (Kafka)](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-1-event-driven-order-processing-kafka)
  - [Пример 2: Task Queue с RabbitMQ](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-2-task-queue-%D1%81-rabbitmq)
  - [Пример 3: Real-Time Notifications (NATS)](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-3-real-time-notifications-nats)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

---

## Введение

В [разделе 4.2](./02_caching.md) мы рассмотрели Pub/Sub в Redis и упомянули, что для надёжной доставки сообщений нужны специализированные решения. Очереди сообщений (Message Queues) — это фундамент асинхронной архитектуры: они позволяют сервисам обмениваться данными без прямой связи, обеспечивая надёжность, масштабируемость и устойчивость к сбоям.

> 💡 **Для C# разработчиков**: В .NET вы привыкли к **MassTransit** или **NServiceBus** — высокоуровневым абстракциям, которые скрывают детали транспорта. Вы регистрируете `IConsumer<T>` в DI, настраиваете retry policies, saga state machines, и фреймворк сам управляет подключениями, сериализацией, dead letter queues и consumer lifecycle. В Go **нет аналога MassTransit**. Вы работаете с клиентскими библиотеками напрямую — это больше кода, но полный контроль над поведением. Горутины делают consumer concurrency тривиальным, а отсутствие скрытой «магии» упрощает отладку.

### Что изменится в вашем подходе

**C# с MassTransit**:
```csharp
// Регистрация — и всё работает «из коробки»
services.AddMassTransit(x =>
{
    x.AddConsumer<OrderCreatedConsumer>();
    x.UsingRabbitMq((context, cfg) =>
    {
        cfg.UseMessageRetry(r => r.Exponential(5, TimeSpan.FromSeconds(1), TimeSpan.FromMinutes(1), TimeSpan.FromSeconds(2)));
        cfg.ConfigureEndpoints(context);
    });
});

// Consumer — чистая бизнес-логика
public class OrderCreatedConsumer : IConsumer<OrderCreated>
{
    public async Task Consume(ConsumeContext<OrderCreated> context)
    {
        // MassTransit сам десериализует, управляет retry, dead letter, tracing
        await ProcessOrder(context.Message);
    }
}
```

**Go — явная реализация**:
```go
// Подключение, consumer loop, retry, DLQ — всё вручную
reader := kafka.NewReader(kafka.ReaderConfig{
    Brokers: []string{"localhost:9092"},
    Topic:   "orders.created",
    GroupID: "order-processor",
})
defer reader.Close()

for {
    msg, err := reader.ReadMessage(ctx)
    if err != nil {
        break
    }

    if err := processOrder(msg); err != nil {
        // Retry, DLQ — реализуем сами
        handleError(ctx, msg, err)
    }
}
```

---

## Экосистема: C# vs Go

| Концепция | C# (.NET) | Go |
|-----------|-----------|-----|
| **Абстракция** | MassTransit, NServiceBus | Нет аналога (явный код) |
| **Kafka клиент** | Confluent.Kafka (через MassTransit) | segmentio/kafka-go, confluent-kafka-go |
| **RabbitMQ клиент** | RabbitMQ.Client (через MassTransit) | amqp091-go |
| **NATS клиент** | NATS.Client | nats.go |
| **In-process очередь** | `System.Threading.Channels` | Go каналы (встроены в язык) |
| **Consumer паттерн** | `IConsumer<T>`, hosted service | Горутина + `for` loop |
| **Retry / DLQ** | Встроено в MassTransit | Ручная реализация |
| **Сериализация** | Автоматическая (System.Text.Json) | Ручная (encoding/json, protobuf) |
| **Saga** | MassTransit Saga / Automatonymous | Ручная реализация |
| **Health checks** | `IHealthCheck` | Ручная проверка или alexliesenfeld/health |
| **Tracing** | `UseOpenTelemetry()` в MassTransit | Ручная инструментация |

### Ключевое отличие

В .NET **фреймворк управляет всем жизненным циклом**: подключение → десериализация → маршрутизация к consumer → retry при ошибке → DLQ при исчерпании попыток → метрики → трейсинг. Вы пишете только бизнес-логику.

В Go **вы управляете каждым шагом явно**: создаёте подключение, читаете сообщения в цикле, десериализуете, обрабатываете ошибки, реализуете retry и DLQ. Это требует больше кода, но:

- **Нет скрытого поведения** — легко отлаживать
- **Полный контроль** над concurrency (горутины, worker pool)
- **Предсказуемая производительность** — нет reflection, нет DI overhead
- **Простота** — нет сложных конфигурационных цепочек

> ⚠️ **Распространённая ошибка C# разработчиков**: искать "Go MassTransit" или пытаться создать аналогичную абстракцию. В Go-сообществе предпочитают явный код библиотечным фреймворкам. Напишите тонкую обёртку для вашего конкретного случая, а не универсальный фреймворк.

### В этом разделе вы научитесь

- Работать с 4 системами обмена сообщениями: **Kafka**, **RabbitMQ**, **NATS**, **Redis Streams**
- Реализовывать **producer** и **consumer** для каждой системы
- Настраивать **production-конфигурацию** (TLS, batching, compression)
- Реализовывать **retry**, **dead letter queue**, **idempotency**
- Применять паттерны: **Outbox**, **Saga**, **Graceful Shutdown**
- Инструментировать очереди через **Prometheus** и **OpenTelemetry**
- Выбирать подходящую технологию для вашего сценария

---

## Apache Kafka (segmentio/kafka-go)

Apache Kafka — распределённый лог событий, оптимизированный для высокой пропускной способности и долгосрочного хранения. Kafka хранит сообщения на диске и позволяет перечитывать их — это делает его идеальным для event sourcing, stream processing и интеграции между микросервисами.

### Почему kafka-go

В Go-экосистеме существуют три основных Kafka-клиента:

| Библиотека | CGo | API стиль | Статус | Когда использовать |
|------------|-----|-----------|--------|-------------------|
| **segmentio/kafka-go** | Нет (pure Go) | Идиоматичный Go | Активная поддержка | Основной выбор для большинства проектов |
| **confluent-kafka-go** | Да (librdkafka) | Обёртка над C | Активная поддержка | Нужны exactly-once транзакции, максимальная производительность |
| **Shopify/sarama** | Нет (pure Go) | Низкоуровневый | IBM передала Shopify, менее активная | Legacy проекты |

> 💡 **Рекомендация**: Используйте `segmentio/kafka-go` как основной клиент. Он не требует CGo (проще кросс-компиляция и Docker), имеет понятный API и активно поддерживается. `confluent-kafka-go` оправдан только если вам нужны exactly-once транзакции Kafka или вы уже используете librdkafka в инфраструктуре.

**C# аналогия**: В C# стандарт — `Confluent.Kafka`, который тоже обёртка над librdkafka. Разница в том, что в Go есть pure-Go альтернатива (kafka-go), которая проще в деплое.

Установка:

```bash
go get github.com/segmentio/kafka-go
```

### Подключение и конфигурация

kafka-go использует два основных типа: `kafka.Writer` для отправки и `kafka.Reader` для потребления. В отличие от Confluent.Kafka в C#, здесь нет единого «клиента» — producer и consumer полностью независимы.

**C#** (Confluent.Kafka):
```csharp
// Producer
var config = new ProducerConfig
{
    BootstrapServers = "localhost:9092",
    Acks = Acks.All,
    EnableIdempotence = true
};
using var producer = new ProducerBuilder<string, string>(config).Build();

// Consumer
var consumerConfig = new ConsumerConfig
{
    BootstrapServers = "localhost:9092",
    GroupId = "my-group",
    AutoOffsetReset = AutoOffsetReset.Earliest
};
using var consumer = new ConsumerBuilder<string, string>(consumerConfig).Build();
```

**Go** (kafka-go):
```go
package main

import (
    "context"
    "log"
    "time"

    "github.com/segmentio/kafka-go"
)

func main() {
    // Writer (producer) — автоматически управляет подключениями
    writer := &kafka.Writer{
        Addr:         kafka.TCP("localhost:9092"),
        Topic:        "orders",
        Balancer:     &kafka.LeastBytes{}, // Стратегия выбора партиции
        BatchTimeout: 10 * time.Millisecond,
        RequiredAcks: kafka.RequireAll, // Аналог Acks.All в C#
    }
    defer writer.Close()

    // Reader (consumer) — привязан к топику и группе
    reader := kafka.NewReader(kafka.ReaderConfig{
        Brokers:        []string{"localhost:9092"},
        Topic:          "orders",
        GroupID:        "order-processor",
        MinBytes:       1,              // Минимум 1 байт для fetch
        MaxBytes:       10e6,           // Максимум 10 MB
        CommitInterval: time.Second,    // Автоматический коммит каждую секунду
        StartOffset:    kafka.FirstOffset, // Аналог AutoOffsetReset.Earliest
    })
    defer reader.Close()

    log.Println("Kafka writer и reader созданы")
}
```

> 💡 **Отличие от C#**: В Confluent.Kafka вы создаёте `ProducerBuilder` и `ConsumerBuilder` с конфигурацией через словарь строк. В kafka-go конфигурация — типизированные структуры с автодополнением в IDE.

### Producer: отправка сообщений

#### Синхронная отправка

```go
// Отправка одного сообщения с ожиданием подтверждения
func sendOrder(ctx context.Context, w *kafka.Writer, order Order) error {
    data, err := json.Marshal(order)
    if err != nil {
        return fmt.Errorf("сериализация заказа: %w", err)
    }

    err = w.WriteMessages(ctx, kafka.Message{
        Key:   []byte(order.ID),     // Ключ определяет партицию
        Value: data,
        Headers: []kafka.Header{
            {Key: "content-type", Value: []byte("application/json")},
            {Key: "source", Value: []byte("order-service")},
        },
    })
    if err != nil {
        return fmt.Errorf("отправка в Kafka: %w", err)
    }

    return nil
}
```

#### Батчевая отправка

```go
// WriteMessages поддерживает отправку нескольких сообщений за раз
func sendOrders(ctx context.Context, w *kafka.Writer, orders []Order) error {
    messages := make([]kafka.Message, 0, len(orders))

    for _, order := range orders {
        data, err := json.Marshal(order)
        if err != nil {
            return fmt.Errorf("сериализация заказа %s: %w", order.ID, err)
        }
        messages = append(messages, kafka.Message{
            Key:   []byte(order.ID),
            Value: data,
        })
    }

    // kafka-go автоматически группирует сообщения в батчи
    // и отправляет их эффективно
    return w.WriteMessages(ctx, messages...)
}
```

#### Стратегии партиционирования

```go
// Round-Robin — равномерное распределение
writer := &kafka.Writer{
    Addr:     kafka.TCP("localhost:9092"),
    Topic:    "events",
    Balancer: &kafka.RoundRobin{},
}

// По ключу — сообщения с одним ключом попадают в одну партицию
// (гарантирует порядок для одного ключа)
writer = &kafka.Writer{
    Addr:     kafka.TCP("localhost:9092"),
    Topic:    "events",
    Balancer: &kafka.Hash{}, // Murmur2 хэш по ключу
}

// Least Bytes — в партицию с наименьшим объёмом данных
writer = &kafka.Writer{
    Addr:     kafka.TCP("localhost:9092"),
    Topic:    "events",
    Balancer: &kafka.LeastBytes{},
}

// Кастомный балансировщик
type RegionBalancer struct{}

func (b *RegionBalancer) Balance(msg kafka.Message, partitions ...int) int {
    // Определяем партицию по региону из headers
    for _, h := range msg.Headers {
        if h.Key == "region" {
            switch string(h.Value) {
            case "eu":
                return partitions[0]
            case "us":
                return partitions[1 % len(partitions)]
            }
        }
    }
    return partitions[0]
}
```

> ⚠️ **Важно**: Если вам нужен строгий порядок сообщений для одной сущности (например, все события одного заказа), используйте `Hash` балансировщик и задавайте `Key` = ID сущности. Это гарантирует, что все сообщения с одним ключом попадут в одну партицию.

#### Асинхронный producer через горутины

```go
// Паттерн: буферизация через канал + горутина-writer
type AsyncProducer struct {
    writer *kafka.Writer
    ch     chan kafka.Message
    wg     sync.WaitGroup
}

func NewAsyncProducer(brokers []string, topic string, bufferSize int) *AsyncProducer {
    p := &AsyncProducer{
        writer: &kafka.Writer{
            Addr:         kafka.TCP(brokers...),
            Topic:        topic,
            Balancer:     &kafka.Hash{},
            BatchTimeout: 50 * time.Millisecond,
            RequiredAcks: kafka.RequireAll,
        },
        ch: make(chan kafka.Message, bufferSize),
    }

    p.wg.Add(1)
    go p.run()

    return p
}

func (p *AsyncProducer) run() {
    defer p.wg.Done()

    batch := make([]kafka.Message, 0, 100)
    ticker := time.NewTicker(100 * time.Millisecond)
    defer ticker.Stop()

    for {
        select {
        case msg, ok := <-p.ch:
            if !ok {
                // Канал закрыт — отправляем оставшиеся
                if len(batch) > 0 {
                    p.flush(batch)
                }
                return
            }
            batch = append(batch, msg)
            if len(batch) >= 100 {
                p.flush(batch)
                batch = batch[:0]
            }

        case <-ticker.C:
            if len(batch) > 0 {
                p.flush(batch)
                batch = batch[:0]
            }
        }
    }
}

func (p *AsyncProducer) flush(batch []kafka.Message) {
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()

    if err := p.writer.WriteMessages(ctx, batch...); err != nil {
        log.Printf("ошибка отправки батча (%d сообщений): %v", len(batch), err)
    }
}

// Send — неблокирующая отправка (блокирует только если буфер полон)
func (p *AsyncProducer) Send(msg kafka.Message) {
    p.ch <- msg
}

// Close — дожидается отправки всех сообщений
func (p *AsyncProducer) Close() {
    close(p.ch)
    p.wg.Wait()
    p.writer.Close()
}
```

**Сравнение с C#**:

| Аспект | C# (Confluent.Kafka) | Go (kafka-go) |
|--------|----------------------|---------------|
| **Sync отправка** | `ProduceAsync()` + `await` | `WriteMessages()` |
| **Async отправка** | `Produce()` + callback | Канал + горутина |
| **Батчинг** | Автоматический (linger.ms) | Автоматический (BatchTimeout) |
| **Подтверждение** | `DeliveryResult` | Ошибка от `WriteMessages` |
| **Ключ** | `Message<TKey, TValue>.Key` | `kafka.Message.Key` ([]byte) |
| **Headers** | `Headers` коллекция | `[]kafka.Header` |

### Consumer: потребление сообщений

#### Базовый consumer

```go
func consumeOrders(ctx context.Context) error {
    reader := kafka.NewReader(kafka.ReaderConfig{
        Brokers:  []string{"localhost:9092"},
        Topic:    "orders",
        GroupID:  "order-processor",
        MinBytes: 1,
        MaxBytes: 10e6,
    })
    defer reader.Close()

    for {
        // ReadMessage блокирует до получения сообщения или отмены контекста
        msg, err := reader.ReadMessage(ctx)
        if err != nil {
            if errors.Is(err, context.Canceled) {
                return nil // Штатное завершение
            }
            return fmt.Errorf("чтение из Kafka: %w", err)
        }

        var order Order
        if err := json.Unmarshal(msg.Value, &order); err != nil {
            log.Printf("невалидное сообщение (offset=%d): %v", msg.Offset, err)
            continue // Пропускаем невалидные — они не будут обработаны
        }

        if err := processOrder(ctx, order); err != nil {
            log.Printf("ошибка обработки заказа %s: %v", order.ID, err)
            // При ошибке обработки — сообщение уже прочитано
            // Нужна стратегия: retry, DLQ или пропуск
        }

        log.Printf("обработан заказ %s (partition=%d, offset=%d)",
            order.ID, msg.Partition, msg.Offset)
    }
}
```

#### Manual commit vs Auto commit

```go
// Auto commit (по умолчанию) — ReadMessage автоматически коммитит offset
reader := kafka.NewReader(kafka.ReaderConfig{
    Brokers:        []string{"localhost:9092"},
    Topic:          "orders",
    GroupID:        "order-processor",
    CommitInterval: time.Second, // Коммит каждую секунду
})

// Manual commit — для at-least-once гарантий
reader = kafka.NewReader(kafka.ReaderConfig{
    Brokers: []string{"localhost:9092"},
    Topic:   "orders",
    GroupID: "order-processor",
    // CommitInterval: 0 — не задаём, коммитим вручную
})

for {
    // FetchMessage НЕ коммитит offset (в отличие от ReadMessage)
    msg, err := reader.FetchMessage(ctx)
    if err != nil {
        break
    }

    // Обрабатываем сообщение
    if err := processOrder(ctx, msg); err != nil {
        log.Printf("ошибка: %v", err)
        continue // Не коммитим — при рестарте сообщение будет обработано повторно
    }

    // Коммитим только после успешной обработки
    if err := reader.CommitMessages(ctx, msg); err != nil {
        log.Printf("ошибка коммита offset: %v", err)
    }
}
```

> 💡 **Для C# разработчиков**: В Confluent.Kafka вы управляете offset через `consumer.Commit()` или `EnableAutoCommit`. В kafka-go разница между `ReadMessage` (auto commit) и `FetchMessage` (manual commit) делает выбор явным.

> ⚠️ **At-least-once**: При manual commit сообщение может быть обработано повторно (crash между обработкой и коммитом). Реализуйте **идемпотентность** в consumer — см. раздел [Паттерны](#идемпотентность-exactly-once-processing).

#### Параллельная обработка с worker pool

```go
// Паттерн: reader читает из Kafka, workers обрабатывают параллельно
func consumeWithWorkers(ctx context.Context, reader *kafka.Reader, workers int) error {
    // Канал для передачи сообщений воркерам
    jobs := make(chan kafka.Message, workers*2)

    var wg sync.WaitGroup

    // Запускаем worker pool
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func(workerID int) {
            defer wg.Done()
            for msg := range jobs {
                if err := processMessage(ctx, msg); err != nil {
                    log.Printf("[worker %d] ошибка обработки offset=%d: %v",
                        workerID, msg.Offset, err)
                    continue
                }
                // Коммитим offset после успешной обработки
                if err := reader.CommitMessages(ctx, msg); err != nil {
                    log.Printf("[worker %d] ошибка коммита: %v", workerID, err)
                }
            }
        }(i)
    }

    // Читаем сообщения и передаём воркерам
    for {
        msg, err := reader.FetchMessage(ctx)
        if err != nil {
            if errors.Is(err, context.Canceled) {
                break
            }
            return fmt.Errorf("чтение: %w", err)
        }
        jobs <- msg
    }

    close(jobs)
    wg.Wait()
    return nil
}
```

> ⚠️ **Предупреждение о порядке**: При параллельной обработке порядок сообщений **не гарантируется**. Если порядок важен, обрабатывайте сообщения последовательно в рамках одной партиции. Вариант — создать отдельный worker на каждую партицию.

### Consumer Groups

Consumer groups позволяют масштабировать обработку: Kafka распределяет партиции между участниками группы. Каждая партиция обрабатывается ровно одним consumer в группе.

```go
// Несколько инстансов с одним GroupID автоматически делят партиции
func startConsumer(ctx context.Context, brokers []string, groupID string) {
    reader := kafka.NewReader(kafka.ReaderConfig{
        Brokers: brokers,
        Topic:   "events",
        GroupID: groupID,          // Все инстансы с одним GroupID = одна группа

        // Стратегия начала чтения для новых групп
        StartOffset: kafka.FirstOffset, // Читать с начала (аналог Earliest)
        // StartOffset: kafka.LastOffset, // Только новые (аналог Latest)

        // Rebalance strategy
        GroupBalancers: []kafka.GroupBalancer{
            kafka.RangeGroupBalancer{},      // По умолчанию
            kafka.RoundRobinGroupBalancer{}, // Равномерное распределение
        },

        // Heartbeat — как часто consumer сообщает, что жив
        HeartbeatInterval: 3 * time.Second,
        // Таймаут сессии — если нет heartbeat, consumer считается мёртвым
        SessionTimeout: 30 * time.Second,
        // Таймаут rebalance — сколько ждать присоединения всех consumers
        RebalanceTimeout: 60 * time.Second,
    })
    defer reader.Close()

    log.Printf("consumer %s запущен (группа: %s)", reader.Config().GroupID, groupID)

    for {
        msg, err := reader.FetchMessage(ctx)
        if err != nil {
            if errors.Is(err, context.Canceled) {
                return
            }
            log.Printf("ошибка чтения: %v", err)
            continue
        }

        log.Printf("partition=%d offset=%d key=%s",
            msg.Partition, msg.Offset, string(msg.Key))

        if err := reader.CommitMessages(ctx, msg); err != nil {
            log.Printf("ошибка коммита: %v", err)
        }
    }
}
```

**Масштабирование**: Запустите N инстансов с одним `GroupID`, и Kafka автоматически распределит партиции. Максимальный параллелизм = количество партиций в топике.

### Production конфигурация Kafka

#### Production Writer (Producer)

```go
func newProductionWriter(brokers []string, topic string) *kafka.Writer {
    return &kafka.Writer{
        Addr:  kafka.TCP(brokers...),
        Topic: topic,

        // Балансировка — по ключу для сохранения порядка
        Balancer: &kafka.Hash{},

        // Батчинг — накапливаем сообщения перед отправкой
        BatchSize:    100,                   // До 100 сообщений в батче
        BatchBytes:   1048576,               // До 1 MB в батче
        BatchTimeout: 10 * time.Millisecond, // Максимум 10ms ожидания

        // Надёжность
        RequiredAcks: kafka.RequireAll,  // Все ISR реплики подтвердили
        MaxAttempts:  10,                // Retry при transient ошибках
        WriteTimeout: 10 * time.Second,
        ReadTimeout:  10 * time.Second,

        // Сжатие — уменьшает трафик и дисковое пространство
        Compression: kafka.Zstd, // Лучшее соотношение сжатие/скорость

        // Логирование
        Logger:      kafka.LoggerFunc(log.Printf),
        ErrorLogger: kafka.LoggerFunc(log.Printf),

        // Автоматическое создание топика (отключить в production!)
        AllowAutoTopicCreation: false,
    }
}
```

#### Production Reader (Consumer)

```go
func newProductionReader(brokers []string, topic, groupID string) *kafka.Reader {
    return kafka.NewReader(kafka.ReaderConfig{
        Brokers: brokers,
        Topic:   topic,
        GroupID: groupID,

        // Размер fetch
        MinBytes: 1,          // Не ждать накопления
        MaxBytes: 10 << 20,   // 10 MB максимум за fetch

        // Offset management
        StartOffset:    kafka.LastOffset,  // Новые группы читают только новые
        CommitInterval: 0,                 // Manual commit

        // Таймауты
        MaxWait:           500 * time.Millisecond,
        HeartbeatInterval: 3 * time.Second,
        SessionTimeout:    30 * time.Second,
        RebalanceTimeout:  60 * time.Second,

        // Retry
        RetentionTime: 7 * 24 * time.Hour, // Хранить offset 7 дней

        // Логирование
        Logger:      kafka.LoggerFunc(log.Printf),
        ErrorLogger: kafka.LoggerFunc(log.Printf),
    })
}
```

#### TLS и SASL аутентификация

```go
import (
    "crypto/tls"
    "crypto/x509"
    "os"

    "github.com/segmentio/kafka-go"
    "github.com/segmentio/kafka-go/sasl/scram"
)

func newTLSWriter(brokers []string, topic string) (*kafka.Writer, error) {
    // Загружаем CA сертификат
    caCert, err := os.ReadFile("/etc/kafka/ca.crt")
    if err != nil {
        return nil, fmt.Errorf("чтение CA сертификата: %w", err)
    }
    caCertPool := x509.NewCertPool()
    caCertPool.AppendCertsFromPEM(caCert)

    // SASL/SCRAM аутентификация
    mechanism, err := scram.Mechanism(scram.SHA512,
        os.Getenv("KAFKA_USERNAME"),
        os.Getenv("KAFKA_PASSWORD"),
    )
    if err != nil {
        return nil, fmt.Errorf("SASL механизм: %w", err)
    }

    // Dialer с TLS и SASL
    dialer := &kafka.Dialer{
        SASLMechanism: mechanism,
        TLS: &tls.Config{
            RootCAs: caCertPool,
        },
    }

    transport := &kafka.Transport{
        TLS:  dialer.TLS,
        SASL: mechanism,
    }

    return &kafka.Writer{
        Addr:      kafka.TCP(brokers...),
        Topic:     topic,
        Transport: transport,
    }, nil
}
```

### Error Handling и Dead Letter Topics

В отличие от MassTransit, где `_error` и `_skipped` очереди создаются автоматически, в Go вы реализуете Dead Letter Topic (DLT) вручную.

#### Классификация ошибок

```go
// Transient ошибки — временные, имеет смысл retry
// Permanent ошибки — повторная обработка не поможет

type permanentError struct {
    err error
}

func (e *permanentError) Error() string { return e.err.Error() }
func (e *permanentError) Unwrap() error { return e.err }

func isPermanent(err error) bool {
    var pe *permanentError
    return errors.As(err, &pe)
}

// Примеры:
// - JSON unmarshal error → permanent (данные невалидны)
// - Database timeout → transient (повторить)
// - Business rule violation → permanent
// - Network error → transient
```

#### Dead Letter Topic реализация

```go
type ConsumerWithDLT struct {
    reader    *kafka.Reader
    dlWriter  *kafka.Writer // Writer для Dead Letter Topic
    maxRetry  int
}

func NewConsumerWithDLT(brokers []string, topic, groupID string, maxRetry int) *ConsumerWithDLT {
    return &ConsumerWithDLT{
        reader: kafka.NewReader(kafka.ReaderConfig{
            Brokers: brokers,
            Topic:   topic,
            GroupID: groupID,
        }),
        dlWriter: &kafka.Writer{
            Addr:  kafka.TCP(brokers...),
            Topic: topic + ".dlq", // Конвенция: <topic>.dlq
        },
        maxRetry: maxRetry,
    }
}

func (c *ConsumerWithDLT) Run(ctx context.Context) error {
    defer c.reader.Close()
    defer c.dlWriter.Close()

    for {
        msg, err := c.reader.FetchMessage(ctx)
        if err != nil {
            if errors.Is(err, context.Canceled) {
                return nil
            }
            return fmt.Errorf("fetch: %w", err)
        }

        if err := c.processWithRetry(ctx, msg); err != nil {
            // Все retry исчерпаны или permanent error — отправляем в DLT
            if dlErr := c.sendToDLT(ctx, msg, err); dlErr != nil {
                log.Printf("КРИТИЧНО: не удалось отправить в DLT: %v", dlErr)
                // Не коммитим — сообщение будет обработано повторно
                continue
            }
            log.Printf("сообщение отправлено в DLT (offset=%d): %v", msg.Offset, err)
        }

        // Коммитим offset (успех или отправка в DLT)
        if err := c.reader.CommitMessages(ctx, msg); err != nil {
            log.Printf("ошибка коммита: %v", err)
        }
    }
}

func (c *ConsumerWithDLT) processWithRetry(ctx context.Context, msg kafka.Message) error {
    var lastErr error

    for attempt := 0; attempt <= c.maxRetry; attempt++ {
        err := processMessage(ctx, msg)
        if err == nil {
            return nil
        }

        // Permanent error — не retry
        if isPermanent(err) {
            return err
        }

        lastErr = err
        if attempt < c.maxRetry {
            // Exponential backoff: 100ms, 200ms, 400ms, 800ms, ...
            backoff := time.Duration(100<<uint(attempt)) * time.Millisecond
            log.Printf("retry %d/%d через %v: %v", attempt+1, c.maxRetry, backoff, err)

            select {
            case <-time.After(backoff):
            case <-ctx.Done():
                return ctx.Err()
            }
        }
    }

    return fmt.Errorf("исчерпаны retry (%d попыток): %w", c.maxRetry, lastErr)
}

func (c *ConsumerWithDLT) sendToDLT(ctx context.Context, original kafka.Message, processingErr error) error {
    // Сохраняем контекст ошибки в headers
    headers := make([]kafka.Header, len(original.Headers))
    copy(headers, original.Headers)

    headers = append(headers,
        kafka.Header{Key: "dlq-error", Value: []byte(processingErr.Error())},
        kafka.Header{Key: "dlq-original-topic", Value: []byte(original.Topic)},
        kafka.Header{Key: "dlq-original-partition", Value: []byte(fmt.Sprintf("%d", original.Partition))},
        kafka.Header{Key: "dlq-original-offset", Value: []byte(fmt.Sprintf("%d", original.Offset))},
        kafka.Header{Key: "dlq-timestamp", Value: []byte(time.Now().UTC().Format(time.RFC3339))},
    )

    return c.dlWriter.WriteMessages(ctx, kafka.Message{
        Key:     original.Key,
        Value:   original.Value,
        Headers: headers,
    })
}
```

**Сравнение с C# MassTransit**:

| Аспект | C# MassTransit | Go (ручная реализация) |
|--------|----------------|----------------------|
| **DLQ создание** | Автоматически (`_error` queue) | Вручную (создать топик, написать логику) |
| **Retry** | `UseMessageRetry(r => r.Exponential(...))` | Цикл с backoff |
| **Error context** | Автоматически (exception details) | Headers с метаданными ошибки |
| **Reprocessing** | MassTransit Retry/Redelivery | Читаем из DLT и отправляем обратно |
| **Конфигурация** | Fluent API | Явный код |

> 💡 **Совет**: Создайте утилиту для мониторинга DLT — Prometheus метрику `dlq_messages_total` и alert, когда DLT начинает расти.

---

## RabbitMQ (amqp091-go)

RabbitMQ — классический брокер сообщений, реализующий протокол AMQP 0.9.1. В отличие от Kafka (лог событий), RabbitMQ — это **очередь**: сообщение доставляется одному consumer и удаляется после подтверждения. RabbitMQ отлично подходит для task queues, RPC и сложной маршрутизации.

> 💡 **Для C# разработчиков**: RabbitMQ — самый популярный брокер в .NET экосистеме. Вы наверняка работали с ним через MassTransit, который скрывает AMQP-детали (exchanges, bindings, channels). В Go вы работаете с AMQP напрямую — это означает, что вы должны понимать, как устроены exchanges и bindings.

Установка:

```bash
go get github.com/rabbitmq/amqp091-go
```

### Подключение и управление каналами

#### Базовое подключение

```go
import amqp "github.com/rabbitmq/amqp091-go"

func connectRabbitMQ(url string) (*amqp.Connection, *amqp.Channel, error) {
    // Подключение к RabbitMQ
    conn, err := amqp.Dial(url)
    if err != nil {
        return nil, nil, fmt.Errorf("подключение к RabbitMQ: %w", err)
    }

    // Создание канала — основной объект для операций
    ch, err := conn.Channel()
    if err != nil {
        conn.Close()
        return nil, nil, fmt.Errorf("создание канала: %w", err)
    }

    return conn, ch, nil
}

func main() {
    conn, ch, err := connectRabbitMQ("amqp://guest:guest@localhost:5672/")
    if err != nil {
        log.Fatal(err)
    }
    defer conn.Close()
    defer ch.Close()

    log.Println("подключение к RabbitMQ установлено")
}
```

**C#** (RabbitMQ.Client):
```csharp
var factory = new ConnectionFactory
{
    HostName = "localhost",
    UserName = "guest",
    Password = "guest"
};
await using var connection = await factory.CreateConnectionAsync();
await using var channel = await connection.CreateChannelAsync();
```

> ⚠️ **Критически важно**: Каналы (`amqp.Channel`) **НЕ goroutine-safe**! Используйте один канал на горутину. Подключения (`amqp.Connection`) — потокобезопасны. В C# `IChannel` также не thread-safe, но MassTransit скрывает это за абстракцией.

#### Пул каналов

```go
// ChannelPool — безопасное управление каналами для concurrent доступа
type ChannelPool struct {
    conn *amqp.Connection
    pool chan *amqp.Channel
}

func NewChannelPool(conn *amqp.Connection, size int) (*ChannelPool, error) {
    pool := make(chan *amqp.Channel, size)

    for i := 0; i < size; i++ {
        ch, err := conn.Channel()
        if err != nil {
            return nil, fmt.Errorf("создание канала %d: %w", i, err)
        }
        pool <- ch
    }

    return &ChannelPool{conn: conn, pool: pool}, nil
}

// Get — получить канал из пула (блокирует, если пул пуст)
func (p *ChannelPool) Get() *amqp.Channel {
    return <-p.pool
}

// Put — вернуть канал в пул
func (p *ChannelPool) Put(ch *amqp.Channel) {
    // Проверяем, что канал ещё жив
    if ch.IsClosed() {
        newCh, err := p.conn.Channel()
        if err != nil {
            log.Printf("ошибка пересоздания канала: %v", err)
            return
        }
        ch = newCh
    }
    p.pool <- ch
}

// WithChannel — выполнить операцию с каналом из пула
func (p *ChannelPool) WithChannel(fn func(*amqp.Channel) error) error {
    ch := p.Get()
    defer p.Put(ch)
    return fn(ch)
}

func (p *ChannelPool) Close() {
    close(p.pool)
    for ch := range p.pool {
        ch.Close()
    }
}
```

### Exchanges, Queues, Bindings

RabbitMQ использует модель exchange → binding → queue. Сообщения отправляются в exchange, который маршрутизирует их в очереди через bindings.

#### Типы exchange

| Тип | Маршрутизация | Аналог в C# MassTransit | Пример использования |
|-----|--------------|-------------------------|---------------------|
| **direct** | По точному routing key | Endpoint name | Точечная доставка |
| **fanout** | Во все привязанные очереди | `Publish<T>()` (все consumers) | Broadcast, notifications |
| **topic** | По паттерну routing key | `Publish<T>()` с фильтром | Логирование по уровням |
| **headers** | По headers сообщения | Редко используется | Сложная маршрутизация |

```go
func setupTopology(ch *amqp.Channel) error {
    // Объявляем exchange
    err := ch.ExchangeDeclare(
        "orders",  // Имя
        "topic",   // Тип
        true,      // Durable — переживёт рестарт RabbitMQ
        false,     // Auto-delete — не удалять при отсутствии bindings
        false,     // Internal — доступен для publish
        false,     // No-wait — ждать подтверждения от сервера
        nil,       // Arguments
    )
    if err != nil {
        return fmt.Errorf("exchange declare: %w", err)
    }

    // Объявляем очередь
    q, err := ch.QueueDeclare(
        "order-processor", // Имя очереди
        true,              // Durable
        false,             // Auto-delete
        false,             // Exclusive (только одно подключение)
        false,             // No-wait
        amqp.Table{
            // Dead letter exchange для отклонённых сообщений
            "x-dead-letter-exchange":    "orders.dlx",
            "x-dead-letter-routing-key": "dead",
            // Максимальная длина очереди (overflow → DLX)
            "x-max-length": int32(100000),
            // TTL сообщений — 24 часа
            "x-message-ttl": int32(86400000),
        },
    )
    if err != nil {
        return fmt.Errorf("queue declare: %w", err)
    }

    // Привязываем очередь к exchange с routing key паттерном
    err = ch.QueueBind(
        q.Name,            // Очередь
        "order.created",   // Routing key (паттерн для topic exchange)
        "orders",          // Exchange
        false,             // No-wait
        nil,               // Arguments
    )
    if err != nil {
        return fmt.Errorf("queue bind: %w", err)
    }

    // Для topic exchange: привязка с wildcard
    // "order.*" — order.created, order.updated, order.deleted
    // "order.#" — order.created, order.payment.completed
    err = ch.QueueBind(q.Name, "order.*", "orders", false, nil)

    log.Printf("топология настроена: exchange=%s, queue=%s", "orders", q.Name)
    return nil
}
```

### Publishing: подтверждения и гарантии

#### Базовая публикация

```go
func publishOrder(ctx context.Context, ch *amqp.Channel, order Order) error {
    body, err := json.Marshal(order)
    if err != nil {
        return fmt.Errorf("сериализация: %w", err)
    }

    return ch.PublishWithContext(ctx,
        "orders",        // Exchange
        "order.created", // Routing key
        false,           // Mandatory — вернуть, если нет подходящей очереди
        false,           // Immediate (deprecated в RabbitMQ 3.x)
        amqp.Publishing{
            ContentType:  "application/json",
            DeliveryMode: amqp.Persistent, // Сообщение сохраняется на диск
            MessageId:    uuid.NewString(), // Уникальный ID для идемпотентности
            Timestamp:    time.Now(),
            Type:         "OrderCreated",
            Body:         body,
        },
    )
}
```

#### Publisher Confirms

```go
// Publisher confirms — RabbitMQ подтверждает, что сообщение записано
func publishWithConfirm(ctx context.Context, ch *amqp.Channel, order Order) error {
    // Включаем режим confirm
    if err := ch.Confirm(false); err != nil {
        return fmt.Errorf("включение confirm mode: %w", err)
    }

    // Канал для получения подтверждений
    confirms := ch.NotifyPublish(make(chan amqp.Confirmation, 1))

    body, err := json.Marshal(order)
    if err != nil {
        return fmt.Errorf("сериализация: %w", err)
    }

    err = ch.PublishWithContext(ctx,
        "orders",
        "order.created",
        true, // Mandatory — обязательно доставить
        false,
        amqp.Publishing{
            ContentType:  "application/json",
            DeliveryMode: amqp.Persistent,
            MessageId:    uuid.NewString(),
            Body:         body,
        },
    )
    if err != nil {
        return fmt.Errorf("publish: %w", err)
    }

    // Ждём подтверждение от RabbitMQ
    select {
    case confirm := <-confirms:
        if !confirm.Ack {
            return fmt.Errorf("сообщение не подтверждено (nack)")
        }
        return nil
    case <-ctx.Done():
        return ctx.Err()
    case <-time.After(5 * time.Second):
        return fmt.Errorf("таймаут ожидания подтверждения")
    }
}
```

> 💡 **Для C# разработчиков**: В RabbitMQ.Client это `channel.WaitForConfirmsAsync()`. MassTransit включает publisher confirms автоматически. В Go — явная настройка через `ch.Confirm()`.

### Consuming: prefetch, ack/nack

```go
func consumeOrders(ctx context.Context, ch *amqp.Channel) error {
    // Prefetch — ограничиваем количество unacked сообщений
    // Это критично для backpressure и равномерного распределения
    err := ch.Qos(
        10,    // Prefetch count — максимум 10 unacked на consumer
        0,     // Prefetch size — 0 = без ограничения по размеру
        false, // Global — false = per consumer, true = per channel
    )
    if err != nil {
        return fmt.Errorf("настройка QoS: %w", err)
    }

    // Начинаем потребление
    deliveries, err := ch.Consume(
        "order-processor", // Очередь
        "worker-1",        // Consumer tag (уникальный идентификатор)
        false,             // Auto-ack: false = manual ack
        false,             // Exclusive
        false,             // No-local
        false,             // No-wait
        nil,               // Arguments
    )
    if err != nil {
        return fmt.Errorf("consume: %w", err)
    }

    for {
        select {
        case d, ok := <-deliveries:
            if !ok {
                return fmt.Errorf("канал deliveries закрыт")
            }

            var order Order
            if err := json.Unmarshal(d.Body, &order); err != nil {
                // Невалидные данные — reject без requeue (пойдут в DLX)
                log.Printf("невалидное сообщение: %v", err)
                d.Reject(false) // false = не возвращать в очередь
                continue
            }

            if err := processOrder(ctx, order); err != nil {
                // Ошибка обработки — nack с requeue для retry
                log.Printf("ошибка обработки: %v", err)
                d.Nack(false, true) // multiple=false, requeue=true
                continue
            }

            // Успешно — ack
            d.Ack(false) // multiple=false (подтверждаем только это сообщение)

        case <-ctx.Done():
            return nil
        }
    }
}
```

#### Worker Pool для параллельной обработки

```go
func consumeWithWorkerPool(ctx context.Context, ch *amqp.Channel, workers int) error {
    // Prefetch = 2x workers — всегда есть сообщения для обработки
    if err := ch.Qos(workers*2, 0, false); err != nil {
        return fmt.Errorf("QoS: %w", err)
    }

    deliveries, err := ch.Consume("order-processor", "", false, false, false, false, nil)
    if err != nil {
        return fmt.Errorf("consume: %w", err)
    }

    var wg sync.WaitGroup
    // Запускаем workers горутин, каждая читает из одного канала deliveries
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func(workerID int) {
            defer wg.Done()
            for {
                select {
                case d, ok := <-deliveries:
                    if !ok {
                        return
                    }
                    if err := processDelivery(ctx, d); err != nil {
                        log.Printf("[worker %d] ошибка: %v", workerID, err)
                        d.Nack(false, true)
                    } else {
                        d.Ack(false)
                    }
                case <-ctx.Done():
                    return
                }
            }
        }(i)
    }

    wg.Wait()
    return nil
}
```

> 💡 **Подсказка по prefetch**: Устанавливайте `prefetch = 2 * workers`. Это обеспечит, что каждый worker всегда имеет следующее сообщение для обработки, минимизируя простой.

**Сравнение ack/nack с C#**:

| Действие | C# (RabbitMQ.Client) | Go (amqp091-go) |
|----------|---------------------|-----------------|
| **Подтвердить** | `channel.BasicAckAsync(tag, false)` | `d.Ack(false)` |
| **Отклонить + requeue** | `channel.BasicNackAsync(tag, false, true)` | `d.Nack(false, true)` |
| **Отклонить без requeue** | `channel.BasicRejectAsync(tag, false)` | `d.Reject(false)` |
| **Auto ack** | `autoAck: true` в `BasicConsumeAsync` | `autoAck: true` в `Consume` |

### Connection Recovery и Reconnection

Это **самый важный** production-аспект RabbitMQ в Go. В отличие от C#, где `RabbitMQ.Client` имеет `AutomaticRecoveryEnabled = true`, библиотека `amqp091-go` **не реализует автоматическое переподключение**.

> ⚠️ **Критическое отличие от C#**: В .NET вы устанавливаете `factory.AutomaticRecoveryEnabled = true` и забываете. В Go вы **обязаны** реализовать reconnection самостоятельно. Без этого любой сетевой сбой убьёт ваш сервис.

```go
// RabbitMQClient — обёртка с автоматическим переподключением
type RabbitMQClient struct {
    url        string
    conn       *amqp.Connection
    ch         *amqp.Channel
    mu         sync.RWMutex
    done       chan struct{}
    notifyClose chan *amqp.Error
}

func NewRabbitMQClient(url string) (*RabbitMQClient, error) {
    client := &RabbitMQClient{
        url:  url,
        done: make(chan struct{}),
    }

    if err := client.connect(); err != nil {
        return nil, err
    }

    go client.reconnectLoop()

    return client, nil
}

func (c *RabbitMQClient) connect() error {
    conn, err := amqp.Dial(c.url)
    if err != nil {
        return fmt.Errorf("dial: %w", err)
    }

    ch, err := conn.Channel()
    if err != nil {
        conn.Close()
        return fmt.Errorf("channel: %w", err)
    }

    c.mu.Lock()
    c.conn = conn
    c.ch = ch
    c.notifyClose = conn.NotifyClose(make(chan *amqp.Error, 1))
    c.mu.Unlock()

    log.Println("подключение к RabbitMQ установлено")
    return nil
}

func (c *RabbitMQClient) reconnectLoop() {
    for {
        select {
        case <-c.done:
            return
        case amqpErr, ok := <-c.notifyClose:
            if !ok {
                return // Штатное закрытие
            }
            log.Printf("соединение с RabbitMQ потеряно: %v", amqpErr)

            // Exponential backoff с jitter
            for attempt := 0; ; attempt++ {
                backoff := time.Duration(math.Min(
                    float64(time.Second)*math.Pow(2, float64(attempt)),
                    float64(30*time.Second),
                ))
                // Добавляем jitter ±25%
                jitter := time.Duration(rand.Int63n(int64(backoff) / 2))
                backoff = backoff + jitter

                log.Printf("переподключение к RabbitMQ через %v (попытка %d)...", backoff, attempt+1)

                select {
                case <-time.After(backoff):
                case <-c.done:
                    return
                }

                if err := c.connect(); err != nil {
                    log.Printf("ошибка переподключения: %v", err)
                    continue
                }

                log.Println("переподключение к RabbitMQ успешно")
                break
            }
        }
    }
}

// Channel — получить текущий канал (потокобезопасно)
func (c *RabbitMQClient) Channel() *amqp.Channel {
    c.mu.RLock()
    defer c.mu.RUnlock()
    return c.ch
}

// Publish — публикация с автоматическим retry при потере соединения
func (c *RabbitMQClient) Publish(ctx context.Context, exchange, routingKey string, msg amqp.Publishing) error {
    for attempt := 0; attempt < 3; attempt++ {
        ch := c.Channel()
        if ch == nil {
            time.Sleep(time.Second)
            continue
        }

        err := ch.PublishWithContext(ctx, exchange, routingKey, false, false, msg)
        if err == nil {
            return nil
        }

        // Если ошибка связана с закрытым каналом, ждём reconnect
        if errors.Is(err, amqp.ErrClosed) {
            log.Printf("канал закрыт, ожидаем переподключения...")
            time.Sleep(time.Second * time.Duration(attempt+1))
            continue
        }

        return err
    }

    return fmt.Errorf("publish не удался после 3 попыток")
}

func (c *RabbitMQClient) Close() {
    close(c.done)
    c.mu.Lock()
    defer c.mu.Unlock()
    if c.ch != nil {
        c.ch.Close()
    }
    if c.conn != nil {
        c.conn.Close()
    }
}
```

### Dead Letter Exchanges (DLX)

DLX — механизм RabbitMQ для обработки сообщений, которые не удалось доставить: отклонённые (`reject`/`nack` без requeue), expired (TTL) или overflow (очередь переполнена).

```
┌─────────┐     publish     ┌──────────┐     binding     ┌────────────┐
│ Producer │ ──────────────→ │ Exchange │ ──────────────→ │   Queue    │
└─────────┘                  └──────────┘                 └────────────┘
                                                               │
                                                          reject/nack
                                                          TTL expired
                                                          overflow
                                                               │
                                                               ▼
                                                         ┌──────────┐     ┌──────────┐
                                                         │   DLX    │ ──→ │ DLQ      │
                                                         └──────────┘     └──────────┘
```

#### Настройка DLX

```go
func setupDLX(ch *amqp.Channel) error {
    // 1. Создаём Dead Letter Exchange
    err := ch.ExchangeDeclare("orders.dlx", "direct", true, false, false, false, nil)
    if err != nil {
        return fmt.Errorf("DLX exchange: %w", err)
    }

    // 2. Создаём Dead Letter Queue
    _, err = ch.QueueDeclare("orders.dlq", true, false, false, false, nil)
    if err != nil {
        return fmt.Errorf("DLQ queue: %w", err)
    }

    // 3. Привязываем DLQ к DLX
    err = ch.QueueBind("orders.dlq", "dead", "orders.dlx", false, nil)
    if err != nil {
        return fmt.Errorf("DLQ bind: %w", err)
    }

    // 4. Основная очередь с указанием DLX
    _, err = ch.QueueDeclare(
        "order-processor",
        true, false, false, false,
        amqp.Table{
            "x-dead-letter-exchange":    "orders.dlx",
            "x-dead-letter-routing-key": "dead",
        },
    )
    if err != nil {
        return fmt.Errorf("main queue: %w", err)
    }

    return nil
}
```

#### Retry через цепочку DLX + TTL

```go
// Паттерн: retry через промежуточные очереди с TTL
// Сообщение → retry-queue (TTL=5s) → expire → DLX → основная очередь
func setupRetryTopology(ch *amqp.Channel) error {
    // Основной exchange
    ch.ExchangeDeclare("orders", "direct", true, false, false, false, nil)
    // Retry exchange
    ch.ExchangeDeclare("orders.retry", "direct", true, false, false, false, nil)
    // DLX для окончательных отказов
    ch.ExchangeDeclare("orders.dlx", "direct", true, false, false, false, nil)

    // Retry очередь с TTL — сообщения «отлёживаются» и возвращаются
    ch.QueueDeclare("orders.retry.5s", true, false, false, false, amqp.Table{
        "x-dead-letter-exchange":    "orders",      // После TTL → обратно в основной exchange
        "x-dead-letter-routing-key": "process",
        "x-message-ttl":             int32(5000),   // 5 секунд
    })
    ch.QueueBind("orders.retry.5s", "retry", "orders.retry", false, nil)

    ch.QueueDeclare("orders.retry.30s", true, false, false, false, amqp.Table{
        "x-dead-letter-exchange":    "orders",
        "x-dead-letter-routing-key": "process",
        "x-message-ttl":             int32(30000), // 30 секунд
    })
    ch.QueueBind("orders.retry.30s", "retry-slow", "orders.retry", false, nil)

    // Основная очередь
    ch.QueueDeclare("order-processor", true, false, false, false, amqp.Table{
        "x-dead-letter-exchange":    "orders.dlx",
        "x-dead-letter-routing-key": "dead",
    })
    ch.QueueBind("order-processor", "process", "orders", false, nil)

    // DLQ
    ch.QueueDeclare("orders.dlq", true, false, false, false, nil)
    ch.QueueBind("orders.dlq", "dead", "orders.dlx", false, nil)

    return nil
}

// При ошибке обработки — отправляем в retry queue
func retryMessage(ch *amqp.Channel, d amqp.Delivery, attempt int) error {
    routingKey := "retry"
    if attempt > 3 {
        routingKey = "retry-slow" // После 3 попыток — более длинная пауза
    }

    return ch.PublishWithContext(context.Background(),
        "orders.retry",
        routingKey,
        false, false,
        amqp.Publishing{
            ContentType: d.ContentType,
            Body:        d.Body,
            Headers: amqp.Table{
                "x-retry-count": int32(attempt),
                "x-first-failure": func() interface{} {
                    if v, ok := d.Headers["x-first-failure"]; ok {
                        return v
                    }
                    return time.Now().UTC().Format(time.RFC3339)
                }(),
            },
        },
    )
}
```

**Сравнение DLX с C# MassTransit**:

| Аспект | C# MassTransit | Go (amqp091-go) |
|--------|----------------|-----------------|
| **Создание DLQ** | Автоматически | Ручная настройка топологии |
| **Retry** | `UseMessageRetry`, `UseDelayedRedelivery` | DLX + TTL цепочки или ручной retry |
| **Error metadata** | Автоматически (exception stack trace) | Headers с ручным добавлением |
| **Reprocessing** | Move message из error queue | Читаем из DLQ, публикуем обратно |
| **Delayed retry** | `UseDelayedExchangeMessageScheduler` | TTL очереди с DLX routing |

---

## NATS (nats.go)

NATS — легковесная система обмена сообщениями с фокусом на простоту и низкую latency. NATS зародился в Cloud Foundry и стал де-факто стандартом для межсервисного общения в Go-микросервисах. NATS имеет два режима: **Core NATS** (fire-and-forget, как Redis Pub/Sub) и **JetStream** (персистентный обмен, аналог Kafka).

> 💡 **Для C# разработчиков**: NATS менее популярен в .NET-мире (хотя `NATS.Client` существует), но очень распространён в Go-экосистеме. Если Kafka — это «тяжёлая артиллерия» для event streaming, а RabbitMQ — «рабочая лошадка» для task queues, то NATS — «спортивный болид» для low-latency коммуникации между сервисами.

Установка:

```bash
go get github.com/nats-io/nats.go
```

### Core NATS: Pub/Sub и Request/Reply

Core NATS — это at-most-once delivery: если subscriber не подключён в момент отправки, сообщение теряется (как Redis Pub/Sub).

#### Pub/Sub

```go
import "github.com/nats-io/nats.go"

func coreNATSExample() error {
    // Подключение
    nc, err := nats.Connect(
        "nats://localhost:4222",
        nats.Name("order-service"),           // Имя клиента для мониторинга
        nats.ReconnectWait(2*time.Second),    // Пауза между переподключениями
        nats.MaxReconnects(60),               // Максимум попыток
        nats.ReconnectHandler(func(nc *nats.Conn) {
            log.Printf("переподключение к NATS: %s", nc.ConnectedUrl())
        }),
        nats.DisconnectErrHandler(func(nc *nats.Conn, err error) {
            log.Printf("отключение от NATS: %v", err)
        }),
    )
    if err != nil {
        return fmt.Errorf("подключение к NATS: %w", err)
    }
    defer nc.Close()

    // Подписка — получаем сообщения асинхронно через callback
    sub, err := nc.Subscribe("orders.created", func(msg *nats.Msg) {
        log.Printf("получен заказ: %s", string(msg.Data))

        var order Order
        if err := json.Unmarshal(msg.Data, &order); err != nil {
            log.Printf("невалидное сообщение: %v", err)
            return
        }

        processOrder(context.Background(), order)
    })
    if err != nil {
        return fmt.Errorf("подписка: %w", err)
    }
    defer sub.Unsubscribe()

    // Публикация
    order := Order{ID: "123", Total: 99.99}
    data, _ := json.Marshal(order)
    if err := nc.Publish("orders.created", data); err != nil {
        return fmt.Errorf("публикация: %w", err)
    }

    // Wildcard подписки
    // "orders.*" — orders.created, orders.updated (один уровень)
    // "orders.>" — orders.created, orders.payment.completed (все уровни)
    nc.Subscribe("orders.*", func(msg *nats.Msg) {
        log.Printf("событие заказа [%s]: %s", msg.Subject, string(msg.Data))
    })

    return nil
}
```

#### Queue Groups (балансировка нагрузки)

```go
// Queue groups — NATS распределяет сообщения между подписчиками в группе
// Каждое сообщение доставляется ровно одному подписчику в группе
func startWorker(nc *nats.Conn, workerID int) (*nats.Subscription, error) {
    return nc.QueueSubscribe(
        "tasks.process",    // Subject
        "task-workers",     // Queue group name
        func(msg *nats.Msg) {
            log.Printf("[worker %d] обработка: %s", workerID, string(msg.Data))
            // Все воркеры в группе "task-workers" делят нагрузку
        },
    )
}

// Запускаем 3 воркера — NATS распределит сообщения между ними
func main() {
    nc, _ := nats.Connect("nats://localhost:4222")
    for i := 0; i < 3; i++ {
        startWorker(nc, i)
    }
    select {} // Блокируем main
}
```

> 💡 **Для C# разработчиков**: Queue groups — аналог competing consumers в RabbitMQ и consumer groups в Kafka. В MassTransit это происходит автоматически при нескольких инстансах одного consumer.

#### Request/Reply (синхронный RPC)

```go
// Сервер — обрабатывает запросы и отвечает
func startRPCServer(nc *nats.Conn) (*nats.Subscription, error) {
    return nc.Subscribe("users.get", func(msg *nats.Msg) {
        var req GetUserRequest
        if err := json.Unmarshal(msg.Data, &req); err != nil {
            msg.Respond([]byte(`{"error":"invalid request"}`))
            return
        }

        user := User{ID: req.ID, Name: "John"}
        data, _ := json.Marshal(user)
        msg.Respond(data) // Ответ отправляется на msg.Reply
    })
}

// Клиент — отправляет запрос и ждёт ответ
func getUser(nc *nats.Conn, userID string) (*User, error) {
    req := GetUserRequest{ID: userID}
    data, _ := json.Marshal(req)

    // Request блокирует до получения ответа или таймаута
    msg, err := nc.Request("users.get", data, 5*time.Second)
    if err != nil {
        return nil, fmt.Errorf("RPC запрос: %w", err)
    }

    var user User
    if err := json.Unmarshal(msg.Data, &user); err != nil {
        return nil, fmt.Errorf("десериализация ответа: %w", err)
    }

    return &user, nil
}
```

### JetStream: персистентный обмен сообщениями

JetStream — надстройка над Core NATS, добавляющая персистентность, at-least-once/exactly-once delivery и возможность перечитывать сообщения. JetStream — это ответ NATS на Kafka.

```go
import (
    "github.com/nats-io/nats.go"
    "github.com/nats-io/nats.go/jetstream"
)

func jetStreamExample() error {
    nc, err := nats.Connect("nats://localhost:4222")
    if err != nil {
        return err
    }
    defer nc.Close()

    // Создаём JetStream context
    js, err := jetstream.New(nc)
    if err != nil {
        return fmt.Errorf("JetStream: %w", err)
    }

    ctx := context.Background()

    // Создаём или обновляем stream — хранилище сообщений
    stream, err := js.CreateOrUpdateStream(ctx, jetstream.StreamConfig{
        Name:     "ORDERS",
        Subjects: []string{"orders.>"},  // Все subjects, начинающиеся с "orders."

        // Хранение
        Storage:   jetstream.FileStorage,  // На диске (или MemoryStorage)
        Retention: jetstream.LimitsPolicy, // Хранить до лимитов

        // Лимиты
        MaxMsgs:    1000000,              // Максимум сообщений
        MaxBytes:   1 << 30,              // Максимум 1 GB
        MaxAge:     7 * 24 * time.Hour,   // Максимум 7 дней

        // Репликация
        Replicas: 3,                      // 3 реплики для HA

        // Дедупликация
        DuplicateWindow: 2 * time.Minute, // Окно дедупликации по Nats-Msg-Id
    })
    if err != nil {
        return fmt.Errorf("создание stream: %w", err)
    }
    log.Printf("stream создан: %s", stream.CachedInfo().Config.Name)

    // Публикация в JetStream — с подтверждением записи
    ack, err := js.Publish(ctx, "orders.created", []byte(`{"id":"123","total":99.99}`),
        jetstream.WithMsgID("order-123"), // ID для дедупликации
    )
    if err != nil {
        return fmt.Errorf("publish: %w", err)
    }
    log.Printf("опубликовано: stream=%s seq=%d", ack.Stream, ack.Sequence)

    return nil
}
```

#### Consumer: получение сообщений из JetStream

```go
func consumeJetStream(ctx context.Context, js jetstream.JetStream) error {
    // Создаём durable consumer — сохраняет позицию между перезапусками
    consumer, err := js.CreateOrUpdateConsumer(ctx, "ORDERS", jetstream.ConsumerConfig{
        Name:          "order-processor",
        Durable:       "order-processor",
        FilterSubject: "orders.created",

        // Delivery policy — откуда начать
        DeliverPolicy: jetstream.DeliverAllPolicy, // С самого начала
        // DeliverPolicy: jetstream.DeliverNewPolicy, // Только новые

        // Ack policy
        AckPolicy: jetstream.AckExplicitPolicy, // Ручное подтверждение
        AckWait:   30 * time.Second,             // Таймаут подтверждения

        // Retry — при отсутствии ack, сообщение будет повторно доставлено
        MaxDeliver: 5, // Максимум 5 попыток доставки

        // Backoff для retry
        BackOff: []time.Duration{
            5 * time.Second,
            15 * time.Second,
            30 * time.Second,
            60 * time.Second,
        },
    })
    if err != nil {
        return fmt.Errorf("создание consumer: %w", err)
    }

    // Потребление сообщений
    iter, err := consumer.Messages()
    if err != nil {
        return fmt.Errorf("messages: %w", err)
    }
    defer iter.Stop()

    for {
        msg, err := iter.Next()
        if err != nil {
            if errors.Is(err, jetstream.ErrMsgIteratorClosed) {
                return nil
            }
            return fmt.Errorf("next: %w", err)
        }

        var order Order
        if err := json.Unmarshal(msg.Data(), &order); err != nil {
            log.Printf("невалидное сообщение: %v", err)
            // Term — навсегда отклонить (не retry)
            msg.Term()
            continue
        }

        if err := processOrder(ctx, order); err != nil {
            log.Printf("ошибка обработки: %v", err)
            // Nak — запросить повторную доставку (с backoff из конфигурации)
            msg.Nak()
            continue
        }

        // Ack — успешно обработано
        msg.Ack()
        log.Printf("обработан заказ %s (seq=%d)", order.ID, msg.Headers().Get("Nats-Sequence"))
    }
}
```

### Push vs Pull Consumers

| Аспект | Push Consumer | Pull Consumer |
|--------|--------------|---------------|
| **Доставка** | NATS отправляет сообщения consumer | Consumer запрашивает сообщения |
| **Backpressure** | Ограничение через `MaxAckPending` | Полный контроль через `Fetch(batch)` |
| **Масштабирование** | Через queue groups | Через горизонтальное масштабирование |
| **Когда использовать** | Простые случаи, реальное время | Батчевая обработка, контроль нагрузки |

```go
// Pull consumer — явный запрос батча сообщений
func pullConsumer(ctx context.Context, js jetstream.JetStream) error {
    consumer, err := js.CreateOrUpdateConsumer(ctx, "ORDERS", jetstream.ConsumerConfig{
        Name:    "batch-processor",
        Durable: "batch-processor",
    })
    if err != nil {
        return err
    }

    for {
        // Fetch — запрашиваем до 10 сообщений, ждём до 5 секунд
        batch, err := consumer.Fetch(10, jetstream.FetchMaxWait(5*time.Second))
        if err != nil {
            if errors.Is(err, context.Canceled) {
                return nil
            }
            log.Printf("fetch ошибка: %v", err)
            continue
        }

        for msg := range batch.Messages() {
            if err := processMessage(ctx, msg); err != nil {
                msg.Nak()
            } else {
                msg.Ack()
            }
        }

        if batch.Error() != nil {
            log.Printf("batch error: %v", batch.Error())
        }
    }
}
```

### Key-Value Store и Object Store

JetStream включает встроенное Key-Value хранилище — лёгкая альтернатива Redis для простых сценариев.

```go
func kvExample(ctx context.Context, js jetstream.JetStream) error {
    // Создаём KV bucket
    kv, err := js.CreateOrUpdateKeyValue(ctx, jetstream.KeyValueConfig{
        Bucket:  "sessions",
        TTL:     30 * time.Minute,  // Автоматическое удаление
        History: 5,                  // Хранить 5 последних версий
    })
    if err != nil {
        return fmt.Errorf("KV bucket: %w", err)
    }

    // Put
    _, err = kv.Put(ctx, "user:123", []byte(`{"token":"abc","role":"admin"}`))
    if err != nil {
        return fmt.Errorf("put: %w", err)
    }

    // Get
    entry, err := kv.Get(ctx, "user:123")
    if err != nil {
        if errors.Is(err, jetstream.ErrKeyNotFound) {
            log.Println("ключ не найден")
            return nil
        }
        return fmt.Errorf("get: %w", err)
    }
    log.Printf("значение: %s (revision=%d)", string(entry.Value()), entry.Revision())

    // Watch — подписка на изменения (аналог Redis SUBSCRIBE, но для KV)
    watcher, err := kv.Watch(ctx, "user.*")
    if err != nil {
        return err
    }
    defer watcher.Stop()

    go func() {
        for entry := range watcher.Updates() {
            if entry == nil {
                continue // Начальный nil при запуске watcher
            }
            log.Printf("изменение: key=%s op=%s", entry.Key(), entry.Operation())
        }
    }()

    // Delete
    err = kv.Delete(ctx, "user:123")
    return err
}
```

> 💡 **NATS KV vs Redis**: NATS KV удобен, если у вас уже есть NATS и нужен простой key-value без дополнительной инфраструктуры. Для сложных сценариев (sorted sets, Lua скрипты, Pub/Sub с паттернами) Redis остаётся лучшим выбором.

---

## Redis Streams

Redis Streams — встроенная в Redis структура данных для persistent messaging. Если вы уже используете Redis (см. [раздел 4.2](./02_caching.md)), Redis Streams позволяет добавить очередь сообщений без дополнительной инфраструктуры.

> 💡 **Для C# разработчиков**: Redis Streams доступны через `StackExchange.Redis` (`StreamAdd`, `StreamRead`), но редко используются в .NET — обычно предпочитают MassTransit с RabbitMQ. В Go Redis Streams популярнее, особенно в проектах, где Redis уже есть для кэширования.

### Основные операции (XADD, XREAD)

```go
import "github.com/redis/go-redis/v9"

func redisStreamsBasic(ctx context.Context, rdb *redis.Client) error {
    // XADD — добавить сообщение в stream
    id, err := rdb.XAdd(ctx, &redis.XAddArgs{
        Stream: "events",
        ID:     "*", // Автоматический ID (timestamp-sequence)
        Values: map[string]interface{}{
            "type":    "order.created",
            "payload": `{"id":"123","total":99.99}`,
            "source":  "order-service",
        },
    }).Result()
    if err != nil {
        return fmt.Errorf("XADD: %w", err)
    }
    log.Printf("добавлено сообщение: %s", id) // 1706000000000-0

    // Ограничение размера stream
    rdb.XAdd(ctx, &redis.XAddArgs{
        Stream: "events",
        MaxLen: 100000,   // Максимум 100k записей
        Approx: true,     // Приблизительное ограничение (эффективнее)
        ID:     "*",
        Values: map[string]interface{}{"type": "test"},
    })

    // XREAD — чтение сообщений (блокирующее)
    streams, err := rdb.XRead(ctx, &redis.XReadArgs{
        Streams: []string{"events", "0"}, // stream name, start ID
        Count:   10,                       // Максимум 10 сообщений
        Block:   5 * time.Second,          // Блокировать до 5 секунд
    }).Result()
    if err != nil {
        if err == redis.Nil {
            log.Println("нет новых сообщений")
            return nil
        }
        return fmt.Errorf("XREAD: %w", err)
    }

    for _, stream := range streams {
        for _, msg := range stream.Messages {
            log.Printf("ID=%s type=%s payload=%s",
                msg.ID, msg.Values["type"], msg.Values["payload"])
        }
    }

    return nil
}
```

### Consumer Groups (Redis)

Consumer groups в Redis Streams работают аналогично Kafka consumer groups: каждое сообщение доставляется одному consumer в группе.

```go
func redisStreamsConsumerGroup(ctx context.Context, rdb *redis.Client) error {
    stream := "events"
    group := "event-processors"
    consumer := "worker-1"

    // Создаём consumer group ($ = только новые сообщения, 0 = с начала)
    err := rdb.XGroupCreateMkStream(ctx, stream, group, "$").Err()
    if err != nil && !strings.Contains(err.Error(), "BUSYGROUP") {
        return fmt.Errorf("создание группы: %w", err)
    }

    for {
        // XREADGROUP — читаем сообщения для нашего consumer
        streams, err := rdb.XReadGroup(ctx, &redis.XReadGroupArgs{
            Group:    group,
            Consumer: consumer,
            Streams:  []string{stream, ">"},  // ">" = только новые
            Count:    10,
            Block:    5 * time.Second,
        }).Result()
        if err != nil {
            if err == redis.Nil {
                continue // Нет новых сообщений
            }
            if errors.Is(err, context.Canceled) {
                return nil
            }
            log.Printf("XREADGROUP ошибка: %v", err)
            time.Sleep(time.Second)
            continue
        }

        for _, stream := range streams {
            for _, msg := range stream.Messages {
                // Обрабатываем сообщение
                if err := processEvent(ctx, msg); err != nil {
                    log.Printf("ошибка обработки %s: %v", msg.ID, err)
                    continue // Не подтверждаем — сообщение останется pending
                }

                // XACK — подтверждаем обработку
                rdb.XAck(ctx, stream.Stream, group, msg.ID)
            }
        }
    }
}
```

### Acknowledgment и Claiming

```go
// Обработка «застрявших» сообщений — если consumer упал,
// другой consumer может забрать его pending сообщения
func claimStaleMessages(ctx context.Context, rdb *redis.Client,
    stream, group, consumer string) error {

    // XPENDING — проверяем pending сообщения
    pending, err := rdb.XPendingExt(ctx, &redis.XPendingExtArgs{
        Stream: stream,
        Group:  group,
        Start:  "-",
        End:    "+",
        Count:  100,
    }).Result()
    if err != nil {
        return fmt.Errorf("XPENDING: %w", err)
    }

    var staleIDs []string
    for _, p := range pending {
        // Если сообщение не подтверждено более 5 минут — забираем
        if p.Idle > 5*time.Minute {
            staleIDs = append(staleIDs, p.ID)
            log.Printf("стагнирующее сообщение: ID=%s consumer=%s idle=%v retries=%d",
                p.ID, p.Consumer, p.Idle, p.RetryCount)
        }
    }

    if len(staleIDs) == 0 {
        return nil
    }

    // XCLAIM — забираем сообщения себе
    messages, err := rdb.XClaim(ctx, &redis.XClaimArgs{
        Stream:   stream,
        Group:    group,
        Consumer: consumer,
        MinIdle:  5 * time.Minute,
        Messages: staleIDs,
    }).Result()
    if err != nil {
        return fmt.Errorf("XCLAIM: %w", err)
    }

    for _, msg := range messages {
        if err := processEvent(ctx, msg); err != nil {
            log.Printf("ошибка обработки claimed %s: %v", msg.ID, err)
            continue
        }
        rdb.XAck(ctx, stream, group, msg.ID)
    }

    log.Printf("обработано %d стагнирующих сообщений", len(messages))
    return nil
}

// XAUTOCLAIM (Redis 6.2+) — автоматически забирает stale сообщения
func autoClaimMessages(ctx context.Context, rdb *redis.Client,
    stream, group, consumer string) error {

    messages, _, err := rdb.XAutoClaim(ctx, &redis.XAutoClaimArgs{
        Stream:   stream,
        Group:    group,
        Consumer: consumer,
        MinIdle:  5 * time.Minute,
        Start:    "0-0",
        Count:    50,
    }).Result()
    if err != nil {
        return fmt.Errorf("XAUTOCLAIM: %w", err)
    }

    for _, msg := range messages {
        if err := processEvent(ctx, msg); err != nil {
            log.Printf("ошибка: %v", err)
            continue
        }
        rdb.XAck(ctx, stream, group, msg.ID)
    }

    return nil
}
```

### Когда использовать Redis Streams

| Критерий | Redis Streams | Рекомендация |
|----------|--------------|--------------|
| Redis уже есть в инфраструктуре | ✅ | Отличный выбор — нет дополнительной зависимости |
| Нужна высокая пропускная способность (>100k msg/sec) | ❌ | Используйте Kafka |
| Нужна сложная маршрутизация | ❌ | Используйте RabbitMQ |
| Нужно долгосрочное хранение событий | ❌ | Используйте Kafka |
| Нужна простая очередь задач | ✅ | Redis Streams + consumer groups |
| Нужен lightweight event bus | ✅ | Подходит для небольших систем |

> 💡 **Совет**: Redis Streams — отличный выбор для MVP и небольших систем. Когда нагрузка вырастет, вы сможете мигрировать на Kafka или RabbitMQ, сохранив ту же семантику consumer groups.

---

## Сравнение технологий

### Сводная таблица

| Аспект | Kafka | RabbitMQ | NATS | Redis Streams |
|--------|-------|----------|------|---------------|
| **Модель** | Распределённый лог | Очередь сообщений | Subject-based messaging | Append-only stream |
| **Персистентность** | Да (диск, retention) | Да (опционально) | JetStream (да) | Да (AOF/RDB) |
| **Порядок** | По партиции | По очереди | По subject | По stream |
| **Consumer groups** | Да | Competing consumers | Queue groups / JetStream | Да (XREADGROUP) |
| **Пропускная способность** | Очень высокая (млн/сек) | Средняя (десятки тыс/сек) | Очень высокая | Средне-высокая |
| **Latency** | Средняя (батчинг) | Низкая | Очень низкая (< 1 мс) | Низкая |
| **Replay** | Да (offset) | Нет | JetStream (да) | Да (по ID) |
| **Маршрутизация** | Topic / partition | Exchanges (гибкая) | Subject hierarchy | Нет |
| **Протокол** | Custom TCP | AMQP 0.9.1 | Custom TCP | RESP (Redis) |
| **Сложность ops** | Высокая (ZooKeeper/KRaft) | Средняя | Низкая | Низкая (если Redis есть) |
| **Go библиотека** | segmentio/kafka-go | amqp091-go | nats.go | go-redis |
| **C# библиотека** | Confluent.Kafka | RabbitMQ.Client | NATS.Client | StackExchange.Redis |
| **MassTransit** | Да (Rider) | Да (основной транспорт) | Нет | Нет |

### Блок-схема выбора

```
Нужна ли постоянная запись событий (event log)?
├── Да → Kafka
│   └── Event sourcing, CQRS, stream processing, audit log
│
└── Нет → Нужна сложная маршрутизация?
    ├── Да → RabbitMQ
    │   └── Topic routing, priority queues, delayed messages, DLX
    │
    └── Нет → Нужна минимальная latency?
        ├── Да → NATS
        │   └── Микросервисы, request/reply, real-time
        │
        └── Нет → Redis уже в инфраструктуре?
            ├── Да → Redis Streams
            │   └── Простые очереди, event bus для небольших систем
            │
            └── Нет → RabbitMQ (универсальный выбор)
```

---

## Паттерны и Best Practices

### Идемпотентность (Exactly-Once Processing)

At-least-once delivery означает, что сообщение может быть обработано **повторно** (crash между обработкой и ack). Идемпотентность гарантирует, что повторная обработка не приведёт к дублированию данных.

> 💡 **Для C# разработчиков**: MassTransit предоставляет `InMemoryOutbox` и message deduplication. В Go вы реализуете идемпотентность самостоятельно — обычно через уникальный ключ в базе данных.

```go
// Идемпотентность через PostgreSQL — INSERT ... ON CONFLICT DO NOTHING
type IdempotencyChecker struct {
    db *pgxpool.Pool
}

func NewIdempotencyChecker(db *pgxpool.Pool) *IdempotencyChecker {
    return &IdempotencyChecker{db: db}
}

// Process — обрабатывает сообщение с гарантией идемпотентности
func (c *IdempotencyChecker) Process(ctx context.Context, messageID string,
    handler func(ctx context.Context) error) error {

    // Начинаем транзакцию
    tx, err := c.db.Begin(ctx)
    if err != nil {
        return fmt.Errorf("begin tx: %w", err)
    }
    defer tx.Rollback(ctx)

    // Пытаемся записать ID сообщения — если уже есть, пропускаем
    var inserted bool
    err = tx.QueryRow(ctx,
        `INSERT INTO processed_messages (message_id, processed_at)
         VALUES ($1, NOW())
         ON CONFLICT (message_id) DO NOTHING
         RETURNING true`,
        messageID,
    ).Scan(&inserted)

    if err != nil {
        if errors.Is(err, pgx.ErrNoRows) {
            // Сообщение уже обработано — пропускаем
            log.Printf("сообщение %s уже обработано, пропускаем", messageID)
            return nil
        }
        return fmt.Errorf("idempotency check: %w", err)
    }

    // Выполняем бизнес-логику в той же транзакции
    if err := handler(ctx); err != nil {
        return err // Rollback — ID удалится, можно retry
    }

    return tx.Commit(ctx)
}

// SQL для создания таблицы:
// CREATE TABLE processed_messages (
//     message_id TEXT PRIMARY KEY,
//     processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
// );
// CREATE INDEX idx_processed_messages_at ON processed_messages(processed_at);
// -- Очистка старых записей: DELETE FROM processed_messages WHERE processed_at < NOW() - INTERVAL '7 days';
```

### Graceful Shutdown

```go
// Универсальный паттерн graceful shutdown для consumer-сервисов
func runConsumer(ctx context.Context) error {
    // Перехватываем системные сигналы
    ctx, stop := signal.NotifyContext(ctx, syscall.SIGINT, syscall.SIGTERM)
    defer stop()

    reader := kafka.NewReader(kafka.ReaderConfig{
        Brokers: []string{"localhost:9092"},
        Topic:   "events",
        GroupID: "processor",
    })

    var wg sync.WaitGroup

    // Worker pool
    jobs := make(chan kafka.Message, 10)

    for i := 0; i < 5; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            for msg := range jobs {
                processMessage(ctx, msg)
                reader.CommitMessages(ctx, msg)
            }
        }(i)
    }

    // Читаем сообщения
    go func() {
        for {
            msg, err := reader.FetchMessage(ctx)
            if err != nil {
                if errors.Is(err, context.Canceled) {
                    return
                }
                log.Printf("fetch error: %v", err)
                continue
            }
            jobs <- msg
        }
    }()

    // Ждём сигнал завершения
    <-ctx.Done()
    log.Println("получен сигнал завершения, останавливаемся...")

    // 1. Прекращаем чтение новых сообщений
    close(jobs)

    // 2. Ждём завершения обработки текущих сообщений
    wg.Wait()

    // 3. Закрываем reader (освобождаем партиции)
    reader.Close()

    log.Println("graceful shutdown завершён")
    return nil
}
```

**Сравнение с C#**:

| Аспект | C# (.NET) | Go |
|--------|-----------|-----|
| **Сигнал** | `IHostApplicationLifetime`, `CancellationToken` | `signal.NotifyContext`, `context.Context` |
| **Lifecycle** | `BackgroundService.StopAsync()` | Ручная реализация |
| **In-flight** | MassTransit ждёт завершения consumers | `sync.WaitGroup` |
| **Timeout** | `HostOptions.ShutdownTimeout` (30s) | Ручной `context.WithTimeout` |

### Retry с Exponential Backoff

```go
// Универсальная функция retry с exponential backoff и jitter
func retryWithBackoff(ctx context.Context, maxRetries int,
    fn func(ctx context.Context) error) error {

    var lastErr error

    for attempt := 0; attempt <= maxRetries; attempt++ {
        err := fn(ctx)
        if err == nil {
            return nil
        }

        // Permanent error — не retry
        if isPermanent(err) {
            return err
        }

        lastErr = err

        if attempt < maxRetries {
            // Backoff: 100ms * 2^attempt, максимум 30 секунд
            base := float64(100*time.Millisecond) * math.Pow(2, float64(attempt))
            maxBackoff := float64(30 * time.Second)
            backoff := time.Duration(math.Min(base, maxBackoff))

            // Jitter: ±25%
            jitter := time.Duration(rand.Int63n(int64(backoff) / 2))
            backoff = backoff/2 + jitter

            select {
            case <-time.After(backoff):
            case <-ctx.Done():
                return ctx.Err()
            }
        }
    }

    return fmt.Errorf("исчерпано %d попыток: %w", maxRetries, lastErr)
}
```

### Dead Letter Queue

Общий паттерн DLQ, независимый от конкретного брокера:

```go
// DeadLetterSender — абстракция для отправки в DLQ
type DeadLetterSender interface {
    SendToDLQ(ctx context.Context, originalMsg []byte, err error, metadata map[string]string) error
}

// KafkaDLQ — реализация для Kafka
type KafkaDLQ struct {
    writer *kafka.Writer
}

func (d *KafkaDLQ) SendToDLQ(ctx context.Context, originalMsg []byte,
    processingErr error, metadata map[string]string) error {

    headers := []kafka.Header{
        {Key: "dlq-error", Value: []byte(processingErr.Error())},
        {Key: "dlq-timestamp", Value: []byte(time.Now().UTC().Format(time.RFC3339))},
    }
    for k, v := range metadata {
        headers = append(headers, kafka.Header{Key: k, Value: []byte(v)})
    }

    return d.writer.WriteMessages(ctx, kafka.Message{
        Value:   originalMsg,
        Headers: headers,
    })
}
```

### Сериализация сообщений

| Формат | Размер | Скорость | Schema | Человекочитаемый | Когда использовать |
|--------|--------|----------|--------|-----------------|-------------------|
| **JSON** | Большой | Средняя | Нет | Да | MVP, отладка, внешние API |
| **Protobuf** | Компактный | Высокая | Да (.proto) | Нет | Высокая нагрузка, микросервисы |
| **Avro** | Компактный | Высокая | Да (Schema Registry) | Нет | Kafka + schema evolution |
| **MessagePack** | Средний | Высокая | Нет | Нет | Компромисс JSON/binary |

```go
// JSON — просто и удобно
data, _ := json.Marshal(order)
writer.WriteMessages(ctx, kafka.Message{
    Value: data,
    Headers: []kafka.Header{
        {Key: "content-type", Value: []byte("application/json")},
    },
})

// Protobuf — компактно и быстро
// (требуется сгенерировать код из .proto файла)
data, _ := proto.Marshal(orderProto)
writer.WriteMessages(ctx, kafka.Message{
    Value: data,
    Headers: []kafka.Header{
        {Key: "content-type", Value: []byte("application/protobuf")},
        {Key: "proto-type", Value: []byte("orders.v1.OrderCreated")},
    },
})
```

> 💡 **Рекомендация**: Начинайте с JSON — проще отлаживать и нет зависимости от codegen. Переходите на Protobuf, когда размер сообщений или скорость сериализации становятся узким местом, или когда команда растёт и нужна строгая типизация через `.proto` файлы.

### Outbox Pattern

Проблема **dual write**: нужно записать в базу И отправить сообщение. Если crash происходит между двумя операциями, данные рассинхронизируются.

> 💡 **Для C# разработчиков**: MassTransit предоставляет `AddEntityFrameworkOutbox<TDbContext>()` — outbox встроен в EF Core транзакции. В Go этот паттерн реализуется вручную.

```go
// Outbox Pattern: записываем событие в ту же транзакцию, что и бизнес-данные

// SQL: CREATE TABLE outbox (
//     id BIGSERIAL PRIMARY KEY,
//     topic TEXT NOT NULL,
//     key TEXT,
//     payload BYTEA NOT NULL,
//     headers JSONB DEFAULT '{}',
//     created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
//     published_at TIMESTAMPTZ
// );
// CREATE INDEX idx_outbox_unpublished ON outbox(created_at) WHERE published_at IS NULL;

type OutboxWriter struct {
    db *pgxpool.Pool
}

// SaveWithEvent — сохраняем бизнес-данные и событие в одной транзакции
func (o *OutboxWriter) SaveWithEvent(ctx context.Context,
    businessFn func(tx pgx.Tx) error,
    topic, key string, payload []byte) error {

    tx, err := o.db.Begin(ctx)
    if err != nil {
        return fmt.Errorf("begin: %w", err)
    }
    defer tx.Rollback(ctx)

    // 1. Бизнес-логика
    if err := businessFn(tx); err != nil {
        return err
    }

    // 2. Записываем событие в outbox (та же транзакция!)
    _, err = tx.Exec(ctx,
        `INSERT INTO outbox (topic, key, payload) VALUES ($1, $2, $3)`,
        topic, key, payload,
    )
    if err != nil {
        return fmt.Errorf("outbox insert: %w", err)
    }

    return tx.Commit(ctx)
}

// OutboxRelay — горутина, которая читает из outbox и отправляет в брокер
type OutboxRelay struct {
    db     *pgxpool.Pool
    writer *kafka.Writer
}

func (r *OutboxRelay) Run(ctx context.Context) error {
    ticker := time.NewTicker(500 * time.Millisecond) // Polling каждые 500ms
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            return nil
        case <-ticker.C:
            if err := r.publishBatch(ctx); err != nil {
                log.Printf("outbox relay ошибка: %v", err)
            }
        }
    }
}

func (r *OutboxRelay) publishBatch(ctx context.Context) error {
    tx, err := r.db.Begin(ctx)
    if err != nil {
        return err
    }
    defer tx.Rollback(ctx)

    // Читаем неопубликованные события (с блокировкой FOR UPDATE SKIP LOCKED)
    rows, err := tx.Query(ctx,
        `SELECT id, topic, key, payload
         FROM outbox
         WHERE published_at IS NULL
         ORDER BY created_at
         LIMIT 100
         FOR UPDATE SKIP LOCKED`)
    if err != nil {
        return err
    }
    defer rows.Close()

    var ids []int64
    var messages []kafka.Message

    for rows.Next() {
        var id int64
        var topic, key string
        var payload []byte
        if err := rows.Scan(&id, &topic, &key, &payload); err != nil {
            return err
        }
        ids = append(ids, id)
        messages = append(messages, kafka.Message{
            Topic: topic,
            Key:   []byte(key),
            Value: payload,
        })
    }

    if len(messages) == 0 {
        return nil
    }

    // Публикуем в Kafka
    if err := r.writer.WriteMessages(ctx, messages...); err != nil {
        return fmt.Errorf("publish: %w", err)
    }

    // Помечаем как опубликованные
    _, err = tx.Exec(ctx,
        `UPDATE outbox SET published_at = NOW() WHERE id = ANY($1)`,
        ids,
    )
    if err != nil {
        return fmt.Errorf("update outbox: %w", err)
    }

    log.Printf("outbox: опубликовано %d событий", len(messages))
    return tx.Commit(ctx)
}
```

### Saga Pattern

Saga — паттерн управления распределёнными транзакциями через последовательность локальных транзакций с компенсирующими действиями.

> 💡 **Для C# разработчиков**: MassTransit предоставляет `MassTransitStateMachine<T>` (Automatonymous) — декларативное описание saga через состояния и события. В Go saga реализуется вручную — обычно через оркестратор или хореографию.

**Два подхода**:

| Подход | Описание | Когда использовать |
|--------|----------|-------------------|
| **Хореография** | Каждый сервис слушает события и реагирует | Простые саги (2-3 шага) |
| **Оркестрация** | Центральный координатор управляет шагами | Сложные саги (4+ шагов) |

```go
// Пример хореографии: Order → Payment → Notification
//
// order-service:  OrderCreated  → (Kafka) → payment-service
// payment-service: PaymentCompleted → (Kafka) → notification-service
// payment-service: PaymentFailed → (Kafka) → order-service (компенсация)

// Оркестрация — центральный координатор
type SagaStep struct {
    Name       string
    Execute    func(ctx context.Context, data any) error
    Compensate func(ctx context.Context, data any) error // Откат
}

type SagaOrchestrator struct {
    steps []SagaStep
}

func (s *SagaOrchestrator) Run(ctx context.Context, data any) error {
    var completedSteps []int

    for i, step := range s.steps {
        log.Printf("saga: выполняю шаг %d (%s)", i, step.Name)

        if err := step.Execute(ctx, data); err != nil {
            log.Printf("saga: шаг %d (%s) failed: %v", i, step.Name, err)

            // Компенсация — откатываем выполненные шаги в обратном порядке
            for j := len(completedSteps) - 1; j >= 0; j-- {
                stepIdx := completedSteps[j]
                compStep := s.steps[stepIdx]
                if compStep.Compensate != nil {
                    log.Printf("saga: компенсация шага %d (%s)", stepIdx, compStep.Name)
                    if compErr := compStep.Compensate(ctx, data); compErr != nil {
                        log.Printf("saga: ОШИБКА компенсации шага %d: %v", stepIdx, compErr)
                        // В production: записать в outbox для повторной компенсации
                    }
                }
            }

            return fmt.Errorf("saga failed на шаге %s: %w", step.Name, err)
        }

        completedSteps = append(completedSteps, i)
    }

    log.Println("saga: все шаги выполнены успешно")
    return nil
}
```

> Детальная реализация saga с persistence и recovery будет рассмотрена в [Части 5: Практические проекты](../part5-projects/) на примере E-commerce платформы.

---

## Production Concerns

### Мониторинг с Prometheus

```go
import "github.com/prometheus/client_golang/prometheus"

var (
    messagesProcessed = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "messages_processed_total",
            Help: "Количество обработанных сообщений",
        },
        []string{"topic", "status"}, // status: success, error, dlq
    )

    messageProcessingDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "message_processing_duration_seconds",
            Help:    "Время обработки сообщения",
            Buckets: prometheus.DefBuckets,
        },
        []string{"topic"},
    )

    consumerLag = prometheus.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "consumer_lag",
            Help: "Отставание consumer от последнего сообщения",
        },
        []string{"topic", "partition"},
    )

    dlqMessages = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "dlq_messages_total",
            Help: "Количество сообщений, отправленных в DLQ",
        },
        []string{"topic", "error_type"},
    )
)

func init() {
    prometheus.MustRegister(messagesProcessed, messageProcessingDuration, consumerLag, dlqMessages)
}

// Инструментированный consumer
func processWithMetrics(ctx context.Context, topic string, msg []byte,
    handler func(context.Context, []byte) error) error {

    start := time.Now()

    err := handler(ctx, msg)

    duration := time.Since(start).Seconds()
    messageProcessingDuration.WithLabelValues(topic).Observe(duration)

    if err != nil {
        messagesProcessed.WithLabelValues(topic, "error").Inc()
        return err
    }

    messagesProcessed.WithLabelValues(topic, "success").Inc()
    return nil
}
```

#### Kafka Consumer Lag

```go
// Мониторинг consumer lag — критичная метрика для Kafka
func monitorConsumerLag(ctx context.Context, brokers []string, topic, groupID string) {
    conn, err := kafka.Dial("tcp", brokers[0])
    if err != nil {
        log.Printf("ошибка подключения для мониторинга: %v", err)
        return
    }
    defer conn.Close()

    ticker := time.NewTicker(30 * time.Second)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            return
        case <-ticker.C:
            partitions, err := conn.ReadPartitions(topic)
            if err != nil {
                log.Printf("ошибка чтения партиций: %v", err)
                continue
            }

            for _, p := range partitions {
                // Получаем last offset партиции
                pConn, err := kafka.DialLeader(ctx, "tcp", brokers[0], topic, p.ID)
                if err != nil {
                    continue
                }
                lastOffset, _ := pConn.ReadLastOffset()
                pConn.Close()

                // Consumer lag = last offset - committed offset
                // (committed offset можно получить через admin API)
                consumerLag.WithLabelValues(topic, fmt.Sprintf("%d", p.ID)).Set(
                    float64(lastOffset), // Упрощённо, в production нужен committed offset
                )
            }
        }
    }
}
```

### OpenTelemetry Instrumentation

```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/propagation"
    "go.opentelemetry.io/otel/trace"
)

var tracer = otel.Tracer("message-queue")

// Producer — инжектируем trace context в headers сообщения
func publishWithTracing(ctx context.Context, w *kafka.Writer, topic string, payload []byte) error {
    ctx, span := tracer.Start(ctx, "kafka.publish",
        trace.WithAttributes(
            attribute.String("messaging.system", "kafka"),
            attribute.String("messaging.destination", topic),
            attribute.String("messaging.operation", "publish"),
        ),
    )
    defer span.End()

    // Инжектируем trace context в Kafka headers
    headers := make([]kafka.Header, 0)
    carrier := &KafkaHeaderCarrier{headers: &headers}
    otel.GetTextMapPropagator().Inject(ctx, carrier)

    return w.WriteMessages(ctx, kafka.Message{
        Value:   payload,
        Headers: headers,
    })
}

// Consumer — извлекаем trace context из headers
func consumeWithTracing(ctx context.Context, msg kafka.Message,
    handler func(context.Context, kafka.Message) error) error {

    // Извлекаем trace context из Kafka headers
    carrier := &KafkaHeaderCarrier{headers: &msg.Headers}
    ctx = otel.GetTextMapPropagator().Extract(ctx, carrier)

    ctx, span := tracer.Start(ctx, "kafka.consume",
        trace.WithAttributes(
            attribute.String("messaging.system", "kafka"),
            attribute.String("messaging.destination", msg.Topic),
            attribute.String("messaging.operation", "receive"),
            attribute.Int64("messaging.kafka.partition", int64(msg.Partition)),
            attribute.Int64("messaging.kafka.offset", msg.Offset),
        ),
    )
    defer span.End()

    err := handler(ctx, msg)
    if err != nil {
        span.RecordError(err)
    }
    return err
}

// KafkaHeaderCarrier — адаптер для OTel propagation
type KafkaHeaderCarrier struct {
    headers *[]kafka.Header
}

func (c *KafkaHeaderCarrier) Get(key string) string {
    for _, h := range *c.headers {
        if h.Key == key {
            return string(h.Value)
        }
    }
    return ""
}

func (c *KafkaHeaderCarrier) Set(key, value string) {
    *c.headers = append(*c.headers, kafka.Header{
        Key:   key,
        Value: []byte(value),
    })
}

func (c *KafkaHeaderCarrier) Keys() []string {
    keys := make([]string, len(*c.headers))
    for i, h := range *c.headers {
        keys[i] = h.Key
    }
    return keys
}
```

> 💡 **Для C# разработчиков**: В MassTransit tracing включается одной строкой: `cfg.UseOpenTelemetry()`. В Go вы вручную инжектируете и извлекаете trace context через headers. Результат тот же — связанные spans от producer к consumer в Jaeger/Tempo.

### Health Checks

```go
// Health check для message queue consumers
type MQHealthChecker struct {
    kafkaReader  *kafka.Reader
    rabbitClient *RabbitMQClient
    natsConn     *nats.Conn
    redisClient  *redis.Client
}

func (h *MQHealthChecker) CheckKafka(ctx context.Context) error {
    // Проверяем, что reader подключён и читает
    stats := h.kafkaReader.Stats()
    if stats.Dials > 0 && stats.Errors > stats.Dials/2 {
        return fmt.Errorf("kafka: высокий уровень ошибок (%d/%d)", stats.Errors, stats.Dials)
    }
    return nil
}

func (h *MQHealthChecker) CheckRabbitMQ(ctx context.Context) error {
    ch := h.rabbitClient.Channel()
    if ch == nil || ch.IsClosed() {
        return fmt.Errorf("rabbitmq: канал закрыт")
    }
    return nil
}

func (h *MQHealthChecker) CheckNATS(ctx context.Context) error {
    if !h.natsConn.IsConnected() {
        return fmt.Errorf("nats: не подключён (status=%v)", h.natsConn.Status())
    }
    return nil
}

func (h *MQHealthChecker) CheckRedisStreams(ctx context.Context) error {
    return h.redisClient.Ping(ctx).Err()
}
```

---

## Практические примеры

### Пример 1: Event-Driven Order Processing (Kafka)

**Задача**: Сервис заказов публикует событие `OrderCreated` в Kafka. Сервис платежей потребляет событие, обрабатывает оплату и публикует `PaymentCompleted`. Реализуем идемпотентность и DLT.

**C# с MassTransit**:
```csharp
// В C# — всё декларативно:
public class OrderCreatedConsumer : IConsumer<OrderCreated>
{
    public async Task Consume(ConsumeContext<OrderCreated> context)
    {
        await _paymentService.ProcessPayment(context.Message.OrderId);
        await context.Publish(new PaymentCompleted(context.Message.OrderId));
    }
}
// MassTransit автоматически: десериализация, retry, DLQ, tracing
```

**Go — полная реализация**:

```go
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "log"
    "os/signal"
    "sync"
    "syscall"
    "time"

    "github.com/jackc/pgx/v5/pgxpool"
    "github.com/segmentio/kafka-go"
)

// --- Модели ---

type OrderCreated struct {
    OrderID    string  `json:"order_id"`
    CustomerID string  `json:"customer_id"`
    Total      float64 `json:"total"`
    Currency   string  `json:"currency"`
    CreatedAt  string  `json:"created_at"`
}

type PaymentCompleted struct {
    OrderID       string  `json:"order_id"`
    TransactionID string  `json:"transaction_id"`
    Amount        float64 `json:"amount"`
    ProcessedAt   string  `json:"processed_at"`
}

// --- Payment Processor ---

type PaymentProcessor struct {
    reader      *kafka.Reader
    writer      *kafka.Writer    // Для публикации PaymentCompleted
    dlqWriter   *kafka.Writer    // Dead Letter Topic
    db          *pgxpool.Pool
    idempotency *IdempotencyChecker
}

func NewPaymentProcessor(brokers []string, db *pgxpool.Pool) *PaymentProcessor {
    return &PaymentProcessor{
        reader: kafka.NewReader(kafka.ReaderConfig{
            Brokers:  brokers,
            Topic:    "orders.created",
            GroupID:  "payment-processor",
            MaxBytes: 10e6,
        }),
        writer: &kafka.Writer{
            Addr:         kafka.TCP(brokers...),
            Topic:        "payments.completed",
            Balancer:     &kafka.Hash{},
            RequiredAcks: kafka.RequireAll,
        },
        dlqWriter: &kafka.Writer{
            Addr:  kafka.TCP(brokers...),
            Topic: "orders.created.dlq",
        },
        db:          db,
        idempotency: NewIdempotencyChecker(db),
    }
}

func (p *PaymentProcessor) Run(ctx context.Context) error {
    defer p.reader.Close()
    defer p.writer.Close()
    defer p.dlqWriter.Close()

    log.Println("payment processor запущен")

    for {
        msg, err := p.reader.FetchMessage(ctx)
        if err != nil {
            if ctx.Err() != nil {
                return nil
            }
            log.Printf("fetch ошибка: %v", err)
            continue
        }

        if err := p.handleMessage(ctx, msg); err != nil {
            log.Printf("обработка сообщения failed (offset=%d): %v", msg.Offset, err)
        }

        // Коммитим offset независимо от результата
        // (ошибки ушли в DLQ или будут обработаны при retry)
        if err := p.reader.CommitMessages(ctx, msg); err != nil {
            log.Printf("commit ошибка: %v", err)
        }
    }
}

func (p *PaymentProcessor) handleMessage(ctx context.Context, msg kafka.Message) error {
    var event OrderCreated
    if err := json.Unmarshal(msg.Value, &event); err != nil {
        // Невалидный JSON — permanent error, сразу в DLQ
        return p.sendToDLQ(ctx, msg, fmt.Errorf("невалидный JSON: %w", err))
    }

    // Идемпотентная обработка
    messageID := getMessageID(msg)
    err := p.idempotency.Process(ctx, messageID, func(ctx context.Context) error {
        return p.processPayment(ctx, event)
    })

    if err != nil {
        // Retry с backoff
        retryErr := retryWithBackoff(ctx, 3, func(ctx context.Context) error {
            return p.idempotency.Process(ctx, messageID, func(ctx context.Context) error {
                return p.processPayment(ctx, event)
            })
        })

        if retryErr != nil {
            return p.sendToDLQ(ctx, msg, retryErr)
        }
    }

    return nil
}

func (p *PaymentProcessor) processPayment(ctx context.Context, event OrderCreated) error {
    // Бизнес-логика обработки платежа
    log.Printf("обработка платежа для заказа %s: %.2f %s",
        event.OrderID, event.Total, event.Currency)

    // Публикуем событие PaymentCompleted
    completed := PaymentCompleted{
        OrderID:       event.OrderID,
        TransactionID: fmt.Sprintf("txn_%s_%d", event.OrderID, time.Now().UnixNano()),
        Amount:        event.Total,
        ProcessedAt:   time.Now().UTC().Format(time.RFC3339),
    }

    data, err := json.Marshal(completed)
    if err != nil {
        return fmt.Errorf("сериализация PaymentCompleted: %w", err)
    }

    return p.writer.WriteMessages(ctx, kafka.Message{
        Key:   []byte(event.OrderID),
        Value: data,
    })
}

func (p *PaymentProcessor) sendToDLQ(ctx context.Context, msg kafka.Message, processingErr error) error {
    log.Printf("отправка в DLQ (offset=%d): %v", msg.Offset, processingErr)

    headers := append(msg.Headers,
        kafka.Header{Key: "dlq-error", Value: []byte(processingErr.Error())},
        kafka.Header{Key: "dlq-timestamp", Value: []byte(time.Now().UTC().Format(time.RFC3339))},
    )

    return p.dlqWriter.WriteMessages(ctx, kafka.Message{
        Key:     msg.Key,
        Value:   msg.Value,
        Headers: headers,
    })
}

func getMessageID(msg kafka.Message) string {
    for _, h := range msg.Headers {
        if h.Key == "message-id" {
            return string(h.Value)
        }
    }
    return fmt.Sprintf("%s-%d-%d", msg.Topic, msg.Partition, msg.Offset)
}

func main() {
    ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
    defer stop()

    db, _ := pgxpool.New(ctx, "postgres://localhost:5432/payments")
    defer db.Close()

    processor := NewPaymentProcessor([]string{"localhost:9092"}, db)

    if err := processor.Run(ctx); err != nil {
        log.Fatal(err)
    }
}
```

---

### Пример 2: Task Queue с RabbitMQ

**Задача**: Фоновая обработка задач (отправка email, генерация отчётов). Worker pool с prefetch, publisher confirms и автоматическим переподключением.

```go
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "log"
    "os/signal"
    "sync"
    "syscall"
    "time"

    amqp "github.com/rabbitmq/amqp091-go"
)

// --- Модели ---

type Task struct {
    ID      string          `json:"id"`
    Type    string          `json:"type"`    // "send_email", "generate_report"
    Payload json.RawMessage `json:"payload"`
}

type EmailPayload struct {
    To      string `json:"to"`
    Subject string `json:"subject"`
    Body    string `json:"body"`
}

// --- Task Publisher ---

type TaskPublisher struct {
    client *RabbitMQClient // Обёртка с reconnection из раздела выше
}

func (p *TaskPublisher) PublishTask(ctx context.Context, task Task) error {
    body, err := json.Marshal(task)
    if err != nil {
        return fmt.Errorf("сериализация: %w", err)
    }

    return p.client.Publish(ctx, "tasks", task.Type, amqp.Publishing{
        ContentType:  "application/json",
        DeliveryMode: amqp.Persistent,
        MessageId:    task.ID,
        Timestamp:    time.Now(),
        Body:         body,
    })
}

// --- Task Worker ---

type TaskWorker struct {
    url       string
    queueName string
    workers   int
    handlers  map[string]func(context.Context, json.RawMessage) error
}

func NewTaskWorker(url, queueName string, workers int) *TaskWorker {
    return &TaskWorker{
        url:       url,
        queueName: queueName,
        workers:   workers,
        handlers:  make(map[string]func(context.Context, json.RawMessage) error),
    }
}

func (w *TaskWorker) RegisterHandler(taskType string, handler func(context.Context, json.RawMessage) error) {
    w.handlers[taskType] = handler
}

func (w *TaskWorker) Run(ctx context.Context) error {
    for {
        err := w.runOnce(ctx)
        if ctx.Err() != nil {
            return nil // Штатное завершение
        }

        // Переподключение при ошибке
        log.Printf("worker ошибка: %v, переподключение...", err)
        select {
        case <-time.After(5 * time.Second):
        case <-ctx.Done():
            return nil
        }
    }
}

func (w *TaskWorker) runOnce(ctx context.Context) error {
    conn, err := amqp.Dial(w.url)
    if err != nil {
        return fmt.Errorf("dial: %w", err)
    }
    defer conn.Close()

    ch, err := conn.Channel()
    if err != nil {
        return fmt.Errorf("channel: %w", err)
    }
    defer ch.Close()

    // Настраиваем топологию
    if err := w.setupTopology(ch); err != nil {
        return err
    }

    // Prefetch = 2 * workers
    if err := ch.Qos(w.workers*2, 0, false); err != nil {
        return fmt.Errorf("qos: %w", err)
    }

    deliveries, err := ch.Consume(w.queueName, "", false, false, false, false, nil)
    if err != nil {
        return fmt.Errorf("consume: %w", err)
    }

    // Следим за закрытием соединения
    connClose := conn.NotifyClose(make(chan *amqp.Error, 1))

    var wg sync.WaitGroup

    for i := 0; i < w.workers; i++ {
        wg.Add(1)
        go func(workerID int) {
            defer wg.Done()
            for {
                select {
                case d, ok := <-deliveries:
                    if !ok {
                        return
                    }
                    w.processDelivery(ctx, workerID, ch, d)

                case <-ctx.Done():
                    return
                }
            }
        }(i)
    }

    // Ждём закрытия соединения или контекста
    select {
    case amqpErr := <-connClose:
        return fmt.Errorf("соединение закрыто: %v", amqpErr)
    case <-ctx.Done():
        wg.Wait()
        return nil
    }
}

func (w *TaskWorker) setupTopology(ch *amqp.Channel) error {
    // Exchange для задач
    if err := ch.ExchangeDeclare("tasks", "direct", true, false, false, false, nil); err != nil {
        return err
    }

    // DLX
    if err := ch.ExchangeDeclare("tasks.dlx", "direct", true, false, false, false, nil); err != nil {
        return err
    }

    // Основная очередь с DLX
    _, err := ch.QueueDeclare(w.queueName, true, false, false, false, amqp.Table{
        "x-dead-letter-exchange":    "tasks.dlx",
        "x-dead-letter-routing-key": "dead",
    })
    if err != nil {
        return err
    }

    // Привязываем все типы задач
    for taskType := range w.handlers {
        if err := ch.QueueBind(w.queueName, taskType, "tasks", false, nil); err != nil {
            return err
        }
    }

    // DLQ
    ch.QueueDeclare("tasks.dlq", true, false, false, false, nil)
    ch.QueueBind("tasks.dlq", "dead", "tasks.dlx", false, nil)

    return nil
}

func (w *TaskWorker) processDelivery(ctx context.Context, workerID int, ch *amqp.Channel, d amqp.Delivery) {
    var task Task
    if err := json.Unmarshal(d.Body, &task); err != nil {
        log.Printf("[worker %d] невалидная задача: %v", workerID, err)
        d.Reject(false) // В DLX
        return
    }

    handler, ok := w.handlers[task.Type]
    if !ok {
        log.Printf("[worker %d] неизвестный тип задачи: %s", workerID, task.Type)
        d.Reject(false) // В DLX
        return
    }

    log.Printf("[worker %d] обработка задачи %s (тип: %s)", workerID, task.ID, task.Type)

    if err := handler(ctx, task.Payload); err != nil {
        // Проверяем количество попыток через x-death header
        retryCount := getRetryCount(d)
        if retryCount >= 3 {
            log.Printf("[worker %d] задача %s: исчерпаны попытки (%d), в DLQ", workerID, task.ID, retryCount)
            d.Reject(false) // В DLX → DLQ
        } else {
            log.Printf("[worker %d] задача %s: ошибка (попытка %d): %v", workerID, task.ID, retryCount+1, err)
            d.Nack(false, true) // Requeue для повтора
        }
        return
    }

    d.Ack(false)
    log.Printf("[worker %d] задача %s обработана успешно", workerID, task.ID)
}

func getRetryCount(d amqp.Delivery) int {
    if d.Headers == nil {
        return 0
    }
    deaths, ok := d.Headers["x-death"].([]interface{})
    if !ok || len(deaths) == 0 {
        return 0
    }
    death, ok := deaths[0].(amqp.Table)
    if !ok {
        return 0
    }
    count, ok := death["count"].(int64)
    if !ok {
        return 0
    }
    return int(count)
}

func main() {
    ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
    defer stop()

    worker := NewTaskWorker("amqp://guest:guest@localhost:5672/", "task-queue", 5)

    // Регистрируем обработчики
    worker.RegisterHandler("send_email", func(ctx context.Context, payload json.RawMessage) error {
        var email EmailPayload
        if err := json.Unmarshal(payload, &email); err != nil {
            return err
        }
        log.Printf("отправка email: to=%s subject=%s", email.To, email.Subject)
        // Здесь реальная отправка через SMTP
        return nil
    })

    worker.RegisterHandler("generate_report", func(ctx context.Context, payload json.RawMessage) error {
        log.Println("генерация отчёта...")
        time.Sleep(2 * time.Second) // Имитация тяжёлой работы
        return nil
    })

    log.Println("task worker запущен (5 воркеров)")
    if err := worker.Run(ctx); err != nil {
        log.Fatal(err)
    }
}
```

---

### Пример 3: Real-Time Notifications (NATS)

**Задача**: Сервис уведомлений получает события через NATS и пересылает подключённым клиентам через WebSocket. JetStream гарантирует, что уведомления не теряются.

```go
package main

import (
    "context"
    "encoding/json"
    "log"
    "net/http"
    "os/signal"
    "sync"
    "syscall"
    "time"

    "github.com/gorilla/websocket"
    "github.com/nats-io/nats.go"
    "github.com/nats-io/nats.go/jetstream"
)

// --- Модели ---

type Notification struct {
    ID        string `json:"id"`
    UserID    string `json:"user_id"`
    Type      string `json:"type"`    // "order_update", "payment", "system"
    Title     string `json:"title"`
    Message   string `json:"message"`
    CreatedAt string `json:"created_at"`
}

// --- WebSocket Hub ---

type Hub struct {
    mu      sync.RWMutex
    clients map[string]map[*websocket.Conn]struct{} // userID → connections
}

func NewHub() *Hub {
    return &Hub{
        clients: make(map[string]map[*websocket.Conn]struct{}),
    }
}

func (h *Hub) Register(userID string, conn *websocket.Conn) {
    h.mu.Lock()
    defer h.mu.Unlock()
    if h.clients[userID] == nil {
        h.clients[userID] = make(map[*websocket.Conn]struct{})
    }
    h.clients[userID][conn] = struct{}{}
    log.Printf("WebSocket подключён: user=%s (всего: %d)", userID, len(h.clients[userID]))
}

func (h *Hub) Unregister(userID string, conn *websocket.Conn) {
    h.mu.Lock()
    defer h.mu.Unlock()
    if conns, ok := h.clients[userID]; ok {
        delete(conns, conn)
        if len(conns) == 0 {
            delete(h.clients, userID)
        }
    }
    conn.Close()
}

func (h *Hub) SendToUser(userID string, data []byte) {
    h.mu.RLock()
    defer h.mu.RUnlock()

    conns, ok := h.clients[userID]
    if !ok {
        return
    }

    for conn := range conns {
        if err := conn.WriteMessage(websocket.TextMessage, data); err != nil {
            log.Printf("ошибка отправки WebSocket: %v", err)
            go h.Unregister(userID, conn)
        }
    }
}

// --- NATS Consumer ---

type NotificationConsumer struct {
    js  jetstream.JetStream
    hub *Hub
}

func NewNotificationConsumer(nc *nats.Conn, hub *Hub) (*NotificationConsumer, error) {
    js, err := jetstream.New(nc)
    if err != nil {
        return nil, err
    }

    return &NotificationConsumer{js: js, hub: hub}, nil
}

func (c *NotificationConsumer) Setup(ctx context.Context) error {
    // Создаём stream для уведомлений
    _, err := c.js.CreateOrUpdateStream(ctx, jetstream.StreamConfig{
        Name:      "NOTIFICATIONS",
        Subjects:  []string{"notifications.>"},
        Storage:   jetstream.FileStorage,
        Retention: jetstream.InterestPolicy, // Удалять после доставки всем consumers
        MaxAge:    24 * time.Hour,
    })
    return err
}

func (c *NotificationConsumer) Run(ctx context.Context) error {
    // Durable consumer — не потеряет сообщения при рестарте
    consumer, err := c.js.CreateOrUpdateConsumer(ctx, "NOTIFICATIONS", jetstream.ConsumerConfig{
        Name:          "ws-gateway",
        Durable:       "ws-gateway",
        DeliverPolicy: jetstream.DeliverNewPolicy,
        AckPolicy:     jetstream.AckExplicitPolicy,
        AckWait:       10 * time.Second,
        MaxDeliver:    3,
    })
    if err != nil {
        return err
    }

    iter, err := consumer.Messages()
    if err != nil {
        return err
    }
    defer iter.Stop()

    for {
        msg, err := iter.Next()
        if err != nil {
            if ctx.Err() != nil {
                return nil
            }
            log.Printf("next ошибка: %v", err)
            continue
        }

        var notif Notification
        if err := json.Unmarshal(msg.Data(), &notif); err != nil {
            log.Printf("невалидное уведомление: %v", err)
            msg.Term() // Не retry — данные невалидны
            continue
        }

        // Отправляем в WebSocket
        c.hub.SendToUser(notif.UserID, msg.Data())
        msg.Ack()

        log.Printf("уведомление доставлено: user=%s type=%s", notif.UserID, notif.Type)
    }
}

// --- HTTP/WebSocket Server ---

var upgrader = websocket.Upgrader{
    CheckOrigin: func(r *http.Request) bool { return true }, // В production: проверяйте origin
}

func wsHandler(hub *Hub) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        userID := r.URL.Query().Get("user_id")
        if userID == "" {
            http.Error(w, "user_id обязателен", http.StatusBadRequest)
            return
        }

        conn, err := upgrader.Upgrade(w, r, nil)
        if err != nil {
            log.Printf("WebSocket upgrade ошибка: %v", err)
            return
        }

        hub.Register(userID, conn)
        defer hub.Unregister(userID, conn)

        // Читаем сообщения от клиента (ping/pong, close)
        for {
            _, _, err := conn.ReadMessage()
            if err != nil {
                break
            }
        }
    }
}

// --- Публикация уведомлений (из других сервисов) ---

func publishNotification(js jetstream.JetStream, notif Notification) error {
    data, err := json.Marshal(notif)
    if err != nil {
        return err
    }

    _, err = js.Publish(context.Background(),
        "notifications."+notif.UserID, // Subject = notifications.<user_id>
        data,
        jetstream.WithMsgID(notif.ID), // Дедупликация
    )
    return err
}

func main() {
    ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
    defer stop()

    // Подключаемся к NATS
    nc, err := nats.Connect("nats://localhost:4222",
        nats.ReconnectWait(2*time.Second),
        nats.MaxReconnects(-1), // Бесконечные попытки
    )
    if err != nil {
        log.Fatal(err)
    }
    defer nc.Close()

    hub := NewHub()

    consumer, err := NewNotificationConsumer(nc, hub)
    if err != nil {
        log.Fatal(err)
    }

    if err := consumer.Setup(ctx); err != nil {
        log.Fatal(err)
    }

    // Запускаем NATS consumer в горутине
    go func() {
        if err := consumer.Run(ctx); err != nil {
            log.Printf("consumer ошибка: %v", err)
        }
    }()

    // HTTP сервер
    mux := http.NewServeMux()
    mux.HandleFunc("/ws", wsHandler(hub))

    server := &http.Server{Addr: ":8080", Handler: mux}

    go func() {
        log.Println("WebSocket сервер запущен на :8080")
        if err := server.ListenAndServe(); err != http.ErrServerClosed {
            log.Fatal(err)
        }
    }()

    <-ctx.Done()
    server.Shutdown(context.Background())
    log.Println("сервер остановлен")
}
```

> 💡 **Для C# разработчиков**: Этот пример — аналог SignalR с backplane на Azure Service Bus. В C# вы бы использовали `IHubContext<NotificationHub>` для отправки сообщений клиентам. В Go — gorilla/websocket (или nhooyr.io/websocket) + NATS JetStream.

---

<!-- AUTO: NAV -->
**Вопросы?** Открой issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Назад: Кэширование](./02_caching.md) | [Вперёд: gRPC →](./04_grpc.md)
<!-- /AUTO: NAV -->
