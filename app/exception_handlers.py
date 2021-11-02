from app.response import Response
from app.exceptions import (UserDoesNotExist, RedeemedPoint
)
from app.status_constants import HttpStatusCode, BusinessErrorCode


def register_error_handlers(api):

    @api.errorhandler(UserDoesNotExist)
    def handle_user_does_not_exists_exception(error):
        return Response.error(
            {"exception": str(error)},
            HttpStatusCode.BAD_REQUEST,
            business_error=BusinessErrorCode.USER_EXIST,
            message=str(error)
        )

    @api.errorhandler(RedeemedPoint)
    def handle_redeemed_point(error):
        return Response.error(
            {"exception": str(error)},
            HttpStatusCode.BAD_REQUEST,
            business_error=None,
            message=str(error)
        )
