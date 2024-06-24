from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import Http404
from django.contrib import messages
from django.utils import timezone
from .models import *
from ipcs_admin.models import*
from django.db import IntegrityError
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.contrib.auth.decorators import user_passes_test
from ipcs_admin.views import admin_login


def not_superuser(user):
    return user.is_authenticated and not user.is_superuser

def customer_login(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        return redirect(customer_home)
    if request.method == "POST":
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            if not user.is_superuser:
                login(request,user)
                return redirect(customer_home)
            else:
                messages.warning(request, "Redirected to admin login page")
                return redirect(admin_login)
        else:
            messages.error(request,"Username or Password is incorrect")
            return redirect(customer_login)
    return render(request, 'customer_sign_in.html')

@user_passes_test(not_superuser, login_url=customer_login)
def customer_logout(request):    
    logout(request)
    return redirect(home)
    
def customer_signup(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        return redirect(customer_home)
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        password = request.POST["password"]
        repeat_password = request.POST["repeat_password"]
        if password == repeat_password:
            try:
                Customer.objects.create(name=name, email=email, phone=phone)
                User.objects.create_user(username=email, password=password)
                messages.success(request, "Sign Up successfull.")
                return redirect(customer_login)    
            except IntegrityError:
                messages.warning(request,'Account already exists!')
                return redirect(customer_login)
        else:
            messages.error(request, "Passwords do not match.")
            return redirect(customer_signup)
    return render(request, 'customer_signup.html')

@user_passes_test(not_superuser, login_url=customer_login)
def reset_customer_password(request):    
    context = {}
    try:
        customer = get_object_or_404(Customer, email = request.user.username)
        context.update({"customer": customer})
    except Http404:
        pass
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        repeat_password = request.POST["repeat_password"]
        username = request.user.username
        user = authenticate(request, username = username, password = current_password)
        if user is not None:
            if new_password == repeat_password:
                user.set_password(new_password)
                messages.success(request, "Password updated successfully.")
                user.save()
                logout(request)
                return redirect(customer_login)
            else:
                messages.warning(request, "New passwords do not match.")
                return redirect(reset_customer_password)
        else:
            messages.error(request, "Invalid current password.")
            return redirect(reset_customer_password)
    return render(request, 'secured/reset_customer_password.html', context)    

@user_passes_test(not_superuser, login_url=customer_login)    
def customer_account(request):    
    context = {}
    try:
        customer = get_object_or_404(Customer, email = request.user.username)
        context.update({"customer": customer})
    except Http404:
        messages.error(request, "Unauthorized user.")
        return redirect(customer_login)
    return render(request, 'secured/account.html', context)    

@user_passes_test(not_superuser, login_url=customer_login)    
def update_customer_info(request):    
    try:
        if request.method == "POST":
            image = request.FILES["image"]
            name = request.POST["name"]
            phone = request.POST["phone"]
            try:
                customer = get_object_or_404(Customer, email = request.user.username)
                customer.name = name
                customer.phone = phone
                if image:
                    customer.photo = image
                customer.save()
                return redirect(customer_account)
            except Http404:
                messages.error(request, "Unauthorized user.")
                return redirect(customer_login)
    except PermissionDenied:
        return redirect(customer_account)
    except SuspiciousOperation:
        return redirect(customer_account)       

@user_passes_test(not_superuser, login_url=customer_login)
def customer_home(request):
    context = {}
    try:
        customer = get_object_or_404(Customer, email = request.user.username)
        context.update({"customer": customer})
    except Http404:
        pass  
    return render(request, 'secured/customer_home.html', context)

def home(request):
    context = {}
    clients = Client.objects.all()
    context.update({"clients": clients})
    products = Product.objects.all
    context.update({"products": products})
    if request.user:
        try:
            customer = get_object_or_404(Customer, email = request.user.username)
            context.update({"customer": customer})
        except Http404:
            pass
    # warranty start 
    expiry_date_and_days_left = False
    warranty_valid = False
    service_valid = False
    warrantied_product = False
    claimed_warranties = False
    warranty_application = False
    approved_warranty = False
            
    completed_services = False
    service_request = False
    scheduled_service = False

    completed_repairs = False
    repair_request = False
    scheduled_repair = False

    try:
        if request.method == "POST":
            id = request.POST["id"]
            if id != "" and " " not in str(id):
                context.update({"id": id})
                
                if str(id).startswith("WTY"):
                    try:
                        warrantied_product = get_object_or_404(Warranty, id = id)
                        context.update({"warrantied_product": warrantied_product})
                        try:
                            claimed_warranties = get_list_or_404(ClaimedWarranty, warranty_id = id)
                            context.update({"claimed_warranties": claimed_warranties})
                        except Http404:
                            pass
                        try:
                            warranty_application = get_object_or_404(WarrantyApplication, id = id)                            
                            context.update({"warranty_application": warranty_application})
                        except Http404:
                            pass
                        try:
                            approved_warranty = get_object_or_404(ApprovedWarrantyApplication, id = id)
                            context.update({"approved_warranty": approved_warranty})
                        except Http404:
                            pass
                    except Http404:
                        pass
                else:  
                    try:
                        warrantied_product = get_object_or_404(Warranty, serial_number = id)
                        context.update({"warrantied_product": warrantied_product})
                        try:
                            claimed_warranties = get_list_or_404(ClaimedWarranty, serial_number = id)
                            context.update({"claimed_warranties": claimed_warranties})
                        except Http404:
                            pass
                        try:
                            warranty_application = get_object_or_404(WarrantyApplication, serial_number = id)
                            context.update({"warranty_application": warranty_application})
                        except Http404:
                            pass
                        try:
                            approved_warranty = get_object_or_404(ApprovedWarrantyApplication, serial_number = id)
                            context.update({"approved_warranty": approved_warranty})
                        except Http404:
                            pass
                    except Http404:
                        pass
            
                if str(id).startswith("SVS"):                    
                    try:
                        completed_services = get_list_or_404(CompletedService, id = id)
                        # completed_service = CompletedService.objects.filter(id = id).first()
                        # warrantied_product = get_object_or_404(Warranty, serial_number = completed_service.serial_number)
                        context.update({
                            "completed_services": completed_services,
                            # "warrantied_product": warrantied_product,
                            })
                    except Http404:
                        pass
                    try:
                        service_request = get_object_or_404(ServiceRequest, id = id)
                        warrantied_product = get_object_or_404(Warranty, serial_number = service_request.serial_number)
                        context.update({
                            "service_request": service_request,
                            "warrantied_product": warrantied_product
                            })
                        try:
                            scheduled_service = get_object_or_404(ScheduledService, id = id)
                            context.update({"scheduled_service": scheduled_service})
                        except Http404:
                            pass                        
                    except Http404:
                        pass
                else:
                    try:
                        completed_services = get_list_or_404(CompletedService, serial_number = id)                        
                        warrantied_product = get_object_or_404(Warranty, serial_number = id)
                        context.update({
                            "completed_services": completed_services,
                            "warrantied_product": warrantied_product,
                            })
                    except Http404:
                        pass
                    try:
                        service_request = get_object_or_404(ServiceRequest, serial_number = id)
                        warrantied_product = get_object_or_404(Warranty, serial_number = id)
                        context.update({
                            "service_request": service_request,
                            "warrantied_product": warrantied_product
                            })
                        try:
                            scheduled_service = get_object_or_404(ScheduledService, service_request__serial_number = id)
                            context.update({"scheduled_service": scheduled_service})
                        except Http404:
                            pass
                    except Http404:
                        pass
                
                if str(id).startswith("REP"):                    
                    try:
                        completed_repairs = get_list_or_404(CompletedRepair, id = id)                                                
                        context.update({"completed_repairs": completed_repairs})
                    except Http404:
                        pass
                    try:
                        repair_request = get_object_or_404(RepairRequest, id = id)
                        context.update({"repair_request": repair_request})
                        try:
                            scheduled_repair = get_object_or_404(ScheduledRepair, id = id)
                            context.update({"scheduled_repair": scheduled_repair})
                        except Http404:
                            pass                        
                    except Http404:
                        pass
                else:
                    try:
                        completed_repairs = get_list_or_404(CompletedRepair, serial_number = id)
                        context.update({"completed_repairs": completed_repairs})
                    except Http404:
                        pass
                    try:
                        repair_request = get_object_or_404(RepairRequest, serial_number = id)
                        context.update({
                            "repair_request": repair_request})
                        try:
                            scheduled_repair = get_object_or_404(ScheduledRepair, repair_request__serial_number = id)
                            context.update({"scheduled_repair": scheduled_repair})
                        except Http404:
                            pass
                    except Http404:
                        pass        

            if warrantied_product:            
                if warrantied_product.duration:
                    current_date = timezone.now().date()
                    expiry_date = warrantied_product.expiry_date
                    date_difference = expiry_date - current_date
                    days_left = date_difference.days
                    if current_date > expiry_date:
                        warranty_valid = False
                        last_serviced_date = False
                        if str(id).startswith("WTY"):
                            try:                                                        
                                last_serviced_date = CompletedService.objects.filter(serial_number = warrantied_product.serial_number).latest('service_date').service_date
                            except:
                                pass
                        else:
                            try:
                                last_serviced_date = CompletedService.objects.filter(serial_number = id).latest('service_date').service_date
                            except:
                                pass
                        if last_serviced_date:
                            available_service_date = last_serviced_date + timedelta(days = 90)
                            if current_date > available_service_date:
                                service_valid = True                            
                                context.update({"service_valid": service_valid})
                        else:
                            service_valid = True                            
                            context.update({"service_valid": service_valid})                     
                        expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Warranty Completed)"                    
                    elif expiry_date == current_date:
                        warranty_valid = True
                        context.update({"warranty_valid": warranty_valid})
                        expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Expiring Today)"
                    else:
                        if days_left > 1:
                            expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Days Left)"                                    
                        else:
                            expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Day Left)"
                        warranty_valid = True
                        context.update({"warranty_valid": warranty_valid})
                    context.update({"expiry_date_and_days_left" : expiry_date_and_days_left})

            if warrantied_product:
                if warranty_application:                    
                    if approved_warranty:
                        messages.info(request, "Warranty has been approved.")
                    else:
                        messages.info(request, "Warranty application has been submitted.")
                elif claimed_warranties:
                    last_claimed_date = False
                    if str(id).startswith("WTY"):
                        try:
                            last_claimed_date = ClaimedWarranty.objects.filter(warranty_id = id).latest('approved_datetime').approved_datetime.date()
                        except:
                            pass
                    else:
                        try:
                            last_claimed_date = ClaimedWarranty.objects.filter(serial_number = id).latest('approved_datetime').approved_datetime.date()
                        except:
                            pass
                    if last_claimed_date:
                        warranty_claimable_date = last_claimed_date + timedelta(days = 30)                    
                        if current_date < warranty_claimable_date:
                            warranty_valid = False
                            context["warranty_valid"] = warranty_valid
                    messages.success(request, "Warranty claimed.")

            if service_request:
                if scheduled_service:
                    messages.info(request, "Service has been scheduled.")
                else:
                    messages.info(request, "Service requested.")
            elif completed_services:
                last_serviced_date = False
                current_date = timezone.now().date()
                if str(id).startswith("SVS"):
                    try:
                        last_serviced_date = CompletedService.objects.filter(id = id).latest('service_date').service_date
                    except:
                        pass
                else:
                    try:
                        last_serviced_date = CompletedService.objects.filter(serial_number = id).latest('service_date').service_date
                    except:
                        pass
                if last_serviced_date:
                    available_service_date = last_serviced_date + timedelta(days = 90)
                    if current_date > available_service_date:
                        service_valid = True                            
                        context.update({"service_valid": service_valid})
                    messages.success(request, "Service Completed.")
                else:
                    service_valid = True
                    context["service_valid"] = service_valid
            if repair_request:
                if scheduled_repair:
                    messages.info(request, "Repair has been scheduled.")
                else:
                    messages.info(request, "Repair requested.")
            elif completed_repairs:                
                messages.success(request, "Repair Completed.")

            # else:
            #     if id != "" and " " not in str(id):
            #         messages.error(request, "Invalid warranty id or serial number.")

    except SuspiciousOperation:
        return render(request, 'warranty_tracking.html', context)
    
    except PermissionDenied:
        return render(request, 'warranty_tracking.html', context)
    return render(request, 'home.html', context)

