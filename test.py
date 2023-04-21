import datetime
import time
from login_flow import api
import pandas as pd
from tg_bot import telegram_send_message, telegram_send_photo_caption, telegram_send_file
import matplotlib.pyplot as plt
import numpy as np
import tvDatafeed

# fetch premium based option strike
def ce_symbol(premium):

    banknifty_tsym = api.searchscrip('NFO','BANK NIFTY FUT')
    banknifty_tsym = banknifty_tsym['values'][0]['tsym']
    ltp = float(api.get_quotes('NFO',banknifty_tsym)['lp'])
    ATM = round(ltp,-2)

    searchscrip = 'BANKNIFTY ' + str(ATM) + ' CE'
    token = api.searchscrip('NFO',searchscrip)['values'][0]['tsym']

    data = api.get_option_chain('NFO',token,ATM,10)
    data = pd.DataFrame(data['values'])
    ce_df = data.loc[data['optt'] == 'CE']                                                                                  # take out ce only

    ce_premium = premium                                                                                                        # desired nearest premium is 200
    ce_strikeList = []                                                                                                      # empty list where all strikes will be stored
    for i in ce_df.index:
        strikeInfo = ce_df.loc[i]                                                                                           # take each row of ce_df
        res = api.get_quotes(exchange='NFO',token=str(strikeInfo['token']))                                                 # search by token no to get ltp
        res = {'tsym' : res['tsym'], 'lp' : float(res['lp']), 'token' : res['token']}                                       # store tsym, ltp & token into res
        ce_strikeList.append(res)                                                                                           # append into strikeList

    ce_strikedf = pd.DataFrame(ce_strikeList)                                                                               # read strike as df
    ce_strikedf.sort_values(by='lp',inplace=True)                                                                           # sort by ltp
    ce_strikedf['diff'] = abs(ce_strikedf['lp'] - ce_premium)                                                               # find nearest strike by 
    ce_strikedf.sort_values(by='diff',inplace=True)                                                                         # sort by lowest diff
    #ce_strike = ce_strikedf.iloc[0]                                                                                        # take only 1st symbol

    ce_strike_tsym = ce_strikedf.iloc[0]['tsym']
    ce_strike_ltp = ce_strikedf.iloc[0]['lp']

    return ce_strike_tsym

# fetch premium based option strike
def pe_symbol(premium):
    
    banknifty_tsym = api.searchscrip('NFO','BANK NIFTY')
    banknifty_tsym = banknifty_tsym['values'][0]['tsym']
    ltp = float(api.get_quotes('NFO',banknifty_tsym)['lp'])
    ATM = round(ltp,-2)

    searchscrip = 'BANKNIFTY ' + str(ATM) + ' PE'
    token = api.searchscrip('NFO',searchscrip)['values'][0]['tsym']

    data = api.get_option_chain('NFO',token,ATM,10)
    data = pd.DataFrame(data['values'])
    pe_df = data.loc[data['optt'] == 'PE']                                                                                  # take out pe only

    pe_premium = premium                                                                                                        # desired nearest premium is 300
    pe_strikeList = []                                                                                                      # empty list where all strikes will be stored
    for i in pe_df.index:
        strikeInfo = pe_df.loc[i]                                                                                           # take each row of pe_df
        res = api.get_quotes(exchange='NFO',token=str(strikeInfo['token']))                                                 # search by token no to get ltp
        res = {'tsym' : res['tsym'], 'lp' : float(res['lp']), 'token' : res['token']}                                       # store tsym, ltp & token into res
        pe_strikeList.append(res)                                                                                           # append into strikeList

    pe_strikedf = pd.DataFrame(pe_strikeList)                                                                               # read strike as df
    pe_strikedf.sort_values(by='lp',inplace=True)                                                                           # sort by ltp
    pe_strikedf['diff'] = abs(pe_strikedf['lp'] - pe_premium)                                                               # find nearest strike by 
    pe_strikedf.sort_values(by='diff',inplace=True)                                                                         # sort by lowest diff

    pe_strike_tsym = pe_strikedf.iloc[0]['tsym']
    pe_strike_ltp = pe_strikedf.iloc[0]['lp']

    return pe_strike_tsym

# definition to add lists to df and return whole df
def trade_log(TL_StrikeList,TL_EntryPrice,TL_ExitPrice,TL_EntryTime,TL_OptionType):
    data = {'TL_StrikeList': TL_StrikeList,
            'TL_EntryPrice': TL_EntryPrice,
            'TL_ExitPrice':TL_ExitPrice,
            'TL_EntryTime':TL_EntryTime,
            'TL_OptionType':TL_OptionType}

    df = pd.DataFrame(data)
    return df

