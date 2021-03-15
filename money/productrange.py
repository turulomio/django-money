from datetime import date
from decimal import Decimal
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from xulpymoney.libmanagers import ObjectManager, DatetimeValueManager
from money.models import Investments, Orders
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
        r=""
        for io in iom.list:
            if self.only_account is not None:#If different account continues
                if io.investment.accounts.id != self.only_account.id:
                    continue
            
            for op in io.io_current:
                if self.only_first is True:#Only first when neccesary
                    if io.io_current.index(op)!=0:
                        continue
                if self.isInside(op["price_investment"])==True:
                    r=r+ f"<a href='{reverse_lazy('investment_view', args=(io.investment.id,))}'>{io.investment.fullName()}</a>. Invested: {Currency(op[ 'invested_user'], io.investment.products.currency)}<br>"
        return r[:-1]
        
    ## Search for orders in self.mem.data and 
    def getOrdersInside(self, orders): 
        r=""
        for o in orders:
            if self.only_account is not None:#If different account continues
                if o.investments.accounts.id != self.only_account.id:
                    continue
            if o.investments.products.id==self.product.id and self.isInside(o.price)==True:
                r=r+f"<a href='{reverse_lazy('order_update',  args=(o.id, ))}'>{o.investments.fullName()}</a>. Amount: {o.currency_amount()}<br>"
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


    ## Returns a list of sma from smas, which dt values are over price parameter
    ## @param dt. datetime
    ## @param price Decimal to compare
    ## @param smas List of integers with the period of the sma
    ## @param dvm_smas. List of DatetimeValueManager with the SMAS with integers are in smas
    ## @param attribute. Can be "open", "high", "close","low"
    ## @return int. With the number of standard sma (10, 50,200) that are over product current price
    def list_of_sma_over_price(self,  dt, price, smas=[10, 50, 200], dvm_smas=None, attribute="close"):
        if dvm_smas==None:#Used when I only neet to calculate one value
            dvm=self.DatetimeValueManager(attribute)
        
            #Calculate smas for all values in smas
            dvm_smas=[]#Temporal list to store sma to fast calculations
            for sma in smas:
                dvm_smas.append(dvm.sma(sma))
            
        # Compare dt sma with price and return a List with smas integers
        r=[]
        for i, dvm_sma in enumerate(dvm_smas):
            sma_value=dvm_sma.find_le(dt).value
            if price<sma_value:
                r.append(smas[i])
        return r


    
    def recomendationMethod2ListSMA(self):
        print("AHORA", self.method)
        if self.method in (0, 1):#ProductRangeInvestRecomendation. None_:
            return []
        elif self.method in (2, 4):#ProductRangeInvestRecomendation.ThreeSMA:      
            return [10, 50, 200]
        elif self.method in (3, 5): #ProductRangeInvestRecomendation.SMA100:           
            return [100, ]
        elif self.method==6:#ProductRangeInvestRecomendation.Strict SMA 10 , 100:      
            return [10,  100]

    ## Set investment recomendations to all ProductRange objects in array 
    def setInvestRecomendation(self, method):
        self.method=int(method)
        print(self.method, self.method.__class__)
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
            dvm_smas=[]
            for sma in [10, 50, 200]:
                dvm_smas.append(dvm.sma(sma))
            
            for o in self.arr:
                number_sma_over_price=len(self.list_of_sma_over_price(date.today(), o.value, [10, 50, 200], dvm_smas,  "close"))
                if number_sma_over_price==3 and o.id % 4==0:
                    o.recomendation_invest=True
                elif number_sma_over_price==2 and o.id %2==0:
                    o.recomendation_invest=True
                elif number_sma_over_price<=1:
                    o.recomendation_invest=True
        elif method==3: #ProductRangeInvestRecomendation.SMA100:           
            list_ohcl=self.product.ohclDailyBeforeSplits()
            dvm=DatetimeValueManager()
            for d in list_ohcl:
                dvm.appendDV(d["date"], d["close"])
            dvm_smas=[]
            for sma in [100, ]:
                dvm_smas.append(dvm.sma(sma))
            
            for o in self.arr:
                number_sma_over_price=len(self.list_of_sma_over_price(date.today(), o.value, [100, ], dvm_smas,  "close"))
                if number_sma_over_price==0:
                    o.recomendation_invest=True
                elif number_sma_over_price==1 and o.id % 4==0:
                    o.recomendation_invest=True
                else: #number_sma_over_price=1 and o.id%4!=0
                    o.recomendation_invest=False
        elif method==4:#ProductRangeInvestRecomendation.StrictThreeSMA:      
            list_ohcl=self.product.ohclDailyBeforeSplits()
            dvm=DatetimeValueManager()
            for d in list_ohcl:
                dvm.appendDV(d["date"], d["close"])
            dvm_smas=[]
            for sma in [10, 50, 200]:
                dvm_smas.append(dvm.sma(sma))
            
            for o in self.arr:
                number_sma_over_price=len(self.list_of_sma_over_price(date.today(), o.value, [10, 50, 200], dvm_smas,  "close"))
                if number_sma_over_price==2 and o.id %2==0:
                    o.recomendation_invest=True
                elif number_sma_over_price<=1:
                    o.recomendation_invest=True
        elif method==5: #ProductRangeInvestRecomendation.SMA100 STRICT:           
            list_ohcl=self.product.ohclDailyBeforeSplits()
            dvm=DatetimeValueManager()
            for d in list_ohcl:
                dvm.appendDV(d["date"], d["close"])
            dvm_smas=[]
            for sma in [100, ]:
                dvm_smas.append(dvm.sma(sma))
            
            for o in self.arr:
                number_sma_over_price=len(self.list_of_sma_over_price(date.today(), o.value, [100, ], dvm_smas,  "close"))
                if number_sma_over_price==0:
                    o.recomendation_invest=True
                else:
                    o.recomendation_invest=False
        elif method==6:#ProductRangeInvestRecomendation.Strict SMA 10 , 100:      
            list_ohcl=self.product.ohclDailyBeforeSplits()
            dvm=DatetimeValueManager()
            for d in list_ohcl:
                dvm.appendDV(d["date"], d["close"])
            dvm_smas=[]
            for sma in [10,  100]:
                dvm_smas.append(dvm.sma(sma))
            
            for o in self.arr:
                number_sma_over_price=len(self.list_of_sma_over_price(date.today(), o.value, [10,  100], dvm_smas,  "close"))
                if number_sma_over_price<2:
                    o.recomendation_invest=True


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
                    
