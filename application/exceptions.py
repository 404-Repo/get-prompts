class BaseException(Exception):
    pass


class InvalidSignatureException(BaseException):
    pass


class InvalidApiKeyException(BaseException):
    pass


class FileWithTextDataDoesntExist(BaseException):
    pass


class NotEnoughPromptsAvailable(BaseException):
    pass
