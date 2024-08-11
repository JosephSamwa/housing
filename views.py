import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Property, Message, Payment
from django.db.models import Q
from django.core.paginator import Paginator
from .mpesa_utils import get_mpesa_access_token, lipa_na_mpesa_online  
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@login_required
def property_list(request):
    properties = Property.objects.filter(is_available=True)
    property_types = Property.PROPERTY_TYPES

    # Apply filters
    search_query = request.GET.get('search')
    property_type = request.GET.get('property_type')
    min_bedrooms = request.GET.get('min_bedrooms')
    max_rent = request.GET.get('max_rent')

    if search_query:
        properties = properties.filter(Q(title__icontains=search_query) | Q(address__icontains=search_query))

    if property_type:
        properties = properties.filter(property_type=property_type)

    if min_bedrooms:
        properties = properties.filter(bedrooms__gte=int(min_bedrooms))

    if max_rent:
        properties = properties.filter(monthly_rent__lte=float(max_rent))

    # Pagination
    paginator = Paginator(properties, 9)  # Show 9 properties per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'properties': page_obj,
        'property_types': property_types,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }

    return render(request, 'properties/property_list.html', context)

def property_detail(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    return render(request, 'properties/property_detail.html', {'property': property})

@login_required
def send_message(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    if request.method == 'POST':
        message_text = request.POST.get('message')
        is_complaint = request.POST.get('is_complaint', False)
        Message.objects.create(
            user=request.user,
            property=property,
            message=message_text,
            is_complaint=is_complaint
        )
        messages.success(request, 'Your message has been sent.')
        return redirect('property_detail', property_id=property.id)
    return render(request, 'properties/send_message.html', {'property': property})

@login_required
def simulate_payment(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    if request.method == 'POST':
        Payment.objects.create(
            user=request.user,
            property=property,
            amount=property.monthly_rent,
            is_simulated=True 
        )
        messages.success(request, 'Your payment has been simulated. Waiting for confirmation.')
        return redirect('property_detail', property_id=property.id)
    return render(request, 'properties/simulate_payment.html', {'property': property})

@login_required
def initiate_payment(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        amount = property.monthly_rent  # Use the property's monthly rent as the amount

        consumer_key = 'your_consumer_key'
        consumer_secret = 'your_consumer_secret'
        business_short_code = 'your_business_short_code'
        lipa_na_mpesa_online_passkey = 'your_lipa_na_mpesa_online_passkey'
        callback_url = request.build_absolute_uri(reverse('mpesa_callback'))

        access_token = get_mpesa_access_token(consumer_key, consumer_secret)
        response = lipa_na_mpesa_online(access_token, business_short_code, lipa_na_mpesa_online_passkey, phone_number, amount, callback_url)

        # Create a new Payment object
        Payment.objects.create(
            user=request.user,
            property=property,
            amount=amount,
            is_simulated=False,
            mpesa_request_id=response.get('MerchantRequestID')  # Store the M-Pesa request ID
        )

        return JsonResponse(response)
    
    return render(request, 'properties/initiate_payment.html', {'property': property})


@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        # Process the callback data
        callback_data = json.loads(request.body)
        
        # Extract relevant information from the callback data
        merchant_request_id = callback_data['Body']['stkCallback']['MerchantRequestID']
        result_code = callback_data['Body']['stkCallback']['ResultCode']
        
        # Find the corresponding Payment object
        try:
            payment = Payment.objects.get(mpesa_request_id=merchant_request_id)
            
            if result_code == 0:
                # Payment successful
                payment.is_confirmed = True
                payment.save()
                
                # Update property availability
                payment.property.is_available = False
                payment.property.save()
            else:
                # Payment failed
                payment.delete()  # Or mark it as failed
        
        except Payment.DoesNotExist:
            # Handle the case where the payment is not found
            pass
        
        return HttpResponse(status=200)
    
    return HttpResponse(status=405)  # Method Not Allowed