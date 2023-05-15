from web3 import Web3
from web3.middleware import geth_poa_middleware
import requests
import time
import telebot

api_tg = 'api_tg'
api_bscscan = 'api_bscscan'

validators = {
    'Legenda III': '0x8b6c8fd93d6f4cea42bbb345dbc6f0dfdb5bec73',
    'Legenda I': '0x295e26495cef6f69dfa69911d9d8e4f3bbadb89b',
    '0x35EBb5849518aFF370cA25E19e1072cC1a9FAbCa': '0x35EBb5849518aFF370cA25E19e1072cC1a9FAbCa'}

bot = telebot.TeleBot(api_tg)
w3 = Web3(Web3.HTTPProvider('https://bsc.blockpi.network/v1/rpc/public'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
same_block_count = last_block_number = i = 0


@bot.message_handler(content_types=['text'])
def start_message(message):
    global same_block_count
    global i
    try:
        response = requests.post(
            f'https://api.bscscan.com/api?module=account&action=txlist&address={list(validators.values())[i]}&page=1&offset=10&sort=desc&apikey={api_bscscan}').json()
    except Exception as e:
        print(e)
        time.sleep(5)
        start_message(message)
    print(response)
    block_number = int(response['result'][0]['blockNumber'])
    if block_number <= last_block_number:
        print('same block')
        same_block_count += 1
        if same_block_count >= 10:
            i += 1
            same_block_count = 0
            if i > len(validators) - 1:
                i = 0
        time.sleep(5)
        start_message(message)
    try:
        block = w3.eth.getBlock(block_number, full_transactions=False)
    except:
        time.sleep(20)
        start_message(message)

    transaction_hashes = block['transactions']

    all_gwei = []

    print(f"Transaction hashes in block {block_number}:")
    for tx_hash in transaction_hashes[-10:]:
        transaction_hash = tx_hash.hex()
        try:
            transaction = w3.eth.getTransaction(transaction_hash)
        except:
            continue

        print("Transaction information:")
        print(f"  Hash: {transaction_hash}")
        print(f"  Gas linit: {transaction['gas']}")
        print(f"  GWEI: {Web3.fromWei(transaction['gasPrice'], 'gwei')} gwei")
        all_gwei.append(Web3.fromWei(transaction['gasPrice'], 'gwei'))
    while 0 in all_gwei:
        all_gwei.remove(0)
    print(f'\nMinimum GWEI: {min(all_gwei)}')
    if min(all_gwei) >= 3:
        i += 1
        if i > len(validators) - 1:
            i = 0
            bot.send_message(message.chat.id,
                             f'👼 Validator: {list(validators.keys())[i]}\n💠 Block: {block_number}\n🔥 Minimum GWEI: {min(all_gwei)}')
        start_message(message)
    else:
        bot.send_message(message.chat.id,
                         f'👼 Validator: {list(validators.keys())[i]}\n💠 Block: {block_number}\n🔥 Minimum GWEI: {min(all_gwei)}')


bot.polling()
