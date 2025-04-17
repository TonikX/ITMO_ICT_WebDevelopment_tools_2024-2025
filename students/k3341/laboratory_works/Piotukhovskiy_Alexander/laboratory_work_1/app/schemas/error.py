from collections import defaultdict


class Error:
    def __init__(self):
        self.is_error = False
        self.errors = defaultdict(list)

    def add_error(self, field_name, field_description):
        self.is_error = True
        self.errors[field_name].append(field_description)
