import os

env = os.getenv("FLASK_ENV") or "dev"
VIP_ADMIN_URL = "https://103.79.223.59:9094"
VIP_BACKEND_URL = "https://103.79.223.59:1013"
VIP_EMAIL_LINK = "103.79.223.61:2561"

if env == "test":
    VIP_ADMIN_URL = "https://103.79.223.59:9094"
    VIP_BACKEND_URL = "https://103.79.223.59:9094"
    VIP_EMAIL_LINK = "103.79.223.61:2561"

