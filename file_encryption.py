from cryptography.fernet import Fernet
import os
import zipfile

# Fungsi untuk menghasilkan kunci Fernet
def generate_key():
    return Fernet.generate_key()

# Fungsi untuk menyimpan kunci ke file
def save_key(key, key_file):
    with open(key_file, 'wb') as file:
        file.write(key)

# Fungsi untuk memuat kunci dari file
def load_key(key_file):
    with open(key_file, 'rb') as file:
        return file.read()

# Fungsi untuk enkripsi file
def encrypt_file(file_path, key):
    fernet = Fernet(key)
    
    with open(file_path, 'rb') as file:
        plaintext = file.read()
    
    ciphertext = fernet.encrypt(plaintext)
    
    # Menyimpan hasil enkripsi ke file yang sama
    with open(file_path, 'wb') as file:  # Menimpa file asli dengan file terenkripsi
        file.write(ciphertext)
    
    return file_path  # Mengembalikan nama file yang sama

# Fungsi untuk membuat file ZIP yang berisi file terenkripsi dan kunci
def create_zip(encrypted_file_path, key):
    zip_file_path = f"{encrypted_file_path}_output.zip"
    with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
        zip_file.write(encrypted_file_path, os.path.basename(encrypted_file_path))
        key_file_path = "secret.key"
        save_key(key, key_file_path)  # Simpan kunci ke file
        zip_file.write(key_file_path, os.path.basename(key_file_path))
    
    return zip_file_path

# Fungsi untuk dekripsi file
def decrypt_file(encrypted_file_path, key):
    fernet = Fernet(key)
    
    with open(encrypted_file_path, 'rb') as file:
        ciphertext = file.read()
    
    decrypted = fernet.decrypt(ciphertext)
    
    # Menyimpan hasil dekripsi ke file yang sama
    with open(encrypted_file_path, 'wb') as file:  # Menimpa file terenkripsi dengan file hasil dekripsi
        file.write(decrypted)
    
    return encrypted_file_path  # Mengembalikan nama file yang sama
