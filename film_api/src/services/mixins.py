from models.common import ListRequest


class ServiceMixin:
    def validate_request(self, request: ListRequest) -> bool:
        actual_sort_field = self.valid_sort_options.get(request.sort[1:], None)
        if actual_sort_field:
            request.sort = request.sort[0] + actual_sort_field
            return True
        return False
