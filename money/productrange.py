from datetime import date
from decimal import Decimal
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from xulpymoney.libmanagers import ObjectManager, DatetimeValueManager
from money.models import Investments, Orders
from money.reusing.tabulator import TabulatorFromListDict
from money.reusing.currency import Currency
from money.reusing.percentage import Percentage
from money.investmentsoperations import InvestmentsOperationsManager_from_investment_queryset

class ProductRange():
    def __init__(self, request,  id=None,  product=None,  value=None, percentage_down=None,  percentage_up=None, only_first=True, only_account=None, decimals=2):
        self.request=request
        self.id=id
        self.product=product
        self.value=value
        self.percentage_down=percentage_down
        self.percentage_up=percentage_up
        self.only_first=only_first
        self.only_account=only_account
        self.decimals=decimals
        self.recomendation_invest=False
        self.recomendation_reinvest=False
        
    def __repr__(self):
        return "({}, {}]".format(
            round(self.range_lowest_value(),  self.decimals), 
            round(self.range_highest_value(), self.decimals), 
        )
    
    ## Returns the value rounded to the number of decimals
    def value_rounded(self):
        return round(self.value, self.decimals)
        
    ## Return th value of the range highest value.. Points + percentage/2
    def range_highest_value(self):
        points_to_next_high= self.value/(1-self.percentage_down.value)-self.value
        return self.value+points_to_next_high/2

    ## Return th value of the range highest value.. Points + percentage/2
    def range_lowest_value(self):
        points_to_next_low=self.value-self.value*(1-self.percentage_down.value)
        return self.value-points_to_next_low/2
        
    ## @return Boolean if it's inside the range
    def isInside(self, value):
        if value<self.range_highest_value() and value>=self.range_lowest_value():
            return True
        else:
            return False

    ## Search for investments in self.mem.data and 
    def getInvestmentsOperationsInside(self, iom):
        r=[]
        for io in iom.list:
            if self.only_account is not None:#If different account continues
                if io.investment.accounts.id != self.only_account.id:
                    continue
            
            for op in io.io_current:
                if self.only_first is True:#Only first when neccesary
                    if io.io_current.index(op)!=0:
                        continue
                if self.isInside(op["price_investment"])==True:
                    print(op)
                    r.append(f"{io.investment.fullName()}. Invested: {Currency(op[ 'invested_user'], io.investment.products.currency)}")
        return r
        
    ## Search for orders in self.mem.data and 
    def getOrdersInside(self, orders): 
        r=[]
        for o in orders:
            if self.only_account is not None:#If different account continues
                if o.investments.accounts.id != self.only_account.id:
                    continue
            if o.investments.products.id==self.product.id and self.isInside(o.price)==True:
                r.append(f"{o.investments.fullName()}. Amount: {o.currency_amount()}")
        return r
      

