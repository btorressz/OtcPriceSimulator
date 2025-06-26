import uuid
import time
from datetime import datetime
from typing import List, Dict, Optional
import threading

class OTCPool:
    """OTC trading pool for managing buy/sell offers"""
    
    def __init__(self):
        self.offers = {}  # Dict to store offers by ID
        self.active_offers = []  # List of active offer IDs
        self.completed_offers = []  # List of completed offer IDs
        self.lock = threading.Lock()  # Thread safety
        self.next_id = 1
    
    def add_offer(self, offer_type: str, sol_amount: float, price_per_sol: float, 
                  user_id: str = "anonymous") -> int:
        """
        Add a new offer to the pool
        
        Args:
            offer_type: "BUY" or "SELL"
            sol_amount: Amount of SOL
            price_per_sol: Price per SOL in USDC
            user_id: User identifier
            
        Returns:
            Offer ID
        """
        with self.lock:
            offer_id = self.next_id
            self.next_id += 1
            
            offer = {
                'id': offer_id,
                'type': offer_type.upper(),
                'sol_amount': sol_amount,
                'price_per_sol': price_per_sol,
                'total_usdc': sol_amount * price_per_sol,
                'user_id': user_id,
                'status': 'ACTIVE',
                'timestamp': datetime.now(),
                'created_at': time.time()
            }
            
            self.offers[offer_id] = offer
            self.active_offers.append(offer_id)
            
            return offer_id
    
    def cancel_offer(self, offer_id: int) -> bool:
        """
        Cancel an active offer
        
        Args:
            offer_id: ID of offer to cancel
            
        Returns:
            True if cancelled, False if not found or already inactive
        """
        with self.lock:
            if offer_id in self.active_offers and offer_id in self.offers:
                self.offers[offer_id]['status'] = 'CANCELLED'
                self.active_offers.remove(offer_id)
                return True
            return False
    
    def get_active_offers(self) -> List[Dict]:
        """Get all active offers"""
        with self.lock:
            return [self.offers[offer_id] for offer_id in self.active_offers 
                   if offer_id in self.offers]
    
    def get_offer(self, offer_id: int) -> Optional[Dict]:
        """Get specific offer by ID"""
        with self.lock:
            return self.offers.get(offer_id)
    
    def get_offers_by_type(self, offer_type: str) -> List[Dict]:
        """Get active offers by type (BUY/SELL)"""
        with self.lock:
            return [self.offers[offer_id] for offer_id in self.active_offers 
                   if offer_id in self.offers and self.offers[offer_id]['type'] == offer_type.upper()]
    
    def simulate_matching(self) -> List[Dict]:
        """
        Simulate order matching between buy and sell offers
        
        Returns:
            List of potential matches
        """
        with self.lock:
            buy_offers = self.get_offers_by_type('BUY')
            sell_offers = self.get_offers_by_type('SELL')
            
            matches = []
            
            # Sort buy offers by price (highest first)
            buy_offers.sort(key=lambda x: x['price_per_sol'], reverse=True)
            # Sort sell offers by price (lowest first)
            sell_offers.sort(key=lambda x: x['price_per_sol'])
            
            for buy_offer in buy_offers:
                for sell_offer in sell_offers:
                    # Check if buy price >= sell price (potential match)
                    if buy_offer['price_per_sol'] >= sell_offer['price_per_sol']:
                        # Calculate match details
                        match_amount = min(buy_offer['sol_amount'], sell_offer['sol_amount'])
                        match_price = (buy_offer['price_per_sol'] + sell_offer['price_per_sol']) / 2
                        spread = buy_offer['price_per_sol'] - sell_offer['price_per_sol']
                        
                        match = {
                            'buy_id': buy_offer['id'],
                            'sell_id': sell_offer['id'],
                            'match_amount': match_amount,
                            'match_price': match_price,
                            'buy_price': buy_offer['price_per_sol'],
                            'sell_price': sell_offer['price_per_sol'],
                            'spread': spread,
                            'total_usdc': match_amount * match_price,
                            'timestamp': datetime.now()
                        }
                        
                        matches.append(match)
            
            return matches
    
    def execute_match(self, buy_id: int, sell_id: int, match_amount: float, 
                     match_price: float) -> bool:
        """
        Execute a match between buy and sell offers
        
        Args:
            buy_id: Buy offer ID
            sell_id: Sell offer ID
            match_amount: Amount of SOL to match
            match_price: Price per SOL for the match
            
        Returns:
            True if match executed successfully
        """
        with self.lock:
            if buy_id not in self.offers or sell_id not in self.offers:
                return False
            
            buy_offer = self.offers[buy_id]
            sell_offer = self.offers[sell_id]
            
            if (buy_offer['status'] != 'ACTIVE' or sell_offer['status'] != 'ACTIVE' or
                buy_id not in self.active_offers or sell_id not in self.active_offers):
                return False
            
            # Update offer amounts
            buy_offer['sol_amount'] -= match_amount
            sell_offer['sol_amount'] -= match_amount
            
            # Mark as completed if fully filled
            if buy_offer['sol_amount'] <= 0:
                buy_offer['status'] = 'COMPLETED'
                self.active_offers.remove(buy_id)
                self.completed_offers.append(buy_id)
            
            if sell_offer['sol_amount'] <= 0:
                sell_offer['status'] = 'COMPLETED'
                self.active_offers.remove(sell_id)
                self.completed_offers.append(sell_id)
            
            return True
    
    def get_pool_stats(self) -> Dict:
        """Get pool statistics"""
        with self.lock:
            active_offers = self.get_active_offers()
            buy_offers = [o for o in active_offers if o['type'] == 'BUY']
            sell_offers = [o for o in active_offers if o['type'] == 'SELL']
            
            stats = {
                'total_active_offers': len(active_offers),
                'buy_offers_count': len(buy_offers),
                'sell_offers_count': len(sell_offers),
                'completed_offers_count': len(self.completed_offers),
                'total_sol_buy_volume': sum(o['sol_amount'] for o in buy_offers),
                'total_sol_sell_volume': sum(o['sol_amount'] for o in sell_offers),
                'avg_buy_price': sum(o['price_per_sol'] for o in buy_offers) / len(buy_offers) if buy_offers else 0,
                'avg_sell_price': sum(o['price_per_sol'] for o in sell_offers) / len(sell_offers) if sell_offers else 0,
                'highest_buy_price': max(o['price_per_sol'] for o in buy_offers) if buy_offers else 0,
                'lowest_sell_price': min(o['price_per_sol'] for o in sell_offers) if sell_offers else 0
            }
            
            return stats
    
    def clear_pool(self) -> None:
        """Clear all offers from the pool"""
        with self.lock:
            self.offers.clear()
            self.active_offers.clear()
            self.completed_offers.clear()
            self.next_id = 1
