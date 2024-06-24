from django.db import models
from datetime import timedelta
import uuid
from django.templatetags.static import static

class Client(models.Model):
    name = models.CharField(blank=False, null=False, max_length=150, unique = True)
    image = models.ImageField(upload_to='client_images/')


class Product(models.Model):
    name = models.CharField(blank=False, null=False, max_length=150, unique=True)
    image = models.ImageField(upload_to='product_images/', default='images/default_images/no_image.jpeg')
    link = models.URLField(max_length=250)

    def __str__(self):
        return self.name

class Technician(models.Model):
    name = models.CharField(blank=False, null=False, max_length=150)
    email = models.EmailField(blank=False, null=False, max_length=254, unique=True)
    mobile = models.CharField(blank=False, null=False, max_length=20, unique=True)
    department = models.CharField(blank=False, null=False, max_length=200)
    residential_location = models.TextField()
    photo = models.ImageField(upload_to='uploads/')

    def __str__(self):
        return self.name
    
def warranty_unique_id(): # for creating an unique id for warranty
    return "WTY" + (str(uuid.uuid4().hex)[:9]).upper()

class Warranty(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=warranty_unique_id, editable=False)
    customer_name = models.CharField(blank=False, null=False, max_length=150)
    date = models.DateField() # purchase date of the product
    duration = models.IntegerField(blank=True, null=True, default=0) # warranty period duration in years
    email_id = models.EmailField(blank=False, null=False, max_length=254)
    contact_number = models.CharField(blank=False, null=False, max_length=20)
    alternative_number = models.CharField(blank=True, null=True, max_length=20)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    billing_name = models.CharField(blank=False, null=False, max_length=150)
    invoice_number = models.CharField(blank=False, null=False, max_length=50)
    serial_number = models.CharField(blank=False, null=False, max_length=50, unique=True)
    model_number = models.CharField(blank=False, null=False, max_length=50)

    @property
    def expiry_date(self):
        if self.duration:
            date = self.date + timedelta(days = 365 * self.duration)
        else:
            date= None
        return date
        
    def __str__(self):
        return self.id

class WarrantyApplication(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    application_date = models.DateTimeField(auto_now_add=True)
    customer_name = models.CharField(blank=False, null=False, max_length=150)
    purchase_date = models.DateField() # purchase date of the product
    duration = models.IntegerField(blank=False, null=False) # warranty period duration in years
    contact_number = models.CharField(blank=False, null=False, max_length=20)
    email_id = models.EmailField(blank=False, null=False, max_length=254)
    alternative_number = models.CharField(blank=True, null=True, max_length=20)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    billing_name = models.CharField(blank=False, null=False, max_length=150)
    invoice_number = models.CharField(blank=False, null=False, max_length=50)
    serial_number = models.CharField(blank=False, null=False, max_length=50, unique=True)
    model_number = models.CharField(blank=False, null=False, max_length=50)
    expiry_date = models.DateField()
    product_complain = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.id
    
class ApprovedWarrantyApplication(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    approved_datetime = models.DateTimeField(auto_now_add=True)
    application_date = models.DateTimeField()
    customer_name = models.CharField(blank=False, null=False, max_length=150)
    purchase_date = models.DateField() # purchase date of the product
    duration = models.IntegerField(blank=False, null=False) # warranty period duration in years
    contact_number = models.CharField(blank=False, null=False, max_length=20)
    email_id = models.EmailField(blank=False, null=False, max_length=254)
    alternative_number = models.CharField(blank=True, null=True, max_length=20)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    billing_name = models.CharField(blank=False, null=False, max_length=150)
    invoice_number = models.CharField(blank=False, null=False, max_length=50)
    serial_number = models.CharField(blank=False, null=False, max_length=50, unique=True)
    model_number = models.CharField(blank=False, null=False, max_length=50)
    product_complain = models.TextField(blank=False, null=False)
    expiry_date = models.DateField()
    feedback = models.TextField(blank=True, null=True, default="On progress !")

    def __str__(self):
        return self.id

class ClaimedWarranty(models.Model):
    warranty_id = models.CharField(max_length=50)
    approved_datetime = models.DateTimeField(auto_now_add=True)
    application_date = models.DateTimeField()
    customer_name = models.CharField(blank=False, null=False, max_length=150)
    purchase_date = models.DateField() # purchase date of the product
    duration = models.IntegerField(blank=False, null=False) # warranty period duration in years
    contact_number = models.CharField(blank=False, null=False, max_length=20)
    email_id = models.EmailField(blank=False, null=False,   max_length=254)
    alternative_number = models.CharField(blank=True, null=True, max_length=20)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    billing_name = models.CharField(blank=False, null=False, max_length=150)
    invoice_number = models.CharField(blank=False, null=False, max_length=50)
    serial_number = models.CharField(blank=False, null=False, max_length=50)
    model_number = models.CharField(blank=False, null=False, max_length=50)
    product_complain = models.TextField(blank=False, null=False)
    expiry_date = models.DateField()

    def __str__(self):
        return self.id
    
def service_unique_id():    # to create an unique id for Service Request
    return "SVS" + (str(uuid.uuid4().hex)[:9]).upper()

class ServiceRequest(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=service_unique_id, editable=False)
    customer_name = models.CharField(blank=False, null=False, max_length=150)
    email = models.EmailField(blank=False, null=False, max_length=254)
    application_datetime = models.DateTimeField(auto_now_add=True)    
    alternative_number = models.CharField(blank=True, null=True, max_length=20)
    address_site = models.TextField(blank=False, null=False)
    item_name = models.CharField(blank=False, null=False, max_length=150)
    contact_number = models.CharField(blank=False, null=False, max_length=20)
    prefered_date = models.DateField()
    serial_number = models.CharField(blank=False, null=False, max_length=50, unique=True)
    bussiness_name = models.CharField(blank=False, null=False, max_length=150)
    service_description = models.CharField(max_length=250)

    def __str__(self):
        return self.id

class ScheduledService(models.Model):
    id = models.CharField(max_length=50, primary_key=True, editable=False)    
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE)
    service_date = models.DateField()
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE, blank=True, null=True)
    starting_time = models.TimeField()
    ending_time = models.TimeField()
    
    def __str__(self):
        return self.id

