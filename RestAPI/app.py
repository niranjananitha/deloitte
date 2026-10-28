# pyrefly: ignore [missing-import]
from flask import Flask
from config import Config
from extensions import db,jwt
from routes import users_bp
from routes.auth import auth_bp
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)


    app.register_blueprint(users_bp)
    app.register_blueprint(auth_bp)
    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
