from passlib.hash import pbkdf2_sha256 as sha256
from run4it.app.database import Column, SurrogatePK, TimestampedModel, db


class User(SurrogatePK, TimestampedModel):

    __tablename__ = 'users'
    username = Column(db.String(16), unique=True, nullable=False, index=True)
    email = Column(db.String(128), unique=True, nullable=False, index=True)
    password = Column(db.String(128), nullable=True)
    confirmed = Column(db.Boolean, nullable=False, default=False)

    def __init__(self, username, email, password=None, **kwargs):
        """Create instance."""
        db.Model.__init__(self, username=username, email=email, **kwargs)
        
        if password:
            self.set_password(password)
        else:
            self.password = None

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def set_password(self, password):
        self.password = sha256.hash(password)
    
    def check_password(self, password):
        return sha256.verify(self.password, password)

    def __repr__(self):
        """Represent as unique string."""
        return '<User({username!r})>'.format(username=self.username)
