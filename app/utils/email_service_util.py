from app import mail
from flask_mail import Message
from flask import render_template


def send_email():
    with mail.connect() as conn:
        users = ['arunyajayan96@gmail.com', 'vishnu1998prasad@gmail.com']
        for user in users:
            message = 'Wellcome to VIP'
            subject = "hello, %s" % user
            msg = Message(recipients=[user],
                          body=message,
                          subject=subject)
            msg.html = render_template('verification_mail.html', sending_mail=True)

            conn.send(msg)