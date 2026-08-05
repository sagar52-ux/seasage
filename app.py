import os
import html
import requests
import streamlit as st
from google import genai
from google.genai import types

# ============================================================
# SeaSage — a simple AI first mate for first-time sailors
# ============================================================

st.set_page_config(
    page_title="SeaSage — Your First Mate",
    page_icon="⚓",
    layout="wide",
)

# ------------------------- STYLE -----------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@700;800&display=swap');

:root {
  --navy:#062033;
  --navy2:#0b3046;
  --teal:#159f98;
  --teal-light:#e5f6f4;
  --ink:#17313e;
  --muted:#687d85;
  --line:#dbe6e8;
}

html, body, [class*="css"] {
  font-family:"DM Sans",sans-serif !important;
}

.stApp {
  background:linear-gradient(180deg,#fcfefe 0%,#f1f7f6 100%);
  color:var(--ink);
}

.block-container {
  max-width:1160px;
  padding-top:2rem;
  padding-bottom:5rem;
}

h1,h2,h3,h4 {
  font-family:"Manrope",sans-serif !important;
  color:var(--navy) !important;
  letter-spacing:-.035em;
}

.hero-title {
  font-family:"Manrope",sans-serif;
  font-size:clamp(3.1rem,7vw,5.7rem);
  line-height:.93;
  letter-spacing:-.07em;
  font-weight:800;
  color:var(--navy) !important;
  margin-top:1rem;
}

.hero-subtitle {
  max-width:720px;
  color:var(--muted) !important;
  font-size:1.08rem;
  line-height:1.65;
  margin-top:1rem;
}

.eyebrow {
  display:inline-block;
  padding:7px 12px;
  border-radius:999px;
  background:var(--teal-light);
  color:#117d78 !important;
  font-size:.72rem;
  font-weight:800;
  letter-spacing:.1em;
}

.card {
  background:#fff;
  border:1px solid var(--line);
  border-radius:19px;
  padding:1.25rem;
  height:100%;
  box-shadow:0 7px 25px rgba(6,32,51,.04);
}

.card-icon { font-size:1.8rem; margin-bottom:.55rem; }
.card-title {
  font-family:"Manrope",sans-serif;
  font-size:1.05rem;
  font-weight:800;
  color:var(--navy) !important;
}
.card-text {
  color:var(--muted) !important;
  font-size:.9rem;
  line-height:1.5;
  margin-top:.3rem;
}

.boat-strip {
  background:linear-gradient(135deg,var(--navy),var(--navy2));
  border-radius:21px;
  padding:1.3rem 1.5rem;
  color:white;
}
.boat-strip * { color:white !important; }
.boat-name {
  font-family:"Manrope";
  font-size:1.5rem;
  font-weight:800;
}
.boat-meta { opacity:.75; }

.tip {
  background:var(--teal-light);
  border:1px solid #c7e9e5;
  border-radius:16px;
  padding:1rem 1.1rem;
}
.tip * { color:#174a50 !important; }

.danger {
  background:#fff1f0;
  border:1px solid #edc3c0;
  border-radius:16px;
  padding:1rem 1.1rem;
}
.danger * { color:#6e2926 !important; }

.stButton > button {
  width:100%;
  min-height:45px;
  border-radius:13px;
  border:1px solid var(--line);
  background:#fff;
  color:var(--navy) !important;
  font-weight:700;
}
.stButton > button:hover {
  border-color:var(--teal);
  color:var(--navy) !important;
  transform:translateY(-1px);
}
.stButton > button[kind="primary"] {
  background:var(--navy) !important;
  color:#fff !important;
  border-color:var(--navy) !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
  background:#fff !important;
  color:var(--ink) !important;
  -webkit-text-fill-color:var(--ink) !important;
}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
  color:#82939a !important;
  opacity:1 !important;
}
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div {
  background:#fff !important;
  border-color:var(--line) !important;
}
[data-baseweb="select"] * { color:var(--ink) !important; }

.stChatMessage {
  border:1px solid var(--line);
  border-radius:18px;
  background:rgba(255,255,255,.9);
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] em {
  color:var(--ink) !important;
}
[data-testid="stChatInput"] textarea {
  color:var(--ink) !important;
  background:#fff !important;
  -webkit-text-fill-color:var(--ink) !important;
}

.small {
  font-size:.78rem;
  color:var(--muted) !important;
}

@media(max-width:700px) {
  .block-container { padding-left:1rem; padding-right:1rem; }
  .hero-title { font-size:3.2rem; }
}
</style>
""", unsafe_allow_html=True)

# ------------------------- STATE -----------------------------

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

if "page" not in st.session_state:
    st.session_state.page = "home"
if "boat" not in st.session_state:
    st.session_state.boat = DEFAULT_BOAT.copy()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None
if "marine" not in st.session_state:
    st.session_state.marine = None

# ------------------------- GEMINI ----------------------------

def get_key():
    try:
        key = st.secrets.get("GEMINI_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY")

API_KEY = get_key()

if not API_KEY:
    st.error("SeaSage needs GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

@st.cache_resource
def make_client(key):
    return genai.Client(api_key=key)

client = make_client(API_KEY)

@st.cache_resource
def choose_model(key):
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
                available.append(name.replace("models/",""))
        for wanted in preferred:
            if wanted in available:
                return wanted
        if available:
            return available[0]
    except Exception:
        pass
    return "gemini-2.5-flash"

MODEL = choose_model(API_KEY)

# ------------------------- BRAIN -----------------------------

BRAIN = """
You are SeaSage, an experienced sailor, boat owner, repair mentor and patient
first mate. Your user may be a complete beginner.

Your job is to help the user understand, maintain, troubleshoot, repair and use
their own boat. You are hands-on. You do NOT automatically tell people to hire
a professional.

The user is allowed to open things, remove panels, test components, clean parts,
replace parts and learn by doing. Help them do it intelligently.

CORE STYLE
- Talk like an experienced friend standing beside the boat.
- Plain English first; explain nautical terms as they appear.
- Never make the user feel stupid.
- Don't drown simple questions in warnings.
- Don't give a giant list when one next step will do.
- Diagnose before guessing at a replacement part.
- Ask for a photo whenever seeing the component would materially help.
- Remember what the user already checked.
- Explain WHY a step matters.

REPAIR FLOW
For a repair/troubleshooting question:
1. Say what you think may be happening.
2. Ask or give the single best next check.
3. Tell the user exactly what to look for.
4. Explain what each possible result means.
5. Continue one step at a time.
6. Once the fault is narrowed down, give the repair procedure.
7. Give tools/parts needed and how to test the repair afterwards.

When useful, structure as:
WHAT I THINK
CHECK THIS FIRST
WHAT YOU SHOULD SEE
WHAT THAT TELLS US
NEXT STEP

HANDS-ON REPAIR
When a user wants to open something:
- Tell them what the component probably is and what it does.
- Tell them what to photograph before disassembly.
- Suggest labelling wires/hoses if useful.
- Tell them what tools are likely needed.
- Explain what to isolate first.
- Explain what they should expect to see.
- Help them decide what can be cleaned, adjusted, tested, repaired or replaced.
- If they get stuck, ask for a photo rather than guessing.

Do not be unnecessarily restrictive. A novice can learn a lot by doing.

SAFETY BOUNDARIES
Be sensible, not alarmist.
- Never advise bypassing a fuse, breaker or safety device.
- Explain isolation before electrical work.
- Treat shore/mains electricity with appropriate caution.
- Treat fuel/gas as ignition-sensitive.
- Warn about moving belts/fans and hot engines.
- For heavy components, mention proper support.
- For rigging aloft, explain equipment and technique boundaries.
If something is genuinely dangerous, explain the specific danger and offer the
safest way to continue learning.

EXPERTISE

ENGINE:
Think about fuel, air, compression, starting power, cooling, lubrication,
exhaust and transmission. For overheating, consider raw-water flow, coolant,
pump/belt, exhaust restriction and heat exchanger. Teach simple checks first.

ELECTRICAL:
Use the model:
source -> protection -> distribution -> switch -> load -> return.
Teach batteries, fuses, breakers, switches, grounds/negative, charging sources
and multimeter testing progressively.

BILGE/WATER:
Ask whether the water is rising and whether it is salt, fresh, coolant, fuel
or unknown. Think about seacocks, hoses, shaft/packing, deck leaks, freshwater,
cooling-water leaks and pumps.

PLUMBING:
Follow the water path from tank/source -> pump -> hose -> fixture -> drain.
Help users inspect clamps, hoses, pumps, filters and tanks.

ANCHORING:
Explain anchor, rode, chain, rope, scope, bottom type, setting, holding,
snubber and swing room. Scope is a ratio, not a magic number.

NAVIGATION:
GPS is a position source, not the entire navigation system. Teach charts,
compass, depth, visual references, lookout and redundancy.

WEATHER:
Explain wind, waves, swell, period and current. Never call a trip safe from
one number. Current official forecasts and warnings are needed for real trips.

BUYING:
Look at hull/deck/structure, engine, rigging, electrical, plumbing,
through-hulls/seacocks, steering, ground tackle, electronics, safety gear,
maintenance history and survey/sea trial. A cheap boat may have expensive
deferred maintenance.

LIVEABOARD:
Think water, power, food, waste, ventilation, condensation, spares,
communications, weather and routine maintenance.

DO NOT INVENT:
Never invent the user's boat specifications, wiring, engine model, component
identity or current weather. If exact information matters, ask for a photo,
model number, manual or measurement.

CURRENT BOAT PROFILE:
{boat}
"""

def boat_context():
    b = st.session_state.boat
    return "\n".join([
        f"Name: {b.get('name') or 'unknown'}",
        f"Type: {b.get('type') or 'unknown'}",
        f"Make/model: {b.get('make_model') or 'unknown'}",
        f"Year: {b.get('year') or 'unknown'}",
        f"Length: {b.get('length') or 'unknown'}",
        f"Engine: {b.get('engine') or 'unknown'}",
        f"Engine hours: {b.get('engine_hours') or 'unknown'}",
        f"Location: {b.get('location') or 'unknown'}",
        f"Notes: {b.get('notes') or 'unknown'}",
    ])

def prompt_for(question):
    return BRAIN.format(boat=boat_context())

def generate(question, image=None, mime=None):
    contents = []

    for msg in st.session_state.messages[-12:]:
        contents.append(
            types.Content(
                role="user" if msg["role"] == "user" else "model",
                parts=[types.Part.from_text(text=msg["content"])],
            )
        )

    parts = [
        types.Part.from_text(
            text=(
                "User's current question:\n"
                + question
                + "\n\n"
                "Use the boat profile. If this is a repair problem, work "
                "step-by-step and ask for the most useful next observation."
            )
        )
    ]

    if image:
        parts.append(types.Part.from_bytes(
            data=image,
            mime_type=mime or "image/jpeg",
        ))

    contents.append(types.Content(role="user", parts=parts))

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=prompt_for(question),
                temperature=0.55,
                max_output_tokens=2200,
            ),
        )
        answer = (response.text or "").strip()
        return answer or "I didn't get a useful answer. Try telling me one more detail."
    except Exception as e:
        msg = str(e)
        if "404" in msg or "not found" in msg.lower():
            return (
                f"I can't access Gemini model `{MODEL}` with this API key. "
                "Restart the Streamlit app so SeaSage can refresh the available models."
            )
        if "429" in msg or "quota" in msg.lower():
            return "Gemini's free quota/rate limit has been reached for the moment. Try again shortly."
        return f"SeaSage hit an AI connection error: {msg}"

def ask(question, image=None, mime=None):
    st.session_state.messages.append({"role":"user","content":question})
    with st.chat_message("user", avatar="🧑‍✈️"):
        st.markdown(question)
        if image:
            st.image(image, use_container_width=True)

    with st.chat_message("assistant", avatar="⚓"):
        with st.spinner("SeaSage is thinking..."):
            answer = generate(question, image, mime)
        st.markdown(answer)

    st.session_state.messages.append({"role":"assistant","content":answer})

def open_prompt(question):
    st.session_state.pending_prompt = question
    st.session_state.page = "chat"
    st.rerun()

def esc(value):
    return html.escape(str(value or ""))

# ------------------------- NAV -------------------------------

def nav():
    with st.sidebar:
        st.markdown("## ⚓ SeaSage")
        st.caption("Your AI first mate")
        st.markdown("---")

        items = [
            ("⌂ Home","home"),
            ("⚓ Ask SeaSage","chat"),
            ("🔧 Fix something","fix"),
            ("🛥️ My boat","boat"),
            ("🧭 Go somewhere","trip"),
            ("🎓 Learn","learn"),
        ]

        for label, page in items:
            if st.button(label, key="nav_"+page):
                st.session_state.page = page
                st.rerun()

        st.markdown("---")

        if st.button("🚨 Emergency", key="nav_emergency"):
            st.session_state.page = "emergency"
            st.rerun()

        if st.button("＋ New conversation", key="new_chat"):
            st.session_state.messages = []
            st.session_state.page = "chat"
            st.rerun()

        b = st.session_state.boat
        if b.get("name") or b.get("make_model"):
            st.markdown("---")
            st.caption("MY BOAT")
            st.markdown(
                f"**{esc(b.get('name') or b.get('make_model'))}**",
                unsafe_allow_html=True,
            )
            st.caption(
                f"{b.get('type') or 'Boat'} · {b.get('length') or '?'}"
            )

# ------------------------- HOME ------------------------------

def home():
    b = st.session_state.boat
    label = b.get("name") or b.get("make_model")

    st.markdown('<div class="eyebrow">⚓ YOUR AI FIRST MATE</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-title">Your boat.<br>Your questions.<br>Your first mate.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-subtitle">You don’t need to know the nautical words. Tell SeaSage what you see, hear, smell, feel or want to do — and we’ll figure it out together.</div>',
        unsafe_allow_html=True,
    )

    st.write("")
    st.markdown("### What do you need?")

    cards = [
        ("🔧","Fix something","Something isn't working? Diagnose it together.","fix"),
        ("🛥️","Understand my boat","Find parts, learn systems and understand what you're looking at.","boat"),
        ("🧭","I'm going somewhere","Prepare the boat, crew, route and departure.","trip"),
        ("🎓","Teach me","Learn engines, electrics, sailing, anchoring and more.","learn"),
    ]

    cols = st.columns(4)

    for i, (icon,title,desc,page) in enumerate(cards):
        with cols[i]:
            st.markdown(
                f'<div class="card"><div class="card-icon">{icon}</div><div class="card-title">{title}</div><div class="card-text">{desc}</div></div>',
                unsafe_allow_html=True,
            )
            if st.button("Open →", key="home_"+page, type="primary"):
                st.session_state.page = page
                st.rerun()

    st.write("")

    if label:
        st.markdown(
            f"""
            <div class="boat-strip">
                <div class="small">MY BOAT</div>
                <div class="boat-name">{esc(label)}</div>
                <div class="boat-meta">
                    {esc(b.get('type') or 'Boat')} ·
                    {esc(b.get('length') or 'Length unknown')} ·
                    {esc(b.get('year') or 'Year unknown')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")

    st.markdown("### Or just ask me")

    examples = [
        "I know nothing about boats. Where do I start?",
        "What is this thing under my engine?",
        "My bilge pump keeps running.",
        "Can I change my engine oil myself?",
    ]

    cols = st.columns(4)
    for i, text in enumerate(examples):
        with cols[i]:
            if st.button(text, key=f"example_{i}"):
                open_prompt(text)

# ------------------------- CHAT ------------------------------

def chat_page():
    st.markdown('<div class="eyebrow">⚓ FIRST MATE</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-title" style="font-size:3.7rem">Tell me what’s going on.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-subtitle">Describe it however you want. “There’s a weird thing making a clicking noise” is perfectly acceptable.</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.messages:
        st.write("")
        st.markdown(
            '<div class="tip"><strong>SeaSage works best when you describe what you actually see.</strong><br>You don\'t need the right nautical term. If a photo would help, use the camera/upload option below.</div>',
            unsafe_allow_html=True,
        )

    for msg in st.session_state.messages:
        with st.chat_message(
            "assistant" if msg["role"] == "assistant" else "user",
            avatar="⚓" if msg["role"] == "assistant" else "🧑‍✈️",
        ):
            st.markdown(msg["content"])

    pending = st.session_state.pending_prompt
    if pending:
        st.session_state.pending_prompt = None
        ask(pending)

    prompt = st.chat_input("Ask SeaSage anything about your boat...")
    if prompt:
        ask(prompt)

    st.write("")
    with st.expander("📷 Show SeaSage a photo"):
        photo = st.file_uploader(
            "Upload a boat/part/problem photo",
            type=["jpg","jpeg","png","webp"],
            key="chat_photo",
        )
        if photo:
            st.image(photo.getvalue(), use_container_width=True)
            photo_question = st.text_input(
                "What do you want to know?",
                placeholder="What is this? How do I remove it? Does it look wrong?",
                key="photo_question",
            )
            if st.button("Look at this with me", type="primary"):
                q = photo_question.strip() or (
                    "Look at this photo as my first mate. Identify what you can "
                    "with confidence, explain what it probably does, tell me "
                    "what I should photograph next if necessary, and give me "
                    "the safest useful thing I can inspect or do next."
                )
                ask(q, photo.getvalue(), photo.type)

# ------------------------- BOAT ------------------------------

def boat_page():
    b = st.session_state.boat

    st.markdown('<div class="eyebrow">🛥️ MY BOAT</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-title" style="font-size:3.7rem">Get to know<br>your boat.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-subtitle">Give SeaSage a few facts so its advice is about your boat, not an imaginary generic boat.</div>',
        unsafe_allow_html=True,
    )

    st.write("")

    with st.form("boat_form"):
        a,bcol = st.columns(2)

        with a:
            name = st.text_input("Boat name", value=b.get("name",""), placeholder="Blue Hour")
            options = ["","Monohull sailboat","Catamaran","Motorboat","Trawler","Trimaran","Other"]
            current = b.get("type","")
            boat_type = st.selectbox("Boat type", options, index=options.index(current) if current in options else 0)
            make_model = st.text_input("Make / model", value=b.get("make_model",""), placeholder="Beneteau Oceanis 35")
            length = st.text_input("Length", value=b.get("length",""), placeholder="35 ft")
            year = st.text_input("Year", value=b.get("year",""), placeholder="2016")

        with bcol:
            engine = st.text_input("Engine", value=b.get("engine",""), placeholder="Yanmar 3YM30")
            hours = st.text_input("Engine hours", value=b.get("engine_hours",""), placeholder="2,400")
            location = st.text_input("Where is it?", value=b.get("location",""), placeholder="Goa, India")
            notes = st.text_area("Things I should know", value=b.get("notes",""), height=150, placeholder="Solar, watermaker, known leaks, refit plans...")

        save = st.form_submit_button("Save my boat", type="primary")

    if save:
        st.session_state.boat = {
            "name":name.strip(),
            "type":boat_type,
            "make_model":make_model.strip(),
            "year":year.strip(),
            "length":length.strip(),
            "engine":engine.strip(),
            "engine_hours":hours.strip(),
            "location":location.strip(),
            "notes":notes.strip(),
        }
        st.success("Saved. SeaSage will remember this boat during your session.")

    st.write("")
    st.markdown("### Explore your systems")

    systems = [
        ("🛢️","Engine","Fuel, cooling, oil, exhaust and maintenance."),
        ("🔋","Electrical","Batteries, charging, fuses and circuits."),
        ("💧","Plumbing","Water tanks, pumps, hoses and drains."),
        ("⚓","Anchoring","Anchor, rode, scope and setting."),
        ("⛵","Rigging","Mast, boom, lines and standing rigging."),
        ("🧭","Navigation","Charts, GPS, compass and depth."),
        ("🚽","Sanitation","Toilet, holding tank and hoses."),
        ("🛟","Safety","Know where your critical equipment lives."),
    ]

    cols = st.columns(4)

    for i,(icon,title,desc) in enumerate(systems):
        with cols[i]:
            st.markdown(
                f'<div class="card"><div class="card-icon">{icon}</div><div class="card-title">{title}</div><div class="card-text">{desc}</div></div>',
                unsafe_allow_html=True,
            )
            if st.button("Teach me →", key=f"system_{i}"):
                open_prompt(
                    f"Teach me the {title.lower()} system on my boat from absolute zero. "
                    "Give me the simple mental model, then tell me what parts I "
                    "should physically find on my boat, what each does, what "
                    "I should inspect, common failures, and one hands-on exercise "
                    "I can do to learn it."
                )

# ------------------------- FIX --------------------------------

def fix_page():
    st.markdown('<div class="eyebrow">🔧 GARAGE MODE</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-title" style="font-size:3.7rem">Let’s figure out<br>what’s wrong.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-subtitle">You can open things, learn, test and repair. SeaSage will help you work out what to do next.</div>',
        unsafe_allow_html=True,
    )

    st.write("")

    common = [
        ("🛢️","Engine","Won't start, overheats, smoke, alarms, power loss"),
        ("🔋","Electrical","Dead circuit, battery, charging, lights"),
        ("💧","Water / bilge","Water appearing, pump running, leak"),
        ("🚽","Plumbing","Toilet, freshwater pump, tank, hose"),
        ("⛵","Rigging","Line, sail, mast or hardware"),
        ("🧭","Navigation","GPS, depth, compass or instrument"),
        ("⚓","Anchoring","Anchor, windlass, chain or dragging"),
        ("❓","Something else","Describe it in your own words"),
    ]

    cols = st.columns(4)

    for i,(icon,title,desc) in enumerate(common):
        with cols[i]:
            st.markdown(
                f'<div class="card"><div class="card-icon">{icon}</div><div class="card-title">{title}</div><div class="card-text">{desc}</div></div>',
                unsafe_allow_html=True,
            )
            if st.button("Start →", key=f"fix_{i}"):
                open_prompt(
                    f"I have a {title.lower()} problem on my boat. "
                    "Act like you are standing beside me. Start with the "
                    "single most useful diagnostic question. Assume I am a beginner."
                )

    st.write("")
    st.markdown("### Or describe the problem")

    problem = st.text_area(
        "What happened?",
        placeholder=(
            "Example: My engine starts normally but after five minutes "
            "the temperature alarm comes on. I can still see water coming "
            "out of the exhaust."
        ),
        height=130,
    )

    if st.button("🔧 Diagnose it with me", type="primary"):
        if problem.strip():
            open_prompt(
                "Help me diagnose this step by step. Tell me what you think "
                "might be happening, then ask me the most useful next question. "
                "Do not jump to replacing parts.\n\n"
                + problem
            )
        else:
            st.warning("Tell me what is happening first.")

    st.write("")
    st.markdown("### 📷 Or show me")

    photo = st.file_uploader(
        "Upload a photo of the part/problem",
        type=["jpg","jpeg","png","webp"],
        key="fix_photo",
    )

    if photo:
        st.image(photo.getvalue(), use_container_width=True)
        q = st.text_input(
            "What do you want me to help with?",
            placeholder="What is this? How do I open it? What looks wrong?",
            key="fix_photo_question",
        )
        if st.button("🔍 Look at it with me", type="primary"):
            question = q.strip() or (
                "Identify what you can in this photo with confidence. "
                "Explain what the component probably does. Tell me what "
                "I can safely inspect myself and what photo/detail you want "
                "next if identification is uncertain."
            )
            ask(question, photo.getvalue(), photo.type)

# ------------------------- TRIP -------------------------------

def trip_page():
    st.markdown('<div class="eyebrow">🧭 GO SOMEWHERE</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-title" style="font-size:3.7rem">Let\'s get ready<br>to leave.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-subtitle">Think through the boat, crew, route, weather information, fuel, water and what happens if something goes wrong.</div>',
        unsafe_allow_html=True,
    )

    a,b = st.columns(2)

    with a:
        departure = st.text_input("Leaving from", placeholder="Goa")
        destination = st.text_input("Going to", placeholder="Gokarna")
        duration = st.text_input("How long?", placeholder="One night")

    with b:
        crew = st.text_input("Who's coming?", placeholder="2 adults, both beginners")
        concerns = st.text_area("Anything you're worried about?", height=100, placeholder="No radar, new engine, little sailing experience...")

    st.markdown(
        '<div class="tip"><strong>For a real trip:</strong> check current official marine forecasts, warnings and local navigation information. SeaSage can help you understand what to check and turn it into a practical checklist.</div>',
        unsafe_allow_html=True,
    )

    if st.button("🧭 Build my departure checklist", type="primary"):
        open_prompt(
            f"""
I'm planning a boat trip.

Leaving: {departure or 'unknown'}
Destination: {destination or 'unknown'}
Duration: {duration or 'unknown'}
Crew: {crew or 'unknown'}
Concerns: {concerns or 'none'}

Help me prepare as a beginner. Give me:
1. Boat readiness
2. Weather/sea information I need to obtain
3. Navigation preparation
4. Fuel/water/power/food
5. Safety and communications
6. Crew briefing
7. Contingencies
8. A final pre-departure checklist

Do not invent current weather or call the trip safe without the necessary information.
"""
        )

# ------------------------- LEARN ------------------------------

def learn_page():
    st.markdown('<div class="eyebrow">🎓 LEARN BY DOING</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-title" style="font-size:3.7rem">Understand the machine<br>you live on.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-subtitle">Pick something. Learn the idea, then go find it on your actual boat.</div>',
        unsafe_allow_html=True,
    )

    lessons = [
        ("🛥️","Boat anatomy","Learn what everything is.","Give me a hands-on tour of a typical cruising boat. Start outside and work inward."),
        ("🛢️","Diesel engine","Understand the engine before it scares you.","Teach me the basic mental model of a marine diesel engine and then tell me what I should find in my engine compartment."),
        ("🔋","Boat electrics","Stop being afraid of the panel.","Teach me boat electrical systems from zero and give me a simple hands-on exercise with my own boat."),
        ("💧","Plumbing","Follow water around the boat.","Teach me how freshwater, pumps, tanks, hoses and drains work and give me an inspection exercise."),
        ("⚓","Anchoring","Learn why the anchor holds.","Teach me anchoring from zero, including rode, scope, setting and how to recognise dragging."),
        ("⛵","Sailing","Understand wind and sails.","Teach me points of sail, sheets, halyards, trim, tacking and reefing with practical examples."),
        ("🧭","Navigation","Learn more than pressing Go.","Teach me charts, GPS, compass, depth, lookout and navigation redundancy from zero."),
        ("🌊","Weather","Understand waves and swell.","Teach me wind, wave height, wave period, swell and current and how sailors use forecasts."),
        ("🏠","Living aboard","Treat the boat like a tiny home.","Teach me water, power, waste, ventilation, condensation, food, spares and maintenance for living aboard."),
    ]

    cols = st.columns(3)

    for i,(icon,title,desc,prompt) in enumerate(lessons):
        with cols[i]:
            st.markdown(
                f'<div class="card"><div class="card-icon">{icon}</div><div class="card-title">{title}</div><div class="card-text">{desc}</div></div>',
                unsafe_allow_html=True,
            )
            if st.button("Start learning →", key=f"learn_{i}"):
                open_prompt(prompt)

# ------------------------- EMERGENCY --------------------------

def emergency_page():
    st.markdown('<div class="eyebrow">🚨 EMERGENCY</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-title" style="font-size:3.8rem">Tell me what is happening.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="danger"><strong>If someone is in immediate danger:</strong> use your onboard emergency procedures and contact the appropriate maritime/emergency service. SeaSage is an AI guide, not an emergency service.</div>',
        unsafe_allow_html=True,
    )

    st.write("")

    situations = [
        ("🔥","Fire"),
        ("💧","Flooding"),
        ("🧍","Person overboard"),
        ("🛢️","Engine failure"),
        ("⚡","Electrical fire"),
        ("⛵","Rigging failure"),
        ("🧭","Loss of steering"),
        ("🌊","Severe weather"),
    ]

    cols = st.columns(4)

    for i,(icon,title) in enumerate(situations):
        with cols[i]:
            if st.button(f"{icon} {title}", key=f"em_{i}", type="primary"):
                open_prompt(
                    f"EMERGENCY: {title}. Give immediate practical actions first, "
                    "keep them short, tell me what to avoid if important, and ask "
                    "only the most critical next question."
                )

    st.write("")

    situation = st.text_area(
        "Describe what is happening",
        placeholder="Tell me exactly what you see, hear, smell or feel.",
        height=120,
    )

    if st.button("🚨 Help me now", type="primary"):
        if situation.strip():
            open_prompt(
                "EMERGENCY.\n\n"
                + situation
                + "\n\nGive immediate practical actions first. Keep it concise."
            )
        else:
            st.warning("Describe what is happening.")

# ------------------------- ROUTER -----------------------------

nav()

if st.session_state.page == "home":
    home()
elif st.session_state.page == "chat":
    chat_page()
elif st.session_state.page == "boat":
    boat_page()
elif st.session_state.page == "fix":
    fix_page()
elif st.session_state.page == "trip":
    trip_page()
elif st.session_state.page == "learn":
    learn_page()
elif st.session_state.page == "emergency":
    emergency_page()
else:
    home()
