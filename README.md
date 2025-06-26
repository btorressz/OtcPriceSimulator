# OtcPriceSimulator - OTC Trading Pool Simulator

A comprehensive Solana-based Over-The-Counter (OTC) trading pool simulator that leverages Jupiter DEX integration for advanced market analysis and trading optimization.

## Overview

This Streamlit-powered web application simulates a private trading pool for SOL/USDC pairs, comparing custom pricing against Jupiter DEX quotes. It provides real-time monitoring, automated order matching, and sophisticated arbitrage opportunity detection for MEV and pre-trade routing simulation.


## Key Features

### 🎯 Core Trading Functionality
- **Interactive OTC Pool**: Create and manage buy/sell offers with custom pricing
- **Automated Order Matching**: Intelligent matching algorithm for compatible orders
- **Real-time Price Monitoring**: Live SOL/USDC pricing from Jupiter DEX and CoinGecko
- **Spread Analysis**: Detailed comparison between OTC and market prices

### 📊 Advanced Analytics
- **Price Impact Analysis**: Interactive charts showing order size vs. price impact
- **Jupiter Route Analysis**: Detailed multi-step swap routing information
- **Technical Indicators**: RSI, volatility, momentum, and moving averages
- **Smart Trading Assistant**: AI-powered pricing suggestions and market insights

### ⚖️ Arbitrage Detection
- **Real-time Scanner**: Automated detection of profitable opportunities
- **Comprehensive Scoring**: Multi-factor opportunity analysis with profitability scores
- **Risk Assessment**: Price impact consideration and net spread calculations
- **Performance Optimization**: Fast scanning with intelligent pre-filtering

### 📈 Market Intelligence
- **Historical Performance**: Track trading performance over time
- **Market Sentiment**: Technical analysis and trend identification
- **Optimal Sizing**: Volatility-based position sizing recommendations
- **Data Export**: CSV logging for external analysis


## How to Use

### 1. Create Trading Offers
- Navigate to the "Create New Offer" section
- Choose BUY or SELL type
- Set SOL amount and price per SOL
- Submit to add to the active pool

### 2. Monitor Market Data
- View real-time SOL and USDC prices
- Track Jupiter DEX quotes and price updates
- Observe spread differences between OTC and market prices

### 3. Analyze Price Impact
- Use the "Price Impact Analysis" tab
- Select multiple SOL amounts to analyze
- View interactive charts showing optimal order sizes

### 4. Scan for Arbitrage
- Click "Scan Arbitrage Opportunities"
- Review detailed opportunity breakdowns
- Analyze gross spreads, price impacts, and net profitability

### 5. Review Technical Indicators
- Access RSI, volatility, and momentum metrics
- View moving averages and trend analysis
- Get AI-powered trading suggestions

  
## Architecture

### Core Components
- **`app.py`**: Main Streamlit interface with real-time updates
- **`jupiter_api.py`**: Jupiter DEX API client with rate limiting
- **`otc_pool.py`**: Order matching and pool management
- **`csv_logger.py`**: Data persistence and logging system
- **`price_monitor.py`**: Background price monitoring service
- **`technical_indicators.py`**: Advanced technical analysis
- **`analytics_engine.py`**: Market intelligence and insights

### Data Flow
1. Background service polls Jupiter API at configurable intervals
2. Users create offers through the web interface
3. Automatic matching of compatible orders
4. All activity logged to CSV files for analysis
5. Real-time updates displayed in the interface

   
## API Integration

### Jupiter DEX API
- **Endpoint**: `https://quote-api.jup.ag/v6`
- **Features**: Real-time quotes, route analysis, price impact calculation
- **Rate Limiting**: Configurable polling intervals
- **Fallback**: Graceful handling of API unavailability

### CoinGecko API
- **Purpose**: Live SOL and USDC market data
- **Features**: Current prices, market cap, 24h volume
- **Backup**: Secondary price source for reliability

  
### Monitoring Settings
- Default polling interval: 15 seconds
- Adjustable through the sidebar interface
- Background thread management for optimal performance

  ## Data Storage

### CSV Logging
- **Matches**: `otc_matches.csv` - Completed trades with spread analysis
- **Prices**: `jupiter_prices.csv` - Historical price data with timestamps
- **Thread-safe**: Concurrent logging without data corruption

### Data Export
- Filter by date ranges
- Export for external analysis
- Statistics and performance metrics

## Performance Features

### Optimization
- Pre-filtering for arbitrage scanning
- Efficient data validation
- Minimal API calls through intelligent caching
- Background processing for UI responsiveness

### Error Handling
- Graceful API failure recovery
- Data validation preventing infinite chart extents
- User-friendly error messages
- Automatic retry mechanisms

## Advanced Features

### Smart Trading Assistant
- Market sentiment analysis
- Optimal pricing suggestions
- Risk-adjusted position sizing
- Historical performance insights

### Arbitrage Scanner
- Multi-factor opportunity scoring
- Price impact consideration
- Detailed profitability analysis
- Real-time market monitoring




