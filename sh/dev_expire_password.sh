#!/bin/bash

cd /mnt/vip/dev/vip_backend_python
source /mnt/vip/dev/env/bin/activate
export FLASK_ENV=dev
python manage.py do_expire_password
