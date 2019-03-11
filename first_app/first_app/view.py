from django.shortcuts import render, redirect
from .forms import ContactForm, LoginForm, RegisterForm
from django.contrib.auth import authenticate,login,get_user_model

def home_page(request):
	context = {"title":"Home Page",
				"content":"Welcome to Home Page"
				}
	if request.user.is_authenticated():
		context["premium_content"] = "Yeahhhhh"
	print('method invoke..home_page')
	return render(request,"home.html",context)

def about_page(request):
	print('method invoke..about_page')
	context = {"title":"About Page",
				"content":"Welcome to About Page"}
	return render(request,"home.html",context)

def contact_page(request):
	print('method invoke__contact_page')
	contact_form = ContactForm(request.POST or None)
	context = {"title":"Contact Page",
				"content":"Welcome to Contact Page",
				"form":contact_form
				}
	if contact_form.is_valid():
		print(contact_form.cleaned_data)
	return render(request,"contact/view.html",context)
def login_page(request):
	form = LoginForm(request.POST or None)
	context = {
		"form": form
	}
	print (request.user.is_authenticated())
	if form.is_valid():
		print (form.cleaned_data)
		username = form.cleaned_data.get("username")
		password = form.cleaned_data.get("password")
		user = authenticate(request,username=username,password=password)
		if user is not None:
			login(request,user)
			return redirect("/")
		else:
			print ("error")
	return render(request,"auth/login.html",context)
User = get_user_model()
def register_page(request):
	form = RegisterForm(request.POST or None)
	context = {"form":form}
	if form.is_valid():
		username = form.cleaned_data.get("username")
		email = form.cleaned_data.get("email")
		password = form.cleaned_data.get("password")
		password2 = form.cleaned_data.get("password2")
		new_user = User.objects.create_user(username,email,password)
		print (new_user)		
	return render(request,"auth/register.html",context)
