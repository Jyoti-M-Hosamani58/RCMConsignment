"""
URL configuration for consign project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from consign_app import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),




    path('index_menu', views.index_menu, name='index_menu'),



    path('', views.userlogin, name='userlogin'),
    path('admin_home', views.admin_home, name='admin_home'),
    path('branch_home',views.branch_home,name='branch_home'),

    path('addConsignment/', views.addConsignment, name='addConsignment'),
    path('printConsignment/<int:track_id>/', views.printConsignment, name='printConsignment'),
    path('branchprintConsignment/<int:track_id>/',views.branchprintConsignment,name='branchprintConsignment'),
    path('view_consignment', views.view_consignment, name='view_consignment'),

    path('invoiceConsignment/<int:pk>', views.invoiceConsignment, name='invoiceConsignment'),


    path('branch', views.branch, name='branch'),
    path('view_branch', views.view_branch, name='view_branch'),

    path('edit_branch/<int:pk>', views.edit_branch, name='edit_branch'),
    path('branch_delete/<int:pk>', views.branch_delete, name='branch_delete'),

    path('driver', views.driver, name='driver'),
    path('view_driver', views.view_driver, name='view_driver'),

    path('driver_edit/<int:pk>', views.driver_edit, name='driver_edit'),
    path('driver_delete/<int:pk>', views.driver_delete, name='driver_delete'),

    path('vehicle', views.vehicle, name='vehicle'),
    path('view_vehicle', views.view_vehicle, name='view_vehicle'),

    path('vehicle_edit/<int:pk>', views.vehicle_edit, name='vehicle_edit'),
    path('vehicle_delete/<int:pk>', views.vehicle_delete, name='vehicle_delete'),

    path('branchConsignment',views.branchConsignment,name='branchConsignment'),
    path('branchprintConsignment/<int:track_id>/', views.branchprintConsignment, name='branchprintConsignment'),
    path('branchviewconsignment',views.branchviewconsignment,name='branchviewconsignment'),


    path('branchconsignment_edit/<int:pk>', views.branchconsignment_edit, name='branchconsignment_edit'),
    path('branchconsignment_delete/<int:pk>', views.branchconsignment_delete, name='branchconsignment_delete'),
    path('branchinvoiceConsignment/<int:track_id>/', views.branchinvoiceConsignment, name='branchinvoiceConsignment'),



    path('branchMaster', views.branchMaster, name='branchMaster'),


    path('get_vehicle_numbers/', views.get_vehicle_numbers, name='get_vehicle_numbers'),
    path('get_driver_name/', views.get_driver_name, name='get_driver_name'),
    path('get_branch/', views.get_branch, name='get_branch'),
    path('get_destination/', views.get_destination, name='get_destination'),



    path('staff', views.staff, name='staff'),
    path('view_staff', views.view_staff, name='view_staff'),
    path('edit_staff/<int:pk>', views.edit_staff, name='edit_staff'),
    path('delete_staff/<int:pk>', views.delete_staff, name='delete_staff'),

    path('get_consignor_name/', views.get_consignor_name, name='get_consignor_name'),
    path('get_consignee_name/', views.get_consignee_name, name='get_consignee_name'),

    path('get_sender_details/', views.get_sender_details, name='get_sender_details'),
    path('get_rec_details/', views.get_rec_details, name='get_rec_details'),

    path('get_account_name/',views.get_account_name,name='get_account_name'),

    path('get_staff',views.get_staff,name='get_staff'),


    path('adminExpenses',views.adminExpenses,name='adminExpenses'),
    path('save-admin-expenses/', views.saveadminExpenses, name='saveadminExpenses'),
    path('adminViewExpenses',views.adminViewExpenses,name='adminViewExpenses'),

    path('payment_history/', views.payment_history, name='payment_history'),
    path('fetch-details/', views.fetch_details, name='fetch_details'),
    path('fetch-consignments/', views.fetch_consignments, name='fetch_consignments'),

    path('credit/', views.credit, name='credit'),

    path('fetch_balance/', views.fetch_balance, name='fetch_balance'),
    path('submit_credit/', views.submit_credit, name='submit_credit'),

    path('credit_print/', views.credit_print, name='credit_print'),
    path('fetch_account_details/', views.fetch_account_details, name='fetch_account_details'),

    path('branchPaymenyHistory',views.branchPaymenyHistory,name='branchPaymenyHistory'),
    path('branchfetch_details',views.branchfetch_details,name='branchfetch_details'),
    path('branchcredit/', views.branchcredit, name='branchcredit'),
    path('branchsubmit_credit',views.branchsubmit_credit,name='branchsubmit_credit'),
    path('branchfetch_balance',views.branchfetch_balance,name='branchfetch_balance'),
    path('branchcredit_print',views.branchcredit_print,name='branchcredit_print'),
    path('branchfetch_account_details',views.branchfetch_account_details,name='branchfetch_account_details'),


    path('branchConsignorView',views.branchConsignorView,name='branchConsignorView'),
    path('branchConsigneeView',views.branchConsigneeView,name='branchConsigneeView'),

    path('adminConsignorView',views.adminConsignorView,name='adminConsignorView'),
    path('adminConsigneeView',views.adminConsigneeView,name='adminConsigneeView'),

    path('adminstaff_view',views.adminstaff_view,name='adminstaff_view'),
    path('adminView_Consignment',views.adminView_Consignment,name='adminView_Consignment'),
    path('admininvoiceConsignment/<int:track_id>/',views.admininvoiceConsignment,name='admininvoiceConsignment'),


    path('adminfetch_account_details',views.adminfetch_account_details,name='adminfetch_account_details'),


    path('adminPaymentHistory',views.adminPaymentHistory,name='adminPaymentHistory'),
    path('adminfetch_details',views.adminfetch_details,name='adminfetch_details'),

    path('consignorMaster',views.consignorMaster,name='consignorMaster'),
    path('consigneeMaster',views.consigneeMaster,name='consigneeMaster'),

    path('addLHS',views.addLHS,name='addLHS'),
    path('saveLHSList',views.saveLHSList,name='saveLHSList'),
    path('addLHSList',views.addLHSList,name='addLHSList'),
    path('saveLHS',views.saveLHS,name='saveLHS'),

    path('LHS', views.LHS, name='LHS'),
    path('viewLHSList', views.viewLHSList, name='viewLHSList'),
    path('editLHSList', views.editLHSList, name='editLHSList'),
    path('update/', views.update_view, name='update_view'),
    path('printLHSList',views.printLHSList,name='printLHSList'),
    path('cancel_trip/<int:trip_id>/', views.cancel_trip, name='cancel_trip'),
    path('delete-trip-sheet-data/', views.delete_trip_sheet_data, name='delete_trip_sheet_data'),

    path('addGDMList', views.addGDMList, name='addGDMList'),
    path('saveGDM', views.saveGDM, name='saveGDM'),
    path('viewGDMList', views.viewGDMList, name='viewGDMList'),
    path('printGDMList', views.printGDMList, name='printGDMList'),

    path('viewLCMList', views.viewLCMList, name='viewLCMList'),
    path('printLCMList', views.printLCMList, name='printLCMList'),

    path('addTURList', views.addTURList, name='addTURList'),
    path('saveTUR', views.saveTUR, name='saveTUR'),
    path('viewTURList', views.viewTURList, name='viewTURList'),
    path('printTURList', views.printTURList, name='printTURList'),

    path('frieghtBillList', views.frieghtBillList, name='frieghtBillList'),
    path('FreightBill/<str:sender_name>/', views.frieghtBillReport, name='frieghtBillReport'),

]
if settings.DEBUG:
     urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

