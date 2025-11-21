class GeneralResponseBody:

    def __init__(self, message, status=0, data=None):
        '''
        A generic response body.
        :param message:
        :param status: 0 OK; 1 Error
        :param data:
        '''
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