# def home(request):
#     context = {}
#     if request.user:
#         try:
#             customer = get_object_or_404(Customer, email = request.user.username)
#             context.update({"customer": customer})
#         except Http404:
#             pass
#     expiry_date_and_days_left = False
#     warranty_valid = False
#     service_valid = False
#     warrantied_product = False
#     claimed_warranties = False
#     warranty_submitted = False
#     warranty_approved = False
            
#     completed_services = False
#     service_request = False
#     scheduled_service = False

#     completed_repairs = False
#     repair_request = False
#     scheduled_repair = False
#     try:
#         if request.method == "POST":
#             id = request.POST["id"]
#             if id != "" and " " not in str(id):
#                 context.update({"id": id})

#                 # Check warranty with id
#                 try:
#                     warrantied_product = get_object_or_404(Warranty, pk = id)
#                     context.update({"warrantied_product": warrantied_product})
#                     if warrantied_product.duration:
#                         current_date = timezone.now().date()
#                         expiry_date = warrantied_product.expiry_date
#                         # date_difference = relativedelta(expiry_date, current_date)
#                         date_difference = expiry_date - current_date
#                         days_left = date_difference.days
#                         if current_date > expiry_date:
#                             expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Warranty Completed)"
#                         elif expiry_date == current_date:
#                             expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Expiring Today)"
#                         else:
#                             if days_left > 1:
#                                 expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Days Left)"                             
#                             else:
#                                 expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Day Left)"
#                         context.update({"expiry_date_and_days_left" : expiry_date_and_days_left})
#                         try:
#                             claimed_warranties = get_list_or_404(ClaimedWarranty, warranty_id = id)
#                             context.update({
#                                 "claimed_warranties" : claimed_warranties,                            
#                                 })
#                             messages.success(request, "Claimed warranty.")
#                             return render(request, 'home.html', context) 

