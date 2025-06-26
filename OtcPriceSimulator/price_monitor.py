import threading
import time
from datetime import datetime
from typing import Optional
import streamlit as st

class PriceMonitor:
    """Background price monitoring service"""
    
    def __init__(self, jupiter_api, otc_pool, csv_logger):
        self.jupiter_api = jupiter_api
        self.otc_pool = otc_pool
        self.csv_logger = csv_logger
        self.monitoring_thread = None
        self.stop_event = threading.Event()
        self.polling_interval = 15  # seconds
        self.last_price = None
        self.last_update = None
    
    def start_monitoring(self, polling_interval: int = 15):
        """
        Start background price monitoring
        
        Args:
            polling_interval: Seconds between price checks
        """
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            return  # Already running
        
        self.polling_interval = polling_interval
        self.stop_event.clear()
        self.monitoring_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop background price monitoring"""
        if self.monitoring_thread:
            self.stop_event.set()
            self.monitoring_thread.join(timeout=5)
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while not self.stop_event.is_set():
            try:
                # Fetch Jupiter price
                price_data = self.jupiter_api.get_sol_usdc_quote(1.0)
                
                if price_data:
                    # Update session state
                    st.session_state.last_jupiter_price = price_data['price']
                    st.session_state.last_update_time = datetime.now()
                    
                    # Log to CSV
                    self.csv_logger.log_jupiter_price(price_data)
                    
                    # Store locally
                    self.last_price = price_data['price']
                    self.last_update = datetime.now()
                    
                    # Check for arbitrage opportunities
                    self._check_arbitrage_opportunities(price_data['price'])
                
                # Fetch market data every 5th cycle (less frequent)
                if hasattr(self, '_market_cycle_count'):
                    self._market_cycle_count += 1
                else:
                    self._market_cycle_count = 1
                    
                if self._market_cycle_count % 5 == 0:
                    try:
                        market_data = self.jupiter_api.get_market_data()
                        if market_data:
                            st.session_state.market_data = market_data
                            st.session_state.last_market_update = datetime.now()
                    except Exception as e:
                        print(f"Error fetching market data: {e}")
                
                # Wait for next update
                self.stop_event.wait(self.polling_interval)
                
            except Exception as e:
                print(f"Error in price monitoring: {e}")
                # Wait before retrying
                self.stop_event.wait(min(self.polling_interval, 30))
    
    def _check_arbitrage_opportunities(self, jupiter_price: float):
        """
        Check for arbitrage opportunities between OTC and Jupiter
        
        Args:
            jupiter_price: Current Jupiter price
        """
        try:
            active_offers = self.otc_pool.get_active_offers()
            
            for offer in active_offers:
                spread_pct = self._calculate_spread_percentage(
                    offer['type'], offer['price_per_sol'], jupiter_price
                )
                
                # Flag significant arbitrage opportunities (>1% spread)
                if abs(spread_pct) > 1.0:
                    opportunity = {
                        'offer_id': offer['id'],
                        'offer_type': offer['type'],
                        'otc_price': offer['price_per_sol'],
                        'jupiter_price': jupiter_price,
                        'spread_pct': spread_pct,
                        'sol_amount': offer['sol_amount'],
                        'timestamp': datetime.now()
                    }
                    
                    # Log opportunity (could be extended to send alerts)
                    self._log_arbitrage_opportunity(opportunity)
        
        except Exception as e:
            print(f"Error checking arbitrage opportunities: {e}")
    
    def _calculate_spread_percentage(self, offer_type: str, otc_price: float, jupiter_price: float) -> float:
        """Calculate spread percentage based on offer type"""
        if offer_type == 'BUY':
            # For buy offers, positive spread means OTC price is higher
            return ((otc_price - jupiter_price) / jupiter_price) * 100
        else:  # SELL
            # For sell offers, positive spread means Jupiter price is higher (OTC is cheaper)
            return ((jupiter_price - otc_price) / jupiter_price) * 100
    
    def _log_arbitrage_opportunity(self, opportunity: dict):
        """Log arbitrage opportunity"""
        # This could be extended to maintain a separate log file for opportunities
        print(f"Arbitrage opportunity: {opportunity}")
    
    def get_current_price(self) -> Optional[float]:
        """Get the last fetched price"""
        return self.last_price
    
    def get_last_update(self) -> Optional[datetime]:
        """Get the timestamp of last price update"""
        return self.last_update
    
    def is_monitoring_active(self) -> bool:
        """Check if monitoring is currently active"""
        if self.monitoring_thread and self.monitoring_thread.is_alive() and not self.stop_event.is_set():
            return True
        return False
    
    def force_price_update(self) -> Optional[float]:
        """Force an immediate price update"""
        try:
            price_data = self.jupiter_api.get_sol_usdc_quote(1.0)
            if price_data:
                st.session_state.last_jupiter_price = price_data['price']
                st.session_state.last_update_time = datetime.now()
                self.csv_logger.log_jupiter_price(price_data)
                self.last_price = price_data['price']
                self.last_update = datetime.now()
                return price_data['price']
            return None
        except Exception as e:
            print(f"Error forcing price update: {e}")
            return None
