import os
import html
import requests
import streamlit as st
from google import genai
from google.genai import types

# ============================================================
# SEASAGE — A first mate for people learning their first boat
# ============================================================

st.set_page_config(
    page_title="SeaSage — Your First Mate",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------- DESIGN -----------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@700;800&display=swap');

:root {
  --ink:#102a35;
  --navy:#082631;
  --navy-2:#0d3948;
  --sea:#0d8b87;
  --sea-soft:#e5f3f1;
  --cream:#f7f5ef;
  --paper:#ffffff;
  --muted:#71828a;
  --line:#dfe7e7;
  --sand:#d9b77b;
  --danger:#a63e36;
}

html, body, [class*="css"] {
  font-family:"DM Sans", sans-serif !important;
}

.stApp {
  background:
    radial-gradient(circle at 10% 0%, rgba(13,139,135,.08), transparent 27rem),
    linear-gradient(180deg,#fbfcfa 0%,#f3f7f5 100%);
  color:var(--ink);
}

.block-container {
  max-width:1180px;
  padding:1.25rem 1.25rem 5rem;
}

header[data-testid="stHeader"] {
  background:transparent;
}

#MainMenu, footer {
  visibility:hidden;
}

/* ---------- logo ---------- */

.ss-logo {
  display:flex;
  align-items:center;
  gap:10px;
  text-decoration:none;
}
.ss-mark {
  width:42px;
  height:42px;
  border-radius:13px;
  background:var(--navy);
  display:flex;
  align-items:center;
  justify-content:center;
  box-shadow:0 8px 20px rgba(8,38,49,.14);
}
.ss-word {
  font-family:"Manrope",sans-serif;
  font-weight:800;
  font-size:1.13rem;
  letter-spacing:-.04em;
  color:var(--navy) !important;
}
.ss-word span { color:var(--sea) !important; }

/* ---------- typography ---------- */

.eyebrow {
  color:var(--sea) !important;
  font-size:.7rem;
  font-weight:800;
  letter-spacing:.13em;
  text-transform:uppercase;
}

.hero {
  max-width:900px;
  padding:3.2rem 0 2.3rem;
}

.hero h1 {
  margin:.55rem 0 1rem;
  font-family:"Manrope",sans-serif !important;
  font-size:clamp(3rem,7vw,6.3rem);
  line-height:.9;
  letter-spacing:-.075em;
  color:var(--navy) !important;
}

.hero p {
  max-width:690px;
  margin:0;
  color:var(--muted) !important;
  font-size:1.05rem;
  line-height:1.7;
}

.page-title {
  font-family:"Manrope",sans-serif !important;
  font-size:clamp(2.3rem,5vw,4.3rem);
  line-height:.95;
  letter-spacing:-.06em;
  color:var(--navy) !important;
  margin:.5rem 0 1rem;
}

.lead {
  color:var(--muted) !important;
  font-size:1rem;
  line-height:1.65;
  max-width:720px;
}

/* ---------- cards ---------- */

.mode-card {
  min-height:210px;
  background:rgba(255,255,255,.86);
  border:1px solid var(--line);
  border-radius:24px;
  padding:1.35rem;
  box-shadow:0 12px 35px rgba(8,38,49,.045);
  margin-bottom:.75rem;
}

.mode-number {
  color:#9aa8aa !important;
  font-size:.7rem;
  font-weight:800;
  letter-spacing:.1em;
}

.mode-icon {
  margin:1.15rem 0 .8rem;
  width:42px;
  height:42px;
  border-radius:13px;
  background:var(--sea-soft);
  display:flex;
  align-items:center;
  justify-content:center;
  color:var(--sea) !important;
  font-weight:800;
  font-size:1.15rem;
}

.mode-title {
  font-family:"Manrope",sans-serif;
  color:var(--navy) !important;
  font-size:1.1rem;
  font-weight:800;
  letter-spacing:-.025em;
}

.mode-desc {
  color:var(--muted) !important;
  line-height:1.5;
  font-size:.86rem;
  margin-top:.35rem;
}

/* ---------- chat ---------- */

.chat-shell {
  max-width:850px;
  margin:0 auto;
}

.chat-header {
  background:var(--navy);
  color:#fff;
  border-radius:24px;
  padding:1.35rem 1.5rem;
  margin:1rem 0 1.2rem;
}

.chat-header * { color:#fff !important; }

.chat-kicker {
  font-size:.68rem;
  font-weight:800;
  letter-spacing:.12em;
  opacity:.65;
  text-transform:uppercase;
}

.chat-title {
  font-family:"Manrope";
  font-size:1.5rem;
  font-weight:800;
  margin-top:.25rem;
}

.chat-sub {
  opacity:.72;
  font-size:.88rem;
  margin-top:.25rem;
}

.step-chip {
  display:inline-block;
  padding:5px 9px;
  border-radius:99px;
  background:var(--sea-soft);
  color:#14706d !important;
  font-size:.7rem;
  font-weight:800;
  margin:.15rem .2rem .15rem 0;
}

/* ---------- visual cards ---------- */

.visual-card {
  border:1px solid var(--line);
  background:#fff;
  border-radius:20px;
  padding:1rem;
  margin:.8rem 0 1rem;
}

.visual-label {
  color:var(--muted) !important;
  text-transform:uppercase;
  letter-spacing:.1em;
  font-size:.64rem;
  font-weight:800;
  margin-bottom:.5rem;
}

/* ---------- info blocks ---------- */

.info {
  background:var(--sea-soft);
  border:1px solid #cbe6e3;
  border-radius:18px;
  padding:1rem 1.1rem;
  color:#214c50 !important;
  margin:.75rem 0;
}
.info * { color:#214c50 !important; }

.warning {
  background:#fff5e7;
  border:1px solid #eedbb8;
  border-radius:18px;
  padding:1rem 1.1rem;
  color:#684d25 !important;
}
.warning * { color:#684d25 !important; }

/* ---------- buttons ---------- */

.stButton > button {
  min-height:44px;
  border-radius:12px;
  border:1px solid var(--line);
  background:#fff;
  color:var(--navy) !important;
  font-weight:700;
  box-shadow:none;
  transition:.15s ease;
}
.stButton > button:hover {
  border-color:var(--sea);
  transform:translateY(-1px);
}
.stButton > button[kind="primary"] {
  background:var(--navy) !important;
  color:#fff !important;
  border-color:var(--navy) !important;
}

/* ---------- inputs ---------- */

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
  color:var(--ink) !important;
  background:#fff !important;
  -webkit-text-fill-color:var(--ink) !important;
  border-radius:12px !important;
}

[data-baseweb="select"] > div {
  background:#fff !important;
  color:var(--ink) !important;
  border-color:var(--line) !important;
}

[data-baseweb="select"] * {
  color:var(--ink) !important;
}

[data-testid="stChatInput"] {
  max-width:850px;
  margin:auto;
}

[data-testid="stChatInput"] textarea {
  color:var(--ink) !important;
  background:#fff !important;
  -webkit-text-fill-color:var(--ink) !important;
}

[data-testid="stChatMessage"] {
  border-radius:18px;
  border:1px solid var(--line);
  margin:.5rem 0;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] strong {
  color:var(--ink) !important;
  line-height:1.65;
}

/* ---------- mobile ---------- */

@media(max-width:700px) {
  .block-container {
    padding:0.8rem .75rem 4rem;
  }

  .hero {
    padding:2.2rem 0 1.5rem;
  }

  .hero h1 {
    font-size:3.25rem;
  }

  .page-title {
    font-size:2.65rem;
  }

  .mode-card {
    min-height:165px;
    padding:1rem;
    border-radius:19px;
  }

  .mode-icon {
    margin:.7rem 0 .55rem;
  }

  .chat-header {
    border-radius:18px;
    padding:1rem;
  }

  .stButton > button {
    min-height:48px;
  }

  [data-testid="stChatInput"] {
    padding-bottom:.5rem;
  }
}
</style>
""", unsafe_allow_html=True)

# ----------------------------- STATE -----------------------------

DEFAULT_BOAT = {
    "name":"",
    "type":"",
    "make_model":"",
    "year":"",
    "length":"",
    "engine":"",
    "engine_hours":"",
    "location":"",
    "notes":"",
}

MODES = {
    "general": {
        "title":"Ask SeaSage",
        "subtitle":"Anything about boats, sailing, repairs or life afloat.",
        "kicker":"FIRST MATE",
    },
    "repair": {
        "title":"Fix something",
        "subtitle":"Diagnose it, open it, understand it and repair it step by step.",
        "kicker":"WORKSHOP",
    },
    "boat": {
        "title":"Understand my boat",
        "subtitle":"Learn what is on your boat and what every system does.",
        "kicker":"BOAT SCHOOL",
    },
    "trip": {
        "title":"Go somewhere",
        "subtitle":"Prepare the boat and yourself before you leave the dock.",
        "kicker":"PASSAGE PLANNING",
    },
    "learn": {
        "title":"Learn by doing",
        "subtitle":"Short lessons followed by something you can actually find or do on your boat.",
        "kicker":"LEARN",
    },
}

if "mode" not in st.session_state:
    st.session_state.mode = "general"

if "boat" not in st.session_state:
    st.session_state.boat = DEFAULT_BOAT.copy()

if "threads" not in st.session_state:
    st.session_state.threads = {key: [] for key in MODES}

if "starter" not in st.session_state:
    st.session_state.starter = None

# ----------------------------- LOGO -----------------------------

def logo():
    st.markdown("""
    <div class="ss-logo">
      <div class="ss-mark">
        <svg width="27" height="27" viewBox="0 0 40 40" fill="none">
          <path d="M8 24.5C11.8 27.7 16 29.3 20.5 29.3C25.4 29.3 29.8 27.5 33 24.1"
                stroke="#7CD4CF" stroke-width="2.7" stroke-linecap="round"/>
          <path d="M20 7V25M20 9L30.5 15.3H20V9Z"
                stroke="white" stroke-width="2.4" stroke-linejoin="round"/>
          <path d="M9 31C12.7 33.3 16.5 34.3 20.5 34.3C24.7 34.3 28.2 33.2 31 31"
                stroke="#D9B77B" stroke-width="2.1" stroke-linecap="round"/>
        </svg>
      </div>
      <div class="ss-word">Sea<span>Sage</span></div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------- GEMINI -----------------------------

def get_api_key():
    try:
        key = st.secrets.get("GEMINI_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY")

API_KEY = get_api_key()

if not API_KEY:
    st.error("SeaSage needs GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

@st.cache_resource
def get_client(key):
    return genai.Client(api_key=key)

client = get_client(API_KEY)

@st.cache_resource
def get_model(key):
    c = genai.Client(api_key=key)
    preferred = [
        "gemini-3.1-flash-lite",
        "gemini-3-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
    ]
    try:
        available = []
        for m in c.models.list():
            name = getattr(m, "name", "")
            actions = getattr(m, "supported_actions", []) or []
            if name and ("generateContent" in actions or not actions):
                available.append(name.replace("models/", ""))
        for model in preferred:
            if model in available:
                return model
        if available:
            return available[0]
    except Exception:
        pass
    return "gemini-2.5-flash"

MODEL = get_model(API_KEY)

# ----------------------------- BRAIN -----------------------------

SYSTEM = """
You are SeaSage: an experienced sailor, boat owner, marine repair mentor,
and patient first mate for a person who may know absolutely nothing about boats.

The user is allowed to learn by doing. They can open panels, remove covers,
trace wires, inspect hoses, clean parts, test components, replace serviceable
parts and carry out sensible maintenance themselves. Do not reflexively tell
them to hire a professional.

Your tone is calm, practical and experienced — like someone standing beside
the user on the dock.

IMPORTANT:
- Use plain English.
- Explain nautical terms when they first appear.
- Do not make the user feel stupid.
- Do not give generic filler.
- Diagnose before recommending replacement parts.
- Ask for a photo when visual identification would materially improve the answer.
- Never invent a boat specification, component, measurement or current weather.
- Remember what the user has already checked.
- Give one useful next step rather than a giant wall of instructions.

FOR REPAIR QUESTIONS:
Start with:
WHAT I THINK
CHECK THIS FIRST
WHAT YOU SHOULD SEE
WHAT THAT TELLS US
NEXT STEP

Work progressively. When the problem is understood, give:
TOOLS
PARTS
ISOLATION / PREPARATION
STEPS
TEST AFTER REPAIR

If the user wants to open something, explain:
1. What it probably is.
2. What it does.
3. What to photograph before opening it.
4. What tools they likely need.
5. What to isolate first.
6. What they should expect to find inside.
7. What can be cleaned/tested/adjusted/repaired/replaced.
8. What to test after reassembly.

ENGINE:
Think through fuel, air, compression, starting power, cooling, lubrication,
exhaust and transmission. For overheating consider raw-water flow, coolant,
pump/belt, exhaust restriction and heat exchanger.

ELECTRICAL:
Use the mental model:
source -> fuse/breaker -> distribution -> switch -> load -> return.
Teach battery, charging, fuse, breaker, positive/negative and multimeter testing.

BILGE / WATER:
Determine whether water is salt, fresh, coolant, fuel or unknown.
Think about seacocks, hoses, shaft/packing, deck leaks, freshwater and pumps.

PLUMBING:
Follow:
source/tank -> pump -> hose -> fixture -> drain.

ANCHORING:
Explain anchor, rode, chain, rope, scope, bottom, setting, holding and swing room.

NAVIGATION:
GPS is a position source, not the whole navigation system. Teach charts,
compass, depth, lookout and redundancy.

WEATHER:
Do not claim a trip is safe from one forecast number. Current official marine
forecasts and warnings are needed for real decisions.

BUYING:
Consider hull/deck/structure, engine, rigging, electrical, plumbing,
through-hulls/seacocks, steering, ground tackle, electronics, safety gear,
maintenance history, survey and sea trial.

LIVEABOARD:
Consider water, power, food, waste, ventilation, condensation, spares,
communications, weather and routine maintenance.

SAFETY:
Do not advise bypassing fuses, breakers or safety devices. Explain isolation
before electrical work. Treat shore/mains electricity, fuel/gas, moving
machinery, hot engines and work aloft with appropriate caution.
Be specific rather than alarmist.

VISUAL EXPLANATIONS:
When explaining a system, use simple labelled visual language in your response
where useful. The application may add a diagram or reference image alongside
your answer.

BOAT PROFILE:
{boat}

CURRENT MODE:
{mode}
"""

def boat_context():
    b = st.session_state.boat
    return "\n".join([
        f"Boat name: {b.get('name') or 'unknown'}",
        f"Type: {b.get('type') or 'unknown'}",
        f"Make/model: {b.get('make_model') or 'unknown'}",
        f"Year: {b.get('year') or 'unknown'}",
        f"Length: {b.get('length') or 'unknown'}",
        f"Engine: {b.get('engine') or 'unknown'}",
        f"Engine hours: {b.get('engine_hours') or 'unknown'}",
        f"Location: {b.get('location') or 'unknown'}",
        f"Notes: {b.get('notes') or 'unknown'}",
    ])

def system_prompt():
    mode = MODES[st.session_state.mode]
    return SYSTEM.format(
        boat=boat_context(),
        mode=mode["title"],
    )

# ----------------------------- VISUALS -----------------------------

def visual_svg(kind):
    navy = "#082631"
    sea = "#0D8B87"
    gold = "#D9B77B"
    grey = "#71828A"
    light = "#E5F3F1"

    if kind == "electrical":
        return f"""
        <div class="visual-card">
          <div class="visual-label">The simple electrical mental model</div>
          <svg viewBox="0 0 900 190" width="100%" role="img">
            <rect x="20" y="58" width="130" height="74" rx="14" fill="{light}"/>
            <text x="85" y="91" text-anchor="middle" font-size="20" font-weight="700" fill="{navy}">BATTERY</text>
            <text x="85" y="116" text-anchor="middle" font-size="14" fill="{grey}">source</text>
            <rect x="205" y="58" width="130" height="74" rx="14" fill="#F7F5EF"/>
            <text x="270" y="91" text-anchor="middle" font-size="20" font-weight="700" fill="{navy}">FUSE</text>
            <text x="270" y="116" text-anchor="middle" font-size="14" fill="{grey}">protection</text>
            <rect x="390" y="58" width="130" height="74" rx="14" fill="#F7F5EF"/>
            <text x="455" y="91" text-anchor="middle" font-size="20" font-weight="700" fill="{navy}">SWITCH</text>
            <text x="455" y="116" text-anchor="middle" font-size="14" fill="{grey}">control</text>
            <rect x="575" y="58" width="130" height="74" rx="14" fill="#F7F5EF"/>
            <text x="640" y="91" text-anchor="middle" font-size="20" font-weight="700" fill="{navy}">LOAD</text>
            <text x="640" y="116" text-anchor="middle" font-size="14" fill="{grey}">light / pump</text>
            <path d="M150 95H205M335 95H390M520 95H575" stroke="{sea}" stroke-width="5"/>
            <path d="M705 95H810V160H85V132" stroke="{gold}" stroke-width="5" fill="none"/>
            <text x="450" y="180" text-anchor="middle" font-size="14" fill="{grey}">return / negative</text>
          </svg>
        </div>
        """

    if kind == "engine":
        return f"""
        <div class="visual-card">
          <div class="visual-label">A marine diesel, simplified</div>
          <svg viewBox="0 0 900 230" width="100%" role="img">
            <rect x="285" y="55" width="330" height="105" rx="22" fill="{navy}"/>
            <text x="450" y="112" text-anchor="middle" font-size="28" font-weight="700" fill="white">ENGINE</text>
            <text x="450" y="139" text-anchor="middle" font-size="14" fill="#B8C9CC">fuel + air + compression</text>
            <circle cx="130" cy="105" r="45" fill="{light}"/>
            <text x="130" y="101" text-anchor="middle" font-size="17" font-weight="700" fill="{navy}">FUEL</text>
            <text x="130" y="122" text-anchor="middle" font-size="13" fill="{grey}">in</text>
            <circle cx="770" cy="105" r="45" fill="{light}"/>
            <text x="770" y="101" text-anchor="middle" font-size="17" font-weight="700" fill="{navy}">EXHAUST</text>
            <text x="770" y="122" text-anchor="middle" font-size="13" fill="{grey}">out</text>
            <path d="M175 105H285M615 105H725" stroke="{sea}" stroke-width="5"/>
            <path d="M450 55V20" stroke="{gold}" stroke-width="5"/>
            <text x="450" y="15" text-anchor="middle" font-size="14" fill="{grey}">AIR</text>
            <path d="M450 160V205" stroke="{gold}" stroke-width="5"/>
            <text x="450" y="225" text-anchor="middle" font-size="14" fill="{grey}">COOLING + LUBRICATION</text>
          </svg>
        </div>
        """

    if kind == "anchor":
        return f"""
        <div class="visual-card">
          <div class="visual-label">Why anchor scope matters</div>
          <svg viewBox="0 0 900 240" width="100%" role="img">
            <rect x="0" y="160" width="900" height="80" fill="{navy}"/>
            <text x="450" y="218" text-anchor="middle" font-size="15" fill="#B8C9CC">SEABED</text>
            <circle cx="250" cy="75" r="30" fill="{light}"/>
            <text x="250" y="80" text-anchor="middle" font-size="15" font-weight="700" fill="{navy}">BOAT</text>
            <path d="M250 105 Q350 140 510 170" stroke="{gold}" stroke-width="6" fill="none"/>
            <path d="M510 170 L535 185 M510 170 L487 188" stroke="{gold}" stroke-width="6"/>
            <text x="370" y="115" text-anchor="middle" font-size="15" fill="{grey}">rode</text>
            <text x="640" y="70" text-anchor="middle" font-size="18" font-weight="700" fill="{navy}">More horizontal pull</text>
            <text x="640" y="95" text-anchor="middle" font-size="14" fill="{grey}">usually helps an anchor hold</text>
          </svg>
        </div>
        """

    if kind == "bilge":
        return f"""
        <div class="visual-card">
          <div class="visual-label">Follow the water</div>
          <svg viewBox="0 0 900 210" width="100%" role="img">
            <rect x="80" y="55" width="170" height="85" rx="18" fill="{light}"/>
            <text x="165" y="91" text-anchor="middle" font-size="19" font-weight="700" fill="{navy}">SOURCE</text>
            <text x="165" y="117" text-anchor="middle" font-size="13" fill="{grey}">leak / hose / rain</text>
            <rect x="365" y="55" width="170" height="85" rx="18" fill="{navy}"/>
            <text x="450" y="91" text-anchor="middle" font-size="19" font-weight="700" fill="white">BILGE</text>
            <text x="450" y="117" text-anchor="middle" font-size="13" fill="#B8C9CC">where it collects</text>
            <rect x="650" y="55" width="170" height="85" rx="18" fill="{light}"/>
            <text x="735" y="91" text-anchor="middle" font-size="19" font-weight="700" fill="{navy}">PUMP</text>
            <text x="735" y="117" text-anchor="middle" font-size="13" fill="{grey}">moves it out</text>
            <path d="M250 98H365M535 98H650" stroke="{sea}" stroke-width="5"/>
          </svg>
        </div>
        """

    return ""

def visual_kind(question):
    q = question.lower()
    if any(x in q for x in ["battery", "fuse", "breaker", "wire", "wiring", "electrical", "multimeter", "alternator", "charging"]):
        return "electrical"
    if any(x in q for x in ["engine", "diesel", "overheat", "oil", "coolant", "exhaust", "starter"]):
        return "engine"
    if any(x in q for x in ["anchor", "anchoring", "windlass", "rode", "chain", "scope"]):
        return "anchor"
    if any(x in q for x in ["bilge", "water leak", "water in", "bilge pump", "flooding"]):
        return "bilge"
    return None

@st.cache_data(ttl=86400, show_spinner=False)
def wikipedia_image(search_term):
    """Free visual reference from Wikimedia Commons. Failure is non-fatal."""
    try:
        url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action":"query",
            "generator":"search",
            "gsrsearch":search_term,
            "gsrnamespace":6,
            "gsrlimit":1,
            "prop":"imageinfo",
            "iiprop":"url",
            "iiurlwidth":900,
            "format":"json",
        }
        r = requests.get(url, params=params, timeout=5)
        data = r.json()
        pages = data.get("query",{}).get("pages",{})
        for page in pages.values():
            info = page.get("imageinfo",[])
            if info:
                return info[0].get("thumburl") or info[0].get("url")
    except Exception:
        pass
    return None

def reference_image(question):
    q = question.lower()
    term = None
    label = None

    terms = [
        (["bilge pump","bilge"], "marine bilge pump", "Reference image · bilge pump"),
        (["alternator"], "marine alternator", "Reference image · alternator"),
        (["starter motor","starter"], "marine diesel starter motor", "Reference image · starter motor"),
        (["battery"], "marine battery", "Reference image · marine battery"),
        (["anchor"], "boat anchor", "Reference image · anchor"),
        (["windlass"], "boat anchor windlass", "Reference image · windlass"),
        (["seacock"], "marine seacock valve", "Reference image · seacock"),
        (["raw water pump","water pump"], "marine engine raw water pump", "Reference image · raw-water pump"),
        (["heat exchanger"], "marine diesel heat exchanger", "Reference image · heat exchanger"),
        (["compass"], "marine compass", "Reference image · compass"),
    ]

    for keywords, search, text in terms:
        if any(k in q for k in keywords):
            term, label = search, text
            break

    if not term:
        return

    image = wikipedia_image(term)
    if image:
        st.markdown(
            f'<div class="visual-card"><div class="visual-label">{html.escape(label)}</div></div>',
            unsafe_allow_html=True,
        )
        st.image(image, use_container_width=True)

# ----------------------------- AI -----------------------------

def generate(question, image_bytes=None, mime=None):
    messages = st.session_state.threads[st.session_state.mode]

    contents = []
    for msg in messages[-12:]:
        contents.append(
            types.Content(
                role="user" if msg["role"] == "user" else "model",
                parts=[types.Part.from_text(text=msg["content"])],
            )
        )

    parts = [
        types.Part.from_text(
            text=(
                "The user is asking this now:\n\n"
                + question
                + "\n\n"
                "Answer specifically and practically. If this is a repair, "
                "start diagnosis rather than jumping to parts. If a photo "
                "would help, say exactly what photo to take."
            )
        )
    ]

    if image_bytes:
        parts.append(types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime or "image/jpeg",
        ))

    contents.append(types.Content(role="user", parts=parts))

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt(),
                temperature=0.48,
                max_output_tokens=2300,
            ),
        )
        return (response.text or "").strip() or "I couldn't get a useful answer. Tell me one more thing about what you're seeing."
    except Exception as e:
        msg = str(e)
        if "404" in msg or "not found" in msg.lower():
            return f"SeaSage cannot access the selected Gemini model ({MODEL}) with this API key. Restart the app to refresh available models."
        if "429" in msg or "quota" in msg.lower():
            return "The Gemini free quota/rate limit has been reached for now. Try again shortly."
        return f"SeaSage hit an AI connection error: {msg}"

