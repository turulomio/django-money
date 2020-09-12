# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from datetime import date
from decimal import Decimal
Decimal()#Internal eval

from django.utils.translation import gettext as _
from django.utils import timezone
from django.db import models, connection

from money.reusing.currency import Currency, currency_symbol
from money.connection_dj import cursor_one_field, cursor_one_column, cursor_one_row, cursor_rows
from money.reusing.datetime_functions import dtaware_month_end, string2dtnaive, dtaware
from money.reusing.percentage import Percentage
from money.listdict_functions import listdict_average_ponderated

from xulpymoney.libxulpymoneytypes import eProductType

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
    
    @staticmethod
    def accounts_balance_user_currency(qs, dt):
        return cursor_one_field("select sum((account_balance(accounts.id,%s,'EUR')).balance_user_currency) from  accounts where id in %s", (dt, qs_list_of_ids(qs)))
    

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
        
    def __str__(self):
        return "{} {} {}".format(self.datetime, self.concepts.name, self.amount)


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
        ordering = ['name']
        
    def __str__(self):
        return self.fullName()
        
    def fullName(self):
        return "{} - {}".format(_(self.name), _(self.operationstypes.name))
        
    @staticmethod
    def dict():
        d={}
        for o in Concepts.objects.all():
            d[o.id]=o.fullName()
        return d


class Creditcards(models.Model):
    name = models.TextField()
    accounts = models.ForeignKey(Accounts, models.DO_NOTHING)
    deferred = models.BooleanField()
    maximumbalance = models.DecimalField(max_digits=100, decimal_places=2, blank=True, null=True)
    active = models.BooleanField()
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


    ## TODO This method should take care of diffrent currencies in accounts. Dividens are in account currency
    @staticmethod
    def netgains_dividends(year, month):
        dividends=cursor_one_field("""
    select 
        sum(net) 
    from 
        dividends 
    where 
        date_part('year',datetime)=%s and
        date_part('month',datetime)=%s
    """, (year, month))
        if dividends is None:
            dividends=0
        return dividends

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
        for d in io:
            d['datetime']=postgres_datetime_string_2_dtaware(d['datetime'])
#        for row in io:
#            print (row['id'],  row['datetime'],  row['shares'], row['price'])
        current= eval(row_io['io_current'])
        for d in current:
            d['datetime']=postgres_datetime_string_2_dtaware(d['datetime'])
#        for row in current:
#            print (row['id'],  row['datetime'],  row['shares'], row['price_investment'])
        historical= eval(row_io['io_historical'])
        for d in historical:
            d['dt_start']=postgres_datetime_string_2_dtaware(d['dt_start'])
            d['dt_end']=postgres_datetime_string_2_dtaware(d['dt_end'])
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
    
    ## @param d Dict with investmentsoperationscurrent
    ## @param d Dict with basic results of investment product
    @staticmethod
    def investmentsoperationscurrent_percentage_annual(d_ioc, d_basic):
        if d_ioc["datetime"].year==date.today().year:
            lastyear=d_ioc["price_investment"] #Product value, self.money_price(type) not needed.
        else:
            lastyear=d_basic["lastyear"]
        if d_basic["lastyear"] is None or lastyear is None:
            return Percentage()

        if d_ioc["shares"]>0:
            return Percentage(d_basic["last"]-lastyear, lastyear)
        else:
            return Percentage(-(d_basic["last"]-lastyear), lastyear)
        
    @staticmethod
    def investmentsoperationscurrent_age(d_ioc):
            return (date.today()-d_ioc["datetime"].date()).days

    @staticmethod
    def investmentsoperationscurrent_percentage_apr(d_ioc):
            dias=Investmentsoperations.investmentsoperationscurrent_age(d_ioc)
            if dias==0:
                dias=1
            return Percentage(Investmentsoperations.investmentsoperationscurrent_percentage_total(d_ioc)*365,  dias)


    @staticmethod
    def investmentsoperationscurrent_percentage_total(d_ioc):
        if d_ioc["invested_investment"] is None:#initiating xulpymoney
            return Percentage()
        return Percentage(d_ioc['gains_gross_investment'], d_ioc["invested_investment"])

    #Investment price 
    def invesmentsoperationscurrent_average_price_investment(listdict_ioc, price_key="price_user"):
        return listdict_average_ponderated(listdict_ioc, "shares", price_key)

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
        self.fullName()
        
    def fullName(self):
        return _(self.name)
        
    @staticmethod
    def dict():
        d={}
        for ot in Operationstypes.objects.all():
            d[ot.id]=ot.fullName()
        return d
        


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
        return self.fullName()
        
    def fullName(self):
        return "{} ({})".format(self.name, self.id)
        
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

    def quote(self, dt):
        return cursor_one_row("select * from quote(%s,%s)", (self.id, dt ))
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





