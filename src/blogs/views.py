from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from pgvector.django import L2Distance
from .models import Blog
from .forms import BlogForm
from .embeddings import generate_embeddings

def blog_list(request):
    """Display all published blogs"""
    profile = request.user.profile

    # Checking for similarity using L2Distance in pgvector
    blogs = Blog.objects.order_by(L2Distance('embeddings', profile.embeddings))

    paginator = Paginator(blogs, 10)  # 10 blogs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blogs/blog_list.html', {'page_obj': page_obj})

def blog_detail(request, pk):
    """Display a single blog"""
    blog = get_object_or_404(Blog, pk=pk, is_published=True)
    return render(request, 'blogs/blog_detail.html', {'blog': blog})

@login_required
def blog_create(request):
    """Create a new blog"""
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.embeddings = generate_embeddings(blog.info)
            blog.save()
            messages.success(request, 'Blog created successfully!')
            return redirect('blog_detail', pk=blog.pk)
    else:
        form = BlogForm()
    
    return render(request, 'blogs/blog_form.html', {'form': form, 'title': 'Create Blog'})

@login_required
def blog_update(request, pk):
    """Update an existing blog"""
    blog = get_object_or_404(Blog, pk=pk, author=request.user)
    if request.method == 'POST':
        form = BlogForm(request.POST, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog updated successfully!')
            return redirect('blog_detail', pk=blog.pk)
    else:
        form = BlogForm(instance=blog)
    
    return render(request, 'blogs/blog_form.html', {'form': form, 'title': 'Update Blog', 'blog': blog})

@login_required
def blog_delete(request, pk):
    """Delete a blog"""
    blog = get_object_or_404(Blog, pk=pk, author=request.user)
    
    if request.method == 'POST':
        blog.delete()
        messages.success(request, 'Blog deleted successfully!')
        return redirect('blog_list')
    
    return render(request, 'blogs/blog_confirm_delete.html', {'blog': blog})

@login_required
def my_blogs(request):
    """Display current user's blogs"""
    blogs = Blog.objects.filter(author=request.user)
    paginator = Paginator(blogs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blogs/my_blogs.html', {'page_obj': page_obj})


