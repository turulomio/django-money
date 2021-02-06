from money.reusing.tabulator import TabulatorFromListDict, TabulatorFromQuerySet
from django.utils.translation import ugettext_lazy as _



def table_InvestmentsOperationsCurrent_Homogeneus_UserCurrency(ld_ioc, local_zone, name="table_ioc_homogeneus_usercurrency"):      
    currency=ld_ioc[0]["currency_user"]
    r=TabulatorFromListDict(name)
    r.setDestinyUrl(None)
    r.setLocalZone(local_zone)
    r.setListDict(ld_ioc)
    r.setFields("id","datetime", "name","operationstypes",  "shares", "price_user", "invested_user", "balance_user", "gains_gross_user", "percentage_annual", "percentage_apr", "percentage_total")
    r.setHeaders("Id", _("Date and time"), _("Name"),  _("Operation type"),  _("Shares"), _("Price"), _("Invested"), _("Current balance"), _("Gross gains"), _("% year"), _("% APR"), _("% Total"))
    r.setTypes("int","datetime", "str", "str",  "Decimal", currency, currency, currency, currency, "percentage", "percentage", "percentage")
    r.setBottomCalc(None, None, None, None, "sum", None,  "sum", "sum", "sum", None, None, None)
    r.showLastRecord(False)
    return r.render()
class TabulatorAccounts(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, local_currency):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setFields("id","name", "active", "number", "balance", "balance_user")
        self.setHeaders("Id", _("Name"), _("Active"), _("Number"), _("Balance"), _("Local curr. B."))
        self.setTypes("int","str", "bool", "str", "str", local_currency)
        self.setBottomCalc(None, "sum", None, "sum", "sum", "sum", None, None, None)


class TabulatorProductQuotesMonthPercentages(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setFields("year", "1","2","3", "4","5","6", "7","8","9", "10","11","12","13" )
        self.setHeaders(_("Year"), _("January"),  _("February"), _("March"), _("April"), _("May"), _("June"), _("July"), _("August"), _("September"), _("October"), _("November"), _("December"), _("Total"))
        self.setTypes("str", *["percentage"]*13)

class TabulatorProductQuotesMonthQuotes(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, currency):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setFields("year", "1","2","3", "4","5","6", "7","8","9", "10","11","12" )
        self.setHeaders(_("Year"), _("January"),  _("February"), _("March"), _("April"), _("May"), _("June"), _("July"), _("August"), _("September"), _("October"), _("November"), _("December"))
        self.setTypes("str", *[currency]*12)

class TabulatorAccountOperations(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, currency,  local_zone):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setLayout("fitDataStretch")
        self.setLocalZone(local_zone)
        self.setFields("id","datetime", "concepts","amount", "balance","comment")
        self.setHeaders("Id", _("Date and time"), _("Concept"), _("Amount"),_("Balance"),  _("Comment"))
        self.setTypes("int","datetime", "str", currency, currency,  "str")
        self.setBottomCalc(None,  None, None, "sum", None, None)

class TabulatorBanks(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, local_currency):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setFields("id","name", "active", "accounts_balance", "investments_balance", "total_balance")
        self.setHeaders("Id", _("Name"), _("Active"), _("Accounts balance"), _("Investments balance"), _("Total balance"))
        self.setTypes("int","str", "bool", local_currency,  local_currency, local_currency)
        self.setBottomCalc(None,  None, None, "sum", "sum", "sum")

class TabulatorConcepts(TabulatorFromQuerySet):
    def __init__(self, name, destiny_url, queryset):
        TabulatorFromQuerySet.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setQuerySet(queryset)
        self.setCallByNames("id", "name", "operationstypes", "editable")
        self.setHeaders(_("Id"), _("Name"), _("Operation type"), _("Editable"))
        self.setTypes("int", "str", "str", "bool")
        self.generate_listdict()

class TabulatorInvestments(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, local_currency, active, local_zone):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setLocalZone(local_zone)
        if active is True:
            self.setFields("id","name", "last_datetime","last_quote","daily_difference", "daily_percentage", "invested_local",  "balance", "gains", "percentage_invested", "percentage_sellingpoint")

            self.setHeaders(_("Id"), _("Name"), _("Last dt.") ,  _("Last quote"), _("Daily diff"), 
            # Translator: xgettext:no-python-format
            _("% daily"), 
            _("Invested"),_("Balance"),  _("Gains"), 
            # Translator: xgettext:no-python-format
            _("% Invested"), 
            # Translator: xgettext:no-python-format
            _("% selling point"))
        else:
            self.setFields("id","name")
            self.setHeaders(_("Id"), _("Name"))
        self.setTypes("int", "str", "str", "float6",  local_currency, "percentage", local_currency, local_currency, local_currency,"percentage", "percentage")
        self.setBottomCalc(None, None, None, None,"sum", None, "sum", "sum", "sum", None, None)
        self.setFilterHeaders(None, "input", None, None, None, None, None, None, None, None, None)
        
        self.setJSCodeAfterObjectCreation(f"""
// Adding background color 
var column = {self.name}.getColumn("percentage_sellingpoint");
if (column !== false){{//Only for active investments
    for (var cell of column.getCells()) {{
        if (cell.getValue()<5 && cell.getValue()>0){{
            cell.getElement().style.backgroundColor='#92ffab';
        }} else if (cell.getValue()>100){{
            cell.getElement().style.backgroundColor='#ff92ab';
        }}
    }}

    // Adding icon 
    for (var row of {self.name}.getRows()) {{
        var dat=row.getData();
        var date = moment(dat.selling_expiration, "YYYY-MM-DD");
        if (date.isValid() && date< moment().startOf('day')){{
            cell=row.getCell("percentage_sellingpoint");
            cell.getElement().style.backgroundRepeat= 'no-repeat';
            cell.getElement().style.backgroundPosition= '3px 3px';
            cell.getElement().style.backgroundImage="url('/static/images/alarm_clock.png')";
            cell.getElement().style.backgroundSize = "16px 16px";
        }}
    }}

    //Sorting
    {self.name}.setSort([
        {{column:"gains", dir:"desc"}}, //sort by this first
        {{column:"percentage_sellingpoint", dir:"asc"}}, //sort by this first
    ]);
}}
""")

class TabulatorInvestmentsPairsInvestCalculator(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, local_currency, local_zone):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)    
        self.setFields("name", "last_datetime","last","invested", "current", "new",   "new_plus_current", "shares")
        self.setHeaders(_("Investment name"), _("Last quote update"),  _("Last quote"), _("Invested"), _("Current balance"),   _("New inversion"), _("Current + new"), _("Shares to invest"))
        self.setTypes("str", "datetime", "Decimal", local_currency, local_currency,local_currency,local_currency,"Decimal")
        self.setBottomCalc(None, None, None,  "sum", "sum",  "sum", "sum", None)

