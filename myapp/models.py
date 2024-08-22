from django.db import models

from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    dob = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)

   

    def __str__(self):
        return self.username


class BankAccount(models.Model):
    
    account_number = models.CharField(max_length=20)  
    account_holder_name = models.CharField(max_length=100) 
    bank_name = models.CharField(max_length=100)  
    branch_name = models.CharField(max_length=100) 
    ifsc_code = models.CharField(max_length=11)  
    
    def __str__(self):
        return f"{self.account_holder_name}"