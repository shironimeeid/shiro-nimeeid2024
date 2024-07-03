# Example in your views.py
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render(request, 'index2.html')
