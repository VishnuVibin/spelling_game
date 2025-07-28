import streamlit as st
import time
from model import game_one, game_two, game_three, game_four, game_five

st.set_page_config(
    page_title="✨ AI Spelling & Suffix Game",
    layout="wide",
    page_icon="🦄"
)

# -- Playful, Animated CSS --
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #FDEB71 0%, #F8D800 100%);
    min-height: 100vh;
    font-family: 'Comic Sans MS', cursive, sans-serif !important;
    
}
.block-container {
    background: transparent;
    background: linear-gradient(135deg, #ffd6e0 0%, #b8c0ff 45%, #ffd6e0 100%);

}

}
h1, h2, h3 {
  font-family: 'Comic Sans MS', cursive, sans-serif !important;
  color: #ff55a3;
  text-shadow: 1px 2px 8px #ffef9f;
}
.stButton>button {
    border-radius: 13px;
    border: 2px solid #FFABF4;
    background: linear-gradient(90deg, #ffd6e8 20%, #e6bcff 100%);
    color: #5a189a;
    font-size: 1.1rem;
    box-shadow: 2px 2px 12px #ffaaee99;
    animation: popin 0.9s;
}
@keyframes popin {
    0% { transform: scale(1.2);}
    100% {transform: scale(1);}
}
.st-radio label {
  font-size: 1.1rem;
  color: #f09;
}
.timer-emoji {
    font-size: 2.2rem;
    animation: shake 0.8s infinite alternate;
    display: inline-block;
}
@keyframes shake {
  0% { transform: rotate(-5deg);}
  100% { transform: rotate(10deg); }
}
.bubble {
  position: fixed;
  border-radius: 50%;
  background: #fff6b9;
  z-index: 0;
  opacity: 0.2;
  animation: floatbubble 18s linear infinite;
}
@keyframes floatbubble {
  0% { bottom: -80px; }
  100% { bottom: 110vh; }
}
.incomplete-word, .hint {
    color: #e379ff;
    font-weight: bold;
    background: #ffd6e8;
    border-radius: 6px;
    padding: 6px 13px;
    margin-bottom: 8px;
    font-size: 1.11em;
}
.footer {
    text-align: center;
    padding: 15px 0 4px 0;
    font-family: 'Comic Sans MS', cursive, sans-serif !important;
    font-size: 1.13rem;
    color: #f5be0b;
}
.confetti {
  font-size: 2.2rem;
  animation: bounce 1s infinite alternate;
  text-align: center;
  margin-bottom: 23px;
  margin-top: 10px;
}
@keyframes bounce {
  0% { transform: scale(1);}
  100% {transform: scale(1.25);}
}
</style>
""", unsafe_allow_html=True)

# Bubbles animation (CSS-generated, up to 10)
for i in range(10):
    x = 4 + 9 * i  # vary left %
    size = 36 + i * 7
    delay = i * 1.6
    st.markdown(f"""
    <div class="bubble" style="left:{x}% ; width:{size}px; height:{size}px; animation-delay: {delay}s"></div>
    """, unsafe_allow_html=True)

st.markdown("""
<h1 style='font-size:2.6rem;text-align:center;'>🦄✨ Welcome to Spell & Suffix Wonderpark! ✨🦄</h1>
<h3 style='text-align:center;'>Play with words, suffixes, & fun! Choose your favorite, race the clock! </h3>
""", unsafe_allow_html=True)

game_options = [
    "Game 1 - Spelling 📝",
    "Game 2 - Suffix ➕",
    "Game 3 - Fill in the Blank ✏️",
    "Game 4 - Error Detection 🔍",
    "Game 5 - Incomplete Word + Hint 💡"
]
TIMER_DURATION = 8  # Make timer longer, more fun for kids!

# Kid-friendly progress bar
progress = st.progress(0, text="Let's Go! 🌟")
correct_count = 0
total_words = 10

# -- Main loop --
for i in range(total_words):
    st.markdown(f"<div class='block-container'>", unsafe_allow_html=True)
    st.markdown(f"<h3 class='kid-block'>🔢 Word <span style='color:#F5BE0B;'>#{i+1}</span> 🎯</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    with col1:
        word = st.text_input(f"✨ Enter a cool word #{i+1}:", key=f"word_{i}", help="Type anything you like!")
    with col2:
        selected_game = st.selectbox(f"🎲 Pick a game for word #{i+1}:",
                                    game_options, key=f"game_{i}")

    # Session state setup (timing, submissions, etc.)
    for key in [f"start_time_{i}", f"time_over_{i}", f"submitted_{i}", f"submitted_choice_{i}"]:
        if key not in st.session_state: st.session_state[key] = None if 'time' in key else False

    generate = st.button(f"✨ Magic! Generate Game {i+1}", key=f"generate_{i}")
    if generate:
        if word.strip():
            if selected_game.startswith("Game 1"):
                options, correct = game_one(word)
            elif selected_game.startswith("Game 2"):
                options, correct = game_two(word)
            elif selected_game.startswith("Game 3"):
                options, correct, incomplete_word_for_display = game_three(word)
                st.session_state[f"incomplete_word_display_{i}"] = incomplete_word_for_display
            elif selected_game.startswith("Game 4"):
                options, correct = game_four(word)
            elif selected_game.startswith("Game 5"):
                options, correct = game_five(word)
            else:
                options, correct = ["error1", "error2", "error3", "error4"], "error1"
            st.session_state[f"options_{i}"] = options
            st.session_state[f"correct_{i}"] = correct
            st.session_state[f"selected_game_{i}"] = selected_game
            st.session_state[f"submitted_{i}"] = False
            st.session_state[f"time_over_{i}"] = False
            st.session_state[f"start_time_{i}"] = time.time()  # Timer starts!
        else:
            st.warning("🎈 Oops! Please type a word above 🦄")

    # -- Timer animated
    options = st.session_state.get(f"options_{i}")
    correct = st.session_state.get(f"correct_{i}")
    selected_game_now = st.session_state.get(f"selected_game_{i}")
    start_time = st.session_state.get(f"start_time_{i}")
    submitted = st.session_state.get(f"submitted_{i}")
    submitted_choice = st.session_state.get(f"submitted_choice_{i}")
    time_over = st.session_state.get(f"time_over_{i}")

    # Timer display
    if start_time:
        elapsed = time.time() - start_time
        remaining = int(TIMER_DURATION - elapsed)
        if remaining <= 0 and not submitted:
            st.session_state[f"time_over_{i}"] = True
            remaining = 0
        timer_emojis = "⏳" * remaining
        st.markdown(
            f'<div class="timer-emoji">{"⏰" if remaining >= 6 else "🕒" if remaining>=3 else "⏱️"} {timer_emojis}</div>',
            unsafe_allow_html=True)

    # -- Show options and allow submit
    if options and selected_game_now:
        choice_key = f"choice_{i}"

        # Animated for Game 3/5 (custom markdown)
        if selected_game_now.startswith("Game 3"):
            incomplete_word = st.session_state.get(f"incomplete_word_display_{i}")
            if incomplete_word:
                st.markdown(f"<div class='incomplete-word'>🧩 Complete the word: <code style='font-size: 1.3em'>{incomplete_word}</code></div>", unsafe_allow_html=True)
            choice = st.radio("Pick the missing letters:", options, key=choice_key, label_visibility="collapsed")
        elif selected_game_now.startswith("Game 5"):
            incomplete, hint, missing_opts = options
            st.markdown(f"<div class='incomplete-word'>🕵️‍♂️ Guess the word: <code style='font-size:1.3em'>{incomplete}</code></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='hint'>💡 Hint: {hint}</div>", unsafe_allow_html=True)
            choice = st.radio("Select missing letters:", missing_opts, key=choice_key, label_visibility="collapsed")
        else:
            choice = st.radio("Choose:", options, key=choice_key, label_visibility="collapsed")
        
        submit = st.button(f"✅ Submit Game {i+1}", key=f"submit_{i}")
        if submit:
            st.session_state[f"submitted_{i}"] = True
            st.session_state[f"submitted_choice_{i}"] = choice
            st.session_state[f"time_over_{i}"] = False

        # Show celebration / result
        show_confetti = False
        if st.session_state.get(f"submitted_{i}"):
            selected = st.session_state.get(f"submitted_choice_{i}")
            if selected == correct:
                correct_count += 1
                show_confetti = True
                st.markdown('<div class="confetti">🎉🌈 Yay! Correct! 🌟🎉</div>', unsafe_allow_html=True)
            else:
                st.error(f"❌ Oops! Correct answer: **{correct}** 🙈")
        elif st.session_state.get(f"time_over_{i}"):
            st.warning("⏰ Time's up! Ready for the next round? 🚀")

        if show_confetti:
            # party popper sound!! (optional, may not run in all browsers)
            st.markdown("""
            <audio autoplay>
                <source src="https://cdn.pixabay.com/audio/2022/07/26/audio_124b0a989e.mp3" type="audio/mpeg">
            </audio>
            """, unsafe_allow_html=True)

    # Progress bar update
    progress.progress((i+1)/total_words, text=f"{i+1} of {total_words} words done!")


    st.markdown("</div>", unsafe_allow_html=True)

# Final Score Celebration
if correct_count > 0:
    st.markdown(f"<div class='confetti'>🎉🎈 You got {correct_count}/{total_words} correct. Awesome! 🎉🎈</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='confetti'>🙌 Game Over! Want to try again?</div>", unsafe_allow_html=True)

st.markdown("""
<div class="footer">
    Built with ❤️ | Try a new word and game each time!<br>
    (Made with Streamlit & LLaMA 🦙)
</div>
""", unsafe_allow_html=True)
