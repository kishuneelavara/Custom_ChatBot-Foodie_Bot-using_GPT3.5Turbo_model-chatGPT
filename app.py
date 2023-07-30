import os
from flask import Flask, flash, request, redirect, url_for, render_template, jsonify
from werkzeug.utils import secure_filename
from utils.openai_utils import FoodAssistant

UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['csv'])

assistant = None  # Initialize as None initially

@app.route('/')
def start_page():
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        statement = 'No file part'
        return render_template('index.html', status="failed", statement=statement)
    file = request.files['file']
    if file.filename == '':
        statement = 'No image selected for uploading'
        return render_template('index.html', status="failed", statement=statement)
    if file and allowed_file(file.filename):
        for filename in os.listdir('static/uploads/'):
            os.remove('static/uploads/' + filename)
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        global assistant
        assistant = FoodAssistant('static/uploads/')  # Initialize FoodAssistant after successful upload
        return render_template('index.html', status="success", filename=filename, statement="Successfully uploaded data")
    else:
        statement = 'Allowed image types are -> csv'
        return render_template('index.html', status="failed", statement=statement)

# Route for chat interaction
@app.route("/chat", methods=["POST"])
def chat():
    try:
        global assistant
        user_input = request.json["user_input"]
        if assistant is None:
            assistant = FoodAssistant('static/uploads/')
            response = assistant.process_user_input(user_input)
            return jsonify({"reply": response})  # If assistant is not initialized, return "No data available"
        response = assistant.process_user_input(user_input)
        return jsonify({"reply": response})
    except Exception as e:
        print(e)
        return jsonify({"reply": "No data available"})

@app.after_request
def add_header(response):
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(port=5001)
