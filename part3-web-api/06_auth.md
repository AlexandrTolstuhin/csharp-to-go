# Аутентификация и авторизация

---

## Введение

> 💡 **Для C# разработчиков**: В ASP.NET Core аутентификация — встроенная инфраструктура: `AddAuthentication()`, `AddJwtBearer()`, атрибут `[Authorize]`, `ClaimsPrincipal`. В Go нет аналогичного фреймворка — вы собираете решение из отдельных библиотек и middleware. Это больше кода, но полный контроль.

Аутентификация отвечает на вопрос "кто ты?", авторизация — "что тебе можно?". В Go оба механизма реализуются через middleware — функции-обёртки над `http.Handler`.

### Что вы узнаете

- JWT: генерация, подпись и проверка токенов с `golang-jwt/jwt`
- Middleware для аутентификации в `net/http` и популярных роутерах
- Access token + Refresh token: реализация и паттерн ротации
- OAuth2: client credentials и authorization code flow
- RBAC: ролевая модель на основе claims
- Сравнение с C#: `[Authorize]`, `ClaimsPrincipal`, `IAuthenticationHandler`
- Типичные ошибки и как их избежать

### Сравнение подходов

| Аспект | ASP.NET Core | Go |
|--------|-------------|-----|
| JWT библиотека | Встроена (Microsoft.AspNetCore.Authentication.JwtBearer) | `github.com/golang-jwt/jwt/v5` |
| Middleware | `app.UseAuthentication()`, `app.UseAuthorization()` | `func(http.Handler) http.Handler` |
| Атрибут доступа | `[Authorize]`, `[Authorize(Roles="Admin")]` | Middleware с проверкой context |
| Текущий пользователь | `HttpContext.User` (ClaimsPrincipal) | `context.Value(userKey)` |
| OAuth2 | `AddOAuth()`, `AddOpenIdConnect()` | `golang.org/x/oauth2` |
| Хранение сессий | ASP.NET Session, IDistributedCache | Redis, DB — вручную |

---

## JWT: генерация и проверка

JWT (JSON Web Token) — стандарт `RFC 7519`. Токен состоит из трёх частей: header.payload.signature.

```bash
go get github.com/golang-jwt/jwt/v5
```

### Структура claims

```go
package auth

import (
    "time"

    "github.com/golang-jwt/jwt/v5"
)

// Claims — данные внутри токена
// Аналог C#: ClaimsPrincipal + набор Claim объектов
type Claims struct {
    UserID   int64    `json:"user_id"`
    Email    string   `json:"email"`
    Roles    []string `json:"roles"`
    // Стандартные JWT поля: exp, iat, iss, sub, jti
    jwt.RegisteredClaims
}
```

### Генерация HS256 токена (HMAC-SHA256)

```go
// TokenManager управляет созданием и проверкой токенов
type TokenManager struct {
    secret        []byte
    accessTTL     time.Duration
    refreshTTL    time.Duration
    issuer        string
}

func NewTokenManager(secret string, accessTTL, refreshTTL time.Duration, issuer string) *TokenManager {
    return &TokenManager{
        secret:     []byte(secret),
        accessTTL:  accessTTL,
        refreshTTL: refreshTTL,
        issuer:     issuer,
    }
}

// GenerateAccessToken создаёт access token с коротким временем жизни
func (m *TokenManager) GenerateAccessToken(userID int64, email string, roles []string) (string, error) {
    now := time.Now()
    claims := Claims{
        UserID: userID,
        Email:  email,
        Roles:  roles,
        RegisteredClaims: jwt.RegisteredClaims{
            Issuer:    m.issuer,
            Subject:   fmt.Sprintf("%d", userID),
            IssuedAt:  jwt.NewNumericDate(now),
            ExpiresAt: jwt.NewNumericDate(now.Add(m.accessTTL)),
            // jti — уникальный ID токена, нужен для отзыва
            ID: uuid.New().String(),
        },
    }

    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString(m.secret)
}

// ParseToken проверяет токен и возвращает claims
func (m *TokenManager) ParseToken(tokenStr string) (*Claims, error) {
    token, err := jwt.ParseWithClaims(tokenStr, &Claims{}, func(token *jwt.Token) (any, error) {
        // ✅ Критично: проверить алгоритм явно!
        // Атака "alg:none" — злоумышленник убирает подпись, меняя alg на "none"
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("неожиданный алгоритм подписи: %v", token.Header["alg"])
        }
        return m.secret, nil
    })
    if err != nil {
        return nil, fmt.Errorf("невалидный токен: %w", err)
    }

    claims, ok := token.Claims.(*Claims)
    if !ok || !token.Valid {
        return nil, fmt.Errorf("невалидные claims")
    }

    return claims, nil
}
```

