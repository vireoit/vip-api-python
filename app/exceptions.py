from .response import Response

class FileNotSelected(Exception):
    def __init__(self, param_name, message="No file selected for uploading"):
        self.message = message + " " + param_name
        super().__init__(self.message)


class FileUploadException(Exception):
    def __init__(self, message="Unable to upload file"):
        self.message = message
        super().__init__(self.message)


class FileFormatException(Exception):
    def __init__(self,param_name, message="Allowed file"):
        self.message = message + " " + param_name
        super().__init__(self.message)


class FileTypeException(Exception):
    def __init__(self, param_name, message="Please upload the required file type."):
        self.message = message
        super().__init__(self.message)
        