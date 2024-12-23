from collections import defaultdict

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, reverse, redirect, get_object_or_404

from consign_app.models import  Account, Login, AddConsignment, AddConsignmentTemp, Disel,\
      Branch, Driver, Vehicle, Staff, Consignee, Consignor, \
    Expenses,Vendor, LHSPrem,LHSTemp,GDMPrem,GDMTemp,TURTemp,TURPrem

# from django.core.mail import send_mail


import json
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from .models import Location

import datetime
import random
import string
import secrets
import pprint

from datetime import datetime, timedelta
import logging

from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
from consign.settings import BASE_DIR
from django.db.models import Q, Max, Min, Subquery
from django.contrib import messages
from django.utils import timezone

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json
from django.views.decorators.http import require_POST
from django.db.models import Count
from datetime import datetime
from django.core.exceptions import ValidationError
from decimal import Decimal

from django.db.models.functions import Concat
from django.db import connection, IntegrityError

from .models import Location  # Assume you have a Location model


# import datetime
# from .models import AddTrack, AddConsignment


def index(request):
    return render(request, 'index.html')

def logout(request):
    return render(request, 'index.html')

def index_menu(request):
    return render(request, 'index_menu.html')


def admin_home(request):
    return render(request, 'admin_home.html')


def branch_home(request):
    return render(request, 'branch_home.html')

def userlogin(request):
    if request.method == "POST":
        username = request.POST.get('t1')
        password = request.POST.get('t2')
        request.session['username'] = username
        ucount = Login.objects.filter(username=username).count()
        if ucount >= 1:
            udata = Login.objects.get(username=username)
            upass = udata.password
            utype = udata.utype
            if password == upass:
                request.session['utype'] = utype
                if utype == 'user':
                    return render(request, 'user_home.html')
                if utype == 'admin':
                    return render(request, 'admin_home.html')
                if utype == 'branch':
                    return render(request, 'branch_home.html')
                if utype == 'staff':
                    return render(request, 'staff_home.html')
            else:
                return render(request, 'userlogin.html', {'msg': 'Invalid Password'})
        else:
            return render(request, 'userlogin.html', {'msg': 'Invalid Username'})
    return render(request, 'userlogin.html')


def branch(request):
    if request.method == "POST":
        companyname = request.POST.get('companyname')
        headname = request.POST.get('headname')
        phonenumber = request.POST.get('phonenumber')
        email = request.POST.get('email')
        password = request.POST.get('password')
        gst = request.POST.get('gst')
        address = request.POST.get('address')
        branchtype = 'mainBranch'

        utype = 'branch'

        if Login.objects.filter(username=email).exists():
            messages.error(request, 'Username (email) already exists.')
            return render(request, 'branch.html')

        # If the email does not exist, create the branch and login records
        Branch.objects.create(
            companyname=companyname,
            phonenumber=phonenumber,
            email=email,
            gst=gst,
            address=address,
            headname=headname,
            password=password,
            branchtype=branchtype
        )
        Login.objects.create(utype=utype, username=email, password=password, name=headname)

        messages.success(request, 'Branch created successfully.')

    return render(request, 'branch.html')


def view_branch(request):
    data = Branch.objects.all()
    return render(request, 'view_branch.html', {'data': data})


def edit_branch(request, pk):
    data = Branch.objects.filter(id=pk).first()  # Retrieve a single object or None

    original_email = data.email

    if request.method == "POST":
        companyname = request.POST.get('companyname')
        headname = request.POST.get('headname')
        phonenumber = request.POST.get('phonenumber')
        email = request.POST.get('email')
        gst = request.POST.get('gst')
        address = request.POST.get('address')
        password = request.POST.get('password')
        prefix = request.POST.get('prefix')

        # Update the object
        data.companyname = companyname
        data.headname = headname
        data.phonenumber = phonenumber
        data.email = email
        data.gst = gst
        data.address = address
        data.password = password
        data.save()

        # Update the Login record using the original staffPhone
        user = Login.objects.filter(username=original_email).first()  # Fetch the user with the original phone number
        if user:
            user.username = email  # Update username to the new phone number
            user.name = headname  # Update name
            user.password = password
            user.save()
        # Redirect to a different URL after successful update
        base_url = reverse('view_branch')
        return redirect(base_url)

    return render(request, 'edit_branch.html', {'data': data})


def branch_delete(request, pk):
    udata = Branch.objects.get(id=pk)
    user = Login.objects.filter(username=udata.email).first()
    if user:
        user.delete()
    udata.delete()
    base_url = reverse('view_branch')
    return redirect(base_url)


def driver(request):
    if request.method == "POST":
        driver_name = request.POST.get('driver_name')
        phone_number = request.POST.get('phonenumber')
        address = request.POST.get('address')
        passport = request.POST.get('passport')
        license = request.POST.get('license')
        aadhar = request.POST.get('aadhar')

        passportfile = request.FILES['passport']
        fs = FileSystemStorage()
        filepassport = fs.save(passportfile.name, passportfile)
        upload_file_url = fs.url(filepassport)
        path = os.path.join(BASE_DIR, '/media/' + filepassport)

        licensefile = request.FILES['license']
        fs = FileSystemStorage()
        filelicense = fs.save(licensefile.name, licensefile)
        upload_file_url = fs.url(filelicense)
        path = os.path.join(BASE_DIR, '/media/' + filelicense)

        aadharfile = request.FILES['aadhar']
        fs = FileSystemStorage()
        fileaadhar = fs.save(aadharfile.name, aadharfile)
        upload_file_url = fs.url(fileaadhar)
        path = os.path.join(BASE_DIR, '/media/' + fileaadhar)

        Driver.objects.create(
            driver_name=driver_name,
            phone_number=phone_number,
            address=address,
            passport=passportfile,
            license=licensefile,
            aadhar=aadharfile
        )
    return render(request, 'driver.html')


def view_driver(request):
    data = Driver.objects.all()
    return render(request, 'view_driver.html', {'data': data})


def driver_edit(request, pk):
    data = Driver.objects.filter(id=pk).first()  # Retrieve a single object or None

    if request.method == "POST":
        driver_name = request.POST.get('driver_name')
        phone_number = request.POST.get('phonenumber')
        address = request.POST.get('address')

        # Update the object
        data.driver_name = driver_name
        data.phone_number = phone_number
        data.address = address

        data.save()

        # Redirect to a different URL after successful update
        base_url = reverse('view_driver')
        return redirect(base_url)

    return render(request, 'driver_edit.html', {'data': data})


def driver_delete(request, pk):
    udata = Driver.objects.get(id=pk)
    udata.delete()
    base_url = reverse('view_driver')
    return redirect(base_url)


def vehicle(request):
    if request.method == "POST":
        vehicle_number = request.POST.get('vehicle_number')
        rcdate = request.POST.get('rcdate')
        incurencedate = request.POST.get('incurencedate')
        permitdate = request.POST.get('permitdate')
        taxdate = request.POST.get('taxdate')
        emissiondate = request.POST.get('emissiondate')

        rcfile = request.FILES['rc']
        fs = FileSystemStorage()
        filerc = fs.save(rcfile.name, rcfile)
        upload_file_url = fs.url(filerc)
        path = os.path.join(BASE_DIR, '/media/' + filerc)

        incurencefile = request.FILES['incurence']
        fs = FileSystemStorage()
        fileincurence = fs.save(incurencefile.name, incurencefile)
        upload_file_url = fs.url(fileincurence)
        path = os.path.join(BASE_DIR, '/media/' + fileincurence)

        permitfile = request.FILES['permit']
        fs = FileSystemStorage()
        filepermit = fs.save(permitfile.name, permitfile)
        upload_file_url = fs.url(filepermit)
        path = os.path.join(BASE_DIR, '/media/' + filepermit)

        taxfile = request.FILES['tax']
        fs = FileSystemStorage()
        filetax = fs.save(taxfile.name, taxfile)
        upload_file_url = fs.url(filetax)
        path = os.path.join(BASE_DIR, '/media/' + filetax)

        emissionfile = request.FILES['emission']
        fs = FileSystemStorage()
        fileemission = fs.save(emissionfile.name, emissionfile)
        upload_file_url = fs.url(fileemission)
        path = os.path.join(BASE_DIR, '/media/' + fileemission)

        if Vehicle.objects.filter(vehicle_number=vehicle_number).exists():
            messages.error(request, 'vehicle number already exists.')
            return render(request, 'vehicle.html')

        Vehicle.objects.create(
            vehicle_number=vehicle_number,
            rccard=rcfile,
            rccardate=rcdate,
            incurencedate=incurencedate,
            incurence=incurencefile,
            permit=permitfile,
            permitdate=permitdate,
            tax=taxfile,
            taxdate=taxdate,
            emission=emissionfile,
            emissiondate=emissiondate
        )
        messages.success(request, 'Vehicle created successfully.')
    return render(request, 'vehicle.html')


from django.utils.timezone import now


def view_vehicle(request):
    today = now().date()  # Get the current date
    data = Vehicle.objects.all()

    # Add a 'days_left' attribute for each field to use in the template
    for vehicle in data:
        vehicle.rc_days_left = (vehicle.rccardate - today).days if vehicle.rccardate else None
        vehicle.insurance_days_left = (vehicle.incurencedate - today).days if vehicle.incurencedate else None
        vehicle.permit_days_left = (vehicle.permitdate - today).days if vehicle.permitdate else None
        vehicle.tax_days_left = (vehicle.taxdate - today).days if vehicle.taxdate else None
        vehicle.emission_days_left = (vehicle.emissiondate - today).days if vehicle.emissiondate else None

    return render(request, 'view_vehicle.html', {'data': data})


def vehicle_edit(request, pk):
    data = Vehicle.objects.filter(id=pk).first()  # Retrieve a single object or None

    if request.method == "POST":
        vehicle_number = request.POST.get('vehicle_number')
        rcdate = request.POST.get('rcdate')
        incurencedate = request.POST.get('incurencedate')
        permitdate = request.POST.get('permitdate')
        taxdate = request.POST.get('taxdate')
        emissiondate = request.POST.get('emissiondate')

        data.vehicle_number = vehicle_number
        data.rccardate = rcdate
        data.incurencedate = incurencedate
        data.permitdate = permitdate
        data.taxdate = taxdate
        data.emissiondate = emissiondate

        data.save()

        # Redirect to a different URL after successful update
        base_url = reverse('view_vehicle')
        return redirect(base_url)

    return render(request, 'vehicle_edit.html', {'data': data})


def vehicle_delete(request, pk):
    udata = Vehicle.objects.get(id=pk)
    udata.delete()
    base_url = reverse('view_vehicle')
    return redirect(base_url)

def get_account_name(request):
    query = request.GET.get('query', '')
    if query:
        sender_names = Account.objects.filter(sender_name__icontains=query).values_list('sender_name',
                                                                                        flat=True).distinct()
        print('sender_names numbers:', list(sender_names))  # Debugging: check the data in the terminal
        return JsonResponse(list(sender_names), safe=False)
    return JsonResponse([], safe=False)


def get_consignor_name(request):
    query = request.GET.get('query', '')
    if query:
        sender_names = Consignor.objects.filter(sender_name__icontains=query).values_list('sender_name', flat=True)
        print('sender_names numbers:', list(sender_names))  # Debugging: check the data in the terminal
        return JsonResponse(list(sender_names), safe=False)
    return JsonResponse([], safe=False)


def get_sender_details(request):
    name = request.GET.get('name', '')
    if name:
        consignor = Consignor.objects.filter(sender_name=name).first()
        if consignor:
            data = {
                'sender_mobile': consignor.sender_mobile,
                'sender_email': consignor.sender_email,
                'sender_GST': consignor.sender_GST,
                'sender_address': consignor.sender_address,
                'sender_company': consignor.sender_company,
            }
        else:
            data = {}
    else:
        data = {}

    return JsonResponse(data)


def get_consignee_name(request):
    query = request.GET.get('query', '')
    if query:
        receiver_names = Consignee.objects.filter(receiver_name__icontains=query).values_list('receiver_name',
                                                                                              flat=True)
        print('sender_names numbers:', list(receiver_names))  # Debugging: check the data in the terminal
        return JsonResponse(list(receiver_names), safe=False)
    return JsonResponse([], safe=False)


def get_rec_details(request):
    name = request.GET.get('name', '')
    if name:
        consignee = Consignee.objects.filter(receiver_name=name).first()
        if consignee:
            data = {
                'receiver_mobile': consignee.receiver_mobile,
                'receiver_GST': consignee.receiver_GST,
                'receiver_email': consignee.receiver_email,
                'receiver_address': consignee.receiver_address,
                'receiver_company': consignee.receiver_company,
            }
        else:
            data = {}
    else:
        data = {}

    return JsonResponse(data)


def branchConsignment(request):
    if request.method == "POST":
        now = datetime.now().replace(microsecond=0)

        con_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")

        uid = request.session.get('username')
        branch = Branch.objects.get(email=uid)
        uname = branch.companyname
        username = branch.headname
        branchemail = branch.email
        branchtype = branch.branchtype

        # Get the last track_id and increment it
        last_track_id = AddConsignment.objects.aggregate(Max('track_id'))['track_id__max']
        track_id = int(last_track_id) + 1 if last_track_id else 1  # Start from a defined base if no entries exist
        con_id = str(track_id)

        # Get the last Consignment_id and increment it
        last_con_id = AddConsignment.objects.aggregate(Max('Consignment_id'))['Consignment_id__max']
        Consignment_id = last_con_id + 1 if last_con_id else 1  # Start from a defined base if no entries exist
        Consignment_id = str(Consignment_id)

        # Sender details
        send_name = request.POST.get('a1')
        send_mobile = request.POST.get('a2')
        send_address = request.POST.get('a4')
        sender_GST = request.POST.get('sendergst')

        # Receiver details
        rec_name = request.POST.get('a5')
        rec_mobile = request.POST.get('a6')
        rec_address = request.POST.get('a8')
        rec_GST = request.POST.get('receivergst')

        copies = []
        if request.POST.get('consignor_copy'):
            copies.append('Consignor Copy')
        if request.POST.get('consignee_copy'):
            copies.append('Consignee Copy')
        if request.POST.get('payment_copy'):
            copies.append('Payment Copy')
        if request.POST.get('ho_copy'):
            copies.append('HO Copy')
        if request.POST.get('file_copy'):
            copies.append('File Copy')
        copy_type = ', '.join(copies)  # Combine into a single string

        delivery_types = []
        if request.POST.get('godownDelivery'):
            copies.append('Godown Delivery')
        if request.POST.get('doorDelivery'):
            copies.append('Door Delivery')
        if request.POST.get('GDMDelivery'):
            copies.append('GDM')
        delivery_type = ', '.join(delivery_types)  # Combine into a single string

        collection_types = []
        if request.POST.get('godownCollection'):
            copies.append('Godown')
        if request.POST.get('lcmDelivery'):
            copies.append('LCM')
        if request.POST.get('gdmCollection'):
            copies.append('GDM')
        collection_type = ', '.join(collection_types)

        # Create or update Consignor
        Consignor.objects.update_or_create(
            sender_name=send_name,
            defaults={
                'sender_mobile': send_mobile,
                'sender_address': send_address,
                'sender_GST': sender_GST,
                'branch': uname,
            }
        )

        # Create or update Consignee
        Consignee.objects.update_or_create(
            receiver_name=rec_name,
            defaults={
                'receiver_mobile': rec_mobile,
                'receiver_address': rec_address,
                'receiver_GST': rec_GST,
                'branch': uname,
            }
        )

        # Handling product entries
        products = request.POST.getlist('product[]')
        pieces = request.POST.getlist('pieces[]')

        # Other consignment details
        delivery = request.POST.get('delivery_option')
        collection = request.POST.get('collection_option')
        prod_invoice = request.POST.get('prod_invoice')
        prod_price = request.POST.get('prod_price')
        weight = float(request.POST.get('weight') or 0)
        weightAmt = float(request.POST.get('weightAmt') or 0)
        freight = float(request.POST.get('freight') or 0)
        hamali = float(request.POST.get('hamali') or 0)
        door_charge = float(request.POST.get('door_charge') or 0)
        st_charge = float(request.POST.get('st_charge') or 0)
        cost = float(request.POST.get('cost') or 0)
        bal = float(request.POST.get('bal') or 0)
        route_from = request.POST.get('from')
        route_to = request.POST.get('to')
        eway_bill = request.POST.get('ewaybill_no')

        pay_status = request.POST.get('payment')

        utype = request.session.get('utype')
        branch_value = 'admin' if utype == 'admin' else uname

        # Determine the appropriate name based on pay_status
        if pay_status == 'Account':
            account_name = send_name
        elif pay_status == 'Consignee_AC':
            account_name = rec_name
        else:
            account_name = send_name  # Default to sender_name if pay_status is neither

        # Use transaction to ensure atomic operations
        with transaction.atomic():
            # Save aggregate data to AddConsignment and AddConsignmentTemp
            for product, piece in zip(products, pieces):
                # Skip rows where product or piece is empty
                if not product or not piece:
                    continue
                AddConsignment.objects.create(
                    track_id=con_id,
                    Consignment_id=Consignment_id,
                    sender_name=send_name,
                    sender_mobile=send_mobile,
                    sender_address=send_address,
                    sender_GST=sender_GST,
                    receiver_name=rec_name,
                    receiver_mobile=rec_mobile,
                    receiver_address=rec_address,
                    receiver_GST=rec_GST,
                    desc_product=product,
                    pieces=piece,
                    prod_invoice=prod_invoice,
                    prod_price=prod_price,
                    weightAmt=weightAmt,
                    weight=weight,
                    balance=bal,
                    freight=freight,
                    hamali=hamali,
                    door_charge=door_charge,
                    st_charge=st_charge,
                    route_from=route_from,
                    route_to=route_to,
                    total_cost=cost,
                    date=con_date,
                    pay_status=pay_status,
                    branch=branch_value,
                    name=username,
                    time=current_time,
                    delivery=delivery,
                    copy_type=copy_type,
                    eway_bill=eway_bill,
                    branchemail=branchemail,
                    delivery_type=delivery_type,
                    collection_type=collection_type,
                )

            for product, piece in zip(products, pieces):
                # Skip rows where product or piece is empty
                if not product or not piece:
                    continue

                AddConsignmentTemp.objects.create(
                    track_id=con_id,
                    Consignment_id=Consignment_id,
                    sender_name=send_name,
                    sender_mobile=send_mobile,
                    sender_address=send_address,
                    sender_GST=sender_GST,
                    receiver_name=rec_name,
                    receiver_mobile=rec_mobile,
                    receiver_address=rec_address,
                    receiver_GST=rec_GST,
                    desc_product=product,
                    pieces=piece,  # Assign the current piece to the pieces field
                    prod_invoice=prod_invoice,
                    prod_price=prod_price,
                    weightAmt=weightAmt,
                    weight=weight,
                    balance=bal,
                    freight=freight,
                    hamali=hamali,
                    door_charge=door_charge,
                    st_charge=st_charge,
                    route_from=route_from,
                    route_to=route_to,
                    total_cost=cost,
                    date=con_date,
                    pay_status=pay_status,
                    branch=branch_value,
                    name=username,
                    time=current_time,
                    delivery=delivery,
                    copy_type=copy_type,
                    eway_bill=eway_bill,
                    branchemail=branchemail,
                    delivery_type=delivery_type,


                )

            # Only handle the Account model if pay_status is 'Shipper A/c' or 'Receiver A/C'
            if pay_status in ['Account', 'Consignee_AC']:
                try:
                    # Initialize balance based on sender_name if it's the first entry for that sender
                    previous_balance_entry = Account.objects.filter(sender_name=account_name).order_by('-Date').first()
                    if previous_balance_entry:
                        previous_balance = float(previous_balance_entry.Balance)
                    else:
                        previous_balance = 0.0  # Initialize balance to 0 if no previous entries

                    # Update the current balance for the sender
                    updated_balance = previous_balance + cost

                    print(f"Creating/Updating Account entry with track_number: {con_id}")
                    print(f"Pay Status: {pay_status}")
                    print(f"Sender Name: {account_name}")
                    print(f"Updated balance: {updated_balance}")

                    # Fetch or create the Account entry
                    account_entry, created = Account.objects.update_or_create(
                        track_number=con_id,
                        defaults={
                            'Date': now,
                            'debit': cost,
                            'credit': 0,
                            'TrType': "sal",
                            'particulars': f"{con_id} Amount Debited",
                            'Balance': updated_balance,
                            'sender_name': account_name,
                            'headname': username,
                            'Branch': branch_value
                        }
                    )
                except Exception as e:
                    print(f"Account entry {'created' if created else 'updated'}: {account_entry}")
                    # Add response in case of error
        # Redirect based on branch type
        if branchtype == "mainBranch":
            return redirect('branchprintConsignment', track_id=con_id)
        elif branchtype == "subBranch":
            return redirect('branchprintConsignmentSub', track_id=con_id)

    else:
        # For GET request, fetch vehicle numbers
        vehicle_numbers = Vehicle.objects.values_list('vehicle_number', flat=True)
        return render(request, 'branchConsignment.html', {'vehicle_numbers': vehicle_numbers})


