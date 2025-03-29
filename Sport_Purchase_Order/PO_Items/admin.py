from django.contrib import admin

# Register your models here.
from .models import Role, User, Supplier, SportsItem, PurchaseOrder, POItem
from django.contrib.auth.admin import UserAdmin

admin.site.register(Role)
admin.site.register(Supplier)
admin.site.register(SportsItem)
admin.site.register(PurchaseOrder)
admin.site.register(POItem)

# If you want to customize the User admin:
admin.site.register(User, UserAdmin)
