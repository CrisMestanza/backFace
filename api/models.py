from django.db import models

class Camaras(models.Model):
    idcamara = models.AutoField(primary_key=True)
    nombrecamara = models.CharField(max_length=100)
    ipcamar = models.CharField(max_length=100)
    activo = models.BooleanField(blank=True, null=True)
    idtipocamara = models.ForeignKey('Tipocamara', models.DO_NOTHING, db_column='idtipocamara', blank=True, null=True)
    estado = models.BooleanField(blank=True, null=True)
    corInicial = models.CharField(max_length=30)
    corFinal = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'camaras'


class Detalleusuariocamara(models.Model):
    iddetalle = models.AutoField(primary_key=True)
    idusuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='idusuario')
    idcamara = models.ForeignKey(Camaras, models.DO_NOTHING, db_column='idcamara')
    fecha = models.DateField()
    hora = models.TimeField()

    class Meta:
        managed = False
        db_table = 'detalleusuariocamara'


class Tipocamara(models.Model):
    idtipocamara = models.AutoField(primary_key=True)
    nombretipocamara = models.CharField(max_length=100)
    estado = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipocamara'


class Tipousuarios(models.Model):
    idtipousuarios = models.AutoField(primary_key=True)
    nombreidtipousuarios = models.CharField(max_length=100)
    estado = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipousuarios'


class Usuarios(models.Model):
    idusuario = models.AutoField(primary_key=True)
    nombreusuario = models.CharField(max_length=100)
    usuario = models.CharField(unique=True, max_length=100)
    dniusuario = models.IntegerField()
    estado = models.BooleanField(blank=True, null=True)
    admin = models.BooleanField(blank=True, null=True)
    contrasena = models.CharField(unique=True, max_length=100)
    class Meta:
        managed = False
        db_table = 'usuarios'



class Detallepersonacamara(models.Model):
    iddetallepc = models.AutoField(db_column='idDetallePC', primary_key=True)  # Field name made lowercase.
    idcamara = models.ForeignKey(Camaras, models.DO_NOTHING, db_column='idcamara')
    idpersona = models.ForeignKey('Personarq', models.DO_NOTHING, db_column='idPersona')  # Field name made lowercase.
    fecha = models.DateField(blank=True, null=True)
    hora = models.TimeField(blank=True, null=True)
    estado = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'detallePersonaCamara'
        
        

class Personarq(models.Model):
    idpersona = models.AutoField(db_column='idPersona', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(max_length=50, blank=True, null=True)
    dni = models.IntegerField(blank=True, null=True)
    estado = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'personaRQ'