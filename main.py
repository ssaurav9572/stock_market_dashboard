import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews

# --- Streamlit UI ---
st.title("📊 Stock Dashboard")

# Sidebar Inputs
ticker = st.sidebar.text_input("Enter Ticker (e.g. AAPL, TSLA, RELIANCE.NS)")
start_date = st.sidebar.date_input("Enter Start Date")
end_date = st.sidebar.date_input("Enter End Date")

if ticker:
    try:
        # Download data
        data = yf.download(ticker, start=start_date, end=end_date)

        if data.empty:
            st.error("No data found for this ticker and date range. Try different inputs.")
            st.stop()

        # --- Fix for MultiIndex columns ---
            # --- Fix for MultiIndex columns ---
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = ['_'.join(col).strip() for col in data.columns.values]

        # Dynamically pick column for y-axis
        if "Adj Close" in data.columns:
            y_col = "Adj Close"
        elif any(col.startswith("Adj Close") for col in data.columns):
            y_col = [col for col in data.columns if col.startswith("Adj Close")][0]
        elif "Close" in data.columns:
            y_col = "Close"
        elif any(col.startswith("Close") for col in data.columns):
            y_col = [col for col in data.columns if col.startswith("Close")][0]
        else:
            y_col = data.select_dtypes(include='number').columns[0]


    except Exception as e:
        st.error(f"Error fetching stock data: {str(e)}")
        st.stop()

    # --- Chart ---
    st.subheader(f"Stock Price for {ticker}")
    fig = px.line(data.reset_index(), x="Date", y=y_col, title=f"{ticker} Price Trend")
    st.plotly_chart(fig)

    # --- Tabs ---
    pricing_data, fundamental_data, news = st.tabs(
        ["Pricing Data", "Fundamental Data", "Top 10 News"]
    )

    # --- Pricing Data ---
    with pricing_data:
        st.header("📈 Price Movements")
        data2 = data.copy()
        data2["% Change"] = data2[y_col].pct_change()
        data2.dropna(inplace=True)
        st.write(data2)

        if not data2.empty:
            annual_return = data2["% Change"].mean() * 252 * 100
            st.write("Annual Return is :", round(annual_return, 2), "%")
        else:
            st.warning("Not enough data to calculate annual return.")

    # --- Fundamental Data ---
    with fundamental_data:
        st.header("📑 Fundamental Data")
        key='PZTY1Y8I6TU9A69I'  # ⚠️ Replace with your Alpha Vantage API key
        fd = FundamentalData(key, output_format="pandas")

        try:
            st.subheader("Balance Sheet")
            balance_sheet, _ = fd.get_balance_sheet_annual(ticker)
            if not balance_sheet.empty:
                bs = balance_sheet.T[2:]
                bs.columns = list(balance_sheet.T.iloc[0])
                st.write(bs)
            else:
                st.warning("No Balance Sheet data available.")

            st.subheader("Income Statement")
            income_statement, _ = fd.get_income_statement_annual(ticker)
            if not income_statement.empty:
                is1 = income_statement.T[2:]
                is1.columns = list(income_statement.T.iloc[0])
                st.write(is1)
            else:
                st.warning("No Income Statement data available.")

            st.subheader("Cash Flow Statement")
            cash_flow, _ = fd.get_cash_flow_annual(ticker)
            if not cash_flow.empty:
                cf = cash_flow.T[2:]
                cf.columns = list(cash_flow.T.iloc[0])
                st.write(cf)
            else:
                st.warning("No Cash Flow data available.")

        except Exception as e:
            st.error(f"Error fetching fundamental data: {str(e)}")

    # --- News ---
    with news:
        st.header(f"📰 Latest News on {ticker}")
        try:
            sn = StockNews(ticker, save_news=False)
            df_news = sn.read_rss()

            if not df_news.empty:
                for i in range(min(10, len(df_news))):
                    st.subheader(f"News {i+1}")
                    st.write(df_news["published"][i])
                    st.write(df_news["title"][i])
                    st.write(df_news["summary"][i])
                    st.write(f"Title Sentiment: {df_news['sentiment_title'][i]}")
                    st.write(f"News Sentiment: {df_news['sentiment_summary'][i]}")
            else:
                st.info(f"No news found for {ticker}.")

        except Exception as e:
            st.error(f"Error fetching news: {str(e)}")

else:
    st.write("👆 Please enter a ticker to fetch data.")
