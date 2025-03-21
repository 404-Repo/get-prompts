class ExceptionBase(Exception):
    pass


class InvalidSignatureException(ExceptionBase):
    pass


class InvalidApiKeyException(ExceptionBase):
    pass


class NoDefaultTextPrompts(ExceptionBase):
    pass


class NoDefaultImagePrompts(ExceptionBase):
    pass
