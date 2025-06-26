import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import base64
from technical_indicators import TechnicalAnalyzer

class AnalyticsEngine:
    """Advanced analytics engine for OTC trading and market analysis"""
    
    def __init__(self, csv_logger, jupiter_api):
        self.csv_logger = csv_logger
        self.jupiter_api = jupiter_api
        self.technical_analyzer = TechnicalAnalyzer()
    
    def analyze_price_impact_curve(self, amounts: List[float]) -> Dict:
        """
        Analyze price impact across different order sizes
        
        Args:
            amounts: List of SOL amounts to analyze
            
        Returns:
            Analysis results with optimal sizing recommendations
        """
        impact_data = self.jupiter_api.get_price_impact_analysis(amounts)
        
        if not impact_data or all(v is None for v in impact_data.values()):
            return {
                'error': 'Unable to fetch price impact data',
                'recommendation': 'Use smaller order sizes'
            }
        
        # Filter out None values
        valid_data = {k: v for k, v in impact_data.items() if v is not None}
        
        if not valid_data:
            return {
                'error': 'No valid price impact data',
                'recommendation': 'Use smaller order sizes'
            }
        
        # Find optimal order size (minimize price impact while maximizing size)
        impact_threshold = 0.5  # 0.5% impact threshold
        optimal_sizes = [amount for amount, impact in valid_data.items() 
                        if impact <= impact_threshold]
        
        recommended_size = max(optimal_sizes) if optimal_sizes else min(valid_data.keys())
        
        return {
            'impact_data': valid_data,
            'recommended_size': recommended_size,
            'impact_threshold': impact_threshold,
            'analysis': {
                'low_impact_range': [k for k, v in valid_data.items() if v <= 0.1],
                'medium_impact_range': [k for k, v in valid_data.items() if 0.1 < v <= 0.5],
                'high_impact_range': [k for k, v in valid_data.items() if v > 0.5]
            }
        }
    
    def analyze_historical_performance(self) -> Dict:
        """
        Analyze historical trading performance from CSV logs
        
        Returns:
            Performance metrics and insights
        """
        try:
            matches_df = self.csv_logger.get_recent_matches(limit=1000)
            prices_df = self.csv_logger.get_recent_price_logs(limit=1000)
            
            if matches_df.empty and prices_df.empty:
                return {
                    'error': 'No historical data available',
                    'recommendation': 'Start trading to generate performance data'
                }
            
            analysis = {}
            
            # Price analysis
            if not prices_df.empty:
                prices_df['timestamp'] = pd.to_datetime(prices_df['timestamp'])
                prices_df = prices_df.sort_values('timestamp')
                
                price_series = pd.Series(
                    prices_df['jupiter_price'].values,
                    index=prices_df['timestamp']
                )
                
                # Technical indicators
                analysis['technical'] = {
                    'rsi': self.technical_analyzer.calculate_rsi(price_series).iloc[-1] if len(price_series) > 14 else 50,
                    'volatility': self.technical_analyzer.calculate_volatility(price_series),
                    'momentum': self.technical_analyzer.calculate_momentum(price_series),
                    'support_resistance': self.technical_analyzer.calculate_support_resistance(price_series),
                    'trading_signal': self.technical_analyzer.generate_trading_signals(price_series)
                }
                
                # Price statistics
                analysis['price_stats'] = {
                    'current_price': price_series.iloc[-1],
                    'price_range_24h': {
                        'high': price_series.tail(24).max() if len(price_series) >= 24 else price_series.max(),
                        'low': price_series.tail(24).min() if len(price_series) >= 24 else price_series.min()
                    },
                    'average_price': price_series.mean(),
                    'price_trend': 'Bullish' if price_series.iloc[-1] > price_series.mean() else 'Bearish'
                }
            
            # Trading performance analysis
            if not matches_df.empty:
                matches_df['timestamp'] = pd.to_datetime(matches_df['timestamp'])
                
                analysis['trading_performance'] = {
                    'total_matches': len(matches_df),
                    'total_volume_sol': matches_df['match_amount'].sum(),
                    'total_volume_usdc': matches_df['total_usdc'].sum(),
                    'average_spread': matches_df['spread'].mean(),
                    'profitable_trades': len(matches_df[matches_df['spread'] > 0]),
                    'win_rate': len(matches_df[matches_df['spread'] > 0]) / len(matches_df) * 100,
                    'best_spread': matches_df['spread'].max(),
                    'worst_spread': matches_df['spread'].min()
                }
                
                # Arbitrage opportunities
                if 'otc_vs_jupiter_spread' in matches_df.columns:
                    arbitrage_data = matches_df['otc_vs_jupiter_spread'].dropna()
                    if not arbitrage_data.empty:
                        analysis['arbitrage_analysis'] = {
                            'total_arbitrage_opportunities': len(arbitrage_data),
                            'profitable_arbitrage': len(arbitrage_data[arbitrage_data > 0]),
                            'average_arbitrage_spread': arbitrage_data.mean(),
                            'best_arbitrage_opportunity': arbitrage_data.max()
                        }
            
            return analysis
            
        except Exception as e:
            return {
                'error': f'Analysis failed: {str(e)}',
                'recommendation': 'Check data integrity and try again'
            }
    
    def generate_market_insights(self, market_data: Dict) -> Dict:
        """
        Generate actionable market insights from current data
        
        Args:
            market_data: Current market data from APIs
            
        Returns:
            Market insights and recommendations
        """
        insights = {
            'market_conditions': {},
            'trading_recommendations': {},
            'risk_assessment': {}
        }
        
        if not market_data:
            return {
                'error': 'No market data available',
                'recommendation': 'Refresh market data to generate insights'
            }
        
        # Analyze SOL market conditions
        if 'solana' in market_data:
            sol_data = market_data['solana']
            
            # Market condition assessment
            change_24h = sol_data.get('change_24h', 0)
            volume_24h = sol_data.get('volume_24h', 0)
            price = sol_data.get('price', 0)
            
            if change_24h > 5:
                market_condition = 'Strong Bullish'
            elif change_24h > 1:
                market_condition = 'Bullish'
            elif change_24h > -1:
                market_condition = 'Neutral'
            elif change_24h > -5:
                market_condition = 'Bearish'
            else:
                market_condition = 'Strong Bearish'
            
            insights['market_conditions'] = {
                'sol_condition': market_condition,
                'price_momentum': change_24h,
                'volume_analysis': 'High' if volume_24h > 1e9 else 'Medium' if volume_24h > 5e8 else 'Low',
                'volatility_level': 'High' if abs(change_24h) > 5 else 'Medium' if abs(change_24h) > 2 else 'Low'
            }
            
            # Trading recommendations based on conditions
            if market_condition in ['Strong Bullish', 'Bullish']:
                insights['trading_recommendations'] = {
                    'bias': 'Buy-side favorable',
                    'strategy': 'Consider buy offers at slight discount to capture upside',
                    'risk_level': 'Medium',
                    'optimal_timeframe': 'Short to medium term'
                }
            elif market_condition in ['Strong Bearish', 'Bearish']:
                insights['trading_recommendations'] = {
                    'bias': 'Sell-side favorable',
                    'strategy': 'Consider sell offers at premium or wait for better entry',
                    'risk_level': 'High',
                    'optimal_timeframe': 'Wait for reversal signals'
                }
            else:
                insights['trading_recommendations'] = {
                    'bias': 'Neutral - Range trading',
                    'strategy': 'Focus on spread capture, both buy and sell opportunities',
                    'risk_level': 'Low to Medium',
                    'optimal_timeframe': 'Flexible'
                }
        
        # Risk assessment
        volatility_level = insights['market_conditions'].get('volatility_level', 'Medium')
        
        risk_factors = []
        if volatility_level == 'High':
            risk_factors.append('High price volatility increases execution risk')
        
        volume_analysis = insights['market_conditions'].get('volume_analysis', 'Medium')
        if volume_analysis == 'Low':
            risk_factors.append('Low volume may impact liquidity')
        
        insights['risk_assessment'] = {
            'overall_risk': 'High' if len(risk_factors) > 1 else 'Medium' if risk_factors else 'Low',
            'risk_factors': risk_factors,
            'recommended_position_size': 'Small' if len(risk_factors) > 1 else 'Medium' if risk_factors else 'Normal'
        }
        
        return insights
    
    def calculate_arbitrage_score(self, otc_price: float, jupiter_price: float, 
                                offer_type: str, volume: float) -> Dict:
        """
        Calculate comprehensive arbitrage opportunity score
        
        Args:
            otc_price: OTC offer price
            jupiter_price: Current Jupiter price
            offer_type: 'BUY' or 'SELL'
            volume: Trade volume
            
        Returns:
            Arbitrage analysis with score and recommendations
        """
        # Calculate spread percentage
        if offer_type == 'BUY':
            spread_pct = ((otc_price - jupiter_price) / jupiter_price) * 100
        else:  # SELL
            spread_pct = ((jupiter_price - otc_price) / jupiter_price) * 100
        
        # Get price impact for the volume
        advanced_quote = self.jupiter_api.get_advanced_quote_with_routes(volume)
        price_impact = advanced_quote.get('price_impact_pct', 0) if advanced_quote else 0
        
        # Calculate net arbitrage after price impact
        net_arbitrage = spread_pct - price_impact
        
        # Score calculation (0-100)
        base_score = max(0, min(100, (net_arbitrage + 5) * 10))  # Scale to 0-100
        
        # Adjust score based on volume and market conditions
        volume_factor = 1.0
        if volume > 10:  # Large orders have higher execution risk
            volume_factor = 0.8
        elif volume < 1:  # Small orders have lower impact
            volume_factor = 1.1
        
        final_score = base_score * volume_factor
        
        # Generate recommendation
        if final_score > 80:
            recommendation = 'Excellent arbitrage opportunity'
            action = 'Execute immediately'
        elif final_score > 60:
            recommendation = 'Good arbitrage opportunity'
            action = 'Consider execution'
        elif final_score > 40:
            recommendation = 'Moderate opportunity'
            action = 'Monitor for better conditions'
        elif final_score > 20:
            recommendation = 'Low opportunity'
            action = 'Wait for better spreads'
        else:
            recommendation = 'Poor opportunity'
            action = 'Avoid execution'
        
        return {
            'score': round(final_score, 2),
            'spread_pct': round(spread_pct, 4),
            'price_impact_pct': round(price_impact, 4),
            'net_arbitrage_pct': round(net_arbitrage, 4),
            'recommendation': recommendation,
            'action': action,
            'risk_level': 'Low' if final_score > 60 else 'Medium' if final_score > 30 else 'High'
        }
    
    def generate_optimal_pricing_suggestion(self, market_data: Dict, 
                                          order_type: str, volume: float) -> Dict:
        """
        Generate optimal pricing suggestions for OTC offers
        
        Args:
            market_data: Current market data
            order_type: 'BUY' or 'SELL'
            volume: Intended order volume
            
        Returns:
            Pricing suggestions with rationale
        """
        if not market_data or 'solana' not in market_data:
            return {
                'error': 'Insufficient market data for pricing suggestion',
                'fallback_strategy': 'Use current Jupiter price with 1-2% buffer'
            }
        
        # Get current Jupiter price with volume consideration
        advanced_quote = self.jupiter_api.get_advanced_quote_with_routes(volume)
        if not advanced_quote:
            return {
                'error': 'Unable to fetch Jupiter quote for volume analysis',
                'fallback_strategy': 'Use smaller order size or retry later'
            }
        
        jupiter_price = advanced_quote['price']
        price_impact = advanced_quote['price_impact_pct']
        
        # Market volatility assessment
        sol_data = market_data['solana']
        volatility = abs(sol_data.get('change_24h', 0))
        
        # Calculate suggested pricing based on market conditions
        if order_type == 'BUY':
            # For buy offers, offer premium to attract sellers
            base_premium = 0.5  # 0.5% base premium
            volatility_adjustment = volatility * 0.1  # Higher volatility = higher premium
            impact_adjustment = price_impact * 0.5  # Account for execution impact
            
            suggested_premium = base_premium + volatility_adjustment + impact_adjustment
            suggested_price = jupiter_price * (1 + suggested_premium / 100)
            
            strategy = f"Offer {suggested_premium:.2f}% premium to attract sellers"
            
        else:  # SELL
            # For sell offers, offer discount to attract buyers
            base_discount = 0.5  # 0.5% base discount
            volatility_adjustment = volatility * 0.1
            impact_adjustment = price_impact * 0.5
            
            suggested_discount = base_discount + volatility_adjustment + impact_adjustment
            suggested_price = jupiter_price * (1 - suggested_discount / 100)
            
            strategy = f"Offer {suggested_discount:.2f}% discount to attract buyers"
        
        # Risk-adjusted alternatives
        conservative_adjustment = 0.5  # Additional 0.5% buffer
        aggressive_adjustment = -0.2   # Reduce buffer by 0.2%
        
        if order_type == 'BUY':
            conservative_price = suggested_price * (1 + conservative_adjustment / 100)
            aggressive_price = suggested_price * (1 + aggressive_adjustment / 100)
        else:
            conservative_price = suggested_price * (1 - conservative_adjustment / 100)
            aggressive_price = suggested_price * (1 + aggressive_adjustment / 100)
        
        return {
            'suggested_price': round(suggested_price, 4),
            'conservative_price': round(conservative_price, 4),
            'aggressive_price': round(aggressive_price, 4),
            'jupiter_reference': round(jupiter_price, 4),
            'price_impact': round(price_impact, 4),
            'strategy': strategy,
            'market_context': {
                'volatility_level': 'High' if volatility > 5 else 'Medium' if volatility > 2 else 'Low',
                'recommended_urgency': 'High' if volatility > 5 else 'Medium'
            },
            'execution_tips': [
                f"Monitor Jupiter price closely - current impact: {price_impact:.2f}%",
                f"Market volatility is {volatility:.2f}% - adjust expectations",
                "Consider partial fills for large orders"
            ]
        }