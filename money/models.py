# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models, connection

from money.reusing.currency import Currency


class Annualtargets(models.Model):
    year = models.IntegerField(primary_key=True)
    percentage = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'annualtargets'


class Banks(models.Model):
    name = models.TextField()
    active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'banks'
        
    def __str__(self):
        return self.name

    def balance(self):
        with connection.cursor() as cursor:
            
            cursor.execute("SELECT accounts_balance(now(), 'EUR')")#, [self.baz])
            row = cursor.fetchone()
            return Currency(row[0], "EUR")

class Conceptos(models.Model):
    id_conceptos = models.AutoField(primary_key=True)
    concepto = models.TextField(blank=True, null=True)
    id_tiposoperaciones = models.IntegerField(blank=True, null=True)
    editable = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'conceptos'


class Cuentas(models.Model):
    id_cuentas = models.AutoField(primary_key=True)
    cuenta = models.TextField(blank=True, null=True)
    banks = models.ForeignKey(Banks, models.DO_NOTHING, blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)
    numerocuenta = models.CharField(max_length=24, blank=True, null=True)
    currency = models.TextField()

    class Meta:
        managed = False
        db_table = 'cuentas'


class Dividends(models.Model):
    id_dividends = models.AutoField(primary_key=True)
    id_inversiones = models.ForeignKey('Inversiones', models.DO_NOTHING, db_column='id_inversiones')
    bruto = models.DecimalField(max_digits=100, decimal_places=2)
    retencion = models.DecimalField(max_digits=100, decimal_places=2)
    neto = models.DecimalField(max_digits=100, decimal_places=2, blank=True, null=True)
    valorxaccion = models.DecimalField(max_digits=100, decimal_places=6, blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    id_opercuentas = models.IntegerField(blank=True, null=True)
    comision = models.DecimalField(max_digits=100, decimal_places=2, blank=True, null=True)
    id_conceptos = models.ForeignKey(Conceptos, models.DO_NOTHING, db_column='id_conceptos')
    currency_conversion = models.DecimalField(max_digits=10, decimal_places=6)

    class Meta:
        managed = False
        db_table = 'dividends'


class Dps(models.Model):
    date = models.DateField(blank=True, null=True)
    gross = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    products = models.ForeignKey('Products', models.DO_NOTHING, blank=True, null=True)
    paydate = models.DateField()

    class Meta:
        managed = False
        db_table = 'dps'


class EstimationsDps(models.Model):
    year = models.IntegerField(primary_key=True)
    estimation = models.DecimalField(max_digits=18, decimal_places=6)
    date_estimation = models.DateField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    manual = models.BooleanField(blank=True, null=True)
    id = models.ForeignKey('Products', models.DO_NOTHING, db_column='id')

    class Meta:
        managed = False
        db_table = 'estimations_dps'
        unique_together = (('year', 'id'),)


class EstimationsEps(models.Model):
    year = models.IntegerField(primary_key=True)
    estimation = models.DecimalField(max_digits=18, decimal_places=6)
    date_estimation = models.DateField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    manual = models.BooleanField(blank=True, null=True)
    id = models.ForeignKey('Products', models.DO_NOTHING, db_column='id')

    class Meta:
        managed = False
        db_table = 'estimations_eps'
        unique_together = (('year', 'id'),)


class Globals(models.Model):
    global_field = models.TextField(db_column='global', primary_key=True)  # Field renamed because it was a Python reserved word.
    value = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'globals'


class Inversiones(models.Model):
    id_inversiones = models.AutoField(primary_key=True)
    inversion = models.TextField()
    active = models.BooleanField()
    id_cuentas = models.ForeignKey(Cuentas, models.DO_NOTHING, db_column='id_cuentas')
    venta = models.DecimalField(max_digits=100, decimal_places=6)
    products = models.ForeignKey('Products', models.DO_NOTHING, blank=True, null=True)
    selling_expiration = models.DateField(blank=True, null=True)
    daily_adjustment = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'inversiones'


class Opercuentas(models.Model):
    id_opercuentas = models.AutoField(primary_key=True)
    id_conceptos = models.ForeignKey(Conceptos, models.DO_NOTHING, db_column='id_conceptos')
    id_tiposoperaciones = models.IntegerField()
    importe = models.DecimalField(max_digits=100, decimal_places=2)
    comentario = models.TextField(blank=True, null=True)
    id_cuentas = models.ForeignKey(Cuentas, models.DO_NOTHING, db_column='id_cuentas')
    datetime = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'opercuentas'


class Opercuentasdeoperinversiones(models.Model):
    id_opercuentas = models.AutoField(primary_key=True)
    id_conceptos = models.IntegerField()
    id_tiposoperaciones = models.IntegerField()
    importe = models.DecimalField(max_digits=100, decimal_places=2)
    comentario = models.TextField(blank=True, null=True)
    id_cuentas = models.IntegerField()
    datetime = models.DateTimeField(blank=True, null=True)
    id_operinversiones = models.IntegerField()
    id_inversiones = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'opercuentasdeoperinversiones'


class Operinversiones(models.Model):
    id_operinversiones = models.AutoField(primary_key=True)
    id_tiposoperaciones = models.IntegerField(blank=True, null=True)
    id_inversiones = models.ForeignKey(Inversiones, models.DO_NOTHING, db_column='id_inversiones', blank=True, null=True)
    acciones = models.DecimalField(max_digits=100, decimal_places=6, blank=True, null=True)
    impuestos = models.DecimalField(max_digits=100, decimal_places=2, blank=True, null=True)
    comision = models.DecimalField(max_digits=100, decimal_places=2, blank=True, null=True)
    valor_accion = models.DecimalField(max_digits=100, decimal_places=6, blank=True, null=True)
    divisa = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)
    comentario = models.TextField(blank=True, null=True)
    show_in_ranges = models.BooleanField(blank=True, null=True)
    currency_conversion = models.DecimalField(max_digits=30, decimal_places=10)

    class Meta:
        managed = False
        db_table = 'operinversiones'