## Converting dates to string in postgres functions return a string datetime instead of a dtaware. Here we convert it
def postgres_datetime_string_2_dtaware(s):
    str_dt_end=s[:19]            
    dt_end_naive=string2dtnaive(str_dt_end, "%Y-%m-%d %H:%M:%S")#Es un string desde postgres
    dt_end=dtaware(dt_end_naive.date(), dt_end_naive.time(), 'UTC')
    return dt_end

def percentage_to_selling_point(shares, selling_price, last_quote):       
    """Función que calcula el tpc selling_price partiendo de las el last y el valor_venta
    Necesita haber cargado mq getbasic y operinversionesactual"""
    if selling_price==0 or selling_price==None:
        return Percentage()
    if shares>0:
        return Percentage(selling_price-last_quote, last_quote)
    else:#Long short products
        return Percentage(-(selling_price-last_quote), last_quote)

## Genera una fila (io, io_current, io_historical) con los totales de todas las inversiones
def get_investments_alltotals(dt, local_currency, only_active):
    row_io= cursor_one_row("select * from  investment_operations_alltotals( %s,%s,%s)", (dt, local_currency, only_active))
    io= eval(row_io["io"])
    current= eval(row_io['io_current'])
    historical= eval(row_io['io_historical'])
    return io,  current, historical
    
## Lista los id, io, io_current_totals, io_historical_current de todas las inversiones
## Devuelve un diccionario d[id][
##        investments_totals_all_investments=get_investmentsoperations_totals_of_all_investments(dt, local_currency)
## investments_totals_all_investments[str(investment.id)]["io_current"]["balance_user"]
def get_investmentsoperations_totals_of_all_investments(dt, local_currency):
    d={}
    for row in cursor_rows("select id, (investment_operations_totals(id, %s,%s)).io, (investment_operations_totals(id, %s, %s)).io_current, (investment_operations_totals(id, %s, %s)).io_historical from  investments;", (dt, local_currency, dt, local_currency, dt, local_currency)):
        d[str(row['id'])]={"io": eval(row['io']),"io_current": eval(row['io_current']),"io_historical": eval(row['io_historical']), }
    return d

def currencies_in_accounts():
    return cursor_one_column("select distinct(currency) from accounts")
    
## @return accounts, investments, totals
def total_balance(dt, local_currency):
    return cursor_one_row("select * from total_balance(%s,%s)", (dt, local_currency, ))






def money_convert(dt, amount, from_,  to_):   
    return cursor_one_field("select * from money_convert(%s, %s, %s, %s)", (dt, amount, from_,  to_))




## This method should take care of diffrent currencies
def balance_user_by_operationstypes(year,  month,  operationstypes_id, local_currency, local_zone):
    r=0
    for currency in currencies_in_accounts():
        for row in cursor_rows("""
            select sum(amount) as amount 
            from 
                accountsoperations,
                accounts
            where 
                operationstypes_id=%s and 
                date_part('year',datetime)=%s and
                date_part('month',datetime)=%s and
                accounts.currency=%s and
                accounts.id=accountsoperations.accounts_id   
        union all 
            select sum(amount) as amount 
            from 
                creditcardsoperations ,
                creditcards,
                accounts
            where 
                operationstypes_id=%s and 
                date_part('year',datetime)=%s and
                date_part('month',datetime)=%s and
                accounts.currency=%s and
                accounts.id=creditcards.accounts_id and
                creditcards.id=creditcardsoperations.creditcards_id""", (operationstypes_id, year, month,  currency, operationstypes_id, year, month,  currency)):

            if row['amount'] is not None:
                if local_currency==currency:
                    r=r+row['amount']
                else:
                    r=r+money_convert(dtaware_month_end(year, month, local_zone), row['amount'], currency, local_currency)
    return r


    
