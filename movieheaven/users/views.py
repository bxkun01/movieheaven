from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,logout,login
from django.contrib import messages
from django.views.generic import UpdateView
from .models import Profile,Follow
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method=='POST':
        email= request.POST.get('email')
        username= request.POST.get('username')
        password= request.POST.get('password')

        if len(password)<8:
            messages.error(request,"Password mustn't be less than 8 characters")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
        else:
            User.objects.create_user(email=email, username=username, password=password)
            return redirect('login')


    return render(request, 'users/register.html')

def user_login(request):
    if request.method=='POST':
        username= request.POST.get('username')
        password= request.POST.get('password')

        user= authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request,'Invalid Login or Password!')

    return render(request, 'users/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def members(request):
    members=User.objects.exclude(username=request.user.username)
    for member in members:
        member.is_following = Follow.objects.filter(follower=request.user, following=member).exists()
    return render(request, 'users/members.html',{'members':members})

@login_required
def profile(request):    
    return render(request, 'users/profile.html')

def users_profile(request,user_id):    
    obj= User.objects.get(id=user_id)
    obj.is_following=Follow.objects.filter(follower=request.user, following=obj).exists()
    return render(request, 'users/users_profile.html',{'obj':obj})

class ProfileUpdateView(LoginRequiredMixin,UpdateView):
    model= Profile
    fields= ['bio','image']
    success_url= reverse_lazy('profile')

    #defines which model to update **Very much required shit!!!!!!
    def get_object(self):
        return self.request.user.profile 

    def form_valid(self, form):
       form.instance.user = self.request.user
       return super().form_valid(form)
    
@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    if request.user != user_to_follow:
        Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
    return redirect('members')

@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    return redirect('members')
        
    