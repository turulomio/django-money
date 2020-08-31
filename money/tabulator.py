from money.reusing.call_by_name import call_by_name
from money.reusing.datetime_functions import dtaware_changes_tz
from django.utils.translation import gettext
from django.urls import reverse

class TabulatorCommons:
    def __init__(self, name):
        self.name=name
        self.destiny_url=None
        self.headers=[] #Table column headers
        self.height=None
        self.translate=True
        self.bottomcalc=None #Is filled in render
        self.field_pk="id"
        self.show_field_pk=False
        self.initial_options=None
        
        self.localzone="UTC"
        
    def setLocalZone(self, s):
        self.localzone=s
    
    def setDestinyUrl(self, destiny_url):
        self.destiny_url=destiny_url
    def setHeaders(self, *args):
        self.headers=args
        
    def setInitialOptions(self, s):
        self.initial_options=s
        
    def setBottomCalc(self, *args):
        self.bottomcalc=args

    ## args, int EUR,USD, percentage, float, Decimal, str. They are python types, not tabulator types
    def setTypes(self, *args):
        self.types=args

    ## @param string 121px
    def setHeight(self, height):
        self.height=height
    
    ## Render from listdict
    def render(self):
        ## Fills bottomCalc if None
        if self.bottomcalc is None:
            self.bottomcalc=[None]*len(self.fields)
        
        tb_list=[]
        for d in self.listdict:
            new_d={}
            for field in self.fields:
                new_d[field]=object_to_tb(d[field], self.translate, self.localzone)
            tb_list.append(new_d)
            
        str_height="" if self.height is None else f'height: "{self.height}",'
        str_initialoptions="" if self.initial_options is None else self.initial_options
        
        if self.destiny_url is None:
            str_destiny_url=""
        else:
            str_url=reverse( self.destiny_url, kwargs={"pk":9999999999})
            str_destiny_url=f"""        rowClick:function(e, row){{
            window.location.href = "{str_url}".replace( 9999999999 , row.getData().id);
            }},"""

        columns=""
        for i in range(len(self.headers)):
            if self.fields[i]==self.field_pk and self.show_field_pk==False:
                continue
            
            if self.types[i]=="datetime":
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}"}}, \n"""
            elif self.types[i] in ("Decimal", "float", "int", "date") and self.bottomcalc[i] is None:
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}", hozAlign:"right" , "formatter": NUMBER}}, \n"""
            elif self.types[i] in ("Decimal", "float", "int") and self.bottomcalc[i] is not None:
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}", hozAlign:"right",  "formatter": NUMBER,  "bottomCalc:"{self.bottomcalc[i]}" }}, \n"""
            elif self.types[i] =="EUR" and self.bottomcalc[i] is None:
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}", formatter: EUR ,hozAlign:"right" }}, \n"""
            elif self.types[i] =="EUR" and self.bottomcalc[i] is not None:
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}", formatter: EUR, hozAlign:"right", bottomCalc:"{self.bottomcalc[i]}",bottomCalcFormatter:EUR}}, \n"""
            elif self.types[i] =="USD" and self.bottomcalc[i] is None:
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}", formatter: USD, ,hozAlign:"right" }}, \n"""
            elif self.types[i] =="USD" and self.bottomcalc[i] is not None:
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}", formatter: USD, hozAlign:"right", bottomCalc:"{self.bottomcalc[i]}",bottomCalcFormatter: USD}}, \n"""
            elif self.types[i]=="str":
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}"}}, \n"""            
            elif self.types[i]=="bool":
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}", formatter:"tickCross", hozAlign:"center" }}, \n"""
            elif self.types[i] =="percentage" and self.bottomcalc[i] is None:
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}", formatter:PERCENTAGE, hozAlign:"right" }}, \n"""


        return f"""
    <div id="{self.name}"></div>
    <script>
        var NUMBER = function(cell, formatterParams){{
    var value = cell.getValue();
    if (value === null) {{return "";}}
    if(value  <0){{
       cell.getElement().style.color="#ff0000";
       return value;
    }}else{{
        return value;
    }}
}};    
    var EUR = function(cell, formatterParams){{
    var value = cell.getValue();
    if (value === null) {{return "";}}
    if(value  <0){{
       cell.getElement().style.color="#ff0000";
       return value.toFixed(2) + " €";
    }}else{{
        return value.toFixed(2) + " €";
    }}
}};    
    var USD = function(cell, formatterParams){{
    var value = cell.getValue();
    if (value === null) {{return "";}}
    if(value  <0){{
       cell.getElement().style.color="#ff0000";
       return value.toFixed(2) + " €";
    }}else{{
        return value.toFixed(2) + " €";
    }}
}};    
    var PERCENTAGE = function(cell, formatterParams){{
    var value = cell.getValue();
    if (value === "") {{return "";}}
    if(value  <0){{
       cell.getElement().style.color="#ff0000";
       return value.toFixed(2) + " %";
    }}else{{
        return value.toFixed(2) + " %";
    }}
}};
    
        var tabledata = {tb_list};  
        var table = new Tabulator("#{self.name}", {{
        {str_height}
        data:tabledata, //assign data to table
        layout:"fitDataTable", //fit columns to width of table (optional)
        columns:[ {columns}
        ],
        {str_initialoptions}
        {str_destiny_url}
        }});
      

    </script>
    """
