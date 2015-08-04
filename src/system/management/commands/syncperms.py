from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, ContentType

from group.models import Group


class Command(BaseCommand):
    args = '<app app ...>'
    help = 'reloads permissions for specified apps, or all apps if no args are specified'

    def handle(self, *args, **options):
        self.app_perms()

    def app_perms(self):
        # Creating groups
        device_group, created = Group.objects.get_or_create(name="Device")
        user_group, created = Group.objects.get_or_create(name="User")
        group_content_type = ContentType.objects.get_by_natural_key('group', 'group')

        # Assigning user group permission
        user_group.permissions.add(
            # Profiles
            Permission.objects.get(codename='add_profile'),
            Permission.objects.get(codename='change_profile'),
            Permission.objects.get(codename='delete_profile'),
            Permission.objects.get(codename='view_profile'),
            # Address
            Permission.objects.get(codename='add_address'),
            Permission.objects.get(codename='change_address'),
            Permission.objects.get(codename='delete_address'),
            Permission.objects.get(codename='view_address'),
            # Groups
            Permission.objects.get(codename='add_group', content_type=group_content_type),
            Permission.objects.get(codename='change_group', content_type_id=group_content_type),
            Permission.objects.get(codename='delete_group', content_type_id=group_content_type),
            Permission.objects.get(codename='view_group', content_type_id=group_content_type),
            # Category
            Permission.objects.get(codename='view_category'),
            # Products
            Permission.objects.get(codename='add_product'),
            Permission.objects.get(codename='change_product'),
            Permission.objects.get(codename='view_product'),
            # Inventories
            Permission.objects.get(codename='add_inventory'),
            Permission.objects.get(codename='change_inventory'),
            Permission.objects.get(codename='view_inventory'),
            # Staticfiles
            Permission.objects.get(codename='add_file'),
            Permission.objects.get(codename='delete_file'),
            # Inquiry
            Permission.objects.get(codename='add_thread'),
            Permission.objects.get(codename='view_thread'),
            Permission.objects.get(codename='add_message'),
            Permission.objects.get(codename='view_message'),
            # Shipping
            Permission.objects.get(codename='add_standardmethod'),
            Permission.objects.get(codename='view_standardmethod'),
            Permission.objects.get(codename='delete_standardmethod'),
            Permission.objects.get(codename='change_standardmethod'),
            # Cart
            Permission.objects.get(codename='change_cart'),
            Permission.objects.get(codename='view_cart'),
            Permission.objects.get(codename='add_rentalitem', content_type__app_label='cart'),
            Permission.objects.get(codename='change_rentalitem', content_type__app_label='cart'),
            Permission.objects.get(codename='delete_rentalitem', content_type__app_label='cart'),
            # Order
            Permission.objects.get(codename='add_order'),
            Permission.objects.get(codename='view_order'),
            Permission.objects.get(codename='change_order'),
            Permission.objects.get(codename='view_orderline'),
            Permission.objects.get(codename='change_orderline'),
            Permission.objects.get(codename='change_item', content_type__app_label='order'),
            # Charges
            Permission.objects.get(codename='add_additionalcharge'),
            Permission.objects.get(codename='view_additionalcharge'),
            Permission.objects.get(codename='change_additionalcharge'),
            Permission.objects.get(codename='delete_additionalcharge'),
            # Invoice
            Permission.objects.get(codename='view_invoice'),
            Permission.objects.get(codename='view_invoiceline'),
            Permission.objects.get(codename='change_invoiceline'),
            Permission.objects.get(codename='view_item', content_type__app_label='invoice'),
            Permission.objects.get(codename='change_item', content_type__app_label='invoice'),
        )

        # Assign device group permission
        device_group.permissions.add(
            # Profiles
            Permission.objects.get(codename='add_profile'),
            # Category
            Permission.objects.get(codename='view_category'),
            Permission.objects.get(codename='view_product'),
        )


