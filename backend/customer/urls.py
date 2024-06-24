from django.urls import path
from . import views

urlpatterns = [
    path('', views.home , name="home"),
    path('customer_login/', views.customer_login, name="customer_login"),
    path('customer_signup/', views.customer_signup , name="customer_signup"),
    path('customer_logout/', views.customer_logout, name="customer_logout"),
    path('home/', views.customer_home, name="customer_home"),
    
    path('service_tracking/', views.service_tracking , name="service_tracking"),
    path('warranty_tracking/', views.warranty_tracking , name="warranty_tracking"),
    path('repair_tracking/', views.repair_tracking , name="repair_tracking"),
    
    path('reset_customer_password/', views.reset_customer_password, name="reset_customer_password"),
    path('customer_account/', views.customer_account, name="customer_account"),
    path('update_customer_info/', views.update_customer_info, name="update_customer_info"),
    path('forgot_id/', views.forgot_id , name="forgot_id"),

    path('warranty_request/<pk>', views.apply_warranty, name="warranty_request"),
    path('request_service/<pk>', views.service_request , name="request_service"),
    path('request_repaira/', views.request_repair , name="request_repair"),    

    path('warranty_history/', views.warranty_history , name="warranty_history"),
    path('service_history/', views.service_history , name="service_history"),
    path('repair_history/', views.repair_history , name="repair_history"),
]