def qs_investments_netgains_usercurrency_in_year_month(qs_investments, year, month, local_currency, local_zone):
    r =0
    #Git investments with investmentsoperations in this year, month
    dt_year_month=dtaware_month_end(year, month, local_zone)
    for investment in Investments.objects.raw("select distinct(investments.*) from investmentsoperations, investments where date_part('year', datetime)=%s and date_part('month', datetime)=%s and investments.id=investmentsoperations.investments_id", (year, month)):
        io, io_current, io_historical=investment.get_investmentsoperations(dt_year_month, 'EUR')
        for ioh in io_historical:
            if ioh['dt_end'].year==year and ioh['dt_end'].month==month:
                    r=r+ioh['net_gains_user']
    return r


def qs_list_of_ids(qs):
    r=[]
    for o in qs:
        r.append(o.id)
    return tuple(r)

from xulpymoney.casts import string2list_of_integers
from xulpymoney.datetime_functions import dtaware2string
from xulpymoney.libxulpymoneytypes import eComment, eMoneyCurrency
from xulpymoney.objects.dividend import Dividend
from xulpymoney.objects.money import Money
## Class who controls all comments from accountsoperations, investmentsoperations ...
class Comment:
    def __init__(self):
        pass

    ##Obtiene el codigo de un comment
    def getCode(self, string):
        (code, args)=self.get(string)
        return code        

    def getArgs(self, string):
        """
            Obtiene los argumentos enteros de un comment
        """
        (code, args)=self.get(string)
        return args

    def get(self, string):
        """Returns (code,args)"""
        string=string
        try:
            number=string2list_of_integers(string, separator=",")
            if len(number)==1:
                code=number[0]
                args=[]
            else:
                code=number[0]
                args=number[1:]
            return(code, args)
        except:
            return(None, None)
            
    ## Function to generate a encoded comment using distinct parameters
    ## Encode parameters can be:
    ## - eComment.DerivativeManagement, hlcontract
    ## - eComment.Dividend, dividend
    ## - eComment.AccountTransferOrigin operaccountorigin, operaccountdestiny, operaccountorigincommission
    ## - eComment.AccountTransferOriginCommission operaccountorigin, operaccountdestiny, operaccountorigincommission
    ## - eComment.AccountTransferDestiny operaccountorigin, operaccountdestiny, operaccountorigincommission
    ## - eComment.CreditCardBilling creditcard, operaccount
    ## - eComment.CreditCardRefund opercreditcardtorefund
    def encode(self, ecomment, *args):
        if ecomment==eComment.InvestmentOperation:
            return "{},{}".format(eComment.InvestmentOperation, args[0].id)
        elif ecomment==eComment.Dividend:
            return "{},{}".format(eComment.Dividend, args[0].id)        
        elif ecomment==eComment.AccountTransferOrigin:
            operaccountorigincommission_id=-1 if args[2]==None else args[2].id
            return "{},{},{},{}".format(eComment.AccountTransferOrigin, args[0].id, args[1].id, operaccountorigincommission_id)
        elif ecomment==eComment.AccountTransferOriginCommission:
            operaccountorigincommission_id=-1 if args[2]==None else args[2].id
            return "{},{},{},{}".format(eComment.AccountTransferOriginCommission, args[0].id, args[1].id, operaccountorigincommission_id)
        elif ecomment==eComment.AccountTransferDestiny:
            operaccountorigincommission_id=-1 if args[2]==None else args[2].id
            return "{},{},{},{}".format(eComment.AccountTransferDestiny, args[0].id, args[1].id, operaccountorigincommission_id)
        elif ecomment==eComment.CreditCardBilling:
            return "{},{},{}".format(eComment.CreditCardBilling, args[0].id, args[1].id)      
        elif ecomment==eComment.CreditCardRefund:
            return "{},{}".format(eComment.CreditCardRefund, args[0].id)        
    
    def validateLength(self, number, code, args):
        if number!=len(args):
            print("Comment {} has not enough parameters".format(code))
            return False
        return True

    def decode(self, string):
        """Sets the comment to show in app"""
        from xulpymoney.objects.accountoperation import AccountOperation
        try:
            (code, args)=self.get(string)
            if code==None:
                return string

            if code==eComment.InvestmentOperation:
                if not self.validateLength(1, code, args): return string
                io=self.mem.data.investments.findInvestmentOperation(args[0])
                if io==None: return string
                if io.investment.hasSameAccountCurrency():
                    return self.tr("{}: {} shares. Amount: {}. Comission: {}. Taxes: {}").format(io.investment.name, io.shares, io.gross(eMoneyCurrency.Product), io.money_commission(eMoneyCurrency.Product), io.taxes(eMoneyCurrency.Product))
                else:
                    return self.tr("{}: {} shares. Amount: {} ({}). Comission: {} ({}). Taxes: {} ({})").format(io.investment.name, io.shares, io.gross(eMoneyCurrency.Product), io.gross(eMoneyCurrency.Account),  io.money_commission(eMoneyCurrency.Product), io.money_commission(eMoneyCurrency.Account),  io.taxes(eMoneyCurrency.Product), io.taxes(eMoneyCurrency.Account))

            elif code==eComment.AccountTransferOrigin:#Operaccount transfer origin
                if not self.validateLength(3, code, args): return string
                aod=AccountOperation(self.mem, args[1])
                return _("Transfer to {}").format(aod.account.name)

            elif code==eComment.AccountTransferDestiny:#Operaccount transfer destiny
                if not self.validateLength(3, code, args): return string
                aoo=AccountOperation(self.mem, args[0])
                return _("Transfer received from {}").format(aoo.account.name)

            elif code==eComment.AccountTransferOriginCommission:#Operaccount transfer origin commission
                if not self.validateLength(3, code, args): return string
                aoo=AccountOperation(self.mem, args[0])
                aod=AccountOperation(self.mem, args[1])
                return _("Comission transfering {} from {} to {}").format(aoo.account.currency.string(aoo.amount), aoo.account.name, aod.account.name)

            elif code==eComment.Dividend:#Comentario de cuenta asociada al dividendo
                if not self.validateLength(1, code, args): return string
                dividend=Dividend(self.mem).init__db_query(args[0])
                investment=self.mem.data.investments.find_by_id(dividend.investment.id)
                if investment.hasSameAccountCurrency():
                    return _( "From {}. Gross {}. Net {}.").format(investment.name, dividend.gross(1), dividend.net(1))
                else:
                    return _( "From {}. Gross {} ({}). Net {} ({}).").format(investment.name, dividend.gross(1), dividend.gross(2), dividend.net(1), dividend.net(2))

            elif code==eComment.CreditCardBilling:#Facturaci´on de tarjeta diferida
                if not self.validateLength(2, code, args): return string
                creditcard=self.mem.data.accounts.find_creditcard_by_id(args[0])
                number=self.mem.con.cursor_one_field("select count(*) from creditcardsoperations where accountsoperations_id=%s", (args[1], ))
                return _("Billing {} movements of {}").format(number, creditcard.name)

            elif code==eComment.CreditCardRefund:#Devolución de tarjeta
                from xulpymoney.objects.creditcardoperation import CreditCardOperation
                if not self.validateLength(1, code, args): return string
                cco=CreditCardOperation(self.mem).init__db_query(args[0])
                money=Money(self.mem, cco.amount, cco.tarjeta.account.currency)
                return _("Refund of {} payment of which had an amount of {}").format(dtaware2string(cco.datetime), money)
        except:
            return self.tr("Error decoding comment {}").format(string)
