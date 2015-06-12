from common.dispatch import Signal


reset_password_request = Signal(providing_args=['instance', 'retry'])
reset_password_done = Signal(providing_args=['instance'])
password_changed = Signal(providing_args=['instance'])
