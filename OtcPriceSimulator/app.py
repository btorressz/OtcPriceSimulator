import streamlit as st
import pandas as pd
import numpy as np
import time
import threading
from datetime import datetime, timedelta
import os
from jupiter_api import JupiterAPI
from otc_pool import OTCPool
from csv_logger import CSVLogger
from price_monitor import PriceMonitor

# Initialize components
@st.cache_resource
def init_components():
    jupiter_api = JupiterAPI()
    otc_pool = OTCPool()
    csv_logger = CSVLogger()
    price_monitor = PriceMonitor(jupiter_api, otc_pool, csv_logger)
    return jupiter_api, otc_pool, csv_logger, price_monitor

def main():
    st.set_page_config(
        page_title="OTC Trading Pool Simulator",
        page_icon="💱",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("💱 OTC Trading Pool Simulator")
    st.markdown("### SOL → USDC Private Pool vs Jupiter DEX")
    
    # Initialize components
    jupiter_api, otc_pool, csv_logger, price_monitor = init_components()
    
    # Real-time market data section
    st.header("📊 Live Market Data")
    
    # Fetch and display live market data
    col1, col2, col3 = st.columns(3)
    
    # Auto-refresh market data when monitoring is active
    if st.session_state.get('monitoring_active', False):
        # Only refresh if it's been more than 60 seconds since last update
        if (not st.session_state.get('last_market_update') or 
            (datetime.now() - st.session_state.last_market_update).seconds > 60):
            market_data = jupiter_api.get_market_data()
            if market_data:
                st.session_state.market_data = market_data
                st.session_state.last_market_update = datetime.now()
    
    with col1:
        if st.button("🔄 Refresh Market Data"):
            market_data = jupiter_api.get_market_data()
            if market_data:
                st.session_state.market_data = market_data
                st.session_state.last_market_update = datetime.now()
                st.success("Market data updated!")
            else:
                st.error("Failed to fetch market data")
            st.rerun()
    
    # Display SOL market data with enhanced styling
    if st.session_state.get('market_data') and 'solana' in st.session_state.market_data:
        sol_data = st.session_state.market_data['solana']
        
        with col1:
            st.subheader("🔸 Solana (SOL)")
            
            # Price with trend indicator
            price_change = sol_data['change_24h']
            price_color = "#00ff88" if price_change >= 0 else "#ff4444"
            trend_icon = "📈" if price_change >= 0 else "📉"
            
            # Create metrics with delta
            st.metric(
                label="Current Price",
                value=f"${sol_data['price']:.4f}",
                delta=f"{price_change:.2f}%"
            )
            
            # Additional metrics in compact format
            st.markdown(f"""
            <div style='background-color: rgba(255,255,255,0.1); padding: 10px; border-radius: 5px; margin: 5px 0;'>
                <strong>Market Cap:</strong> ${sol_data['market_cap']:,.0f}<br>
                <strong>24h Volume:</strong> ${sol_data['volume_24h']:,.0f}<br>
                <strong>Rank:</strong> #{sol_data['market_cap_rank']}<br>
                <strong>Supply:</strong> {sol_data['circulating_supply']:,.0f} SOL
            </div>
            """, unsafe_allow_html=True)
    
    # Display USDC market data with enhanced styling
    if st.session_state.get('market_data') and 'usdc' in st.session_state.market_data:
        usdc_data = st.session_state.market_data['usdc']
        
        with col2:
            st.subheader("🔹 USD Coin (USDC)")
            
            # USDC price with stability indicator
            price_change = usdc_data['change_24h']
            
            st.metric(
                label="Current Price",
                value=f"${usdc_data['price']:.6f}",
                delta=f"{price_change:.4f}%"
            )
            
            # USDC specific metrics
            st.markdown(f"""
            <div style='background-color: rgba(255,255,255,0.1); padding: 10px; border-radius: 5px; margin: 5px 0;'>
                <strong>Market Cap:</strong> ${usdc_data['market_cap']:,.0f}<br>
                <strong>24h Volume:</strong> ${usdc_data['volume_24h']:,.0f}<br>
                <strong>Rank:</strong> #{usdc_data['market_cap_rank']}<br>
                <strong>Supply:</strong> {usdc_data['circulating_supply']:,.0f} USDC
            </div>
            """, unsafe_allow_html=True)
    
    # Display additional market metrics with enhanced presentation
    with col3:
        st.subheader("📈 Market Analysis")
        
        if st.session_state.get('market_data') and 'solana' in st.session_state.market_data:
            sol_data = st.session_state.market_data['solana']
            
            # Performance metrics with visual indicators
            changes = [
                ("1h", sol_data.get('change_1h', 0)),
                ("24h", sol_data.get('change_24h', 0)),
                ("7d", sol_data.get('change_7d', 0))
            ]
            
            # Create a performance dashboard
            for period, change in changes:
                color = "#00ff88" if change >= 0 else "#ff4444"
                icon = "▲" if change >= 0 else "▼"
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; padding: 5px; margin: 2px 0; background-color: rgba(255,255,255,0.05); border-radius: 3px;'>
                    <span><strong>SOL {period}:</strong></span>
                    <span style='color: {color}'>{icon} {change:+.2f}%</span>
                </div>
                """, unsafe_allow_html=True)
            
            # Market status indicator
            overall_trend = sum([sol_data.get('change_1h', 0), sol_data.get('change_24h', 0), sol_data.get('change_7d', 0)]) / 3
            if overall_trend > 1:
                market_status = "🟢 Bullish"
            elif overall_trend > -1:
                market_status = "🟡 Neutral"
            else:
                market_status = "🔴 Bearish"
            
            st.markdown(f"**Market Sentiment:** {market_status}")
            
            # Last update with freshness indicator
            if st.session_state.get('last_market_update'):
                update_age = (datetime.now() - st.session_state.last_market_update).seconds
                freshness = "🟢 Fresh" if update_age < 60 else "🟡 Stale" if update_age < 300 else "🔴 Old"
                st.markdown(f"**Data Status:** {freshness}")
                st.markdown(f"**Last Update:** {st.session_state.last_market_update.strftime('%H:%M:%S')}")
        else:
            st.info("Click 'Refresh Market Data' to load live prices")
    
    st.divider()
    
    # Advanced Jupiter Analytics Section
    st.header("🔬 Advanced Jupiter Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Price Impact Analysis", "Route Analysis", "Technical Indicators"])
    
    with tab1:
        st.subheader("📊 Price Impact Analysis")
        col1, col2 = st.columns([2, 1])
        
        with col2:
            if st.button("🔍 Analyze Price Impact"):
                with st.spinner("Analyzing price impact across order sizes..."):
                    amounts = [0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]
                    impact_data = jupiter_api.get_price_impact_analysis(amounts)
                    
                    if impact_data and any(v is not None for v in impact_data.values()):
                        st.session_state.impact_analysis = impact_data
                        st.success("Analysis complete!")
                    else:
                        st.error("Unable to fetch price impact data")
        
        with col1:
            if st.session_state.get('impact_analysis'):
                valid_data = {k: v for k, v in st.session_state.impact_analysis.items() 
                             if v is not None and not pd.isna(v) and isinstance(v, (int, float)) 
                             and np.isfinite(v) and np.isfinite(k)}
                
                if valid_data and len(valid_data) >= 2:
                    # Create properly validated chart data
                    amounts = sorted(list(valid_data.keys()))
                    impacts = [valid_data[a] for a in amounts]
                    
                    # Only proceed if we have valid numeric data
                    if all(isinstance(a, (int, float)) and isinstance(i, (int, float)) for a, i in zip(amounts, impacts)):
                        chart_df = pd.DataFrame({
                            'Price_Impact_Pct': impacts
                        }, index=amounts)
                        chart_df.index.name = 'Amount_SOL'
                        
                        # Final validation - ensure no inf/nan values
                        if not chart_df.isnull().any().any() and np.isfinite(chart_df.values).all():
                            st.line_chart(chart_df)
                            
                            # Categorize by impact
                            low_impact = [k for k, v in valid_data.items() if v <= 0.1]
                            medium_impact = [k for k, v in valid_data.items() if 0.1 < v <= 0.5]
                            high_impact = [k for k, v in valid_data.items() if v > 0.5]
                            
                            st.markdown("**Optimal Order Sizes:**")
                            if low_impact:
                                st.success(f"Low Impact (<0.1%): {', '.join(map(str, low_impact))} SOL")
                            if medium_impact:
                                st.warning(f"Medium Impact (0.1-0.5%): {', '.join(map(str, medium_impact))} SOL")
                            if high_impact:
                                st.error(f"High Impact (>0.5%): {', '.join(map(str, high_impact))} SOL")
                        else:
                            st.info("Price impact data contains invalid values")
                    else:
                        st.info("Invalid price impact data format")
                else:
                    st.info("Click 'Analyze Price Impact' to see results")
    
    with tab2:
        st.subheader("🛣️ Jupiter Route Analysis")
        route_amount = st.number_input("Amount for Route Analysis", min_value=0.1, value=5.0, step=0.1)
        
        if st.button("🗺️ Analyze Routes"):
            with st.spinner("Fetching detailed routing information..."):
                advanced_quote = jupiter_api.get_advanced_quote_with_routes(route_amount)
                
                if advanced_quote:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Price per SOL", f"${advanced_quote['price']:.4f}")
                        st.metric("Price Impact", f"{advanced_quote['price_impact_pct']:.4f}%")
                        st.metric("Output Amount", f"{advanced_quote['output_amount']:.2f} USDC")
                    
                    with col2:
                        st.metric("Route Steps", advanced_quote['route_count'])
                        st.metric("Processing Time", f"{advanced_quote.get('time_taken', 0)}ms")
                        
                    if advanced_quote['routes']:
                        st.markdown("**Routing Steps:**")
                        for route in advanced_quote['routes']:
                            percent = route.get('percent', 0)
                            st.markdown(f"- Step {route['step']}: {percent}% of trade")
                else:
                    st.error("Unable to fetch routing data")
    
    with tab3:
        st.subheader("📈 Technical Analysis Dashboard")
        
        try:
            price_logs_df = csv_logger.get_recent_price_logs(limit=100)
            if not price_logs_df.empty:
                price_logs_df['timestamp'] = pd.to_datetime(price_logs_df['timestamp'])
                price_logs_df = price_logs_df.sort_values('timestamp')
                prices = price_logs_df['jupiter_price']
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if len(prices) > 14 and isinstance(prices, pd.Series):
                        try:
                            delta = prices.diff()
                            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                            
                            # Avoid division by zero
                            rs = gain.div(loss).fillna(0)
                            rsi = 100 - (100 / (1 + rs))
                            
                            # Get the last valid RSI value
                            valid_rsi = rsi.dropna()
                            if len(valid_rsi) > 0:
                                current_rsi = valid_rsi.iloc[-1]
                                
                                st.metric("RSI (14)", f"{current_rsi:.1f}")
                                if current_rsi > 70:
                                    st.error("Overbought")
                                elif current_rsi < 30:
                                    st.success("Oversold")
                                else:
                                    st.info("Neutral")
                            else:
                                st.metric("RSI (14)", "Calculating...")
                        except Exception:
                            st.metric("RSI (14)", "Error")
                    else:
                        st.metric("RSI (14)", "Need more data")
                
                with col2:
                    if len(prices) > 1:
                        returns = prices.pct_change().dropna()
                        volatility = returns.std() * np.sqrt(24)
                        
                        st.metric("24h Volatility", f"{volatility:.2%}")
                        
                        if volatility > 0.1:
                            st.error("High volatility")
                        elif volatility > 0.05:
                            st.warning("Medium volatility")
                        else:
                            st.success("Low volatility")
                    else:
                        st.metric("24h Volatility", "N/A")
                
                with col3:
                    current_price = prices.iloc[-1]
                    if len(prices) > 10:
                        ma_short = prices.tail(5).mean()
                        ma_long = prices.tail(20).mean() if len(prices) >= 20 else prices.mean()
                        
                        momentum = ((current_price - ma_long) / ma_long) * 100
                        st.metric("Price Momentum", f"{momentum:+.2f}%")
                        
                        if momentum > 2:
                            st.success("Strong bullish")
                        elif momentum > 0:
                            st.success("Bullish")
                        elif momentum > -2:
                            st.info("Sideways")
                        else:
                            st.error("Bearish")
                    else:
                        st.metric("Price Momentum", "N/A")
                
                # Price chart with moving averages
                if len(prices) >= 10:
                    try:
                        chart_df = price_logs_df.tail(50).copy()
                        
                        # Ensure we have valid data before calculations
                        if 'jupiter_price' in chart_df.columns and not chart_df['jupiter_price'].empty:
                            # Calculate moving averages
                            chart_df['MA_5'] = chart_df['jupiter_price'].rolling(window=5, min_periods=1).mean()
                            if len(chart_df) >= 20:
                                chart_df['MA_20'] = chart_df['jupiter_price'].rolling(window=20, min_periods=1).mean()
                            
                            # Clean and validate data
                            valid_mask = (
                                pd.notna(chart_df['jupiter_price']) & 
                                pd.notna(chart_df['timestamp']) &
                                (chart_df['jupiter_price'] > 0) &
                                np.isfinite(chart_df['jupiter_price'])
                            )
                            
                            clean_df = chart_df[valid_mask].copy()
                            
                            if len(clean_df) >= 5:
                                # Create chart data with proper structure
                                timestamps = pd.to_datetime(clean_df['timestamp'])
                                prices = clean_df['jupiter_price'].values
                                ma5_series = clean_df['MA_5'].fillna(clean_df['jupiter_price'])
                                
                                chart_data = pd.DataFrame({
                                    'Price': prices,
                                    'MA 5': ma5_series.values
                                }, index=timestamps)
                                
                                if 'MA_20' in clean_df.columns:
                                    ma20_series = clean_df['MA_20'].fillna(clean_df['jupiter_price'])
                                    chart_data['MA 20'] = ma20_series.values
                                
                                # Final validation - ensure all values are finite
                                chart_data = chart_data.select_dtypes(include=[np.number])
                                chart_data = chart_data.replace([np.inf, -np.inf], np.nan).dropna()
                                
                                if not chart_data.empty and len(chart_data) > 1:
                                    st.line_chart(chart_data)
                                else:
                                    st.info("Building chart with more data points...")
                            else:
                                st.info("Collecting price data for chart...")
                        else:
                            st.info("Start price monitoring to see price chart")
                    except Exception:
                        st.info("Price chart will appear after data collection")
            else:
                st.info("Start price monitoring to see technical analysis")
        
        except Exception as e:
            st.error(f"Technical analysis error: {str(e)}")
    
    # Smart Trading Assistant
    st.header("🎯 Smart Trading Assistant")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💡 Optimal Pricing Suggestions")
        suggest_type = st.selectbox("Order Type", ["BUY", "SELL"])
        suggest_amount = st.number_input("Order Amount (SOL)", min_value=0.1, value=1.0, step=0.1)
        
        if st.button("🔮 Get Pricing Suggestion"):
            if st.session_state.get('last_jupiter_price'):
                quote_data = jupiter_api.get_advanced_quote_with_routes(suggest_amount)
                
                if quote_data:
                    jupiter_price = quote_data['price']
                    price_impact = quote_data['price_impact_pct']
                    
                    # Calculate suggested pricing
                    base_adjustment = 0.5
                    impact_adjustment = price_impact * 0.5
                    market_vol = abs(st.session_state.get('market_data', {}).get('solana', {}).get('change_24h', 0)) * 0.1
                    
                    total_adjustment = base_adjustment + impact_adjustment + market_vol
                    
                    if suggest_type == "BUY":
                        suggested_price = jupiter_price * (1 + total_adjustment / 100)
                        st.success(f"Suggested Buy Price: ${suggested_price:.4f}")
                        st.info(f"Premium: {total_adjustment:.2f}%")
                    else:
                        suggested_price = jupiter_price * (1 - total_adjustment / 100)
                        st.success(f"Suggested Sell Price: ${suggested_price:.4f}")
                        st.info(f"Discount: {total_adjustment:.2f}%")
                    
                    st.markdown(f"**Jupiter Reference:** ${jupiter_price:.4f}")
                    st.markdown(f"**Price Impact:** {price_impact:.4f}%")
                else:
                    st.error("Unable to fetch pricing data")
            else:
                st.warning("Please refresh Jupiter price first")
    
    with col2:
        st.subheader("⚖️ Arbitrage Scanner")
        
        if st.button("🔍 Scan Arbitrage Opportunities"):
            active_offers = otc_pool.get_active_offers()
            jupiter_price = st.session_state.get('last_jupiter_price')
            
            if active_offers and jupiter_price:
                with st.spinner("Scanning for arbitrage opportunities..."):
                    opportunities = []
                    
                    for offer in active_offers:
                        otc_price = offer['price_per_sol']
                        offer_type = offer['type']
                        amount = offer['sol_amount']
                        
                        # Calculate basic spread first
                        if offer_type == 'BUY':
                            spread = ((otc_price - jupiter_price) / jupiter_price) * 100
                        else:
                            spread = ((jupiter_price - otc_price) / jupiter_price) * 100
                        
                        # Only fetch detailed quote if spread looks promising
                        if abs(spread) > 1.0:  # Pre-filter for efficiency
                            try:
                                quote_data = jupiter_api.get_sol_usdc_quote(amount)
                                if quote_data and 'price_impact_pct' in quote_data:
                                    price_impact_raw = quote_data.get('price_impact_pct', 0)
                                    
                                    # Handle different price impact formats
                                    if isinstance(price_impact_raw, str):
                                        try:
                                            price_impact = float(price_impact_raw.replace('%', ''))
                                        except:
                                            price_impact = 0.0
                                    else:
                                        price_impact = float(price_impact_raw) if price_impact_raw else 0.0
                                    
                                    net_spread = spread - price_impact
                                    
                                    # Lower threshold for better opportunity detection
                                    if net_spread > 0.25:
                                        score = min(100, max(0, net_spread * 15))  # More generous scoring
                                        opportunities.append({
                                            'id': offer['id'],
                                            'type': offer_type,
                                            'amount': amount,
                                            'otc_price': otc_price,
                                            'jupiter_price': jupiter_price,
                                            'spread': spread,
                                            'price_impact': price_impact,
                                            'net_spread': net_spread,
                                            'score': score
                                        })
                                else:
                                    # Fallback without price impact
                                    if abs(spread) > 2.0:  # Higher threshold without impact data
                                        opportunities.append({
                                            'id': offer['id'],
                                            'type': offer_type,
                                            'amount': amount,
                                            'otc_price': otc_price,
                                            'jupiter_price': jupiter_price,
                                            'spread': spread,
                                            'price_impact': 0.0,
                                            'net_spread': spread,
                                            'score': min(100, max(0, abs(spread) * 10))
                                        })
                            except Exception as e:
                                st.warning(f"Error analyzing offer #{offer['id']}: {str(e)}")
                                continue
                    
                    if opportunities:
                        st.success(f"Found {len(opportunities)} arbitrage opportunities!")
                        opportunities.sort(key=lambda x: x['score'], reverse=True)
                        
                        # Display top opportunities
                        for i, opp in enumerate(opportunities[:5]):  # Show top 5
                            score = opp['score'] 
                            
                            # Color coding
                            if score > 70:
                                st.success(f"🎯 **High Value Opportunity #{i+1}**")
                            elif score > 40:
                                st.warning(f"⚡ **Medium Opportunity #{i+1}**")
                            else:
                                st.info(f"📊 **Low Opportunity #{i+1}**")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Offer ID", f"#{opp['id']}")
                                st.metric("Type", opp['type'])
                            with col2:
                                st.metric("Amount", f"{opp['amount']} SOL")
                                st.metric("OTC Price", f"${opp['otc_price']:.4f}")
                            with col3:
                                st.metric("Gross Spread", f"{opp['spread']:.2f}%")
                                st.metric("Net Spread", f"{opp['net_spread']:.2f}%")
                            
                            st.metric("Opportunity Score", f"{score:.0f}/100")
                            st.divider()
                    else:
                        st.info("No profitable arbitrage opportunities found at current market conditions")
                        
                        # Show why no opportunities exist
                        if active_offers:
                            st.markdown("**Analysis Summary:**")
                            total_offers = len(active_offers)
                            buy_offers = len([o for o in active_offers if o['type'] == 'BUY'])
                            sell_offers = len([o for o in active_offers if o['type'] == 'SELL'])
                            
                            st.markdown(f"- Analyzed {total_offers} offers ({buy_offers} BUY, {sell_offers} SELL)")
                            st.markdown(f"- Jupiter reference price: ${jupiter_price:.4f}")
                            st.markdown("- All spreads below profitability threshold (0.25%)")
            else:
                if not active_offers:
                    st.warning("No active offers in the pool. Create some offers first!")
                else:
                    st.warning("Jupiter price not available. Try refreshing market data.")
    
    st.divider()
    
    # Initialize session state
    if 'monitoring_active' not in st.session_state:
        st.session_state.monitoring_active = False
    if 'last_jupiter_price' not in st.session_state:
        st.session_state.last_jupiter_price = None
    if 'last_update_time' not in st.session_state:
        st.session_state.last_update_time = None
    if 'market_data' not in st.session_state:
        st.session_state.market_data = None
    if 'last_market_update' not in st.session_state:
        st.session_state.last_market_update = None
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Theme selection
        st.subheader("🎨 Theme Options")
        theme_option = st.selectbox(
            "Choose Theme",
            ["Dark Green", "Dark Blue", "Purple", "Orange", "Red", "Light Mode"],
            index=0
        )
        
        # Apply theme changes
        if theme_option != st.session_state.get('current_theme', 'Dark Green'):
            st.session_state.current_theme = theme_option
            theme_colors = {
                "Dark Green": {"primary": "#00ff88", "bg": "#0e1117", "secondary": "#262730"},
                "Dark Blue": {"primary": "#1f77b4", "bg": "#0e1117", "secondary": "#262730"},
                "Purple": {"primary": "#9467bd", "bg": "#0e1117", "secondary": "#262730"},
                "Orange": {"primary": "#ff7f0e", "bg": "#0e1117", "secondary": "#262730"},
                "Red": {"primary": "#d62728", "bg": "#0e1117", "secondary": "#262730"},
                "Light Mode": {"primary": "#ff4b4b", "bg": "#ffffff", "secondary": "#f0f2f6"}
            }
            
            # Update config file
            selected_theme = theme_colors[theme_option]
            config_content = f"""[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
base = "{'light' if theme_option == 'Light Mode' else 'dark'}"
primaryColor = "{selected_theme['primary']}"
backgroundColor = "{selected_theme['bg']}"
secondaryBackgroundColor = "{selected_theme['secondary']}"
textColor = "{'#262730' if theme_option == 'Light Mode' else '#ffffff'}"
"""
            
            with open('.streamlit/config.toml', 'w') as f:
                f.write(config_content)
            
            st.info("Theme updated! Refresh the page to see changes.")
        
        # Monitoring controls
        st.subheader("📊 Price Monitoring")
        polling_interval = st.slider("Polling Interval (seconds)", 5, 60, 15)
        
        if st.button("Start Monitoring" if not st.session_state.monitoring_active else "Stop Monitoring"):
            if not st.session_state.monitoring_active:
                price_monitor.start_monitoring(polling_interval)
                st.session_state.monitoring_active = True
                st.success("Monitoring started!")
            else:
                price_monitor.stop_monitoring()
                st.session_state.monitoring_active = False
                st.info("Monitoring stopped!")
            st.rerun()
        
        # Jupiter API status
        st.subheader("Jupiter API Status")
        if st.session_state.last_jupiter_price:
            st.metric("SOL/USDC Price", f"${st.session_state.last_jupiter_price:.4f}")
            if st.session_state.last_update_time:
                st.caption(f"Last update: {st.session_state.last_update_time.strftime('%H:%M:%S')}")
        else:
            st.info("Fetching initial price...")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Post OTC Offer")
        
        # Offer form
        with st.form("otc_offer_form"):
            offer_type = st.selectbox("Offer Type", ["BUY", "SELL"])
            sol_amount = st.number_input("SOL Amount", min_value=0.01, value=1.0, step=0.01)
            price_per_sol = st.number_input("Price per SOL (USDC)", min_value=0.01, value=100.0, step=0.01)
            
            submitted = st.form_submit_button("Post Offer")
            
            if submitted:
                offer_id = otc_pool.add_offer(offer_type, sol_amount, price_per_sol)
                st.success(f"Offer posted! ID: {offer_id}")
                st.rerun()
    
    with col2:
        st.header("💰 Current Jupiter Price")
        
        # Fetch current Jupiter price
        if st.button("Refresh Jupiter Price"):
            try:
                price_data = jupiter_api.get_sol_usdc_quote(1.0)
                if price_data:
                    st.session_state.last_jupiter_price = price_data['price']
                    st.session_state.last_update_time = datetime.now()
                    st.success(f"Updated! Price: ${price_data['price']:.4f}")
                else:
                    st.error("Failed to fetch Jupiter price")
            except Exception as e:
                st.error(f"Error fetching price: {str(e)}")
            st.rerun()
        
        # Display current price comparison with enhanced styling
        if st.session_state.last_jupiter_price:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Current Jupiter Price", f"${st.session_state.last_jupiter_price:.4f}")
            with col2:
                if st.session_state.last_update_time:
                    time_diff = (datetime.now() - st.session_state.last_update_time).seconds
                    st.metric("Last Update", f"{time_diff}s ago")
            
            # Show price comparison for active offers with color coding
            active_offers = otc_pool.get_active_offers()
            if active_offers:
                st.subheader("🔍 Price Comparison")
                for offer in active_offers[-3:]:  # Show last 3 offers
                    jupiter_price = st.session_state.last_jupiter_price
                    otc_price = offer['price_per_sol']
                    
                    # Create columns for better layout
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**{offer['type']} #{offer['id']}** - {offer['sol_amount']} SOL")
                    
                    with col2:
                        st.write(f"${otc_price:.4f}")
                    
                    with col3:
                        if offer['type'] == 'BUY':
                            spread = ((otc_price - jupiter_price) / jupiter_price) * 100
                            if spread > 0:
                                st.markdown(f"<span style='color: #00ff88'>+{spread:.2f}%</span>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<span style='color: #ff4444'>{spread:.2f}%</span>", unsafe_allow_html=True)
                        else:  # SELL
                            spread = ((jupiter_price - otc_price) / jupiter_price) * 100
                            if spread > 0:
                                st.markdown(f"<span style='color: #00ff88'>+{spread:.2f}%</span>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<span style='color: #ff4444'>{spread:.2f}%</span>", unsafe_allow_html=True)
    
    # Active offers section with enhanced styling
    st.header("📊 Active OTC Offers")
    
    active_offers = otc_pool.get_active_offers()
    if active_offers:
        offers_df = pd.DataFrame(active_offers)
        
        # Add comparison columns if Jupiter price is available
        if st.session_state.last_jupiter_price:
            jupiter_price = st.session_state.last_jupiter_price
            offers_df['Jupiter Price'] = jupiter_price
            offers_df['Spread %'] = offers_df.apply(
                lambda row: calculate_spread(row['type'], row['price_per_sol'], jupiter_price), 
                axis=1
            )
            # Enhanced status with color coding
            def format_status(spread):
                if spread > 5:
                    return "🟢 Excellent"
                elif spread > 1:
                    return "🟡 Good"
                elif spread > -1:
                    return "⚪ Fair"
                else:
                    return "🔴 Poor"
            
            offers_df['Status'] = offers_df['Spread %'].apply(format_status)
        
        # Format the dataframe for display with better column names
        display_df = offers_df.copy()
        display_df['Created'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%H:%M:%S')
        display_df = display_df.drop(['timestamp', 'user_id', 'created_at'], axis=1, errors='ignore')
        
        # Rename columns for better display
        column_mapping = {
            'id': 'ID',
            'type': 'Type',
            'sol_amount': 'SOL Amount',
            'price_per_sol': 'OTC Price',
            'total_usdc': 'Total USDC',
            'status': 'Order Status'
        }
        display_df = display_df.rename(columns=column_mapping)
        
        # Apply color styling to dataframe
        def highlight_spreads(val):
            if isinstance(val, (int, float)):
                if val > 5:
                    return 'background-color: rgba(0, 255, 136, 0.3)'
                elif val > 1:
                    return 'background-color: rgba(255, 193, 7, 0.3)'
                elif val > -1:
                    return 'background-color: rgba(255, 255, 255, 0.1)'
                else:
                    return 'background-color: rgba(255, 68, 68, 0.3)'
            return ''
        
        if 'Spread %' in display_df.columns:
            styled_df = display_df.style.map(highlight_spreads, subset=['Spread %'])
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.dataframe(display_df, use_container_width=True)
        
        # Offer management
        st.subheader("🗑️ Manage Offers")
        col1, col2 = st.columns(2)
        
        with col1:
            offer_to_cancel = st.selectbox(
                "Select offer to cancel",
                options=[f"#{offer['id']} - {offer['type']} {offer['sol_amount']} SOL @ ${offer['price_per_sol']}" 
                        for offer in active_offers],
                key="cancel_select"
            )
            
            if st.button("Cancel Offer"):
                offer_id = int(offer_to_cancel.split('#')[1].split(' ')[0])
                if otc_pool.cancel_offer(offer_id):
                    st.success(f"Offer #{offer_id} cancelled!")
                    st.rerun()
        
        with col2:
            if st.button("🎯 Simulate Matching"):
                matches = otc_pool.simulate_matching()
                if matches:
                    st.success(f"Found {len(matches)} potential matches!")
                    for match in matches:
                        csv_logger.log_match(match)
                        st.info(f"Match: Buy #{match['buy_id']} with Sell #{match['sell_id']} - Spread: {match['spread']:.4f}")
                else:
                    st.info("No matches found")
    else:
        st.info("No active offers. Post an offer to get started!")
    
    # Recent matches and logs
    st.header("📈 Recent Activity")
    
    # Display recent matches
    try:
        matches_df = csv_logger.get_recent_matches(limit=10)
        if not matches_df.empty:
            st.subheader("Recent Matches")
            st.dataframe(matches_df, use_container_width=True)
    except Exception as e:
        st.info("No match history available yet")
    
    # Display price logs
    try:
        price_logs_df = csv_logger.get_recent_price_logs(limit=20)
        if not price_logs_df.empty:
            st.subheader("Price History")
            st.line_chart(price_logs_df.set_index('timestamp')['jupiter_price'])
    except Exception as e:
        st.info("No price history available yet")
    
    # Auto-refresh for monitoring
    if st.session_state.monitoring_active:
        time.sleep(1)
        st.rerun()

def calculate_spread(offer_type, otc_price, jupiter_price):
    """Calculate spread percentage based on offer type"""
    if offer_type == 'BUY':
        # For buy offers, positive spread means OTC price is higher (good for seller)
        return ((otc_price - jupiter_price) / jupiter_price) * 100
    else:  # SELL
        # For sell offers, positive spread means OTC price is lower (good for buyer)
        return ((jupiter_price - otc_price) / jupiter_price) * 100

if __name__ == "__main__":
    main()
