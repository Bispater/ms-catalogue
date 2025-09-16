from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Product, Category


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
