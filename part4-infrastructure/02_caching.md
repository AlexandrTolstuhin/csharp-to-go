# 4.2 Кэширование

## Содержание

- [Введение](#введение)
- [Redis в Go: go-redis](#redis-в-go-go-redis)
  - [Установка и подключение](#установка-и-подключение)
  - [Конфигурация для Production](#конфигурация-для-production)
  - [Основные операции](#основные-операции)
  - [Pipelining и транзакции](#pipelining-и-транзакции)
  - [Pub/Sub](#pubsub)
  - [Распределённые блокировки (Redlock)](#распределённые-блокировки-redlock)
- [In-Memory кэширование](#in-memory-кэширование)
  - [sync.Map: когда использовать](#syncmap-когда-использовать)
  - [map + RWMutex: простейший кэш](#map--rwmutex-простейший-кэш)
  - [patrickmn/go-cache: простой TTL кэш](#patrickmngo-cache-простой-ttl-кэш)
  - [dgraph-io/ristretto: высокопроизводительный кэш](#dgraph-ioristretto-высокопроизводительный-кэш)
  - [allegro/bigcache: GC-friendly кэш](#allegrobigcache-gc-friendly-кэш)
  - [Сравнительная таблица](#сравнительная-таблица-in-memory-библиотек)
- [Абстракция над кэшами: eko/gocache](#абстракция-над-кэшами-ekogocache)
- [Паттерны кэширования](#паттерны-кэширования)
  - [Cache-Aside (Lazy Loading)](#cache-aside-lazy-loading)
  - [Write-Through](#write-through)
  - [Write-Behind (Write-Back)](#write-behind-write-back)
  - [Read-Through](#read-through)
  - [Cache Stampede Prevention (singleflight)](#cache-stampede-prevention-singleflight)
  - [Стратегии TTL](#стратегии-ttl)
  - [Инвалидация кэша](#инвалидация-кэша)
- [Multi-Level кэширование (L1 + L2)](#multi-level-кэширование-l1--l2)
  - [Архитектура](#архитектура)
  - [Реализация](#реализация)
  - [Инвалидация между инстансами](#инвалидация-между-инстансами)
- [Production Concerns](#production-concerns)
  - [Прогрев кэша (Cache Warming)](#прогрев-кэша-cache-warming)
  - [Мониторинг](#мониторинг)
  - [Сериализация](#сериализация)
  - [Connection Pooling и Resilience](#connection-pooling-и-resilience)
  - [Память и GC](#память-и-gc)
  - [OpenTelemetry Instrumentation](#opentelemetry-instrumentation)
- [Практические примеры](#практические-примеры)
  - [Пример 1: Production-Ready Redis Cache Layer](#пример-1-production-ready-redis-cache-layer)
  - [Пример 2: Multi-Level Cache с singleflight](#пример-2-multi-level-cache-с-singleflight)
  - [Пример 3: Session Storage с Redis](#пример-3-session-storage-с-redis)
- [Чек-лист](#чек-лист)

---

## Введение

В [разделе 3.3](../part3-web-api/03_database.md) мы настроили работу с PostgreSQL, а в [разделе 4.1](./01_production_postgresql.md) довели её до production-уровня. Но даже идеально оптимизированная база данных не спасёт от проблем под высокой нагрузкой — именно здесь на помощь приходит **кэширование**.

> 💡 **Для C# разработчиков**: В ASP.NET Core вы привыкли к `IMemoryCache`, `IDistributedCache`, `StackExchange.Redis`, а также к готовым абстракциям вроде `LazyCache` и `FusionCache`. В Go единого интерфейса кэширования нет — вместо этого вы комбинируете конкретные библиотеки и паттерны. Это требует больше ручной работы, но даёт полный контроль над производительностью и поведением.

### Экосистема кэширования: C# vs Go

| Концепция | C# (.NET) | Go |
|-----------|-----------|-----|
| **Единый API** | `IDistributedCache` | Нет стандартного интерфейса |
| **In-memory** | `IMemoryCache` | `map` + `sync.RWMutex` / go-cache / ristretto |
| **Distributed** | `StackExchange.Redis` | go-redis |
| **Multi-level** | `FusionCache` / `HybridCache` | Ручная композиция (или eko/gocache) |
| **Абстракция** | `LazyCache` | eko/gocache |
| **Stampede protection** | Встроено в `LazyCache` | `singleflight` (ручная интеграция) |
| **GC-friendly** | Не актуально (CLR GC иначе работает) | bigcache, freecache (критично для Go GC) |
| **Output caching** | `[OutputCache]` middleware | Нет аналога, реализуется вручную |

### Ключевое отличие от C#

В .NET вы обычно:
1. Регистрируете `IDistributedCache` в DI
2. Инжектите интерфейс в сервис
3. Используете `GetAsync` / `SetAsync`
4. Фреймворк сам управляет сериализацией и подключением

В Go вы:
1. Создаёте клиент конкретной библиотеки (go-redis, ristretto и т.д.)
2. Передаёте его через конструктор (composition)
3. Вызываете типизированные методы напрямую
4. Сами управляете сериализацией, TTL и обработкой ошибок

Это больше кода, но меньше "магии" — вы точно знаете, что происходит на каждом шаге.

### Что вы узнаете

- Работа с Redis через go-redis v9: подключение, операции, pipelining, Pub/Sub, блокировки
- In-memory кэширование: go-cache, ristretto, bigcache — и когда какой выбрать
- Паттерны: Cache-Aside, Write-Through, Read-Through, stampede prevention
- Multi-level кэширование (L1 in-memory + L2 Redis)
- Production: мониторинг, сериализация, GC impact, resilience

---

## Redis в Go: go-redis

[go-redis](https://github.com/redis/go-redis) — основная библиотека для работы с Redis в Go. Это аналог `StackExchange.Redis` из мира .NET, но с важными отличиями в API и подходе к подключениям.

### Установка и подключение

```bash
go get github.com/redis/go-redis/v9
```

**C# — StackExchange.Redis**:
```csharp
// C#: ConnectionMultiplexer — синглтон, потокобезопасный
var redis = ConnectionMultiplexer.Connect("localhost:6379");
IDatabase db = redis.GetDatabase();

// Операции — синхронные или async
string? value = await db.StringGetAsync("key");
await db.StringSetAsync("key", "value", TimeSpan.FromMinutes(5));
```

**Go — go-redis**:
```go
package main

import (
    "context"
    "fmt"
    "time"

    "github.com/redis/go-redis/v9"
)

func main() {
    // go-redis клиент — потокобезопасный, используйте один на приложение
    rdb := redis.NewClient(&redis.Options{
        Addr:     "localhost:6379",
        Password: "",  // без пароля
        DB:       0,   // default DB
    })
    defer rdb.Close()

    ctx := context.Background()

    // Проверка подключения
    if err := rdb.Ping(ctx).Err(); err != nil {
        panic(fmt.Sprintf("не удалось подключиться к Redis: %v", err))
    }

    // Базовые операции — всегда с context
    err := rdb.Set(ctx, "key", "value", 5*time.Minute).Err()
    if err != nil {
        panic(err)
    }

    val, err := rdb.Get(ctx, "key").Result()
    if err != nil {
        panic(err)
    }
    fmt.Println("key:", val) // key: value
}
```

> 💡 **Ключевое отличие от C#**: В go-redis **каждая операция принимает `context.Context`**. Это позволяет задавать таймауты и отмену для каждого вызова, в отличие от `StackExchange.Redis`, где таймауты настраиваются глобально.

| Аспект | C# (StackExchange.Redis) | Go (go-redis) |
|--------|--------------------------|---------------|
| **Подключение** | `ConnectionMultiplexer.Connect()` | `redis.NewClient()` |
| **Мультиплексирование** | Да, одно TCP-соединение | Пул соединений (по умолчанию 10) |
| **Context/Cancellation** | `CancellationToken` (опционально) | `context.Context` (обязательно) |
| **Результат** | `RedisValue` (неявное приведение) | Типизированные команды (`StringCmd`, `IntCmd`) |
| **Ошибки** | Исключения | `error` (проверяйте `redis.Nil` для "not found") |

### Обработка "ключ не найден"

```go
val, err := rdb.Get(ctx, "nonexistent").Result()
if err == redis.Nil {
    // Ключ не существует — это НЕ ошибка
    fmt.Println("ключ не найден")
} else if err != nil {
    // Реальная ошибка (сеть, таймаут и т.д.)
    return fmt.Errorf("ошибка Redis: %w", err)
} else {
    fmt.Println("значение:", val)
}
```

> ⚠️ **Частая ошибка C# разработчиков**: В C# `StringGet` возвращает `RedisValue`, который может быть `IsNull`. В Go отсутствие ключа — это **специальная ошибка** `redis.Nil`, а не нулевое значение. Всегда проверяйте `err == redis.Nil` перед `err != nil`.

### Конфигурация для Production

```go
rdb := redis.NewClient(&redis.Options{
    Addr:     "redis-primary.internal:6379",
    Password: os.Getenv("REDIS_PASSWORD"),
    DB:       0,

    // === Пул соединений ===
    PoolSize:     50,              // максимум соединений (default: 10 * NumCPU)
    MinIdleConns: 10,              // минимум idle соединений
    MaxIdleConns: 30,              // максимум idle соединений

    // === Таймауты ===
    DialTimeout:  5 * time.Second, // таймаут подключения (default: 5s)
    ReadTimeout:  3 * time.Second, // таймаут чтения (default: 3s)
    WriteTimeout: 3 * time.Second, // таймаут записи (default: 3s)
    PoolTimeout:  4 * time.Second, // ожидание свободного соединения из пула

    // === Retry ===
    MaxRetries:      3,                    // количество повторов
    MinRetryBackoff: 8 * time.Millisecond, // мин. задержка между повторами
    MaxRetryBackoff: 512 * time.Millisecond,

    // === TLS ===
    TLSConfig: &tls.Config{
        MinVersion: tls.VersionTLS12,
        // Для production с проверкой сертификата:
        // InsecureSkipVerify: false,
        // RootCAs: certPool,
    },
})
```

**Сравнение параметров пула**:

| Параметр | C# (StackExchange.Redis) | Go (go-redis) |
|----------|--------------------------|---------------|
| **Модель** | Мультиплексирование (1 TCP) | Пул соединений (N TCP) |
| **Размер пула** | Нет (одно соединение) | `PoolSize` (default: 10*CPU) |
| **Idle** | N/A | `MinIdleConns`, `MaxIdleConns` |
| **Retry** | `ConnectRetry` | `MaxRetries`, `MinRetryBackoff` |
| **TLS** | `ssl=true` в connection string | `TLSConfig` |

> 💡 **Важное отличие**: `StackExchange.Redis` использует **мультиплексирование** — все команды идут через одно TCP-соединение. go-redis использует **пул соединений** — каждая горутина берёт соединение из пула. Это лучше для Go, где тысячи горутин могут одновременно обращаться к Redis.

### Redis Cluster и Sentinel

```go
// Redis Cluster — автоматический шардинг
rdbCluster := redis.NewClusterClient(&redis.ClusterOptions{
    Addrs: []string{
        "redis-node-1:6379",
        "redis-node-2:6379",
        "redis-node-3:6379",
    },
    Password:     os.Getenv("REDIS_PASSWORD"),
    PoolSize:     50,
    ReadTimeout:  3 * time.Second,
    WriteTimeout: 3 * time.Second,

    // Чтение с реплик для снижения нагрузки на primary
    RouteByLatency: true,
    // или RouteRandomly: true,
})

// Redis Sentinel — автоматический failover
rdbSentinel := redis.NewFailoverClient(&redis.FailoverOptions{
    MasterName:    "mymaster",
    SentinelAddrs: []string{
        "sentinel-1:26379",
        "sentinel-2:26379",
        "sentinel-3:26379",
    },
    Password:     os.Getenv("REDIS_PASSWORD"),
    PoolSize:     50,
    ReadTimeout:  3 * time.Second,
    WriteTimeout: 3 * time.Second,
})
```

### Основные операции

#### Strings (аналог C# `StringSet` / `StringGet`)

```go
ctx := context.Background()

// Set с TTL
err := rdb.Set(ctx, "user:1:name", "Alice", 10*time.Minute).Err()

// Set только если ключ НЕ существует (аналог C# When.NotExists)
ok, err := rdb.SetNX(ctx, "lock:resource", "owner-1", 30*time.Second).Result()

// Get с проверкой существования
val, err := rdb.Get(ctx, "user:1:name").Result()
if err == redis.Nil {
    // ключ не найден
}

// Атомарный инкремент (аналог C# StringIncrement)
newVal, err := rdb.Incr(ctx, "counter").Result()
// или с шагом:
newVal, err = rdb.IncrBy(ctx, "counter", 5).Result()

// Множественные операции
err = rdb.MSet(ctx, "key1", "val1", "key2", "val2").Err()
vals, err := rdb.MGet(ctx, "key1", "key2").Result() // []interface{}
```

#### Hashes (аналог C# `HashSet` / `HashGet`)

```go
// Сохранить объект как hash (аналог C# HashSet)
err := rdb.HSet(ctx, "user:1", map[string]interface{}{
    "name":  "Alice",
    "email": "alice@example.com",
    "age":   30,
}).Err()

// Получить одно поле
name, err := rdb.HGet(ctx, "user:1", "name").Result()

// Получить все поля (аналог C# HashGetAll)
fields, err := rdb.HGetAll(ctx, "user:1").Result() // map[string]string

// Scan в структуру
type User struct {
    Name  string `redis:"name"`
    Email string `redis:"email"`
    Age   int    `redis:"age"`
}

var user User
err = rdb.HGetAll(ctx, "user:1").Scan(&user)
```

> 💡 **Scan в структуру** — мощная фича go-redis. В C# вам пришлось бы вручную маппить `HashEntry[]` в объект. В Go достаточно тегов `redis:"field_name"`.

#### Lists, Sets, Sorted Sets

```go
// Lists (очередь)
rdb.LPush(ctx, "queue:tasks", "task-1", "task-2")
task, err := rdb.RPop(ctx, "queue:tasks").Result()
// Блокирующий Pop (аналог BrokeredMessage в C#)
result, err := rdb.BLPop(ctx, 5*time.Second, "queue:tasks").Result()

// Sets (уникальные значения)
rdb.SAdd(ctx, "tags:article:1", "go", "redis", "caching")
isMember, _ := rdb.SIsMember(ctx, "tags:article:1", "go").Result()
members, _ := rdb.SMembers(ctx, "tags:article:1").Result()

// Sorted Sets (с рейтингом — аналог SortedSetAdd в C#)
rdb.ZAdd(ctx, "leaderboard", redis.Z{Score: 100, Member: "player-1"})
rdb.ZAdd(ctx, "leaderboard", redis.Z{Score: 200, Member: "player-2"})

// Top-10 игроков (по убыванию)
players, _ := rdb.ZRevRangeWithScores(ctx, "leaderboard", 0, 9).Result()
for _, p := range players {
    fmt.Printf("%s: %.0f\n", p.Member, p.Score)
}
```

#### Ключи: TTL, Expire, Delete

```go
// Установить TTL на существующий ключ
rdb.Expire(ctx, "session:abc", 30*time.Minute)

// Узнать оставшееся время жизни
ttl, _ := rdb.TTL(ctx, "session:abc").Result()
fmt.Println("TTL:", ttl) // 29m58s

// Проверить существование
exists, _ := rdb.Exists(ctx, "user:1").Result() // 1 или 0

// Удалить
deleted, _ := rdb.Del(ctx, "key1", "key2").Result() // кол-во удалённых
```

### Pipelining и транзакции

#### Pipeline — батч-операции

Pipeline отправляет несколько команд за одно сетевое обращение, значительно снижая латентность.

**C#**:
```csharp
// C#: IBatch — аналог Pipeline
var batch = db.CreateBatch();
var task1 = batch.StringSetAsync("key1", "val1");
var task2 = batch.StringSetAsync("key2", "val2");
var task3 = batch.StringGetAsync("key1");
batch.Execute();
await Task.WhenAll(task1, task2);
string? result = await task3;
```

**Go**:
```go
// Pipeline — команды буферизуются и отправляются одним пакетом
pipe := rdb.Pipeline()

// Добавляем команды в pipeline (ещё не отправлены)
incr := pipe.Incr(ctx, "counter")
pipe.Expire(ctx, "counter", time.Hour)
get := pipe.Get(ctx, "user:1:name")

// Отправляем все команды разом
_, err := pipe.Exec(ctx)
if err != nil && err != redis.Nil {
    return err
}

// Читаем результаты
fmt.Println("counter:", incr.Val())
fmt.Println("name:", get.Val())
```

Альтернативный синтаксис с callback:

```go
results, err := rdb.Pipelined(ctx, func(pipe redis.Pipeliner) error {
    pipe.Set(ctx, "key1", "val1", time.Hour)
    pipe.Set(ctx, "key2", "val2", time.Hour)
    pipe.Set(ctx, "key3", "val3", time.Hour)
    return nil
})
// results содержит Cmd для каждой команды
```

> 💡 **Производительность**: Pipeline с 100 командами может быть в 10-50x быстрее, чем 100 отдельных вызовов, потому что экономит на сетевых round-trip.

#### Транзакции (MULTI/EXEC)

```go
// TxPipeline — атомарное выполнение (MULTI/EXEC)
// Аналог C# ITransaction
_, err := rdb.TxPipelined(ctx, func(pipe redis.Pipeliner) error {
    pipe.Set(ctx, "balance:user1", 900, 0)
    pipe.Set(ctx, "balance:user2", 1100, 0)
    return nil
})
// Либо ОБА Set выполнятся, либо ни один
```

#### Watch — оптимистичные блокировки

```go
// Watch + MULTI/EXEC — аналог optimistic concurrency в C#
// Повторяем, пока транзакция не завершится без конфликта
const maxRetries = 100

for i := 0; i < maxRetries; i++ {
    err := rdb.Watch(ctx, func(tx *redis.Tx) error {
        // Читаем текущее значение
        balance, err := tx.Get(ctx, "balance:user1").Int64()
        if err != nil && err != redis.Nil {
            return err
        }

        if balance < 100 {
            return fmt.Errorf("недостаточно средств: %d", balance)
        }

        // Атомарно обновляем, если ключ не изменился
        _, err = tx.TxPipelined(ctx, func(pipe redis.Pipeliner) error {
            pipe.Set(ctx, "balance:user1", balance-100, 0)
            pipe.Set(ctx, "balance:user2", balance+100, 0)
            return nil
        })
        return err
    }, "balance:user1") // Watch за этим ключом

    if err == nil {
        break // Успех
    }
    if err == redis.TxFailedErr {
        continue // Ключ изменился, повторяем
    }
    return err // Реальная ошибка
}
```

### Pub/Sub

Redis Pub/Sub позволяет отправлять сообщения между сервисами. Это **fire-and-forget** — если подписчик не подключён, сообщение теряется.

> ⚠️ **Важно**: Pub/Sub — **не очередь сообщений**. Для надёжной доставки используйте Redis Streams или выделенную очередь (см. [раздел 4.3](./03_message_queues.md)).

**C#**:
```csharp
// C#: StackExchange.Redis Pub/Sub
var sub = redis.GetSubscriber();
await sub.SubscribeAsync("notifications", (channel, message) =>
{
    Console.WriteLine($"Получено: {message}");
});

await sub.PublishAsync("notifications", "Hello!");
```

**Go**:
```go
// Подписка
sub := rdb.Subscribe(ctx, "notifications")
defer sub.Close()

// Получение сообщений в горутине
ch := sub.Channel()
go func() {
    for msg := range ch {
        fmt.Printf("Канал: %s, Сообщение: %s\n", msg.Channel, msg.Payload)
    }
}()

// Публикация
err := rdb.Publish(ctx, "notifications", "Hello!").Err()
```

**Pattern-подписка** (по маске):

```go
// Подписка на все каналы "events.*"
sub := rdb.PSubscribe(ctx, "events.*")
defer sub.Close()

for msg := range sub.Channel() {
    fmt.Printf("Pattern: %s, Канал: %s, Сообщение: %s\n",
        msg.Pattern, msg.Channel, msg.Payload)
}
```

### Распределённые блокировки (Redlock)

Для координации между инстансами приложения часто нужны распределённые блокировки. В Go для этого используется библиотека [redsync](https://github.com/go-redsync/redsync).

**C# — RedLock.net**:
```csharp
// C#: RedLock.net
await using var redLock = await redlockFactory.CreateLockAsync(
    "resource:123",
    TimeSpan.FromSeconds(30));

if (redLock.IsAcquired)
{
    // Критическая секция
}
```

**Go — redsync**:
```go
import (
    "github.com/go-redsync/redsync/v4"
    "github.com/go-redsync/redsync/v4/redis/goredis/v9"
)

// Создаём redsync (один раз при старте)
pool := goredis.NewPool(rdb)
rs := redsync.New(pool)

// Создаём мьютекс
mutex := rs.NewMutex("lock:resource:123",
    redsync.WithExpiry(30*time.Second),       // TTL блокировки
    redsync.WithTries(32),                     // макс. попыток
    redsync.WithRetryDelay(100*time.Millisecond),
)

// Захват блокировки
if err := mutex.LockContext(ctx); err != nil {
    return fmt.Errorf("не удалось захватить блокировку: %w", err)
}
defer func() {
    if ok, err := mutex.UnlockContext(ctx); !ok || err != nil {
        log.Printf("ошибка при снятии блокировки: %v", err)
    }
}()

// Критическая секция — только один инстанс выполняет этот код
processResource(ctx, "resource:123")
```

> ⚠️ **Ограничения Redlock**: Алгоритм Redlock имеет известные проблемы (описанные Martin Kleppmann). Для критичных операций рассмотрите блокировки на уровне БД (SELECT FOR UPDATE) или etcd/ZooKeeper. Для большинства задач (дедупликация, rate limiting) Redlock работает отлично.

**Когда использовать распределённые блокировки**:

| Задача | Redis Lock | DB Lock | etcd/ZooKeeper |
|--------|-----------|---------|----------------|
| **Дедупликация задач** | ✅ Хорошо | ➖ Медленно | ➖ Overkill |
| **Rate limiting** | ✅ Хорошо | ➖ Медленно | ➖ Overkill |
| **Финансовые операции** | ⚠️ С осторожностью | ✅ Надёжно | ✅ Надёжно |
| **Leader election** | ⚠️ Не рекомендуется | ➖ | ✅ Идеально |

---

## In-Memory кэширование

In-memory кэш — это первая линия защиты от нагрузки на БД и Redis. Обращение к локальной памяти на порядки быстрее сетевого вызова (наносекунды vs микросекунды). Однако в Go есть нюанс, которого нет в C#: **GC сканирует все указатели в heap**, и миллионы закэшированных объектов могут вызвать паузы GC.

> 💡 **Для C# разработчиков**: В .NET вы используете `IMemoryCache` и не думаете о GC — CLR GC работает с поколениями и крупными объектами в Large Object Heap. В Go GC работает иначе (см. [раздел 2.3](../part2-advanced/03_gc.md)), и выбор библиотеки кэширования напрямую влияет на паузы GC.

### sync.Map: когда использовать

`sync.Map` подробно рассмотрен в [разделе 2.4](../part2-advanced/04_sync_primitives.md). Здесь — краткие рекомендации для кэширования.

**Когда sync.Map подходит**:
- Конфигурации, загруженные один раз при старте
- DNS-кэш (редкие записи, частые чтения)
- Кэш скомпилированных регулярных выражений

**Когда sync.Map НЕ подходит для кэширования**:
- Нет TTL — записи живут вечно
- Нет ограничения размера — память растёт бесконтрольно
- Нет политики вытеснения (eviction) — нет LRU/LFU
- Нет метрик (hit/miss rate)

```go
// sync.Map — подходит ТОЛЬКО для write-once/read-many сценариев
var configCache sync.Map

// Загрузка при старте
configCache.Store("feature.enabled", true)
configCache.Store("max.retries", 3)

// Чтение (потокобезопасно, без блокировок на read path)
if val, ok := configCache.Load("feature.enabled"); ok {
    enabled := val.(bool)
    // ...
}
```

> ⚠️ **Для кэширования с TTL и eviction используйте специализированные библиотеки**, описанные ниже.

### map + RWMutex: простейший кэш

Прежде чем тянуть зависимости, иногда достаточно `map` с `sync.RWMutex` и generics.

**C# — Dictionary с lock**:
```csharp
// C#: простейший потокобезопасный кэш
public class SimpleCache<TKey, TValue> where TKey : notnull
{
    private readonly Dictionary<TKey, (TValue Value, DateTime Expiry)> _cache = new();
    private readonly object _lock = new();

    public bool TryGet(TKey key, out TValue value)
    {
        lock (_lock)
        {
            if (_cache.TryGetValue(key, out var entry) && entry.Expiry > DateTime.UtcNow)
            {
                value = entry.Value;
                return true;
            }
            value = default!;
            return false;
        }
    }
}
```

**Go — map + RWMutex с generics**:
```go
// Простейший TTL-кэш с generics (Go 1.18+)
type SimpleCache[K comparable, V any] struct {
    mu    sync.RWMutex
    items map[K]cacheItem[V]
}

type cacheItem[V any] struct {
    value     V
    expiresAt time.Time
}

func NewSimpleCache[K comparable, V any]() *SimpleCache[K, V] {
    return &SimpleCache[K, V]{
        items: make(map[K]cacheItem[V]),
    }
}

func (c *SimpleCache[K, V]) Set(key K, value V, ttl time.Duration) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.items[key] = cacheItem[V]{
        value:     value,
        expiresAt: time.Now().Add(ttl),
    }
}

func (c *SimpleCache[K, V]) Get(key K) (V, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()

    item, ok := c.items[key]
    if !ok || time.Now().After(item.expiresAt) {
        var zero V
        return zero, false
    }
    return item.value, true
}

func (c *SimpleCache[K, V]) Delete(key K) {
    c.mu.Lock()
    defer c.mu.Unlock()
    delete(c.items, key)
}
```

**Когда этого достаточно**:
- Небольшой кэш (< 10 000 записей)
- Простые требования (TTL, без eviction)
- Не хотите добавлять зависимости

**Когда нужна библиотека**:
- Нужна политика вытеснения (LRU/LFU)
- Тысячи и более записей (конкуренция на мьютексе)
- Нужны метрики hit/miss
- Важна производительность GC

### patrickmn/go-cache: простой TTL кэш

[go-cache](https://github.com/patrickmn/go-cache) — простая, проверенная временем библиотека для in-memory кэширования с автоматической очисткой просроченных записей.

```bash
go get github.com/patrickmn/go-cache
```

**C# аналог**: `MemoryCache` с `MemoryCacheEntryOptions`.

```go
import "github.com/patrickmn/go-cache"

// Создаём кэш: default TTL 5 минут, очистка каждые 10 минут
c := cache.New(5*time.Minute, 10*time.Minute)

// Set (с default TTL)
c.Set("user:1", &User{Name: "Alice"}, cache.DefaultExpiration)

// Set с кастомным TTL
c.Set("session:abc", sessionData, 30*time.Minute)

// Set без TTL (живёт вечно)
c.Set("config:version", "1.0", cache.NoExpiration)

// Get с type assertion
if val, found := c.Get("user:1"); found {
    user := val.(*User) // type assertion — нет generics
    fmt.Println(user.Name)
}

// Delete
c.Delete("user:1")

// Атомарный инкремент
c.IncrementInt("counter", 1)

// Количество элементов
count := c.ItemCount()
```

**Достоинства**:
- Простой API, минимум конфигурации
- Автоматическая очистка просроченных записей (janitor goroutine)
- Потокобезопасный

**Недостатки**:
- Хранит `interface{}` — нет generics, нужен type assertion
- Нет политики вытеснения — только TTL
- Нет ограничения размера — память может расти бесконтрольно
- GC pressure при большом количестве записей (всё хранится как указатели)
- Не поддерживается активно (последний релиз — 2020)

> 💡 **Идеально для**: Небольших кэшей (до 100K записей) с простыми требованиями TTL. Если нужна eviction policy или высокая производительность — используйте ristretto.

### dgraph-io/ristretto: высокопроизводительный кэш

[ristretto](https://github.com/dgraph-io/ristretto) — высокопроизводительный кэш от команды Dgraph, использующий **TinyLFU** (admission policy) и **Sampled LFU** (eviction policy) для оптимального hit ratio.

```bash
go get github.com/dgraph-io/ristretto/v2
```

> 💡 **Для C# разработчиков**: Ristretto ближе всего к `LazyCache` по философии — он оптимизирует hit ratio через admission policy. Но в отличие от `LazyCache`, ristretto v2 поддерживает generics.

```go
import "github.com/dgraph-io/ristretto/v2"

// Создаём кэш с generics (v2)
cache, err := ristretto.NewCache(&ristretto.Config[string, *User]{
    // NumCounters: количество ключей для отслеживания частоты (TinyLFU)
    // Рекомендация: 10x от ожидаемого количества ключей
    NumCounters: 100_000,

    // MaxCost: максимальный "вес" всех элементов
    // Например, максимум 64MB данных (если cost = размер в байтах)
    MaxCost: 64 << 20, // 64 MB

    // BufferItems: размер буфера для асинхронной записи
    // 64 — рекомендуемое значение
    BufferItems: 64,
})
if err != nil {
    panic(err)
}
defer cache.Close()

// Set с cost (вес элемента)
user := &User{Name: "Alice", Email: "alice@example.com"}
cache.SetWithTTL("user:1", user, 1, 5*time.Minute)
// cost=1 — если считаем по количеству элементов
// cost=len(data) — если считаем по размеру данных

// Важно: Set асинхронный! Значение может быть недоступно сразу
cache.Wait() // ждём, пока буфер обработается

// Get
if user, found := cache.Get("user:1"); found {
    fmt.Println(user.Name) // уже типизированный *User!
}

// Delete
cache.Del("user:1")

// Метрики
metrics := cache.Metrics
fmt.Printf("Hits: %d, Misses: %d, Hit Ratio: %.2f%%\n",
    metrics.Hits(), metrics.Misses(),
    metrics.Ratio()*100)
```

**Как работает TinyLFU admission**:

```
Новый элемент "X" → Проверка admission policy:
  1. Достаточно ли часто запрашивается "X"?
  2. Если да → допускаем в кэш
  3. Если кэш полон → вытесняем менее популярный элемент
  4. Если "X" непопулярен → НЕ кладём в кэш (защита от scan pollution)
```

> ⚠️ **Важный нюанс**: `Set` в ristretto **асинхронный и не гарантирует запись**! Admission policy может отклонить элемент, если он недостаточно "популярен". Это нормально — ristretto оптимизирует общий hit ratio, а не отдельные записи. Для данных, которые **обязательно** должны быть в кэше, это неподходящий инструмент.

**Достоинства**:
- Высокий hit ratio благодаря TinyLFU
- Generics в v2 — типобезопасность
- Cost-based eviction — ограничение по памяти
- Встроенные метрики (hits, misses, ratio)
- Конкурентный доступ без общих блокировок

**Недостатки**:
- `Set` асинхронный — значение может не попасть в кэш
- Сложнее в настройке, чем go-cache
- Eventual consistency (буферизация записей)

### allegro/bigcache: GC-friendly кэш

[bigcache](https://github.com/allegro/bigcache) — кэш, спроектированный для **минимального влияния на GC**. Критически важен для сценариев с миллионами записей.

```bash
go get github.com/allegro/bigcache/v3
```

**Проблема**: Обычный `map[string]*Object` с миллионом записей создаёт миллион указателей. Go GC при каждом цикле сканирует **все** указатели в heap — это может вызвать паузы в десятки миллисекунд.

**Как bigcache решает проблему**:

```
Обычный map:     map[string]*Value  → миллионы указателей → GC сканирует всё
bigcache:        map[uint64]uint32  → БЕЗ указателей → GC не трогает
                 + []byte (данные)  → один большой slice → GC видит ОДИН объект
```

Подробнее об этом трюке — в [разделе 2.3](../part2-advanced/03_gc.md).

```go
import "github.com/allegro/bigcache/v3"

cache, err := bigcache.New(context.Background(), bigcache.Config{
    // Количество шардов (должно быть степенью 2)
    Shards: 1024,

    // TTL для всех записей (одинаковый!)
    LifeWindow: 10 * time.Minute,

    // Очистка просроченных записей
    CleanWindow: 5 * time.Minute,

    // Начальный размер каждого шарда (в записях)
    MaxEntriesInWindow: 1000 * 10 * 60, // ожидаемые записи за LifeWindow

    // Максимальный размер одной записи (в байтах)
    MaxEntrySize: 500,

    // Вывод логов
    Verbose: false,

    // Максимальный размер кэша (MB). 0 = без ограничений
    HardMaxCacheSize: 256,
})
if err != nil {
    panic(err)
}
defer cache.Close()

// Set — только []byte!
data, _ := json.Marshal(&User{Name: "Alice"})
cache.Set("user:1", data)

// Get — возвращает []byte
entry, err := cache.Get("user:1")
if err != nil {
    // bigcache возвращает ошибку для miss (не sentinel value)
    fmt.Println("miss:", err)
    return
}

var user User
json.Unmarshal(entry, &user)
```

**Достоинства**:
- Минимальное влияние на GC — идеален для миллионов записей
- Быстрый: шардирование снижает конкуренцию на блокировках
- Ограничение по памяти (`HardMaxCacheSize`)

**Недостатки**:
- Работает **только с `[]byte`** — нужна ручная сериализация
- **Один TTL для всех записей** — нельзя задать TTL per-key
- Hash-коллизии могут перезаписать данные (редко, но возможно)
- Нет admission/eviction policy (FIFO в рамках шарда)

> 💡 **Когда выбирать bigcache**: У вас миллионы записей и важна стабильная латентность (P99). Типичный пример — кэш сессий, DNS-записей, или результатов API.

### Сравнительная таблица in-memory библиотек

| Характеристика | `map` + `RWMutex` | go-cache | ristretto v2 | bigcache |
|---------------|-------------------|----------|--------------|----------|
| **Generics** | ✅ Да | ❌ `interface{}` | ✅ Да (v2) | ❌ `[]byte` |
| **TTL** | Ручной | ✅ Per-key | ✅ Per-key | ⚠️ Глобальный |
| **Eviction Policy** | ❌ Нет | ❌ Только TTL | ✅ TinyLFU | ❌ FIFO |
| **Max Size** | ❌ Нет | ❌ Нет | ✅ Cost-based | ✅ MB-based |
| **GC Pressure** | 🔴 Высокая | 🔴 Высокая | 🟡 Средняя | 🟢 Минимальная |
| **Метрики** | ❌ Нет | ❌ Нет | ✅ Встроенные | ❌ Нет |
| **Потокобезопасность** | ✅ Да | ✅ Да | ✅ Да | ✅ Да |
| **Сложность** | Минимальная | Низкая | Средняя | Низкая |
| **Лучший сценарий** | < 1K записей | < 100K записей | Важен hit ratio | > 1M записей |

**Блок-схема выбора**:

```
Сколько записей в кэше?
│
├── < 1 000 → map + RWMutex (не тяните зависимости)
│
├── 1K - 100K
│   ├── Нужен лучший hit ratio? → ristretto
│   └── Простой TTL кэш? → go-cache
│
└── > 100K
    ├── Записи > 1 KB? → bigcache (GC-friendly)
    ├── Нужен hit ratio? → ristretto (но следите за GC)
    └── Критична P99 латентность? → bigcache
```

---

## Абстракция над кэшами: eko/gocache

В C# есть `IDistributedCache` — стандартный интерфейс, за которым может стоять Redis, SQL Server или in-memory хранилище. В Go стандартного интерфейса нет, но библиотека [eko/gocache](https://github.com/eko/gocache) предоставляет подобную абстракцию.

```bash
go get github.com/eko/gocache/lib/v4
go get github.com/eko/gocache/store/redis/v4
go get github.com/eko/gocache/store/ristretto/v4
go get github.com/eko/gocache/store/bigcache/v4
```

### Единый интерфейс для разных бэкендов

```go
import (
    "github.com/eko/gocache/lib/v4/cache"
    "github.com/eko/gocache/lib/v4/store"
    redisstore "github.com/eko/gocache/store/redis/v4"
    ristrettostore "github.com/eko/gocache/store/ristretto/v4"
)

// Redis store
redisStore := redisstore.NewRedis(rdb)

// Ristretto store
ristrettoStore := ristrettostore.NewRistretto(ristrettoCache)

// Единый API для любого store
cacheManager := cache.New[*User](redisStore)

// Set / Get / Delete — одинаковый API
err := cacheManager.Set(ctx, "user:1", &User{Name: "Alice"},
    store.WithExpiration(5*time.Minute),
)

user, err := cacheManager.Get(ctx, "user:1")
// user уже типизированный *User

err = cacheManager.Delete(ctx, "user:1")
```

### Chain Cache (L1 + L2)

Главная фича gocache — **цепочка кэшей**, аналог `FusionCache` / `HybridCache` в .NET:

```go
import "github.com/eko/gocache/lib/v4/cache"

// L1: быстрый in-memory (ristretto)
ristrettoStore := ristrettostore.NewRistretto(ristrettoCache)

// L2: общий distributed (Redis)
redisStore := redisstore.NewRedis(rdb)

// Chain: сначала L1, потом L2
chainCache := cache.NewChain[*User](
    cache.New[*User](ristrettoStore),
    cache.New[*User](redisStore),
)

// Get: ristretto → (miss) → Redis → (miss) → error
user, err := chainCache.Get(ctx, "user:1")

// Set: записывает в ОБА уровня
err = chainCache.Set(ctx, "user:1", user,
    store.WithExpiration(5*time.Minute),
)
```

### Loadable Cache (auto-populate)

```go
// Loadable cache — автоматически загружает данные при miss
// Аналог C# LazyCache.GetOrAdd()
loadableCache := cache.NewLoadable[*User](
    // Функция загрузки данных
    func(ctx context.Context, key any) (*User, error) {
        return userRepo.FindByID(ctx, key.(string))
    },
    // Кэш (может быть chain cache)
    chainCache,
)

// Get: cache hit → return
// Get: cache miss → вызов loader → сохранение в кэш → return
user, err := loadableCache.Get(ctx, "user:1")
```

### Metric Cache

```go
import "github.com/eko/gocache/lib/v4/metrics"

// Оборачиваем кэш в метрики (Prometheus)
metricCache := metrics.NewMetrics[*User](
    promMetrics,       // *metrics.Prometheus
    chainCache,
)
// Автоматически отправляет hit/miss метрики в Prometheus
```

### Когда использовать gocache vs собственную реализацию

| Критерий | gocache | Своя реализация |
|----------|---------|-----------------|
| **Несколько бэкендов** | ✅ Chain из коробки | Нужно писать самому |
| **Auto-populate** | ✅ Loadable cache | Нужно писать самому |
| **Метрики** | ✅ Prometheus из коробки | Нужно писать самому |
| **Контроль** | Ограничен API gocache | Полный контроль |
| **Зависимости** | Добавляет 4+ модуля | Минимум |
| **Stampede protection** | ❌ Нет (нужен singleflight) | Можете добавить |

> 💡 **Идиоматичный Go**: Многие Go-команды предпочитают собственную реализацию поверх конкретных библиотек (go-redis + ristretto), чем абстракцию gocache. Это больше кода, но меньше зависимостей и полный контроль. Мы покажем оба подхода в практических примерах.

---

## Паттерны кэширования

Независимо от выбора библиотеки, вам нужно решить **как** кэшировать данные. Паттерны кэширования определяют, когда данные попадают в кэш, когда обновляются и как обеспечивается консистентность.

### Cache-Aside (Lazy Loading)

Самый распространённый паттерн. Приложение само управляет кэшем: проверяет → при miss загружает из БД → кладёт в кэш.

```
Клиент → Приложение:
  1. Проверить кэш
  2. Cache HIT  → вернуть данные
  3. Cache MISS → запросить БД → сохранить в кэш → вернуть данные
```

**C# — IDistributedCache**:
```csharp
// C#: типичный Cache-Aside
public async Task<User?> GetUserAsync(string id)
{
    var cached = await _cache.GetStringAsync($"user:{id}");
    if (cached != null)
        return JsonSerializer.Deserialize<User>(cached);

    var user = await _dbContext.Users.FindAsync(id);
    if (user != null)
    {
        await _cache.SetStringAsync($"user:{id}",
            JsonSerializer.Serialize(user),
            new DistributedCacheEntryOptions
            {
                AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(5)
            });
    }
    return user;
}
```

**Go — Cache-Aside**:
```go
func (s *UserService) GetUser(ctx context.Context, id string) (*User, error) {
    key := fmt.Sprintf("user:%s", id)

    // 1. Проверяем кэш
    cached, err := s.redis.Get(ctx, key).Bytes()
    if err == nil {
        var user User
        if err := json.Unmarshal(cached, &user); err == nil {
            return &user, nil
        }
        // Ошибка десериализации — идём в БД
    } else if err != redis.Nil {
        // Ошибка Redis (не miss) — логируем, но не падаем
        s.logger.Warn("ошибка Redis", "error", err, "key", key)
    }

    // 2. Cache miss — загружаем из БД
    user, err := s.repo.FindByID(ctx, id)
    if err != nil {
        return nil, fmt.Errorf("поиск пользователя: %w", err)
    }

    // 3. Сохраняем в кэш (асинхронно, ошибка не критична)
    data, _ := json.Marshal(user)
    if err := s.redis.Set(ctx, key, data, 5*time.Minute).Err(); err != nil {
        s.logger.Warn("не удалось закэшировать", "error", err, "key", key)
    }

    return user, nil
}
```

> 💡 **Важный принцип**: Ошибка кэширования **не должна** ломать основную логику. Кэш — это оптимизация, а не источник правды. Если Redis недоступен, приложение должно работать (медленнее, но работать).

**Достоинства**: Кэшируются только запрошенные данные. Простой в реализации.

**Недостатки**: Первый запрос всегда медленный (cold cache). Данные могут устареть (stale).

### Write-Through

Данные записываются в кэш **одновременно** с записью в БД. Кэш всегда актуален.

```go
func (s *UserService) UpdateUser(ctx context.Context, user *User) error {
    // 1. Записываем в БД
    if err := s.repo.Update(ctx, user); err != nil {
        return fmt.Errorf("обновление пользователя: %w", err)
    }

    // 2. Обновляем кэш (синхронно!)
    key := fmt.Sprintf("user:%s", user.ID)
    data, _ := json.Marshal(user)
    if err := s.redis.Set(ctx, key, data, 5*time.Minute).Err(); err != nil {
        // Кэш не обновился — данные устареют, но не потеряются
        s.logger.Warn("не удалось обновить кэш", "error", err, "key", key)
    }

    return nil
}
```

**Достоинства**: Кэш всегда содержит актуальные данные. Нет stale reads.

**Недостатки**: Увеличенная латентность записи (БД + кэш). Кэшируются данные, которые могут никогда не быть прочитаны.

### Write-Behind (Write-Back)

Данные сначала записываются в кэш, а в БД — **асинхронно** через буфер. Минимальная латентность записи, но есть риск потери данных.

```go
type WriteBackCache struct {
    redis  *redis.Client
    writes chan writeOp
    repo   UserRepository
}

type writeOp struct {
    key  string
    user *User
}

func NewWriteBackCache(rdb *redis.Client, repo UserRepository) *WriteBackCache {
    wbc := &WriteBackCache{
        redis:  rdb,
        writes: make(chan writeOp, 1000), // буфер на 1000 операций
        repo:   repo,
    }
    go wbc.processWrites() // фоновая горутина для записи в БД
    return wbc
}

func (wbc *WriteBackCache) Set(ctx context.Context, user *User) error {
    key := fmt.Sprintf("user:%s", user.ID)
    data, _ := json.Marshal(user)

    // 1. Записываем в кэш (быстро)
    if err := wbc.redis.Set(ctx, key, data, 10*time.Minute).Err(); err != nil {
        return err
    }

    // 2. Отправляем в очередь для записи в БД (неблокирующе)
    select {
    case wbc.writes <- writeOp{key: key, user: user}:
    default:
        // Буфер полон — записываем синхронно
        return wbc.repo.Update(ctx, user)
    }
    return nil
}

func (wbc *WriteBackCache) processWrites() {
    for op := range wbc.writes {
        ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
        if err := wbc.repo.Update(ctx, op.user); err != nil {
            log.Printf("ошибка записи в БД: %v (key=%s)", err, op.key)
            // TODO: retry logic, DLQ
        }
        cancel()
    }
}
```

> ⚠️ **Риск потери данных**: Если приложение упадёт до записи в БД, данные из буфера будут потеряны. Используйте только для некритичных данных (счётчики просмотров, last seen и т.д.).

### Read-Through

Кэш сам загружает данные при miss — приложение работает только с кэшем.

```go
// Read-Through с помощью функции-загрузчика
type ReadThroughCache[V any] struct {
    cache  *redis.Client
    loader func(ctx context.Context, key string) (V, error)
    ttl    time.Duration
}

func (c *ReadThroughCache[V]) Get(ctx context.Context, key string) (V, error) {
    // 1. Пробуем кэш
    cached, err := c.cache.Get(ctx, key).Bytes()
    if err == nil {
        var val V
        if err := json.Unmarshal(cached, &val); err == nil {
            return val, nil
        }
    }

    // 2. Cache miss — вызываем loader
    val, err := c.loader(ctx, key)
    if err != nil {
        return val, err
    }

    // 3. Сохраняем в кэш
    data, _ := json.Marshal(val)
    c.cache.Set(ctx, key, data, c.ttl)

    return val, nil
}

// Использование
userCache := &ReadThroughCache[*User]{
    cache: rdb,
    loader: func(ctx context.Context, key string) (*User, error) {
        id := strings.TrimPrefix(key, "user:")
        return userRepo.FindByID(ctx, id)
    },
    ttl: 5 * time.Minute,
}

user, err := userCache.Get(ctx, "user:123")
```

> 💡 **Read-Through vs Cache-Aside**: В Cache-Aside приложение явно управляет кэшем. В Read-Through логика загрузки инкапсулирована в кэш. Read-Through проще использовать, но менее гибок.

### Cache Stampede Prevention (singleflight)

**Cache stampede** (также known as "thundering herd") — ситуация, когда TTL ключа истекает и сотни горутин одновременно запрашивают одни и те же данные из БД.

```
TTL ключа "popular:item" истёк
  → 500 горутин одновременно делают GET → miss
  → 500 запросов к БД
  → 500 SET в Redis
  → БД перегружена, Redis перегружен
```

Решение — **`singleflight`** (подробнее о нём в [разделе 2.4](../part2-advanced/04_sync_primitives.md)). Только одна горутина выполняет запрос, остальные ждут её результат.

**C# — LazyCache (встроенная защита)**:
```csharp
// C#: LazyCache автоматически предотвращает stampede
var user = await _lazyCache.GetOrAddAsync($"user:{id}", async entry =>
{
    entry.AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(5);
    return await _dbContext.Users.FindAsync(id);
});
```

**Go — singleflight + кэш**:
```go
import "golang.org/x/sync/singleflight"

type CachedUserService struct {
    redis  *redis.Client
    repo   UserRepository
    sf     singleflight.Group
}

func (s *CachedUserService) GetUser(ctx context.Context, id string) (*User, error) {
    key := fmt.Sprintf("user:%s", id)

    // 1. Проверяем кэш
    cached, err := s.redis.Get(ctx, key).Bytes()
    if err == nil {
        var user User
        if err := json.Unmarshal(cached, &user); err == nil {
            return &user, nil
        }
    }

    // 2. Cache miss — singleflight: только ОДНА горутина идёт в БД
    result, err, shared := s.sf.Do(key, func() (interface{}, error) {
        // Повторная проверка кэша (другая горутина могла уже заполнить)
        cached, err := s.redis.Get(ctx, key).Bytes()
        if err == nil {
            var user User
            if err := json.Unmarshal(cached, &user); err == nil {
                return &user, nil
            }
        }

        // Загружаем из БД
        user, err := s.repo.FindByID(ctx, id)
        if err != nil {
            return nil, err
        }

        // Сохраняем в кэш
        data, _ := json.Marshal(user)
        s.redis.Set(ctx, key, data, 5*time.Minute)

        return user, nil
    })

    if err != nil {
        return nil, err
    }

    _ = shared // true, если результат был shared с другими горутинами
    return result.(*User), nil
}
```

> 💡 **Это самый важный паттерн кэширования в Go**. Без `singleflight` кэш под нагрузкой может усилить проблему вместо того, чтобы её решить.

### Стратегии TTL

| Стратегия | Описание | Когда использовать |
|-----------|----------|-------------------|
| **Fixed TTL** | Ключ живёт ровно N минут | Большинство случаев |
| **Sliding** | TTL обновляется при каждом доступе | Сессии, "горячие" данные |
| **Jittered** | TTL = base ± random | Предотвращение thundering herd |
| **No TTL + Event** | Без TTL, инвалидация по событию | Критичная консистентность |

**Jittered TTL** — добавляем случайный разброс, чтобы ключи не истекали одновременно:

```go
// Без jitter: все ключи истекают одновременно → stampede
ttl := 5 * time.Minute

// С jitter: ключи истекают в разное время → плавная нагрузка
func jitteredTTL(base time.Duration, jitterPercent float64) time.Duration {
    jitter := time.Duration(float64(base) * jitterPercent * (rand.Float64()*2 - 1))
    return base + jitter
}

ttl := jitteredTTL(5*time.Minute, 0.1) // 4.5 - 5.5 минут
```

**Sliding TTL** — обновление TTL при каждом обращении:

```go
func (s *SessionService) GetSession(ctx context.Context, sessionID string) (*Session, error) {
    key := "session:" + sessionID

    data, err := s.redis.Get(ctx, key).Bytes()
    if err != nil {
        return nil, err
    }

    // Продлеваем TTL при каждом доступе (sliding)
    s.redis.Expire(ctx, key, 30*time.Minute)

    var session Session
    json.Unmarshal(data, &session)
    return &session, nil
}
```

### Инвалидация кэша

> "В компьютерных науках есть только две сложные вещи: инвалидация кэша и именование."

| Подход | Реализация | Плюсы | Минусы |
|--------|-----------|-------|--------|
| **TTL** | `Set(key, val, 5*time.Minute)` | Простой, автоматический | Stale данные до истечения TTL |
| **Явное удаление** | `Del(key)` при обновлении | Точный, немедленный | Нужно знать все ключи |
| **Pub/Sub** | Публикация события инвалидации | Распределённый | Redis Pub/Sub ненадёжен |
| **Tag-based** | Группы ключей по тегу | Удобная массовая инвалидация | Сложная реализация |
| **Version-based** | `user:v3:123` вместо `user:123` | Мгновенный, без удаления | Старые версии остаются |

**Явное удаление** при обновлении:

```go
func (s *UserService) UpdateUser(ctx context.Context, user *User) error {
    if err := s.repo.Update(ctx, user); err != nil {
        return err
    }

    // Инвалидируем все связанные ключи
    keys := []string{
        fmt.Sprintf("user:%s", user.ID),
        fmt.Sprintf("user:email:%s", user.Email),
        fmt.Sprintf("user:list:page:*"), // паттерн — нужен SCAN
    }
    s.redis.Del(ctx, keys[:2]...) // точные ключи

    // Для паттернов — используем SCAN (не KEYS!)
    s.invalidateByPattern(ctx, "user:list:page:*")

    return nil
}

func (s *UserService) invalidateByPattern(ctx context.Context, pattern string) {
    iter := s.redis.Scan(ctx, 0, pattern, 100).Iterator()
    var keys []string
    for iter.Next(ctx) {
        keys = append(keys, iter.Val())
    }
    if len(keys) > 0 {
        s.redis.Del(ctx, keys...)
    }
}
```

> ⚠️ **Никогда не используйте `KEYS`** в production! Команда `KEYS` блокирует Redis на время выполнения. Используйте `SCAN` — он итерирует по ключам порциями, не блокируя сервер.

**Version-based** ключи — элегантное решение без удаления:

```go
// Вместо инвалидации — меняем версию
// Старые ключи автоматически истекут по TTL

func (s *UserService) getCacheVersion(ctx context.Context) (int64, error) {
    return s.redis.Get(ctx, "user:cache:version").Int64()
}

func (s *UserService) GetUser(ctx context.Context, id string) (*User, error) {
    version, _ := s.getCacheVersion(ctx)
    key := fmt.Sprintf("user:v%d:%s", version, id)
    // ...
}

func (s *UserService) InvalidateAll(ctx context.Context) error {
    // Инкрементируем версию — все старые ключи больше не читаются
    return s.redis.Incr(ctx, "user:cache:version").Err()
}
```

---

## Multi-Level кэширование (L1 + L2)

В production-системах с высокой нагрузкой одного уровня кэша недостаточно. **Multi-level cache** комбинирует in-memory (L1) и distributed (L2) кэши для оптимальной производительности.

> 💡 **Для C# разработчиков**: Это аналог `FusionCache` / `HybridCache` из .NET 9. L1 — `IMemoryCache`, L2 — `IDistributedCache`. В Go вы строите эту архитектуру вручную.

### Архитектура

```
Запрос → L1 (ristretto, in-memory)
           │
           ├── HIT → возврат (наносекунды)
           │
           └── MISS → L2 (Redis, distributed)
                        │
                        ├── HIT → сохранить в L1 → возврат (микросекунды)
                        │
                        └── MISS → БД → сохранить в L2 + L1 → возврат (миллисекунды)
```

**Зачем два уровня**:

| | L1 (in-memory) | L2 (Redis) |
|---|---|---|
| **Скорость** | ~100 ns | ~500 µs (сеть) |
| **Объём** | Ограничен RAM процесса | Десятки GB |
| **Scope** | Локальный для инстанса | Общий для всех инстансов |
| **Консистентность** | Может быть stale между инстансами | Единый источник |
| **TTL** | Короткий (1-5 минут) | Длинный (10-60 минут) |

### Реализация

```go
type MultiLevelCache[V any] struct {
    l1    *ristretto.Cache[string, V]   // in-memory
    l2    *redis.Client                  // distributed
    sf    singleflight.Group             // stampede prevention
    ttlL1 time.Duration
    ttlL2 time.Duration
}

func NewMultiLevelCache[V any](
    l1 *ristretto.Cache[string, V],
    l2 *redis.Client,
    ttlL1, ttlL2 time.Duration,
) *MultiLevelCache[V] {
    return &MultiLevelCache[V]{
        l1:    l1,
        l2:    l2,
        ttlL1: ttlL1,
        ttlL2: ttlL2,
    }
}

func (c *MultiLevelCache[V]) Get(
    ctx context.Context,
    key string,
    loader func(ctx context.Context) (V, error),
) (V, error) {
    // 1. Проверяем L1 (наносекунды)
    if val, found := c.l1.Get(key); found {
        return val, nil
    }

    // 2. singleflight — только одна горутина идёт дальше
    result, err, _ := c.sf.Do(key, func() (interface{}, error) {
        // 3. Проверяем L2 (Redis)
        cached, err := c.l2.Get(ctx, key).Bytes()
        if err == nil {
            var val V
            if err := json.Unmarshal(cached, &val); err == nil {
                // Заполняем L1
                c.l1.SetWithTTL(key, val, 1, c.ttlL1)
                return val, nil
            }
        }

        // 4. Cache miss на обоих уровнях — загружаем из источника
        val, err := loader(ctx)
        if err != nil {
            return val, err
        }

        // 5. Заполняем оба уровня
        data, _ := json.Marshal(val)
        c.l2.Set(ctx, key, data, c.ttlL2)
        c.l1.SetWithTTL(key, val, 1, c.ttlL1)

        return val, nil
    })

    if err != nil {
        var zero V
        return zero, err
    }
    return result.(V), nil
}

func (c *MultiLevelCache[V]) Invalidate(ctx context.Context, key string) {
    c.l1.Del(key)
    c.l2.Del(ctx, key)
}

func (c *MultiLevelCache[V]) Set(ctx context.Context, key string, val V) error {
    c.l1.SetWithTTL(key, val, 1, c.ttlL1)
    data, err := json.Marshal(val)
    if err != nil {
        return err
    }
    return c.l2.Set(ctx, key, data, c.ttlL2).Err()
}
```

### Инвалидация между инстансами

Проблема: Pod A обновляет данные → удаляет из L2 → но L1 на Pod B, Pod C всё ещё содержит stale данные.

Решение: **Redis Pub/Sub** для уведомления об инвалидации.

```go
type DistributedCache[V any] struct {
    *MultiLevelCache[V]
    pubsub    *redis.PubSub
    channel   string
    cancelCtx context.CancelFunc
}

func NewDistributedCache[V any](
    l1 *ristretto.Cache[string, V],
    l2 *redis.Client,
    ttlL1, ttlL2 time.Duration,
    channel string,
) *DistributedCache[V] {
    ctx, cancel := context.WithCancel(context.Background())

    dc := &DistributedCache[V]{
        MultiLevelCache: NewMultiLevelCache(l1, l2, ttlL1, ttlL2),
        channel:         channel,
        cancelCtx:       cancel,
    }

    // Подписываемся на канал инвалидации
    dc.pubsub = l2.Subscribe(ctx, channel)
    go dc.listenInvalidations(ctx)

    return dc
}

func (dc *DistributedCache[V]) listenInvalidations(ctx context.Context) {
    ch := dc.pubsub.Channel()
    for {
        select {
        case <-ctx.Done():
            return
        case msg := <-ch:
            // Другой инстанс попросил инвалидировать ключ
            dc.l1.Del(msg.Payload)
        }
    }
}

// Инвалидация: удаляем из L1, L2, и уведомляем все инстансы
func (dc *DistributedCache[V]) Invalidate(ctx context.Context, key string) {
    dc.l1.Del(key)
    dc.l2.Del(ctx, key)
    // Уведомляем другие инстансы удалить из своих L1
    dc.l2.Publish(ctx, dc.channel, key)
}

func (dc *DistributedCache[V]) Close() {
    dc.cancelCtx()
    dc.pubsub.Close()
}
```

> ⚠️ **Pub/Sub ненадёжен**: Если инстанс временно отключился от Redis, он пропустит сообщения об инвалидации. Комбинируйте Pub/Sub с **коротким TTL на L1** (1-5 минут) — даже если инвалидация не дошла, данные обновятся при истечении TTL.

---

## Production Concerns

### Прогрев кэша (Cache Warming)

После деплоя или рестарта кэш пуст. Первые запросы попадают сразу в БД, что может вызвать пик нагрузки.

**C# — IHostedService**:
```csharp
// C#: прогрев кэша при старте
public class CacheWarmingService : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        var popularUsers = await _db.Users.OrderByDescending(u => u.LastLogin)
            .Take(1000).ToListAsync(ct);
        foreach (var user in popularUsers)
            await _cache.SetAsync($"user:{user.Id}", user);
    }
}
```

**Go — errgroup для параллельного прогрева**:
```go
func WarmCache(ctx context.Context, rdb *redis.Client, repo UserRepository) error {
    // Загружаем популярные данные
    users, err := repo.FindMostActive(ctx, 1000)
    if err != nil {
        return fmt.Errorf("загрузка пользователей: %w", err)
    }

    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(20) // параллельность: 20 горутин

    for _, user := range users {
        user := user // capture loop variable
        g.Go(func() error {
            key := fmt.Sprintf("user:%s", user.ID)
            data, _ := json.Marshal(user)
            return rdb.Set(ctx, key, data, 30*time.Minute).Err()
        })
    }

    return g.Wait()
}

// Вызов при старте приложения
func main() {
    // ... инициализация ...

    // Прогрев кэша в фоне (не блокируем старт сервера)
    go func() {
        ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
        defer cancel()
        if err := WarmCache(ctx, rdb, repo); err != nil {
            slog.Error("ошибка прогрева кэша", "error", err)
        } else {
            slog.Info("кэш прогрет", "keys", 1000)
        }
    }()

    // Сервер начинает работать сразу
    server.ListenAndServe()
}
```

### Мониторинг

Кэш без мониторинга — это чёрный ящик. Ключевые метрики:

| Метрика | Описание | Тревога |
|---------|----------|---------|
| **Hit Rate** | % запросов из кэша | < 80% — проблема |
| **Miss Rate** | % промахов | > 20% — расследовать |
| **Eviction Rate** | Частота вытеснений | Резкий рост — мало памяти |
| **Latency P99** | Задержка 99-го перцентиля | > 5ms для Redis |
| **Pool Usage** | Использование пула соединений | > 80% — увеличить пул |
| **Memory Usage** | Объём памяти кэша | Приближение к лимиту |

**Prometheus метрики для кэша**:

```go
import "github.com/prometheus/client_golang/prometheus"

var (
    cacheOps = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "cache_operations_total",
            Help: "Количество операций кэша",
        },
        []string{"operation", "result"}, // operation: get/set/del, result: hit/miss/error
    )

    cacheLatency = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "cache_operation_duration_seconds",
            Help:    "Латентность операций кэша",
            Buckets: prometheus.DefBuckets,
        },
        []string{"operation", "level"}, // level: l1/l2
    )

    cacheSize = prometheus.NewGauge(prometheus.GaugeOpts{
        Name: "cache_entries_total",
        Help: "Количество записей в кэше",
    })
)

func init() {
    prometheus.MustRegister(cacheOps, cacheLatency, cacheSize)
}

// Middleware для метрик
func (c *InstrumentedCache) Get(ctx context.Context, key string) ([]byte, error) {
    start := time.Now()
    defer func() {
        cacheLatency.WithLabelValues("get", "l2").Observe(time.Since(start).Seconds())
    }()

    val, err := c.inner.Get(ctx, key).Bytes()
    if err == redis.Nil {
        cacheOps.WithLabelValues("get", "miss").Inc()
        return nil, err
    }
    if err != nil {
        cacheOps.WithLabelValues("get", "error").Inc()
        return nil, err
    }

    cacheOps.WithLabelValues("get", "hit").Inc()
    return val, nil
}
```

> 💡 **Правило**: Hit rate ниже 80% означает, что кэш не приносит достаточной пользы. Проверьте: правильные ли данные кэшируются? Достаточен ли TTL? Не слишком ли маленький размер кэша?

### Сериализация

В C# `IDistributedCache` работает с `byte[]`, и вы обычно используете `System.Text.Json`. В Go для кэширования есть несколько вариантов:

| Формат | Библиотека | Скорость | Размер | Читаемость |
|--------|-----------|----------|--------|------------|
| **JSON** | `encoding/json` | Средняя | Большой | Да |
| **MessagePack** | `vmihailenco/msgpack` | Быстрая | Компактный | Нет |
| **Protocol Buffers** | `google.golang.org/protobuf` | Быстрая | Компактный | Нет |

**JSON** — простой, но медленный:
```go
import "encoding/json"

func cacheSet(ctx context.Context, rdb *redis.Client, key string, val any, ttl time.Duration) error {
    data, err := json.Marshal(val)
    if err != nil {
        return err
    }
    return rdb.Set(ctx, key, data, ttl).Err()
}
```

**MessagePack** — оптимальный баланс скорости и размера:
```go
import "github.com/vmihailenco/msgpack/v5"

func cacheSetMsgpack(ctx context.Context, rdb *redis.Client, key string, val any, ttl time.Duration) error {
    data, err := msgpack.Marshal(val)
    if err != nil {
        return err
    }
    return rdb.Set(ctx, key, data, ttl).Err()
}

func cacheGetMsgpack[V any](ctx context.Context, rdb *redis.Client, key string) (V, error) {
    var val V
    data, err := rdb.Get(ctx, key).Bytes()
    if err != nil {
        return val, err
    }
    err = msgpack.Unmarshal(data, &val)
    return val, err
}
```

**Примерные характеристики** (типичный объект User):

| Формат | Размер | Marshal | Unmarshal |
|--------|--------|---------|-----------|
| JSON | 195 bytes | 800 ns | 1200 ns |
| MessagePack | 128 bytes | 350 ns | 450 ns |
| Protobuf | 98 bytes | 200 ns | 280 ns |

> 💡 **Рекомендация**: Для большинства случаев **MessagePack** — лучший выбор. Он в ~2x быстрее JSON, на ~35% компактнее, и не требует генерации кода (в отличие от Protobuf). Protobuf выбирайте, если данные уже определены через `.proto` файлы.

### Connection Pooling и Resilience

go-redis имеет встроенный пул соединений. Мониторинг пула:

```go
// Статистика пула соединений
stats := rdb.PoolStats()
fmt.Printf("Hits: %d, Misses: %d, Timeouts: %d\n",
    stats.Hits, stats.Misses, stats.Timeouts)
fmt.Printf("Total: %d, Idle: %d, Stale: %d\n",
    stats.TotalConns, stats.IdleConns, stats.StaleConns)
```

**Circuit Breaker** для Redis (подробнее о паттерне — в [разделе 4.1](./01_production_postgresql.md)):

```go
import "github.com/sony/gobreaker/v2"

type ResilientCache struct {
    rdb *redis.Client
    cb  *gobreaker.CircuitBreaker[[]byte]
}

func NewResilientCache(rdb *redis.Client) *ResilientCache {
    cb := gobreaker.NewCircuitBreaker[[]byte](gobreaker.Settings{
        Name:        "redis-cache",
        MaxRequests: 5,                 // запросов в half-open
        Interval:    10 * time.Second,  // сброс счётчиков
        Timeout:     30 * time.Second,  // время в open state
        ReadyToTrip: func(counts gobreaker.Counts) bool {
            return counts.ConsecutiveFailures > 5
        },
    })

    return &ResilientCache{rdb: rdb, cb: cb}
}

func (rc *ResilientCache) Get(ctx context.Context, key string) ([]byte, error) {
    result, err := rc.cb.Execute(func() ([]byte, error) {
        return rc.rdb.Get(ctx, key).Bytes()
    })
    if err != nil {
        // Circuit breaker open или Redis недоступен
        // Graceful degradation — идём напрямую в БД
        return nil, err
    }
    return result, nil
}
```

> 💡 **Graceful degradation**: Когда Redis недоступен, приложение должно продолжать работать, обращаясь напрямую к БД. Это медленнее, но лучше, чем ошибки 500.

### Память и GC

Влияние разных подходов к кэшированию на Go GC (подробнее — [раздел 2.3](../part2-advanced/03_gc.md)):

| Подход | 1M записей | GC Pause | Почему |
|--------|-----------|----------|--------|
| `map[string]*Object` | ~500 MB | 10-50 ms | Миллионы указателей сканируются GC |
| `map[string]Object` (по значению) | ~400 MB | 5-20 ms | Меньше указателей, но string — это указатель |
| bigcache | ~300 MB | < 1 ms | `map[uint64]uint32` — нет указателей |
| ristretto | ~350 MB | 3-10 ms | Шардирование снижает конкуренцию |
| Redis (external) | 0 MB в Go | 0 ms | Данные в отдельном процессе |

```go
// Мониторинг GC для оценки влияния кэша
import "runtime"

func logGCStats() {
    var stats runtime.MemStats
    runtime.ReadMemStats(&stats)

    slog.Info("memory stats",
        "alloc_mb", stats.Alloc/1024/1024,
        "sys_mb", stats.Sys/1024/1024,
        "gc_pause_ns", stats.PauseNs[(stats.NumGC+255)%256],
        "num_gc", stats.NumGC,
    )
}
```

> ⚠️ **Если GC pause > 5ms** и у вас большой in-memory кэш — рассмотрите переход на bigcache или вынос данных в Redis.

### OpenTelemetry Instrumentation

go-redis имеет официальный пакет для OpenTelemetry:

```bash
go get github.com/redis/go-redis/extra/redisotel/v9
```

```go
import "github.com/redis/go-redis/extra/redisotel/v9"

rdb := redis.NewClient(&redis.Options{
    Addr: "localhost:6379",
})

// Включаем tracing
if err := redisotel.InstrumentTracing(rdb); err != nil {
    panic(err)
}

// Включаем метрики
if err := redisotel.InstrumentMetrics(rdb); err != nil {
    panic(err)
}

// Теперь все операции Redis автоматически создают spans
// и экспортируют метрики в OpenTelemetry collector
```

Подробнее об OpenTelemetry — в [разделе 4.5](./05_observability.md).

---

## Практические примеры

### Пример 1: Production-Ready Redis Cache Layer

Полноценный cache-сервис с generics, msgpack сериализацией, Prometheus метриками и graceful degradation.

```go
package cache

import (
    "context"
    "errors"
    "fmt"
    "log/slog"
    "time"

    "github.com/prometheus/client_golang/prometheus"
    "github.com/redis/go-redis/v9"
    "github.com/vmihailenco/msgpack/v5"
)

var ErrCacheMiss = errors.New("cache miss")

// Метрики
var (
    opsTotal = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "cache_operations_total",
            Help: "Total cache operations",
        },
        []string{"op", "result"},
    )
    opDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "cache_operation_duration_seconds",
            Help:    "Cache operation duration",
            Buckets: []float64{.0001, .0005, .001, .005, .01, .05, .1},
        },
        []string{"op"},
    )
)

func init() {
    prometheus.MustRegister(opsTotal, opDuration)
}

// RedisCache — production-ready кэш с generics
type RedisCache[V any] struct {
    rdb    *redis.Client
    prefix string
    logger *slog.Logger
}

func NewRedisCache[V any](rdb *redis.Client, prefix string, logger *slog.Logger) *RedisCache[V] {
    return &RedisCache[V]{
        rdb:    rdb,
        prefix: prefix,
        logger: logger,
    }
}

func (c *RedisCache[V]) key(id string) string {
    return fmt.Sprintf("%s:%s", c.prefix, id)
}

func (c *RedisCache[V]) Get(ctx context.Context, id string) (V, error) {
    start := time.Now()
    defer func() {
        opDuration.WithLabelValues("get").Observe(time.Since(start).Seconds())
    }()

    var zero V
    data, err := c.rdb.Get(ctx, c.key(id)).Bytes()
    if err == redis.Nil {
        opsTotal.WithLabelValues("get", "miss").Inc()
        return zero, ErrCacheMiss
    }
    if err != nil {
        opsTotal.WithLabelValues("get", "error").Inc()
        c.logger.Warn("cache get error", "key", c.key(id), "error", err)
        return zero, ErrCacheMiss // graceful degradation
    }

    var val V
    if err := msgpack.Unmarshal(data, &val); err != nil {
        opsTotal.WithLabelValues("get", "error").Inc()
        c.logger.Warn("cache unmarshal error", "key", c.key(id), "error", err)
        // Удаляем битые данные
        c.rdb.Del(ctx, c.key(id))
        return zero, ErrCacheMiss
    }

    opsTotal.WithLabelValues("get", "hit").Inc()
    return val, nil
}

func (c *RedisCache[V]) Set(ctx context.Context, id string, val V, ttl time.Duration) {
    start := time.Now()
    defer func() {
        opDuration.WithLabelValues("set").Observe(time.Since(start).Seconds())
    }()

    data, err := msgpack.Marshal(val)
    if err != nil {
        opsTotal.WithLabelValues("set", "error").Inc()
        c.logger.Warn("cache marshal error", "key", c.key(id), "error", err)
        return
    }

    if err := c.rdb.Set(ctx, c.key(id), data, ttl).Err(); err != nil {
        opsTotal.WithLabelValues("set", "error").Inc()
        c.logger.Warn("cache set error", "key", c.key(id), "error", err)
        return
    }

    opsTotal.WithLabelValues("set", "ok").Inc()
}

func (c *RedisCache[V]) Delete(ctx context.Context, id string) {
    if err := c.rdb.Del(ctx, c.key(id)).Err(); err != nil {
        c.logger.Warn("cache delete error", "key", c.key(id), "error", err)
    }
}

// GetOrLoad — Cache-Aside + singleflight в одном методе
func (c *RedisCache[V]) GetOrLoad(
    ctx context.Context,
    id string,
    ttl time.Duration,
    loader func(ctx context.Context) (V, error),
) (V, error) {
    // 1. Пробуем кэш
    val, err := c.Get(ctx, id)
    if err == nil {
        return val, nil
    }

    // 2. Загружаем из источника
    val, err = loader(ctx)
    if err != nil {
        return val, err
    }

    // 3. Кэшируем (не блокируя основной flow)
    c.Set(ctx, id, val, ttl)

    return val, nil
}
```

**Использование**:

```go
// Создание
userCache := cache.NewRedisCache[*User](rdb, "user", slog.Default())

// Cache-Aside
user, err := userCache.GetOrLoad(ctx, "123", 5*time.Minute, func(ctx context.Context) (*User, error) {
    return repo.FindByID(ctx, "123")
})
```

### Пример 2: Multi-Level Cache с singleflight

L1 (ristretto) + L2 (Redis) + singleflight + Pub/Sub инвалидация.

```go
package cache

import (
    "context"
    "encoding/json"
    "fmt"
    "log/slog"
    "time"

    "github.com/dgraph-io/ristretto/v2"
    "github.com/redis/go-redis/v9"
    "golang.org/x/sync/singleflight"
)

type TwoLevelCache[V any] struct {
    l1         *ristretto.Cache[string, V]
    l2         *redis.Client
    sf         singleflight.Group
    pubsub     *redis.PubSub
    channel    string
    ttlL1      time.Duration
    ttlL2      time.Duration
    logger     *slog.Logger
    cancelFunc context.CancelFunc
}

type TwoLevelConfig struct {
    L1NumCounters int64
    L1MaxCost     int64
    L1TTL         time.Duration
    L2TTL         time.Duration
    Channel       string
}

func NewTwoLevelCache[V any](
    rdb *redis.Client,
    cfg TwoLevelConfig,
    logger *slog.Logger,
) (*TwoLevelCache[V], error) {
    l1, err := ristretto.NewCache(&ristretto.Config[string, V]{
        NumCounters: cfg.L1NumCounters,
        MaxCost:     cfg.L1MaxCost,
        BufferItems: 64,
    })
    if err != nil {
        return nil, fmt.Errorf("создание ristretto cache: %w", err)
    }

    ctx, cancel := context.WithCancel(context.Background())

    c := &TwoLevelCache[V]{
        l1:         l1,
        l2:         rdb,
        channel:    cfg.Channel,
        ttlL1:      cfg.L1TTL,
        ttlL2:      cfg.L2TTL,
        logger:     logger,
        cancelFunc: cancel,
    }

    // Подписка на инвалидации от других инстансов
    c.pubsub = rdb.Subscribe(ctx, cfg.Channel)
    go c.listenInvalidations(ctx)

    return c, nil
}

func (c *TwoLevelCache[V]) Get(
    ctx context.Context,
    key string,
    loader func(ctx context.Context) (V, error),
) (V, error) {
    // L1 — наносекунды
    if val, ok := c.l1.Get(key); ok {
        return val, nil
    }

    // singleflight — дедупликация конкурентных запросов
    result, err, _ := c.sf.Do(key, func() (interface{}, error) {
        // L2 — микросекунды
        data, err := c.l2.Get(ctx, key).Bytes()
        if err == nil {
            var val V
            if err := json.Unmarshal(data, &val); err == nil {
                c.l1.SetWithTTL(key, val, 1, c.ttlL1)
                return val, nil
            }
        }

        // Загрузка из источника — миллисекунды
        val, err := loader(ctx)
        if err != nil {
            return val, err
        }

        // Заполняем оба уровня
        c.l1.SetWithTTL(key, val, 1, c.ttlL1)
        if data, err := json.Marshal(val); err == nil {
            c.l2.Set(ctx, key, data, c.ttlL2)
        }

        return val, nil
    })

    if err != nil {
        var zero V
        return zero, err
    }
    return result.(V), nil
}

func (c *TwoLevelCache[V]) Invalidate(ctx context.Context, key string) {
    c.l1.Del(key)
    c.l2.Del(ctx, key)
    // Уведомляем другие инстансы
    c.l2.Publish(ctx, c.channel, key)
}

func (c *TwoLevelCache[V]) listenInvalidations(ctx context.Context) {
    ch := c.pubsub.Channel()
    for {
        select {
        case <-ctx.Done():
            return
        case msg := <-ch:
            if msg != nil {
                c.l1.Del(msg.Payload)
                c.logger.Debug("L1 invalidated by remote",
                    "key", msg.Payload)
            }
        }
    }
}

func (c *TwoLevelCache[V]) Close() {
    c.cancelFunc()
    c.pubsub.Close()
    c.l1.Close()
}
```

**Использование**:

```go
cache, err := NewTwoLevelCache[*Product](rdb, TwoLevelConfig{
    L1NumCounters: 100_000,
    L1MaxCost:     50 << 20, // 50 MB
    L1TTL:         2 * time.Minute,
    L2TTL:         15 * time.Minute,
    Channel:       "cache:invalidate:products",
}, slog.Default())
defer cache.Close()

// Чтение с автозагрузкой
product, err := cache.Get(ctx, "product:42", func(ctx context.Context) (*Product, error) {
    return productRepo.FindByID(ctx, 42)
})

// Инвалидация при обновлении (все инстансы получат уведомление)
cache.Invalidate(ctx, "product:42")
```

### Пример 3: Session Storage с Redis

HTTP сессии в Redis — аналог ASP.NET Core Distributed Session.

```go
package session

import (
    "context"
    "crypto/rand"
    "encoding/hex"
    "encoding/json"
    "fmt"
    "net/http"
    "time"

    "github.com/redis/go-redis/v9"
)

const (
    cookieName = "session_id"
    keyPrefix  = "session:"
    defaultTTL = 30 * time.Minute
)

// Session — данные сессии
type Session struct {
    ID   string
    Data map[string]any
}

// Store — хранилище сессий в Redis
type Store struct {
    rdb *redis.Client
    ttl time.Duration
}

func NewStore(rdb *redis.Client) *Store {
    return &Store{rdb: rdb, ttl: defaultTTL}
}

func (s *Store) generateID() string {
    b := make([]byte, 16)
    rand.Read(b)
    return hex.EncodeToString(b)
}

func (s *Store) Get(ctx context.Context, sessionID string) (*Session, error) {
    key := keyPrefix + sessionID
    data, err := s.rdb.Get(ctx, key).Bytes()
    if err == redis.Nil {
        return nil, nil // сессия не найдена
    }
    if err != nil {
        return nil, fmt.Errorf("получение сессии: %w", err)
    }

    var sessionData map[string]any
    if err := json.Unmarshal(data, &sessionData); err != nil {
        return nil, fmt.Errorf("десериализация сессии: %w", err)
    }

    // Продлеваем TTL (sliding expiration)
    s.rdb.Expire(ctx, key, s.ttl)

    return &Session{ID: sessionID, Data: sessionData}, nil
}

func (s *Store) Save(ctx context.Context, session *Session) error {
    key := keyPrefix + session.ID
    data, err := json.Marshal(session.Data)
    if err != nil {
        return fmt.Errorf("сериализация сессии: %w", err)
    }
    return s.rdb.Set(ctx, key, data, s.ttl).Err()
}

func (s *Store) Destroy(ctx context.Context, sessionID string) error {
    return s.rdb.Del(ctx, keyPrefix+sessionID).Err()
}

// Middleware — HTTP middleware для работы с сессиями
func Middleware(store *Store) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            var session *Session

            // Читаем session ID из cookie
            cookie, err := r.Cookie(cookieName)
            if err == nil {
                session, _ = store.Get(r.Context(), cookie.Value)
            }

            // Создаём новую сессию если нет существующей
            if session == nil {
                session = &Session{
                    ID:   store.generateID(),
                    Data: make(map[string]any),
                }
            }

            // Устанавливаем cookie
            http.SetCookie(w, &http.Cookie{
                Name:     cookieName,
                Value:    session.ID,
                Path:     "/",
                HttpOnly: true,
                Secure:   true,
                SameSite: http.SameSiteLaxMode,
                MaxAge:   int(defaultTTL.Seconds()),
            })

            // Добавляем сессию в context
            ctx := context.WithValue(r.Context(), sessionKey, session)

            // ResponseWriter wrapper для сохранения сессии после ответа
            sw := &sessionWriter{
                ResponseWriter: w,
                session:        session,
                store:          store,
                ctx:            ctx,
            }

            next.ServeHTTP(sw, r.WithContext(ctx))

            // Сохраняем сессию после обработки запроса
            if sw.modified {
                store.Save(ctx, session)
            }
        })
    }
}

type contextKeyType string

const sessionKey contextKeyType = "session"

// FromContext — получение сессии из context
func FromContext(ctx context.Context) *Session {
    session, _ := ctx.Value(sessionKey).(*Session)
    return session
}

type sessionWriter struct {
    http.ResponseWriter
    session  *Session
    store    *Store
    ctx      context.Context
    modified bool
}
```

**Использование с chi router**:

```go
func main() {
    rdb := redis.NewClient(&redis.Options{Addr: "localhost:6379"})
    store := session.NewStore(rdb)

    r := chi.NewRouter()
    r.Use(session.Middleware(store))

    r.Post("/login", func(w http.ResponseWriter, r *http.Request) {
        sess := session.FromContext(r.Context())
        sess.Data["user_id"] = "123"
        sess.Data["logged_in"] = true
        // Сессия автоматически сохранится в Redis

        w.Write([]byte("OK"))
    })

    r.Get("/profile", func(w http.ResponseWriter, r *http.Request) {
        sess := session.FromContext(r.Context())
        userID, ok := sess.Data["user_id"].(string)
        if !ok {
            http.Error(w, "not authenticated", http.StatusUnauthorized)
            return
        }
        fmt.Fprintf(w, "User: %s", userID)
    })

    http.ListenAndServe(":8080", r)
}
```

---

## Чек-лист

После изучения этого раздела вы должны уметь:

### Redis
- [ ] Подключить go-redis v9 с production-конфигурацией (пул, таймауты, TLS)
- [ ] Выполнять основные операции (strings, hashes, lists, sets, sorted sets)
- [ ] Обрабатывать `redis.Nil` как "ключ не найден" (не как ошибку)
- [ ] Использовать Pipeline для батч-операций
- [ ] Использовать TxPipeline + Watch для оптимистичных транзакций
- [ ] Настроить Redis Cluster или Sentinel для высокой доступности
- [ ] Реализовать распределённые блокировки через redsync

### In-Memory кэширование
- [ ] Выбрать подходящую библиотеку для вашего сценария
- [ ] Понимать влияние разных библиотек на Go GC
- [ ] Использовать ristretto для оптимального hit ratio
- [ ] Использовать bigcache для миллионов записей (GC-friendly)
- [ ] Знать когда `sync.Map` подходит, а когда нет

### Паттерны
- [ ] Реализовать Cache-Aside (lazy loading)
- [ ] Предотвратить cache stampede с помощью `singleflight`
- [ ] Использовать jittered TTL для предотвращения thundering herd
- [ ] Выбрать стратегию инвалидации (TTL, event, version-based)
- [ ] Реализовать multi-level кэш (L1 in-memory + L2 Redis)

### Production
- [ ] Мониторить hit/miss rate через Prometheus
- [ ] Реализовать graceful degradation при недоступности Redis
- [ ] Выбрать формат сериализации (JSON / msgpack / protobuf)
- [ ] Настроить cache warming при деплое
- [ ] Инструментировать Redis через OpenTelemetry

---

## Следующие шаги

Переходите к [4.3 Очереди сообщений](./03_message_queues.md) — Kafka, RabbitMQ, NATS, Redis Streams.

---

**Вопросы?** Откройте issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Назад: 4.1 Production PostgreSQL](./01_production_postgresql.md) | [Вперёд: 4.3 Очереди сообщений →](./03_message_queues.md)
