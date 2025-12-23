from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status
from django.shortcuts import get_object_or_404, get_list_or_404
from django.db.models import Q
from .models import Article, Comment
from .serializers import ArticleListSerializer, ArticleDetailSerializer, CommentSerializer, ArticleCreateSerializer

# 게시글 목록 조회 & 생성 
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])    # 로그인 하지 않아도 조회는 가능
def article_list(request):
    if request.method == 'GET':
        articles = Article.objects.all().order_by('-created_at')

        search_keyword = request.GET.get('search', '')     # 검색어 (없으면 빈 문자열)
        search_condition = request.GET.get('condition', 'title_content')   # 검색 조건 (기본값: 제목+내용)

        if search_keyword:
            if search_condition == 'title':
                articles = articles.filter(title__icontains=search_keyword)
            
            elif search_condition == 'content':
                articles = articles.filter(content__icontains=search_keyword)
            
            elif search_condition == 'author':
                articles = articles.filter(user__username__icontains=search_keyword)
            
            else: 
                articles = articles.filter(
                    Q(title__icontains=search_keyword) | 
                    Q(content__icontains=search_keyword)
                )

        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ArticleCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

# 2. 게시글 상세 조회, 수정, 삭제
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def article_detail(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)

    if request.method == 'GET':
        # 조회수 기능 구현
        article.hits += 1
        article.save()

        serializer = ArticleDetailSerializer(article)
        return Response(serializer.data)
    
    if request.user != article.user:
        return Response({'message': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'DELETE':
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    elif request.method == 'PUT':
        if request.data.get('image_clear') == 'true':
            article.image = None 
        
        serializer = ArticleDetailSerializer(article, data=request.data, partial=True)
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

# 댓글 생성
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_create(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(article=article, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def comment_delete(request, article_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    
    if request.user != comment.user:
        return Response({'message': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    
    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# 좋아요 기능
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_article(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)
    if article.like_users.filter(pk=request.user.pk).exists():
        article.like_users.remove(request.user) # 좋아요 취소
        liked = False
    else:
        article.like_users.add(request.user) # 좋아요
        liked = True
    
    return Response({
        'liked': liked, 
        'count': article.like_users.count()
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_comments(request):
    comments = request.user.comments.all().order_by('-created_at')
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)