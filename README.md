# Z-Score Analysis, Buy/Sell Signals, and PnL with Streamlit and Plotly

This project provides an interactive dashboard to analyze stock prices, calculate Z-scores, and generate buy/sell signals using a simple statistical trading strategy. The app is built using Streamlit, yFinance, and Plotly.

---

## Features

- **Z-Score Calculation**: Computes Z-scores for stock prices based on rolling mean and standard deviation.
- **Buy/Sell Signals**: Generates buy/sell signals based on user-defined Z-score thresholds.
- **Performance Metrics**:
  - Yearly Yield
  - Sharpe Ratio
  - Number of Buy/Sell Signals
- **PnL Tracking**: Calculates daily profit and loss (PnL) and cumulative PnL.
- **Interactive Charts**: Visualizes Z-scores, thresholds, buy/sell signals, and cumulative PnL.

---

## Getting Started

### Prerequisites

Ensure you have Python installed and the following libraries:

- `streamlit`
- `yfinance`
- `pandas`
- `numpy`
- `plotly`

Install the dependencies using pip:

```bash
pip install streamlit yfinance pandas numpy plotly
```

## Running the App

Clone the repository:

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

## Usage

1. **Enter Stock Ticker**: Input the stock ticker (e.g., `AAPL` for Apple).  
2. **Set Parameters**:  
   - **Moving Average Window** (e.g., `10`)  
   - **Z-Score Threshold** (e.g., `2.0`)  
   - **Date Range**: Specify the analysis start and end dates.  
3. **Click Calculate Z-Scores and Signals**.  

### The dashboard will display:
- A data table with Z-scores, signals, and PnL.
- Metrics summary.
- Interactive charts.

---

## Example Output

1. **Buy/Sell Signal Chart**  
2. **Cumulative PnL Chart**  

---

## File Structure

```bash
.
├── app.py             # Main application code
├── README.md          # Documentation
└── requirements.txt   # Dependencies
```

## Author
Made by Vinay Singh Yadav

## License
This project is licensed under the MIT License.

