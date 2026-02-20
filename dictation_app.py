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
# WORD-BY-WORD SCORING
# -------------------------

def score_sentence(user_input, correct):
    user_words = normalize(user_input).split()
    correct_words = normalize(correct).split()

    feedback = []
    correct_count = 0
    max_len = max(len(user_words), len(correct_words))

    for i in range(max_len):
        if i < len(correct_words) and i < len(user_words):
            if user_words[i] == correct_words[i]:
                correct_count += 1
                feedback.append(f"✅ {correct_words[i]}")
            else:
                feedback.append(
                    f"❌ {correct_words[i]} (you wrote: {user_words[i]})"
                )
        elif i < len(correct_words):
            feedback.append(f"❌ {correct_words[i]} (missing)")
        else:
            feedback.append(f"❌ extra word: {user_words[i]}")

    accuracy = round((correct_count / len(correct_words)) * 100, 2)
    return accuracy, feedback

# -------------------------
# APP
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

if "audio_played" not in st.session_state:
    st.session_state.audio_played = False

if "audio_finished" not in st.session_state:
    st.session_state.audio_finished = False

if "show_feedback" not in st.session_state:
    st.session_state.show_feedback = False

# -------------------------
# MAIN FLOW
# -------------------------

if st.session_state.index < len(correct_sentences):

    sentence_number = st.session_state.index + 1
    current_sentence = correct_sentences[st.session_state.index]
    audio_path = audio_folder / f"sentence_{sentence_number:02d}.mp3"

    st.subheader(f"{lesson.upper()} — Sentence {sentence_number}/{len(correct_sentences)}")

    # ---- AUDIO CONTROL ----

    if not st.session_state.audio_played:

        if st.button("▶ Start Listening"):
            st.session_state.audio_played = True
            st.session_state.audio_finished = False
            st.rerun()

    elif st.session_state.audio_played and not st.session_state.audio_finished:

        if audio_path.exists():
            st.audio(str(audio_path), start_time=0)
        else:
            st.warning("Audio missing.")

        st.info("Listen carefully. You can only hear this once.")

        if st.button("✔ I Finished Listening"):
            st.session_state.audio_finished = True
            st.rerun()

    # ---- TYPING ENABLED ONLY AFTER AUDIO ----

    if st.session_state.audio_finished:

        with st.form(key=f"form_{st.session_state.index}"):

            user_input = st.text_input(
                "Type what you heard:",
                key=f"user_input_{st.session_state.input_key}",
                autocomplete="off"
            )

            submitted = st.form_submit_button("Submit (Press Enter)")

            if submitted:
                accuracy, feedback = score_sentence(user_input, current_sentence)

                st.session_state.scores.append(accuracy)
                st.session_state.current_feedback = feedback
                st.session_state.current_accuracy = accuracy
                st.session_state.show_feedback = True

    # ---- FEEDBACK ----

    if st.session_state.show_feedback:

        st.markdown(f"### Accuracy: {st.session_state.current_accuracy}%")

        st.markdown("### Feedback:")
        for item in st.session_state.current_feedback:
            st.write(item)

        st.markdown("### Correct Sentence:")
        st.info(current_sentence)

        if st.button("Next Sentence"):

            st.session_state.index += 1
            st.session_state.input_key += 1
            st.session_state.audio_played = False
            st.session_state.audio_finished = False
            st.session_state.show_feedback = False
            st.rerun()

    # ---- OVERALL SCORE ----

    if st.session_state.scores:
        overall = round(sum(st.session_state.scores) / len(st.session_state.scores), 2)
        st.sidebar.markdown(f"📊 Overall Score: {overall}%")

else:
    st.success("Lesson Completed!")

    if st.session_state.scores:
        final_score = round(sum(st.session_state.scores) / len(st.session_state.scores), 2)
        st.markdown(f"## Final Score: {final_score}%")
