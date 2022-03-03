from decimal import ROUND_DOWN, Decimal
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from settings import settings
from django.utils.translation import gettext_lazy as _
from orders.models import Order, OrderHistory

@receiver(pre_save, sender=Order)
def order_pre_save(sender, instance, **kwargs):
    if instance.id:
        old_instance = getattr(instance, '_old_instance', None)
        # Clear invoice_number and invoicing_date if status is coming back from 'Registered 'to 'Invoiced'.
        if instance.status == 4 and old_instance.status == 3:
            instance.invoicing_date = None
            instance.invoice_number = ''


@receiver(post_save, sender=Order)
def order_post_save(sender, instance, created=False, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    request_user = getattr(instance, '_request_user', None)
    # Order Inclusion
    if created:
        order_history = OrderHistory(order=instance, user=instance.client_user, history_type="I")
        if instance.status == 1:
            order_history.history_description = _("Order created with 'Typing' status.")
        if instance.status == 2:
            order_history.history_description = _("Order created with 'Transferred' status.")
        order_history.save()
    # Order Status Alteration
    else:
        order_history = OrderHistory(order=instance, history_type="A")
        # Change order status
        if old_instance.status != instance.status:
            old_status = instance.get_status_verbose_name(old_instance.status)
            new_status = instance.get_status_verbose_name(instance.status)
            order_history.history_description = _("- Order status changed from '{old_status}' to '{new_status}'.").format(old_status=old_status, 
                    new_status=new_status)
        # If request_user is ClientUser
        if instance.client_user == request_user:
            order_history.user = instance.client_user
            # Client User update OrderedItems
            if old_instance.order_amount != instance.order_amount:
                old_amount = old_instance.order_amount
                # This is for reduce decimal places for 2
                new_amount = instance.order_amount.quantize(Decimal('.01'), rounding=ROUND_DOWN)
                order_history.history_description += _("\n- Order amount changed from '{old_amount}' to '{new_amount}'.").format(old_amount=old_amount, new_amount=new_amount)
            # Client User update update note
            if old_instance.note != instance.note:
                order_history.history_description += _("\n- Order note changed.")
        # If request_user is Agent/ERP
        else:
            order_history.user = request_user
            # Agent create note
            if old_instance.agent_note != instance.agent_note:
                order_history.history_description += _("\n - Agent note added.")
                order_history.agent_note = instance.agent_note
                if old_instance.status == instance.status:
                    order_history.history_type = "N"
        order_history.save()