```csharp
// C# — аналог TokenManager
// Конфигурация в Program.cs:
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options => {
        options.TokenValidationParameters = new TokenValidationParameters {
            ValidateIssuer = true,
            ValidIssuer = "myapp",
            ValidateAudience = false,
            ValidateLifetime = true,
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secret)),
            ClockSkew = TimeSpan.Zero,
        };
    });

// Генерация токена:
var tokenDescriptor = new SecurityTokenDescriptor {
    Subject = new ClaimsIdentity(new[] {
        new Claim(ClaimTypes.NameIdentifier, userId.ToString()),
        new Claim(ClaimTypes.Email, email),
        new Claim(ClaimTypes.Role, "admin"),
    }),
    Expires = DateTime.UtcNow.AddMinutes(15),
    SigningCredentials = new SigningCredentials(key, SecurityAlgorithms.HmacSha256Signature),
};
var tokenHandler = new JwtSecurityTokenHandler();
var token = tokenHandler.CreateToken(tokenDescriptor);
var tokenString = tokenHandler.WriteToken(token);
```

### RS256: асимметричный алгоритм (рекомендуется для production)

```go
import (
    "crypto/rsa"
    "os"

    "github.com/golang-jwt/jwt/v5"
)

// RSATokenManager использует RSA пару ключей
// Приватный ключ — только на сервере аутентификации
// Публичный ключ — можно раздать всем сервисам для проверки
type RSATokenManager struct {
    privateKey *rsa.PrivateKey
    publicKey  *rsa.PublicKey
    issuer     string
    accessTTL  time.Duration
}

func NewRSATokenManager(privateKeyPath, publicKeyPath, issuer string, ttl time.Duration) (*RSATokenManager, error) {
    privBytes, err := os.ReadFile(privateKeyPath)
    if err != nil {
        return nil, fmt.Errorf("чтение приватного ключа: %w", err)
    }
    privateKey, err := jwt.ParseRSAPrivateKeyFromPEM(privBytes)
    if err != nil {
        return nil, fmt.Errorf("парсинг приватного ключа: %w", err)
    }

    pubBytes, err := os.ReadFile(publicKeyPath)
    if err != nil {
        return nil, fmt.Errorf("чтение публичного ключа: %w", err)
    }
    publicKey, err := jwt.ParseRSAPublicKeyFromPEM(pubBytes)
    if err != nil {
        return nil, fmt.Errorf("парсинг публичного ключа: %w", err)
    }

    return &RSATokenManager{
        privateKey: privateKey,
        publicKey:  publicKey,
        issuer:     issuer,
        accessTTL:  ttl,
    }, nil
}

func (m *RSATokenManager) GenerateToken(userID int64, roles []string) (string, error) {
    claims := Claims{
        UserID: userID,
        Roles:  roles,
        RegisteredClaims: jwt.RegisteredClaims{
            Issuer:    m.issuer,
            IssuedAt:  jwt.NewNumericDate(time.Now()),
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(m.accessTTL)),
        },
    }
    token := jwt.NewWithClaims(jwt.SigningMethodRS256, claims)
    return token.SignedString(m.privateKey)
}

func (m *RSATokenManager) ParseToken(tokenStr string) (*Claims, error) {
    token, err := jwt.ParseWithClaims(tokenStr, &Claims{}, func(t *jwt.Token) (any, error) {
        // ✅ Проверяем алгоритм: только RSA
        if _, ok := t.Method.(*jwt.SigningMethodRSA); !ok {
            return nil, fmt.Errorf("неожиданный алгоритм: %v", t.Header["alg"])
        }
        return m.publicKey, nil
    })
    if err != nil {
        return nil, err
    }
    return token.Claims.(*Claims), nil
}
```

> 💡 **RS256 vs HS256**: HS256 — один секрет для подписи и проверки (симметричный). RS256 — приватный ключ для подписи, публичный для проверки. В микросервисной архитектуре RS256 безопаснее: каждый сервис получает только публичный ключ, не может сам выписывать токены.

---

## Middleware для аутентификации

Middleware в Go — функция вида `func(http.Handler) http.Handler`. Она оборачивает следующий обработчик, добавляя логику до и/или после него.

### Ключи контекста

```go
// contextKey — приватный тип для ключей контекста
// Предотвращает коллизии с другими пакетами
type contextKey struct{ name string }

var (
    userKey   = &contextKey{"user"}
    claimsKey = &contextKey{"claims"}
)

// UserFromContext извлекает пользователя из контекста
func UserFromContext(ctx context.Context) (*Claims, bool) {
    claims, ok := ctx.Value(claimsKey).(*Claims)
    return claims, ok
}

// WithClaims добавляет claims в контекст
func WithClaims(ctx context.Context, claims *Claims) context.Context {
    return context.WithValue(ctx, claimsKey, claims)
}
```

```csharp
// C# аналог — HttpContext.User
// В контроллере:
var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
var roles = User.FindAll(ClaimTypes.Role).Select(c => c.Value);
```

### Middleware для net/http