class Opertarjetas(models.Model):
    id_opertarjetas = models.AutoField(primary_key=True)
    id_conceptos = models.ForeignKey(Conceptos, models.DO_NOTHING, db_column='id_conceptos')
    id_tiposoperaciones = models.IntegerField()
    importe = models.DecimalField(max_digits=100, decimal_places=2)
    comentario = models.TextField(blank=True, null=True)
    id_tarjetas = models.ForeignKey('Tarjetas', models.DO_NOTHING, db_column='id_tarjetas')
    pagado = models.BooleanField()
    fechapago = models.DateTimeField(blank=True, null=True)
    id_opercuentas = models.BigIntegerField(blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'opertarjetas'


class Opportunities(models.Model):
    date = models.DateField()
    removed = models.DateField(blank=True, null=True)
    executed = models.DateField(blank=True, null=True)
    entry = models.DecimalField(max_digits=100, decimal_places=2)
    products = models.ForeignKey('Products', models.DO_NOTHING)
    target = models.DecimalField(max_digits=100, decimal_places=2, blank=True, null=True)
    stoploss = models.DecimalField(max_digits=100, decimal_places=2, blank=True, null=True)
    short = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'opportunities'


class Orders(models.Model):
    date = models.DateField()
    expiration = models.DateField()
    shares = models.DecimalField(max_digits=100, decimal_places=6, blank=True, null=True)
    price = models.DecimalField(max_digits=100, decimal_places=2, blank=True, null=True)
    investments = models.ForeignKey(Inversiones, models.DO_NOTHING)
    executed = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orders'


class Products(models.Model):
    name = models.TextField(blank=True, null=True)
    isin = models.TextField(blank=True, null=True)
    currency = models.TextField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    agrupations = models.TextField(blank=True, null=True)
    web = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    mail = models.TextField(blank=True, null=True)
    percentage = models.IntegerField()
    pci = models.CharField(max_length=1)
    leveraged = models.IntegerField()
    stockmarkets_id = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    obsolete = models.BooleanField()
    tickers = models.TextField(blank=True, null=True)  # This field type is a guess.
    high_low = models.BooleanField(blank=True, null=True)
    decimals = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'products'


class Quotes(models.Model):
    datetime = models.DateTimeField(blank=True, null=True)
    quote = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    id_quotes = models.AutoField(primary_key=True)
    id = models.ForeignKey(Products, models.DO_NOTHING, db_column='id', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'quotes'


class Simulations(models.Model):
    database = models.TextField(blank=True, null=True)
    starting = models.DateTimeField(blank=True, null=True)
    ending = models.DateTimeField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    creation = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'simulations'


class Splits(models.Model):
    datetime = models.DateTimeField()
    products = models.ForeignKey(Products, models.DO_NOTHING)
    before = models.IntegerField()
    after = models.IntegerField()
    comment = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'splits'


class Strategies(models.Model):
    name = models.TextField()
    investments = models.TextField(blank=True, null=True)
    dt_from = models.DateTimeField(blank=True, null=True)
    dt_to = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'strategies'


class Tarjetas(models.Model):
    id_tarjetas = models.AutoField(primary_key=True)
    tarjeta = models.TextField(blank=True, null=True)
    id_cuentas = models.ForeignKey(Cuentas, models.DO_NOTHING, db_column='id_cuentas', blank=True, null=True)
    pagodiferido = models.BooleanField(blank=True, null=True)
    saldomaximo = models.DecimalField(max_digits=100, decimal_places=2, blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)
    numero = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tarjetas'