#                         except Http404:
#                             try:
#                                 warranty_approved = get_object_or_404(ApprovedWarrantyApplication, pk = id)
#                                 feedback = warranty_approved.feedback
#                                 context.update({
#                                     "warranty_approved" : warranty_approved,
#                                     "feedback": feedback,
#                                     })
#                                 messages.success(request, "The submitted warranty application has been approved.")
#                                 return render(request, 'home.html', context) 

#                             except Http404:
#                                 try:
#                                     warranty_submitted = get_object_or_404(WarrantyApplication, pk = id)                                                                
#                                     context.update({"warranty_submitted": warranty_submitted})
#                                     messages.success(request, "The warranty application has already been submitted.")
#                                     return render(request, 'home.html', context)                        

#                                 except Http404:
#                                     if current_date > expiry_date:
#                                         service_valid = True
#                                         context.update({"service_valid" : service_valid})                                                                
#                                     elif expiry_date == current_date:
#                                         warranty_valid = True
#                                         context.update({"warranty_valid": warranty_valid})                                                                
#                                     else:
#                                         warranty_valid = True
#                                         days_left = (expiry_date-current_date).days                                
#                                         context.update({"warranty_valid": warranty_valid})
#                                         if days_left > 1:
#                                             expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Days Left)"                                    
#                                         else:
#                                             expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Day Left)" 
#                                     context.update({"expiry_date_and_days_left" : expiry_date_and_days_left})                          
#                     else:
#                         messages.error(request, "The given product does not have warranty.")                    
#                         return render(request, 'home.html', context)
                    
#                 except Http404:
#                     # Check warranty with serial_number
#                     try:
#                         warrantied_product = get_object_or_404(Warranty, serial_number = id)                    
#                         context.update({"warrantied_product": warrantied_product})            
#                         if warrantied_product.duration:
#                             current_date = timezone.now().date()
#                             expiry_date = warrantied_product.expiry_date
#                             # date_difference = relativedelta(expiry_date, current_date)
#                             date_difference = expiry_date - current_date
#                             days_left = date_difference.days
#                             if current_date > expiry_date:
#                                 expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Warranty Completed)"                    
#                             elif expiry_date == current_date:
#                                 expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Expiring Today)"
#                             else:
#                                 if days_left > 1:
#                                     expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Days Left)"                                    
#                                 else:
#                                     expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Day Left)"
#                             context.update({"expiry_date_and_days_left" : expiry_date_and_days_left})

#                             try:
#                                 claimed_warranties = get_list_or_404(ClaimedWarranty, serial_number = id)
#                                 context.update({
#                                     "claimed_warranties" : claimed_warranties,                            
#                                     })
#                                 messages.success(request, "Claimed warranty.")
#                                 return render(request, 'home.html', context)
#                             except Http404:
#                                 try:
#                                     warranty_approved = get_object_or_404(ApprovedWarrantyApplication, serial_number = id)
#                                     feedback = warranty_approved.feedback
#                                     context.update({"warranty_approved" : warranty_approved})
#                                     context.update({"feedback": feedback})                    
#                                     messages.success(request, "The submitted warranty application has been approved.")
#                                     return render(request, 'home.html', context) 

#                                 except Http404:
#                                     try:
#                                         warranty_submitted = get_object_or_404(WarrantyApplication, serial_number = id)                                                                        
#                                         context.update({"warranty_submitted": warranty_submitted})
#                                         messages.success(request, "The warranty application has already been submitted.")
#                                         return render(request, 'home.html', context) 

#                                     except Http404:                                                        
#                                         if current_date > expiry_date:

#                                             # check service request with serial number
#                                             service_request = False                                                 
#                                             try:
#                                                 service_request = get_object_or_404(ServiceRequest, serial_number = id)
#                                                 scheduled_service = get_object_or_404(ScheduledService, pk = service_request.id)
#                                                 warrantied_product = get_object_or_404(Warranty, serial_number = scheduled_service.service_request.serial_number)
#                                                 # to get warrantied product using serial number from scheduled_service object.
#                                                 if warrantied_product.duration:
#                                                     current_date = timezone.now().date()
#                                                     expiry_date = warrantied_product.expiry_date
#                                                     # date_difference = relativedelta(expiry_date, current_date)
#                                                     date_difference = expiry_date - current_date
#                                                     days_left = date_difference.days
#                                                     if current_date > expiry_date:
#                                                         expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Warranty Completed)"                    
#                                                     elif expiry_date == current_date:
#                                                         expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Expiring Today)"
#                                                     else:
#                                                         if days_left > 1:
#                                                             expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Days Left)"                                    
#                                                         else:
#                                                             expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Day Left)"
#                                                     context.update({
#                                                         "scheduled_service": scheduled_service,
#                                                         "warrantied_product": warrantied_product,
#                                                         "expiry_date_and_days_left" : expiry_date_and_days_left,
#                                                     })                                            
#                                                 messages.success(request, f"Service scheduled for {scheduled_service.service_date.strftime("%d %b %Y")} at {scheduled_service.starting_time.strftime("%I:%M %p")}.")
#                                                 # return render(request, 'home.html', context)

