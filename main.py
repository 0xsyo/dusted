import os
import time
import json
import random
from datetime import datetime
import requests
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account.messages import encode_defunct
from uuid import uuid4
from colorama import Fore, Style, init
from fake_useragent import UserAgent
import asyncio

# Inisialisasi colorama
init(autoreset=True)

# Konfigurasi
config = {
    'rpcUrl': 'https://testnet-rpc2.monad.xyz/52227f026fa8fac9e2014c58fbf5643369b3bfc6',
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

# Definisikan room_id
room_id = 35490697943453696  # Contoh room_id, sesuaikan dengan nilai yang benar

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
        print(Fore.YELLOW + f"⏳ Checking MON Rewards {wallet_address}")

# Fungsi untuk mengirim data ke Vercel Insights
async def send_vercel_insights(user_agent, referer):
    url = "https://www.dusted.app/_vercel/insights/view"
    payload = {
        "o": referer,
        "sv": "0.1.2",
        "sdkn": "@vercel/analytics/react",
        "sdkv": "1.5.0",
        "ts": int(time.time() * 1000)
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': user_agent,
        'Referer': referer,
        'Origin': 'https://www.dusted.app'
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(Fore.GREEN + "Vercel Insights data sent successfully.")
    else:
        print(Fore.RED + f"Failed to send Vercel Insights data: {response.status_code} - {response.text}")

# Fungsi untuk mendapatkan status notifikasi
async def get_notifications_status(api):
    try:
        response = api.get(f"{config['apiBaseUrl']}/notifications/status")
        if response.status_code == 200:
            print(Fore.GREEN + "Notifications status retrieved successfully.")
            return response.json()
        else:
            print(Fore.RED + f"Failed to get notifications status: {response.status_code} - {response.text}")
            return None
    except Exception as error:
        print(Fore.RED + f'Error getting notifications status: {str(error)}')
        return None

# Fungsi untuk mendapatkan pesan room
async def get_room_messages(api):
    try:
        response = api.get(f"{config['apiBaseUrl']}/rooms/monad-testnet/native/messages")
        if response.status_code == 200:
            print(Fore.GREEN + "Room messages retrieved successfully.")
            return response.json()
        else:
            print(Fore.RED + f"Failed to get room messages: {response.status_code} - {response.text}")
            return None
    except Exception as error:
        print(Fore.RED + f'Error getting room messages: {str(error)}')
        return None

# Fungsi untuk mendapatkan Bearer Token
async def get_bearer_token(wallet_address, private_key, user_agent):
    try:
        # Generate nonce sebagai UUID
        nonce = str(uuid4())

        # Format pesan sesuai dengan yang diharapkan oleh server
        message = (
            f"www.dusted.app wants you to sign in with your Ethereum account:\n{wallet_address}\n\n"
            f"I am proving ownership of the Ethereum account {wallet_address}.\n\n"
            f"URI: https://www.dusted.app\n"
            f"Version: 1\n"
            f"Chain ID: 1\n"
            f"Nonce: {nonce}\n"
            f"Issued At: {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z"
        )

        # Encode pesan dan tanda tangani
        encoded_message = encode_defunct(text=message)
        web3 = Web3(Web3.HTTPProvider(config['rpcUrl']))
        signed_message = web3.eth.account.sign_message(encoded_message, private_key=private_key)

        # URL endpoint untuk sign-in
        sign_in_url = f"{config['apiBaseUrl']}/signature/evm/{wallet_address}/sign"

        # Payload untuk request
        payload = {
            "message": message,
            "signature": signed_message.signature.hex(),
            "provider": "metamask",
            "chainId": "0x279f"  # Sesuaikan dengan chain ID yang diharapkan server
        }

        # Header untuk request
        headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Origin': 'https://www.dusted.app',
            'Referer': 'https://www.dusted.app/',
            'User-Agent': user_agent,
            'priority': 'u=1, i',  # Tambahkan header priority
            'sec-gpc': '1',  # Tambahkan header sec-gpc
        }

        # Kirim request ke API
        response = requests.post(sign_in_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception jika status code bukan 2xx

        # Ambil token dari response
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

# Fungsi reusable untuk melakukan Claiming MON - PERBAIKAN DISINI
async def claim_mon(wallet_address, private_key, signature, score):
    try:
        web3 = Web3(Web3.HTTPProvider(config['rpcUrl']))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        wallet = web3.eth.account.from_key(private_key)
        
        # Pastikan alamat kontrak menggunakan checksum address
        contract_address = web3.to_checksum_address(config['contractAddress'])
        contract = web3.eth.contract(address=contract_address, abi=ABI)

        print(Fore.GREEN + f'Claiming MON for {wallet_address} with Score {score}...')
        print(Fore.YELLOW + f'Using signature: {signature}')

        # Format signature yang benar 
        # Hapus 0x prefix jika ada
        if isinstance(signature, str):
            if signature.startswith('0x'):
                signature_bytes = bytes.fromhex(signature[2:])
            else:
                signature_bytes = bytes.fromhex(signature)
        else:
            signature_bytes = signature

        # Pastikan score dalam format integer
        if isinstance(score, str):
            score = int(score)

        # Dapatkan harga gas (Gwei) dari jaringan
        gas_price = get_gas_price(web3)
        if not gas_price:
            gas_price = web3.to_wei('5', 'gwei')  # Fallback ke 5 Gwei jika gagal mendapatkan harga gas

        # Tambahkan buffer gas limit
        gas_limit = int(200000)  # Tingkatkan gas limit untuk menghindari out of gas

        # Debug print
        print(Fore.YELLOW + f'Contract Address: {contract_address}')
        print(Fore.YELLOW + f'Wallet Address: {wallet.address}')
        print(Fore.YELLOW + f'Score (totalPoints): {score}')
        print(Fore.YELLOW + f'Signature (bytes): {signature_bytes.hex()}')

        # Build dan kirim transaksi
        nonce = web3.eth.get_transaction_count(wallet.address)
        
        tx = contract.functions.claim(
            score,
            signature_bytes
        ).build_transaction({
            'from': wallet.address,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': config['chainId']
        })
        
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(Fore.GREEN + f'Transaction submitted for {wallet_address}: {tx_hash.hex()}')

        # Menunggu konfirmasi transaksi
        try:
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)  # Timeout lebih lama
            if receipt.status == 1:
                print(Fore.GREEN + f'✅ Transaction confirmed in block for {wallet_address}: {receipt["blockNumber"]}')
            else:
                print(Fore.RED + f'❌ Transaction failed for {wallet_address}')
        except Exception as error:
            print(Fore.RED + f'❌ Error waiting for transaction receipt for {wallet_address}: {str(error)}')

    except Exception as error:
        print(Fore.RED + f'Error claiming MON for {wallet_address}: {str(error)}')
        import traceback
        traceback.print_exc()

# Fungsi untuk melakukan Claim Referral Code
async def claim_referral_code(api, wallet_address):
    try:
        # Baca ref code dari file refcodes.txt
        with open('refcodes.txt', 'r') as file:
            ref_codes = file.read().splitlines()

        if not ref_codes:
            print(Fore.RED + f'No referral codes found in refcodes.txt for {wallet_address}')
            return False

        ref_code = ref_codes[0]  # Ambil ref code pertama
        claim_url = f"{config['apiBaseUrl']}/referralcode/claim"

        # Payload dengan wallet ID (jika diperlukan)
        payload = {
            "referralCode": ref_code,
            "walletId": wallet_address  # Sertakan wallet ID jika diperlukan
        }

        # Header dengan Bearer Token (pastikan tidak ada duplikasi kata "Bearer")
        headers = {
            'Content-Type': 'application/json',
            'Authorization': api.headers["Authorization"],  # Gunakan token yang sudah ada tanpa menambahkan "Bearer" lagi
            'User-Agent': api.headers['User-Agent']
        }

        # Kirim request POST
        response = requests.post(claim_url, json=payload, headers=headers)
        response.raise_for_status()  # Akan raise exception jika status code bukan 2xx

        print(Fore.GREEN + f'Process Claims Code {ref_code}')
        return True
    except requests.exceptions.HTTPError as error:
        print(Fore.RED + f'Error claiming referral code for {wallet_address}: {error.response.status_code} - {error.response.text}')
        return False
    except Exception as error:
        print(Fore.RED + f'Error claiming referral code for {wallet_address}: {str(error)}')
        return False

# Fungsi untuk melakukan Join Room
async def join_room(api, wallet_id, wallet_address, room_id):
    try:
        join_url = f"{config['apiBaseUrl']}/rooms/monad-testnet/native/subscribe"

        # Payload dengan wallet ID dan wallet address
        payload = {
            "wallet_id": wallet_id,
            "wallet_address": wallet_address,
            "room_id": room_id  # Gunakan room_id yang diterima sebagai parameter
        }

        # Header dengan Bearer Token dan header tambahan
        headers = {
            'Content-Type': 'application/json',
            'Authorization': api.headers["Authorization"],  # Gunakan token yang sudah ada tanpa menambahkan "Bearer" lagi
            'User-Agent': api.headers['User-Agent'],
            'Accept': '*/*',
            'Accept-Language': 'id-ID,id;q=0.6',
            'Origin': 'https://www.dusted.app',
            'Referer': 'https://www.dusted.app/',
            'Sec-CH-UA': '"Not(A:Brand";v="99", "Brave";v="133", "Chromium";v="133"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Linux"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-GPC': '1'
        }

        # Kirim request POST
        response = requests.post(join_url, json=payload, headers=headers)
        response.raise_for_status()  # Akan raise exception jika status code bukan 2xx

        print(Fore.GREEN + f'Successfully joined room for {wallet_id}')
        return True
    except requests.exceptions.HTTPError as error:
        print(Fore.RED + f'Error joining room for {wallet_id}: {error.response.status_code} - {error.response.text}')
        return False
    except Exception as error:
        print(Fore.RED + f'Error joining room for {wallet_id}: {str(error)}')
        return False

# Fungsi untuk memeriksa apakah wallet sudah terdaftar di room
async def is_wallet_registered_in_room(api, wallet_address):
    try:
        response = api.get(f"{config['apiBaseUrl']}/rooms/monad-testnet/native/messages")
        if response.status_code == 200:
            return True  # Wallet sudah terdaftar di room
        elif response.status_code == 403 and response.json().get('error') == 'NOT_ROOM_MEMBER':
            return False  # Wallet belum terdaftar di room
        else:
            print(Fore.RED + f'Unexpected response for {wallet_address}: {response.status_code} - {response.text}')
            return False
    except Exception as error:
        print(Fore.RED + f'Error checking room registration for {wallet_address}: {str(error)}')
        return False

# Fungsi untuk memproses setiap wallet
async def process_wallet(private_key):
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
                bearer_token = await get_bearer_token(wallet_address, private_key, user_agents[wallet_address])
                if bearer_token:
                    tokens[wallet_address] = bearer_token
                    save_json(tokens_file, tokens)
        else:
            bearer_token = await get_bearer_token(wallet_address, private_key, user_agents[wallet_address])
            if bearer_token:
                tokens[wallet_address] = bearer_token
                save_json(tokens_file, tokens)

        if not bearer_token:
            raise ValueError("Failed to retrieve Bearer Token")

        # Simpan header untuk digunakan di proses selanjutnya
        api = requests.Session()
        api.headers.update({
            'Authorization': f'Bearer {bearer_token}',
            'Accept': '*/*',
            'Origin': 'https://www.dusted.app',
            'Referer': 'https://www.dusted.app/',
            'User-Agent': user_agents[wallet_address]
        })

        # Kirim data ke Vercel Insights
        await send_vercel_insights(user_agents[wallet_address], 'https://www.dusted.app/')

        # Dapatkan wallet_id secara dinamis
        wallet_id = await get_wallet_id(wallet_address, bearer_token)
        if not wallet_id:
            print(Fore.RED + f'Failed to get wallet ID for {wallet_address}. Skipping further actions.')
            return

        # Lanjutkan ke proses selanjutnya (claim referral code, join room, dll.)
        await process_wallet_actions(api, wallet_id, wallet_address, private_key)

    except Exception as error:
        print(Fore.RED + f'Error processing wallet {wallet_address}: {str(error)}')
        if hasattr(error, 'response') and hasattr(error.response, 'json'):
            try:
                print(Fore.RED + f'API Response for {wallet_address}: {error.response.json()}')
            except:
                print(Fore.RED + f'API Response for {wallet_address}: {error.response.text}')

# Fungsi untuk mendapatkan wallet_id dari endpoint /users/@me
async def get_wallet_id(wallet_address, bearer_token):
    try:
        # Gunakan endpoint yang benar untuk mendapatkan wallet_id
        url = f"{config['apiBaseUrl']}/users/@me"
        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Origin': 'https://www.dusted.app',
            'Referer': 'https://www.dusted.app/',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            'priority': 'u=1, i',
            'sec-gpc': '1'
        }

        # Kirim request GET ke API
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise exception jika status code bukan 2xx

        # Ambil wallet_id dari respons API
        user_data = response.json()
        wallet_id = user_data.get('wallet', {}).get('wallet_id')

        if not wallet_id:
            raise ValueError("Wallet ID not found in response")

        return wallet_id
    except requests.exceptions.HTTPError as error:
        print(Fore.RED + f'Error getting wallet ID for {wallet_address}: {error.response.status_code} - {error.response.text}')
        return None
    except Exception as error:
        print(Fore.RED + f'Error getting wallet ID for {wallet_address}: {str(error)}')
        return None

