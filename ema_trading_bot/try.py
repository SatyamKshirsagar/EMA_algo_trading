


import yfinance as yf
import pandas as pd
import input_functions as input_functios
import json
from datetime import datetime
import os
import time
import requests

import yfinance as yf
import pandas as pd
import input_functions as input_functios
import json
from datetime import datetime
import os
import time
import requests

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, params=params)
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")
    else:
        print("Message sent successfully")

def give_predictoin_for_given_symbol(sector, decimal):
    result_dict = {}
    
    for symbol in sector:
        Suggetion = None
        price = False
        target = False
        stop_loss = False
        trend = None
        probablity_for_wining = 0
        
        # Download the stock data
        data = yf.download(symbol, interval='1m', period='5d')
        
        # Run your decision logic
        trend = input_functios.check_for_given(data, 15, 11)
        print(symbol, trend)
        print(data.shape[0])
        
        if trend != 'Consolidated':
            crossing_25_ema_flag, data = input_functios.check_cross_over(data, trend)
            print(crossing_25_ema_flag)
        
            if crossing_25_ema_flag:
                probablity_for_wining += 20
                supports, resistances = input_functios.get_support_resistance(data, decimal, trend)
                print(supports, resistances)
                
                valid_trend, valid_gap = input_functios.check_validity(trend, data)
                print(f'valid_trend is {valid_trend}, and valid_gap is {valid_gap}')
                
                if valid_trend and valid_gap:
                    probablity_for_wining += 20
                    stocastic_flag, stocastic_crossover = input_functios.valid_stocastic(data, 14, trend)
                    print(stocastic_flag, stocastic_crossover)
                    
                    touching_100_ema, crossing_25_ema_within_8, crossing_index, valid_last_14_candles = input_functios.check_for_consolidation_before_breakout(data, trend)
                    print(f'touching_100_ema: {touching_100_ema}, crossing_25_ema_within_8: {crossing_25_ema_within_8}, crossing_index: {crossing_index}, valid_last_14_candles: {valid_last_14_candles}')
                    #and valid_last_14_candlesv
                    if crossing_25_ema_within_8 and stocastic_flag  :
                        if not touching_100_ema:
                            probablity_for_wining += 40
                            probablity_for_wining += 10 if crossing_index < 5 else 5
                            probablity_for_wining += 10 if stocastic_crossover else 5
                            
                            price_to_bet, ema_50 = input_functios.place_order(data)
                            #print(trend)
                            
                            if trend == 'uptrend':
                                price = round(price_to_bet, decimal)
                                target = round(price + abs(1.5 * (price - ema_50)), decimal)
                                stop_loss = round(ema_50, decimal)
                            elif trend == 'Downtrend':
                                price = round(price_to_bet, decimal)
                                target = round(price - abs(1.5 * (price - ema_50)), decimal)
                                stop_loss = round(ema_50, decimal)
                            else:
                                pass
        
        # Set Suggetion based on price and target
        if price and target:
            Suggetion = 'Buy' if target > price else 'Sell' if target < price else None
        
        # Append results to the dictionary
        result_dict[symbol] = {
            'suggetion': Suggetion,
            'Trend': trend,
            'price': price,
            'target': target,
            'stop_loss': stop_loss,
            'probablity_for_wining': probablity_for_wining
        }
    
    return result_dict


# Function to append data to JSON file
def append_to_json(file_path, new_data):
    if os.path.exists(file_path):
        # Load existing data
        with open(file_path, "r") as json_file:
            try:
                existing_data = json.load(json_file)
            except json.JSONDecodeError:
                existing_data = {}
    else:
        existing_data = {}
    
    # Append new data to existing data
    if 'enjoy' in existing_data:
        existing_data['enjoy'].update(new_data)
    else:
        existing_data['enjoy'] = new_data
    
    # Write updated data back to JSON
    with open(file_path, "w") as json_file:
        json.dump(existing_data, json_file, indent=4)


# Function to format the output as a string for Telegram
def format_output_for_telegram(data):
    message = "*Trading Suggestions:*\n\n"
    for symbol, result in data.items():
        message += f"Symbol: *{symbol}*\n"
        message += f"Suggestion: {result['suggetion']}\n"
        message += f"Trend: {result['Trend']}\n"
        message += f"Price: {result['price']}\n"
        message += f"Target: {result['target']}\n"
        message += f"Stop Loss: {result['stop_loss']}\n"
        message += f"Winning Probability: {result['probablity_for_wining']}%\n"
        message += "\n"  # Add a blank line between symbols
    return message


