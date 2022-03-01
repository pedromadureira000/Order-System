from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

#  def agent_has_access_to_this_item_category(agent, item_category):
    #  item_tables = get_agent_item_tables(agent)
    #  if item_category.item_table not in item_tables:
        #  return False
    #  else: 

def non_negative_number(value):
    if value < 0:
        raise serializers.ValidationError(_('This field cannot be an negative number.'))

def positive_number(value):
    if value <= 0:
        raise serializers.ValidationError(_('This field must be an positive number.'))

def order_has_changed(order, attrs):
    return False if order.order_amount == attrs.get('order_amount', order.order_amount) and order.status == attrs.get('status', order.status) and order.note == attrs.get('note', order.note) and order.agent_note == attrs.get('agent_note', order.agent_note) and order.invoice_number == attrs.get('invoice_number', order.invoice_number) and order.billing_date == attrs.get('billing_date', order.billing_date) else True
