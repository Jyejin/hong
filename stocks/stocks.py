import os
import threading
import time
import datetime
from urllib.request import Request, urlopen
import pandas as pd
from bs4 import BeautifulSoup
import requests

#from colorama import init, Style
import json
from collections import namedtuple
import re

#init()
KOSPI = pd.read_csv("../data/name_code_list_KOSPI.csv",index_col='KOSPI_NAME')
KOSDAQ = pd.read_csv("../data/name_code_list_KOSDAQ.csv",index_col='KOSDAQ_NAME')
COIN = pd.read_csv("../data/crypto.csv",index_col='NAME')

with open('../data/my_stocks.txt') as f:
    my_stocks = [i.strip() for i in f]

with open('../data/my_coins.txt') as f:
    my_coins = [i.strip() for i in f]

def url_set_naver(name):
    if name in KOSPI.index:
        result = KOSPI.loc[name]['CODE']
    elif name in KOSDAQ.index:
        result = KOSDAQ.loc[name]['CODE']

    url_form ='http://finance.naver.com/item/sise.nhn?code=' + str(result).zfill(6)
    url = None
    url = url_form.format(result=result)

    return url

def extracting_stock_naver(name):

    url = url_set_naver(name)
    html = urlopen(url)
    soup = BeautifulSoup(html, "html.parser")

    return soup

def price():
    for stock in my_stocks:
        name_num = len(re.findall('[가-힣]',stock))
        stock_name = stock.ljust(14-name_num)

        soup = extracting_stock_naver(stock)
        table = soup.find_all('table')
        td_numbers = table[1].find_all('td',{'class':{'num'}})
        temp_numbers = [td_number.text.translate({ord('\n'): ' ',ord('\t'): '' }) for td_number in td_numbers]
    
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #output = stock_name + '{:>11}{:>12}{:>11}{:>20}'.format(temp_numbers[0].strip(),temp_numbers[2].strip(),'('+temp_numbers[4].strip()+')',now_time)

        if '하락' in temp_numbers[2]:
            output = stock_name + '{:>11}{:>11}{:>9}{:>23}'.format(temp_numbers[0].strip(),temp_numbers[2].strip(),'('+temp_numbers[4].strip()+')',now_time)
            output = output.replace('하락','▼')
            output = '\033[34m' + output + '\033[0m'
        elif '상승' in temp_numbers[2]:
            output = stock_name + '{:>11}{:>12}{:>9}{:>23}'.format(temp_numbers[0].strip(),temp_numbers[2].strip(),'('+temp_numbers[4].strip()+')',now_time)
            output = output.replace('상승 ','▲')
            output = '\033[31m' + output + '\033[0m'   
        else:
            output = '\033[30m' + output + '\033[0m'

        print(output)

