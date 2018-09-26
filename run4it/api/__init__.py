from webargs.flaskparser import use_kwargs, parser, abort
from run4it.app.extensions import jwt
from run4it.api.exceptions import report_error_and_abort
from run4it.api.user.model import TokenRegistry


@parser.error_handler
def webargs_parser_error(err, req, sch):
    code = getattr(err, "status_code", 400)
    data = getattr(err, "messages" , "Invalid request.")
    abort(code, errors=data)


@jwt.token_in_blacklist_loader
def jwt_check_if_token_is_blacklisted(decoded_token):
    return TokenRegistry.is_token_revoked(decoded_token) 

@jwt.unauthorized_loader
def jwt_missing_authorization_header(msg):
    report_error_and_abort(401, "auth", msg)

@jwt.invalid_token_loader
def jwt_invalid_token_or_token_type(msg):
    report_error_and_abort(422, "auth", "Invalid token")