```go
// AuthMiddleware проверяет JWT токен из заголовка Authorization
func AuthMiddleware(tokenManager *TokenManager) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            // Извлечь токен из заголовка: "Authorization: Bearer <token>"
            authHeader := r.Header.Get("Authorization")
            if authHeader == "" {
                http.Error(w, `{"error":"токен не предоставлен"}`, http.StatusUnauthorized)
                return
            }

            // ✅ Проверить формат "Bearer <token>"
            const prefix = "Bearer "
            if !strings.HasPrefix(authHeader, prefix) {
                http.Error(w, `{"error":"неверный формат токена"}`, http.StatusUnauthorized)
                return
            }
            tokenStr := authHeader[len(prefix):]

            // Проверить токен
            claims, err := tokenManager.ParseToken(tokenStr)
            if err != nil {
                http.Error(w, `{"error":"невалидный токен"}`, http.StatusUnauthorized)
                return
            }

            // Добавить claims в контекст
            ctx := WithClaims(r.Context(), claims)
            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }
}

// Использование с стандартным ServeMux (Go 1.22+)
func main() {
    tokenManager := NewTokenManager(os.Getenv("JWT_SECRET"), 15*time.Minute, 7*24*time.Hour, "myapp")

    mux := http.NewServeMux()

    // Публичные маршруты
    mux.HandleFunc("POST /api/auth/login", loginHandler(tokenManager))
    mux.HandleFunc("POST /api/auth/refresh", refreshHandler(tokenManager))

    // Защищённые маршруты — оборачиваем AuthMiddleware
    protectedMux := http.NewServeMux()
    protectedMux.HandleFunc("GET /api/users/me", meHandler)
    protectedMux.HandleFunc("GET /api/orders", ordersHandler)

    mux.Handle("/api/", AuthMiddleware(tokenManager)(protectedMux))

    http.ListenAndServe(":8080", mux)
}
```

### Middleware для chi роутера

```go
import "github.com/go-chi/chi/v5"

func setupRouter(tokenManager *TokenManager) http.Handler {
    r := chi.NewRouter()

    // Глобальные middleware
    r.Use(middleware.Logger)
    r.Use(middleware.Recoverer)

    // Публичные маршруты
    r.Post("/api/auth/login", loginHandler(tokenManager))
    r.Post("/api/auth/refresh", refreshHandler(tokenManager))

    // Защищённые маршруты — группа с middleware
    r.Group(func(r chi.Router) {
        r.Use(AuthMiddleware(tokenManager))

        r.Get("/api/users/me", meHandler)
        r.Get("/api/orders", ordersHandler)

        // Маршруты только для администраторов
        r.Group(func(r chi.Router) {
            r.Use(RoleMiddleware("admin"))
            r.Get("/api/admin/users", adminUsersHandler)
            r.Delete("/api/admin/users/{id}", adminDeleteUserHandler)
        })
    })

    return r
}
```

### Обработчики с использованием контекста

```go
// meHandler — получить данные текущего пользователя
func meHandler(w http.ResponseWriter, r *http.Request) {
    claims, ok := UserFromContext(r.Context())
    if !ok {
        // Этого не должно случиться — middleware уже проверил
        http.Error(w, "unauthorized", http.StatusUnauthorized)
        return
    }

    response := map[string]any{
        "user_id": claims.UserID,
        "email":   claims.Email,
        "roles":   claims.Roles,
    }
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response)
}

// loginHandler — аутентификация и выдача токенов
func loginHandler(tm *TokenManager) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        var req struct {
            Email    string `json:"email"`
            Password string `json:"password"`
        }
        if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
            http.Error(w, "неверный запрос", http.StatusBadRequest)
            return
        }

        // В реальном приложении: проверить пароль через bcrypt
        user, err := findUserByEmail(r.Context(), req.Email)
        if err != nil || !checkPassword(user.PasswordHash, req.Password) {
            http.Error(w, "неверный email или пароль", http.StatusUnauthorized)
            return
        }

        accessToken, err := tm.GenerateAccessToken(user.ID, user.Email, user.Roles)
        if err != nil {
            http.Error(w, "внутренняя ошибка", http.StatusInternalServerError)
            return
        }

        refreshToken, err := generateRefreshToken()
        if err != nil {
            http.Error(w, "внутренняя ошибка", http.StatusInternalServerError)
            return
        }

        // Сохранить refresh token в БД/Redis
        if err := saveRefreshToken(r.Context(), user.ID, refreshToken, tm.refreshTTL); err != nil {
            http.Error(w, "внутренняя ошибка", http.StatusInternalServerError)
            return
        }

        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(map[string]string{
            "access_token":  accessToken,
            "refresh_token": refreshToken,
            "token_type":    "Bearer",
        })
    }
}
```

---

## Access Token + Refresh Token

### Модель токенов

```go
// RefreshToken — запись в БД/Redis
type RefreshToken struct {
    Token     string    // случайная строка (uuid или crypto/rand)
    UserID    int64
    ExpiresAt time.Time
    CreatedAt time.Time
    // Для ротации: токен однократного использования
    Used bool
}

// generateRefreshToken создаёт случайный токен
func generateRefreshToken() (string, error) {
    b := make([]byte, 32)
    if _, err := rand.Read(b); err != nil {
        return "", fmt.Errorf("генерация токена: %w", err)
    }
    return base64.URLEncoding.EncodeToString(b), nil
}
```

