import datetime
import time
from login_flow import api
import pandas as pd
from tg_bot import telegram_send_message, telegram_send_photo_caption, telegram_send_file
import matplotlib.pyplot as plt
import numpy as np


chat_id = "YOUR_TELEGRAM_CHAT_ID"
# ALGO STARTED
print(telegram_send_message(f'\nRS BNF - Algo Started @ {datetime.datetime.now().time()}',chat_id))


# START & END TIME
start_time = datetime.time(hour=9,minute=16)
qty = 25
TL_StrikeList = []
TL_EntryPrice = []
TL_ExitPrice = []
TL_EntryTime = []


# WAITING FOR START TIME
while datetime.datetime.now().time() < start_time:
    print(f'Waiting for {start_time}. Time : {datetime.datetime.now().time()}')
    time.sleep(1)




# EXECUTE AT START TIME
while True:

    # banknifty spot token, LTP, ATM Strike & Diff between LTP & ATM
    spot_token = api.searchscrip('NSE','NIFTY BANK')['values'][0]['token']
    banknifty_LTP = float(api.get_quotes('NSE',spot_token)['lp'])
    banknifty_ATM = round(banknifty_LTP,-2)
    difference = banknifty_LTP - banknifty_ATM
    
    print(f'\nLTP is {banknifty_LTP} & ATM is {banknifty_ATM} & difference is {difference} points.')

    # if difference is between +20/-20 points
    if banknifty_LTP - banknifty_ATM <= 5 and banknifty_LTP - banknifty_ATM >= -5:
       
        # search for ATM CE/PE trading symbol
        search_ce = 'BANKNIFTY ' + str(banknifty_ATM) + ' CE'
        search_pe = 'BANKNIFTY ' + str(banknifty_ATM) + ' PE'
        
        # ATM CE/PE trading symbol
        ce_symbol = api.searchscrip('NFO',search_ce)['values'][0]['tsym']
        pe_symbol = api.searchscrip('NFO',search_pe)['values'][0]['tsym']

        # CE & PE LTP
        ce_ltp = float(api.get_quotes(exchange='NFO',token=ce_symbol)['lp'])
        pe_ltp = float(api.get_quotes(exchange='NFO',token=pe_symbol)['lp'])

        # Defining Straddle Strike & Price
        StraddleStrike = banknifty_ATM
        StraddlePrice = ce_ltp + pe_ltp

        print(telegram_send_message(f'Sell {round(StraddleStrike)} Straddle @ {round(StraddlePrice,2)} \nTime: {datetime.datetime.now().time()}',chat_id))

        # Setting straddle price as entry price and adding to trade log list
        Entry_Price = StraddlePrice

        TL_StrikeList.append(StraddleStrike)
        TL_EntryPrice.append(Entry_Price)
        TL_EntryTime.append(datetime.datetime.now().time())
        
        break

    else:
        print('Wait for 2 more seconds. Checking again...')
        time.sleep(2)





# End time & PNL List
end_time = datetime.time(hour=15,minute=25)
pnl_list = []




