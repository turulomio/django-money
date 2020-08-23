# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models, connection
from money.reusing.currency import Currency


class Accounts(models.Model):
    name = models.TextField(blank=True, null=True)
    banks = models.ForeignKey('Banks', models.DO_NOTHING, blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)
    number = models.CharField(max_length=24, blank=True, null=True)
    currency = models.TextField()

    class Meta:
        managed = False
        db_table = 'accounts'


class Accountsoperations(models.Model):
    concepts = models.ForeignKey('Concepts', models.DO_NOTHING)
    operationstypes_id = models.IntegerField()
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    comment = models.TextField(blank=True, null=True)
    accounts = models.ForeignKey(Accounts, models.DO_NOTHING)
    datetime = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'accountsoperations'


class Annualtargets(models.Model):
    year = models.IntegerField(primary_key=True)
    percentage = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'annualtargets'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


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
            
    def accounts(self):
        return Accounts.objects.all()


class Concepts(models.Model):
    name = models.TextField(blank=True, null=True)
    operationstypes_id = models.IntegerField(blank=True, null=True)
    editable = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'concepts'


class Creditcards(models.Model):
    name = models.TextField(blank=True, null=True)
    accounts = models.ForeignKey(Accounts, models.DO_NOTHING, blank=True, null=True)
    deferred = models.BooleanField(blank=True, null=True)
    maximumbalance = models.DecimalField(max_digits=100, decimal_places=2, blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)
    number = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'creditcards'


class Creditcardsoperations(models.Model):
    concepts = models.ForeignKey(Concepts, models.DO_NOTHING)
    operationstypes_id = models.IntegerField()
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    comment = models.TextField(blank=True, null=True)
    creditcards = models.ForeignKey(Creditcards, models.DO_NOTHING)
    paid = models.BooleanField()
    paid_datetime = models.DateTimeField(blank=True, null=True)
    accountsoperations_id = models.BigIntegerField(blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'creditcardsoperations'


class Dividends(models.Model):
    investments = models.ForeignKey('Investments', models.DO_NOTHING)
    gross = models.DecimalField(max_digits=100, decimal_places=2)
    taxes = models.DecimalField(max_digits=100, decimal_places=2)
    net = models.DecimalField(max_digits=100, decimal_places=2, blank=True, null=True)
    dps = models.DecimalField(max_digits=100, decimal_places=6, blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)
    accountsoperations_id = models.IntegerField(blank=True, null=True)
    commission = models.DecimalField(max_digits=100, decimal_places=2, blank=True, null=True)
    concepts = models.ForeignKey(Concepts, models.DO_NOTHING)
    currency_conversion = models.DecimalField(max_digits=10, decimal_places=6)

    class Meta:
        managed = False
        db_table = 'dividends'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


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


class Investments(models.Model):
    name = models.TextField()
    active = models.BooleanField()
    accounts = models.ForeignKey(Accounts, models.DO_NOTHING)
    selling_price = models.DecimalField(max_digits=100, decimal_places=6)
    products = models.ForeignKey('Products', models.DO_NOTHING, blank=True, null=True)
    selling_expiration = models.DateField(blank=True, null=True)
    daily_adjustment = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'investments'


class Investmentsaccountsoperations(models.Model):
    concepts_id = models.IntegerField()
    operationstypes_id = models.IntegerField()
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    comment = models.TextField(blank=True, null=True)
    accounts_id = models.IntegerField()
    datetime = models.DateTimeField(blank=True, null=True)
    investmentsoperations_id = models.IntegerField()
    investments_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'investmentsaccountsoperations'


class Investmentsoperations(models.Model):
    operationstypes_id = models.IntegerField(blank=True, null=True)
    investments = models.ForeignKey(Investments, models.DO_NOTHING, blank=True, null=True)
    shares = models.DecimalField(max_digits=100, decimal_places=6, blank=True, null=True)
    taxes = models.DecimalField(max_digits=100, decimal_places=2, blank=True, null=True)
    commission = models.DecimalField(max_digits=100, decimal_places=2, blank=True, null=True)
    price = models.DecimalField(max_digits=100, decimal_places=6, blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    show_in_ranges = models.BooleanField(blank=True, null=True)
    currency_conversion = models.DecimalField(max_digits=30, decimal_places=10)

    class Meta:
        managed = False
        db_table = 'investmentsoperations'


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
    investments = models.ForeignKey(Investments, models.DO_NOTHING)
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
    products = models.ForeignKey(Products, models.DO_NOTHING, blank=True, null=True)

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
