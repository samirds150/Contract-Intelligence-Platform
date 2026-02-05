from django import forms


class UploadForm(forms.Form):
    file = forms.FileField(required=True, help_text='Upload a text file (.txt)')


class AskForm(forms.Form):
    question = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), max_length=500)
