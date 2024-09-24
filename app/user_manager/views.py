from django.shortcuts import render, redirect
from django.contrib.auth import login, logout

from .forms import RegisterForm, LoginForm


def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            return redirect("index")
    else:
        form = LoginForm()

    return render(
        request,
        template_name="user_app/login.html",
        context={
            "form": form,
        },
    )


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            login(request, user)

            return redirect("index")
    else:
        form = RegisterForm()

    return render(
        request,
        template_name="user_app/register.html",
        context={
            "form": form,
        },
    )


def logout_view(request):
    logout(request)
    return redirect("login")