def ask(question, image_bytes=None, mime=None):
    mode = st.session_state.mode
    st.session_state.threads[mode].append({
        "role":"user",
        "content":question,
    })

    with st.chat_message("user"):
        st.markdown(question)
        if image_bytes:
            st.image(image_bytes, use_container_width=True)

    with st.chat_message("assistant"):
        with st.spinner("SeaSage is thinking..."):
            answer = generate(question, image_bytes, mime)
        st.markdown(answer)

        diagram = visual_kind(question)
        if diagram:
            st.markdown(visual_svg(diagram), unsafe_allow_html=True)

        reference_image(question)

    st.session_state.threads[mode].append({
        "role":"assistant",
        "content":answer,
    })

def switch_mode(mode, starter=None):
    st.session_state.mode = mode
    st.session_state.starter = starter
    st.rerun()

# ----------------------------- NAV -----------------------------

def topbar():
    logo()
    st.write("")

# ----------------------------- HOME -----------------------------

def home():
    topbar()

    st.markdown("""
    <div class="hero">
      <div class="eyebrow">YOUR AI FIRST MATE</div>
      <h1>Learn your boat.<br>One thing at a time.</h1>
      <p>
        SeaSage is for the person who bought a boat before they knew what
        half the things on it were. Ask questions, open things up, fix them,
        and learn as you go.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Where should we start?")

    modes = [
        ("01","repair","Fix something","Something isn't working? Let's diagnose it together.","WORKSHOP"),
        ("02","boat","Understand my boat","Find a part, learn a system, understand what you're looking at.","BOAT SCHOOL"),
        ("03","trip","Go somewhere","Get the boat, route and crew ready before leaving the dock.","PASSAGE PLANNING"),
        ("04","learn","Learn by doing","Short practical lessons that take you back to your actual boat.","LEARN"),
    ]

    cols = st.columns(4)

    for i,(number,key,title,desc,kicker) in enumerate(modes):
        with cols[i]:
            st.markdown(
                f"""
                <div class="mode-card">
                  <div class="mode-number">{number} / {kicker}</div>
                  <div class="mode-icon">{'↗' if key=='repair' else '◈' if key=='boat' else '⌁' if key=='trip' else '＋'}</div>
                  <div class="mode-title">{title}</div>
                  <div class="mode-desc">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Open →", key="home_"+key, type="primary"):
                switch_mode(key)

    st.write("")
    st.markdown("### Or just ask")

    cols = st.columns(3)
    starters = [
        ("I know nothing about boats. Give me a practical starting point.","general"),
        ("My engine is overheating. Help me diagnose it step by step.","repair"),
        ("I want to understand everything in my engine bay.","boat"),
    ]

    for i,(text,mode) in enumerate(starters):
        with cols[i]:
            if st.button(text, key=f"starter_{i}"):
                switch_mode(mode, text)

    st.write("")
    b = st.session_state.boat
    if b.get("name") or b.get("make_model"):
        st.markdown(
            f"""
            <div class="info">
              <strong>{html.escape(b.get("name") or b.get("make_model"))}</strong>
              · {html.escape(b.get("type") or "Boat")}
              · {html.escape(b.get("length") or "length unknown")}
              <br><span style="opacity:.7">SeaSage is using this boat profile in your conversations.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ----------------------------- CHAT -----------------------------

def chat_page():
    mode = st.session_state.mode
    meta = MODES[mode]

    topbar()

    st.markdown(
        f"""
        <div class="chat-shell">
          <div class="chat-header">
            <div class="chat-kicker">{html.escape(meta["kicker"])}</div>
            <div class="chat-title">{html.escape(meta["title"])}</div>
            <div class="chat-sub">{html.escape(meta["subtitle"])}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.starter:
        starter = st.session_state.starter
        st.session_state.starter = None
        ask(starter)

    messages = st.session_state.threads[mode]

    if not messages:
        if mode == "repair":
            st.markdown(
                '<div class="info"><strong>Tell me what is wrong in normal human language.</strong><br>“It makes a clicking noise” is better than trying to name the part incorrectly.</div>',
                unsafe_allow_html=True,
            )
        elif mode == "boat":
            st.markdown(
                '<div class="info"><strong>Show me things.</strong><br>Upload a photo of a component and I’ll help identify it, explain what it does and tell you what to inspect next.</div>',
                unsafe_allow_html=True,
            )
        elif mode == "trip":
            st.markdown(
                '<div class="info"><strong>We’ll prepare rather than guess.</strong><br>Tell me where you’re going, what boat you have and how experienced the crew is.</div>',
                unsafe_allow_html=True,
            )
        elif mode == "learn":
            st.markdown(
                '<div class="info"><strong>Learning should end at the boat.</strong><br>I’ll explain the concept, then give you something you can physically find or inspect.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="info"><strong>No nautical vocabulary required.</strong><br>Describe what you see, hear, smell or feel. We’ll work out the terminology together.</div>',
                unsafe_allow_html=True,
            )

    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input(
        {
            "general":"Ask SeaSage anything...",
            "repair":"What is broken or behaving strangely?",
            "boat":"What are you looking at?",
            "trip":"Where are you thinking of going?",
            "learn":"What do you want to understand?",
        }[mode]
    )

    if prompt:
        ask(prompt)

    with st.expander("📷 Show SeaSage a photo"):
        photo = st.file_uploader(
            "Upload a photo of the boat, part, panel or problem",
            type=["jpg","jpeg","png","webp"],
            key=f"photo_{mode}",
        )
        if photo:
            st.image(photo.getvalue(), use_container_width=True)
            question = st.text_input(
                "What do you want to know about it?",
                placeholder="What is this? How do I open it? Does anything look wrong?",
                key=f"photo_q_{mode}",
            )
            if st.button("Look at this with me", key=f"photo_send_{mode}", type="primary"):
                ask(
                    question.strip() or
                    "Look at this photo as my first mate. Identify what you can with confidence, explain what it probably does, and tell me the most useful thing I should inspect or photograph next.",
                    photo.getvalue(),
                    photo.type,
                )

    st.write("")
    c1,c2,c3 = st.columns(3)

    with c1:
        if st.button("← Home", key="back_home"):
            st.session_state.starter = None
            st.rerun()

    with c2:
        if st.button("New conversation", key="new_thread"):
            st.session_state.threads[mode] = []
            st.rerun()

    with c3:
        if st.button("My boat", key="go_boat"):
            st.session_state.mode = "boat"
            st.rerun()

# ----------------------------- BOAT PROFILE -----------------------------

def boat_profile():
    topbar()

    st.markdown('<div class="eyebrow">BOAT PROFILE</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Give SeaSage<br>your boat’s story.</div>', unsafe_allow_html=True)
    st.markdown('<div class="lead">A few details make the difference between generic boating advice and advice that actually fits the boat sitting in front of you.</div>', unsafe_allow_html=True)

    st.write("")

    b = st.session_state.boat

    with st.form("boat_profile"):
        left,right = st.columns(2)

        with left:
            name = st.text_input("Boat name", b["name"], placeholder="Blue Hour")
            options = ["","Monohull sailboat","Catamaran","Motorboat","Trawler","Trimaran","Other"]
            current = b["type"]
            boat_type = st.selectbox(
                "Type",
                options,
                index=options.index(current) if current in options else 0,
            )
            make = st.text_input("Make / model", b["make_model"], placeholder="Oceanis 35")
            length = st.text_input("Length", b["length"], placeholder="35 ft")
            year = st.text_input("Year", b["year"], placeholder="2016")

        with right:
            engine = st.text_input("Engine", b["engine"], placeholder="Yanmar 3YM30")
            hours = st.text_input("Engine hours", b["engine_hours"], placeholder="2400")
            location = st.text_input("Where is the boat?", b["location"], placeholder="Goa, India")
            notes = st.text_area(
                "What else should I know?",
                b["notes"],
                height=155,
                placeholder="Solar, watermaker, known leaks, refit plans, anything you've already fixed...",
            )

        if st.form_submit_button("Save boat profile", type="primary"):
            st.session_state.boat = {
                "name":name.strip(),
                "type":boat_type,
                "make_model":make.strip(),
                "year":year.strip(),
                "length":length.strip(),
                "engine":engine.strip(),
                "engine_hours":hours.strip(),
                "location":location.strip(),
                "notes":notes.strip(),
            }
            st.success("Boat profile saved for this session.")

    st.write("")
    if st.button("Start a boat tour →", type="primary"):
        switch_mode("boat", "Give me a practical tour of my boat. Start with the major systems I should physically find and understand.")

# ----------------------------- ROUTER -----------------------------

# Keep navigation deliberately minimal. Each major area is its own chat thread.
topbar()

nav_cols = st.columns([1,1,1,1,1,1])
nav_items = [
    ("Home","home"),
    ("Ask","general"),
    ("Fix","repair"),
    ("My boat","profile"),
    ("Trip","trip"),
    ("Learn","learn"),
]

for col,(label,target) in zip(nav_cols, nav_items):
    with col:
        if st.button(label, key="top_"+target):
            if target == "home":
                st.session_state.view = "home"
            elif target == "profile":
                st.session_state.view = "profile"
            else:
                st.session_state.view = "chat"
                st.session_state.mode = target
            st.rerun()

if "view" not in st.session_state:
    st.session_state.view = "home"

if st.session_state.view == "home":
    home()
elif st.session_state.view == "profile":
    boat_profile()
else:
    chat_page()
