from django.shortcuts import (
    get_object_or_404,
    render, redirect
)
from django.http import HttpResponse, HttpResponseNotFound
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Quote
from .forms import QuoteForm

def index(request):
    quote = Quote.weighted_random()
    if quote:
        quote.increase_views()
    return render(request, 'quoter/index.html', {'quote': quote})

def top_num_view(request, num_id):
    quotes = Quote.objects.order_by('-views_cnt')[:num_id]
    return render(request, 'quoter/top.html', {
        'quotes': quotes,
        'num_id': num_id
    })

def top_10_view(request):
    uri = reverse('top', args=(10, ))
    return redirect(uri , permanent=True)

def page_not_found(request, exception):
    return HttpResponseNotFound("Page not found")

def add_new(request):
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = QuoteForm()

    return render(request, 'quoter/add.html', {'form': form})

@require_POST
def like_quote(request, quote_id):
    quote = get_object_or_404(Quote, pk=quote_id)
    quote.like()
    return redirect('home')

@require_POST
def dislike_quote(request, quote_id):
    quote = get_object_or_404(Quote, pk=quote_id)
    quote.dislike()
    return redirect('home')