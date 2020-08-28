# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models, connection
from money.reusing.currency import Currency, currency_symbol
from money.connection_dj import cursor_one_row, cursor_one_field
from django.utils.translation import gettext as _
from django.utils import timezone
from xulpymoney.libxulpymoneytypes import eProductType
from decimal import Decimal
Decimal()#Internal eval

class Accounts(models.Model):
    name = models.TextField(blank=True, null=True)
    banks = models.ForeignKey('Banks', models.DO_NOTHING, blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)
    number = models.CharField(max_length=24, blank=True, null=True)
    currency = models.TextField()

    class Meta:
        managed = False
        db_table = 'accounts'
        
    def __str__(self):
        return self.fullName()
        
    def fullName(self):
        return "{} ({})".format(self.name, self.banks.name)
        
    ## @return Tuple (balance_account_currency | balance_user_currency)
    def balance(self, dt):
        ## @todo search other solution for local_currency
        local_currency=cursor_one_field("select value from globals where global='mem/localcurrency'")
        r=cursor_one_row("select * from account_balance(%s,%s,%s)", (self.id, dt, local_currency))
        return Currency(r['balance_account_currency'], self.currency), Currency(r['balance_user_currency'], r['user_currency'])

    def currency_symbol(self):
        return currency_symbol(self.currency)


class Accountsoperations(models.Model):
    concepts = models.ForeignKey('Concepts', models.DO_NOTHING)
    operationstypes = models.ForeignKey('Operationstypes', models.DO_NOTHING)
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
            
    def accounts(self, active):
        return Accounts.objects.all().filter(banks_id=self.id, active=active)

    def investments(self, active):
        investments= Investments.objects.raw('SELECT investments.* FROM investments, accounts where accounts.id=investments.accounts_id and accounts.banks_id=%s and investments.active=%s', (self.id, active))
        return investments
        

class Concepts(models.Model):
    name = models.TextField(blank=True, null=True)
    operationstypes = models.ForeignKey('Operationstypes', models.DO_NOTHING, blank=True, null=True)
    editable = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'concepts'
        
    def __str__(self):
        return "{} - {}".format(_(self.name), _(self.operationstypes.name))


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
    operationstypes = models.ForeignKey('Operationstypes', models.DO_NOTHING)
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
    balance_percentage = models.DecimalField(max_digits=18, decimal_places=6)

    class Meta:
        managed = False
        db_table = 'investments'


    def fullName(self):
        return "{} ({})".format(self.name, self.accounts.name)
            

        
        
    ## Lista los id, io, io_current_totals, io_historical_current  de esta inversion
    def get_investmentsoperations_totals(self, dt, local_currency):
        row_io= cursor_one_row("select * from investment_operations_totals(%s,%s,%s)", (self.id, dt, local_currency))
        io= eval(row_io["io"])
        current= eval(row_io['io_current'])
        historical= eval(row_io['io_historical'])
        #print(io, current, historical)
        return io,  current, historical
    
    def get_investmentsoperations(self, dt, local_currency):
        row_io=cursor_one_row("select * from investment_operations(%s,%s,%s)", (self.id, dt, local_currency))
        io= eval(row_io["io"])
#        for row in io:
#            print (row['id'],  row['datetime'],  row['shares'], row['price'])
        current= eval(row_io['io_current'])
#        for row in current:
#            print (row['id'],  row['datetime'],  row['shares'], row['price_investment'])
        historical= eval(row_io['io_historical'])
#        for row in historical:
#            print (row['id'],  row['dt_end'],  row['shares'])
        return io,  current, historical

        

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
    operationstypes = models.ForeignKey('Operationstypes', models.DO_NOTHING, blank=True, null=True)
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


class Leverages(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    multiplier = models.DecimalField(max_digits=65535, decimal_places=65535)

    class Meta:
        managed = False
        db_table = 'leverages'

class Operationstypes(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()

    class Meta:
        managed = False
        db_table = 'operationstypes'
        
    def __str__(self):
        return _(self.name)

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
    productstypes = models.ForeignKey('Productstypes', models.DO_NOTHING, blank=True, null=True)
    agrupations = models.TextField(blank=True, null=True)
    web = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    mail = models.TextField(blank=True, null=True)
    percentage = models.IntegerField()
    pci = models.CharField(max_length=1)
    leverages = models.ForeignKey(Leverages, models.DO_NOTHING)
    stockmarkets_id = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    obsolete = models.BooleanField()
    tickers = models.TextField(blank=True, null=True)  # This field type is a guess.
    high_low = models.BooleanField(blank=True, null=True)
    decimals = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'products'
        
    def __str__(self):
        return self.name
        
    def currency_symbol(self):
        return currency_symbol(self.currency)
    def basic_results(self):
        return cursor_one_row("select * from last_penultimate_lastyear(%s,%s)", (self.id, timezone.now() ))
    ## IBEXA es x2 pero esta en el pricio
    ## CFD DAX no está en el precio
    def real_leveraged_multiplier(self):
        if self.productstypes.id in (eProductType.CFD, eProductType.Future):
            return self.leverages.multiplier
        return 1

class Productstypes(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()

    class Meta:
        managed = False
        db_table = 'productstypes'

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
