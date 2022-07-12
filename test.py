import requests
import json
import re
import time
import sys

#Querying bitQuery for fetching other data.

def bitquery_api_request(query, variables):

  url = "https://graphql.bitquery.io/"

  payload = json.dumps({
  "query": query,
  "variables": variables
})

  headers = {
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Cookie': 'connect.sid=s%3AoZjcaJs5RCQuzX8WLqt7wSQ5knu3OgAh.ENwEo060r%2BJ%2BzRUGwrkcFA4SV5uo3a2jveyeB254Cao; _fw_crm_v=afbef42e-d8a1-43b9-ecba-483239135f58; _gid=GA1.2.115487869.1657553630; _ga=GA1.1.1393592384.1657549879; _ga_J5F4SQLVDZ=GS1.1.1657610565.5.1.1657610900.0',
    'Origin': 'https://graphql.bitquery.io',
    'Referer': 'https://graphql.bitquery.io/ide',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'X-API-KEY': 'BQYiCdXuobP11neW3wgQ7LqmLqyyirfA',
    'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"'
  }

  response = requests.request("POST", url, headers=headers, data=payload)

  return response.text

#GETTING ETHER PRICE IN USD

def get_current_ether_price_in_usd():
  resp = requests.get("https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD,ETH")
  data = json.loads(resp.text)
  price_in_usd = data.get("USD")
  return price_in_usd


ether_price_usd = get_current_ether_price_in_usd()


def getting_Account_balance(each_address, ether_price_usd):
  query = "{\n  ethereum {\n    address(address: {is: \"each_address\"}) {\n      balance\n    }\n  }\n}\n"
  variables = ""
  query = query.replace('each_address',each_address)
  data = bitquery_api_request(query, variables)
  try:
    data = json.loads(data)
    balance_block = (((data.get("data").get("ethereum").get("address")))[0])
    balance = (balance_block.get("balance"))
    balance_tmp = "{:.2f}".format(balance)
    balance_in_usd = float(balance_tmp) * float(ether_price_usd)
  except Exception as e:
    balance = 0.0
    balance_in_usd = 0.0
    pass
  return balance, balance_in_usd

def getting_current_holdings(each_address):
  variables = "{\n  \"limit\": 150,\n  \"offset\": 0,\n  \"network\": \"ethereum\",\n  \"address\": \"address_new\"\n}"
  variables = variables.replace("address_new", each_address )
  query = "query ($network: EthereumNetwork!, $address: String!) {\n  ethereum(network: $network) {\n    address(address: {is: $address}) {\n      balances {\n        currency {\n          address\n          symbol\n          tokenType\n        name\n        }\n        value\n      }\n    }\n  }\n}\n"
  data = bitquery_api_request(query, variables)
  try:
    data = json.loads(data)
    #print(data)
    holdings_data = (((data.get("data").get("ethereum").get("address")))[0])
    holdings_data = holdings_data.get("balances")
    all_holdings_list = []
    for record in holdings_data:
      temp_dict = {}
      value = record.get("value")
      if int(value) == 0.0:
        continue
      temp_dict['symbol'] = record.get("currency").get("symbol")
      temp_dict['tokenType'] = record.get("currency").get("tokenType")
      temp_dict['name'] = record.get("currency").get("name")
      temp_dict['value'] = value
      all_holdings_list.append((temp_dict))
  except:
    all_holdings_list = []
  return all_holdings_list


def get_transactions(each_address):
    url = f'https://api.etherscan.io/api?module=account&action=txlist&address={each_address}&startblock=0&endblock=99999999&page=1&offset=15&sort=asc&apikey=XCPX4IE2HNZYK4CDIUN1VQU8A68Z8XQRPU'
    resp = requests.get(url)

    data = (resp.text)
    data = json.loads(data)
    transaction_data = data.get("result")

    all_transactions_list = []
    for each_transaction in transaction_data:
      transaction_dict = {}
      transaction_dict['from'] = each_transaction.get("from")
      transaction_dict['to'] = each_transaction.get("to")
      transaction_dict['value'] = each_transaction.get("value")
      transaction_dict['timeStamp'] = each_transaction.get('timeStamp')
      transaction_dict['hash'] = each_transaction.get('hash')
      all_transactions_list.append((transaction_dict))
    return all_transactions_list



#Saved list of 100 random addresses from etherscan. Reading the file.


master_dict_list = []

f = open("address.txt", "r")
Lines = f.readlines()
  
count = 0
if sys.argv[1] == "ETH":
  for line in Lines:
      master_dict = {}
      address = line.strip()
      count = count + 1
      if count == 10:
        time.sleep(3)   
      account_balance = (getting_Account_balance(address, ether_price_usd))[0]
      account_balance_usd = (getting_Account_balance(address, ether_price_usd))[1]
      if account_balance == 0.0:
        continue
      master_dict['address'] = address
      master_dict['balance'] = account_balance
      master_dict['balance_USD'] = f'$ {account_balance_usd}'
      positions = getting_current_holdings(address)
      master_dict['positions'] = positions
      transactions = get_transactions(address)
      master_dict['transactions'] = transactions
      master_dict_list.append(((master_dict)))

# writing output to a json file

with open("output.json", "w") as outfile:
  for each_record in master_dict_list: 
    outfile.write(json.dumps(each_record))
    outfile.write('\n')



