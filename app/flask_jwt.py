import jwt

from functools import wraps
from re import split

from flask import _request_ctx_stack
from flask import request
from flask_jwt_extended.config import config
from flask_jwt_extended.exceptions import InvalidHeaderError
from flask_jwt_extended.exceptions import NoAuthorizationError


def jwt_required(optional=False, fresh=False, refresh=False, locations=None):
    """
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request(optional, fresh, refresh, locations)
            return fn(*args, **kwargs)

        return decorator

    return wrapper


def verify_jwt_in_request(optional=False, fresh=False, refresh=False, locations=None):
    """
    """
    if request.method in config.exempt_methods:
        return

    jwt_data = _decode_jwt_from_headers()
    decoded = jwt.decode(jwt_data[0], options={"verify_signature": False})
    _request_ctx_stack.top.jwt = decoded
    return jwt_data


def _decode_jwt_from_headers():
    header_name = config.header_name
    header_type = config.header_type

    # Verify we have the auth header
    auth_header = request.headers.get(header_name, None)
    if not auth_header:
        raise NoAuthorizationError("Missing {} Header".format(header_name))

    # Make sure the header is in a valid format that we are expecting, ie
    # <HeaderName>: <HeaderType(optional)> <JWT>
    jwt_header = None

    # Check if header is comma delimited, ie
    # <HeaderName>: <field> <value>, <field> <value>, etc...
    if header_type:
        field_values = split(r",\s*", auth_header)
        jwt_header = [s for s in field_values if s.split()[0] == header_type]
        if len(jwt_header) < 1 or len(jwt_header[0].split()) != 2:
            msg = "Bad {} header. Expected value '{} <JWT>'".format(
                header_name, header_type
            )
            raise InvalidHeaderError(msg)
        jwt_header = jwt_header[0]
    else:
        jwt_header = auth_header

    parts = jwt_header.split()
    if not header_type:
        if len(parts) != 1:
            msg = "Bad {} header. Expected value '<JWT>'".format(header_name)
            raise InvalidHeaderError(msg)
        encoded_token = parts[0]
    else:
        encoded_token = parts[1]

    return encoded_token, None
