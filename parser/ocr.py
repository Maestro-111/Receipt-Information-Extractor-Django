import subprocess
import openai
from openai import OpenAI
import os
from parser.settings import SINGLE_RECEIPT_DIR
from  django.conf import settings


def run_craft():
    python_path = r'C:/Python39/python.exe'
    command = [python_path, "C:/Custom-Craft/test.py", "--trained_model", "C:/Custom-Craft/craft_mlt_25k.pth",
               "--test_folder", "test/", "--res_txt_path", "text_output.txt",
               "--dir_path", SINGLE_RECEIPT_DIR]

    subprocess.run(command)

def text_extraction(text):

    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    with open(os.path.join(settings.SINGLE_RECEIPT_DIR,'prompt.txt'), 'r') as file:
        message_template = file.read()

    message = message_template.format(text)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": message,
            }
        ],
        model="gpt-4",
    )

    resp = chat_completion.choices[0].message.content
    resp = resp.split('\n')

    resp = [i for i in resp if i]


    total = None
    subtotal = None
    name_of_store = None
    pay_type = None
    date = None # 4
    address = None # 5
    products = [] # 6
    dumb_names = []

    for i in range(len(resp)):
        st = resp[i]

        try:
            name,value = st.split(":")
        except ValueError:
            continue

        if i == 0:
            total = value
        elif i == 1:
            subtotal = value
        elif i == 2:
            name_of_store = value
        elif i == 3:
            pay_type = value
        elif i == 4:
            date = value
        elif i == 5:
            address = value
        else:
            value = value.split(',')

            count = 1

            for i in range(len(value)):
                dumb_names.append(f"product#{count}")
                count += 1


            products = value

    data1 = {'total': [total], 'subtotal': [subtotal], 'store': [name_of_store], 'payment type': [pay_type], 'date':[date],'address':[address]}

    data2 = {'product_count':dumb_names, 'product_name':products}

    return data1,data2
