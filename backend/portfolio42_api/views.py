from django.shortcuts import redirect, render
from django.contrib.auth import login
from django.http import HttpResponse
from portfolio42_api.models import User
from portfolio42_api.api42utils import intra_fail_reason
import requests
import os

"""
Welcome Page
"""
# def api_home(request):
# 	return HttpResponse("<center><h1>Welcome to 42Api</h1></center>")

"""
Helper Function, rediret to intra or homepage
This function can help us login fast, so we don't need to get the link from intra.
"""
def login_intra(request):
	if request.user.is_authenticated:
		return redirect("api_home")
	return redirect("https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-12ea5db76c55712f66929aac2d7b89e4199018d87ca91386c1f3bf7def515052&redirect_uri=http%3A%2F%2Flocalhost%3A3002%2Fapi%2Fauth%2Fcallback_intra&response_type=code")

"""
All information about callback here:
 - https://github.com/pulgamecanica/42Portfolio/wiki/2---Authentication
This function will be called after the user grants permission
"""
def callback_intra(request):
	get_token_path = "https://api.intra.42.fr/oauth/token"
	data = {
		'grant_type': 'authorization_code',
		'client_id':  os.environ.get('INTRA_UID'),
		'client_secret': os.environ.get('INTRA_SECRET'),
		'code': request.GET["code"],
		'redirect_uri': 'http://localhost:%s/api/auth/callback_intra' % os.environ.get('BACKEND_PORT'),
	}
	r = requests.post(get_token_path, data=data)

	"""
		Check if request was succesfull, if not,
		return an error Response with the reason
	"""
	if (r.status_code != 200):
		return HttpResponse("[Error] Reason: %s" % intra_fail_reason(r.status_code));

	"""
		Get the token from the response
		Build Headers with the token
	"""
	try:
		token = r.json()['access_token']
		headers = {"Authorization": "Bearer %s" % token}
	except:
		return HttpResponse("[Error] Reason: %s" % intra_fail_reason("json"));

	"""
		Check if request was succesfull, if not,
		return an error Response with the reason
	"""
	user_response = requests.get("https://api.intra.42.fr/v2/me", headers=headers)
	if (user_response.status_code != 200):
		return HttpResponse("[Error] Reason: %s" % intra_fail_reason(r.status_code));

	"""
		login the user, if the user does not exists
		yet, we will create it, using get_or_create
	"""
	try:
		user_response_json = user_response.json()
		"""
			TODO
			Missing image_url, intra_url, check other
			stuff that might be predefined...
		"""
		user, created = User.objects.get_or_create(
	    		intra_id=user_response_json['id'],
	    		username=user_response_json['login'],
	    		first_name=user_response_json['first_name'],
	    		last_name=user_response_json['last_name'],
	    		email=user_response_json['email'],
		)
	except:
		return HttpResponse("[Error] Reason: %s" % intra_fail_reason("json"));

	login(request, user)
	return HttpResponse("User %s %s" % (user, "created now" if created else "found"))