# Fungsi untuk memproses semua aksi wallet (claim referral code, join room, play lasso, claim MON)
async def process_wallet_actions(api, wallet_id, wallet_address, private_key):
    try:
        # Cek apakah wallet sudah terdaftar di room
        if not await is_wallet_registered_in_room(api, wallet_address):
            print(Fore.YELLOW + f'Wallet {wallet_address} not registered. \nProceeding to claim referral code...')
            
            # Coba claim referral code terlebih dahulu
            if await claim_referral_code(api, wallet_address):
                print(Fore.GREEN + f'Successfully claimed referral code for {wallet_address}. \nProceeding to join room...')
                
                # Setelah claim referral code berhasil, coba join room
                if await join_room(api, wallet_id, wallet_address, room_id):
                    print(Fore.GREEN + f'Successfully joined room for {wallet_address}')
                else:
                    print(Fore.RED + f'Failed to join room for {wallet_address}. Skipping further actions.')
                    return
            else:
                print(Fore.RED + f'Failed to claim referral code for {wallet_address}. Skipping further actions.')
                return

        # Lanjutkan ke proses play lasso seperti sebelumnya
        response = api.get(f"{config['apiBaseUrl']}/lasso/score")
        score_data = response.json()
        print_stats(wallet_address, score_data)

        if score_data.get('remainingPlays', 0) == 0:
            # Langsung coba claim meskipun remainingPlays = 0
            claim_response = api.get(f"{config['apiBaseUrl']}/lasso/claim")
            claim_data = claim_response.json()
            print(Fore.GREEN + f'Claim response for {wallet_address}: {json.dumps(claim_data, indent=2)}')

            # Perbaikan: Pastikan signature dan score ada dan valid
            if isinstance(claim_data, dict) and 'signature' in claim_data and 'score' in claim_data:
                # Jika signature bukan string "Claim not available" dan score bukan 0
                if claim_data['signature'] != 'Claim not available' and claim_data['score'] > 0:
                    await claim_mon(wallet_address, private_key, claim_data['signature'], claim_data['score'])
                else:
                    print(Fore.YELLOW + f'No claim available for {wallet_address} at this time')
            else:
                print(Fore.YELLOW + f'No claim available for {wallet_address} at this time')  
            return

        # LOGIKA BARU: Habiskan semua remainingPlays terlebih dahulu
        play_count = 0
        max_plays = score_data.get('remainingPlays', 0)

        print(Fore.CYAN + f'Akan melakukan {max_plays} permainan untuk {wallet_address}...')

        while play_count < max_plays:
            play_count += 1
            print(Fore.GREEN + f'Permainan ke-{play_count}/{max_plays} untuk {wallet_address}...')

            # Mainkan Lasso
            play_response = api.post(f"{config['apiBaseUrl']}/lasso/play", params={'network': 'monad', 'chain_id': config['chainId']})
            play_data = play_response.json()
            print(Fore.GREEN + f'Play response for {wallet_address} (Game #{play_count}): {json.dumps(play_data, indent=2)}')

            if 'error' in play_data:
                print(Fore.RED + f'Error playing minigame for {wallet_address}: {play_data["error"]}')
                break

            # Tambahkan delay antar permainan
            if play_count < max_plays:
                delay = random.randint(2, 7)  # Sedikit lebih lama
                print(Fore.CYAN + f'Waiting {delay} seconds before next play for {wallet_address}...')
                await asyncio.sleep(delay)

        # Setelah semua permainan selesai, coba claim
        print(Fore.GREEN + f'All games completed for {wallet_address}. Checking for claim availability...')
        # Tambahkan delay yang lebih panjang sebelum mencoba claim pertama kali
        await asyncio.sleep(15)  # Tunggu 15 detik (bukan 5) untuk memastikan score terupdate

        # Refresh status skor terbaru sebelum claim
        try:
            refresh_response = api.get(f"{config['apiBaseUrl']}/lasso/score")
            refreshed_data = refresh_response.json()
            print(Fore.CYAN + "Updated stats before claim:")
            print_stats(wallet_address, refreshed_data)
        except Exception as e:
            print(Fore.RED + f'Failed to refresh player stats: {str(e)}')

        max_claim_attempts = 5  # Tingkatkan jumlah percobaan
        for attempt in range(max_claim_attempts):
            print(Fore.GREEN + f'Getting claim signature for {wallet_address} (Attempt {attempt+1}/{max_claim_attempts})...')
            
            # Tambahkan parameter timestamp ke request claim untuk menghindari caching
            claim_response = api.get(f"{config['apiBaseUrl']}/lasso/claim", 
                                    params={'timestamp': int(time.time())})
            
            try:
                claim_data = claim_response.json()
                print(Fore.GREEN + f'Claim response for {wallet_address}: {json.dumps(claim_data, indent=2)}')

                # Perbaikan: Pastikan signature dan score ada dan valid
                if isinstance(claim_data, dict) and 'signature' in claim_data and 'score' in claim_data:
                    if claim_data['signature'] != 'Claim not available' and claim_data['score'] > 0:
                        await claim_mon(wallet_address, private_key, claim_data['signature'], claim_data['score'])
                        break
                    else:
                        print(Fore.YELLOW + f'Claim not available for {wallet_address}. Waiting before retry...')
                elif isinstance(claim_data, dict) and 'message' in claim_data and claim_data['message'] == 'Not available to claim':
                    print(Fore.YELLOW + f'Not available to claim for {wallet_address}. Waiting before retry...')
                else:
                    print(Fore.YELLOW + f'Unexpected claim response for {wallet_address}. Waiting before retry...')
                
                # Tunggu lebih lama antara percobaan (semakin lama untuk setiap percobaan)
                wait_time = 10 + (attempt * 5)  # 10s, 15s, 20s, 25s, 30s
                print(Fore.CYAN + f'Waiting {wait_time} seconds before next attempt...')
                await asyncio.sleep(wait_time)
                
                # Refresh skor sebelum mencoba lagi
                if attempt < max_claim_attempts - 1:
                    try:
                        refresh_response = api.get(f"{config['apiBaseUrl']}/lasso/score")
                        refreshed_data = refresh_response.json()
                        print(Fore.CYAN + "Refreshed stats before next attempt:")
                        print_stats(wallet_address, refreshed_data)
                    except Exception as e:
                        print(Fore.RED + f'Failed to refresh player stats: {str(e)}')
                
            except Exception as e:
                print(Fore.RED + f'Error parsing claim response: {str(e)}')
                await asyncio.sleep(5)
        else:
            print(Fore.RED + f'Failed to get claim after {max_claim_attempts} attempts for {wallet_address}.')

    except Exception as error:
        print(Fore.RED + f'Error processing wallet {wallet_address}: {str(error)}')
        if hasattr(error, 'response') and hasattr(error.response, 'json'):
            try:
                print(Fore.RED + f'API Response for {wallet_address}: {error.response.json()}')
            except:
                print(Fore.RED + f'API Response for {wallet_address}: {error.response.text}')

