from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required(login_url='login')
def status_view(request):
    return render(request, 'status/status.html')


