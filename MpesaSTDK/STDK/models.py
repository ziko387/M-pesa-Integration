from django.db import models

# Create your models here.
class Transaction(models.Model):
    # transaction id: field to store transaction id
     transaction_id= models.CharField(max_length=120,blank=True,null=True)
     ## phone number : number initializing transaction
     phone_number= models.CharField(max_length=15)
     amount = models.DecimalField(decimal_places=2,max_digits=10)
     ##Mpesa recipet number
     mpesa_receipt_number= models.CharField(max_length=100,blank=True,null=True)
    ## transaction status: pending , completed, faliure
     status = models.CharField(max_length=100,blank=True,null=True)
description=models.CharField(blank=True,null=True)
transaction_date = models.DateTimeField(blank=True,null=True)
date_created = models.DateTimeField(auto_now_add=True)
email = models.EmailField(blank=True,null=True)
name= models.CharField( max_length=100,blank=True,null=True)




