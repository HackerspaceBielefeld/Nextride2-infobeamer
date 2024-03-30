from flask import Flask, render_template, request, redirect, url_for
import os

from filehandler import sanitize_file, safe_file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit

@app.route('/')
def upload_form():
    # Get list of uploaded images
    uploaded_images = os.listdir(app.config['UPLOAD_FOLDER'])    
    return render_template('upload.html', uploaded_images=uploaded_images)

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        file = sanitize_file(file, app.config['MAX_CONTENT_LENGTH'])
        if file == False: return redirect(url_for('upload_form'))
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        #safe_file(file, app.config['UPLOAD_FOLDER'])
    return redirect(url_for('upload_form'))

if __name__ == '__main__':
    app.run(debug=True)