#                                             except Http404:                        
#                                                 try:
#                                                     service_request = get_object_or_404(ServiceRequest, serial_number = id)                                            
#                                                     warrantied_product = get_object_or_404(Warranty, serial_number = service_request.serial_number)                        
#                                                     if warrantied_product.duration:
#                                                         current_date = timezone.now().date()
#                                                         expiry_date = warrantied_product.expiry_date
#                                                         # date_difference = relativedelta(expiry_date, current_date)
#                                                         date_difference = expiry_date - current_date
#                                                         days_left = date_difference.days
#                                                         if current_date > expiry_date:
#                                                             expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Warranty Completed)"                    
#                                                         elif expiry_date == current_date:
#                                                             expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Expiring Today)"
#                                                         else:
#                                                             if days_left > 1:
#                                                                 expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Days Left)"                                    
#                                                             else:
#                                                                 expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Day Left)"
#                                                         context.update({
#                                                             "service_request": service_request,
#                                                             "warrantied_product": warrantied_product,
#                                                             "expiry_date_and_days_left" : expiry_date_and_days_left,
#                                                         })                                    
#                                                     # return render(request, 'home.html', context)
                                                
#                                                 except Http404:
#                                                     service_valid = True
#                                                     context.update({"service_valid" : service_valid})

#                                             try:
#                                                 completed_services = get_list_or_404(CompletedService, serial_number = id)
#                                                 context.update({"completed_services": completed_services})
#                                                 try:
#                                                     service_request = get_object_or_404(ServiceRequest, serial_number = id)
#                                                     try:
#                                                         scheduled_service = get_object_or_404(ScheduledService, pk = service_request.id)
#                                                         context.update({"scheduled_service": scheduled_service})
#                                                     except Http404:
#                                                         context.update({"service_request": service_request})                                                
#                                                     warrantied_product = get_object_or_404(Warranty, serial_number = service_request.serial_number)
#                                                     if warrantied_product.duration:
#                                                         current_date = timezone.now().date()
#                                                         expiry_date = warrantied_product.expiry_date
#                                                         # date_difference = relativedelta(expiry_date, current_date)
#                                                         date_difference = expiry_date - current_date
#                                                         days_left = date_difference.days
#                                                         if current_date > expiry_date:
#                                                             expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Warranty Completed)"                    
#                                                         elif expiry_date == current_date:
#                                                             expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Expiring Today)"
#                                                         else:
#                                                             if days_left > 1:
#                                                                 expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Days Left)"                                    
#                                                             else:
#                                                                 expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Day Left)"
#                                                         context.update({
#                                                             "warrantied_product": warrantied_product,
#                                                             "expiry_date_and_days_left" : expiry_date_and_days_left,
#                                                             })                                                                                                
#                                                 except Http404:                                                
#                                                     if not service_request:
#                                                         messages.success(request, "Service completed.")
#                                                         return render(request, 'home.html', context)

#                                             except Http404:
#                                                 pass
#                                             return render(request, 'home.html', context)

#                                         elif expiry_date == current_date:
#                                             warranty_valid = True
#                                             context.update({"warranty_valid": warranty_valid})                                                                
#                                         else:
#                                             warranty_valid = True
#                                             days_left = (expiry_date-current_date).days                                
#                                             context.update({"warranty_valid": warranty_valid})
#                                             if days_left > 1:
#                                                 expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Days Left)"                                    
#                                             else:
#                                                 expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Day Left)" 
#                                         context.update({"expiry_date_and_days_left" : expiry_date_and_days_left})                                                                
#                         else:
#                             messages.error(request, "The given product does not have warranty.")                    
#                             return render(request, 'home.html', context)
                        
#                     except Http404:
#                         # check service request with id
#                         try:
#                             completed_service = get_object_or_404(CompletedService, pk = id)                        
#                             warrantied_product = get_object_or_404(Warranty, serial_number = completed_service.serial_number)
#                             completed_service_with_id = True                        
#                             if warrantied_product.duration:
#                                 current_date = timezone.now().date()
#                                 expiry_date = warrantied_product.expiry_date
#                                 # date_difference = relativedelta(expiry_date, current_date)
#                                 date_difference = expiry_date - current_date
#                                 days_left = date_difference.days
#                                 if current_date > expiry_date:
#                                     expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Warranty Completed)"                    
#                                 elif expiry_date == current_date:
#                                     expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Expiring Today)"
#                                 else:
#                                     if days_left > 1:
#                                         expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Days Left)"                                    
#                                     else:
#                                         expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Day Left)"
#                                 context.update({
#                                     "completed_service" : completed_service,
#                                     "warrantied_product": warrantied_product,
#                                     "completed_service_with_id": completed_service_with_id,
#                                     "expiry_date_and_days_left" : expiry_date_and_days_left,                       
#                                     })
#                             messages.success(request, "Service completed.")
#                             return render(request, 'home.html', context)

#                         except Http404:
#                             try:
#                                 scheduled_service = get_object_or_404(ScheduledService, pk = id)
#                                 # to get warrantied product using serial number from scheduled_service object.
#                                 warrantied_product = get_object_or_404(Warranty, serial_number = scheduled_service.service_request.serial_number)
#                                 if warrantied_product.duration:
#                                     current_date = timezone.now().date()
#                                     expiry_date = warrantied_product.expiry_date
#                                     # date_difference = relativedelta(expiry_date, current_date)
#                                     date_difference = expiry_date - current_date
#                                     days_left = date_difference.days
#                                     if current_date > expiry_date:
#                                         expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Warranty Completed)"                    
#                                     elif expiry_date == current_date:
#                                         expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Expiring Today)"
#                                     else:
#                                         if days_left > 1:
#                                             expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Days Left)"                                    
#                                         else:
#                                             expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Day Left)"
#                                     context.update({
#                                         "scheduled_service": scheduled_service,
#                                         "warrantied_product": warrantied_product,
#                                         "expiry_date_and_days_left" : expiry_date_and_days_left,
#                                     })                            
#                                 messages.success(request, f"Service scheduled for {scheduled_service.service_date.strftime("%d %b %Y")} at {scheduled_service.starting_time.strftime("%I:%M %p")}.")
#                                 return render(request, 'home.html', context)

