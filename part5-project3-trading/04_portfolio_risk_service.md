# Portfolio и Risk сервисы

---

## Введение

Portfolio и Risk — два сервиса, которые реагируют на события о совершённых сделках. Portfolio ведёт учёт позиций и PnL (Profit & Loss) в реальном времени. Risk следит за лимитами, считает VaR (Value at Risk) и выдаёт алерты при нарушениях.

> **Для C# разработчиков**: Оба сервиса — классические event-driven consumers. В C# это реализуется через `IHostedService` + MassTransit consumer. В Go — горутина + NATS subscriber + context для graceful shutdown. Логика одна и та же, но без фреймворкового overhead.

---

## Portfolio Service

### Доменная модель позиции

```go
// internal/position/model.go
package position

import (
    "sync"
    "time"

    "github.com/shopspring/decimal"
)

// Position — позиция клиента по инструменту
type Position struct {
    ClientID    string
    Symbol      string
    Quantity    decimal.Decimal // отрицательная = short позиция
    AvgPrice    decimal.Decimal // средняя цена открытия
    RealizedPnL decimal.Decimal // реализованный PnL (закрытые сделки)
    UpdatedAt   time.Time
}

// UnrealizedPnL — нереализованный PnL по текущей рыночной цене
func (p *Position) UnrealizedPnL(currentPrice decimal.Decimal) decimal.Decimal {
    if p.Quantity.IsZero() || p.AvgPrice.IsZero() {
        return decimal.Zero
    }
    // PnL = (текущая цена - средняя цена) * количество
    return currentPrice.Sub(p.AvgPrice).Mul(p.Quantity)
}

// TotalPnL — общий PnL
func (p *Position) TotalPnL(currentPrice decimal.Decimal) decimal.Decimal {
    return p.RealizedPnL.Add(p.UnrealizedPnL(currentPrice))
}

// PositionStore — хранилище позиций в памяти
// Все позиции клиентов кэшируем в Redis и снапшотируем в PostgreSQL
type PositionStore struct {
    mu        sync.RWMutex
    positions map[string]map[string]*Position // clientID → symbol → position
}

// NewPositionStore — создание хранилища
func NewPositionStore() *PositionStore {
    return &PositionStore{
        positions: make(map[string]map[string]*Position),
    }
}

// Get — получение позиции (nil если нет открытой позиции)
func (s *PositionStore) Get(clientID, symbol string) *Position {
    s.mu.RLock()
    defer s.mu.RUnlock()

    if clientPositions, ok := s.positions[clientID]; ok {
        if pos, ok := clientPositions[symbol]; ok {
            // Копируем, чтобы не отдавать указатель на внутренний объект
            cp := *pos
            return &cp
        }
    }
    return nil
}

// GetAll — все позиции клиента
func (s *PositionStore) GetAll(clientID string) []Position {
    s.mu.RLock()
    defer s.mu.RUnlock()

    clientPositions, ok := s.positions[clientID]
    if !ok {
        return nil
    }

    result := make([]Position, 0, len(clientPositions))
    for _, pos := range clientPositions {
        result = append(result, *pos)
    }
    return result
}

// Update — атомарное обновление позиции по сделке
func (s *PositionStore) Update(clientID, symbol string, fn func(*Position)) {
    s.mu.Lock()
    defer s.mu.Unlock()

    if _, ok := s.positions[clientID]; !ok {
        s.positions[clientID] = make(map[string]*Position)
    }

    pos, ok := s.positions[clientID][symbol]
    if !ok {
        pos = &Position{
            ClientID:  clientID,
            Symbol:    symbol,
            UpdatedAt: time.Now().UTC(),
        }
        s.positions[clientID][symbol] = pos
    }

    fn(pos)
    pos.UpdatedAt = time.Now().UTC()
}
```

### Расчёт PnL по сделкам

