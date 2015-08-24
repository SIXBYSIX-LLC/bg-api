from common.dispatch import Signal


invoice_paid = Signal(providing_args=['instance', 'now', 'force', 'confirm_order'])
new_invoice_generated = Signal(providing_args=['instance'])
post_invoiceline_approve = Signal(providing_args=['instance'])
post_invoice_approve = Signal(providing_args=['instance', 'force'])
