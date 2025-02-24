import os
import time
import json
import random
from datetime import datetime, timedelta
import requests
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account.messages import encode_defunct
from colorama import Fore, Style, init
from fake_useragent import UserAgent

# Inisialisasi colorama
init(autoreset=True)

# Konfigurasi
config = {
    'rpcUrl': 'https://testnet-rpc.monad.xyz',
    'chainId': 10143,
    'contractAddress': '0x18C9534dfe16a0314B66395F48549716FfF9AA66',
    'apiBaseUrl': 'https://api.xyz.land',
    'signInEndpoint': '/signature/evm/{address}/sign',
    'chainIdHex': '0x279f'
}

ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "totalPoints", "type": "uint256"},
            {"name": "signature", "type": "bytes"}
        ],
        "name": "claim",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# File untuk menyimpan token dan user-agent
tokens_file = 'tokens.json'
user_agents_file = 'user_agents.json'

# Fungsi untuk menampilkan rainbow banner
def rainbow_banner():
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    banner = """
  _______                          
 |     __|.--.--.---.-.-----.---.-.
 |__     ||  |  |  _  |-- __|  _  |
 |_______||___  |___._|_____|___._|
          |_____|                   
    """
    
    for i, char in enumerate(banner):
        print(colors[i % len(colors)] + char, end="")
        time.sleep(0.007)
    print(Fore.LIGHTYELLOW_EX + "\nPlease wait...")
    time.sleep(2)
    # Clear screen setelah banner pertama
    os.system("clear" if os.name == "posix" else "cls")
    for i, char in enumerate(banner):
        print(colors[i % len(colors)] + char, end="")
    print(Fore.LIGHTYELLOW_EX + "\n")

# Fungsi untuk memuat data dari file JSON
def load_json(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Fungsi untuk menyimpan data ke file JSON
def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f)

