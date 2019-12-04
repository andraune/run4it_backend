from webargs.flaskparser import use_kwargs, parser, abort
from run4it.app.extensions import jwt
from run4it.api.templates import report_error_and_abort
from run4it.api.token.model import TokenRegistry


@parser.error_handler
def webargs_parser_error(err, req, sch, status_code, header):
    data = getattr(err, "messages" , "Invalid request.")
    abort(status_code, errors=data)


@jwt.token_in_blacklist_loader
def jwt_check_if_token_is_blacklisted(decoded_token):
    jti = decoded_token["jti"]
    return TokenRegistry.is_token_revoked(jti) 

@jwt.unauthorized_loader
def jwt_missing_authorization_header(msg):
    report_error_and_abort(401, "auth", msg)

@jwt.invalid_token_loader
def jwt_invalid_token_or_token_type(msg):
    report_error_and_abort(422, "auth", "Invalid token.")

@jwt.needs_fresh_token_loader
def jwt_fresh_token_required():
    report_error_and_abort(401, "auth", "Fresh token required.")

@jwt.expired_token_loader
def jwt_expired_token_handler(expired_token):
	report_error_and_abort(401, "auth", "Expired token.")

@jwt.revoked_token_loader
def jwt_revoked_token_handler():
	report_error_and_abort(401, "auth", "Revoked token.")
