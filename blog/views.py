from django.shortcuts import render , get_object_or_404
from django.core.paginator import Paginator, EmptyPage,\
                                                PageNotAnInteger
from .models import Post , Comment
from .forms import EmailPostForm , CommentForm
from taggit.models import Tag
from django.db.models import Count
# Create your views here.

def post_list(request, tag_slug=None):
    post = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = post.filter(tags__in=[tag])
    paginator = Paginator(post, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)

    
    return render(request, 'blog/post/list.html', {'page': page,'posts': posts, 'tag':tag})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published',
                                            publish__year=year,
                                            publish__month=month,
                                            publish__day=day)

    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]
    return render(request, 'blog/post/detail.html', {'post':post, 'comments':comments, 
                                                    'new_comment':new_comment , 'comment_form':comment_form,
                                                    'similar_posts': similar_posts})

def post_share(request, post_id):
# Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    if request.method == 'POST':
# Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
# Form fields passed validation
            cd = form.cleaned_data
# ... send email
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form})