```go
// internal/position/calculator.go
package position

import (
    "github.com/shopspring/decimal"
)

// TradeInfo — информация о сделке для обновления позиции
type TradeInfo struct {
    ClientID  string
    Symbol    string
    Side      string // "BUY" или "SELL"
    Price     decimal.Decimal
    Quantity  decimal.Decimal
}

// Calculator — калькулятор позиций
type Calculator struct {
    store *PositionStore
}

// NewCalculator — создание калькулятора
func NewCalculator(store *PositionStore) *Calculator {
    return &Calculator{store: store}
}

// ApplyTrade — обновление позиции по совершённой сделке
// Использует алгоритм средней цены (average cost basis)
func (c *Calculator) ApplyTrade(trade TradeInfo) {
    c.store.Update(trade.ClientID, trade.Symbol, func(pos *Position) {
        if trade.Side == "BUY" {
            c.applyBuy(pos, trade)
        } else {
            c.applySell(pos, trade)
        }
    })
}

// applyBuy — покупка увеличивает/открывает long позицию
func (c *Calculator) applyBuy(pos *Position, trade TradeInfo) {
    if pos.Quantity.IsNegative() {
        // Закрываем short позицию
        if trade.Quantity.LessThanOrEqual(pos.Quantity.Abs()) {
            // Частичное закрытие short
            realizedPnL := pos.AvgPrice.Sub(trade.Price).Mul(trade.Quantity)
            pos.RealizedPnL = pos.RealizedPnL.Add(realizedPnL)
            pos.Quantity = pos.Quantity.Add(trade.Quantity)
            return
        }
        // Полное закрытие short + открытие long
        shortQty := pos.Quantity.Abs()
        realizedPnL := pos.AvgPrice.Sub(trade.Price).Mul(shortQty)
        pos.RealizedPnL = pos.RealizedPnL.Add(realizedPnL)

        remainingBuy := trade.Quantity.Sub(shortQty)
        pos.Quantity = remainingBuy
        pos.AvgPrice = trade.Price
        return
    }

    // Увеличиваем long позицию — пересчитываем среднюю цену
    // AvgPrice = (старый объём * старая цена + новый объём * новая цена) / суммарный объём
    totalCost := pos.Quantity.Mul(pos.AvgPrice).Add(trade.Quantity.Mul(trade.Price))
    pos.Quantity = pos.Quantity.Add(trade.Quantity)
    if pos.Quantity.IsPositive() {
        pos.AvgPrice = totalCost.Div(pos.Quantity)
    }
}

// applySell — продажа уменьшает long / открывает short
func (c *Calculator) applySell(pos *Position, trade TradeInfo) {
    if pos.Quantity.IsPositive() {
        // Закрываем long позицию
        if trade.Quantity.LessThanOrEqual(pos.Quantity) {
            // Частичное закрытие
            realizedPnL := trade.Price.Sub(pos.AvgPrice).Mul(trade.Quantity)
            pos.RealizedPnL = pos.RealizedPnL.Add(realizedPnL)
            pos.Quantity = pos.Quantity.Sub(trade.Quantity)
            if pos.Quantity.IsZero() {
                pos.AvgPrice = decimal.Zero
            }
            return
        }
        // Полное закрытие long + открытие short
        realizedPnL := trade.Price.Sub(pos.AvgPrice).Mul(pos.Quantity)
        pos.RealizedPnL = pos.RealizedPnL.Add(realizedPnL)

        remainingSell := trade.Quantity.Sub(pos.Quantity)
        pos.Quantity = remainingSell.Neg()
        pos.AvgPrice = trade.Price
        return
    }

    // Увеличиваем short позицию
    totalCost := pos.Quantity.Abs().Mul(pos.AvgPrice).Add(trade.Quantity.Mul(trade.Price))
    pos.Quantity = pos.Quantity.Sub(trade.Quantity)
    pos.AvgPrice = totalCost.Div(pos.Quantity.Abs())
}
```

### Portfolio Service: Consumer

