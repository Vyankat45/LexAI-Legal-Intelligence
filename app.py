import streamlit as st
from langchain_openai import ChatOpenAI
import os
import html
import markdown as md_lib
from langchain_core.output_parsers import StrOutputParser
from prompts import analysis_prompt, advice_prompt
from langchain_core.runnables import RunnablePassthrough

# ================== CONFIG ==================
st.set_page_config(
    page_title="LexAI — Legal Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== PREMIUM CSS ==================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600;700&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
/* ===========================
   CSS VARIABLES & RESET
=========================== */
:root {
    --gold:       #c9a84c;
    --gold-light: #e8c96e;
    --gold-dim:   #7a5f2a;
    --ink:        #08090d;
    --ink-2:      #0e1018;
    --ink-3:      #161923;
    --ink-4:      #1e2330;
    --smoke:      #2a3044;
    --mist:       #3d4a60;
    --silver:     #8896b0;
    --cloud:      #c8d0df;
    --white:      #f0f2f6;
    --red-dim:    #7a2a2a;
    --green-dim:  #2a5a3a;
    --radius-sm:  8px;
    --radius-md:  16px;
    --radius-lg:  24px;
    --shadow:     0 8px 40px rgba(0,0,0,0.5);
    --glow:       0 0 30px rgba(201,168,76,0.15);
}

/* ===========================
   GLOBAL RESET
=========================== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    font-family: 'DM Sans', sans-serif;
    background: var(--ink) !important;
    color: var(--cloud);
    min-height: 100vh;
    overflow-x: hidden;
}

/* ===========================
   ANIMATED BACKGROUND
=========================== */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    z-index: 0;
    background:
        radial-gradient(ellipse 80% 60% at 15% 10%,  rgba(201,168,76,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 85% 80%,  rgba(37,99,235,0.08)  0%, transparent 55%),
        radial-gradient(ellipse 70% 70% at 50% 50%,  rgba(14,16,24,0.9)    0%, transparent 100%),
        linear-gradient(160deg, #08090d 0%, #0e1018 40%, #111620 100%);
    pointer-events: none;
}

.stApp::after {
    content: '';
    position: fixed;
    inset: 0;
    z-index: 0;
    background-image:
        radial-gradient(1px 1px at 20% 30%, rgba(201,168,76,0.3) 0%, transparent 100%),
        radial-gradient(1px 1px at 80% 70%, rgba(201,168,76,0.2) 0%, transparent 100%),
        radial-gradient(1px 1px at 40% 80%, rgba(200,208,223,0.15) 0%, transparent 100%),
        radial-gradient(1px 1px at 70% 20%, rgba(200,208,223,0.15) 0%, transparent 100%);
    background-size: 400px 400px, 600px 600px, 300px 300px, 500px 500px;
    animation: stars 120s linear infinite;
    pointer-events: none;
    opacity: 0.6;
}

@keyframes stars {
    from { background-position: 0 0, 0 0, 0 0, 0 0; }
    to   { background-position: 400px 400px, -600px 600px, 300px -300px, -500px 500px; }
}

/* ===========================
   ORBS (floating ambient blobs)
=========================== */
.orb-container {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    overflow: hidden;
}
.orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.12;
    animation: float 20s ease-in-out infinite;
}
.orb-1 {
    width: 500px; height: 500px;
    background: radial-gradient(circle, #c9a84c, transparent);
    top: -150px; left: -100px;
    animation-duration: 25s;
}
.orb-2 {
    width: 600px; height: 600px;
    background: radial-gradient(circle, #2563eb, transparent);
    bottom: -200px; right: -100px;
    animation-duration: 30s;
    animation-delay: -10s;
}
.orb-3 {
    width: 300px; height: 300px;
    background: radial-gradient(circle, #c9a84c, transparent);
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    animation-duration: 18s;
    animation-delay: -5s;
    opacity: 0.06;
}
@keyframes float {
    0%, 100% { transform: translate(0, 0) scale(1); }
    33%       { transform: translate(40px, -30px) scale(1.05); }
    66%       { transform: translate(-30px, 40px) scale(0.95); }
}

/* ===========================
   STREAMLIT LAYOUT WRAPPERS
=========================== */
.block-container {
    position: relative;
    z-index: 1;
    max-width: 1100px !important;
    padding: 2rem 2rem 6rem !important;
}

/* ===========================
   HEADER BLOCK
=========================== */
.lex-header {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 28px 0 8px;
    border-bottom: 1px solid rgba(201,168,76,0.18);
    margin-bottom: 8px;
    animation: fadeDown 0.8s ease both;
}
.lex-logo {
    font-size: 3rem;
    line-height: 1;
    filter: drop-shadow(0 0 14px rgba(201,168,76,0.5));
    animation: pulseGlow 3s ease-in-out infinite;
}
@keyframes pulseGlow {
    0%, 100% { filter: drop-shadow(0 0 14px rgba(201,168,76,0.4)); }
    50%       { filter: drop-shadow(0 0 28px rgba(201,168,76,0.8)); }
}
.lex-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.6rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    background: linear-gradient(135deg, var(--gold-light), var(--gold), var(--cloud));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
}
.lex-subtitle {
    font-size: 0.78rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--silver);
    margin-top: 4px;
}
@keyframes fadeDown {
    from { opacity: 0; transform: translateY(-20px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ===========================
   STATUS BAR
=========================== */
.status-bar {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 10px 0 18px;
    font-size: 0.74rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--silver);
    animation: fadeIn 1s ease 0.3s both;
}
.status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #4ade80;
    box-shadow: 0 0 8px #4ade80;
    animation: blink 2s ease-in-out infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
}
.status-sep { color: rgba(201,168,76,0.35); }

/* ===========================
   CHAT AREA
=========================== */
.chat-wrapper {
    display: flex;
    flex-direction: column;
    gap: 18px;
    padding: 8px 0 24px;
    min-height: 200px;
    animation: fadeIn 0.6s ease both;
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}

/* ===========================
   MESSAGE BUBBLES
=========================== */
.msg-row {
    display: flex;
    gap: 14px;
    animation: slideUp 0.4s cubic-bezier(0.22, 1, 0.36, 1) both;
}
@keyframes slideUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
.msg-row.user  { flex-direction: row-reverse; }
.msg-row.bot   { flex-direction: row; }

.msg-avatar {
    width: 38px; height: 38px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
    border: 1px solid rgba(201,168,76,0.25);
    background: var(--ink-3);
}
.msg-row.user .msg-avatar {
    background: linear-gradient(135deg, #1e3a8a, #1d4ed8);
    border-color: rgba(59,130,246,0.35);
}

.msg-bubble {
    max-width: 72%;
    padding: 14px 18px;
    border-radius: var(--radius-md);
    font-size: 0.93rem;
    line-height: 1.65;
    position: relative;
}
.msg-row.user .msg-bubble {
    background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 100%);
    border: 1px solid rgba(59,130,246,0.3);
    border-top-right-radius: 4px;
    color: #e0eaff;
    box-shadow: 0 4px 24px rgba(29,78,216,0.3), var(--glow);
}
.msg-row.bot .msg-bubble {
    background: linear-gradient(135deg, var(--ink-3) 0%, var(--ink-4) 100%);
    border: 1px solid rgba(201,168,76,0.18);
    border-top-left-radius: 4px;
    color: var(--cloud);
    box-shadow: 0 4px 24px rgba(0,0,0,0.4), 0 0 0 1px rgba(201,168,76,0.06);
}

/* Gold accent bar on bot messages */
.msg-row.bot .msg-bubble::before {
    content: '';
    position: absolute;
    left: 0; top: 14px; bottom: 14px;
    width: 2.5px;
    background: linear-gradient(to bottom, var(--gold), transparent);
    border-radius: 0 2px 2px 0;
}

.msg-meta {
    font-size: 0.68rem;
    color: var(--silver);
    margin-top: 5px;
    letter-spacing: 0.06em;
    text-align: right;
}
.msg-row.bot .msg-meta { text-align: left; }

/* ===========================
   EMPTY STATE
=========================== */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    text-align: center;
    gap: 16px;
    color: var(--silver);
    animation: fadeIn 1s ease 0.5s both;
    opacity: 0;
}
.empty-icon {
    font-size: 3.5rem;
    filter: drop-shadow(0 0 18px rgba(201,168,76,0.4));
    animation: pulseGlow 3s ease-in-out infinite;
}
.empty-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.5rem;
    color: var(--cloud);
    letter-spacing: 0.04em;
}
.empty-body {
    font-size: 0.84rem;
    line-height: 1.7;
    max-width: 420px;
    color: var(--silver);
}
.pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin-top: 8px;
}
.pill {
    padding: 6px 14px;
    border: 1px solid rgba(201,168,76,0.25);
    border-radius: 999px;
    font-size: 0.75rem;
    color: var(--gold);
    background: rgba(201,168,76,0.06);
    letter-spacing: 0.06em;
}

