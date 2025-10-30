from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt



# مقداردهی اولیه SQLAlchemy
db = SQLAlchemy()
bcrypt = Bcrypt()

# تعریف مدل `User`
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # کلید اصلی
    username = db.Column(db.String(100), unique=True, nullable=False)  # نام کاربری
    email = db.Column(db.String(120), unique=True, nullable=False)  # ایمیل
    password = db.Column(db.String(200), nullable=False)  # رمز عبور

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

