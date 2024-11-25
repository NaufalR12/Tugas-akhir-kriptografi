import hashlib
import sqlite3
import streamlit as st
import re
import os
from enkripsidekripsitext import super_encrypt, super_decrypt
from file_encryption import encrypt_file, decrypt_file, generate_key, save_key, load_key, create_zip
from steganografigambar import encrypt_message_with_key, decrypt_message_with_key, generate_key_file, create_zip_stegano

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def hash_aes_key(aes_key: str) -> str:
    hashed_key = hashlib.sha256(aes_key.encode()).hexdigest()
    return hashed_key

def hash_scytale_key(scytale_key: int) -> str:
    hashed_key = hashlib.sha256(str(scytale_key).encode()).hexdigest()
    return hashed_key


# ... existing code ...
import supabase

def create_connection():
    url = "https://qxvuktkvfrzzuduinfla.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF4dnVrdGt2ZnJ6enVkdWluZmxhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI0OTgyMTQsImV4cCI6MjA0ODA3NDIxNH0.oilmkT4S49LVX0fxDMkY9pNajzNIGBRFAPXzqmV4n_E"
    supabase_client = supabase.create_client(url, key)
    return supabase_client

def add_user(username, password):
    conn = create_connection()
    # ... existing code ...
    if conn.table('users').select('username').eq('username', username).execute().data:
        raise Exception("Username sudah ada")  # Ganti dengan exception yang sesuai
    conn.table('users').insert({'username': username, 'password': hash_password(password)}).execute()
    # ... existing code ...

def check_user(username, password):
    conn = create_connection()
    user = conn.table('users').select('*').eq('username', username).eq('password', hash_password(password)).execute().data
    #conn.close()
    return user

def save_encryption_log(user_id, action, ciphertext, scytale_key, aes_key):
    conn = create_connection()
    conn.table('encryption_logs').insert({
        'user_id': user_id,
        'action': action,
        'ciphertext': ciphertext,
        'scytale_key': scytale_key,
        'aes_key': aes_key
    }).execute()
    #conn.close()

def save_file_log(user_id, action, file_name, encrypted_file, decrypted_file, key_file):
    conn = create_connection()
    conn.table('file_logs').insert({
        'user_id': user_id,
        'action': action,
        'file_name': file_name,
        'encrypted_file': encrypted_file,
        'decrypted_file': decrypted_file,
        'key_file': key_file
    }).execute()
    #conn.close()

def save_image_log(user_id, action, image_name, encrypted_image, decrypted_message, key_file):
    conn = create_connection()
    conn.table('gambar_logs').insert({
        'user_id': user_id,
        'action': action,
        'image_name': image_name,
        'encrypted_image': encrypted_image,
        'key_file': key_file
    }).execute()
    #conn.close()
# ... existing code ...



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


def validate_no_empty_lines(plaintext):
    lines = plaintext.split("\n")
    
    for i in range(1, len(lines)):
        if lines[i].strip() == "" and lines[i-1].strip() == "":
            return False  
    return True  


#buat tabel jika belum ada
#create_tables()

#Sidebar
def create_sidebar():
    st.sidebar.image("gambar/logoprofil.png", use_container_width=True)

    st.sidebar.header("Selamat Datang, Agen {} di MissionEncrypt!".format(st.session_state.user_name))   
    
    
    mode = st.sidebar.selectbox("Pilih Mode:", ["🔒Enkripsi", "🔑Dekripsi"])
    
    if st.sidebar.button("Logout"):
        st.session_state.page = "Login"
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.rerun()
    
    return mode

#logo CIA
col1, col2, col3 = st.columns([3, 2, 3])  
with col2:
    st.image("gambar/logo.png", width=200)

#Nama Aplikasi
st.markdown(
    """
    <style>
    .title {
        text-align: center;
        font-size: 40px;
        font-weight: bold;
    }
    </style>
    <div class="title">
        MissionEncrypt
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <style>
    .center {
        text-align: center;
        font-size: 20px;
        
    }
    </style>
    <div class="center">
        Selamat Datang Agen CIA! Keamanan adalah Tugasmu, Kerahasiaan adalah Kekuatanmu!
    </div>
    """,
    unsafe_allow_html=True
)

if 'page' not in st.session_state:
    st.session_state.page = "Login"
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

