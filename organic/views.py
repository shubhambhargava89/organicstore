from django import views
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.forms import Form
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from .models import Customer, Product, Cart, OrderPlaced, Feedback
from .forms import CustomerRegistrationForm, CustomerProfileForm, feedbackForm
from django.contrib import messages
from organic import models
from organic.models import Customer
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from .serializers import CustomerSerializer, OrderPlacedSerializer, ProductSerializer, CartSerializer
from rest_framework.parsers import JSONParser
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def customer(request):
    if request.method == "GET":
        regis = Customer.objects.all()
        print("students = ", regis)
        serializer = CustomerSerializer(regis, many=True)
        print("serializer = ", serializer.data)
        return JsonResponse(serializer.data, safe=False, status=200)
    return HttpResponse("success")


@csrf_exempt
def product(request):
    if request.method == "GET":
        regis = Product.objects.all()
        print("students = ", regis)
        serializer = ProductSerializer(regis, many=True)
        print("serializer = ", serializer.data)
        return JsonResponse(serializer.data, safe=False, status=200)
    return HttpResponse("success")


@csrf_exempt
def carts(request):
    if request.method == "GET":
        regis = Cart.objects.all()
        print("students = ", regis)
        serializer = CartSerializer(regis, many=True)
        print("serializer = ", serializer.data)
        return JsonResponse(serializer.data, safe=False, status=200)
    return HttpResponse("success")


@csrf_exempt
def orderplaced(request):
    if request.method == "GET":
        regis = OrderPlaced.objects.all()
        print("students = ", regis)
        serializer = OrderPlacedSerializer(regis, many=True)
        print("serializer = ", serializer.data)
        return JsonResponse(serializer.data, safe=False, status=200)
    # elif request.method == 'POST':
    #     data = JSONParser().parse(request)
    #     serializer = RegistraionSerializer(data=data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return JsonResponse(serializer.data, status=201)
    #     return JsonResponse(serializer.errors, status=400)
    return HttpResponse("success")


class ProductView(View):
    def get(self, request):
        totalitem = 0
        bodycare = Product.objects.filter(category='bc')
        vegetables = Product.objects.filter(category='ve')
        fruits = Product.objects.filter(category='fr')
        haircare = Product.objects.filter(category='hc')
        facecare = Product.objects.filter(category='fc')
        dryfruit = Product.objects.filter(category='df')
        flour = Product.objects.filter(category='fl')
        chocolate = Product.objects.filter(category='pc')
        protein = Product.objects.filter(category='pb')
        candy = Product.objects.filter(category='ca')
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'home.html',
                      {'bodycare': bodycare, 'haircare': haircare, 'vegetables': vegetables, 'fruits': fruits,
                       'totalitem': totalitem, 'facecare': facecare, 'dryfruit':dryfruit, 'flour': flour, 'chocolate': chocolate,
                       'protein':protein,'candy':candy})


class ProductDetailView(View):
    def get(self, request, pk):
        totalitem = 0
        product = Product.objects.get(pk=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
            if request.user.is_authenticated:
                totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'productdetail.html',
                      {'product': product, 'item_already_in_cart': item_already_in_cart, 'totalitem': totalitem})


@login_required
def add_to_cart(request):
    totalitem = 0
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return redirect('/cart', {'totalitem': totalitem})


def show_cart(request):
    if request.user.is_authenticated:
        totalitem = 0
        user = request.user
        cart = Cart.objects.filter(user=user)
        # print(cart)
        amount = 0.0
        shipping_amount = 70.0
        totalamount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        # print(cart_product)
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
                totalamount = amount + shipping_amount
            return render(request, 'addtocart.html', {'carts': cart, 'totalamount': totalamount, 'amount': amount,
                                                      'shipping_amount': shipping_amount, 'totalitem': totalitem})
        else:
            return render(request, 'emptycart.html')


def buy_now(request):
    return render(request, 'buynow.html')


def address(request):
    totalitem = 0
    add = Customer.objects.filter(user=request.user)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'address.html', {'add': add, 'active': 'btn-warning', 'totalitem': totalitem})


