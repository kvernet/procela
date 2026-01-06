"""procela.core.exceptions."""


class SemanticViolation(TypeError):
    """
    Raised when an operation violates Key semantics.

    This includes attempts to order, compose, or derive meaning from Keys,
    which are prohibited by the Key semantic specification.
    """

    pass
