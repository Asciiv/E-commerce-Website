from django.shortcuts import render,redirect
from .models import Product, Contact, Orders, OrderUpdate
from django.http import HttpResponse
from math import ceil
import json
from QuickzyKart import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
# Create your views here.
from django.http import HttpResponse
import razorpay
razorpay_client = razorpay.Client(auth=(settings.razorpay_id,settings.razorpay_account_id))
def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds':allProds}
    return render(request, 'shop/index.html', params)

def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query)<4:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'shop/search.html', params)


def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    thank = False
    if request.method=="POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
    return render(request, 'shop/contact.html', {'thank': thank})


def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'shop/tracker.html')

def productView(request, myid):

    # Fetch the product using the id
    product = Product.objects.filter(id=myid)
    return render(request, 'shop/prodView.html', {'product':product[0]})


def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/user/login')
    else:
        return render(request, 'shop/checkout.html')

def app_create(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order_amount = int(request.POST.get('formprice', ''))
        order_currency = 'INR'
        order_receipt = 'order_rcptid_11'
        notes = {'Shipping address': address}
        razorpay_order = razorpay_client.order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt, notes=notes, payment_capture='0'))
        print(razorpay_order['id'])
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city, state=state, zip_code=zip_code, phone=phone, amount=order_amount, razorpay_order_id=razorpay_order['id'])
        order.save()
        return render(request, 'shop/payment.html', {'order_id': razorpay_order['id'], 'cname': name, 'cemail': email, 'cphone': phone})


@csrf_exempt
def app_charge(request):
    if request.method == "POST":
        try:
            razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            razorpay_signature = request.POST.get('razorpay_signature', '')

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            order_db = Orders.objects.filter(razorpayid=razorpay_order_id).first()

            # verify the payment signature
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            # capture the payment
            razorpay_client.payment.capture(razorpay_payment_id, order_db.amount * 100)

            # update the order in the database
            order_db.paymentstatus = "PAID"
            order_db.amountpaid = order_db.amount
            order_db.save()

            # create a new OrderUpdate object to track the order status
            update = OrderUpdate(order_id=order_db.order_id, update_desc="the order has been placed")
            update.save()

            print("Payment Successful")

            # define the response dictionary
            response = {
                'status': 'success',
                'order_id': order_db.order_id,
                'payment_id': razorpay_payment_id,
                'amount': order_db.amount,
                'currency': 'INR',
                'method': 'Razorpay',
                'error_code': None,
                'error_description': None
            }

            return render(request, 'shop/paymentstatus.html', {'response': response})
        except Exception as e:
            print(str(e))

            # define the response dictionary
            response = {
                'status': 'failure',
                'order_id': None,
                'payment_id': None,
                'amount': None,
                'currency': None,
                'method': 'Razorpay',
                'error_code': str(e),
                'error_description': 'Payment Failed'
            }

            return render(request, 'shop/paymentstatus.html', {'response': response})
    else:
        return HttpResponse("Invalid Request")

def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/auth/logins')
    currentuser=request.user.username
    items=Orders.objects.filter(email=currentuser)
    rid=""
    for i in items:
        print(i.oid)
        # print(i.order_id)
        myid=i.oid
        rid=myid.replace("ShopyCart","")
        print(rid)
    status=OrderUpdate.objects.filter(order_id=int(rid))
    for j in status:
        print(j.update_desc)

   
    context ={"items":items,"status":status}
    # print(currentuser)
    return render(request,"shop/profile.html",context)