# Main logic to run the prediction and append results every 1 minute
def main():
    # Define the file path for the JSON output
    file_path = "D:/Users/satyam.kshirsagar/Desktop/forex_bot/DATA/jeson_data/output.json"
    
    # Define the Telegram bot token and chat ID
    bot_token = "7633003504:AAGXoFdMuHmWZCyyD6sYSjeOCk7KkbcaiYk"
    chat_id = "-4547002355"
    

    # Fetch current timestamp, date, and month
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    date = now.strftime("%Y-%m-%d")
    month = now.strftime("%B")
    
    # Create the dictionary to store results
    Output_dict_final = {
        'timestamp': timestamp,
        'date': date,
        'month': month,
        'enjoy': {}
    }
    
    # Define the symbols for BTC/USDT and ETH/USDT
    #forex_pairs = ['USDJPY=X', 'EURUSD=X', 'USDCAD=X', 'USDAUD=X', 'EURCAD=X', 'EURJPY=X', 'EURAUD=X', 'AUDCAD=X', 'AUDJPY=X', 'CADJPY=X', 'CHFJPY=X']
    #crypto = ['BTC-USD', 'ETH-USD']
    
    forex_pairs = [
        'USDJPY=X', 'EURUSD=X', 'USDCAD=X', 'AUDUSD=X', 'EURCAD=X', 'EURJPY=X', 'EURAUD=X',
        'AUDCAD=X', 'AUDJPY=X', 'CADJPY=X', 'CHFJPY=X', 'GBPUSD=X', 'GBPAUD=X', 'GBPCAD=X',
        'GBPJPY=X', 'NZDUSD=X', 'NZDJPY=X', 'NZDCAD=X', 'NZDEUR=X', 'USDMXN=X', 'USDCHF=X',
        'USDHKD=X', 'USDINR=X', 'USDSGD=X', 'USDZAR=X', 'EURGBP=X', 'EURCHF=X', 'AUDCHF=X',
        'AUDNZD=X', 'CADCHF=X', 'GBPNZD=X', 'GBPCHF=X', 'EURNZD=X', 'NZDCHF=X'
    ]
    
    crypto=['BTC-USD', 'ETH-USD', 'LTC-USD', 'XRP-USD', 'ADA-USD', 'BNB-USD', 'SOL-USD', 'DOGE-USD', 
'DOT-USD', 'AVAX-USD', 'SHIB-USD', 'MATIC-USD', 'ATOM-USD', 'LINK-USD', 'UNI-USD', 'AAVE-USD', 
'BCH-USD', 'XLM-USD', 'FIL-USD', 'ETC-USD']
    
    metels=[ 'GC=F',  # Gold
'SI=F',  # Silver
'CL=F',  # Crude Oil (WTI)
'BZ=F',  # Brent Crude Oil
'NG=F',  # Natural Gas
'HG=F',  # Copper
'PL=F',  # Platinum
'PA=F'   ]
    
    # List of sectors and their respective rounding decimals
    sector_list = [forex_pairs,crypto,metels]
    round_of_lst = [4, 1,2]
    
    # Final output dict for the current run
    final_output = {}
    
    # Process each sector and store results
    for sector, decimal in zip(sector_list, round_of_lst):
        sector_output_dict = give_predictoin_for_given_symbol(sector, decimal)
        final_output.update(sector_output_dict)
    
    # Process the results to filter out invalid entries
    modified_dict = {}
    for symbol, result in final_output.items():
        if result['price'] not in [False, 'false', None]:
            if '=' in symbol:
                pair = symbol.split('=')[0]
            else:
                pair = symbol
            modified_dict[pair] = result
    
    # Append the data to the JSON file
    append_to_json(file_path, modified_dict)
    
    # Send Telegram message only if `modified_dict` contains data
    if modified_dict:
        telegram_message = format_output_for_telegram(modified_dict)
        send_telegram_message(bot_token, chat_id, telegram_message)
    
    # Print the final output for the current iteration
    print(f"Appended data and sent to Telegram at {timestamp}")
    
    # Wait for 1 minute before the next run
   


# Run the main function
if __name__ == "__main__":
    main()
    
    
    
    

