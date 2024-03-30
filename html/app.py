from flask import Flask, render_template, request, redirect, url_for, session
import os

from filehandler import sanitize_file, safe_file

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit

@app.route('/')
def upload_form():
    # Clear session data related to uploaded file
    session.pop('uploaded_file', None)

    # Get list of uploaded images
    uploaded_images = os.listdir(app.config['UPLOAD_FOLDER'])    
    return render_template('upload.html', uploaded_images=uploaded_images)

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']

        file = sanitize_file(file, app.config['MAX_CONTENT_LENGTH'])
        if file == False:
            return upload_result(status="File upload wasn't successful")
        
        safe_file(file, app.config['UPLOAD_FOLDER'])
        
        # Store the filename in the session
        session['uploaded_file'] = file.filename
        
        return upload_result('File upload was successful')

@app.route('/upload/result')
def upload_result(status="911 How can I help you?"):
    # Get the filename from the session
    uploaded_file = session.pop('uploaded_file', None)

    return render_template('upload_result.html', file=uploaded_file, status=status)

if __name__ == '__main__':
    app.run(debug=True)
