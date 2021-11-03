import re
from bson.objectid import ObjectId
from flask import request


def check_user_by_id(mongo_db, user_id):
    user = mongo_db.db.Subjects.find_one({"_id": ObjectId(str(user_id)), "IsActive": True})
    if user:
        user_dict = dict(user)
        user_data = dict()

        user_data["_id"] = user_id
        user_data["Name"] = user_dict["Name"]
        user_data["Email"] = user_dict["Email"]
        user_data["Address"] = user_dict["Address"]
        user_data["Gender"] = user_dict["Gender"]
        user_data["Phone"] = user_dict["Phone"]
        user_data["AddedOn"] = user_dict["AddedOn"]
        user_data["ActivatedOn"] = user_dict["ActivatedOn"]
        user_data["IsActive"] = user_dict["IsActive"]

        return user_data
    return user


def detect_device():

    browser = request.user_agent.browser
    version = request.user_agent.version and int(request.user_agent.version.split('.')[0])
    platform = request.user_agent.platform
    uas = request.user_agent.string

    device_type = "Web"

    if browser and version:

        if re.search('Mobile', uas):
            device_type = "Mobile"
    device = {"browser": browser, "version": version, "platform": platform, "device_type": device_type, "user_agent": uas}

    return device
