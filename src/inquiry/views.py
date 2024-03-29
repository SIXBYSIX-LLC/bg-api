from rest_framework.mixins import (ListModelMixin, CreateModelMixin)
from django.db.models import Count, Case, When, Value, Q

from common.viewsets import GenericViewSet, NestedViewSetMixin
from .models import (Message, Thread)
from .serializers import (ThreadSerializer, MessageSerializer)


class ThreadViewSet(GenericViewSet, ListModelMixin, CreateModelMixin):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer

    ownership_fields = ('user', 'to_user')

    def get_queryset(self):
        user = self.request.parent_user or self.request.user
        qs = super(ThreadViewSet, self).get_queryset()
        # Unread message count
        qs = qs.annotate(unread_count=Count(Case(When(
            Q(message__is_read=False) & ~Q(message__user=user), then=Value(1)
        ))))
        # Total message count
        qs = qs.annotate(message_count=Count('message'))

        return qs


class MessageViewSet(NestedViewSetMixin, GenericViewSet, ListModelMixin, CreateModelMixin):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def list(self, request, *args, **kwargs):
        # Auto mark as read
        self.get_queryset().update(is_read=True)
        return super(MessageViewSet, self).list(request, *args, **kwargs)
