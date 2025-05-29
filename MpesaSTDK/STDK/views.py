from os import  times
import requests
from django.db.models.expressions import result
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from.models import Transaction
import base64
from datetime import datetime
import json
from django.core.mail import send_mail
from django.core.paginator import Paginator
from .utility import CONSUMER_KEY,CONSUMER_SECRET,BASE_NGROK_URL,BASE_URL,SHORTCODE,PASSKEY,NGROK_URL
# Create your views here.
##CREATING THE Mpesa PASSKEY
class MpesaPassword:
      @staticmethod
      def generate_security_credentials():
         timestamp=datetime.now().strftime('%Y%m%d%H%M%S')
         data_to_encode=SHORTCODE+timestamp+PASSKEY
         online_password=base64.b64encode(data_to_encode.encode()).decode()
         return online_password
# access token: security credentials provides from daraja mpesa to authorize tokens
def generate_access_token():
    auth_url=f'{BASE_URL}/oauth/v1/generate?grant_type=client_credentials'
    response=requests.post(auth_url,auth=(CONSUMER_KEY,CONSUMER_SECRET))
    result=response.json().get('access_token')
    print(result)
    return result

def index(request):
    return render(request,'index.html')
@csrf_exempt
def stk_push(request):
    pass
def waiting(request,transaction_id):
    transaction=Transaction.objects.get(id=transaction_id)
    return render(request,'waiting.html',
                  {'transaction_id':transaction_id})

## callback METHOD
@csrf_exempt
def callback(request):
    pass
## check status will enable us to track the status of the transaction
def check_status(request,transaction_id):
    pass
def payment_success(request):
    return render(request,'payment_successful.html')
def payment_failed(request):
    return render(request,'payment_failed.html')
def payment_cancelled(request):
    return render(request,'payment_cancelled.html')


