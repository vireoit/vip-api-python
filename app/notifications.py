from datetime import datetime
from bson.objectid import ObjectId
from flask import render_template

from app.utils.email_service_util import send_email
from app.base_urls import PASSWORD_RESET_LINK


class Notification:

    PASSWORD_EXPIRE_ALERT_DAYS = 88
    PASSWORD_EXPIRE_AT = 90

    @staticmethod
    def password_expiry(mongo_db):

        users = mongo_db.db.Subjects.find({})
        now = datetime.now()
        for user in users:
            last_updated_date = user.get("LastPasswordUpdatedDate")
            if last_updated_date:
                email_id = user.get("Email")
                days = (now - last_updated_date).days
                if days == Notification.PASSWORD_EXPIRE_ALERT_DAYS:
                    print("send notification  --------")
                    data_dict = {"name": user.get("Name", ""), "reset_link": "https://example.com"}
                    html_body = render_template('password_expiry_alert.html', sending_mail=True, context_data=data_dict)
                    # TODO
                    send_email("VIP password expiry notification", sender="vip@tangentia.com", recipients=[email_id],
                               text_body="", html_body=html_body)

    @staticmethod
    def do_expire_password(mongo_db):

        users = mongo_db.db.Subjects.find({})
        now = datetime.now()
        for user in users:
            last_updated_date = user.get("LastPasswordUpdatedDate")
            if last_updated_date:
                days = (now - last_updated_date).days
                user_id = user.get("_id")

                if days == Notification.PASSWORD_EXPIRE_AT:
                    print("Make expire password  --------")
                    mongo_db.db.Subjects.find_one_and_update({'_id': ObjectId(user_id)},
                                                             {'$set': {"IsMailExpired": True}})
