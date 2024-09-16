# Uncomment the required imports before adding the code

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
#from .restapis import get_request, analyze_review_sentiments, post_review
from .models import CarMake, CarModel
from .populate import initiate
import logging
import json

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
    logout(request)
    data = {"userName":""}
    return JsonResponse(data)
# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    context = {}

    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    email_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,password=password, email=email)
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName":username,"status":"Authenticated"}
        return JsonResponse(data)
    else :
        data = {"userName":username,"error":"Already Registered"}
        return JsonResponse(data)


# Fetch and return car models
def get_cars(request):
    count = CarMake.objects.count()
    if count == 0:
        initiate()
    
    car_models = CarModel.objects.select_related('car_make')
    cars = [{"CarModel": car_model.name, "CarMake": car_model.car_make.name} for car_model in car_models]
    return JsonResponse({"CarModels": cars})

# Fetch and return list of dealerships (all by default or particular state if state is passed)
# def get_dealerships(request, state="All"):
#     if state == "All":
#         endpoint = "/fetchDealers"
#     else:
#         endpoint = f"/fetchDealers/{state}"
    
#     dealerships = get_request(endpoint)
#     return JsonResponse({"status": 200, "dealers": dealerships})

# # Fetch and return details of a dealer by dealer_id
# def get_dealer_details(request, dealer_id):
#     endpoint = f"/fetchDealer/{dealer_id}"
#     dealer_details = get_request(endpoint)
    
#     if dealer_details:
#         return JsonResponse({"status": 200, "dealer": dealer_details})
#     else:
#         return JsonResponse({"status": 404, "message": "Dealer not found"})

# # Fetch and return reviews for a dealer by dealer_id, also perform sentiment analysis
# def get_dealer_reviews(request, dealer_id):
#     endpoint = f"/fetchReviews/dealer/{dealer_id}"
#     reviews = get_request(endpoint)
    
#     if not reviews:
#         return JsonResponse({"status": 404, "message": "No reviews found"})
    
#     # Analyze sentiment of each review
#     for review in reviews:
#         sentiment = analyze_review_sentiments(review.get('review'))
#         review['sentiment'] = sentiment
    
#     return JsonResponse({"status": 200, "reviews": reviews})

# # Create a view to handle review posting
# @csrf_exempt
# def add_review(request):
#     if request.method == 'POST':
#         # Ensure the user is authenticated
#         if not request.user.is_anonymous:
#             try:
#                 # Parse review data from the request
#                 data = json.loads(request.body)
#                 response = post_review(data)
                
#                 if response:
#                     return JsonResponse({"status": 200, "message": "Review added successfully"})
#                 else:
#                     return JsonResponse({"status": 400, "message": "Error in posting review"})
#             except Exception as e:
#                 return JsonResponse({"status": 401, "message": f"Invalid data format: {str(e)}"})
#         else:
#             return JsonResponse({"status": 403, "message": "Unauthorized"})
#     else:
#         return JsonResponse({"status": 405, "message": "Method not allowed"})
