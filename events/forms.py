"""
Forms for Events App
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import Event


class MultipleFileInput(forms.FileInput):
    """Custom widget to handle multiple file uploads"""
    def __init__(self, attrs=None):
        super().__init__(attrs)
        if attrs is None:
            attrs = {}
        attrs['multiple'] = True
        self.attrs = attrs

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return files.get(name)


class MultipleFileField(forms.FileField):
    """Custom field to handle multiple file uploads"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class EventForm(forms.ModelForm):
    """
    Form for creating and editing events
    """
    class Meta:
        model = Event
        fields = ['name', 'description', 'event_date', 'location', 'cover_image', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event Name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Event Description',
                'rows': 4
            }),
            'event_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event Location'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class BulkPhotoUploadForm(forms.Form):
    """
    Form for bulk photo upload
    """
    photos = MultipleFileField(
        required=True,
        help_text='Select multiple photos to upload (JPEG, PNG, WebP)'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['photos'].widget.attrs.update({
            'accept': 'image/*',
            'class': 'form-control'
        })


class SelfieUploadForm(forms.Form):
    """
    Form for user selfie upload for face matching
    """
    selfie = forms.ImageField(
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'class': 'form-control',
            'id': 'selfie-upload'
        }),
        required=True,
        help_text='Upload a clear photo of your face'
    )
    
    tolerance = forms.FloatField(
        initial=0.6,
        min_value=0.3,
        max_value=0.8,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.05',
            'id': 'tolerance-slider'
        }),
        required=False,
        help_text='Matching sensitivity (lower = stricter matching)'
    )
