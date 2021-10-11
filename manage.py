import os
from flask_script import Manager
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from app import create_app
from flask_cors import CORS

env = os.getenv("FLASK_ENV") or "dev"
print(f"Active environment: * {env} *")


app, mongo_db = create_app(env)

migrate = Migrate(app, mongo_db)

manager = Manager(app)

# jwt = JWTManager(app)

# CORS enabling

CORS(app)


@manager.command
def run():
    app.run(debug=True, host="0.0.0.0", ssl_context=('cert/vip_cert.pem', 'cert/vip_key.pem'))


@manager.command
def do_expire_users():
    users = mongo_db.db.Subjects.find({})
    for user in users:
        print("users", user["Email"])


if __name__ == "__main__":
    manager.run()


