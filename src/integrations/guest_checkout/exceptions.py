class GuestCheckoutError(Exception):
    """Base class for all Guest Checkout integration errors."""


class GuestCheckoutRequestError(GuestCheckoutError):
    """The Guest Checkout API returned a non-success response, or the request
    itself failed (network error, timeout).

    Not raised by anything yet — nothing in the running application calls
    src.integrations.guest_checkout.client.call_guest_checkout. Defined now so
    the eventual real caller (src/modules/fulfilment/service.py::allocate_package)
    has a ready-made exception type to catch, matching the same pattern
    src/integrations/transfi/exceptions.py already established.
    """
