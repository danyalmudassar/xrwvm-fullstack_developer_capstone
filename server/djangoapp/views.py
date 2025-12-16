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

# --- CRITICAL IMPORTS ---
from .populate import initiate 
# Import all required restapi functions: 
from .restapis import get_request, get_dealers_from_api, get_dealer_reviews_from_api, analyze_review_sentiments, post_review 


# Get an instance of a logger
logger = logging.getLogger(__name__)


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


# --- VIEW FOR CARS ---
def get_cars(request):
    """
    Fetches the list of all CarModels and their associated CarMakes.
    If the database is empty, it calls initiate() to populate it.
    """
    count = CarMake.objects.filter().count()
    print(f"Total Car Makes in DB: {count}")
    
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


# --- PROXY VIEW: GET DEALERSHIPS ---
def get_dealerships(request, state="All"):
    """
    Proxy service view to fetch dealer data from the external backend API.
    Can filter by state or return all dealers.
    """
    if(state == "All"):
        endpoint = "/fetchDealers"
    else:
        # Note: The backend Express API must handle filtering via a path parameter
        endpoint = "/fetchDealers/"+state
        
    print(f"Fetching dealers from endpoint: {endpoint}")
    
    # Use the generic get_request function to fetch data from the external backend
    dealerships = get_request(endpoint)
    
    # Return the raw data directly to the client as JSON
    return JsonResponse({"status": 200, "dealers": dealerships})


# --- PROXY VIEW: GET DEALER DETAILS ---
def get_dealer_details(request, dealer_id):
    """
    Proxy service view to fetch details for a single dealer by ID.
    Uses /fetchDealer/<dealer_id> endpoint.
    """
    if(dealer_id):
        endpoint = "/fetchDealer/"+str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status":200,"dealer":dealership})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})


# --- PROXY VIEW: GET DEALER REVIEWS WITH SENTIMENT ANALYSIS ---
def get_dealer_reviews(request, dealer_id):
    """
    Proxy service view to fetch reviews for a dealer, then analyzes the sentiment 
    for each review using the external microservice.
    """
    # if dealer id has been provided
    if(dealer_id):
        endpoint = "/fetchReviews/dealer/"+str(dealer_id)
        # Fetch reviews (raw JSON list/dict)
        reviews = get_request(endpoint)
        
        # Check if reviews were successfully retrieved and is a list
        if reviews is not None and isinstance(reviews, list):
            for review_detail in reviews:
                # 1. Extract the review text
                review_text = review_detail.get('review', '')
                
                # 2. Call the sentiment microservice consumer
                response = analyze_review_sentiments(review_text)
                
                # 3. Extract the sentiment result
                print(f"Sentiment response for review: {response}")
                review_detail['sentiment'] = response.get('sentiment', 'N/A')
                
            return JsonResponse({"status":200,"reviews":reviews})
        else:
             # Handle case where reviews could not be fetched
            return JsonResponse({"status":404, "message":"Reviews not found for this dealer."})
    else:
        return JsonResponse({"status":400,"message":"Bad Request: Missing dealer ID"})


# --- PROXY VIEW: ADD REVIEW ---
@csrf_exempt
def add_review(request):
    """
    Proxy service view to submit a new review via a POST request to the external backend.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"status": 403, "message": "Unauthorized: User is not logged in"})
        
    if request.method == 'POST':
        try:
            # Load the JSON payload from the request body
            data = json.loads(request.body)
            print(f"Received review data: {data}")
            
            # Use the post_review utility function to send data to the backend
            response = post_review(data)
            
            if response.get("status") == "success":
                return JsonResponse({"status": 201, "message": "Review posted successfully"})
            else:
                # Return the error message provided by the post_review utility
                return JsonResponse({"status": 500, "message": f"Failed to post review: {response.get('message')}"})

        except json.JSONDecodeError:
            return JsonResponse({"status": 400, "message": "Invalid JSON format in request body"})
        except Exception as e:
            logger.error(f"Error posting review: {e}")
            return JsonResponse({"status": 500, "message": f"An unexpected error occurred: {str(e)}"})
    else:
        return JsonResponse({"status": 405, "message": "Method not allowed"})