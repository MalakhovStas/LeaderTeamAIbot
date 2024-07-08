from django.contrib import admin
from core.models import AssistantSettings, Feedback


@admin.register(AssistantSettings)
class AssistantConfAdmin(admin.ModelAdmin):
    """Регистрация модели AssistantSettings в админке"""

    def has_add_permission(self, request):
        return not AssistantSettings.objects.exists()


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """Регистрация модели Feedback в админке"""
    model = Feedback
    fields = (
        'created_at',
        'is_active',
        'user',
        'feedback',
        'response',
        'admin',
    )
    ordering = ('created_at',)
    readonly_fields = (
        'created_at',
    )
    search_fields = ('feedback', 'response')
    # extra = 0
    # max_num = 0
    # can_delete = False
    # classes = ('collapse',)
    # verbose_name_plural = _('command')
    # exclude = ('pk',)
    # FIXME исправить отображение admin(видит только себя), если is_active=False нельзя редактировать response
    # def get_queryset(self, request):
    #     """Возвращает набор экземпляров модели Seller в зависимости от прав пользователя"""
    #     queryset = super().get_queryset(request)
    #     # if request.user.is_superuser:
    #     #     return queryset
    #     return queryset.filter(admin=request.user)
