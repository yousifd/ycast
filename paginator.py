class PaginatorException(Exception):
    pass

class FirstPageException(PaginatorException):
    pass

class LastPageException(PaginatorException):
    pass

class Paginator:
        def __init__(self, entries, min_index, max_index, jump_length=10):
            self.entries = entries
            self.min_index = min_index
            self.max_index = max_index
            self.jump_length = jump_length
            self.current_min = min_index
            self.current_max = jump_length if max_index > jump_length else max_index

        def get_current_page(self):
            return self.entries[self.current_min:self.current_max]

        def get_next(self):
            if self.current_min + self.jump_length >= self.max_index:  # Last Page
                raise LastPageException
            self.current_min += self.jump_length
            # Too few entries in last page
            if self.current_max + self.jump_length > self.max_index:
                self.current_max = self.max_index
            else:
                self.current_max += self.jump_length

        def get_prev(self):
            if self.current_max - self.jump_length <= self.min_index:  # First Page
                raise FirstPageException
            self.current_min -= self.jump_length
            if self.current_max == self.max_index:
                self.current_max = self.current_min + self.jump_length
            else:
                self.current_max -= self.jump_length
