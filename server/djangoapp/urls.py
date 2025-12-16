# server/djangoapp/urls.py

from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'
urlpatterns = [
    # --- USER AUTHENTICATION ROUTES ---
    path(route='registration', view=views.registration, name='registration'),
    path(route='login', view=views.login_user, name='login'),
    path(route='logout', view=views.logout_request, name='logout'),

    # --- CAR INVENTORY (Django ORM) ---
    path(route='get_cars', view=views.get_cars, name='getcars'),
    
    # --- DEALERSHIP PROXY ROUTES (GET requests) ---
    # GET all dealers
    path(route='get_dealers', view=views.get_dealerships, name='get_dealers'),
    # GET dealers by state
    path(route='get_dealers/<str:state>', view=views.get_dealerships, name='get_dealers_by_state'),

    # GET dealer details by ID
    path(route='dealer/<int:dealer_id>', view=views.get_dealer_details, name='dealer_details'),

    # --- REVIEW PROXY ROUTES ---
    # GET reviews for a specific dealer (includes Sentiment Analysis)
    path(route='reviews/dealer/<int:dealer_id>', view=views.get_dealer_reviews, name='dealer_reviews'),
    
    # POST a new review
    path(route='add_review', view=views.add_review, name='add_review'),

# Serve static files and media files (if needed) during development
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)