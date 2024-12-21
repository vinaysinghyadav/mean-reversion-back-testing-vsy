import yfinance as yf
import pandas as pd
import datetime
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def calculate_buy_sell_signals(ticker, window=10, z_score_threshold=2):
    """Calculates z-scores, buy/sell signals, and daily PnL."""
    try:
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(365)

        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            print(f"No data found for {ticker}")
            return None

        data['Rolling_Mean'] = data['Close'].rolling(window=window).mean()
        data['Rolling_Std'] = data['Close'].rolling(window=window).std()
        data.dropna(inplace=True)

        close_values = data['Close'].values
        rolling_mean_values = data['Rolling_Mean'].values
        rolling_std_values = data['Rolling_Std'].values

        nan_indices_mean = np.isnan(rolling_mean_values)
        nan_indices_std = np.isnan(rolling_std_values)

        rolling_mean_filled = np.copy(rolling_mean_values)
        rolling_std_filled = np.copy(rolling_std_values)

        rolling_mean_filled[nan_indices_mean] = 0.0
        rolling_std_filled[nan_indices_std] = 1.0

        close_values = close_values.flatten()
        rolling_mean_filled = rolling_mean_filled.flatten()
        rolling_std_filled = rolling_std_filled.flatten()

        data['Z-Score'] = (close_values - rolling_mean_filled) / rolling_std_filled

        data['Signal'] = np.where(data['Z-Score'] < -z_score_threshold, 1,  # Buy = 1
                                np.where(data['Z-Score'] > z_score_threshold, -1, 0)) # Sell = -1, Hold = 0

        # Calculate Daily PnL
        data['Daily_Return'] = data['Close'].pct_change()
        data['Position'] = data['Signal'].shift(1).fillna(0) # Shift signals to avoid lookahead bias
        data['Daily_PnL'] = data['Position'] * data['Daily_Return']

        # Calculate additional metrics
        data['Cumulative_PnL'] = data['Daily_PnL'].cumsum()
        yearly_yield = data['Cumulative_PnL'].iloc[-1]
        num_buy_signals = int((data['Signal'] == 1).sum())
        num_sell_signals = int((data['Signal'] == -1).sum())

        # Holding periods
        holding_periods = data[data['Signal'] != 0].index.to_series().diff().fillna(pd.Timedelta(seconds=0))

        # Sharpe Ratio
        sharpe_ratio = data['Daily_PnL'].mean() / data['Daily_PnL'].std() * np.sqrt(252) if data['Daily_PnL'].std() != 0 else np.nan

        metrics = {
            'Yearly Yield': yearly_yield,
            'Number of Buy Signals': num_buy_signals,
            'Number of Sell Signals': num_sell_signals,
            'Sharpe Ratio': sharpe_ratio,
            'Holding Periods': holding_periods
        }

        return data[['Close', 'Rolling_Mean', 'Rolling_Std', 'Z-Score', 'Signal', 'Daily_PnL']], metrics

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        print(traceback.format_exc())
        return None, None

# Streamlit App
st.title("Z-Score Analysis, Buy/Sell Signals, and PnL")
st.sidebar.title("Input Parameters")
st.sidebar.image("https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png", width=100)
st.sidebar.text("Made by Vinay Singh Yadav")

# State management for plot reset
stock = st.sidebar.text_input("Enter stock ticker (e.g., AAPL)", "AAPL")
window = st.sidebar.number_input("Moving Average Window", 10)
z_score_threshold = st.sidebar.number_input("Z-Score Threshold (for Buy/Sell)", 2.0)
start_date_for_analysis = st.sidebar.date_input("Analysis Start Date", pd.to_datetime("2023-01-03"))
start_date = start_date_for_analysis - datetime.timedelta(days=window)
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-01-03"))

@st.cache_data # Use st.cache_data for caching
def get_data(stock, window, z_score_threshold, start_date, end_date):
    return calculate_buy_sell_signals(stock, window, z_score_threshold)

if st.sidebar.button("Calculate Z-Scores and Signals"):
    with st.spinner("Fetching data and calculating..."):
        try:
            result_df, metrics = get_data(stock, window, z_score_threshold, start_date, end_date)

            if result_df is not None:
                st.write("### Z-Scores, Signals, Closing Prices, and Daily PnL")
                st.dataframe(result_df)

                st.write("### Key Metrics")
                st.write(metrics)

                # Create subplots using Plotly
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.6, 0.4])

                # Plot Z-Scores
                fig.add_trace(go.Scatter(x=result_df.index, y=result_df['Z-Score'], name="Z-Scores"), row=1, col=1)
                fig.add_trace(go.Scatter(x=result_df.index, y=[z_score_threshold] * len(result_df),
                                        line=dict(color='red', dash='dash'), name=f"Sell Threshold (+{z_score_threshold})"), row=1, col=1)
                fig.add_trace(go.Scatter(x=result_df.index, y=[-z_score_threshold] * len(result_df),
                                        line=dict(color='green', dash='dash'), name=f"Buy Threshold (-{z_score_threshold})"), row=1, col=1)

                # Add Buy/Sell Signal markers
                buy_signals = result_df[result_df['Signal'] == 1]
                sell_signals = result_df[result_df['Signal'] == -1]
                fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Z-Score'], mode='markers',
                                        marker=dict(symbol='triangle-up', color='green', size=10), name='Buy Signal'), row=1, col=1)
                fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['Z-Score'], mode='markers',
                                        marker=dict(symbol='triangle-down', color='red', size=10), name='Sell Signal'), row=1, col=1)

                # Plot Cumulative PnL
                fig.add_trace(go.Scatter(x=result_df.index, y=result_df['Daily_PnL'].cumsum(), name='Cumulative PnL'), row=2, col=1)

                fig.update_yaxes(automargin=True, row=2, col=1)
                fig.update_layout(height=800,
                                title_text=f"Z-Scores, Buy/Sell Signals, and PnL for {stock} ({window}-Day Window)",
                                xaxis_rangeslider_visible=True,
                                xaxis=dict(rangeslider=dict(thickness=0.1)))

                st.plotly_chart(fig)

                # Center the creator line
                st.markdown("<h4 style='text-align: center; color: blue;'>Made by Vinay Singh Yadav</h4>", unsafe_allow_html=True)

            else:
                st.warning("No valid data to display. Check ticker symbol or date range.")

        except Exception as e:
            st.error(f"An error occurred: {e}")
            import traceback
            st.write(traceback.format_exc())