```go
// internal/service/portfolio_service.go
package service

import (
    "context"
    "encoding/json"
    "fmt"
    "log/slog"
    "time"

    "github.com/nats-io/nats.go/jetstream"

    "trading/portfolio/internal/messaging"
    "trading/portfolio/internal/position"
    "trading/portfolio/internal/storage"
)

// PortfolioService — главный сервис
type PortfolioService struct {
    calculator *position.Calculator
    store      *position.PositionStore
    repo       *storage.PositionRepository
    publisher  *messaging.NATSPublisher
    logger     *slog.Logger
}

// NewPortfolioService — создание сервиса
func NewPortfolioService(
    store *position.PositionStore,
    repo *storage.PositionRepository,
    publisher *messaging.NATSPublisher,
    logger *slog.Logger,
) *PortfolioService {
    return &PortfolioService{
        calculator: position.NewCalculator(store),
        store:      store,
        repo:       repo,
        publisher:  publisher,
        logger:     logger,
    }
}

// HandleTrade — обработка события о сделке
func (s *PortfolioService) HandleTrade(ctx context.Context, msg jetstream.Msg) {
    var event messaging.TradeEvent
    if err := json.Unmarshal(msg.Data(), &event); err != nil {
        s.logger.Error("unmarshal trade event", "err", err)
        msg.Nak()
        return
    }

    // Обновляем позиции обоих участников сделки
    buyerTrade := position.TradeInfo{
        ClientID: event.BuyClientID,
        Symbol:   event.Symbol,
        Side:     "BUY",
        Price:    event.Price,
        Quantity: event.Quantity,
    }
    sellerTrade := position.TradeInfo{
        ClientID: event.SellClientID,
        Symbol:   event.Symbol,
        Side:     "SELL",
        Price:    event.Price,
        Quantity: event.Quantity,
    }

    s.calculator.ApplyTrade(buyerTrade)
    s.calculator.ApplyTrade(sellerTrade)

    // Асинхронное сохранение в PostgreSQL
    go func() {
        saveCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
        defer cancel()
        if err := s.persistPositions(saveCtx, event); err != nil {
            s.logger.Error("persist positions", "err", err)
        }
    }()

    // Уведомление клиентов об обновлении портфеля
    for _, clientID := range []string{event.BuyClientID, event.SellClientID} {
        pos := s.store.GetAll(clientID)
        updateEvent := messaging.PortfolioUpdateEvent{
            ClientID:  clientID,
            Positions: toPositionDTOs(pos),
            UpdatedAt: time.Now().UTC(),
        }
        subject := fmt.Sprintf("portfolio.updated.%s", clientID)
        if err := s.publisher.Publish(ctx, subject, updateEvent); err != nil {
            s.logger.Warn("publish portfolio update", "err", err, "client", clientID)
        }
    }

    msg.Ack()
}

// persistPositions — сохранение позиций в PostgreSQL + Redis
func (s *PortfolioService) persistPositions(ctx context.Context, event messaging.TradeEvent) error {
    // Upsert позиций в PostgreSQL
    for _, clientID := range []string{event.BuyClientID, event.SellClientID} {
        pos := s.store.Get(clientID, event.Symbol)
        if pos == nil {
            continue
        }
        if err := s.repo.Upsert(ctx, pos); err != nil {
            return fmt.Errorf("upsert position %s/%s: %w", clientID, event.Symbol, err)
        }
    }
    return nil
}

// toPositionDTOs — конвертация позиций в DTO
func toPositionDTOs(positions []position.Position) []messaging.PositionDTO {
    dtos := make([]messaging.PositionDTO, len(positions))
    for i, p := range positions {
        dtos[i] = messaging.PositionDTO{
            Symbol:      p.Symbol,
            Quantity:    p.Quantity,
            AvgPrice:    p.AvgPrice,
            RealizedPnL: p.RealizedPnL,
        }
    }
    return dtos
}
```

---

## Risk Service

### Лимиты и параметры риска