def branchprintConsignment(request, track_id):
    grouped_userdata = {}
    copy_types = []

    try:
        # Filter consignments by track_id
        consignments = AddConsignment.objects.filter(track_id=track_id)
        uid = request.session.get('username')

        branchdetails = Branch.objects.get(email=uid)
        branchprefix = branchdetails.prefix

        if not consignments.exists():
            return render(request, '404.html')  # Handle the case where no consignments are found.

        for consignment in consignments:
            track_id = consignment.track_id
            if track_id not in grouped_userdata:
                grouped_userdata[track_id] = {field.name: getattr(consignment, field.name) for field in
                                              AddConsignment._meta.fields}

                grouped_userdata[track_id]['pieces'] = 0
                grouped_userdata[track_id]['products'] = []

            # Aggregate total pieces
            grouped_userdata[track_id]['pieces'] += consignment.pieces

            # Collect product details
            product_detail = consignment.desc_product
            grouped_userdata[track_id]['products'].append(product_detail)

            if consignment.copy_type not in copy_types:
                copy_types.append(consignment.copy_type)

        for track_id, details in grouped_userdata.items():
            details['products'] = ', '.join(details['products'])

    except ObjectDoesNotExist:
        grouped_userdata = {}

    return render(request, 'branchprintConsignment.html', {
        'grouped_userdata': grouped_userdata,
        'branchdetails': branchdetails,
        'branchprefix ': branchprefix,
        'copy_types': ', '.join(copy_types),  # Include the aggregated copy types

    })

def branchviewconsignment(request):
    uid = request.session.get('username')
    grouped_userdata = {}

    if uid:
        try:
            branch = Branch.objects.get(email=uid)
            user_branch = branch.companyname  # Adjust if the branch info is stored differently
            branchemail = branch.email
            branchprefix = branch.prefix

            consigner = request.POST.get('consigner')
            consigee = request.POST.get('consignee')
            track_id = request.POST.get('lrno')

            from_date_str = request.POST.get('from_date')
            to_date_str = request.POST.get('to_date')

            # Parse dates
            from_date = parse_date(from_date_str) if from_date_str else None
            to_date = parse_date(to_date_str) if to_date_str else None

            # Fetch consignments for the branch
            consignments = AddConsignment.objects.filter(branchemail=branchemail)

            if consigner:
                consignments = consignments.filter(sender_name=consigner)
            if consigee:
                consignments = consignments.filter(receiver_name=consigee)
            if track_id:
                consignments = consignments.filter(track_id=track_id)

            if from_date and to_date:
                consignments = consignments.filter(date__range=(from_date, to_date))
            elif from_date:
                consignments = consignments.filter(date__gte=from_date)
            elif to_date:
                consignments = consignments.filter(date__lte=to_date)

            # Group consignments by track_id and concatenate product details
            for consignment in consignments:
                track_id = consignment.track_id
                if track_id not in grouped_userdata:
                    grouped_userdata[track_id] = {
                        'route_from': consignment.route_from,
                        'route_to': consignment.route_to,
                        'sender_name': consignment.sender_name,
                        'sender_mobile': consignment.sender_mobile,
                        'receiver_name': consignment.receiver_name,
                        'receiver_mobile': consignment.receiver_mobile,
                        'total_cost': consignment.total_cost,
                        'pieces': 0,
                        'weight': consignment.weight,
                        'prefix': branchprefix,
                        'pay_status': consignment.pay_status,
                        'products': []
                    }
                # Aggregate total cost
                grouped_userdata[track_id]['pieces'] += consignment.pieces
                # Concatenate product details without ID
                product_detail = consignment.desc_product
                grouped_userdata[track_id]['products'].append(product_detail)

        except ObjectDoesNotExist:
            pass

    # Convert the list of product details to a single string
    for track_id, details in grouped_userdata.items():
        details['products'] = ', '.join(details['products'])

    return render(request, 'branchviewConsignment.html', {'grouped_userdata': grouped_userdata})


def branchMaster(request):
    uid = request.session['username']
    email = Branch.objects.get(email=uid)
    bid = email.id
    data = Branch.objects.filter(id=bid).first()  # Retrieve a single object or None
    if request.method == "POST":
        companyname = request.POST.get('companyname')
        phonenumber = request.POST.get('phonenumber')
        email = request.POST.get('email')
        gst = request.POST.get('gst')
        address = request.POST.get('address')
        image = request.POST.get('image')

        # Update the object
        data.companyname = companyname
        data.phonenumber = phonenumber
        data.email = email
        data.gst = gst
        data.address = address
        data.image = image

        data.save()

        # Redirect to a different URL after successful update
        base_url = reverse('branchMaster')
        return redirect(base_url)

    return render(request, 'branchMaster.html', {'data': data})


from django.core.exceptions import ObjectDoesNotExist


from datetime import datetime


def branchconsignment_edit(request, pk):
    # Fetch the main consignment object (first record only)
    userdata = AddConsignment.objects.filter(track_id=pk).first()
    if not userdata:
        return HttpResponse("Consignment not found", status=404)

    # Fetch all products under this consignment
    products = AddConsignment.objects.filter(track_id=pk)

    # Fetch consignment temp data if it exists
    userdatatemp = AddConsignmentTemp.objects.filter(track_id=pk)

    if request.method == "POST":
        userdata.date = request.POST.get('date')
        userdata.route_from = request.POST.get('from')
        userdata.route_to = request.POST.get('to')
        userdata.sender_name = request.POST.get('a1')
        userdata.receiver_name = request.POST.get('a5')
        userdata.total_cost = request.POST.get('cost')
        userdata.weight = request.POST.get('weight')
        userdata.balance = request.POST.get('bal')
        userdata.pay_status = request.POST.get('payment')

        # Additional fields
        userdata.sender_address = request.POST.get('a4')
        userdata.sender_mobile = request.POST.get('a2')
        userdata.sender_GST = request.POST.get('sendergst')
        userdata.receiver_address = request.POST.get('a8')
        userdata.receiver_mobile = request.POST.get('a6')
        userdata.receiver_GST = request.POST.get('receivergst')
        userdata.prod_invoice = request.POST.get('prod_invoice')
        userdata.prod_price = request.POST.get('prod_price')
        userdata.weightAmt = request.POST.get('weightAmt')
        userdata.freight = request.POST.get('freight')
        userdata.hamali = request.POST.get('hamali')
        userdata.door_charge = request.POST.get('door_charge')
        userdata.st_charge = request.POST.get('st_charge')
        userdata.save()

        # Update AddConsignmentTemp only if userdatatemp exists
        if userdatatemp.exists():
            for temp_obj in userdatatemp:
                temp_obj.date = request.POST.get('date')
                temp_obj.route_from = request.POST.get('from')
                temp_obj.route_to = request.POST.get('to')
                temp_obj.sender_name = request.POST.get('a1')
                temp_obj.receiver_name = request.POST.get('a5')
                temp_obj.total_cost = request.POST.get('cost')
                temp_obj.weight = request.POST.get('weight')
                temp_obj.balance = request.POST.get('bal')
                temp_obj.pay_status = request.POST.get('payment')
                temp_obj.sender_address = request.POST.get('a4')
                temp_obj.sender_mobile = request.POST.get('a2')
                temp_obj.sender_GST = request.POST.get('sendergst')
                temp_obj.receiver_address = request.POST.get('a8')
                temp_obj.receiver_mobile = request.POST.get('a6')
                temp_obj.receiver_GST = request.POST.get('receivergst')
                temp_obj.prod_invoice = request.POST.get('prod_invoice')
                temp_obj.prod_price = request.POST.get('prod_price')
                temp_obj.weightAmt = request.POST.get('weightAmt')
                temp_obj.freight = request.POST.get('freight')
                temp_obj.hamali = request.POST.get('hamali')
                temp_obj.door_charge = request.POST.get('door_charge')
                temp_obj.st_charge = request.POST.get('st_charge')
                temp_obj.save()

        # Handling products - updating or adding new ones
        product_ids = request.POST.getlist('product_id[]')
        products_list = request.POST.getlist('product[]')
        pieces_list = request.POST.getlist('pieces[]')

        for product_id, product_desc, piece in zip(product_ids, products_list, pieces_list):
            if product_desc and piece:
                if product_id:  # Update existing product
                    product_obj = AddConsignment.objects.filter(id=product_id).first()
                    if product_obj:
                        product_obj.desc_product = product_desc
                        product_obj.pieces = piece
                        product_obj.save()
                else:  # Add new product
                    AddConsignment.objects.create(
                        track_id=userdata.track_id,
                        desc_product=product_desc,
                        pieces=piece,
                        sender_name=userdata.sender_name,
                        receiver_name=userdata.receiver_name
                    )

        # Redirect after saving
        return redirect(reverse('branchviewconsignment'))

    return render(request, 'branchconsignment_edit.html', {
        'userdata': userdata,
        'products': products,
    })

def branchconsignment_delete(request, pk):
    udata = AddConsignment.objects.get(id=pk)
    udata.delete()
    base_url = reverse('view_consignment')
    return redirect(base_url)


from django.shortcuts import redirect


def branchinvoiceConsignment(request, track_id):
    grouped_userdata = {}
    copy_types = []

    try:
        # Filter consignments by track_id
        consignments = AddConsignment.objects.filter(track_id=track_id)
        uid = request.session.get('username')
        branchdetails = Branch.objects.get(email=uid)
        branchprefix = branchdetails.prefix

        # Check branch type and redirect if it is subBranch
        if branchdetails.branchtype == "subBranch":
            return redirect('branchinvoiceConsignmentSub', track_id=track_id)

        for consignment in consignments:
            track_id = consignment.track_id
            if track_id not in grouped_userdata:
                grouped_userdata[track_id] = {field.name: getattr(consignment, field.name) for field in
                                              AddConsignment._meta.fields}

                grouped_userdata[track_id]['pieces'] = 0
                grouped_userdata[track_id]['products'] = []

            # Aggregate total pieces
            grouped_userdata[track_id]['pieces'] += consignment.pieces

            # Collect product details
            product_detail = consignment.desc_product
            grouped_userdata[track_id]['products'].append(product_detail)

            if consignment.copy_type not in copy_types:
                copy_types.append(consignment.copy_type)

        for track_id, details in grouped_userdata.items():
            details['products'] = ', '.join(details['products'])

    except ObjectDoesNotExist:
        grouped_userdata = {}

    return render(request, 'branchinvoiceConsignment.html', {
        'grouped_userdata': grouped_userdata,
        'branchdetails': branchdetails,
        'branchprefix': branchprefix,
        'copy_types': ', '.join(copy_types),  # Include the aggregated copy types

    })

def get_vehicle_numbers(request):
    query = request.GET.get('query', '')
    if query:
        vehicle_numbers = Vehicle.objects.filter(vehicle_number__icontains=query).values_list('vehicle_number',
                                                                                              flat=True)
        print('Vehicle numbers:', list(vehicle_numbers))  # Debugging: check the data in the terminal
        return JsonResponse(list(vehicle_numbers), safe=False)
    return JsonResponse([], safe=False)


def get_driver_name(request):
    query = request.GET.get('query', '')
    if query:
        driver_name = Driver.objects.filter(driver_name__icontains=query).values_list('driver_name', flat=True)
        print('Driver Name:', list(driver_name))  # Debugging: check the data in the terminal
        return JsonResponse(list(driver_name), safe=False)
    return JsonResponse([], safe=False)


def get_branch(request):
    query = request.GET.get('query', '')
    if query:
        companyname = Branch.objects.filter(companyname__icontains=query).values_list('companyname', flat=True)
        print('Branch Name:', list(companyname))  # Debugging: check the data in the terminal
        return JsonResponse(list(companyname), safe=False)
    return JsonResponse([], safe=False)


def get_destination(request):
    query = request.GET.get('query', '')
    if query:
        # Filter and get distinct route_to values
        route_to = AddConsignment.objects.filter(route_to__icontains=query).values_list('route_to',
                                                                                        flat=True).distinct()
        print('Distinct route_to numbers:', list(route_to))  # Debugging: check the data in the terminal
        return JsonResponse(list(route_to), safe=False)
    return JsonResponse([], safe=False)

def staff(request):
    if request.method == "POST":

        uid = request.session.get('username')
        branch = Branch.objects.get(email=uid)
        branchname = branch.companyname
        branchemail = branch.email

        staff = random.randint(111111, 999999)
        staffid = str(staff)

        staffname = request.POST.get('staffname')
        staffPhone = request.POST.get('staffPhone')
        staffaddress = request.POST.get('staffaddress')
        aadhar = request.POST.get('aadhar')
        passbook = request.POST.get('passbookno')

        passport = request.POST.get('passport')
        passbookphoto = request.POST.get('passport')

        passportfile = request.FILES['passport']
        fs = FileSystemStorage()
        filepassport = fs.save(passportfile.name, passportfile)
        upload_file_url = fs.url(filepassport)
        path = os.path.join(BASE_DIR, '/media/' + filepassport)

        passbookfile = request.FILES['passbook']
        fs = FileSystemStorage()
        filepassbook = fs.save(passportfile.name, passbookfile)
        upload_file_url = fs.url(filepassbook)
        path = os.path.join(BASE_DIR, '/media/' + filepassbook)

        utype = 'staff'

        if Login.objects.filter(username=staffPhone).exists():
            messages.error(request, 'Username (Phone) already exists.')
            return render(request, 'staff.html')

        Staff.objects.create(
            staffname=staffname,
            staffPhone=staffPhone,
            staffaddress=staffaddress,
            aadhar=aadhar,
            staffid=staffid,
            Branch=branchname,
            passport=passportfile,
            passbook=passbook,
            passbookphoto=passbookfile,
            branchemail=branchemail

        )
        Login.objects.create(utype=utype, username=staffPhone, password=staffid, name=staffname)

    return render(request, 'staff.html')


