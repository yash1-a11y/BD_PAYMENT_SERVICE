class PackageNotEligibleError(Exception):
    pass


class DuplicatePackageIdError(Exception):
    pass


class ImmutableFieldError(Exception):
    pass


class InvalidPriceError(Exception):
    pass


class CatalogueEntryNotFoundError(Exception):
    pass