#                             except Http404:                        
#                                 try:
#                                     service_request = get_object_or_404(ServiceRequest, pk = id)                        
#                                     warrantied_product = get_object_or_404(Warranty, serial_number = service_request.serial_number)                        
#                                     if warrantied_product.duration:
#                                         current_date = timezone.now().date()
#                                         expiry_date = warrantied_product.expiry_date
#                                         # date_difference = relativedelta(expiry_date, current_date)
#                                         date_difference = expiry_date - current_date
#                                         days_left = date_difference.days
#                                         if current_date > expiry_date:
#                                             expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Warranty Completed)"                    
#                                         elif expiry_date == current_date:
#                                             expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Expiring Today)"
#                                         else:
#                                             if days_left > 1:
#                                                 expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Days Left)"                                    
#                                             else:
#                                                 expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Day Left)"
#                                         context.update({
#                                             "service_request": service_request,
#                                             "warrantied_product": warrantied_product,
#                                             "expiry_date_and_days_left" : expiry_date_and_days_left,
#                                         })                                    
#                                     return render(request, 'home.html', context)                            

#                                 # checkin repair with id
#                                 except Http404:
#                                     try:
#                                         completed_repairs = get_list_or_404(CompletedRepair, pk = id)
#                                         messages.success(request, "Repair completed")
#                                         context.update({
#                                             "completed_repairs": completed_repairs
#                                             })
#                                         return render(request, 'home.html', context)
#                                     except Http404:
#                                         try:
#                                             repair_request = get_object_or_404(RepairRequest, pk = id)
#                                             try:
#                                                 scheduled_repair = get_object_or_404(ScheduledRepair, pk = id)
#                                                 messages.success(request, f"Repair is scheduled for {scheduled_repair.repair_date.strftime("%d %b %Y")} at {scheduled_repair.starting_time.strftime("%I:%M %p")}")
#                                                 context.update({
#                                                     "repair_request": repair_request,
#                                                     "scheduled_repair": scheduled_repair
#                                                     })
#                                                 return render(request, 'home.html', context)
#                                             except Http404:
#                                                     messages.success(request, "Repair request has been already submitted.")
#                                                     context.update({"repair_request": repair_request})
#                                                     return render(request, 'home.html', context)                                    
                                            
#                                             # checkin repair with serial number
#                                         except Http404:                                        
#                                             repair_request = False
#                                             try:
#                                                 repair_request = get_object_or_404(RepairRequest, serial_number = id)
#                                                 try:
#                                                     scheduled_repair = get_object_or_404(ScheduledRepair, pk = repair_request.pk)
#                                                     msg = f"Repair is scheduled for {scheduled_repair.repair_date.strftime("%d %b %Y")} at {scheduled_repair.starting_time.strftime("%I:%M %p")}"                                                
#                                                     context.update({
#                                                         "repair_request": repair_request,
#                                                         "scheduled_repair": scheduled_repair
#                                                         })
#                                                     # return render(request, 'home.html', context)
#                                                 except Http404:                                            
#                                                     msg = "Repair request has been already submitted."
#                                                     context.update({"repair_request": repair_request})
#                                                 # return render(request, 'home.html', context)
#                                             except Http404:
#                                                 pass

#                                             try:
#                                                 completed_repairs = get_list_or_404(CompletedRepair, serial_number = id)
#                                                 if not repair_request:
#                                                     msg = "Repair completed"                                            
#                                                 context.update({
#                                                     "completed_repairs": completed_repairs
#                                                     })
#                                                 messages.warning(request, msg)
#                                                 return render(request, 'home.html', context)
                                            

#                                             except Http404:                                            
#                                                 invalid = True
#                                                 context.update({"invalid": invalid})
#                                                 msg = "Invalid serial number or id."

#                                             messages.error(request, msg)
#                                             return render(request, 'home.html', context)
#     except SuspiciousOperation:
#         return render(request, 'home.html', context)
    
#     except PermissionDenied:
#         return render(request, 'home.html', context)

#     return render(request, 'home.html', context)               

def forgot_id(request):
    if request.method == 'POST':
        warrantied_products = False
        completed_services = False
        service_requests = False
        completed_repairs = False
        repair_requests = False        
        email = request.POST.get("email")

        valid_email_id = False

        try:
            warrantied_products = get_list_or_404(Warranty, email_id = email)
            valid_email_id = True
        except Http404:
            pass

        try:
            service_requests = get_list_or_404(ServiceRequest, email = email)
            valid_email_id = True
        except Http404:
            pass

        try:
            completed_services = get_list_or_404(CompletedService, email = email)
            valid_email_id = True
        except Http404:
            pass

        try:
            repair_requests = get_list_or_404(RepairRequest, email_id = email)
            valid_email_id = True
        except Http404:
            pass                    

        try:
            completed_repairs = get_list_or_404(CompletedRepair, email_id = email)
            valid_email_id = True
        except Http404:
            pass

        
        if valid_email_id:
            msg = ""
            if warrantied_products:
                msg += "\nWarranttied Products:\n"
                for warrantied_product in warrantied_products:                
                    msg += f"\nWarranty ID Date: {warrantied_product.id}\nProduct Name: {warrantied_product.product.name}\nSerial Number: {warrantied_product.serial_number}\n"
                msg += "\n"

            if service_requests:
                msg += "\nOngoing Services:\n"
                for service_request in service_requests:
                    msg += f"\nService ID Date: {service_request.id}\nProduct Name: {service_request.item_name}\nSerial Number: {service_request.serial_number}\n"
                msg += "\n"

            if completed_services:
                msg += "\nCompleted Services:\n"
                for completed_service in completed_services:
                    msg += f"\nService ID Date: {completed_service.id}\nProduct Name: {completed_service.item_name}\nSerial Number: {completed_service.serial_number}\n"
                msg += "\n"

            if completed_repairs:
                msg += "\nCompleted Repairs:\n"
                for completed_repair in completed_repairs:
                    msg += f"\nRepair ID Date: {completed_repair.id}\nProduct Name: {completed_repair.item_name} \nSerial Number: {completed_repair.serial_number}\n"
                msg += "\n"

            if repair_requests:
                msg += "\nOngoing Repairs:\n"
                for repair_request in repair_requests:
                    msg += f"\nRepair ID Date: {repair_request.id}\nProduct Name: {repair_request.item_name}\nSerial Number: {repair_request.serial_number}\n"
                msg += "\n"

            # if warrantied_products or completed_repairs:        
            subject = "Product IDs"
            message = msg
            from_email = 'w3digitalpmna@gmail.com'
            recipient_list = [str(email)]

            send_mail(subject, message, from_email, recipient_list)
            messages.success(request, "Please check your mail.")
            return redirect(home)

        else:            
            messages.error(request, "Invalid email id. Please check and try again.")
            return redirect(home)

    return render(request, 'home.html')

