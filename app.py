import streamlit as st
from tensorflow.keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
import random
import streamlit.components.v1 as components

#  PAGE
st.set_page_config(page_title="BinBuddy", page_icon="♻️", layout="centered")

#  STYLES
st.markdown("""
<style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?auto=format&fit=crop&w=1600&q=80");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
.main .block-container {
        background: rgba(255,255,255,0.90);
        border-radius: 24px;
        padding: 2rem;
    }

    html, body, [class*="css"] {
        color: black !important;
    }

    .main-title {
        text-align: center;
        font-size: 3.2rem;
        font-weight: 800;
        color: #184d3b;
        margin-bottom: 0.25rem;
    }

    .subtitle {
        text-align: center;
        font-size: 1.15rem;
        color: #4f655a;
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #21382d;
        margin-top: 0.6rem;
        margin-bottom: 0.7rem;
    }

    .bin-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-top: 0.5rem;
        margin-bottom: 1.2rem;
    }

    .bin-card {
        border-radius: 20px;
        padding: 18px;
        color: black;
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
        font-weight: 600;
    }

    .bin-title {
        font-size: 1.35rem;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .bin-text {
        font-size: 1rem;
        line-height: 1.4;
    }

    .result-card {
        border-radius: 24px;
        padding: 1.4rem;
        box-shadow: 0 10px 28px rgba(0,0,0,0.08);
        margin-top: 1rem;
        text-align: center;
    }

    .result-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #24322d;
        margin-bottom: 0.25rem;
    }

    .result-sub {
        color: #596b62;
        margin-bottom: 1rem;
        font-size: 1rem;
    }

    .info-box {
        background: rgba(255,255,255,0.72);
        border-radius: 16px;
        padding: 0.95rem 1rem;
        margin-top: 0.8rem;
        color: #22312a;
        font-size: 1.05rem;
        text-align: left;
    }

    .stButton button {
        width: 100%;
        border-radius: 14px;
        border: none;
        padding: 0.75rem 1rem;
        font-weight: 700;
        background: linear-gradient(90deg, #2e8b57 0%, #49a96c 100%);
        color: white !important;
        box-shadow: 0 8px 18px rgba(46, 139, 87, 0.22);
    }

    .stButton button:hover {
        color: white !important;
    }

    label, .stRadio label, .stCheckbox label, .stFileUploader label, .stCameraInput label {
        color: black !important;
        font-weight: 800 !important;
    }

    /* Remove weird spacing from empty elements */
    div[data-testid="stVerticalBlock"] > div:empty {
        display: none !important;
    }
    div[role="radiogroup"] {
    display: flex !important;
    justify-content: center !important;
    gap: 2rem !important;
    margin-bottom: 1rem !important;
}

[data-testid="stCheckbox"] {
    display: flex !important;
    justify-content: center !important;
    margin-top: 0.5rem !important;
    margin-bottom: 1rem !important;
}

[data-testid="stCameraInput"] label,
[data-testid="stFileUploader"] label {
    text-align: center !important;
    display: block !important;
    width: 100% !important;
    font-weight: 1000 !important;
    color: white !important;
}

[data-testid="stCameraInput"],
[data-testid="stFileUploader"] {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
}
</style>
""", unsafe_allow_html=True)

#  HEADER
st.markdown('<div class="main-title">♻️ BinBuddy</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Show or upload a waste item and I will tell you which bin it belongs to.</div>',
    unsafe_allow_html=True
)

