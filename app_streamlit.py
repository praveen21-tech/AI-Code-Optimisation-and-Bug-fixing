import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from gtts import gTTS

# Load API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("API Key not found! Set the GROQ_API_KEY environment variable.")
    st.stop()

# Model Selection
model_options = {
    "DeepSeek-R1-Distill-Qwen-32B": "deepseek-r1-distill-qwen-32b",
    "Gemma2-9B-IT": "gemma2-9b-it",
    "LLaMA 3.3-70B": "llama-3.3-70b-versatile",
}

selected_model = st.selectbox("🤖 Choose AI Model:", list(model_options.keys()))

# Temperature Selection
temperature = st.slider("🔥 Set Temperature:", min_value=0.0, max_value=1.0, value=0.3, step=0.05)

# Initialize LangChain AI model
chat_model = ChatOpenAI(
    openai_api_key=api_key,
    openai_api_base="https://api.groq.com/openai/v1",
    model_name=model_options[selected_model],
    temperature=temperature,
    max_tokens=2048,
)

# Streamlit UI
st.title("🚀 AI-Powered Code Optimizer")
st.write("Optimize your code and analyze its performance.")

# Input fields
language = st.selectbox("📝 Select Programming Language:", ["Python", "JavaScript", "Java", "C++", "HTML"])
output_language = st.selectbox("🌍 Select Explanation Language:", ["English", "Tamil", "Hindi"])
user_code = st.text_area("🖊️ Paste your code here:", height=200, key="code_input")

# Function to generate audio
def generate_audio():
    if "last_explanation" not in st.session_state:
        st.error("No explanation available to generate audio.")
        return
    
    explanation_text = st.session_state["last_explanation"]
    tts_lang_code = {"Tamil": "ta", "Hindi": "hi", "English": "en"}.get(output_language, "en")

    try:
        audio_path = "audio_explanation.mp3"
        tts = gTTS(text=explanation_text, lang=tts_lang_code)
        tts.save(audio_path)
        st.session_state["audio_path"] = audio_path
        st.success("✅ Audio Generated Successfully!")
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")

# Check if optimize button is clicked
if st.button("⚡ Optimize Code"):
    if not user_code.strip():
        st.error("Please enter some code before optimizing.")
    else:
        language_prompt_map = {
            "Python": "Fix any bugs and optimize the following Python code...",
            "JavaScript": "Fix any bugs and optimize the following JavaScript code...",
            "Java": "Fix any bugs and optimize the following Java code...",
            "C++": "Fix any bugs and optimize the following C++ code...",
            "HTML": "Fix any structural and semantic issues in the following HTML code...",
        }

        # Constructing the prompt
        prompt = (
            f"{language_prompt_map[language]}\n\n"
            f"### Original Code:\n```{language.lower()}\n{user_code}\n```\n\n"
            f"### Analyze the original code:\n"
            f"- Identify and fix any bugs.\n"
            f"- Optimize it for efficiency and readability.\n"
            f"- Provide time and space complexity analysis before optimization.\n\n"
            f"### Optimized Code & Explanation:\n"
            f"- Provide the optimized code.\n"
            f"- Explain the improvements in a structured format.\n"
        )

        if output_language == "Tamil":
            prompt += "\nProvide a clear, detailed explanation in Tamil, ensuring a natural and structured response without repetition."
        elif output_language == "Hindi":
            prompt += "\nProvide a clear, detailed explanation in Hindi."
        else:
            prompt += "\nProvide a clear, detailed explanation in English."

        # Fetch AI response
        try:
            response = chat_model.invoke([HumanMessage(content=prompt)])
            response_text = response.content.strip()

            # Post-processing to remove repetitive sentences
            response_lines = response_text.split("\n")
            filtered_response = []
            seen_sentences = set()
            for line in response_lines:
                if line.strip() not in seen_sentences:
                    filtered_response.append(line)
                    seen_sentences.add(line.strip())
            response_text = "\n".join(filtered_response)

            # Store output in session state
            st.session_state["last_explanation"] = response_text  

        except Exception as e:
            st.error(f"Error: {str(e)}")

# Display the stored optimized response if available
if "last_explanation" in st.session_state:
    st.subheader("📜 Optimized Code & Analysis")
    st.markdown(st.session_state["last_explanation"], unsafe_allow_html=True)

    # Generate Audio from Explanation
    if st.button("🎙️ Generate Audio Explanation"):
        generate_audio()  

# Play Button for Audio
if "audio_path" in st.session_state:
    st.audio(st.session_state["audio_path"])