```go
// internal/limits/limits.go
package limits

import (
    "github.com/shopspring/decimal"
)

// RiskLimits — лимиты риска для клиента
type RiskLimits struct {
    ClientID         string
    MaxPositionUSD   decimal.Decimal // максимальная позиция в USD
    MaxDailyLossUSD  decimal.Decimal // максимальный дневной убыток
    MaxLeverage      decimal.Decimal // максимальное плечо
    AllowedSymbols   []string        // разрешённые инструменты (nil = все)
}

// DefaultLimits — стандартные лимиты
func DefaultLimits(clientID string) RiskLimits {
    return RiskLimits{
        ClientID:       clientID,
        MaxPositionUSD: decimal.NewFromFloat(100_000),
        MaxDailyLossUSD: decimal.NewFromFloat(10_000),
        MaxLeverage:    decimal.NewFromFloat(3),
    }
}

// AlertType — тип риск-алерта
type AlertType string

const (
    AlertMarginCall      AlertType = "MARGIN_CALL"
    AlertPositionLimit   AlertType = "POSITION_LIMIT"
    AlertDailyLossLimit  AlertType = "DAILY_LOSS_LIMIT"
    AlertLeverageLimit   AlertType = "LEVERAGE_LIMIT"
)

// Alert — риск-предупреждение
type Alert struct {
    ClientID  string
    Type      AlertType
    Message   string
    Severity  string // "WARNING" (80% лимита) или "CRITICAL" (100%)
}
```

### Расчёт VaR (Value at Risk)

```go
// internal/var/calculator.go
package var_calc

import (
    "math"
    "sort"

    "github.com/shopspring/decimal"
)

// HistoricalReturns — исторические доходности (для параметрического VaR)
type HistoricalReturns []float64

// VaRResult — результат расчёта VaR
type VaRResult struct {
    ConfidenceLevel float64         // 0.95 или 0.99
    TimeHorizon     int             // в днях
    VaR             decimal.Decimal // максимальный ожидаемый убыток
}

// HistoricalVaR — исторический VaR (непараметрический)
// Самый простой и надёжный метод для небольших портфелей
//
// confidence = 0.95 → 95% VaR (5% worst case)
// returns — отсортированные исторические доходности (в %)
func HistoricalVaR(returns HistoricalReturns, positionValueUSD float64, confidence float64) VaRResult {
    if len(returns) == 0 {
        return VaRResult{}
    }

    // Сортируем доходности по возрастанию (худшие первые)
    sorted := make([]float64, len(returns))
    copy(sorted, returns)
    sort.Float64s(sorted)

    // Квантиль: для 95% confidence → 5% худших наблюдений
    quantileIdx := int(math.Floor(float64(len(sorted)) * (1 - confidence)))
    if quantileIdx >= len(sorted) {
        quantileIdx = len(sorted) - 1
    }

    worstReturn := sorted[quantileIdx] // отрицательное число (убыток в %)
    varAmount := positionValueUSD * math.Abs(worstReturn) / 100

    return VaRResult{
        ConfidenceLevel: confidence,
        TimeHorizon:     1,
        VaR:             decimal.NewFromFloat(varAmount).Round(2),
    }
}

// ParametricVaR — параметрический VaR (на основе нормального распределения)
// Быстрее, но предполагает нормальное распределение доходностей
func ParametricVaR(returns HistoricalReturns, positionValueUSD float64, confidence float64) VaRResult {
    if len(returns) == 0 {
        return VaRResult{}
    }

    // Среднее
    mean := 0.0
    for _, r := range returns {
        mean += r
    }
    mean /= float64(len(returns))

    // Стандартное отклонение
    variance := 0.0
    for _, r := range returns {
        diff := r - mean
        variance += diff * diff
    }
    variance /= float64(len(returns))
    stdDev := math.Sqrt(variance)

    // Z-score для заданного уровня доверия
    // 95% → z = 1.645, 99% → z = 2.326
    zScore := normalQuantile(1 - confidence)
    varPercent := mean - zScore*stdDev
    varAmount := positionValueUSD * math.Abs(varPercent) / 100

    return VaRResult{
        ConfidenceLevel: confidence,
        TimeHorizon:     1,
        VaR:             decimal.NewFromFloat(varAmount).Round(2),
    }
}

// normalQuantile — квантиль стандартного нормального распределения
// Приближение Beasley-Springer-Moro
func normalQuantile(p float64) float64 {
    // Упрощённая таблица для распространённых значений
    switch {
    case p <= 0.01:
        return -2.326
    case p <= 0.05:
        return -1.645
    case p <= 0.10:
        return -1.282
    default:
        return -1.645
    }
}
```

