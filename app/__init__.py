from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
scheduler = BackgroundScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    CORS(app)
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()
        
    from .routes import main
    app.register_blueprint(main)
    
    if not scheduler.running:
        scheduler.start()
    
    return app




