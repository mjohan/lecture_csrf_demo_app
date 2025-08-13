from flask import Flask
from .blueprints.csrf import bp as csrf_bp

def create_app():
    app = Flask(__name__)
    app.config.update(
        DEBUG=True,
        TEMPLATES_AUTO_RELOAD=True,
        SECRET_KEY="dev-only",  # fine for local demos
    )

    # blueprints
    app.register_blueprint(csrf_bp)

    return app
