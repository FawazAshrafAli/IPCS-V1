from django.urls import path
from . import views

urlpatterns = [    
    path('', views.admin_login, name="login"),
    path('admin_home/', views.home, name="admin_home"),
    path('logout/', views.admin_logout, name="logout"),
    path('reset_password/', views.reset_password, name="reset_password"),

    # clients
    path('clients/', views.list_clients, name="clients"),
    path('add_client/', views.add_client, name="add_client"),
    path('client/<pk>', views.detail_client, name="client"),
    path('update_client/<pk>', views.update_client, name="update_client"),    
    path('delete_client/<pk>', views.delete_client, name="delete_client"),

    # product
    path('products/', views.list_products, name="products"),
    path('add_product/', views.add_product, name="add_product"),
    path('product/<pk>', views.detail_product, name="product"),
    path('update_product/<pk>', views.update_product, name="update_product"),    
    path('delete_product/<pk>', views.delete_product, name="delete_product"),

    # admin warrantied products
    path('add_warranty/', views.add_warranty, name="add_warranty"),
    path('update_warranty/<pk>', views.update_warranty, name="update_warranty"),
    path('warrantied_products/', views.list_warrantied_products, name="warrantied_products"),
    path('warrantied_product/<pk>', views.detail_warrantied_product, name="warrantied_product"),
    path('delete_warranty/<pk>', views.delete_warranty, name="delete_warranty"),

    # admin warranty
    path('warranty_applications/', views.list_warranty_applications, name="warranty_applications"),
    path('warranty_application/<pk>', views.detail_warranty_application, name="warranty_application"),
    path("approved_warranties/", views.list_approved_warranty_applications, name="approved_warranties"),
    path('approve_warranty/<pk>', views.approve_warranty, name="approve_warranty"),
    path('approved_warranty_detail/<pk>', views.detail_approved_warranty_application, name="approved_warranty_detail"),
    path('delete_approved_warranty_application/<pk>', views.delete_approved_warranty_application, name="delete_approved_warranty_application"),
    path('complete_warranty/<pk>', views.complete_warranty, name="complete_warranty"),
    
    path('completed_warranties/', views.list_completed_warranties, name="completed_warranties"),
    path('completed_warranty/<pk>', views.detail_completed_warranty, name="completed_warranty"),

    # admin technician
    path('add_technician/', views.add_technician, name="add_technician"),
    path('technicians/', views.list_technicians, name="technicians"),
    path('technician/<pk>', views.detail_technician, name="technician"),
    path('update_technician/<pk>', views.update_technician, name="update_technician"),
    path('delete_technician/<pk>', views.delete_technician, name="delete_technician"),

    # admin service
    path('service_requests/', views.list_service_requests , name="service_requests"),
    path('service_request/<pk>', views.detail_service_request , name="service_request"),
    path('schedule_service/<pk>', views.schedule_service , name="schedule_service"),
    path('scheduled_services/', views.list_scheduled_services , name="scheduled_services"),
    path('scheduled_service/<pk>', views.detail_scheduled_service , name="scheduled_service"),
    path('update_scheduled_service/<pk>', views.update_scheduled_service , name="update_scheduled_service"),
    path('delete_scheduled_service/<pk>', views.delete_scheduled_service , name="delete_scheduled_service"),
    path('complete_service/<pk>', views.complete_service, name="complete_service"),
    path('completed_services/', views.list_completed_services, name="completed_services"),
    path('completed_service/<pk>', views.detail_completed_service, name="completed_service"),
    
    # admin repair
    path('repair_requests/', views.list_repair_requests , name="repair_requests"),
    path('repair_request/<pk>', views.detail_repair_request , name="repair_request"),
    path('schedule_repair/<pk>', views.schedule_repair , name="schedule_repair"),
    path('update_scheduled_repair/<pk>', views.update_scheduled_repair , name="update_scheduled_repair"),
    path('delete_scheduled_repair/<pk>', views.delete_scheduled_repair , name="delete_scheduled_repair"),
    path('scheduled_repairs/', views.list_scheduled_repairs , name="scheduled_repairs"),
    path('scheduled_repair/<pk>', views.detail_scheduled_repair , name="scheduled_repair"),
    path('complete_repair/<pk>', views.complete_repair , name="complete_repair"),
    path('completed_repairs/', views.list_completed_repairs , name="completed_repairs"),
    path('completed_repair/<pk>', views.detail_completed_repair , name="completed_repair"),
]

