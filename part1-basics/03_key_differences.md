# 1.3 Ключевые отличия от C#

## Содержание
- [Философия языков](#философия-языков)
- [Отсутствие классов и наследования](#отсутствие-классов-и-наследования)
- [Error Handling vs Exceptions](#error-handling-vs-exceptions)
- [Композиция vs Наследование](#композиция-vs-наследование)
- [Zero Values](#zero-values)
- [Видимость через регистр](#видимость-через-регистр)
- [Идиоматичные различия](#идиоматичные-различия)
- [Практические примеры](#практические-примеры)
- [Чек-лист перехода](#чек-лист-перехода)

---

## Философия языков

### C# философия
- **Богатство возможностей**: множество способов решить задачу
- **ООП-центричность**: классы, наследование, полиморфизм
- **Enterprise-ориентированность**: SOLID, паттерны, абстракции
- **"Batteries included"**: огромная стандартная библиотека

### Go философия
- **Простота**: один очевидный способ
- **Прагматизм**: решение задач, а не красота архитектуры
- **Минимализм**: 25 ключевых слов
- **"Less is more"**: композиция, а не иерархии

> 💡 **Ключевое отличие**: C# даёт инструменты для создания сложных архитектур, Go заставляет писать простой код.

---

## Отсутствие классов и наследования

### C# подход

```csharp
// Классы, наследование, виртуальные методы
public abstract class Animal
{
    public string Name { get; set; }

    public abstract void MakeSound();

    public virtual void Move()
    {
        Console.WriteLine($"{Name} is moving");
    }
}

public class Dog : Animal
{
    public override void MakeSound()
    {
        Console.WriteLine("Woof!");
    }

    public override void Move()
    {
        base.Move();
        Console.WriteLine("Running on four legs");
    }
}

public class Cat : Animal
{
    public override void MakeSound()
    {
        Console.WriteLine("Meow!");
    }
}

// Использование
Animal dog = new Dog { Name = "Buddy" };
dog.MakeSound(); // Woof!
dog.Move();      // Buddy is moving \n Running on four legs
```

### Go подход

```go
// Структуры + интерфейсы (неявная реализация)
type Animal interface {
    MakeSound()
    Move()
}

type Dog struct {
    Name string
}

func (d Dog) MakeSound() {
    fmt.Println("Woof!")
}

func (d Dog) Move() {
    fmt.Printf("%s is moving\n", d.Name)
    fmt.Println("Running on four legs")
}

type Cat struct {
    Name string
}

func (c Cat) MakeSound() {
    fmt.Println("Meow!")
}

func (c Cat) Move() {
    fmt.Printf("%s is moving\n", c.Name)
}

// Использование
var dog Animal = Dog{Name: "Buddy"}
dog.MakeSound() // Woof!
dog.Move()      // Buddy is moving \n Running on four legs
```

### Ключевые отличия

| Аспект | C# | Go |
|--------|----|----|
| **Тип системы** | Классы, наследование | Структуры, композиция |
| **Полиморфизм** | Явный (`: BaseClass`, `override`) | Неявный (duck typing) |
| **Переиспользование** | Наследование + интерфейсы | Композиция + встраивание |
| **Абстракция** | Абстрактные классы | Только интерфейсы |
| **Виртуальные методы** | Есть (`virtual`, `override`) | Все методы интерфейса "виртуальные" |

> ⚠️ **Важно**: В Go нет наследования в классическом понимании. Вместо "is-a" используется "has-a".

---

## Error Handling vs Exceptions

### C# подход: Exceptions

```csharp
// Исключения - норма
public class UserService
{
    public User GetUser(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID", nameof(id));

        var user = _repository.FindById(id);
        if (user == null)
            throw new UserNotFoundException($"User {id} not found");

        return user;
    }

    public async Task<Order> CreateOrder(CreateOrderRequest request)
    {
        try
        {
            ValidateRequest(request);
            var user = GetUser(request.UserId);
            var order = await _orderRepository.Create(request);
            await _emailService.SendConfirmation(user.Email, order);
            return order;
        }
        catch (UserNotFoundException ex)
        {
            _logger.LogError(ex, "User not found");
            throw; // Пробрасываем дальше
        }
        catch (SmtpException ex)
        {
            _logger.LogWarning(ex, "Email failed, order created");
            // Не критично - заказ создан
            throw new OrderCreatedButEmailFailedException(order.Id, ex);
        }
    }
}

// Использование
try
{
    var order = await service.CreateOrder(request);
    return Ok(order);
}
catch (ArgumentException ex)
{
    return BadRequest(ex.Message);
}
catch (UserNotFoundException ex)
{
    return NotFound(ex.Message);
}
catch (Exception ex)
{
    return StatusCode(500, "Internal error");
}
```

### Go подход: Явные ошибки

```go
// Ошибки как значения
type UserService struct {
    repository *UserRepository
    logger     *Logger
}

var (
    ErrInvalidUserID   = errors.New("invalid user ID")
    ErrUserNotFound    = errors.New("user not found")
    ErrEmailFailed     = errors.New("email sending failed")
)

func (s *UserService) GetUser(id int) (*User, error) {
    if id <= 0 {
        return nil, fmt.Errorf("%w: %d", ErrInvalidUserID, id)
    }

    user, err := s.repository.FindByID(id)
    if err != nil {
        return nil, fmt.Errorf("find user: %w", err)
    }
    if user == nil {
        return nil, fmt.Errorf("%w: %d", ErrUserNotFound, id)
    }

    return user, nil
}

func (s *UserService) CreateOrder(ctx context.Context, req CreateOrderRequest) (*Order, error) {
    if err := s.validateRequest(req); err != nil {
        return nil, fmt.Errorf("validate: %w", err)
    }

    user, err := s.GetUser(req.UserID)
    if err != nil {
        s.logger.Error("get user failed", "error", err)
        return nil, err
    }

    order, err := s.orderRepository.Create(ctx, req)
    if err != nil {
        return nil, fmt.Errorf("create order: %w", err)
    }

    // Email - не критично
    if err := s.emailService.SendConfirmation(user.Email, order); err != nil {
        s.logger.Warn("email failed", "order_id", order.ID, "error", err)
        // Не возвращаем ошибку - заказ создан
    }

    return order, nil
}

// Использование
order, err := service.CreateOrder(ctx, request)
if err != nil {
    switch {
    case errors.Is(err, ErrInvalidUserID):
        return nil, status.Error(codes.InvalidArgument, err.Error())
    case errors.Is(err, ErrUserNotFound):
        return nil, status.Error(codes.NotFound, err.Error())
    default:
        return nil, status.Error(codes.Internal, "internal error")
    }
}
return &pb.CreateOrderResponse{Order: order}, nil
```

### Идиоматичные паттерны обработки ошибок

#### 1. Early Return (Guard Clauses)

**C#**:
```csharp
public Result ProcessOrder(Order order)
{
    if (order == null)
        throw new ArgumentNullException(nameof(order));

    if (!order.IsValid())
        throw new ValidationException("Invalid order");

    if (order.Amount <= 0)
        throw new ArgumentException("Amount must be positive");

    // Основная логика
    return PerformProcessing(order);
}
```

**Go** (идиоматично):
```go
func ProcessOrder(order *Order) (*Result, error) {
    if order == nil {
        return nil, errors.New("order is nil")
    }

    if !order.IsValid() {
        return nil, errors.New("invalid order")
    }

    if order.Amount <= 0 {
        return nil, errors.New("amount must be positive")
    }

    // Основная логика
    return performProcessing(order)
}
```

#### 2. Обёртывание ошибок

**C#**:
```csharp
catch (SqlException ex)
{
    throw new DatabaseException("Failed to save user", ex);
}
```

**Go** (идиоматично):
```go
if err := db.SaveUser(user); err != nil {
    return fmt.Errorf("save user: %w", err) // %w сохраняет цепочку
}

// Проверка типа ошибки
if errors.Is(err, sql.ErrNoRows) {
    // Обработка
}

// Извлечение конкретной ошибки
var netErr *net.OpError
if errors.As(err, &netErr) {
    // Работа с netErr
}
```

#### 3. Множественные возвращаемые значения

**C#**:
```csharp
// Try-паттерн
public bool TryParseUser(string data, out User user)
{
    user = null;
    try
    {
        user = JsonSerializer.Deserialize<User>(data);
        return true;
    }
    catch
    {
        return false;
    }
}

// Использование
if (TryParseUser(data, out var user))
{
    Process(user);
}
```

**Go** (естественно):
```go
func ParseUser(data string) (*User, error) {
    var user User
    if err := json.Unmarshal([]byte(data), &user); err != nil {
        return nil, fmt.Errorf("unmarshal user: %w", err)
    }
    return &user, nil
}

// Использование
user, err := ParseUser(data)
if err != nil {
    return err
}
process(user)
```

### Сравнение подходов

| Аспект | C# Exceptions | Go Errors |
|--------|---------------|-----------|
| **Явность** | Неявные (не видны в сигнатуре) | Явные (часть возврата) |
| **Производительность** | Медленные (stack unwinding) | Быстрые (обычные значения) |
| **Контроль потока** | Неявный (try-catch) | Явный (if err != nil) |
| **Типизация** | Сильная (иерархия классов) | Слабая (error интерфейс) |
| **Стек вызовов** | Автоматический | Ручной (fmt.Errorf) |
| **Частота проверки** | Выборочная | Каждый вызов |

> 💡 **Философия Go**: "Errors are values" - обрабатывай ошибки там, где они возникают.

---

## Композиция vs Наследование

### C# наследование

```csharp
public abstract class BaseRepository<T> where T : class
{
    protected readonly DbContext _context;

    protected BaseRepository(DbContext context)
    {
        _context = context;
    }

    public virtual async Task<T> GetByIdAsync(int id)
    {
        return await _context.Set<T>().FindAsync(id);
    }

    public virtual async Task<IEnumerable<T>> GetAllAsync()
    {
        return await _context.Set<T>().ToListAsync();
    }
}

public class UserRepository : BaseRepository<User>
{
    public UserRepository(DbContext context) : base(context) { }

    // Переопределяем базовый метод
    public override async Task<User> GetByIdAsync(int id)
    {
        return await _context.Users
            .Include(u => u.Orders)
            .FirstOrDefaultAsync(u => u.Id == id);
    }

    // Добавляем специфичный метод
    public async Task<User> GetByEmailAsync(string email)
    {
        return await _context.Users
            .FirstOrDefaultAsync(u => u.Email == email);
    }
}
```

### Go композиция (embedding)

```go
// Базовый репозиторий
type BaseRepository struct {
    db *sql.DB
}

func (r *BaseRepository) GetByID(ctx context.Context, table string, id int, dest interface{}) error {
    query := fmt.Sprintf("SELECT * FROM %s WHERE id = $1", table)
    return r.db.QueryRowContext(ctx, query, id).Scan(dest)
}

func (r *BaseRepository) GetAll(ctx context.Context, table string, dest interface{}) error {
    query := fmt.Sprintf("SELECT * FROM %s", table)
    rows, err := r.db.QueryContext(ctx, query)
    if err != nil {
        return err
    }
    defer rows.Close()
    // Сканирование в dest...
    return nil
}

// UserRepository встраивает BaseRepository
type UserRepository struct {
    BaseRepository // Встраивание (embedding)
}

func NewUserRepository(db *sql.DB) *UserRepository {
    return &UserRepository{
        BaseRepository: BaseRepository{db: db},
    }
}

// "Переопределяем" метод (на самом деле - затеняем)
func (r *UserRepository) GetByID(ctx context.Context, id int) (*User, error) {
    query := `
        SELECT u.*, o.*
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE u.id = $1
    `
    var user User
    err := r.db.QueryRowContext(ctx, query, id).Scan(&user /* ... */)
    if err != nil {
        return nil, fmt.Errorf("get user: %w", err)
    }
    return &user, nil
}

// Добавляем специфичный метод
func (r *UserRepository) GetByEmail(ctx context.Context, email string) (*User, error) {
    query := "SELECT * FROM users WHERE email = $1"
    var user User
    err := r.db.QueryRowContext(ctx, query, email).Scan(&user /* ... */)
    if err != nil {
        return nil, fmt.Errorf("get user by email: %w", err)
    }
    return &user, nil
}

// Использование
repo := NewUserRepository(db)
user, err := repo.GetByID(ctx, 123)        // Вызывает UserRepository.GetByID
user, err = repo.GetByEmail(ctx, "a@b.c") // Специфичный метод
```

### Композиция через интерфейсы (более идиоматично)

```go
// Определяем интерфейсы для нужной функциональности
type Reader interface {
    Get(ctx context.Context, id int) (interface{}, error)
    List(ctx context.Context) ([]interface{}, error)
}

type Writer interface {
    Create(ctx context.Context, entity interface{}) error
    Update(ctx context.Context, entity interface{}) error
    Delete(ctx context.Context, id int) error
}

// Logger - ещё один интерфейс
type Logger interface {
    Log(msg string, args ...interface{})
}

// UserService композирует нужные зависимости
type UserService struct {
    repo   Reader  // Только чтение
    writer Writer  // Только запись
    logger Logger  // Логирование
    cache  Cache   // Кеширование
}

func NewUserService(repo Reader, writer Writer, logger Logger, cache Cache) *UserService {
    return &UserService{
        repo:   repo,
        writer: writer,
        logger: logger,
        cache:  cache,
    }
}

func (s *UserService) GetUser(ctx context.Context, id int) (*User, error) {
    // Пробуем кеш
    if cached, ok := s.cache.Get(id); ok {
        s.logger.Log("cache hit", "id", id)
        return cached.(*User), nil
    }

    // Идём в БД
    entity, err := s.repo.Get(ctx, id)
    if err != nil {
        s.logger.Log("repo error", "error", err)
        return nil, err
    }

    user := entity.(*User)
    s.cache.Set(id, user)
    return user, nil
}
```

### Идиоматичная композиция: пример с HTTP middleware

**C# (ASP.NET Core)**:
```csharp
// Базовый класс middleware
public abstract class BaseMiddleware
{
    protected readonly RequestDelegate _next;

    protected BaseMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public abstract Task InvokeAsync(HttpContext context);
}

// Наследование
public class LoggingMiddleware : BaseMiddleware
{
    private readonly ILogger _logger;

    public LoggingMiddleware(RequestDelegate next, ILogger logger)
        : base(next)
    {
        _logger = logger;
    }

    public override async Task InvokeAsync(HttpContext context)
    {
        _logger.LogInformation($"Request: {context.Request.Path}");
        await _next(context);
        _logger.LogInformation($"Response: {context.Response.StatusCode}");
    }
}
```

**Go (идиоматично через функции)**:
```go
// Middleware - это просто функция
type Middleware func(http.HandlerFunc) http.HandlerFunc

// Логирование
func LoggingMiddleware(logger *log.Logger) Middleware {
    return func(next http.HandlerFunc) http.HandlerFunc {
        return func(w http.ResponseWriter, r *http.Request) {
            logger.Printf("Request: %s %s", r.Method, r.URL.Path)
            next(w, r)
            logger.Printf("Completed: %s", r.URL.Path)
        }
    }
}

// Аутентификация
func AuthMiddleware(authService *AuthService) Middleware {
    return func(next http.HandlerFunc) http.HandlerFunc {
        return func(w http.ResponseWriter, r *http.Request) {
            token := r.Header.Get("Authorization")
            if !authService.Validate(token) {
                http.Error(w, "Unauthorized", http.StatusUnauthorized)
                return
            }
            next(w, r)
        }
    }
}

// Композиция middleware
func Chain(handler http.HandlerFunc, middlewares ...Middleware) http.HandlerFunc {
    for i := len(middlewares) - 1; i >= 0; i-- {
        handler = middlewares[i](handler)
    }
    return handler
}

// Использование
func main() {
    logger := log.New(os.Stdout, "HTTP: ", log.LstdFlags)
    authService := NewAuthService()

    handler := Chain(
        handleUser,
        LoggingMiddleware(logger),
        AuthMiddleware(authService),
    )

    http.HandleFunc("/user", handler)
}
```

> 💡 **В Go**: Предпочитай композицию через интерфейсы, а не встраивание структур.

---

## Zero Values

### C# значения по умолчанию

```csharp
// Классы - null по умолчанию
User user;          // null (но компилятор предупредит в C# 8+)
string name;        // null
int[] numbers;      // null

// Value types - нулевые значения
int count;          // 0
bool isActive;      // false
DateTime created;   // 01.01.0001 00:00:00

// Nullable value types
int? nullableCount; // null
DateTime? date;     // null

// Default
var items = new List<string>(); // Пустая коллекция
var dict = new Dictionary<string, int>(); // Пустой словарь

// Проблема: null reference exceptions
public class UserService
{
    private ILogger _logger; // null!

    public void DoSomething()
    {
        _logger.LogInfo("test"); // NullReferenceException
    }
}
```

### Go zero values

```go
// Все типы имеют zero value - безопасны для использования
var user *User      // nil
var name string     // "" (пустая строка)
var numbers []int   // nil (но можно итерировать!)
var count int       // 0
var isActive bool   // false
var created time.Time // 0001-01-01 00:00:00 UTC

// Zero values полезны!
var buffer bytes.Buffer  // Готов к использованию
buffer.WriteString("hello") // Работает без инициализации

var wg sync.WaitGroup    // Готов к использованию
wg.Add(1)
wg.Done()

// nil slice безопасен
var items []string       // nil
fmt.Println(len(items))  // 0 (не паника!)
for _, item := range items { // Корректно (ничего не выполнится)
    fmt.Println(item)
}

// nil map - небезопасен для записи!
var counts map[string]int // nil
value := counts["key"]     // 0 (безопасно)
counts["key"] = 1          // ПАНИКА! assignment to entry in nil map

// Правильно
counts = make(map[string]int)
counts["key"] = 1           // OK
```

### Идиоматичное использование zero values

#### 1. Конструкторы через zero values

**C#**:
```csharp
public class Config
{
    public string Host { get; set; } = "localhost";
    public int Port { get; set; } = 8080;
    public TimeSpan Timeout { get; set; } = TimeSpan.FromSeconds(30);

    // Нужен конструктор для инициализации
    public Config()
    {
        // Уже инициализировано через initializers
    }
}
```

**Go** (идиоматично):
```go
type Config struct {
    Host    string        // "" если не указано
    Port    int           // 0 если не указано
    Timeout time.Duration // 0 если не указано
}

// Инициализация со значениями по умолчанию
func NewConfig() *Config {
    return &Config{
        Host:    "localhost",
        Port:    8080,
        Timeout: 30 * time.Second,
    }
}

// Или через functional options pattern (идиоматично)
type Option func(*Config)

func WithHost(host string) Option {
    return func(c *Config) {
        c.Host = host
    }
}

func WithPort(port int) Option {
    return func(c *Config) {
        c.Port = port
    }
}

func NewConfigWithOptions(opts ...Option) *Config {
    // Zero value как основа
    cfg := &Config{
        Host:    "localhost", // default
        Port:    8080,
        Timeout: 30 * time.Second,
    }

    for _, opt := range opts {
        opt(cfg)
    }

    return cfg
}

// Использование
cfg := NewConfigWithOptions(
    WithHost("example.com"),
    WithPort(9000),
)
```

#### 2. Проверка на zero value

**Go идиомы**:
```go
// Структуры
var t time.Time
if t.IsZero() {  // Идиоматичная проверка
    t = time.Now()
}

// Указатели
var user *User
if user == nil {
    user = &User{Name: "Guest"}
}

// Слайсы
var items []string
if len(items) == 0 {  // Идиоматично (работает и для nil)
    items = []string{"default"}
}

// Мапы - осторожно!
var counts map[string]int
if counts == nil {
    counts = make(map[string]int)
}

// Каналы
var ch chan int
if ch == nil {
    ch = make(chan int, 10)
}
```

#### 3. Zero value в методах

```go
// sync.Mutex не требует инициализации
type Counter struct {
    mu    sync.Mutex // Zero value готов к использованию!
    count int
}

func (c *Counter) Increment() {
    c.mu.Lock()         // Работает сразу
    defer c.mu.Unlock()
    c.count++
}

// bytes.Buffer тоже
type Logger struct {
    buf bytes.Buffer // Zero value готов
}

func (l *Logger) Log(msg string) {
    l.buf.WriteString(msg) // Работает без make/new
}
```

### Сравнение

| Тип | C# default | Go zero value | Безопасность |
|-----|------------|---------------|--------------|
| **Числа** | 0 | 0 | ✅ Идентично |
| **bool** | false | false | ✅ Идентично |
| **string** | null | "" | ⚠️ В Go безопаснее |
| **Массивы** | null | zero values элементов | ✅ В Go инициализированы |
| **Слайсы** | null | nil (можно читать) | ⚠️ В Go безопаснее |
| **Мапы** | null | nil (нельзя писать) | ⚠️ В Go опаснее |
| **Указатели** | null | nil | ✅ Идентично |
| **Интерфейсы** | null | nil | ✅ Идентично |

> 💡 **Философия Go**: Zero value должен быть полезным. Проектируй типы так, чтобы zero value был готов к использованию.

---

## Видимость через регистр

### C# модификаторы доступа

```csharp
public class UserService
{
    // Public - доступен везде
    public string PublicField;

    // Private - только внутри класса
    private string _privateField;

    // Protected - класс и наследники
    protected string ProtectedField;

    // Internal - только в сборке
    internal string InternalField;

    // Protected internal - сборка + наследники
    protected internal string ProtectedInternalField;

    // Private protected - только наследники в сборке
    private protected string PrivateProtectedField;

    public void PublicMethod() { }
    private void PrivateMethod() { }
    internal void InternalMethod() { }
}
```

### Go видимость через регистр

```go
package user

// Exported (Public) - первая буква заглавная
type User struct {
    ID       int    // Exported поле
    Name     string // Exported поле
    email    string // unexported (private) поле
    password string // unexported поле
}

// Exported функция
func NewUser(name, email string) *User {
    return &User{
        Name:  name,
        email: email,
    }
}

// Exported метод
func (u *User) GetEmail() string {
    return u.email
}

// unexported метод
func (u *User) validatePassword(pwd string) bool {
    return u.password == hashPassword(pwd)
}

// unexported функция
func hashPassword(pwd string) string {
    // ...
}

// Exported константы
const MaxUsers = 1000
const DefaultTimeout = 30 * time.Second

// unexported константы
const minPasswordLength = 8
const saltSize = 32
```

### Идиоматичные паттерны видимости

#### 1. Инкапсуляция через unexported поля

**C#**:
```csharp
public class BankAccount
{
    private decimal _balance;

    public decimal Balance => _balance; // Read-only property

    public void Deposit(decimal amount)
    {
        if (amount <= 0)
            throw new ArgumentException("Amount must be positive");
        _balance += amount;
    }

    public void Withdraw(decimal amount)
    {
        if (amount > _balance)
            throw new InvalidOperationException("Insufficient funds");
        _balance -= amount;
    }
}
```

**Go** (идиоматично):
```go
package bank

type Account struct {
    id      string  // unexported - нельзя изменить снаружи
    balance float64 // unexported
}

func NewAccount(id string) *Account {
    return &Account{id: id, balance: 0}
}

// Exported getter
func (a *Account) Balance() float64 {
    return a.balance
}

// Exported методы для изменения
func (a *Account) Deposit(amount float64) error {
    if amount <= 0 {
        return errors.New("amount must be positive")
    }
    a.balance += amount
    return nil
}

func (a *Account) Withdraw(amount float64) error {
    if amount > a.balance {
        return errors.New("insufficient funds")
    }
    a.balance -= amount
    return nil
}
```

#### 2. Фабричные функции для валидации

```go
package config

// Структура с unexported полями
type Config struct {
    host string
    port int
    timeout time.Duration
}

// Exported геттеры
func (c *Config) Host() string        { return c.host }
func (c *Config) Port() int           { return c.port }
func (c *Config) Timeout() time.Duration { return c.timeout }

// Фабрика с валидацией
func NewConfig(host string, port int, timeout time.Duration) (*Config, error) {
    if host == "" {
        return nil, errors.New("host cannot be empty")
    }
    if port <= 0 || port > 65535 {
        return nil, errors.New("invalid port")
    }
    if timeout <= 0 {
        return nil, errors.New("timeout must be positive")
    }

    return &Config{
        host:    host,
        port:    port,
        timeout: timeout,
    }, nil
}

// Нельзя создать невалидный Config:
// cfg := &config.Config{host: "", port: -1} // ОШИБКА КОМПИЛЯЦИИ
```

#### 3. Internal packages (Go 1.4+)

```go
// Структура проекта:
// myapp/
//   cmd/
//     server/
//       main.go
//   internal/           // "internal" - специальное имя
//     database/
//       db.go           // Доступно только внутри myapp/
//     auth/
//       auth.go
//   pkg/
//     api/
//       api.go          // Публичное API

// internal/database/db.go
package database

// Экспортировано, но только внутри myapp/
type Connection struct {
    dsn string
}

func NewConnection(dsn string) *Connection {
    return &Connection{dsn: dsn}
}

// cmd/server/main.go
package main

import "myapp/internal/database" // OK - внутри myapp/

func main() {
    db := database.NewConnection("...")
}

// Попытка использовать снаружи:
// otherproject/main.go
import "myapp/internal/database" // ОШИБКА КОМПИЛЯЦИИ
```

### Сравнение уровней доступа

| C# | Go | Описание |
|----|----|----|
| `public` | `Exported` (заглавная) | Доступно везде |
| `private` | `unexported` (строчная) | Только в пакете |
| `internal` | `internal/` package | Только в модуле |
| `protected` | ❌ Нет | Нет наследования |
| `protected internal` | ❌ Нет | Нет аналога |
| `private protected` | ❌ Нет | Нет аналога |

> ⚠️ **Важно**: В Go нет `protected` - нет наследования, нет необходимости.

---

## Идиоматичные различия

### 1. Обработка nil

**C# - defensive programming**:
```csharp
public class OrderService
{
    private readonly ILogger _logger;

    public OrderService(ILogger logger)
    {
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public Order ProcessOrder(Order order)
    {
        if (order == null)
            throw new ArgumentNullException(nameof(order));

        if (order.Items == null || !order.Items.Any())
            throw new ArgumentException("Order must have items");

        _logger?.LogInformation($"Processing order {order.Id}");

        // ...
    }
}
```

**Go - early return**:
```go
type OrderService struct {
    logger *Logger
}

func NewOrderService(logger *Logger) *OrderService {
    if logger == nil {
        panic("logger cannot be nil") // Или вернуть error
    }
    return &OrderService{logger: logger}
}

func (s *OrderService) ProcessOrder(order *Order) (*Order, error) {
    if order == nil {
        return nil, errors.New("order is nil")
    }

    if len(order.Items) == 0 {
        return nil, errors.New("order must have items")
    }

    s.logger.Info("processing order", "id", order.ID)

    // ...
    return order, nil
}
```

### 2. Коллекции и LINQ vs циклы

**C# - LINQ**:
```csharp
var activeUsers = users
    .Where(u => u.IsActive)
    .Select(u => new UserDTO
    {
        Id = u.Id,
        Name = u.Name
    })
    .OrderBy(u => u.Name)
    .ToList();

var totalAmount = orders
    .Where(o => o.Status == OrderStatus.Completed)
    .Sum(o => o.Amount);

var usersByCity = users
    .GroupBy(u => u.City)
    .ToDictionary(g => g.Key, g => g.ToList());
```

**Go - явные циклы** (идиоматично):
```go
// Фильтрация + маппинг
activeUsers := make([]UserDTO, 0, len(users))
for _, u := range users {
    if u.IsActive {
        activeUsers = append(activeUsers, UserDTO{
            ID:   u.ID,
            Name: u.Name,
        })
    }
}

// Сортировка
sort.Slice(activeUsers, func(i, j int) bool {
    return activeUsers[i].Name < activeUsers[j].Name
})

// Агрегация
var totalAmount float64
for _, o := range orders {
    if o.Status == OrderStatusCompleted {
        totalAmount += o.Amount
    }
}

// Группировка
usersByCity := make(map[string][]*User)
for _, u := range users {
    usersByCity[u.City] = append(usersByCity[u.City], u)
}
```

**Go - функциональный стиль** (менее идиоматично, но возможно):
```go
// Можно создать вспомогательные функции
func Filter[T any](slice []T, predicate func(T) bool) []T {
    result := make([]T, 0)
    for _, item := range slice {
        if predicate(item) {
            result = append(result, item)
        }
    }
    return result
}

func Map[T, U any](slice []T, mapper func(T) U) []U {
    result := make([]U, len(slice))
    for i, item := range slice {
        result[i] = mapper(item)
    }
    return result
}

// Использование
activeUsers := Filter(users, func(u User) bool { return u.IsActive })
userDTOs := Map(activeUsers, func(u User) UserDTO {
    return UserDTO{ID: u.ID, Name: u.Name}
})
```

> 💡 **В Go предпочитают явные циклы** - они понятнее и производительнее.

### 3. Async/Await vs Goroutines

**C# - async/await**:
```csharp
public async Task<User> GetUserWithOrdersAsync(int userId)
{
    var user = await _userRepository.GetByIdAsync(userId);

    var ordersTask = _orderRepository.GetByUserIdAsync(userId);
    var paymentsTask = _paymentRepository.GetByUserIdAsync(userId);

    await Task.WhenAll(ordersTask, paymentsTask);

    user.Orders = ordersTask.Result;
    user.Payments = paymentsTask.Result;

    return user;
}

// Обработка нескольких пользователей параллельно
public async Task<List<User>> GetMultipleUsersAsync(List<int> userIds)
{
    var tasks = userIds.Select(id => GetUserWithOrdersAsync(id));
    var users = await Task.WhenAll(tasks);
    return users.ToList();
}
```

**Go - goroutines + channels**:
```go
func (s *Service) GetUserWithOrders(ctx context.Context, userID int) (*User, error) {
    user, err := s.userRepo.GetByID(ctx, userID)
    if err != nil {
        return nil, err
    }

    // Параллельные запросы
    type ordersResult struct {
        orders []*Order
        err    error
    }
    type paymentsResult struct {
        payments []*Payment
        err      error
    }

    ordersCh := make(chan ordersResult, 1)
    paymentsCh := make(chan paymentsResult, 1)

    // Goroutine для заказов
    go func() {
        orders, err := s.orderRepo.GetByUserID(ctx, userID)
        ordersCh <- ordersResult{orders: orders, err: err}
    }()

    // Goroutine для платежей
    go func() {
        payments, err := s.paymentRepo.GetByUserID(ctx, userID)
        paymentsCh <- paymentsResult{payments: payments, err: err}
    }()

    // Ожидание результатов
    ordersRes := <-ordersCh
    paymentsRes := <-paymentsCh

    if ordersRes.err != nil {
        return nil, fmt.Errorf("get orders: %w", ordersRes.err)
    }
    if paymentsRes.err != nil {
        return nil, fmt.Errorf("get payments: %w", paymentsRes.err)
    }

    user.Orders = ordersRes.orders
    user.Payments = paymentsRes.payments

    return user, nil
}

// Обработка нескольких пользователей параллельно
func (s *Service) GetMultipleUsers(ctx context.Context, userIDs []int) ([]*User, error) {
    type result struct {
        user *User
        err  error
    }

    results := make(chan result, len(userIDs))

    // Запускаем goroutine для каждого пользователя
    for _, id := range userIDs {
        go func(userID int) {
            user, err := s.GetUserWithOrders(ctx, userID)
            results <- result{user: user, err: err}
        }(id)
    }

    // Собираем результаты
    users := make([]*User, 0, len(userIDs))
    for i := 0; i < len(userIDs); i++ {
        res := <-results
        if res.err != nil {
            return nil, res.err
        }
        users = append(users, res.user)
    }

    return users, nil
}
```

**Go - errgroup (идиоматично для параллельных задач)**:
```go
import "golang.org/x/sync/errgroup"

func (s *Service) GetUserWithOrders(ctx context.Context, userID int) (*User, error) {
    user, err := s.userRepo.GetByID(ctx, userID)
    if err != nil {
        return nil, err
    }

    var orders []*Order
    var payments []*Payment

    g, ctx := errgroup.WithContext(ctx)

    // Goroutine для заказов
    g.Go(func() error {
        var err error
        orders, err = s.orderRepo.GetByUserID(ctx, userID)
        return err
    })

    // Goroutine для платежей
    g.Go(func() error {
        var err error
        payments, err = s.paymentRepo.GetByUserID(ctx, userID)
        return err
    })

    // Ожидаем завершения всех goroutines
    if err := g.Wait(); err != nil {
        return nil, err
    }

    user.Orders = orders
    user.Payments = payments

    return user, nil
}

// Обработка нескольких пользователей с ограничением параллелизма
func (s *Service) GetMultipleUsers(ctx context.Context, userIDs []int) ([]*User, error) {
    users := make([]*User, len(userIDs))

    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(10) // Максимум 10 параллельных запросов

    for i, id := range userIDs {
        i, id := i, id // Захват переменных цикла
        g.Go(func() error {
            user, err := s.GetUserWithOrders(ctx, id)
            if err != nil {
                return err
            }
            users[i] = user
            return nil
        })
    }

    if err := g.Wait(); err != nil {
        return nil, err
    }

    return users, nil
}
```

### 4. Конструкторы и инициализация

**C# - конструкторы**:
```csharp
public class UserService
{
    private readonly IUserRepository _repository;
    private readonly ILogger _logger;
    private readonly ICache _cache;

    // Основной конструктор
    public UserService(
        IUserRepository repository,
        ILogger logger,
        ICache cache)
    {
        _repository = repository ?? throw new ArgumentNullException(nameof(repository));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        _cache = cache ?? throw new ArgumentNullException(nameof(cache));
    }

    // Конструктор с default значениями
    public UserService(IUserRepository repository, ILogger logger)
        : this(repository, logger, new NullCache())
    {
    }

    // Object initializer syntax
    var config = new Config
    {
        Host = "localhost",
        Port = 8080,
        Timeout = TimeSpan.FromSeconds(30)
    };
}
```

**Go - функции New**:
```go
type UserService struct {
    repository UserRepository
    logger     *Logger
    cache      Cache
}

// Основной конструктор
func NewUserService(repo UserRepository, logger *Logger, cache Cache) *UserService {
    if repo == nil {
        panic("repository cannot be nil")
    }
    if logger == nil {
        panic("logger cannot be nil")
    }
    if cache == nil {
        panic("cache cannot be nil")
    }

    return &UserService{
        repository: repo,
        logger:     logger,
        cache:      cache,
    }
}

// Конструктор с default значениями
func NewUserServiceWithDefaults(repo UserRepository, logger *Logger) *UserService {
    return NewUserService(repo, logger, &NullCache{})
}

// Composite literal (аналог object initializer)
config := &Config{
    Host:    "localhost",
    Port:    8080,
    Timeout: 30 * time.Second,
}
```

**Go - Functional Options Pattern** (идиоматично для сложных случаев):
```go
type UserService struct {
    repository UserRepository
    logger     *Logger
    cache      Cache
    timeout    time.Duration
    maxRetries int
}

type Option func(*UserService)

func WithCache(cache Cache) Option {
    return func(s *UserService) {
        s.cache = cache
    }
}

func WithTimeout(timeout time.Duration) Option {
    return func(s *UserService) {
        s.timeout = timeout
    }
}

func WithMaxRetries(retries int) Option {
    return func(s *UserService) {
        s.maxRetries = retries
    }
}

func NewUserService(repo UserRepository, logger *Logger, opts ...Option) *UserService {
    if repo == nil || logger == nil {
        panic("repo and logger are required")
    }

    // Default значения
    s := &UserService{
        repository: repo,
        logger:     logger,
        cache:      &NullCache{},
        timeout:    30 * time.Second,
        maxRetries: 3,
    }

    // Применяем опции
    for _, opt := range opts {
        opt(s)
    }

    return s
}

// Использование
service := NewUserService(
    repo,
    logger,
    WithCache(redisCache),
    WithTimeout(60*time.Second),
    WithMaxRetries(5),
)
```

### 5. Generics (Обобщения)

**C# - generics везде**:
```csharp
public interface IRepository<T> where T : class
{
    Task<T> GetByIdAsync(int id);
    Task<IEnumerable<T>> GetAllAsync();
    Task<T> AddAsync(T entity);
}

public class Repository<T> : IRepository<T> where T : class
{
    private readonly DbContext _context;

    public async Task<T> GetByIdAsync(int id)
    {
        return await _context.Set<T>().FindAsync(id);
    }
}

// Generic методы
public static T FirstOrDefault<T>(IEnumerable<T> source, Func<T, bool> predicate)
{
    foreach (var item in source)
    {
        if (predicate(item))
            return item;
    }
    return default(T);
}

// Generic constraints
public class Cache<TKey, TValue> where TKey : IEquatable<TKey>
{
    private Dictionary<TKey, TValue> _items = new();

    public void Set(TKey key, TValue value) => _items[key] = value;
    public TValue Get(TKey key) => _items.TryGetValue(key, out var value) ? value : default;
}
```

**Go - generics (Go 1.18+)**:
```go
// Generic интерфейс
type Repository[T any] interface {
    GetByID(ctx context.Context, id int) (T, error)
    GetAll(ctx context.Context) ([]T, error)
    Add(ctx context.Context, entity T) (T, error)
}

// Generic struct
type GenericRepository[T any] struct {
    db *sql.DB
}

func (r *GenericRepository[T]) GetByID(ctx context.Context, id int) (T, error) {
    var entity T
    // ... реализация
    return entity, nil
}

// Generic функция
func FirstOrDefault[T any](slice []T, predicate func(T) bool) T {
    for _, item := range slice {
        if predicate(item) {
            return item
        }
    }
    var zero T
    return zero
}

// Generic constraints
type Equatable interface {
    Equal(other Equatable) bool
}

type Cache[K comparable, V any] struct {
    items map[K]V
    mu    sync.RWMutex
}

func NewCache[K comparable, V any]() *Cache[K, V] {
    return &Cache[K, V]{
        items: make(map[K]V),
    }
}

func (c *Cache[K, V]) Set(key K, value V) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.items[key] = value
}

func (c *Cache[K, V]) Get(key K) (V, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    value, ok := c.items[key]
    return value, ok
}

// Использование
cache := NewCache[string, *User]()
cache.Set("user1", &User{Name: "John"})
user, ok := cache.Get("user1")
```

**Идиоматично в Go - interface{}**:
```go
// До generics (Go < 1.18) - и часто предпочитается сейчас
type Cache struct {
    items map[string]interface{}
    mu    sync.RWMutex
}

func (c *Cache) Set(key string, value interface{}) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.items[key] = value
}

func (c *Cache) Get(key string) (interface{}, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    value, ok := c.items[key]
    return value, ok
}

// Использование с type assertion
cache := &Cache{items: make(map[string]interface{})}
cache.Set("user1", &User{Name: "John"})
if value, ok := cache.Get("user1"); ok {
    if user, ok := value.(*User); ok {
        fmt.Println(user.Name)
    }
}
```

> 💡 **В Go**: Generics появились недавно (1.18). Многие библиотеки до сих пор используют `interface{}` + type assertions.

#### Почему Go так долго ждал generics

Команда Go намеренно откладывала добавление generics:
1. **Простота важнее**: Generics усложняют язык и компилятор
2. **Интерфейсы работали**: Для большинства задач `interface{}` + type assertion было достаточно
3. **Не хотели повторять ошибки**: Java generics с type erasure, C++ templates с cryptic errors

> ⚠️ **Важно**: Generics в Go — это **не** замена интерфейсам. Это дополнительный инструмент для случаев, когда нужна **type safety без runtime overhead**.

#### Type constraints

Constraints (ограничения) определяют, какие типы могут использоваться как type parameters.

```go
import "cmp"

// any — любой тип (аналог interface{})
func Print[T any](value T) {
    fmt.Println(value)
}

// comparable — типы, сравниваемые через == и !=
func Contains[T comparable](slice []T, target T) bool {
    for _, item := range slice {
        if item == target {
            return true
        }
    }
    return false
}

// cmp.Ordered — типы с операторами <, >, <=, >= (Go 1.21+)
func Min[T cmp.Ordered](a, b T) T {
    if a < b {
        return a
    }
    return b
}
```

**Сравнение constraints: C# vs Go**

| C# Constraint | Go Equivalent | Пример |
|---------------|---------------|--------|
| `where T : class` | Нет прямого аналога | — |
| `where T : new()` | Нет прямого аналога | — |
| `where T : IComparable<T>` | `[T cmp.Ordered]` | `Max[T cmp.Ordered](a, b T)` |
| `where T : IEquatable<T>` | `[T comparable]` | `Contains[T comparable](...)` |
| `where T : SomeInterface` | `[T SomeInterface]` | `[T io.Reader]` |
| `where T : BaseClass` | Нет (нет наследования) | — |

**Custom constraints:**

```go
// ~ означает "underlying type" — включает type aliases
type Number interface {
    ~int | ~int8 | ~int16 | ~int32 | ~int64 |
    ~uint | ~uint8 | ~uint16 | ~uint32 | ~uint64 |
    ~float32 | ~float64
}

func Sum[T Number](numbers []T) T {
    var total T
    for _, n := range numbers {
        total += n
    }
    return total
}

type MyInt int
sum := Sum([]MyInt{1, 2, 3})  // Работает благодаря ~int
```

#### Когда использовать generics

**Используйте generics для:**

1. **Структур данных (контейнеров)**:
```go
type Set[T comparable] struct {
    items map[T]struct{}
}

func NewSet[T comparable]() *Set[T] {
    return &Set[T]{items: make(map[T]struct{})}
}

func (s *Set[T]) Add(item T) { s.items[item] = struct{}{} }
func (s *Set[T]) Contains(item T) bool {
    _, ok := s.items[item]
    return ok
}
```

2. **Утилит для работы с коллекциями**:
```go
func Filter[T any](slice []T, predicate func(T) bool) []T {
    var result []T
    for _, item := range slice {
        if predicate(item) {
            result = append(result, item)
        }
    }
    return result
}

func Map[T, R any](slice []T, fn func(T) R) []R {
    result := make([]R, len(slice))
    for i, item := range slice {
        result[i] = fn(item)
    }
    return result
}
```

**НЕ используйте generics когда:**

```go
// ❌ Избыточно — достаточно конкретного типа
func ProcessUsers[T User](users []T) { ... }
// ✅ Проще
func ProcessUsers(users []User) { ... }

// ❌ Интерфейс понятнее
func Process[T interface{ Process() error }](item T) error {
    return item.Process()
}
// ✅ Классический Go-style
type Processor interface {
    Process() error
}
func Process(item Processor) error {
    return item.Process()
}

// ❌ Over-engineering для 1-2 типов
func FormatID[T int | int64 | string](id T) string { ... }
// ✅ Два простых метода
func FormatIntID(id int) string { ... }
func FormatStringID(id string) string { ... }
```

> ⚠️ **Правило для C# разработчиков**: В Go простой код предпочтительнее clever-кода. Если не уверены — начните без generics. Добавите позже, если действительно понадобится.

#### Performance и GC

Go использует **частичную мономорфизацию** (GCShape stenciling):

```go
// Компилятор создаёт отдельные версии для:
// - Non-pointer types (каждый размер отдельно)
// - Pointer types (все указатели используют одну версию)

// Process[int] и Process[int64] — разные версии
// Process[*User] и Process[*Order] — одна версия (оба pointer)
```

Performance penalty от generics в Go **минимален** (~3%). Не избегайте generics из соображений производительности — используйте их там, где они улучшают читаемость и type safety.

#### Self-referential generics (Go 1.26)

> 💡 **Для C# разработчиков**: Аналог recursive type constraints в C# — `where T : IComparable<T>`.

Go 1.26 добавил поддержку **рекурсивных generic constraints** — тип может ссылаться сам на себя в ограничении.

**C# — recursive type constraints (давно поддерживаются):**
```csharp
// T : IComparable<T> — рекурсивное ограничение
public interface ISortable<T> where T : ISortable<T>
{
    int CompareTo(T other);
}

public class Temperature : ISortable<Temperature>
{
    public int CompareTo(Temperature other) => this.Value.CompareTo(other.Value);
    public double Value { get; }
}
```

**Go 1.26 — self-referential generics:**
```go
// Интерфейс с рекурсивным ограничением
type Adder[A Adder[A]] interface {
    Add(A) A
}

// Реализация
type Vector struct{ X, Y float64 }

func (v Vector) Add(other Vector) Vector {
    return Vector{X: v.X + other.X, Y: v.Y + other.Y}
}

// Использование в generic функции
func Sum[A Adder[A]](items []A) A {
    var result A
    for _, item := range items {
        result = result.Add(item)
    }
    return result
}

total := Sum([]Vector{{1, 2}, {3, 4}, {5, 6}})
// total = {9, 12}
```

**Другой пример — Builder pattern:**
```go
// Типобезопасный Builder с method chaining
type Builder[B Builder[B]] interface {
    Set(key, value string) B
    Build() map[string]string
}

type QueryBuilder struct {
    params map[string]string
}

func (q *QueryBuilder) Set(key, value string) *QueryBuilder {
    q.params[key] = value
    return q
}

func (q *QueryBuilder) Build() map[string]string {
    return q.params
}
```

> ⚠️ **Осторожно**: Self-referential generics мощны, но усложняют код. Используйте только когда рекурсивное ограничение действительно необходимо для type safety.

### 6. Properties vs Getters/Setters

**C#**:
```csharp
public class User
{
    // Auto-property
    public string Name { get; set; }

    // Read-only property
    public int Age { get; }

    // Property with backing field
    private string _email;
    public string Email
    {
        get => _email;
        set
        {
            if (string.IsNullOrEmpty(value))
                throw new ArgumentException("Email cannot be empty");
            _email = value.ToLower();
        }
    }

    // Computed property
    public string FullInfo => $"{Name} ({Age})";

    // Init-only property (C# 9+)
    public DateTime CreatedAt { get; init; }
}

// Использование
var user = new User
{
    Name = "John",
    Email = "JOHN@EXAMPLE.COM", // Преобразуется в lowercase
    CreatedAt = DateTime.Now
};

Console.WriteLine(user.Email); // john@example.com
Console.WriteLine(user.FullInfo); // John (0)
```

**Go**:
```go
type User struct {
    name      string    // unexported
    age       int       // unexported
    email     string    // unexported
    createdAt time.Time // unexported
}

// Getters (без префикса "Get" - идиоматично)
func (u *User) Name() string {
    return u.name
}

func (u *User) Age() int {
    return u.age
}

func (u *User) Email() string {
    return u.email
}

func (u *User) CreatedAt() time.Time {
    return u.createdAt
}

// Setters (с валидацией)
func (u *User) SetName(name string) error {
    if name == "" {
        return errors.New("name cannot be empty")
    }
    u.name = name
    return nil
}

func (u *User) SetEmail(email string) error {
    if email == "" {
        return errors.New("email cannot be empty")
    }
    u.email = strings.ToLower(email)
    return nil
}

// Computed method (вместо property)
func (u *User) FullInfo() string {
    return fmt.Sprintf("%s (%d)", u.name, u.age)
}

// Конструктор для инициализации
func NewUser(name, email string, age int) (*User, error) {
    if name == "" {
        return nil, errors.New("name cannot be empty")
    }
    if email == "" {
        return nil, errors.New("email cannot be empty")
    }

    return &User{
        name:      name,
        email:     strings.ToLower(email),
        age:       age,
        createdAt: time.Now(),
    }, nil
}

// Использование
user, err := NewUser("John", "JOHN@EXAMPLE.COM", 30)
if err != nil {
    log.Fatal(err)
}

fmt.Println(user.Email())     // john@example.com
fmt.Println(user.FullInfo())  // John (30)

if err := user.SetEmail("new@example.com"); err != nil {
    log.Fatal(err)
}
```

**Go - Публичные поля** (когда валидация не нужна):
```go
type Point struct {
    X float64 // Публичное поле
    Y float64 // Публичное поле
}

// Простое использование
p := Point{X: 10, Y: 20}
p.X = 30 // Прямое изменение - нормально для простых данных
```

> 💡 **Идиома Go**: Геттеры без префикса `Get`, сеттеры с префиксом `Set`. Для простых данных - публичные поля.

---

## Практические примеры

### Пример 1: HTTP Handler

**C# (ASP.NET Core)**:
```csharp
[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    private readonly IUserService _userService;
    private readonly ILogger<UsersController> _logger;

    public UsersController(IUserService userService, ILogger<UsersController> logger)
    {
        _userService = userService;
        _logger = logger;
    }

    [HttpGet("{id}")]
    [ProducesResponseType(typeof(UserDTO), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<ActionResult<UserDTO>> GetUser(int id)
    {
        try
        {
            var user = await _userService.GetUserAsync(id);
            return Ok(user);
        }
        catch (UserNotFoundException ex)
        {
            _logger.LogWarning(ex, "User {UserId} not found", id);
            return NotFound(new { error = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting user {UserId}", id);
            return StatusCode(500, new { error = "Internal server error" });
        }
    }

    [HttpPost]
    [ProducesResponseType(typeof(UserDTO), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<UserDTO>> CreateUser([FromBody] CreateUserRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        try
        {
            var user = await _userService.CreateUserAsync(request);
            return CreatedAtAction(nameof(GetUser), new { id = user.Id }, user);
        }
        catch (ValidationException ex)
        {
            return BadRequest(new { error = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating user");
            return StatusCode(500, new { error = "Internal server error" });
        }
    }
}
```

**Go (идиоматично)**:
```go
type UserHandler struct {
    service *UserService
    logger  *slog.Logger
}

func NewUserHandler(service *UserService, logger *slog.Logger) *UserHandler {
    return &UserHandler{
        service: service,
        logger:  logger,
    }
}

func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
    // Извлекаем ID из URL
    idStr := r.PathValue("id") // Go 1.22+
    id, err := strconv.Atoi(idStr)
    if err != nil {
        h.respondError(w, http.StatusBadRequest, "invalid user ID")
        return
    }

    // Получаем пользователя
    user, err := h.service.GetUser(r.Context(), id)
    if err != nil {
        if errors.Is(err, ErrUserNotFound) {
            h.logger.Warn("user not found", "id", id)
            h.respondError(w, http.StatusNotFound, "user not found")
            return
        }

        h.logger.Error("get user failed", "id", id, "error", err)
        h.respondError(w, http.StatusInternalServerError, "internal server error")
        return
    }

    h.respondJSON(w, http.StatusOK, user)
}

func (h *UserHandler) CreateUser(w http.ResponseWriter, r *http.Request) {
    var req CreateUserRequest

    // Декодируем JSON
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        h.respondError(w, http.StatusBadRequest, "invalid request body")
        return
    }

    // Валидация
    if err := req.Validate(); err != nil {
        h.respondError(w, http.StatusBadRequest, err.Error())
        return
    }

    // Создаём пользователя
    user, err := h.service.CreateUser(r.Context(), req)
    if err != nil {
        if errors.Is(err, ErrValidation) {
            h.respondError(w, http.StatusBadRequest, err.Error())
            return
        }

        h.logger.Error("create user failed", "error", err)
        h.respondError(w, http.StatusInternalServerError, "internal server error")
        return
    }

    w.Header().Set("Location", fmt.Sprintf("/api/users/%d", user.ID))
    h.respondJSON(w, http.StatusCreated, user)
}

// Вспомогательные методы
func (h *UserHandler) respondJSON(w http.ResponseWriter, status int, data interface{}) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(data)
}

func (h *UserHandler) respondError(w http.ResponseWriter, status int, message string) {
    h.respondJSON(w, status, map[string]string{"error": message})
}

// Регистрация маршрутов
func (h *UserHandler) RegisterRoutes(mux *http.ServeMux) {
    mux.HandleFunc("GET /api/users/{id}", h.GetUser)
    mux.HandleFunc("POST /api/users", h.CreateUser)
}
```

### Пример 2: Работа с базой данных

**C# (Entity Framework)**:
```csharp
public class UserRepository : IUserRepository
{
    private readonly AppDbContext _context;

    public UserRepository(AppDbContext context)
    {
        _context = context;
    }

    public async Task<User> GetByIdAsync(int id)
    {
        return await _context.Users
            .Include(u => u.Orders)
            .Include(u => u.Profile)
            .FirstOrDefaultAsync(u => u.Id == id);
    }

    public async Task<IEnumerable<User>> GetActiveUsersAsync()
    {
        return await _context.Users
            .Where(u => u.IsActive && u.DeletedAt == null)
            .OrderBy(u => u.CreatedAt)
            .ToListAsync();
    }

    public async Task<User> CreateAsync(User user)
    {
        _context.Users.Add(user);
        await _context.SaveChangesAsync();
        return user;
    }

    public async Task<bool> UpdateAsync(User user)
    {
        _context.Entry(user).State = EntityState.Modified;

        try
        {
            await _context.SaveChangesAsync();
            return true;
        }
        catch (DbUpdateConcurrencyException)
        {
            return false;
        }
    }
}
```

**Go (database/sql)**:
```go
type UserRepository struct {
    db *sql.DB
}

func NewUserRepository(db *sql.DB) *UserRepository {
    return &UserRepository{db: db}
}

func (r *UserRepository) GetByID(ctx context.Context, id int) (*User, error) {
    query := `
        SELECT u.id, u.name, u.email, u.is_active, u.created_at,
               o.id, o.amount, o.status,
               p.id, p.bio, p.avatar_url
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        LEFT JOIN profiles p ON u.id = p.user_id
        WHERE u.id = $1
    `

    var user User
    var orders []Order
    var profile Profile

    rows, err := r.db.QueryContext(ctx, query, id)
    if err != nil {
        return nil, fmt.Errorf("query user: %w", err)
    }
    defer rows.Close()

    // Сканирование результатов...
    // (упрощено для примера)

    if err := rows.Err(); err != nil {
        return nil, fmt.Errorf("scan rows: %w", err)
    }

    user.Orders = orders
    user.Profile = &profile

    return &user, nil
}

func (r *UserRepository) GetActiveUsers(ctx context.Context) ([]*User, error) {
    query := `
        SELECT id, name, email, is_active, created_at
        FROM users
        WHERE is_active = true AND deleted_at IS NULL
        ORDER BY created_at
    `

    rows, err := r.db.QueryContext(ctx, query)
    if err != nil {
        return nil, fmt.Errorf("query active users: %w", err)
    }
    defer rows.Close()

    var users []*User
    for rows.Next() {
        var u User
        if err := rows.Scan(&u.ID, &u.Name, &u.Email, &u.IsActive, &u.CreatedAt); err != nil {
            return nil, fmt.Errorf("scan user: %w", err)
        }
        users = append(users, &u)
    }

    if err := rows.Err(); err != nil {
        return nil, fmt.Errorf("iterate rows: %w", err)
    }

    return users, nil
}

func (r *UserRepository) Create(ctx context.Context, user *User) error {
    query := `
        INSERT INTO users (name, email, is_active, created_at)
        VALUES ($1, $2, $3, $4)
        RETURNING id
    `

    err := r.db.QueryRowContext(
        ctx,
        query,
        user.Name,
        user.Email,
        user.IsActive,
        user.CreatedAt,
    ).Scan(&user.ID)

    if err != nil {
        return fmt.Errorf("create user: %w", err)
    }

    return nil
}

func (r *UserRepository) Update(ctx context.Context, user *User) error {
    query := `
        UPDATE users
        SET name = $1, email = $2, is_active = $3
        WHERE id = $4
    `

    result, err := r.db.ExecContext(ctx, query, user.Name, user.Email, user.IsActive, user.ID)
    if err != nil {
        return fmt.Errorf("update user: %w", err)
    }

    rows, err := result.RowsAffected()
    if err != nil {
        return fmt.Errorf("get rows affected: %w", err)
    }

    if rows == 0 {
        return ErrUserNotFound
    }

    return nil
}
```

**Go (sqlx - более удобная библиотека)**:
```go
import "github.com/jmoiron/sqlx"

type UserRepository struct {
    db *sqlx.DB
}

func (r *UserRepository) GetByID(ctx context.Context, id int) (*User, error) {
    var user User
    query := `SELECT * FROM users WHERE id = $1`

    if err := r.db.GetContext(ctx, &user, query, id); err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, ErrUserNotFound
        }
        return nil, fmt.Errorf("get user: %w", err)
    }

    return &user, nil
}

func (r *UserRepository) GetActiveUsers(ctx context.Context) ([]*User, error) {
    var users []*User
    query := `
        SELECT * FROM users
        WHERE is_active = true AND deleted_at IS NULL
        ORDER BY created_at
    `

    if err := r.db.SelectContext(ctx, &users, query); err != nil {
        return nil, fmt.Errorf("get active users: %w", err)
    }

    return users, nil
}
```

---

## Чек-лист перехода

### Ментальные сдвиги

- [ ] **Отказ от наследования**: Мыслю композицией, а не иерархиями
- [ ] **Явные ошибки**: Каждая функция с `error` требует проверки
- [ ] **Простота vs абстракции**: Предпочитаю понятный код сложным паттернам
- [ ] **Zero values**: Проектирую типы готовыми к использованию "из коробки"
- [ ] **Интерфейсы малы**: 1-3 метода, не больше
- [ ] **Видимость через регистр**: Привык к заглавным/строчным буквам

### Технические привычки

- [ ] **Error handling**: Пишу `if err != nil` после каждого вызова
- [ ] **Early returns**: Guard clauses вместо вложенных условий
- [ ] **Явные циклы**: Предпочитаю `for range` вместо LINQ
- [ ] **Goroutines + channels**: Понимаю, когда использовать вместо async/await
- [ ] **Context**: Передаю `ctx` первым параметром
- [ ] **Defer**: Использую для cleanup (Close, Unlock и т.д.)

### Инструменты

- [ ] **go fmt**: Автоформатирование (забыл про споры о стиле)
- [ ] **go vet**: Статический анализ
- [ ] **golangci-lint**: Линтеры
- [ ] **pprof**: Профилирование (CPU, память)
- [ ] **benchmarks**: `go test -bench`
- [ ] **race detector**: `go test -race`

### Библиотеки и экосистема

- [ ] Изучил стандартную библиотеку Go
- [ ] Знаю, когда использовать `interface{}` vs generics
- [ ] Понимаю работу с `context.Context`
- [ ] Освоил `errgroup` для параллельных задач
- [ ] Использую `slog` для структурированного логирования

---

## Итоги

### Что остаётся похожим

| Концепция | C# | Go |
|-----------|----|----|
| Типизация | Статическая, строгая | Статическая, строгая |
| Компиляция | Да (в IL, потом JIT) | Да (в нативный код) |
| GC | Да | Да |
| Указатели | Есть (unsafe) | Есть (повсеместно) |
| Интерфейсы | Есть | Есть |
| Пакеты/модули | Namespaces, NuGet | Packages, Go modules |

### Что радикально отличается

| Аспект | C# | Go |
|--------|----|----|
| **Парадигма** | ООП + функциональное | Процедурное + интерфейсы |
| **Наследование** | Есть | Нет |
| **Исключения** | Есть | Нет (только error) |
| **Async** | async/await | goroutines + channels |
| **Generics** | С начала (2.0) | С 1.18 (2022) |
| **Properties** | Есть | Нет (методы) |
| **LINQ** | Есть | Нет (циклы) |
| **Reflection** | Мощный | Ограниченный |

### Ключевые идиомы Go для C# разработчиков

1. **"Errors are values"** - обрабатывай явно, не полагайся на try-catch
2. **"Accept interfaces, return structs"** - гибкость на входе, конкретность на выходе
3. **"Make zero value useful"** - проектируй типы готовыми к работе
4. **"A little copying is better than a little dependency"** - дублирование > абстракция
5. **"Clear is better than clever"** - понятный код > умный код
6. **"Don't communicate by sharing memory, share memory by communicating"** - каналы > locks

---

## Следующие шаги

1. ✅ Прочитал и понял философию Go
2. 🎯 **Следующий раздел**: [1.4 Практика](04_practice.md) - применяем знания на реальных примерах
3. 📚 Дополнительное чтение:
   - [Effective Go](https://go.dev/doc/effective_go)
   - [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments)
   - [Go Proverbs](https://go-proverbs.github.io/)

---

**Вопросы?** Открой issue на [GitHub](https://github.com/AlexandrTolstuhin/csharp-to-go/issues)

[← Назад: Синтаксис и базовые концепции](02_syntax_basics.md) | [Вперёд: Практика →](04_practice.md)
