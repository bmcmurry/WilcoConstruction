from django.contrib import admin
from .models import *


admin.site.register(Tenant)
admin.site.register(RentalProperty)
admin.site.register(PropertyPhoto)
admin.site.register(Lease)
admin.site.register(TenantPayment)
admin.site.register(ConstructionJob)
admin.site.register(ConstructionJobPhoto)
