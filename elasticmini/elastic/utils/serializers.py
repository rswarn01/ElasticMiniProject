class EmailData:

    email = None
    subject = None
    title = None
    message = None
    module_name = None

    def __init__(self, _email, _subject, _title, _message, _file_name=None):
        self.email = _email
        self.subject = _subject
        self.title = _title
        self.message = _message
        self.file_name = _file_name
