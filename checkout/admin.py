from django.contrib import admin
from .models import Order, OrderLineItem


class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ('lineitem_total',)


class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline,)
    list_display = ('order_number', 'user', 'created_at',
                    'order_total', 'delivery_cost', 'grand_total')
    search_fields = ['user__username']
    readonly_fields = ['order_number', 'created_at',
                       'order_total', 'delivery_cost']

    def user(self, obj):
        return obj.user.username

    user.admin_order_field = 'user'
    user.short_description = 'User'


admin.site.register(Order, OrderAdmin)
