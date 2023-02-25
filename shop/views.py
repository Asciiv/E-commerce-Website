from django.shortcuts import render
from .models import Product
from math import ceil

from django.http import HttpResponse
# Create your views here.

def index(request):
    products = Product.objects.all()
    print(products)
    n = len(products)
    nSlides = n//4 + ceil((n/4)-(n//4))
   # params = {'no_of_slides':nSlides,'range':range(1,nSlides),'product': products}
    allProds = [[products, range(1,nSlides), nSlides],
               [products, range(1,nSlides), nSlides]]
           
    params= {'allProds':allProds}
    return render (request, 'shop/index.html', params)
def about(request):
    return render (request, 'shop/about.html')
def contact(request):
    return HttpResponse ('We are at contact page')
def tracker(request):
    return HttpResponse ('We are at tracker page')
def search(request):
    return HttpResponse ('We are at Search page')
def productview(request):
    return HttpResponse ('We are at View page')
def checkout(request):
    return HttpResponse ('We are at  Checkout page')

    