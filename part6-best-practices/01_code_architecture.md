# 6.1 Код и архитектура

## Содержание

- [Введение](#%D0%B2%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5)
  - [Enterprise C# mindset vs Go mindset](#enterprise-c-mindset-vs-go-mindset)
  - [Что вы узнаете](#%D1%87%D1%82%D0%BE-%D0%B2%D1%8B-%D1%83%D0%B7%D0%BD%D0%B0%D0%B5%D1%82%D0%B5)
- [Accept Interfaces, Return Structs](#accept-interfaces-return-structs)
  - [Принцип и мотивация](#%D0%BF%D1%80%D0%B8%D0%BD%D1%86%D0%B8%D0%BF-%D0%B8-%D0%BC%D0%BE%D1%82%D0%B8%D0%B2%D0%B0%D1%86%D0%B8%D1%8F)
  - [C# подход: интерфейсы везде](#c-%D0%BF%D0%BE%D0%B4%D1%85%D0%BE%D0%B4-%D0%B8%D0%BD%D1%82%D0%B5%D1%80%D1%84%D0%B5%D0%B9%D1%81%D1%8B-%D0%B2%D0%B5%D0%B7%D0%B4%D0%B5)
  - [Go подход: гибкость на входе, конкретность на выходе](#go-%D0%BF%D0%BE%D0%B4%D1%85%D0%BE%D0%B4-%D0%B3%D0%B8%D0%B1%D0%BA%D0%BE%D1%81%D1%82%D1%8C-%D0%BD%D0%B0-%D0%B2%D1%85%D0%BE%D0%B4%D0%B5-%D0%BA%D0%BE%D0%BD%D0%BA%D1%80%D0%B5%D1%82%D0%BD%D0%BE%D1%81%D1%82%D1%8C-%D0%BD%D0%B0-%D0%B2%D1%8B%D1%85%D0%BE%D0%B4%D0%B5)
  - [Когда использовать интерфейсы на входе](#%D0%BA%D0%BE%D0%B3%D0%B4%D0%B0-%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D1%8C-%D0%B8%D0%BD%D1%82%D0%B5%D1%80%D1%84%D0%B5%D0%B9%D1%81%D1%8B-%D0%BD%D0%B0-%D0%B2%D1%85%D0%BE%D0%B4%D0%B5)
  - [Когда нарушать правило](#%D0%BA%D0%BE%D0%B3%D0%B4%D0%B0-%D0%BD%D0%B0%D1%80%D1%83%D1%88%D0%B0%D1%82%D1%8C-%D0%BF%D1%80%D0%B0%D0%B2%D0%B8%D0%BB%D0%BE)
  - [Сравнительная таблица](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F-%D1%82%D0%B0%D0%B1%D0%BB%D0%B8%D1%86%D0%B0)
- [Маленькие интерфейсы](#%D0%BC%D0%B0%D0%BB%D0%B5%D0%BD%D1%8C%D0%BA%D0%B8%D0%B5-%D0%B8%D0%BD%D1%82%D0%B5%D1%80%D1%84%D0%B5%D0%B9%D1%81%D1%8B)
  - [ISP: теория vs практика](#isp-%D1%82%D0%B5%D0%BE%D1%80%D0%B8%D1%8F-vs-%D0%BF%D1%80%D0%B0%D0%BA%D1%82%D0%B8%D0%BA%D0%B0)
  - [Почему в Go маленькие интерфейсы — норма](#%D0%BF%D0%BE%D1%87%D0%B5%D0%BC%D1%83-%D0%B2-go-%D0%BC%D0%B0%D0%BB%D0%B5%D0%BD%D1%8C%D0%BA%D0%B8%D0%B5-%D0%B8%D0%BD%D1%82%D0%B5%D1%80%D1%84%D0%B5%D0%B9%D1%81%D1%8B--%D0%BD%D0%BE%D1%80%D0%BC%D0%B0)
  - [Стандартная библиотека как эталон](#%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D0%B0%D1%8F-%D0%B1%D0%B8%D0%B1%D0%BB%D0%B8%D0%BE%D1%82%D0%B5%D0%BA%D0%B0-%D0%BA%D0%B0%D0%BA-%D1%8D%D1%82%D0%B0%D0%BB%D0%BE%D0%BD)
  - [Consumer-side interface definition](#consumer-side-interface-definition)
  - [Композиция интерфейсов](#%D0%BA%D0%BE%D0%BC%D0%BF%D0%BE%D0%B7%D0%B8%D1%86%D0%B8%D1%8F-%D0%B8%D0%BD%D1%82%D0%B5%D1%80%D1%84%D0%B5%D0%B9%D1%81%D0%BE%D0%B2)
  - [Анти-паттерны](#%D0%B0%D0%BD%D1%82%D0%B8-%D0%BF%D0%B0%D1%82%D1%82%D0%B5%D1%80%D0%BD%D1%8B)
  - [Сравнительная таблица](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F-%D1%82%D0%B0%D0%B1%D0%BB%D0%B8%D1%86%D0%B0-1)
- [Composition over Inheritance](#composition-over-inheritance)
  - [Философия: Has-a вместо Is-a](#%D1%84%D0%B8%D0%BB%D0%BE%D1%81%D0%BE%D1%84%D0%B8%D1%8F-has-a-%D0%B2%D0%BC%D0%B5%D1%81%D1%82%D0%BE-is-a)
  - [Embedding в Go](#embedding-%D0%B2-go)
  - [Forwarding vs Embedding](#forwarding-vs-embedding)
  - [Decorator pattern](#decorator-pattern)
  - [Сравнительная таблица: паттерны](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F-%D1%82%D0%B0%D0%B1%D0%BB%D0%B8%D1%86%D0%B0-%D0%BF%D0%B0%D1%82%D1%82%D0%B5%D1%80%D0%BD%D1%8B)
- [Explicit is Better than Implicit](#explicit-is-better-than-implicit)
  - [Философия явности](#%D1%84%D0%B8%D0%BB%D0%BE%D1%81%D0%BE%D1%84%D0%B8%D1%8F-%D1%8F%D0%B2%D0%BD%D0%BE%D1%81%D1%82%D0%B8)
  - [Конструкторы и инициализация](#%D0%BA%D0%BE%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D0%BE%D1%80%D1%8B-%D0%B8-%D0%B8%D0%BD%D0%B8%D1%86%D0%B8%D0%B0%D0%BB%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F)
  - [Functional Options Pattern](#functional-options-pattern)
  - [Сравнительная таблица](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F-%D1%82%D0%B0%D0%B1%D0%BB%D0%B8%D1%86%D0%B0-2)
- [Errors are Values](#errors-are-values)
  - [Философия](#%D1%84%D0%B8%D0%BB%D0%BE%D1%81%D0%BE%D1%84%D0%B8%D1%8F)
  - [Типичные ошибки C# разработчиков](#%D1%82%D0%B8%D0%BF%D0%B8%D1%87%D0%BD%D1%8B%D0%B5-%D0%BE%D1%88%D0%B8%D0%B1%D0%BA%D0%B8-c-%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%87%D0%B8%D0%BA%D0%BE%D0%B2)
  - [Quick Reference](#quick-reference)
- [Организация пакетов](#%D0%BE%D1%80%D0%B3%D0%B0%D0%BD%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-%D0%BF%D0%B0%D0%BA%D0%B5%D1%82%D0%BE%D0%B2)
  - [internal/ — ваш лучший друг](#internal--%D0%B2%D0%B0%D1%88-%D0%BB%D1%83%D1%87%D1%88%D0%B8%D0%B9-%D0%B4%D1%80%D1%83%D0%B3)
  - [Package по feature vs по layer](#package-%D0%BF%D0%BE-feature-vs-%D0%BF%D0%BE-layer)
  - [Cyclic imports](#cyclic-imports)
  - [Naming conventions](#naming-conventions)
- [Типичные ошибки C# разработчиков](#%D1%82%D0%B8%D0%BF%D0%B8%D1%87%D0%BD%D1%8B%D0%B5-%D0%BE%D1%88%D0%B8%D0%B1%D0%BA%D0%B8-c-%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%87%D0%B8%D0%BA%D0%BE%D0%B2-1)
  - [1. Overengineering](#1-overengineering)
  - [2. Getter/Setter для всего](#2-gettersetter-%D0%B4%D0%BB%D1%8F-%D0%B2%D1%81%D0%B5%D0%B3%D0%BE)
  - [3. Интерфейсы "на всякий случай"](#3-%D0%B8%D0%BD%D1%82%D0%B5%D1%80%D1%84%D0%B5%D0%B9%D1%81%D1%8B-%D0%BD%D0%B0-%D0%B2%D1%81%D1%8F%D0%BA%D0%B8%D0%B9-%D1%81%D0%BB%D1%83%D1%87%D0%B0%D0%B9)
  - [4. Panic вместо error](#4-panic-%D0%B2%D0%BC%D0%B5%D1%81%D1%82%D0%BE-error)
  - [5. Игнорирование context.Context](#5-%D0%B8%D0%B3%D0%BD%D0%BE%D1%80%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5-contextcontext)
  - [6. Неправильная работа с nil](#6-%D0%BD%D0%B5%D0%BF%D1%80%D0%B0%D0%B2%D0%B8%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F-%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%B0-%D1%81-nil)
  - [7. LINQ-стиль вместо простых циклов](#7-linq-%D1%81%D1%82%D0%B8%D0%BB%D1%8C-%D0%B2%D0%BC%D0%B5%D1%81%D1%82%D0%BE-%D0%BF%D1%80%D0%BE%D1%81%D1%82%D1%8B%D1%85-%D1%86%D0%B8%D0%BA%D0%BB%D0%BE%D0%B2)
  - [Сводная таблица](#%D1%81%D0%B2%D0%BE%D0%B4%D0%BD%D0%B0%D1%8F-%D1%82%D0%B0%D0%B1%D0%BB%D0%B8%D1%86%D0%B0)
- [API Design](#api-design)
  - [Экспорт и видимость](#%D1%8D%D0%BA%D1%81%D0%BF%D0%BE%D1%80%D1%82-%D0%B8-%D0%B2%D0%B8%D0%B4%D0%B8%D0%BC%D0%BE%D1%81%D1%82%D1%8C)
  - [Версионирование](#%D0%B2%D0%B5%D1%80%D1%81%D0%B8%D0%BE%D0%BD%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5)
  - [Обратная совместимость](#%D0%BE%D0%B1%D1%80%D0%B0%D1%82%D0%BD%D0%B0%D1%8F-%D1%81%D0%BE%D0%B2%D0%BC%D0%B5%D1%81%D1%82%D0%B8%D0%BC%D0%BE%D1%81%D1%82%D1%8C)
  - [Документирование API](#%D0%B4%D0%BE%D0%BA%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5-api)
  - [Сравнительная таблица](#%D1%81%D1%80%D0%B0%D0%B2%D0%BD%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F-%D1%82%D0%B0%D0%B1%D0%BB%D0%B8%D1%86%D0%B0-3)
- [Практические примеры](#%D0%BF%D1%80%D0%B0%D0%BA%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B5-%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80%D1%8B)
  - [Пример 1: Рефакторинг Repository](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-1-%D1%80%D0%B5%D1%84%D0%B0%D0%BA%D1%82%D0%BE%D1%80%D0%B8%D0%BD%D0%B3-repository)
  - [Пример 2: Миграция DI-сервиса](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-2-%D0%BC%D0%B8%D0%B3%D1%80%D0%B0%D1%86%D0%B8%D1%8F-di-%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D0%B0)
  - [Пример 3: Организация микросервиса](#%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80-3-%D0%BE%D1%80%D0%B3%D0%B0%D0%BD%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F-%D0%BC%D0%B8%D0%BA%D1%80%D0%BE%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D0%B0)

---

## Введение

В [разделе 1.3](../part1-basics/03_key_differences.md) мы познакомились с философскими отличиями Go от C#: простота вместо богатства возможностей, композиция вместо наследования, явность вместо магии. Этот раздел систематизирует **архитектурные принципы и идиомы**, которые делают Go-код идиоматичным.

> 💡 **Для C# разработчиков**: Переход на Go — это не просто изучение нового синтаксиса. Это **смена парадигмы мышления**. Многие паттерны, которые вы годами оттачивали в C#, в Go либо не нужны, либо реализуются принципиально иначе. Этот раздел поможет "разучиться" и научиться заново.

### Enterprise C# mindset vs Go mindset

| Аспект | C# (Enterprise) | Go |
|--------|-----------------|-----|
| **Абстракции** | Чем больше, тем лучше | Минимум необходимого |
| **DI-контейнер** | Обязателен | Не нужен (manual DI) |
| **Интерфейсы** | На каждый класс | Только когда нужен полиморфизм |
| **Наследование** | Основной инструмент переиспользования | Отсутствует (композиция) |
| **Conventions** | Магия фреймворка | Явный код |
| **Generics** | Активно используются | Только когда необходимы |
| **Сложность** | "Enterprise-ready" | "Simple is better than clever" |

### Что вы узнаете

- **Accept interfaces, return structs** — золотое правило Go
- **Маленькие интерфейсы** — почему 1-3 метода это идеал
- **Композиция** — как заменить наследование
- **Явность** — почему explicit лучше implicit
- **Организация пакетов** — структура production-ready проекта
- **Типичные ошибки** — чего избегать при переходе с C#

---

## Accept Interfaces, Return Structs

Это одно из самых важных правил проектирования в Go. Понимание этого принципа кардинально меняет подход к написанию кода.

### Принцип и мотивация

**Правило**: Функции должны **принимать интерфейсы** (когда нужен полиморфизм) и **возвращать конкретные типы** (структуры).

**Почему это работает**:
- **Гибкость на входе**: Вызывающий код может передать любую реализацию
- **Конкретность на выходе**: Вызывающий код получает полный API структуры
- **Тестируемость**: Легко подменить зависимость в тестах
- **Отсутствие over-abstraction**: Интерфейс создаётся только когда нужен

### C# подход: интерфейсы везде

В C# принято создавать интерфейс для каждого сервиса, даже если реализация одна:

```csharp
// C#: типичный Enterprise-стиль
public interface IUserRepository
{
    Task<User?> GetByIdAsync(int id);
    Task<User?> GetByEmailAsync(string email);
    Task<IEnumerable<User>> GetAllAsync();
    Task<User> CreateAsync(User user);
    Task UpdateAsync(User user);
    Task DeleteAsync(int id);
}

public interface IUserService
{
    Task<UserDto?> GetUserAsync(int id);
    Task<UserDto> CreateUserAsync(CreateUserRequest request);
    Task UpdateUserAsync(int id, UpdateUserRequest request);
    Task DeleteUserAsync(int id);
}

// Реализации
public class UserRepository : IUserRepository { ... }
public class UserService : IUserService
{
    private readonly IUserRepository _repository;
    private readonly ILogger<UserService> _logger;

    public UserService(IUserRepository repository, ILogger<UserService> logger)
    {
        _repository = repository;
        _logger = logger;
    }
    // ...
}

// Регистрация в DI
services.AddScoped<IUserRepository, UserRepository>();
services.AddScoped<IUserService, UserService>();
```

**Проблемы этого подхода**:
- Интерфейс создаётся "на всякий случай", даже если реализация одна
- DI-контейнер скрывает зависимости
- Сложно понять, какие методы реально используются

### Go подход: гибкость на входе, конкретность на выходе

```go
// Go: идиоматичный подход

// UserRepository — конкретная структура, НЕ интерфейс
type UserRepository struct {
    db *sql.DB
}

// NewUserRepository возвращает конкретный тип, не интерфейс
func NewUserRepository(db *sql.DB) *UserRepository {
    return &UserRepository{db: db}
}

func (r *UserRepository) GetByID(ctx context.Context, id int) (*User, error) {
    // ...
}

func (r *UserRepository) GetByEmail(ctx context.Context, email string) (*User, error) {
    // ...
}

func (r *UserRepository) Create(ctx context.Context, user *User) error {
    // ...
}

// UserService — конкретная структура
type UserService struct {
    repo   *UserRepository  // Конкретный тип, если не нужен полиморфизм
    logger *slog.Logger
}

// NewUserService возвращает конкретный тип
func NewUserService(repo *UserRepository, logger *slog.Logger) *UserService {
    return &UserService{
        repo:   repo,
        logger: logger,
    }
}

// main.go — явная инициализация
func main() {
    db, _ := sql.Open("postgres", os.Getenv("DATABASE_URL"))
    logger := slog.Default()

    repo := NewUserRepository(db)
    svc := NewUserService(repo, logger)
    // ...
}
```

**Преимущества**:
- Нет лишних абстракций — интерфейс появляется только когда нужен
- Зависимости явные — видно в конструкторе
- Полный API доступен — вызывающий код видит все методы

### Когда использовать интерфейсы на входе

Интерфейс нужен, когда:
1. **Тестирование** — нужно подменить зависимость в тестах
2. **Полиморфизм** — несколько реализаций в runtime
3. **Внешняя зависимость** — абстрагирование от внешнего API

```go
// Интерфейс для тестирования
type UserGetter interface {
    GetByID(ctx context.Context, id int) (*User, error)
}

// Сервис принимает интерфейс — можно подменить в тестах
type UserService struct {
    repo UserGetter  // Интерфейс, не конкретный тип
}

func NewUserService(repo UserGetter) *UserService {
    return &UserService{repo: repo}
}

// В тестах
type mockUserRepo struct {
    user *User
    err  error
}

func (m *mockUserRepo) GetByID(ctx context.Context, id int) (*User, error) {
    return m.user, m.err
}

func TestUserService_GetUser(t *testing.T) {
    mock := &mockUserRepo{
        user: &User{ID: 1, Name: "Test"},
    }
    svc := NewUserService(mock)
    // ...
}
```

### Когда нарушать правило

**1. Factory functions с множественными реализациями:**

```go
// Возвращаем интерфейс, когда конкретный тип определяется в runtime
type Storage interface {
    Save(key string, data []byte) error
    Load(key string) ([]byte, error)
}

func NewStorage(storageType string) Storage {
    switch storageType {
    case "s3":
        return &S3Storage{...}
    case "gcs":
        return &GCSStorage{...}
    default:
        return &FileStorage{...}
    }
}
```

**2. Библиотеки для внешнего использования:**

```go
// Публичный API библиотеки может возвращать интерфейс
// для сокрытия деталей реализации
type Client interface {
    Get(ctx context.Context, key string) (string, error)
    Set(ctx context.Context, key, value string) error
}

func NewClient(addr string) Client {
    return &client{addr: addr}
}
```

### Сравнительная таблица

| Аспект | C# | Go |
|--------|----|----|
| **Параметр функции** | Часто интерфейс | Интерфейс только для полиморфизма |
| **Возвращаемое значение** | Часто интерфейс | Конкретный тип (*Struct) |
| **Создание интерфейса** | Заранее, "на всякий случай" | Когда реально нужен |
| **Определение интерфейса** | Рядом с реализацией | Рядом с потребителем |
| **DI** | Через контейнер | Через конструкторы |

---

## Маленькие интерфейсы

### ISP: теория vs практика

Interface Segregation Principle (ISP) — один из принципов SOLID. И в C#, и в Go он важен. Разница в том, насколько язык **поощряет** его соблюдение.

**В C#** ISP — это принцип, которому нужно **осознанно следовать**. На практике он часто нарушается:

```csharp
// C#: типичный "жирный" интерфейс
// ISP нарушен, но код работает
public interface IUserRepository
{
    // CRUD
    Task<User?> GetByIdAsync(int id);
    Task<User?> GetByEmailAsync(string email);
    Task<IEnumerable<User>> GetAllAsync();
    Task<User> CreateAsync(User user);
    Task UpdateAsync(User user);
    Task DeleteAsync(int id);

    // Поиск
    Task<IEnumerable<User>> SearchAsync(string query);
    Task<IEnumerable<User>> GetByRoleAsync(string role);

    // Статистика
    Task<int> CountAsync();
    Task<int> CountActiveAsync();

    // Batch-операции
    Task CreateManyAsync(IEnumerable<User> users);
    Task DeleteManyAsync(IEnumerable<int> ids);
}

// Проблема: сервис использует только 2 метода, но зависит от всего интерфейса
public class UserProfileService
{
    private readonly IUserRepository _repository; // 12+ методов

    public async Task<UserProfile> GetProfile(int userId)
    {
        var user = await _repository.GetByIdAsync(userId); // использует 1 метод
        return MapToProfile(user);
    }
}
```

**Почему это происходит в C#**:
- DI-контейнер поощряет "один интерфейс на класс"
- Generic Repository паттерн с полным CRUD
- Привычка создавать интерфейс заранее
- Явная реализация (`class X : IY`) требует реализовать ВСЕ методы

### Почему в Go маленькие интерфейсы — норма

**В Go** маленькие интерфейсы — это **естественный результат дизайна языка**:

```go
// Go: интерфейс определяется там, где используется
// Только те методы, которые реально нужны

// В пакете profile — только то, что нужно ProfileService
type UserGetter interface {
    GetByID(ctx context.Context, id int) (*User, error)
}

type ProfileService struct {
    users UserGetter // 1 метод — достаточно
}

func (s *ProfileService) GetProfile(ctx context.Context, userID int) (*Profile, error) {
    user, err := s.users.GetByID(ctx, userID)
    if err != nil {
        return nil, fmt.Errorf("get user: %w", err)
    }
    return mapToProfile(user), nil
}

// В пакете admin — другой интерфейс
type UserLister interface {
    List(ctx context.Context, filter Filter) ([]*User, error)
    Count(ctx context.Context) (int, error)
}

type AdminService struct {
    users UserLister // 2 метода — достаточно
}
```

**Почему это естественно в Go**:
1. **Неявная реализация (duck typing)** — структура реализует интерфейс автоматически
2. **Определение у потребителя** — интерфейс создаётся там, где нужен
3. **Стандартная библиотека** — задаёт эталон (`io.Reader` — 1 метод)
4. **Нет DI-контейнера** — нет давления "один интерфейс на класс"

### Стандартная библиотека как эталон

Go stdlib — образец минималистичных интерфейсов:

```go
// io.Reader — 1 метод
type Reader interface {
    Read(p []byte) (n int, err error)
}

// io.Writer — 1 метод
type Writer interface {
    Write(p []byte) (n int, err error)
}

// io.Closer — 1 метод
type Closer interface {
    Close() error
}

// fmt.Stringer — 1 метод
type Stringer interface {
    String() string
}

// error — 1 метод
type error interface {
    Error() string
}

// sort.Interface — 3 метода (максимум для сложного поведения)
type Interface interface {
    Len() int
    Less(i, j int) bool
    Swap(i, j int)
}
```

> 💡 **Идиома Go**: Если интерфейс содержит больше 3 методов — это сигнал пересмотреть дизайн. Возможно, интерфейс делает слишком много.

### Consumer-side interface definition

Ключевое отличие от C#: **интерфейс определяется там, где он используется**, а не там, где реализуется.

```go
// ❌ C#-стиль: интерфейс рядом с реализацией
// package repository
type UserRepository interface {
    GetByID(ctx context.Context, id int) (*User, error)
    GetByEmail(ctx context.Context, email string) (*User, error)
    Create(ctx context.Context, user *User) error
    Update(ctx context.Context, user *User) error
    Delete(ctx context.Context, id int) error
    List(ctx context.Context) ([]*User, error)
    // ... ещё 10 методов
}

type userRepository struct { db *sql.DB }
// реализация...

// ✅ Go-стиль: интерфейс у потребителя
// package repository — только структура
type UserRepository struct { db *sql.DB }

func (r *UserRepository) GetByID(ctx context.Context, id int) (*User, error) { ... }
func (r *UserRepository) Create(ctx context.Context, user *User) error { ... }
// ... все методы

// package service — интерфейс определяется здесь
type userStore interface {
    GetByID(ctx context.Context, id int) (*User, error)
    Create(ctx context.Context, user *User) error
}

type Service struct {
    users userStore // только нужные методы
}

// package notification — свой интерфейс
type userGetter interface {
    GetByID(ctx context.Context, id int) (*User, error)
}

type Notifier struct {
    users userGetter // только 1 метод
}
```

**Преимущества consumer-side definition**:
- Каждый потребитель зависит только от того, что использует
- Легко тестировать — маленький интерфейс = простой mock
- Нет "interface pollution" — интерфейсы не экспортируются без необходимости

### Композиция интерфейсов

Маленькие интерфейсы легко комбинировать:

```go
// Базовые интерфейсы — по 1 методу
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type Closer interface {
    Close() error
}

// Композиция — встраивание интерфейсов
type ReadWriter interface {
    Reader
    Writer
}

type ReadCloser interface {
    Reader
    Closer
}

type WriteCloser interface {
    Writer
    Closer
}

type ReadWriteCloser interface {
    Reader
    Writer
    Closer
}

// Использование
func Copy(dst Writer, src Reader) (int64, error) {
    // работает с любыми Reader и Writer
}

func ProcessFile(rwc ReadWriteCloser) error {
    defer rwc.Close()
    // читаем, обрабатываем, пишем
}
```

### Анти-паттерны

**1. God Interface (общий для C# и Go)**

```go
// ❌ Слишком много методов
type UserService interface {
    GetByID(ctx context.Context, id int) (*User, error)
    GetByEmail(ctx context.Context, email string) (*User, error)
    Create(ctx context.Context, user *User) error
    Update(ctx context.Context, user *User) error
    Delete(ctx context.Context, id int) error
    List(ctx context.Context, filter Filter) ([]*User, error)
    Search(ctx context.Context, query string) ([]*User, error)
    Activate(ctx context.Context, id int) error
    Deactivate(ctx context.Context, id int) error
    ChangePassword(ctx context.Context, id int, pwd string) error
    ResetPassword(ctx context.Context, email string) error
    SendVerification(ctx context.Context, id int) error
    // ... ещё 20 методов
}

// ✅ Разбить на маленькие интерфейсы
type UserGetter interface {
    GetByID(ctx context.Context, id int) (*User, error)
}

type UserCreator interface {
    Create(ctx context.Context, user *User) error
}

type PasswordManager interface {
    ChangePassword(ctx context.Context, id int, pwd string) error
    ResetPassword(ctx context.Context, email string) error
}
```

**2. Interface just in case**

```go
// ❌ Интерфейс "на всякий случай" — единственная реализация
type Logger interface {
    Info(msg string, args ...any)
    Error(msg string, args ...any)
}

type logger struct { /* ... */ }

// ✅ Просто используй конкретный тип
type Logger struct { /* ... */ }

// Интерфейс создашь, когда понадобится вторая реализация или тесты
```

**3. Экспорт интерфейса без необходимости**

```go
// ❌ Экспортируем интерфейс для внутреннего использования
type UserRepository interface { // экспортирован (заглавная буква)
    GetByID(ctx context.Context, id int) (*User, error)
}

// ✅ Если интерфейс только для внутреннего использования — не экспортируй
type userRepository interface { // не экспортирован (строчная буква)
    GetByID(ctx context.Context, id int) (*User, error)
}
```

### Сравнительная таблица

| Аспект | C# (теория) | C# (практика) | Go |
|--------|-------------|---------------|-----|
| Размер интерфейса | 1-5 методов (ISP) | 10-20 методов | 1-3 метода |
| Определение | Рядом с реализацией | Рядом с реализацией | У потребителя |
| Создание | Заранее | Заранее | Когда нужен |
| Экспорт | Всегда public | Всегда public | По необходимости |
| Именование | `IUserRepository` | `IUserRepository` | `UserGetter` |
| Реализация | Явная (`: IInterface`) | Явная | Неявная (duck typing) |

---

## Composition over Inheritance

### Философия: Has-a вместо Is-a

Go не имеет классического наследования. Это **осознанное решение дизайнеров языка**, а не ограничение.

**C# мышление**: "Dog **is-a** Animal"
**Go мышление**: "Dog **has-a** AnimalBehavior"

```csharp
// C#: иерархия наследования
public abstract class Animal
{
    public string Name { get; set; }

    public virtual void Eat()
    {
        Console.WriteLine($"{Name} is eating");
    }

    public abstract void MakeSound();
}

public class Dog : Animal
{
    public override void MakeSound()
    {
        Console.WriteLine("Woof!");
    }

    public void Fetch()
    {
        Console.WriteLine($"{Name} is fetching");
    }
}

public class Cat : Animal
{
    public override void MakeSound()
    {
        Console.WriteLine("Meow!");
    }
}
```

```go
// Go: композиция через embedding
type Animal struct {
    Name string
}

func (a Animal) Eat() {
    fmt.Printf("%s is eating\n", a.Name)
}

type Dog struct {
    Animal // embedding — Dog "has" Animal
}

func (d Dog) MakeSound() {
    fmt.Println("Woof!")
}

func (d Dog) Fetch() {
    fmt.Printf("%s is fetching\n", d.Name)
}

type Cat struct {
    Animal // embedding
}

func (c Cat) MakeSound() {
    fmt.Println("Meow!")
}

// Использование
func main() {
    dog := Dog{Animal: Animal{Name: "Buddy"}}
    dog.Eat()       // метод Animal доступен напрямую
    dog.MakeSound() // метод Dog
    dog.Fetch()

    cat := Cat{Animal: Animal{Name: "Whiskers"}}
    cat.Eat()
    cat.MakeSound()
}
```

### Embedding в Go

**Embedding** — встраивание одной структуры в другую. Это не наследование, а композиция с "продвижением" методов.

```go
// Embedding структуры
type Logger struct {
    prefix string
}

func (l Logger) Log(msg string) {
    fmt.Printf("[%s] %s\n", l.prefix, msg)
}

func (l Logger) Error(msg string) {
    fmt.Printf("[%s] ERROR: %s\n", l.prefix, msg)
}

type Service struct {
    Logger // embedding
    name   string
}

func (s *Service) DoWork() {
    s.Log("starting work")  // метод Logger доступен напрямую
    // ... работа
    s.Log("work completed")
}

// Можно переопределить метод
func (s *Service) Error(msg string) {
    s.Logger.Error(fmt.Sprintf("[%s] %s", s.name, msg))
}

// Использование
func main() {
    svc := &Service{
        Logger: Logger{prefix: "SVC"},
        name:   "UserService",
    }
    svc.DoWork()
    svc.Error("something went wrong")
}
```

**Embedding интерфейса**:

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

// Embedding интерфейсов
type ReadWriter interface {
    Reader
    Writer
}

// Структура может встраивать интерфейс
type CountingWriter struct {
    io.Writer       // embedding интерфейса
    BytesWritten int
}

func (cw *CountingWriter) Write(p []byte) (n int, err error) {
    n, err = cw.Writer.Write(p) // вызов встроенного Writer
    cw.BytesWritten += n
    return
}
```

### Forwarding vs Embedding

**Embedding** — когда нужен доступ к методам встроенного типа напрямую:

```go
// Embedding: методы Logger доступны на Service
type Service struct {
    Logger
}

svc := &Service{Logger: Logger{prefix: "SVC"}}
svc.Log("message") // Logger.Log продвигается на Service
```

**Forwarding (делегирование)** — когда нужен контроль над вызовами:

```go
// Forwarding: явное делегирование
type Service struct {
    logger Logger // не embedding
}

func (s *Service) Log(msg string) {
    // Можем добавить логику
    s.logger.Log(fmt.Sprintf("[%s] %s", time.Now().Format(time.RFC3339), msg))
}

svc := &Service{logger: Logger{prefix: "SVC"}}
svc.Log("message") // вызывает наш метод
```

**Когда использовать что**:

| Сценарий | Embedding | Forwarding |
|----------|-----------|------------|
| Нужны все методы встроенного типа | ✅ | ❌ |
| Нужно изменить поведение некоторых методов | ⚠️ Можно, но осторожно | ✅ |
| Нужно скрыть некоторые методы | ❌ | ✅ |
| Несколько типов с одинаковыми методами | ⚠️ Конфликты | ✅ |
| Простота кода | ✅ | ❌ |

### Decorator pattern

В Go decorator реализуется через функции, принимающие и возвращающие интерфейс:

```go
// Интерфейс
type Handler interface {
    Handle(ctx context.Context, req Request) (Response, error)
}

// Конкретная реализация
type userHandler struct {
    service *UserService
}

func (h *userHandler) Handle(ctx context.Context, req Request) (Response, error) {
    // бизнес-логика
    return Response{}, nil
}

// Decorator: логирование
func WithLogging(h Handler, logger *slog.Logger) Handler {
    return &loggingHandler{next: h, logger: logger}
}

type loggingHandler struct {
    next   Handler
    logger *slog.Logger
}

func (h *loggingHandler) Handle(ctx context.Context, req Request) (Response, error) {
    h.logger.Info("handling request", "request", req)
    resp, err := h.next.Handle(ctx, req)
    if err != nil {
        h.logger.Error("request failed", "error", err)
    }
    return resp, err
}

// Decorator: метрики
func WithMetrics(h Handler, metrics *Metrics) Handler {
    return &metricsHandler{next: h, metrics: metrics}
}

type metricsHandler struct {
    next    Handler
    metrics *Metrics
}

func (h *metricsHandler) Handle(ctx context.Context, req Request) (Response, error) {
    start := time.Now()
    resp, err := h.next.Handle(ctx, req)
    h.metrics.RecordDuration(time.Since(start))
    if err != nil {
        h.metrics.IncrementErrors()
    }
    return resp, err
}

// Использование: композиция декораторов
func main() {
    handler := &userHandler{service: userService}

    // Оборачиваем в декораторы
    handler = WithLogging(handler, logger)
    handler = WithMetrics(handler, metrics)

    // Теперь каждый вызов логируется и измеряется
    resp, err := handler.Handle(ctx, req)
}
```

**Функциональный стиль** (для HTTP middleware):

```go
type Middleware func(http.Handler) http.Handler

func Logging(logger *slog.Logger) Middleware {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            logger.Info("request", "method", r.Method, "path", r.URL.Path)
            next.ServeHTTP(w, r)
        })
    }
}

func Recover() Middleware {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            defer func() {
                if err := recover(); err != nil {
                    http.Error(w, "Internal Server Error", 500)
                }
            }()
            next.ServeHTTP(w, r)
        })
    }
}

// Применение
handler := Logging(logger)(Recover()(myHandler))
```

### Сравнительная таблица: паттерны

| Паттерн | C# | Go |
|---------|----|----|
| **Наследование** | `class Child : Parent` | Embedding / Композиция |
| **Abstract class** | `abstract class Base` | Interface + struct |
| **Virtual methods** | `virtual` / `override` | Interface methods |
| **Template Method** | Base class + virtual methods | Functional options / Strategy |
| **Decorator** | Interface-based, DI | Function wrapping |
| **Mixin** | Multiple inheritance (нет), traits (нет) | Embedding + interfaces |

---

## Explicit is Better than Implicit

### Философия явности

Go следует принципу **"explicit is better than implicit"** (явное лучше неявного). Это означает:

- Нет магии — код делает то, что написано
- Нет скрытых зависимостей — всё передаётся явно
- Нет conventions — конфигурация через код
- Читаемость важнее краткости

> 💡 **Для C# разработчиков**: В .NET много "магии": DI-контейнер резолвит зависимости, Entity Framework отслеживает изменения, ASP.NET маршрутизирует по conventions. В Go всё явно — и это преимущество, а не недостаток.

### Конструкторы и инициализация

**C#: Скрытые зависимости через DI**

```csharp
// C#: зависимости скрыты в DI-контейнере
public class UserService
{
    private readonly IUserRepository _repository;
    private readonly ILogger<UserService> _logger;
    private readonly IEmailService _emailService;
    private readonly IOptions<UserServiceOptions> _options;

    // DI резолвит всё автоматически
    public UserService(
        IUserRepository repository,
        ILogger<UserService> logger,
        IEmailService emailService,
        IOptions<UserServiceOptions> options)
    {
        _repository = repository;
        _logger = logger;
        _emailService = emailService;
        _options = options;
    }
}

// Startup.cs — регистрация скрыта
services.AddScoped<IUserRepository, UserRepository>();
services.AddScoped<IEmailService, SendGridEmailService>();
services.Configure<UserServiceOptions>(Configuration.GetSection("UserService"));
services.AddScoped<UserService>();
```

**Go: Явные зависимости через конструкторы**

```go
// Go: все зависимости видны в конструкторе
type UserService struct {
    repo    *UserRepository
    logger  *slog.Logger
    email   *EmailService
    options UserServiceOptions
}

// Конструктор явно показывает все зависимости
func NewUserService(
    repo *UserRepository,
    logger *slog.Logger,
    email *EmailService,
    options UserServiceOptions,
) *UserService {
    return &UserService{
        repo:    repo,
        logger:  logger,
        email:   email,
        options: options,
    }
}

// main.go — инициализация явная
func main() {
    cfg := config.Load()

    db, _ := sql.Open("postgres", cfg.DatabaseURL)
    logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

    repo := repository.NewUserRepository(db)
    email := email.NewService(cfg.SendGridAPIKey)

    svc := service.NewUserService(repo, logger, email, cfg.UserService)
    // Все зависимости видны в одном месте
}
```

### Functional Options Pattern

Когда конструктор имеет много опциональных параметров, используется **Functional Options Pattern**:

```go
// Структура с опциями
type Server struct {
    host         string
    port         int
    timeout      time.Duration
    maxConns     int
    logger       *slog.Logger
    readTimeout  time.Duration
    writeTimeout time.Duration
}

// Option — функция, модифицирующая Server
type Option func(*Server)

// Функции-опции
func WithHost(host string) Option {
    return func(s *Server) {
        s.host = host
    }
}

func WithPort(port int) Option {
    return func(s *Server) {
        s.port = port
    }
}

func WithTimeout(d time.Duration) Option {
    return func(s *Server) {
        s.timeout = d
    }
}

func WithMaxConnections(n int) Option {
    return func(s *Server) {
        s.maxConns = n
    }
}

func WithLogger(l *slog.Logger) Option {
    return func(s *Server) {
        s.logger = l
    }
}

func WithReadTimeout(d time.Duration) Option {
    return func(s *Server) {
        s.readTimeout = d
    }
}

func WithWriteTimeout(d time.Duration) Option {
    return func(s *Server) {
        s.writeTimeout = d
    }
}

// Конструктор с variadic options
func NewServer(opts ...Option) *Server {
    // Значения по умолчанию
    s := &Server{
        host:         "localhost",
        port:         8080,
        timeout:      30 * time.Second,
        maxConns:     100,
        logger:       slog.Default(),
        readTimeout:  10 * time.Second,
        writeTimeout: 10 * time.Second,
    }

    // Применяем опции
    for _, opt := range opts {
        opt(s)
    }

    return s
}

// Использование — чистый, читаемый код
func main() {
    // С дефолтами
    server1 := NewServer()

    // С кастомными опциями
    server2 := NewServer(
        WithHost("0.0.0.0"),
        WithPort(9000),
        WithTimeout(60*time.Second),
        WithLogger(customLogger),
    )

    // Легко понять, что настроено
}
```

**Преимущества Functional Options**:
- Значения по умолчанию встроены
- Опции можно добавлять без breaking changes
- Код использования читаемый
- Опции можно комбинировать и переиспользовать

**Альтернатива: Config struct**

```go
// Для простых случаев — структура конфигурации
type ServerConfig struct {
    Host         string        `env:"HOST" envDefault:"localhost"`
    Port         int           `env:"PORT" envDefault:"8080"`
    Timeout      time.Duration `env:"TIMEOUT" envDefault:"30s"`
    MaxConns     int           `env:"MAX_CONNS" envDefault:"100"`
    ReadTimeout  time.Duration `env:"READ_TIMEOUT" envDefault:"10s"`
    WriteTimeout time.Duration `env:"WRITE_TIMEOUT" envDefault:"10s"`
}

func NewServer(cfg ServerConfig) *Server {
    return &Server{
        host:         cfg.Host,
        port:         cfg.Port,
        timeout:      cfg.Timeout,
        maxConns:     cfg.MaxConns,
        readTimeout:  cfg.ReadTimeout,
        writeTimeout: cfg.WriteTimeout,
    }
}

// Использование
cfg := ServerConfig{Port: 9000}  // остальное — дефолты
server := NewServer(cfg)
```

### Сравнительная таблица

| Аспект | C# (Implicit) | Go (Explicit) |
|--------|---------------|---------------|
| **DI** | Контейнер + `[Inject]` | Manual конструкторы |
| **Config** | `IOptions<T>` через DI | Config struct, явная передача |
| **Routing** | `[Route("api/[controller]")]` | Явная регистрация маршрутов |
| **Validation** | `[Required]`, `[StringLength]` | Явные функции валидации |
| **ORM mapping** | Conventions, Fluent API | Struct tags или явный mapping |
| **Middleware** | `app.UseXxx()` + conventions | Явное оборачивание handlers |
| **Опциональные параметры** | Named parameters, default values | Functional Options |

---

## Errors are Values

> 📖 **Подробно**: Этот раздел — краткое напоминание. Детальное изучение — в [разделе 2.5 Обработка ошибок](../part2-advanced/05_error_handling.md).

### Философия

В Go ошибки — это **значения**, а не исключения. Они явно возвращаются и явно проверяются.

```go
// Go: ошибка — часть возвращаемого значения
func GetUser(id int) (*User, error) {
    user, err := db.QueryUser(id)
    if err != nil {
        return nil, fmt.Errorf("get user %d: %w", id, err)
    }
    return user, nil
}

// Вызывающий код ОБЯЗАН обработать ошибку
user, err := GetUser(42)
if err != nil {
    // обработка ошибки
    return err
}
// использование user
```

### Типичные ошибки C# разработчиков

**1. Использование panic вместо error**

```go
// ❌ C#-мышление: "выбросить исключение"
func GetUser(id int) *User {
    user, err := db.QueryUser(id)
    if err != nil {
        panic(err) // НЕТ! Panic — не для бизнес-ошибок
    }
    return user
}

// ✅ Go-way: возвращать ошибку
func GetUser(id int) (*User, error) {
    user, err := db.QueryUser(id)
    if err != nil {
        return nil, fmt.Errorf("get user %d: %w", id, err)
    }
    return user, nil
}
```

**2. Игнорирование ошибок**

```go
// ❌ Игнорирование ошибки
json.Unmarshal(data, &user) // ошибка игнорируется!

// ✅ Всегда проверять
if err := json.Unmarshal(data, &user); err != nil {
    return fmt.Errorf("unmarshal user: %w", err)
}
```

**3. Не использование errors.Is / errors.As**

```go
// ❌ Прямое сравнение строк или типов
if err.Error() == "user not found" { ... } // Хрупко!

// ✅ Использовать errors.Is для sentinel errors
if errors.Is(err, ErrUserNotFound) { ... }

// ✅ Использовать errors.As для typed errors
var validErr *ValidationError
if errors.As(err, &validErr) {
    // доступ к полям validErr
}
```

### Quick Reference

```go
// Создание ошибок
err := errors.New("something went wrong")
err := fmt.Errorf("user %d not found", id)

// Wrapping (добавление контекста)
return fmt.Errorf("get user: %w", err)

// Проверка типа ошибки
if errors.Is(err, ErrNotFound) { ... }

// Извлечение typed error
var e *MyError
if errors.As(err, &e) { ... }

// Sentinel errors
var ErrNotFound = errors.New("not found")
var ErrInvalid = errors.New("invalid")
```

---

## Организация пакетов

### internal/ — ваш лучший друг

Директория `internal/` — **компилятор Go запрещает** импорт кода из неё извне модуля.

```
myapp/
├── go.mod
├── cmd/
│   └── api/
│       └── main.go          # entry point
├── internal/                 # приватный код
│   ├── user/
│   │   ├── handler.go
│   │   ├── service.go
│   │   └── repository.go
│   ├── order/
│   │   └── ...
│   └── platform/             # общие internal-пакеты
│       ├── database/
│       └── logger/
└── pkg/                      # публичный код (для библиотек)
    └── validator/
```

**Почему это важно**:

```go
// Другой модуль НЕ СМОЖЕТ импортировать:
import "github.com/company/myapp/internal/user" // Ошибка компиляции!

// Но может импортировать:
import "github.com/company/myapp/pkg/validator" // OK
```

**Сравнение с C#**:

| Механизм | C# | Go |
|----------|----|----|
| Видимость внутри проекта | `internal` keyword | `internal/` директория |
| Гарантия | Runtime/Compile time | **Compile time** |
| Применение | На класс/метод | На весь пакет |

### Package по feature vs по layer

**C#-стиль (по layer) — НЕ рекомендуется в Go**:

```
// ❌ Организация по слоям
myapp/
├── controllers/
│   ├── user_controller.go
│   └── order_controller.go
├── services/
│   ├── user_service.go
│   └── order_service.go
├── repositories/
│   ├── user_repository.go
│   └── order_repository.go
└── models/
    ├── user.go
    └── order.go
```

**Проблемы**:
- Высокая связанность между пакетами
- Сложно понять границы домена
- Часто приводит к циклическим зависимостям

**Go-стиль (по feature) — рекомендуется**:

```
// ✅ Организация по фичам/доменам
myapp/
├── cmd/
│   └── api/
│       └── main.go
├── internal/
│   ├── user/                 # всё про users вместе
│   │   ├── handler.go
│   │   ├── service.go
│   │   ├── repository.go
│   │   ├── model.go
│   │   └── user_test.go
│   ├── order/                # всё про orders вместе
│   │   ├── handler.go
│   │   ├── service.go
│   │   └── ...
│   └── platform/             # общая инфраструктура
│       ├── postgres/
│       ├── redis/
│       └── http/
└── pkg/                      # публичные библиотеки
```

**Преимущества**:
- Код связанный логически — рядом физически
- Легко понять границы домена
- Минимум зависимостей между пакетами
- Легко выделить в отдельный сервис

### Cyclic imports

Go **запрещает** циклические зависимости между пакетами. Это compile-time ошибка.

```go
// ❌ Цикл: user → order → user
// package user
import "myapp/internal/order"  // user зависит от order

// package order
import "myapp/internal/user"   // order зависит от user
// ОШИБКА КОМПИЛЯЦИИ!
```

**Решения**:

**1. Интерфейсы для разрыва зависимости**:

```go
// package user — определяет интерфейс
type OrderGetter interface {
    GetByUserID(ctx context.Context, userID int) ([]*Order, error)
}

type Service struct {
    orders OrderGetter  // зависимость через интерфейс
}

// package order — реализует, но не знает про user
type Service struct { /* ... */ }

func (s *Service) GetByUserID(ctx context.Context, userID int) ([]*Order, error) {
    // ...
}

// main.go — связывание
userSvc := user.NewService(orderSvc)  // orderSvc реализует OrderGetter
```

**2. Общий пакет с типами**:

```go
// package domain — общие типы
type User struct { ... }
type Order struct { ... }

// package user
import "myapp/internal/domain"

// package order
import "myapp/internal/domain"

// Нет цикла — оба зависят от domain
```

**3. Dependency Inversion**:

```go
// package notification — нижний уровень
type UserGetter interface {
    GetByID(ctx context.Context, id int) (*User, error)
}

type Service struct {
    users UserGetter
}

// package user — верхний уровень
// Реализует UserGetter, но не знает про notification
```

### Naming conventions

**Имена пакетов**:

```go
// ✅ Хорошо: короткие, lowercase, без подчёркиваний
package user
package httputil
package postgres

// ❌ Плохо
package userService      // camelCase
package user_service     // snake_case
package UserService      // PascalCase
package util             // слишком общее
package common           // слишком общее
package helpers          // слишком общее
```

**Избегать stutter (заикания)**:

```go
// ❌ Stutter: user.UserService, user.UserRepository
package user

type UserService struct { ... }  // user.UserService — повторение

// ✅ Без stutter
type Service struct { ... }      // user.Service — чисто
type Repository struct { ... }   // user.Repository — чисто
```

**Именование файлов**:

```go
// Один файл — одна логическая единица
user/
├── service.go       // type Service struct
├── repository.go    // type Repository struct
├── handler.go       // type Handler struct
├── model.go         // type User struct, type CreateRequest struct
└── service_test.go  // тесты для service.go
```

---

## Типичные ошибки C# разработчиков

### 1. Overengineering

```go
// ❌ C#-стиль: слишком много абстракций
type IUserRepositoryFactory interface {
    Create() IUserRepository
}

type IUserRepository interface {
    // 15 методов
}

type IUserService interface {
    // 10 методов
}

type IUserServiceFactory interface {
    Create() IUserService
}

// ✅ Go-стиль: просто и прямо
type UserRepository struct {
    db *sql.DB
}

type UserService struct {
    repo *UserRepository
}
```

### 2. Getter/Setter для всего

```go
// ❌ C#-стиль: getter/setter
type User struct {
    name string
    age  int
}

func (u *User) GetName() string { return u.name }
func (u *User) SetName(n string) { u.name = n }
func (u *User) GetAge() int { return u.age }
func (u *User) SetAge(a int) { u.age = a }

// ✅ Go-стиль: публичные поля
type User struct {
    Name string
    Age  int
}

// Getter/setter только если нужна валидация или side effects
```

### 3. Интерфейсы "на всякий случай"

```go
// ❌ Интерфейс для единственной реализации
type UserService interface {
    GetUser(id int) (*User, error)
    CreateUser(u *User) error
}

type userService struct { ... }

var _ UserService = (*userService)(nil)  // "проверка реализации"

// ✅ Просто структура
type UserService struct { ... }

// Интерфейс создашь когда понадобится для тестов или полиморфизма
```

### 4. Panic вместо error

```go
// ❌ Panic для бизнес-ошибок
func MustGetUser(id int) *User {
    user, err := db.GetUser(id)
    if err != nil {
        panic(err)  // Плохо!
    }
    return user
}

// ✅ Возвращать ошибку
func GetUser(id int) (*User, error) {
    user, err := db.GetUser(id)
    if err != nil {
        return nil, fmt.Errorf("get user %d: %w", id, err)
    }
    return user, nil
}

// Panic только для инициализации (Must-функции)
func MustParseTemplate(name string) *template.Template {
    t, err := template.ParseFiles(name)
    if err != nil {
        panic(err)  // OK — ошибка при старте приложения
    }
    return t
}
```

### 5. Игнорирование context.Context

```go
// ❌ Нет context
func GetUser(id int) (*User, error) {
    return db.Query("SELECT * FROM users WHERE id = ?", id)
}

// ✅ Context первым параметром
func GetUser(ctx context.Context, id int) (*User, error) {
    return db.QueryContext(ctx, "SELECT * FROM users WHERE id = ?", id)
}
```

### 6. Неправильная работа с nil

```go
// ❌ Не проверять nil
func ProcessUser(u *User) {
    fmt.Println(u.Name)  // Panic если u == nil!
}

// ✅ Проверять nil или использовать значения
func ProcessUser(u *User) error {
    if u == nil {
        return errors.New("user is nil")
    }
    fmt.Println(u.Name)
    return nil
}

// Или использовать значение вместо указателя
func ProcessUser(u User) {  // Копия, не указатель
    fmt.Println(u.Name)  // Работает с zero value
}
```

### 7. LINQ-стиль вместо простых циклов

```go
// ❌ Попытка сделать LINQ
users := Filter(users, func(u User) bool { return u.Age > 18 })
users = Map(users, func(u User) UserDTO { return ToDTO(u) })
result := Reduce(users, 0, func(acc int, u UserDTO) int { return acc + 1 })

// ✅ Простой цикл — читаемее и быстрее
var adults []UserDTO
for _, u := range users {
    if u.Age > 18 {
        adults = append(adults, ToDTO(u))
    }
}
count := len(adults)
```

### Сводная таблица

| Ошибка | Почему плохо | Go-way |
|--------|--------------|--------|
| Getters/Setters | Избыточность, бойлерплейт | Экспортируемые поля |
| Много интерфейсов | Interface pollution | По необходимости |
| Panic для ошибок | Не идиоматично, сложно обрабатывать | Return error |
| Игнорирование err | Потеря информации, скрытые баги | Всегда проверять |
| Нет context | Нет cancellation, timeout | Context первым параметром |
| LINQ-стиль | Медленнее, сложнее читать | Простые циклы |
| Factories везде | Overengineering | Простые конструкторы |
| DTO на каждый слой | Много маппинга | Минимум преобразований |

---

## API Design

### Экспорт и видимость

В Go видимость определяется **регистром первой буквы**:

```go
package user

// Экспортируется (публичный API)
type User struct {       // ✅ Доступен извне пакета
    ID   int             // ✅ Поле доступно
    Name string          // ✅ Поле доступно
    hash string          // ❌ Поле приватное
}

func NewUser(name string) *User { ... }  // ✅ Функция экспортируется
func (u *User) Validate() error { ... }  // ✅ Метод экспортируется

// Не экспортируется (внутреннее)
type userCache struct { ... }            // ❌ Только внутри пакета
func hashPassword(pwd string) string { } // ❌ Только внутри пакета
func (u *User) setHash(h string) { }     // ❌ Метод приватный
```

**Правило минимального экспорта**:

```go
// ❌ Экспортируем всё
type UserRepository struct {
    DB        *sql.DB      // Зачем клиенту доступ к DB?
    Cache     *redis.Client
    TableName string
}

// ✅ Минимальный публичный API
type UserRepository struct {
    db        *sql.DB       // приватные поля
    cache     *redis.Client
    tableName string
}

// Только нужные методы экспортируются
func (r *UserRepository) GetByID(ctx context.Context, id int) (*User, error)
func (r *UserRepository) Create(ctx context.Context, u *User) error
```

### Версионирование

Go modules используют **semantic versioning** с особенностями:

```
v1.2.3
│ │ │
│ │ └── Patch: багфиксы, без breaking changes
│ └──── Minor: новые фичи, без breaking changes
└────── Major: breaking changes
```

**Major version suffix** (для v2+):

```
// Для v0.x и v1.x — обычный путь
import "github.com/company/mylib"

// Для v2+ — суффикс в пути
import "github.com/company/mylib/v2"
import "github.com/company/mylib/v3"
```

**Структура репозитория для v2+**:

```
mylib/
├── go.mod           # module github.com/company/mylib/v2
├── v2/              # опционально, код может быть в корне
│   └── ...
└── ...
```

### Обратная совместимость

**Что НЕ ломает совместимость** (ok в minor/patch):
- Добавление нового экспортируемого типа
- Добавление нового метода в структуру
- Добавление нового поля в структуру
- Добавление новой функции

**Что ЛОМАЕТ совместимость** (требует major bump):
- Удаление экспортируемого типа/функции/метода
- Изменение сигнатуры функции
- Изменение типа поля структуры
- Удаление поля структуры
- Изменение поведения функции

```go
// v1.0.0
func ParseConfig(path string) (*Config, error)

// v1.1.0 — добавили опциональный параметр через Functional Options
func ParseConfig(path string, opts ...Option) (*Config, error)  // ✅ Совместимо

// v2.0.0 — изменили сигнатуру
func ParseConfig(path string, strict bool) (*Config, error)  // ❌ Breaking change
```

### Документирование API

**godoc-стиль**:

```go
// Package user предоставляет функционал управления пользователями.
//
// Основные типы:
//   - User: представление пользователя
//   - Service: бизнес-логика работы с пользователями
//   - Repository: доступ к данным
package user

// User представляет пользователя системы.
//
// Поля ID и Email обязательны и уникальны.
// CreatedAt устанавливается автоматически при создании.
type User struct {
    ID        int       // Уникальный идентификатор
    Email     string    // Email пользователя (уникальный)
    Name      string    // Отображаемое имя
    CreatedAt time.Time // Время создания
}

// NewUser создаёт нового пользователя с указанным email и именем.
// Возвращает ошибку, если email невалидный.
//
// Пример:
//
//     user, err := NewUser("user@example.com", "John Doe")
//     if err != nil {
//         log.Fatal(err)
//     }
func NewUser(email, name string) (*User, error) {
    // ...
}

// ErrUserNotFound возвращается когда пользователь не найден.
var ErrUserNotFound = errors.New("user not found")
```

### Сравнительная таблица

| Аспект | C# | Go |
|--------|----|----|
| Видимость | `public`, `internal`, `private`, `protected` | Заглавная/строчная буква |
| Scope модификаторов | Класс, метод, поле | Пакет целиком |
| Версионирование | NuGet SemVer | Go modules SemVer |
| Major version | Новый пакет NuGet | `/v2`, `/v3` suffix в import |
| Документация | XML comments, `///` | Комментарии перед объявлением |
| Генерация доков | Swagger, DocFX | `go doc`, pkg.go.dev |

---

## Практические примеры

### Пример 1: Рефакторинг Repository

**C# оригинал**:

```csharp
// C#: типичный generic repository
public interface IRepository<T> where T : class
{
    Task<T?> GetByIdAsync(int id);
    Task<IEnumerable<T>> GetAllAsync();
    Task<T> AddAsync(T entity);
    Task UpdateAsync(T entity);
    Task DeleteAsync(int id);
    Task<bool> ExistsAsync(int id);
    Task<int> CountAsync();
    IQueryable<T> Query();
}

public interface IUserRepository : IRepository<User>
{
    Task<User?> GetByEmailAsync(string email);
    Task<IEnumerable<User>> GetActiveUsersAsync();
}

public class UserRepository : IUserRepository
{
    private readonly AppDbContext _context;

    public UserRepository(AppDbContext context)
    {
        _context = context;
    }

    // 9+ методов реализации...
}

public class UserService
{
    private readonly IUserRepository _repository;  // 9+ методов, используем 2

    public async Task<UserDto> GetUserProfile(int userId)
    {
        var user = await _repository.GetByIdAsync(userId);
        return MapToDto(user);
    }
}
```

**Go рефакторинг**:

```go
// Go: маленькие интерфейсы у потребителя

// package postgres — конкретная реализация без интерфейса
type UserRepository struct {
    db *sql.DB
}

func NewUserRepository(db *sql.DB) *UserRepository {
    return &UserRepository{db: db}
}

func (r *UserRepository) GetByID(ctx context.Context, id int) (*domain.User, error) {
    var u domain.User
    err := r.db.QueryRowContext(ctx,
        "SELECT id, email, name, created_at FROM users WHERE id = $1", id,
    ).Scan(&u.ID, &u.Email, &u.Name, &u.CreatedAt)
    if errors.Is(err, sql.ErrNoRows) {
        return nil, domain.ErrUserNotFound
    }
    return &u, err
}

func (r *UserRepository) GetByEmail(ctx context.Context, email string) (*domain.User, error) {
    // ...
}

func (r *UserRepository) Create(ctx context.Context, u *domain.User) error {
    // ...
}

func (r *UserRepository) List(ctx context.Context, filter Filter) ([]*domain.User, error) {
    // ...
}

// package service — интерфейс определяется здесь
type userGetter interface {
    GetByID(ctx context.Context, id int) (*domain.User, error)
}

type ProfileService struct {
    users userGetter  // только 1 нужный метод
}

func NewProfileService(users userGetter) *ProfileService {
    return &ProfileService{users: users}
}

func (s *ProfileService) GetProfile(ctx context.Context, userID int) (*Profile, error) {
    user, err := s.users.GetByID(ctx, userID)
    if err != nil {
        return nil, fmt.Errorf("get user: %w", err)
    }
    return mapToProfile(user), nil
}

// package admin — свой интерфейс
type userLister interface {
    List(ctx context.Context, filter Filter) ([]*domain.User, error)
}

type AdminService struct {
    users userLister  // только нужные методы
}
```

### Пример 2: Миграция DI-сервиса

**C# оригинал**:

```csharp
// C#: сложная DI-конфигурация
public class Startup
{
    public void ConfigureServices(IServiceCollection services)
    {
        services.AddDbContext<AppDbContext>(options =>
            options.UseNpgsql(Configuration.GetConnectionString("Default")));

        services.AddScoped<IUserRepository, UserRepository>();
        services.AddScoped<IOrderRepository, OrderRepository>();
        services.AddScoped<IEmailService, SendGridEmailService>();
        services.AddScoped<IUserService, UserService>();
        services.AddScoped<IOrderService, OrderService>();

        services.Configure<EmailOptions>(Configuration.GetSection("Email"));
        services.Configure<CacheOptions>(Configuration.GetSection("Cache"));

        services.AddStackExchangeRedisCache(options =>
            options.Configuration = Configuration.GetConnectionString("Redis"));
    }
}

public class UserService : IUserService
{
    private readonly IUserRepository _userRepo;
    private readonly IEmailService _emailService;
    private readonly ILogger<UserService> _logger;
    private readonly IOptions<EmailOptions> _emailOptions;

    public UserService(
        IUserRepository userRepo,
        IEmailService emailService,
        ILogger<UserService> logger,
        IOptions<EmailOptions> emailOptions)
    {
        _userRepo = userRepo;
        _emailService = emailService;
        _logger = logger;
        _emailOptions = emailOptions;
    }
}
```

**Go рефакторинг**:

```go
// Go: явная инициализация

// config/config.go
type Config struct {
    Database DatabaseConfig
    Redis    RedisConfig
    Email    EmailConfig
}

func Load() (*Config, error) {
    var cfg Config
    if err := env.Parse(&cfg); err != nil {
        return nil, fmt.Errorf("parse config: %w", err)
    }
    return &cfg, nil
}

// main.go — всё явно
func main() {
    // Загрузка конфигурации
    cfg, err := config.Load()
    if err != nil {
        log.Fatal("load config", "error", err)
    }

    // Инициализация инфраструктуры
    db, err := sql.Open("postgres", cfg.Database.URL)
    if err != nil {
        log.Fatal("connect db", "error", err)
    }
    defer db.Close()

    redisClient := redis.NewClient(&redis.Options{
        Addr: cfg.Redis.Addr,
    })
    defer redisClient.Close()

    logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

    // Инициализация слоёв — зависимости явные
    userRepo := postgres.NewUserRepository(db)
    orderRepo := postgres.NewOrderRepository(db)
    emailSvc := email.NewService(cfg.Email)
    cache := rediscache.New(redisClient)

    userSvc := service.NewUserService(userRepo, emailSvc, logger, cfg.Email)
    orderSvc := service.NewOrderService(orderRepo, userSvc, cache, logger)

    // HTTP handlers
    userHandler := api.NewUserHandler(userSvc)
    orderHandler := api.NewOrderHandler(orderSvc)

    // Router
    mux := http.NewServeMux()
    mux.Handle("GET /users/{id}", userHandler.GetUser())
    mux.Handle("POST /orders", orderHandler.CreateOrder())

    // Server
    server := &http.Server{
        Addr:    cfg.Server.Addr,
        Handler: mux,
    }

    log.Info("starting server", "addr", cfg.Server.Addr)
    if err := server.ListenAndServe(); err != nil {
        log.Fatal("server failed", "error", err)
    }
}
```

### Пример 3: Организация микросервиса

```
user-service/
├── cmd/
│   └── api/
│       └── main.go              # Entry point
├── internal/
│   ├── config/
│   │   └── config.go            # Конфигурация
│   ├── user/                    # Домен User
│   │   ├── model.go             # type User struct
│   │   ├── service.go           # Бизнес-логика
│   │   ├── service_test.go      # Тесты
│   │   ├── repository.go        # Интерфейс репозитория
│   │   └── errors.go            # ErrUserNotFound и т.д.
│   ├── postgres/                # Реализация для PostgreSQL
│   │   ├── user_repository.go
│   │   └── migrations/
│   ├── api/                     # HTTP handlers
│   │   ├── handler.go
│   │   ├── middleware.go
│   │   └── router.go
│   └── platform/                # Общая инфраструктура
│       ├── logger/
│       └── metrics/
├── pkg/                         # Публичные пакеты (если нужны)
│   └── userid/
│       └── userid.go            # type ID string
├── go.mod
├── go.sum
├── Dockerfile
└── Makefile
```

**internal/user/service.go**:

```go
package user

import (
    "context"
    "fmt"
)

// Repository — интерфейс определён в пакете user (consumer-side)
type Repository interface {
    GetByID(ctx context.Context, id int) (*User, error)
    GetByEmail(ctx context.Context, email string) (*User, error)
    Create(ctx context.Context, u *User) error
    Update(ctx context.Context, u *User) error
}

type Service struct {
    repo   Repository
    logger *slog.Logger
}

func NewService(repo Repository, logger *slog.Logger) *Service {
    return &Service{
        repo:   repo,
        logger: logger,
    }
}

func (s *Service) GetUser(ctx context.Context, id int) (*User, error) {
    user, err := s.repo.GetByID(ctx, id)
    if err != nil {
        return nil, fmt.Errorf("get user %d: %w", id, err)
    }
    return user, nil
}

func (s *Service) CreateUser(ctx context.Context, req CreateRequest) (*User, error) {
    // Валидация
    if err := req.Validate(); err != nil {
        return nil, fmt.Errorf("validate: %w", err)
    }

    // Проверка уникальности email
    existing, err := s.repo.GetByEmail(ctx, req.Email)
    if err != nil && !errors.Is(err, ErrUserNotFound) {
        return nil, fmt.Errorf("check email: %w", err)
    }
    if existing != nil {
        return nil, ErrEmailExists
    }

    // Создание
    user := &User{
        Email:     req.Email,
        Name:      req.Name,
        CreatedAt: time.Now(),
    }

    if err := s.repo.Create(ctx, user); err != nil {
        return nil, fmt.Errorf("create user: %w", err)
    }

    s.logger.Info("user created", "id", user.ID, "email", user.Email)
    return user, nil
}
```

---