# definition to record current time
def time_now():
    time_now = datetime.datetime.now().time()
    return time_now

# definition to record current minute
def minute_now():
    minute_now = datetime.datetime.now().minute
    return minute_now

# definition to record current second
def second_now():
    second_now = datetime.datetime.now().second
    return second_now

# chat ID of telegram channel
chat_id = -1001260902486
# ALGO STARTED
print(telegram_send_message(f'\nDND Setup - Algo Started @ {time_now()}',chat_id))


# START & END TIME
start_time = datetime.time(hour=9,minute=20)
qty = 25
TL_StrikeList = []
TL_EntryPrice = []
TL_ExitPrice = []
TL_EntryTime = []
TL_OptionType = []
TL_Qty = []


# WAITING FOR START TIME
while time_now() < start_time:
    print(f'Waiting for {start_time}. Time : {time_now()}')
    time.sleep(1)


# set trading view variable
tv = tvDatafeed.TvDatafeed()
# fetch last 2 days data
data = tv.get_hist(symbol='BANKNIFTY',exchange='NSE',interval=tvDatafeed.Interval.in_daily,n_bars=2,fut_contract=None)
print(data)

# access yesterday's hlc
pdh = data.iloc[0]['high']
pdl = data.iloc[0]['low']
TodayOpen = data.iloc[1]['open']

print(telegram_send_message(f'\nPDH is {pdh}, PDL is {pdl} & Today\'s Open is {TodayOpen}',chat_id))

# EXECUTE AT START TIME
while True:

    # fetch banknifty LTP
    spot_token = api.searchscrip('NSE','NIFTY BANK')['values'][0]['token']
    banknifty_LTP = float(api.get_quotes('NSE',spot_token)['lp'])
    print(f'\nBanknifty LTP is {banknifty_LTP}, Time Now : {time_now()}')
    
    # banknifty is neutral
    if banknifty_LTP < pdh and banknifty_LTP > pdl:

        # Sell 25 qty of 100 CP Call & Put each
        Position = 'Neutral'
        ce_tsym = ce_symbol(100)
        pe_tsym = pe_symbol(100)
        ce_ltp = float(api.get_quotes(exchange='NFO',token=ce_tsym)['lp'])
        pe_ltp = float(api.get_quotes(exchange='NFO',token=pe_tsym)['lp'])
        CEQty = 25
        PEQty = 25
        print(telegram_send_message(f'\nSell {CEQty} qty {ce_tsym} at {ce_ltp} \nSell {PEQty} qty {pe_tsym} at {pe_ltp} \n Time: {time_now()}',chat_id))

        CEStrike = ce_tsym
        CEEntryPrice = ce_ltp
        PEStrike = pe_tsym
        PEEntryPrice = pe_ltp

        TL_StrikeList.append(CEStrike)
        TL_StrikeList.append(PEStrike)
        TL_EntryTime.append(time_now())
        TL_EntryTime.append(time_now())
        TL_EntryPrice.append(CEEntryPrice)
        TL_EntryPrice.append(PEEntryPrice)
        TL_ExitPrice.append(None)
        TL_ExitPrice.append(None)
        TL_OptionType.append('Call')
        TL_OptionType.append('Put')
        TL_Qty.append(CEQty)
        TL_Qty.append(PEQty)

        break

    # banknifty is bullish
    elif banknifty_LTP > pdh and banknifty_LTP > TodayOpen:

        # Sell 50 qty of 100 CP Put
        Position = 'Bullish'
        pe_tsym = pe_symbol(100)
        pe_ltp = float(api.get_quotes(exchange='NFO',token=pe_tsym)['lp'])
        PEQty = 50
        print(telegram_send_message(f'\nSell {PEQty} qty {pe_tsym} at {pe_ltp} \n Time: {time_now()}',chat_id))

        PEStrike = pe_tsym
        PEEntryPrice = pe_ltp

        TL_StrikeList.append(PEStrike)
        TL_EntryTime.append(time_now())
        TL_EntryPrice.append(PEEntryPrice)
        TL_ExitPrice.append(None)
        TL_OptionType.append('Put')
        TL_Qty.append(PEQty)

        break


    # banknifty is bearish (BNF < PDL & RED Candle)
    elif banknifty_LTP < pdl and banknifty_LTP < TodayOpen:

        # Sell 50 qty of 100 CP Call
        Position = 'Bearish'
        ce_tsym = ce_symbol(100)
        ce_ltp = float(api.get_quotes(exchange='NFO',token=ce_tsym)['lp'])
        CEQty = 50
        print(telegram_send_message(f'Sell {CEQty} qty {ce_tsym} at {ce_ltp} \n Time: {time_now()}',chat_id))

        CEStrike = ce_tsym
        CEEntryPrice = ce_ltp

        TL_StrikeList.append(CEStrike)
        TL_EntryTime.append(time_now())
        TL_EntryPrice.append(CEEntryPrice)
        TL_ExitPrice.append(None)
        TL_OptionType.append('Call')
        TL_Qty.append(CEQty)

        break


    # else wait
    else:
        print(f'Wait for 2 more seconds. Checking again... {time_now()}')
        time.sleep(2)