/* ===========================
   INPUT AREA
=========================== */
.stTextInput > div > div > input {
    background: var(--ink-3) !important;
    border: 1px solid rgba(201,168,76,0.25) !important;
    border-radius: var(--radius-md) !important;
    color: var(--white) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.93rem !important;
    padding: 14px 18px !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.stTextInput > div > div > input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.12), 0 0 20px rgba(201,168,76,0.1) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder {
    color: var(--mist) !important;
}
label[data-testid="stWidgetLabel"] {
    color: var(--silver) !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
}

/* ===========================
   SPINNER
=========================== */
.stSpinner > div {
    border-color: var(--gold) transparent transparent transparent !important;
}

/* ===========================
   SIDEBAR
=========================== */
section[data-testid="stSidebar"] {
    background: var(--ink-2) !important;
    border-right: 1px solid rgba(201,168,76,0.12);
}
section[data-testid="stSidebar"] .block-container {
    padding: 2rem 1.2rem !important;
}
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 24px;
    padding-bottom: 20px;
    border-bottom: 1px solid rgba(201,168,76,0.15);
}
.sidebar-brand-icon { font-size: 1.6rem; }
.sidebar-brand-text {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--gold-light);
    letter-spacing: 0.05em;
}
.sidebar-section {
    margin: 20px 0;
}
.sidebar-label {
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--gold-dim);
    margin-bottom: 10px;
    font-weight: 500;
}
.sidebar-feature {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-radius: var(--radius-sm);
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 7px;
    font-size: 0.83rem;
    color: var(--cloud);
}
.feat-icon { font-size: 1rem; }
.sidebar-stat {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 0.8rem;
}
.stat-label { color: var(--silver); }
.stat-value { color: var(--gold); font-family: 'DM Mono', monospace; }
.sidebar-disclaimer {
    font-size: 0.72rem;
    color: var(--mist);
    line-height: 1.6;
    padding: 12px;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: var(--radius-sm);
    background: rgba(255,255,255,0.02);
    margin-top: 24px;
}

