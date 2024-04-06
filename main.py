import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews

title=st.title("Stock Dashboard")
ticker=st.sidebar.text_input("Enter Ticker")
start_date=st.sidebar.date_input("Enter Start Date")
end_date=st.sidebar.date_input("Enter End Date")
if ticker:
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
    except Exception as e:
            st.error(f"Error fetching stock data: {str(e)}")
            st.stop()
    fig=px.line(data,x=data.index,y=data['Adj Close'],title=ticker)
    st.plotly_chart(fig)
    pricing_data,fundamental_data,news=st.tabs(["Pricing Data", "Fundamental Data", "Top 10 News"])
    with pricing_data:
        st.header('Price Movements')
        data2=data
        data2['% Change']=data['Adj Close']/data['Adj Close'].shift(1) -1
        data2.dropna(inplace=True)
        st.write(data2)
        annual_return=data2['% Change'].mean()*252*100
        st.write('Annual Return is :',annual_return,'%')



    with fundamental_data:
        key='PZTY1Y8I6TU9A69I'
        fd=FundamentalData(key,output_format='pandas')
        st.subheader('Balance Sheet')
        balance_sheet=fd.get_balance_sheet_annual(ticker)[0]
        bs=balance_sheet.T[2:]
        bs.columns=list(balance_sheet.T.iloc[0])
        st.write(bs)
        st.subheader('income Statement')
        income_statement=fd.get_income_statement_annual(ticker)[0]
        is1=income_statement.T[2:]
        is1.columns = list(income_statement.T.iloc[0])
        st.write(is1)
        st.subheader('Cash Flow Statement')
        cash_flow=fd.get_cash_flow_annual(ticker)[0]
        cf=cash_flow.T[2:]
        cf.columns=list(cash_flow.T.iloc[0])
        st.write(cf)



    with news:
        st.header(f'News of {ticker}')
        sn=StockNews(ticker,save_news=False)
        df_news=sn.read_rss()
        if not df_news.empty:
            for i in range(10):
                st.subheader(f'News {i+1}')
                st.write(df_news['published'][i])
                st.write(df_news['title'][i])
                st.write(df_news['summary'][i])
                title_sentiment=df_news['sentiment_title'][i]
                st.write(f'Title Sentiment {title_sentiment}')
                news_sentiment=df_news['sentiment_summary'][i]
                st.write(f'News Sentiment {news_sentiment}')
        else:
                st.write(f"No news found for {ticker}.")
else:
    st.write("Please enter a ticker to fetch data.")