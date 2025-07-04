from rest_framework import serializers
from .models import Camaras
from .models import Tipocamara
from .models import Usuarios
from .models import Detalleusuariocamara
from .models import Personarq
from .models import Detallepersonacamara

# Camaras
class TipocamaraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipocamara
        fields = '__all__'

class CamarasSerializer(serializers.ModelSerializer):
    tipoCamara = TipocamaraSerializer(source='idtipocamara')
    class Meta:
        model = Camaras
        fields = '__all__'
        
class CamarasAgregar(serializers.ModelSerializer):
    class Meta:
        model = Camaras
        fields = '__all__'

class CamarasUpdate(serializers.ModelSerializer):
    class Meta:
        model = Camaras
        fields = '__all__'

# Usuarios
class UsuariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = '__all__'
        
class usuarioLogin(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = '__all__'
        
class UsuarioLogeado(serializers.ModelSerializer):
    class Meta:
        model = Detalleusuariocamara
        fields = '__all__'
        
class PersonarqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personarq
        fields = '__all__'
        
class DetallepersonacamaraSerializer(serializers.ModelSerializer):
    camaras = CamarasSerializer(source='idcamara', read_only=True)
    class Meta:
        model = Detallepersonacamara
        fields = '__all__'