def service_tracking(request):    
    context = {}
    clients = Client.objects.all()
    context.update({"clients": clients})
    products = Product.objects.all
    context.update({"products": products})
    if request.user:
        try:
            customer = get_object_or_404(Customer, email = request.user.username)
            context.update({"customer": customer})
        except Http404:
            pass
    expiry_date_and_days_left = False
    service_valid = False
    warrantied_product = False
    completed_services = False
    service_request = False
    scheduled_service = False
    try:
        if request.method == "POST":
            id = request.POST["id"]
            if id != "" and " " not in str(id):
                context.update({"id": id})
                if str(id).startswith("SVS"):                    
                    try:
                        completed_services = get_list_or_404(CompletedService, id = id)
                        completed_service = CompletedService.objects.filter(id = id).first()
                        warrantied_product = get_object_or_404(Warranty, serial_number = completed_service.serial_number)
                        context.update({
                            "completed_services": completed_services,
                            "warrantied_product": warrantied_product,
                            })
                    except Http404:
                        pass
                    try:
                        service_request = get_object_or_404(ServiceRequest, id = id)
                        warrantied_product = get_object_or_404(Warranty, serial_number = service_request.serial_number)
                        context.update({
                            "service_request": service_request,
                            "warrantied_product": warrantied_product
                            })
                        try:
                            scheduled_service = get_object_or_404(ScheduledService, id = id)
                            context.update({"scheduled_service": scheduled_service})
                        except Http404:
                            pass                        
                    except Http404:
                        pass
                else:
                    try:
                        completed_services = get_list_or_404(CompletedService, serial_number = id)                        
                        warrantied_product = get_object_or_404(Warranty, serial_number = id)
                        context.update({
                            "completed_services": completed_services,
                            "warrantied_product": warrantied_product,
                            })
                    except Http404:
                        pass
                    try:
                        service_request = get_object_or_404(ServiceRequest, serial_number = id)
                        warrantied_product = get_object_or_404(Warranty, serial_number = id)
                        context.update({
                            "service_request": service_request,
                            "warrantied_product": warrantied_product
                            })
                        try:
                            scheduled_service = get_object_or_404(ScheduledService, service_request__serial_number = id)
                            context.update({"scheduled_service": scheduled_service})
                        except Http404:
                            pass
                    except Http404:
                        pass
            
            else:
                messages.error(request, "Please provide service id or serial number.")

            if warrantied_product:
                if warrantied_product.duration:
                    current_date = timezone.now().date()
                    expiry_date = warrantied_product.expiry_date
                    date_difference = expiry_date - current_date
                    days_left = date_difference.days
                    if current_date > expiry_date:
                        service_valid = True
                        context.update({"service_valid": service_valid})
                        expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Warranty Completed)"                    
                    elif expiry_date == current_date:
                        expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Expiring Today)"
                    else:
                        if days_left > 1:
                            expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Days Left)"                                    
                        else:
                            expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Day Left)"
                    context.update({"expiry_date_and_days_left" : expiry_date_and_days_left})

            if service_request:
                if scheduled_service:
                    messages.info(request, "Service has been scheduled.")
                else:
                    messages.info(request, "Service requested.")
            elif completed_services:
                last_serviced_date = False
                if str(id).startswith("SVS"): 
                    last_serviced_date = CompletedService.objects.filter(id = id).latest('service_date').service_date
                else:
                    last_serviced_date = CompletedService.objects.filter(serial_number = id).latest('service_date').service_date
                if last_serviced_date:
                    available_service_date = last_serviced_date + timedelta(days = 90)
                    if current_date < available_service_date:
                        service_valid = False
                        context["service_valid"] = service_valid
                    messages.success(request, "Service Completed.")
            else:
                if id != "" and " " not in str(id):
                    messages.error(request, "Invalid service id or serial number.")
        return render(request, 'service_tracking.html', context)
    
    except SuspiciousOperation:
        return render(request, 'service_tracking.html', context)
    
    except PermissionDenied:
        return render(request, 'service_tracking.html', context)