### Risk Service: Consumer и проверки

```go
// internal/service/risk_service.go
package service

import (
    "context"
    "encoding/json"
    "fmt"
    "log/slog"
    "time"

    "github.com/nats-io/nats.go/jetstream"
    "github.com/shopspring/decimal"

    "trading/risk/internal/limits"
    "trading/risk/internal/messaging"
    "trading/risk/internal/storage"
    var_calc "trading/risk/internal/var"
)

// RiskService — сервис управления рисками
type RiskService struct {
    limitsRepo  *storage.LimitsRepository
    historyRepo *storage.PriceHistoryRepository
    publisher   *messaging.NATSPublisher
    logger      *slog.Logger
}

// NewRiskService — создание сервиса
func NewRiskService(
    limitsRepo *storage.LimitsRepository,
    historyRepo *storage.PriceHistoryRepository,
    publisher *messaging.NATSPublisher,
    logger *slog.Logger,
) *RiskService {
    return &RiskService{
        limitsRepo:  limitsRepo,
        historyRepo: historyRepo,
        publisher:   publisher,
        logger:      logger,
    }
}

// HandleTrade — проверка лимитов после совершения сделки
func (s *RiskService) HandleTrade(ctx context.Context, msg jetstream.Msg) {
    var event messaging.TradeEvent
    if err := json.Unmarshal(msg.Data(), &event); err != nil {
        s.logger.Error("unmarshal trade", "err", err)
        msg.Nak()
        return
    }

    // Параллельная проверка для обоих участников
    for _, clientID := range []string{event.BuyClientID, event.SellClientID} {
        go s.checkClientRisk(ctx, clientID, event)
    }

    msg.Ack()
}

// checkClientRisk — полная проверка риска для клиента
func (s *RiskService) checkClientRisk(ctx context.Context, clientID string, trade messaging.TradeEvent) {
    // Загружаем лимиты (с кэшированием в Redis)
    clientLimits, err := s.limitsRepo.Get(ctx, clientID)
    if err != nil {
        s.logger.Error("get limits", "client", clientID, "err", err)
        return
    }

    // Загружаем текущие позиции
    positions, err := s.limitsRepo.GetPositions(ctx, clientID)
    if err != nil {
        s.logger.Error("get positions", "client", clientID, "err", err)
        return
    }

    var alerts []limits.Alert

    // 1. Проверка размера позиции
    if alert := s.checkPositionLimit(positions, clientLimits, trade.Symbol); alert != nil {
        alerts = append(alerts, *alert)
    }

    // 2. Проверка дневного убытка
    if alert := s.checkDailyLoss(ctx, clientID, clientLimits); alert != nil {
        alerts = append(alerts, *alert)
    }

    // 3. Расчёт VaR
    if alert := s.checkVaR(ctx, positions, clientLimits, trade.Symbol); alert != nil {
        alerts = append(alerts, *alert)
    }

    // Публикация алертов
    for _, alert := range alerts {
        s.publishAlert(ctx, alert)
    }
}

// checkPositionLimit — проверка максимального размера позиции
func (s *RiskService) checkPositionLimit(
    positions []messaging.PositionDTO,
    clientLimits *limits.RiskLimits,
    symbol string,
) *limits.Alert {
    var totalExposureUSD decimal.Decimal

    for _, pos := range positions {
        if pos.Symbol != symbol {
            continue
        }
        // Экспозиция = |количество| * текущая цена
        // В реальности: получаем текущую цену из Redis/market data
        exposure := pos.Quantity.Abs().Mul(pos.AvgPrice)
        totalExposureUSD = totalExposureUSD.Add(exposure)
    }

    limit := clientLimits.MaxPositionUSD
    ratio := totalExposureUSD.Div(limit)

    if ratio.GreaterThanOrEqual(decimal.NewFromFloat(1.0)) {
        return &limits.Alert{
            ClientID: clientLimits.ClientID,
            Type:     limits.AlertPositionLimit,
            Message: fmt.Sprintf("Position size $%s exceeds limit $%s for %s",
                totalExposureUSD.StringFixed(2), limit.StringFixed(2), symbol),
            Severity: "CRITICAL",
        }
    }

    if ratio.GreaterThanOrEqual(decimal.NewFromFloat(0.8)) {
        return &limits.Alert{
            ClientID: clientLimits.ClientID,
            Type:     limits.AlertPositionLimit,
            Message: fmt.Sprintf("Position size at %.0f%% of limit for %s",
                ratio.Mul(decimal.NewFromFloat(100)).InexactFloat64(), symbol),
            Severity: "WARNING",
        }
    }

    return nil
}

// checkDailyLoss — проверка дневного убытка
func (s *RiskService) checkDailyLoss(
    ctx context.Context,
    clientID string,
    clientLimits *limits.RiskLimits,
) *limits.Alert {
    // Загружаем реализованный PnL за сегодня из TimescaleDB
    dailyLoss, err := s.limitsRepo.GetDailyRealizedLoss(ctx, clientID)
    if err != nil {
        s.logger.Error("get daily loss", "client", clientID, "err", err)
        return nil
    }

    if dailyLoss.IsNegative() { // убыток отрицательный
        loss := dailyLoss.Abs()
        limit := clientLimits.MaxDailyLossUSD
        ratio := loss.Div(limit)

        if ratio.GreaterThanOrEqual(decimal.NewFromFloat(1.0)) {
            return &limits.Alert{
                ClientID: clientID,
                Type:     limits.AlertDailyLossLimit,
                Message: fmt.Sprintf("Daily loss $%s exceeds limit $%s",
                    loss.StringFixed(2), limit.StringFixed(2)),
                Severity: "CRITICAL",
            }
        }
    }

    return nil
}

// checkVaR — расчёт Value at Risk
func (s *RiskService) checkVaR(
    ctx context.Context,
    positions []messaging.PositionDTO,
    clientLimits *limits.RiskLimits,
    symbol string,
) *limits.Alert {
    // Загружаем исторические доходности за последние 252 торговых дня
    returns, err := s.historyRepo.GetDailyReturns(ctx, symbol, 252)
    if err != nil || len(returns) < 30 {
        return nil // недостаточно данных
    }

    // Считаем суммарную позицию по инструменту
    var positionUSD float64
    for _, pos := range positions {
        if pos.Symbol == symbol {
            v, _ := pos.Quantity.Abs().Mul(pos.AvgPrice).Float64()
            positionUSD += v
        }
    }

    // 95% VaR за 1 день
    varResult := var_calc.HistoricalVaR(returns, positionUSD, 0.95)

    // Порог: VaR > 50% дневного лимита = WARNING
    limit := clientLimits.MaxDailyLossUSD
    if varResult.VaR.GreaterThan(limit.Mul(decimal.NewFromFloat(0.5))) {
        return &limits.Alert{
            ClientID: clientLimits.ClientID,
            Type:     limits.AlertMarginCall,
            Message: fmt.Sprintf("95%% VaR ($%s) exceeds 50%% of daily limit for %s",
                varResult.VaR.StringFixed(2), symbol),
            Severity: "WARNING",
        }
    }

    return nil
}

// publishAlert — публикация алерта в NATS
func (s *RiskService) publishAlert(ctx context.Context, alert limits.Alert) {
    event := messaging.RiskAlertEvent{
        ClientID:  alert.ClientID,
        AlertType: string(alert.Type),
        Message:   alert.Message,
        Severity:  alert.Severity,
        At:        time.Now().UTC(),
    }

    subject := fmt.Sprintf("risk.alert.%s", alert.ClientID)
    if err := s.publisher.Publish(ctx, subject, event); err != nil {
        s.logger.Error("publish risk alert", "client", alert.ClientID, "err", err)
        return
    }

    s.logger.Warn("risk alert published",
        "client", alert.ClientID,
        "type", alert.Type,
        "severity", alert.Severity,
        "message", alert.Message,
    )
}
```

