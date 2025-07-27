from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Blog, Category
from .forms import BlogForm
import json

def blog_list(request):
    """Display all published blogs with search and filtering"""
    blogs = Blog.objects.filter(status='published').select_related('author', 'category')
    categories = Category.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        blogs = blogs.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    # Category filtering
    category_slug = request.GET.get('category', '')
    if category_slug:
        blogs = blogs.filter(category__slug=category_slug)
    
    # Featured blogs
    featured_blogs = blogs.filter(is_featured=True)[:3]
    
    # Pagination
    paginator = Paginator(blogs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'blogs': page_obj,
        'categories': categories,
        'featured_blogs': featured_blogs,
        'search_query': search_query,
        'selected_category': category_slug,
    }
    return render(request, 'blog/blog_list.html', context)

def blog_detail(request, slug):
    """Display individual blog post"""
    blog = get_object_or_404(Blog, slug=slug, status='published')
    
    # Increment view count
    blog.views_count += 1
    blog.save(update_fields=['views_count'])
    
    # Related posts
    related_blogs = Blog.objects.filter(
        category=blog.category, 
        status='published'
    ).exclude(id=blog.id)[:3]
    
    context = {
        'blog': blog,
        'related_blogs': related_blogs,
    }
    return render(request, 'blog/blog_detail.html', context)

@login_required
def blog_create(request):
    """Create new blog post"""
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            messages.success(request, 'Blog post created successfully!')
            return redirect('blog:detail', slug=blog.slug)
    else:
        form = BlogForm()
    
    context = {
        'form': form,
        'title': 'Create New Blog Post',
        'button_text': 'Create Post',
    }
    return render(request, 'blog/blog_form.html', context)

@login_required
def blog_edit(request, slug):
    """Edit existing blog post"""
    blog = get_object_or_404(Blog, slug=slug, author=request.user)
    
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            blog = form.save()
            messages.success(request, 'Blog post updated successfully!')
            return redirect('blog:detail', slug=blog.slug)
    else:
        form = BlogForm(instance=blog)
    
    context = {
        'form': form,
        'blog': blog,
        'title': 'Edit Blog Post',
        'button_text': 'Update Post',
    }
    return render(request, 'blog/blog_form.html', context)

@login_required
def blog_delete(request, slug):
    """Delete blog post"""
    blog = get_object_or_404(Blog, slug=slug, author=request.user)
    
    if request.method == 'POST':
        blog.delete()
        messages.success(request, 'Blog post deleted successfully!')
        return redirect('blog:list')
    
    context = {'blog': blog}
    return render(request, 'blog/blog_confirm_delete.html', context)

@login_required
def my_blogs(request):
    """Display user's own blog posts"""
    blogs = Blog.objects.filter(author=request.user).select_related('category')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        blogs = blogs.filter(status=status_filter)
    
    paginator = Paginator(blogs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'blogs': page_obj,
        'status_filter': status_filter,
    }
    return render(request, 'blog/my_blogs.html', context)

@csrf_exempt
@login_required
def upload_image(request):
    """Handle image uploads for rich text editor"""
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        # You can add validation here
        # Save the file and return the URL
        # This is a simplified version - implement proper file handling
        return JsonResponse({
            'success': True,
            'file': {
                'url': uploaded_file.url if hasattr(uploaded_file, 'url') else '#'
            }
        })
    return JsonResponse({'success': False})