def warranty_tracking(request):
    context = {}
    clients = Client.objects.all()
    context.update({"clients": clients})
    products = Product.objects.all
    context.update({"products": products})
    if request.user:
        try:
            customer = get_object_or_404(Customer, email = request.user.username)
            context.update({"customer": customer})
        except Http404:
            pass
    expiry_date_and_days_left = False
    warranty_valid = False
    service_valid = False
    warrantied_product = False
    claimed_warranties = False
    warranty_application = False
    approved_warranty = False
    try:
        if request.method == "POST":
            id = request.POST["id"]
            if id != "" and " " not in str(id):
                context.update({"id": id})
                if str(id).startswith("WTY"):
                    try:
                        warrantied_product = get_object_or_404(Warranty, id = id)
                        context.update({"warrantied_product": warrantied_product})
                        try:
                            claimed_warranties = get_list_or_404(ClaimedWarranty, warranty_id = id)
                            context.update({"claimed_warranties": claimed_warranties})
                        except Http404:
                            pass
                        try:
                            warranty_application = get_object_or_404(WarrantyApplication, id = id)                            
                            context.update({"warranty_application": warranty_application})
                        except Http404:
                            pass
                        try:
                            approved_warranty = get_object_or_404(ApprovedWarrantyApplication, id = id)
                            context.update({"approved_warranty": approved_warranty})
                        except Http404:
                            pass
                    except Http404:
                        pass
                else:  
                    try:
                        warrantied_product = get_object_or_404(Warranty, serial_number = id)
                        context.update({"warrantied_product": warrantied_product})
                        try:
                            claimed_warranties = get_list_or_404(ClaimedWarranty, serial_number = id)
                            context.update({"claimed_warranties": claimed_warranties})
                        except Http404:
                            pass
                        try:
                            warranty_application = get_object_or_404(WarrantyApplication, serial_number = id)
                            context.update({"warranty_application": warranty_application})
                        except Http404:
                            pass
                        try:
                            approved_warranty = get_object_or_404(ApprovedWarrantyApplication, serial_number = id)
                            context.update({"approved_warranty": approved_warranty})
                        except Http404:
                            pass
                    except Http404:
                        pass
            
            else:
                messages.error(request, "Please provide warranty id or serial number.")

            if warrantied_product:            
                if warrantied_product.duration:
                    current_date = timezone.now().date()
                    expiry_date = warrantied_product.expiry_date
                    date_difference = expiry_date - current_date
                    days_left = date_difference.days
                    if current_date > expiry_date:
                        last_serviced_date = False
                        if str(id).startswith("WTY"):
                            try:
                                last_serviced_date = CompletedService.objects.filter(warranty_id = id).latest('service_date').service_date
                            except:
                                pass
                        else:
                            try:
                                last_serviced_date = CompletedService.objects.filter(serial_number = id).latest('service_date').service_date
                            except:
                                pass
                        if last_serviced_date:
                            available_service_date = last_serviced_date + timedelta(days = 90)
                            if current_date > available_service_date:
                                service_valid = True                            
                                context.update({"service_valid": service_valid})                        
                        expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Warranty Completed)"                    
                    elif expiry_date == current_date:
                        warranty_valid = True
                        context.update({"warranty_valid": warranty_valid})
                        expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} (Expiring Today)"
                    else:
                        if days_left > 1:
                            expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Days Left)"                                    
                        else:
                            expiry_date_and_days_left = f"{warrantied_product.expiry_date.strftime('%d-%m-%Y')} ({days_left} Day Left)"
                        warranty_valid = True
                        context.update({"warranty_valid": warranty_valid})
                    context.update({"expiry_date_and_days_left" : expiry_date_and_days_left})

            if warrantied_product:
                if warranty_application:                    
                    if approved_warranty:
                        messages.info(request, "Warranty has been approved.")
                    else:
                        messages.info(request, "Warranty application has been submitted.")
                elif claimed_warranties:
                    last_claimed_date = False
                    if str(id).startswith("WTY"):
                        try:
                            last_claimed_date = ClaimedWarranty.objects.filter(warranty_id = id).latest('approved_datetime').approved_datetime.date()
                        except:
                            pass
                    else:
                        try:
                            last_claimed_date = ClaimedWarranty.objects.filter(serial_number = id).latest('approved_datetime').approved_datetime.date()
                        except:
                            pass
                    if last_claimed_date:
                        warranty_claimable_date = last_claimed_date + timedelta(days = 30)                    
                        if current_date < warranty_claimable_date:
                            warranty_valid = False
                            context["warranty_valid"] = warranty_valid
                    messages.success(request, "Warranty claimed.")
            else:
                if id != "" and " " not in str(id):
                    messages.error(request, "Invalid warranty id or serial number.")
        return render(request, 'warranty_tracking.html', context)

    except SuspiciousOperation:
        return render(request, 'warranty_tracking.html', context)
    
    except PermissionDenied:
        return render(request, 'warranty_tracking.html', context)

def repair_tracking(request):
    context = {}
    clients = Client.objects.all()
    context.update({"clients": clients})
    products = Product.objects.all()
    context.update({"products": products})
    if request.user:
        try:
            customer = get_object_or_404(Customer, email = request.user.username)
            context.update({"customer": customer})
        except Http404:
            pass
    completed_repairs = False
    repair_request = False
    scheduled_repair = False
    try:
        if request.method == "POST":
            id = request.POST["id"]
            if id != "" and " " not in str(id):
                context.update({"id": id})
                if str(id).startswith("REP"):                    
                    try:
                        completed_repairs = get_list_or_404(CompletedRepair, id = id)                                                
                        context.update({"completed_repairs": completed_repairs})
                    except Http404:
                        pass
                    try:
                        repair_request = get_object_or_404(RepairRequest, id = id)
                        context.update({"repair_request": repair_request})
                        try:
                            scheduled_repair = get_object_or_404(ScheduledRepair, id = id)
                            context.update({"scheduled_repair": scheduled_repair})
                        except Http404:
                            pass                        
                    except Http404:
                        pass
                else:
                    try:
                        completed_repairs = get_list_or_404(CompletedRepair, serial_number = id)
                        context.update({"completed_repairs": completed_repairs})
                    except Http404:
                        pass
                    try:
                        repair_request = get_object_or_404(RepairRequest, serial_number = id)
                        context.update({
                            "repair_request": repair_request})
                        try:
                            scheduled_repair = get_object_or_404(ScheduledRepair, repair_request__serial_number = id)
                            context.update({"scheduled_repair": scheduled_repair})
                        except Http404:
                            pass
                    except Http404:
                        pass
            
            else:
                messages.error(request, "Please provide repair id or serial number.")            

            if repair_request:
                if scheduled_repair:
                    messages.info(request, "Repair has been scheduled.")
                else:
                    messages.info(request, "Repair requested.")
            elif completed_repairs:                
                messages.success(request, "Repair Completed.")
            else:
                if id != "" and " " not in str(id):
                    messages.error(request, "Invalid repair id or serial number.")
        return render(request, 'repair_request.html', context)
    
    except SuspiciousOperation:
        return render(request, 'repair_request.html', context)
    
    except PermissionDenied:
        return render(request, 'repair_request.html', context)

def apply_warranty(request, pk):
    context = {}
    if request.user:
        try:
            customer = get_object_or_404(Customer, email = request.user.username)
            context.update({"customer": customer})
        except Http404:
            pass
    products = Product.objects.all()
    context.update({"products": products})
    try:
        warrantied_product = get_object_or_404(Warranty, pk=pk)
        context.update({"warrantied_product": warrantied_product})
        purchased_date = str(warrantied_product.date) # to fetch date in the form        
        context.update({"purchased_date": purchased_date})
        if request.method == "POST":            
            product_complain = request.POST["product_complain"]
            WarrantyApplication.objects.create(
                id = warrantied_product.id,
                customer_name = warrantied_product.customer_name,
                purchase_date = warrantied_product.date,
                duration = warrantied_product.duration,
                contact_number = warrantied_product.contact_number,
                email_id = warrantied_product.email_id,
                alternative_number = warrantied_product.alternative_number,
                product = warrantied_product.product,
                billing_name = warrantied_product.billing_name,
                invoice_number = warrantied_product.invoice_number,
                serial_number = warrantied_product.serial_number,
                model_number = warrantied_product.model_number,
                expiry_date = warrantied_product.expiry_date,
                product_complain = product_complain
                )            
            messages.success(request, "Successfully applied for warranty claim.")
            return redirect(home)        
    except Http404:
        messages.error(request, "The given product does not exist in our database.")        
    return render(request, "warranty_request.html", context)
    