---

## PostgreSQL: хранилище позиций

```go
// internal/storage/position_repository.go
package storage

import (
    "context"
    "fmt"

    "github.com/jackc/pgx/v5/pgxpool"

    "trading/portfolio/internal/position"
)

// PositionRepository — репозиторий позиций в PostgreSQL
type PositionRepository struct {
    pool *pgxpool.Pool
}

// NewPositionRepository — создание репозитория
func NewPositionRepository(pool *pgxpool.Pool) *PositionRepository {
    return &PositionRepository{pool: pool}
}

// Upsert — создание или обновление позиции
// INSERT ... ON CONFLICT DO UPDATE — идемпотентно
func (r *PositionRepository) Upsert(ctx context.Context, pos *position.Position) error {
    const query = `
        INSERT INTO positions (client_id, symbol, quantity, avg_price, realized_pnl, updated_at)
        VALUES ($1, $2, $3, $4, $5, NOW())
        ON CONFLICT (client_id, symbol)
        DO UPDATE SET
            quantity     = EXCLUDED.quantity,
            avg_price    = EXCLUDED.avg_price,
            realized_pnl = EXCLUDED.realized_pnl,
            updated_at   = EXCLUDED.updated_at
    `
    _, err := r.pool.Exec(ctx, query,
        pos.ClientID,
        pos.Symbol,
        pos.Quantity.String(),
        pos.AvgPrice.String(),
        pos.RealizedPnL.String(),
    )
    if err != nil {
        return fmt.Errorf("upsert position: %w", err)
    }
    return nil
}

// GetByClient — все позиции клиента из БД
func (r *PositionRepository) GetByClient(ctx context.Context, clientID string) ([]position.Position, error) {
    const query = `
        SELECT symbol, quantity, avg_price, realized_pnl, updated_at
        FROM positions
        WHERE client_id = $1 AND quantity != 0
        ORDER BY symbol
    `
    rows, err := r.pool.Query(ctx, query, clientID)
    if err != nil {
        return nil, fmt.Errorf("query positions: %w", err)
    }
    defer rows.Close()

    var positions []position.Position
    for rows.Next() {
        var p position.Position
        p.ClientID = clientID
        var qty, avgPrice, realizedPnL string

        if err := rows.Scan(&p.Symbol, &qty, &avgPrice, &realizedPnL, &p.UpdatedAt); err != nil {
            return nil, fmt.Errorf("scan position: %w", err)
        }

        // Парсинг decimal из строк
        p.Quantity, _ = decimal.NewFromString(qty)
        p.AvgPrice, _ = decimal.NewFromString(avgPrice)
        p.RealizedPnL, _ = decimal.NewFromString(realizedPnL)

        positions = append(positions, p)
    }

    return positions, rows.Err()
}
```