# End time & PNL List
end_time = datetime.time(hour=15,minute=25)
pnl_list = []



# if end time has not come yet then
while time_now() < end_time:
    try:

        # if position is Neutral
        if Position == 'Neutral':

            # Find ATM
            banknifty_LTP = float(api.get_quotes('NSE',spot_token)['lp'])

            # record PNL
            ce_ltp = float(api.get_quotes('NFO',CEStrike)['lp'])
            pe_ltp = float(api.get_quotes('NFO',PEStrike)['lp'])

            CEpnl = (CEEntryPrice - ce_ltp) * CEQty
            PEpnl = (PEEntryPrice - pe_ltp) * PEQty

            pnl = CEpnl + PEpnl
            pnl = round(pnl,2)

            # create a list of pnl
            pnl_list.append(pnl)
            
            # If positiion turns Bullish
            if banknifty_LTP > pdh and minute_now() % 5 == 0:
                
                # Create a trade log from df
                TL_df = trade_log(TL_StrikeList,TL_EntryPrice,TL_ExitPrice,TL_EntryTime,TL_OptionType)
                print(TL_df)

                # Find open call positions and fetch call trading symbol to exit
                open_calls = TL_df[(TL_df['TL_OptionType'] == 'Call') & (TL_df['TL_ExitPrice'].isna())]
                print(open_calls)
                
                call_to_exit = open_calls.iloc[0]['TL_StrikeList']
                print(f'call_to_exit is {call_to_exit}')
                
                # Fetch LTP of open call and exit on limit & record it in trade log list
                CE_ExitPrice = float(api.get_quotes(exchange='NFO',token=call_to_exit)['lp'])
                CallToExitIndex = TL_df.loc[(TL_df['TL_OptionType'] == 'Call') & (TL_df['TL_ExitPrice'].isna()), 'TL_ExitPrice'].index[0]
                TL_ExitPrice[CallToExitIndex] = CE_ExitPrice

                print(telegram_send_message(f'Exit {CEQty} qty {call_to_exit} at {CE_ExitPrice} \n Time: {time_now()}',chat_id))


                # find new PE of 100 rs premium
                pe_tsym = pe_symbol(100)
                pe_ltp = float(api.get_quotes(exchange='NFO',token=pe_tsym)['lp'])
                PEQty = 25
                print(telegram_send_message(f'Sell {PEQty} qty {pe_tsym} at {pe_ltp} \n Time: {time_now()}',chat_id))

                PEStrike = pe_tsym
                PEEntryPrice = pe_ltp + (pnl/50)

                TL_StrikeList.append(PEStrike)
                TL_EntryTime.append(time_now())
                TL_EntryPrice.append(pe_ltp)
                TL_ExitPrice.append(None)
                TL_OptionType.append('Put')
                TL_Qty.append(PEQty)

                Position = 'Bullish'

                time.sleep(60)


            # If position turns bearish
            elif banknifty_LTP < pdl and minute_now() % 5 == 0:

                # Create a trade log from df
                TL_df = trade_log(TL_StrikeList,TL_EntryPrice,TL_ExitPrice,TL_EntryTime,TL_OptionType)
                print(TL_df)

                # Find open call positions and fetch trading symbol
                open_puts = TL_df[(TL_df['TL_OptionType'] == 'Put') & (TL_df['TL_ExitPrice'].isna())]
                print(open_puts)
                put_to_exit = open_puts.iloc[0]['TL_StrikeList']
                print(f'put_to_exit is {put_to_exit}')
                
                # Fetch LTP of open call and exit on limit & record it in trade log list
                PE_ExitPrice = float(api.get_quotes(exchange='NFO',token=put_to_exit)['lp'])
                PutToExitIndex = TL_df.loc[(TL_df['TL_OptionType'] == 'Put') & (TL_df['TL_ExitPrice'].isna()), 'TL_ExitPrice'].index[0]
                TL_ExitPrice[PutToExitIndex] = PE_ExitPrice

                print(telegram_send_message(f'Exit {PEQty} qty {put_to_exit} at {PE_ExitPrice} \n Time: {time_now()}',chat_id))


                # find new CE of 100 rs premium
                ce_tsym = ce_symbol(100)
                ce_ltp = float(api.get_quotes(exchange='NFO',token=ce_tsym)['lp'])
                CEQty = 25
                print(telegram_send_message(f'Exit {PEQty} qty {put_to_exit} at {PE_ExitPrice} \nSell {CEQty} qty {ce_tsym} at {ce_ltp} \n Time: {time_now()}',chat_id))

                CEStrike = ce_tsym
                CEEntryPrice = ce_ltp  + (pnl/50)

                TL_StrikeList.append(CEStrike)
                TL_EntryTime.append(time_now())
                TL_EntryPrice.append(ce_ltp)
                TL_ExitPrice.append(None)
                TL_OptionType.append('Call')
                TL_Qty.append(CEQty)

                Position = 'Bearish'

                time.sleep(60)



            # post photo to telegram group every half an hour
            elif minute_now() % 30 == 0:
                
                # x axis, fig size, padding
                x = np.arange(len(pnl_list))
                fig = plt.figure(figsize=(12, 4))
                plt.subplots_adjust(left=0.07, right=0.97, top=0.90, bottom=0.15)

                # avg pnl, max pnl, min pnl & mid chart point
                avg_pnl = round(sum(pnl_list)/len(pnl_list),2)
                max_pnl = round(max(pnl_list),2)
                min_pnl = round(min(pnl_list),2)
                mid_chart = round(len(pnl_list)/2,2)

                # plot the chart
                plt.plot(x,pnl_list)

                # this excerpt is for shading of pnl
                zero_line = np.zeros_like(pnl_list)
                greater_than_zero = np.array(pnl_list) > 0
                less_than_zero = np.array(pnl_list) < 0
                plt.fill_between(x, zero_line, pnl_list, where=greater_than_zero, color='limegreen', alpha=0.5)
                plt.fill_between(x, zero_line, pnl_list, where=less_than_zero, color='red', alpha=0.5)

                # plot max pnl text at top, min pnl at bottom & avg at avg point
                #plt.text(x,y,data)
                plt.text(1,max_pnl+20,f'max pnl {max_pnl}')
                plt.text(1,min_pnl-20,f'min pnl {min_pnl}')
                plt.text(1,avg_pnl+20,f'avg pnl {avg_pnl}')

                # horizontal line for max pnl, min pnl & avg pnl
                plt.axhline(y=max_pnl,color='green')
                plt.axhline(y=min_pnl,color='red')
                plt.axhline(y=avg_pnl,color='blue')

                # x and y axis labels, title of chart plus save the final picture to PC
                plt.ylabel('pnl in ₹')
                plt.xlabel('time scale')
                plt.title('DND Setup')
                plt.savefig(f'c:/algo/pnl_monitor/dnd/pnl_{datetime.datetime.now().date()}.png')

                # send pnl photo to telegram
                photo_path = f'c:/algo/pnl_monitor/dnd/pnl_{datetime.datetime.now().date()}.png'
                telegram_send_photo_caption(photo_path,f'Current MTM : {pnl_list[-1]}, Time : {time_now()}',chat_id)

                time.sleep(60)


            # post pnl to telegram group every 5 minutes
            elif minute_now() % 5 == 0:

                # convert the list into a df and export as csv
                pnl_df = pd.DataFrame()
                pnl_df['pnl'] = pnl_list
                pnl_df.to_csv(f'c:/algo/pnl_monitor/dnd/pnl_{datetime.datetime.now().date()}.csv',index=False)
                
                print(f'Position : {Position}, Current MTM : {pnl}, Time : {time_now()}')
                time.sleep(60)

            
            else:
                print(f'Position : {Position}, Current MTM : {pnl}, Time : {time_now()}')
                time.sleep(10)

        
        # if position is Bullish
        elif Position == 'Bullish':

            # Find ATM
            banknifty_LTP = float(api.get_quotes('NSE',spot_token)['lp'])

            # record PNL
            pe_ltp = float(api.get_quotes('NFO',PEStrike)['lp'])
            PEpnl = (PEEntryPrice - pe_ltp) * PEQty
            pnl = PEpnl
            pnl = round(pnl,2)

            # create a list of pnl
            pnl_list.append(pnl)

            # if market turns neutral
            if banknifty_LTP < pdh and banknifty_LTP > pdl and minute_now() % 5 == 0:
                
                PEQty = 25
                
                # Create a trade log from df
                TL_df = trade_log(TL_StrikeList,TL_EntryPrice,TL_ExitPrice,TL_EntryTime,TL_OptionType)
                print(TL_df)

                # Find open call positions and fetch put trading symbol to exit
                open_puts = TL_df[(TL_df['TL_OptionType'] == 'Put') & (TL_df['TL_ExitPrice'].isna())]
                print(open_puts)
                put_to_exit = open_puts.iloc[0]['TL_StrikeList']
                print(f'put_to_exit is {put_to_exit}')
                
                # Fetch LTP of open call and exit on limit & record it in trade log list
                PE_ExitPrice = float(api.get_quotes(exchange='NFO',token=put_to_exit)['lp'])
                PutToExitIndex = TL_df.loc[(TL_df['TL_OptionType'] == 'Put') & (TL_df['TL_ExitPrice'].isna()), 'TL_ExitPrice'].index[0]
                TL_ExitPrice[PutToExitIndex] = PE_ExitPrice

                print(telegram_send_message(f'Exit {PEQty} qty {put_to_exit} at {PE_ExitPrice}  \n Time: {time_now()}',chat_id))


                # find new CE of 100 rs premium
                ce_tsym = ce_symbol(100)
                ce_ltp = float(api.get_quotes(exchange='NFO',token=ce_tsym)['lp'])
                CEQty = 25
                print(telegram_send_message(f'Sell {CEQty} qty {ce_tsym} at {ce_ltp} \n Time: {time_now()}',chat_id))

                CEStrike = ce_tsym
                CEEntryPrice = ce_ltp  + (pnl/50)

                TL_StrikeList.append(CEStrike)
                TL_EntryTime.append(time_now())
                TL_EntryPrice.append(ce_ltp)
                TL_ExitPrice.append(None)
                TL_OptionType.append('Call')
                TL_Qty.append(CEQty)

                Position = 'Neutral'

                time.sleep(60)



            # post photo to telegram group every half an hour
            elif minute_now() %30 == 0:
                
                # x axis, fig size, padding
                x = np.arange(len(pnl_list))
                fig = plt.figure(figsize=(12, 4))
                plt.subplots_adjust(left=0.07, right=0.97, top=0.90, bottom=0.15)

                # avg pnl, max pnl, min pnl & mid chart point
                avg_pnl = round(sum(pnl_list)/len(pnl_list),2)
                max_pnl = round(max(pnl_list),2)
                min_pnl = round(min(pnl_list),2)
                mid_chart = round(len(pnl_list)/2,2)

                # plot the chart
                plt.plot(x,pnl_list)

                # this excerpt is for shading of pnl
                zero_line = np.zeros_like(pnl_list)
                greater_than_zero = np.array(pnl_list) > 0
                less_than_zero = np.array(pnl_list) < 0
                plt.fill_between(x, zero_line, pnl_list, where=greater_than_zero, color='limegreen', alpha=0.5)
                plt.fill_between(x, zero_line, pnl_list, where=less_than_zero, color='red', alpha=0.5)

                # plot max pnl text at top, min pnl at bottom & avg at avg point
                #plt.text(x,y,data)
                plt.text(1,max_pnl+20,f'max pnl {max_pnl}')
                plt.text(1,min_pnl-20,f'min pnl {min_pnl}')
                plt.text(1,avg_pnl+20,f'avg pnl {avg_pnl}')

                # horizontal line for max pnl, min pnl & avg pnl
                plt.axhline(y=max_pnl,color='green')
                plt.axhline(y=min_pnl,color='red')
                plt.axhline(y=avg_pnl,color='blue')

                # x and y axis labels, title of chart plus save the final picture to PC
                plt.ylabel('pnl in ₹')
                plt.xlabel('time scale')
                plt.title('DND Setup')
                plt.savefig(f'c:/algo/pnl_monitor/dnd/pnl_{datetime.datetime.now().date()}.png')

                # send pnl photo to telegram
                photo_path = f'c:/algo/pnl_monitor/dnd/pnl_{datetime.datetime.now().date()}.png'
                telegram_send_photo_caption(photo_path,f'Current MTM : {pnl_list[-1]}, Time : {time_now()}',chat_id)

                time.sleep(60)



            # post pnl to telegram group every 5 minutes
            elif minute_now() %5 == 0:

                # convert the list into a df and export as csv
                pnl_df = pd.DataFrame()
                pnl_df['pnl'] = pnl_list
                pnl_df.to_csv(f'c:/algo/pnl_monitor/dnd/pnl_{datetime.datetime.now().date()}.csv',index=False)
                
                print(f'Position : {Position}, Current MTM : {pnl}, Time : {time_now()}')
                time.sleep(60)

            else:
                print(f'Position : {Position}, Current MTM : {pnl}, Time : {time_now()}')
                time.sleep(10)


                

        # if position is Bearish
        elif Position == 'Bearish':

            # Find ATM
            banknifty_LTP = float(api.get_quotes('NSE',spot_token)['lp'])

            # record PNL
            ce_ltp = float(api.get_quotes('NFO',CEStrike)['lp'])
            CEpnl = (CEEntryPrice - ce_ltp) * CEQty
            pnl = CEpnl
            pnl = round(pnl,2)

            # create a list of pnl
            pnl_list.append(pnl)

            if banknifty_LTP < pdh and banknifty_LTP > pdl and minute_now() % 5 == 0:
                
                CEQty = 25
                        
                # Create a trade log from df
                TL_df = trade_log(TL_StrikeList,TL_EntryPrice,TL_ExitPrice,TL_EntryTime,TL_OptionType)
                print(TL_df)

                # Find open call positions and fetch trading symbol
                open_calls = TL_df[(TL_df['TL_OptionType'] == 'Call') & (TL_df['TL_ExitPrice'].isna())]
                print(open_calls)
                call_to_exit = open_calls.iloc[0]['TL_StrikeList']
                print(f'call_to_exit is {call_to_exit}')
                        
                # Fetch LTP of open call and exit on limit & record it in trade log list
                CE_ExitPrice = float(api.get_quotes(exchange='NFO',token=call_to_exit)['lp'])
                CallToExitIndex = TL_df.loc[(TL_df['TL_OptionType'] == 'Call') & (TL_df['TL_ExitPrice'].isna()), 'TL_ExitPrice'].index[0]
                TL_ExitPrice[CallToExitIndex] = CE_ExitPrice

                print(telegram_send_message(f'Exit {CEQty} qty {call_to_exit} at {CE_ExitPrice} \n Time: {time_now()}',chat_id))


                # find new PE of 100 rs premium
                pe_tsym = pe_symbol(100)
                pe_ltp = float(api.get_quotes(exchange='NFO',token=pe_tsym)['lp'])
                PEQty = 25
                print(telegram_send_message(f'Sell {PEQty} qty {pe_tsym} at {pe_ltp} \n Time: {time_now()}',chat_id))

                PEStrike = pe_tsym
                PEEntryPrice = pe_ltp  + (pnl/50)

                TL_StrikeList.append(PEStrike)
                TL_EntryTime.append(time_now())
                TL_EntryPrice.append(pe_ltp)
                TL_ExitPrice.append(None)
                TL_OptionType.append('Put')
                TL_Qty.append(PEQty)

                Position = 'Neutral'

                time.sleep(60)



            # post photo to telegram group every half an hour
            elif minute_now() %30 == 0:
                
                # x axis, fig size, padding
                x = np.arange(len(pnl_list))
                fig = plt.figure(figsize=(12, 4))
                plt.subplots_adjust(left=0.07, right=0.97, top=0.90, bottom=0.15)

                # avg pnl, max pnl, min pnl & mid chart point
                avg_pnl = round(sum(pnl_list)/len(pnl_list),2)
                max_pnl = round(max(pnl_list),2)
                min_pnl = round(min(pnl_list),2)
                mid_chart = round(len(pnl_list)/2,2)

                # plot the chart
                plt.plot(x,pnl_list)

                # this excerpt is for shading of pnl
                zero_line = np.zeros_like(pnl_list)
                greater_than_zero = np.array(pnl_list) > 0
                less_than_zero = np.array(pnl_list) < 0
                plt.fill_between(x, zero_line, pnl_list, where=greater_than_zero, color='limegreen', alpha=0.5)
                plt.fill_between(x, zero_line, pnl_list, where=less_than_zero, color='red', alpha=0.5)

                # plot max pnl text at top, min pnl at bottom & avg at avg point
                #plt.text(x,y,data)
                plt.text(1,max_pnl+20,f'max pnl {max_pnl}')
                plt.text(1,min_pnl-20,f'min pnl {min_pnl}')
                plt.text(1,avg_pnl+20,f'avg pnl {avg_pnl}')

                # horizontal line for max pnl, min pnl & avg pnl
                plt.axhline(y=max_pnl,color='green')
                plt.axhline(y=min_pnl,color='red')
                plt.axhline(y=avg_pnl,color='blue')

                # x and y axis labels, title of chart plus save the final picture to PC
                plt.ylabel('pnl in ₹')
                plt.xlabel('time scale')
                plt.title('DND Setup')
                plt.savefig(f'c:/algo/pnl_monitor/dnd/pnl_{datetime.datetime.now().date()}.png')

                # send pnl photo to telegram
                photo_path = f'c:/algo/pnl_monitor/dnd/pnl_{datetime.datetime.now().date()}.png'
                telegram_send_photo_caption(photo_path,f'Current MTM : {pnl_list[-1]}, Time : {time_now()}',chat_id)

                time.sleep(60)


            # post pnl to telegram group every 5 minutes
            elif minute_now() %5 == 0:

                # convert the list into a df and export as csv
                pnl_df = pd.DataFrame()
                pnl_df['pnl'] = pnl_list
                pnl_df.to_csv(f'c:/algo/pnl_monitor/dnd/pnl_{datetime.datetime.now().date()}.csv',index=False)
                
                print(f'Position : {Position}, Current MTM : {pnl}, Time : {time_now()}')
                time.sleep(60)

            else:
                print(f'Position : {Position}, Current MTM : {pnl}, Time : {time_now()}')
                time.sleep(10)


        else:
            time.sleep(10)
            print(f'Wait for 10 seconds. Banknifty LTP is {banknifty_LTP}, Time : {time_now()}')

    except:
        pass