/* ===========================
   BUTTONS
=========================== */
.stButton > button {
    background: linear-gradient(135deg, rgba(201,168,76,0.12), rgba(201,168,76,0.06)) !important;
    color: var(--gold-light) !important;
    border: 1px solid rgba(201,168,76,0.3) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.83rem !important;
    letter-spacing: 0.06em !important;
    padding: 8px 16px !important;
    transition: all 0.2s ease !important;
    width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(201,168,76,0.22), rgba(201,168,76,0.12)) !important;
    border-color: var(--gold) !important;
    box-shadow: 0 0 20px rgba(201,168,76,0.2) !important;
    transform: translateY(-1px) !important;
}

/* ===========================
   DIVIDER
=========================== */
hr {
    border: none !important;
    border-top: 1px solid rgba(201,168,76,0.15) !important;
    margin: 16px 0 !important;
}

/* ===========================
   SCROLLBAR
=========================== */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--ink-2); }
::-webkit-scrollbar-thumb { background: var(--smoke); border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold-dim); }

/* ===========================
   SELECTBOX / OTHER WIDGETS
=========================== */
.stSelectbox div[data-baseweb="select"] > div {
    background: var(--ink-3) !important;
    border-color: rgba(201,168,76,0.2) !important;
}

/* ===========================
   TYPING INDICATOR
=========================== */
.typing-indicator {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 10px 16px;
    background: var(--ink-3);
    border: 1px solid rgba(201,168,76,0.15);
    border-radius: var(--radius-md);
    border-top-left-radius: 4px;
    width: fit-content;
}
.typing-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--gold);
    animation: typingDot 1.4s ease-in-out infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typingDot {
    0%, 60%, 100% { opacity: 0.2; transform: scale(0.8); }
    30%            { opacity: 1;   transform: scale(1.2); }
}

