from flask import Blueprint, request, render_template, send_file, send_from_directory
import Backend.orthogonal as ortho
from werkzeug.utils import secure_filename
import app, os, glob, tempfile, shutil
import random, io
import string, sqlite3
# Defining a blueprint
encrypt_bp = Blueprint(
    'encrypt_bp', __name__,
    template_folder='templates',
    static_folder='static',
)

@encrypt_bp.route('/index')
@encrypt_bp.route('/')
def index():
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(10))
    return render_template('index.html', key = result_str)

def ConnectDB():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@encrypt_bp.route('/encryptForm')
def encryptForm():
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(10))
    return render_template('encrypt.html', key = result_str)

# @encrypt_bp.route('/encrypt/read_file')
def OpenFile(file_upload):
    file = open(file_upload, "r")
    content = file.read()
    return content

def WriteFile(file_name, content):
    file = open(file_name, "w+")
    file.write(content)
    file.close()
    return 

def DuplicateIt(file_name):
    cache = io.BytesIO()
    cache = tempfile.NamedTemporaryFile()
    with open(file_name, "rb") as fp:
        shutil.copyfileobj(fp, cache)
        cache.flush()
    cache.seek(0)
    return cache

@encrypt_bp.route('/Delete_file', methods = ['DELETE'])
def DeleteAllFiles():
    files = glob.glob('static/files/*')

    for f in files :
        os.remove(f)
    return 'done'

@encrypt_bp.route('/encrypt', methods = ['POST'])
def Encrypt():
    if request.method =='POST':

        file_upload = request.files['file']

        key_pass = request.form['key']
        
        file = os.path.join('static/files', secure_filename(file_upload.filename))
        
        file_upload.save(file)
        content = OpenFile(file)

        # return render_template('encrypt.html')
        encrypted_text = ortho.orthogonal_encrypt(content, 7)
        WriteFile(file, encrypted_text)

        conn = ConnectDB()
        conn.execute('INSERT INTO encrypts (name_file, gen_key, used) VALUES (?, ?, ?)', (file_upload.filename, key_pass, 0))
        conn.commit()
        conn.close()

        return send_from_directory('static/files', file_upload.filename, as_attachment = True)

@encrypt_bp.route('/decrypt', methods = ['POST'])
def decrypt():
    if request.method == 'POST':
        file_upload = request.files['file']

        key_pass = request.form['key']
        
        file = os.path.join('static/files', secure_filename(file_upload.filename))
        
        content = OpenFile(file)
        decrypted_text = ortho.orthogonal_decrypt(content, 7)
        
        conn = ConnectDB()
        check = conn.execute('SELECT * FROM encrypts WHERE gen_key = ? AND name_file = ?', (key_pass, file_upload.filename)).fetchall()
        
        if check == [] or check == '':
            raise Exception('Kombinasi file dengan password tersebut tidak ada')

        conn.execute('UPDATE encrypts SET used = ? WHERE name_file = ? AND gen_key = ?', (True, file_upload.filename, key_pass))
        conn.execute('DELETE FROM encrypts WHERE name_file = ? AND gen_key = ? AND used = ?', (file_upload.filename, key_pass, True))
        conn.commit()
        conn.close()
        
        WriteFile(file, decrypted_text)
        newFile = DuplicateIt(file)
        os.remove(file)

        downloadable_file = send_file(newFile, download_name = file_upload.filename, as_attachment = True)
        return downloadable_file