class TabulatorInvestmentsOperationsCurrentHeterogeneus(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, local_currency, local_zone):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setLocalZone(local_zone)
        self.setListDict(listdict)
        self.setFields("id","datetime", "name",  "operationstypes",  "shares", "price_investment", "invested_investment", "balance_investment", "gains_gross_investment", "percentage_annual", "percentage_apr", "percentage_total")
        self.setHeaders("Id", _("Date and time"), _("Name"),  _("Operation type"),  _("Shares"), _("Price"), _("Invested"), _("Current balance"), _("Gross gains"), _("% year"), _("% APR"), _("% Total"))
        self.setTypes("int","datetime", "str", "str",  "Decimal", local_currency, local_currency, local_currency,  local_currency, "percentage", "percentage", "percentage")
        self.setBottomCalc(None, None,  None, None, None, None, "sum", "sum", "sum", None, None, None)
        self.showLastRecord(False)

class TabulatorProducts(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, local_currency, local_zone):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setLocalZone(local_zone)
        self.setListDict(listdict)
        self.setFields("id",  "code","name", "isin", "last_datetime", "last", "percentage_day", "percentage_year",  "percentage_dps")
        self.setHeaders(_("Id"), _("Code"),  _("Name"), _("ISIN"), _("Last quote datetime"), _("Last quote"), _("% day"), _("% year"), _("% DPS"))
        self.setTypes("int", "int","str", "str", "str", "Decimal6", "percentage", "percentage", "percentage")
        self.setFilterHeaders(None,  *["input"]*8)



