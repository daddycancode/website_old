import os
from flask import Flask, Blueprint, render_template, send_from_directory, redirect, url_for, flash, request

files = Blueprint('files', __name__, static_folder='static', template_folder='templates')
#app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
target = os.path.join(APP_ROOT, 'files/')
password = 'pass'

@files.route('/')
def home():
    file_names = os.listdir(target)
    return render_template('files.html', files=file_names)
        
@files.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if request.form['password'] == password:
            for upload in request.files.getlist('file'):
                filename = upload.filename
                destination = '/'.join([target, filename])
                upload.save(destination)
            flash('File/s successfully uploaded!')
            return redirect(url_for('files.home'))
        else:
            flash('Incorrect password.')
            return render_template('upload.html')
    else:
        return render_template('upload.html')

@files.route('/<filename>')
def view(filename):
    return send_from_directory('files/files', filename)

if __name__ == '__main__':
    print('WRONG FILE HAS BEEN RUN!')
