# Uncomment the required imports before adding the code
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime
from django.db.models import F # Needed for ORM operations if used
from .models import CarMake, CarModel # Import the models for the get_cars view

# from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
# --- CRITICAL CHANGE: IMPORTING initiate FROM .populate ---
from .populate import initiate 


# Get an instance of a logger
logger = logging.getLogger(__name__)


# --- POPULATE FUNCTION ---
# The previous placeholder initiate() function has been REMOVED here
# and is now imported from .populate.py to be compliant with the lab structure.


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Use Django's built-in logout function
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)

# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']

    # Check if user already exists
    username_exist = False
    try:
        User.objects.get(username=username)
        username_exist = True
    except User.DoesNotExist:
        # If not, simply log the exception
        logger.debug(f"{username} is a new user.")

    # If user exists, return failure
    if username_exist:
        data = {"userName": username, "error": "Already Registered"}
        return JsonResponse(data)
    
    # Otherwise, create the user and login
    user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email)
    login(request, user)
    data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)


# --- NEWLY ADDED VIEW FOR CARS ---
def get_cars(request):
    """
    Fetches the list of all CarModels and their associated CarMakes.
    If the database is empty, it calls initiate() to populate it.
    """
    count = CarMake.objects.filter().count()
    print(f"Total Car Makes in DB: {count}")
    
    # This now calls the initiate function imported from populate.py
    if count == 0:
        initiate() 

    # Use select_related to efficiently fetch CarModel and its related CarMake in one query
    car_models = CarModel.objects.select_related('car_make').all()
    cars = []
    
    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name, 
            "CarMake": car_model.car_make.name,
            "Year": car_model.year,
            "Type": car_model.type
        })
        
    return JsonResponse({"CarModels": cars})


# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
# def get_dealerships(request):
#     # ... implementation goes here ...
#     pass

# Create a `get_dealer_reviews` view to render the reviews of a dealer
# def get_dealer_reviews(request,dealer_id):
#     # ... implementation goes here ...
#     pass

# Create a `get_dealer_details` view to render the dealer details
# def get_dealer_details(request, dealer_id):
#     # ... implementation goes here ...
#     pass

# Create a `add_review` view to submit a review
# def add_review(request):
#     # ... implementation goes here ...
#     pass