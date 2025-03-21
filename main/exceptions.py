class BaseException(Exception):
    pass


class InvalidSignatureException(BaseException):
    pass


class InvalidApiKeyException(BaseException):
    pass


class NoDefaultTextPrompts(BaseException):
    pass


class NoDefaultImagePrompts(BaseException):
    pass
