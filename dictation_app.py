import streamlit as st
import re
import importlib
from pathlib import Path
import json
from datetime import date

# -------------------------
# PERSISTENCE FILE
# -------------------------

DATA_FILE = "user_progress.json"

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
    errors = 0

    for i, word in enumerate(correct_words):
        if i < len(user_words) and user_words[i] == word:
            correct_count += 1
        else:
            errors += 1

    if len(user_words) > len(correct_words):
        errors += len(user_words) - len(correct_words)

    accuracy = round((correct_count / total) * 100, 2)
    return accuracy, errors

# -------------------------
# STREAMLIT UI
# -------------------------

st.title("Dutch Dictation Trainer V2")

lessons_path = Path("lessons")
available_lessons = sorted([folder.name for folder in lessons_path.iterdir() if folder.is_dir()])

lesson = st.selectbox("Select lesson", available_lessons)

lesson_path = lessons_path / lesson
audio_folder = lesson_path / "audio"

sentences_module = importlib.import_module(f"lessons.{lesson}.sentences")
correct_sentences = sentences_module.sentences

# Initialize lesson data
if lesson not in data:
    data[lesson] = {
        "scores": [],
        "weak_sentences": [],
        "completed": False
    }

if "index" not in st.session_state:
    st.session_state.index = 0

# Reset if lesson changes
if "current_lesson" not in st.session_state:
    st.session_state.current_lesson = lesson

if st.session_state.current_lesson != lesson:
    st.session_state.current_lesson = lesson
    st.session_state.index = 0

# -------------------------
# DAILY STREAK
# -------------------------

today = str(date.today())

if "last_practice" not in data:
    data["last_practice"] = today
    data["streak"] = 1
else:
    if data["last_practice"] != today:
        data["streak"] += 1
        data["last_practice"] = today

st.sidebar.markdown(f"🔥 Streak: {data.get('streak',1)} days")

# -------------------------
# MAIN LOGIC
# -------------------------

if st.session_state.index < len(correct_sentences):

    sentence_number = st.session_state.index + 1
    current_sentence = correct_sentences[st.session_state.index]
    audio_path = audio_folder / f"sentence_{sentence_number:02d}.mp3"

    st.subheader(f"{lesson.upper()} — Sentence {sentence_number}/{len(correct_sentences)}")

    if audio_path.exists():
        st.audio(str(audio_path))
    else:
        st.warning("Audio file missing.")

    user_input = st.text_input("Type what you hear:")

    if st.button("Check Answer"):
        accuracy, errors = score_sentence(user_input, current_sentence)

        st.markdown(f"## Accuracy: {accuracy}%")

        data[lesson]["scores"].append(accuracy)

        if accuracy < 100:
            data[lesson]["weak_sentences"].append(st.session_state.index)

        save_data(data)

    if st.button("Next Sentence"):
        st.session_state.index += 1
        st.rerun()

else:
    st.success("Lesson Completed!")

    avg_score = round(sum(data[lesson]["scores"]) / len(data[lesson]["scores"]), 2)
    st.markdown(f"### Final Lesson Average: {avg_score}%")

    if data[lesson]["weak_sentences"]:
        st.warning("You have weak sentences to review.")

        if st.button("Review Weak Sentences"):
            st.session_state.index = data[lesson]["weak_sentences"][0]
            st.rerun()

    data[lesson]["completed"] = True
    save_data(data)

# -------------------------
# SIDEBAR PROGRESS
# -------------------------

if data[lesson]["scores"]:
    avg = round(sum(data[lesson]["scores"]) / len(data[lesson]["scores"]), 2)
    st.sidebar.markdown(f"📊 Lesson Average: {avg}%")
    st.sidebar.markdown(f"Completed: {data[lesson]['completed']}")
