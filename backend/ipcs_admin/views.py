from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.db import IntegrityError
from django.http import Http404
from django.contrib import messages
from .models import *
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.templatetags.static import static

# Administrator!

def is_superuser(user):
    return user.is_authenticated and user.is_superuser

def admin_login(request):
    if request.user.is_superuser and request.user.is_superuser:
        return redirect(home)
    try:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_superuser:
                    login(request,user)
                    return redirect(home)
                else:
                    messages.warning(request, "Unauthorized user.")
            else:
                messages.error(request,"Username or Password is incorrect")
                return redirect(admin_login)
    except SuspiciousOperation:
        return render(request, 'sign-in.html')
    
    except PermissionDenied:
        return render(request, 'sign-in.html')
    return render(request, 'sign-in.html')

@user_passes_test(is_superuser, login_url=admin_login)
def admin_logout(request):
    logout(request)
    return redirect(admin_login)

@user_passes_test(is_superuser, login_url=admin_login)
def home(request):    
    return render(request, 'admin_home.html')    
    
@user_passes_test(is_superuser, login_url=admin_login)
def reset_password(request):
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
                return redirect(admin_login)
            else:
                messages.warning(request, "New passwords do not match.")
                return redirect(reset_password)
        else:
            messages.error(request, "Invalid current password.")
            return redirect(reset_password)
    return render(request, 'reset_password.html')

@user_passes_test(is_superuser, login_url=admin_login)
def add_product(request):
    if request.method == "POST":
        product_name = request.POST.get("product_name")
        image = request.FILES.get("image")
        link = request.POST.get("link")        
        if product_name != "" and not str(product_name).startswith(" "):
            try:
                Product.objects.create(name = product_name, image = image, link = link)
                messages.success(request, "Product created successfully.")          
                return redirect(add_product)
            except IntegrityError:
                messages.error(request, "This product already exists.")
                return redirect(add_product)  

    return render(request, 'products/add_product.html')            

@user_passes_test(is_superuser, login_url=admin_login)
def list_products(request):
    products = Product.objects.all().order_by('name')
    context = {
        "products": products,
    }
    return render(request, 'products/list_products.html', context)

