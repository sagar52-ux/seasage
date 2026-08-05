import os
import requests
import streamlit as st
from google import genai

# Page Config
st.set_page_config(
    page_title="SeaSage - Global Marine Mentor",
    page_icon="⚓",
    layout="centered"
)

# Custom Marine UI Styling
st.markdown("""
<style>
    .stApp {
        background-color: #0d1b2a;
        color: #e0e1dd;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .sage-card {
        background-color: #1b263b;
        border-left: 5px solid #62b6cb;
        border-radius: 8px;
        padding: 20px;
        margin-top: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .sage-title {
        color: #62b6cb;
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 8px;
    }
    .stButton>button {
        background-color: #1b4965;
        color: white;
        border-radius: 8px;
        border: none;
        width: 100%;
        padding: 10px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #62b6cb;
        color: #0d1b2a;
    }
</style>
""", unsafe_allow_html=True)

# Fetch API Key
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("Missing GEMINI_API_KEY! Please check your Streamlit Secrets settings.")
    st.stop()

@st.cache_resource
def get_client():
    return genai.Client(api_key=api_key)

client = get_client()

SYSTEM_PROMPT = """
You are SeaSage, an expert marine mentor for first-time sailors globally. 
Provide practical, plain-English guidance for boat buying, repairs, and living at sea.
When diagnosing issues or answering queries, structure your response as follows:
- HAZARD CHECK: Immediate safety steps or checks.
- REQUIRED TOOLS: What basic tools or materials are needed.
- ACTION PLAN: Clear, numbered step-by-step instructions.
- WHEN TO CALL A PRO: Threshold conditions for hiring a certified surveyor/mechanic.
"""

def get_marine_weather(lat: float, lon: float):
    url = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&current=wave_height,wave_direction,wind_wave_height,swell_wave_height,ocean_current_velocity"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get("current", {})
    except Exception as e:
        return {"error": str(e)}
    return {}

# UI Interface Header
st.title("⚓ SeaSage")
st.caption("Your Global Marine Mentor & Boat Assistant")

tab_chat, tab_weather = st.tabs(["💬 Ask Mentor", "🌊 Live Weather"])

with tab_chat:
    uploaded_image = st.file_uploader("📷 Upload photo (Engine, Hull, Leak)", type=["jpg", "png", "jpeg"])
    user_query = st.text_area("💬 Describe your issue or question:", placeholder="e.g., My hull is cracked what do I do?")
    
    if st.button("Get Guidance", type="primary"):
        if not user_query and not uploaded_image:
            st.warning("Please enter a question or upload an image.")
        else:
            with st.spinner("Consulting marine knowledge base..."):
                try:
                    contents = []
                    if uploaded_image:
                        from PIL import Image
                        img = Image.open(uploaded_image)
                        contents.append(img)
                    if user_query:
                        contents.append(user_query)

                    # Updated to gemini-2.0-flash
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=contents,
                        config={"system_instruction": SYSTEM_PROMPT}
                    )
                    
                    st.markdown('<div class="sage-card"><div class="sage-title">🧭 SeaSage Guidance:</div>', unsafe_allow_html=True)
                    st.write(response.text)
                    st.markdown('</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error connecting to SeaSage: {e}")

with tab_weather:
    st.subheader("Offshore Weather Check")
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("Latitude", value=25.7617)
    with col2:
        lon = st.number_input("Longitude", value=-80.1918)
        
    if st.button("Fetch Marine Conditions"):
        data = get_marine_weather(lat, lon)
        if "error" in data:
            st.error("Unable to retrieve weather data.")
        else:
            st.metric("Wave Height", f"{data.get('wave_height', 'N/A')} m")
            st.metric("Swell Height", f"{data.get('swell_wave_height', 'N/A')} m")
            st.metric("Current Velocity", f"{data.get('ocean_current_velocity', 'N/A')} km/h")
