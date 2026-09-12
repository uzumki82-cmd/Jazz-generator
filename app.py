import streamlit as st
import google.generativeai as genai
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Jazz Room Prompt Generator", page_icon="🎷", layout="centered")

st.title("🎷 Jazz Room Prompt Generator")
st.write("Buat prompt atmosfer ruangan & musik Jazz secara otomatis.")

# --- API KEY SETUP ---
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    api_key = st.text_input("Masukkan Gemini API Key Kamu:", type="password")

if not api_key:
    st.warning("Silakan masukkan Gemini API Key untuk melanjutkan.")
    st.stop()

# Konfigurasi Library Gemini
genai.configure(api_key=api_key)

# --- INPUT FORM ---
mood_options = ["NIGHT JAZZ", "COZY CAFE JAZZ", "RAINY DAY JAZZ", "VINTAGE LUXURY JAZZ", "SMOKY BAR JAZZ"]
selected_mood = st.selectbox("Mood / Fungsi Ruang:", mood_options)
custom_mood = st.text_input("Atau ketik mood sendiri (opsional):")

final_mood = custom_mood if custom_mood.strip() != "" else selected_mood

# --- GENERATE ACTION ---
if st.button("🚀 GENERATE PROMPTS"):
    with st.spinner("Meracik prompt terbaik... ⏳"):
        try:
            # Mencoba model flash versi stabil
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception:
                model = genai.GenerativeModel('gemini-2.0-flash')
            
            prompt_input = f"""
            Buatkan 3 ide prompt visual & atmosfer untuk musik Jazz dengan tema/mood: {final_mood}.
            Sajikan hasil secara rapi dengan format:
            1. Visual Ambience (Pencahayaan & Dekorasi)
            2. Audio Mood (Instrumen utama & Tempo)
            3. Prompt Gambar/Image Generator (dalam bahasa Inggris untuk Midjourney/FLUX)
            """
            
            response = model.generate_content(prompt_input)
            
            st.markdown("---")
            st.subheader("3. Output Generator")
            st.success("Berhasil di-generate!")
            st.write(response.text)
            
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memanggil AI API: {e}")
