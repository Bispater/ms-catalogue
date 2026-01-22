from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Product, Category, ClientConfiguration
import json


class PrettyJSONWidget(forms.Textarea):
    """Widget personalizado para mostrar JSON formateado"""
    
    def format_value(self, value):
        """Formatea el valor JSON para mostrarlo bonito"""
        if value is None or value == '':
            return ''
        
        try:
            # Si es string, parsearlo
            if isinstance(value, str):
                obj = json.loads(value)
            else:
                obj = value
            
            # Formatear con indentación
            return json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=False)
        except (ValueError, TypeError):
            return value


class ProductAdminForm(forms.ModelForm):
    """
    Formulario personalizado para el modelo Product en el admin.
    Incluye widgets de CKEditor 5 para los campos de descripción.
    """
    description = forms.CharField(
        widget=CKEditorUploadingWidget(),
        required=False,
        label=_('Descripción completa'),
        help_text=_('Descripción detallada del producto')
    )
    
    short_description = forms.CharField(
        widget=CKEditorUploadingWidget(),
        required=False,
        label=_('Descripción corta'),
        help_text=_('Breve descripción que se mostrará en listados')
    )

    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'categories': FilteredSelectMultiple(
                verbose_name=_('Categorías'),
                is_stacked=False
            )
        }


class MyModelForm(forms.ModelForm):
    """
    Formulario personalizado para el modelo Category en el admin.
    Incluye un campo de descripción con CKEditor 5.
    """
    description = forms.CharField(
        widget=CKEditorUploadingWidget(),
        required=False,
        label=_('Descripción'),
        help_text=_('Descripción de la categoría')
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurarse de que el campo icon_file acepte múltiples tipos de archivo
        self.fields['icon_file'].widget.attrs.update({
            'accept': 'image/*,.svg',
            'class': 'vFileUploadField'
        })

    class Meta:
        model = Category
        fields = '__all__'


class ClientConfigurationForm(forms.ModelForm):
    """
    Formulario personalizado para ClientConfiguration con color picker y JSON editor.
    """
    class Meta:
        model = ClientConfiguration
        fields = '__all__'
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color'}),
            'accent_color': forms.TextInput(attrs={'type': 'color'}),
            'metadata': PrettyJSONWidget(attrs={
                'rows': 25,
                'cols': 100,
                'style': 'font-family: "Courier New", monospace; font-size: 13px; line-height: 1.5;',
                'class': 'vLargeTextField',
                'placeholder': 'JSON configuration...'
            }),
        }
