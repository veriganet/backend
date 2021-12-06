import requests
import json
from backend.settings import env


def request_to_drone_ci(url, method, data=None, headers=None):
    if headers is None:
        headers = {"Authorization": "Bearer %s" % env('DRONE_TOKEN')}
    if data is None:
        data = {}

    r = {}
    error = {}

    try:
        # send the api request
        r = requests.request(method=method, url=url, data=data, headers=headers)
        r.raise_for_status()
    except requests.exceptions.Timeout as et:
        error['status_code'] = 'TIMEOUT'
        error['status'] = 'failed'
        error['message'] = json.dumps(str(et))
        return error
    except requests.exceptions.HTTPError as eh:
        error['status_code'] = 'HTTPError'
        error['status'] = 'failed'
        error['message'] = json.dumps(str(eh))
    except requests.exceptions.ConnectionError as errc:
        error['status_code'] = 'ConnectTimeout'
        error['status'] = 'failed'
        errorMessage = errc
        print("Message: ", errorMessage)
        error['message'] = str(errorMessage)
        return error
    except requests.exceptions.RequestException as err:
        error['status_code'] = 'GENErr'
        error['status'] = 'failed'
        error['message'] = json.dumps(str(err))
        return error

    return r