---

## Тестирование

### Unit-тесты позиций

```go
// internal/position/calculator_test.go
package position_test

import (
    "testing"

    "github.com/shopspring/decimal"

    "trading/portfolio/internal/position"
)

func TestCalculator_BuyIncreasesLong(t *testing.T) {
    store := position.NewPositionStore()
    calc := position.NewCalculator(store)

    // Первая покупка: 1 BTC @ 65000
    calc.ApplyTrade(position.TradeInfo{
        ClientID: "client-1", Symbol: "BTCUSD",
        Side: "BUY", Price: decimal.NewFromFloat(65000), Quantity: decimal.NewFromFloat(1),
    })

    // Вторая покупка: 1 BTC @ 67000
    calc.ApplyTrade(position.TradeInfo{
        ClientID: "client-1", Symbol: "BTCUSD",
        Side: "BUY", Price: decimal.NewFromFloat(67000), Quantity: decimal.NewFromFloat(1),
    })

    pos := store.Get("client-1", "BTCUSD")
    if pos == nil {
        t.Fatal("position not found")
    }

    // Количество = 2 BTC
    if !pos.Quantity.Equal(decimal.NewFromFloat(2)) {
        t.Errorf("quantity: got %s, want 2", pos.Quantity)
    }

    // Средняя цена = (65000 + 67000) / 2 = 66000
    want := decimal.NewFromFloat(66000)
    if !pos.AvgPrice.Equal(want) {
        t.Errorf("avg price: got %s, want %s", pos.AvgPrice, want)
    }
}

func TestCalculator_SellRealizesPnL(t *testing.T) {
    store := position.NewPositionStore()
    calc := position.NewCalculator(store)

    // Купили 1 BTC @ 65000
    calc.ApplyTrade(position.TradeInfo{
        ClientID: "client-1", Symbol: "BTCUSD",
        Side: "BUY", Price: decimal.NewFromFloat(65000), Quantity: decimal.NewFromFloat(1),
    })

    // Продали @ 70000 — реализованный PnL = +5000
    calc.ApplyTrade(position.TradeInfo{
        ClientID: "client-1", Symbol: "BTCUSD",
        Side: "SELL", Price: decimal.NewFromFloat(70000), Quantity: decimal.NewFromFloat(1),
    })

    pos := store.Get("client-1", "BTCUSD")

    // Позиция закрыта
    if !pos.Quantity.IsZero() {
        t.Errorf("quantity: got %s, want 0", pos.Quantity)
    }

    // Реализованный PnL = 5000
    wantPnL := decimal.NewFromFloat(5000)
    if !pos.RealizedPnL.Equal(wantPnL) {
        t.Errorf("realized PnL: got %s, want %s", pos.RealizedPnL, wantPnL)
    }
}

func TestCalculator_UnrealizedPnL(t *testing.T) {
    pos := &position.Position{
        Quantity: decimal.NewFromFloat(2),
        AvgPrice: decimal.NewFromFloat(65000),
    }

    currentPrice := decimal.NewFromFloat(68000)
    pnl := pos.UnrealizedPnL(currentPrice)

    // PnL = (68000 - 65000) * 2 = 6000
    want := decimal.NewFromFloat(6000)
    if !pnl.Equal(want) {
        t.Errorf("unrealized PnL: got %s, want %s", pnl, want)
    }
}
```

