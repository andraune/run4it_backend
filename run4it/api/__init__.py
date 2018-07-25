from webargs.flaskparser import use_kwargs, parser, abort


@parser.error_handler
def webargs_parser_error(err, req, sch):
    code = getattr(err, "status_code", 400)
    data = getattr(err, "messages" , "Invalid request.")
    abort(code, errors=data)
