from django.db import models
from django.contrib.auth.models import User



# Create your models here.
# <--------------- WILLS ----------------->
# <--------------- WILLS ----------------->
# <--------------- WILLS ----------------->

class BlockchainWill(models.Model):
    id_w = models.AutoField(primary_key=True)
    transaction_id = models.CharField(max_length=255, unique=True, null=True)
    email = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=15)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    full_legal_name = models.CharField(max_length=255, null=True)
    birthdate = models.DateField(null=True)
    birth_country = models.CharField(max_length=57, null=True)
    associated_email1 = models.CharField(max_length=40, null=True)
    associated_email2 = models.CharField(max_length=40, null=True)
    associated_email3 = models.CharField(max_length=40, null=True)
    selfie_photo_url = models.CharField(max_length=255, null=True)      
    document_id_url = models.CharField(max_length=255, null=True)      
    video_url = models.CharField(max_length=255, null=True)      

class Beneficiary(models.Model):
    blockchain_wills = models.ManyToManyField(BlockchainWill)
    full_legal_name = models.CharField(max_length=255, null=True)
    birthdate = models.DateField(null=True)
    birth_country = models.CharField(max_length=57, null=True)
    relationship = models.CharField(max_length=50, null=True)
    associated_email1 = models.CharField(max_length=40, null=True)
    associated_email2 = models.CharField(max_length=40, null=True)
    will_percentage = models.IntegerField(null=True)
    selfie_photo_url = models.CharField(max_length=255, null=True)

# <--------------- WILLS ----------------->
# <--------------- WILLS ----------------->
# <--------------- WILLS -----------------> 