### Тест VaR

```go
// internal/var/calculator_test.go
package var_calc_test

import (
    "testing"

    var_calc "trading/risk/internal/var"
)

func TestHistoricalVaR(t *testing.T) {
    // 100 дней исторических доходностей (в %)
    returns := make(var_calc.HistoricalReturns, 100)
    for i := range returns {
        // Нормальное распределение ~N(0, 2%)
        returns[i] = float64(i%20-10) * 0.4
    }

    positionUSD := 100_000.0
    result := var_calc.HistoricalVaR(returns, positionUSD, 0.95)

    // VaR должен быть положительным числом
    if result.VaR.IsNegative() {
        t.Errorf("VaR should be positive, got %s", result.VaR)
    }

    // VaR не должен превышать размер позиции
    if result.VaR.InexactFloat64() > positionUSD {
        t.Errorf("VaR %s exceeds position $%.0f", result.VaR, positionUSD)
    }

    t.Logf("95%% VaR for $%.0f position: $%s", positionUSD, result.VaR.StringFixed(2))
}
```

---

## Сравнение с C#

| Аспект | C# | Go |
|--------|----|----|
| Event consumer | MassTransit `IConsumer<T>` | функция `func(ctx, msg jetstream.Msg)` |
| Background service | `IHostedService` + `ExecuteAsync` | горутина + `context.Done()` |
| In-memory state | `ConcurrentDictionary` | `sync.RWMutex` + map |
| Decimal arithmetic | встроенный `decimal` | shopspring/decimal |
| DB upsert | EF Core `AddOrUpdate` | pgx + `ON CONFLICT DO UPDATE` |
| Unit testing | xUnit + FluentAssertions | testing + ручные сравнения |