# Fungsi utama
async def main():
    try:
        with open('pk.txt', 'r') as file:
            private_keys = file.read().splitlines()

        for private_key in private_keys:
            if private_key.strip():  # Hanya proses key yang tidak kosong
                await process_wallet(private_key)
                # Delay antara proses wallet
                delay = random.randint(1, 7)
                print(Fore.CYAN + f'Waiting {delay} seconds before next wallet...')
                await asyncio.sleep(delay)
                print(Fore.CYAN + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    except Exception as error:
        print(Fore.RED + f'Error in main function: {str(error)}')

# Fungsi untuk countdown
async def countdown(seconds):
    while seconds:
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        timer = f'{hours:02d}:{mins:02d}:{secs:02d}'
        print(Fore.BLUE + f"⏳ Next run in: {timer}", end="\r")
        await asyncio.sleep(1)
        seconds -= 1

if __name__ == '__main__':
    try:
        os.system("clear" if os.name == "posix" else "cls")
        rainbow_banner()
        print(Fore.CYAN + "Starting Dusted...")
        loop = asyncio.get_event_loop()
        while True:
            loop.run_until_complete(main())
            # Random delay antara 24 jam sampai 24 jam 77 menit
            delay = 86400 + random.randint(0, 4620)  # 86400 detik = 24 jam, 4620 detik = 77 menit
            print(Fore.CYAN + f'Completed run. Next run in approximately {delay//3600} hours.')
            loop.run_until_complete(countdown(delay))
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nProgram stopped by user.")
    except Exception as error:
        print(Fore.RED + f'Unexpected error: {str(error)}')