class ProductRangeManager(ObjectManager):
    def __init__(self, request, product, percentage_down, percentage_up, only_first=True, only_account=None, decimals=2):
        ObjectManager.__init__(self)
        self.only_first=only_first
        self.only_account=only_account
        self.request=request
        self.product=product
        self.percentage_down=Percentage(percentage_down, 100)
        self.percentage_up=Percentage(percentage_up, 100)
        self.decimals=decimals
        
        max_=self.product.highest_investment_operation_price()
        min_=self.product.lowest_investment_operation_price()
        
        
        if max_ is not None and min_ is not None: #Investment with shares
            range_highest=max_*Decimal(1+self.percentage_down.value*10)#5 times up value
            range_lowest=min_*Decimal(1-self.percentage_down.value*10)#5 times down value
        else: # No investment jet and shows ranges from product current price
            range_highest=self.product.result.basic.last.quote*Decimal(1+self.percentage_down.value*10)#5 times up value
            range_lowest=self.product.result.basic.last.quote*Decimal(1-self.percentage_down.value*10)#5 times down value

        if range_lowest<Decimal(0.001):#To avoid infinity loop
            range_lowest=Decimal(0.001)



        self.highest_range_value=10000000
        current_value=self.highest_range_value
        i=0
        while current_value>range_lowest:
            if current_value>=range_lowest and current_value<=range_highest:
                self.append(ProductRange(self.request,  i, self.product,current_value, self.percentage_down, percentage_up, self.only_first, self.only_account))
            current_value=current_value*(1-self.percentage_down.value)
            i=i+1

        self.qs_investments=Investments.objects.select_related("accounts").filter(active=True, products_id=self.product.id)
        self.iom=InvestmentsOperationsManager_from_investment_queryset(self.qs_investments, timezone.now(), self.request)
        
        self.orders=Orders.objects.select_related("investments").select_related("investments__accounts").select_related("investments__products").select_related("investments__products__leverages").select_related("investments__products__productstypes").filter(executed=None, expiration__gte=date.today())

        
    ## @return LIst of range values of the manager
    def list_of_range_values(self):
        return self.list_of("value")

    ## Set investment recomendations to all ProductRange objects in array 
    def setInvestRecomendation(self, method, method1_smas=[10, 50, 200]):
        method=int(method)
        if method==0:#ProductRangeInvestRecomendation. None_:
            for o in self.arr:
                o.recomendation_invest=False
        elif method==1:#ProductRangeInvestRecomendation.All:
            for o in self.arr:
                o.recomendation_invest=True
        elif method==2:#ProductRangeInvestRecomendation.ThreeSMA:      
            list_ohcl=self.product.ohclDailyBeforeSplits()
            dvm=DatetimeValueManager()
            for d in list_ohcl:
                dvm.appendDV(d["date"], d["close"])
#            dvm=self.product.result.ohclDaily.DatetimeValueManager("close")
            dvm_smas=[]
            for sma in method1_smas:
                dvm_smas.append(dvm.sma(sma))
            
            for o in self.arr:
                number_sma_over_price=len(self.product.result.ohclDaily.list_of_sma_over_price(self.mem.localzone_now(), o.value, method1_smas, dvm_smas,  "close"))
                if number_sma_over_price==3 and o.id % 4==0:
                    o.recomendation_invest=True
                elif number_sma_over_price==2 and o.id %2==0:
                    o.recomendation_invest=True
                elif number_sma_over_price<=1:
                    o.recomendation_invest=True
        elif method==3: #ProductRangeInvestRecomendation.SMA100:           
            dvm=self.product.result.ohclDaily.DatetimeValueManager("close")
            dvm_smas=[]
            for sma in [100, ]:
                dvm_smas.append(dvm.sma(sma))
            
            for o in self.arr:
                number_sma_over_price=len(self.product.result.ohclDaily.list_of_sma_over_price(self.mem.localzone_now(), o.value, [100, ], dvm_smas,  "close"))
                if number_sma_over_price==0:
                    o.recomendation_invest=True
                elif number_sma_over_price==1 and o.id % 4==0:
                    o.recomendation_invest=True
                else: #number_sma_over_price=1 and o.id%4!=0
                    o.recomendation_invest=False

    def listdict(self):
        r=[]
        for i, o in enumerate(self.arr):
            r.append({
                "value": int(o.value), 
                "recomendation_invest": o.recomendation_invest, 
                "investments_inside": o.getInvestmentsOperationsInside(self.iom), 
                "orders_inside": o.getOrdersInside(self.orders), 
            })
        return r
                    
    def tabulator(self):
        r=TabulatorFromListDict("productrange_table")
        r.setDestinyUrl(None)
        r.setLocalZone(self.request.local_zone)
        r.setListDict(self.listdict())
        r.setFields("id","value","recomendation_invest", "investments_inside","orders_inside")
        r.setHeaders("Id", _("Value"), _("Recomendation"),  _("Investments"),  _("Orders"))
        r.setTypes("int","int", "bool", "str",  "str")
        return r.render()
