import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_jwt_extended import JWTManager
from app import create_app, db
from flask_cors import CORS

env = os.getenv("FLASK_ENV") or "dev"
print(f"Active environment: * {env} *")


app = create_app(env)

migrate = Migrate(app, db)

manager = Manager(app)

jwt = JWTManager(app)

# CORS enabling

CORS(app)

@manager.command
def run():
    app.run(debug=True, host="0.0.0.0", ssl_context=('cert/inscholaris_cert.pem', 'cert/inscholaris_key.pem'))


manager.add_command('db', MigrateCommand)


if __name__ == "__main__":
    manager.run()


