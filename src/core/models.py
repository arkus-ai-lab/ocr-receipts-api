from django.db import models

class Receipt_eTransaction(models.Model):
    etrasaction_id = models.CharField(max_length=100, primary_key=True) 
    amount = models.BigIntegerField()
    rfc = models.CharField(max_length=100)
    account = models.CharField(max_length=100)

    def __str__(self):
        return self.etrasaction_id
    
class Receipt(models.Model):
    file = models.FileField(upload_to='')
    uploaded_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name