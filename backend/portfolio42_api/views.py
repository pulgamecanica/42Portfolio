from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
"""

"""
def	api_home(request):
	return HttpResponse("<center><h1>Welcome to 42Api</h1></center>")

def login(request):
	if request.user.is_authenticated:
		return redirect("api_home")
	return redirect("https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-12ea5db76c55712f66929aac2d7b89e4199018d87ca91386c1f3bf7def515052&redirect_uri=http%3A%2F%2Flocalhost%3A3002%2Fapi%2Fauth%2Fcallback_intra&response_type=code")

def callback_intra(request):
	pass