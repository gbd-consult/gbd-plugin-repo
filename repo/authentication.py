from repo.models import User
from repo import auth

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(name = username).first()
    if user:
        return user.check_password(password)
    else:
        return False