/* ===========================
   MARKDOWN INSIDE BOT BUBBLES
=========================== */
.msg-bubble table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
    font-size: 0.85rem;
}
.msg-bubble table th {
    background: rgba(201,168,76,0.12);
    color: var(--gold-light);
    padding: 8px 12px;
    text-align: left;
    border: 1px solid rgba(201,168,76,0.2);
    font-weight: 600;
    letter-spacing: 0.04em;
}
.msg-bubble table td {
    padding: 7px 12px;
    border: 1px solid rgba(255,255,255,0.07);
    color: var(--cloud);
    vertical-align: top;
    line-height: 1.5;
}
.msg-bubble table tr:nth-child(even) td {
    background: rgba(255,255,255,0.02);
}
.msg-bubble strong { color: var(--gold-light); font-weight: 600; }
.msg-bubble em     { color: var(--silver); font-style: italic; }
.msg-bubble ul, .msg-bubble ol {
    padding-left: 20px;
    margin: 8px 0;
}
.msg-bubble li     { margin-bottom: 4px; line-height: 1.6; }
.msg-bubble h1, .msg-bubble h2, .msg-bubble h3 {
    font-family: 'Cormorant Garamond', serif;
    color: var(--gold-light);
    margin: 12px 0 6px;
    letter-spacing: 0.03em;
}
.msg-bubble h1 { font-size: 1.2rem; }
.msg-bubble h2 { font-size: 1.05rem; }
.msg-bubble h3 { font-size: 0.95rem; }
.msg-bubble p  { margin: 6px 0; }
.msg-bubble hr {
    border: none !important;
    border-top: 1px solid rgba(201,168,76,0.15) !important;
    margin: 10px 0 !important;
}
.msg-bubble code {
    background: rgba(201,168,76,0.08);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    color: var(--gold);
}
.msg-bubble blockquote {
    border-left: 3px solid var(--gold-dim);
    margin: 8px 0;
    padding: 4px 12px;
    color: var(--silver);
    font-style: italic;
}

