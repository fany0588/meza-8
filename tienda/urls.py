from django.urls import path
from . import views

urlpatterns = [
    # Páginas principales
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_cliente, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    
    path('administrador/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('administrador/clientes/', views.gestion_clientes, name='gestion_clientes'),
    path('administrador/productos/', views.gestion_productos, name='gestion_productos'),
    path('administrador/pedidos/', views.gestion_pedidos, name='gestion_pedidos'),
    path('administrador/resenas/', views.gestion_resenas, name='gestion_resenas'),
    
    
    # CRUD Productos
    path('admin/productos/crear/', views.crear_producto, name='crear_producto'),
    path('admin/productos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('admin/productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    
    # Tienda
    path('tienda/', views.tienda_home, name='tienda_home'),
    path('categoria/<int:categoria_id>/', views.productos_por_categoria, name='productos_categoria'),
    path('productos/', views.todos_productos, name='todos_productos'),
    path('buscar/', views.buscar_productos, name='buscar_productos'),
    path('producto/<int:producto_id>/', views.producto_detalle, name='producto_detalle'),
    
    # Carrito y compras
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Usuario
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('cancelar-pedido/<int:pedido_id>/', views.cancelar_pedido, name='cancelar_pedido'),
    path('mis-favoritos/', views.mis_favoritos, name='mis_favoritos'),
    path('favoritos/agregar/<int:producto_id>/', views.agregar_favorito, name='agregar_favorito'),
    path('favoritos/eliminar/<int:favorito_id>/', views.eliminar_favorito, name='eliminar_favorito'),
    
    # Reseñas
    path('resena/crear/<int:producto_id>/', views.crear_resena, name='crear_resena'),
    path('resena/editar/<int:resena_id>/', views.editar_resena, name='editar_resena'),
    path('resena/eliminar/<int:resena_id>/', views.eliminar_resena, name='eliminar_resena'),
]