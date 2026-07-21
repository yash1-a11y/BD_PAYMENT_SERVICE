from pydantic import BaseModel

# Field names below mirror the Guest Checkout API's expected request
# contract exactly as shared by the backend team — camelCase, not our own
# snake_case convention, since this is a direct wire-format mirror of an
# external API, not our own internal style (same convention already
# established in src/integrations/transfi/schemas.py).


class GuestCheckoutPackageItem(BaseModel):
    packageId: str
    price: str
    foreignCurrency: str = "BDT"
    foreignPrice: str


class GuestCheckoutRequest(BaseModel):
    name: str
    email: str
    mobile: str
    transactionPrice: str
    transactionId: str
    packageList: list[GuestCheckoutPackageItem]
