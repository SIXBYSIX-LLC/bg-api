from common.dispatch import Signal


invoice_paid = Signal(providing_args=['instance', 'now', 'force', 'confirm_order'])
