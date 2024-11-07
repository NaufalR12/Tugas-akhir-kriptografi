from Crypto.Cipher import AES
import base64
import hashlib
import math

# Fungsi untuk mengenkripsi teks menggunakan Scytale cipher dan AES
def super_encrypt(plaintext, scytale_key, aes_key):
    # Enkripsi menggunakan Scytale cipher
    scytale_encrypted = scytale_encrypt(plaintext, scytale_key)

    # Enkripsi menggunakan AES
    aes_encrypted = aes_encrypt(scytale_encrypted, aes_key)

    return aes_encrypted

# Fungsi untuk mendekripsi teks menggunakan Scytale cipher dan AES
def super_decrypt(ciphertext, scytale_key, aes_key):
    # Dekripsi menggunakan AES
    aes_decrypted = aes_decrypt(ciphertext, aes_key)

    # Dekripsi menggunakan Scytale cipher
    plaintext = scytale_decrypt(aes_decrypted, scytale_key)

    return plaintext

# Fungsi untuk mengenkripsi teks dengan Scytale cipher
def scytale_encrypt(plaintext, scytale_key):
    # Menambahkan padding agar panjang plaintext dapat dibagi habis dengan scytale_key
    if len(plaintext) % scytale_key != 0:
        padding_length = scytale_key - (len(plaintext) % scytale_key)
        plaintext += ' ' * padding_length
    
    # Hitung jumlah baris
    num_rows = len(plaintext) // scytale_key
    # Membuat grid untuk menyimpan hasil enkripsi
    grid = [''] * scytale_key
    for i in range(len(plaintext)):
        grid[i % scytale_key] += plaintext[i]

    # Gabungkan grid untuk menghasilkan ciphertext
    ciphertext = ''.join(grid)
    return ciphertext


# Fungsi untuk mendekripsi teks dengan Scytale cipher
def scytale_decrypt(ciphertext, scytale_key):
    # Hitung jumlah baris
    num_rows = len(ciphertext) // scytale_key
    # Tambahkan padding jika panjang ciphertext tidak dibagi habis oleh scytale_key
    if len(ciphertext) % scytale_key != 0:
        num_rows += 1
        ciphertext += ' ' * (scytale_key - len(ciphertext) % scytale_key)
    
    # Membaca ciphertext ke dalam grid dengan scytale_key sebagai jumlah kolom
    grid = [''] * num_rows
    for i in range(len(ciphertext)):
        grid[i % num_rows] += ciphertext[i]

    # Gabungkan kembali grid menjadi plaintext
    plaintext = ''.join(grid).strip()
    return plaintext


# Fungsi untuk mengenkripsi teks dengan AES (gunakan mode ECB untuk kemudahan)
def aes_encrypt(plaintext, key):
    # Pastikan key AES panjangnya 16, 24, atau 32 byte
    key = hashlib.sha256(key.encode()).digest()  # Menggunakan SHA-256 untuk menghasilkan key yang tepat panjangnya
    cipher = AES.new(key, AES.MODE_ECB)

    # Padding untuk memastikan panjang teks kelipatan 16 byte
    padding_length = 16 - (len(plaintext) % 16)
    padded_text = plaintext + chr(padding_length) * padding_length

    encrypted = cipher.encrypt(padded_text.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')

# Fungsi untuk mendekripsi teks dengan AES
def aes_decrypt(ciphertext, key):
    key = hashlib.sha256(key.encode()).digest()
    cipher = AES.new(key, AES.MODE_ECB)

    # Decode base64 dan dekripsi AES
    decrypted = cipher.decrypt(base64.b64decode(ciphertext)).decode('utf-8')

    # Menghapus padding
    padding_length = ord(decrypted[-1])
    return decrypted[:-padding_length]
