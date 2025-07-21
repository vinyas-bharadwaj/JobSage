from django.shortcuts import render

# Create your views here.
def home_page(request):
    return render(request, 'home/home.html', context={})

def about_page(request):
    return render(request, 'home/about.html', context={})