def view_staff(request):
    uid = request.session.get('username')
    branch = Branch.objects.get(email=uid)
    branchname = branch.companyname
    name = request.POST.get('name', '')
    if branch:
        # Filter staff data based on the branch name (case-insensitive search)
        staff_data = Staff.objects.filter(staffname__icontains=name, Branch=branchname)
    else:
        staff_data = Staff.objects.filter(Branch=branchname)
    return render(request, 'view_staff.html', {'data': staff_data})


def get_staff(request):
    query = request.GET.get('query', '')
    if query:
        staffname = Staff.objects.filter(staffname__icontains=query).values_list('staffname', flat=True)
        print('Staff Name:', list(staffname))  # Debugging: check the data in the terminal
        return JsonResponse(list(staffname), safe=False)
    return JsonResponse([], safe=False)


def delete_staff(request, pk):
    try:
        staff = Staff.objects.get(id=pk)

        user = Login.objects.filter(username=staff.staffPhone).first()
        if user:
            user.delete()
        staff.delete()

    except ObjectDoesNotExist:
        pass
    base_url = reverse('view_staff')
    return redirect(base_url)


def edit_staff(request, pk):
    # Retrieve the Staff record
    data = Staff.objects.filter(id=pk).first()  # Retrieve a single object or None

    if not data:
        return HttpResponse("Staff record not found.", status=404)

    # Store the original staffPhone
    original_staffPhone = data.staffPhone

    if request.method == "POST":
        # Get updated values from the POST request
        staffname = request.POST.get('staffname')
        staffPhone = request.POST.get('staffPhone')
        staffaddress = request.POST.get('staffaddress')
        aadhar = request.POST.get('aadhar')
        staffid = request.POST.get('staffid')

        # Update the Staff object
        data.staffname = staffname
        data.staffPhone = staffPhone
        data.staffaddress = staffaddress
        data.aadhar = aadhar
        data.staffid = staffid
        data.save()

        # Update the Login record using the original staffPhone
        user = Login.objects.filter(
            username=original_staffPhone).first()  # Fetch the user with the original phone number
        if user:
            user.username = staffPhone  # Update username to the new phone number
            user.name = staffname  # Update name
            user.password = staffid  # Update password if necessary
            user.save()

        # Redirect to a different URL after successful update
        base_url = reverse('view_staff')
        return redirect(base_url)

    return render(request, 'edit_staff.html', {'data': data})

from django.db.models import Max
from django.db import transaction


def addConsignment(request):
    if request.method == "POST":
        now = datetime.now().replace(microsecond=0)
        con_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")

        uid = request.session.get('username')
        branch = Staff.objects.get(staffPhone=uid)
        uname = branch.Branch
        branchemail = branch.branchemail
        username = branch.staffname

        branchdata = Branch.objects.get(email=branchemail)
        branchtype = branchdata.branchtype

        # Get the last track_id and increment it
        last_track_id = AddConsignment.objects.aggregate(Max('track_id'))['track_id__max']
        track_id = int(last_track_id) + 1 if last_track_id else 1  # Start from a defined base if no entries exist
        con_id = str(track_id)

        # Get the last Consignment_id and increment it
        last_con_id = AddConsignment.objects.aggregate(Max('Consignment_id'))['Consignment_id__max']
        Consignment_id = last_con_id + 1 if last_con_id else 1  # Start from a defined base if no entries exist
        Consignment_id = str(Consignment_id)

        # Sender details
        send_name = request.POST.get('a1')
        send_mobile = request.POST.get('a2')
        send_address = request.POST.get('a4')
        sender_GST = request.POST.get('sendergst')

        # Receiver details
        rec_name = request.POST.get('a5')
        rec_mobile = request.POST.get('a6')
        rec_address = request.POST.get('a8')
        rec_GST = request.POST.get('receivergst')

        copies = []
        if request.POST.get('consignor_copy'):
            copies.append('Consignor Copy')
        if request.POST.get('consignee_copy'):
            copies.append('Consignee Copy')
        if request.POST.get('lorry_copy'):
            copies.append('Lorry Copy')
        copy_type = ', '.join(copies)  # Combine into a single string

        # Create or update Consignor
        Consignor.objects.update_or_create(
            sender_name=send_name,
            defaults={
                'sender_mobile': send_mobile,
                'sender_address': send_address,
                'sender_GST': sender_GST,
                'branch': uname,
            }
        )

        # Create or update Consignee
        Consignee.objects.update_or_create(
            receiver_name=rec_name,
            defaults={
                'receiver_mobile': rec_mobile,
                'receiver_address': rec_address,
                'receiver_GST': rec_GST,
                'branch': uname,
            }
        )

        # Handling product entries
        products = request.POST.getlist('product[]')
        pieces = request.POST.getlist('pieces[]')

        # Other consignment details
        delivery = request.POST.get('delivery_option')
        prod_invoice = request.POST.get('prod_invoice')
        prod_price = request.POST.get('prod_price')
        weight = float(request.POST.get('weight') or 0)
        weightAmt = float(request.POST.get('weightAmt') or 0)
        freight = float(request.POST.get('freight') or 0)
        hamali = float(request.POST.get('hamali') or 0)
        door_charge = float(request.POST.get('door_charge') or 0)
        st_charge = float(request.POST.get('st_charge') or 0)
        cost = float(request.POST.get('cost') or 0)
        bal = float(request.POST.get('bal') or 0)
        route_from = request.POST.get('from')
        route_to = request.POST.get('to')
        eway_bill = request.POST.get('ewaybill_no')

        pay_status = request.POST.get('payment')

        utype = request.session.get('utype')
        branch_value = 'admin' if utype == 'admin' else uname

        # Determine the appropriate name based on pay_status
        if pay_status == 'Account':
            account_name = send_name
        elif pay_status == 'Consignee_AC':
            account_name = rec_name
        else:
            account_name = send_name  # Default to sender_name if pay_status is neither

        # Use transaction to ensure atomic operations
        with transaction.atomic():
            # Save aggregate data to AddConsignment and AddConsignmentTemp
            for product, piece in zip(products, pieces):
                # Skip rows where product or piece is empty
                if not product or not piece:
                    continue
                AddConsignment.objects.create(
                    track_id=con_id,
                    Consignment_id=Consignment_id,
                    sender_name=send_name,
                    sender_mobile=send_mobile,
                    sender_address=send_address,
                    sender_GST=sender_GST,
                    receiver_name=rec_name,
                    receiver_mobile=rec_mobile,
                    receiver_address=rec_address,
                    receiver_GST=rec_GST,
                    desc_product=product,
                    pieces=piece,
                    prod_invoice=prod_invoice,
                    prod_price=prod_price,
                    weightAmt=weightAmt,
                    weight=weight,
                    balance=bal,
                    freight=freight,
                    hamali=hamali,
                    door_charge=door_charge,
                    st_charge=st_charge,
                    route_from=route_from,
                    route_to=route_to,
                    total_cost=cost,
                    date=con_date,
                    pay_status=pay_status,
                    branch=branch_value,
                    name=username,
                    time=current_time,
                    delivery=delivery,
                    copy_type=copy_type,
                    eway_bill=eway_bill,
                    branchemail=branchemail
                )

            for product, piece in zip(products, pieces):
                # Skip rows where product or piece is empty
                if not product or not piece:
                    continue

                AddConsignmentTemp.objects.create(
                    track_id=con_id,
                    Consignment_id=Consignment_id,
                    sender_name=send_name,
                    sender_mobile=send_mobile,
                    sender_address=send_address,
                    sender_GST=sender_GST,
                    receiver_name=rec_name,
                    receiver_mobile=rec_mobile,
                    receiver_address=rec_address,
                    receiver_GST=rec_GST,
                    desc_product=product,
                    pieces=piece,  # Assign the current piece to the pieces field
                    prod_invoice=prod_invoice,
                    prod_price=prod_price,
                    weightAmt=weightAmt,
                    weight=weight,
                    balance=bal,
                    freight=freight,
                    hamali=hamali,
                    door_charge=door_charge,
                    st_charge=st_charge,
                    route_from=route_from,
                    route_to=route_to,
                    total_cost=cost,
                    date=con_date,
                    pay_status=pay_status,
                    branch=branch_value,
                    name=username,
                    time=current_time,
                    delivery=delivery,
                    copy_type=copy_type,
                    eway_bill=eway_bill,
                    branchemail=branchemail

                )

            # Only handle the Account model if pay_status is 'Shipper A/c' or 'Receiver A/C'
            if pay_status in ['Account', 'Consignee_AC']:
                try:
                    # Initialize balance based on sender_name if it's the first entry for that sender
                    previous_balance_entry = Account.objects.filter(sender_name=account_name).order_by('-Date').first()
                    if previous_balance_entry:
                        previous_balance = float(previous_balance_entry.Balance)
                    else:
                        previous_balance = 0.0  # Initialize balance to 0 if no previous entries

                    # Update the current balance for the sender
                    updated_balance = previous_balance + cost

                    print(f"Creating/Updating Account entry with track_number: {con_id}")
                    print(f"Pay Status: {pay_status}")
                    print(f"Sender Name: {account_name}")
                    print(f"Updated balance: {updated_balance}")

                    # Fetch or create the Account entry
                    account_entry, created = Account.objects.update_or_create(
                        track_number=con_id,
                        defaults={
                            'Date': now,
                            'debit': cost,
                            'credit': 0,
                            'TrType': "sal",
                            'particulars': f"{con_id} Amount Debited",
                            'Balance': updated_balance,
                            'sender_name': account_name,
                            'headname': username,
                            'Branch': branch_value
                        }
                    )
                    print(f"Account entry {'created' if created else 'updated'}: {account_entry}")

                except Exception as e:
                    print(f"Error updating Account table: {e}")
            # Redirect to a success page or another relevant page
            if branchtype == "mainBranch":
                return redirect('printConsignment', track_id=con_id)
            elif branchtype == "subBranch":
                return redirect('printConsignmentSub', track_id=con_id)
    else:
        # Fetch the vehicle numbers from the Driver model
        vehicle_numbers = Vehicle.objects.values_list('vehicle_number', flat=True)

        # Pass vehicle numbers to the template
        return render(request, 'addConsignment.html', {'vehicle_numbers': vehicle_numbers})


def printConsignment(request, track_id):
    grouped_userdata = {}
    copy_types = []

    try:
        consignments = AddConsignment.objects.filter(track_id=track_id)
        uid = request.session.get('username')

        staff = Staff.objects.get(staffPhone=uid)
        user_branch = staff.Branch  # Adjust if the branch info is stored differently
        branchemail = staff.branchemail
        branchdetails = Branch.objects.get(email=branchemail)
        branchprefix = branchdetails.prefix

        for consignment in consignments:
            track_id = consignment.track_id
            if track_id not in grouped_userdata:
                grouped_userdata[track_id] = {field.name: getattr(consignment, field.name) for field in
                                              AddConsignment._meta.fields}

                grouped_userdata[track_id]['pieces'] = 0
                grouped_userdata[track_id]['products'] = []

            # Aggregate total pieces
            grouped_userdata[track_id]['pieces'] += consignment.pieces

            # Collect product details
            product_detail = consignment.desc_product
            grouped_userdata[track_id]['products'].append(product_detail)

            if consignment.copy_type not in copy_types:
                copy_types.append(consignment.copy_type)

        for track_id, details in grouped_userdata.items():
            details['products'] = ', '.join(details['products'])

    except ObjectDoesNotExist:
        grouped_userdata = {}

    return render(request, 'printConsignment.html', {
        'grouped_userdata': grouped_userdata,
        'branchdetails': branchdetails,
        'branchprefix': branchprefix

    })

def invoiceConsignment(request, track_id):
    grouped_userdata = {}
    copy_types = []

    try:
        # Filter consignments by track_id
        consignments = AddConsignment.objects.filter(track_id=track_id)
        # Get common details from the first consignment
        consignment = consignments.first()

        # Fetch the branch name from the consignment
        branch_name = consignment.branch  # Adjust this field based on your model
        branchemail = consignment.branchemail

        # Fetch branch details using the branch name
        branchdetails = get_object_or_404(Branch, email=branchemail)
        branchprefix = branchdetails.prefix

        if not consignments.exists():
            return render(request, '404.html')  # Handle the case where no consignments are found.

        for consignment in consignments:
            track_id = consignment.track_id
            if track_id not in grouped_userdata:
                grouped_userdata[track_id] = {field.name: getattr(consignment, field.name) for field in
                                              AddConsignment._meta.fields}

                grouped_userdata[track_id]['pieces'] = 0
                grouped_userdata[track_id]['products'] = []

            # Aggregate total pieces
            grouped_userdata[track_id]['pieces'] += consignment.pieces

            # Collect product details
            product_detail = consignment.desc_product
            grouped_userdata[track_id]['products'].append(product_detail)

            if consignment.copy_type not in copy_types:
                copy_types.append(consignment.copy_type)

        for track_id, details in grouped_userdata.items():
            details['products'] = ', '.join(details['products'])

    except ObjectDoesNotExist:
        grouped_userdata = {}

    return render(request, 'invoiceConsignment.html', {
        'grouped_userdata': grouped_userdata,
        'branchdetails': branchdetails,
        'branchprefix': branchprefix
    })


def view_consignment(request):
    uid = request.session.get('username')
    grouped_userdata = {}

    if uid:
        try:
            from_date_str = request.POST.get('from_date')
            to_date_str = request.POST.get('to_date')

            consigner = request.POST.get('consigner')
            consigee = request.POST.get('consignee')
            track_id = request.POST.get('lrno')

            # Parse dates
            from_date = parse_date(from_date_str) if from_date_str else None
            to_date = parse_date(to_date_str) if to_date_str else None

            # Fetch the staff and associated branch
            staff = Staff.objects.get(staffPhone=uid)
            user_branch = staff.Branch  # Adjust if the branch info is stored differently
            branchemail = staff.branchemail

            branch = Branch.objects.get(email=branchemail)
            branchprefix = branch.prefix

            # Start building the query
            consignments = AddConsignment.objects.filter(branchemail=branchemail)

            if consigner:
                consignments = consignments.filter(sender_name=consigner)
            if consigee:
                consignments = consignments.filter(receiver_name=consigee)
            if track_id:
                consignments = consignments.filter(track_id=track_id)

            if from_date and to_date:
                consignments = consignments.filter(date__range=(from_date, to_date))
            elif from_date:
                consignments = consignments.filter(date__gte=from_date)
            elif to_date:
                consignments = consignments.filter(date__lte=to_date)

            # Group consignments by track_id and concatenate product details
            for consignment in consignments:
                track_id = consignment.track_id
                if track_id not in grouped_userdata:
                    grouped_userdata[track_id] = {
                        'route_from': consignment.route_from,
                        'route_to': consignment.route_to,
                        'sender_name': consignment.sender_name,
                        'sender_mobile': consignment.sender_mobile,
                        'receiver_name': consignment.receiver_name,
                        'receiver_mobile': consignment.receiver_mobile,
                        'total_cost': 0,
                        'pieces': 0,
                        'weight': consignment.weight,
                        'pay_status': consignment.pay_status,
                        'prefix': branchprefix,
                        'products': []
                    }
                # Aggregate total cost and pieces
                grouped_userdata[track_id]['total_cost'] += consignment.total_cost
                grouped_userdata[track_id]['pieces'] += consignment.pieces

                # Concatenate product details without ID
                product_detail = consignment.desc_product
                grouped_userdata[track_id]['products'].append(product_detail)

        except ObjectDoesNotExist:
            # In case of staff or branch not found, return an empty set
            grouped_userdata = {}

    # Convert the list of product details to a single string
    for track_id, details in grouped_userdata.items():
        details['products'] = ', '.join(details['products'])

    return render(request, 'view_consignment.html', {'grouped_userdata': grouped_userdata})

def adminExpenses(request):
    return render(request, 'adminExpenses.html')


def saveadminExpenses(request):
    if request.method == 'POST':
        uid = request.session.get('username')
        if uid:
            try:
                branch = Login.objects.get(username=uid)
                branchname = branch.utype
                username = branch.name

                # Parse and validate date
                date_str = request.POST.get('date')
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    print("Invalid date format.")  # Debugging statement
                    return redirect('adminExpenses')

                amount = request.POST.get('amt')
                reason = request.POST.get('reason')
                salaryDetails = request.POST.get('salaryDetails')

                Expenses.objects.create(
                    Date=date,
                    Reason=reason,
                    Amount=amount,
                    staffname=salaryDetails,
                    username=username,
                    branch=branchname
                )
            except Branch.DoesNotExist:
                print("Branch does not exist.")  # Debugging statement
        else:
            print("No username found in session.")  # Debugging statement

        return redirect('adminExpenses')  # Replace with your desired success URL

    return render(request, 'adminExpenses.html')


