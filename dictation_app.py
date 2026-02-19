import streamlit as st
import re
import importlib
from pathlib import Path

# -------------------------
# NORMALIZATION
# -------------------------

def normalize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()

# -------------------------
# STRICT SCORING FUNCTION
# -------------------------

def score_sentence(user_input, correct):
    user_words = normalize(user_input).split()
    correct_words = normalize(correct).split()

    total = len(correct_words)
    correct_count = 0
    feedback = []

    for i, word in enumerate(correct_words):
        if i < len(user_words):
            if user_words[i] == word:
                correct_count += 1
                feedback.append(f"✅ {word}")
            else:
                feedback.append(f"❌ {word} (you wrote: {user_words[i]})")
        else:
            feedback.append(f"❌ {word} (missing)")

    if len(user_words) > len(correct_words):
        extra_words = user_words[len(correct_words):]
        for w in extra_words:
            feedback.append(f"❌ extra word: {w}")

    accuracy = round((correct_count / total) * 100, 2)
    return accuracy, feedback

# -------------------------
# STREAMLIT UI
# -------------------------

st.title("Dutch Dictation Trainer")

# Detect available lessons automatically
lessons_path = Path("lessons")
available_lessons = [folder.name for folder in lessons_path.iterdir() if folder.is_dir()]

lesson = st.selectbox("Select lesson", sorted(available_lessons))

lesson_path = lessons_path / lesson
audio_folder = lesson_path / "audio"

# Dynamically import sentence list
sentences_module = importlib.import_module(f"lessons.{lesson}.sentences")
correct_sentences = sentences_module.sentences

# Reset index if lesson changes
if "current_lesson" not in st.session_state:
    st.session_state.current_lesson = lesson
    st.session_state.index = 0

if st.session_state.current_lesson != lesson:
    st.session_state.current_lesson = lesson
    st.session_state.index = 0

# -------------------------
# MAIN LOGIC
# -------------------------

if st.session_state.index < len(correct_sentences):

    current_sentence = correct_sentences[st.session_state.index]
    audio_path = audio_folder / f"sentence_{st.session_state.index+1:02d}.mp3"

    st.subheader(f"Sentence {st.session_state.index + 1}")

    if audio_path.exists():
        st.audio(str(audio_path))
    else:
        st.warning("Audio file not found.")

    user_input = st.text_input("Type what you hear:")

    if st.button("Check Answer"):
        accuracy, feedback = score_sentence(user_input, current_sentence)

        st.markdown(f"## Accuracy: {accuracy}%")
        st.markdown("### Feedback:")

        for item in feedback:
            st.write(item)

    if st.button("Next Sentence"):
        st.session_state.index += 1
        st.rerun()

else:
    st.success("You completed this lesson!")
