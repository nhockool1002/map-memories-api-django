from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination class that matches the original API format
    """
    page_size = 20
    page_size_query_param = 'limit'
    max_page_size = 100
    page_query_param = 'page'

    def get_paginated_response(self, data):
        """
        Return paginated response in the format expected by the frontend
        """
        return Response(OrderedDict([
            ('success', True),
            ('message', 'Data retrieved successfully'),
            ('data', data),
            ('pagination', OrderedDict([
                ('current_page', self.page.number),
                ('per_page', self.page.paginator.per_page),
                ('total', self.page.paginator.count),
                ('total_pages', self.page.paginator.num_pages),
                ('has_next', self.page.has_next()),
                ('has_prev', self.page.has_previous()),
                ('next_page', self.page.next_page_number() if self.page.has_next() else None),
                ('prev_page', self.page.previous_page_number() if self.page.has_previous() else None),
            ]))
        ]))


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination for larger datasets
    """
    page_size = 50
    page_size_query_param = 'limit'
    max_page_size = 200
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('success', True),
            ('message', 'Data retrieved successfully'),
            ('data', data),
            ('pagination', OrderedDict([
                ('current_page', self.page.number),
                ('per_page', self.page.paginator.per_page),
                ('total', self.page.paginator.count),
                ('total_pages', self.page.paginator.num_pages),
                ('has_next', self.page.has_next()),
                ('has_prev', self.page.has_previous()),
                ('next_page', self.page.next_page_number() if self.page.has_next() else None),
                ('prev_page', self.page.previous_page_number() if self.page.has_previous() else None),
            ]))
        ]))


class SmallResultsSetPagination(PageNumberPagination):
    """
    Pagination for smaller datasets
    """
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 50
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('success', True),
            ('message', 'Data retrieved successfully'),
            ('data', data),
            ('pagination', OrderedDict([
                ('current_page', self.page.number),
                ('per_page', self.page.paginator.per_page),
                ('total', self.page.paginator.count),
                ('total_pages', self.page.paginator.num_pages),
                ('has_next', self.page.has_next()),
                ('has_prev', self.page.has_previous()),
                ('next_page', self.page.next_page_number() if self.page.has_next() else None),
                ('prev_page', self.page.previous_page_number() if self.page.has_previous() else None),
            ]))
        ]))