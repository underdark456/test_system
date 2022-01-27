class NoSuchParamException(Exception):
    """Cannot find such parameter"""
    pass


class ObjectNotFoundException(Exception):
    """Cannot find the object"""
    pass


class ObjectNotCreatedException(Exception):
    """Cannot create the object"""
    pass


class ObjectNotUpdatedException(Exception):
    """Cannot update the object"""
    pass


class ObjectNotDeletedException(Exception):
    """Cannot delete the object"""
    pass


class DriverInitException(Exception):
    """Cannot initialize the driver"""
    pass


class InvalidIdException(Exception):
    """No such ID exists"""
    pass


class NotImplementedException(Exception):
    """Метод не реализован"""
    pass


class UhpResponseException(Exception):
    """Cannot get the response from UHP"""
    pass


class InvalidOptionsException(Exception):
    """The options provided for a test are either incomplete or invalid"""
    pass


class NmsControlledModeException(Exception):
    """UHP under a test is not in the NMS controlled mode"""
    pass


class ParameterNotPassedException(Exception):
    """Required parameter is not passed to the called method"""
    pass


class NmsErrorResponseException(Exception):
    """NMS returned either non-zero error code or error status"""
    pass


class UhpUpStateException(Exception):
    """UHP either controller or station is not in UP state"""
    pass


class NmsWebDriverTimeout(Exception):
    """Web driver timed out"""
    pass


class InvalidModeException(Exception):
    """Wrong object mode"""
    pass


class NmsDownloadException(Exception):
    """Cannot download from NMS"""
    pass