def service_request(request, pk):
    context = {}
    clients = Client.objects.all()
    context.update({"clients": clients})
    products = Product.objects.all
    context.update({"products": products})
    if request.user:
        try:
            customer = get_object_or_404(Customer, email = request.user.username)
            context.update({"customer": customer})
        except Http404:
            pass
    warrantied_product = get_object_or_404(Warranty, pk=pk)
    products = Product.objects.all()
    context.update({
        "warrantied_product": warrantied_product,
        "products": products,
        })
    if request.method == "POST":
        prefered_date = request.POST.get("prefered_date")
        contact_number = request.POST.get("contact_number")
        alternative_number = request.POST.get("alternative_number")
        address_site = request.POST.get("address_site")
        service_description = request.POST.get("service_description")
        try:
            ServiceRequest.objects.create(
                customer_name = warrantied_product.customer_name,
                email = warrantied_product.email_id,
                alternative_number = alternative_number,
                address_site = address_site,
                item_name = warrantied_product.product,
                contact_number = contact_number,
                prefered_date = prefered_date,
                serial_number = warrantied_product.serial_number,
                bussiness_name = warrantied_product.billing_name,
                service_description = service_description,
            )
            messages.success(request, "Service request submitted successfully.")
            return redirect(home)            
        except IntegrityError:
            messages.error(request, "Service request for the given serial number has been already registered.")
            return redirect(home)
    return render(request, 'service_request.html', context)

def request_repair(request):
    context = {}
    clients = Client.objects.all()
    context.update({"clients": clients})
    products = Product.objects.all()
    context.update({"products": products})
    if request.user:
        try:
            customer = get_object_or_404(Customer, email = request.user.username)
            context.update({"customer": customer})
        except Http404:
            pass
    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        alternative_number = request.POST.get("alternative_number")
        address_customer = request.POST.get("address_customer")
        email_id = request.POST.get("email_id")
        item_name = request.POST.get("item_name")
        contact_number = request.POST.get("contact_number")
        serial_number = request.POST.get("serial_number")
        item_description = request.POST.get("item_description")

        current_date = timezone.now().date()
        last_repaired_date = False
        try:
            last_repaired_date = CompletedRepair.objects.filter(serial_number = serial_number).latest('repair_date').repair_date
        except:
            pass
        if last_repaired_date:
            available_repair_date = last_repaired_date + timedelta(days = 90)
            if current_date < available_repair_date:                
                messages.warning(request, f"The next repair will only be available on or after {available_repair_date.strftime('%d-%B-%Y')}")
                return render(request, 'repair_request.html', context)
        try:
            RepairRequest.objects.create(
                customer_name = customer_name,
                alternative_number = alternative_number,
                address_customer = address_customer,
                email_id = email_id,
                item_name = item_name,
                contact_number = contact_number,
                serial_number = serial_number,
                item_description = item_description,                
            )
            messages.success(request, "Repair request submitted successfully.")
            return redirect(home)
        except IntegrityError:
            -messages.warning(request, "Serial number already exists in the database.")
            return render(request, 'repair_request.html', context)
    return render(request, 'repair_request.html', context)

@user_passes_test(not_superuser, login_url=customer_login)
def warranty_history(request):
    context = {}    
    try:
        customer = get_object_or_404(Customer, email = request.user.username)
        context.update({"customer": customer})
    except Http404:
        pass  
    username = request.user.username
    claimed_warranties = False
    approved_warranties = False
    warranty_applications = False

    try:
        claimed_warranties = get_list_or_404(ClaimedWarranty, email_id = username)
        context.update({"claimed_warranties" : claimed_warranties})
    except Http404:
        pass

    try:
        approved_warranties = get_list_or_404(ApprovedWarrantyApplication, email_id = username)
        context.update({"approved_warranties" : approved_warranties})
    except Http404:
        pass

    try:
        warranty_applications = get_list_or_404(WarrantyApplication, email_id = username)
        context.update({"warranty_applications" : warranty_applications})
    except Http404:
        pass

    return render(request, 'secured/warranty_history.html', context)    

@user_passes_test(not_superuser, login_url=customer_login)
def service_history(request):
    context = {}    
    try:
        customer = get_object_or_404(Customer, email = request.user.username)
        context.update({"customer": customer})
    except Http404:
        pass  
    username = request.user.username
    completed_services = False
    scheduled_services = False
    service_requests = False

    try:
        completed_services = get_list_or_404(CompletedService, email = username)
        context.update({"completed_services" : completed_services})
    except Http404:
        pass

    try:
        scheduled_services = get_list_or_404(ScheduledService, service_request__email = username)
        context.update({"scheduled_services" : scheduled_services})
    except Http404:
        pass

    try:
        service_requests = get_list_or_404(ServiceRequest, email = username)
        context.update({"service_requests" : service_requests})
    except Http404:
        pass

    return render(request, 'secured/service_history.html', context)    

@user_passes_test(not_superuser, login_url=customer_login)
def repair_history(request):
    context = {}    
    try:
        customer = get_object_or_404(Customer, email = request.user.username)
        context.update({"customer": customer})
    except Http404:
        pass  
    username = request.user.username
    completed_repairs = False
    scheduled_repairs = False
    repair_requests = False

    try:
        completed_repairs = get_list_or_404(CompletedRepair, email_id = username)
        context.update({"completed_repairs" : completed_repairs})
    except Http404:
        pass

    try:
        scheduled_repairs = get_list_or_404(ScheduledRepair, repair_request__email_id = username)
        context.update({"scheduled_repairs" : scheduled_repairs})
    except Http404:
        pass

    try:
        repair_requests = get_list_or_404(RepairRequest, email_id = username)
        context.update({"repair_requests" : repair_requests})
    except Http404:
        pass

    return render(request, 'secured/repair_history.html', context)    
