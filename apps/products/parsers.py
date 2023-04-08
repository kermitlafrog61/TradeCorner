from rest_framework.parsers import DataAndFiles
from rest_framework.parsers import MultiPartParser


class ProductParser(MultiPartParser):
    def parse(self, stream, media_type=None, parser_context=None):
        raw_parse = super().parse(stream, media_type, parser_context)

        data = raw_parse.data.copy()
        files = raw_parse.files.copy()

        categories = data.get('categories')
        if categories:
            data.setlist('categories', categories.split(','))
        return DataAndFiles(data, files)
