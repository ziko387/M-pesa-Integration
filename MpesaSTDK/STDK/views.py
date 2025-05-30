from http.client import responses
from os import  times
import requests
from django.db.models.expressions import result
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from pyexpat.errors import messages

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
    if request.method =='POST':
#        capture the form inputs
        phone= request.POST.get('phone')
        amount=request.POST.get('amount')
        name=request.POST.get('name')
        email=request.POST.get('email')
        transaction=Transaction.objects.create(
            phone_number=phone,
            amount=amount,
            status='pending',
            name=name,
            email=email,
        )
#         sending an stk push  to mpesa via daraja api
        access_token= generate_access_token()
        print(access_token)
        stk_url= f'{BASE_URL}/mpesa/stkpush/v1/processrequest'
        headers={'Authorization': f'Bearer {access_token}',
                 'content-type': 'application/json'}
        timestamp=datetime.now().strftime('%Y%m%d%H%M%S')
        password=base64.b64decode(
            f'{SHORTCODE}{PASSKEY}{timestamp}'.encode()
        ).decode()
        print(stk_url)
        print(password)
        print(timestamp)
        payload={
            "BusinessShortCode": SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "partyA": phone,
            "partyB": SHORTCODE,
            "phoneNumber": phone,
            "CallbackUrl": f"{NGROK_URL}/callback",
            "AccountReference": f"Transaction_{transaction.transaction_id}",
            "TransactionDesc":"Payment Request",
        }
        responses= requests.post(stk_url,headers=headers,json=payload)
        print('responses',responses)
        responses_data=responses.json()
        print(responses_data)

        transaction_id=responses_data.get('CheckoutRequestId',None)
        transaction.transaction_id=transaction_id
        transaction.description=responses_data.get('ResposeDescription','no description')
        transaction.save()

        return redirect('waiting',transaction_id=transaction_id)
    return JsonResponse({'error':'invalid request',},status=400)



def waiting(request,transaction_id):
    transaction=Transaction.objects.get(id=transaction_id)
    return render(request,'waiting.html',
                  {'transaction_id':transaction_id})

## callback METHOD
@csrf_exempt
def callback(request):
    if request.method =='POST':
        try:
           data=json.loads(request.body)
           print('received callback data',data)
           stk_callback=data.get('Body',{}).get('stkCallback',{})
           result_code=stk_callback.get('ResultCode',None)
           result_desc=stk_callback.get('ResultDesc','')
           transaction_id=stk_callback.get('CheckoutRequestId',None)
           print("callback result")
           print(transaction_id,result_code)
           if transaction_id:
               transaction= Transaction.objects.get(id=transaction_id)
               print("current transaction in db",transaction)
               if transaction:
                   if result_code == 0:
                       callback_metadata= (stk_callback.get('CallbackMetadata',{})
                                           .get('Item',[]))
                       receipt_number =next((item.get('value')
                                             for item in callback_metadata
                                                 if item.get('name') == 'MpesaReceiptNumber'),
                                             None)
                       amount=next((item.get('value')
                                   for item in callback_metadata
                                    if item.get('name') == 'Amount'),
                                   None)
                       transaction_date_str= next((item.get('value')
                                                   for item in callback_metadata
                                                   if item.get('name') == 'TransactionDate'),
                                                  None)
                       #cleaning transaction date
                       transaction_date=None
                       if transaction_date_str:
                           transaction_date=datetime.strptime(str(transaction_date_str),'%Y%m%d%H%M%S')
                       #update our transaction
                       transaction.mpesa_receipt_number=receipt_number
                       transaction.transaction_date=transaction_date
                       transaction.amount=amount
                       transaction.description='payment successful'
                       transaction.save()
                       print(f"transaction update{transaction_id}- {transaction.status}")

                       #send email to the user
                       if transaction.email:
                           subject="payment Receipt"
                           message=(
                               f"Dear{transaction.name},\n\n"
                               f"thanks for your payment{transaction.amount}"
                               f"for confirmation receipt is{transaction.mpesa_receipt_number}"
                           )
                           send_mail(subject,message,"mwangiian973@gmail.com",[transaction.email],fail_silently=False)
                           print("payment receipt received via email")

                   elif result_code == 1:
                       transaction.status = 'failed'
                       transaction.description= result_desc
                       transaction.save()
                       print(f"transaction failed{transaction_id}")
                   elif result_code == 1032:
                       transaction.status = 'cancelled'
                       transaction.description= "cancelled"
                       transaction.save()
                       print(f"transaction cancelled{transaction.transaction_id}")
           return JsonResponse({'message':'callback received',},status=200)

        except Exception as e:
            print(f"Error is from callback: {e}")
            return JsonResponse({'error':'Error is from callback: {e}',},status=500)
    return JsonResponse({'error':'invalid request method',},status=400)

## check status will enable us to track the status of the transaction
def check_status(request,transaction_id):
    pass
def payment_success(request):
    return render(request,'payment_successful.html')
def payment_failed(request):
    return render(request,'payment_failed.html')
def payment_cancelled(request):
    return render(request,'payment_cancelled.html')


