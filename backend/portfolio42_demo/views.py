from django.http import HttpResponse
from django.shortcuts import render, redirect

def home_page(request):
    return render(request, "home.html")

def profile(request):
	if not request.user.is_authenticated:
		return redirect("login_intra")
	return render(request, "profile.html")