from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Producto, Resena

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    telefono = forms.CharField(max_length=15, required=True)
    calle = forms.CharField(max_length=100, required=True)
    numero_casa = forms.CharField(max_length=10, required=True)
    colonia = forms.CharField(max_length=100, required=True)
    ciudad = forms.CharField(max_length=100, required=True)
    codigo_postal = forms.CharField(max_length=10, required=True)
    descripcion_direccion = forms.CharField(widget=forms.Textarea, required=False)
    
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2',
                 'telefono', 'calle', 'numero_casa', 'colonia', 'ciudad', 
                 'codigo_postal', 'descripcion_direccion')

class PerfilForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    email = forms.EmailField(required=True, label='Correo electrónico')
    telefono = forms.CharField(max_length=15, required=True, label='Teléfono')
    calle = forms.CharField(max_length=100, required=True, label='Calle')
    numero_casa = forms.CharField(max_length=10, required=True, label='Número')
    colonia = forms.CharField(max_length=100, required=True, label='Colonia')
    ciudad = forms.CharField(max_length=100, required=True, label='Ciudad')
    codigo_postal = forms.CharField(max_length=10, required=True, label='Código Postal')
    descripcion_direccion = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}), 
        required=False, 
        label='Referencias'
    )
    metodo_pago = forms.CharField(max_length=50, required=False, label='Método de Pago Preferido')
    
    class Meta:
        model = Usuario
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'telefono',
            'calle',
            'numero_casa', 
            'colonia',
            'ciudad',
            'codigo_postal',
            'descripcion_direccion',
            'metodo_pago'
        ]

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }

class ResenaForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ('calificacion', 'comentario', 'foto_producto')
        widgets = {
            'calificacion': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comentario': forms.Textarea(attrs={'rows': 4}),
        }