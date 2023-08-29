import os
import requests
from .api_error import ApiException
import time
from datetime import datetime, timedelta
import logging

class AuthApi42():
    _TOKEN_URL = 'https://api.intra.42.fr/oauth/token'

    def __init__(self,
                 uid : str = os.environ.get('INTRA_UID'),
                 secret : str = os.environ.get('INTRA_SECRET'),
                 reqs_per_second : int = 2,
                 wait_for_limit : bool = False):
        self._uid = uid
        self._secret = secret

        self._token_expires = datetime(1,1,1)
        self._access_token = None
        self._reqs_per_second = reqs_per_second
        self._await_limit = wait_for_limit
        self._window = [] # Will store when a request expires (aka datetime.now() + 1 second)

    @property
    def uid(self):
        return self._uid

    @property
    def secret(self):
        return self._secret

    @secret.setter
    def secret(self, _secret : str):
        self._secret = _secret

    @property
    def access_token(self):
        return self._access_token


    @property
    def await_limit(self):
        return self._await_limit

    @await_limit.setter
    def await_limit(self, flag : bool):
        self._await_limit = flag

    # This function should be called each time the user wants to make a request
    @property
    def token(self):
        if (self._token_expires > datetime.now() and self._access_token is not None):
            # removed timed-out requests from our window
            self._window = [t for t in self._window if datetime.now() < t]

            # If we hit the request limit wait until a slot in the window opens up
            if (len(self._window) >= self._reqs_per_second):
                if (self._await_limit):
                    sleep_time = self._window[0] - datetime.now()
                    time.sleep(sleep_time.total_seconds())
                else:
                    logging.error('Too Many Requests')
                    raise ApiException('Too many requests')
            return self._access_token

        # If the token has expired or its not available try to refresh token
        data = {
            'grant_type': 'client_credentials',
            'client_id': self._uid,
            'client_secret': self._secret
        }

        # Fetch token
        res = requests.post(AuthApi42._TOKEN_URL, data=data)
        json = res.json()

        # throw an exception if we encounter an error (non 200 response code)
        if (res.status_code != 200):
            error_str = f"Unknown Error ({res.status_code})"
            try:
                error_str = res.json()['error_description']
            except:
                pass
            raise ApiException(error_str)

        # Extract info from response
        self._access_token = json['access_token']
        self._token_expires = datetime.now() + timedelta(seconds=json['expires_in'])

        logging.info(f"Fetched new token, expires at {self._token_expires}")

        now = datetime.now()

        # removed timed-out requests from our window
        self._window = [t for t in self._window if now < t]

        if (len(self._window) >= self._reqs_per_second):
            if (self.await_limit):
                sleep_time = self._window[0] - datetime.now()
                time.sleep(sleep_time.total_seconds())
            else:
                raise ApiException('Too many requests')

        return self._access_token

    # Should be called after making a request,
    # updates the window for more accurate rate limit checking
    def report_request(self):
        self._window.append(datetime.now() + timedelta(seconds=1))


class Api42():
    _API_URL = "https://api.intra.42.fr/v2"

    """
        Interface for interacting with the 42 api

        uid - UID of application obtained from intra
        secret - SECRET of application obtained from intra
        req_limit - The amount of requests that can be made per second
    """
    def __init__(self, uid :str, secret : str, req_limit : int = 2):
        self._auth = AuthApi42(uid, secret, reqs_per_second = req_limit, wait_for_limit= True)

    def await_limit(self, should_wait : bool):
        self._auth.await_limit(should_wait)

    def get(self, endpoint : str, params : dict = { }):
        # Make request
        headers = {'Authorization': f"Bearer {self._auth.token}"}
        res = requests.get(f"{Api42._API_URL}{endpoint}",
                           headers=headers, params=params)
        self._auth.report_request()

        logging.info(f"Made request to 42 API at {endpoint} ({res.status_code})")

        # Check the status code
        if(res.status_code != 200):
            error_reason = f"Error while fetching, status code: {res.status_code}"
            try:
                error_reason = res.json()['error']
            except:
                if (len(res.text) != 0):
                    error_reason = res.text
                pass
            logging.error(error_reason)
            raise ApiException(error_reason)

        # Try parsing json
        try:
            return res.json()
        except:
            logging.error("Response was not in json format")
            raise ApiException("Response was not in json format")


