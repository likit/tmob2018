from django.shortcuts import render

# Create your views here.
def res_list(request):
    search_term = request.GET.get('q')
    return render(request, template_name='analytics/res_list.html',
            context={'search_term': search_term})
