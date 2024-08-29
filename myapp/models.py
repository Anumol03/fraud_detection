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
    user_id=models.PositiveIntegerField(null=True,blank=True)
    
    def __str__(self):
        return f"{self.account_holder_name}"
    
class Transaction(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # The amount of the transaction
    
    oldbalanceOrg = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)  # Balance before the transaction (Sender)
    newbalanceOrig = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)  # Balance after the transaction (Sender)
    oldbalanceDest = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)  # Initial balance of the recipient before the transaction
    newbalanceDest = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)  # New balance of the recipient after the transaction
    
    ac_number = models.CharField(max_length=255)  # Account name of the recipient
    ifsc_code = models.CharField(max_length=11)  # IFSC code of the recipient's bank
    nameOrig = models.CharField(max_length=255)  # Name of the recipient
    transaction_type = models.CharField(
        max_length=20, 
        choices=[('transfer', 'Transfer'), ('payment', 'Payment')]
    )  # Type of the transaction

   
    is_fraud = models.BooleanField(default=False)  # Field to mark if the transaction is fraudulent
    isFlaggedFraud = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)  # Additional field for flagged fraud
    
    user_id = models.PositiveIntegerField(null=True, blank=True)  # User ID linked to the transaction

    def __str__(self):
        return f"Transaction {self.id} - {self.amount}"
    

