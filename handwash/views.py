

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
import requests
from .forms import ProductForm, UserRegistrationForm, ProfileUpdateForm
from .models import Product, Supplier
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Order,updateStockRequest
from django.db.models import F
from django.contrib.auth.models import User
from django.db.models import Case, When, BooleanField

from django.shortcuts import render
import google.generativeai as genai

def adminpage(request):
    products_at_reorder_level = Product.objects.filter(quantity__lte=F('reorderlevel'))
    product = Product.objects.annotate(
        is_approved=Case(
            When(updatestockrequest__is_approved=False, then=False),
            default=True,
            output_field=BooleanField()
        )
    )
    requested_stock_updates = updateStockRequest.objects.all()
    context = {
        'products_at_reorder_level': products_at_reorder_level,
        'productdata': product,
        'requested_stock_updates': requested_stock_updates
    }
    
    return render(request, 'user.html', context)

def admin_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_superuser:
                login(request, user)
                url="/adminpage/"
                x=f'''
                    <script>
                        alert("wlecome admin");
                        window.location.href = "{url}"; 
                    </script>
                '''
                
                return HttpResponse(x)
            
        else:
            form = AuthenticationForm()  
            error_message = 'Invalid credentials. Please try again.'
            return render(request, 'admin_login.html', {'form': form, 'error_message': error_message})
    
    else:
        form = AuthenticationForm()

    return render(request, 'admin_login.html', {'form': form})

def user_register(request):
    registration_successful = False

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            user.set_password(password)  
            user.save() 
            login(request, user) 
            registration_successful = True
            return redirect('user_login')
    else:
        form = UserRegistrationForm()

    return render(request, 'user_register.html', {'form': form, 'registration_successful': registration_successful})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'user_login.html', {'form': form})

def supplier_list(request):
    supplier = Supplier.objects.all()
    return render(request, 'supplier_details.html', {'supplier': supplier})

def user_logout(request):
    logout(request)
    # Redirect to the index page after logout

    return redirect('index')

# @login_required
# def profile_update(request):
#     # Get the UserProfile object for the current user or create it if it doesn't exist
#     profile, created = UserProfile.objects.get_or_create(username=request.user)

#     if request.method == 'POST':
#         form = UserProfileForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             return redirect('profile_update_success')  # Redirect to a success page
#     else:
#         form = UserProfileForm(instance=profile)
    
#     return render(request, 'profile_update.html', {'form': form})
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import make_password
from django.contrib import messages

@login_required
def profile_update(request):
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)
        if profile_form.is_valid() and password_form.is_valid():
            
            password_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('user_login')  # Redirect to the profile update page
    else:
        profile_form = ProfileUpdateForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)
    return render(request, 'profile_update.html', {'form': profile_form, 'password_form': password_form})

def admin_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            
            form.save()

            return redirect('adminpage')  # Redirect after adding a product
    else:
        form = ProductForm()

    return render(request, 'admin_add.html', {'form': form})

def index(request):   #user page product view
    products = Product.objects.all()
    if "category" in request.GET:
            category=request.GET.get("category")
            products=products.filter(category__exact=category)
    return render(request, 'index.html', {'productdata': products})

from django.urls import reverse



def product_list(request): #admin page product view
    products = Product.objects.all()
    return render(request, 'myapp/user.html', {'product': products})


def edit_product(request, product_id):
    product_to_edit = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product_to_edit)
        if form.is_valid():
            form.save()
            return redirect('adminpage')  # Redirect to the user page
    else:
        form = ProductForm(instance=product_to_edit)

    return render(request, 'edit_product.html', {'form': form, 'product': product_to_edit})



def delete_product(request, product_id):
    product_to_delete = get_object_or_404(Product, pk=product_id)  # Assuming product is the name of model

    if request.method == 'POST':
        confirmation = request.POST.get('confirmation', None)
        if confirmation == 'confirmed':
            #product_to_delete.is_active = False  # Set the product as inactive
            product_to_delete.delete()
            return redirect('adminpage')  # Redirect to the user page after deletion
        else:
            return redirect('adminpage')  # Redirect without deleting if not confirmed

    return render(request, 'confirmation_page.html', {'product': product_to_delete})
    