def orders(request):
    totalitem = 0
    op = OrderPlaced.objects.filter(user=request.user)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'orders.html', {'order_placed': op, 'totalitem': totalitem})


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'customerregistration.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Congratulations!! You are registered Successfully.')
        return render(request, 'customerregistration.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class Feedbacks(View):
    def get(self, request):
        form = feedbackForm()
        return render(request, 'feedback.html', {'form': form, 'active': 'btn-primary'})

    def post(self, request):
        form = feedbackForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            mobile = form.cleaned_data['mobile']
            city = form.cleaned_data['city']
            pincode = form.cleaned_data['pincode']
            state = form.cleaned_data['state']
            description = form.cleaned_data['description']
            reg = Feedback(name=name, mobile=mobile, city=city, pincode=pincode, state=state, description=description)
            reg.save()
            messages.success(request, 'Congratulations!! Feedback Submit Successfully.')
        return render(request, 'feedback.html', {'form': form, 'active': 'btn-primary'})


@login_required
def checkout(request):
    totalitem = 0
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 70.0
    totalamount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
    totalamount = amount + shipping_amount
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'checkout.html',
                  {'add': add, 'totalamount': totalamount, 'cart_items': cart_items, 'totalitem': totalitem})


def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
        c.delete()

    return redirect("orders")


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    totalitem = 0

    def get(self, request):
        form = CustomerProfileForm()
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'profile.html', {'form': form, 'active': 'btn-warning', 'totalitem': totalitem})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            mobile = form.cleaned_data['mobile']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr, name=name, mobile=mobile, locality=locality, city=city, state=state,
                           zipcode=zipcode)
            reg.save()
            messages.success(request, 'Profile Updated Successfully')
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'profile.html', {'form': form, 'active': 'btn-warning', 'totalitem': totalitem})


def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount
        }

        return JsonResponse(data)


def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount
        }

        return JsonResponse(data)


def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
            totalamount = amount

        data = {
            'amount': amount,
            'totalamount': amount + shipping_amount
        }

        return JsonResponse(data)


def bodycare(request, data=None):
    totalitem = 0
    if data == None:
        bodycare = Product.objects.filter(category='bc')
    elif data == 'below':
        bodycare = Product.objects.filter(category='bc').filter(discounted_price__lt=500)
    elif data == 'above':
        bodycare = Product.objects.filter(category='bc').filter(discounted_price__gt=500)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'bodycare.html', {'bodycare': bodycare, 'totalitem': totalitem})


def fruits(request, data=None):
    totalitem = 0
    if data == None:
        fruits = Product.objects.filter(category='fr')
    elif data == 'below':
        fruits = Product.objects.filter(category='fr').filter(discounted_price__lt=500)
    elif data == 'above':
        fruits = Product.objects.filter(category='fr').filter(discounted_price__gt=500)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'fruits.html', {'fruits': fruits, 'totalitem': totalitem})


def vegetables(request, data=None):
    totalitem = 0
    if data == None:
        vegetables = Product.objects.filter(category='ve')
    elif data == 'below':
        vegetables = Product.objects.filter(category='ve').filter(discounted_price__lt=500)
    elif data == 'above':
        vegetables = Product.objects.filter(category='ve').filter(discounted_price__gt=500)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'vegetables.html', {'vegetables': vegetables, 'totalitem': totalitem})


def haircare(request, data=None):
    totalitem = 0
    if data == None:
        haircare = Product.objects.filter(category='hc')
    elif data == 'below':
        haircare = Product.objects.filter(category='hc').filter(discounted_price__lt=500)
    elif data == 'above':
        haircare = Product.objects.filter(category='hc').filter(discounted_price__gt=500)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'haircare.html', {'haircare': haircare, 'totalitem': totalitem})


def facecare(request, data=None):
    totalitem = 0
    if data == None:
        facecare = Product.objects.filter(category='fc')
    elif data == 'below':
        facecare = Product.objects.filter(category='fc').filter(discounted_price__lt=500)
    elif data == 'above':
        facecare = Product.objects.filter(category='fc').filter(discounted_price__gt=500)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'facecare.html', {'facecare': facecare, 'totalitem': totalitem})


def flour(request, data=None):
    totalitem = 0
    if data == None:
        flour = Product.objects.filter(category='fl')
    elif data == 'below':
        flour = Product.objects.filter(category='fl').filter(discounted_price__lt=500)
    elif data == 'above':
        flour = Product.objects.filter(category='fl').filter(discounted_price__gt=500)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'flour.html', {'flour': flour, 'totalitem': totalitem})

