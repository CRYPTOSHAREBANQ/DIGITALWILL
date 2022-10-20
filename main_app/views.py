from django.shortcuts import render
from django.contrib import messages

from django.conf import settings as django_settings

from django.http import HttpResponse
from main_app.models import BlockchainWill, Beneficiary
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import formats
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, Http404

from common.utils import get_currencies_exchange_rate, calculate_credit_grade, swap_crypto_info, countries_tuples, FIAT_CURRENCIES

from decimal import Decimal

import cv2
from PIL import Image
import os

# Create your views here.
@login_required()
def blockchain_wills(request):

    if request.method == "POST":
        digital_currency_object = DigitalCurrency.objects.get(symbol="CSC")
        user_balance = Balance.objects.get(email = request.user, digital_currency_name = digital_currency_object)

        blockchain_will_price = 100      #PRICE IN CRYPTOSHARE CREDITS

        if user_balance.amount < blockchain_will_price:
            messages.info(request, "You do not have enough funds to create a business. Please buy more CryptoShare Credits.")
            return redirect('atm_functions:Home')
            
        user_balance.amount -= Decimal(blockchain_will_price)
        user_balance.save()
        blockchain_will = BlockchainWill.objects.create(email= request.user, status="NOT COMPLETED")
        beneficiary = Beneficiary(will_percentage=100)
        beneficiary.save()
        beneficiary.blockchain_wills.add(blockchain_will)

        return redirect(reverse('atm_functions:RegisterBlockchainWill')+f"?id={blockchain_will.id_w}")
    if request.method == "GET":
        blockchain_wills = BlockchainWill.objects.filter(email=request.user)
        context = {
            "blockchain_wills": blockchain_wills
        }
        return render(request, 'blockchain_wills.html', context)

    return render(request, 'blockchain_wills.html')

@login_required()
def register_blockchain_will(request):

    will_id = request.GET.get('id','')

    if not will_id:
        messages.info(request, "Invalid request, please try again.")
        return redirect('atm_functions:BlockchainWills')
    else:
        blockchain_will = BlockchainWill.objects.get(id_w=will_id)
        if blockchain_will.email != request.user:

            messages.info(request, "Invalid request, please try again.")
            return redirect('atm_functions:BlockchainWills')

    if request.method == "GET":
        beneficiary = Beneficiary.objects.filter(blockchain_wills__in = [blockchain_will])
        if beneficiary:
            beneficiary = beneficiary[0]
        else:
            # beneficiary = Beneficiary(
            #                             full_legal_name = "",
            #                             birthdate = "",
            #                             birth_country = "",
            #                             relationship = "",
            #                             associated_email1 = "",
            #                             associated_email2 = "",
            #                             will_percentage = 100,
            #                             selfie_photo_url = ""
            #                         )
            beneficiary = None

        countries = countries_tuples

        context = {
            "blockchain_will": blockchain_will,
            "beneficiary": beneficiary,
            "beneficiary_relationships": ["Wife", "Husband", "Life Partner", "Child", "Friend", "Other"],
            "countries": countries
        }
        return render(request, 'blockchain_will_edit.html', context)

    grantor_fullname = request.POST.get("grantor_fullname", None)
    grantor_birthdate = request.POST.get("grantor_birthdate", None)
    grantor_country = request.POST.get("grantor_country", None)
    grantor_email_1 = request.POST.get("grantor_email_1", None)
    grantor_email_2 = request.POST.get("grantor_email_2", None)
    grantor_email_3 = request.POST.get("grantor_email_3", None)
    grantor_selfie_photo_url = request.POST.get("grantor_selfie_photo", None)
    grantor_id_document_url = request.POST.get("grantor_id_document", None)
    grantor_video_url = request.POST.get("grantor_selfie_video", None)

    blockchain_will.full_legal_name = grantor_fullname
    if grantor_birthdate:
        blockchain_will.birthdate = grantor_birthdate
    blockchain_will.birth_country = grantor_country
    blockchain_will.associated_email1 = grantor_email_1
    blockchain_will.associated_email2 = grantor_email_2
    blockchain_will.associated_email3 = grantor_email_3
    blockchain_will.selfie_photo_url = grantor_selfie_photo_url
    blockchain_will.document_id_url = grantor_id_document_url
    blockchain_will.video_url = grantor_video_url

    #BENEFICIARY

    beneficiary_id = request.POST.get("beneficiary_id", None)
    beneficiary_fullname = request.POST.get("beneficiary_fullname", None)
    beneficiary_birthdate = request.POST.get("beneficiary_birthdate", None)
    beneficiary_country = request.POST.get("beneficiary_country", None)
    beneficiary_relationship = request.POST.get("beneficiary_relationship", None)
    beneficiary_email_1 = request.POST.get("beneficiary_email_1", None)
    beneficiary_email_2 = request.POST.get("beneficiary_email_2", None)
    beneficiary_selfie_photo_url = request.POST.get("beneficiary_selfie_photo", None)

    beneficiary = Beneficiary.objects.get(pk=int(beneficiary_id))
    beneficiary.full_legal_name = beneficiary_fullname
    if beneficiary_birthdate:
        beneficiary.birthdate = beneficiary_birthdate
    beneficiary.birth_country = beneficiary_country
    beneficiary.relationship = beneficiary_relationship
    beneficiary.associated_email1 = beneficiary_email_1
    beneficiary.associated_email2 = beneficiary_email_2
    beneficiary.selfie_photo_url = beneficiary_selfie_photo_url
    beneficiary.save()

    save_will = request.GET.get('save_will','')

    if not save_will:
        # cryptoapis_client = CryptoApis()
        # transaction_response = cryptoapis_client.generate_coins_transaction_from_wallet("dash", "mainnet", "Xh1daZF6rafvc2gieJXzhr71wQtzuvk6C3", "1", data=f"CryptoShare Blockchain Will - {blockchain_will.id_w}|{str(blockchain_will.email)}")
        # transaction_id = transaction_response["transactionRequestId"]

        blockchain_will.status = "ACTIVE"
        blockchain_will.transaction_id = blockchain_will.id_w
        messages.info(request, "Blockchain Will successfully created.")


    blockchain_will.save()

    if save_will:
        json_response = {
            "beneficiary_id": beneficiary.id
        }
        if not beneficiary_id:
            json_response["status"] = "NEW_BENEFICIARY",
        else:
            json_response["status"] = "SUCCESS"

        return HttpResponse(json.dumps(json_response), content_type="application/json")

    return redirect('atm_functions:BlockchainWills')