# at 3.25 pm, exit all existing positions
if Position == 'Neutral':

    # Create a trade log from df
    TL_df = trade_log(TL_StrikeList,TL_EntryPrice,TL_ExitPrice,TL_EntryTime,TL_OptionType)
    print(TL_df)

    # Find open call positions and fetch trading symbol
    open_calls = TL_df[(TL_df['TL_OptionType'] == 'Call') & (TL_df['TL_ExitPrice'].isna())]
    open_puts = TL_df[(TL_df['TL_OptionType'] == 'Put') & (TL_df['TL_ExitPrice'].isna())]
    print(open_calls)
    print(open_puts)
    
    call_to_exit = open_calls.iloc[0]['TL_StrikeList']
    put_to_exit = open_puts.iloc[0]['TL_StrikeList']
    print(f'call_to_exit is {call_to_exit}')
    print(f'put_to_exit is {put_to_exit}')
                
    # Fetch LTP of open call and exit on limit & record it in trade log list
    CE_ExitPrice = float(api.get_quotes(exchange='NFO',token=call_to_exit)['lp'])
    PE_ExitPrice = float(api.get_quotes(exchange='NFO',token=put_to_exit)['lp'])
    
    CallToExitIndex = TL_df.loc[(TL_df['TL_OptionType'] == 'Call') & (TL_df['TL_ExitPrice'].isna()), 'TL_ExitPrice'].index[0]
    TL_ExitPrice[CallToExitIndex] = CE_ExitPrice
    PutToExitIndex = TL_df.loc[(TL_df['TL_OptionType'] == 'Put') & (TL_df['TL_ExitPrice'].isna()), 'TL_ExitPrice'].index[0]
    TL_ExitPrice[PutToExitIndex] = PE_ExitPrice

    print(telegram_send_message(f'Exit {CEQty} qty {call_to_exit} at {CE_ExitPrice} \nExit {PEQty} qty {put_to_exit} at {PE_ExitPrice} \nTime: {time_now()}',chat_id))

