import hashlib
import sqlite3
import streamlit as st
import re
import os
from enkripsidekripsitext import super_encrypt, super_decrypt
from file_encryption import encrypt_file, decrypt_file, generate_key, save_key, load_key, create_zip
from steganografigambar import encrypt_message_with_key, decrypt_message_with_key, generate_key_file, create_zip

# Fungsi untuk meng-hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Fungsi untuk membuat koneksi ke database
def create_connection():
    conn = sqlite3.connect('users.db')
    return conn

# Fungsi untuk membuat tabel pengguna dan log enkripsi/dekripsi
def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS encryption_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        action TEXT,
                        plaintext TEXT,
                        ciphertext TEXT,
                        scytale_key INTEGER,
                        aes_key TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS file_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        action TEXT,
                        file_name TEXT,
                        encrypted_file TEXT,
                        decrypted_file TEXT,
                        key_file TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS gambar_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        action TEXT,
                        image_name TEXT,
                        encrypted_image TEXT,
                        decrypted_message TEXT,
                        key_file TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()

# Fungsi untuk menambahkan pengguna ke database
def add_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hash_password(password)))
    conn.commit()
    conn.close()

# Fungsi untuk memeriksa pengguna
def check_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user

# Fungsi untuk menyimpan log enkripsi/dekripsi
def save_encryption_log(user_id, action, plaintext, ciphertext, scytale_key, aes_key):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO encryption_logs (user_id, action, plaintext, ciphertext, scytale_key, aes_key)
                      VALUES (?, ?, ?, ?, ?, ?)''', (user_id, action, plaintext, ciphertext, scytale_key, aes_key))
    conn.commit()
    conn.close()

# Fungsi untuk menyimpan log enkripsi/dekripsi file
def save_file_log(user_id, action, file_name, encrypted_file, decrypted_file, key_file):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO file_logs (user_id, action, file_name, encrypted_file, decrypted_file, key_file)
                      VALUES (?, ?, ?, ?, ?, ?)''', (user_id, action, file_name, encrypted_file, decrypted_file, key_file))
    conn.commit()
    conn.close()

