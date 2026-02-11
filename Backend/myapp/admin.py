from django.contrib import admin

from .models import DailyLog,QuestionnaireResponse, Resource

admin.site.register(DailyLog)
admin.site.register(QuestionnaireResponse)
@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'category', 'created_at')
    list_filter = ('course', 'category')
    search_fields = ('title',)


