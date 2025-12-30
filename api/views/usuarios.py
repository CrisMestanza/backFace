# api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Usuarios
from ..serializers import UsuariosSerializer
from ..serializers import usuarioLogin
from ..serializers import UsuarioLogeado
#Obtener 
@api_view(['GET'])
def getUsuarios(request):
    usuarios = Usuarios.objects.filter(estado=True)
    serializer = UsuariosSerializer(usuarios, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
#Agregar
@api_view(['POST'])
def createUsuario(request):
    print( request.data)
    serializer = UsuariosSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#Actualizar
@api_view(['PUT'])
def updateUsuario(request, pk):
    usuario = Usuarios.objects.get(idusuario=pk)
    serializer = UsuariosSerializer(usuario,data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#Eliminar
@api_view(['PUT'])
def updateEstadoUsuario(request, pk):
    usuario = Usuarios.objects.get(idusuario=pk)
    data = {"estado":"False"}
    serializer = UsuariosSerializer(usuario, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#Un usuario por id
@api_view(['GET'])
def getUsuarioPk(request, pk):
    try:
        usuario = Usuarios.objects.get(idusuario=pk, estado=True)
        serializer = UsuariosSerializer(usuario)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except usuario.DoesNotExist:
        return Response({"errwor": "Camara not found"}, status=status.HTTP_404_NOT_FOUND)

#Para login
@api_view(['POST'])
def loginUsuario(request):
    try:
        usuario = Usuarios.objects.get(
            usuario=request.data['usuario'],
            contrasena=request.data['contrasena'],
            estado=True
        )
        serializer = usuarioLogin(usuario)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Usuarios.DoesNotExist:
        # Si no se encuentra el usuario
        return Response({"error": "Usuario o contraseña incorrectos"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def logueadoUsuario(request):
    try: 
        usuario = UsuarioLogeado(data = request.data)
        if usuario.is_valid():
            usuario.save()
            return Response(usuario.data, status=status.HTTP_201_CREATED)
        return Response(usuario.errors, status=status.HTTP_400_BAD_REQUEST)
    except Usuarios.DoesNotExist:
        return Response({"error": "No se puedo registrar"}, status=status.HTTP_404_NOT_FOUND)
        