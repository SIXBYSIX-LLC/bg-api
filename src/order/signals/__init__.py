from common.dispatch import Signal

item_status_change = Signal(providing_args=['instance', 'old_status', 'new_status'])
item_pre_cancel = Signal(providing_args=['instance'])
item_post_cancel = Signal(providing_args=['instance'])
