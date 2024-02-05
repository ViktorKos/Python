from django import forms
from .models import Quote, Author


class QuoteForm(forms.ModelForm):
    # Використовуємо звичайне поле CharField для тегів
    tags = forms.CharField(max_length=84, widget=forms.TextInput(attrs={'placeholder': 'Enter tags'}))

    class Meta:
        model = Quote
        fields = ['quote', 'tags']

    def clean_tags(self):
        # Розбиваємо введений рядок тегів на список, використовуючи кому як роздільник
        tags = self.cleaned_data['tags']
        return [tag.strip() for tag in tags.split(',')]


class AuthorForm(forms.ModelForm):
    # Додаємо атрибут placeholder для зручності користувача
    fullname = forms.CharField(max_length=64, required=True, widget=forms.TextInput(attrs={'placeholder': 'Full Name'}))

    class Meta:
        model = Author
        fields = ['fullname']


class AuthorEditForm(forms.ModelForm):
    # Використовуємо Textarea для багаторядкового введення тексту
    born_date = forms.CharField(max_length=64, help_text="Please follow the format: December 25, 2000.",
                                widget=forms.TextInput(attrs={'placeholder': 'December 25, 2000'}))
    born_location = forms.CharField(max_length=256, help_text="Please follow the format: in Florida, USA.",
                                    widget=forms.TextInput(attrs={'placeholder': 'in Florida, USA'}))
    description = forms.Textarea(attrs={'placeholder': 'Enter a brief description...'})

    class Meta:
        model = Author
        fields = ['born_date', 'born_location', 'description']
