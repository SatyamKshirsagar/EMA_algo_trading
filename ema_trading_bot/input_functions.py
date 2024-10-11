import numpy as np
import pandas as pd
import pandas as pd
from collections import Counter




def check_for_given(df,how_mant_to_chech,minimum_for_trend):
    
    df['EMA_25'] = df['Close'].ewm(span=25, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA_100'] = df['Close'].ewm(span=100, adjust=False).mean()
    
    #### checking for the trend
    lst=[]
    trend_df=df.iloc[-how_mant_to_chech:,:]
    trend_df=trend_df[['EMA_100']]
    for i in range(1,len(trend_df)):
 
        lst.append(trend_df['EMA_100'][i]-trend_df['EMA_100'][i-1])
        
    positive=0
    negative=0
    consolidate=0
    
    
    for i in lst:
        if i<0:
            negative=negative+1
        elif i>0:
            positive=positive+1
        else:
            consolidate=consolidate+1
            
    if positive>minimum_for_trend:
        final_trend= 'uptrend'
    elif negative>minimum_for_trend:
        final_trend= 'Downtrend'
    else:
        final_trend= 'Consolidated'
        
    #print(f'positive {positive}, negative  {negative},consolidate {consolidate} ')
        
    return final_trend



def check_cross_over(df,trend):
    crossing_25_ema=False
    df['EMA_25'] = df['Close'].ewm(span=25, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA_100'] = df['Close'].ewm(span=100, adjust=False).mean()
    
    #print(df.tail(2))
    
    
    last_close_price=list(df['Close'])[-1]
    last_open_price=list(df['Open'])[-1]
    ema_25=list(df['EMA_25'])[-1]
    ema_50=list(df['EMA_50'])[-1]
    ema_100=list(df['EMA_100'])[-1]
    
    
    
    if trend=='uptrend':
        
        if last_close_price>ema_25 and last_open_price<ema_25:
            crossing_25_ema=True
                
                
            
    else:
        pass
    if trend=='Downtrend':
         
    
        if last_close_price<ema_25 and last_open_price>ema_25:
            crossing_25_ema=True
    else:
        pass
        
    return crossing_25_ema,df




#def check_distance_between_points()


        
    
            




def get_support_resistance(df,round_of_value,trend):
    
    supports=[]
    resistances=[]
    
    current_price=list(df['Close'])[-1]
    
    df_supp_res=df[['High','Low','Close']]
    df_supp_res=round(df_supp_res,round_of_value)
    support_resistance=[]
    for i in df_supp_res.columns:
        support_resistance.extend(list(df_supp_res[i]))
 
    counted_numbers = Counter(support_resistance)
    df = pd.DataFrame(counted_numbers.items(), columns=['value', 'Count'])
    df = df.sort_values(by='Count', ascending=False).reset_index(drop=True)
    sup_res_lst_final=list(df.iloc[0:5,:]['value'])
    
   
    if trend=='uptrend':
        for val in sup_res_lst_final:
            if val>current_price:
                resistances.append(val)
            else:
                supports.append(val)
                
    elif trend=='Downtrend':
        for val in sup_res_lst_final:
            if val>current_price:
                supports.append(val)
            else:
                resistances.append(val)
                
    else:
        pass
        
    return supports,resistances
    
    
def check_validity(trend,data):
    
    valid_trend=False
    valid_gap=False
    
    
    valid_data=data.iloc[-22:,:]
    valid_data['gap_25_50']=valid_data['EMA_25']-valid_data['EMA_50']
    valid_data['gap_50_100']=valid_data['EMA_50']-valid_data['EMA_100']
    valid_data['gap_25_100']=valid_data['EMA_25']-valid_data['EMA_100']
    valid_df=valid_data[['gap_25_50','gap_50_100','gap_25_100']]
    
    
   
    
    
    if trend=='uptrend' and (valid_df>=0).all().all()==True:
        
        valid_trend=True
        
        valid_df=abs(valid_df)
        valid_df=valid_df.iloc[:-1,:]
        current_val=valid_df.tail(1)
        
        
        max_25_50=np.max(list(valid_df['gap_25_50']))
        max_50_100=np.max(list(valid_df['gap_50_100']))
        max_25_100=np.max(list(valid_df['gap_25_100']))
        
        current_25_50_gap=list(current_val['gap_25_50'])[0]
        current_50_100_gap=list(current_val['gap_50_100'])[0]
        current_25_100_gap=list(current_val['gap_25_100'])[0]
        
        if current_25_50_gap>=(max_25_50/2) and current_50_100_gap>=(max_50_100/1.75):
            valid_gap=True
            
    elif trend=='Downtrend' and (valid_df<=0).all().all()==True:
        valid_trend=True
        valid_df=abs(valid_df)
        valid_df=valid_df.iloc[:-1,:]
        current_val=valid_df.tail(1)
        
        
        max_25_50=np.max(list(valid_df['gap_25_50']))
        max_50_100=np.max(list(valid_df['gap_50_100']))
        max_25_100=np.max(list(valid_df['gap_25_100']))
        
        current_25_50_gap=list(current_val['gap_25_50'])[0]
        current_50_100_gap=list(current_val['gap_50_100'])[0]
        current_25_100_gap=list(current_val['gap_25_100'])[0]
        
        if current_25_50_gap>=(max_25_50/2) and current_50_100_gap>=(max_50_100/1.75):
            valid_gap=True
            
    else:
        pass
    
    return valid_trend,valid_gap



##########

def valid_stocastic(df,lookback_period,trend):
    stocastic_flag=False
    stocastic_crossover=False
    
    lookback_period = 14


    df['Lowest Low'] = df['Low'].rolling(window=lookback_period).min()
    df['Highest High'] = df['High'].rolling(window=lookback_period).max()

    df['%K'] = ((df['Close'] - df['Lowest Low']) / (df['Highest High'] - df['Lowest Low'])) * 100

    
    df['%D'] = df['%K'].rolling(window=3).mean()

 
    df = df[['Close', '%K', '%D']]
    
    k_data=list(df.iloc[-8:,:]['%K'])
    last_k=k_data[-1]
    d_data=list(df.iloc[-8:,:]['%D'])
    last_d=d_data[-1]
    #print(df.tail(10))
    
    
    if trend=='uptrend':
        any(value < 25 for value in k_data)==True
        stocastic_flag=True
        if last_k>last_d:
            stocastic_crossover=True
            
    elif trend=='Downtrend':
        any(value >=75 for value in k_data)==True
        stocastic_flag=True
        if last_k<last_d:
            stocastic_crossover=True
    else:
        pass
    
    return stocastic_flag,stocastic_crossover

def check_for_consolidation_before_breakout(data,trend):
    new_data=data.iloc[-9:,:]
    
    df_with_14_cadles=data.iloc[-22:,:]
    
    
    touching_100_ema=False
    crossing_25_ema_within_8=False
    crossing_index='not_yet_found'
    valid_last_14_candles=False
    
    
    if trend=='uptrend':
    
        new_data['above_and_below_25'] = new_data.apply(
        lambda x: 'Yes' if x['Open'] > x['EMA_25'] and x['Close'] < x['EMA_25'] else 'No', 
        axis=1)
        
        new_data['touching_100_ema'] = new_data.apply(
        lambda x: 'yes' if x['Low'] >= x['EMA_100'] else 'no', 
        axis=1)
    
        if 'Yes' in list(new_data['touching_100_ema']):
            touching_100_ema=True
            
        if 'Yes' in list(new_data['above_and_below_25']):
            rev_lst=list(new_data['above_and_below_25'])[::-1]
            crossing_25_ema_within_8=True
            crossing_index=rev_lst.index('Yes')
            
            df_with_14_cadles['closing_below_25']=new_data.apply(
            lambda x: 'invalid' if x['Open'] > x['EMA_25'] and x['Close'] < x['EMA_25'] else 'valid', 
            axis=1)
            
            list_14_candles=list(df_with_14_cadles['closing_below_25'])[:-crossing_index]
            
            if 'invalid' not  in list_14_candles:
                valid_last_14_candles=True
    
    
    if trend=='Downtrend':
    
        new_data['above_and_below_25'] = new_data.apply(
        lambda x: 'Yes' if x['Open'] < x['EMA_25'] and x['Close'] > x['EMA_25'] else 'No', 
        axis=1)
        
        new_data['touching_100_ema'] = new_data.apply(
        lambda x: 'yes' if x['High'] >= x['EMA_100'] else 'no', 
        axis=1)
    
        if 'Yes' in list(new_data['touching_100_ema']):
            touching_100_ema=True
            
        if 'Yes' in list(new_data['above_and_below_25']):
            rev_lst=list(new_data['above_and_below_25'])[::-1]
            crossing_25_ema_within_8=True
            crossing_index=rev_lst.index('Yes')
            
            df_with_14_cadles['closing_below_25']=new_data.apply(
            lambda x: 'invalid' if x['Open'] > x['EMA_25'] and x['Close'] < x['EMA_25'] else 'valid', 
            axis=1)
            
            list_14_candles=list(df_with_14_cadles['closing_below_25'])[:-crossing_index]
            
            if 'invalid' not  in list_14_candles:
                valid_last_14_candles=True
                
    return touching_100_ema,crossing_25_ema_within_8,crossing_index,valid_last_14_candles


def place_order(data):
    final=data.iloc[-1:,:]
    open_price=list(final['Open'])[0]
    close_price=list(final['Close'])[0]
    high_price=list(final['Close'])[0]
    low_price=list(final['Close'])[0]
    
    ema_25=list(final['EMA_25'])[0]
    ema_50=list(final['EMA_50'])[0]
    
    

        
    close_25_diff=abs(close_price-ema_25)
    ema_25_50_diff=abs(ema_25-ema_50)
    high_low_diff=abs(high_price-low_price)
    
    if close_25_diff<ema_25_50_diff:
        price_to_bet=close_price
    else:
        price_to_bet=(50*(high_low_diff))/100
        
    return price_to_bet,ema_50
        
        
        
        
    
    
      
    
    
                
    
                
            
            
            
            
    




            
        
        
        
        
    
    


    
            
        
        
        
        
        
    
    
    
    
    
    
    
    
        
        
            
            
            
        
        
        
        
    
    
    
    