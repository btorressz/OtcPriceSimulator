import requests
import json
import time
from typing import Dict, Optional, List
import streamlit as st

class JupiterAPI:
    """Jupiter API client for fetching SOL/USDC quotes"""
    
    def __init__(self):
        self.base_url = "https://quote-api.jup.ag/v6"
        self.sol_mint = "So11111111111111111111111111111111111111112"  # SOL mint address
        self.usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC mint address
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OTC-Simulator/1.0',
            'Accept': 'application/json'
        })
    
    def get_sol_usdc_quote(self, amount: float = 1.0) -> Optional[Dict]:
        """
        Get SOL to USDC quote from Jupiter
        
        Args:
            amount: Amount of SOL to quote (default: 1.0)
            
        Returns:
            Dict with quote data or None if failed
        """
        try:
            # Convert SOL amount to lamports (1 SOL = 1e9 lamports)
            input_amount = int(amount * 1e9)
            
            params = {
                'inputMint': self.sol_mint,
                'outputMint': self.usdc_mint,
                'amount': input_amount,
                'slippageBps': 50,  # 0.5% slippage
                'onlyDirectRoutes': 'false',
                'asLegacyTransaction': 'false'
            }
            
            response = self.session.get(
                f"{self.base_url}/quote",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract the output amount (in USDC micro units)
                out_amount = int(data['outAmount'])
                # Convert to USDC (1 USDC = 1e6 micro units)
                usdc_amount = out_amount / 1e6
                
                # Calculate price per SOL
                price_per_sol = usdc_amount / amount
                
                return {
                    'price': price_per_sol,
                    'input_amount': amount,
                    'output_amount': usdc_amount,
                    'route_plan': data.get('routePlan', []),
                    'price_impact_pct': data.get('priceImpactPct', 0),
                    'timestamp': time.time()
                }
            else:
                st.error(f"Jupiter API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            st.error("Jupiter API request timed out")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"Jupiter API request failed: {str(e)}")
            return None
        except (KeyError, ValueError) as e:
            st.error(f"Failed to parse Jupiter API response: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Unexpected error fetching Jupiter quote: {str(e)}")
            return None
    
    def get_multiple_quotes(self, amounts: list) -> Dict[float, Optional[Dict]]:
        """
        Get quotes for multiple SOL amounts
        
        Args:
            amounts: List of SOL amounts to quote
            
        Returns:
            Dict mapping amounts to quote data
        """
        quotes = {}
        for amount in amounts:
            quotes[amount] = self.get_sol_usdc_quote(amount)
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        return quotes
    
    def get_advanced_quote_with_routes(self, amount: float = 1.0) -> Optional[Dict]:
        """
        Get detailed quote with all available routes and price impact analysis
        
        Args:
            amount: Amount of SOL to quote
            
        Returns:
            Dict with detailed routing and price impact data
        """
        try:
            input_amount = int(amount * 1e9)
            
            params = {
                'inputMint': self.sol_mint,
                'outputMint': self.usdc_mint,
                'amount': input_amount,
                'slippageBps': 50,
                'onlyDirectRoutes': 'false',
                'asLegacyTransaction': 'false',
                'maxAccounts': 64
            }
            
            response = self.session.get(f"{self.base_url}/quote", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                out_amount = int(data['outAmount'])
                usdc_amount = out_amount / 1e6
                price_per_sol = usdc_amount / amount
                
                # Extract detailed route information
                routes = []
                if 'routePlan' in data:
                    for i, route in enumerate(data['routePlan']):
                        routes.append({
                            'step': i + 1,
                            'swap_info': route.get('swapInfo', {}),
                            'percent': route.get('percent', 0)
                        })
                
                return {
                    'price': price_per_sol,
                    'input_amount': amount,
                    'output_amount': usdc_amount,
                    'price_impact_pct': float(data.get('priceImpactPct', 0)),
                    'routes': routes,
                    'route_count': len(routes),
                    'context_slot': data.get('contextSlot', 0),
                    'time_taken': data.get('timeTaken', 0),
                    'timestamp': time.time()
                }
            else:
                return None
                
        except Exception as e:
            print(f"Error fetching advanced quote: {e}")
            return None
    
    def get_supported_tokens(self) -> Optional[List[Dict]]:
        """
        Get list of all supported tokens from Jupiter
        
        Returns:
            List of token information
        """
        try:
            response = self.session.get(
                "https://token.jup.ag/all",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"Error fetching token list: {e}")
            return None
    
    def get_price_impact_analysis(self, amounts: List[float]) -> Dict[float, float]:
        """
        Analyze price impact across different order sizes
        
        Args:
            amounts: List of SOL amounts to analyze
            
        Returns:
            Dict mapping amounts to price impact percentages
        """
        impact_analysis = {}
        
        for amount in amounts:
            quote_data = self.get_advanced_quote_with_routes(amount)
            if quote_data:
                impact_analysis[amount] = quote_data['price_impact_pct']
            else:
                impact_analysis[amount] = None
            
            time.sleep(0.1)  # Rate limiting
        
        return impact_analysis
    
    def get_token_prices(self) -> Optional[Dict]:
        """Get current token prices from CoinGecko API"""
        try:
            # Using CoinGecko API for real-time price data
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': 'solana,usd-coin',
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'solana': {
                        'price_usd': data.get('solana', {}).get('usd', 0),
                        'change_24h': data.get('solana', {}).get('usd_24h_change', 0),
                        'market_cap': data.get('solana', {}).get('usd_market_cap', 0),
                        'volume_24h': data.get('solana', {}).get('usd_24h_vol', 0)
                    },
                    'usdc': {
                        'price_usd': data.get('usd-coin', {}).get('usd', 0),
                        'change_24h': data.get('usd-coin', {}).get('usd_24h_change', 0),
                        'market_cap': data.get('usd-coin', {}).get('usd_market_cap', 0),
                        'volume_24h': data.get('usd-coin', {}).get('usd_24h_vol', 0)
                    },
                    'timestamp': time.time()
                }
            else:
                return None
                
        except Exception as e:
            print(f"Error fetching token prices: {e}")
            return None

    def get_market_data(self) -> Optional[Dict]:
        """Get comprehensive market data for SOL and USDC"""
        try:
            # Get detailed market data
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'ids': 'solana,usd-coin',
                'order': 'market_cap_desc',
                'per_page': 2,
                'page': 1,
                'sparkline': 'false',
                'price_change_percentage': '1h,24h,7d'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                market_data = {}
                for coin in data:
                    if coin['id'] == 'solana':
                        market_data['solana'] = {
                            'price': coin['current_price'],
                            'market_cap': coin['market_cap'],
                            'volume_24h': coin['total_volume'],
                            'change_1h': coin.get('price_change_percentage_1h_in_currency', 0),
                            'change_24h': coin.get('price_change_percentage_24h_in_currency', 0),
                            'change_7d': coin.get('price_change_percentage_7d_in_currency', 0),
                            'market_cap_rank': coin['market_cap_rank'],
                            'circulating_supply': coin['circulating_supply'],
                            'total_supply': coin['total_supply'],
                            'max_supply': coin['max_supply']
                        }
                    elif coin['id'] == 'usd-coin':
                        market_data['usdc'] = {
                            'price': coin['current_price'],
                            'market_cap': coin['market_cap'],
                            'volume_24h': coin['total_volume'],
                            'change_1h': coin.get('price_change_percentage_1h_in_currency', 0),
                            'change_24h': coin.get('price_change_percentage_24h_in_currency', 0),
                            'change_7d': coin.get('price_change_percentage_7d_in_currency', 0),
                            'market_cap_rank': coin['market_cap_rank'],
                            'circulating_supply': coin['circulating_supply'],
                            'total_supply': coin['total_supply']
                        }
                
                market_data['timestamp'] = time.time()
                return market_data
            else:
                return None
                
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return None

    def test_connection(self) -> bool:
        """Test connection to Jupiter API"""
        try:
            response = self.session.get(
                f"{self.base_url}/quote",
                params={
                    'inputMint': self.sol_mint,
                    'outputMint': self.usdc_mint,
                    'amount': 1000000000,  # 1 SOL in lamports
                    'slippageBps': 50
                },
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