def search_view(request):
    query = request.GET.get('query')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = []
    return render(request, 'search_result.html', {'products': products, 'query': query})

# from requests import request
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def checkout_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_amount = sum(item.quantity * item.product.price for item in cart_items)

    if request.method == 'POST':
        # Retrieve form data
        fullname = request.POST.get('fullname')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')

        # Construct redirect URL with parameters
        redirect_url = reverse('order_summary')
        booked_items = Cart.objects.filter(user=request.user)
        print("booked")
        print(booked_items)
        params = {
            'fullname': fullname,
            'address': address,
            'city': city,
            'postal_code': postal_code,
            'total_amount': total_amount,
            'booked_items': booked_items,
        }

        redirect_url += '?' + '&'.join([f"{key}={value}" for key, value in params.items()])
        
        # Send email confirmation to the user
        subject = 'Order Confirmation'
        message = render_to_string('order_confirmation_email.html', {
            'fullname': fullname,
            'address': address,
            'city': city,
            'postal_code': postal_code,
            'total_amount': total_amount,
        })
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [request.user.email]
        send_mail(subject, message, email_from, recipient_list, html_message=message)
        
        return HttpResponse(pop_message(redirect_url, 'checkout done'))
        
    return render(request, 'checkout.html', {'total_amount': total_amount})

def order_summary_view(request):
    fullname = request.GET.get('fullname')
    address = request.GET.get('address')
    city = request.GET.get('city')
    postal_code = request.GET.get('postal_code')
    total_amount = request.GET.get('total_amount')
    print('asas')
    cart_product = Cart.objects.filter(user=request.user)

    print(cart_product)
    
    # product_ids = list(cart.keys())
    # qu=list(cart.values())
    
    # print(product_ids,qu)
    
    # cart_products = []

    # if product_ids:
    #     final=[]
    #     cart_products = Product.objects.filter(id__in=product_ids)
    #     for i,j in zip(cart_products,qu):
    #         print(i.name,j)
    #         final.append({'name':i.name,'quanity':j})

    print(cart_product)
    context = {
        'fullname': fullname,
        'address': address,
        'city': city,
        'postal_code': postal_code,
        'total_amount': total_amount,
        'cart_products': cart_product
        
    }

    order = Order.objects.create(
                user=request.user,
                fullname=fullname,
                address=address,
                city=city,
                postal_code=postal_code,
                total_amount=total_amount,
            )
            
            # Retrieve and clear cart items for the current user
    cart_items = Cart.objects.filter(user=request.user)
    for cart_item in cart_items:
        order.items.create(product=cart_item.product, quantity=cart_item.quantity)
    
    cart_item.delete()
            
    


    
    return render(request, 'order_summary.html', context)


from .models import Cart
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required(login_url=user_login)
def add_to_cart(request, product_id):

    product = Product.objects.get(pk=product_id)
    # print(isinstance(request.user,UserProfile)
    if request.method=='POST':
        if product.quantity > 0:
            cart_item = Cart(user=request.user, product=product, quantity=1)  # Adjust quantity as needed
            cart_item.save()
            # Decrease product quantity by 1
            product.quantity -= 1
            product.save()
            # Redirect to the cart page or product detail page
            return redirect('cart')  # Redirect to cart page or wherever you manage cart items
        else:
            # Handle out of stock case
            return render(request, 'out_of_stock.html', {'product': product})

def decrease_to_cart(request, product_id):
    cart_items = Cart.objects.filter(product_id=product_id,user=request.user).first()
    print('============')
    print("items",cart_items)

    cart_items.delete()
    return redirect('cart')




def remove_from_cart(request, product_id):
    print('--------')
    cart_items = Cart.objects.filter(product_id=product_id,user=request.user).all()
    print('============')
    print("items",cart_items)
    cart_items.delete()
    return redirect('cart')