elif Position == 'Bullish':

    # Create a trade log from df
    TL_df = trade_log(TL_StrikeList,TL_EntryPrice,TL_ExitPrice,TL_EntryTime,TL_OptionType)
    print(TL_df)

    # Find open call positions and fetch trading symbol
    open_puts = TL_df[(TL_df['TL_OptionType'] == 'Put') & (TL_df['TL_ExitPrice'].isna())]
    print(open_puts)
    put_to_exit = open_puts.iloc[0]['TL_StrikeList']
    put_to_exit1 = open_puts.iloc[1]['TL_StrikeList']
    print(f'put_to_exit is {put_to_exit} & {put_to_exit1}')

    # Fetch LTP of open call and exit on limit & record it in trade log list
    PE_ExitPrice = float(api.get_quotes(exchange='NFO',token=put_to_exit)['lp'])
    PE_ExitPrice1 = float(api.get_quotes(exchange='NFO',token=put_to_exit1)['lp'])

    print(telegram_send_message(f'Exit {PEQty} qty {put_to_exit} at {PE_ExitPrice} & {put_to_exit1} at {PE_ExitPrice1} \nTime: {time_now()}',chat_id))

    PutToExitIndex = TL_df.loc[(TL_df['TL_OptionType'] == 'Put') & (TL_df['TL_ExitPrice'].isna()), 'TL_ExitPrice'].index[0]
    TL_ExitPrice[PutToExitIndex] = PE_ExitPrice
    PutToExitIndex = TL_df.loc[(TL_df['TL_OptionType'] == 'Put') & (TL_df['TL_ExitPrice'].isna()), 'TL_ExitPrice'].index[0]
    TL_ExitPrice[PutToExitIndex] = PE_ExitPrice