### Хранение в Redis

```go
import "github.com/redis/go-redis/v9"

type TokenStore struct {
    redis *redis.Client
}

// saveRefreshToken сохраняет refresh token в Redis
func (s *TokenStore) SaveRefreshToken(ctx context.Context, userID int64, token string, ttl time.Duration) error {
    key := fmt.Sprintf("refresh_token:%s", token)
    return s.redis.Set(ctx, key, userID, ttl).Err()
}

// GetUserID извлекает userID по refresh token
func (s *TokenStore) GetUserID(ctx context.Context, token string) (int64, error) {
    key := fmt.Sprintf("refresh_token:%s", token)
    val, err := s.redis.Get(ctx, key).Int64()
    if err == redis.Nil {
        return 0, fmt.Errorf("токен не найден или истёк")
    }
    return val, err
}

// RevokeRefreshToken отзывает refresh token
func (s *TokenStore) RevokeRefreshToken(ctx context.Context, token string) error {
    key := fmt.Sprintf("refresh_token:%s", token)
    return s.redis.Del(ctx, key).Err()
}

// RevokeAllUserTokens отзывает все токены пользователя (logout everywhere)
// Требует хранения set токенов per user:
// user_tokens:{userID} → set of token keys
func (s *TokenStore) RevokeAllUserTokens(ctx context.Context, userID int64) error {
    setKey := fmt.Sprintf("user_tokens:%d", userID)
    tokens, err := s.redis.SMembers(ctx, setKey).Result()
    if err != nil {
        return err
    }
    if len(tokens) == 0 {
        return nil
    }

    pipe := s.redis.Pipeline()
    for _, token := range tokens {
        pipe.Del(ctx, fmt.Sprintf("refresh_token:%s", token))
    }
    pipe.Del(ctx, setKey)
    _, err = pipe.Exec(ctx)
    return err
}
```

### Ротация refresh токенов (Refresh Token Rotation)

```go
// refreshHandler — обмен refresh token на новую пару токенов
// При каждом использовании refresh token выдаётся новый (ротация)
func refreshHandler(tm *TokenManager, store *TokenStore) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        var req struct {
            RefreshToken string `json:"refresh_token"`
        }
        if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
            http.Error(w, "неверный запрос", http.StatusBadRequest)
            return
        }

        // Найти userID по refresh token
        userID, err := store.GetUserID(r.Context(), req.RefreshToken)
        if err != nil {
            // ✅ Одинаковый ответ — не раскрываем причину
            http.Error(w, `{"error":"невалидный токен"}`, http.StatusUnauthorized)
            return
        }

        // Отозвать использованный токен (ротация)
        if err := store.RevokeRefreshToken(r.Context(), req.RefreshToken); err != nil {
            http.Error(w, "внутренняя ошибка", http.StatusInternalServerError)
            return
        }

        // Получить данные пользователя для нового токена
        user, err := findUserByID(r.Context(), userID)
        if err != nil {
            http.Error(w, "пользователь не найден", http.StatusUnauthorized)
            return
        }

        // Выдать новую пару токенов
        newAccessToken, err := tm.GenerateAccessToken(user.ID, user.Email, user.Roles)
        if err != nil {
            http.Error(w, "внутренняя ошибка", http.StatusInternalServerError)
            return
        }

        newRefreshToken, err := generateRefreshToken()
        if err != nil {
            http.Error(w, "внутренняя ошибка", http.StatusInternalServerError)
            return
        }

        if err := store.SaveRefreshToken(r.Context(), user.ID, newRefreshToken, tm.refreshTTL); err != nil {
            http.Error(w, "внутренняя ошибка", http.StatusInternalServerError)
            return
        }

        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(map[string]string{
            "access_token":  newAccessToken,
            "refresh_token": newRefreshToken,
        })
    }
}
```

```csharp
// C# — refresh token в ASP.NET Core Identity
// Identity встроено поддерживает refresh tokens через
// UserManager и SignInManager, но логика ротации — ваша:

[HttpPost("refresh")]
public async Task<IActionResult> Refresh([FromBody] RefreshRequest req)
{
    var principal = _tokenService.GetPrincipalFromExpiredToken(req.AccessToken);
    var userId = principal.FindFirstValue(ClaimTypes.NameIdentifier);

    var user = await _userManager.FindByIdAsync(userId);
    if (user == null || user.RefreshToken != req.RefreshToken
        || user.RefreshTokenExpiry <= DateTime.UtcNow)
        return Unauthorized();

    var newAccessToken = _tokenService.GenerateAccessToken(principal.Claims);
    var newRefreshToken = _tokenService.GenerateRefreshToken();

    user.RefreshToken = newRefreshToken;
    await _userManager.UpdateAsync(user);

    return Ok(new { accessToken = newAccessToken, refreshToken = newRefreshToken });
}
```

