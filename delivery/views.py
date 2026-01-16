from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import logout

from .models import Cart, Item, Restaurant, User

# Create your views here.
def index(request):
    return render(request, "index.html")

def open_signup(request):
    return render(request, "signup.html")

def open_signin(request):
    return render(request, "signin.html")

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        address = request.POST.get('address')

        if User.objects.filter(email=email).exists():
            messages.error(request, "This Email is already Registered")
            return render(request, 'signup.html')
        
        if User.objects.filter(mobile=mobile).exists():
            messages.error(request, "This Mobile no. is already Registered")
            return render(request, 'signup.html')
        
        user = User(username=username, 
                    password=password, 
                    mobile=mobile, 
                    email=email, 
                    address=address)
        user.save()
        messages.success(request, "Signup successful. Please login.")
        return redirect('signin')
    
    return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Please fill Username and Password")
            return render(request, 'signin.html')

        try:
            User.objects.get(username=username, password=password)

            if username == 'admin':
                return render(request, 'admin_home.html')
            else:
                restaurantList = Restaurant.objects.all()
                return render(
                    request,
                    'customer_home.html',
                    {
                        "restaurantList": restaurantList,
                        "username": username
                    }
                )

        except User.DoesNotExist:
            messages.error(request, "Invalid Username or Password")
            return render(request, 'signin.html')

    return render(request, 'signin.html')


def open_add_restaurant(request):
    return render(request, 'add_restaurant.html')


def add_restaurant(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')

        if Restaurant.objects.filter(name = name).exists(): 
            messages.error(request, "❌ Restaurant already exists!")
        else:
            Restaurant.objects.create(
                name = name,
                picture = picture,
                cuisine = cuisine,
                rating = rating,
            )
            messages.success(request, "✅ Item added successfully!")
        return render(request, 'admin_home.html') 

def open_show_restaurants(request):
    restaurantList = Restaurant.objects.all()
    return render(request, 'show_restaurants.html', {"restaurantList": restaurantList})


def open_update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    itemList = restaurant.items.all()
    return render(request, 'update_menu.html', {"itemList" : itemList, "restaurant" : restaurant})



def update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    itemList = restaurant.items.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        vegeterian = request.POST.get('vegeterian') == 'on'
        picture = request.POST.get('picture')
        if Item.objects.filter(name=name, restaurant=restaurant).exists():
            messages.error(request, "❌ Item already exists!")
        else:
            Item.objects.create(
                restaurant=restaurant,
                name=name,
                description=description,
                price=price,
                vegeterian=vegeterian,
                picture=picture,
            )
            messages.success(request, "✅ Item added successfully!")

        return redirect('update_menu', restaurant_id)
    
    return render(request, 'update_menu.html', {
        'restaurant': restaurant,
        'itemList': itemList
    })

def delete_item(request, item_id):
    item = Item.objects.get(id = item_id)
    restaurant_id = item.restaurant_id   # save before delete
    item.delete()
    return redirect('update_menu', restaurant_id)



def open_update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    return render(request, 'update_restaurant.html', {"restaurant" : restaurant})

def update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')

        restaurant.name = name
        restaurant.picture = picture
        restaurant.cuisine = cuisine
        restaurant.rating = rating

        restaurant.save()
    
    restaurantList = Restaurant.objects.all()
    return render(request, 'show_restaurants.html', {"restaurantList" : restaurantList})

def delete_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    restaurant.delete()
    restaurantList = Restaurant.objects.all()
    return render(request, 'show_restaurants.html', {"restaurantList" : restaurantList})


def view_menu(request, restaurant_id, username):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    itemList = restaurant.items.all()

    cart_count = 0
    try:
        user = User.objects.get(username=username)
        cart = Cart.objects.get(customer=user)
        cart_count = cart.items.count()
    except Cart.DoesNotExist:
        cart_count = 0

    return render(request, 'customer_menu.html',
                   {
                      "itemList" : itemList,
                      "restaurant" : restaurant,
                      "username" : username,
                      "cart_count": cart_count,
                   }
                )

def back(request):
    return render(request, 'admin_home.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def add_to_cart(request, item_id, username):
    item = Item.objects.get(id = item_id)
    customer = User.objects.get(username = username)
    cart, created = Cart.objects.get_or_create(customer = customer)

    cart.items.add(item)

    messages.success(request, "added to cart")

    restaurant_id = item.restaurant.id

    return redirect('view_menu', restaurant_id=restaurant_id, username=username)


def show_cart(request, username):
    customer = User.objects.get(username = username)
    cart = Cart.objects.filter(customer=customer).first()
    items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    return render(request, 'cart.html',{"itemList" : items, "total_price" : total_price, "username":username})