def adminViewExpenses(request):
    expenses = []
    if request.method == 'POST':
        from_date_str = request.POST.get('from_date')
        to_date_str = request.POST.get('to_date')

        if from_date_str and to_date_str:
            try:
                # Parse the date strings into datetime objects
                from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
                to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()

                expenses = Expenses.objects.filter(Date__range=(from_date, to_date))

            except ValueError:
                print("Invalid date format.")  # Handle invalid date formats
        else:
            print("Both from_date and to_date are required.")
    return render(request, 'adminViewExpenses.html', {'expenses': expenses})

def branchConsignorView(request):
    uid = request.session.get('username')
    if uid:
        branch = Branch.objects.get(email=uid)
        branchname = branch.companyname
        consignor = Consignor.objects.filter(branch=branchname)
    return render(request, 'branchConsignorView.html', {'consignor': consignor})


def branchConsigneeView(request):
    uid = request.session.get('username')
    if uid:
        branch = Branch.objects.get(email=uid)
        branchname = branch.companyname
        consignee = Consignee.objects.filter(branch=branchname)
    return render(request, 'branchConsigneeView.html', {'consignee': consignee})


def adminConsignorView(request):
    consignor = Consignor.objects.all()  # Initialize consignee as an empty list

    if request.method == 'POST':
        consignor = Consignor.objects.all()
        print(f"Consignee: {consignor}")  # Debugging: Print the consignee queryset

    return render(request, 'adminConsignorView.html', {'consignor': consignor})


def adminConsigneeView(request):
    consignee = []  # Initialize consignee as an empty list

    if request.method == 'POST':
        branch = request.POST.get('t2')
        print(f"Branch: {branch}")  # Debugging: Print the branch name
        consignee = Consignee.objects.filter(branch=branch)
        print(f"Consignee: {consignee}")  # Debugging: Print the consignee queryset

    return render(request, 'adminConsigneeView.html', {'consignee': consignee})


def adminstaff_view(request):
    branch = request.POST.get('branch', '')
    if branch:
        # Filter staff data based on the branch name (case-insensitive search)
        staff_data = Staff.objects.filter(Branch__icontains=branch)
    else:
        # If no branch is provided, fetch all staff data
        staff_data = Staff.objects.all()

    # Render the template with the filtered data
    return render(request, 'adminstaff_view.html', {'data': staff_data, 'branch': branch})


from django.utils.dateparse import parse_date


def adminView_Consignment(request):
    grouped_userdata = {}  # Initialize as an empty dictionary to group data

    # Start with a base queryset
    queryset = AddConsignment.objects.all()

    if request.method == 'POST':
        branch = request.POST.get('t2')
        from_date_str = request.POST.get('from_date')
        to_date_str = request.POST.get('to_date')
        consigner = request.POST.get('consigner')
        consignee = request.POST.get('consignee')
        track_id = request.POST.get('lrno')

        # Parse dates
        from_date = parse_date(from_date_str) if from_date_str else None
        to_date = parse_date(to_date_str) if to_date_str else None

        print("Branch: {}".format(branch))  # Debugging: Print the branch name
        print("From Date: {}".format(from_date))  # Debugging: Print the from date
        print("To Date: {}".format(to_date))  # Debugging: Print the to date

        # Apply filters only if they are provided
        if branch:
            queryset = queryset.filter(branch=branch)
        if consigner:
            queryset = queryset.filter(sender_name=consigner)
        if consignee:
            queryset = queryset.filter(receiver_name=consignee)
        if track_id:
            queryset = queryset.filter(track_id=track_id)

        # Apply date filters
        if from_date and to_date:
            queryset = queryset.filter(date__range=(from_date, to_date))
        elif from_date:
            queryset = queryset.filter(date__gte=from_date)
        elif to_date:
            queryset = queryset.filter(date__lte=to_date)

    # Group consignments by track_id and concatenate product details
    for consignment in queryset:
        track_id = consignment.track_id

        try:
            branch = Branch.objects.get(email=consignment.branchemail)
            branch_prefix = branch.prefix  # Get the prefix from the Branch model
        except Branch.DoesNotExist:
            branch_prefix = "Unknown"  # If no Branch is found, set to "Unknown"

        if track_id not in grouped_userdata:
            grouped_userdata[track_id] = {
                'branch': consignment.branch,
                'route_from': consignment.route_from,
                'route_to': consignment.route_to,
                'sender_name': consignment.sender_name,
                'sender_mobile': consignment.sender_mobile,
                'receiver_name': consignment.receiver_name,
                'receiver_mobile': consignment.receiver_mobile,
                'total_cost': 0,
                'pieces': 0,
                'weight': consignment.weight,
                'pay_status': consignment.pay_status,
                'prefix': branch_prefix,  # Add the prefix here
                'products': []
            }
        # Aggregate total cost and pieces
        # Aggregate total cost and pieces, ensuring total_cost defaults to 0 if None
        grouped_userdata[track_id]['total_cost'] += (consignment.total_cost or 0)
        grouped_userdata[track_id]['pieces'] += (consignment.pieces or 0)

        # Concatenate product details without ID
        product_detail = consignment.desc_product
        grouped_userdata[track_id]['products'].append(product_detail)

    # Convert the list of product details to a single string
    for track_id, details in grouped_userdata.items():
        details['products'] = ', '.join(details['products'])

    # Render the template with grouped data
    return render(request, 'adminView_Consignment.html', {'grouped_userdata': grouped_userdata})


def admininvoiceConsignment(request, track_id):
    grouped_userdata = {}
    copy_types = []

    try:
        # Filter consignments by track_id
        consignments = AddConsignment.objects.filter(track_id=track_id)
        # Get common details from the first consignment
        consignment = consignments.first()

        # Fetch the branch name from the consignment
        branchemail = consignment.branchemail
        branch_name = consignment.branch  # Adjust this field based on your model

        # Fetch branch details using the branch name
        branchdetails = get_object_or_404(Branch, email=branchemail)
        branchprefix = branchdetails.prefix

        if not consignments.exists():
            return render(request, '404.html')  # Handle the case where no consignments are found.

        for consignment in consignments:
            track_id = consignment.track_id
            if track_id not in grouped_userdata:
                grouped_userdata[track_id] = {field.name: getattr(consignment, field.name) for field in
                                              AddConsignment._meta.fields}

                grouped_userdata[track_id]['pieces'] = 0
                grouped_userdata[track_id]['products'] = []

            # Aggregate total pieces
            grouped_userdata[track_id]['pieces'] += consignment.pieces

            # Collect product details
            product_detail = consignment.desc_product
            grouped_userdata[track_id]['products'].append(product_detail)

            if consignment.copy_type not in copy_types:
                copy_types.append(consignment.copy_type)

        for track_id, details in grouped_userdata.items():
            details['products'] = ', '.join(details['products'])

    except ObjectDoesNotExist:
        grouped_userdata = {}

    return render(request, 'admininvoiceConsignment.html', {
        'grouped_userdata': grouped_userdata,
        'branchdetails': branchdetails,
        'branchprefix': branchprefix
    })


def payment_history(request):
    return render(request, 'payment_history.html')

def adminPaymentHistory(request):
    return render(request, 'adminPaymentHistory.html')