# Fungsi untuk menyimpan log enkripsi/dekripsi gambar
def save_image_log(user_id, action, image_name, encrypted_image, decrypted_message, key_file):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO gambar_logs (user_id, action, image_name, encrypted_image, decrypted_message, key_file)
                      VALUES (?, ?, ?, ?, ?, ?)''', (user_id, action, image_name, encrypted_image, decrypted_message, key_file))
    conn.commit()
    conn.close()




# Fungsi untuk memvalidasi password
def validate_password(password):
    errors = []
    if len(password) < 8:
        errors.append("Password harus minimal 8 karakter.")
    if not re.search(r"[a-z]", password):
        errors.append("Password harus mengandung huruf kecil.")
    if not re.search(r"[A-Z]", password):
        errors.append("Password harus mengandung huruf besar.")
    if not re.search(r"[^a-zA-Z]", password):
        errors.append("Password harus mengandung karakter non-alfabet.")
    return errors

# Fungsi untuk memeriksa apakah ada baris kosong
# Fungsi untuk memeriksa apakah ada dua baris kosong berturut-turut
def validate_no_empty_lines(plaintext):
    lines = plaintext.split("\n")
    # Memeriksa apakah ada dua atau lebih baris kosong berturut-turut
    for i in range(1, len(lines)):
        if lines[i].strip() == "" and lines[i-1].strip() == "":
            return False  # Ada dua baris kosong berturut-turut
    return True  # Tidak ada dua baris kosong berturut-turut



# Membuat tabel jika belum ada
create_tables()

# Streamlit UI
st.title("Aplikasi Kriptografi")

# Menggunakan session_state untuk menyimpan halaman dan user_id aktif
if 'page' not in st.session_state:
    st.session_state.page = "Login"
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Menggunakan st.empty() untuk menghapus elemen UI sebelumnya
placeholder = st.empty()

# Navigasi antar halaman
if st.session_state.page == "Login":
    with placeholder.container():
        st.subheader("Halaman Login")
        username = st.text_input("Masukkan username:")
        password = st.text_input("Masukkan password:", type="password")

        if st.button("Login"):
            if not username or not password:
                st.error("Username dan password tidak boleh kosong.")
            else:
                user = check_user(username, password)
                if user:
                    st.session_state.user_id = user[0]  # Menyimpan user_id ke dalam session
                    st.session_state.page = "Menu"  # Mengubah halaman ke "Menu"
                    st.experimental_rerun()  # Memperbarui tampilan
                else:
                    st.error("Username atau password salah.")

        if st.button("Buat Akun"):
            st.session_state.page = "Daftar"  # Mengubah halaman ke "Daftar"
            st.experimental_rerun()  # Memperbarui tampilan

elif st.session_state.page == "Daftar":
    with placeholder.container():
        st.subheader("Halaman Pendaftaran")
        new_username = st.text_input("Masukkan username baru:")
        new_password = st.text_input("Masukkan password baru:", type="password")

        if new_password:
            validation_errors = validate_password(new_password)
            if validation_errors:
                for error in validation_errors:
                    st.warning(error)

        if st.button("Daftar"):
            if not new_username or not new_password:
                st.error("Username dan password tidak boleh kosong.")
            elif validation_errors:
                st.error("Perbaiki kesalahan di atas sebelum mendaftar.")
            else:
                try:
                    add_user(new_username, new_password)
                    st.success("Pengguna berhasil didaftarkan!")
                except sqlite3.IntegrityError:
                    st.error("Username sudah ada. Silakan pilih username lain.")

        if st.button("Sudah Punya Akun"):
            st.session_state.page = "Login"
            st.experimental_rerun()

elif st.session_state.page == "Menu":
    with placeholder.container():
        st.subheader("Halaman Menu")
        st.write("Pilih opsi:")

        option = st.selectbox("Pilih:", ["Enkripsi", "Dekripsi"])

        if option == "Enkripsi":
            st.write("Pilih jenis data yang ingin dienkripsi:")
            data_type = st.selectbox("Pilih:", ["Teks", "File", "Gambar"])
            if data_type == "Teks":
                text_to_encrypt = st.text_area("Masukkan teks:")
                scytale_key = st.number_input("Masukkan kunci Scytale (angka):", min_value=1, value=5)
                aes_key = st.text_input("Masukkan kunci AES:")
                if st.button("Enkripsi Teks"):
                    if not text_to_encrypt or not aes_key:
                        st.error("Teks dan kunci AES tidak boleh kosong.")
                    elif not validate_no_empty_lines(text_to_encrypt):  # Validasi baris kosong
                        st.error("Teks tidak boleh mengandung dua baris kosong berturut-turut.")
                    else:
                        text_to_encrypt = text_to_encrypt.replace("\n\n", "\n")
                        encrypted_text = super_encrypt(text_to_encrypt, scytale_key, aes_key)
                        st.success("Teks berhasil dienkripsi!")
                        st.text_area("Teks yang dienkripsi:", value=encrypted_text, height=200)
                        # Simpan log enkripsi
                        save_encryption_log(st.session_state.user_id, "enkripsi", text_to_encrypt, encrypted_text, scytale_key, aes_key)
            elif data_type == "File":
                uploaded_file = st.file_uploader("Pilih file untuk dienkripsi", type=["txt", "pdf", "jpg", "png", "gif", "mp3", "mp4", "zip", "rar", "*"])
                if st.button("Enkripsi File"):
                    if uploaded_file is not None:
                        # Simpan file sementara
                        with open(uploaded_file.name, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        # Menghasilkan dan menyimpan kunci
                        key = generate_key()
                        # Enkripsi file
                        encrypted_file_path = encrypt_file(uploaded_file.name, key)
                        # Buat file ZIP yang berisi file terenkripsi dan kunci
                        zip_file_path = create_zip(encrypted_file_path, key)
                        st.success("File berhasil dienkripsi dan disimpan dalam ZIP!")

                        # Menyediakan tombol unduh untuk file ZIP
                        with open(zip_file_path, "rb") as f:
                            st.download_button(
                                label="Download File ZIP",
                                data=f,
                                file_name=zip_file_path.split("/")[-1],
                                mime="application/zip"
                            )
                    else:
                        st.error("Silakan pilih file.")
            elif data_type == "Gambar":
                
                uploaded_image = st.file_uploader("Pilih gambar", type=["png", "jpg", "jpeg"])
                message = st.text_input("Masukkan pesan yang ingin disembunyikan")

                if uploaded_image:
                    # Menyimpan gambar yang diunggah di session state
                    st.session_state["uploaded_image"] = uploaded_image

                if st.button("Enkripsi Gambar"):
                    if st.session_state["uploaded_image"] and message:
                        image_path = f"temp_input.{uploaded_image.type.split('/')[-1]}"
                        with open(image_path, "wb") as f:
                            f.write(st.session_state["uploaded_image"].getbuffer())

                        key_file_path, key = generate_key_file()
                        st.session_state["key_file_path"] = key_file_path

                        output_path = f"encrypted_image.{uploaded_image.type.split('/')[-1]}"
                        encrypted_image_path = encrypt_message_with_key(image_path, message, output_path, key)
                        st.session_state["encrypted_image_path"] = encrypted_image_path

                        st.success("Gambar berhasil dienkripsi!")

                        # Save the log into the database
                        save_image_log(st.session_state.user_id, "enkripsi", uploaded_image.name, encrypted_image_path, None, key_file_path)

                        # Buat file ZIP yang berisi gambar terenkripsi dan kunci
                        zip_file_path = create_zip(encrypted_image_path, key_file_path)

                        # Menyediakan tombol unduh untuk file ZIP
                        with open(zip_file_path, "rb") as zip_file:
                            st.download_button("Download Gambar dan Kunci dalam ZIP", data=zip_file, file_name=zip_file_path.split('/')[-1])
        elif option == "Dekripsi":
            st.write("Pilih jenis data yang ingin didekripsi:")
            data_type = st.selectbox("Pilih:", ["Teks", "File", "Gambar"])
            if data_type == "Teks":
                text_to_decrypt = st.text_area("Masukkan teks:")
                scytale_key = st.number_input("Masukkan kunci Scytale (angka):", min_value=1, value=5)
                aes_key = st.text_input("Masukkan kunci AES:")
                if st.button("Dekripsi Teks"):
                    if not text_to_decrypt or not aes_key:
                        st.error("Teks dan kunci AES tidak boleh kosong.")
                    elif not validate_no_empty_lines(text_to_decrypt):  # Validasi baris kosong
                        st.error("Teks tidak boleh mengandung dua baris kosong berturut-turut.")
                    else:
                        text_to_decrypt = text_to_decrypt.replace("\n\n", "\n")
                        decrypted_text = super_decrypt(text_to_decrypt, scytale_key, aes_key)
                        st.success("Teks berhasil didekripsi!")
                        st.text_area("Teks yang didekripsi:", value=decrypted_text, height=200)
                        # Simpan log dekripsi
                        save_encryption_log(st.session_state.user_id, "dekripsi", decrypted_text, text_to_decrypt, scytale_key, aes_key)
            elif data_type == "File":
                encrypted_file = st.file_uploader("Pilih file terenkripsi", type=["txt", "pdf", "jpg", "png", "gif", "mp3", "mp4", "zip", "rar", "*"])
                key_file = st.file_uploader("Pilih file kunci", type=["key"])

                if st.button("Dekripsi File"):
                    # After decrypting the file, save the log
                    if encrypted_file is not None and key_file is not None:
                        encrypted_file_path = encrypted_file.name
                        with open(encrypted_file_path, "wb") as f:
                            f.write(encrypted_file.getbuffer())
                        key = key_file.read()

                        decrypted_file_path = decrypt_file(encrypted_file_path, key)
                        st.success("File berhasil didekripsi!")

                        # Save the log into the database
                        save_file_log(st.session_state.user_id, "dekripsi", encrypted_file.name, None, decrypted_file_path, "secret.key")

                        with open(decrypted_file_path, "rb") as f:
                            st.download_button("Download File Terdekripsi", f, file_name=decrypted_file_path)

                    else:
                        st.error("Silakan pilih file.")
            elif data_type == "Gambar":
                encrypted_image = st.file_uploader("Unggah gambar terenkripsi", type=["png", "jpg", "jpeg", "img"])
                uploaded_key = st.file_uploader("Unggah file kunci", type=["txt"])
                if st.button("Dekripsi Gambar"):
                    # After decrypting the image, save the log
                    if encrypted_image and uploaded_key:
                        encrypted_image_path = f"temp_encrypted.{encrypted_image.type.split('/')[-1]}"
                        with open(encrypted_image_path, "wb") as f:
                            f.write(encrypted_image.getbuffer())

                        key = uploaded_key.getvalue().decode("utf-8").strip()

                        decrypted_message = decrypt_message_with_key(encrypted_image_path, key)
                        st.write("Pesan Terdekripsi:", decrypted_message)

                        # Save the log into the database
                        save_image_log(st.session_state.user_id, "dekripsi", encrypted_image.name, None, decrypted_message, uploaded_key.name)
