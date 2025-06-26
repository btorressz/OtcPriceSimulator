import csv
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import threading

class CSVLogger:
    """CSV logger for matches and price data"""
    
    def __init__(self, matches_file: str = "otc_matches.csv", 
                 prices_file: str = "jupiter_prices.csv"):
        self.matches_file = matches_file
        self.prices_file = prices_file
        self.lock = threading.Lock()
        
        # Initialize CSV files with headers if they don't exist
        self._init_csv_files()
    
    def _init_csv_files(self):
        """Initialize CSV files with headers"""
        # Matches file
        if not os.path.exists(self.matches_file):
            with open(self.matches_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'buy_id', 'sell_id', 'match_amount', 'match_price',
                    'buy_price', 'sell_price', 'spread', 'total_usdc', 'jupiter_price',
                    'otc_vs_jupiter_spread'
                ])
        
        # Prices file
        if not os.path.exists(self.prices_file):
            with open(self.prices_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'jupiter_price', 'input_amount', 'output_amount',
                    'price_impact_pct', 'route_count'
                ])
    
    def log_match(self, match_data: Dict, jupiter_price: Optional[float] = None):
        """
        Log a match to CSV
        
        Args:
            match_data: Match data dictionary
            jupiter_price: Current Jupiter price for comparison
        """
        with self.lock:
            try:
                # Calculate OTC vs Jupiter spread if Jupiter price is provided
                otc_vs_jupiter_spread = None
                if jupiter_price:
                    otc_vs_jupiter_spread = ((match_data['match_price'] - jupiter_price) / jupiter_price) * 100
                
                with open(self.matches_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        match_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                        match_data['buy_id'],
                        match_data['sell_id'],
                        match_data['match_amount'],
                        match_data['match_price'],
                        match_data['buy_price'],
                        match_data['sell_price'],
                        match_data['spread'],
                        match_data['total_usdc'],
                        jupiter_price,
                        otc_vs_jupiter_spread
                    ])
            except Exception as e:
                print(f"Error logging match: {e}")
    
    def log_jupiter_price(self, price_data: Dict):
        """
        Log Jupiter price data to CSV
        
        Args:
            price_data: Price data from Jupiter API
        """
        with self.lock:
            try:
                with open(self.prices_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        price_data['price'],
                        price_data['input_amount'],
                        price_data['output_amount'],
                        price_data.get('price_impact_pct', 0),
                        len(price_data.get('route_plan', []))
                    ])
            except Exception as e:
                print(f"Error logging Jupiter price: {e}")
    
    def log_offer_comparison(self, offer_data: Dict, jupiter_price: float):
        """
        Log offer vs Jupiter price comparison
        
        Args:
            offer_data: OTC offer data
            jupiter_price: Current Jupiter price
        """
        # This could be extended to log individual offer comparisons
        # For now, we'll use the existing price logging
        pass
    
    def get_recent_matches(self, limit: int = 50) -> pd.DataFrame:
        """
        Get recent matches from CSV
        
        Args:
            limit: Maximum number of matches to return
            
        Returns:
            DataFrame with recent matches
        """
        try:
            if os.path.exists(self.matches_file):
                df = pd.read_csv(self.matches_file)
                if not df.empty:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    return df.tail(limit).sort_values('timestamp', ascending=False)
            return pd.DataFrame()
        except Exception as e:
            print(f"Error reading matches: {e}")
            return pd.DataFrame()
    
    def get_recent_price_logs(self, limit: int = 100) -> pd.DataFrame:
        """
        Get recent price logs from CSV
        
        Args:
            limit: Maximum number of price logs to return
            
        Returns:
            DataFrame with recent price logs
        """
        try:
            if os.path.exists(self.prices_file):
                df = pd.read_csv(self.prices_file)
                if not df.empty:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    return df.tail(limit).sort_values('timestamp', ascending=False)
            return pd.DataFrame()
        except Exception as e:
            print(f"Error reading price logs: {e}")
            return pd.DataFrame()
    
    def get_match_statistics(self) -> Dict:
        """Get statistics from match logs"""
        try:
            df = self.get_recent_matches(limit=1000)  # Get more data for stats
            if df.empty:
                return {}
            
            stats = {
                'total_matches': len(df),
                'total_volume_sol': df['match_amount'].sum(),
                'total_volume_usdc': df['total_usdc'].sum(),
                'avg_match_price': df['match_price'].mean(),
                'avg_spread': df['spread'].mean(),
                'avg_otc_vs_jupiter_spread': df['otc_vs_jupiter_spread'].mean() if 'otc_vs_jupiter_spread' in df.columns else None,
                'max_spread': df['spread'].max(),
                'min_spread': df['spread'].min(),
                'matches_today': len(df[df['timestamp'].dt.date == datetime.now().date()])
            }
            
            return stats
        except Exception as e:
            print(f"Error calculating match statistics: {e}")
            return {}
    
    def export_data(self, start_date: Optional[str] = None, 
                   end_date: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Export filtered data for analysis
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dict containing matches and prices DataFrames
        """
        try:
            matches_df = self.get_recent_matches(limit=10000)
            prices_df = self.get_recent_price_logs(limit=10000)
            
            # Apply date filters if provided
            if start_date:
                start_dt = pd.to_datetime(start_date)
                matches_df = matches_df[matches_df['timestamp'] >= start_dt]
                prices_df = prices_df[prices_df['timestamp'] >= start_dt]
            
            if end_date:
                end_dt = pd.to_datetime(end_date)
                matches_df = matches_df[matches_df['timestamp'] <= end_dt]
                prices_df = prices_df[prices_df['timestamp'] <= end_dt]
            
            return {
                'matches': matches_df,
                'prices': prices_df
            }
        except Exception as e:
            print(f"Error exporting data: {e}")
            return {'matches': pd.DataFrame(), 'prices': pd.DataFrame()}
