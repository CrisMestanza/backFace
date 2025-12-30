# api/urls.py
from django.urls import path
from .views import camaras
from .views import usuarios
from .views import viewsCamaras
from .views import subProcess
from .views import imagenes
from .views import personasRq
from .views import mapa
from .views import datosMapa
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #Mostrar camara
    path('camera_feed/<str:camera_id>/<str:nombre>/', viewsCamaras.camera_feed, name='camaras-view'),  # Para obtener una cámara específica por ID
    path('deseleccionar_camara/<int:camera_id>/', viewsCamaras.deseleccionar_camara, name='deseleccionar_camara'),

    #Camaras 
    path('camaras/', camaras.get_camaras, name='camaras-list'), 
    path('getCamarasSinEstado/', camaras.getCamarasSinEstado, name='getCamarasSinEstado'), 
    path('camarasPost/', camaras.create_camara, name='camaras-create'),  
    path('camarasPut/<int:pk>/', camaras.update_camara, name='camaras-update'),  
    path('camarasDelete/<int:pk>/', camaras.update_camara_estado, name='camaras-delete'),  
    path('camara/<int:pk>/', camaras.getCamaraPk, name='camara'), 
    path('camaraSearch/<str:data>/', camaras.searchCamaras, name='camaraSearch'), 
    
    #Tipo camara
    path('tipoCamara/', camaras.tipoCamara, name='tipoCamara-list'),  # Para obtener todas las cámaras
    
    #Usuarios
    path('usuarios/', usuarios.getUsuarios, name='usuarios-list'),  # Para obtener todas las cámaras
    path('usuariosPost/', usuarios.createUsuario, name='usuarios-create'),  # Para obtener todas las cámaras
    path('usuariosPut/<int:pk>/', usuarios.updateUsuario, name='usuarios-update'),  # Para crear una nueva cámara
    path('usuariosDelete/<int:pk>/', usuarios.updateEstadoUsuario, name='usuarios-delete'),  # Para crear una nueva cámara
    path('usuario/<int:pk>/', usuarios.getUsuarioPk, name='camara'), 
    path('usuariosLogueado/', usuarios.logueadoUsuario, name='usuarios-logueado'),  # Para obtener todas las cámaras
    
    #Login
    path('usuarioLogin/', usuarios.loginUsuario, name='usuarios-login'),  # Para obtener todas las cámaras
    
    #Gráficos 
    path('usuarioActivo/', camaras.usuarios_mas_activos, name='usuarios-activo'),  # Para obtener todas las cámaras
    path('camarUsada/', camaras.camara_mas_usada, name='camara-Usada'),  # Para obtener todas las cámaras
    path('horaPico/', camaras.horas_pico_camaras, name='hora-Pico'),  # Para obtener todas las cámaras
    path('horaPico/', camaras.horas_pico_camaras, name='hora-Pico'),  # Para obtener todas las cámaras

    #Extraer embedding de las  imagenes
    path('extraerEmbdding/', subProcess.extraer_placas, name='extraerEmbdding'),  # Para obtener el embedding de las personas 
    
    #Ver imágenes
    path('verImagen/', imagenes.imagen, name='verImagen'),  # Para obtener todas las cámaras
    
    #Personas con Rq
    path('extraerPersonas/', personasRq.extractPersonaRq, name='extractPersonaRq'),  # Para obtener todas las cámaras
    path('getPersonasRq/', personasRq.getPersonasRq, name='getPersonasRq'),  # Para obtener todas las cámaras
    path('getPersonasRqPk/<int:pk>', personasRq.getPersonasRqPk, name='getPersonasRqPk'),  # Para obtener todas las cámaras
    #Mapa
    path('getListSerenos/', mapa.getListSerenos, name='getListSerenos'),  # Para obtener todas las cámaras
    path('getBanda/', mapa.getBanda, name='getBanda'),  # Para obtener todas las cámaras
    path('getTarapoto/', mapa.getTarapoto, name='getTarapoto'),  # Para obtener todas las cámaras
    path('getMorales/', mapa.getMorales, name='getMorales'),  # Para obtener todas las cámaras
    path('getMapa/<int:z>/<int:x>/<int:y>.png', mapa.getMapa, name='getMapa'),
    # Subir nuevas personas 
    path("upload-zip/", subProcess.upload_zip, name="upload-zip"),

    # Datos para mapa
    path('datosMapa/', datosMapa.datosForMapa, name='datosMapa'),  # Para obtener todas las cámaras
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)