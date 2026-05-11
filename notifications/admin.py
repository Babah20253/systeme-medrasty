from django.contrib import admin

from notifications.models import OTPCode, SMSLog


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ('phone', 'purpose', 'expires_at', 'is_used', 'created_at')
    list_filter = ('purpose', 'is_used')
    search_fields = ('phone',)
    readonly_fields = ('created_at',)


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ('phone', 'purpose', 'status', 'sent_at')
    list_filter = ('purpose', 'status')
    search_fields = ('phone',)
    readonly_fields = ('sent_at',)
