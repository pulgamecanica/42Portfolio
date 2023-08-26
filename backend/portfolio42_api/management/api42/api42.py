import os
import requests
from .api_error import ApiException
import time
from datetime import datetime, timedelta
import logging

class AuthApi42():
    __token_url = 'https://api.intra.42.fr/oauth/token'

    def __init__(self,
                 uid : str = os.environ.get('INTRA_UID'),
                 secret : str = os.environ.get('INTRA_SECRET'),
                 reqs_per_second : int = 2,
                 wait_for_limit : bool = False):
        self.__uid = uid
        self.__secret = secret

        self.__token_expires = datetime(1,1,1)
        self.__access_token = None
        self.__reqs_per_second = reqs_per_second
        self.__await_limit = wait_for_limit
        self.__window = [] # Will store when a request expires (aka datetime.now() + 1 second)

    @property
    def uid(self):
        return self.__uid

    @property
    def secret(self):
        return self.__secret

    @secret.setter
    def secret(self, _secret : str):
        self.__secret = _secret

    @property
    def access_token(self):
        return self.__access_token


    @property
    def await_limit(self):
        return self.__await_limit

    @await_limit.setter
    def await_limit(self, flag : bool):
        self.__await_limit = flag

    # This function should be called each time the user wants to make a request
    @property
    def token(self):
        if (self.__token_expires > datetime.now() and self.__access_token is not None):
            # removed timed-out requests from our window
            self.__window = [t for t in self.__window if datetime.now() < t]

            # If we hit the request limit wait until a slot in the window opens up
            if (len(self.__window) >= self.__reqs_per_second):
                if (self.__await_limit):
                    sleep_time = self.__window[0] - datetime.now()
                    time.sleep(sleep_time.total_seconds())
                else:
                    logging.error('Too Many Requests')
                    raise ApiException('Too many requests')
            return self.__access_token

        # If the token has expired or its not available try to refresh token
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.__uid,
            'client_secret': self.__secret
        }

        # Fetch token
        res = requests.post(AuthApi42.__token_url, data=data)
        json = res.json()

        # throw an exception if we encounter an error (non 200 response code)
        if (res.status_code != 200):
            error_str = f"Unknown Error ({res.status_code})"
            try:
                error_str = res.json()['error_description']
            except:
                pass
            raise RuntimeError(error_str)

        # Extract info from response
        self.__access_token = json['access_token']
        self.__token_expires = datetime.now() + timedelta(seconds=json['expires_in'])

        logging.info(f"Fetched new token, expires at {self.__token_expires}")

        now = datetime.now()

        # removed timed-out requests from our window
        self.__window = [t for t in self.__window if now < t]

        if (len(self.__window) >= self.__reqs_per_second):
            if (self.await_limit):
                sleep_time = self.__window[0] - datetime.now()
                time.sleep(sleep_time.total_seconds())
            else:
                raise ApiException('Too many requests')

        return self.__access_token

    # Should be called after making a request,
    # updates the window for more accurate rate limit checking
    def report_request(self):
        self.__window.append(datetime.now() + timedelta(seconds=1))


class Api42():
    __api_base_url = "https://api.intra.42.fr"

    """
        Interface for interacting with the 42 api

        uid - UID of application obtained from intra
        secret - SECRET of application obtained from intra
        req_limit - The amount of requests that can be made per second
    """
    def __init__(self, uid :str, secret : str, req_limit : int = 2):
        self.__auth = AuthApi42(uid, secret, reqs_per_second = req_limit, wait_for_limit= True)

    def await_limit(self, should_wait : bool):
        self.__auth.await_limit(should_wait)

    def get(self, endpoint : str, params : dict = { }):
        # Make request
        headers = {'Authorization': f"Bearer {self.__auth.token()}"}
        res = requests.get(f"{Api42.__api_base_url}{endpoint}",
                           headers=headers, params=params)
        self.__auth.report_request()

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
            logging.error("error_reason")
            raise ApiException(error_reason)

        # Try parsing json
        try:
            return res.json()
        except:
            logging.error("Response was not in json format")
            raise ApiException("Response was not in json format")


