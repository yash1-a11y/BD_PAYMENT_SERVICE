from pydantic import BaseModel

# Field names below mirror Transfi's documented request contract exactly
# (confirmed against their real Postman collection) — camelCase, not our
# own snake_case convention, since this is a direct wire-format mirror of
# an external API, not our own internal style.


class Address(BaseModel):
    """Transfi's example payload includes this on every request. Our checkout
    form doesn't collect an address (only Name/Email/Phone, per spec), so
    these are sent empty — flagged as a real gap if Transfi's validation
    turns out to require non-empty values; not something to fabricate."""

    city: str = ""
    state: str = ""
    street: str = ""
    postalCode: str = ""


class ProductDetails(BaseModel):
    name: str
    description: str
    imageUrl: str | None = None


class IndividualDetails(BaseModel):
    firstName: str
    lastName: str
    email: str
    phone: str
    country: str = "BD"
    phoneCode: str = "+880"
    address: Address = Address()


class PaymentInvoiceRequest(BaseModel):
    paymentLinkId: str
    amount: str
    currency: str = "BDT"
    customerOrderId: str
    productDetails: ProductDetails
    individual: IndividualDetails
    successRedirectUrl: str
    failureRedirectUrl: str
