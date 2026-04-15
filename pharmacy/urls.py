# pharmacy/urls.py  — COMPLETE FILE with eSewa routes

from django.urls import path
from . import views

urlpatterns = [

    
    path('login/',                  views.login_view,            name='login'),
    path('admin-login/',      views.admin_login_view,      name='admin_login'),
    path('pharmacist-login/', views.pharmacist_login_view, name='pharmacist_login'),
    path('logout/',           views.logout_view,           name='logout'),

    
    path('dashboard/',        views.dashboard,             name='dashboard'),

    
    path('medicines/',                  views.medicine_list,   name='medicine_list'),
    path('medicines/<int:pk>/',         views.medicine_detail, name='medicine_detail'),
    path('medicines/add/',              views.medicine_add,    name='medicine_add'),
    path('medicines/<int:pk>/edit/',    views.medicine_edit,   name='medicine_edit'),
    path('medicines/<int:pk>/delete/',  views.medicine_delete, name='medicine_delete'),

    
    path('cart/',                       views.cart_view,        name='cart'),
    path('cart/add/<int:pk>/',          views.add_to_cart,      name='add_to_cart'),
    path('cart/update/<int:pk>/',       views.update_cart,      name='update_cart'),
    path('cart/remove/<int:pk>/',       views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/',                 views.clear_cart,       name='clear_cart'),

    
    path('cart/order/<int:pk>/',        views.order_now,        name='order_now'),
    # My orders list
    path('my-orders/',                  views.my_orders,        name='my_orders'),
    
   

    
    path('esewa/form/',                 views.EsewaFormView.as_view(), name='esewa_form'),
    
    path('esewa/success/',              views.esewa_success,    name='esewa_success'),
    
    path('esewa/failure/',              views.esewa_failure,    name='esewa_failure'),

    
    path('billing/',                    views.create_bill,      name='create_bill'),
    path('bills/',                      views.bill_list,        name='bill_list'),
    path('bills/<int:pk>/',             views.bill_invoice,     name='bill_invoice'),

    
    path('reports/',                    views.reports,          name='reports'),

    
    path('users/',                      views.user_list,        name='user_list'),
    path('users/create/',               views.user_create,      name='user_create'),

    
    path('api/medicine/<int:pk>/price/', views.get_medicine_price, name='medicine_price'),
]