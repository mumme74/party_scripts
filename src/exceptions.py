
class AppException(Exception):
    """Base exception for this app"""
    pass

class ReadFileException(AppException):
    """When an error occurs reading a file
    
    Attributes
    ----------
    file: str
        The path to the file that could not be read
    """
    def __init__(self, file, *args):
        super().__init__(*args)
        self.file = file

class ReadFileNotFound(ReadFileException):
    """When a file could not be found"""
    pass

class ReadFileUnhandledFormat(ReadFileException):
    """When trying to open an unhandled format"""
    pass

class InputDataBadFormat(ReadFileException):
    """When input has wrong format"""
    pass

class WriteFileException(AppException):
    def __init__(self, file, *args):
        super().__init__(*args)
        self.file = file

class WriteFileExists(WriteFileException):
    pass

class DataRetrivalError(AppException):
    """When trying to get an invalid value"""
    pass

class DuplicatePersonException(AppException):
    """When a person is included twice

    Attributes
    ----------
    person: Person
        A instance of the duplicate person
    """
    def __init__(self, person, *args):
        super().__init__(*args)
        self.name = person

class TooFewSeats(AppException):
    """When there are more persons to place than there are seats"""
    pass