class TabulatorInvestmentsOperationsHistoricalHeterogeneus(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, local_currency, local_zone):
        print("deprecated use LdoInvestmentsOperationsHistoricalHeterogeneus")
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setLocalZone(local_zone)
        self.setListDict(listdict)
        self.setFields("id","dt_end", "years", "name", "operationstypes","shares", "gross_start_user", "gross_end_user", "gains_gross_user", "commissions_user", "taxes_user", "gains_net_user")
        self.setHeaders("Id", _("Date and time"), _("Years"),_("Investment"), _("Operation type"),  _("Shares"), _("Gross start"), _("Gross end"), _("Gross gains"), _("Commissions"), _("Taxes"), _("Net gains"))
        self.setTypes("int","datetime", "int", "str",   "str", "Decimal", local_currency, local_currency, local_currency, local_currency, local_currency, local_currency)
        self.setBottomCalc(None, None, None, None, None, None, "sum", "sum", "sum", "sum", "sum", "sum")

        
class TabulatorCreditCards(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, account):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setFields("id", "name", "number", "deferred", "maximumbalance", "balance")
        self.setHeaders(_("Id"), _("Name"), _("Number"), _("Deferred pay"), _("Maximum balance"), _("balance"))
        self.setTypes("int", "str", "str", "bool", account.currency, account.currency)  

class TabulatorReportConcepts(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, local_currency):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setFields("id", "name", "operationstypes","total","percentage_total",  "median")
        self.setHeaders(_("id"), _("Name"), _("Operation type"),  _("Total"), _("% total"),  _("Median"))
        self.setTypes("int","str", "str", local_currency, "percentage", local_currency)
        self.setBottomCalc(None, None, None,"sum", None, None)   
        self.setInitialOptions("""
    initialSort:[
    {column:"total", dir:"desc"}, //sort by this first
    ],""")        

class TabulatorOrders(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, local_currency):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setFields("id", "date", "expiration", "name", "currency","shares", "price", "amount", "percentage_from_price","executed")
        self.setHeaders(_("Id"), _("Date"),_("Expiration"), _("Investment"), _("Currency"),   _("Shares"), _("Price"), _("Amount"), _("% from price"), _("Executed"))
        self.setTypes("int", "str", "str", "str",  "str",   "Decimal", "Decimal", "Decimal", "percentage","str")
        self.setBottomCalc(None, None, None, None, None,None,None,"sum", None, None)        
        

class TabulatorReportTotal(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, investment):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setLayout("fitColumns")
        self.setFields("month", "account_balance","investment_balance", "total", "diff_lastmonth", "percentage_year")
        self.setHeaders(_("Month"), _("Account balance"), _("Investment balance"), _("Total balance"), _("Last month diff"), _("% year to date"))
        self.setTypes("str","EUR", "EUR", "EUR", "EUR","percentage")
        self.showLastRecord(False)
        self.setBottomCalc(None, None, None, None, "sum", None)      

class TabulatorReportIncomeTotal(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, local_currency):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url, destiny_type=2, new_tab=True)##Type=2 year, month as parameter in id in the form "year/month/"
        self.setListDict(listdict)
        self.setLayout("fitColumns")
        self.setFields("id","month", "incomes","expenses", "gains", "dividends", "total")
        self.setHeaders("Id", _("Month"), _("Incomes"), _("Expenses"), _("Net gains"), _("Net dividends"), _("Total"))
        self.setTypes("int","str","EUR", "EUR", "EUR", "EUR","EUR")
        self.setBottomCalc(None, None, "sum", "sum", "sum", "sum", "sum")
        self.showLastRecord(False)

class TabulatorStrategies(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, local_currency):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setFields("id","name", "dt_from","dt_to", "gains_net_current", "gains_net_historical","dividends_net", "total_net")
        self.setHeaders("Id", _("Name"), _("From"), _("To"), _("Current net gains"), _("Historical net gains"), _("Net dividends"), _("Net total"))
        self.setTypes("int","str", "str", "str","EUR", "EUR", "EUR","EUR")
        self.setBottomCalc(None, None, None,None, "sum", "sum", "sum", "sum")

class TabulatorInvestmentsGainsByProductType(TabulatorFromListDict):
    def __init__(self, name, destiny_url, listdict, local_currency):
        TabulatorFromListDict.__init__(self, name)
        self.setDestinyUrl(destiny_url)
        self.setListDict(listdict)
        self.setFields("id","name", "gains_gross",  "dividends_gross","gains_net","dividends_net")
        self.setHeaders("Id", _("Name"), _("Gross gains"), _("Gross dividends"), _("Net gains"), _("Net dividends"))
        self.setTypes("int","str", local_currency, local_currency, local_currency, local_currency)
        self.setBottomCalc(None, None, "sum", "sum", "sum", "sum")
