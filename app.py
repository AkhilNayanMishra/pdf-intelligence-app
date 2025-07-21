from flask import Flask, send_from_directory, render_template
# Initialize the Flask application
app = Flask(__name__, static_folder='frontend')

@app.route('/')
def serve_index():
    """
    Serves the main index.html file for the web application.
    """
    return send_from_directory('frontend', 'index.html')

@app.route('/frontend/<path:filename>')
def serve_static(filename):
    """
    Serves static files (CSS, JS) from the 'frontend' directory.
    """
    return send_from_directory('frontend', filename)

@app.route('/output/<path:filename>')
def get_json(filename):
    """
    Provides an API endpoint to get a JSON analysis file from the 'output' directory.
    """
    return send_from_directory('output', filename)

@app.route('/input/<path:filename>')
def get_pdf(filename):
    """
    Provides an API endpoint to get a PDF document from the 'input' directory.
    """
    return send_from_directory('input', filename)

if __name__ == '__main__':
    # Run the Flask app on the local development server
    # The host '0.0.0.0' makes it accessible on your local network
    app.run(host='0.0.0.0', port=5001, debug=True)
