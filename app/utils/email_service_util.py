from app import mail, app
from flask_mail import Message
from threading import Thread

def _send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender="vip@tangentia.com", recipients=[], text_body="", html_body=""):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    thr = Thread(target=_send_async_email, args=[app, msg])
    thr.start()

