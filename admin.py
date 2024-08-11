from django.contrib import admin
from .models import Property, PropertyImage, PropertyVideo, Message, Payment

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1

class PropertyVideoInline(admin.TabularInline):
    model = PropertyVideo
    extra = 1

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_type', 'monthly_rent', 'is_available')
    list_filter = ('property_type', 'is_available')
    search_fields = ('title', 'address')
    inlines = [PropertyImageInline, PropertyVideoInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'property','created_at', 'message', 'is_complaint', 'is_read')
    list_filter = ('is_complaint', 'is_read')
    search_fields = ('user__username', 'property__title')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'amount', 'created_at', 'is_confirmed')
    list_filter = ('is_confirmed',)
    search_fields = ('user__username', 'property__title')
    actions = ['confirm_payment']

    def confirm_payment(self, request, queryset):
        for payment in queryset:
            payment.is_confirmed = True
            payment.property.is_available = False
            payment.property.save()
            payment.save()
        self.message_user(request, f"{queryset.count()} payment(s) confirmed and properties marked as unavailable.")
    confirm_payment.short_description = "Confirm selected payments and mark properties as unavailable"