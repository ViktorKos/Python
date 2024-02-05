from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views import View
from django.db.models import Count  # Додано імпорт Count

from .forms import QuoteForm, AuthorForm, AuthorEditForm
from .models import Author, Quote, Tag


def main(request, page=1):
    quotes = get_list_or_404(Quote.objects.select_related('author', 'user').all())

    elem_per_page = 10
    paginator = Paginator(quotes, elem_per_page)
    quotes_on_page = paginator.page(page)

    # Додано логіку для отримання топ-10 тегів
    top_tags = Tag.objects.annotate(num_quotes=Count('quote')).order_by('-num_quotes')[:10]

    return render(request, "quotes/index.html", context={"quotes": quotes_on_page, "top_tags": top_tags})


def author_detail(request, author_id):
    author = get_object_or_404(Author, id=author_id)
    return render(request, "quotes/author_detail.html", context={"author": author})


@login_required
def add_quote(request):
    if request.method == 'POST':
        quote_form = QuoteForm(request.POST)
        author_form = AuthorForm(request.POST)

        if quote_form.is_valid():
            author_name = request.POST.get('fullname')
            author, created = Author.objects.get_or_create(fullname=author_name, defaults={'user': request.user})

            quote = quote_form.save(commit=False)
            quote.user = request.user
            quote.author = author
            quote.save()

            tags = quote_form.cleaned_data['tags']
            tag_objects = [Tag.objects.get_or_create(name=tag.strip())[0] for tag in tags]
            quote.tags.set(tag_objects)

            return redirect('quotes:root')
    else:
        quote_form = QuoteForm()
        author_form = AuthorForm()

    return render(request, 'quotes/add_quote.html', {'quote_form': quote_form, 'author_form': author_form})


@login_required
def edit_author(request, author_id):
    author = get_object_or_404(Author, id=author_id)

    # Додавання перевірки, чи існує author.user перед порівнянням id
    if author.user and request.user.id != author.user.id:
        return redirect('quotes:root')

    if request.method == 'POST':
        form = AuthorEditForm(request.POST, instance=author)
        if form.is_valid():
            form.save()
            return redirect('quotes:author_detail', author_id=author_id)
    else:
        form = AuthorEditForm(instance=author)

    return render(request, 'quotes/edit_author.html', {'form': form, 'author': author})


@login_required
def delete_quote(request, quote_id):
    if request.method == 'POST':
        quote = get_object_or_404(Quote, id=quote_id)

        if quote.user == request.user:
            author = quote.author
            quote.delete()

            if Quote.objects.filter(author=author).count() == 0:
                author.delete()

            return redirect('quotes:root')
        else:
            return JsonResponse({'message': 'Your access was not authorized or Quote does not exist.'}, status=401)
    else:
        return HttpResponseNotAllowed(['POST'])


class TagQuotesView(View):
    template_name = 'quotes/tag_quotes.html'
    quotes_per_page = 10

    def get(self, request, *args, **kwargs):
        tag_name = kwargs['tag_name']
        tag = get_object_or_404(Tag, name=tag_name)
        quotes_with_tag = get_list_or_404(Quote.objects.filter(tags=tag))

        paginator = Paginator(quotes_with_tag, self.quotes_per_page)
        page = request.GET.get('page')

        try:
            quotes_per_page = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            quotes_per_page = paginator.page(1)

        context = {
            'tag_name': tag_name,
            'quotes_with_tag': quotes_per_page,
        }

        return render(request, self.template_name, context)