# if end time has not come yet then
while datetime.datetime.now().time() < end_time:
    try:
        
        #set minute & second
        minute = datetime.datetime.now().minute
        second = datetime.datetime.now().second

        # Find ATM
        banknifty_LTP = float(api.get_quotes('NSE',spot_token)['lp'])
        banknifty_ATM = round(banknifty_LTP,-2)
        difference = banknifty_LTP - banknifty_ATM
        print(f'\nLTP is {banknifty_LTP} & ATM is {banknifty_ATM} & difference is {difference} points.')
        
        # fetch ltp of Straddle Sold & calculate PNL
        ce_ltp = float(api.get_quotes('NFO',ce_symbol)['lp'])
        pe_ltp = float(api.get_quotes('NFO',pe_symbol)['lp'])
        StraddlePrice = ce_ltp + pe_ltp
        
        pnl = (Entry_Price - StraddlePrice) * qty
        pnl = round(pnl,2)

        # create a list of pnl
        pnl_list.append(pnl)


        # if the LTP has crossed and skipped the ATM where position was to be adjusted
        if banknifty_ATM != StraddleStrike and (banknifty_LTP > (StraddleStrike+106) or banknifty_LTP < (StraddleStrike-106)):
            
            # pnl before adjustment
            print(telegram_send_message(f'Exit {StraddleStrike} Straddle at {StraddlePrice} \nPNL: {pnl}',chat_id))
            TL_ExitPrice.append(StraddlePrice)

            # search for ATM CE/PE Trading Symbol & LTP
            search_ce = 'BANKNIFTY ' + str(banknifty_ATM) + ' CE'
            search_pe = 'BANKNIFTY ' + str(banknifty_ATM) + ' PE'

            ce_symbol = api.searchscrip('NFO',search_ce)['values'][0]['tsym']
            pe_symbol = api.searchscrip('NFO',search_pe)['values'][0]['tsym']

            ce_ltp = float(api.get_quotes(exchange='NFO',token=ce_symbol)['lp'])
            pe_ltp = float(api.get_quotes(exchange='NFO',token=pe_symbol)['lp'])

            # Straddle Price
            StraddleStrike = banknifty_ATM
            StraddlePrice = ce_ltp + pe_ltp

            print(telegram_send_message(f'Adjustment: Sold new straddle of {round(StraddleStrike)} at {StraddlePrice} \nTime: {datetime.datetime.now().time()}',chat_id))

            Entry_Price = StraddlePrice + (pnl/qty)

            TL_StrikeList.append(StraddleStrike)
            TL_EntryPrice.append(Entry_Price)
            TL_EntryTime.append(datetime.datetime.now().time())

            time.sleep(10)



        
        # adjustment criteria : roll if the ATM has changed and LTP is closest to ATM
        elif banknifty_ATM != StraddleStrike and banknifty_LTP - banknifty_ATM <= 5 and banknifty_LTP - banknifty_ATM >= -5:
            
            # pnl before adjustment
            print(telegram_send_message(f'Exit {StraddleStrike} Straddle at {StraddlePrice} \nPNL: {pnl}',chat_id))
            TL_ExitPrice.append(StraddlePrice)


            # search for ATM CE/PE Trading Symbol & LTP
            search_ce = 'BANKNIFTY ' + str(banknifty_ATM) + ' CE'
            search_pe = 'BANKNIFTY ' + str(banknifty_ATM) + ' PE'

            ce_symbol = api.searchscrip('NFO',search_ce)['values'][0]['tsym']
            pe_symbol = api.searchscrip('NFO',search_pe)['values'][0]['tsym']

            ce_ltp = float(api.get_quotes(exchange='NFO',token=ce_symbol)['lp'])
            pe_ltp = float(api.get_quotes(exchange='NFO',token=pe_symbol)['lp'])

            # Straddle Price
            StraddleStrike = banknifty_ATM
            StraddlePrice = ce_ltp + pe_ltp

            print(telegram_send_message(f'Adjustment: Sold new straddle of {round(StraddleStrike)} at {StraddlePrice} \nTime: {datetime.datetime.now().time()}',chat_id))

            Entry_Price = StraddlePrice + (pnl/qty)

            TL_StrikeList.append(StraddleStrike)
            TL_EntryPrice.append(StraddlePrice)
            TL_EntryTime.append(datetime.datetime.now().time())

            time.sleep(10)




        # post photo to telegram group every half an hour
        elif minute%30 == 0:
            
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
            plt.title('RS BNF')
            plt.savefig(f'output/pnl_{datetime.datetime.now().date()}.png')

            # send pnl photo to telegram
            photo_path = f'output/pnl_{datetime.datetime.now().date()}.png'
            telegram_send_photo_caption(photo_path,f'Current MTM : {pnl_list[-1]}, Time : {datetime.datetime.now().time()}',chat_id)

            time.sleep(10)



        # post pnl to telegram group every 5 minutes
        elif minute%5 == 0:

            # convert the list into a df and export as csv
            pnl_df = pd.DataFrame()
            pnl_df['pnl'] = pnl_list
            pnl_df.to_csv(f'output/pnl_{datetime.datetime.now().date()}.csv',index=False)
            
            print(f'Current MTM : {pnl}, Time :  {datetime.datetime.now().time()}')
            time.sleep(10)


        # check conditions in every 10 seconds
        else:
            
            print(f'Current MTM : {pnl}, Time : {datetime.datetime.now().time()}')
            time.sleep(10)

    except:
        continue



# at 3.25 pm, exit all existing positions
print(telegram_send_message(f'Exit {StraddleStrike} Straddle at {StraddlePrice} \nPNL: {pnl}',chat_id))
TL_ExitPrice.append(StraddlePrice)

# create a dataframe for trade log and post csv on telegram channel
trade_log = pd.DataFrame()
trade_log['Strike'] = TL_StrikeList
trade_log['Entry Time'] = TL_EntryTime
trade_log['Entry Price'] = TL_EntryPrice
trade_log['Exit Price'] = TL_ExitPrice
trade_log.to_csv(f'output/tradelog_{datetime.datetime.now().date()}.csv',index=False)
telegram_send_file(f'output/tradelog_{datetime.datetime.now().date()}.csv',chat_id)


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
plt.title('RS BNF')
plt.savefig(f'output/pnl_{datetime.datetime.now().date()}.png')

# send pnl photo to telegram
photo_path = f'output/pnl_{datetime.datetime.now().date()}.png'
telegram_send_photo_caption(photo_path,f'Current MTM : {pnl_list[-1]}, Time : {datetime.datetime.now().time()}',chat_id)
