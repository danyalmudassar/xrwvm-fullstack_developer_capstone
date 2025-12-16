import requests 
import os
import json
from dotenv import load_dotenv

# Import the external data models (assuming CarDealer and DealerReview are defined in .models)
from .models import CarDealer, DealerReview 

load_dotenv()

# --- Environment Configuration ---
backend_url = os.getenv(
    'backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="http://localhost:5050/")

# --- 1. Generic GET Request Handler ---
def get_request(endpoint, **kwargs):
    """
    Handles GET requests to the external backend API.
    Constructs the URL with query parameters and returns JSON data.
    """
    params = ""
    if(kwargs):
        # Manually construct query string: ?key1=value1&key2=value2&...
        for key,value in kwargs.items():
            params=params+key+"="+str(value)+"&" # Convert value to string for URL

    # Construct the full request URL
    # Note: We must strip the trailing '&' if present, and append the '?'
    request_url = backend_url + endpoint + "?" + params
    
    # Simple check to remove trailing '&' if it's the last character
    if request_url.endswith('&'):
        request_url = request_url[:-1]

    print("GET from {} ".format(request_url))
    
    try:
        # Call get method of requests library with the full URL
        response = requests.get(request_url)
        
        # Check for success status (200 OK)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Request failed with status code {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        # Handle all network-related errors (DNS failure, connection refused, timeout, etc.)
        print(f"Network exception occurred: {e}")
        return None
    except json.JSONDecodeError:
        # Handle case where response is not valid JSON
        print("Failed to decode JSON response")
        return None


# --- 2. Fetch Dealerships ---
def get_dealers_from_api(endpoint="/api/dealership"):
    """
    Fetches all dealerships from the external Express API and converts them 
    into a list of CarDealer objects.
    """
    json_result = get_request(endpoint)
    dealers = []

    if json_result:
        # Assuming the external API returns the list directly or under a specific key
        dealer_data = json_result if isinstance(json_result, list) else json_result.get("dealerships", [])
        
        # Iterate over API results and convert them to CarDealer objects
        for data in dealer_data:
            dealer = CarDealer(
                address=data.get("address"), city=data.get("city"), full_name=data.get("full_name"),
                id=data.get("id"), lat=data.get("lat"), long=data.get("long"), 
                st=data.get("st"), zip=data.get("zip")
            )
            dealers.append(dealer)
            
    return dealers


# --- 3. Fetch Dealer Reviews ---
def get_dealer_reviews_from_api(dealer_id):
    """
    Fetches reviews for a specific dealer from the external API (using dealerId).
    Returns a list of DealerReview objects.
    """
    # The API endpoint likely accepts dealerId as a query parameter
    json_result = get_request("/api/review", dealerId=dealer_id)
    reviews = []

    if json_result:
        # Assuming the API returns the list directly or under a specific key
        review_data = json_result if isinstance(json_result, list) else json_result.get("reviews", [])
        
        for data in review_data:
            review_obj = DealerReview(
                dealership=data.get("dealership"), name=data.get("name"), purchase=data.get("purchase"), 
                review=data.get("review"), purchase_date=data.get("purchase_date"), car_make=data.get("car_make"),
                car_model=data.get("car_model"), car_year=data.get("car_year"), 
                sentiment=data.get("sentiment", "N/A"), id=data.get("id", "N/A") 
            )
            reviews.append(review_obj)

    return reviews


# --- 4. Analyze Sentiment Microservice Consumer ---
def analyze_review_sentiments(text):
    """
    Calls the external Sentiment Analyzer microservice to get the sentiment for a given text.
    """
    # URL is constructed using the base URL from .env and the endpoint path
    request_url = sentiment_analyzer_url + "analyze/" + text
    
    print(f"GET from {request_url}")
    
    try:
        # Call get method of requests library with URL
        response = requests.get(request_url)
        
        # Check for success status (200 OK)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Sentiment Analyzer request failed with status code {response.status_code}")
            return {"sentiment": "N/A"} # Return a default structure on non-200 status
            
    except Exception as err:
        # Catch network or other general exceptions
        print(f"Unexpected {err=}, {type(err)=}")
        print("Network exception occurred")
        return {"sentiment": "N/A"} # Return a default structure on error


# --- 5. Post Review ---
def post_review(data_dict):
    """
    Handles POST requests for submitting a new review to the external backend API.
    """
    request_url = backend_url + "/api/review"
    print(f"POST to {request_url}")

    try:
        # Call post method of requests library with URL and JSON payload
        response = requests.post(request_url, json=data_dict)
    except Exception as e:
        print(f"Network exception occurred during POST: {e}")
        return {"error": "Network connection failed"}

    status_code = response.status_code
    print(f"With status {status_code}")

    if status_code in [201, 202]: # Typical success codes for POST/creation
        return {"status": "success", "data": response.json()}
    else:
        print(f"POST failed with status code {status_code}. Response: {response.text}")
        # Assuming the backend returns an error message in the JSON body if available
        try:
            return {"status": "error", "message": response.json()}
        except:
            return {"status": "error", "message": f"Failed with status code {status_code}"}