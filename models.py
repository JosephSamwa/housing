from django.db import models
from django.conf import settings

class Property(models.Model):
    PROPERTY_TYPES = (
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
    )
    
    title = models.CharField(max_length=200)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    square_footage = models.IntegerField()
    address = models.CharField(max_length=200)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    available_from = models.DateField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cover_image = models.ImageField(upload_to='property_covers/', blank=True, null=True)

    def __str__(self):
        return self.title

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='property_images/')
    
    def __str__(self):
        return f"Image for {self.property.title}"

class PropertyVideo(models.Model):
    property = models.ForeignKey(Property, related_name='videos', on_delete=models.CASCADE)
    video = models.FileField(upload_to='property_videos/')
    
    def __str__(self):
        return f"Video for {self.property.title}"

class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_complaint = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.user.username} about {self.property.title}"

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)
    is_simulated = models.BooleanField(default=False)
    mpesa_request_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{'Simulated ' if self.is_simulated else ''}Payment of {self.amount} for {self.property.title}"