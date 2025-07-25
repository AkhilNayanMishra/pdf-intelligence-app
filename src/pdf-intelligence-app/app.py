import os
import datetime
import json
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from src.main import run_analysis_pipeline

# Initialize the Flask app
# It looks for the HTML file in a 'frontend' folder.
app = Flask(__name__, template_folder='frontend', static_folder='frontend')

# Configuration for file uploads
# A folder named 'input' will be created to temporarily store uploaded files.
UPLOAD_FOLDER = 'input'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    API endpoint to handle file uploads and trigger the analysis pipeline.
    """
    # --- 1. Get data from the request ---
    if 'files' not in request.files:
        return jsonify({"error": "No files part in the request"}), 400

    files = request.files.getlist('files')
    persona = request.form.get('persona', '')
    job_to_be_done = request.form.get('job', '')

    if not files or files[0].filename == '':
        return jsonify({"error": "No selected files"}), 400
    
    if not persona or not job_to_be_done:
        return jsonify({"error": "Persona and Job-to-be-Done are required fields"}), 400

    # --- 2. Save uploaded files temporarily ---
    doc_paths = []
    for file in files:
        if file and file.filename.lower().endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            doc_paths.append(filepath)

    if not doc_paths:
        return jsonify({"error": "No valid PDF files were uploaded"}), 400

    # --- 3. Run the analysis pipeline ---
    try:
        result = run_analysis_pipeline(doc_paths, persona, job_to_be_done)
        return jsonify(result)
    except Exception as e:
        # Provide a more specific error message if possible
        print(f"Error during analysis: {e}")
        return jsonify({"error": f"An error occurred during analysis: {str(e)}"}), 500
    finally:
        # --- 4. Clean up the uploaded files ---
        for path in doc_paths:
            if os.path.exists(path):
                os.remove(path)

if __name__ == '__main__':
    # Runs the Flask app. Host='0.0.0.0' makes it accessible from outside the Docker container.
    app.run(host='0.0.0.0', debug=True, port=5001)
