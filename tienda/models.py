from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def crear_categorias_predeterminadas(sender, **kwargs):
    if sender.name == 'tienda':
        from .models import Categoria
        categorias = [
            'Mujer',
            'Hombre', 
            'Niñas',
            'Niños',
            'Bebés'
        ]
        
        for nombre in categorias:
            Categoria.objects.get_or_create(nombre=nombre)




class Usuario(AbstractUser):
    TIPO_USUARIO = [
        ('admin', 'Administrador'),
        ('cliente', 'Cliente'),
    ]
    
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO, default='cliente')
    telefono = models.CharField(max_length=15, blank=True)
    calle = models.CharField(max_length=100, blank=True)
    numero_casa = models.CharField(max_length=10, blank=True)
    colonia = models.CharField(max_length=100, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    descripcion_direccion = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    TALLAS = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Extra Extra Large'),
    ]
    
    TEMPORADAS = [
        ('primavera', 'Primavera'),
        ('verano', 'Verano'),
        ('otono', 'Otoño'),
        ('invierno', 'Invierno'),
    ]
    
    TIPOS = [
        ('camisa', 'Camisa'),
        ('pantalon', 'Pantalón'),
        ('vestido', 'Vestido'),
        ('falda', 'Falda'),
        ('blusa', 'Blusa'),
        ('chaqueta', 'Chaqueta'),
        ('zapatos', 'Zapatos'),
        ('accesorio', 'Accesorio'),
    ]
    
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    talla = models.CharField(max_length=10, choices=TALLAS)
    color = models.CharField(max_length=50)
    material = models.CharField(max_length=100)
    temporada = models.CharField(max_length=20, choices=TEMPORADAS)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    imagen = models.ImageField(upload_to='productos/')
    destacado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Campos específicos para niños/niñas
    edad_recomendada = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('en_proceso', 'En Proceso'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    METODOS_PAGO = [
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('paypal', 'PayPal'),
        ('transferencia', 'Transferencia Bancaria'),
        ('efectivo', 'Efectivo'),
    ]
    
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)
    direccion_envio = models.TextField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    impuestos = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_seguimiento = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.username}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

class Resena(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    calificacion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    foto_producto = models.ImageField(upload_to='resenas/', blank=True)
    
    def __str__(self):
        return f"Reseña de {self.cliente.username} para {self.producto.nombre}"

class Carrito(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    def subtotal(self):
        return self.cantidad * self.producto.precio

class Favorito(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.cliente.username} - {self.producto.nombre}"