def adminfetch_details(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    consignor_id = request.GET.get('a1')


    current_date = datetime.today().strftime('%d-%m-%Y')  # Format as 'DD-MM-YYYY'

    if from_date:
        from_date1 = datetime.strptime(from_date, '%Y-%m-%d').strftime('%d-%m-%Y')
    if to_date:
        to_date1 = datetime.strptime(to_date, '%Y-%m-%d').strftime('%d-%m-%Y')

    # Query the consignments based on the filters
    consignments = AddConsignment.objects.filter(pay_status='Account')

    if from_date:
        consignments = consignments.filter(date__gte=from_date)
    if to_date:
        consignments = consignments.filter(date__lte=to_date)
    if consignor_id:
        consignments = consignments.filter(sender_name=consignor_id)


    # Group consignments by track_id and process desc_product and pieces
    grouped_data = defaultdict(lambda: {
        'track_id': '',
        'date': '',
        'prod_invoice': '',
        'route_to': '',
        'freight': '',
        'st_charge': '',
        'sender_name': '',
        'receiver_name': '',
        'desc_product': '',
        'pay_status': '',
        'pieces': 0,  # Initialize pieces to 0 for summing
        'total_cost': 0
    })

    for consignment in consignments:
        track_id = consignment.track_id
        if track_id not in grouped_data:
            # Initialize data for the new track_id
            grouped_data[track_id]['track_id'] = track_id
            grouped_data[track_id]['date'] = consignment.date
            grouped_data[track_id]['prod_invoice'] = consignment.prod_invoice  # Assuming prod_invoice exists on consignment
            grouped_data[track_id]['freight'] = consignment.freight  # Assuming prod_invoice exists on consignment
            grouped_data[track_id]['st_charge'] = consignment.st_charge  # Assuming prod_invoice exists on consignment
            grouped_data[track_id]['route_to'] = consignment.route_to  # Assuming route_to exists on consignment
            grouped_data[track_id]['sender_name'] = consignment.sender_name
            grouped_data[track_id]['receiver_name'] = consignment.receiver_name
            grouped_data[track_id]['pay_status'] = consignment.pay_status
            grouped_data[track_id]['total_cost'] = consignment.total_cost

        # Concatenate pieces and desc_product
        grouped_data[track_id]['pieces'] += consignment.pieces  # Sum up pieces
        if grouped_data[track_id]['desc_product']:
            grouped_data[track_id]['desc_product'] += ', ' + consignment.desc_product
        else:
            grouped_data[track_id]['desc_product'] = consignment.desc_product

    # Prepare the data for the response
    data = list(grouped_data.values())

    # Get consignor details
    consignor = None
    if consignor_id:
        try:
            consignor = Consignor.objects.get(sender_name__iexact=consignor_id)
        except Consignor.DoesNotExist:
            consignor = None  # If no consignor found, keep consignor as None
    print(f"Consignor ID: {consignor_id}")
    print(request.GET)

    context = {
        'consignments': data,
        'from_date': from_date1,
        'to_date': to_date1,
        'consignor_id': consignor_id,
        'consignor': consignor,  # Make sure to pass consignor as singular object
        'current_date': current_date,  # Pass current date to the template

    }

    return render(request, 'adminPaymentHistory.html', context)

def credit(request):
    credit = Account.objects.all()
    return render(request, 'credit.html', {'credit': credit})

def fetch_details(request):
    uid = request.session.get('username')

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    pay_status = request.GET.get('pay_status')
    consignor_id = request.GET.get('consignor_id')
    consignee_id = request.GET.get('consignee_id')

    # Initialize an empty queryset
    consignments = AddConsignment.objects.none()
    data = []
    if uid:
        try:
            # Fetch the branch of the logged-in user
            branch = Staff.objects.get(staffPhone=uid).Branch

            # Start with filtering consignments by branch
            consignments = AddConsignment.objects.filter(branch=branch)

            # Further filter consignments based on the provided parameters
            if consignor_id:
                consignments = consignments.filter(sender_name__icontains=consignor_id)
            if consignee_id:
                consignments = consignments.filter(receiver_name__icontains=consignee_id)
            if from_date and to_date:
                from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
                consignments = consignments.filter(date__range=(from_date, to_date))

            # Handle pay_status filtering
            if pay_status and pay_status != 'all':
                consignments = consignments.filter(pay_status__icontains=pay_status)

            # Group consignments by track_id
            grouped_data = defaultdict(lambda: {
                'track_id': '',
                'sender_name': '',
                'receiver_name': '',
                'desc_product': '',
                'pay_status': '',
                'pieces': '',
                'total_cost': 0
            })

            for consignment in consignments:
                track_id = consignment.track_id
                if track_id not in grouped_data:
                    grouped_data[track_id]['track_id'] = track_id
                    grouped_data[track_id]['sender_name'] = consignment.sender_name
                    grouped_data[track_id]['receiver_name'] = consignment.receiver_name
                    grouped_data[track_id]['pay_status'] = consignment.pay_status
                    grouped_data[track_id]['total_cost'] = consignment.total_cost

                # Concatenate pieces and desc_product as strings
                if grouped_data[track_id]['pieces']:
                    grouped_data[track_id]['pieces'] += consignment.pieces
                else:
                    grouped_data[track_id]['pieces'] = consignment.pieces

                if grouped_data[track_id]['desc_product']:
                    grouped_data[track_id]['desc_product'] += ', ' + consignment.desc_product
                else:
                    grouped_data[track_id]['desc_product'] = consignment.desc_product

            # Prepare the data for JSON response
            data = list(grouped_data.values())
        except Staff.DoesNotExist:
            print("Staff does not exist for the provided uid.")  # Handle case where Staff does not exist

    return JsonResponse({'data': data})


def branchfetch_details(request):
    uid = request.session.get('username')

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    pay_status = request.GET.get('pay_status')
    consignor_id = request.GET.get('consignor_id')
    consignee_id = request.GET.get('consignee_id')

    # Initialize data and consignments
    consignments = AddConsignment.objects.none()
    data = []

    if uid:
        try:
            # Fetch the branch of the logged-in user
            branch = Branch.objects.get(email=uid)
            uname = branch.companyname

            # Start with filtering consignments by branch
            consignments = AddConsignment.objects.filter(branch=uname)

            # Further filter consignments based on the provided parameters
            if consignor_id:
                consignments = consignments.filter(sender_name__icontains=consignor_id)
            if consignee_id:
                consignments = consignments.filter(receiver_name__icontains=consignee_id)
            if from_date and to_date:
                from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
                consignments = consignments.filter(date__range=(from_date, to_date))
            if pay_status and pay_status != 'all':
                consignments = consignments.filter(pay_status__icontains=pay_status)

            # Group consignments by track_id
            grouped_data = defaultdict(lambda: {
                'track_id': '',
                'sender_name': '',
                'receiver_name': '',
                'desc_product': '',
                'pay_status': '',
                'pieces': '',
                'total_cost': 0
            })

            for consignment in consignments:
                track_id = consignment.track_id
                if track_id not in grouped_data:
                    grouped_data[track_id]['track_id'] = track_id
                    grouped_data[track_id]['sender_name'] = consignment.sender_name
                    grouped_data[track_id]['receiver_name'] = consignment.receiver_name
                    grouped_data[track_id]['pay_status'] = consignment.pay_status
                    grouped_data[track_id]['total_cost'] = consignment.total_cost

                # Concatenate pieces and desc_product as strings
                if grouped_data[track_id]['pieces']:
                    grouped_data[track_id]['pieces'] += consignment.pieces
                else:
                    grouped_data[track_id]['pieces'] = consignment.pieces

                if grouped_data[track_id]['desc_product']:
                    grouped_data[track_id]['desc_product'] += ', ' + consignment.desc_product
                else:
                    grouped_data[track_id]['desc_product'] = consignment.desc_product

                # Sum up total costs

            # Prepare the data for JSON response
            data = list(grouped_data.values())
        except Branch.DoesNotExist:
            print("Branch does not exist for the provided uid.")  # Handle case where Branch does not exist

    # Include the uid in the response data
    return JsonResponse({'uid': uid, 'data': data})

def fetch_consignments(request):
    consignments = AddConsignment.objects.all()
    consignments_data = [
        {
            'id': consignment.id,
            'track_id': consignment.track_id,
            'sender_name': consignment.sender_name,
            'receiver_name': consignment.receiver_name,
        }
        for consignment in consignments
    ]
    return JsonResponse(consignments_data, safe=False)

@csrf_exempt
def fetch_balance(request):
    uid = request.session.get('username')

    if uid:
        try:
            # Fetch the branch of the logged-in user
            branch = Staff.objects.get(staffPhone=uid).Branch

            if request.method == 'GET':
                sender_name = request.GET.get('sender_name')
                if sender_name:
                    # Filter accounts by sender_name and branch
                    accounts = Account.objects.filter(sender_name=sender_name, Branch=branch)
                    if accounts.exists():
                        latest_account = accounts.latest('Date')  # Get the latest record by date
                        return JsonResponse({'balance': latest_account.Balance})
                    return JsonResponse({'balance': '0'})  # Default if no records found
                return JsonResponse({'status': 'error', 'message': 'Sender name is required'})
            return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
        except Branch.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Branch does not exist for this user'})


@csrf_exempt
def submit_credit(request):
    if request.method == 'POST':
        uid = request.session.get('username')

        consignor_name = request.POST.get('consignor_name')
        credit_amount = request.POST.get('credit_amount')
        desc = request.POST.get('desc')
        now = datetime.now().replace(microsecond=0)

        if consignor_name and credit_amount:
            try:

                branch = Staff.objects.get(staffPhone=uid)
                username = branch.staffname
                branchname = branch.Branch
                # Fetch all matching records
                accounts = Account.objects.filter(sender_name=consignor_name)

                if accounts.exists():
                    # Get the latest account for calculating the new balance
                    latest_account = accounts.latest('Date')  # Assuming you want to get the latest record

                    # Calculate the new balance
                    new_balance = float(latest_account.Balance) - float(credit_amount)

                    # Create a new record with updated balance
                    new_account = Account(
                        sender_name=consignor_name,
                        credit=credit_amount,
                        debit='0',
                        TrType="ReCap",
                        particulars=desc,  # Set debit to zero
                        Balance=str(new_balance),  # Set the new balance
                        Date=now,  # Use the date of the latest record or set to current date
                        headname=username,
                        Branch=branchname
                    )
                    new_account.save()

                    return JsonResponse({'status': 'success'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'No account found with the given sender name'})

            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})

        return JsonResponse({'status': 'error', 'message': 'Invalid data'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def credit_print(request):
    credit = Account.objects.all()
    return render(request, 'credit_print.html', {'credit': credit})

@csrf_exempt
def branchfetch_balance(request):
    uid = request.session.get('username')

    if uid:
        try:
            # Fetch the branch of the logged-in user
            branch = Branch.objects.get(email=uid).companyname

            if request.method == 'GET':
                sender_name = request.GET.get('sender_name')
                if sender_name:
                    # Filter accounts by sender_name and branch
                    accounts = Account.objects.filter(sender_name=sender_name, Branch=branch)
                    if accounts.exists():
                        latest_account = accounts.latest('Date')  # Get the latest record by date
                        return JsonResponse({'balance': latest_account.Balance})
                    return JsonResponse({'balance': '0'})  # Default if no records found
                return JsonResponse({'status': 'error', 'message': 'Sender name is required'})
            return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
        except Branch.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Branch does not exist for this user'})


def branchPaymenyHistory(request):
    return render(request, 'branchPaymenyHistory.html')


def branchcredit(request):
    credit = Account.objects.all()
    return render(request, 'branchcredit.html', {'credit': credit})


import logging

logger = logging.getLogger(__name__)


@csrf_exempt
def branchsubmit_credit(request):
    if request.method == 'POST':
        uid = request.session.get('username')

        consignor_name = request.POST.get('consignor_name')
        credit_amount = request.POST.get('credit_amount')
        desc = request.POST.get('desc')
        now = datetime.now().replace(microsecond=0)

        if consignor_name and credit_amount:
            try:

                branch = Branch.objects.get(email=uid)
                username = branch.headname
                branchcompany = branch.companyname
                # Fetch all matching records
                accounts = Account.objects.filter(sender_name=consignor_name)

                if accounts.exists():
                    # Get the latest account for calculating the new balance
                    latest_account = accounts.latest('Date')  # Assuming you want to get the latest record

                    # Calculate the new balance
                    new_balance = float(latest_account.Balance) - float(credit_amount)

                    # Create a new record with updated balance
                    new_account = Account(
                        sender_name=consignor_name,
                        credit=credit_amount,
                        debit='0',
                        TrType="ReCap",
                        particulars=desc,  # Set debit to zero
                        Balance=str(new_balance),  # Set the new balance
                        Date=now,  # Use the date of the latest record or set to current date
                        headname=username,
                        Branch=branchcompany
                    )
                    new_account.save()

                    return JsonResponse({'status': 'success'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'No account found with the given sender name'})

            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})

        return JsonResponse({'status': 'error', 'message': 'Invalid data'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def branchcredit_print(request):
    credit = Account.objects.all()
    return render(request, 'branchcredit_print.html', {'credit': credit})

# Set up logging
import logging

logger = logging.getLogger(__name__)


def branchfetch_account_details(request):
    if request.method == 'POST':
        uid = request.session.get('username')

        sender_name = request.POST.get('sender_name')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')

        logger.info(f"Received request with sender_name: {sender_name}, from_date: {from_date}, to_date: {to_date}")

        # Check if the required parameters are provided
        if sender_name and from_date and to_date:
            try:
                branch = Branch.objects.get(email=uid).companyname

                # Convert from_date and to_date to proper datetime objects
                from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

                # Ensure the end date includes the entire day
                to_date_end = to_date + timedelta(days=1)

                # Fetch all accounts based on sender_name, branch, and date range
                accounts = Account.objects.filter(
                    sender_name=sender_name,
                    Branch=branch,
                    Date__gte=from_date,
                    Date__lt=to_date_end
                ).values(
                    'Date', 'track_number', 'TrType', 'particulars', 'debit', 'credit', 'Balance'
                ).order_by('Date')  # Order by date if needed

                logger.info(f"Fetched accounts: {list(accounts)}")

                return render(request, 'branchcredit_print.html', {
                    'accounts': accounts,
                    'sender_name': sender_name,
                    'from_date_str': from_date,
                    'to_date_str': to_date,
                    'branch': branch
                })

            except ValueError:
                logger.error("Invalid date format")
                return render(request, 'branchcredit_print.html', {'error': 'Invalid date format'})

    logger.error("Missing required parameters")
    return render(request, 'branchcredit_print.html', {'error': 'Missing required parameters'})


logger = logging.getLogger(__name__)


@csrf_exempt
def fetch_account_details(request):
    if request.method == 'POST':

        uid = request.session.get('username')

        sender_name = request.POST.get('sender_name')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')

        logger.info(f"Received request with sender_name: {sender_name}, from_date: {from_date}, to_date: {to_date}")

        # Check if the required parameters are provided
        if sender_name and from_date and to_date:
            try:
                branch = Staff.objects.get(staffPhone=uid).Branch

                # Convert from_date and to_date to proper datetime objects
                from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

                # Ensure the end date includes the entire day
                to_date_end = to_date + timedelta(days=1)

                # Fetch all accounts based on sender_name, branch, and date range
                accounts = Account.objects.filter(
                    sender_name=sender_name,
                    Branch=branch,
                    Date__gte=from_date,
                    Date__lt=to_date_end
                ).values(
                    'Date', 'track_number', 'TrType', 'particulars', 'debit', 'credit', 'Balance'
                ).order_by('Date')  # Order by date if needed

                logger.info(f"Fetched accounts: {list(accounts)}")

                return render(request, 'staffcredit_print.html', {
                    'accounts': accounts,
                    'sender_name': sender_name,
                    'from_date_str': from_date,
                    'to_date_str': to_date,
                    'branch': branch
                })

            except ValueError:
                logger.error("Invalid date format")
                return render(request, 'staffcredit_print.html', {'error': 'Invalid date format'})

    logger.error("Missing required parameters")
    return render(request, 'staffcredit_print.html', {'error': 'Missing required parameters'})

@csrf_exempt
def adminfetch_account_details(request):
    if request.method == 'POST':

        sender_name = request.POST.get('sender_name')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')

        logger.info(f"Received request with sender_name: {sender_name}, from_date: {from_date}, to_date: {to_date}")

        # Check if the required parameters are provided
        if sender_name and from_date and to_date:
            try:

                # Convert from_date and to_date to proper datetime objects
                from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

                # Ensure the end date includes the entire day
                to_date_end = to_date + timedelta(days=1)

                # Fetch all accounts based on sender_name, branch, and date range
                accounts = Account.objects.filter(
                    sender_name=sender_name,
                    Date__gte=from_date,
                    Date__lt=to_date_end
                ).values(
                    'Date', 'track_number', 'TrType', 'particulars', 'debit', 'credit', 'Balance'
                ).order_by('Date')  # Order by date if needed

                logger.info(f"Fetched accounts: {list(accounts)}")

                return render(request, 'account_report.html', {
                    'accounts': accounts,
                    'sender_name': sender_name,
                    'from_date_str': from_date,
                    'to_date_str': to_date,
                    'branch': branch
                })

            except ValueError:
                logger.error("Invalid date format")
                return render(request, 'account_report.html', {'error': 'Invalid date format'})

    logger.error("Missing required parameters")
    return render(request, 'account_report.html', {'error': 'Missing required parameters'})

def consignorMaster(request):
    if request.method == "POST":
        send_name = request.POST.get('a1')
        send_mobile = request.POST.get('a2')
        send_address = request.POST.get('a4')
        sender_GST = request.POST.get('sendergst')


        # Create or update Consignor
        Consignor.objects.create(
            sender_name=send_name,
                sender_mobile=send_mobile,
                sender_address= send_address,
                sender_GST= sender_GST,

        )


    messages.success(request, 'Data created successfully.')

    return render(request, 'consignorMaster.html')

def consigneeMaster(request):
    if request.method == "POST":

        # Receiver details
        rec_name = request.POST.get('a5')
        rec_mobile = request.POST.get('a6')
        rec_address = request.POST.get('a8')
        rec_GST = request.POST.get('receivergst')

        # Create or update Consignee
        Consignee.objects.create(
                receiver_name=rec_name,
                receiver_mobile= rec_mobile,
                receiver_address= rec_address,
                receiver_GST= rec_GST,
        )

    messages.success(request, 'Data created successfully.')

    return render(request, 'consigneeMaster.html')


def addLHS(request):
    route_to = AddConsignmentTemp.objects.values_list('route_to', flat=True).distinct()
    addtrip = defaultdict(
        lambda: {'desc_product': [], 'pieces': 0, 'receiver_name': '', 'pay_status': '', 'route_to': '', 'total': '',
                 'weightAMt': '', 'freight': '', 'hamali': '', 'door_charge': '', 'st_charge': ''})
    no_data_found = False  # Flag to check if data was found

    uid = request.session.get('username')
    if uid:
        try:
            branch = Branch.objects.get(email=uid)
            user_branch = branch.companyname

            if request.method == 'POST':
                route_to = request.POST.get('dest')

                if user_branch:
                    consignments = AddConsignmentTemp.objects.filter(
                        route_to=route_to,
                        branch=user_branch
                    )

                    if consignments.exists():
                        for consignment in consignments:
                            consignment_data = addtrip[consignment.track_id]
                            consignment_data['desc_product'].append(consignment.desc_product)
                            consignment_data['pieces'] += consignment.pieces
                            consignment_data['route_to'] = consignment.route_to
                            consignment_data['receiver_name'] = consignment.receiver_name
                            consignment_data['pay_status'] = consignment.pay_status
                            consignment_data['total_cost'] = consignment.total_cost
                            consignment_data['weightAmt'] = consignment.weightAmt
                            consignment_data['freight'] = consignment.freight
                            consignment_data['hamali'] = consignment.hamali
                            consignment_data['door_charge'] = consignment.door_charge
                            consignment_data['st_charge'] = consignment.st_charge
                    else:
                        no_data_found = True  # Set the flag if no data is found

            addtrip = [
                {
                    'track_id': track_id,
                    'desc_product': ', '.join(consignment_data['desc_product']),
                    'pieces': consignment_data['pieces'],
                    'route_to': consignment_data['route_to'],
                    'receiver_name': consignment_data['receiver_name'],
                    'pay_status': consignment_data['pay_status'],
                    'total_cost': consignment_data['total_cost'],
                    'weightAmt': consignment_data['weightAmt'],
                    'freight': consignment_data['freight'],
                    'hamali': consignment_data['hamali'],
                    'door_charge': consignment_data['door_charge'],
                    'st_charge': consignment_data['st_charge']
                }
                for track_id, consignment_data in addtrip.items()
            ]

        except Branch.DoesNotExist:
            addtrip = []
            no_data_found = True  # Set the flag if the branch does not exist

    return render(request, 'addLHS.html', {
        'route_to': route_to,
        'trip': addtrip,
        'no_data_found': no_data_found  # Pass the flag to the template
    })

def saveLHSList(request):
    print("saveTripSheet function called")
    if request.method == 'POST':
        print("POST request received")  # Debugging statement


        uid = request.session.get('username')
        if uid:
            try:
                branch = Branch.objects.get(email=uid)
                branchname = branch.companyname
                username = branch.headname

                now = datetime.now()
                con_date = now.strftime("%Y-%m-%d")
                current_time = now.strftime("%H:%M:%S")


                total_rows = int(request.POST.get('total_rows', 0))


                selected_rows = request.POST.getlist('selected_rows')

                for i in range(1, total_rows + 1):
                    if str(i) in selected_rows:  # Only process if the row is selected
                        track_id = request.POST.get(f'track_id_{i}')
                        pieces = request.POST.get(f'pieces_{i}')
                        desc_product = request.POST.get(f'desc_product_{i}')
                        route_to = request.POST.get(f'route_to_{i}')
                        receiver_name = request.POST.get(f'receiver_name_{i}')
                        pay_status = request.POST.get(f'pay_status_{i}')
                        total_cost = request.POST.get(f'total_cost{i}')
                        weightAmt = request.POST.get(f'weightAmt{i}')
                        freight = request.POST.get(f'freight{i}')
                        hamali = request.POST.get(f'hamali{i}')
                        door_charge = request.POST.get(f'door_charge{i}')
                        st_charge = request.POST.get(f'st_charge{i}')

                        print(f"Track ID: {track_id}, Pieces: {pieces}, Description: {desc_product}, Route: {route_to}, Receiver: {receiver_name}, Pay Status: {pay_status}, total_cost:{total_cost},weightAmt:{weightAmt},freight:{freight},hamali:{hamali},door_charge:{door_charge},st_charge:{st_charge}")  # Debugging statement


                        # Save to TripSheetTemp
                        LHSTemp.objects.create(
                            LRno=track_id,
                            qty=pieces,
                            desc=desc_product,
                            dest=route_to,
                            consignee=receiver_name,
                            pay_status=pay_status,
                            branch=branchname,
                            username=username,
                            Date=con_date,
                            total_cost=total_cost,
                            weightAmt=weightAmt,
                            freight=freight,
                            hamali=hamali,
                            door_charge=door_charge,
                            st_charge=st_charge,
                            )

                        # Delete from AddConsignmentTemp
                        AddConsignmentTemp.objects.filter(track_id=track_id).delete()

                        print(f"Data for Track ID {track_id} saved and deleted from AddConsignmentTemp successfully.")  # Debugging statement
            except Branch.DoesNotExist:
                print("Branch does not exist.")  # Debugging statement
        else:
            print("No username found in session.")  # Debugging statement

        return redirect('addLHS')  # Replace with your desired success URL

    print("Not a POST request, redirecting back to form.")  # Debugging statement
    return render(request, 'addLHS.html')  # Redirect back to the form if not a POST request

def addLHSList(request):
    addtrip = []  # Initialize an empty list to store trip details
    uid = request.session.get('username')
    no_data_found = False  # Flag to check if no data is found
    totalNo = 0  # Variable to store total number of LR
    totalWeightAmt = 0  # Variable to store total amount of weightAmt

    if uid:
        try:
            # Fetch the user's branch from the session
            branch = Branch.objects.get(email=uid)
            user_branch = branch.companyname

            if request.method == 'POST':
                # Get the selected date from the form
                date = request.POST.get('date')

                if date:
                    # Query LHSTemp table based on the selected date and user's branch
                    consignments = LHSTemp.objects.filter(
                        Date=date,
                        branch=user_branch
                    )

                    # Check if consignments exist
                    if consignments.exists():
                        # Calculate totals
                        totalNo = consignments.count()
                        totalWeightAmt = consignments.aggregate(
                            total_weight=Sum('weightAmt')
                        )['total_weight'] or 0

                        # Prepare data for the template
                        addtrip = [
                            {
                                'track_id': consignment.LRno,
                                'desc': consignment.desc,
                                'qty': consignment.qty,
                                'dest': consignment.dest,
                                'consignee': consignment.consignee,
                                'pay_status': consignment.pay_status,
                                'total_cost': consignment.total_cost,
                                'weightAmt': consignment.weightAmt,
                                'freight': consignment.freight,
                                'hamali': consignment.hamali,
                                'door_charge': consignment.door_charge,
                                'st_charge': consignment.st_charge
                            }
                            for consignment in consignments
                        ]
                    else:
                        no_data_found = True  # Set the flag if no data is found

        except Branch.DoesNotExist:
            addtrip = []
            no_data_found = True  # Set the flag if the branch does not exist

    # Render the template with the trip data, no_data_found flag, totalNo, and totalWeightAmt
    return render(request, 'addLHSList.html', {
        'trip': addtrip,
        'no_data_found': no_data_found,
        'totalNo': totalNo,
        'totalWeightAmt': totalWeightAmt,
    })


def saveLHS(request):
    print("saveTripSheet function called")

    if request.method == 'POST':
        print("POST request received")  # Debugging statement

        # Generate trip_id
        last_trip_id = LHSPrem.objects.aggregate(Max('trip_id'))['trip_id__max']
        trip_id = int(last_trip_id) + 1 if last_trip_id else 1000  # Start from a defined base if no entries exist
        con_id = str(trip_id)

        uid = request.session.get('username')
        if uid:
            try:
                branch = Branch.objects.get(email=uid)
                branchname = branch.companyname
                username = branch.headname

                now = datetime.now()
                con_date = now.strftime("%Y-%m-%d")
                current_time = now.strftime("%H:%M:%S")

                # Get form data
                route_from = request.POST.get('route_from')
                route_to = request.POST.get('route_to')
                DLNo = request.POST.get('dl_no')
                ownerName = request.POST.get('owner_name')
                countGC = request.POST.get('count_gc')
                paidWeight = request.POST.get('weight_Amt')
                vehicle = request.POST.get('vehical')
                drivername = request.POST.get('drivername')
                adv = request.POST.get('advance')
                ltrate = request.POST.get('ltrate') or 0
                ltr = request.POST.get('liter') or 0

                literate = float(ltrate)
                liter = float(ltr)
                diesel_total = literate * liter

                driver = Driver.objects.get(driver_name=drivername)
                phone = driver.phone_number
                # Save to Disel table
                Disel.objects.create(
                    Date=con_date,
                    vehicalno=vehicle,
                    drivername=drivername,
                    ltrate=ltrate,
                    liter=ltr,
                    total=diesel_total,  # Diesel total cost
                    trip_id=con_id
                )

                total_rows = int(request.POST.get('total_rows', 0))

                print(f"Vehicle: {vehicle}, Driver Name: {drivername}")  # Debugging statement

                for i in range(1, total_rows + 1):
                    track_id = request.POST.get(f'track_id_{i}')
                    desc = request.POST.get(f'desc_{i}')
                    qty = request.POST.get(f'qty_{i}')
                    dest = request.POST.get(f'dest_{i}')
                    consignee = request.POST.get(f'consignee_{i}')
                    total_cost = request.POST.get(f'total_cost_{i}')
                    pay_status = request.POST.get(f'pay_status_{i}')
                    weightAmt = request.POST.get(f'weightAmt_{i}')
                    freight = request.POST.get(f'freight_{i}')
                    hamali = request.POST.get(f'hamali_{i}')
                    door_charge = request.POST.get(f'door_charge_{i}')
                    st_charge = request.POST.get(f'st_charge_{i}')

                    print(
                        f"Track ID: {track_id}, Description: {desc}, Quantity: {qty}, Route: {dest}, Receiver: {consignee}")  # Debugging



                    # Save to TripSheetPrem
                    LHSPrem.objects.create(
                        route_from=route_from,
                        route_to=route_to,
                        DLNo=DLNo,
                        ownerName=ownerName,
                        countGC=countGC,
                        paidWeight=paidWeight,
                        LRno=track_id,
                        qty=qty,
                        desc=desc,
                        dest=dest,
                        consignee=consignee,
                        pay_status=pay_status,
                        VehicalNo=vehicle,
                        DriverName=drivername,
                        DriverNumber=phone,
                        branch=branchname,
                        username=username,
                        Date=con_date,
                        Time=current_time,
                        AdvGiven=adv,
                        LTRate=ltrate,
                        Ltr=ltr,
                        total_cost=total_cost,
                        weightAmt=float(weightAmt),
                        freight=freight,
                        hamali=hamali,
                        door_charge=door_charge,
                        st_charge=st_charge,
                        trip_id=con_id,
                        status='TripSheet Added',
                    )

                    # Save to TripSheetPrem
                    GDMTemp.objects.create(
                        route_from=route_from,
                        route_to=route_to,
                        DLNo=DLNo,
                        ownerName=ownerName,
                        countGC=countGC,
                        paidWeight=paidWeight,
                        LRno=track_id,
                        qty=qty,
                        desc=desc,
                        dest=dest,
                        consignee=consignee,
                        pay_status=pay_status,
                        VehicalNo=vehicle,
                        DriverName=drivername,
                        DriverNumber=phone,
                        branch=branchname,
                        username=username,
                        Date=con_date,
                        Time=current_time,
                        AdvGiven=adv,
                        LTRate=ltrate,
                        Ltr=ltr,
                        total_cost=total_cost,
                        weightAmt=float(weightAmt),
                        freight=freight,
                        hamali=hamali,
                        door_charge=door_charge,
                        st_charge=st_charge,
                        trip_id=con_id,
                        status='TripSheet Added',
                    )

                    # Delete from AddConsignmentTemp
                    LHSTemp.objects.filter(LRno=track_id).delete()

                    print(f"Data for Track ID {track_id} saved successfully.")  # Debugging statement
            except Branch.DoesNotExist:
                print("Branch does not exist.")  # Debugging statement
        else:
            print("No username found in session.")  # Debugging statement

        return redirect('addLHSList')  # Replace with your desired success URL

    return render(request, 'addLHSList.html')  # Redirect back if not a POST request



from django.db.models import Sum, F, FloatField

def LHS(request):
    return render(request,'LHS.html')

def tripSheetList(request):
    trips = []
    total_value = 0
    total_qty = 0
    grand_total = {
        'ToPay': 0,
        'Paid': 0,
        'Consigner_AC': 0,
        'Consignee_AC': 0,
        'grand_freight': 0,
        'grand_hamali': 0,
        'grand_st_charge': 0,
        'grand_door_charge': 0,
        'grand_weightAmt': 0,
        'grand_total': 0
    }
    summary = {
        'ToPay': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0},
        'Paid': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0},
        'Consigner_AC': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0},
        'Consignee_AC': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0}
    }

    uid = request.session.get('username')

    if uid:
        try:
            branch = Branch.objects.get(email=uid)
            user_branch = branch.companyname

            if request.method == 'POST':
                vehicle_number = request.POST.get('vehical')
                date = request.POST.get('t3')

                if date:
                    trips = LHSPrem.objects.filter(
                        VehicalNo=vehicle_number,
                        Date=date,
                        branch=user_branch
                    )
                    # Calculate total quantity
                    total_qty = trips.aggregate(total_qty=Sum('qty'))['total_qty'] or 0

                    # Aggregate data based on pay_status
                    statuses = ['ToPay', 'Paid', 'Consigner_AC', 'Consignee_AC']
                    for status in statuses:
                        status_trips = trips.filter(pay_status=status)
                        summary[status]['freight'] = status_trips.aggregate(total=Sum('freight'))['total'] or 0
                        summary[status]['hamali'] = status_trips.aggregate(total=Sum('hamali'))['total'] or 0
                        summary[status]['st_charge'] = status_trips.aggregate(total=Sum('st_charge'))['total'] or 0
                        summary[status]['door_charge'] = status_trips.aggregate(total=Sum('door_charge'))['total'] or 0
                        summary[status]['weightAmt'] = status_trips.aggregate(total=Sum('weightAmt'))['total'] or 0
                        summary[status]['total_cost'] = status_trips.aggregate(total=Sum('total_cost'))['total'] or 0

                        # Update grand totals
                        grand_total[status] = summary[status]['total_cost']
                        grand_total['grand_freight'] += summary[status]['freight']
                        grand_total['grand_hamali'] += summary[status]['hamali']
                        grand_total['grand_st_charge'] += summary[status]['st_charge']
                        grand_total['grand_door_charge'] += summary[status]['door_charge']
                        grand_total['grand_weightAmt'] += summary[status]['weightAmt']
                        grand_total['grand_total'] += summary[status]['total_cost']

                    # Calculate the total value using the first row
                    if trips.exists():
                        first_trip = trips.first()
                        total_ltr_value = float(
                            first_trip.LTRate * first_trip.Ltr) if first_trip.LTRate and first_trip.Ltr else 0.0
                        total_adv_given = float(first_trip.AdvGiven) if first_trip.AdvGiven else 0.0
                        total_value = total_ltr_value + total_adv_given
                    else:
                        total_value = 0.0

        except ObjectDoesNotExist:
            trips = LHSTemp.objects.none()

    return render(request, 'TripSheetList.html', {
        'trips': trips,
        'total_value': total_value,
        'total_qty': total_qty,
        'grand_total': grand_total,
        'summary': summary
    })


