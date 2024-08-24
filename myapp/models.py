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
    
class Transaction(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    nameOrig = models.CharField(max_length=255)
    oldbalanceOrg = models.DecimalField(max_digits=10, decimal_places=2)
    newbalanceOrig = models.DecimalField(max_digits=10, decimal_places=2)
    oldbalanceDest = models.DecimalField(max_digits=10, decimal_places=2)
    newbalanceDest = models.DecimalField(max_digits=10, decimal_places=2)
    ac_name = models.CharField(max_length=255)
    ifsc_code = models.CharField(max_length=11)
    recipient_name = models.CharField(max_length=255)
    transaction_type = models.CharField(max_length=20, choices=[('transfer', 'Transfer'), ('payment', 'Payment'), ('cash_in', 'Cash In'), ('cash_out', 'Cash Out')])
    total_balance = models.DecimalField(max_digits=10, decimal_places=2)
    is_fraud = models.BooleanField(default=False)
    isFlaggedFraud = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)  # New field

    def __str__(self):
        return f"Transaction {self.id} by {self.nameOrig}"