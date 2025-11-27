from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta
from .models import *
from .forms import *

def es_administrador(user):
    return user.is_authenticated and user.tipo_usuario == 'admin'

def index(request):
    if request.user.is_authenticated:
        if request.user.tipo_usuario == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('tienda_home')
    return render(request, 'tienda/index.html')

def login_view(request):
    if request.method == 'POST':
        tipo_usuario = request.POST.get('tipo_usuario')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if tipo_usuario == 'admin' and user.tipo_usuario == 'admin':
                login(request, user)
                return redirect('admin_dashboard')
            elif tipo_usuario == 'cliente' and user.tipo_usuario == 'cliente':
                login(request, user)
                return redirect('tienda_home')
            else:
                messages.error(request, 'Tipo de usuario incorrecto')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'tienda/login.html')

def registro_cliente(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.tipo_usuario = 'cliente'
            user.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido a FashionStyle')
            return redirect('tienda_home')
    else:
        form = RegistroForm()
    return render(request, 'tienda/registro.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
@user_passes_test(es_administrador)
def admin_dashboard(request):
    # Estadísticas
    total_clientes = Usuario.objects.filter(tipo_usuario='cliente').count()
    total_productos = Producto.objects.count()
    total_pedidos = Pedido.objects.count()
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    
    # Ventas del último mes
    fecha_inicio = datetime.now() - timedelta(days=30)
    ventas_mes = Pedido.objects.filter(
        fecha_pedido__gte=fecha_inicio,
        estado__in=['confirmado', 'en_proceso', 'enviado', 'entregado']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Productos más vendidos
    productos_mas_vendidos = DetallePedido.objects.values(
        'producto__nombre'
    ).annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')[:5]
    
    context = {
        'total_clientes': total_clientes,
        'total_productos': total_productos,
        'total_pedidos': total_pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'ventas_mes': ventas_mes,
        'productos_mas_vendidos': productos_mas_vendidos,
    }
    return render(request, 'tienda/admin_dashboard.html', context)

# Vistas de gestión (CRUD)
@login_required
@user_passes_test(es_administrador)
def gestion_clientes(request):
    clientes = Usuario.objects.filter(tipo_usuario='cliente')
    return render(request, 'tienda/gestion_clientes.html', {'clientes': clientes})

@login_required
@user_passes_test(es_administrador)
def gestion_productos(request):
    productos = Producto.objects.all()
    categorias = Categoria.objects.all()
    return render(request, 'tienda/gestion_productos.html', {
        'productos': productos,
        'categorias': categorias
    })

@login_required
@user_passes_test(es_administrador)
def gestion_pedidos(request):
    pedidos = Pedido.objects.all().order_by('-fecha_pedido')
    return render(request, 'tienda/gestion_pedidos.html', {'pedidos': pedidos})

@login_required
@user_passes_test(es_administrador)
def gestion_resenas(request):
    resenas = Resena.objects.all().order_by('-fecha')
    return render(request, 'tienda/gestion_resenas.html', {'resenas': resenas})

# Vistas CRUD para cada modelo
@login_required
@user_passes_test(es_administrador)
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente')
            return redirect('gestion_productos')
    else:
        form = ProductoForm()
    return render(request, 'tienda/crear_producto.html', {'form': form})

@login_required
@user_passes_test(es_administrador)
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente')
            return redirect('gestion_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'tienda/editar_producto.html', {'form': form, 'producto': producto})

@login_required
@user_passes_test(es_administrador)
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente')
        return redirect('gestion_productos')
    return render(request, 'tienda/eliminar_producto.html', {'producto': producto})

# Vistas para la tienda
def tienda_home(request):
    productos_destacados = Producto.objects.filter(destacado=True)[:8]
    productos_nuevos = Producto.objects.all().order_by('-fecha_creacion')[:8]
    
    context = {
        'productos_destacados': productos_destacados,
        'productos_nuevos': productos_nuevos,
    }
    return render(request, 'tienda/tienda_home.html', context)

def productos_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    productos = Producto.objects.filter(categoria=categoria)
    return render(request, 'tienda/productos_categoria.html', {
        'categoria': categoria,
        'productos': productos
    })

def todos_productos(request):
    productos = Producto.objects.all().order_by('-fecha_creacion')
    categorias = Categoria.objects.all()
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if precio_min:
        productos = productos.filter(precio__gte=precio_min)
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)
    
    return render(request, 'tienda/todos_productos.html', {
        'productos': productos,
        'categorias': categorias
    })

def buscar_productos(request):
    query = request.GET.get('q', '')
    if query:
        productos = Producto.objects.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__nombre__icontains=query)
        )
    else:
        productos = Producto.objects.none()
    
    return render(request, 'tienda/resultados_busqueda.html', {
        'productos': productos,
        'query': query
    })

def producto_detalle(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    resenas = Resena.objects.filter(producto=producto)
    
    # Productos relacionados
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria
    ).exclude(pk=producto_id)[:4]
    
    context = {
        'producto': producto,
        'resenas': resenas,
        'productos_relacionados': productos_relacionados,
    }
    return render(request, 'tienda/producto_detalle.html', context)

@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    carrito_item, created = Carrito.objects.get_or_create(
        cliente=request.user,
        producto=producto,
        defaults={'cantidad': 1}
    )
    
    if not created:
        carrito_item.cantidad += 1
        carrito_item.save()
    
    messages.success(request, f'"{producto.nombre}" agregado al carrito')
    return redirect('ver_carrito')

@login_required
def ver_carrito(request):
    carrito_items = Carrito.objects.filter(cliente=request.user)
    total = sum(item.subtotal() for item in carrito_items)
    
    context = {
        'carrito_items': carrito_items,
        'total': total,
    }
    return render(request, 'tienda/carrito.html', context)

@login_required
def actualizar_carrito(request, item_id):
    carrito_item = get_object_or_404(Carrito, pk=item_id, cliente=request.user)
    
    if request.method == 'POST':
        nueva_cantidad = int(request.POST.get('cantidad', 1))
        if nueva_cantidad > 0:
            carrito_item.cantidad = nueva_cantidad
            carrito_item.save()
            messages.success(request, 'Carrito actualizado')
        else:
            carrito_item.delete()
            messages.success(request, 'Producto eliminado del carrito')
    
    return redirect('ver_carrito')

@login_required
def eliminar_del_carrito(request, item_id):
    carrito_item = get_object_or_404(Carrito, pk=item_id, cliente=request.user)
    carrito_item.delete()
    messages.success(request, 'Producto eliminado del carrito')
    return redirect('ver_carrito')

@login_required
def checkout(request):
    carrito_items = Carrito.objects.filter(cliente=request.user)
    
    if not carrito_items:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('tienda_home')
    
    total = sum(item.subtotal() for item in carrito_items)
    
    # CORRECCIÓN: Usar Decimal para cálculos
    from decimal import Decimal
    impuestos = total * Decimal('0.16')  # 16% de IVA
    total_final = total + impuestos
    
    if request.method == 'POST':
        # Procesar el pedido
        pedido = Pedido.objects.create(
            cliente=request.user,
            metodo_pago=request.POST.get('metodo_pago'),
            direccion_envio=request.POST.get('direccion_envio'),
            subtotal=total,
            impuestos=impuestos,
            total=total_final,
            codigo_seguimiento=f"FS{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        
        # Crear detalles del pedido y actualizar stock
        for item in carrito_items:
            DetallePedido.objects.create(
                pedido=pedido,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio,
                subtotal=item.subtotal()
            )
            
            # Actualizar stock
            item.producto.stock -= item.cantidad
            item.producto.save()
        
        # Vaciar carrito
        carrito_items.delete()
        
        messages.success(request, f'¡Pedido realizado exitosamente! Tu número de seguimiento es: {pedido.codigo_seguimiento}')
        return redirect('mis_pedidos')
    
    context = {
        'carrito_items': carrito_items,
        'total': total,
        'impuestos': impuestos,
        'total_final': total_final,
    }
    return render(request, 'tienda/checkout.html', context)
@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(cliente=request.user).order_by('-fecha_pedido')
    return render(request, 'tienda/mis_pedidos.html', {'pedidos': pedidos})

@login_required
def cancelar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id, cliente=request.user)
    
    if pedido.estado in ['pendiente', 'confirmado']:
        pedido.estado = 'cancelado'
        pedido.save()
        
        # Restaurar stock
        detalles = DetallePedido.objects.filter(pedido=pedido)
        for detalle in detalles:
            producto = detalle.producto
            producto.stock += detalle.cantidad
            producto.save()
        
        messages.success(request, 'Pedido cancelado exitosamente')
    else:
        messages.error(request, 'No se puede cancelar el pedido en su estado actual')
    
    return redirect('mis_pedidos')

@login_required
def agregar_favorito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    favorito, created = Favorito.objects.get_or_create(
        cliente=request.user,
        producto=producto
    )
    
    if created:
        messages.success(request, f'"{producto.nombre}" agregado a favoritos')
    else:
        messages.info(request, f'"{producto.nombre}" ya está en tus favoritos')
    
    return redirect('mis_favoritos')

@login_required
def mis_favoritos(request):
    favoritos = Favorito.objects.filter(cliente=request.user)
    return render(request, 'tienda/mis_favoritos.html', {'favoritos': favoritos})

@login_required
def eliminar_favorito(request, favorito_id):
    favorito = get_object_or_404(Favorito, pk=favorito_id, cliente=request.user)
    favorito.delete()
    messages.success(request, 'Producto eliminado de favoritos')
    return redirect('mis_favoritos')


@login_required
def crear_resena(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    
    if request.method == 'POST':
        form = ResenaForm(request.POST, request.FILES)
        if form.is_valid():
            resena = form.save(commit=False)
            resena.cliente = request.user
            resena.producto = producto
            resena.save()
            messages.success(request, 'Reseña publicada exitosamente')
            return redirect('producto_detalle', producto_id=producto_id)
    else:
        form = ResenaForm()
    
    return render(request, 'tienda/crear_resena.html', {
        'form': form,
        'producto': producto
    })

@login_required
def editar_resena(request, resena_id):
    resena = get_object_or_404(Resena, pk=resena_id, cliente=request.user)
    
    if request.method == 'POST':
        form = ResenaForm(request.POST, request.FILES, instance=resena)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reseña actualizada exitosamente')
            return redirect('producto_detalle', producto_id=resena.producto.id)
    else:
        form = ResenaForm(instance=resena)
    
    return render(request, 'tienda/editar_resena.html', {
        'form': form,
        'resena': resena
    })

@login_required
def eliminar_resena(request, resena_id):
    resena = get_object_or_404(Resena, pk=resena_id, cliente=request.user)
    producto_id = resena.producto.id
    resena.delete()
    messages.success(request, 'Reseña eliminada exitosamente')
    return redirect('producto_detalle', producto_id=producto_id)

# Vistas CRUD para clientes
@login_required
@user_passes_test(es_administrador)
def editar_cliente(request, pk):
    cliente = get_object_or_404(Usuario, pk=pk, tipo_usuario='cliente')
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado exitosamente')
            return redirect('gestion_clientes')
    else:
        form = PerfilForm(instance=cliente)
    return render(request, 'tienda/editar_cliente.html', {'form': form, 'cliente': cliente})

@login_required
@user_passes_test(es_administrador)
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Usuario, pk=pk, tipo_usuario='cliente')
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado exitosamente')
        return redirect('gestion_clientes')
    return render(request, 'tienda/eliminar_cliente.html', {'cliente': cliente})

# Vistas CRUD para pedidos
@login_required
@user_passes_test(es_administrador)
def ver_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    detalles = DetallePedido.objects.filter(pedido=pedido)
    return render(request, 'tienda/ver_pedido.html', {'pedido': pedido, 'detalles': detalles})

@login_required
@user_passes_test(es_administrador)
def editar_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        # Lógica para editar pedido
        pass
    return render(request, 'tienda/editar_pedido.html', {'pedido': pedido})

# Vistas para crear y editar productos
@login_required
@user_passes_test(es_administrador)
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente')
            return redirect('gestion_productos')
    else:
        form = ProductoForm()
    return render(request, 'tienda/crear_producto.html', {'form': form})

@login_required
@user_passes_test(es_administrador)
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente')
            return redirect('gestion_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'tienda/editar_producto.html', {'form': form, 'producto': producto})

@login_required
@user_passes_test(es_administrador)
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente')
        return redirect('gestion_productos')
    return render(request, 'tienda/eliminar_producto.html', {'producto': producto})

@login_required
def perfil_usuario(request):
    print("=== DEBUG PERFIL ===")
    print(f"Usuario: {request.user.username}")
    print(f"Datos del usuario: {request.user.first_name} {request.user.last_name}")
    
    if request.method == 'POST':
        print("Método POST recibido")
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            print("Formulario válido, guardando...")
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente')
            return redirect('perfil_usuario')
        else:
            print("Formulario inválido:", form.errors)
    else:
        print("Método GET - Mostrando formulario")
        form = PerfilForm(instance=request.user)
        print("Datos en el formulario:")
        for field in form:
            print(f"{field.name}: '{field.value()}'")
    
    return render(request, 'tienda/perfil.html', {'form': form})