@require_POST
def delete_trip_sheet_data(request):
    vehicle_number = request.POST.get('vehical')
    date = request.POST.get('t3')
    uid = request.session.get('username')

    print(f"Received vehicle_number: {vehicle_number}, date: {date}, uid: {uid}")

    if uid and vehicle_number and date:
        try:
            branch = Branch.objects.get(email=uid)
            user_branch = branch.companyname
            LHSTemp.objects.filter(
                VehicalNo=vehicle_number,
                Date=date,
                branch=user_branch
            ).delete()
            return JsonResponse({'status': 'success'})
        except ObjectDoesNotExist:
            print("Branch does not exist.")
            return JsonResponse({'status': 'error', 'message': 'Branch does not exist'})

    print("Invalid parameters received.")
    return JsonResponse({'status': 'error', 'message': 'Invalid parameters'})

def viewLHSList(request):
    grouped_trips = []
    uid = request.session.get('username')

    if uid:
        try:
            branch = Branch.objects.get(email=uid)
            user_branch = branch.companyname

            if request.method == 'POST':
                date = request.POST.get('t3')

                if date:
                    # Group by VehicalNo and Date, and annotate with count
                    grouped_trips = (
                        LHSPrem.objects
                        .filter(Date=date, branch=user_branch)
                        .values('VehicalNo', 'Date')
                        .annotate(trip_count=Count('id'))
                    )

        except ObjectDoesNotExist:
            grouped_trips = []

    return render(request, 'viewLHSList.html', {
        'grouped_trips': grouped_trips
    })


def editLHSList(request):
    trips = []
    total_value = 0
    total_qty = 0
    grand_total = {
        'ToPay': 0,
        'Paid': 0,
        'Consigner_AC': 0,
        'Consignee_AC': 0,
        'grand_freight': 0,
        'grand_hamali': 0,
        'grand_st_charge': 0,
        'grand_door_charge': 0,
        'grand_weightAmt': 0,
        'grand_total': 0
    }
    summary = {
        'ToPay': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0},
        'Paid': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0},
        'Consigner_AC': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0},
        'Consignee_AC': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0}
    }

    uid = request.session.get('username')

    if uid:
        try:
            branch = Branch.objects.get(email=uid)
            user_branch = branch.companyname

            if request.method == 'POST':
                vehicle_number = request.POST.get('vehical')
                date_str = request.POST.get('t3')

                if date_str:
                    # Directly use date_str if it's in yyyy-mm-dd format
                    date = date_str

                    # Filter trips based on the vehicle number, date, and branch
                    trips = LHSPrem.objects.filter(
                        VehicalNo=vehicle_number,
                        Date=date,
                        branch=user_branch
                    )
                    # Calculate total quantity
                    total_qty = trips.aggregate(total_qty=Sum('qty'))['total_qty'] or 0

                    # Aggregate data based on pay_status
                    statuses = ['ToPay', 'Paid', 'Consigner_AC', 'Consignee_AC']
                    for status in statuses:
                        status_trips = trips.filter(pay_status=status)
                        summary[status]['freight'] = status_trips.aggregate(total=Sum('freight'))['total'] or 0
                        summary[status]['hamali'] = status_trips.aggregate(total=Sum('hamali'))['total'] or 0
                        summary[status]['st_charge'] = status_trips.aggregate(total=Sum('st_charge'))['total'] or 0
                        summary[status]['door_charge'] = status_trips.aggregate(total=Sum('door_charge'))['total'] or 0
                        summary[status]['weightAmt'] = status_trips.aggregate(total=Sum('weightAmt'))['total'] or 0
                        summary[status]['total_cost'] = status_trips.aggregate(total=Sum('total_cost'))['total'] or 0

                        # Update grand totals
                        grand_total[status] = summary[status]['total_cost']
                        grand_total['grand_freight'] += summary[status]['freight']
                        grand_total['grand_hamali'] += summary[status]['hamali']
                        grand_total['grand_st_charge'] += summary[status]['st_charge']
                        grand_total['grand_door_charge'] += summary[status]['door_charge']
                        grand_total['grand_weightAmt'] += summary[status]['weightAmt']
                        grand_total['grand_total'] += summary[status]['total_cost']

                    # Calculate the total value using the first row
                    if trips.exists():
                        first_trip = trips.first()
                        total_ltr_value = float(
                            first_trip.LTRate * first_trip.Ltr) if first_trip.LTRate and first_trip.Ltr else 0.0
                        total_adv_given = float(first_trip.AdvGiven) if first_trip.AdvGiven else 0.0
                        total_value = total_ltr_value + total_adv_given
                    else:
                        total_value = 0.0

        except Branch.DoesNotExist:
            trips = LHSTemp.objects.none()

    return render(request, 'editLHSList.html', {
        'trips': trips,
        'total_value': total_value,
        'total_qty': total_qty,
        'grand_total': grand_total,
        'summary': summary
    })


def update_view(request):
    if request.method == "POST":
        trip_id = request.POST.get("trip_id")
        print(f"Received trip_id: {trip_id}")  # Debugging line

        # Fetch all records with the matching trip_id
        trips = LHSPrem.objects.filter(trip_id=trip_id)

        if trips.exists():
            print(f"Found {trips.count()} trip records to update")
            for trip in trips:
                # Update the fields for each trip
                trip.LTRate = request.POST.get("ltrate")
                trip.Ltr = request.POST.get("ltr")
                trip.AdvGiven = request.POST.get("advgiven")
                trip.commission = request.POST.get("commission")
                trip.save()

            # Redirect after saving
            return redirect('viewLHSList')  # Replace with your success URL
        else:
            print("No trip records found")
            return render(request, 'editLHSList.html', {'error_message': 'No trips found with the provided trip_id.'})

    return render(request, 'editLHSList.html')  # Replace with your template

def printLHSList(request):
    trips = []
    total_value = 0
    total_qty = 0
    grand_total = {
        'ToPay': 0,
        'Paid': 0,
        'Consigner_AC': 0,
        'Consignee_AC': 0,
        'grand_freight': 0,
        'grand_hamali': 0,
        'grand_st_charge': 0,
        'grand_door_charge': 0,
        'grand_weightAmt': 0,
        'grand_total': 0
    }
    summary = {
        'ToPay': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0},
        'Paid': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0},
        'Consigner_AC': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0},
        'Consignee_AC': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0}
    }

    uid = request.session.get('username')

    if uid:
        try:
            branch = Branch.objects.get(email=uid)
            user_branch = branch.companyname

            vehical_no = request.POST.get('vehical')
            date = request.POST.get('t3')

            # Filter trips based on VehicleNo, Date, and branch
            trips = LHSPrem.objects.filter(
                VehicalNo=vehical_no,
                Date=date,
                branch=user_branch
            )

            # Calculate total quantity
            total_qty = trips.aggregate(total_qty=Sum('qty'))['total_qty'] or 0

            # Aggregate data based on pay_status
            statuses = ['ToPay', 'Paid', 'Consigner_AC', 'Consignee_AC']
            for status in statuses:
                status_trips = trips.filter(pay_status=status)
                summary[status]['freight'] = status_trips.aggregate(total=Sum('freight'))['total'] or 0
                summary[status]['hamali'] = status_trips.aggregate(total=Sum('hamali'))['total'] or 0
                summary[status]['st_charge'] = status_trips.aggregate(total=Sum('st_charge'))['total'] or 0
                summary[status]['door_charge'] = status_trips.aggregate(total=Sum('door_charge'))['total'] or 0
                summary[status]['weightAmt'] = status_trips.aggregate(total=Sum('weightAmt'))['total'] or 0
                summary[status]['total_cost'] = status_trips.aggregate(total=Sum('total_cost'))['total'] or 0

                # Update grand totals
                grand_total[status] = summary[status]['total_cost']
                grand_total['grand_freight'] += summary[status]['freight']
                grand_total['grand_hamali'] += summary[status]['hamali']
                grand_total['grand_st_charge'] += summary[status]['st_charge']
                grand_total['grand_door_charge'] += summary[status]['door_charge']
                grand_total['grand_weightAmt'] += summary[status]['weightAmt']
                grand_total['grand_total'] += summary[status]['total_cost']

            # Calculate the total value using the first row
            if trips.exists():
                first_trip = trips.first()
                total_ltr_value = float(first_trip.LTRate * first_trip.Ltr) if first_trip.LTRate and first_trip.Ltr else 0.0
                total_adv_given = float(first_trip.AdvGiven) if first_trip.AdvGiven else 0.0
                total_value = total_ltr_value
            else:
                total_value = 0.0

        except Branch.DoesNotExist:
            trips = LHSPrem.objects.none()  # Handle case where Branch does not exist

    return render(request, 'printLHSList.html', {
        'trips': trips,
        'total_value': total_value,
        'total_qty': total_qty,
        'grand_total': grand_total,
        'summary': summary
    })

def cancel_trip(request, trip_id):
    trip = get_object_or_404(LHSPrem, LRno=trip_id)
    con = get_object_or_404(AddConsignment, track_id=trip_id)
    con = get_object_or_404(AddConsignment, track_id=trip_id)

    # Copy the trip data to TripSheetTemp
    AddConsignmentTemp.objects.create(
        track_id=con.track_id,
        Consignment_id=con.Consignment_id,
        sender_name=con.sender_name,
        sender_mobile=con.sender_mobile,
        sender_address=con.sender_address,
        sender_GST=con.sender_GST,
        receiver_name=con.receiver_name,
        receiver_mobile=con.receiver_mobile,
        receiver_address=con.receiver_address,
        receiver_GST=con.receiver_GST,
        desc_product=con.desc_product,
        pieces=con.pieces,
        prod_invoice=con.prod_invoice,
        prod_price=con.prod_price,
        weightAmt=con.weightAmt,
        weight=con.weight,
        balance=con.balance,
        freight=con.freight,
        hamali=con.hamali,
        door_charge=con.door_charge,
        st_charge=con.st_charge,
        route_from=con.route_from,
        route_to=con.route_to,
        total_cost=con.total_cost,
        date=con.date,
        pay_status=con.pay_status,
        branch=con.branch,
        name=con.name,
        time=con.time,
        copy_type=con.copy_type,
        delivery=con.delivery,
        eway_bill=con.eway_bill
    )

    # Optionally, mark the trip as cancelled (if needed for other logic)
    trip.is_cancelled = True
    trip.save()

    # Remove the trip record from TripSheetPrem after saving
    trip.delete()

    messages.success(request, f"Trip {trip.LRno} has been cancelled, saved in TripSheetTemp, and removed from TripSheetPrem.")
    return redirect('viewLHSList')  # Replace with the actual view name if needed