placeholder = st.empty()

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
                    st.session_state.user_id = user[0]['id']  
                    st.session_state.user_name = username
                    st.session_state.page = "Menu"  
                    st.rerun()  
                else:
                    st.error("Username atau password salah.")

        if st.button("Buat Akun"):
            st.session_state.page = "Daftar"  
            st.rerun()  

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
            st.rerun()

elif st.session_state.page == "Menu":
    mode = create_sidebar()
    with placeholder.container():
        st.subheader(f"📃Halaman Menu ({mode})")
        st.write("Silakan pilih menu yang anda inginkan!")

        

        if mode == "🔒Enkripsi":
            data_type = st.selectbox("Pilih jenis data yang ingin dienkripsi:", ["💬Teks", "📁File", "📷Gambar"])
            if data_type == "💬Teks":
                text_to_encrypt = st.text_area("Masukkan teks:")
                scytale_key = st.number_input("Masukkan kunci Scytale (angka):", min_value=1, value=5)
                aes_key = st.text_input("Masukkan kunci AES:")
                
                if st.button("Enkripsi Teks"):
                    if not text_to_encrypt or not aes_key:
                        st.error("Teks dan kunci AES tidak boleh kosong.")
                    elif not validate_no_empty_lines(text_to_encrypt):  
                        st.error("Teks tidak boleh mengandung dua baris kosong berturut-turut.")
                    else:
                        text_to_encrypt = text_to_encrypt.replace("\n\n", "\n")
                        try:
                            encrypted_text = super_encrypt(text_to_encrypt, scytale_key, aes_key)
                            st.success("Teks berhasil dienkripsi!")
                            st.text_area("Teks yang dienkripsi:", value=encrypted_text, height=200)
                            hashed_scytale_key = hash_scytale_key(scytale_key)
                            hashed_aes_key = hash_aes_key(aes_key)
                        
                            save_encryption_log(st.session_state.user_id, "enkripsi", encrypted_text, hashed_scytale_key, hashed_aes_key)
                            print(f"Inserting log: user_id={st.session_state.user_id}, action='enkripsi', ciphertext={encrypted_text}, scytale_key={scytale_key}, aes_key={aes_key}")
                        except Exception as e:
                            st.error(f"Terjadi kesalahan saat proses enkripsi: {str(e)}")
            elif data_type == "📁File":
                uploaded_file = st.file_uploader("Pilih file untuk dienkripsi", type=["txt", "pdf", "jpg", "png", "gif", "mp3", "mp4", "zip", "csv", "docx"])
                if st.button("Enkripsi File"):
                    if uploaded_file is not None:
                        try:
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
                            save_file_log(st.session_state.user_id, "enkripsi", uploaded_file.name, encrypted_file_path, None, "secret.key")
                            # Menyediakan tombol unduh untuk file ZIP
                            with open(zip_file_path, "rb") as f:
                                st.download_button(
                                    label="Download File ZIP",
                                    data=f,
                                    file_name=zip_file_path.split("/")[-1],
                                    mime="application/zip"
                                )
                        except Exception as e:
                            st.error(f"Terjadi kesalahan: {e}")
                    else:
                        st.error("Silakan pilih file.")
            elif data_type == "📷Gambar":
                camera_input = st.camera_input("Ambil Foto dengan Kamera")
                uploaded_image = camera_input if camera_input else st.file_uploader("Pilih gambar", type=["png", "jpg", "jpeg"])
                message = st.text_input("Masukkan pesan yang ingin disembunyikan")

                if uploaded_image:
                    
                    st.session_state["uploaded_image"] = uploaded_image

                if st.button("Enkripsi Gambar"):
                    if st.session_state["uploaded_image"] and message:
                        try:
                            image_path = f"temp_input.{uploaded_image.type.split('/')[-1]}"
                            with open(image_path, "wb") as f:
                                f.write(st.session_state["uploaded_image"].getbuffer())

                            key_file_path, key = generate_key_file()
                            st.session_state["key_file_path"] = key_file_path

                            output_path = f"encrypted_image.{uploaded_image.type.split('/')[-1]}"
                            encrypted_image_path = encrypt_message_with_key(image_path, message, output_path, key)
                            st.session_state["encrypted_image_path"] = encrypted_image_path

                            st.success("Gambar berhasil dienkripsi!")

                            
                            save_image_log(st.session_state.user_id, "enkripsi", uploaded_image.name, encrypted_image_path, None, key_file_path)

                            
                            zip_file_path = create_zip_stegano(encrypted_image_path, key_file_path)

                            with open(zip_file_path, "rb") as zip_file:
                                st.download_button("Download Gambar dan Kunci dalam ZIP", data=zip_file, file_name=zip_file_path.split('/')[-1])
                        except Exception as e:
                            st.error(f"Terjadi kesalahan: {e}")
        elif mode == "🔑Dekripsi":
            data_type = st.selectbox("Pilih jenis data yang ingin didekripsi:", ["💬Teks", "📁File", "📷Gambar"])
            if data_type == "💬Teks":
                text_to_decrypt = st.text_area("Masukkan teks:")
                scytale_key = st.number_input("Masukkan kunci Scytale (angka):", min_value=1, value=5)
                aes_key = st.text_input("Masukkan kunci AES:")
                if st.button("Dekripsi Teks"):
                    if not text_to_decrypt or not aes_key:
                        st.error("Teks dan kunci AES tidak boleh kosong.")
                    elif not validate_no_empty_lines(text_to_decrypt):  
                        st.error("Teks tidak boleh mengandung dua baris kosong berturut-turut.")
                    else:
                        text_to_decrypt = text_to_decrypt.replace("\n\n", "\n")
                        try:
                            decrypted_text = super_decrypt(text_to_decrypt, scytale_key, aes_key)
                            st.success("Teks berhasil didekripsi!")
                            st.text_area("Teks yang didekripsi:", value=decrypted_text, height=200)
                            hashed_scytale_key = hash_scytale_key(scytale_key)
                            hashed_aes_key = hash_aes_key(aes_key)
                            
                            save_encryption_log(st.session_state.user_id, "dekripsi", text_to_decrypt, hashed_scytale_key, hashed_aes_key)
                        except Exception as e:
                            st.error(f"Terjadi kesalahan saat proses dekripsi: {str(e)}")
            elif data_type == "📁File":
                encrypted_file = st.file_uploader("Pilih file terenkripsi", type=["txt", "pdf", "jpg", "png", "gif", "mp3", "mp4", "zip", "csv", "docx"])
                key_file = st.file_uploader("Pilih file kunci", type=["key"])

                if st.button("Dekripsi File"):
                    
                    if encrypted_file is not None and key_file is not None:
                        try:
                            encrypted_file_path = encrypted_file.name
                            with open(encrypted_file_path, "wb") as f:
                                f.write(encrypted_file.getbuffer())
                            key = key_file.read()

                            decrypted_file_path = decrypt_file(encrypted_file_path, key)
                            st.success("File berhasil didekripsi!")

                            
                            save_file_log(st.session_state.user_id, "dekripsi", encrypted_file.name, None, decrypted_file_path, "secret.key")

                            with open(decrypted_file_path, "rb") as f:
                                st.download_button("Download File Terdekripsi", f, file_name=decrypted_file_path)
                        except Exception as e:
                            st.error(f"Terjadi kesalahan: {e}")
                    else:
                        st.error("Silakan pilih file.")
            elif data_type == "📷Gambar":
                encrypted_image = st.file_uploader("Unggah gambar terenkripsi", type=["png", "jpg", "jpeg", "img"])
                uploaded_key = st.file_uploader("Unggah file kunci", type=["txt"])
                if st.button("Dekripsi Gambar"):
                    
                    if encrypted_image and uploaded_key:
                        try:
                            encrypted_image_path = f"temp_encrypted.{encrypted_image.type.split('/')[-1]}"
                            with open(encrypted_image_path, "wb") as f:
                                f.write(encrypted_image.getbuffer())

                            key = uploaded_key.getvalue().decode("utf-8").strip()

                            decrypted_message = decrypt_message_with_key(encrypted_image_path, key)
                            st.write("Pesan Terdekripsi:", decrypted_message)

                            
                            save_image_log(st.session_state.user_id, "dekripsi", encrypted_image.name, None, decrypted_message, uploaded_key.name)
                        except Exception as e:
                            st.error(f"Terjadi kesalahan: {e}")
