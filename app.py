from flask import Flask, render_template, request, jsonify
import os
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from gtts import gTTS

app = Flask(__name__, static_url_path='/static')

# Load API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("API Key not found! Set the GROQ_API_KEY environment variable.")

# Available models
model_name = "llama-3.3-70b-versatile"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize_code():
    data = request.json
    language = data.get('language', '').lower()
    output_language = data.get('output_language', '').lower()
    user_code = data.get('code', '')
    temperature = float(data.get('temperature', 0.3))

    if not user_code:
        return jsonify({'error': 'No code provided'}), 400

    language_prompt_map = {
        "python": "Fix and optimize the following Python code, focusing on efficiency and readability.",
        "javascript": "Fix and optimize the following JavaScript code, focusing on performance.",
        "java": "Fix and optimize the following Java code, improving efficiency.",
        "c++": "Fix and optimize the following C++ code, making it more efficient.",
        "html": "Improve the following HTML structure and accessibility.",
    }

    if language not in language_prompt_map:
        return jsonify({'error': f"Sorry, the language '{language}' is not supported at this time."}), 400

    prompt = (
        f"{language_prompt_map[language]}\n\n"
        f"### Original Code:\n{user_code}\n\n"
        f"### Analysis:\n"
        f"1. Identify and fix bugs.\n"
        f"2. Optimize performance and readability.\n"
        f"3. Provide time and space complexity analysis.\n\n"
        f"### Optimized Code:\n"
        f"1. Provide the optimized version.\n"
        f"2. Explain improvements and complexity changes.\n\n"
    )

    if output_language == 'tamil':
        prompt += "Finally, provide a detailed explanation in Tamil."
    elif output_language == 'hindi':
        prompt += "Finally, provide a detailed explanation in Hindi."
    else:
        prompt += "Finally, provide a detailed explanation in English."

    chat_model = ChatOpenAI(
        openai_api_key=api_key,
        openai_api_base="https://api.groq.com/openai/v1",
        model_name=model_name,
        temperature=temperature,
        max_tokens=2048,
    )

    try:
        response = chat_model.invoke([HumanMessage(content=prompt)])
        response_text = response.content.strip()
        token_usage = response.token_usage.total_tokens

        return jsonify({'response': response_text.split("\n\n"), 'tokens_used': token_usage})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    data = request.json
    explanation_text = data.get('text', '')
    output_language = data.get('language', 'english').lower()

    if not explanation_text:
        return jsonify({'error': 'No explanation provided'}), 400

    tts_lang_code = {'tamil': 'ta', 'hindi': 'hi', 'english': 'en'}.get(output_language, 'en')
    audio_filename = f"static/audio_explanation.mp3"

    try:
        tts = gTTS(text=explanation_text, lang=tts_lang_code)
        tts.save(audio_filename)
        return jsonify({'audio_url': f"/static/audio_explanation.mp3"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
