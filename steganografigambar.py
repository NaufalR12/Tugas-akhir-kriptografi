from PIL import Image
from stegano import lsb
import zipfile
import os
from io import BytesIO

# Fungsi untuk membuat file kunci enkripsi
def generate_key_file(file_path="encryption_key.txt"):
    key = os.urandom(16).hex()  # Membuat kunci acak 16 byte dalam format heksadesimal
    with open(file_path, 'w') as f:
        f.write(key)
    return file_path, key

# Fungsi untuk mengenkripsi pesan ke dalam gambar
def encrypt_message_with_key(image_buffer, message, key):
    from PIL import Image
    from stegano import lsb

    # Membuka gambar dari buffer
    image = Image.open(image_buffer)

    # Mengenkripsi pesan
    encrypted_image = lsb.hide(image, f"{key}:{message}")

    return encrypted_image


# Fungsi untuk mendekripsi pesan dari gambar dengan kunci
def decrypt_message_with_key(encrypted_image_buffer, key):
    from PIL import Image
    from stegano import lsb

    # Membuka gambar dari buffer
    encrypted_image = Image.open(encrypted_image_buffer)

    # Mendekripsi pesan
    hidden_message = lsb.reveal(encrypted_image)
    if hidden_message and hidden_message.startswith(f"{key}:"):
        return hidden_message[len(key) + 1:]  # Mengambil pesan tersembunyi
    else:
        return "Kunci tidak valid atau gambar rusak."


# Fungsi untuk membuat file ZIP yang berisi gambar terenkripsi dan kunci
def create_zip_stegano_buffer(encrypted_image_buffer, key_file_path):
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        # Menambahkan gambar terenkripsi ke ZIP
        zip_file.writestr("encrypted_image.png", encrypted_image_buffer.getvalue())

        # Menambahkan file kunci ke ZIP
        with open(key_file_path, "r") as key_file:
            zip_file.writestr("encryption_key.txt", key_file.read())

    zip_buffer.seek(0)
    zip_file_path = "encrypted_image_and_key.zip"
    
    # Simpan ZIP ke file sementara untuk unduhan (hanya untuk Streamlit)
    with open(zip_file_path, "wb") as f:
        f.write(zip_buffer.getvalue())

    return zip_file_path

