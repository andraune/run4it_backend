import datetime as dt
from flask_jwt_extended import decode_token
from random import choice
from string import ascii_letters, digits
from sqlalchemy.orm.exc import NoResultFound
from passlib.hash import pbkdf2_sha256 as sha256
from run4it.app.database import Column, SurrogatePK, TimestampedModel, db, Model


class User(SurrogatePK, TimestampedModel):
    __tablename__ = 'users'
    username = Column(db.String(16), unique=True, nullable=False, index=True)
    email = Column(db.String(128), unique=True, nullable=False, index=True)
    password = Column(db.String(128), nullable=True)
    confirmed = Column(db.Boolean, nullable=False, default=False)
    access_token = ''
    refresh_token  = ''

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
        return sha256.verify(password, self.password)

    def __repr__(self):
        return '<User({username!r})>'.format(username=self.username)


class UserConfirmation(SurrogatePK, Model):
    __tablename__ = 'user_confirmation_codes'
    username = Column(db.String(16), unique=True, nullable=False, index=True)
    code = Column(db.String(64), nullable=False)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, username, confirmation_code=None, **kwargs):
        db.Model.__init__(self, username=username, **kwargs)

        if confirmation_code:
            self.code = confirmation_code
        else:
            self.generate_code(32)
    
    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    def generate_code(self, size):
        self.code = ''.join(choice(ascii_letters + digits) for _ in range(size))

    def check_code(self, confirmation_code):
        return self.code == confirmation_code
    
    def check_expiration(self, seconds):
        now = dt.datetime.utcnow()
        is_expired = False
        
        try:
            datedelta = now - self.created_at
            is_expired = (datedelta.days > 0 or datedelta.seconds > seconds)
        except:
            # timedelta overflow
            is_expired = True
        
        return not is_expired
    
    def __repr__(self):
        return '<UserConfirmation({username!r}:{code!r})>'.format(username=self.username, code=self.code)


class TokenRegistry(SurrogatePK, Model):
    __tablename__ = 'token_registry'
    jti = Column(db.String(64), nullable=False, index=True)
    token_type = Column(db.String(8), nullable=False)
    username = Column(db.String(16), nullable=False, index=True)
    revoked = Column(db.Boolean, nullable=False)
    expires = Column(db.DateTime, nullable=False)

    def __init__(self, jti, token_type, username, revoked, expires):
        db.Model.__init__(self, jti=jti, token_type=token_type, username=username, revoked=revoked, expires=expires)
    
    @classmethod
    def is_token_revoked(cls, jti):
        try:
            token = cls.query.filter_by(jti=jti).first()
            return token.revoked
        except NoResultFound:
            return True

    @classmethod
    def add_encoded_token(encoded_token, username):
        decoded_token = decode_token(encoded_token)
        jti = decoded_token['jti']
        token_type = decoded_token['type']
        expires = dt.datetime.fromtimestamp(decoded_token['exp'])
        revoked = False
        token = cls(jti, token_type, username, revoked, expires)
        token.save()

    @classmethod
    def remove_expired_tokens(cls):
        now = dt.datetime.now()
        expired_list = cls.query.filter(TokenRegistry.expires < now).all()
        
        for token in expired_list:
            token.delete(False) # do not commit every delete for itself

        db.session.commit()
        return len(expired_list)

    def __repr__(self):
        return '<Token({username!r}:{jti!r})>'.format(username=self.username, jti=self.jti)
