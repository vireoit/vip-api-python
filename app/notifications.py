from datetime import datetime


class Notification:

    PASSWORD_EXPIRE_ALERT_DAYS = 88
    PASSWORD_EXPIRE_AT = 90

    @staticmethod
    def password_expiry(mongo_db):

        users = mongo_db.db.Subjects.find({})
        now = datetime.now()
        for user in users:
            last_updated_date = user["ResetMailSentDate"]
            if last_updated_date:
                days = (now - last_updated_date).days
                if days >= Notification.PASSWORD_EXPIRE_ALERT_DAYS:
                    print("send notification  --------")
                    print(last_updated_date, Notification.PASSWORD_EXPIRE_ALERT_DAYS, days)

    @staticmethod
    def do_expire_password(mongo_db):

        users = mongo_db.db.Subjects.find({})
        now = datetime.now()
        for user in users:
            last_updated_date = user["ResetMailSentDate"]
            if last_updated_date:
                days = (now - last_updated_date).days
                if days >= Notification.PASSWORD_EXPIRE_AT:
                    print("Make expire password  --------")