def dryfruit(request, data=None):
    totalitem = 0
    if data == None:
        dryfruit = Product.objects.filter(category='df')
    elif data == 'below':
        dryfruit = Product.objects.filter(category='df').filter(discounted_price__lt=500)
    elif data == 'above':
        dryfruit = Product.objects.filter(category='df').filter(discounted_price__gt=500)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'dryfruit.html', {'dryfruit': dryfruit, 'totalitem': totalitem})

def chocolate(request, data=None):
    totalitem = 0
    if data == None:
        chocolate = Product.objects.filter(category='pc')
    elif data == 'below':
        chocolate = Product.objects.filter(category='pc').filter(discounted_price__lt=500)
    elif data == 'above':
        chocolate = Product.objects.filter(category='pc').filter(discounted_price__gt=500)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'chocolate.html', {'chocolate': chocolate, 'totalitem': totalitem})

def protein(request, data=None):
    totalitem = 0
    if data == None:
        protein = Product.objects.filter(category='pb')
    elif data == 'below':
        protein = Product.objects.filter(category='pb').filter(discounted_price__lt=500)
    elif data == 'above':
        protein = Product.objects.filter(category='pb').filter(discounted_price__gt=500)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'protein.html', {'protein': protein, 'totalitem': totalitem})

def candy(request, data=None):
    totalitem = 0
    if data == None:
        candy = Product.objects.filter(category='ca')
    elif data == 'below':
        candy = Product.objects.filter(category='ca').filter(discounted_price__lt=500)
    elif data == 'above':
        candy = Product.objects.filter(category='ca').filter(discounted_price__gt=500)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'candy.html', {'candy': candy, 'totalitem': totalitem})

def jam(request, data=None):
    totalitem = 0
    if data == None:
        jam = Product.objects.filter(category='ja')
    elif data == 'below':
        jam = Product.objects.filter(category='ja').filter(discounted_price__lt=500)
    elif data == 'above':
        jam = Product.objects.filter(category='ja').filter(discounted_price__gt=500)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'jam.html', {'jam': jam, 'totalitem': totalitem})

def peanut(request, data=None):
    totalitem = 0
    if data == None:
        peanut = Product.objects.filter(category='pe')
    elif data == 'below':
        peanut = Product.objects.filter(category='pe').filter(discounted_price__lt=500)
    elif data == 'above':
        peanut = Product.objects.filter(category='pe').filter(discounted_price__gt=500)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'peanut.html', {'peanut': peanut, 'totalitem': totalitem})

def pickle(request, data=None):
    totalitem = 0
    if data == None:
        pickle = Product.objects.filter(category='pi')
    elif data == 'below':
        pickle = Product.objects.filter(category='pi').filter(discounted_price__lt=500)
    elif data == 'above':
        pickle = Product.objects.filter(category='pi').filter(discounted_price__gt=500)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'pickle.html', {'pickle': pickle, 'totalitem': totalitem})

def chutney(request, data=None):
    totalitem = 0
    if data == None:
        chutney = Product.objects.filter(category='cp')
    elif data == 'below':
        chutney = Product.objects.filter(category='cp').filter(discounted_price__lt=500)
    elif data == 'above':
        chutney = Product.objects.filter(category='cp').filter(discounted_price__gt=500)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'chutney.html', {'chutney': chutney, 'totalitem': totalitem})

def soap(request, data=None):
    totalitem = 0
    if data == None:
        soap = Product.objects.filter(category='bs')
    elif data == 'below':
        soap = Product.objects.filter(category='bs').filter(discounted_price__lt=500)
    elif data == 'above':
        soap = Product.objects.filter(category='bs').filter(discounted_price__gt=500)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'soap.html', {'soap': soap, 'totalitem': totalitem})

def oil(request, data=None):
    totalitem = 0
    if data == None:
        oil = Product.objects.filter(category='bo')
    elif data == 'below':
        oil = Product.objects.filter(category='bo').filter(discounted_price__lt=500)
    elif data == 'above':
        oil = Product.objects.filter(category='bo').filter(discounted_price__gt=500)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'oil.html', {'oil': oil, 'totalitem': totalitem})

def food(request, data=None):
    totalitem = 0
    if data == None:
        food = Product.objects.filter(category='bf')
    elif data == 'below':
        food = Product.objects.filter(category='bf').filter(discounted_price__lt=500)
    elif data == 'above':
        food = Product.objects.filter(category='bf').filter(discounted_price__gt=500)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'food.html', {'food': food, 'totalitem': totalitem})