import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io
import base64

st.set_page_config(page_title="Smooth Jazz Generator", page_icon="🎷", layout="wide", initial_sidebar_state="expanded")

# Styling CSS
st.markdown("""
<style>
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    .stApp { background-color: #12161f; color: #e0e0e0; }
    h1, h2, h3 { color: #d4af37; }
    .stButton>button { background-color: #d4af37; color: #12161f; font-weight: bold; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

SYSTEM_INSTRUCTION = """
Anda adalah Insinyur Prompt Profesional untuk menghasilkan background visual YouTube Long-Form & Thumbnail Smooth Jazz.
Ikuti Master Prompt untuk menghasilkan 5 JSON Latar Belakang terpisah dan 2 JSON Thumbnail terpisah.
Setiap prompt WAJIB memasukkan elemen audio: Luxury Amplifier, Premium Active Speaker, JBL-Style Premium Active Speaker, Audiophile Headphones, Vinyl Turntable.
Jika mood = Relax & Unwind, tambahkan teks pada thumbnail: "SMOOTH JAZZ" (besar) dan "Relax & Unwind" (kecil).
"""

# SIDEBAR (Pengaturan API Key)
with st.sidebar:
    st.title("⚙️ Pengaturan")
    api_key = st.text_input("Gemini API Key", type="password", help="Masukkan API Key Google Gemini Anda di sini.")
    st.markdown("""
    ---
    **🔑 Belum punya API Key?**
    1. Buka [Google AI Studio](https://aistudio.google.com/app/apikey).
    2. Login pakai akun Google/Gmail.
    3. Klik **Create API key**.
    4. *Copy* kodenya dan *paste* di kolom atas.
    
    *Tenang, API Key ini 100% Gratis!*
    ---
    """)
    st.caption("Aplikasi Smooth Jazz YouTube Long-Form Prompt Generator.")

st.markdown("<h1 style='text-align: center;'>🎷 SMOOTH JAZZ GENERATOR & VISUALIZER</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("1. Referensi Visual & Audio")
    uploaded_file = st.file_uploader("Unggah gambar latar belakang", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Gambar Referensi", use_container_width=True)

    uploaded_audio = st.file_uploader("Unggah Musik Jazz (.mp3 / .wav)", type=["mp3", "wav"])
    
    if uploaded_audio:
        st.caption("🎵 Audio Spectrum Visualizer (Bergerak Mengikuti Lagu):")
        audio_bytes = uploaded_audio.read()
        b64_audio = base64.b64encode(audio_bytes).decode()
        audio_type = uploaded_audio.type

        # HTML5 & Web Audio API Visualizer Spectrum
        visualizer_html = f"""
        <div style="text-align:center; background:#0b0d13; padding:15px; border-radius:12px; border:1px solid #d4af37;">
            <canvas id="canvas" width="400" height="100" style="width:100%; height:100px; border-bottom: 2px solid #d4af37;"></canvas>
            <br/><br/>
            <audio id="audio" controls style="width:100%;">
                <source src="data:{audio_type};base64,{b64_audio}" type="{audio_type}">
            </audio>
        </div>

        <script>
            const audio = document.getElementById('audio');
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');

            let audioCtx, analyser, source;

            audio.onplay = () => {{
                if (!audioCtx) {{
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    analyser = audioCtx.createAnalyser();
                    source = audioCtx.createMediaElementSource(audio);
                    source.connect(analyser);
                    analyser.connect(audioCtx.destination);
                    analyser.fftSize = 64;
                    draw();
                }}
                audioCtx.resume();
            }};

            function draw() {{
                requestAnimationFrame(draw);
                const bufferLength = analyser.frequencyBinCount;
                const dataArray = new Uint8Array(bufferLength);
                analyser.getByteFrequencyData(dataArray);

                ctx.clearRect(0, 0, canvas.width, canvas.height);

                const barWidth = (canvas.width / bufferLength) * 1.5;
                let barHeight;
                let x = 0;

                for(let i = 0; i < bufferLength; i++) {{
                    barHeight = dataArray[i] / 2.5;
                    ctx.fillStyle = '#d4af37';
                    ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
                    x += barWidth + 2;
                }}
            }}
        </script>
        """
        st.components.v1.html(visualizer_html, height=200)

    st.subheader("2. Waktu & Mood")
    time_option = st.select_slider("Waktu Hari:", options=["Pagi hari", "Siang hari", "Sore hari", "Golden Hour", "Malam hari"], value="Malam hari")
    mood_options = ["NIGHT JAZZ", "SLEEP", "DEEP RELAX", "RELAXING", "FOCUS", "STUDY", "WORK", "PRODUCTIVITY", "READING", "CHILL", "RAINY JAZZ", "MORNING JAZZ", "EVENING JAZZ", "JAZZ LOUNGE"]
    selected_mood = st.selectbox("Mood / Fungsi Ruang:", mood_options)
    custom_mood = st.text_input("Atau ketik mood sendiri:")
    final_mood = custom_mood if custom_mood.strip() != "" else selected_mood

    generate_btn = st.button("🚀 GENERATE PROMPTS", use_container_width=True)

with col2:
    st.subheader("3. Output Generator")
    if generate_btn:
        if not api_key:
            st.error("Masukkan Gemini API Key di sidebar!")
        elif not uploaded_file:
            st.warning("Unggah gambar referensi terlebih dahulu.")
        else:
            with st.spinner("Menganalisis gambar dan membuat prompt..."):
                try:
                    client = genai.Client(api_key=api_key)
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format=image.format or 'JPEG')
                    img_bytes = img_byte_arr.getvalue()

                    prompt_text = f"Analisis gambar. Waktu: {time_option}. Mood: {final_mood}. Hasilkan 5 Background JSON & 2 Thumbnail JSON."

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[types.Part.from_bytes(data=img_bytes, mime_type=uploaded_file.type), prompt_text],
                        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION, temperature=0.7)
                    )
                    st.success("Berhasil!")
                    st.text_area("Output Prompt JSON:", value=response.text, height=500)
                except Exception as e:
                    st.error(f"Eror: {str(e)}")
