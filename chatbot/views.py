from django.shortcuts import render, redirect
from django.http import JsonResponse
import openai

from django.contrib import auth, messages
from django.contrib.auth.models import User
from .models import Chat

from django.utils import timezone


from .api_keys import API_KEY # use your own API key :P
# Create your views here.


openai.api_key=API_KEY

def ask_gpt(message, model):
    response =openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role":"system", "content":"You are a helpful assistant."},
            {"role": "user", "content": message},
        ]
    )
    #print(response)

    answer=response.choices[0].message.content.strip()
    return answer

def ask_text(message, model):
    response =openai.Completion.create(
        model=model,
        prompt=message,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    #print(response)

    answer =response.choices[0].text.strip()
    return answer

def chatbot(request):
    if request.user.is_authenticated:
        chats= Chat.objects.filter(user=request.user)
    else:
        messages.error(request, 'Please login before using this tool!!')
        return redirect('login')
    context={
        'chats':chats
    }
    if request.method=='POST':
        message=request.POST.get('message')
        selectedModel=request.POST.get('selectedModel')
        print(selectedModel)
        if selectedModel == 'gpt-3.5-turbo' or selectedModel == 'gpt-4':
            response=ask_gpt(message, selectedModel)
        else:
            response=ask_text(message, selectedModel)

        chat=Chat(user=request.user, message=message, response=response, created_at=timezone.now)
        chat.save()
        return JsonResponse({'response':response,'message':message, 'selectedModel': selectedModel})
    return render(request, 'chatbot.html',context)

def login(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message='Invalid user!'
            return render(request, 'login.html', {'error_message':error_message})
    else:
        return render(request, "login.html")

def register(request):
    if request.method=='POST':
        username=request.POST['username']
        email=request.POST['email']
        password1=request.POST['password1']
        password2=request.POST['password2']

        if password1==password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message='Error during create account!'
                return render(request, 'register.html', {'error_message':error_message})
        else:
            error_message='Password not match!!'
            return render(request, 'register.html', {'error_message':error_message})
    return render(request, "register.html")

def logout(request):
    auth.logout(request)
    return redirect('login')

def delete(request):
    chat=Chat.objects.filter(user=request.user)
    if request.method =='POST':
        chat.delete()
        return redirect('chatbot')
    return render(request, 'delete.html')