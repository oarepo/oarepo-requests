class OpenRequestAlreadyExists(Exception):
    """An open request already exists."""

    def __init__(self, request, record):
        self.request = request
        self.record = record

    @property
    def description(self):
        """Exception's description."""
        return f"There is already an open request of {self.request.name} on {self.record.id}."


class UnknownRequestType(Exception):
    def __init__(self, request_type):
        self.request_type = request_type

    @property
    def description(self):
        """Exception's description."""
        return f"Unknown request type {self.request_type}."


class RequestTypeNotInWorkflow(Exception):
    def __init__(self, request_type, workflow):
        self.request_type = request_type
        self.workflow = workflow

    @property
    def description(self):
        """Exception's description."""
        return f"Request type {self.request_type} not in workflow {self.workflow}."