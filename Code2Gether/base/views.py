from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.http import HttpResponse
from .models import Room,Messages,Topic,Profile,about
from .forms import RoomForm,UserForm,ProfileForm
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# Create your views here.
@cache_control(no_store=True, max_age=0)
def login_page(request):
    page = "login"
    
    if request.user.is_authenticated:
        return redirect('home')
        
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        
        except:
            messages.error(request, 'user does not exist')
            
        user = authenticate(request, username=username, password=password)

        if user != None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'username and password does not match')

    context = {'page':page}
    return render(request, 'login.html', context)

@cache_control(no_store=True, max_age=0, must_revalidate=True)
def logoutUser(request):
    logout(request)
    return redirect ('home')





def reg(request):
    page = "register"
    form = UserCreationForm()      
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user = form.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'an error occured during registeration')
            
       
    context = {'form': form}
    return render(request,'signup.html', context)




@cache_control(no_store=True, max_age=0, must_revalidate=True)
def home (request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains = q)|
        Q(name__icontains = q)|
        Q(description__icontains = q)|
        Q(host__username__icontains = q))
    room_count = rooms.count()
    total_cnt = Room.objects.count()
    topic = Topic.objects.all()[0:5]
    room_messages = Messages.objects.filter(Q(room__topic__name__icontains=q)).order_by('-created')
    context = {'rooms':rooms, 'topics':topic, 'room_count':room_count,'room_messages':room_messages,'total_cnt':total_cnt}
    return render(request,'home.html', context)
 
 

def room (request,pk):
    room = Room.objects.get(id=pk)
    messagess = Messages.objects.filter(room=room).order_by('-created')
    participants = room.participants.all()
    if request.method == "POST":
        Messages.objects.create(
            user = request.user,
            room=room,
            body=request.POST.get('msgfield')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    
    context = {'room':room,'messagess':messagess,'participants':participants}
    return render(request,'room.html',context)




@login_required(login_url = 'login_page')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
#        form = RoomForm(request.POST)
#        if form.is_valid():
#            room = form.save(commit=False)
#            room.host = request.user
#            form.save()
        return redirect('home')
    context = {'form':form,'topics':topics}
    return render(request , 'create_form.html',context)




@login_required(login_url = 'login_page')
@cache_control(no_store=True, max_age=0)
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse("you are not the owner")

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
    
        room.host = request.user 
        room.name = request.POST.get('name')
        room.topic=topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'room': room}
    return render(request, 'update.html', context)



@login_required(login_url = 'login_page')
@cache_control(no_store=True, max_age=0)
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
        return HttpResponse("you are not the owner")
    
    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'delete.html', {'obj':room.name})


@login_required(login_url = 'login_page')
@cache_control(no_store=True, max_age=0, must_revalidate=True)
def deleteMsg(request,pk):
    try:
        message = Messages.objects.get(id=pk)
    except ObjectDoesNotExist:
        return redirect('home')
    
    
    if request.user != message.user:
        return HttpResponse("you are not the owner")
    
    if request.method == "POST":
        message.delete()
        return redirect('room',message.room.id)
    return render(request, 'delete.html',{'obj':message})


@cache_control(no_store=True, max_age=0, must_revalidate=True)
def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    total_cnt = Room.objects.count()
    room_messages = user.messages_set.all()
    topics = Topic.objects.all()
    context = {'user':user,'rooms':rooms,'topics':topics,'room_messages':room_messages,'total_cnt':total_cnt}
    return render(request,'profile.html',context)


def editUser(request):

    user = User.objects.get(id=request.user.id)
    profile, created = Profile.objects.get_or_create(user=user)
    abouts, created = about.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            abouts.bio = user_form.cleaned_data['bio']
            abouts.save()
            return redirect('home')
    else:
        user_form = UserForm(instance=user, initial={'bio': abouts.bio})
        profile_form = ProfileForm(instance=profile)

    context = {'form': user_form, 'profile_form': profile_form, 'abouts': abouts}
    return render(request, 'edit-user.html', context)


def mobtop(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains = q)
    topicss = Topic.objects.all()
    total_cnt = Room.objects.count()
    context = {'topics':topics,'total_cnt':total_cnt,'topicss':topicss}
    return render(request,'mob_topics.html',context)


def mobact(request,pk):
    room_messages = Messages.objects.all()
    total_cnt = Room.objects.count()
    context = {'room_messages':room_messages}
    return render(request,'mob_activity.html',context)