---

## OAuth2

### Client Credentials Flow (машина → машина)

```go
import "golang.org/x/oauth2/clientcredentials"

// OAuth2ClientCredentials — для сервис-к-сервис аутентификации
// C# аналог: IHttpClientFactory + NamedClient с OAuth2 handler
func newOAuth2Client(clientID, clientSecret, tokenURL string, scopes []string) *http.Client {
    config := clientcredentials.Config{
        ClientID:     clientID,
        ClientSecret: clientSecret,
        TokenURL:     tokenURL,
        Scopes:       scopes,
    }

    // TokenSource автоматически обновляет токен при истечении
    ctx := context.Background()
    return config.Client(ctx)
}

// Использование:
func main() {
    client := newOAuth2Client(
        os.Getenv("OAUTH2_CLIENT_ID"),
        os.Getenv("OAUTH2_CLIENT_SECRET"),
        "https://auth.example.com/oauth/token",
        []string{"api:read", "api:write"},
    )

    // client автоматически добавляет Bearer токен в запросы
    resp, err := client.Get("https://api.example.com/data")
    // ...
}
```

### Authorization Code Flow (пользователь → браузер → сервис)

```go
import "golang.org/x/oauth2"

// OAuth2Config — настройка для authorization code flow
// C# аналог: AddOAuth() или AddOpenIdConnect() в Program.cs
var oauth2Config = &oauth2.Config{
    ClientID:     os.Getenv("OAUTH2_CLIENT_ID"),
    ClientSecret: os.Getenv("OAUTH2_CLIENT_SECRET"),
    RedirectURL:  "https://myapp.com/auth/callback",
    Scopes:       []string{"openid", "profile", "email"},
    Endpoint: oauth2.Endpoint{
        AuthURL:  "https://auth.example.com/oauth/authorize",
        TokenURL: "https://auth.example.com/oauth/token",
    },
}

// Шаг 1: Редирект пользователя на страницу авторизации
func oauthLoginHandler(w http.ResponseWriter, r *http.Request) {
    // state — случайная строка для защиты от CSRF
    state, err := generateRefreshToken() // используем тот же генератор
    if err != nil {
        http.Error(w, "внутренняя ошибка", http.StatusInternalServerError)
        return
    }

    // Сохранить state в cookie/session для проверки на callback
    http.SetCookie(w, &http.Cookie{
        Name:     "oauth_state",
        Value:    state,
        MaxAge:   300, // 5 минут
        HttpOnly: true,
        Secure:   true,
        SameSite: http.SameSiteLaxMode,
    })

    url := oauth2Config.AuthCodeURL(state, oauth2.AccessTypeOffline)
    http.Redirect(w, r, url, http.StatusFound)
}

// Шаг 2: Обработка callback от провайдера
func oauthCallbackHandler(w http.ResponseWriter, r *http.Request) {
    // Проверить state против CSRF
    cookie, err := r.Cookie("oauth_state")
    if err != nil || cookie.Value != r.URL.Query().Get("state") {
        http.Error(w, "невалидный state", http.StatusBadRequest)
        return
    }

    // Обменять code на токен
    code := r.URL.Query().Get("code")
    token, err := oauth2Config.Exchange(r.Context(), code)
    if err != nil {
        http.Error(w, "ошибка обмена кода", http.StatusInternalServerError)
        return
    }

    // Получить данные пользователя через UserInfo endpoint
    client := oauth2Config.Client(r.Context(), token)
    resp, err := client.Get("https://auth.example.com/userinfo")
    if err != nil {
        http.Error(w, "ошибка получения профиля", http.StatusInternalServerError)
        return
    }
    defer resp.Body.Close()

    var userInfo struct {
        Sub   string `json:"sub"`
        Email string `json:"email"`
        Name  string `json:"name"`
    }
    if err := json.NewDecoder(resp.Body).Decode(&userInfo); err != nil {
        http.Error(w, "ошибка парсинга профиля", http.StatusInternalServerError)
        return
    }

    // Найти или создать пользователя, выдать собственный JWT
    // ...

    http.Redirect(w, r, "/dashboard", http.StatusFound)
}
```

---

## RBAC: Ролевая авторизация

### Определение ролей

```go
// Role — тип роли
type Role string

const (
    RoleAdmin  Role = "admin"
    RoleEditor Role = "editor"
    RoleViewer Role = "viewer"
)

// HasRole проверяет, есть ли у пользователя роль
func (c *Claims) HasRole(role Role) bool {
    for _, r := range c.Roles {
        if r == string(role) {
            return true
        }
    }
    return false
}

// HasAnyRole проверяет наличие хотя бы одной из ролей
func (c *Claims) HasAnyRole(roles ...Role) bool {
    for _, r := range roles {
        if c.HasRole(r) {
            return true
        }
    }
    return false
}
```

### Middleware для ролей

