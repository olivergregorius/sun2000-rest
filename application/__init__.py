from flask import Flask


def create_app(test_config: dict = None) -> Flask:
    app = Flask(__name__)
    if test_config:
        app.config.from_mapping(test_config)
    else:
        app.config.from_pyfile('config.py')

    with app.app_context():
        from . import routes
        app.register_blueprint(routes.bp)

        return app
