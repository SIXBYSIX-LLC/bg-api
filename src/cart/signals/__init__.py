from common.dispatch import Signal


pre_cost_calculation = Signal(providing_args=['instance'])
post_cost_calculation = Signal(providing_args=['instance'])
