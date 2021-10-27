# vip_backend_python

### gunicorn --certfile cert/vip_cert.pem --keyfile cert/vip_key.pem -b 0.0.0.0:5005 manage:app

#### [Unit]
##### Description=VIP  application
##### After=network.target

[Service]
#### User=developer
##### WorkingDirectory=/mnt/vip/dev/vip_backend_python
##### ExecStart=/mnt/vip/dev/env/bin/gunicorn --certfile cert/vip_cert.pem --keyfile cert/vip_key.pem -b 0.0.0.0:5005 manage:app
##### Restart=always

#### [Install]
##### WantedBy=multi-user.target