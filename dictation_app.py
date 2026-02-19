import streamlit as st
import re
from difflib import SequenceMatcher
from pathlib import Path

AUDIO_FOLDER = "audio_sentences"

correct_sentences = [
"Welke dag is het vandaag?",
"Het is vandaag dinsdag.",
"Gisteren was het maandag.",
"En morgen is het woensdag.",
"Na woensdag volgen donderdag en vrijdag.",
"De laatste twee dagen van de week zijn zaterdag en zondag.",
"Dan is het weekend.",
"Wanneer werken de meeste mensen?",
"Van maandag tot en met vrijdag.",
"De meeste mensen zijn in het weekend vrij.",
"We werken dan meestal niet.",
"We gaan dan naar familie. Of we gaan naar buiten met de kinderen, of met vrienden.",
"We hebben ook tijd om boodschappen te doen.",
"Of andere leuke dingen",
"bijvoorbeeld Nederlands leren.",
"Op welke dagen zijn de winkels open?",
"De meeste winkels zijn op maandag tot en met zaterdag open",
"en veel winkels ook op zondag.",
"Op maandagmorgen zijn veel winkels dicht.",
"Mensen die in een winkel werken zijn dus meestal niet in het weekend vrij.",
"Ze hebben op een andere dag vrij, bijvoorbeeld op maandag.",
"Zijn scholen in het weekend dicht?",
"Ja, alle scholen zijn dicht in het weekend.",
"In het weekend hebben kinderen geen les.",
"Kinderen tot twaalf jaar hebben meestal ook vrij op woensdagmiddag.",
"En ze hebben zes weken vrij in de zomer!",
"Hoe is dat in jullie land?"
]

def normalize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()

def score_sentence(user_input, correct):
    user_words = normalize(user_input).split()
    correct_words = normalize(correct).split()

    total = len(correct_words)
    correct_count = 0
    feedback = []

    for i, word in enumerate(correct_words):
        if i < len(user_words):
            similarity = SequenceMatcher(None, user_words[i], word).ratio()
            if similarity > 0.85:
                correct_count += 1
                feedback.append(f"✅ {word}")
            else:
                feedback.append(f"❌ {word} (you wrote: {user_words[i]})")
        else:
            feedback.append(f"❌ {word} (missing)")
    
    accuracy = round((correct_count / total) * 100, 2)
    return accuracy, feedback

st.title("Dutch Dictation Trainer")

if "index" not in st.session_state:
    st.session_state.index = 0

if st.session_state.index < len(correct_sentences):

    current_sentence = correct_sentences[st.session_state.index]
    audio_path = Path(AUDIO_FOLDER) / f"sentence_{st.session_state.index+1:02d}.mp3"

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
    st.success("You completed all sentences!")