@user_passes_test(is_superuser, login_url=admin_login)
def detail_product(request, pk):    
    try:
        product = get_object_or_404(Product, pk = pk)            
    except Http404:
        messages.error(request, "Error. Product not found.")
    context = {
        "product": product
    }
    return render(request, 'products/detail_product.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)
def update_product(request, pk):    
    context = {}
    try:
        product = get_object_or_404(Product, pk=pk)
        if request.method == "POST":
            product_name = request.POST.get("product_name")
            image = request.FILES.get("image")
            link = request.POST["link"]
            # updaing product object
            if product_name != "" or not str(product_name).startswith(" "):
                product.name = product_name
                product.link = link
                if image:
                    product.image = image                                                        
                product.save()                        
                messages.success(request, "Product updated successfully")
                return redirect(detail_product, pk)
            else:
                messages.warning(request, "Product name cannot be blank or begin with white space.")
                return redirect(update_product, pk)
        context.update({"product": product})
    except Http404:
        messages.error(request, "Error. Product not found.")
    return render(request, 'products/update_product.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)
def delete_product(request, pk):    
    try:
        product = get_object_or_404(Product, pk = pk)
        product.delete()
        messages.success(request, "Product deleted successfully.")
    except Http404:
        messages.error(request, "Error. Product not found.")
    return redirect(list_products)    

@user_passes_test(is_superuser, login_url=admin_login)
def add_client(request):
    if request.method == "POST":
        name = request.POST.get("name")
        image = request.FILES.get("image")
        try:
            Client.objects.create(name = name, image = image)
            messages.success(request, "Client added successfully.")
            return redirect(add_client)
        except IntegrityError:
            messages.warning(request, "This client already exists.")
            return redirect(add_client)
    return render(request, 'client/add_client.html')        

@user_passes_test(is_superuser, login_url=admin_login)
def list_clients(request):    
    clients = Client.objects.all().order_by('name')
    context = {
        "clients": clients,
    }
    return render(request, 'client/list_clients.html', context)

@user_passes_test(is_superuser, login_url=admin_login)
def detail_client(request, pk):    
    try:
        client = get_object_or_404(Client, pk = pk)            
    except Http404:
        messages.error(request, "Error. Client not found.")
    context = {
        "client": client
    }
    return render(request, 'client/detail_client.html', context)

@user_passes_test(is_superuser, login_url=admin_login)
def update_client(request, pk):    
    context = {}
    try:
        client = get_object_or_404(Client, pk=pk)
        if request.method == "POST":
            name = request.POST.get("name")
            image = request.FILES.get("image")            
            # updaing client object
            client.name = name            
            if image:
                client.image = image            
            client.save()                        
            messages.success(request, "Client updated successfully")
            return redirect(detail_client, pk)                
        context.update({"client": client})
    except Http404:
        messages.error(request, "Error. Client not found.")
    return render(request, 'client/update_client.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)
def delete_client(request, pk):    
    try:
        client = get_object_or_404(Client, pk = pk)
        client.delete()
        messages.success(request, "Client deleted successfully.")
    except Http404:
        messages.error(request, "Error. Client not found.")
    return redirect(list_clients)

@user_passes_test(is_superuser, login_url=admin_login)
def add_technician(request):    
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        department = request.POST.get("department")
        residential_location = request.POST.get("residential_location")
        photo = request.FILES.get("photo")
        try:
            Technician.objects.create(
                name = name,
                email = email,
                mobile = mobile,
                department = department,
                residential_location = residential_location,
                photo = photo
            )
            messages.success(request, "Created technician successfully.")        
            return redirect(list_technicians)
        except IntegrityError:
            messages.warning(request, "Technician with same contact number or email already exists.")
            return redirect(list_technicians)
    return render(request, 'technician/add_technician.html')    

@user_passes_test(is_superuser, login_url=admin_login)
def list_technicians(request):    
    technicians = Technician.objects.all().order_by("name")
    context = {
        "technicians": technicians,
    }
    return render(request, 'technician/list_technicians.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)
def detail_technician(request, pk):    
    context = {}            
    try:
        technician = get_object_or_404(Technician, pk = pk)
        context.update({"technician": technician})          
    except Http404:
        messages.error(request, "Error. Technician not found.")
    return render(request, 'technician/detail_technician.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)
def update_technician(request, pk):    
    context = {}
    try:   
        technician = get_object_or_404(Technician, pk=pk)
        if request.method == "POST":
            name = request.POST.get("name")
            email = request.POST.get("email")
            mobile = request.POST.get("mobile")
            department = request.POST.get("department")
            residential_location = request.POST.get("residential_location")
            photo = request.FILES.get("photo")

            # updating technician object
            technician.name = name
            technician.email = email
            technician.mobile = mobile
            technician.department = department
            technician.residential_location = residential_location            

            # update photo if provided
            if photo:
                technician.photo = photo

            # save the updated technician object
            try:
                technician.save()
            except IntegrityError:
                messages.warning(request, "Technician with same contact number or email already exists.")
                return redirect(list_technicians)


            messages.success(request, "Technician updated successfully.")
            return redirect(detail_technician, pk)
        context.update({"technician" : technician})        
    except Http404:
        messages.error(request, "Error. Technician not found.")
    return render(request, 'technician/update_technician.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)
def delete_technician(request, pk):    
    try:
        technician = get_object_or_404(Technician, pk = pk)        
        technician.delete()
        messages.success(request, "Technician deleted successfully.")
    except Http404:
        messages.error(request, "Error. Technician not found.")
    return redirect(list_technicians)    

#  Adding warranty
@user_passes_test(is_superuser, login_url=admin_login)
def add_warranty(request):    
    context = {}
    products = Product.objects.all()
    context.update({"products" : products})
    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        date = request.POST.get("date")
        email_id = request.POST.get("email_id")
        contact_number = request.POST.get("contact_number")
        alternative_number = request.POST.get("alternative_number")
        product_id = request.POST.get("product_id")
        try:
            product = get_object_or_404(Product, pk = product_id)
        except Http404:
            messages.error(request, "Error. Invalid product.")
            return redirect(add_warranty)
        billing_name = request.POST.get("billing_name")
        invoice_number = request.POST.get("invoice_number")
        serial_number = request.POST.get("serial_number")
        model_number = request.POST.get("model_number")
        duration = request.POST.get("duration")
        try:
            Warranty.objects.create(
                customer_name = customer_name,
                date = date,
                email_id = email_id,
                contact_number = contact_number,
                alternative_number = alternative_number,
                product = product,
                billing_name = billing_name,
                invoice_number = invoice_number,
                serial_number = serial_number,
                model_number = model_number,
                duration = duration,
            )
            messages.success(request, "Warranty successfully created.")
            return redirect(add_warranty)
        except IntegrityError:
            default_date = str(date)
            context.update({
                "customer_name": customer_name,
                "default_date": default_date,
                "email_id": email_id,
                "contact_number": contact_number,
                "alternative_number": alternative_number,
                "product_id":  get_object_or_404(Product, pk = product_id),
                "billing_name": billing_name,
                "invoice_number": invoice_number,
                "model_number": model_number,
                "duration": duration,
            })
            messages.error(request, "Warranty for the given serial number is already registered.")
            return render(request, 'warranty/add_warranty.html', context)
    return render(request, 'warranty/add_warranty.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)
def update_warranty(request, pk):    
    context = {}
    try:
        products = Product.objects.all()
        warrantied_product = get_object_or_404(Warranty, pk = pk)
        context.update({
            "products": products,
            "warrantied_product": warrantied_product,
            })   
        date = str(warrantied_product.date)
        if request.method == 'POST':
            customer_name = request.POST.get("customer_name")
            date = request.POST.get("date")
            email_id = request.POST.get("email_id")
            contact_number = request.POST.get("contact_number")
            alternative_number = request.POST.get("alternative_number")
            product_id = request.POST.get("product_id")
            try:
                product = get_object_or_404(Product, pk = product_id)
            except Http404:
                messages.error(request, "Error. Invalid product.")
                return redirect(add_warranty)
            billing_name = request.POST.get("billing_name")
            invoice_number = request.POST.get("invoice_number")
            serial_number = request.POST.get("serial_number")
            model_number = request.POST.get("model_number")
            duration = request.POST.get("duration")
            
            # updating warranty object  
            warrantied_product.customer_name = customer_name
            warrantied_product.date = date
            warrantied_product.email_id = email_id
            warrantied_product.contact_number = contact_number
            warrantied_product.alternative_number = alternative_number
            warrantied_product.product = product
            warrantied_product.billing_name = billing_name
            warrantied_product.invoice_number = invoice_number
            warrantied_product.serial_number = serial_number
            warrantied_product.model_number = model_number
            warrantied_product.duration = duration
            warrantied_product.save()
            messages.success(request, "Warranty updated")
            return redirect(detail_warrantied_product, pk)
    except Http404:
        messages.error(request, "Error! Warranty not found.")
    context.update({"date": date})
    return render(request, 'warranty/update_warrantied_product.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)
def delete_warranty(request, pk):    
    try:
        warrantied_product = get_object_or_404(Warranty, pk = pk)
        warrantied_product.delete()
        messages.success(request, "Successfully deleted the warranty record.")
        return redirect(list_warrantied_products)
    except Http404:
        return redirect(list_warrantied_products)

@user_passes_test(is_superuser, login_url=admin_login)
def list_warrantied_products(request):    
    warrantied_products = Warranty.objects.all().order_by('id')
    context = {
        "warrantied_products" : warrantied_products,
    }
    return render(request, 'warranty/list_warrantied_products.html', context)

@user_passes_test(is_superuser, login_url=admin_login)
def detail_warrantied_product(request, pk):    
    context = {}
    try:
        warrantied_product = get_object_or_404(Warranty, pk = pk)        
        context.update({"warrantied_product": warrantied_product})
    except Http404:
        messages.error(request, f"Error. Warrantied product not found.")
        return redirect(list_warrantied_products)
    return render(request, 'warranty/detail_warrantied_product.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)
def list_warranty_applications(request):    
    applications = WarrantyApplication.objects.all().order_by("-application_date")
    context = {
        "applications": applications
    }
    return render(request, "warranty/list_warranty_applications.html", context)    

# warranty applications
@user_passes_test(is_superuser, login_url=admin_login)
def detail_warranty_application(request, pk):    
    context = {}
    try:
        application = get_object_or_404(WarrantyApplication, pk = pk)
        application_already_submitted = False
        approve_application = ApprovedWarrantyApplication.objects.filter(pk = pk).first()
        if approve_application:
                application_already_submitted = True
        context.update({
            "application": application,
            "application_already_submitted": application_already_submitted
        })
    except Http404:
        messages.error(request, "Error. Warranty application not found.")
    return render(request, "warranty/detail_warranty_application.html", context)    

@user_passes_test(is_superuser, login_url=admin_login)
def approve_warranty(request, pk):    
    try:
        application = get_object_or_404(WarrantyApplication, pk = pk)    
        ApprovedWarrantyApplication.objects.create(
            application_date = application.application_date, 
            id = application.id,
            customer_name = application.customer_name,
            purchase_date = application.purchase_date,
            duration = application.duration,
            contact_number = application.contact_number,
            email_id = application.email_id,
            alternative_number = application.alternative_number,
            product = application.product,
            billing_name = application.billing_name,
            invoice_number = application.invoice_number,
            serial_number = application.serial_number,
            model_number = application.model_number,
            expiry_date = application.expiry_date,
            product_complain = application.product_complain,
        )
        try:
            get_object_or_404(ApprovedWarrantyApplication, pk= pk)            
            application.delete()
            messages.success(request, "The warranty has been approved.")
            return redirect(list_warranty_applications)
        except Http404:
            messages.error(request, "Error in approving application.")        
    except Http404:
        messages.error(request, "Error. Warranty application not found.")
    return redirect(detail_approved_warranty_application, pk)    

@user_passes_test(is_superuser, login_url=admin_login)
def list_approved_warranty_applications(request):    
    applications = ApprovedWarrantyApplication.objects.all().order_by("-approved_datetime")        
    context = {
        "applications": applications,        
    }
    return render(request, "warranty/list_warranty_approved.html", context)    

@user_passes_test(is_superuser, login_url=admin_login)
def detail_approved_warranty_application(request, pk):    
    context = {}
    try:
        application = get_object_or_404(ApprovedWarrantyApplication, pk = pk)
        feedback = application.feedback
        if request.method == "POST":
            feedback = request.POST.get("feedback")
            application.feedback = feedback
            application.save()            
            messages.success(request, "Feedback has been updated.")
            return redirect(detail_approved_warranty_application, pk)
        context.update({
            "application": application,
            "feedback" : feedback
        })
    except Http404:
        messages.error(request, "Error. Approved application not found.")
    return render(request, "warranty/detail_warranty_approved.html", context)        

@user_passes_test(is_superuser, login_url=admin_login)
def delete_approved_warranty_application(request, pk):    
    try:
        approved_warranty_application = get_object_or_404(ApprovedWarrantyApplication, pk = pk)
        approved_warranty_application.delete()
        messages.success(request, "Successfully deleted approved warranty application.")
    except Http404:
        messages.error(request, "Error. Approved warranty application not found.")
    return redirect(list_approved_warranty_applications)    

@user_passes_test(is_superuser, login_url=admin_login)
def complete_warranty(request, pk):    
    context = {}
    try:
        approve_warranty = get_object_or_404(ApprovedWarrantyApplication, pk=pk)
        context.update({"approve_warranty": approve_warranty})
        try:
            ClaimedWarranty.objects.create(
                application_date = approve_warranty.application_date, 
                warranty_id = approve_warranty.id,
                customer_name = approve_warranty.customer_name,
                purchase_date = approve_warranty.purchase_date,
                duration = approve_warranty.duration,
                contact_number = approve_warranty.contact_number,
                email_id = approve_warranty.email_id,
                alternative_number = approve_warranty.alternative_number,
                product = approve_warranty.product,
                billing_name = approve_warranty.billing_name,
                invoice_number = approve_warranty.invoice_number,
                serial_number = approve_warranty.serial_number,
                model_number = approve_warranty.model_number,
                expiry_date = approve_warranty.expiry_date,
                product_complain = approve_warranty.product_complain,
            )
            try:
                get_list_or_404(ClaimedWarranty, warranty_id = pk)
                approve_warranty.delete()
                messages.success(request, "Warranty claim successfull.")
                return redirect(list_approved_warranty_applications)
            except Http404:
                messages.error(request, "Error claiming warranty.")
        except IntegrityError:
            messages.warning(request, "Warranty already completed.")
            # return redirect() 
        return redirect(detail_approved_warranty_application, pk)
    except Http404:
        messages.error(request, "Invalid approved warranty.")
        return redirect(list_approved_warranty_applications)    

@user_passes_test(is_superuser, login_url=admin_login)   
def list_completed_warranties(request):    
    completed_warranties = ClaimedWarranty.objects.all().order_by("pk")
    context = {
        "completed_warranties": completed_warranties,
    }
    return render(request, 'warranty/list_completed_warranties.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)
def detail_completed_warranty(request, pk):    
    context = {}
    try:
        completed_warranty = get_object_or_404(ClaimedWarranty, pk = pk)
        context.update({"completed_warranty": completed_warranty})        
    except Http404:
        messages.error(request, "Invalid completed warranty.")
        return redirect(list_completed_warranties)
    return render(request, 'warranty/detail_completed_warranty.html', context)    

# service
@user_passes_test(is_superuser, login_url=admin_login)
def list_service_requests(request):    
    service_requests = ServiceRequest.objects.all().order_by("-application_datetime")
    scheduled_services = ScheduledService.objects.values_list('id' , flat=True)
    service_requests = service_requests.exclude(pk__in = scheduled_services)
    context = {
        "service_requests": service_requests,
    }
    return render(request, 'service/list_service_requests.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)
def detail_service_request(request, pk):    
    context = {}
    try:
        get_object_or_404(ScheduledService, pk = pk)
        context['is_scheduled'] = True
    except:
        pass   
    try:
        service_request = get_object_or_404(ServiceRequest, pk = pk)                
        context.update({"service_request": service_request})
    except Http404:
        messages.error(request, "Error. Service request not found.")
        return redirect(list_service_requests   )
    return render(request, 'service/detail_service_request.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)
def schedule_service(request, pk):    
    technicians = Technician.objects.all()
    try:
        get_object_or_404(ScheduledService, pk = pk)
        return redirect(detail_scheduled_service, pk)
    except:
        pass
    try:
        service_request = get_object_or_404(ServiceRequest, pk = pk)
        if request.method == "POST":
            service_date = request.POST.get("service_date")
            technician = request.POST.get("technician")
            try:
                    technician = get_object_or_404(Technician, pk = technician)
            except Http404:
                messages.error(request, "Invalid technician.")
                return redirect(schedule_service, pk)
            starting_time = request.POST.get("starting_time")
            ending_time = request.POST.get("ending_time")

            # check whether there is any ovelapping time intervels, so that we can we avoid that
            if has_overlap(technician, service_date, starting_time, ending_time):                
                scheduled_services = ScheduledService.objects.filter(technician=technician, service_date=service_date)
                scheduled_repairs = ScheduledRepair.objects.filter(technician=technician, repair_date=service_date)
                scheduled_works = list(scheduled_services) + list(scheduled_repairs)
                occuppied_time_slots = [{str(scheduled_work.starting_time.strftime("%I:%M %p")) : str(scheduled_work.ending_time.strftime("%I:%M %p"))} for scheduled_work in scheduled_works]
                messages.error(request, f"For the date {datetime.strptime(service_date, "%Y-%m-%d").strftime("%d-%b-%Y")} the selected technician is busy on the following time slots: {occuppied_time_slots}")
                return redirect(schedule_service, pk)

            try:
                ScheduledService.objects.create(
                    id = service_request.pk,
                    service_request = service_request,
                    service_date = service_date,
                    technician = technician,
                    starting_time = starting_time,
                    ending_time = ending_time
                )
                try:
                    get_object_or_404(ScheduledService, pk = pk)
                    messages.success(request, "Service scheduled successfully!")
                    return redirect(list_service_requests)
                except Http404:
                    messages.error(request, "Error scheduling service.")
                    return redirect(schedule_service, pk)
            except IntegrityError:
                try:
                    get_object_or_404(ScheduledService, service_request = pk)
                    messages.warning(request, "Service is already scheduled for this service request.")
                    return redirect(schedule_service, pk)
                except Exception as e:
                    print(e)
                    return redirect(list_service_requests)
        context = {
            "service_request" : service_request,
            "technicians" : technicians,
            "preffered_date" : str(service_request.prefered_date),
        }
    except Http404:
        messages.error(request, "Error. Service request not found.")
    return render(request, 'service/schedule_service.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)
def update_scheduled_service(request, pk):    
    context = {}
    technicians = Technician.objects.all()
    try:
        scheduled_service = get_object_or_404(ScheduledService, pk=pk)
        context.update({
            "scheduled_service": scheduled_service,
            "technicians": technicians,
            })
        if request.method == "POST":
            service_date = request.POST.get("service_date")
            technician = request.POST.get("technician")
            try:
                technician = get_object_or_404(Technician, pk = technician)
            except Http404:
                messages.error(request, "Invalid technician.")
                return redirect(update_scheduled_service, pk)
            starting_time = request.POST.get("starting_time")
            ending_time = request.POST.get("ending_time")

            # check whether there is any ovelapping time intervels, so that we can avoid that
            if has_overlap(technician, service_date, starting_time, ending_time):                
                scheduled_services = ScheduledService.objects.filter(technician=technician, service_date=service_date)
                scheduled_repairs = ScheduledRepair.objects.filter(technician=technician, repair_date=service_date)                
                scheduled_works = list(scheduled_services) + list(scheduled_repairs)
                occuppied_time_slots = [{str(scheduled_work.starting_time.strftime("%I:%M %p")) : str(scheduled_work.ending_time.strftime("%I:%M %p"))} for scheduled_work in scheduled_works]
                messages.error(request, f"For the date {datetime.strptime(service_date, "%Y-%m-%d").strftime("%d-%b-%Y")} the selected technician is busy on the following time slots: {occuppied_time_slots}")
                return redirect(update_scheduled_service, pk)

            # updating values into the given scheduled service object
            scheduled_service.service_date = service_date
            scheduled_service.technician = technician
            scheduled_service.starting_time = starting_time
            scheduled_service.ending_time = ending_time
            # save the updation
            scheduled_service.save()
            messages.success(request, "Updated scheduled service successfully.")
            return redirect(detail_scheduled_service, pk)

    except Http404:
        messages.error(request, "Invalid scheduled service object.")
        return redirect(list_scheduled_services)
    return render(request, "service/update_scheduled_service.html", context)    

# function to check ovelapping of time intervals for scheduling service
def has_overlap(technician, service_date, starting_time, ending_time):
    overlapping_services = ScheduledService.objects.filter(
        technician = technician,
        service_date = service_date,
        starting_time__lt = ending_time,
        ending_time__gt = starting_time,
    )
    overlapping_repairs = ScheduledRepair.objects.filter(
        technician = technician,
        repair_date = service_date,
        starting_time__lt = ending_time,
        ending_time__gt = starting_time,
    )

    return overlapping_services.exists() or overlapping_repairs.exists()

@user_passes_test(is_superuser, login_url=admin_login)
def delete_scheduled_service(request, pk):    
    try:
        scheduled_service = get_object_or_404(ScheduledService, pk=pk)
        scheduled_service.delete()
        messages.success(request, "Deleted scheduled service successfully.")
        return redirect(list_scheduled_services)
    except Http404:
        messages.error(request, "Invalid scheduled service.")
        return redirect(list_scheduled_services)    

@user_passes_test(is_superuser, login_url=admin_login)
def list_scheduled_services(request):    
    scheduled_services = ScheduledService.objects.all().order_by("service_date")        
    context = {"scheduled_services" : scheduled_services}
    return render(request, 'service/list_scheduled_services.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)
def detail_scheduled_service(request, pk):    
    scheduled_service = get_object_or_404(ScheduledService, pk = pk)
    context = {"scheduled_service" : scheduled_service}
    return render(request, 'service/detail_scheduled_service.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)  
def complete_service(request, pk):    
    try:
        scheduled_service = get_object_or_404(ScheduledService, pk = pk)
        try:
            CompletedService.objects.create(
                id = scheduled_service.id,
                
                # data of service request
                customer_name = scheduled_service.service_request.customer_name,
                email = scheduled_service.service_request.email,
                application_datetime = scheduled_service.service_request.application_datetime,
                alternative_number = scheduled_service.service_request.alternative_number,
                address_site = scheduled_service.service_request.address_site,
                item_name = scheduled_service.service_request.item_name,
                contact_number = scheduled_service.service_request.contact_number,
                prefered_date = scheduled_service.service_request.prefered_date,
                serial_number = scheduled_service.service_request.serial_number,
                bussiness_name = scheduled_service.service_request.bussiness_name,
                service_description = scheduled_service.service_request.service_description,

                # data exclusive to scheduled service object
                service_date = scheduled_service.service_date,
                technician = scheduled_service.technician,
                starting_time = scheduled_service.starting_time,
                ending_time = scheduled_service.ending_time,
            )
            try:
                get_object_or_404(CompletedService, pk = pk)
                service_request = get_object_or_404(ServiceRequest, pk=pk)
                scheduled_service.delete()
                service_request.delete()
                messages.success(request, "Service completed.")
                return redirect(list_scheduled_services)        
            except Http404:
                messages.error(request, "Service completion failed.")
                return redirect(detail_scheduled_service, pk)
            
        except IntegrityError:
            messages.error(request, "This service has already been completed.")
            return redirect(list_completed_services)
    except Http404:
        messages.error(request, "Invalid scheduled service.")    

@user_passes_test(is_superuser, login_url=admin_login)
def list_completed_services(request):    
    completed_services = CompletedService.objects.all().order_by("pk")
    context = {
        "completed_services": completed_services,
    }
    return render(request, 'service/list_completed_services.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)
def detail_completed_service(request, pk):    
    context = {}
    try:
        completed_service = get_object_or_404(CompletedService, pk=pk)
        context.update({
            "completed_service": completed_service
        })
    except Http404:
        messages.error(request, "Invalid. Completed service not found.")
        return redirect(list_completed_services)
    return render(request, 'service/detail_completed_service.html', context)    

# repair
@user_passes_test(is_superuser, login_url=admin_login)
def list_repair_requests(request):             
    repair_requests = RepairRequest.objects.all().order_by("-datetime")
    scheduled_repair_ids = ScheduledRepair.objects.values_list('repair_request_id', flat=True)
    repair_requests = repair_requests.exclude(pk__in=scheduled_repair_ids)
    context = {
        "repair_requests": repair_requests,
    }
    return render(request, 'repair/list_repair_requests.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)
def detail_repair_request(request, pk):    
    context = {}
    try:
        repair_request = get_object_or_404(RepairRequest, pk = pk)
        context.update({"repair_request": repair_request})
        try:
            get_object_or_404(ScheduledRepair, pk = pk)
            context['is_scheduled'] = True
        except Http404:
            pass
    except Http404:
        messages.error(request, "Error. Repair request not found.")        
    return render(request, 'repair/detail_repair_request.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)
def schedule_repair(request, pk):    
    context = {}
    technicians = Technician.objects.all()
    context.update({"technicians": technicians})
    try:
        get_object_or_404(ScheduledRepair, pk = pk)
        messages.error(request, "Repair already scheduled.")
        return redirect(list_scheduled_repairs)
    except:
        pass
    try:
        repair_request = get_object_or_404(RepairRequest, pk = pk)
        context.update({"repair_request": repair_request})
        if request.method == "POST":
            repair_date = request.POST.get("repair_date")
            technician = request.POST.get("technician")
            try:
                technician = get_object_or_404(Technician, pk = technician)
            except Http404:
                messages.error(request, "Invalid technician.")
                return redirect(schedule_repair, pk)
            starting_time = request.POST.get("starting_time")
            ending_time = request.POST.get("ending_time")

            # check whether there is any ovelapping time intervels, so that we can we avoid that
            if has_overlap(technician, repair_date, starting_time, ending_time):                
                scheduled_services = ScheduledService.objects.filter(technician=technician, service_date=repair_date)
                scheduled_repairs = ScheduledRepair .objects.filter(technician=technician, repair_date=repair_date)
                scheduled_works = list(scheduled_services) + list(scheduled_repairs)
                occuppied_time_slots = [{str(scheduled_work.starting_time.strftime("%I:%M %p")) : str(scheduled_work.ending_time.strftime("%I:%M %p"))} for scheduled_work in scheduled_works]                
                messages.error(request, f"For the date {datetime.strptime(repair_date, "%Y-%m-%d").strftime("%d-%b-%Y")} the selected technician is busy on the following time slots: {occuppied_time_slots}")
                return redirect(schedule_repair, pk)
            
            try:
                ScheduledRepair.objects.create(
                    id = repair_request.id,
                    repair_request = repair_request,
                    repair_date = repair_date,
                    technician = technician,
                    starting_time = starting_time,
                    ending_time = ending_time
                )
                messages.success(request, "Repair scheduled successfully!")
                return redirect(list_repair_requests)
            except IntegrityError:                
                messages.warning(request, "Repair is already scheduled for this repair request.")
                return redirect(schedule_repair, pk)                
    except Http404:
        messages.error(request, "Invalid repair request.")
    return render(request, 'repair/schedule_repair.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)
def update_scheduled_repair(request, pk):    
    context = {}
    technicians = Technician.objects.all()
    try:
        scheduled_repair = get_object_or_404(ScheduledRepair, pk=pk)
        context.update({
            "scheduled_repair": scheduled_repair,
            "technicians": technicians,
            })
        if request.method == "POST":
            repair_date = request.POST.get("repair_date")
            technician = request.POST.get("technician")            
            try:
                technician = get_object_or_404(Technician, pk = technician)
            except Http404:
                messages.error(request, "Invalid technician selected.")
                return redirect(update_scheduled_repair, pk)
            starting_time = request.POST.get("starting_time")
            ending_time = request.POST.get("ending_time")

            # check whether there is any ovelapping time intervels, so that we can avoid that
            if has_overlap(technician, repair_date, starting_time, ending_time):                
                scheduled_services = ScheduledService.objects.filter(technician=technician, service_date=repair_date)
                scheduled_repairs = ScheduledRepair.objects.filter(technician=technician, repair_date=repair_date)
                scheduled_works = list(scheduled_services) + list(scheduled_repairs)
                occuppied_time_slots = [{str(scheduled_work.starting_time.strftime("%I:%M %p")) : str(scheduled_work.ending_time.strftime("%I:%M %p"))} for scheduled_work in scheduled_works]
                messages.error(request, f"For the date {datetime.strptime(repair_date, "%Y-%m-%d").strftime("%d-%b-%Y")} the selected technician is busy on the following time slots: {occuppied_time_slots}")
                return redirect(update_scheduled_repair, pk)

            # updating values into the given scheduled repair object
            scheduled_repair.repair_date = repair_date
            scheduled_repair.technician = technician
            scheduled_repair.starting_time = starting_time
            scheduled_repair.ending_time = ending_time
            # save the updation
            scheduled_repair.save()
            messages.success(request, "Updated scheduled repair successfully.")
            return redirect(detail_scheduled_repair, pk)

    except Http404:
        messages.error(request, "Invalid scheduled repair object.")
        return redirect(list_scheduled_repairs)
    return render(request, "repair/update_scheduled_repair.html", context)    

# function to check ovelapping of time intervals for scheduling repair
def has_overlap(technician, repair_date, starting_time, ending_time):
    overlapping_services = ScheduledService.objects.filter(
        technician = technician,
        service_date = repair_date,
        starting_time__lt = ending_time,
        ending_time__gt = starting_time,
    )
    overlapping_repairs = ScheduledRepair.objects.filter(
        technician = technician,
        repair_date = repair_date,
        starting_time__lt = ending_time,
        ending_time__gt = starting_time,
    )

    return overlapping_services.exists() or overlapping_repairs.exists()

@user_passes_test(is_superuser, login_url=admin_login)
def delete_scheduled_repair(request, pk):    
    try:
        scheduled_repair = get_object_or_404(ScheduledRepair, pk=pk)
        scheduled_repair.delete()
        messages.success(request, "Deleted scheduled repair successfully.")
        return redirect(list_scheduled_repairs)
    except Http404:
        messages.error(request, "Invalid scheduled repair.")
        return redirect(list_scheduled_repairs)    

@user_passes_test(is_superuser, login_url=admin_login)
def list_scheduled_repairs(request):    
    scheduled_repairs = ScheduledRepair.objects.all().order_by("repair_date")
    context = {
        "scheduled_repairs": scheduled_repairs
    }
    return render(request, 'repair/list_scheduled_repairs.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)
def detail_scheduled_repair(request, pk):    
    try:
        scheduled_repair = get_object_or_404(ScheduledRepair, pk = pk)
        context = {"scheduled_repair" : scheduled_repair}
    except Http404:
        messages.error(request, "Invalid scheduled repair.")
        return redirect(list_scheduled_repairs)
    return render(request, 'repair/detail_scheduled_repair.html', context)    

@user_passes_test(is_superuser, login_url=admin_login)
def complete_repair(request, pk):    
    try:
        scheduled_repair = get_object_or_404(ScheduledRepair, pk = pk)
        try:
            CompletedRepair.objects.create(
                id = scheduled_repair.id,
                
                # data of repair request
                customer_name = scheduled_repair.repair_request.customer_name,
                email_id = scheduled_repair.repair_request.email_id,
                datetime = scheduled_repair.repair_request.datetime,
                alternative_number = scheduled_repair.repair_request.alternative_number,
                address_customer = scheduled_repair.repair_request.address_customer,
                item_name = scheduled_repair.repair_request.item_name,
                contact_number = scheduled_repair.repair_request.contact_number,
                serial_number = scheduled_repair.repair_request.serial_number,
                item_description = scheduled_repair.repair_request.serial_number,

                # data exclusive to scheduled repair object
                repair_date = scheduled_repair.repair_date,
                technician = scheduled_repair.technician,
                starting_time = scheduled_repair.starting_time,
                ending_time = scheduled_repair.ending_time,
            )
            try:
                get_object_or_404(CompletedRepair, pk = pk)
                repair_request = get_object_or_404(RepairRequest, pk=pk)
                scheduled_repair.delete()
                repair_request.delete()
                messages.success(request, "Repair completed.")
                return redirect(list_scheduled_repairs)        
            except Http404:
                messages.error(request, "Repair completion failed.")
                return redirect(detail_scheduled_repair, pk)
            
        except IntegrityError:
            messages.error(request, "This repair has already been completed.")
            return redirect(list_completed_repairs)
    except Http404:
        messages.error(request, "Invalid scheduled repair.")
        return redirect(list_scheduled_repairs)    

@user_passes_test(is_superuser, login_url=admin_login)
def list_completed_repairs(request):    
    completed_repairs = CompletedRepair.objects.all().order_by("pk")
    context = {
        "completed_repairs": completed_repairs,
    }
    return render(request, 'repair/list_completed_repairs.html', context)

@user_passes_test(is_superuser, login_url=admin_login)
def detail_completed_repair(request, pk):    
    context = {}
    try:
        completed_repair = get_object_or_404(CompletedRepair, pk=pk)
        context.update({
            "completed_repair": completed_repair
        })
    except Http404:
        messages.error(request, "Invalid. Completed repair not found.")
        return redirect(list_completed_repairs)
    return render(request, 'repair/detail_completed_repair.html', context)    