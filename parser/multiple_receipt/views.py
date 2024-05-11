from django.shortcuts import render
from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect
from django.template.loader import render_to_string
from django.conf import settings



def index(request):
    return render(request,'multiple_receipt/parse_multiple.html')


def upload_multiple_receipts(request):

    if request.method == 'POST' and request.FILES.get('receipt_images'):

        receipt_images = request.FILES.getlist('receipt_images')

        for uploaded_file in receipt_images:
            print(uploaded_file.name)

        return HttpResponse(f"Success")
    else:
        return HttpResponse(f"error")