@login_required()
def certificate_blockchain_will(request, id = None):
    def write_text(image, text, FONT, textsize, x, y):

        textX = (x - textsize[0]) // 2
        textY = (y + textsize[1]) // 2

        cv2.putText(image, text, (textX, textY), FONT, 1, (0, 0, 0), 1, cv2.LINE_AA)

    def generate_certificate(name, transactionId, innerTransactionId, date, b_name, b_birthdate, b_country, b_relationship):
        template_url = os.path.join(django_settings.BASE_DIR, 'static/pdf_templates/Will_Certificate_Template4.jpg')
        temp_certificates = os.path.join(django_settings.BASE_DIR, 'static/temp_certificates')
        new_certificate = f"{temp_certificates}/{name.strip()}.pdf"

        certificate_template_image = cv2.imread(template_url)
        FONT = cv2.FONT_HERSHEY_DUPLEX

        text = name.strip()

        textsize_name = cv2.getTextSize(text, FONT, 1, 0)[0]
        textsize = cv2.getTextSize(text, FONT, 0.5, 0)[0]

        coordinates = [
            [180 * 2, 1020 * 2],
            [540 * 2, 1180 * 2],
            [100 * 2, 1590 * 2],
            [1040 * 2, 1830 * 2],

            [100 * 2, 1700 * 2],

            [100 * 2, 1760 * 2],
            [100 * 2, 1790 * 2],
            [100 * 2, 1820 * 2],
            [100 * 2, 1850 * 2],
        ]

        # write_text(certificate_template_image, transactionId.strip(), FONT, textsize, coordinates[0][0], coordinates[0][1])
        write_text(certificate_template_image, date.strip(), FONT, textsize, coordinates[1][0], coordinates[1][1])
        write_text(certificate_template_image, innerTransactionId.strip(), FONT, textsize, coordinates[2][0], coordinates[2][1])
        write_text(certificate_template_image, name.strip(), FONT, textsize_name, coordinates[3][0], coordinates[3][1])

        write_text(certificate_template_image, "BENEFICIARY:".strip(), FONT, textsize, coordinates[4][0], coordinates[4][1])

        write_text(certificate_template_image, "NAME:           " + b_name.strip(), FONT, textsize, coordinates[5][0], coordinates[5][1])
        write_text(certificate_template_image, "BIRTHDATE:      " + b_birthdate.strftime('%Y-%m-%d'), FONT, textsize, coordinates[6][0], coordinates[6][1])
        write_text(certificate_template_image, "COUNTRY CODE:   " + b_country.strip(), FONT, textsize, coordinates[7][0], coordinates[7][1])
        write_text(certificate_template_image, "RELATIONSHIP:   " + b_relationship.strip(), FONT, textsize, coordinates[8][0], coordinates[8][1])

        cv2_path = f"{temp_certificates}/{name.strip()}.jpg"
        cv2.imwrite(cv2_path, certificate_template_image)

        img = Image.open(f"{temp_certificates}/{name.strip()}.jpg")
        img = img.convert("RGB")
        img.save(new_certificate, format="PDF")

        return new_certificate

    if id is None:
        return redirect('atm_functions:BlockchainWills')

    user = request.user
    user_name = user.first_name + " " + user.last_name
    blockchain_will = BlockchainWill.objects.get(pk=id)

    if blockchain_will.email != request.user or blockchain_will.status != "ACTIVE":
        return redirect('atm_functions:BlockchainWills')

    if blockchain_will.transaction_id is None:
        blockchain_will.transaction_id = "18b513a31bc8381ca73258b98229c8661d562ae92e30df81936aa398c74e3118"
    
    beneficiary = Beneficiary.objects.filter(blockchain_wills__in = [blockchain_will])[0]
    url = generate_certificate(
        user_name, 
        blockchain_will.transaction_id, 
        f"{id}|{blockchain_will.transaction_id}", 
        f"{formats.date_format(blockchain_will.creation_datetime, 'DATETIME_FORMAT')} UTC",
        beneficiary.full_legal_name,
        beneficiary.birthdate,
        beneficiary.birth_country,
        beneficiary.relationship
        )

    try:
        return FileResponse(open(url, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()