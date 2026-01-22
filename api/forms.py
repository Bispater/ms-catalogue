from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Product, Category, ClientConfiguration


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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Formatear JSON para mejor visualización
        if self.instance and self.instance.metadata:
            import json
            try:
                # Formatear JSON con indentación
                formatted_json = json.dumps(self.instance.metadata, indent=2, ensure_ascii=False)
                self.initial['metadata'] = formatted_json
            except:
                pass
    
    class Meta:
        model = ClientConfiguration
        fields = '__all__'
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color'}),
            'accent_color': forms.TextInput(attrs={'type': 'color'}),
            'metadata': forms.Textarea(attrs={
                'rows': 20,
                'cols': 80,
                'style': 'font-family: monospace; font-size: 12px;',
                'class': 'vLargeTextField'
            }),
        }
