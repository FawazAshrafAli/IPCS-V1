from django.contrib import admin
from .models import *

class TechnicianAdmin(admin.ModelAdmin):
    list_display = [
        "name", "email", "mobile", "department",
        "residential_location"
        ]
admin.site.register(Technician, TechnicianAdmin)

# admin.site.register(Product)

class WarrantyAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "customer_name", "date",
        "contact_number", "email_id",
        "alternative_number", "billing_name",
        "invoice_number", "serial_number",
        "model_number"
        ]
admin.site.register(Warranty, WarrantyAdmin)

class WarrantyApplicationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "application_date",
        "customer_name",
        "purchase_date",
        "duration",
        "contact_number",
        "email_id",
        "alternative_number",
        "billing_name",
        "invoice_number",
        "serial_number",
        "model_number",
        "expiry_date",
    ]
admin.site.register(WarrantyApplication, WarrantyApplicationAdmin)

class ApprovedWarrantyApplicationAdmin(admin.ModelAdmin):
    list_display = [
        "approved_datetime",    
        "application_date",
        "customer_name",
        "purchase_date",
        "duration",
        "contact_number",
        "email_id",
        "alternative_number",
        "billing_name",
        "invoice_number",
        "serial_number",
        "model_number",        
        "expiry_date",
    ]
admin.site.register(ApprovedWarrantyApplication, ApprovedWarrantyApplicationAdmin)

admin.site.register(ClaimedWarranty)

class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "customer_name", "email",
        "application_datetime", "alternative_number",
        "address_site", "item_name",
        "contact_number", "prefered_date",
        "serial_number", "service_description"
    ]
admin.site.register(ServiceRequest, ServiceRequestAdmin)

class ScheduledServiceAdmin(admin.ModelAdmin):
    list_display = [
        "service_request",
        "service_date",
        "technician",
        "starting_time",
        "ending_time",        
    ]

admin.site.register(ScheduledService, ScheduledServiceAdmin)

admin.site.register(CompletedService)

admin.site.register(RepairRequest)

admin.site.register(ScheduledRepair)