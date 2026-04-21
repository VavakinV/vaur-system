from django.contrib import admin

from works.models import Work, WorkCorrection, WorkType


@admin.register(WorkType)
class WorkTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('topic', 'work_type', 'student', 'supervisor', 'department', 'norm_control_status', 'document_original_name')
    list_filter = ('work_type', 'norm_control_status', 'department')
    search_fields = (
        'topic',
        'document_original_name',
        'student__user__last_name',
        'student__user__first_name',
        'supervisor__user__last_name',
        'supervisor__user__first_name',
        'department__name',
        'work_type__name',
    )


@admin.register(WorkCorrection)
class WorkCorrectionAdmin(admin.ModelAdmin):
    list_display = ('work', 'author', 'author_role', 'is_resolved', 'resolved_at', 'created_at')
    list_filter = ('author_role', 'is_resolved', 'created_at')
    search_fields = (
        'work__topic',
        'author__user__last_name',
        'author__user__first_name',
        'author__user__email',
    )
