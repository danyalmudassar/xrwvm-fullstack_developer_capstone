from django.contrib import admin
from .models import CarMake, CarModel # Import the models we created

# 1. CarModelInline class (for CarMakeAdmin)
# This allows CarModels to be added/edited directly from the CarMake admin page.
class CarModelInline(admin.TabularInline):
    """
    Allows editing CarModel objects inline on the CarMake change form.
    """
    model = CarModel
    # You can specify the number of empty forms to display for adding new models
    extra = 3 
    
# 2. CarModelAdmin class
class CarModelAdmin(admin.ModelAdmin):
    """
    Customizes the display and functionality for the CarModel in the admin.
    """
    # Fields to display in the main list view
    list_display = ('car_make', 'name', 'type', 'year', 'price') 
    
    # Fields to use for filtering the list
    list_filter = ('car_make', 'type', 'year')
    
    # Fields to include in the search bar
    search_fields = ('name', 'car_make__name') # You can search by model name or make name
    
    # Fields to use in the edit form (optional: specifies the order)
    fields = ('car_make', 'name', 'type', 'year', 'price', 'dealer_id') 

# 3. CarMakeAdmin class with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
    """
    Customizes the display and functionality for the CarMake in the admin.
    Includes CarModelInline for seamless related object management.
    """
    # Fields to display in the main list view
    list_display = ('name', 'description', 'country')
    
    # Fields to include in the search bar
    search_fields = ['name']
    
    # The key to linking CarModels to CarMake: include the inline class
    inlines = [CarModelInline]


# 4. Register models here
admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)