# def cart(request):
#     cart = request.session.get('cart', {})
#     product_ids = list(cart.keys())

#     cart_items = []
#     total_amount = 0

#     if product_ids:
#         cart_products = Product.objects.filter(id__in=product_ids)
#         for cart_product in cart_products:
#             quantity = cart.get(str(cart_product.id), 0)
#             if quantity > 0:
#                 item_total = quantity * cart_product.price
#                 total_amount += item_total
#                 cart_items.append({
#                     'product': cart_product,
#                     'quantity': quantity,
#                     'item_total': item_total,
#                 })
    

#     return render(request, 'cart.html', {'cart_products': cart_items, 'total_amount': total_amount})

from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, Product

@login_required
def cart(request):
    upcart_items = Cart.objects.filter(user=request.user)
    
    
    # <QuerySet [<Cart: Cart for alvin: Apple VX max>, <Cart: Cart for alvin: Apple VX max>]>
    cart_items={}
    for item in upcart_items:
        # print(item.product.name)
        
        if item.product.name in cart_items:
            cart_items[item.product.name]['quantity']+=1
            cart_items[item.product.name]['total_price']+=cart_items[item.product.name]['price']
            
        else:
            cart_items[item.product.name]={
                'id':item.product.id,
                'name':item.product.name,
                'price':item.product.price,
                'quantity':item.quantity,
                'price':item.product.price,
                'total_price':item.product.price,
                'image':item.product.image
            }
            # print(cart_items)

    total_price = sum(item['total_price'] for item in cart_items.values())

    
    context= {
        'cart_items': cart_items,
        'total_price': total_price
        }
    
    return render(request, 'cart.html',context)
 
def product_detail(request, product_id):
    product = Product.objects.get(pk=product_id)
    if request.method == 'POST':
        # Handle adding product to cart
        if product.quantity > 0:
            # Decrement quantity and add to cart logic here
            product.quantity -= 1
            product.save()
            # Add to cart logic here
            return redirect('cart')  # Redirect to cart page after adding to cart
        else:
            # Product is out of stock, handle this case as needed
            return render(request, 'product_detail.html', {'product': product, 'message': 'Out of Stock'})
    else:
        return render(request, 'product_detail.html', {'product': product})
#wishlist
@login_required(login_url=user_login)
def add_to_wishlist(request, product_id):
    if 'wishlist' not in request.session:  
        request.session['wishlist'] = []  

    wishlist = request.session['wishlist'] 
    if product_id not in wishlist:  
        wishlist.append(product_id)
        request.session['wishlist'] = wishlist 
        message='Item added to your wishlist!'
    else:
        message='Item already in wishlist'

    url='/'
    return HttpResponse(pop_message(url,message))
#return HttpRespone
    
@login_required(login_url=user_login)
def remove_to_wishlist(request, product_id):
    wishlist = request.session['wishlist']   
    wishlist.remove(product_id)
    request.session['wishlist']=wishlist
    return redirect('index')





@login_required(login_url=user_login)
def view_to_wishlist(request):
    if 'wishlist' not in request.session:  
        context={
            'product':'',
        }
    else:
        wishlist = request.session['wishlist'] 
        data=Product.objects.filter(id__in=wishlist)
        
        context={
            'data':data
        }

    return render(request,'wishlist.html',context)



#custom popup message

def pop_message(url,message):
    url=url
    x=f'''
        <script>
            alert("{message}");
            window.location.href = "{url}"; 
        </script>
    '''
    return(x)



@login_required
def admin_order_view(request):
    # Admin view to display all orders
    orders = Order.objects.all()
    context = {'orders': orders}
    return render(request, 'order_list_and_detail.html', context)

@login_required
def order_detail_view(request, order_id):
    # Admin view to display order details
    order = Order.objects.get(id=order_id)
    items = order.items.all()
    context = {'order': order, 'items': items}
    return render(request, 'order_detail.html', context)

