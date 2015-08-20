from common.dispatch import Signal

pre_status_change = Signal(providing_args=['instance', 'old_status', 'new_status'])
post_status_change = Signal(providing_args=['instance', 'old_status', 'new_status'])
order_confirm = Signal(providing_args=['instance', 'now'])
