from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Chatmodel(models.Model):
    name=models.TextField()
    inputprice=models.FloatField()
    outputprice=models.FloatField()
    profilepic=models.ImageField(null=True, default="avatar.svg")
    greeting=models.TextField(null=True, default="Hi, I am, you can ask me anything.")

    def __str__(self):
        return self.name


class Chat(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    message=models.TextField()
    response=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    # selectedmodel=models.TextField(default="AI Chatbot")
    selectedmodel=models.ForeignKey(Chatmodel, on_delete=models.SET_NULL, null=True)
    prompt_tokens=models.IntegerField(default=0)
    completion_tokens=models.IntegerField(default=0)
    total_tokens=models.IntegerField(default=0)
    modelrole=models.TextField(default="assistant")

    def __str__(self):
        return f'{self.user.username}:{self.message}'
    
