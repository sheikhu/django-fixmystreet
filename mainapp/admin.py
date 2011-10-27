from mainapp.models import EmailRule, Ward, ReportCategory, Report, City, ReportCategoryClass, FaqEntry, Councillor
from django.contrib import admin
from transmeta import canonical_fieldname
from django import forms


class ReportCategoryClassAdmin(admin.ModelAdmin):
    list_display = ('name',)
    
admin.site.register(ReportCategoryClass,ReportCategoryClassAdmin)


class ReportCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'hint',)

admin.site.register(ReportCategory, ReportCategoryAdmin)


class FaqEntryAdmin(admin.ModelAdmin):
    list_display = ('q', 'order')

admin.site.register(FaqEntry, FaqEntryAdmin)


class CouncillorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')
    fields = ('first_name', 'last_name', 'email')

admin.site.register(Councillor,CouncillorAdmin)


#class ReportAdmin(admin.ModelAdmin):
    #list_display = ('ward','title','point',)
    #list_display_links = ('title',)
    #ordering = ['ward', 'point']
    #exclude = ['photo']
#
#admin.site.register(Report,ReportAdmin)


class EmailRuleAdmin(admin.ModelAdmin):
	pass
 
admin.site.register(EmailRule,EmailRuleAdmin)
