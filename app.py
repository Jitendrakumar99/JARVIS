"""
Smart College Student Assistance Portal
Main Application Entry Point
"""
import os
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from config import config
from models import db, Admin

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'admin.login'
login_manager.login_message = 'Please login to access this page.'
login_manager.login_message_category = 'warning'


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Ensure required directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))
    
    # Register blueprints
    from routes.admin import admin_bp
    from routes.student import student_bp
    from routes.ai_chat import chat_bp
    from routes.jobs import jobs_bp
    from routes.assistant import assistant_bp
    
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(student_bp)
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(jobs_bp, url_prefix='/jobs')
    app.register_blueprint(assistant_bp, url_prefix='/assistant')
    
    # Home route
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Create database tables and default admin
    with app.app_context():
        db.create_all()
        
        # Create default admin if not exists
        if not Admin.query.filter_by(username=app.config['ADMIN_USERNAME']).first():
            admin = Admin(username=app.config['ADMIN_USERNAME'])
            admin.set_password(app.config['ADMIN_PASSWORD'])
            db.session.add(admin)
            db.session.commit()
            print(f"Default admin created: {app.config['ADMIN_USERNAME']}")
    
    return app


# Create Flask app instance
flask_env = os.getenv('FLASK_ENV', 'development')
app = create_app(flask_env)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  Smart College Student Assistance Portal")
    print("  Running at: http://localhost:5000")
    print("  Admin Login: http://localhost:5000/admin/login")
    print("="*60 + "\n")
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
