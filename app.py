from flask import Flask
from Encrypt import url
from Backend import orthogonal



app = Flask(__name__)

app.register_blueprint(url.encrypt_bp)
app.register_blueprint(orthogonal.orthogonal_bp)

def create_app():
    from . import db
    db.init_app(app)

    return app

app.config['UPLOAD_FOLDER'] = 'static/files'

if __name__ == '__main__':
    app.run(debug=True)