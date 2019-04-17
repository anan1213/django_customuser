"""
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.views import generic
from .models import Category, Url
from .forms import UrlCreateForm, CategoryCreateForm
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.contrib import messages

class CategoryIndexView(generic.ListView):
    model = Category
    template_name = 'share/category_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = SubClass.objects.all()
        return context

class UrlIndexView(generic.ListView):
    model = Url
    template_name = 'share/url_list.html'


    def get_queryset(self):
        queryset = super().get_queryset()
        detail = get_object_or_404(Category, category=self.kwargs['get_category'])
        queryset = queryset.filter(category=detail)

        return queryset

    def get_context_data(self):
        context = super().get_context_data()
        context['title_name'] = get_object_or_404(Category, category=self.kwargs['category'])
        return context

class UrlCreateView(generic.CreateView):
    model = Url
    template_name = 'share/url_create_form.html'
    success_url = reverse_lazy('share:index')
    form_class = UrlCreateForm


class CategoryCreateView(generic.CreateView):
    model = Category
    template_name = 'share/category_create_form.html'
    success_url = reverse_lazy('share:index')
    form_class = CategoryCreateForm

'''
class DeleteViewSubclass(generic.DeleteView):
    model = SubClass
    templete_name = 'url/delete_category_'
'''

@require_POST
def Urldelete(request):
    delete_id = request.POST['delete_id']
    if delete_id:
        Url.objects.filter(id=delete_id).delete()
    return redirect('share:index')



def Categorydelete(request):
    delete_id = request.POST['delete_id']
    if delete_id:
        subclass = SubClass.objects.get(id=delete_id)
        url_exit = Url.objects.filter(subclass=subclass)
        if url_exit:
            def form_invalid(self, form):
                messages.error(self.request, 'ファイルが空じゃありません')
                return super().form_invalid(form)
        else:
            SubClass.objects.filter(id=delete_id).delete()
    return redirect('share:index')


class IndexView(generic.TemplateView):
    templete_name = 'share/index.html'

"""
