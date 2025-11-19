class GeneralResponseBody:

    def __init__(self, message, status=1, data=None):
        self.message = message
        self.status = status
        self.data = data

    def get_response_body(self):
        body = {
            'status': self.status,
            'message': self.message,
            'data': self.data
        }

        return body