#            for (let i = 0; i < tabledata.length; i++) {{
#      if (tabledata[i].amount < 0) {{
#      alert(tabledata[i].amount);
#        tabledata[i].amount = "<span class='red'>" + tabledata[i].amount*100 + "</span>";
#      }} else {{
#        tabledata[i].amount = '$' + tabledata[i].amount;
#      }}
#    }}
class TabulatorFromQuerySet(TabulatorCommons):
    def __init__(self, name):
        TabulatorCommons.__init__(self, name)
        self.callbyname=[]
        self.queryset=None
        

    def setCallByNames(self, *args):
        self.callbyname=args
        
        ##Select wich fields from listdict, generated from callbyname
        self.fields=[]
        for cbn in self.callbyname:
            if cbn.__class__.__name__=="str":
                self.fields.append(cbn.replace(".", "_"))
            else:#Tuple
                self.fields.append(cbn[0].replace(".", "_"))

        
    def setQuerySet(self, queryset):
        self.queryset=queryset
        
        
    def generate_listdict(self):
            self.listdict=tb_custom_queryset(self.queryset, self.fields,  self.callbyname, self.translate, self.localzone)      
        

class TabulatorFromListDict(TabulatorCommons):
    def __init__(self, name):
        TabulatorCommons.__init__(self, name)
        self.listdict=None
        
    def setListDict(self, listdict):
        self.listdict=listdict
        
    ##Select wich fields from listdict
    def setFields(self, *args):
        self.fields=args
        
        
def tb_queryset(queryset, translate, localzone):
    l=[]
    for o in queryset:
        d={}
        for field in queryset[0]._meta.fields:
            d[field.name]=object_to_tb(getattr(o, field.name), translate, localzone)
                
        l.append(d)
    return l

## If a field is not found as a None value
## @param call_by_name_list is a a list of call_by_name orders
def tb_custom_queryset(queryset, fields,  call_by_name_list,  translate, localzone):
    l=[]
    for o in queryset:
        d={}
        for i,  cbn in enumerate(call_by_name_list):
            try:
                d[fields[i]]=object_to_tb(call_by_name(o, cbn), translate, localzone)
            except:
                d[fields[i]]=None
        l.append(d)
    return l

## Addapt a listdict to a tabulation listdict
def tb_listdict(listdict, translate, localzone):
    r=[]
    for row in listdict:
        d={}
        for field in row.keys():
            d[field]=object_to_tb(row[field], translate, localzone)
        r.append(d)
    return r
    
def object_to_tb(object, translate, localzone):
        if object.__class__.__name__ in ["str"]:
            return object if translate is False else gettext(object)
        elif object.__class__.__name__ in ["int",  "float"]:
            return object
        elif object.__class__.__name__ in ["bool", ]:
            return str(object).lower()
        elif object.__class__.__name__ in ["Decimal"]:
            return float(object)
        elif object.__class__.__name__ in ["Currency"]:
            return float(object.amount)
        elif object.__class__.__name__ in ["datetime"]:
            return str(dtaware_changes_tz(object,  localzone))[:19]
        elif object.__class__.__name__ in ["Percentage"]:
            try:
                return float(object.value_100())
            except:
                return ""
        else:
            return str(object)

