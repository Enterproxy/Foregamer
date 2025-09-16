import os
import json
import streamlit as st
from styles import TAB3_STYLE
from styles import TAB4_STYLE
from openai import OpenAI
import requests
import re

# ---------- Konfiguracja ----------
LMSTUDIO_API_BASE = "http://127.0.0.1:1234/v1"
MODEL_NAME = os.getenv("LMSTUDIO_MODEL", "mistralai/mistral-7b-instruct-v0.3")

client = OpenAI(base_url=LMSTUDIO_API_BASE, api_key="not-needed")


def summarize_story(story: str, max_tokens: int = 500) -> str:
    """Tworzy krótkie streszczenie świata fantasy na podstawie tekstu."""
    prompt = f"""
You are a fantasy lore summarizer. Read the following story/world lore and produce a concise summary
highlighting factions, important locations, main characters, conflicts, and general world setup.

Story:
{story}

Summary (max {max_tokens} tokens):
"""
    summary = query_llm(prompt, max_tokens=max_tokens)
    return summary


@st.cache_resource
def load_story(path: str = "fantasy.md") -> str:
    """Wczytuje plik z pełnym opisem świata fantasy."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def query_llm(messages_or_prompt, temperature: float = 0.7, max_tokens: int = 1000) -> str:
    """Wysyła zapytanie do modelu (LM Studio API) i zwraca wygenerowaną odpowiedź."""
    url_chat = f"{LMSTUDIO_API_BASE}/chat/completions"
    url_comp = f"{LMSTUDIO_API_BASE}/completions"
    headers = {"Content-Type": "application/json"}

    if isinstance(messages_or_prompt, str):
        messages = [{"role": "user", "content": messages_or_prompt}]
    else:
        messages = list(messages_or_prompt)

    safe_messages = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if role not in ("user", "assistant"):
            content = f"SYSTEM: {content}"
            role = "user"
        safe_messages.append({"role": role, "content": content})

    payload_chat = {
        "model": MODEL_NAME,
        "messages": safe_messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    r = requests.post(url_chat, headers=headers, json=payload_chat, timeout=30)

    if r.status_code == 200:
        data = r.json()
        choice = data.get("choices", [{}])[0]
        text = ((choice.get("message") or {}).get("content")) or choice.get("text") or ""
        return text.strip()

    # fallback do endpointu completions
    joined = []
    for m in safe_messages:
        joined.append(f"{m['role'].upper()}:\n{m['content']}\n")
    single_prompt = "\n".join(joined)

    payload_fallback = {
        "model": MODEL_NAME,
        "prompt": single_prompt,
        "temperature": temperature,
        "max_new_tokens": max_tokens,
    }

    r2 = requests.post(url_comp, headers=headers, json=payload_fallback, timeout=30)

    d2 = r2.json()
    ch = d2.get("choices", [{}])[0]
    text = ch.get("text") or (ch.get("message") or {}).get("content") or ""
    return text.strip()


def answer_question(story: str, question: str) -> str:
    """Odpowiada na pytanie dotyczące świata fantasy na podstawie tekstu historii."""
    prompt = f"""
You are a fantasy lore assistant.
Story:
{story}

Question: {question}
Answer concisely and based only on the story.
"""
    return query_llm(prompt)


GENERATED_NAMES = set()

def generate_npc(story: str, request: str) -> dict:
    """Generuje nowego NPC w formacie JSON zgodnie z zadanymi regułami."""
    prompt = f"""
    You are an NPC generator for a fantasy RPG world. STRICT RULES:
    - Output ONLY valid JSON. No explanations, no Markdown.
    - Use double quotes for keys and string values.
    - Arrays must be normal JSON arrays.
    - No trailing commas. Do not invent fields beyond the schema.
    - Required fields: name, faction, profession, personality_traits (4-6 short traits), backstory_short (<=200 chars).

Story:
{story}

