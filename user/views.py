from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, UserLoginForm
from .models import User


class UserLoginView(LoginView):
    template_name = 'user/login.html'
    authentication_form = UserLoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        if self.request.user.is_restaurant_owner:
            return reverse_lazy('restaurant:dashboard')
        return reverse_lazy('restaurant:table_select')


class UserRegistrationView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'user/register.html'
    success_url = reverse_lazy('user:login')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.user_type = 'customer'  # Default to customer
        user.save()
        return super().form_valid(form)
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('restaurant:home')
        return super().get(request, *args, **kwargs)


def logout_view(request):
    logout(request)
    return redirect('restaurant:home') 