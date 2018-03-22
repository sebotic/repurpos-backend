from flask_mail import Message

from project.server import app, mail

def send_email(to, subject, template):
	msg = Message(
		subject,
		recipients=[to],
		html=template,
		sender=app.config.get('MAIL_DEFAULT_SENDER')
	)
	mail.send(msg)