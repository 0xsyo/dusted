# Dusted Bot

## Description

Dusted Bot is an automated tool designed to interact with the Dusted app's API to play the Lasso game and claim MON tokens. This bot is perfect for users who want to automate their interactions with the Dusted app, ensuring they maximize their plays and claims efficiently. The bot leverages various Python modules to handle HTTP requests, MON Testnet transactions, and more.

**Key Features:**
- Automated interaction with the Dusted app's API
- Plays the Lasso game and claims MON tokens
- Handles MON Testnet transactions
- Customizable user-agent for better anonymity
- Rainbow banner for a visually pleasing start-up

## How to Use

### Step-by-step Guide

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/0xsyo/dusted.git
   cd dusted
   ```

2. **Set Up Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `pk.txt` File:**
   - Add your private keys in the `pk.txt` file, one per line.

5. **Run the Bot:**
   - On Linux/macOS:
     ```bash
     python3 main.py
     ```
   - On Windows:
     ```bash
     python main.py
     ```

## Risks and Considerations

- **Security Risks:** Storing private keys in a text file poses a security risk. Ensure that the `pk.txt` file is stored securely and not shared.
- **API Rate Limits:** Be aware of the rate limits imposed by the Dusted app's API to prevent being blocked.
- **MON Transaction Costs:** Make sure to have enough MON in your wallet to cover gas fees for transactions.


---


## Deskripsi

Dusted Bot adalah alat otomatis yang dirancang untuk berinteraksi dengan API aplikasi Dusted untuk memainkan game Lasso dan mengklaim token MON. Bot ini sangat cocok untuk pengguna yang ingin mengotomatiskan interaksi mereka dengan aplikasi Dusted, memastikan mereka memaksimalkan permainan dan klaim mereka dengan efisien. Bot ini memanfaatkan berbagai modul Python untuk menangani permintaan HTTP, transaksi MON Testnet, dan lainnya.

**Fitur Utama:**
- Interaksi otomatis dengan API aplikasi Dusted
- Memainkan game Lasso dan mengklaim token MON
- Menangani transaksi MON Testnet
- User-agent yang dapat disesuaikan untuk anonimitas yang lebih baik
- Banner pelangi untuk startup yang menarik secara visual

## Cara Menggunakan

### Panduan Langkah-demi-Langkah

1. **Clone Repositori:**
   ```bash
   git clone https://github.com/0xsyo/dusted.git
   cd dusted
   ```

2. **Siapkan Lingkungan Virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Di Windows gunakan `venv\Scripts\activate`
   ```

3. **Instalasi Dependensi:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Buat File `pk.txt`:**
   - Tambahkan private key Anda di file `pk.txt`, satu per baris.

5. **Jalankan Bot:**
   - Di Linux/macOS:
     ```bash
     python3 main.py
     ```
   - Di Windows:
     ```bash
     python main.py
     ```

## Risiko dan Pertimbangan

- **Risiko Keamanan:** Menyimpan private key dalam file teks merupakan risiko keamanan. Pastikan file `pk.txt` disimpan dengan aman dan tidak dibagikan.
- **Batasan API:** Perhatikan batasan jumlah permintaan yang diberlakukan oleh API aplikasi Dusted untuk menghindari pemblokiran.
- **Biaya Transaksi MON:** Pastikan memiliki cukup MON di dompet Anda untuk menutupi biaya gas untuk transaksi.

