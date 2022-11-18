import os
import sys

import flask
import molecalc.data.db_session as db_session
# from molecalc.infrastructure.config import DevConfig, ProdConfig
# from molecalc.data.extensions import db

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, folder)
# import molecalc.data.db_session as db_session

app = flask.Flask(__name__)


def main():
    configure()
    app.run(debug=True, port=5006)


def configure():
    print("Configuring Flask app:")

    register_blueprints()
    print("Registered blueprints")

    setup_db()
    print("DB setup completed.")
    print("", flush=True)


def setup_db():
    db_file = os.path.join(
        os.path.dirname(__file__),
        'db',
        'pypi.sqlite')

    db_session.global_init(db_file)


def register_blueprints():
    from molecalc.views import home_views
    from molecalc.views import calc_views

    app.register_blueprint(home_views.bp)
    app.register_blueprint(calc_views.bp)


if __name__ == '__main__':
    main()
else:
    configure()
