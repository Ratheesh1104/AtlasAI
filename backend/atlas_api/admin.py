from django.contrib import admin

from . import models

admin.site.register(models.Company)
admin.site.register(models.Contact)
admin.site.register(models.EmailMessage)
admin.site.register(models.Ticket)
admin.site.register(models.Note)
admin.site.register(models.Meeting)
admin.site.register(models.Invoice)
admin.site.register(models.Policy)
admin.site.register(models.Product)
admin.site.register(models.Quote)
admin.site.register(models.Brief)
admin.site.register(models.Followup)
admin.site.register(models.WorkbenchCard)
admin.site.register(models.Task)
