import pandas as pd
import numpy as np
import yfinance as yf
import input_functions as input_function
import plotly.graph_objects as go



symbol='RELIANCE.NS'

data = yf.download(symbol, interval='30m', period='5d')

print(data)

final_trend=input_function.check_for_given(data,40,30)
print(final_trend)
supports, resistances = input_function.get_support_resistance(data, 0, final_trend)
print(supports, resistances)
########

data=data.iloc[-200:,]

print(data.tail(10))










    