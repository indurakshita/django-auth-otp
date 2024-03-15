from rest_framework.filters import BaseFilterBackend


class SortFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        ordering = request.query_params.get("sort", None)
        if ordering:
            return queryset.order_by(ordering)
        return queryset
