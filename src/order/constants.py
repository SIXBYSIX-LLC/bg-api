class Status(object):
    NOT_CONFIRMED = 'not_confirmed'  # Order placed but payment not confirmed
    CONFIRMED = 'confirmed'  # Order placed and payment confirmed, ie, confirmed by the system
    APPROVED = 'approved'  # Approved by seller
    READY_TO_SHIP = 'ready_to_ship'  # Item is ready to ship
    DISPATCHED = 'dispatched'  # Item has been dispatched, shipped
    READY_TO_PICKUP = 'ready_to_pickup'  # Item is ready to be picked up
    PICKED_UP = 'picked_up'  # Item has been picked up
    DELIVERED = 'delivered'  # Item is delivered
    CANCEL = 'cancelled'  # Item is cancelled by buyer or seller
