#!/bin/bash

cd /mnt/vip/qa/vip_backend_python
source /mnt/vip/qa/env/bin/activate
export FLASK_ENV=test
python manage.py do_expire_password
