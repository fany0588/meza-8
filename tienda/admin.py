from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Categoria, Producto, Pedido, DetallePedido, Resena, Carrito, Favorito

class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'tipo_usuario', 'is_staff')
    list_filter = ('tipo_usuario', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('tipo_usuario', 'telefono', 'calle', 'numero_casa', 'colonia', 
                      'ciudad', 'codigo_postal', 'descripcion_direccion', 'metodo_pago')
        }),
    )

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock', 'destacado', 'fecha_creacion')
    list_filter = ('categoria', 'temporada', 'tipo', 'destacado')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('precio', 'stock', 'destacado')

class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_pedido', 'estado', 'total', 'metodo_pago')
    list_filter = ('estado', 'metodo_pago', 'fecha_pedido')
    search_fields = ('cliente__username', 'codigo_seguimiento')

class ResenaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'producto', 'calificacion', 'fecha')
    list_filter = ('calificacion', 'fecha')
    search_fields = ('cliente__username', 'producto__nombre')

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Categoria)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(DetallePedido)
admin.site.register(Resena, ResenaAdmin)
admin.site.register(Carrito)
admin.site.register(Favorito)