/* ===========================
   API KEY SECTION
=========================== */
.api-key-box {
    background: rgba(201,168,76,0.04);
    border: 1px solid rgba(201,168,76,0.2);
    border-radius: var(--radius-sm);
    padding: 14px;
    margin-bottom: 6px;
}
.api-key-title {
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--gold-dim);
    margin-bottom: 10px;
    font-weight: 500;
}
.api-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.75rem;
    margin-top: 8px;
    padding: 6px 10px;
    border-radius: 6px;
}
.api-status.ok  { background: rgba(74,222,128,0.08); color: #4ade80; border: 1px solid rgba(74,222,128,0.2); }
.api-status.err { background: rgba(248,113,113,0.08); color: #f87171; border: 1px solid rgba(248,113,113,0.2); }
.api-status-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; flex-shrink: 0; }

/* ===========================
   STREAMLIT OVERRIDES
=========================== */
.stMarkdown p { color: var(--cloud); }
footer { display: none !important; }
#MainMenu { display: none !important; }
header[data-testid="stHeader"] {
    background: transparent !important;
    border-bottom: none !important;
}
</style>

<!-- Floating orbs -->
<div class="orb-container">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
</div>
""", unsafe_allow_html=True)


# ================== SESSION STATE ==================
if "memory" not in st.session_state:
    st.session_state.memory = []
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "msg_count" not in st.session_state:
    st.session_state.msg_count = 0
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "key_saved" not in st.session_state:
    st.session_state.key_saved = False

# ================== MODEL (lazy, rebuilds on key change) ==================
def build_chain(api_key: str):
    _model = ChatOpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
        model="openai/gpt-oss-20b",
        temperature=0.7
    )
    _parser = StrOutputParser()
    _analysis_chain = analysis_prompt | _model | _parser
    _chain = (
        {
            "analysis_output": _analysis_chain,
            "chat_history": lambda x: x["chat_history"]
        }
        | advice_prompt
        | _model
        | _parser
    )
    return _model, _chain

def format_memory(memory):
    return "\n".join(memory)

def time_label():
    from datetime import datetime
    return datetime.now().strftime("%H:%M")

# ================== TOPIC GUARD ==================
def is_legal_question(text: str, api_key: str) -> bool:
    """Returns True only if the message is related to legal matters."""
    guard = ChatOpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
        model="openai/gpt-oss-20b",
        temperature=0
    )
    prompt = f"""You are a strict legal topic classifier.

Decide if the user message is related to legal matters.

LEGAL topics include: contracts, disputes, rights, laws, courts, crime, liability,
employment law, tenant rights, family law, intellectual property, business law,
immigration, consumer protection, defamation, fraud, negligence, legal procedures,
legal documents, legal advice, and anything requiring legal analysis.

NOT legal: coding, technology, general knowledge, personal trivia, jokes, cooking,
sports, science, math, history, entertainment, software deployment, and anything
unrelated to law.

User message: "{text}"

Reply with ONLY one word — YES or NO. No explanation."""
    result = guard.invoke(prompt)
    return result.content.strip().upper().startswith("YES")

import random
_REFUSALS = [
    "I'm **LexAI** — a specialized legal intelligence assistant. I can only help with legal matters such as contracts, disputes, tenant rights, employment issues, court procedures, and more.\n\nCould you describe a legal situation you need help with?",
    "That question is outside my scope. I'm built exclusively for **legal analysis and case guidance**.\n\nFeel free to ask about contracts, liability, family law, business disputes, or any legal concern you have.",
    "I'm designed specifically for **legal questions**. I'm not able to assist with that topic.\n\nIf you have a legal matter — a dispute, rights question, or contract issue — I'm here to help.",
]
def get_refusal() -> str:
    return random.choice(_REFUSALS)

# ================== SIDEBAR ==================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <span class="sidebar-brand-icon">⚖️</span>
        <span class="sidebar-brand-text">LexAI</span>
    </div>
    """, unsafe_allow_html=True)

    # ── API KEY SECTION ──────────────────────────────
    st.markdown('<div class="api-key-title">🔑 &nbsp;API Configuration</div>', unsafe_allow_html=True)
    st.markdown('<div class="api-key-box">', unsafe_allow_html=True)

    entered_key = st.text_input(
        "Groq API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="gsk_••••••••••••••••••••",
        key="api_key_input",
        label_visibility="collapsed"
    )

    col_save, col_clear = st.columns(2)
    with col_save:
        if st.button("💾 Save Key", use_container_width=True):
            if entered_key.strip():
                st.session_state.api_key = entered_key.strip()
                st.session_state.key_saved = True
                st.rerun()
            else:
                st.session_state.key_saved = False
    with col_clear:
        if st.button("🗑 Clear Key", use_container_width=True):
            st.session_state.api_key = ""
            st.session_state.key_saved = False
            st.rerun()

    if st.session_state.key_saved and st.session_state.api_key:
        masked = st.session_state.api_key[:6] + "••••••••" + st.session_state.api_key[-4:]
        st.markdown(f'''
        <div class="api-status ok">
            <div class="api-status-dot"></div>
            Key active &nbsp;·&nbsp; {masked}
        </div>''', unsafe_allow_html=True)
    else:
        st.markdown('''
        <div class="api-status err">
            <div class="api-status-dot"></div>
            No key set — enter key above
        </div>''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── CAPABILITIES ────────────────────────────────
    st.markdown('<div class="sidebar-label">Capabilities</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-feature"><span class="feat-icon">🔍</span> Case Analysis & Risk Assessment</div>
    <div class="sidebar-feature"><span class="feat-icon">📋</span> Legal Document Guidance</div>
    <div class="sidebar-feature"><span class="feat-icon">🛡️</span> Rights & Liability Mapping</div>
    <div class="sidebar-feature"><span class="feat-icon">🤝</span> Contract Clause Review</div>
    <div class="sidebar-feature"><span class="feat-icon">⚡</span> Jurisdiction-Aware Advice</div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── SESSION STATS ────────────────────────────────
    st.markdown('<div class="sidebar-label">Session Stats</div>', unsafe_allow_html=True)
    total_msgs = len(st.session_state.memory)
    user_msgs  = sum(1 for m in st.session_state.memory if m["role"] == "user")
    st.markdown(f"""
    <div class="sidebar-stat">
        <span class="stat-label">Messages</span>
        <span class="stat-value">{total_msgs:02d}</span>
    </div>
    <div class="sidebar-stat">
        <span class="stat-label">Queries</span>
        <span class="stat-value">{user_msgs:02d}</span>
    </div>
    <div class="sidebar-stat">
        <span class="stat-label">Model</span>
        <span class="stat-value">GPT-OSS-20B</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    if st.button("🧹  Clear Conversation"):
        st.session_state.memory = []
        st.session_state.input_key += 1
        st.rerun()

    st.markdown("""
    <div class="sidebar-disclaimer">
        ⚠️ LexAI provides general legal information only. 
        This does not constitute legal advice. Consult a 
        qualified attorney for your specific situation.
    </div>
    """, unsafe_allow_html=True)


# ================== HEADER ==================
st.markdown("""
<div class="lex-header">
    <div class="lex-logo">⚖️</div>
    <div>
        <div class="lex-title">LexAI Legal Intelligence</div>
        <div class="lex-subtitle">Case Analysis · Risk Assessment · Legal Guidance</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="status-bar">
    <div class="status-dot"></div>
    <span>System Operational</span>
    <span class="status-sep">|</span>
    <span>AI Engine Active</span>
    <span class="status-sep">|</span>
    <span>Secure Session</span>
</div>
""", unsafe_allow_html=True)

# ================== CHAT DISPLAY ==================
st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)

if not st.session_state.memory:
    if not st.session_state.key_saved or not st.session_state.api_key:
        # ── No key yet: show onboarding prompt ──────────────────
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🔑</div>
            <div class="empty-title">Enter Your API Key to Begin</div>
            <div class="empty-body">
                LexAI runs on your own <strong style="color:var(--gold)">Groq API key</strong>.<br>
                Paste it in the sidebar and click <strong style="color:var(--gold)">Save Key</strong> — 
                your key is never stored on any server.
            </div>
            <div class="pill-row" style="margin-top:20px;">
                <span class="pill">① Open sidebar</span>
                <span class="pill">② Paste Groq key</span>
                <span class="pill">③ Click Save Key</span>
                <span class="pill">④ Ask your legal question</span>
            </div>
            <div class="empty-body" style="margin-top:18px; font-size:0.76rem;">
                Don't have a key? Get one free at
                <a href="https://console.groq.com/keys" target="_blank"
                   style="color:var(--gold);text-decoration:underline;">
                   console.groq.com/keys
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── Key set, no messages yet: show topic pills ───────────
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">⚖️</div>
            <div class="empty-title">How can I assist you today?</div>
            <div class="empty-body">
                Describe your legal situation in plain language. 
                I'll analyze the key issues, identify risks, and provide 
                structured guidance tailored to your case.
            </div>
            <div class="pill-row">
                <span class="pill">Contract Disputes</span>
                <span class="pill">Employment Law</span>
                <span class="pill">Tenant Rights</span>
                <span class="pill">Business Liability</span>
                <span class="pill">Intellectual Property</span>
                <span class="pill">Family Law</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    for i, msg in enumerate(st.session_state.memory):
        delay = min(i * 0.05, 0.4)
        if msg["role"] == "user":
            # Escape user input to prevent HTML injection
            safe_content = html.escape(msg['content'])
            st.markdown(f"""
            <div class="msg-row user" style="animation-delay:{delay}s">
                <div>
                    <div class="msg-bubble">{safe_content}</div>
                    <div class="msg-meta">You · {msg.get('time', '—')}</div>
                </div>
                <div class="msg-avatar">🧑</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Convert markdown → HTML so tables, bold, lists render correctly
            html_content = md_lib.markdown(
                msg['content'],
                extensions=['tables', 'nl2br', 'fenced_code']
            )
            st.markdown(f"""
            <div class="msg-row bot" style="animation-delay:{delay}s">
                <div class="msg-avatar">⚖️</div>
                <div>
                    <div class="msg-bubble">{html_content}</div>
                    <div class="msg-meta">LexAI · {msg.get('time', '—')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ================== INPUT ==================
col_input, col_btn = st.columns([6, 1])

with col_input:
    user_input = st.text_input(
        "DESCRIBE YOUR LEGAL MATTER",
        placeholder="e.g. My landlord is refusing to return my security deposit after I moved out...",
        key=f"user_input_{st.session_state.input_key}"
    )

with col_btn:
    st.markdown("<div style='height:27px'></div>", unsafe_allow_html=True)  # align with input
    submitted = st.button("⚖️ Submit", use_container_width=True)

# ================== HANDLE INPUT ==================
if submitted and user_input:
    # ── API KEY CHECK ─────────────────────────────────────────
    if not st.session_state.api_key or not st.session_state.key_saved:
        st.markdown("""
        <div class="api-status err" style="margin-top:12px; font-size:0.82rem; padding:10px 14px;">
            <div class="api-status-dot"></div>
            &nbsp;No API key configured. Please add your Groq API key in the sidebar to get started.
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    active_key = st.session_state.api_key
    t = time_label()
    st.session_state.memory.append({
        "role": "user",
        "content": user_input,
        "time": t
    })

    # Show typing indicator
    typing_placeholder = st.empty()
    typing_placeholder.markdown("""
    <div class="msg-row bot" style="margin-top:8px;">
        <div class="msg-avatar">⚖️</div>
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner(""):
        # ── GUARD: only process legal questions ──────────────────
        if not is_legal_question(user_input, active_key):
            response = get_refusal()
        else:
            _, chain = build_chain(active_key)
            chat_history = format_memory(
                [m["content"] for m in st.session_state.memory]
            )
            response = chain.invoke({
                "user_input": user_input,
                "chat_history": chat_history
            })

    typing_placeholder.empty()

    st.session_state.memory.append({
        "role": "assistant",
        "content": response,
        "time": time_label()
    })

    st.session_state.input_key += 1
    st.rerun()