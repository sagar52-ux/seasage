import os
import requests
import streamlit as st
from google import genai
from google.genai import types

APP_NAME = "SeaSage"
MODEL_NAME = "gemini-3.1-flash-lite"
OPEN_METEO_MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"

st.set_page_config(
    page_title="SeaSage — Your AI First Mate",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

:root {
    --deep: #071c2c;
    --sea: #0e3b52;
    --mint: #2bb8ad;
    --pale: #dff4f2;
    --bg: #f5faf9;
    --text: #102a3a;
    --muted: #6b7f8c;
    --line: #dce8eb;
}

html, body, [class*="css"] { font-family: "DM Sans", sans-serif; }
.stApp {
    background: radial-gradient(circle at 85% 5%, rgba(43,184,173,.10), transparent 25%),
                linear-gradient(180deg,#f8fcfc 0%,#eef6f6 100%);
    color: var(--text);
}
.block-container { max-width: 1250px; padding-top: 2rem; padding-bottom: 5rem; }
h1,h2,h3 { font-family: "Manrope", sans-serif !important; letter-spacing: -.035em; }
.hero-title {
    font-family: "Manrope", sans-serif;
    font-size: clamp(2.7rem,6vw,5rem);
    line-height: .96;
    font-weight: 800;
    letter-spacing: -.06em;
    color: var(--deep);
    margin-bottom: 1rem;
}
.hero-subtitle { font-size: 1.08rem; line-height: 1.65; max-width: 700px; color: var(--muted); }
.eyebrow {
    display:inline-block; background:var(--pale); color:#137b76;
    border-radius:999px; padding:7px 13px; font-size:.76rem;
    font-weight:700; letter-spacing:.08em; margin-bottom:1rem;
}
.sea-card {
    background:rgba(255,255,255,.94); border:1px solid var(--line);
    border-radius:20px; padding:1.35rem; box-shadow:0 8px 30px rgba(7,28,44,.05);
    min-height:145px;
}
.sea-card-dark {
    background:linear-gradient(145deg,#071c2c,#0e3c51);
    color:white; border-radius:24px; padding:1.7rem;
}
.card-icon { font-size:1.8rem; margin-bottom:.5rem; }
.card-title { font-family:"Manrope"; font-weight:800; font-size:1.05rem; margin-bottom:.35rem; }
.card-description { color:var(--muted); line-height:1.5; font-size:.9rem; }
.stButton > button {
    border-radius:13px; min-height:46px; font-weight:700;
    border:1px solid var(--line); transition:.18s ease;
}
.stButton > button:hover { transform:translateY(-1px); border-color:var(--mint); }
section[data-testid="stSidebar"] { background:#071c2c; }
section[data-testid="stSidebar"] * { color:#edf8f7 !important; }
section[data-testid="stSidebar"] .stButton > button {
    background:transparent; border-color:transparent; text-align:left;
}
section[data-testid="stSidebar"] .stButton > button:hover { background:rgba(255,255,255,.08); }
.status-pill {
    display:inline-flex; align-items:center; gap:7px; padding:7px 11px;
    background:#e4f7f4; color:#157b75; border-radius:999px;
    font-size:.78rem; font-weight:700;
}
.status-dot { width:8px; height:8px; background:#2bb8ad; border-radius:50%; }
.metric-card {
    background:white; border:1px solid var(--line); border-radius:18px;
    padding:1rem; text-align:center;
}
.metric-value { font-family:"Manrope"; font-weight:800; font-size:1.45rem; color:var(--deep); }
.metric-label { color:var(--muted); font-size:.75rem; margin-top:.25rem; }
.warning-card {
    background:#fff8ec; border:1px solid #f0d5a6;
    border-radius:16px; padding:1rem 1.2rem;
}
.emergency-banner {
    background:linear-gradient(135deg,#5e1818,#9e2e2e);
    color:white; border-radius:22px; padding:1.6rem;
    margin-bottom:1.2rem;
}
.emergency-banner h1 { color:white !important; }
[data-testid="stChatMessage"] { border-radius:18px; }
@media(max-width:800px) {
    .block-container { padding-left:1rem; padding-right:1rem; }
    .hero-title { font-size:3rem; }
}
</style>
""", unsafe_allow_html=True)

DEFAULT_PROFILE = {"name": "", "experience": "", "goal": "", "boat_status": "Not bought yet"}
DEFAULT_BOAT = {"name": "", "type": "", "make_model": "", "length": "", "year": "", "engine": "", "location": "", "notes": ""}

for key, value in {
    "profile": DEFAULT_PROFILE.copy(),
    "boat": DEFAULT_BOAT.copy(),
    "messages": [],
    "mode": "home",
    "onboarding_complete": False,
    "marine_data": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

def get_api_key():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY")

API_KEY = get_api_key()
client = None
if API_KEY:
    try:
        client = genai.Client(api_key=API_KEY)
    except Exception as exc:
        st.error(f"Could not initialise SeaSage AI: {exc}")

SYSTEM_PROMPT = """
You are SeaSage, an AI first mate and mentor for people new to boating,
sailing, boat ownership and living aboard.

The user may know almost nothing about boats. Never assume nautical knowledge.
Your job is not merely to answer questions. Help the user understand what is
happening, decide what to do next, and learn enough to become more independent.

PERSONALITY:
- Calm, patient, practical and reassuring without false reassurance.
- Experienced-sailor energy without pretending to be a human sailor.
- Never condescending.
- Explain jargon immediately.
- Prefer short actionable steps over walls of text.

For practical problems:
1. Briefly explain what may be happening.
2. Give the safest immediate action.
3. Give a short numbered checklist.
4. Ask one useful follow-up question if necessary.
5. Say when to stop and get a qualified professional.

For troubleshooting, start with safe observations. Never tell a beginner to
randomly dismantle equipment. Do not instruct dangerous mechanical, electrical,
fuel, gas, rigging or other hazardous work beyond safe basic checks.

For fire, flooding, gas, fuel, electrical systems, batteries, propulsion,
steering, rigging under load, severe weather, person overboard or medical
emergencies, prioritise immediate safety and appropriate emergency/maritime
assistance.

You are not a substitute for emergency services, qualified marine engineers,
professional boat surveyors, licensed skippers, official nautical charts,
official warnings or local maritime authorities.

Marine forecasts are informational. Do not present forecast data as certainty
and do not replace official navigation information.

For boat buying, consider intended use, location, experience, budget, survey,
engine, rigging, electrical, plumbing, safety, insurance and total ownership
cost. Encourage a professional marine survey before purchase.

For image analysis, identify only what the image supports. Clearly distinguish
confidence from uncertainty. Never encourage touching hazardous equipment just
to investigate.

Emergency mode: be concise, action-oriented and ask only critical questions.

Always adapt to the user's experience level. If they are a complete beginner,
explain terminology from scratch. When information is missing, ask a focused
question rather than inventing facts.
"""

def profile_context():
    p, b = st.session_state.profile, st.session_state.boat
    return f"""
USER:
Name: {p.get("name") or "Not provided"}
Experience: {p.get("experience") or "Not provided"}
Goal: {p.get("goal") or "Not provided"}
Boat status: {p.get("boat_status") or "Not provided"}

BOAT:
Name: {b.get("name") or "Not provided"}
Type: {b.get("type") or "Not provided"}
Make/model: {b.get("make_model") or "Not provided"}
Length: {b.get("length") or "Not provided"}
Year: {b.get("year") or "Not provided"}
Engine: {b.get("engine") or "Not provided"}
Location: {b.get("location") or "Not provided"}
Notes: {b.get("notes") or "Not provided"}
"""

def mode_instruction(mode):
    return {
        "chat": "Normal first-mate mode. Help with whatever the user needs.",
        "buy": "Help a first-time boat buyer. Be cautious and practical.",
        "fix": "Guide troubleshooting progressively, starting with safe observations.",
        "trip": "Help plan a trip considering boat capability, crew, weather, fuel, water, provisions, navigation and contingencies.",
        "learn": "Teach a complete beginner progressively, using simple analogies.",
        "emergency": "EMERGENCY MODE. Prioritise immediate safety and appropriate emergency or maritime assistance. Keep responses concise.",
    }.get(mode, "Normal first-mate mode.")

def build_contents(user_text, image_bytes=None, mime_type=None):
    contents = []
    for message in st.session_state.messages[-16:]:
        contents.append(types.Content(
            role="user" if message["role"] == "user" else "model",
            parts=[types.Part.from_text(text=message["content"])]
        ))
    parts = [types.Part.from_text(text=f"""
APPLICATION CONTEXT:
{profile_context()}

CURRENT MODE:
{st.session_state.mode}

MODE INSTRUCTIONS:
{mode_instruction(st.session_state.mode)}

USER MESSAGE:
{user_text}
""")]
    if image_bytes:
        parts.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type or "image/jpeg"))
    contents.append(types.Content(role="user", parts=parts))
    return contents

def ask_seasage(user_text, image_bytes=None, mime_type=None):
    if not client:
        return "I’m ready to come aboard, but my AI connection isn't configured yet. Please add `GEMINI_API_KEY` to Streamlit Secrets."
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=build_contents(user_text, image_bytes, mime_type),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=1800,
            ),
        )
        return (response.text or "I couldn't generate a useful response just now. Try again.").strip()
    except Exception as exc:
        error = str(exc)
        if "404" in error or "not found" in error.lower():
            return f"SeaSage couldn't reach the configured Gemini model `{MODEL_NAME}`. Check that your API key has access to this model."
        if "429" in error or "quota" in error.lower():
            return "I've hit the current Gemini usage limit. Please wait a little and try again."
        return f"SeaSage hit a connection error: {error}"

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

def start_conversation(prompt, mode="chat"):
    st.session_state.mode = mode
    add_message("user", prompt)
    add_message("assistant", ask_seasage(prompt))
    st.rerun()

@st.cache_data(ttl=900)
def get_marine_data(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "wave_height,wave_direction,wave_period,swell_wave_height,swell_wave_direction,ocean_current_velocity,ocean_current_direction,sea_surface_temperature",
        "forecast_days": 3,
        "timezone": "auto",
    }
    response = requests.get(OPEN_METEO_MARINE_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json()

def marine_context(data):
    c = data.get("current", {})
    return f"""
Wave height: {c.get("wave_height", "N/A")} m
Wave direction: {c.get("wave_direction", "N/A")}°
Wave period: {c.get("wave_period", "N/A")} s
Swell height: {c.get("swell_wave_height", "N/A")} m
Current speed: {c.get("ocean_current_velocity", "N/A")} km/h
Current direction: {c.get("ocean_current_direction", "N/A")}°
Sea temperature: {c.get("sea_surface_temperature", "N/A")} °C
"""

with st.sidebar:
    st.markdown("""
    <div style="padding:.6rem 0 1.3rem">
        <div style="font-size:2rem">⚓</div>
        <div style="font-family:Manrope;font-weight:800;font-size:1.35rem">SeaSage</div>
        <div style="font-size:.8rem;opacity:.7">Your AI First Mate</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### Navigate")
    nav = [
        ("⌂  Home", "home"), ("💬  Ask SeaSage", "chat"),
        ("🛥️  My Boat", "boat"), ("🔧  Fix Something", "fix"),
        ("🧭  Plan a Trip", "trip"), ("🌊  Check the Sea", "sea"),
        ("🎓  Teach Me", "learn"), ("🚨  Emergency", "emergency"),
    ]
    for label, mode in nav:
        if st.button(label, use_container_width=True, key=f"nav_{mode}"):
            st.session_state.mode = mode
            st.rerun()
    st.markdown("---")
    p, b = st.session_state.profile, st.session_state.boat
    st.markdown("### Your profile")
    st.caption(f"👤 {p['name'] or 'Sailor profile not complete'}")
    st.caption(f"🎓 {p['experience'] or 'Experience not set'}")
    st.caption(f"🛥️ {b['name'] or b['make_model'] or 'Boat not added'}")
    st.markdown("---")
    if st.button("↻  Start fresh", use_container_width=True):
        st.session_state.messages = []
        st.session_state.mode = "home"
        st.session_state.marine_data = None
        st.rerun()
    st.markdown('<div style="font-size:.7rem;opacity:.55;margin-top:1rem">SeaSage is an AI guide, not a substitute for official navigation, emergency services or qualified marine professionals.</div>', unsafe_allow_html=True)

def onboarding():
    st.markdown('<div class="eyebrow">WELCOME ABOARD</div>', unsafe_allow_html=True)
    st.markdown("<div class=\"hero-title\">Let’s get to know<br>the sailor.</div>", unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">SeaSage gets more useful as it learns about you. This takes about a minute.</div>', unsafe_allow_html=True)
    st.write("")
    with st.form("onboarding_form"):
        name = st.text_input("What should SeaSage call you?", placeholder="e.g. Sagar")
        experiences = ["", "I've never sailed", "I've been on boats but never sailed myself", "I'm comfortable with the basics", "I'm an experienced sailor"]
        goals = ["", "Buy my first boat", "Weekend trips", "Longer passages", "Live aboard", "Cruise around the coast", "I'm still figuring it out"]
        statuses = ["Not bought yet", "Researching boats", "About to buy", "I own a boat", "I live aboard"]
        experience = st.selectbox("How much boating experience do you have?", experiences)
        goal = st.selectbox("What are you hoping to do?", goals)
        boat_status = st.selectbox("Where are you in your boat journey?", statuses)
        if st.form_submit_button("Come aboard →", use_container_width=True):
            st.session_state.profile = {"name": name.strip(), "experience": experience, "goal": goal, "boat_status": boat_status}
            st.session_state.onboarding_complete = True
            greeting = f"Welcome aboard{', ' + name.strip() if name.strip() else ''}. I'm SeaSage. I’ll help you learn the boat, understand what's happening around you, and figure out what to do next."
            st.session_state.messages = [{"role": "assistant", "content": greeting}]
            st.session_state.mode = "home"
            st.rerun()

def home():
    p, b = st.session_state.profile, st.session_state.boat
    greeting = f"Good to see you, {p['name']}." if p["name"] else "Welcome aboard."
    st.markdown('<div class="eyebrow">⚓ YOUR FIRST MATE</div>', unsafe_allow_html=True)
    st.markdown(f"<div class=\"hero-title\">{greeting}<br>What are we doing today?</div>", unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Ask questions, learn your boat, troubleshoot problems, understand the sea, or let SeaSage walk you through something step by step.</div>', unsafe_allow_html=True)
    st.write("")
    actions = [
        ("🛥️", "I'm buying a boat", "Compare boats, inspect listings and understand ownership costs.", "buy"),
        ("🔧", "I need to fix something", "Tell me what's wrong or show me a photo.", "fix"),
        ("🧭", "I'm planning a trip", "Prepare the boat, crew, route and departure checklist.", "trip"),
        ("🌊", "Check the sea", "Look at marine conditions and understand what they mean.", "sea"),
        ("🎓", "Teach me", "Learn boating from zero without drowning in jargon.", "learn"),
        ("🚨", "Something is wrong", "Enter emergency mode and focus on immediate safety.", "emergency"),
    ]
    cols = st.columns(3)
    for i, (icon, title, description, mode) in enumerate(actions):
        with cols[i % 3]:
            st.markdown(f'<div class="sea-card"><div class="card-icon">{icon}</div><div class="card-title">{title}</div><div class="card-description">{description}</div></div>', unsafe_allow_html=True)
            if st.button("Open →", key=f"home_{mode}", use_container_width=True):
                st.session_state.mode = mode
                st.rerun()
        if i % 3 == 2:
            st.write("")
    st.write("")
    st.markdown("### Or just tell me what’s on your mind.")
    prompts = [
        "I know nothing about boats. Where should I start?",
        "What should I check before buying a used sailboat?",
        "Teach me the 10 things every first-time boat owner should know.",
    ]
    cols = st.columns(3)
    for i, prompt in enumerate(prompts):
        with cols[i]:
            if st.button(prompt, key=f"quick_{i}", use_container_width=True):
                start_conversation(prompt)
    if b["name"] or b["make_model"]:
        st.write("")
        st.markdown("### Your boat")
        label = b["name"] or b["make_model"]
        st.markdown(f'<div class="sea-card-dark"><div style="font-size:.75rem;opacity:.65;letter-spacing:.1em">MY BOAT</div><div style="font-family:Manrope;font-size:1.8rem;font-weight:800;margin-top:.4rem">{label}</div><div style="opacity:.75">{b["type"] or "Boat type not set"} {"· " + b["length"] if b["length"] else ""} {"· " + b["year"] if b["year"] else ""}</div></div>', unsafe_allow_html=True)

def boat_page():
    st.markdown('<div class="eyebrow">MY BOAT</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title" style="font-size:3.4rem">Know your boat.</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">The more SeaSage knows about your boat, the more specific its advice becomes.</div>', unsafe_allow_html=True)
    st.write("")
    with st.form("boat_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Boat name", value=st.session_state.boat["name"], placeholder="e.g. Wanderer")
            types_list = ["", "Monohull sailboat", "Catamaran", "Motorboat", "Trawler", "Trimaran", "Other"]
            current_type = st.session_state.boat["type"]
            boat_type = st.selectbox("Boat type", types_list, index=types_list.index(current_type) if current_type in types_list else 0)
            make_model = st.text_input("Make / model", value=st.session_state.boat["make_model"], placeholder="e.g. Beneteau Oceanis 35")
            length = st.text_input("Length", value=st.session_state.boat["length"], placeholder="e.g. 35 ft")
        with c2:
            year = st.text_input("Year", value=st.session_state.boat["year"], placeholder="e.g. 2014")
            engine = st.text_input("Engine", value=st.session_state.boat["engine"], placeholder="e.g. Yanmar diesel")
            location = st.text_input("Usual location", value=st.session_state.boat["location"], placeholder="e.g. Goa, India")
            notes = st.text_area("Anything else SeaSage should know?", value=st.session_state.boat["notes"], placeholder="Known issues, equipment, plans, etc.")
        if st.form_submit_button("Save boat profile", use_container_width=True):
            st.session_state.boat = {"name": name.strip(), "type": boat_type, "make_model": make_model.strip(), "length": length.strip(), "year": year.strip(), "engine": engine.strip(), "location": location.strip(), "notes": notes.strip()}
            st.success("Boat profile saved. SeaSage will use it in future conversations.")
    st.write("")
    st.markdown("### Learn your boat's systems")
    systems = [
        ("🔋", "Electrical", "Batteries, charging, shore power and panels"),
        ("🛢️", "Engine", "Cooling, fuel, oil and basic checks"),
        ("💧", "Water", "Tanks, pumps, plumbing and freshwater"),
        ("⚓", "Anchoring", "Anchor, rode, scope and holding"),
        ("⛵", "Rigging", "Mast, boom, lines and standing rigging"),
        ("🧭", "Navigation", "Charts, instruments, compass and position"),
        ("🚽", "Sanitation", "Toilets, holding tanks and waste systems"),
        ("🛟", "Safety", "PFDs, flares, fire equipment and emergency gear"),
    ]
    cols = st.columns(4)
    for i, (icon, title, description) in enumerate(systems):
        with cols[i % 4]:
            st.markdown(f'<div class="sea-card"><div class="card-icon">{icon}</div><div class="card-title">{title}</div><div class="card-description">{description}</div></div>', unsafe_allow_html=True)
            if st.button("Learn →", key=f"system_{i}", use_container_width=True):
                start_conversation(f"Teach me about the {title.lower()} system on my boat. Assume I'm a first-time boat owner. Start from the basics and tell me what I should know and regularly check.")

def fix_page():
    st.markdown('<div class="eyebrow">TROUBLESHOOTING</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title" style="font-size:3.5rem">Something’s wrong.</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Don’t worry. We’ll work through it one observation at a time. If you can, take a photo of what you’re seeing.</div>', unsafe_allow_html=True)
    st.write("")
    categories = [
        ("💧", "Water / bilge", "Water where it shouldn't be"),
        ("🔥", "Heat / smoke", "Something is hot, smoking or burning"),
        ("⚡", "Electrical", "Power, battery or wiring problem"),
        ("🛢️", "Engine", "Engine won't start, overheats or sounds wrong"),
        ("⛵", "Rigging", "Mast, lines, sails or rigging issue"),
        ("🚽", "Plumbing", "Toilet, pump, tank or freshwater issue"),
        ("🧭", "Navigation", "Instrument or navigation problem"),
        ("❓", "I don't know", "I can't identify the problem"),
    ]
    cols = st.columns(4)
    for i, (icon, title, description) in enumerate(categories):
        with cols[i % 4]:
            st.markdown(f'<div class="sea-card"><div class="card-icon">{icon}</div><div class="card-title">{title}</div><div class="card-description">{description}</div></div>', unsafe_allow_html=True)
            if st.button("Start →", key=f"fix_{i}", use_container_width=True):
                start_conversation(f"I have a {title.lower()} problem on my boat. Help me troubleshoot it step by step. Assume I'm a beginner and prioritise safety.", "fix")
    st.write("")
    st.markdown("### 📷 Show me")
    uploaded = st.file_uploader("Upload a photo of the problem", type=["jpg", "jpeg", "png", "webp"])
    camera = st.camera_input("Or take a photo")
    image = camera if camera is not None else uploaded
    if image:
        image_bytes = image.getvalue()
        mime_type = image.type or "image/jpeg"
        st.image(image_bytes, caption="Photo for SeaSage", use_container_width=True)
        question = st.text_input("What would you like me to look at?", placeholder="e.g. What is this component? Does anything look wrong?")
        if st.button("🔍 Ask SeaSage about this photo", use_container_width=True):
            question = question.strip() or "Look at this photo. What am I probably looking at? Explain it to a complete beginner, tell me what you can identify with confidence, what you cannot identify, and what I should safely check next."
            with st.spinner("SeaSage is looking closely..."):
                answer = ask_seasage(question, image_bytes, mime_type)
            add_message("user", question)
            add_message("assistant", answer)
            st.session_state.mode = "chat"
            st.rerun()

def trip_page():
    st.markdown('<div class="eyebrow">PASSAGE PLANNER</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title" style="font-size:3.5rem">Where are we going?</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">SeaSage will help you think through the trip before you leave.</div>', unsafe_allow_html=True)
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        departure = st.text_input("Departure", placeholder="e.g. Goa")
        destination = st.text_input("Destination", placeholder="e.g. Gokarna")
        distance = st.text_input("Approximate distance", placeholder="e.g. 80 nautical miles")
    with c2:
        departure_time = st.text_input("Planned departure", placeholder="e.g. Tomorrow at 06:00")
        crew = st.text_input("Who is coming?", placeholder="e.g. Me + 2 friends")
        crew_experience = st.selectbox("Crew experience", ["Mostly beginners", "Some sailing experience", "Experienced crew"])
    notes = st.text_area("Anything else?", placeholder="Boat limitations, weather concerns, fuel range, etc.")
    if st.button("🧭 Build my pre-departure plan", use_container_width=True):
        prompt = f"""Help me plan this trip as a first-time sailor.
Departure: {departure}
Destination: {destination}
Approximate distance: {distance}
Planned departure: {departure_time}
Crew: {crew}
Crew experience: {crew_experience}
Additional information: {notes}
Create a practical pre-departure plan covering boat readiness, fuel and water,
safety equipment, weather and sea-state information, navigation, communications,
food/provisions, crew briefing, reasons to postpone and final checks.
Do not pretend to know current weather unless current marine data is supplied."""
        start_conversation(prompt, "trip")

def sea_page():
    st.markdown('<div class="eyebrow">THE SEA</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title" style="font-size:3.5rem">What’s happening out there?</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Enter your approximate position to see marine conditions.</div>', unsafe_allow_html=True)
    st.write("")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        latitude = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=15.49, step=.01, format="%.2f")
    with c2:
        longitude = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=73.83, step=.01, format="%.2f")
    with c3:
        st.write("")
        st.write("")
        if st.button("🌊 Check conditions", use_container_width=True):
            try:
                with st.spinner("Reading the sea..."):
                    st.session_state.marine_data = get_marine_data(latitude, longitude)
            except Exception as exc:
                st.error(f"Couldn't retrieve marine conditions right now: {exc}")
    data = st.session_state.marine_data
    if data:
        c = data.get("current", {})
        metrics = [
            ("🌊", c.get("wave_height"), "Wave height", "m"),
            ("⏱️", c.get("wave_period"), "Wave period", "sec"),
            ("〰️", c.get("swell_wave_height"), "Swell", "m"),
            ("🌡️", c.get("sea_surface_temperature"), "Sea temperature", "°C"),
        ]
        st.write("")
        cols = st.columns(4)
        for i, (icon, value, label, unit) in enumerate(metrics):
            with cols[i]:
                display = "—" if value is None else f"{value} {unit}"
                st.markdown(f'<div class="metric-card"><div>{icon}</div><div class="metric-value">{display}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)
        st.write("")
        st.markdown('<div class="warning-card"><strong>Important:</strong> Marine forecasts are useful for planning and understanding conditions, but they do not replace official navigation information, charts, local warnings or professional judgement.</div>', unsafe_allow_html=True)
        st.write("")
        if st.button("💬 Explain these conditions to me", use_container_width=True):
            prompt = f"""Explain these marine conditions to a first-time sailor:
{marine_context(data)}
Explain what the numbers mean, what deserves attention, what information is missing,
and what the user should check before making a decision. Do not give a definitive
safe/unsafe-to-sail answer without knowing the boat, crew, route and official warnings."""
            start_conversation(prompt)
        if st.button("🧭 What should I check before leaving?", use_container_width=True):
            prompt = f"""Current marine conditions:
{marine_context(data)}
I am a first-time sailor. Do not tell me simply whether I should sail.
Explain what I need to know before making a departure decision and what additional
information you need about my boat, crew and route."""
            start_conversation(prompt)

def learn_page():
    st.markdown('<div class="eyebrow">LEARNING MODE</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title" style="font-size:3.5rem">Teach me.</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">No sailing degree required. Ask anything and we’ll start from where you are.</div>', unsafe_allow_html=True)
    st.write("")
    lessons = [
        ("⚓", "Boat basics", "Learn the parts of a boat and what they do.", "Teach me the basic parts of a boat from zero."),
        ("🧭", "Navigation", "Understand charts, compass, bearings and position.", "Teach me navigation from absolute zero."),
        ("🌬️", "Weather", "Understand wind, waves, swell and forecasts.", "Teach me how a beginner should read marine weather."),
        ("⛵", "Sailing", "Learn sails, points of sail, tacking and gybing.", "Teach me the fundamentals of sailing."),
        ("⚓", "Anchoring", "Learn how to anchor and what can go wrong.", "Teach me anchoring from scratch."),
        ("🔋", "Boat electrical", "Understand batteries, charging and power.", "Teach me boat electrical systems like I know nothing."),
        ("🛢️", "Engine basics", "Understand the engine without becoming a mechanic.", "Teach me the basics of a marine diesel engine."),
        ("🛟", "Safety", "Build your mental emergency checklist.", "Teach me the most important safety knowledge for a new boat owner."),
    ]
    cols = st.columns(4)
    for i, (icon, title, description, prompt) in enumerate(lessons):
        with cols[i % 4]:
            st.markdown(f'<div class="sea-card"><div class="card-icon">{icon}</div><div class="card-title">{title}</div><div class="card-description">{description}</div></div>', unsafe_allow_html=True)
            if st.button("Start lesson →", key=f"lesson_{i}", use_container_width=True):
                start_conversation(prompt, "learn")

def emergency_page():
    st.markdown('<div class="emergency-banner"><h1>🚨 Something is wrong.</h1><div style="opacity:.85">Stay calm. SeaSage will help you focus on the next important action.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="warning-card"><strong>If anyone is in immediate danger:</strong> contact the appropriate emergency or maritime authorities and use your onboard emergency procedures. SeaSage is not an emergency service.</div>', unsafe_allow_html=True)
    st.write("")
    emergencies = [("🔥", "Fire"), ("💧", "Flooding"), ("🧍", "Person overboard"), ("🛢️", "Engine failure"), ("⚡", "Electrical"), ("⛵", "Rigging"), ("🧭", "Steering"), ("🌊", "Severe weather")]
    cols = st.columns(4)
    for i, (icon, title) in enumerate(emergencies):
        with cols[i % 4]:
            if st.button(f"{icon}  {title}", key=f"emergency_{i}", use_container_width=True):
                prompt = f"""EMERGENCY MODE.
The user reports a {title.lower()} emergency.
Give the safest immediate actions first. Keep it short. Do not overwhelm them.
Ask only the most important next question. Encourage appropriate emergency
or maritime assistance. Do not assume missing details."""
                start_conversation(prompt, "emergency")
    st.write("")
    st.markdown("### Or tell me exactly what happened.")
    emergency_text = st.text_area("Describe the situation", placeholder="Example: The engine alarm is sounding and the temperature gauge is rising.", height=130, label_visibility="collapsed")
    if st.button("🚨 Get immediate guidance", use_container_width=True):
        if emergency_text.strip():
            prompt = f"""EMERGENCY MODE.
The user reports:
{emergency_text}
Respond with immediate safety guidance using short numbered steps.
Tell them what not to do if relevant. Ask only the next critical question.
Encourage appropriate emergency/maritime assistance."""
            st.session_state.mode = "emergency"
            add_message("user", emergency_text)
            add_message("assistant", ask_seasage(prompt))
            st.rerun()

def chat_page():
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown('<div class="eyebrow">⚓ SEASAGE</div>', unsafe_allow_html=True)
        st.markdown('<h1 style="font-size:3rem;margin-bottom:.2rem">Your first mate.</h1>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="status-pill"><div class="status-dot"></div> AI online</div>', unsafe_allow_html=True)
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            with st.chat_message("assistant", avatar="⚓"):
                st.markdown(message["content"])
        else:
            with st.chat_message("user", avatar="🧑‍✈️"):
                st.markdown(message["content"])
    if not st.session_state.messages:
        st.markdown('<div class="sea-card"><div class="card-icon">⚓</div><div class="card-title" style="font-size:1.4rem">I’m here.</div><div class="card-description">Tell me what you’re trying to do, what you’re worried about, or what you want to learn.</div></div>', unsafe_allow_html=True)
        st.write("")
        starters = ["I've never owned a boat. Where should I start?", "I'm thinking of buying a used sailboat. What should I inspect?", "Teach me how to anchor properly."]
        cols = st.columns(3)
        for i, prompt in enumerate(starters):
            with cols[i]:
                if st.button(prompt, key=f"starter_{i}", use_container_width=True):
                    start_conversation(prompt)
    user_prompt = st.chat_input("Ask SeaSage anything...")
    if user_prompt:
        add_message("user", user_prompt)
        with st.chat_message("user", avatar="🧑‍✈️"):
            st.markdown(user_prompt)
        with st.chat_message("assistant", avatar="⚓"):
            with st.spinner("SeaSage is thinking..."):
                answer = ask_seasage(user_prompt)
            st.markdown(answer)
        add_message("assistant", answer)

if not st.session_state.onboarding_complete:
    onboarding()
else:
    mode = st.session_state.mode
    if mode == "home":
        home()
    elif mode == "boat":
        boat_page()
    elif mode == "fix":
        fix_page()
    elif mode == "trip":
        trip_page()
    elif mode == "sea":
        sea_page()
    elif mode == "learn":
        learn_page()
    elif mode == "emergency":
        emergency_page()
    elif mode == "chat":
        chat_page()
    else:
        home()
