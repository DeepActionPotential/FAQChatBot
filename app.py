from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename

from core.FAQ_answer_manager import FAQAnswerManager
from services.IO_manager import IOManager
from services.faiss_manager import FaissVectorDatabase
from services.llm_api_manager import GeminiLLMAPIManager
from utils.utils import chunk_text, filter_json

from config import GeneralCfg, LLMPrompts
from logging import Logger
import os
from dotenv import load_dotenv

# Initialize Flask app first
app = Flask(__name__)

# Then initialize other components
logger = Logger(__name__)
io_manager = IOManager()

faiss_vector_database = FaissVectorDatabase(
    model_name=GeneralCfg.text_embedding_model_name,
    logger=logger
)

load_dotenv(dotenv_path="keys.env")
gemini_api_key = os.getenv("GEMINI_API_KEY")

gemini_llm_api_manager = GeminiLLMAPIManager(
    api_key=gemini_api_key,
    model_name=GeneralCfg.llm_api_model_name
)

faq_answer_manager = FAQAnswerManager(
    Faiss_vecotr_database=faiss_vector_database,
    llm_api_manager=gemini_llm_api_manager,
    io_manager=io_manager,
    logger=logger
)







@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():

    try:
        question = request.json.get('message')
        if not question:
            return jsonify({'response': 'No question provided'}), 400
            
        # Get answers using the FAQ manager
        answers = faq_answer_manager.get_answers(
            question=question,
            FAQ_answer_prompt=LLMPrompts.FAQ_answer_prompt,
            top_k=GeneralCfg.top_k,
            n_answers=GeneralCfg.n_answers
        )

        
        # Format the response
        if not answers:
            response = "I couldn't find any answers to your question."
        else:
            response = answers
            
        return jsonify({'response': response})
    
    except Exception as e:
        print(f"Error processing question: {str(e)}")
        return jsonify({'response': f'Sorry, there was an error processing your question. Error:\n\n{str(e)}'}), 500

@app.route('/load_faiss', methods=['POST'])
def load_faiss():
    file = request.files.get('file')
    if not file:
        return jsonify({'message': 'No file uploaded'}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join('uploads', filename)
    os.makedirs('uploads', exist_ok=True)
    file.save(filepath)
    try:
        # Use default values for n_characters and overlap
        faq_answer_manager.load_text_into_faiss(filepath, n_char=GeneralCfg.n_char, overlap=GeneralCfg.overlap)
        return jsonify({'message': 'File loaded successfully'})
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

@app.route('/save_faiss_index', methods=['POST'])
def save_faiss_index():
    try:
        data = request.get_json()
        path = data.get('path')
        faq_answer_manager.save_faiss_index(path)
        return jsonify({'message': f'Database saved to {path}.'})
    except Exception as e:
        return jsonify({'message': f'Error saving database: {str(e)}'}), 500

@app.route('/load_faiss_index', methods=['POST'])
def load_faiss_index():
    try:
        data = request.get_json()
        path = data.get('path')
        faq_answer_manager.load_faiss_index(path)
        return jsonify({'message': f'Database loaded from {path}.'})
    except Exception as e:
        return jsonify({'message': f'Error loading database: {str(e)}'}), 500

@app.route('/clear_faiss_index', methods=['POST'])
def clear_faiss_index():
    try:
        faq_answer_manager.clear_faiss_index()
        return jsonify({'message': 'Database cleared.'})
    except Exception as e:
        return jsonify({'message': f'Error clearing database: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)