```go
// RoleMiddleware проверяет, что пользователь имеет одну из требуемых ролей
// Аналог C#: [Authorize(Roles = "Admin,Editor")]
func RoleMiddleware(roles ...Role) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            claims, ok := UserFromContext(r.Context())
            if !ok {
                http.Error(w, `{"error":"не авторизован"}`, http.StatusUnauthorized)
                return
            }

            if !claims.HasAnyRole(roles...) {
                http.Error(w, `{"error":"недостаточно прав"}`, http.StatusForbidden)
                return
            }

            next.ServeHTTP(w, r)
        })
    }
}

// Использование:
r.Group(func(r chi.Router) {
    r.Use(AuthMiddleware(tokenManager))

    // Только для просмотра
    r.With(RoleMiddleware(RoleViewer, RoleEditor, RoleAdmin)).
        Get("/api/reports", reportsHandler)

    // Только для редакторов и выше
    r.With(RoleMiddleware(RoleEditor, RoleAdmin)).
        Post("/api/articles", createArticleHandler)

    // Только для администраторов
    r.With(RoleMiddleware(RoleAdmin)).
        Delete("/api/articles/{id}", deleteArticleHandler)
})
```

```csharp
// C# — аналог через атрибуты и политики
// Атрибут:
[Authorize(Roles = "Admin,Editor")]
[HttpPost("articles")]
public IActionResult CreateArticle([FromBody] ArticleDto dto) { ... }

// Политика (более гибко):
builder.Services.AddAuthorization(options => {
    options.AddPolicy("CanDelete", policy =>
        policy.RequireRole("Admin")
              .RequireClaim("department", "editorial"));
});

[Authorize(Policy = "CanDelete")]
[HttpDelete("articles/{id}")]
public IActionResult DeleteArticle(int id) { ... }
```

### Permission-based авторизация (расширение RBAC)

```go
// Permission — конкретное разрешение
type Permission string

const (
    PermReadUsers   Permission = "users:read"
    PermWriteUsers  Permission = "users:write"
    PermDeleteUsers Permission = "users:delete"
    PermReadOrders  Permission = "orders:read"
)

// RolePermissions — маппинг ролей на разрешения
var RolePermissions = map[Role][]Permission{
    RoleAdmin:  {PermReadUsers, PermWriteUsers, PermDeleteUsers, PermReadOrders},
    RoleEditor: {PermReadUsers, PermReadOrders},
    RoleViewer: {PermReadOrders},
}

// HasPermission проверяет разрешение через роли
func (c *Claims) HasPermission(perm Permission) bool {
    for _, roleName := range c.Roles {
        perms, ok := RolePermissions[Role(roleName)]
        if !ok {
            continue
        }
        for _, p := range perms {
            if p == perm {
                return true
            }
        }
    }
    return false
}

// PermissionMiddleware — middleware для проверки разрешений
func PermissionMiddleware(perm Permission) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            claims, ok := UserFromContext(r.Context())
            if !ok {
                http.Error(w, `{"error":"не авторизован"}`, http.StatusUnauthorized)
                return
            }

            if !claims.HasPermission(perm) {
                http.Error(w, `{"error":"недостаточно прав"}`, http.StatusForbidden)
                return
            }

            next.ServeHTTP(w, r)
        })
    }
}
```

---

## Сравнение с C#

### Архитектурное сравнение

| Концепция | ASP.NET Core | Go |
|-----------|-------------|-----|
| Аутентификация | `AddAuthentication()` + схема | `AuthMiddleware` функция |
| Авторизация | `AddAuthorization()` + политики | `RoleMiddleware`, `PermissionMiddleware` |
| Текущий пользователь | `HttpContext.User` (ClaimsPrincipal) | `r.Context().Value(claimsKey)` |
| Атрибут доступа | `[Authorize]`, `[Authorize(Roles="Admin")]` | `r.Use(AuthMiddleware)`, `r.With(RoleMiddleware)` |
| Claims | `ClaimsPrincipal` + `IEnumerable<Claim>` | Кастомный `Claims` struct |
| Middleware pipeline | `app.UseAuthentication()`, `app.UseAuthorization()` | `func(http.Handler) http.Handler` |
| JWT библиотека | `Microsoft.AspNetCore.Authentication.JwtBearer` | `github.com/golang-jwt/jwt/v5` |
| OAuth2 клиент | `System.Net.Http.HttpClient` + `Microsoft.Identity.Client` | `golang.org/x/oauth2` |
| Refresh tokens | ASP.NET Identity (встроено) | Вручную: Redis/DB |

### Стек аутентификации по сценариям

```
Простой API (только JWT):
  Go:  TokenManager + AuthMiddleware
  C#:  AddJwtBearer() + [Authorize]

Микросервисы (сервис-к-сервис):
  Go:  clientcredentials.Config → oauth2.Client
  C#:  IHttpClientFactory + OAuthMessageHandler

Веб-приложение (пользователи):
  Go:  Authorization Code Flow + сессии/куки
  C#:  AddOpenIdConnect() + AddCookie()

SaaS с ролями:
  Go:  JWT Claims + RoleMiddleware + PermissionMiddleware
  C#:  [Authorize(Policy = "...")] + RequireRole/Claim
```