@login_required
def update_status(request, order_id):
    # Update order status view
    if request.method == 'POST':
        new_status = request.POST.get('status')
        try:
            order = Order.objects.get(pk=order_id)
            order.status = new_status
            order.save()
            messages.success(request, 'Order status updated successfully.')
        except Order.DoesNotExist:
            messages.error(request, 'Order not found.')
    return redirect('order_list_and_detail')  # Redirect to orders list
def order_list_and_detail(request):
    orders = Order.objects.all()
    context = {'orders': orders}
    return render(request, 'order_list_and_detail.html', context)

@login_required
def user_order_view(request):
    # Admin view to display all orders
    orders = Order.objects.filter(user=request.user).all()
    context = {'orders': orders}
    return render(request, 'order_list_and_detail.html', context)



def supplier_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = Supplier.objects.filter(username=username, password=password).first()
        if user is not None:
            login(request, user)

            return redirect('supplier_dashboard')
        else:
            return render(request, 'supplier_login.html', {'error': 'Invalid credentials'})
    else:
        return render(request, 'supplier_login.html')

def supplier_index(request):
    products = Product.objects.annotate(
        is_approved=Case(
            When(updatestockrequest__is_approved=False, then=False),
            default=True,
            output_field=BooleanField()
        )
    )
    return render(request, 'supplier.html', {'productdata':products})

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def updateStock(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = Product.objects.get(pk=product_id)
        new_quantity = int(request.POST.get('new_quantity'))
        product.quantity += new_quantity
        product.save()
        reset_stock_requests = updateStockRequest.objects.filter(product=product)
        reset_stock_requests.delete()
        return redirect('supplier_dashboard')
    return render(request, 'supplier.html')

    
def sendStockUpdateRequest(request, product_id):
    product = Product.objects.get(pk=product_id)
    request = updateStockRequest.objects.create(product=product)
    return redirect('adminpage')


# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.contrib import messages
from .helpers import send_forget_password_mail

def request_password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            userid=user.id
            token = get_random_string(length=32)
            user.reset_token = token
            user.save()
            send_forget_password_mail(email, token,userid)
            messages.success(request, 'Password reset link has been sent to your email.')
            return redirect('request_password_reset')
        else:
            messages.error(request, 'No user with this email exists.')
            return redirect('request_password_reset')
    return render(request, 'request_password_reset.html')


from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages

def reset_password(request, token, userid):
    # Decode the user ID from the token
    user = User.objects.get(pk=userid)
    
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been reset successfully.')
            return redirect('user_login')  # Redirect to login page after password reset
    else:
        form = SetPasswordForm(user)

    return render(request, 'reset_password.html', {'form': form})


# Configure Gemini API with your API key
genai.configure(api_key="AIzaSyAEpxEaoSLL6Z6gBM3Ha0edMAECjW6h61g")

def furniture_recommendation(request):
    recommendation = None
    material = furniture_type = room_type = color = budget = None

    if request.method == "POST":
        material = request.POST['material']
        furniture_type = request.POST['furniture_type']
        room_type = request.POST['room_type']
        color = request.POST['color']
        budget = request.POST['budget']

        # Define the prompt to send to the Gemini API
        user_input = f"""
        Material: {material}
        Furniture Type: {furniture_type}
        Room Type: {room_type}
        Color: {color}
        Budget: {budget}
        """

        # Call the Gemini model
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(user_input)
        
        recommendation = response.text  # Fetch the recommendation result

        # Redirect to the recommendation result page
        return render(request, 'recommendation_result.html', {
            'material': material,
            'furniture_type': furniture_type,
            'room_type': room_type,
            'color': color,
            'budget': budget,
            'recommendation': recommendation
        })
    
    return render(request, 'furniture_recommendation.html')


#views for visualization
import matplotlib.pyplot as plt
from django.shortcuts import render, redirect
from io import BytesIO
import base64
from .forms import RecommendationForm
from .models import FurnitureRecommendation
from django.db import models

def visualization_result(request):
    if request.method == "POST":
        form = RecommendationForm(request.POST)
        
        if form.is_valid():
            # Extract cleaned data
            material = form.cleaned_data['material']
            furniture_type = form.cleaned_data['furniture_type']
            room_type = form.cleaned_data['room_type']
            color = form.cleaned_data['color']
            budget = form.cleaned_data['budget']
            
            # Calculate recommendations_count
            recommendations_count = FurnitureRecommendation.objects.filter(material=material).count() + 1
            
            # Save the recommendation
            recommendation = FurnitureRecommendation(
                material=material,
                furniture_type=furniture_type,
                room_type=room_type,
                color=color,
                budget=budget,
                recommendations_count=recommendations_count
            )
            recommendation.save()

            # Redirect to the recommendation results page
            return redirect('recommendation_results')
    else:
        form = RecommendationForm()
    
    return render(request, 'visualization_result.html', {
        'form': form
    })

def recommendation_results(request):
    # Fetch all recommendations for the results page
    recommendations = FurnitureRecommendation.objects.all()

    # Data for the visualization (example: distribution of recommendations by material)
    recommendations_by_material = FurnitureRecommendation.objects.values('material').annotate(count=models.Count('id'))
    
    # Create bar chart
    materials = [item['material'] for item in recommendations_by_material]
    counts = [item['count'] for item in recommendations_by_material]
    
    plt.figure(figsize=(6, 4))
    plt.bar(materials, counts, color='green')
    plt.xlabel('Material')
    plt.ylabel('Number of Recommendations')
    plt.title('Recommendations by Material')
    
    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    # Convert the image to base64 for embedding in HTML
    graphic = base64.b64encode(image_png).decode('utf-8')

    return render(request, 'recommendation_results.html', {
        'recommendations': recommendations,
        'graphic': graphic
    })

#csv and pdf
import csv
from django.http import HttpResponse
from .models import FurnitureRecommendation

def download_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="recommendations.csv"'

    writer = csv.writer(response)
    # Write the header
    writer.writerow(['Furniture Type', 'Material', 'Room Type', 'Color', 'Budget'])

    # Write data
    recommendations = FurnitureRecommendation.objects.all().values_list(
        'furniture_type', 'material', 'room_type', 'color', 'budget')
    for recommendation in recommendations:
        writer.writerow(recommendation)

    return response


#pdf
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .models import FurnitureRecommendation

def download_pdf(request):
    # Create the HttpResponse object with the appropriate PDF header.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="recommendations.pdf"'

    # Create a PDF object
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Add Title to the PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, "Furniture Recommendations")

    # Fetch the recommendations from the database
    recommendations = FurnitureRecommendation.objects.all()

    # Set font for the table content
    p.setFont("Helvetica", 12)

    # Write the table headers
    p.drawString(100, height - 80, "Furniture Type | Material | Room Type | Color | Budget")

    y = height - 100  # Initial Y position for data rows
    for recommendation in recommendations:
        data = f"{recommendation.furniture_type} | {recommendation.material} | {recommendation.room_type} | {recommendation.color} | {recommendation.budget}"
        p.drawString(100, y, data)
        y -= 20  # Move Y position down for the next row

    # Close the PDF object
    p.showPage()
    p.save()

    return response




#chatbot
#chatbot
import os
from django.http import JsonResponse
from django.shortcuts import render
import google.generativeai as genai

# Configure Google Gemini API
api_key = "AIzaSyCHQUGXY0ao4gikIjraxw-dT2vMxpb9qko"  # Use your provided API key directly for testing; for production, consider using environment variables
genai.configure(api_key=api_key)

# Configure the model for shorter responses
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 100,  # Limit response length
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

def chatbot_view(request):
    if request.method == "POST":
        user_input = request.POST.get("user_input")

        if not user_input:
            return JsonResponse({"error": "No input provided"}, status=400)

        # Modify user input to request short answers
        prompt = f"{user_input}. Please give a short and concise answer."

        # Initialize chat session
        chat_session = model.start_chat()

        # Send message and get response
        response = chat_session.send_message(prompt)
        chatbot_response = response.text

        return JsonResponse({"response": chatbot_response})

    return render(request, "chatbot.html")  # Render chatbot UI
