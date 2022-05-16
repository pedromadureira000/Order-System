from decimal import ROUND_HALF_UP, Decimal
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderHistory

@receiver(pre_save, sender=Order)
def order_pre_save(sender, instance, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    if old_instance:
        # Clear invoice_number and invoicing_date if status is coming back from 'Registered 'to 'Invoiced'.
        if instance.status == 3 and old_instance.status == 4:
            instance.invoicing_date = None
            instance.invoice_number = ''


@receiver(post_save, sender=Order)
def order_post_save(sender, instance, created=False, **kwargs):
    old_instance = getattr(instance, '_old_instance', None)
    request_user = getattr(instance, '_request_user', None)
    # Order Inclusion
    if created:
        order_history = OrderHistory(order=instance, user_id=instance.client_user_id, history_type="I")
        if instance.status == 1:
            order_history.history_description = "- " + _("Order created with 'Typing' status.")
        if instance.status == 2:
            order_history.history_description = "- " + _("Order created with 'Transferred' status.")
        order_history.save()
    # Order Status Alteration
    else:
        order_history = OrderHistory(order=instance, history_type="A")
        # Change order status
        if old_instance.status != instance.status:
            old_status = instance.get_status_verbose_name(old_instance.status)
            new_status = instance.get_status_verbose_name(instance.status)
            order_history.history_description = _("- Order status changed from '{old_status}' to '{new_status}'.").format(old_status=old_status, new_status=new_status)
        # If request_user is ClientUser
        if instance.client_user_id == request_user.user_code:
            order_history.user_id = instance.client_user_id
            # Client User update OrderedItems
            if old_instance.order_amount != instance.order_amount:
                old_amount = old_instance.order_amount
                # This is for reduce decimal places for 2
                new_amount = instance.order_amount.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
                order_history.history_description += _("\n- Order amount changed from '{old_amount}' to '{new_amount}'.").format(old_amount=old_amount, new_amount=new_amount)
            # Client User update update note
            if old_instance.note != instance.note:
                order_history.history_description += _("\n- Order note changed.")

            sequence_number_was_changed = getattr(instance, 'sequence_number_was_changed', None)
            if sequence_number_was_changed:
                order_history.history_description += _("\n- Items sequence was changed.")
        # If request_user is Agent/ERP
        else:
            order_history.user_id = request_user.user_code
            # Agent create note
            if old_instance.agent_note != instance.agent_note:
                order_history.history_description += _("\n - Agent note added.")
                order_history.agent_note = instance.agent_note
                if old_instance.status == instance.status:
                    order_history.history_type = "N"
            # Add invoice_number field
            if old_instance.invoice_number != instance.invoice_number:
                if not instance.invoice_number:
                    order_history.history_description += _("\n - The invoice number field was cleaned.")
                else:
                    order_history.history_description += _("\n - Invoice number added with value '{invoice_number}'.").format(invoice_number=instance.invoice_number)
            # Add invoicing_date field
            if old_instance.invoicing_date != instance.invoicing_date:
                if not instance.invoicing_date:
                    order_history.history_description += _("\n - The invoice date field was cleaned.")
                else:
                    order_history.history_description += _("\n - Invoice date added with value '{invoicing_date}'.").format(invoicing_date=instance.invoicing_date)
        order_history.save()
