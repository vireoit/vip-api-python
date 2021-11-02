import os

env = os.getenv("FLASK_ENV") or "dev"
VIP_ADMIN_URL = "https://103.79.223.59:9094"
VIP_BACKEND_URL = "https://103.79.223.59:1013"


if env == "test":
    VIP_ADMIN_URL = "https://103.79.223.59:9094"
    VIP_BACKEND_URL = "https://103.79.223.59:9094"



