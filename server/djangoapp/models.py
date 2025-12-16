from django.db import models
from django.utils.timezone import now
from django.core.validators import MaxValueValidator, MinValueValidator

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
class CarMake(models.Model):
    """
    Represents the manufacturer/make of a car (e.g., Ford, Toyota).
    """
    # Name of the car make
    name = models.CharField(max_length=100)
    
    # A brief description of the car make
    description = models.TextField()
    
    # Optional: Add a field for the country of origin
    country = models.CharField(max_length=50, default="USA") 

    # __str__ method to print a car make object
    def __str__(self):
        return self.name

# Define choices for the car type
CAR_TYPES = [
    ('SEDAN', 'Sedan'),
    ('SUV', 'SUV'),
    ('WAGON', 'Wagon'),
    ('TRUCK', 'Truck'),
    ('COUPE', 'Coupe'),
    ('HATCHBACK', 'Hatchback'),
]

# <HINT> Create a Car Model model `class CarModel(models.Model):`:
class CarModel(models.Model):
    """
    Represents a specific model of a car (e.g., Camry, F-150).
    """
    # Many-To-One relationship to Car Make model
    # One Car Make can have many Car Models. If the make is deleted, 
    # the model records are also deleted (models.CASCADE).
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    
    # Name of the specific car model
    name = models.CharField(max_length=100)
    
    # Type of car using predefined choices
    type = models.CharField(
        max_length=10, 
        choices=CAR_TYPES, 
        default='SUV'
    )
    
    # Year (IntegerField) with min and max value constraints
    year = models.IntegerField(
        default=2023,
        validators=[
            MinValueValidator(2015),
            MaxValueValidator(2023)
        ]
    )
    
    # Optional: Retail price of the car
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    # Optional: Date the model was added to the database
    added_date = models.DateTimeField(default=now)

    # __str__ method to print the car make and car model object
    def __str__(self):
        # Accessing the related CarMake's name for a readable output
        return f"{self.car_make.name} - {self.name} ({self.year})"