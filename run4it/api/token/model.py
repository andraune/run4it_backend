import datetime as dt
from flask_jwt_extended import decode_token
from run4it.app.database import Column, SurrogatePK, db, Model


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
		token = cls.query.filter_by(jti=jti).first()
		
		if token is None:
			return True

		return token.revoked

	@classmethod
	def add_token(cls, encoded_token):
		decoded_token = decode_token(encoded_token)
		jti = decoded_token['jti']
		token_type = decoded_token['type']
		username = decoded_token['identity']
		expires = dt.datetime.fromtimestamp(decoded_token['exp'])
		revoked = False
		token = cls(jti, token_type, username, revoked, expires)
		token.save()

	@classmethod
	def find_by_username(cls, username):
		return cls.query.filter_by(username=username).order_by(cls.token_type.asc(), cls.expires.desc()).all()

	@classmethod
	def find_by_jti(cls, jti):
		return cls.query.filter_by(jti=jti).first()

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
