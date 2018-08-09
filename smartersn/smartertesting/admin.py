from django.contrib import admin

# Register your models here.
from .models import UpdateSet, SNObjectType, SNObject, SNTest

admin.site.register(UpdateSet)
admin.site.register(SNObjectType)
admin.site.register(SNObject)
admin.site.register(SNTest)
