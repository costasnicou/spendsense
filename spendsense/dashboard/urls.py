from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
   
  
    # path('delete-wallet/<int:wallet_id>/', views.delete_wallet, name='delete_wallet'),
]
