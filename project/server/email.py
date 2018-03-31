from flask_mail import Message
from boto3 import client

from project.server import app, mail

def send_email(to, subject, template):
	ses = boto3.client(
		'ses',
		region_name=app.config.get('SES_REGION_NAME'),
		aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
		aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY')
	)

	msg = {
		'Subject': {'Data': subject},
		'Body': {
			'Text': {'Data': template}
		}
	}

	ses.send_email(
		Source=app.config.get('SES_EMAIL_SOURCE'),
		Destination={'ToAddresses': [to]},
		Message=msg
	)

	# msg = Message(
	# 	subject,
	# 	recipients=[to],
	# 	html=template,
	# 	sender=app.config.get('MAIL_DEFAULT_SENDER')
	# )
	# mail.send(msg)