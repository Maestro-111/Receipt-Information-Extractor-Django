import subprocess
import openai
from openai import OpenAI
import os
from parser.settings import SINGLE_RECEIPT_DIR
from django.conf import settings
import shutil
import re
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, filename=os.path.join(settings.BASE_DIR, 'GPT_log.log'),
                    filemode="w", format="%(asctime)s %(levelname)s %(message)s")

def run_craft(path, multiple=False, mul_dir='/txt_output'):

    """
    CRAFT
    """

    python_path = r'C:/Python39/python.exe'

    if not multiple:
        command = [python_path, "C:/Custom-Craft/test.py", "--trained_model", "C:/Custom-Craft/craft_mlt_25k.pth",
                   "--test_folder", "test/", "--res_txt_path", "text_output.txt",
                   "--dir_path", path]
    else:
        command = [python_path, "C:/Custom-Craft/test.py", "--trained_model", "C:/Custom-Craft/craft_mlt_25k.pth",
                   "--test_folder", "test/", "--res_txt_path", "text_output.txt",
                   "--dir_path", path, "--multiple","True",'--mul_dir',mul_dir]

    subprocess.run(command)


def text_extraction(text):

    """
    Use GPT to analyze OCR response and them extract text from GPT response
    """

    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    with open(os.path.join(settings.BASE_DIR,'prompt.txt'), 'r') as file:
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
    location = None # 5
    products = [] # 6

    product_count = []

    for i in range(len(resp)):
        st = resp[i]

        try:
            name,value = st.split(":")
        except ValueError:
            logging.warning(f"Wrong GPT output for {st}\n")
            continue

        if i == 0 and not re.findall(r'\bNone\b',value):
            total = value
        if i == 1 and not re.findall(r'\bNone\b',value):
            subtotal = value
        if i == 2 and not re.findall(r'\bNone\b',value):
            name_of_store = value
        if i == 3 and not re.findall(r'\bNone\b',value):
            pay_type = value
        if i == 4 and not re.findall(r'\bNone\b',value):
            date = value
        if i == 5 and not re.findall(r'\bNone\b',value):
            location = value
        if i == 6:

            value = value.split(',')
            count = 1

            for i in range(len(value)):
                product_count.append(f"product#{count}")
                count += 1

            products = value

    general_info = {'total': [total], 'subtotal': [subtotal], 'store': [name_of_store], 'payment type': [pay_type],
             'date': [date], 'location':[location]}

    product_info = {'product_count':product_count, 'product_name':products}

    logging.info("Successfully parsed GPT response")

    return general_info, product_info



def construct_dataframes(txt_path,image_names):

    """
    construct corpus of text data
    """


    txt_files = os.listdir(txt_path)
    corpus = []

    for file in txt_files:
        with open(os.path.join(txt_path, file), 'r') as file:
            lines = file.readlines()
            txt_output = [line.strip() for line in lines]
            txt_output = [line for line in txt_output if line]
            corpus.append(txt_output)

    general = pd.DataFrame()
    products = pd.DataFrame()

    for i in range(len(corpus)):

        text = corpus[i]
        name = image_names[i]

        if len(text) > 0:

            general_info, product_info = text_extraction(text)

            print(general_info)

            general_info = pd.DataFrame(general_info)
            product_info = pd.DataFrame(product_info)

            general_info["Image Name"] = name
            product_info["Image Name"] = name

            general = pd.concat([general, general_info])
            products = pd.concat([products, product_info])

    general.reset_index(drop=True, inplace=True)
    products.reset_index(drop=True, inplace=True)

    if general.shape[0]>=1:
        logging.info("Successfully created dataframes")
    else:
        logging.warning("Dataframes were not created")

    return general,products


def prepare_data_to_store(general):

    """
    Generate dict for all objects to save in db
    """

    for row in general.iterrows():

        series = row[1]
        total, subtotal, store, payment_type, date, location, image_name = series
        image_id, rest = image_name.split('.')

        try:
            total = float(total)
        except (ValueError, TypeError):
            total = None

        try:
            subtotal = float(subtotal)
        except (ValueError, TypeError):
            subtotal = None

        if date is not None:
            try:
                date = date.strip()
                date = datetime.strptime(date, '%d/%m/%Y').date()
            except (ValueError, TypeError):
                date = None

        data_to_save = {
            'image_id': int(image_id),
            'total': total,
            'subtotal': subtotal,
            'store': store,
            'payment_type': payment_type,
            'date': date,
            'location': location
        }

        yield data_to_save



