# Uncomment the imports before you add the code
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'
urlpatterns = [
    # path for registration
    path(route='registration', view=views.registration, name='registration'),

    # path for login
    path(route='login', view=views.login_user, name='login'),

    # path for logout
    path(route='logout', view=views.logout_request, name='logout'),

    # path for get_cars (ADDED from previous step)
    path(route='get_cars', view=views.get_cars, name='getcars'),
    
    # path for dealer reviews view (Placeholder for future lab steps)
    # path(route='reviews/dealer/<int:dealer_id>', view=views.get_dealer_reviews, name='dealer_details'),

    # path for add a review view (Placeholder for future lab steps)
    # path(route='add_review', view=views.add_review, name='add_review'),
    
    # Add other paths like get_dealerships, get_dealer_details here in future steps

# Serve static files and media files (if needed) during development
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)