elif Position == 'Bearish':

    TL_df = trade_log(TL_StrikeList,TL_EntryPrice,TL_ExitPrice,TL_EntryTime,TL_OptionType)
    print(TL_df)

    # Find open call positions and fetch trading symbol
    open_calls = TL_df[(TL_df['TL_OptionType'] == 'Call') & (TL_df['TL_ExitPrice'].isna())]
    print(open_calls)
    call_to_exit = open_calls.iloc[0]['TL_StrikeList']
    call_to_exit1 = open_calls.iloc[1]['TL_StrikeList']
    print(f'call_to_exit is {call_to_exit} & {call_to_exit1}')
   
    # Fetch LTP of open call and exit on limit & record it in trade log list
    CE_ExitPrice = float(api.get_quotes(exchange='NFO',token=call_to_exit)['lp'])
    CE_ExitPrice1 = float(api.get_quotes(exchange='NFO',token=call_to_exit1)['lp'])

    print(telegram_send_message(f'Exit {CEQty} qty {call_to_exit} at {CE_ExitPrice} & {call_to_exit1} at {CE_ExitPrice1} \nTime: {time_now()}',chat_id))

    CallToExitIndex = TL_df.loc[(TL_df['TL_OptionType'] == 'Call') & (TL_df['TL_ExitPrice'].isna()), 'TL_ExitPrice'].index[0]
    TL_ExitPrice[CallToExitIndex] = CE_ExitPrice
    CallToExitIndex = TL_df.loc[(TL_df['TL_OptionType'] == 'Call') & (TL_df['TL_ExitPrice'].isna()), 'TL_ExitPrice'].index[0]
    TL_ExitPrice[CallToExitIndex] = CE_ExitPrice

    