#    def tabulator(self):
#        r=TabulatorFromListDict("productrange_table")
#        r.setDestinyUrl(None)
#        r.setLocalZone(self.request.local_zone)
#        r.setListDict(self.listdict())
#        r.setFields("id","value","recomendation_invest", "investments_inside","orders_inside")
#        r.setHeaders("Id", _("Value"), _("Recomendation"),  _("Investments"),  _("Orders"))
#        r.setTypes("int","int", "bool", "str",  "str")
#        return r.render()

    def mytable(self):        
        def rows():
            r=""
            for o in self:
                if o.recomendation_invest is True:
                    neworder=f"<a href='{reverse_lazy('order_new')}?price={round(o.value, self.product.decimals)}'>{_('Order')}</a>"
                    checked="checked"
                else:
                    neworder=""
                    checked=""
                    
                
              
                classcurrent=' class="green"'  if o.isInside(self.product.basic_results()["last"]) is True else ""
                r=r+ f"""
<tr>
    <td{classcurrent}><a href="javascript:alert('{o}');">{round(o.value, self.product.decimals)}</a></td>
    <td><input type="checkbox" onclick="return false;" {checked}/></td>
    <td>{o.getInvestmentsOperationsInside(self.iom)}</td>
    <td>{o.getOrdersInside(self.orders)}</td>
    <td>{neworder}</td>
</tr>"""
            return r
        #-------------------------------------------
        r=f"""
<table class="mytable">
<tr>
    <th>{_("Value")}</th>
    <th>{_("Must invert")}</th>
    <th>{_("Investments")}</th>
    <th>{_("Orders")}</th>
    <th>{_("Commands")}</th>
    
</tr>
{rows()}
</table>
"""
        return r
