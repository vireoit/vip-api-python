import requests
import json
from requests.exceptions import ConnectionError
from requests.models import Response


def perform_http_request(url, authorization, body, request_method):
    headers = {
        'Authorization': authorization,
        'Content-Type': 'application/json'
    }

    response = Response()
    if request_method == "POST":
        # try:
        response = requests.post(url, headers=headers, data=json.dumps(body), verify=False)
        # except (requests.exceptions.RequestException., ConnectionError) as e:  # This is the correct syntax
        #     print(e)

    if request_method == "PUT":
        # try:
        response = requests.put(url, headers=headers, data=json.dumps(body), verify=False, )
        # except ConnectionError as e:  # This is the correct syntax
        #     print(e)

    if request_method == "GET":
        response = requests.get(url, headers=headers, verify=False)

    response_dict = response.json()
    return response_dict