else:
    pass


# create a dataframe for trade log and post csv on telegram channel
TL_df = trade_log(TL_StrikeList,TL_EntryPrice,TL_ExitPrice,TL_EntryTime,TL_OptionType)
print(TL_df)
TL_df.to_csv(f'c:/algo/pnl_monitor/dnd/tradelog_{datetime.datetime.now().date()}.csv',index=False)
telegram_send_file(f'c:/algo/pnl_monitor/dnd/tradelog_{datetime.datetime.now().date()}.csv',chat_id)


# after the trade is over, post pnl chart with max pnl, min pnl and avg pnl stats
print(telegram_send_message(f'\nPNL for the day is {pnl}',chat_id))

# x axis, fig size, padding
x = np.arange(len(pnl_list))
fig = plt.figure(figsize=(12, 4))
plt.subplots_adjust(left=0.07, right=0.97, top=0.90, bottom=0.15)

# avg pnl, max pnl, min pnl & mid chart point
avg_pnl = round(sum(pnl_list)/len(pnl_list),2)
max_pnl = round(max(pnl_list),2)
min_pnl = round(min(pnl_list),2)
mid_chart = round(len(pnl_list)/2,2)

# plot the chart
plt.plot(x,pnl_list)

# this excerpt is for shading of pnl
zero_line = np.zeros_like(pnl_list)
greater_than_zero = np.array(pnl_list) > 0
less_than_zero = np.array(pnl_list) < 0
plt.fill_between(x, zero_line, pnl_list, where=greater_than_zero, color='limegreen', alpha=0.5)
plt.fill_between(x, zero_line, pnl_list, where=less_than_zero, color='red', alpha=0.5)

# plot max pnl text at top, min pnl at bottom & avg at avg point
#plt.text(x,y,data)
plt.text(1,max_pnl+20,f'max pnl {max_pnl}')
plt.text(1,min_pnl-20,f'min pnl {min_pnl}')
plt.text(1,avg_pnl+20,f'avg pnl {avg_pnl}')

# horizontal line for max pnl, min pnl & avg pnl
plt.axhline(y=max_pnl,color='green')
plt.axhline(y=min_pnl,color='red')
plt.axhline(y=avg_pnl,color='blue')

# x and y axis labels, title of chart plus save the final picture to PC
plt.ylabel('pnl in ₹')
plt.xlabel('time scale')
plt.title('DND Setup')
plt.savefig(f'c:/algo/pnl_monitor/dnd/pnl_{datetime.datetime.now().date()}.png')

# send pnl photo to telegram
photo_path = f'c:/algo/pnl_monitor/dnd/pnl_{datetime.datetime.now().date()}.png'
telegram_send_photo_caption(photo_path,f'Current MTM : {pnl_list[-1]}, Time : {time_now()}',chat_id)
