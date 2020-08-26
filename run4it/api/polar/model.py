import datetime as dt
from random import choice
from string import ascii_letters, digits
from sqlalchemy import UniqueConstraint
from flask import current_app
from run4it.app.database import Column, SurrogatePK, reference_col, relationship, db


POLAR_AUTHORIZATION_URL = "https://flow.polar.com/oauth2/authorization?response_type=code&client_id={0}&state={1}"


class PolarUser(SurrogatePK, db.Model):
	__tablename__ = 'polar_users'
	profile_id = reference_col('user_profiles', unique=True, nullable=False, index=True)
	member_id = Column(db.String(24), unique=True, nullable=False)
	polar_user_id = Column(db.Integer, nullable=False)
	state = Column(db.String(16), unique=False, nullable=True)
	access_token = Column(db.String(64), nullable=True)
	access_token_expires = Column(db.DateTime, nullable=True)
	updated_at = Column(db.DateTime, nullable=True)

	def __init__(self, profile_id, username):
		member_id = 'R4IT_{0}'.format(username)
		db.Model.__init__(self, profile_id=profile_id, member_id=member_id, polar_user_id=0)

	@classmethod
	def find_by_member_id(cls, id):
		return cls.query.filter_by(member_id=id).first()

	@classmethod
	def find_by_state_code(cls, code):
		polar_users = cls.query.filter_by(state=code).all()

		if (polar_users is None or len(polar_users) != 1):
			return None

		return polar_users[0]
	
	@property
	def auth_url(self):
		if self.has_valid_access_token() or self.state is None:
			return ''
		return POLAR_AUTHORIZATION_URL.format(current_app.config["POLAR_API_CLIENT_ID"], self.state)

	def generate_state_code(self):
		self.state = ''.join(choice(ascii_letters + digits) for _ in range(15))
	
	def is_registered(self):
		return self.polar_user_id > 0 and self.access_token is not None and len(self.access_token) > 0

	def has_valid_access_token(self):
		if self.is_registered():
			now = dt.datetime.utcnow()
			return self.access_token_expires > now
		return False

	def __repr__(self):
		return '<PolarUser({id!r}:{member!r})>'.format(
			id=self.profile_id,
			member=self.member_id)
