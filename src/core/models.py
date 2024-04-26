from django.db import models

class Receipt(models.Model):
    file = models.FileField(upload_to='')
    uploaded_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name