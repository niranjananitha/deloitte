from extensions import db
from bcrypt import hashpw , checkpw , gensalt



class User(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    name = db.Column(db.String(80), nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password= db.Column(db.String(120), nullable = False)

    def set_password(self ,password):
        self.password=hashpw(password.encode('utf-8'),gensalt()).decode('utf-8')

    def check_password(self,password):
        return checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

    def to_dict(self):
        return{
            "id" : self.id,
            "name" : self.name,
            "email" : self.email
        }