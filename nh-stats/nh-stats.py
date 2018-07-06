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

IP = "127.0.0.1"
DB = "nhstats"
USER = "pythonwriter"
PASSWORD = os.environ['NHS_INFLUXDB_PYTHON_WRITE_PASSWORD']
WALLET = os.environ['NHS_INTERNAL_WALLET']
ENERGY_COST_KWHR = float(os.environ['NHS_ENERGY_COST_FIAT_PER_KWHR'])
WEMO_DEVICE_IP = os.environ['NHS_WEMO_DEVICE_IP']
DEFAULT_ENERGY_COST_FIAT_PER_DAY = float(os.environ['NHS_DEFAULT_ENERGY_COST_FIAT_PER_DAY'])

if WEMO_DEVICE_IP == 'false':
	WEMO_DEVICE_IP = False

FIAT = os.environ['NHS_FIAT_CURRENCY']
prev_value_file = '/nh-stats/prev_balance.pickle'

curr_price = crypto_api.get_btc_price(FIAT)

print("Balances: \n")
balances = crypto_api.get_balances(wallet=WALLET)
curr_timestamp = time.time()

num_algos = len(balances)
total_balance = 0.0
for idx_algo in range(num_algos):
	total_balance = total_balance + balances[idx_algo]['balance']

selected_algos = [5, 8, 14, 20, 24, 32, 33]

running_total = 0.0
for idx_algo in selected_algos:
	v = "crypto_{0:d}_{1:s} value={2:f}".format(idx_algo, balances[idx_algo]['algo_str'],balances[idx_algo]['balance'])
	print(v)
	r = requests.post("http://%s:8086/write?db=%s" %(IP, DB), auth=(USER, PASSWORD), data=v)
	if r.status_code != 204:
	    print 'Failed to add point to influxdb (%d) - aborting.' %r.status_code
	    sys.exit(1)  	
	running_total = running_total + balances[idx_algo]['balance']

v = "crypto_other value={0:f}".format(total_balance-running_total)
print(v)
r = requests.post("http://%s:8086/write?db=%s" %(IP, DB), auth=(USER, PASSWORD), data=v)
if r.status_code != 204:
    print 'Failed to add point to influxdb (%d) - aborting.' %r.status_code
    sys.exit(1)  	

v = "crypto_total value={0:f}".format(total_balance)
print(v)
r = requests.post("http://%s:8086/write?db=%s" %(IP, DB), auth=(USER, PASSWORD), data=v)
if r.status_code != 204:
    print 'Failed to add point to influxdb (%d) - aborting.' %r.status_code
    sys.exit(1)  	

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
	debug1 = 1.0
	debug2 = float(curr_data['total_balance'])
	debug3 = measurement_time_delta
else:
	btc_per_day = 86400.0 * (curr_data['total_balance']-prev_data['total_balance']) / (measurement_time_delta) 
	debug1 = 1.0
	debug2 = float(curr_data['total_balance']-prev_data['total_balance'])
	debug3 = measurement_time_delta	

print("Time between measurements: {0:f}".format(measurement_time_delta))	

v = 'debug1 value=%f' % debug1
r = requests.post("http://%s:8086/write?db=%s" %(IP, DB), auth=(USER, PASSWORD), data=v)
if r.status_code != 204:
    print 'Failed to add point to influxdb (%d) - aborting.' %r.status_code
    sys.exit(1)

v = 'debug2 value=%f' % debug2
r = requests.post("http://%s:8086/write?db=%s" %(IP, DB), auth=(USER, PASSWORD), data=v)
if r.status_code != 204:
    print 'Failed to add point to influxdb (%d) - aborting.' %r.status_code
    sys.exit(1)

v = 'debug3 value=%f' % debug3
r = requests.post("http://%s:8086/write?db=%s" %(IP, DB), auth=(USER, PASSWORD), data=v)
if r.status_code != 204:
    print 'Failed to add point to influxdb (%d) - aborting.' %r.status_code
    sys.exit(1)



with open(prev_value_file, 'wb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(curr_data, f, pickle.HIGHEST_PROTOCOL)


fiat_per_day = btc_per_day*curr_price

print("+{0} BTC/day".format(btc_per_day))
print("+{0} fiat/day".format(fiat_per_day))

# Write to InfluxDB

v = 'btc_per_day value=%f' % btc_per_day
r = requests.post("http://%s:8086/write?db=%s" %(IP, DB), auth=(USER, PASSWORD), data=v)
if r.status_code != 204:
    print 'Failed to add point to influxdb (%d) - aborting.' %r.status_code
    sys.exit(1)

v = 'fiat_per_day value=%f' % fiat_per_day
r = requests.post("http://%s:8086/write?db=%s" %(IP, DB), auth=(USER, PASSWORD), data=v)
if r.status_code != 204:
    print 'Failed to add point to influxdb (%d) - aborting.' %r.status_code
    sys.exit(1)    


#Get power usage
energy_cost_fiat_per_day = DEFAULT_ENERGY_COST_FIAT_PER_DAY

if(WEMO_DEVICE_IP != False):
	port = pywemo.ouimeaux_device.probe_wemo(WEMO_DEVICE_IP)
	if(port):
		url = 'http://%s:%i/setup.xml' % (WEMO_DEVICE_IP, port)
		device = pywemo.discovery.device_from_description(url, None)
		device.update_insight_params()
		current_power_mw = float(device.current_power)
		current_power_kw = current_power_mw / 1000 / 1000
		energy_cost_fiat_per_day = current_power_kw * ENERGY_COST_KWHR * 24		

profit_fiat_per_day = fiat_per_day-energy_cost_fiat_per_day

print("-{0} fiat/day (energy cost)".format(energy_cost_fiat_per_day))
print("={0} fiat/day (profit)".format(profit_fiat_per_day))

v = 'energy_cost_fiat_per_day value=%f' % energy_cost_fiat_per_day
r = requests.post("http://%s:8086/write?db=%s" %(IP, DB), auth=(USER, PASSWORD), data=v)
if r.status_code != 204:
    print 'Failed to add point to influxdb (%d) - aborting.' %r.status_code
    sys.exit(1)  

v = 'profit_fiat_per_day value=%f' % profit_fiat_per_day
r = requests.post("http://%s:8086/write?db=%s" %(IP, DB), auth=(USER, PASSWORD), data=v)
if r.status_code != 204:
    print 'Failed to add point to influxdb (%d) - aborting.' %r.status_code
    sys.exit(1)  	







