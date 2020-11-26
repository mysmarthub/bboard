from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.generics import RetrieveAPIView

from main.models import Bb, Comment
from .serializers import BbSerializers, BbDetailSerializer, CommentSerializer


@api_view(['GET', ])
def bbs(request):
    if request.method == 'GET':
        bb_list = Bb.objects.filter(is_active=True)[:10]
        serializer = BbSerializers(bb_list, many=True)
        return Response(serializer.data)


class BbDetailView(RetrieveAPIView):
    queryset = Bb.objects.filter(is_active=True)
    serializer_class = BbDetailSerializer


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticatedOrReadOnly, ))
def comments(request, pk):
    if request.method == 'POST':
        serializers = CommentSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=HTTP_201_CREATED)
        else:
            return Response(serializers.errors, status=HTTP_400_BAD_REQUEST)
    else:
        comment_list = Comment.objects.filter(is_active=True, bb=pk)
        serializers = CommentSerializer(comment_list, many=True)
        return Response(serializers.data)
