import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

class TechnicalAnalyzer:
    """Technical analysis and statistical calculations for price data"""
    
    def __init__(self):
        pass
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            prices: Series of prices
            period: Period for RSI calculation
            
        Returns:
            Series with RSI values
        """
        if len(prices) < period + 1:
            return pd.Series([50] * len(prices), index=prices.index)
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50) if hasattr(rsi, 'fillna') else pd.Series([50] * len(prices), index=prices.index)
    
    def calculate_moving_averages(self, prices: pd.Series, 
                                windows: List[int] = [5, 10, 20, 50]) -> Dict[str, pd.Series]:
        """
        Calculate multiple moving averages
        
        Args:
            prices: Series of prices
            windows: List of window sizes
            
        Returns:
            Dict with moving averages for each window
        """
        mas = {}
        for window in windows:
            if len(prices) >= window:
                mas[f'MA_{window}'] = prices.rolling(window=window).mean()
            else:
                mas[f'MA_{window}'] = pd.Series([prices.mean()] * len(prices), index=prices.index)
        return mas
    
    def calculate_bollinger_bands(self, prices: pd.Series, window: int = 20, 
                                num_std: float = 2.0) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Args:
            prices: Series of prices
            window: Rolling window size
            num_std: Number of standard deviations
            
        Returns:
            Dict with upper, middle, and lower bands
        """
        if len(prices) < window:
            mean_price = prices.mean()
            std_price = prices.std() if len(prices) > 1 else 0
            return {
                'upper': pd.Series([mean_price + num_std * std_price] * len(prices), index=prices.index),
                'middle': pd.Series([mean_price] * len(prices), index=prices.index),
                'lower': pd.Series([mean_price - num_std * std_price] * len(prices), index=prices.index)
            }
        
        rolling_mean = prices.rolling(window=window).mean()
        rolling_std = prices.rolling(window=window).std()
        
        return {
            'upper': rolling_mean + (rolling_std * num_std),
            'middle': rolling_mean,
            'lower': rolling_mean - (rolling_std * num_std)
        }
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, 
                      slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            prices: Series of prices
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line EMA period
            
        Returns:
            Dict with MACD line, signal line, and histogram
        """
        if len(prices) < slow:
            return {
                'macd': pd.Series([0] * len(prices), index=prices.index),
                'signal': pd.Series([0] * len(prices), index=prices.index),
                'histogram': pd.Series([0] * len(prices), index=prices.index)
            }
        
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def calculate_volatility(self, prices: pd.Series, window: int = 20) -> Dict[str, float]:
        """
        Calculate various volatility measures
        
        Args:
            prices: Series of prices
            window: Rolling window for calculations
            
        Returns:
            Dict with volatility metrics
        """
        if len(prices) < 2:
            return {
                'daily_volatility': 0.0,
                'annualized_volatility': 0.0,
                'rolling_volatility': 0.0
            }
        
        returns = prices.pct_change().dropna()
        
        daily_vol = returns.std()
        annualized_vol = daily_vol * np.sqrt(365)
        
        if len(returns) >= window:
            rolling_vol = returns.rolling(window=window).std().iloc[-1]
        else:
            rolling_vol = daily_vol
        
        return {
            'daily_volatility': daily_vol,
            'annualized_volatility': annualized_vol,
            'rolling_volatility': rolling_vol
        }
    
    def calculate_price_momentum(self, prices: pd.Series, periods: List[int] = [1, 7, 30]) -> Dict[str, float]:
        """
        Calculate price momentum over different periods
        
        Args:
            prices: Series of prices
            periods: List of periods to calculate momentum
            
        Returns:
            Dict with momentum percentages
        """
        momentum = {}
        current_price = prices.iloc[-1] if len(prices) > 0 else 0
        
        for period in periods:
            if len(prices) > period:
                past_price = prices.iloc[-(period + 1)]
                momentum[f'momentum_{period}d'] = ((current_price - past_price) / past_price) * 100
            else:
                momentum[f'momentum_{period}d'] = 0.0
        
        return momentum
    
    def calculate_support_resistance(self, prices: pd.Series, window: int = 20) -> Dict[str, float]:
        """
        Calculate support and resistance levels
        
        Args:
            prices: Series of prices
            window: Window for local min/max calculation
            
        Returns:
            Dict with support and resistance levels
        """
        if len(prices) < window:
            price_mean = prices.mean()
            price_std = prices.std() if len(prices) > 1 else 0
            return {
                'support': price_mean - price_std,
                'resistance': price_mean + price_std,
                'current_level': prices.iloc[-1] if len(prices) > 0 else price_mean
            }
        
        # Find local minima and maxima
        rolling_min = prices.rolling(window=window, center=True).min()
        rolling_max = prices.rolling(window=window, center=True).max()
        
        # Get recent support/resistance levels
        recent_support = rolling_min.tail(window).min()
        recent_resistance = rolling_max.tail(window).max()
        
        return {
            'support': recent_support,
            'resistance': recent_resistance,
            'current_level': prices.iloc[-1]
        }
    
    def generate_trading_signals(self, prices: pd.Series) -> Dict[str, str]:
        """
        Generate trading signals based on technical indicators
        
        Args:
            prices: Series of prices
            
        Returns:
            Dict with trading signals and reasons
        """
        if len(prices) < 20:
            return {
                'signal': 'HOLD',
                'strength': 'WEAK',
                'reason': 'Insufficient data for analysis'
            }
        
        signals = []
        
        # RSI signal
        rsi = self.calculate_rsi(prices)
        current_rsi = rsi.iloc[-1]
        if current_rsi > 70:
            signals.append(('SELL', 'RSI overbought'))
        elif current_rsi < 30:
            signals.append(('BUY', 'RSI oversold'))
        
        # Moving average signal
        ma_short = prices.rolling(window=5).mean().iloc[-1]
        ma_long = prices.rolling(window=20).mean().iloc[-1]
        current_price = prices.iloc[-1]
        
        if ma_short > ma_long and current_price > ma_short:
            signals.append(('BUY', 'Price above rising MA'))
        elif ma_short < ma_long and current_price < ma_short:
            signals.append(('SELL', 'Price below falling MA'))
        
        # Bollinger Bands signal
        bb = self.calculate_bollinger_bands(prices)
        if current_price > bb['upper'].iloc[-1]:
            signals.append(('SELL', 'Price above upper Bollinger Band'))
        elif current_price < bb['lower'].iloc[-1]:
            signals.append(('BUY', 'Price below lower Bollinger Band'))
        
        # Aggregate signals
        buy_signals = [s for s in signals if s[0] == 'BUY']
        sell_signals = [s for s in signals if s[0] == 'SELL']
        
        if len(buy_signals) > len(sell_signals):
            signal = 'BUY'
            strength = 'STRONG' if len(buy_signals) >= 2 else 'MODERATE'
            reason = '; '.join([s[1] for s in buy_signals])
        elif len(sell_signals) > len(buy_signals):
            signal = 'SELL'
            strength = 'STRONG' if len(sell_signals) >= 2 else 'MODERATE'
            reason = '; '.join([s[1] for s in sell_signals])
        else:
            signal = 'HOLD'
            strength = 'NEUTRAL'
            reason = 'Mixed signals'
        
        return {
            'signal': signal,
            'strength': strength,
            'reason': reason
        }
    
    def calculate_optimal_order_size(self, prices: pd.Series, 
                                   available_balance: float,
                                   risk_tolerance: float = 0.02) -> Dict[str, float]:
        """
        Calculate optimal order size based on volatility and risk management
        
        Args:
            prices: Series of prices
            available_balance: Available trading balance
            risk_tolerance: Maximum risk as fraction of balance (default 2%)
            
        Returns:
            Dict with recommended order sizes
        """
        if len(prices) < 10:
            return {
                'conservative': available_balance * 0.1,
                'moderate': available_balance * 0.2,
                'aggressive': available_balance * 0.3
            }
        
        volatility = self.calculate_volatility(prices)
        daily_vol = volatility['daily_volatility']
        
        # Calculate position size based on volatility
        # Higher volatility = smaller position size
        vol_adjustment = 1 / (1 + daily_vol * 10)  # Scale factor
        
        base_conservative = available_balance * 0.1 * vol_adjustment
        base_moderate = available_balance * 0.2 * vol_adjustment
        base_aggressive = available_balance * 0.3 * vol_adjustment
        
        # Apply risk management
        max_risk_amount = available_balance * risk_tolerance
        current_price = prices.iloc[-1]
        
        return {
            'conservative': min(base_conservative, max_risk_amount / (daily_vol * current_price)),
            'moderate': min(base_moderate, max_risk_amount / (daily_vol * current_price * 0.8)),
            'aggressive': min(base_aggressive, max_risk_amount / (daily_vol * current_price * 0.6))
        }