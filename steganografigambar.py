# steganografigambar.py
from PIL import Image
from stegano import lsb
import zipfile
import os

# Fungsi untuk membuat file kunci enkripsi
def generate_key_file(file_path="encryption_key.txt"):
    key = os.urandom(16).hex()  # Membuat kunci acak 16 byte dalam format heksadesimal
    with open(file_path, 'w') as f:
        f.write(key)
    return file_path, key

# Fungsi untuk mengenkripsi pesan ke dalam gambar
def encrypt_message_with_key(image_path, message, output_path, key):
    encrypted_image = lsb.hide(image_path, f"{key}:{message}")
    encrypted_image.save(output_path)
    return output_path

# Fungsi untuk mendekripsi pesan dari gambar dengan kunci
def decrypt_message_with_key(encrypted_image_path, key):
    hidden_message = lsb.reveal(encrypted_image_path)
    if hidden_message and hidden_message.startswith(f"{key}:"):
        return hidden_message[len(key) + 1:]  # Mengambil pesan tersembunyi
    else:
        return "Kunci tidak valid atau gambar rusak."

# Fungsi untuk membuat file ZIP yang berisi gambar terenkripsi dan kunci
def create_zip(image_path, key_file_path):
    zip_file_path = f"{image_path}.zip"
    with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
        zip_file.write(image_path, image_path.split('/')[-1])  # Menggunakan nama file dari path
        zip_file.write(key_file_path, key_file_path.split('/')[-1])  # Menggunakan nama file dari path
    return zip_file_path