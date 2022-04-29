from organization.facade import get_agent_companies
from organization.models import Company, Establishment
from .models import Order, OrderHistory, OrderedItem
from django.db.models import Prefetch

# ----------------------------/ Orders /-----------------------------
def get_orders_by_agent(agent):
    return Order.objects.filter(establishment__in=agent.establishments.all())

def fetch_comps_with_estabs_to_fill_filter_selectors_to_search_orders(user):
    establishments = Establishment.objects.all()
    return Company.objects.filter(contracting_id=user.contracting_id).prefetch_related(
        Prefetch('establishment_set', queryset=establishments, to_attr='establishments')
    )

def fetch_comps_with_estabs_to_fill_filter_selectors_to_search_orders_by_agent(user):
    return get_agent_companies(user).prefetch_related(
        Prefetch('establishment_set', queryset=user.establishments.all(), to_attr='establishments')
    )

def fetch_comps_with_estabs_to_fill_filter_selectors_to_search_orders_by_client_user(user):
    #  establishments = user.client.establishments.all()  <-- This would make a unnecessary query to 'client' 
    establishments = Establishment.objects.filter(clientestablishment__client_id=user.client_id)
    return Company.objects.filter(establishment__in=establishments).prefetch_related(
        Prefetch('establishment_set', queryset=establishments, to_attr='establishments')
    )

def update_ordered_items(order, ordered_items, current_ordered_items):
    # Create set of OrderedItems as tuples
    ordered_items_set = {(ordered_item['item'].item_compound_id, ordered_item['quantity'], ordered_item['unit_price'], 
        ordered_item['sequence_number']) for ordered_item in ordered_items}
    current_ordered_items_set = set(current_ordered_items.values_list('item__item_compound_id', 'quantity', 'unit_price', 'sequence_number'))
    intersection = ordered_items_set.intersection(current_ordered_items_set)
    to_delete = current_ordered_items_set.difference(intersection)
    to_create = ordered_items_set.difference(intersection)
    to_delete_item_list = [ordered_item[0] for ordered_item in to_delete]
    current_ordered_items.filter(item__item_compound_id__in=to_delete_item_list).delete()
    # List the OrderedItems to be created from the serialized 'ordered_items'. 
    ordered_items_to_create = list(filter(lambda ordered_item: (ordered_item["item"].item_compound_id, 
        ordered_item['quantity'], ordered_item['unit_price'], ordered_item['sequence_number']) in to_create, ordered_items))
    if ordered_items_to_create:
        # Create a list with the real OrderedItem instances to be saved with bulk_create.
        ordered_items_to_create = [OrderedItem(item=obj['item'], quantity=obj['quantity'], unit_price=obj['unit_price'],
            order=order, sequence_number=obj['sequence_number']) for obj in  ordered_items_to_create]
        order.ordered_items.bulk_create(ordered_items_to_create)

#---------------------------Old apis

#  def get_items_by_category():
    #  itens_actives = Item.objects.filter(active=True)
    #  return ItemCategory.objects.prefetch_related(
        #  Prefetch('item_set', queryset=itens_actives, to_attr='items')).all()

#  def user_category_items_queryset(request):
    #  if not request.user.company:
        #  return None
    #  try:
        #  table = PriceTable.objects.get(company=request.user.company)
    #  except PriceTable.DoesNotExist:
        #  return None
    #  items = Item.objects.filter(active=True).filter(pricetable=table)
    #  return ItemCategory.objects.prefetch_related(
        #  Prefetch('item_set', queryset=items, to_attr='items')).all()
                    # >> itens = Item.objects.prefetch_related('item_code').filter(pricetable=user.company.pricetable)
                    # items = request.user.company.pricetable.itens_preco.select_related('item')
                    # items = request.user.company.pricetable.itens.prefetch_related('item_code')
                    # items = Item.objects.prefetch_related('item_code').filter(pricetable=request.user.company.pricetable)
                    # itemspreco = request.user.company.pricetable.itens_preco.all()
                    # items = Item.objects.prefetch_related(Prefetch('item_code', queryset=itemspreco, to_attr='itempreco'))

                    # if not request.user.company or not request.user.company.pricetable:
                    #     return None
                    #
                    # items = Item.objects.filter(active=True).filter(pricetable__pk=request.user.company.pricetable_id)
                    # return ItemCategory.objects.prefetch_related(
                    #     Prefetch('item_set', queryset=items, to_attr='itens')).all()

#  def get_all_items_by_category():
    #  items = Item.objects.all()
    #  return ItemCategory.objects.prefetch_related(
        #  Prefetch('item_set', queryset=items, to_attr='items')).all()

#  def get_orders(request):
    #  if request.GET.get('term') is not None and request.GET.get('term') != '':
        #  term = request.GET.get('term')
        #  for status in Order.status_choices:
            #  if term.lower() in status[1].lower():
                #  return Order.objects.filter(status=status[0]).all()
        #  fields = Concat('user__first_name', Value(' '), 'user__last_name')  # Value is needed fo the blank space ' '
        #  if has_role(request.user, "ERPClient"):
            #  return Order.objects.annotate(full_name=fields).order_by('-order_date').filter(
                #  Q(status=term) | Q(company__name__icontains=term) |
                #  Q(order_amount__icontains=term) | Q(user__first_name__icontains=term) | Q(user__last_name__icontains=term)
                #  | Q(full_name__icontains=term), company=request.user.company).select_related(
                #  'company', 'user')
        #  return Order.objects.annotate(full_name=fields).order_by('-order_date').filter(
            #  Q(status__icontains=term) | Q(company__name__icontains=term) |
            #  Q(order_amount__icontains=term) | Q(user__first_name__icontains=term) | Q(user__last_name__icontains=term)
            #  | Q(full_name__icontains=term), user=request.user).select_related('company')

    #  if has_role(request.user, "ERPClient"):
        #  return Order.objects.order_by('-order_date').filter(company=request.user.company_id).select_related(
            #  'company', 'user')
    #  return Order.objects.order_by('-order_date').filter(user=request.user).select_related(
        #  'company')

