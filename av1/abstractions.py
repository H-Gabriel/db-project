import math

bucket_size = 4

class Table:
    def __init__(self, load_size, max_page_size) -> None:
        self.max_page_size = max_page_size
        self.pages_amount = math.ceil(load_size/max_page_size)
        self.pages = [[] for _ in range(self.pages_amount)]

    def load_pages(self, load):
        load.seek(0)  # Coloca a leitura do arquivo no início
        for page in self.pages:
            size = 0
            while size < self.max_page_size:
                line = load.readline().strip()
                if not line:
                    break
                page.append(line)
                size += 1

class Bucket:
    def __init__(self) -> None:
        self.refs : list[BucketRef] = []
        self.overflow_ref : Bucket = None

class BucketRef:
    def __init__(self, line, page) -> None:
        self.line = line
        self.page = page