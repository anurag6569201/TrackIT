from django.shortcuts import render
from .models import GmailAccountDetails,GmailAccountLabelsCounts

from gmail_manage.gmail_auth.gmail_readonly_authentication import authenticate_gmail_for_readonly
from gmail_manage.gmail_actions import get_account_details_gmail_api,get_account_labels_gmail_api


def refresh_gmail_data(request):
    gmail_detials_service=authenticate_gmail_for_readonly()
    get_account_details_gmail_api(request,gmail_detials_service)

    account_details, created = GmailAccountDetails.objects.get_or_create(user=request.user)
    return render(request, 'apps/gmail/partials/gmail_details.html', {'account_details': account_details})


def refresh_gmail_labels(request):
    gmail_labels_service=authenticate_gmail_for_readonly()
    get_account_labels_gmail_api(request,gmail_labels_service)

    account_labels_details, created = GmailAccountLabelsCounts.objects.get_or_create(user=request.user)
    label_info = account_labels_details.label_info or {} 
    return render(request, 'apps/gmail/partials/gmail_labels.html', {'account_labels_details': label_info})


def gmail_manage(request):
    account_labels_details, created = GmailAccountLabelsCounts.objects.get_or_create(user=request.user)
    label_info = account_labels_details.label_info or {} 

    account_details, created = GmailAccountDetails.objects.get_or_create(user=request.user)

    context = {
        'account_details': account_details,
        'account_labels_details': label_info, 
    }
    
    return render(request, 'apps/gmail/gmail_manage.html', context)
