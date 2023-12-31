from django.shortcuts import render, redirect
from django.http import JsonResponse
import openai
from django.core.serializers import serialize
from django.contrib import auth
import django
from django.contrib.auth.models import User
from .models import Chat, Chatmodel
from django.forms.models import model_to_dict
from django.utils import timezone


from .api_keys import API_KEY # use your own API key :P
# Create your views here.


#get own api key
openai.api_key=API_KEY

def ask_gpt(message, model):
    if model =="gpt-3.5-turbo":
        name="Belinda"
    elif model =="gpt-4":
        name="Chris"
    instruction="You are a helpful assistant. Please reply in consice and short. Your name is "+name
    response =openai.ChatCompletion.create(
        model=model,
        max_tokens=150,
        messages=[
            {"role":"system", "content": instruction},
            {"role": "user", "content": message},
        ]
    )
    print(response)
    return response

def ask_text(message, model):
    response =openai.Completion.create(
        model=model,
        prompt=message,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    print(response)
    return response

def chat_gpt(messages, model):
    response =openai.ChatCompletion.create(
        model=model,
        messages=messages
    )
    print(response)
    return response


def chatbot(request):
    if request.user.is_authenticated:
        chats= Chat.objects.filter(user=request.user, selectedmodel=Chatmodel.objects.first()) 
        chatmodels=Chatmodel.objects.all()
    else:
        django.contrib.messages.error(request, 'Please login to use the full function of this tool.')
        return redirect('login')
    context={
        'chats':chats,
        'chatmodels':chatmodels,
        'firstmodel':Chatmodel.objects.first()
    }
    if request.method=='POST':
        message=request.POST.get('message')
        selectedModel=request.POST.get('selectedModel')
        
        if selectedModel == 'gpt-3.5-turbo' or selectedModel == 'gpt-4':
            response=ask_gpt(message, selectedModel)
            answer=response.choices[0].message.content.strip()
            modelrole=response.choices[0].message.role
        elif selectedModel =='gpt-3.5 chat':
            chat=Chat.objects.filter(user=request.user, selectedmodel=Chatmodel.objects.get(name='gpt-3.5 chat')) 
            messages=[
            {"role":"system", "content":"You are a helpful assistant. Please reply in consice and short. Your name is Amanda."},]
            for i in chat:
                messages.append({"role": "user", "content": i.message})
                messages.append( {"role":"system", "content":i.response})
            messages.append({"role": "user", "content": message})
            response=chat_gpt(messages, 'gpt-3.5-turbo')
            answer=response.choices[0].message.content.strip()
            modelrole=response.choices[0].message.role
        else:
            response=ask_text(message, selectedModel)
            answer=response.choices[0].text.strip()
            modelrole=''

        selectedmodel=Chatmodel.objects.get(name=selectedModel)
        chatmodel=model_to_dict(selectedmodel)
        chatmodel.pop('profilepic')
        chat=Chat(
            user=request.user, 
            message=message, 
            response=answer, 
            created_at=timezone.now, 
            selectedmodel=selectedmodel,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
            modelrole=modelrole
            )
        chat.save()
        print(chatmodel)
        pic=selectedmodel.profilepic.url
        context={
            'response':answer,
            'message':message, 
            'chatmodel':chatmodel,
            'selectedModel': selectedModel, 
            'pic': pic}
        return JsonResponse(context)
    
    return render(request, 'chatbot_v2.html',context)

def changemodel(request):
    if request.method=='GET':
        
        selectmodel=request.GET['selectmodel']
        selectedmodel=Chatmodel.objects.get(name=selectmodel)
        chats= Chat.objects.filter(user=request.user, selectedmodel=selectedmodel)
        serialized_data = serialize("json", chats)
        pic=selectedmodel.profilepic.url
        chatmodel=model_to_dict(selectedmodel)
        chatmodel.pop('profilepic')
        data={
        "chats":serialized_data,
        "pic":pic,
        "chatmodel":chatmodel,
        }
        return JsonResponse(data)


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

def clear(request,pk):
    chatmodel=Chatmodel.objects.get(id=pk)
    chat=Chat.objects.filter(user=request.user, selectedmodel=chatmodel)
    context={
        'chatmodel':chatmodel,
    }
    if request.method =='POST':
        chat.delete()
        return redirect('chatbot')
    return render(request, 'clear.html', context)