#  BIN GUIDE
st.markdown('<div class="section-title">🗂️ Bin color guide</div>', unsafe_allow_html=True)
st.markdown("""
<div class="bin-grid">
    <div class="bin-card" style="background:#DCEEFF;">
        <div class="bin-title">🔵 Blue bin</div>
        <div class="bin-text">Plastic, metal, and drink cartons (PMD)</div>
    </div>
    <div class="bin-card" style="background:#FFF3B0;">
        <div class="bin-title">🟡 Yellow bin</div>
        <div class="bin-text">Paper</div>
    </div>
    <div class="bin-card" style="background:#E5E5E5;">
        <div class="bin-title">⚪ Grey bin</div>
        <div class="bin-text">Glass</div>
    </div>
    <div class="bin-card" style="background:#DDF4E4;">
        <div class="bin-title">🟢 Green bin</div>
        <div class="bin-text">Other waste</div>
    </div>
</div>
""", unsafe_allow_html=True)

#  MODEL
np.set_printoptions(suppress=True)

model = load_model("keras_Model.h5", compile=False)
class_names = open("labels.txt", "r").readlines()

def normalize_class_name(name: str) -> str:
    name = name.lower().strip()
    aliases = {
        "plastic": "plastic",
        "metal": "metal",
        "drink carton": "drink carton",
        "drink cartoon": "drink carton",
        "paper": "paper",
        "glass": "glass",
        "other waste": "other waste",
        "other": "other waste",
        "organic": "other waste",
        "rest": "other waste",
        "residual": "other waste",
    }
    return aliases.get(name, name)

CLASS_INFO = {
    "plastic": {
        "display": "Plastic",
        "icon": "♻️",
        "bin": "Blue bin",
        "hex": "#DCEEFF",
        "facts": [
            "Plastic bottles can be recycled into new bottles, bags, and even clothing.",
            "Recycling plastic helps reduce waste in landfills and oceans.",
            "Sorting plastic correctly makes recycling more effective."
        ],
        "praise": ["Well done, You just saved the bin from confusion!", "Great job, The planet says thank you!", "Nice sorting, You’ve got serious bin instincts!"]
    },
    "metal": {
        "display": "Metal",
        "icon": "🥫",
        "bin": "Blue bin",
        "hex": "#EEF1F4",
        "facts": [
            "Metal can be recycled many times without losing quality.",
            "Recycling metal saves a lot of energy.",
            "Aluminum cans can return as new cans very quickly."
        ],
        "praise": ["Trash-tastic job!", "Bin there, sorted that!", "Certified sorting legend!"]
    },
    "drink carton": {
        "display": "Drink carton",
        "icon": "🧃",
        "bin": "Blue bin",
        "hex": "#E8F5FF",
        "facts": [
            "Drink cartons can be recycled into paper products and other materials.",
            "Flattening cartons saves space in the recycling bin.",
            "Drink cartons are made of layers that help keep drinks fresh."
        ],
        "praise": ["Eco hero unlocked!", "The bin approves!", "That item found its home!"]
    },
    "paper": {
        "display": "Paper",
        "icon": "📄",
        "bin": "Yellow bin",
        "hex": "#FFF3B0",
        "facts": [
            "Recycling paper helps save trees.",
            "Paper can often be recycled several times.",
            "Keeping paper dry and clean improves recycling."
        ],
        "praise": ["Look at you, making trash decisions like a boss.", "Even the garbage is impressed.", "Not all heroes wear capes, some sort trash."]
    },
    "glass": {
        "display": "Glass",
        "icon": "🫙",
        "bin": "Grey bin",
        "hex": "#E5E5E5",
        "facts": [
            "Glass can be recycled again and again without losing quality.",
            "Recycled glass can become new bottles and jars.",
            "Sorting glass correctly helps keep recycling clean."
        ],
        "praise": ["Great job, planet protector!", "You helped the Earth today!", "Awesome work, eco star!"]
    },
    "other waste": {
        "display": "Other waste",
        "icon": "🗑️",
        "bin": "Green bin",
        "hex": "#DDF4E4",
        "facts": [
            "Some items cannot be recycled and should go into general waste.",
            "Sorting waste correctly prevents contamination.",
            "When in doubt, checking first is better than guessing."
        ],
        "praise": ["A masterpiece in waste management.", "The planet says thank you.", "Woohoo! The bin is smiling."]
    }
}

