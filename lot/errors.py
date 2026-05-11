class LoTError(Exception):
    """Base class for LoT-related errors."""


class LoTConfigError(LoTError):
    """Invalid or inconsistent configuration."""


class LoTSemanticsError(LoTError):
    """Program cannot be executed under the current semantics."""


class LoTComplexityError(LoTError):
    """Complexity/minimal-program computation failed."""
