from flask import Flask, render_template, request, send_from_directory
import os
import subprocess
from werkzeug.utils import secure_filename


app = Flask(__name__, template_folder='static/templates')

current_path = os.path.abspath(__file__)
directory_path = os.path.dirname(current_path)
output_folder = directory_path + "/output"

app.config['STATIC_FOLDER'] = directory_path + '/static'
app.config['STATIC_URL_PATH'] = '/static'
app.config['UPLOAD_FOLDER'] = os.path.abspath(directory_path + '/inputs')

def index():
    return render_template('index.html')

app.add_url_rule('/', 'index', index)

@app.route('/process_file', methods=['POST'])
def process_file():
    # Check if a file is attached to the POST request
    if 'file' not in request.files:
        return "No file uploaded.", 400

    # Save the uploaded file to the server's filesystem
    file = request.files['file']
    if file.filename == '':
        return "No selected file.", 400
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))

    #Run python script with the path to the uploaded file
    subprocess.run(["poetry", "install"])
    subprocess.run(["poetry", "run", "python", os.path.join(directory_path, "MusicAssist.py"), file.filename])

    # Check if the output folder exists
    if os.path.exists(output_folder):
        zip_filename = f"{os.path.splitext(file.filename)[0]}.zip"
        zip_filepath = os.path.join(directory_path, zip_filename)
        
        if os.path.exists(zip_filepath):
            # Prepare the zip file for download
            return send_from_directory(directory_path, zip_filename, as_attachment=True)
        else:
            return f"Zip file not found: {zip_filepath}", 404
    else:
        return f"Output folder not found: {directory_path}", 404


if __name__ == '__main__':
    app.run(debug=True)
