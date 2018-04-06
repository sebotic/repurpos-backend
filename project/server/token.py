from itsdangerous import URLSafeTimedSerializer

from project.server import app


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config.get('SECRET_KEY'))
    return serializer.dumps(email, salt=app.config.get('SECRET_PASSWORD_SALT'))


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config.get('SECRET_KEY'))
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECRET_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email
