from rest_framework import generics
from ..models import PostPage
from .serializers import PostPageSerializer

class PostPageListView(generics.ListAPIView):
    queryset = PostPage.objects.all()
    serializer_class = PostPageSerializer


class PostPageDetailView(generics.RetrieveAPIView):
    queryset = PostPage.objects.all()
    serializer_class = PostPageSerializer