class CompletedService(models.Model):
    id = models.CharField(max_length=50, primary_key=True, editable=False) 

    customer_name = models.CharField(blank=False, null=False, max_length=150)
    email = models.EmailField(blank=False, null=False, max_length=254)
    application_datetime = models.DateTimeField(auto_now_add=True)    
    alternative_number = models.CharField(blank=True, null=True, max_length=20)
    address_site = models.TextField(blank=False, null=False)
    item_name = models.CharField(blank=False, null=False, max_length=150)
    contact_number = models.CharField(blank=False, null=False, max_length=20)
    prefered_date = models.DateField()
    serial_number = models.CharField(blank=False, null=False, max_length=50)
    bussiness_name = models.CharField(blank=False, null=False, max_length=150)
    service_description = models.CharField(max_length=250)

    service_date = models.DateField()
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE, blank=True, null=True)
    starting_time = models.TimeField()
    ending_time = models.TimeField()

    def __str__(self):
        return self.id
    

def repair_unique_id():
    return "REP" + (str(uuid.uuid4().hex)[:9]).upper()

class RepairRequest(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=repair_unique_id, editable=False)
    customer_name = models.CharField(blank=False, null=False, max_length=150)
    address_customer = models.TextField(blank=False, null=False)
    email_id = models.EmailField(blank=False, null=False, max_length=254)
    datetime = models.DateTimeField(auto_now_add=True)
    item_name = models.CharField(blank=False, null=False, max_length=150)
    contact_number = models.CharField(blank=False, null=False, max_length=20)
    alternative_number = models.CharField(blank=True, null=True, max_length=20)
    serial_number = models.CharField(blank=False, null=False, max_length=50, unique=True)
    item_description = models.CharField(blank=False, null=False, max_length=200)    

    def __str__(self):
        return self.id
    
class ScheduledRepair(models.Model):
    id = models.CharField(max_length=50, primary_key=True, editable=False)    
    repair_request = models.OneToOneField(RepairRequest, on_delete=models.CASCADE)
    repair_date = models.DateField()
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE, blank=True, null=True)
    starting_time = models.TimeField()
    ending_time = models.TimeField()

    def __str__(self):
        return self.id
    
class CompletedRepair(models.Model):
    id = models.CharField(max_length=50, primary_key=True, editable=False) 

    customer_name = models.CharField(blank=False, null=False, max_length=150)
    address_customer = models.TextField(blank=False, null=False)
    email_id = models.EmailField(blank=False, null=False, max_length=254)
    datetime = models.DateTimeField(auto_now_add=True)
    item_name = models.CharField(blank=False, null=False, max_length=150)
    contact_number = models.CharField(blank=False, null=False, max_length=20)
    alternative_number = models.CharField(blank=True, null=True, max_length=20)
    serial_number = models.CharField(blank=False, null=False, max_length=50)
    item_description = models.CharField(blank=False, null=False, max_length=200)    

    repair_date = models.DateField()
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE, blank=True, null=True)
    starting_time = models.TimeField()
    ending_time = models.TimeField()

    def __str__(self):
        return self.id

    