# Fungsi untuk menampilkan statistik dengan format yang rapi
def print_stats(wallet_address, data):
    print(Fore.CYAN + "📊 Current Stats for " + Fore.YELLOW + wallet_address)
    print(Fore.CYAN + "🏅 Rank:", Fore.WHITE + str(data.get('rank', 'N/A')))
    print(Fore.CYAN + "⭐ Total Score:", Fore.WHITE + str(data.get('score', 'N/A')))
    print(Fore.CYAN + "⏳ Remaining Plays:", Fore.WHITE + str(data.get('remainingPlays', 'N/A')))
    print(Fore.CYAN + "❌ Daily Score:", Fore.WHITE + str(data.get('dailyScore', 'N/A')))
    if data.get('remainingPlays', 0) == 0:
        print(Fore.RED + "🚫 No remaining plays for today for " + Fore.YELLOW + wallet_address)
    print(Fore.CYAN + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# Fungsi untuk mendapatkan Bearer Token
def get_bearer_token(wallet_address, private_key, user_agent):
    try:
        message = f"www.dusted.app wants you to sign in with your Ethereum account:\n{wallet_address}\n\nI am proving ownership of the Ethereum account {wallet_address}.\n\nURI: https://www.dusted.app\nVersion: 1\nChain ID: 1\nNonce: {os.urandom(16).hex()}\nIssued At: {datetime.utcnow().isoformat()}Z"
        encoded_message = encode_defunct(text=message)
        web3 = Web3(Web3.HTTPProvider(config['rpcUrl']))
        signed_message = web3.eth.account.sign_message(encoded_message, private_key=private_key)

        sign_in_url = f"{config['apiBaseUrl']}{config['signInEndpoint'].format(address=wallet_address)}"
        payload = {
            "message": message,
            "signature": signed_message.signature.hex(),
            "provider": "metamask",
            "chainId": config['chainIdHex']
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Origin': 'https://www.dusted.app',
            'Referer': 'https://www.dusted.app/',
            'User-Agent': user_agent
        }
        response = requests.post(sign_in_url, json=payload, headers=headers)
        response.raise_for_status()

        token = response.json().get('token')
        if not token:
            raise ValueError("Token not found in response")
        return token
    except Exception as error:
        print(Fore.RED + f'Error getting Bearer Token for {wallet_address}: {str(error)}')
        return None

# Fungsi untuk memeriksa validitas token
def is_token_valid(api):
    try:
        response = api.get(f"{config['apiBaseUrl']}/lasso/score")
        return response.status_code == 200
    except Exception:
        return False

# Fungsi untuk mendapatkan harga gas (Gwei) dari jaringan
def get_gas_price(web3):
    try:
        gas_price = web3.eth.gas_price
        return gas_price
    except Exception as error:
        print(Fore.RED + f'Error getting gas price: {str(error)}')
        return None

# Fungsi untuk melakukan Claiming MON
def claim_mon(wallet_address, private_key, signatures, scores):
    try:
        web3 = Web3(Web3.HTTPProvider(config['rpcUrl']))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        wallet = web3.eth.account.from_key(private_key)
        contract = web3.eth.contract(address=config['contractAddress'], abi=ABI)

        # Gabungkan semua skor
        total_score = sum(scores)

        # Gunakan signature terakhir
        signature = signatures[-1]

        print(Fore.GREEN + f'Claiming MON for {wallet_address}...')
        
        # Dapatkan harga gas (Gwei) dari jaringan
        gas_price = get_gas_price(web3)
        if not gas_price:
            raise ValueError("Failed to get gas price")

        # Tambahkan buffer gas limit (misalnya, 1.5x dari estimasi)
        gas_limit = int(21000 * 1.5)  # Contoh: 1.5x dari gas limit standar

        tx = contract.functions.claim(total_score, signature).buildTransaction({
            'from': wallet.address,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': web3.eth.getTransactionCount(wallet.address)
        })
        signed_tx = wallet.signTransaction(tx)
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print(Fore.GREEN + f'Transaction submitted for {wallet_address}: {tx_hash.hex()}')

        # Menunggu konfirmasi transaksi
        try:
            receipt = web3.eth.waitForTransactionReceipt(tx_hash, timeout=120)  # Timeout 120 detik
            if receipt.status == 1:
                print(Fore.GREEN + f'✅ Transaction confirmed in block for {wallet_address}: {receipt["blockNumber"]}')
            else:
                print(Fore.RED + f'❌ Transaction failed for {wallet_address}')
        except Exception as error:
            print(Fore.RED + f'❌ Error waiting for transaction receipt for {wallet_address}: {str(error)}')

    except Exception as error:
        print(Fore.RED + f'Error claiming MON for {wallet_address}: {str(error)}')

# Fungsi untuk memproses setiap wallet
def process_wallet(private_key):
    try:
        web3 = Web3(Web3.HTTPProvider(config['rpcUrl']))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        wallet = web3.eth.account.from_key(private_key)
        wallet_address = wallet.address

        # Muat token dan user-agent
        tokens = load_json(tokens_file)
        user_agents = load_json(user_agents_file)

        # Jika user-agent belum ada, buat yang baru
        if wallet_address not in user_agents:
            user_agents[wallet_address] = UserAgent().random
            save_json(user_agents_file, user_agents)

        # Jika token sudah ada, cek validitas
        bearer_token = tokens.get(wallet_address)
        if bearer_token:
            api = requests.Session()
            api.headers.update({
                'Authorization': f'Bearer {bearer_token}',
                'User-Agent': user_agents[wallet_address]
            })
            if not is_token_valid(api):
                print(Fore.YELLOW + f"Token expired for {wallet_address}. Signing in again...")
                bearer_token = get_bearer_token(wallet_address, private_key, user_agents[wallet_address])
                if bearer_token:
                    tokens[wallet_address] = bearer_token
                    save_json(tokens_file, tokens)
        else:
            bearer_token = get_bearer_token(wallet_address, private_key, user_agents[wallet_address])
            if bearer_token:
                tokens[wallet_address] = bearer_token
                save_json(tokens_file, tokens)

        if not bearer_token:
            raise ValueError("Failed to retrieve Bearer Token")

        api = requests.Session()
        api.headers.update({
            'Authorization': f'Bearer {bearer_token}',
            'Accept': '*/*',
            'Origin': 'https://www.dusted.app',
            'Referer': 'https://www.dusted.app/',
            'User-Agent': user_agents[wallet_address]
        })

        # Cek skor dan rank
        response = api.get(f"{config['apiBaseUrl']}/lasso/score")
        score_data = response.json()
        print_stats(wallet_address, score_data)

        if score_data.get('remainingPlays', 0) == 0:
            print(Fore.YELLOW + f"🚫 No remaining plays for {wallet_address}. Skipping...")
            return

        signatures = []
        scores = []

        while score_data.get('remainingPlays', 0) > 0:
            print(Fore.GREEN + f'Playing Lasso for {wallet_address}...')
            play_response = api.post(f"{config['apiBaseUrl']}/lasso/play", params={'network': 'monad', 'chain_id': config['chainId']})
            play_data = play_response.json()

            if 'error' in play_data:
                print(Fore.RED + f'Error playing minigame for {wallet_address}: {play_data["error"]}')
                break

            print(Fore.GREEN + f'Getting claim signature for {wallet_address}...')
            claim_response = api.get(f"{config['apiBaseUrl']}/lasso/claim")
            claim_data = claim_response.json()
            print(Fore.GREEN + f'Claim response for {wallet_address}: {claim_data}')

            signatures.append(claim_data['signature'])
            scores.append(claim_data['score'])

            # Update remaining plays
            score_data['remainingPlays'] -= 1

            # Delay antara 10 sampai 30 detik
            delay = random.randint(10, 30)
            time.sleep(delay)

        # Setelah semua permainan selesai, lakukan Claiming MON
        if signatures and scores:
            claim_mon(wallet_address, private_key, signatures, scores)

    except Exception as error:
        print(Fore.RED + f'Error processing wallet {wallet_address}: {str(error)}')
        if hasattr(error, 'response'):
            print(Fore.RED + f'API Response for {wallet_address}: {error.response.json()}')

# Fungsi utama
def main():
    with open('pk.txt', 'r') as file:
        private_keys = file.read().splitlines()

    for private_key in private_keys:
        process_wallet(private_key)

# Fungsi untuk countdown
def countdown(seconds):
    while seconds:
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        timer = f'{hours:02d}:{mins:02d}:{secs:02d}'
        print(Fore.BLUE + f"⏳ Next run in: {timer}", end="\r")
        time.sleep(1)
        seconds -= 1

if __name__ == '__main__':
    os.system("clear" if os.name == "posix" else "cls")
    rainbow_banner()
    print(Fore.CYAN + "Starting Dusted...")
    while True:
        main()
        # Random delay antara 24 jam sampai 24 jam 77 menit
        delay = 86400 + random.randint(0, 4620)  # 86400 detik = 24 jam, 4620 detik = 77 menit
        countdown(delay)
