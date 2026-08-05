import os
import json
import requests
import streamlit as st

from google import genai
from google.genai import types


# ============================================================
# SEASAGE V1 — FIRST MATE
# ============================================================

APP_NAME = "SeaSage"
APP_TAGLINE = "Your first mate for learning, maintaining and living aboard."
MODEL_NAME = "gemini-3.1-flash-lite"
OPEN_METEO_MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SeaSage — Your AI First Mate",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

:root {
    --sea-deep: #071c2c;
    --sea-dark: #0b2638;
    --sea: #0f3b52;
    --sea-light: #dff4f2;
    --foam: #f5faf9;
    --white: #ffffff;
    --text: #102a3a;
    --muted: #6b7f8c;
    --line: #dce8eb;
    --accent: #2bb8ad;
    --accent-dark: #168f88;
    --warning: #d98b2b;
    --danger: #c94343;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 85% 5%, rgba(43,184,173,0.10), transparent 25%),
        linear-gradient(180deg, #f7fbfb 0%, #eef6f6 100%);
    color: var(--text);
}

.block-container {
    max-width: 1280px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: #071c2c;
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] * {
    color: #edf8f7 !important;
}

section[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: 1px solid transparent;
    text-align: left;
    border-radius: 12px;
    min-height: 42px;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.08);
    border-color: rgba(255,255,255,0.08);
}

/* Main headings */

h1, h2, h3 {
    font-family: 'Manrope', sans-serif !important;
    letter-spacing: -0.03em;
}

.hero-title {
    font-family: 'Manrope', sans-serif;
    font-size: clamp(2.4rem, 6vw, 5.4rem);
    line-height: 0.95;
    font-weight: 800;
    letter-spacing: -0.06em;
    color: var(--sea-deep);
    margin-bottom: 1rem;
}

.hero-subtitle {
    font-size: 1.15rem;
    line-height: 1.65;
    max-width: 680px;
    color: var(--muted);
}

