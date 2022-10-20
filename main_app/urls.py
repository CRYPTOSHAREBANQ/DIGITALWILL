from django.urls import path
from . import views

app_name = "digitalwill"
urlpatterns = [

    path("BlockchainWills/", views.blockchain_wills, name="BlockchainWills"),
    path("RegisterBlockchainWill/", views.register_blockchain_will, name="RegisterBlockchainWill"),
    path("CertificateBlockchainWill/", views.certificate_blockchain_will, name="CertificateBlockchainWill"),     
    path("CertificateBlockchainWill/<int:id>/", views.certificate_blockchain_will, name="CertificateBlockchainWill"), 
    
]