def addGDMList(request):
    addtrip = []  # Initialize an empty list to store trip details
    uid = request.session.get('username')
    no_data_found = False  # Flag to check if no data is found
    totalNo = 0  # Variable to store total number of LR
    totalWeightAmt = 0  # Variable to store total amount of weightAmt

    # Initialize driver and vehicle details
    driver_details = {}

    if uid:
        try:
            # Fetch the user's branch from the session
            branch = Branch.objects.get(email=uid)
            user_branch = branch.companyname

            if request.method == 'POST':
                # Get the selected date and vehicle number from the form
                date = request.POST.get('date')
                vehicleNo = request.POST.get('vehical')

                if date:
                    # Query LHSPrem table based on the selected date, branch, and vehicle number
                    consignments = GDMTemp.objects.filter(
                        Date=date,
                        branch=user_branch,
                        VehicalNo=vehicleNo
                    )

                    # Check if consignments exist
                    if consignments.exists():
                        # Calculate totals
                        totalNo = consignments.count()
                        totalWeightAmt = consignments.aggregate(
                            total_weight=Sum('weightAmt')
                        )['total_weight'] or 0

                        # Get driver and vehicle details from the first consignment
                        first_consignment = consignments.first()
                        driver_details = {
                            'DriverName': first_consignment.DriverName,
                            'DriverNumber': first_consignment.DriverNumber,
                            'VehicalNo': first_consignment.VehicalNo,
                            'AdvGiven': first_consignment.AdvGiven,
                            'DLNo': first_consignment.DLNo,
                            'ownerName': first_consignment.ownerName,
                            'route_from': first_consignment.route_from,
                            'route_to': first_consignment.route_to,
                            'countGC': first_consignment.countGC,
                            'paidWeight': first_consignment.paidWeight,
                            'Ltr': first_consignment.Ltr,
                            'LTRate': first_consignment.LTRate,
                        }

                        # Prepare data for the template
                        addtrip = [
                            {
                                'LRno': consignment.LRno,
                                'desc': consignment.desc,
                                'qty': consignment.qty,
                                'dest': consignment.dest,
                                'consignee': consignment.consignee,
                                'pay_status': consignment.pay_status,
                                'total_cost': consignment.total_cost,
                                'weightAmt': consignment.weightAmt,
                                'freight': consignment.freight,
                                'hamali': consignment.hamali,
                                'door_charge': consignment.door_charge,
                                'st_charge': consignment.st_charge
                            }
                            for consignment in consignments
                        ]
                    else:
                        no_data_found = True  # Set the flag if no data is found

        except Branch.DoesNotExist:
            addtrip = []
            no_data_found = True  # Set the flag if the branch does not exist

    # Render the template with the trip data, driver details, and other context variables
    return render(request, 'addGDMList.html', {
        'trip': addtrip,
        'no_data_found': no_data_found,
        'totalNo': totalNo,
        'totalWeightAmt': totalWeightAmt,
        'driver_details': driver_details,
    })


def saveGDM(request):
    print("saveTripSheet function called")

    if request.method == 'POST':
        print("POST request received")  # Debugging statement

        # Generate trip_id
        last_trip_id = LHSPrem.objects.aggregate(Max('trip_id'))['trip_id__max']
        trip_id = int(last_trip_id) + 1 if last_trip_id else 1000  # Start from a defined base if no entries exist
        con_id = str(trip_id)

        uid = request.session.get('username')
        if uid:
            try:
                branch = Branch.objects.get(email=uid)
                branchname = branch.companyname
                username = branch.headname

                now = datetime.now()
                con_date = now.strftime("%Y-%m-%d")
                current_time = now.strftime("%H:%M:%S")

                # Get form data
                route_from = request.POST.get('route_from')
                route_to = request.POST.get('route_to')
                DLNo = request.POST.get('dl_no')
                ownerName = request.POST.get('owner_name')
                countGC = request.POST.get('count_gc')
                paidWeight = request.POST.get('weight_Amt')
                vehicle = request.POST.get('vehical')
                drivername = request.POST.get('drivername')
                DriverNumber = request.POST.get('vehicalPhone')
                adv = request.POST.get('advance')
                ltrate = request.POST.get('ltrate') or 0
                ltr = request.POST.get('liter') or 0

                literate = float(ltrate)
                liter = float(ltr)
                diesel_total = literate * liter


                total_rows = int(request.POST.get('total_rows', 0))

                selected_rows = request.POST.getlist('selected_rows')

                for i in range(1, total_rows + 1):
                    if str(i) in selected_rows:  # Only process if the row is selected
                        track_id = request.POST.get(f'LRno_{i}')
                        qty = request.POST.get(f'qty_{i}')
                        desc = request.POST.get(f'desc_{i}')
                        dest = request.POST.get(f'dest_{i}')
                        consignee = request.POST.get(f'consignee_{i}')
                        pay_status = request.POST.get(f'pay_status_{i}')
                        total_cost = request.POST.get(f'total_cost{i}')
                        weightAmt = request.POST.get(f'weightAmt{i}')
                        freight = request.POST.get(f'freight{i}')
                        hamali = request.POST.get(f'hamali{i}')
                        door_charge = request.POST.get(f'door_charge{i}')
                        st_charge = request.POST.get(f'st_charge{i}')

                        print(
                        f"Track ID: {track_id}, Description: {desc}, Quantity: {qty}, Route: {dest}, Receiver: {consignee}")  # Debugging



                    # Save to TripSheetPrem
                    GDMPrem.objects.create(
                        route_from=route_from,
                        route_to=route_to,
                        DLNo=DLNo,
                        ownerName=ownerName,
                        countGC=countGC,
                        paidWeight=paidWeight,
                        LRno=track_id,
                        qty=qty,
                        desc=desc,
                        dest=dest,
                        consignee=consignee,
                        pay_status=pay_status,
                        VehicalNo=vehicle,
                        DriverName=drivername,
                        DriverNumber=DriverNumber,
                        branch=branchname,
                        username=username,
                        Date=con_date,
                        Time=current_time,
                        AdvGiven=adv,
                        LTRate=ltrate,
                        Ltr=ltr,
                        total_cost=total_cost,
                        weightAmt=float(weightAmt),
                        freight=freight,
                        hamali=hamali,
                        door_charge=door_charge,
                        st_charge=st_charge,
                        trip_id=con_id,
                        status='TripSheet Added',
                    )

                    GDMTemp.objects.filter(LRno=track_id).delete()

            except Branch.DoesNotExist:
                print("Branch does not exist.")  # Debugging statement
        else:
            print("No username found in session.")  # Debugging statement

        return redirect('addGDMList')  # Replace with your desired success URL

    return render(request, 'addGDMList.html')  # Redirect back if not a POST request

def viewGDMList(request):
    grouped_trips = []
    uid = request.session.get('username')

    if uid:
        try:
            branch = Branch.objects.get(email=uid)
            user_branch = branch.companyname

            if request.method == 'POST':
                date = request.POST.get('t3')

                if date:
                    # Group by VehicalNo and Date, and annotate with count
                    grouped_trips = (
                        GDMPrem.objects
                        .filter(Date=date, branch=user_branch)
                        .values('VehicalNo', 'Date')
                        .annotate(trip_count=Count('id'))
                    )

        except ObjectDoesNotExist:
            grouped_trips = []

    return render(request, 'viewGDMList.html', {
        'grouped_trips': grouped_trips
    })

def printGDMList(request):
    trips = []
    total_value = 0
    total_qty = 0
    grand_total = {
        'ToPay': 0,
        'Paid': 0,
        'Consigner_AC': 0,
        'Consignee_AC': 0,
        'grand_freight': 0,
        'grand_hamali': 0,
        'grand_st_charge': 0,
        'grand_door_charge': 0,
        'grand_weightAmt': 0,
        'grand_total': 0
    }
    summary = {
        'ToPay': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0},
        'Paid': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0},
        'Consigner_AC': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0},
        'Consignee_AC': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0}
    }

    uid = request.session.get('username')

    if uid:
        try:
            branch = Branch.objects.get(email=uid)
            user_branch = branch.companyname


            vehical_no = request.POST.get('vehical')
            date = request.POST.get('t3')

            # Filter trips based on VehicleNo, Date, and branch
            trips = GDMPrem.objects.filter(
                VehicalNo=vehical_no,
                Date=date,
                branch=user_branch
            )

            # Calculate total quantity
            total_qty = trips.aggregate(total_qty=Sum('qty'))['total_qty'] or 0

            # Aggregate data based on pay_status
            statuses = ['ToPay', 'Paid', 'Consigner_AC', 'Consignee_AC']
            for status in statuses:
                status_trips = trips.filter(pay_status=status)
                summary[status]['freight'] = status_trips.aggregate(total=Sum('freight'))['total'] or 0
                summary[status]['hamali'] = status_trips.aggregate(total=Sum('hamali'))['total'] or 0
                summary[status]['st_charge'] = status_trips.aggregate(total=Sum('st_charge'))['total'] or 0
                summary[status]['door_charge'] = status_trips.aggregate(total=Sum('door_charge'))['total'] or 0
                summary[status]['weightAmt'] = status_trips.aggregate(total=Sum('weightAmt'))['total'] or 0
                summary[status]['total_cost'] = status_trips.aggregate(total=Sum('total_cost'))['total'] or 0

                # Update grand totals
                grand_total[status] = summary[status]['total_cost']
                grand_total['grand_freight'] += summary[status]['freight']
                grand_total['grand_hamali'] += summary[status]['hamali']
                grand_total['grand_st_charge'] += summary[status]['st_charge']
                grand_total['grand_door_charge'] += summary[status]['door_charge']
                grand_total['grand_weightAmt'] += summary[status]['weightAmt']
                grand_total['grand_total'] += summary[status]['total_cost']

            # Calculate the total value using the first row
            if trips.exists():
                first_trip = trips.first()
                total_ltr_value = float(first_trip.LTRate * first_trip.Ltr) if first_trip.LTRate and first_trip.Ltr else 0.0
                total_adv_given = float(first_trip.AdvGiven) if first_trip.AdvGiven else 0.0
                total_value = total_ltr_value
            else:
                total_value = 0.0

        except Branch.DoesNotExist:
            trips = LHSPrem.objects.none()  # Handle case where Branch does not exist

    return render(request, 'printGDMList.html', {
        'trips': trips,
        'total_value': total_value,
        'total_qty': total_qty,
        'grand_total': grand_total,
        'summary': summary
    })

def saveGDM(request):
    print("saveTripSheet function called")

    if request.method == 'POST':
        print("POST request received")  # Debugging statement

        # Generate trip_id
        last_trip_id = LHSPrem.objects.aggregate(Max('trip_id'))['trip_id__max']
        trip_id = int(last_trip_id) + 1 if last_trip_id else 1000  # Start from a defined base if no entries exist
        con_id = str(trip_id)

        uid = request.session.get('username')
        if uid:
            try:
                branch = Branch.objects.get(email=uid)
                branchname = branch.companyname
                username = branch.headname

                now = datetime.now()
                con_date = now.strftime("%Y-%m-%d")
                current_time = now.strftime("%H:%M:%S")

                # Get form data
                route_from = request.POST.get('route_from')
                route_to = request.POST.get('route_to')
                DLNo = request.POST.get('dl_no')
                ownerName = request.POST.get('owner_name')
                countGC = request.POST.get('count_gc')
                paidWeight = request.POST.get('weight_Amt')
                vehicle = request.POST.get('vehical')
                drivername = request.POST.get('drivername')
                DriverNumber = request.POST.get('vehicalPhone')
                adv = request.POST.get('advance')
                ltrate = request.POST.get('ltrate') or 0
                ltr = request.POST.get('liter') or 0

                literate = float(ltrate)
                liter = float(ltr)
                diesel_total = literate * liter


                total_rows = int(request.POST.get('total_rows', 0))

                selected_rows = request.POST.getlist('selected_rows')

                for i in range(1, total_rows + 1):
                    if str(i) in selected_rows:  # Only process if the row is selected
                        track_id = request.POST.get(f'LRno_{i}')
                        qty = request.POST.get(f'qty_{i}')
                        desc = request.POST.get(f'desc_{i}')
                        dest = request.POST.get(f'dest_{i}')
                        consignee = request.POST.get(f'consignee_{i}')
                        pay_status = request.POST.get(f'pay_status_{i}')
                        total_cost = request.POST.get(f'total_cost{i}')
                        weightAmt = request.POST.get(f'weightAmt{i}')
                        freight = request.POST.get(f'freight{i}')
                        hamali = request.POST.get(f'hamali{i}')
                        door_charge = request.POST.get(f'door_charge{i}')
                        st_charge = request.POST.get(f'st_charge{i}')

                        print(
                        f"Track ID: {track_id}, Description: {desc}, Quantity: {qty}, Route: {dest}, Receiver: {consignee}")  # Debugging



                    # Save to TripSheetPrem
                    GDMPrem.objects.create(
                        route_from=route_from,
                        route_to=route_to,
                        DLNo=DLNo,
                        ownerName=ownerName,
                        countGC=countGC,
                        paidWeight=paidWeight,
                        LRno=track_id,
                        qty=qty,
                        desc=desc,
                        dest=dest,
                        consignee=consignee,
                        pay_status=pay_status,
                        VehicalNo=vehicle,
                        DriverName=drivername,
                        DriverNumber=DriverNumber,
                        branch=branchname,
                        username=username,
                        Date=con_date,
                        Time=current_time,
                        AdvGiven=adv,
                        LTRate=ltrate,
                        Ltr=ltr,
                        total_cost=total_cost,
                        weightAmt=float(weightAmt),
                        freight=freight,
                        hamali=hamali,
                        door_charge=door_charge,
                        st_charge=st_charge,
                        trip_id=con_id,
                        status='TripSheet Added',
                    )
                    TURTemp.objects.create(
                        route_from=route_from,
                        route_to=route_to,
                        DLNo=DLNo,
                        ownerName=ownerName,
                        countGC=countGC,
                        paidWeight=paidWeight,
                        LRno=track_id,
                        qty=qty,
                        desc=desc,
                        dest=dest,
                        consignee=consignee,
                        pay_status=pay_status,
                        VehicalNo=vehicle,
                        DriverName=drivername,
                        DriverNumber=DriverNumber,
                        branch=branchname,
                        username=username,
                        Date=con_date,
                        Time=current_time,
                        AdvGiven=adv,
                        LTRate=ltrate,
                        Ltr=ltr,
                        total_cost=total_cost,
                        weightAmt=float(weightAmt),
                        freight=freight,
                        hamali=hamali,
                        door_charge=door_charge,
                        st_charge=st_charge,
                        trip_id=con_id,
                        status='TripSheet Added',
                    )

                    GDMTemp.objects.filter(LRno=track_id).delete()

            except Branch.DoesNotExist:
                print("Branch does not exist.")  # Debugging statement
        else:
            print("No username found in session.")  # Debugging statement

        return redirect('addGDMList')  # Replace with your desired success URL

    return render(request, 'addGDMList.html')  # Redirect back if not a POST request

from django.db.models import Count, Q
def viewLCMList(request):
    grouped_trips = []
    matched_data = []
    matched_count = 0
    uid = request.session.get('username')  # Get the logged-in user's username (email)

    if uid:
        try:
            # Fetch the user's branch using the email
            branch = Branch.objects.get(email=uid)
            user_branch = branch.companyname

            if request.method == 'POST':
                # Retrieve the selected date and vehicle number from the form
                date = request.POST.get('t3')
                VehicalNo = request.POST.get('vehical')

                if date and VehicalNo:
                    # Group data by vehicle number and date in LHSPrem
                    grouped_trips = (
                        LHSPrem.objects
                        .filter(Date=date, branch=user_branch, VehicalNo=VehicalNo)
                        .values('VehicalNo', 'Date')
                        .annotate(trip_count=Count('id'))
                    )

                    # Fetch all details from LHSPrem where LRno matches track_id in AddConsignment with collection_type='LCM'
                    matched_queryset = LHSPrem.objects.filter(
                        Date=date,
                        branch=user_branch,
                        VehicalNo=VehicalNo,
                        LRno__in=AddConsignment.objects.filter(
                            collection_type='LCM'
                        ).values_list('track_id', flat=True)
                    )

                    # Convert queryset to list for rendering
                    matched_data = list(matched_queryset)

                    # Get count of matched details
                    matched_count = matched_queryset.count()

        except ObjectDoesNotExist:
            grouped_trips = []
            matched_data = []
            matched_count = 0

    # Render the template with grouped trips, matched consignment data, and count
    return render(request, 'viewLCMList.html', {
        'grouped_trips': grouped_trips,
        'matched_data': matched_data,
        'matched_count': matched_count
    })