User request: {request}
"""
    raw = query_llm(prompt)
    npc = json.loads(raw)

    if npc["name"] in GENERATED_NAMES:
        npc["name"] += " II"
    GENERATED_NAMES.add(npc["name"])
    return npc


def load_npcs(directory="NPCs"):
    """Ładuje pliki JSON z NPC-ami z podanego katalogu."""
    npcs = {}
    for fname in os.listdir(directory):
        if fname.endswith(".json"):
            with open(os.path.join(directory, fname), "r", encoding="utf-8") as f:
                data = json.load(f)
                npcs[data["name"]] = data
    return npcs


def talk_with_npc(npc, user_input, history):
    """Prowadzenie rozmowy z wybranym NPC, korzystając z historii, opisu świata i charakterystyki postaci."""
    system_prompt = (
        "You are a fantasy RPG character. Always stay in character and make your responses vivid and exaggerated. "
        "Strongly emphasize the character's personality traits, emotions, and quirks in every reply. "
        "If the character is brave, be boldly heroic; if arrogant, be boastful; if shy, be overly hesitant; etc. "
        "Avoid being neutral or generic – your goal is to make the character feel unique and memorable."
    )

    npc_info = (
        f"{system_prompt}\n\n"
        f"Story summary:\n{story_summary}\n\n"
        f"Roleplay as {npc.get('name', 'Unknown')}.\n"
        f"Faction: {npc.get('faction', 'Unknown')}\n"
        f"Profession: {npc.get('profession', 'Unknown')}\n"
        f"Personality traits: {', '.join(npc.get('personality_traits', []))}\n"
        f"Backstory: {npc.get('backstory_short', '')}"
    )

    safe_history = []
    for m in history:
        r = m.get("role", "user")
        c = m.get("content", "")
        if r not in ("user", "assistant"):
            r = "user"
        safe_history.append({"role": r, "content": str(c)})

    messages = [{"role": "user", "content": npc_info}] + safe_history + [{"role": "user", "content": str(user_input)}]

    reply = query_llm(messages, max_tokens=400)
    return reply


def talk_ai_vs_ai(npc1, npc2, history):
    """Rozmowa między dwoma NPC, generując dialog na zmianę."""
    def npc_info(npc, partner_name):
        return (
            f"You are roleplaying as a fantasy RPG character. Stay strictly in character and reply ONLY as this character.\n\n"  
            f"Strongly emphasize the character's personality traits, emotions, and quirks in every reply.\n\n"  
            f"If the character is brave, be boldly heroic; if arrogant, be boastful; if shy, be overly hesitant; etc.\n\n"  
            f"Avoid being neutral or generic – your goal is to make the character feel unique and memorable.\n\n"  
            f"Story summary:\n{story_summary}\n\n"
            f"Your name: {npc.get('name','Unknown')}\n"
            f"Faction: {npc.get('faction','Unknown')}\n"
            f"Profession: {npc.get('profession','Unknown')}\n"
            f"Personality traits: {', '.join(npc.get('personality_traits', []))}\n"
            f"Backstory: {npc.get('backstory_short','')}\n\n"
            f"Important rules:\n"
            f"- Speak ONLY as {npc.get('name','Unknown')}.\n"
            f"- NEVER write lines, actions, or dialogue for {partner_name}.\n"
            f"- Do not prefix your message with your name (no 'Ironheart:'), just speak naturally.\n"
            f"- Keep responses short and natural, like real dialogue (1–3 sentences).\n"
            f"- Do not narrate inner thoughts unless they would realistically be spoken aloud.\n"
            f"- When adressing you partner use their proper name (without surname) instead of NPC1 or NPC2\n"
            f"- If the conversation becomes repetitive,, break the pattern by adding vivid flavor: humor, tension, surprise, or a small twist that keeps the roleplay lively.\n"
        )

    turn = "npc1" if not history or history[-1]["role"] == "npc2" else "npc2"
    speaker = npc1 if turn == "npc1" else npc2
    partner = npc2 if turn == "npc1" else npc1
    partner_name = partner.get("name", "Unknown")

    safe_history = []
    for msg in history:
        safe_history.append({
            "role": "user",
            "content": f"{msg['role']} said: {msg['content']}"
        })

    system = npc_info(speaker, partner_name)
    messages = [{"role": "system", "content": system}] + safe_history

    messages.append({
        "role": "user",
        "content": f"Now continue the conversation. Reply shortly only as {speaker.get('name','Unknown')}."
    })

    reply = query_llm(messages, max_tokens=400)
    return turn, reply.strip()


# ---------- UI ----------
st.set_page_config(page_title="NPC Generator", page_icon="🧙", layout="wide")
st.title("🧙 NPC Generation System")
story_text = load_story()
story_summary = "null" #summarize_story(story_text)

tab1, tab2, tab3, tab4 = st.tabs(["📖 Story Q&A", "🧙 NPC Generator", "💬 Talk with NPC", "⚔️ AI vs AI"])

# --- Zakładka 1: Pełna historia świata ---
with tab1:
    st.subheader("Ask about the story world")
    q = st.text_area("Your question", "Who are the main factions?")
    if st.button("Ask", type="primary"):
        ans = answer_question(story_text, q)
        st.markdown("**Answer:**")
        st.write(ans)

# --- Zakładka 2: Generowanie NPC ---
with tab2:
    st.subheader("Generate a new NPC")
    req = st.text_area("Character request", "Create a noble warrior from the ironhold clans.")

    if st.button("Generate NPC", type="primary"):
        npc = generate_npc(story_text, req)
        st.session_state["last_npc"] = npc

    if "last_npc" in st.session_state:
        npc = st.session_state["last_npc"]
        st.json(npc)

        npc_json_str = json.dumps(npc, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Download NPC JSON",
            data=npc_json_str,
            file_name=f"{npc['name'].replace(' ', '_')}.json",
            mime="application/json"
        )

# --- Zakładka 3: Rozmowa z NPC ---
with tab3:
    st.subheader("Talk with an NPC")
    npcs = load_npcs()
    if not npcs:
        st.warning("No NPCs found in the NPCs/ directory. Generate one, download the JSON, and put it there.")
    else:
        npc_name = st.selectbox("Choose an NPC to talk to:", list(npcs.keys()))
        selected_npc = npcs[npc_name]

        st.markdown(f"**Talking with {selected_npc['name']}**")
        st.json(selected_npc)

        hist_key = f"chat_history_{npc_name}"
        input_key = f"user_input_{npc_name}"

        if hist_key not in st.session_state:
            st.session_state[hist_key] = []
        if input_key not in st.session_state:
            st.session_state[input_key] = ""

        def send_message(n=npc_name, npc_obj=selected_npc, hk=hist_key, ik=input_key):
            user_text = st.session_state[ik].strip()
            if not user_text:
                return
            history = st.session_state.get(hk, [])
            reply = talk_with_npc(npc_obj, user_text, history)
            history.append({"role": "user", "content": user_text})
            history.append({"role": "assistant", "content": reply})
            st.session_state[hk] = history
            st.session_state[ik] = ""  # reset inputa

        user_text = st.chat_input("Type your message...")
        if user_text:
            st.session_state[input_key] = user_text
            send_message()

        def _esc(s: str) -> str:
            return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>"))

        history = st.session_state[hist_key]
        html = TAB3_STYLE

        # zmiana kolejnosci czatu
        for msg in reversed(history):
            content_html = _esc(msg["content"])
            if msg["role"] == "user":
                html += f"<div class='msg user'><div class='meta'>You</div><div>{content_html}</div></div>"
            else:
                html += f"<div class='msg npc'><div class='meta'>{_esc(selected_npc['name'])}</div><div>{content_html}</div></div>"

        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

# --- Zakładka 4: Rozmowa NPC vs NPC ---
with tab4:
    st.subheader("AI talks to AI")

    npcs = load_npcs()
    if len(npcs) < 2:
        st.warning("You need at least 2 NPC JSON files in the NPCs/ directory.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            npc1_name = st.selectbox("Choose first NPC:", list(npcs.keys()), key="npc1_select")
        with col2:
            npc2_name = st.selectbox("Choose second NPC:", list(npcs.keys()), key="npc2_select")

        npc1, npc2 = npcs[npc1_name], npcs[npc2_name]

        init_context = st.text_area("Initial situation/context:",
                                    "They meet in a tavern and talk about their adventures over beer.")

        if st.button("Start new conversation", type="primary"):
            hist_key = f"ai_vs_ai_{npc1_name}_{npc2_name}"
            st.session_state[hist_key] = [{"role": "context", "content": init_context}]

        hist_key = f"ai_vs_ai_{npc1_name}_{npc2_name}"
        if hist_key in st.session_state:
            history = st.session_state[hist_key]

            if st.button("Next turn"):
                turn, msg = talk_ai_vs_ai(npc1, npc2, history)
                history.append({"role": turn, "content": msg})
                st.session_state[hist_key] = history

            # renderowanie czatu
            def _esc(s: str) -> str:
                return (s.replace("&", "&amp;")
                          .replace("<", "&lt;")
                          .replace(">", "&gt;")
                          .replace("\n", "<br>"))


            html = TAB4_STYLE

            for msg in reversed(history):
                if msg["role"] == "npc1":
                    html += f"<div class='msg npc1'><div class='meta'>{_esc(npc1_name)}</div><div>{_esc(msg['content'])}</div></div>"
                elif msg["role"] == "npc2":
                    html += f"<div class='msg npc2'><div class='meta'>{_esc(npc2_name)}</div><div>{_esc(msg['content'])}</div></div>"
                elif msg["role"] == "context":
                    html += f"<div class='msg context'><div>📜 {_esc(msg['content'])}</div></div>"

            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)