---

## Типичные ошибки

### 1. Секрет в коде

```go
// ❌ Никогда не хардкодить секрет
tokenManager := NewTokenManager("my-secret-key-123", ...)

// ✅ Загружать из переменных окружения
secret := os.Getenv("JWT_SECRET")
if secret == "" {
    log.Fatal("JWT_SECRET не задан")
}
if len(secret) < 32 {
    log.Fatal("JWT_SECRET слишком короткий: минимум 32 символа")
}
tokenManager := NewTokenManager(secret, ...)
```

### 2. Отсутствие проверки алгоритма (alg:none атака)

```go
// ❌ Опасно: принимает любой алгоритм, включая "none"
token, err := jwt.Parse(tokenStr, func(t *jwt.Token) (any, error) {
    return secret, nil // не проверяем t.Method!
})

// ✅ Всегда проверять метод подписи
token, err := jwt.ParseWithClaims(tokenStr, &Claims{}, func(t *jwt.Token) (any, error) {
    if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
        return nil, fmt.Errorf("неожиданный алгоритм: %v", t.Header["alg"])
    }
    return secret, nil
})
```

### 3. Токен в URL параметрах

```go
// ❌ Токен в URL — попадает в логи, history браузера, Referer header
// GET /api/data?token=eyJhbGciOiJIUzI1NiJ9...

// ✅ Только через Authorization заголовок
// GET /api/data
// Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...

// В обработчике — только из заголовка:
authHeader := r.Header.Get("Authorization")
```

### 4. Слишком длинный access token

```go
// ❌ Access token на 24 часа — если украден, долго работает
tokenManager := NewTokenManager(secret, 24*time.Hour, 30*24*time.Hour, "app")

// ✅ Access token короткий + refresh token для обновления
tokenManager := NewTokenManager(secret, 15*time.Minute, 7*24*time.Hour, "app")
```

### 5. Отсутствие проверки exp при ручном парсинге

```go
// ❌ Если используете jwt.Parse без WithExpirationRequired — токен не проверяется
// golang-jwt v5 проверяет exp по умолчанию, но явность не вредит:
token, err := jwt.ParseWithClaims(
    tokenStr,
    &Claims{},
    keyFunc,
    jwt.WithExpirationRequired(), // явно требовать поле exp
    jwt.WithIssuedAt(),           // проверять iat (не будущий токен)
)
```

### 6. Одинаковые ответы 401 не раскрывают причину

```go
// ❌ Раскрываем детали — помогаем атакующему
if tokenExpired {
    http.Error(w, "токен истёк", http.StatusUnauthorized)
    return
}
if tokenInvalid {
    http.Error(w, "неверная подпись", http.StatusUnauthorized)
    return
}

// ✅ Единый ответ, детали — в логах
claims, err := tokenManager.ParseToken(tokenStr)
if err != nil {
    // Логируем подробности для мониторинга
    slog.Warn("невалидный токен", "error", err, "ip", r.RemoteAddr)
    // Клиенту — только 401
    http.Error(w, `{"error":"не авторизован"}`, http.StatusUnauthorized)
    return
}
```

### 7. Хранение токена в localStorage (уязвимость XSS)

```go
// Документируйте для фронтенда:
// ❌ localStorage — доступен любому JS на странице (XSS)
// ✅ httpOnly cookie — недоступен JS, защищает от XSS

// Для API, где нужны httpOnly cookies:
func setTokenCookie(w http.ResponseWriter, token string) {
    http.SetCookie(w, &http.Cookie{
        Name:     "access_token",
        Value:    token,
        Path:     "/",
        MaxAge:   900, // 15 минут
        HttpOnly: true,  // ❌ для JS
        Secure:   true,  // только HTTPS
        SameSite: http.SameSiteStrictMode, // защита от CSRF
    })
}
```

---

## Полный пример: сервис аутентификации