def printLCMList(request):
    trips = []
    total_value = 0
    total_qty = 0
    grand_total = {
        'ToPay': 0,
        'Paid': 0,
        'Consigner_AC': 0,
        'Consignee_AC': 0,
        'grand_freight': 0,
        'grand_hamali': 0,
        'grand_st_charge': 0,
        'grand_door_charge': 0,
        'grand_weightAmt': 0,
        'grand_total': 0
    }
    summary = {
        'ToPay': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0},
        'Paid': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0},
        'Consigner_AC': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0},
        'Consignee_AC': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0}
    }

    uid = request.session.get('username')

    if uid:
        try:
            branch = Branch.objects.get(email=uid)
            user_branch = branch.companyname

            vehical_no = request.POST.get('vehical')
            date = request.POST.get('t3')

            # Filter trips based on VehicleNo, Date, branch, and collection_type='LCM'
            trips = LHSPrem.objects.filter(
                VehicalNo=vehical_no,
                Date=date,
                branch=user_branch,
                LRno__in=AddConsignment.objects.filter(
                    collection_type='LCM'
                ).values_list('track_id', flat=True)
            )

            # Calculate total quantity
            total_qty = trips.aggregate(total_qty=Sum('qty'))['total_qty'] or 0

            # Aggregate data based on pay_status
            statuses = ['ToPay', 'Paid', 'Consigner_AC', 'Consignee_AC']
            for status in statuses:
                status_trips = trips.filter(pay_status=status)
                summary[status]['freight'] = status_trips.aggregate(total=Sum('freight'))['total'] or 0
                summary[status]['hamali'] = status_trips.aggregate(total=Sum('hamali'))['total'] or 0
                summary[status]['st_charge'] = status_trips.aggregate(total=Sum('st_charge'))['total'] or 0
                summary[status]['door_charge'] = status_trips.aggregate(total=Sum('door_charge'))['total'] or 0
                summary[status]['weightAmt'] = status_trips.aggregate(total=Sum('weightAmt'))['total'] or 0
                summary[status]['total_cost'] = status_trips.aggregate(total=Sum('total_cost'))['total'] or 0

                # Update grand totals
                grand_total[status] = summary[status]['total_cost']
                grand_total['grand_freight'] += summary[status]['freight']
                grand_total['grand_hamali'] += summary[status]['hamali']
                grand_total['grand_st_charge'] += summary[status]['st_charge']
                grand_total['grand_door_charge'] += summary[status]['door_charge']
                grand_total['grand_weightAmt'] += summary[status]['weightAmt']
                grand_total['grand_total'] += summary[status]['total_cost']

            # Calculate the total value using the first row
            if trips.exists():
                first_trip = trips.first()
                total_ltr_value = float(first_trip.LTRate * first_trip.Ltr) if first_trip.LTRate and first_trip.Ltr else 0.0
                total_adv_given = float(first_trip.AdvGiven) if first_trip.AdvGiven else 0.0
                total_value = total_ltr_value
            else:
                total_value = 0.0

        except Branch.DoesNotExist:
            trips = LHSPrem.objects.none()  # Handle case where Branch does not exist

    return render(request, 'printLCMList.html', {
        'trips': trips,
        'total_value': total_value,
        'total_qty': total_qty,
        'grand_total': grand_total,
        'summary': summary
    })


def addTURList(request):
    addtrip = []  # Initialize an empty list to store trip details
    uid = request.session.get('username')
    no_data_found = False  # Flag to check if no data is found
    totalNo = 0  # Variable to store total number of LR
    totalWeightAmt = 0  # Variable to store total amount of weightAmt

    # Initialize driver and vehicle details
    driver_details = {}

    if uid:
        try:
            # Fetch the user's branch from the session
            branch = Branch.objects.get(email=uid)
            user_branch = branch.companyname

            if request.method == 'POST':
                # Get the selected date and vehicle number from the form
                date = request.POST.get('date')
                vehicleNo = request.POST.get('vehical')

                if date:
                    # Query LHSPrem table based on the selected date, branch, and vehicle number
                    consignments = TURTemp.objects.filter(
                        Date=date,
                        branch=user_branch,
                        VehicalNo=vehicleNo
                    )

                    # Check if consignments exist
                    if consignments.exists():
                        # Calculate totals
                        totalNo = consignments.count()
                        totalWeightAmt = consignments.aggregate(
                            total_weight=Sum('weightAmt')
                        )['total_weight'] or 0

                        # Get driver and vehicle details from the first consignment
                        first_consignment = consignments.first()
                        driver_details = {
                            'DriverName': first_consignment.DriverName,
                            'DriverNumber': first_consignment.DriverNumber,
                            'VehicalNo': first_consignment.VehicalNo,
                            'AdvGiven': first_consignment.AdvGiven,
                            'DLNo': first_consignment.DLNo,
                            'ownerName': first_consignment.ownerName,
                            'route_from': first_consignment.route_from,
                            'route_to': first_consignment.route_to,
                            'countGC': first_consignment.countGC,
                            'paidWeight': first_consignment.paidWeight,
                            'Ltr': first_consignment.Ltr,
                            'LTRate': first_consignment.LTRate,
                        }

                        # Prepare data for the template
                        addtrip = [
                            {
                                'LRno': consignment.LRno,
                                'desc': consignment.desc,
                                'qty': consignment.qty,
                                'dest': consignment.dest,
                                'consignee': consignment.consignee,
                                'pay_status': consignment.pay_status,
                                'total_cost': consignment.total_cost,
                                'weightAmt': consignment.weightAmt,
                                'freight': consignment.freight,
                                'hamali': consignment.hamali,
                                'door_charge': consignment.door_charge,
                                'st_charge': consignment.st_charge
                            }
                            for consignment in consignments
                        ]
                    else:
                        no_data_found = True  # Set the flag if no data is found

        except Branch.DoesNotExist:
            addtrip = []
            no_data_found = True  # Set the flag if the branch does not exist

    # Render the template with the trip data, driver details, and other context variables
    return render(request, 'addTURList.html', {
        'trip': addtrip,
        'no_data_found': no_data_found,
        'totalNo': totalNo,
        'totalWeightAmt': totalWeightAmt,
        'driver_details': driver_details,
    })


def saveTUR(request):
    print("saveTripSheet function called")

    if request.method == 'POST':
        print("POST request received")  # Debugging statement

        # Generate trip_id
        last_trip_id = LHSPrem.objects.aggregate(Max('trip_id'))['trip_id__max']
        trip_id = int(last_trip_id) + 1 if last_trip_id else 1000  # Start from a defined base if no entries exist
        con_id = str(trip_id)

        uid = request.session.get('username')
        if uid:
            try:
                branch = Branch.objects.get(email=uid)
                branchname = branch.companyname
                username = branch.headname

                now = datetime.now()
                con_date = now.strftime("%Y-%m-%d")
                current_time = now.strftime("%H:%M:%S")

                # Get form data
                route_from = request.POST.get('route_from')
                route_to = request.POST.get('route_to')
                DLNo = request.POST.get('dl_no')
                ownerName = request.POST.get('owner_name')
                countGC = request.POST.get('count_gc')
                paidWeight = request.POST.get('weight_Amt')
                vehicle = request.POST.get('vehical')
                drivername = request.POST.get('drivername')
                DriverNumber = request.POST.get('vehicalPhone')
                adv = request.POST.get('advance')
                ltrate = request.POST.get('ltrate') or 0
                ltr = request.POST.get('liter') or 0

                literate = float(ltrate)
                liter = float(ltr)
                diesel_total = literate * liter


                total_rows = int(request.POST.get('total_rows', 0))

                selected_rows = request.POST.getlist('selected_rows')

                for i in range(1, total_rows + 1):
                    if str(i) in selected_rows:  # Only process if the row is selected
                        track_id = request.POST.get(f'LRno_{i}')
                        qty = request.POST.get(f'qty_{i}')
                        desc = request.POST.get(f'desc_{i}')
                        dest = request.POST.get(f'dest_{i}')
                        consignee = request.POST.get(f'consignee_{i}')
                        pay_status = request.POST.get(f'pay_status_{i}')
                        total_cost = request.POST.get(f'total_cost{i}')
                        weightAmt = request.POST.get(f'weightAmt{i}')
                        freight = request.POST.get(f'freight{i}')
                        hamali = request.POST.get(f'hamali{i}')
                        door_charge = request.POST.get(f'door_charge{i}')
                        st_charge = request.POST.get(f'st_charge{i}')

                        print(
                        f"Track ID: {track_id}, Description: {desc}, Quantity: {qty}, Route: {dest}, Receiver: {consignee}")  # Debugging



                    # Save to TripSheetPrem
                    TURPrem.objects.create(
                        route_from=route_from,
                        route_to=route_to,
                        DLNo=DLNo,
                        ownerName=ownerName,
                        countGC=countGC,
                        paidWeight=paidWeight,
                        LRno=track_id,
                        qty=qty,
                        desc=desc,
                        dest=dest,
                        consignee=consignee,
                        pay_status=pay_status,
                        VehicalNo=vehicle,
                        DriverName=drivername,
                        DriverNumber=DriverNumber,
                        branch=branchname,
                        username=username,
                        Date=con_date,
                        Time=current_time,
                        AdvGiven=adv,
                        LTRate=ltrate,
                        Ltr=ltr,
                        total_cost=total_cost,
                        weightAmt=float(weightAmt),
                        freight=freight,
                        hamali=hamali,
                        door_charge=door_charge,
                        st_charge=st_charge,
                        trip_id=con_id,
                        status='TripSheet Added',
                    )

                    TURTemp.objects.filter(LRno=track_id).delete()

            except Branch.DoesNotExist:
                print("Branch does not exist.")  # Debugging statement
        else:
            print("No username found in session.")  # Debugging statement

        return redirect('addTURList')  # Replace with your desired success URL

    return render(request, 'addTURList.html')  # Redirect back if not a POST request


def viewTURList(request):
    grouped_trips = []
    uid = request.session.get('username')

    if uid:
        try:
            branch = Branch.objects.get(email=uid)
            user_branch = branch.companyname

            if request.method == 'POST':
                date = request.POST.get('t3')

                if date:
                    # Group by VehicalNo and Date, and annotate with count
                    grouped_trips = (
                        TURPrem.objects
                        .filter(Date=date, branch=user_branch)
                        .values('VehicalNo', 'Date')
                        .annotate(trip_count=Count('id'))
                    )

        except ObjectDoesNotExist:
            grouped_trips = []

    return render(request, 'viewTURList.html', {
        'grouped_trips': grouped_trips
    })

def printTURList(request):
    trips = []
    total_value = 0
    total_qty = 0
    grand_total = {
        'ToPay': 0,
        'Paid': 0,
        'Consigner_AC': 0,
        'Consignee_AC': 0,
        'grand_freight': 0,
        'grand_hamali': 0,
        'grand_st_charge': 0,
        'grand_door_charge': 0,
        'grand_weightAmt': 0,
        'grand_total': 0
    }
    summary = {
        'ToPay': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0},
        'Paid': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0},
        'Consigner_AC': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0},
        'Consignee_AC': {'freight': 0, 'hamali': 0, 'st_charge': 0, 'door_charge': 0, 'weightAmt': 0, 'total_cost': 0}
    }

    uid = request.session.get('username')

    if uid:
        try:
            branch = Branch.objects.get(email=uid)
            user_branch = branch.companyname


            vehical_no = request.POST.get('vehical')
            date = request.POST.get('t3')

            # Filter trips based on VehicleNo, Date, and branch
            trips = TURPrem.objects.filter(
                VehicalNo=vehical_no,
                Date=date,
                branch=user_branch
            )

            # Calculate total quantity
            total_qty = trips.aggregate(total_qty=Sum('qty'))['total_qty'] or 0

            # Aggregate data based on pay_status
            statuses = ['ToPay', 'Paid', 'Consigner_AC', 'Consignee_AC']
            for status in statuses:
                status_trips = trips.filter(pay_status=status)
                summary[status]['freight'] = status_trips.aggregate(total=Sum('freight'))['total'] or 0
                summary[status]['hamali'] = status_trips.aggregate(total=Sum('hamali'))['total'] or 0
                summary[status]['st_charge'] = status_trips.aggregate(total=Sum('st_charge'))['total'] or 0
                summary[status]['door_charge'] = status_trips.aggregate(total=Sum('door_charge'))['total'] or 0
                summary[status]['weightAmt'] = status_trips.aggregate(total=Sum('weightAmt'))['total'] or 0
                summary[status]['total_cost'] = status_trips.aggregate(total=Sum('total_cost'))['total'] or 0

                # Update grand totals
                grand_total[status] = summary[status]['total_cost']
                grand_total['grand_freight'] += summary[status]['freight']
                grand_total['grand_hamali'] += summary[status]['hamali']
                grand_total['grand_st_charge'] += summary[status]['st_charge']
                grand_total['grand_door_charge'] += summary[status]['door_charge']
                grand_total['grand_weightAmt'] += summary[status]['weightAmt']
                grand_total['grand_total'] += summary[status]['total_cost']

            # Calculate the total value using the first row
            if trips.exists():
                first_trip = trips.first()
                total_ltr_value = float(first_trip.LTRate * first_trip.Ltr) if first_trip.LTRate and first_trip.Ltr else 0.0
                total_adv_given = float(first_trip.AdvGiven) if first_trip.AdvGiven else 0.0
                total_value = total_ltr_value
            else:
                total_value = 0.0

        except Branch.DoesNotExist:
            trips = LHSPrem.objects.none()  # Handle case where Branch does not exist

    return render(request, 'printTURList.html', {
        'trips': trips,
        'total_value': total_value,
        'total_qty': total_qty,
        'grand_total': grand_total,
        'summary': summary
    })


def frieghtBillList(request):
    # Get filter values from the request
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    sender_name = request.GET.get('sender_name')
    receiver_name = request.GET.get('consignee')

    # Start building the query
    queryset = AddConsignment.objects.filter(
        Q(pay_status="Consigner_AC") | Q(pay_status="Consignee_AC")
    )

    # Apply date range filter if both from_date and to_date are provided
    if from_date_str and to_date_str:
        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()

            # Filter the queryset by the date range
            queryset = queryset.filter(date__range=(from_date, to_date))
        except ValueError:
            return render(request, 'partywise_report.html', {
                'error': 'Invalid date format.'
            })

    # Apply sender_name filter if provided
    if sender_name:
        queryset = queryset.filter(sender_name__icontains=sender_name)
    if receiver_name:
        queryset = queryset.filter(receiver_name__icontains=receiver_name)

    # Group by sender_name and calculate sum of pieces, total cost, and count of track_id
    consignments_by_sender = queryset.values('sender_name').annotate(
        total_pieces=Sum('pieces'),
        total_cost=Sum('total_cost'),
        track_id_count=Count('track_id', distinct=True)
    ).order_by('sender_name')

    # Calculate the grand total of total_cost
    grand_total_cost = queryset.aggregate(grand_total=Sum('total_cost'))['grand_total']

    # Pass the aggregated data to the template
    context = {
        'consignments_by_sender': consignments_by_sender,
        'from_date': from_date_str,
        'to_date': to_date_str,
        'sender_name': sender_name,
        'grand_total_cost': grand_total_cost
    }

    return render(request, 'frieghtBillList.html', context)

from django.db.models import Q, Sum
from datetime import datetime
from django.shortcuts import render

def frieghtBillReport(request, sender_name):
    # Get filter values from the request
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')

    # Start building the query to include both Consigner_AC and Consignee_AC
    consignments = AddConsignment.objects.filter(
        Q(sender_name=sender_name) | Q(receiver_name=sender_name),
        Q(pay_status="Consigner_AC") | Q(pay_status="Consignee_AC")
    )

    # Apply date range filter if both from_date and to_date are provided
    if from_date_str and to_date_str:
        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()

            # Filter the queryset by the date range
            consignments = consignments.filter(date__range=(from_date, to_date))
        except ValueError:
            return render(request, 'frieghtBillReport.html', {
                'error': 'Invalid date format.',
                'sender_name': sender_name,
            })

    if not consignments.exists():
        return render(request, 'frieghtBillReport.html', {'error': 'No consignments found for this sender.'})

    # Aggregate details based on Consignment_id
    aggregated_data = consignments.values(
        'Consignment_id',
        'track_id',
        'sender_name',
        'sender_mobile',
        'sender_address',
        'receiver_name',
        'receiver_mobile',
        'receiver_address',
        'date',
        'route_from',
        'route_to',
        'prod_invoice',
        'prod_price',
        'branch',
        'name',
        'time',
        'copy_type',
        'delivery',
        'eway_bill'
    ).annotate(
        total_cost=Sum('total_cost'),
        pieces=Sum('pieces'),
        weight=Sum('weight'),
        freight=Sum('freight'),
        hamali=Sum('hamali'),
        door_charge=Sum('door_charge'),
        st_charge=Sum('st_charge'),
        weightAmt=Sum('weightAmt'),
    ).order_by('track_id')  # Sort by track_id

    # Create a list of dictionaries for the final data to be displayed
    detailed_data = []
    total_account_cost = 0  # Initialize the variable to calculate total account cost

    for consignment in aggregated_data:
        descriptions = consignments.filter(Consignment_id=consignment['Consignment_id']).values_list('desc_product', flat=True)

        # Get the total_cost for both pay_status ("Consigner_AC" and "Consignee_AC") for this Consignment_id
        account_total_cost = consignments.filter(
            Q(Consignment_id=consignment['Consignment_id']) &
            (Q(pay_status='Consigner_AC') | Q(pay_status='Consignee_AC'))
        ).aggregate(Sum('total_cost'))['total_cost__sum'] or 0

        # Update the total_account_cost for all consignments
        total_account_cost += account_total_cost

        # Append each description with aggregated data
        detailed_data.append({
            **consignment,
            'desc_products': descriptions,
            'account_total_cost': account_total_cost,
        })

    # Calculate total pieces for the sender
    total_pieces = consignments.aggregate(total_pieces=Sum('pieces'))['total_pieces'] or 0

    # Pass from_date_str, to_date_str, and total_account_cost to the template context
    return render(request, 'frieghtBillReport.html', {
        'sender_name': sender_name,
        'consignments': detailed_data,
        'total_pieces': total_pieces,
        'total_account_cost': total_account_cost,  # Add total account cost to context
        'from_date': from_date_str,
        'to_date': to_date_str
    })

