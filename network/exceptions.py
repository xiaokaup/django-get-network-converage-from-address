from rest_framework.response import Response


# class BadResquest(Exception):
#     status_code = 400
#     default_detail = "Bad Request"
#     error_code = "BAD_REQUEST"

#     def __init__(self, detail, status_code=None):
#         self.detail = detail
#         if status_code is not None:
#             self.status_code = status_code


class BadResponse(Response):
    status = 400
    data = "invalid request"

    def __init__(self, data: str = None):
        super().__init__(data if data else self.data, self.status)
