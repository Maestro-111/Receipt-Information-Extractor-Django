from django.shortcuts import render
from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect
from django.template.loader import render_to_string
from django.conf import settings
import os
import shutil
from ocr import run_craft
from ocr import text_extraction
import re
from  create_folders import create_folders
import pandas as pd
from .models import Receipt
from datetime import datetime
from django.db.models import Q

def delete_files_in_directory(directory_path):
    files = os.listdir(directory_path)
    for file_name in files:
        file_path = os.path.join(directory_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted: {file_path}")
    print("All files deleted successfully.")


def index(request):

    context = {
            'folder_path': '/static/folder.png',
    }


    return render(request,'multiple_receipt/parse_multiple.html',context)


def download_multiple_file(request, filename):

    file_path = os.path.join(settings.MULTIPLE_EXPORTS_DIR, filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    else:
        return HttpResponse("File not found", status=404)


def download_multiple_receipt(request):

    output_path = request.GET.get('output_path')

    if output_path:
        filename = os.path.basename(output_path)  # Get the filename from the path
        context = {
            'output_path': output_path,
            'filename': filename,
            'path': '/static/success_1.jpg'
        }
        return render(request, 'multiple_receipt/result_1_1.html', context)

    else:
        return HttpResponse("Error downloading file.")

def upload_multiple_receipts(request):

    if request.method == 'POST' and request.FILES.get('receipt_images'):

        receipt_images = request.FILES.getlist('receipt_images')

        create_folders(settings.MULTIPLE_RECEIPT_DIR)

        for uploaded_file in receipt_images:

            file_path = os.path.join(settings.MULTIPLE_MEDIA_ROOT, uploaded_file.name)
            test_path = os.path.join(settings.MULTIPLE_TEST_ROOT, uploaded_file.name)

            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

        images = os.listdir(settings.MULTIPLE_MEDIA_ROOT)

        for image in images:

            file_path = os.path.join(settings.MULTIPLE_MEDIA_ROOT, image)
            test_path = os.path.join(settings.MULTIPLE_TEST_ROOT, image)

            shutil.copy(file_path, test_path)

        run_craft(path=settings.MULTIPLE_RECEIPT_DIR, multiple=True)

        delete_files_in_directory(os.path.join(settings.MULTIPLE_RECEIPT_DIR,'test'))
        delete_files_in_directory(os.path.join(settings.MULTIPLE_RECEIPT_DIR, 'result'))
        delete_files_in_directory(os.path.join(settings.MULTIPLE_RECEIPT_DIR, 'test_boxes_from_craft/coords'))
        delete_files_in_directory(os.path.join(settings.MULTIPLE_RECEIPT_DIR, 'test_boxes_from_craft/imgs'))
        delete_files_in_directory(os.path.join(settings.MULTIPLE_RECEIPT_DIR, 'uploads'))

       # add parsing txt logic database?

        txt_path = os.path.join(settings.MULTIPLE_RECEIPT_DIR, 'txt_output')

        txt_files = os.listdir(os.path.join(txt_path))

        corpus = []

        for file in txt_files:
            print(file)
            with open(os.path.join(txt_path, file), 'r') as file:
                lines = file.readlines()
                txt_output = [line.strip() for line in lines]
                txt_output = [line for line in txt_output if line]
                corpus.append(txt_output)

        delete_files_in_directory(os.path.join(settings.MULTIPLE_RECEIPT_DIR, 'txt_output'))

        general = pd.DataFrame()
        products = pd.DataFrame()

        for i in range(len(corpus)):

            text  = corpus[i]
            name = images[i]

            if len(text)>0:

                extarcted_text, product_text = text_extraction(text)


                general_info = pd.DataFrame(extarcted_text)
                product_info = pd.DataFrame(product_text)

                general_info["Image Name"] = name
                product_info["Image Name"] = name


                general = pd.concat([general,general_info])
                products = pd.concat([products, product_info])


        general.reset_index(drop=True,inplace=True)
        products.reset_index(drop=True, inplace=True)


        for row in general.iterrows():

            series = row[1]
            total,subtotal,store,payment_type,date,address,image_name = series
            image_id = image_name[:-4]

            try:
                total = float(total)
            except ValueError:
                total = None

            try:
                subtotal = float(subtotal)
            except ValueError:
                subtotal = None

            if date is not None:
                try:
                    date = datetime.strptime(date, '%d/%m/%y').date()
                except ValueError:
                    date = None

            data_to_save = {
                'image_id': int(image_id),
                'total': total,
                'subtotal': subtotal,
                'store': store,
                'payment_type': payment_type,
                'date': date,
                'address': address
            }

            print(data_to_save)


            existing_receipt = Receipt.objects.filter(image_id=data_to_save['image_id']).first()

            if existing_receipt:
                print(f"Receipt with image_id {image_id} already exists.")
                print(existing_receipt)
            else:
                print(f"New receipt with image_id {image_id}.")

            instance = Receipt(**data_to_save)
            instance.save()


        output_path = os.path.join(settings.MULTIPLE_RECEIPT_DIR, f'exports/output.xlsx')

        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            general.to_excel(writer, sheet_name='general_info', index=False)

        with pd.ExcelWriter(output_path, engine='openpyxl', mode='a') as writer:
            products.to_excel(writer, sheet_name='product_info', index=False)

        return HttpResponseRedirect(reverse('download_multiple_receipt') + f'?output_path={output_path}')

    else:
        return HttpResponse(f"error")