```go
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "log/slog"
    "net/http"
    "os"
    "strings"
    "time"

    "github.com/go-chi/chi/v5"
    "github.com/go-chi/chi/v5/middleware"
    "github.com/golang-jwt/jwt/v5"
    "github.com/google/uuid"
)

// ---- Типы ----

type Claims struct {
    UserID int64    `json:"user_id"`
    Email  string   `json:"email"`
    Roles  []string `json:"roles"`
    jwt.RegisteredClaims
}

type contextKey struct{ name string }
var claimsKey = &contextKey{"claims"}

// ---- TokenManager ----

type TokenManager struct {
    secret     []byte
    accessTTL  time.Duration
    refreshTTL time.Duration
    issuer     string
}

func NewTokenManager(secret string, accessTTL, refreshTTL time.Duration) *TokenManager {
    return &TokenManager{
        secret:     []byte(secret),
        accessTTL:  accessTTL,
        refreshTTL: refreshTTL,
        issuer:     "myapp",
    }
}

func (m *TokenManager) Issue(userID int64, email string, roles []string) (string, error) {
    claims := Claims{
        UserID: userID,
        Email:  email,
        Roles:  roles,
        RegisteredClaims: jwt.RegisteredClaims{
            Issuer:    m.issuer,
            Subject:   fmt.Sprintf("%d", userID),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(m.accessTTL)),
            ID:        uuid.New().String(),
        },
    }
    return jwt.NewWithClaims(jwt.SigningMethodHS256, claims).SignedString(m.secret)
}

func (m *TokenManager) Parse(tokenStr string) (*Claims, error) {
    token, err := jwt.ParseWithClaims(tokenStr, &Claims{},
        func(t *jwt.Token) (any, error) {
            if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
                return nil, fmt.Errorf("неожиданный алгоритм: %v", t.Header["alg"])
            }
            return m.secret, nil
        },
        jwt.WithExpirationRequired(),
    )
    if err != nil {
        return nil, err
    }
    return token.Claims.(*Claims), nil
}

// ---- Middleware ----

func AuthMiddleware(tm *TokenManager) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            header := r.Header.Get("Authorization")
            if !strings.HasPrefix(header, "Bearer ") {
                jsonError(w, "не авторизован", http.StatusUnauthorized)
                return
            }

            claims, err := tm.Parse(header[7:])
            if err != nil {
                slog.Warn("невалидный токен", "err", err, "ip", r.RemoteAddr)
                jsonError(w, "не авторизован", http.StatusUnauthorized)
                return
            }

            ctx := context.WithValue(r.Context(), claimsKey, claims)
            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }
}

func RequireRole(role string) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            claims, ok := r.Context().Value(claimsKey).(*Claims)
            if !ok {
                jsonError(w, "не авторизован", http.StatusUnauthorized)
                return
            }
            for _, r := range claims.Roles {
                if r == role {
                    next.ServeHTTP(w, r.WithContext(r.Context()))
                    return
                }
            }
            jsonError(w, "недостаточно прав", http.StatusForbidden)
        })
    }
}

// ---- Хелперы ----

func jsonError(w http.ResponseWriter, msg string, code int) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(code)
    json.NewEncoder(w).Encode(map[string]string{"error": msg})
}

// ---- Роутер ----

func NewRouter(tm *TokenManager) http.Handler {
    r := chi.NewRouter()
    r.Use(middleware.Logger)
    r.Use(middleware.Recoverer)

    r.Post("/auth/login", func(w http.ResponseWriter, r *http.Request) {
        // В реальном приложении: проверить credentials в БД
        token, _ := tm.Issue(1, "user@example.com", []string{"viewer"})
        json.NewEncoder(w).Encode(map[string]string{"access_token": token})
    })

    r.Group(func(r chi.Router) {
        r.Use(AuthMiddleware(tm))

        r.Get("/me", func(w http.ResponseWriter, r *http.Request) {
            claims := r.Context().Value(claimsKey).(*Claims)
            json.NewEncoder(w).Encode(map[string]any{
                "user_id": claims.UserID,
                "email":   claims.Email,
                "roles":   claims.Roles,
            })
        })

        r.Group(func(r chi.Router) {
            r.Use(RequireRole("admin"))
            r.Get("/admin/users", func(w http.ResponseWriter, r *http.Request) {
                w.Write([]byte(`{"users": []}`))
            })
        })
    })

    return r
}

func main() {
    secret := os.Getenv("JWT_SECRET")
    if len(secret) < 32 {
        slog.Error("JWT_SECRET должен быть минимум 32 символа")
        os.Exit(1)
    }

    tm := NewTokenManager(secret, 15*time.Minute, 7*24*time.Hour)
    router := NewRouter(tm)

    slog.Info("сервер запущен", "addr", ":8080")
    if err := http.ListenAndServe(":8080", router); err != nil {
        slog.Error("ошибка запуска", "err", err)
        os.Exit(1)
    }
}
```

---

## Итог

| Задача | Библиотека / подход |
|--------|---------------------|
| JWT генерация и проверка | `github.com/golang-jwt/jwt/v5` |
| Middleware в net/http | `func(http.Handler) http.Handler` |
| Middleware в chi | `r.Use(...)`, `r.With(...)` |
| Передача user в контекст | `context.WithValue` + приватный ключ |
| Refresh tokens | Случайные байты + Redis/PostgreSQL |
| OAuth2 client credentials | `golang.org/x/oauth2/clientcredentials` |
| OAuth2 authorization code | `golang.org/x/oauth2` |
| RBAC | Claims + middleware |

**Ссылки**:
- [golang-jwt/jwt](https://github.com/golang-jwt/jwt)
- [golang.org/x/oauth2](https://pkg.go.dev/golang.org/x/oauth2)
- [RFC 7519: JSON Web Token](https://tools.ietf.org/html/rfc7519)
- [OWASP: JWT Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
