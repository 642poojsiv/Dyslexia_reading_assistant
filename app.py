import streamlit as st
from groq import Groq
from gtts import gTTS
import io
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def simplify(text):
    client = Groq(api_key=GROQ_API_KEY)
    chat = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": (
                "Rewrite this text for a dyslexic reader. "
                "Output the simplified text only. No commentary.\n\n"
                "Text:\n" + text
            )
        }]
    )
    return chat.choices[0].message.content

def extract_difficult_words(text):
    client = Groq(api_key=GROQ_API_KEY)
    chat = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": (
                "Extract the 8 most difficult or complex words from this text "
                "that a dyslexic student might struggle to pronounce. "
                "Output only the words separated by commas, nothing else. "
                "No numbering, no explanation.\n\n"
                "Text:\n" + text
            )
        }]
    )
    words = chat.choices[0].message.content.strip()
    return [w.strip() for w in words.split(",") if w.strip()]

def pronounce_word(word):
    client = Groq(api_key=GROQ_API_KEY)
    chat = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": (
                "Help a dyslexic student pronounce this word. Do the following:\n"
                "1. Break it into syllables with hyphens (e.g. pho-to-syn-the-sis)\n"
                "2. Write a simple phonetic pronunciation using easy everyday words (e.g. sounds like: foh-toh-SIN-thuh-sis)\n"
                "3. Give a one sentence meaning in very simple words\n"
                "4. Give a simple example sentence using the word\n\n"
                "Format your response exactly like this:\n"
                "Syllables: ...\n"
                "Sounds like: ...\n"
                "Meaning: ...\n"
                "Example: ...\n\n"
                "Word: " + word
            )
        }]
    )
    return chat.choices[0].message.content.strip()

def show_pronunciation(word):
    with st.spinner(f"Breaking down **{word}**..."):
        breakdown = pronounce_word(word)

    lines = breakdown.split("\n")
    for line in lines:
        if line.startswith("Syllables:"):
            syllables = line.replace("Syllables:", "").strip()
            st.markdown(f"""
            <div style="background:#E8F4FD;padding:15px;border-radius:10px;
            font-size:28px;font-family:Verdana;text-align:center;
            letter-spacing:4px;color:#1a73e8;font-weight:bold;">
            {syllables}
            </div>""", unsafe_allow_html=True)

        elif line.startswith("Sounds like:"):
            sounds = line.replace("Sounds like:", "").strip()
            st.markdown(f"""
            <div style="background:#FFF3E0;padding:15px;border-radius:10px;
            font-size:22px;font-family:Verdana;text-align:center;
            color:#E65100;margin-top:10px;">
            🔊 {sounds}
            </div>""", unsafe_allow_html=True)

        elif line.startswith("Meaning:"):
            meaning = line.replace("Meaning:", "").strip()
            st.markdown(f"**📖 Meaning:** {meaning}")

        elif line.startswith("Example:"):
            example = line.replace("Example:", "").strip()
            st.markdown(f"**✏️ Example:** *{example}*")

    st.divider()
    with st.spinner("Generating audio..."):
        tts = gTTS(text=word, lang="en", slow=True)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        st.write("🎧 Listen to the pronunciation:")
        st.audio(buf.getvalue(), format="audio/mp3")

# ─── APP ───
st.set_page_config(page_title="Dyslexia Assistant", layout="centered")
st.title("Dyslexia Reading Assistant")

tab1, tab2 = st.tabs(["📖 Text Simplifier", "🔤 Pronunciation Helper"])

# ════════════════════════════════════════
# TAB 1 — Text Simplifier
# ════════════════════════════════════════
with tab1:
    user_input = st.text_area("Paste complex text here:", height=160)

    if st.button("Simplify & Read"):
        if not user_input.strip():
            st.warning("Please enter some text.")
        else:
            with st.spinner("Simplifying text..."):
                result = simplify(user_input)
            
            # Save to session so Tab 2 can use it
            st.session_state["simplified_text"] = result
            st.session_state["original_text"] = user_input

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Original")
                st.info(user_input)
            with col2:
                st.subheader("Simplified")
                st.markdown(f"""
                <div style="font-family:Verdana;background:#FFFDD0;padding:20px;
                border-radius:12px;font-size:20px;line-height:1.9;color:#333;">
                {result}
                </div>""", unsafe_allow_html=True)

            st.divider()
            with st.spinner("Generating audio..."):
                tts = gTTS(text=result, lang="en", slow=True)
                buf = io.BytesIO()
                tts.write_to_fp(buf)
                st.audio(buf.getvalue(), format="audio/mp3")

# ════════════════════════════════════════
# TAB 2 — Pronunciation Helper
# ════════════════════════════════════════
with tab2:
    st.subheader("🔤 Pronunciation Helper")

    # ── Option 1: Use words from Tab 1 ──
    if "simplified_text" in st.session_state:
        st.success("✅ Words extracted from your text! Click any word to learn how to say it.")

        with st.spinner("Extracting difficult words..."):
            if "difficult_words" not in st.session_state:
                st.session_state["difficult_words"] = extract_difficult_words(
                    st.session_state["original_text"]
                )

        words = st.session_state["difficult_words"]

        # Show words as clickable buttons in a row
        st.write("👇 Pick a word:")
        cols = st.columns(4)
        for i, word in enumerate(words):
            with cols[i % 4]:
                if st.button(word, key=f"word_{i}"):
                    st.session_state["selected_word"] = word

        # Show pronunciation for selected word
        if "selected_word" in st.session_state:
            st.divider()
            st.subheader(f"📝 {st.session_state['selected_word']}")
            show_pronunciation(st.session_state["selected_word"])

    else:
        st.info("💡 First go to **Text Simplifier** tab, paste your text and click Simplify — difficult words will appear here automatically!")

    # ── Option 2: Manual word entry ──
    st.divider()
    st.write("Or type any word manually:")
    word_input = st.text_input("Enter a word:", placeholder="e.g. photosynthesis, algorithm")
    if st.button("Help me pronounce it!"):
        if not word_input.strip():
            st.warning("Please enter a word.")
        else:
            st.session_state["selected_word"] = word_input.strip()
            show_pronunciation(word_input.strip())