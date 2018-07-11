import sys
import requests
import time
import datetime

# API URLS
URL_STATS_PROVIDER = 'https://api.nicehash.com/api?method=stats.provider&addr={}'
URL_BTC_PRICE = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC&tsyms={}'

WALLET = '1P5PNW6Wd53QiZLdCs9EXNHmuPTX3rD6hW' #Dummy wallet. To be overwritten


###############################################################################

def req_url(url):
    try:
        response = requests.get(url).json()
    except Exception as e:        
        print("Error using API: {0:s}".format(str(e)))
        return None
    return response


###############################################################################

def get_btc_price(fiat='USD'):
    response = req_url(URL_BTC_PRICE.format(fiat))

    if response is None:
        return None

    curr_price = response['BTC'][fiat]
    return curr_price


def get_balances(wallet=WALLET):
    response = req_url(URL_STATS_PROVIDER.format(wallet))

    if response is None:
        return None

    if 'error' in response['result']:
        print(response['result']['error'])
        return None

    curr_stats = response['result']['stats']
    num_resp = len(curr_stats)

    dictlist = [dict() for x in range(35)]

    for idx_algo in range(35):

        if (idx_algo == 0):
            algo_str = 'Scrypt'
        elif (idx_algo == 1):
            algo_str = 'SHA256'
        elif (idx_algo == 2):
            algo_str = 'ScryptNf'
        elif (idx_algo == 3):
            algo_str = 'X11'
        elif (idx_algo == 4):
            algo_str = 'X13'
        elif (idx_algo == 5):
            algo_str = 'Keccak'
        elif (idx_algo == 6):
            algo_str = 'X15'
        elif (idx_algo == 7):
            algo_str = 'Nist5'
        elif (idx_algo == 8):
            algo_str = 'NeoScrypt'
        elif (idx_algo == 9):
            algo_str = 'Lyra2RE'
        elif (idx_algo == 10):
            algo_str = 'WhirlpoolX'
        elif (idx_algo == 11):
            algo_str = 'Qubit'
        elif (idx_algo == 12):
            algo_str = 'Quark'
        elif (idx_algo == 13):
            algo_str = 'Axiom'
        elif (idx_algo == 14):
            algo_str = 'Lyra2REv2'
        elif (idx_algo == 15):
            algo_str = 'ScryptJaneNf16'
        elif (idx_algo == 16):
            algo_str = 'Blake256r8'
        elif (idx_algo == 17):
            algo_str = 'Blake256r14'
        elif (idx_algo == 18):
            algo_str = 'Blake256r8vnl'
        elif (idx_algo == 19):
            algo_str = 'Hodl'
        elif (idx_algo == 20):
            algo_str = 'DaggerHashimoto'
        elif (idx_algo == 21):
            algo_str = 'Decred'
        elif (idx_algo == 22):
            algo_str = 'CryptoNight'
        elif (idx_algo == 23):
            algo_str = 'Lbry'
        elif (idx_algo == 24):
            algo_str = 'Equihash'
        elif (idx_algo == 25):
            algo_str = 'Pascal'
        elif (idx_algo == 26):
            algo_str = 'X11Gost'
        elif (idx_algo == 27):
            algo_str = 'Sia'
        elif (idx_algo == 28):
            algo_str = 'Blake2s'
        elif (idx_algo == 29):
            algo_str = 'Skunk'
        elif (idx_algo == 30):
            algo_str = 'CryptoNightV7'
        elif (idx_algo == 31):
            algo_str = 'CryptoNightHeavy'   
        elif (idx_algo == 32):
            algo_str = 'Lyra2Z'
        elif (idx_algo == 33):
            algo_str = 'X16R'
        else:
            algo_str = 'other'                            

        dictlist[idx_algo]['algo_str'] = algo_str
        dictlist[idx_algo]['balance'] = float(0)

    for idx_resp in range(num_resp):
        current_resp = curr_stats[idx_resp]     

        if( (current_resp['algo']<=33) and (current_resp['algo']>=0) ):
            dictlist[current_resp['algo']]['balance'] = float(current_resp['balance'])
        else:
            dictlist[34]['balance'] = dictlist[34]['balance']+float(current_resp['balance'])
    return dictlist        
    