def coinoneAPI(code):
    # 1분당 90회 요청 가능합니다.
    # https://api.coinone.co.kr/ticker/?currency=bch&format=json
    url = "https://api.coinone.co.kr/ticker/?currency=" + code + "&format=json"
    read_ticker =urlopen(url).read()
    #json_ticker = json.loads(read_ticker.decode('utf-8'))
    coin_data = json.loads(read_ticker.decode('utf-8'), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    return coin_data

def coinone_coins():
    print('{:>14}|{:>12}|{:>7}|{:>11}|{:>18}'.format('코인이름','현재가','등락률','거래대금','날짜'))

    for coin in my_coins:
        try:
            coin_code = COIN['CODE'][coin]
            coin_info = coinoneAPI(coin_code)   

            coin_name = coin+coin_code
            name_num = len(re.findall('[가-힣]',coin_name))
            coin_name = coin_name.rjust(18-name_num)

            last = float(coin_info.last)
            volume = coin_info.volume
            yesterday_last = float(coin_info.yesterday_last)
            percentage_change = round((last-yesterday_last)/yesterday_last*100,2)
            now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
            output = coin_name + '|{:>15}|{:>10}|{:>15}|{:>20}'.format(last,str(percentage_change)+'%',volume,now_time)
    
            if percentage_change > 0:
                output = '\033[31m' + output + '\033[0m'
            elif percentage_change < 0:
                output = '\033[34m' + output + '\033[0m'
            else:
                output = '\033[30m' + output + '\033[0m'

            print(output)
        except KeyError:
            pass
        
                   
def poloniexAPI():
    url = "https://poloniex.com/public?command=returnTicker"
    resp = requests.get(url)
    data = json.loads(resp.text)

    return data

def poloniex_coins():
    print('{:>8}|{:>15}|{:>15}|{:>16}|{:>20}|{:>20}'.format('코인이름','Last','PercentChange','BaseVolume','QuoteVolume','Time'))
    coin_array = poloniexAPI()   
    for coin in my_coins:
        try:
            coin_name = 'BTC_'+COIN['CODE'][coin]
            coin_info = coin_array[coin_name]
        
            last = coin_info['last']
            base_volume = coin_info['baseVolume']
            quote_volume = coin_info['quoteVolume']
            percentage_change = float(coin_info['percentChange'])
            now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
            output = '{:>12}|{:>15}|{:>15}|{:>16}|{:>20}|{:>20}'.format(coin_name,last,percentage_change,base_volume,quote_volume,now_time)
    
            if percentage_change > 0:
                output = '\033[31m' + output + '\033[0m'
            elif percentage_change < 0:
                output = '\033[34m' + output + '\033[0m'
            else:
                output = '\033[30m' + output + '\033[0m'

            print(output)
        except KeyError:
            pass
        
flag = True

def del_stock():
    stat = True
    while stat == True:
            os.system('cls||CLS||clear')
            print('현재 나의 주식: ',my_stocks)
            print('현재 나의 코인: ',my_coins)
            print('나가기는 "q"')
            temp = input('지울 종목을 입력하시게나:')
           
            if temp in my_stocks:  
                my_stocks.remove(temp)
                with open('my_stocks.txt','w') as f:
                    for stock in my_stocks:
                        f.write(stock+'\n')
            elif temp in my_coins:
                my_coins.remove(temp)
                with open('my_coins.txt','w') as f:
                    for coin in my_coins:
                        f.write(coin+'\n')
            elif temp == 'q':
                menu()
                stat = False
            else:
                print('그런건 없다네!\n')
                continue

def view_mine():
    global flag
    while flag == True:
        os.system('cls||CLS||clear')

        print('주식 시세')
        price()
            
        print('\n코인원 시세') 
        coinone_coins()
        
        print('\n폴로닉스시세')
        poloniex_coins()
        print('\n데이터는 10초 간격으로 갱신됩니다')
        print('Enter to quit')
        time.sleep(10)
        
       
def get_input():
    global flag
    while True:
        name=input()
        if not name:
            flag = False
            break

def menu():
    
    print('등록을 마쳤다면 이제 구경해보게나!')
    print('[1]시세보기 [2]주식 지우기 [3]되돌아가기')
    num = input('입력: ')
    if num == '1':
        thread1=threading.Thread(target=get_input)
        thread2=threading.Thread(target=view_mine)
        thread2.daemon = True
        thread1.start()
        thread2.start()

    elif num == '2':
        del_stock()

    elif num == '3':
        return

    else:
        pass
            

  
def main(): 
    while True:
        os.system('cls||CLS||clear')
        print('\033[31m'+'************홍길동 주식*************'+'\033[0m')
        print('반갑네 당신의 주식 친구 홍길동이라네!\n')
        print('현재 나의 주식: ',my_stocks)
        print('현재 나의 비트코인: ',my_coins,'\n')
        print('추가하고 싶은 주식이나 비트코인이 있다면 아래 입력창에다 입력하게나\n 그리고 등록이 끝나면 Enter를 눌러')
        print('나가기는 q')

        name = input('추가하기: ')
        if not name:
            menu()
            break
        elif (name in KOSPI['CODE']) or (name in KOSDAQ['CODE']):
            my_stocks.append(name)
            with open('my_stocks.txt','a') as f:
                f.write(name+'\n')
        elif name in COIN.index:
            my_coins.append(name)
            with open('my_coins.txt','a') as f:
                f.write(name+'\n')
        elif name == 'q':
            print('다음에 또 봅세!')
            break
        else:
            print('그런건 없다네!')
            time.sleep(0.3)
        
    
if __name__ == "__main__":
    main()