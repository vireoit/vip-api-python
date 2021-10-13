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

jwt = JWTManager(app)

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


@manager.command
def test():
    from bson.objectid import ObjectId
    from datetime import datetime
    import pytz

    query_data = mongo_db.db.Logs.find({"Subject._id": ObjectId("60bb10c89cf5432080d40346")})
    datetime_date = datetime.strptime("10-12-2021", "%m-%d-%Y")
    start_date = datetime.strptime("2021-08-17 00", "%Y-%m-%d %H")
    end_date = datetime.strptime("2021-08-17 23", "%Y-%m-%d %H")


    print(end_date)
    query_data = mongo_db.db.Logs.find({"DateOfLog": "2021-06-19", "IsActive": True})
    query_data = mongo_db.db.Logs.find({'DateOfLog': datetime(2021, 8, 17, 18, 30, tzinfo=pytz.utc)})

    query_data = mongo_db.db.Logs.find({'DateOfLog':
                                            {'$gte': datetime(2021, 8, 17, 23, 59, tzinfo=pytz.utc),
                                             '$lte': datetime(2021, 8, 17, 00, 00, tzinfo=pytz.utc)}})

    query_data = mongo_db.db.Logs.find({"DateOfLog": {"$lte": end_date, '$gt': start_date}})


    date = datetime_date.astimezone(pytz.utc)
    print(list(query_data))
    print(date)


if __name__ == "__main__":
    manager.run()


