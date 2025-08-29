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
    # Fix the embeddings check to avoid the array boolean error
    if (request.user.is_authenticated and 
        hasattr(request.user, 'profile') and 
        request.user.profile.embeddings is not None):
        try:
            blogs = Blog.objects.filter(is_published=True).order_by(L2Distance('embeddings', request.user.profile.embeddings))
        except:
            blogs = Blog.objects.filter(is_published=True).order_by('-created_at')
    else:
        blogs = Blog.objects.filter(is_published=True).order_by('-created_at')

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
        print("POST request received")
        print("POST data:", request.POST)
        
        form = BlogForm(request.POST)
        print("Form is valid:", form.is_valid())
        
        if not form.is_valid():
            print("Form errors:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        else:
            blog = form.save(commit=False)
            blog.author = request.user
            
            # Use the info property from the model
            try:
                blog_info_text = " ".join(blog.info)
                blog.embeddings = generate_embeddings(blog_info_text)
                print("Embeddings generated successfully")
            except Exception as e:
                print(f"Embeddings generation failed: {e}")
                blog.embeddings = None
                
            blog.save()
            print(f"Blog saved with ID: {blog.id}")
            messages.success(request, 'Blog created successfully!')
            
            if blog.is_published:
                return redirect('blog_detail', pk=blog.pk)
            else:
                return redirect('my_blogs')
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
            updated_blog = form.save(commit=False)
            
            # Update embeddings using info property
            try:
                blog_info_text = " ".join(updated_blog.info)
                updated_blog.embeddings = generate_embeddings(blog_info_text)
            except Exception as e:
                print(f"Embeddings update failed: {e}")
                
            updated_blog.save()
            messages.success(request, 'Blog updated successfully!')
            
            if updated_blog.is_published:
                return redirect('blog_detail', pk=blog.pk)
            else:
                return redirect('my_blogs')
        else:
            # Add form errors to messages for debugging
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
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
    blogs = Blog.objects.filter(author=request.user).order_by('-created_at')
    paginator = Paginator(blogs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blogs/my_blogs.html', {'page_obj': page_obj})


