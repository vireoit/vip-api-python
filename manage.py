import os
from datetime import datetime
from flask_script import Manager
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from app import create_app
from flask_cors import CORS

from app.notifications import Notification as notify

env = os.getenv("FLASK_ENV") or "dev"
print(f"Active environment: * {env} *")


app, mongo_db = create_app(env)

migrate = Migrate(app, mongo_db)

manager = Manager(app)

jwt = JWTManager(app)

# CORS enabling

CORS(app)


@manager.command
def run():
    app.run(debug=True, host="0.0.0.0", ssl_context=('cert/inscholaris_cert.pem', 'cert/inscholaris_key.pem'))


@manager.command
def notify_password_expiry():
    notify.password_expiry(mongo_db)


@manager.command
def expire_password():
    notify.password_expiry(mongo_db)


if __name__ == "__main__":
    manager.run()


