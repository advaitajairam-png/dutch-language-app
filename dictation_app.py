import streamlit as st
import re
import importlib
from pathlib import Path
import json
from datetime import date

# -------------------------
# CONFIG
# -------------------------

DATA_FILE = "user_progress.json"

# -------------------------
# LOAD / SAVE DATA
# -------------------------

def load_data():
    if Path(DATA_FILE).exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

# -------------------------
# NORMALIZATION
# -------------------------

def normalize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()

# -------------------------
# STRICT SCORING
# -------------------------

def score_sentence(user_input, correct):
    user_words = normalize(user_input).split()
    correct_words = normalize(correct).split()

    total = len(correct_words)
    correct_count = 0

    for i, word in enumerate(correct_words):
        if i < len(user_words) and user_words[i] == word:
            correct_count += 1

    accuracy = round((correct_count / total) * 100, 2)
    return accuracy

# -------------------------
# STREAMLIT UI
# -------------------------

st.set_page_config(page_title="Dutch Dictation Trainer", layout="centered")
st.title("Dutch Dictation Trainer")

lessons_path = Path("lessons")
available_lessons = sorted([f.name for f in lessons_path.iterdir() if f.is_dir()])
lesson = st.selectbox("Select lesson", available_lessons)

lesson_path = lessons_path / lesson
audio_folder = lesson_path / "audio"

sentences_module = importlib.import_module(f"lessons.{lesson}.sentences")
correct_sentences = sentences_module.sentences

# -------------------------
# SESSION STATE
# -------------------------

if "index" not in st.session_state:
    st.session_state.index = 0

if "scores" not in st.session_state:
    st.session_state.scores = []

if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# Reset when lesson changes
if "current_lesson" not in st.session_state:
    st.session_state.current_lesson = lesson

if st.session_state.current_lesson != lesson:
    st.session_state.current_lesson = lesson
    st.session_state.index = 0
    st.session_state.scores = []
    st.session_state.input_key += 1

# -------------------------
# MAIN FLOW
# -------------------------

if st.session_state.index < len(correct_sentences):

    sentence_number = st.session_state.index + 1
    current_sentence = correct_sentences[st.session_state.index]
    audio_path = audio_folder / f"sentence_{sentence_number:02d}.mp3"

    st.subheader(f"{lesson.upper()} — Sentence {sentence_number}/{len(correct_sentences)}")

    if audio_path.exists():
        st.audio(str(audio_path))
    else:
        st.warning("Audio missing.")

    # FORM enables Enter to submit
    with st.form(key=f"form_{st.session_state.index}"):

        user_input = st.text_input(
            "Type what you hear:",
            key=f"user_input_{st.session_state.input_key}",
            autocomplete="off"
        )

        submitted = st.form_submit_button("Submit (Press Enter)")

        if submitted:

            accuracy = score_sentence(user_input, current_sentence)
            st.session_state.scores.append(accuracy)

            st.markdown(f"### Accuracy: {accuracy}%")

            # Move to next sentence automatically
            st.session_state.index += 1
            st.session_state.input_key += 1
            st.rerun()

    # Live overall score
    if st.session_state.scores:
        overall = round(sum(st.session_state.scores) / len(st.session_state.scores), 2)
        st.sidebar.markdown(f"📊 Overall Score: {overall}%")

else:
    st.success("Lesson Completed!")

    if st.session_state.scores:
        final_score = round(sum(st.session_state.scores) / len(st.session_state.scores), 2)
        st.markdown(f"## Final Score: {final_score}%")
