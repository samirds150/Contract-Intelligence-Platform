from django import forms


class UploadForm(forms.Form):
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=True)


class AskForm(forms.Form):
    question = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), max_length=500)
