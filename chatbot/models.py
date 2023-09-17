from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Chat(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    message=models.TextField()
    response=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    selectedmodel=models.TextField(default="AI Chatbot")
    prompt_tokens=models.IntegerField(default=0)
    completion_tokens=models.IntegerField(default=0)
    total_tokens=models.IntegerField(default=0)
    modelrole=models.TextField(default="assistant")

    def __str__(self):
        return f'{self.user.username}:{self.message}'