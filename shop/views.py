from django.shortcuts import render
from .models import Product , Contact , Order , OrderUpdate
from math import ceil
import json

# Create your views here
from django.http import HttpResponse


def index(request):
    allprods = []
    catprods = Product.objects.values('category','id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n= len(prod)
        Nslide =  n//4 + ceil(n/4 - n//4)
        allprods.append([prod,range(1,Nslide),Nslide])
    params = {'allprods':allprods}    
    return render(request, 'shop/index.html',params)

def searchMatch(query,item):
    query = query.lower()
    if query in item.description.lower() or query in item.product_name.lower() or query in item.category.lower() or query in item.sub_category.lower():
        return True
    return False

def search(request):
    query = request.GET.get('search')
    allprods = []
    catprods = Product.objects.values('category','id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query,item)]
        n= len(prod)
        Nslide =  n//4 + ceil(n/4 - n//4)
        if n != 0:
            allprods.append([prod,range(1,Nslide),Nslide])
    params = {'allprods':allprods,'msg':""}
    if len(allprods)==0 or len(query)<3:
        params = {'msg':"Please make sure to enter a relevant search query"}
    return render(request, 'shop/search.html',params)



def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    thank = False
    if request.method=="POST":
        name = request.POST.get('name','')
        email = request.POST.get('email','')
        phone = request.POST.get('phone','')
        desc = request.POST.get('desc','')            
        contact = Contact(name=name,email=email,phone=phone,desc=desc)
        contact.save()
        thank = True
    return render(request, 'shop/contact.html',{'thank':thank})





def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Order.objects.filter(order_id=orderId, email=email)
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


def productview(request,myid):
    #fetch the product using id
    product = Product.objects.filter(id = myid)
    return render(request, 'shop/productview.html',{'product': product[0]})


def checkout(request):
    if request.method=="POST":    
        items_json = request.POST.get('itemsjson','')
        name = request.POST.get('name','')
        amount =  request.POST.get('amount','')
        email = request.POST.get('email','')
        address = request.POST.get('address1','') + " " + request.POST.get('address1','')
        city = request.POST.get('city','')
        state = request.POST.get('state','')
        zip_code = request.POST.get('zip_code','')        
        phone = request.POST.get('phone','')

        order = Order(items_json=items_json,name=name,amount=amount,email=email,address=address,city=city,state=state,zip_code=zip_code, phone=phone,)
        order.save()

        update = OrderUpdate(order_id=order.order_id,update_desc="The order is placed")
        update.save()
        thank = True    
        return render(request, 'shop/checkout.html',{'thank': thank})

    return render(request, 'shop/checkout.html')

