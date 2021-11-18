from app import mail
from flask_mail import Message
from flask import render_template


def send_email_patient_activation(data_list, message, subject, template):
    with mail.connect() as conn:
        for data in data_list:
            msg = Message(recipients=[data['email_id']],
                          body=message,
                          subject=subject)
            msg.html = render_template(template, sending_mail=True, data=data)
            conn.send(msg)
