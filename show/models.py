from django.db import models

# Create your models here.
from django.db import models

class Search(models.Model):
    search_text = models.CharField(max_length=500)
    search_time = models.DateTimeField('search push time')

    def __str__(self):
        return self.search_text