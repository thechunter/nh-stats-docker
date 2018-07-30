import datetime
now = datetime.datetime.now()
print("\n")
print(now)

import crypto_api
import json
import requests
import sys
import pywemo
import pickle
import time
import os

curr_timestamp = time.time()

IP = "127.0.0.1"
DB = "nhstats"
USER = "pythonwriter"
PASSWORD = os.environ['NHS_INFLUXDB_PYTHON_WRITE_PASSWORD']
WALLET_VEC = os.environ['NHS_INTERNAL_WALLET'].split(',')
ENERGY_COST_KWHR = float(os.environ['NHS_ENERGY_COST_FIAT_PER_KWHR'])
WEMO_DEVICE_IP_VEC =  os.environ['NHS_WEMO_DEVICE_IP'].split(',')
DEFAULT_ENERGY_COST_FIAT_PER_DAY = float(os.environ['NHS_DEFAULT_ENERGY_COST_FIAT_PER_DAY'])

if WEMO_DEVICE_IP_VEC == 'false':
	WEMO_DEVICE_IP_VEC = False

FIAT = os.environ['NHS_FIAT_CURRENCY']
prev_value_file = '/nh-stats/prev_balance.pickle'

def write_influxDB(data):
	print(data)	
	r = requests.post("http://{0:s}:8086/write?db={1:s}".format(IP,DB), auth=(USER, PASSWORD), data=data)
	if r.status_code != 204:
	    print("Failed to add point to influxdb ({0}) - aborting.".format(r.status_code))
	    sys.exit(1)  	

curr_price = crypto_api.get_btc_price(FIAT)

print("Balances: \n")

idx_wallet = 0
for WALLET in WALLET_VEC:
	if idx_wallet == 0:
		balances = crypto_api.get_balances(wallet=WALLET)
	else:
		balances_tmp = crypto_api.get_balances(wallet=WALLET)

		if balances_tmp is None:
			print("Error in NH API call. Exiting before logging anything")
			sys.exit(1)

		for idx_algo in range(35):
			balances[idx_algo]['balance'] += balances_tmp[idx_algo]['balance']

	idx_wallet+=1

#Heuristic: we're going to skip writing zero-valued balances
total_balance = 0.0
for idx_algo in range(35):
	total_balance = total_balance + balances[idx_algo]['balance']

if(total_balance == 0.0):
	print("No balance reported. Exiting before logging anything")
	sys.exit(1)

num_algos = len(balances)
total_balance = 0.0
for idx_algo in range(num_algos):
	total_balance = total_balance + balances[idx_algo]['balance']

selected_algos = [5, 8, 14, 20, 24, 32, 33]

running_total = 0.0
for idx_algo in selected_algos:
	v = "crypto_{0:d}_{1:s} value={2:f}".format(idx_algo, balances[idx_algo]['algo_str'],balances[idx_algo]['balance'])	
	write_influxDB(v)
	running_total = running_total + balances[idx_algo]['balance']

v = "crypto_other value={0:f}".format(total_balance-running_total)
write_influxDB(v)

v = "crypto_total value={0:f}".format(total_balance)
write_influxDB(v)

#write current total to file
curr_data = {
    'timestamp': curr_timestamp,
    'total_balance': total_balance   
}

prev_data = curr_data

with open(prev_value_file, 'rb') as f:
    prev_data = pickle.load(f)

#Handle wrapping when Nicehash pays out the balance
measurement_time_delta = float(curr_data['timestamp']-prev_data['timestamp'])

if(curr_data['total_balance'] < prev_data['total_balance']):
	btc_per_day = 86400.0 * (curr_data['total_balance']) / (measurement_time_delta)
else:
	btc_per_day = 86400.0 * (curr_data['total_balance']-prev_data['total_balance']) / (measurement_time_delta) 

print("Time between measurements: {0:f}".format(measurement_time_delta))

if(measurement_time_delta < 50.0):
	#For whatever reason, this latest measurement was unexpectedly close to in time
	#to the previous measurement. I don't trust the btc_per_day calculation in this
	#case, so we'll just quit before entering these measurements.
	sys.exit(0)


with open(prev_value_file, 'wb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(curr_data, f, pickle.HIGHEST_PROTOCOL)


fiat_per_day = btc_per_day*curr_price

print("+{0} BTC/day".format(btc_per_day))
print("+{0} fiat/day".format(fiat_per_day))

# Write to InfluxDB
v = "btc_per_day value={0:f}".format(btc_per_day)
write_influxDB(v)


#Get power usage

if(WEMO_DEVICE_IP_VEC != False):

	energy_cost_fiat_per_day = 0.0;

	for WEMO_DEVICE_IP in WEMO_DEVICE_IP_VEC:	
		port = pywemo.ouimeaux_device.probe_wemo(WEMO_DEVICE_IP)
		if(port):
			url = "http://{0:s}:{1:d}/setup.xml".format(WEMO_DEVICE_IP, port)
			device = pywemo.discovery.device_from_description(url, None)
			device.update_insight_params()
			current_power_mw = float(device.current_power)
			current_power_kw = current_power_mw / 1000 / 1000
			energy_cost_fiat_per_day += current_power_kw * ENERGY_COST_KWHR * 24	
else:
	energy_cost_fiat_per_day = DEFAULT_ENERGY_COST_FIAT_PER_DAY	

profit_fiat_per_day = fiat_per_day-energy_cost_fiat_per_day

print("-{0} fiat/day (energy cost)".format(energy_cost_fiat_per_day))
print("={0} fiat/day (profit)".format(profit_fiat_per_day))



v1 = "fiat_per_day value={0:f}".format(fiat_per_day)

v2 = "energy_cost_fiat_per_day value={0:f}".format(energy_cost_fiat_per_day)

v3 = "profit_fiat_per_day value={0:f}".format(profit_fiat_per_day)

v = v1+"\n"+v2+"\n"+v3

write_influxDB(v)