#  PREDICTION
def predict_image(image: Image.Image):
    # Exact Teachable Machine style
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    data[0] = normalized_image_array

    prediction = model.predict(data, verbose=0)
    index = int(np.argmax(prediction))

    raw_class_name = class_names[index]
    class_name = normalize_class_name(raw_class_name[2:].strip())
    confidence_score = float(prediction[0][index])

    return class_name, confidence_score

#  VOICE
def speak_text(text: str):
    safe_text = text.replace("\\", "\\\\").replace("`", "\\`").replace('"', '\\"')
    components.html(
        f"""
        <script>
            const utterance = new SpeechSynthesisUtterance("{safe_text}");
            utterance.rate = 0.95;
            utterance.pitch = 1.0;
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(utterance);
        </script>
        """,
        height=0,
    )

#  INPUT
st.markdown('<div class="section-title" style="text-align:center; color:#228B22;">📸 Add your picture</div>', unsafe_allow_html=True)

source = st.radio(
    "Source",
    ["📱 Take a photo", "📂 Upload an image"],
    horizontal=True,
    label_visibility="collapsed"
)

read_aloud = st.checkbox("🔊 Read the result aloud", value=True)

image = None

if source == "📱 Take a photo":
    camera_image = st.camera_input("Take a clear photo of the waste item")
    if camera_image is not None:
        image = Image.open(camera_image).convert("RGB")

elif source == "📂 Upload an image":
    uploaded_file = st.file_uploader("Upload a JPG or PNG image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")

col1, col2 = st.columns(2)
with col1:
    analyze = st.button("✨ Analyze item", use_container_width=True)
with col2:
    restart = st.button("↺ Restart", use_container_width=True)

if restart:
    st.rerun()

#  RESULT
#  RESULT
if image is not None:
    st.image(image, caption="Selected image", use_container_width=True)

if image is not None and analyze:
    class_name, confidence_score = predict_image(image)

    if class_name not in CLASS_INFO:
        class_name = "other waste"

    info = CLASS_INFO[class_name]
    fact = random.choice(info["facts"])
    praise = random.choice(info["praise"])

    # If confidence is too low, ask user to retry
    if confidence_score < 0.70:
        retry_messages = [
            "Well... this is awkward. I am not confident enough about this one. Could you please take a better picture?",
            "Oops. My recycling brain is having a moment. Please try again with a clearer photo.",
            "Sorry, but I would rather not embarrass myself with a bad guess. Please take another picture.",
            "Hmm... I am not confident enough to judge this trash today. Please try again with a closer and brighter photo.",
            "My apologies, but that picture has defeated my bin wisdom. Please take a clearer one."
        ]

        retry_message = random.choice(retry_messages)

        st.markdown(
            f"""
            <div class="result-card" style="background:#FDEDEC;">
                <div class="result-title">🙈 Not sure enough</div>
                <div class="result-sub">Confidence: {confidence_score:.0%}</div>
                <div class="info-box"><b>Message:</b> {retry_message}</div>
                <div class="info-box"><b>Tip:</b> Try again with better lighting, less background, and a closer photo of the item.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if read_aloud:
            speak_text(retry_message)

    else:
        voice_text = f"This is {info['display']}. It goes to the {info['bin']}. {praise}"

        st.markdown(
            f"""
            <div class="result-card" style="background:{info['hex']};">
                <div class="result-title">{info['icon']} {info['display']}</div>
                <div class="result-sub">Confidence: {confidence_score:.0%}</div>
                <div class="info-box"><b>Bin color:</b> {info['bin']}</div>
                <div class="info-box"><b>Message:</b> {praise} This goes to the <b>{info['bin']}</b>.</div>
                <div class="info-box"><b>Fun fact:</b> {fact}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if read_aloud:
            speak_text(voice_text)