.eyebrow {
    display: inline-block;
    background: #dff4f2;
    color: #137b76;
    border-radius: 999px;
    padding: 7px 13px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

/* Cards */

.sea-card {
    background: rgba(255,255,255,0.92);
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 1.4rem;
    box-shadow: 0 8px 30px rgba(7,28,44,0.05);
    height: 100%;
}

.sea-card-dark {
    background: linear-gradient(145deg, #071c2c, #0e3c51);
    color: white;
    border-radius: 24px;
    padding: 1.8rem;
    box-shadow: 0 18px 50px rgba(7,28,44,0.18);
}

.sea-card h3,
.sea-card-dark h3 {
    margin-top: 0;
}

.card-icon {
    font-size: 1.8rem;
    margin-bottom: 0.6rem;
}

.card-title {
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
    font-size: 1.08rem;
    margin-bottom: 0.35rem;
}

.card-description {
    color: var(--muted);
    line-height: 1.5;
    font-size: 0.92rem;
}

/* Buttons */

.stButton > button {
    border-radius: 13px;
    min-height: 48px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 700;
    border: 1px solid var(--line);
    transition: all 0.18s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    border-color: var(--accent);
}

.primary-button .stButton > button {
    background: var(--sea-deep);
    color: white;
    border: none;
}

/* Chat */

[data-testid="stChatMessage"] {
    border-radius: 18px;
}

[data-testid="stChatInput"] {
    border-radius: 16px;
}

/* Status pill */

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 7px 11px;
    background: #e4f7f4;
    color: #157b75;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
}

.status-dot {
    width: 8px;
    height: 8px;
    background: #2bb8ad;
    border-radius: 50%;
}

/* Emergency */

.emergency-banner {
    background: linear-gradient(135deg, #5e1818, #9e2e2e);
    color: white;
    border-radius: 22px;
    padding: 1.7rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 15px 40px rgba(150,30,30,0.18);
}

.emergency-banner h1 {
    color: white !important;
    margin-bottom: 0.3rem;
}

.warning-card {
    background: #fff8ec;
    border: 1px solid #f0d5a6;
    border-radius: 16px;
    padding: 1rem 1.2rem;
}

/* Metrics */

.metric-card {
    background: white;
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 1rem;
    text-align: center;
}

.metric-value {
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
    font-size: 1.55rem;
    color: var(--sea-deep);
}

.metric-label {
    color: var(--muted);
    font-size: 0.76rem;
    margin-top: 0.25rem;
}

/* Progress */

.progress-label {
    color: var(--muted);
    font-size: 0.78rem;
    margin-bottom: 5px;
}

/* Mobile */

@media (max-width: 800px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .hero-title {
        font-size: 3.1rem;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_PROFILE = {
    "name": "",
    "experience": "",
    "goal": "",
    "boat_status": "Not bought yet",
}

DEFAULT_BOAT = {
    "name": "",
    "type": "",
    "make_model": "",
    "length": "",
    "year": "",
    "engine": "",
    "location": "",
    "notes": "",
}

if "profile" not in st.session_state:
    st.session_state.profile = DEFAULT_PROFILE.copy()

if "boat" not in st.session_state:
    st.session_state.boat = DEFAULT_BOAT.copy()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "mode" not in st.session_state:
    st.session_state.mode = "home"

if "onboarding_complete" not in st.session_state:
    st.session_state.onboarding_complete = False

if "marine_data" not in st.session_state:
    st.session_state.marine_data = None

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None


# ============================================================
# GEMINI
# ============================================================

def get_api_key():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    return os.environ.get("GEMINI_API_KEY")


API_KEY = get_api_key()

if API_KEY:
    try:
        client = genai.Client(api_key=API_KEY)
    except Exception as e:
        client = None
        st.error(f"Could not initialise SeaSage AI: {e}")
else:
    client = None


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are SeaSage, an AI first mate and mentor for people who are new to boating,
sailing, boat ownership and living aboard.

Your user may know almost nothing about boats. Never assume knowledge of
nautical terminology.

Your job is not merely to answer questions. Your job is to help the user
understand what is happening, decide what to do next, and learn enough to
become more independent.

PERSONALITY
- Calm.
- Patient.
- Practical.
- Reassuring without being falsely reassuring.
- Experienced-sailor energy without pretending to be a human sailor.
- Never condescending.
- Never unnecessarily technical.
- Explain jargon immediately when it is necessary.
- Speak naturally, like a trusted first mate.
- Prefer short actionable steps over huge walls of text.

DEFAULT RESPONSE STRUCTURE
When the user has a practical problem:
1. Briefly tell them what you think is happening.
2. Tell them the safest immediate action.
3. Give a short numbered checklist.
4. Ask ONE useful follow-up question if necessary.
5. Tell them when to stop and call a qualified professional.

For learning questions:
- Explain the concept simply.
- Give a real-world boat example.
- Tell the user why it matters.
- Then offer the next thing they should learn.

For troubleshooting:
- Never tell a beginner to randomly dismantle equipment.
- Ask them to observe before touching.
- Tell them what to switch off/isolate where appropriate.
- Distinguish between "safe to inspect", "needs caution", and "stop and get professional help".

SAFETY
Safety is more important than completing the user's requested task.

For anything involving:
- fire
- flooding
- gas
- fuel
- electrical systems
- batteries
- propulsion
- steering
- rigging under load
- severe weather
- person overboard
- medical emergencies
- navigation danger

prioritise immediate safety.

If a situation could be life-threatening, do not bury emergency actions beneath a long explanation.

Do not pretend to be a substitute for:
- emergency services
- a qualified marine engineer
- a professional boat surveyor
- a licensed skipper
- official nautical charts
- official navigation warnings
- local maritime authorities

MARINE DATA
If marine data is provided by the application, explain it in plain English.
Do not turn forecast data into false certainty.

The Open-Meteo marine data is useful for orientation and planning but does
not replace official navigation information, nautical charts, local warnings,
or professional judgement.

BUYING A BOAT
If the user is considering buying a boat:
- Ask about intended use, location, experience and budget.
- Separate purchase price from total ownership cost.
- Explain survey, engine, rigging, electrical, plumbing, safety and insurance
  considerations.
- Encourage a professional marine survey before purchase.
- Do not confidently declare a boat "good" or "bad" without enough information.

LIVING ABOARD
Remember that living aboard is not just about the boat.
Discuss:
- water
- power
- waste
- cooking
- sleeping
- ventilation
- weather
- maintenance
- internet/communications
- provisioning
- shore access
- safety
- local laws and marina/anchoring rules

IMAGE ANALYSIS
When the user uploads a photo:
- First describe what you can actually identify.
- Clearly distinguish identification from uncertainty.
- Never claim certainty when the image does not support it.
- If identifying a component, explain what it probably does.
- Then explain what the user should check.
- Never encourage touching hazardous equipment simply to investigate.

EMERGENCY MODE
When emergency mode is active:
- Be concise.
- Give one immediate action at a time.
- Ask only critical questions.
- Encourage the user to contact appropriate emergency/maritime services.
- Do not create false confidence.
- Do not replace emergency services.

IMPORTANT
You are a guide, not an autonomous captain.
When information is missing, ask a focused question instead of inventing facts.

Always adapt to the user's experience level.

If the user says they are a complete beginner, assume they need terminology
explained from scratch.
"""


# ============================================================
# HELPERS
# ============================================================

def profile_context():
    p = st.session_state.profile
    b = st.session_state.boat

    return f"""
USER PROFILE
Name: {p.get('name') or 'Not provided'}
Experience: {p.get('experience') or 'Not provided'}
Primary goal: {p.get('goal') or 'Not provided'}
Boat status: {p.get('boat_status') or 'Not provided'}

BOAT PROFILE
Boat name: {b.get('name') or 'Not provided'}
Type: {b.get('type') or 'Not provided'}
Make/model: {b.get('make_model') or 'Not provided'}
Length: {b.get('length') or 'Not provided'}
Year: {b.get('year') or 'Not provided'}
Engine: {b.get('engine') or 'Not provided'}
Location: {b.get('location') or 'Not provided'}
Notes: {b.get('notes') or 'Not provided'}
"""


def mode_instruction(mode):
    instructions = {
        "chat": """
You are in normal SeaSage First Mate mode.
Help the user with whatever they need.
""",
        "buy": """
You are helping a first-time boat buyer.
Think like a cautious marine surveyor and experienced owner.
Help them compare boats, identify hidden costs and prepare inspection questions.
Do not make a purchase recommendation without sufficient information.
""",
        "fix": """
You are in guided troubleshooting mode.
Do not overwhelm the user.
Diagnose progressively.
Start with safe observations and simple checks.
Do not ask the user to perform dangerous mechanical, electrical or rigging work.
""",
        "trip": """
You are helping plan a boating trip.
Think about boat capability, distance, weather, fuel, water, provisions,
navigation, safety equipment, crew experience and contingency planning.
Do not present forecast data as a guarantee.
""",
        "learn": """
You are teaching a complete beginner.
Use simple analogies and explain nautical terms.
Teach progressively, from fundamentals to practical application.
""",
        "emergency": """
EMERGENCY MODE IS ACTIVE.
Prioritise immediate safety and appropriate emergency/maritime assistance.
Keep responses concise and action-oriented.
Ask only essential questions.
""",
    }

    return instructions.get(mode, instructions["chat"])


def build_contents(user_text, image_bytes=None, mime_type=None):
    contents = []

    # Keep the latest 20 messages to control token use.
    history = st.session_state.messages[-20:]

    for message in history:
        role = "user" if message["role"] == "user" else "model"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=message["content"])],
            )
        )

    current_parts = [
        types.Part.from_text(
            text=f"""
APPLICATION CONTEXT:
{profile_context()}

CURRENT MODE:
{st.session_state.mode}

MODE INSTRUCTIONS:
{mode_instruction(st.session_state.mode)}

USER MESSAGE:
{user_text}
"""
        )
    ]

    if image_bytes:
        current_parts.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type or "image/jpeg",
            )
        )

    contents.append(
        types.Content(
            role="user",
            parts=current_parts,
        )
    )

    return contents


def ask_seasage(user_text, image_bytes=None, mime_type=None):
    if not client:
        return (
            "I’m ready to come aboard, but my AI connection isn't configured yet. "
            "Please add `GEMINI_API_KEY` to Streamlit Secrets."
        )

    contents = build_contents(
        user_text=user_text,
        image_bytes=image_bytes,
        mime_type=mime_type,
    )

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=1800,
            ),
        )

        if response.text:
            return response.text.strip()

        return "I couldn't generate a useful response just now. Try asking me again."

    except Exception as e:
        error = str(e)

        if "404" in error or "not found" in error.lower():
            return (
                "SeaSage couldn't reach the Gemini model. "
                f"The app is configured for `{MODEL_NAME}`. "
                "Please check that your Gemini API key has access to this model."
            )

        if "429" in error or "quota" in error.lower():
            return (
                "I've hit the current Gemini usage limit. "
                "Because SeaSage is running on a free tier, wait a little and try again."
            )

        return f"SeaSage hit a connection error: {error}"


def add_message(role, content):
    st.session_state.messages.append(
        {
            "role": role,
            "content": content,
        }
    )


def start_conversation(prompt):
    answer = ask_seasage(prompt)
    add_message("user", prompt)
    add_message("assistant", answer)
    st.session_state.mode = "chat"
    st.rerun()


# ============================================================
# MARINE DATA
# ============================================================

@st.cache_data(ttl=900)
def get_marine_data(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(
            [
                "wave_height",
                "wave_direction",
                "wave_period",
                "swell_wave_height",
                "swell_wave_direction",
                "ocean_current_velocity",
                "ocean_current_direction",
                "sea_surface_temperature",
            ]
        ),
        "current": ",".join(
            [
                "wave_height",
                "wave_direction",
                "wave_period",
                "swell_wave_height",
                "swell_wave_direction",
                "ocean_current_velocity",
                "ocean_current_direction",
                "sea_surface_temperature",
            ]
        ),
        "forecast_days": 3,
        "timezone": "auto",
    }

    response = requests.get(
        OPEN_METEO_MARINE_URL,
        params=params,
        timeout=15,
    )

    response.raise_for_status()
    return response.json()


def format_marine_data(data):
    if not data:
        return "No marine data available."

    current = data.get("current", {})

    wave = current.get("wave_height")
    wave_dir = current.get("wave_direction")
    wave_period = current.get("wave_period")
    swell = current.get("swell_wave_height")
    current_speed = current.get("ocean_current_velocity")
    current_dir = current.get("ocean_current_direction")
    sea_temp = current.get("sea_surface_temperature")

    return f"""
CURRENT MARINE CONDITIONS
Wave height: {wave if wave is not None else 'N/A'} m
Wave direction: {wave_dir if wave_dir is not None else 'N/A'}°
Wave period: {wave_period if wave_period is not None else 'N/A'} s
Swell height: {swell if swell is not None else 'N/A'} m
Ocean current: {current_speed if current_speed is not None else 'N/A'} km/h
Current direction: {current_dir if current_dir is not None else 'N/A'}°
Sea surface temperature: {sea_temp if sea_temp is not None else 'N/A'} °C
"""


def marine_advice():
    data = st.session_state.marine_data

    if not data:
        return

    context = format_marine_data(data)

    prompt = f"""
The user wants help understanding the current marine conditions.

{context}

Explain these conditions for a first-time sailor.
Do not give a definitive "safe/unsafe to sail" answer without knowing the boat,
crew, route and local conditions.

Focus on:
- what the numbers mean
- what deserves attention
- what information is missing
- what the user should check before making a decision
"""

    answer = ask_seasage(prompt)
    add_message("user", "Explain the current marine conditions to me.")
    add_message("assistant", answer)
    st.session_state.mode = "chat"
    st.rerun()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="padding: 0.6rem 0 1.3rem 0;">
            <div style="font-size:2rem;">⚓</div>
            <div style="font-family:Manrope;font-weight:800;font-size:1.35rem;">
                SeaSage
            </div>
            <div style="font-size:0.8rem;opacity:0.7;">
                Your AI First Mate
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Navigate")

    if st.button("⌂  Home", use_container_width=True):
        st.session_state.mode = "home"
        st.rerun()

    if st.button("💬  Ask SeaSage", use_container_width=True):
        st.session_state.mode = "chat"
        st.rerun()

    if st.button("🛥️  My Boat", use_container_width=True):
        st.session_state.mode = "boat"
        st.rerun()

    if st.button("🔧  Fix Something", use_container_width=True):
        st.session_state.mode = "fix"
        st.rerun()

    if st.button("🧭  Plan a Trip", use_container_width=True):
        st.session_state.mode = "trip"
        st.rerun()

    if st.button("🌊  Check the Sea", use_container_width=True):
        st.session_state.mode = "sea"
        st.rerun()

    if st.button("🎓  Teach Me", use_container_width=True):
        st.session_state.mode = "learn"
        st.rerun()

    st.markdown("---")

    if st.button("🚨  Emergency", use_container_width=True):
        st.session_state.mode = "emergency"
        st.rerun()

    st.markdown("---")

    # Profile summary

    p = st.session_state.profile
    b = st.session_state.boat

    st.markdown("### Your profile")

    if p["name"]:
        st.caption(f"👤 {p['name']}")
    else:
        st.caption("👤 Sailor profile not complete")

    if p["experience"]:
        st.caption(f"🎓 {p['experience']}")

    if b["name"]:
        st.caption(f"🛥️ {b['name']}")
    elif b["make_model"]:
        st.caption(f"🛥️ {b['make_model']}")
    else:
        st.caption("🛥️ Boat not added")

    st.markdown("---")

    if st.button("↻  Start fresh", use_container_width=True):
        st.session_state.messages = []
        st.session_state.mode = "home"
        st.session_state.marine_data = None
        st.rerun()

    st.markdown(
        """
        <div style="font-size:0.7rem;opacity:0.55;margin-top:1rem;">
        SeaSage is an AI guide, not a substitute for official navigation,
        emergency services or qualified marine professionals.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# ONBOARDING
# ============================================================

def onboarding():

    st.markdown(
        '<div class="eyebrow">WELCOME ABOARD</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero-title">Let’s get to know<br>the sailor.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-subtitle">
        SeaSage gets more useful as it learns about you.
        This takes about a minute.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    with st.form("onboarding_form"):

        name = st.text_input(
            "What should SeaSage call you?",
            value=st.session_state.profile["name"],
            placeholder="e.g. Sagar",
        )

        experience = st.selectbox(
            "How much boating experience do you have?",
            [
                "",
                "I've never sailed",
                "I've been on boats but never sailed myself",
                "I'm comfortable with the basics",
                "I'm an experienced sailor",
            ],
            index=0
            if not st.session_state.profile["experience"]
            else [
                "",
                "I've never sailed",
                "I've been on boats but never sailed myself",
                "I'm comfortable with the basics",
                "I'm an experienced sailor",
            ].index(st.session_state.profile["experience"]),
        )

        goal = st.selectbox(
            "What are you hoping to do?",
            [
                "",
                "Buy my first boat",
                "Weekend trips",
                "Longer passages",
                "Live aboard",
                "Cruise around the coast",
                "I'm still figuring it out",
            ],
            index=0
            if not st.session_state.profile["goal"]
            else [
                "",
                "Buy my first boat",
                "Weekend trips",
                "Longer passages",
                "Live aboard",
                "Cruise around the coast",
                "I'm still figuring it out",
            ].index(st.session_state.profile["goal"]),
        )

        boat_status = st.selectbox(
            "Where are you in your boat journey?",
            [
                "Not bought yet",
                "Researching boats",
                "About to buy",
                "I own a boat",
                "I live aboard",
            ],
            index=[
                "Not bought yet",
                "Researching boats",
                "About to buy",
                "I own a boat",
                "I live aboard",
            ].index(st.session_state.profile["boat_status"]),
        )

        submitted = st.form_submit_button(
            "Come aboard →",
            use_container_width=True,
        )

        if submitted:

            st.session_state.profile = {
                "name": name.strip(),
                "experience": experience,
                "goal": goal,
                "boat_status": boat_status,
            }

            st.session_state.onboarding_complete = True

            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": (
                        f"Welcome aboard"
                        + (f", {name.strip()}" if name.strip() else "")
                        + ". I'm SeaSage. "
                        "I’ll help you learn the boat, understand what's happening "
                        "around you, and figure out what to do next."
                    ),
                }
            ]

            st.session_state.mode = "home"
            st.rerun()


# ============================================================
# HOME
# ============================================================

def home():

    p = st.session_state.profile
    b = st.session_state.boat

    greeting = f"Good to see you, {p['name']}." if p["name"] else "Welcome aboard."

    st.markdown(
        '<div class="eyebrow">⚓ YOUR FIRST MATE</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="hero-title">{greeting}<br>What are we doing today?</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-subtitle">
        Ask questions, learn your boat, troubleshoot problems, understand the sea,
        or let SeaSage walk you through something step by step.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    # Main actions

    actions = [
        (
            "🛥️",
            "I'm buying a boat",
            "Compare boats, inspect listings and understand ownership costs.",
            "buy",
        ),
        (
            "🔧",
            "I need to fix something",
            "Tell me what's wrong or show me a photo.",
            "fix",
        ),
        (
            "🧭",
            "I'm planning a trip",
            "Prepare the boat, crew, route and departure checklist.",
            "trip",
        ),
        (
            "🌊",
            "Check the sea",
            "Look at marine conditions and understand what they mean.",
            "sea",
        ),
        (
            "🎓",
            "Teach me",
            "Learn boating from zero without drowning in jargon.",
            "learn",
        ),
        (
            "🚨",
            "Something is wrong",
            "Enter emergency mode and focus on immediate safety.",
            "emergency",
        ),
    ]

    cols = st.columns(3, gap="medium")

    for i, (icon, title, description, mode) in enumerate(actions):

        with cols[i % 3]:

            st.markdown(
                f"""
                <div class="sea-card">
                    <div class="card-icon">{icon}</div>
                    <div class="card-title">{title}</div>
                    <div class="card-description">{description}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                "Open →",
                key=f"home_action_{mode}",
                use_container_width=True,
            ):
                st.session_state.mode = mode
                st.rerun()

        if i % 3 == 2:
            st.write("")

    st.write("")

    # Quick-start prompts

    st.markdown("### Or just tell me what’s on your mind.")

    quick_cols = st.columns(3)

    prompts = [
        "I know nothing about boats. Where should I start?",
        "What should I check before buying a used sailboat?",
        "Teach me the 10 things every first-time boat owner should know.",
    ]

    for i, prompt in enumerate(prompts):
        with quick_cols[i]:
            if st.button(
                prompt,
                key=f"quick_{i}",
                use_container_width=True,
            ):
                start_conversation(prompt)

    st.write("")

    # Profile card

    if b["name"] or b["make_model"]:

        st.markdown("### Your boat")

        boat_label = b["name"] or b["make_model"]

        st.markdown(
            f"""
            <div class="sea-card-dark">
                <div style="font-size:0.75rem;opacity:0.65;text-transform:uppercase;
                letter-spacing:0.1em;">MY BOAT</div>
                <div style="font-family:Manrope;font-size:1.8rem;font-weight:800;
                margin-top:0.4rem;">{boat_label}</div>
                <div style="opacity:0.75;margin-top:0.4rem;">
                    {b["type"] or "Boat type not set"}
                    {" · " + b["length"] if b["length"] else ""}
                    {" · " + b["year"] if b["year"] else ""}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# MY BOAT
# ============================================================

def boat_page():

    st.markdown('<div class="eyebrow">MY BOAT</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="hero-title" style="font-size:3.4rem;">Know your boat.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-subtitle">
        The more SeaSage knows about your boat, the more specific its advice becomes.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    with st.form("boat_form"):

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input(
                "Boat name",
                value=st.session_state.boat["name"],
                placeholder="e.g. Wanderer",
            )

            boat_type = st.selectbox(
                "Boat type",
                [
                    "",
                    "Monohull sailboat",
                    "Catamaran",
                    "Motorboat",
                    "Trawler",
                    "Trimaran",
                    "Other",
                ],
                index=0
                if not st.session_state.boat["type"]
                else [
                    "",
                    "Monohull sailboat",
                    "Catamaran",
                    "Motorboat",
                    "Trawler",
                    "Trimaran",
                    "Other",
                ].index(st.session_state.boat["type"]),
            )

            make_model = st.text_input(
                "Make / model",
                value=st.session_state.boat["make_model"],
                placeholder="e.g. Beneteau Oceanis 35",
            )

            length = st.text_input(
                "Length",
                value=st.session_state.boat["length"],
                placeholder="e.g. 35 ft",
            )

        with col2:

            year = st.text_input(
                "Year",
                value=st.session_state.boat["year"],
                placeholder="e.g. 2014",
            )

            engine = st.text_input(
                "Engine",
                value=st.session_state.boat["engine"],
                placeholder="e.g. Yanmar diesel",
            )

            location = st.text_input(
                "Usual location",
                value=st.session_state.boat["location"],
                placeholder="e.g. Goa, India",
            )

            notes = st.text_area(
                "Anything else SeaSage should know?",
                value=st.session_state.boat["notes"],
                placeholder="Known issues, equipment, plans, etc.",
            )

        saved = st.form_submit_button(
            "Save boat profile",
            use_container_width=True,
        )

        if saved:

            st.session_state.boat = {
                "name": name.strip(),
                "type": boat_type,
                "make_model": make_model.strip(),
                "length": length.strip(),
                "year": year.strip(),
                "engine": engine.strip(),
                "location": location.strip(),
                "notes": notes.strip(),
            }

            st.success("Boat profile saved. SeaSage will use it in future conversations.")

    st.write("")

    # Boat systems

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

            st.markdown(
                f"""
                <div class="sea-card">
                    <div class="card-icon">{icon}</div>
                    <div class="card-title">{title}</div>
                    <div class="card-description">{description}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                f"Learn →",
                key=f"system_{title}",
                use_container_width=True,
            ):
                prompt = (
                    f"Teach me about the {title.lower()} system on my boat. "
                    "Assume I'm a first-time boat owner. Start from the basics "
                    "and tell me what I should know and regularly check."
                )
                start_conversation(prompt)


# ============================================================
# FIX PAGE
# ============================================================

def fix_page():

    st.markdown('<div class="eyebrow">TROUBLESHOOTING</div>', unsafe_allow_html=True)

    st.markdown(
       "<div class=\"hero-title\" style=\"font-size:3.5rem;\">Something's wrong.</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-subtitle">
        Don't worry. We'll work through it one observation at a time.
        If you can, take a photo of what you're seeing.
        </div>
        """,
        unsafe_allow_html=True,
    )

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

            st.markdown(
                f"""
                <div class="sea-card">
                    <div class="card-icon">{icon}</div>
                    <div class="card-title">{title}</div>
                    <div class="card-description">{description}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                "Start →",
                key=f"fix_{i}",
                use_container_width=True,
            ):

                prompt = (
                    f"I have a {title.lower()} problem on my boat. "
                    "Help me troubleshoot it step by step. "
                    "Assume I'm a beginner and prioritise safety."
                )

                st.session_state.mode = "chat"
                add_message("user", prompt)
                st.rerun()

    st.write("")

    st.markdown("### 📷 Show me")

    uploaded = st.file_uploader(
        "Upload a photo of the problem",
        type=["jpg", "jpeg", "png", "webp"],
        key="problem_photo",
    )

    camera = st.camera_input(
        "Or take a photo",
        key="problem_camera",
    )

    image = camera if camera is not None else uploaded

    if image:

        image_bytes = image.getvalue()
        mime_type = image.type or "image/jpeg"

        st.image(image_bytes, caption="Photo for SeaSage", use_container_width=True)

        question = st.text_input(
            "What would you like me to look at?",
            placeholder="e.g. What is this component? Does anything look wrong?",
            key="image_question",
        )

        if st.button(
            "🔍 Ask SeaSage about this photo",
            use_container_width=True,
        ):

            if not question.strip():
                question = (
                    "Look at this photo. What am I probably looking at? "
                    "Explain it to a complete beginner, tell me what you can "
                    "identify with confidence, what you cannot identify, and "
                    "what I should safely check next."
                )

            with st.spinner("SeaSage is looking closely..."):

                answer = ask_seasage(
                    question,
                    image_bytes=image_bytes,
                    mime_type=mime_type,
                )

            add_message("user", question)
            add_message("assistant", answer)

            st.session_state.mode = "chat"
            st.rerun()


# ============================================================
# TRIP PAGE
# ============================================================

def trip_page():

    st.markdown('<div class="eyebrow">PASSAGE PLANNER</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="hero-title" style="font-size:3.5rem;">Where are we going?</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-subtitle">
        SeaSage will help you think through the trip before you leave.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    col1, col2 = st.columns(2)

    with col1:

        departure = st.text_input(
            "Departure",
            placeholder="e.g. Goa",
        )

        destination = st.text_input(
            "Destination",
            placeholder="e.g. Gokarna",
        )

        distance = st.text_input(
            "Approximate distance",
            placeholder="e.g. 80 nautical miles",
        )

    with col2:

        departure_time = st.text_input(
            "Planned departure",
            placeholder="e.g. Tomorrow at 06:00",
        )

        crew = st.text_input(
            "Who is coming?",
            placeholder="e.g. Me + 2 friends",
        )

        experience = st.selectbox(
            "Crew experience",
            [
                "Mostly beginners",
                "Some sailing experience",
                "Experienced crew",
            ],
        )

    notes = st.text_area(
        "Anything else?",
        placeholder="Boat limitations, weather concerns, fuel range, etc.",
    )

    if st.button(
        "🧭 Build my pre-departure plan",
        use_container_width=True,
    ):

        prompt = f"""
Help me plan this trip as a first-time sailor.

Departure: {departure}
Destination: {destination}
Approximate distance: {distance}
Planned departure: {departure_time}
Crew: {crew}
Crew experience: {experience}
Additional information: {notes}

Create a practical pre-departure plan covering:
1. Boat readiness
2. Fuel and water
3. Safety equipment
4. Weather and sea-state information I need
5. Navigation
6. Communications
7. Food/provisions
8. Crew briefing
9. What could make us postpone
10. What to check immediately before departure

Do not pretend to know current weather unless current marine data is supplied.
"""

        start_conversation(prompt)


# ============================================================
# SEA PAGE
# ============================================================

def sea_page():

    st.markdown('<div class="eyebrow">THE SEA</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="hero-title" style="font-size:3.5rem;">What's happening out there?</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-subtitle">
        Enter your approximate position to see marine conditions.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        latitude = st.number_input(
            "Latitude",
            min_value=-90.0,
            max_value=90.0,
            value=15.49,
            step=0.01,
            format="%.2f",
        )

    with col2:
        longitude = st.number_input(
            "Longitude",
            min_value=-180.0,
            max_value=180.0,
            value=73.83,
            step=0.01,
            format="%.2f",
        )

    with col3:

        st.write("")
        st.write("")

        if st.button(
            "🌊 Check conditions",
            use_container_width=True,
        ):

            try:

                with st.spinner("Reading the sea..."):

                    data = get_marine_data(
                        latitude,
                        longitude,
                    )

                st.session_state.marine_data = data

            except Exception as e:

                st.error(
                    f"Couldn't retrieve marine conditions right now: {e}"
                )

    if st.session_state.marine_data:

        current = st.session_state.marine_data.get("current", {})

        wave = current.get("wave_height")
        period = current.get("wave_period")
        swell = current.get("swell_wave_height")
        temp = current.get("sea_surface_temperature")

        st.write("")

        metrics = [
            ("🌊", wave, "Wave height", "m"),
            ("⏱️", period, "Wave period", "sec"),
            ("〰️", swell, "Swell", "m"),
            ("🌡️", temp, "Sea temperature", "°C"),
        ]

        cols = st.columns(4)

        for i, (icon, value, label, unit) in enumerate(metrics):

            with cols[i]:

                display = "—" if value is None else f"{value} {unit}"

                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div>{icon}</div>
                        <div class="metric-value">{display}</div>
                        <div class="metric-label">{label}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.write("")

        st.markdown(
            """
            <div class="warning-card">
            <strong>Important:</strong> Marine forecasts are useful for planning
            and understanding conditions, but they do not replace official
            navigation information, charts, local warnings or professional
            judgement.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        if st.button(
            "💬 Explain these conditions to me",
            use_container_width=True,
        ):

            marine_advice()

        if st.button(
            "🧭 Help me decide what I should check before leaving",
            use_container_width=True,
        ):

            prompt = f"""
Here are the current marine conditions:

{format_marine_data(st.session_state.marine_data)}

I am a first-time sailor.

Do not tell me simply whether I should sail or not.
Instead, explain what I need to know before making a departure decision.
Tell me what additional information you need about my boat, crew and route.
"""

            start_conversation(prompt)


# ============================================================
# LEARN PAGE
# ============================================================

def learn_page():

    st.markdown('<div class="eyebrow">LEARNING MODE</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="hero-title" style="font-size:3.5rem;">Teach me.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-subtitle">
        No sailing degree required. Ask anything and we'll start from where you are.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    lessons = [
        (
            "⚓",
            "Boat basics",
            "Learn the parts of a boat and what they do.",
            "Teach me the basic parts of a boat from zero.",
        ),
        (
            "🧭",
            "Navigation",
            "Understand charts, compass, bearings and position.",
            "Teach me navigation from absolute zero.",
        ),
        (
            "🌬️",
            "Weather",
            "Understand wind, waves, swell and forecasts.",
            "Teach me how a beginner should read marine weather.",
        ),
        (
            "⛵",
            "Sailing",
            "Learn sails, points of sail, tacking and gybing.",
            "Teach me the fundamentals of sailing.",
        ),
        (
            "⚓",
            "Anchoring",
            "Learn how to anchor and what can go wrong.",
            "Teach me anchoring from scratch.",
        ),
        (
            "🔋",
            "Boat electrical",
            "Understand batteries, charging and power.",
            "Teach me boat electrical systems like I know nothing.",
        ),
        (
            "🛢️",
            "Engine basics",
            "Understand the engine without becoming a mechanic.",
            "Teach me the basics of a marine diesel engine.",
        ),
        (
            "🛟",
            "Safety",
            "Build your mental emergency checklist.",
            "Teach me the most important safety knowledge for a new boat owner.",
        ),
    ]

    cols = st.columns(4)

    for i, (icon, title, description, prompt) in enumerate(lessons):

        with cols[i % 4]:

            st.markdown(
                f"""
                <div class="sea-card">
                    <div class="card-icon">{icon}</div>
                    <div class="card-title">{title}</div>
                    <div class="card-description">{description}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                "Start lesson →",
                key=f"lesson_{i}",
                use_container_width=True,
            ):
                start_conversation(prompt)


# ============================================================
# EMERGENCY PAGE
# ============================================================

def emergency_page():

    st.markdown(
        """
        <div class="emergency-banner">
            <h1>🚨 Something is wrong.</h1>
            <div style="opacity:0.85;">
            Stay calm. SeaSage will help you focus on the next important action.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="warning-card">
        <strong>If anyone is in immediate danger:</strong>
        contact the appropriate emergency or maritime authorities and use your
        onboard emergency procedures. SeaSage is not an emergency service.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    emergencies = [
        ("🔥", "Fire"),
        ("💧", "Flooding"),
        ("🧍", "Person overboard"),
        ("🛢️", "Engine failure"),
        ("⚡", "Electrical"),
        ("⛵", "Rigging"),
        ("🧭", "Steering"),
        ("🌊", "Severe weather"),
    ]

    cols = st.columns(4)

    for i, (icon, title) in enumerate(emergencies):

        with cols[i % 4]:

            if st.button(
                f"{icon}  {title}",
                key=f"emergency_{i}",
                use_container_width=True,
            ):

                prompt = f"""
EMERGENCY MODE.

The user says they have a {title.lower()} emergency.

Respond with the safest immediate actions first.
Keep the response short.
Do not overwhelm them.
Ask only the most important next question.
Encourage appropriate emergency/maritime assistance.

Do not assume details that the user has not provided.
"""

                st.session_state.mode = "chat"
                add_message("user", prompt)
                st.rerun()

    st.write("")

    st.markdown("### Or tell me exactly what happened.")

    emergency_text = st.text_area(
        "Describe the situation",
        placeholder="Example: The engine alarm is sounding and the temperature gauge is rising.",
        height=130,
        label_visibility="collapsed",
    )

    if st.button(
        "🚨 Get immediate guidance",
        use_container_width=True,
    ):

        if emergency_text.strip():

            prompt = f"""
EMERGENCY MODE.

The user reports:

{emergency_text}

Respond with immediate safety guidance.
Use short numbered steps.
Tell them what not to do if relevant.
Ask only the next critical question.
Encourage appropriate emergency/maritime assistance.
"""

            answer = ask_seasage(prompt)

            add_message("user", emergency_text)
            add_message("assistant", answer)

            st.session_state.mode = "chat"
            st.rerun()


# ============================================================
# CHAT PAGE
# ============================================================

def chat_page():

    # Header

    col1, col2 = st.columns([4, 1])

    with col1:

        st.markdown(
            '<div class="eyebrow">⚓ SEASAGE</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<h1 style="font-size:3rem;margin-bottom:0.2rem;">Your first mate.</h1>',
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            """
            <div class="status-pill">
                <div class="status-dot"></div>
                AI online
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Show messages

    for message in st.session_state.messages:

        role = message["role"]

        if role == "assistant":
            with st.chat_message("assistant", avatar="⚓"):
                st.markdown(message["content"])

        else:
            with st.chat_message("user", avatar="🧑‍✈️"):
                st.markdown(message["content"])

    # Starter state

    if not st.session_state.messages:

        st.markdown(
            """
            <div class="sea-card">
                <div class="card-icon">⚓</div>
                <div class="card-title" style="font-size:1.4rem;">
                    I'm here.
                </div>
                <div class="card-description">
                    Tell me what you're trying to do, what you're worried about,
                    or what you want to learn.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        starter_cols = st.columns(3)

        starters = [
            "I've never owned a boat. Where should I start?",
            "I'm thinking of buying a used sailboat. What should I inspect?",
            "Teach me how to anchor properly.",
        ]

        for i, prompt in enumerate(starters):

            with starter_cols[i]:

                if st.button(
                    prompt,
                    key=f"chat_starter_{i}",
                    use_container_width=True,
                ):
                    start_conversation(prompt)

    # Chat input

    user_prompt = st.chat_input(
        "Ask SeaSage anything..."
    )

    if user_prompt:

        add_message("user", user_prompt)

        with st.chat_message("user", avatar="🧑‍✈️"):
            st.markdown(user_prompt)

        with st.chat_message("assistant", avatar="⚓"):

            with st.spinner("SeaSage is thinking..."):

                answer = ask_seasage(user_prompt)

            st.markdown(answer)

        add_message("assistant", answer)


# ============================================================
# ROUTER
# ============================================================

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
