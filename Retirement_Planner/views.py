from django.http import HttpResponseRedirect

def HomeView(request):
    return HttpResponseRedirect('/Retirement_Dashboard/Dashboard')