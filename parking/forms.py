from django import forms
from .models import VehicleEntry

class VehicleEntryForm(forms.ModelForm):
    """
    Form for recording vehicle entries into the parking area.
    """
    class Meta:
        model = VehicleEntry
        fields = ['plate_number', 'vehicle_type', 'color', 'notes']
        widgets = {
            'plate_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: B 1234 ABC'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Hitam'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Catatan tambahan (opsional)', 'rows': 3}),
        }
