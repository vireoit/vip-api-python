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


@manager.command
def test_nested():
    from bson.objectid import ObjectId
    from datetime import datetime
    import pytz

    survey_sub_query = {'_id': {'$in': [ObjectId("618cf4098523c5097c524315")]}}
    patient_sub_query = {'Patients.DatesInfo.QuestionsAndAnswers': {'$elemMatch': {'payout_amount': {'$gte': 0}}}}
    patient_sub_query = {'_id': {'$in': [ObjectId("618b9d75282c5e202073368e"), ObjectId("618ba92d282c5e202073368f")]},
                         'Patients.DatesInfo.QuestionsAndAnswers.Answers': {'$elemMatch': {"Answer": {'$exists': True}}}}

    patient_sub_query = {
                         'Patients.DatesInfo.QuestionsAndAnswers.Answers': {
                             '$elemMatch': {"Answer": {'$exists': True, '$not': {'$size': 0}}}}}

    patient_sub_query = {'Patients._id': {'$in': [ObjectId("618ceb067c92cf3d385c9b0a")]}}

    aggr_data = mongo_db.db.Surveys.aggregate([
        {"$unwind": "$Patients"},
        {"$unwind": "$Patients.DatesInfo"},
        {"$unwind": "$Patients.DatesInfo.QuestionsAndAnswers"},
        {"$unwind": "$Patients.DatesInfo.QuestionsAndAnswers.Answers"},
        {"$match": survey_sub_query},
        # {"$match": patient_sub_query},
        # {"$match": {"Patients.DatesInfo.QuestionsAndAnswers.Answers.Answer": {"$nin": ['null', ""]}}},

        {"$match": {"Patients.DatesInfo.QuestionsAndAnswers.Question": {'$in': ["Question1"]}}},

        {"$project": {'Patients.Name': 1, 'Patients.DatesInfo.QuestionsAndAnswers.Answers': 1, 'Patients._id': 1,
                      "Patients.DatesInfo.QuestionsAndAnswers.Question": 1, "Patients.DatesInfo.SubmittedDate": 1}},

        {"$group": {"_id": "$Patients.Name",
                    "data": {"$push": {"question": "$Patients.DatesInfo.QuestionsAndAnswers.Question",
                                       "answer": "$Patients.DatesInfo.QuestionsAndAnswers.Answers.Answer",
                                       "SubmittedDate": "$Patients.DatesInfo.SubmittedDate",
                                       "subjectName": "$Patients.Name", "subject_id": "$Patients._id"}}
                    }}])

    # query_data = mongo_db.db.Surveys.find(aggr)
    # data = list(query_data)
    data = list(aggr_data)
    new_list = list()
    for data_dict in data:
        new_list.extend(data_dict["data"])
    # print("list", data, ">>>>>>>", len(data))
    print(new_list)


if __name__ == "__main__":
    manager.run()


