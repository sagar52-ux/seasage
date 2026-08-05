import os
import requests
import streamlit as st
from google import genai
from google.genai import types

# -------------------------------------------------------------------
# Configuration & Setup
# -------------------------------------------------------------------
st.set_page_config(
    page_title="SeaSage - Global Marine Mentor",
    page_icon="⚓",
    layout="centered"
)

# Initialize Gemini Client (Ensure GEMINI_API_KEY environment variable is set)
@st.cache_resource
def get_gemini_client():
    return genai.Client()

client = get_gemini_client()

SYSTEM_PROMPT = """
You are SeaSage, a marine mentor for first-time sailors globally. 
Provide practical, plain-English guidance for boat buying, repairs, and living at sea.
When diagnosing issues, always state: 1. Safety Check, 2. Tools Needed, 3. Step-by-Step Fix, 4. When to Call a Pro.
"""

# -------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------
def get_marine_weather(lat: float, lon: float):
    """Fetch free global marine weather data from Open-Meteo Marine API."""
    url = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&current=wave_height,wave_direction,wind_wave_height,swell_wave_height,ocean_current_velocity"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get("current", {})
    except Exception as e:
        return {"error": str(e)}
    return {}

# -------------------------------------------------------------------
# User Interface (Streamlit)
# -------------------------------------------------------------------
st.title("⚓ SeaSage")
st.caption("Your Global Marine Mentor & Boat Assistant")

# Navigation Tabs
tab_chat, tab_weather = st.tabs(["💬 Ask Mentor", "🌊 Live Marine Weather"])

# --- TAB 1: AI Chatbot & Visual Diagnostics ---
with tab_chat:
    st.subheader("How can I help you on deck today?")
    
    # Image Uploader for Diagnostic Mode
    uploaded_image = st.file_uploader("Upload engine, hull, or electrical photo for analysis", type=["jpg", "png", "jpeg"])
    
    user_query = st.text_area("Describe your issue, question, or location:", placeholder="e.g., My diesel engine is spitting steam, or what should I check when buying a 35ft sailboat?")
    
    if st.button("Get Guidance", type="primary"):
        if not user_query and not uploaded_image:
            st.warning("Please provide a question or upload an image.")
        else:
            with st.spinner("Analyzing nautical manuals and live web data..."):
                contents = []
                if uploaded_image:
                    image_bytes = uploaded_image.read()
                    contents.append(types.Part.from_bytes(data=image_bytes, mime_type=uploaded_image.type))
                
                if user_query:
                    contents.append(user_query)

                # Query Gemini 2.5 Flash with Google Search Grounding enabled
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT,
                            tools=[{"google_search": {}}],  # Enables real-time web search grounding
                            temperature=0.7,
                        )
                    )
                    st.markdown("### 🧭 SeaSage Guidance:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Error connecting to SeaSage brain: {e}")

# --- TAB 2: Marine Weather ---
with tab_weather:
    st.subheader("Global Offshore Weather Check")
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("Latitude", value=25.7617)  # Default: Miami/Bahamas approach
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
