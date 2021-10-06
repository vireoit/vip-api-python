class BaseErrors:
    @classmethod
    def all(cls):
        return {name: value for name, value in vars(cls).items() if name.isupper()}


class AppError(BaseErrors):

    API_ERROR_MSG = "Oops something went wrong .Please try after sometime."
    SITE_MAINTENANCE_ERROR_MSG = "IT Centre maintenance is under progress. Please try after sometimes"
    NO_NETWORK_MSG = "We’re sorry but there seems to be an issue loading your drive information .Please check your data connection &try again in a few moments"
    API_ERROR_IMAGE = ""
    SITE_MAINTENANCE_ERROR_IMAGE = ""
