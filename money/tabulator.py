from money.reusing.call_by_name import call_by_name
from money.reusing.datetime_functions import dtaware_changes_tz
from django.utils.translation import gettext
from django.urls import reverse

class TabulatorCommons:
    def __init__(self, name):
        self.name=name
        
        self.destiny_url=None
        self.destiny_type=None # To render different click functions
        
        self.headers=[] #Table column headers
        self.height=None
        self.translate=True
        self.bottomcalc=None #Is filled in render
        self.field_pk="id"
        self.show_field_pk=False
        self.initial_options=None
        self.layout="fitDataTable"
        self.show_last_record=True
        
        self.localzone="UTC"
        
    def setLocalZone(self, s):
        self.localzone=s
    
    def setDestinyUrl(self, destiny_url, destiny_type=1, new_tab=False):
        self.destiny_url=destiny_url
        self.destiny_type=destiny_type
        self.destiny_new_tab=new_tab
        
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
        
    def setLayout(self, layout):
        self.layout=layout
    
    def showLastRecord(self, b):
        self.show_last_record=b
    
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
                        
        if self.show_last_record is True and len(tb_list)>0:
            str_show_last_record="""        
                var last = table.getRowFromPosition(tabledata.length-1, true);
                table.scrollToRow(last.getData().id, "top", true);
            """
        else:
            str_show_last_record=""

        str_height="" if self.height is None else f'height: "{self.height}",'
        str_initialoptions="" if self.initial_options is None else self.initial_options
        
        if self.destiny_url is None:
            str_destiny_url=""
        else:
            if self.destiny_type==1: #Normal with id field as pk
                str_url=reverse( self.destiny_url, kwargs={"pk":9999999999})
                str_destiny_url=f"""
                    rowClick:function(e, row){{
                        window.location.href = "{str_url}".replace(9999999999 , row.getData().id);
                    }},"""
            elif self.destiny_type==2:#Type=2 year, month as parameter in id in the form "year/month/"
                str_url=reverse( self.destiny_url)## Needs default year month in url view (today(), to allow it
                if self.destiny_new_tab==True:
                    where=f"window.open('{str_url}'.concat(row.getData().id), '_blank');"
                else:
                    where=f'window.location.href = "{str_url}".concat(row.getData().id);'
                str_destiny_url=f"""
                    rowClick:function(e, row){{
                        {where}
                    }},"""

        columns=""
        for i in range(len(self.headers)):
            if self.fields[i]==self.field_pk and self.show_field_pk==False:
                continue
            
            if self.types[i] in ("datetime", "date"):
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}"}}, \n"""
            elif self.types[i] in ("Decimal", "float", "int") and self.bottomcalc[i] is None:
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}", hozAlign:"right" , formatter: NUMBER }}, \n"""
            elif self.types[i] in ("Decimal", "float", "int") and self.bottomcalc[i] is not None:
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}", hozAlign:"right",  formatter: NUMBER, bottomCalc:"{self.bottomcalc[i]}" }}, \n"""
            elif self.types[i] =="EUR" and self.bottomcalc[i] is None:
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}", minWidth:100,  formatter: NUMBER, formatterParams:{{"suffix": "€"}}, hozAlign:"right" }}, \n"""
            elif self.types[i] =="EUR" and self.bottomcalc[i] is not None:
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}", minWidth:100, formatter: NUMBER, formatterParams:{{"suffix": "€"}}, hozAlign:"right", bottomCalc:"{self.bottomcalc[i]}",bottomCalcFormatter: NUMBER, bottomCalcFormatterParams:{{"suffix": "€"}} }}, \n"""
            elif self.types[i] =="USD" and self.bottomcalc[i] is None:
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}", minWidth:100, formatter: NUMBER, formatterParams:{{"suffix": "$"}}, hozAlign:"right" }}, \n"""
            elif self.types[i] =="USD" and self.bottomcalc[i] is not None:
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}", minWidth:100, formatter: NUMBER, formatterParams:{{"suffix": "$"}},  hozAlign:"right", bottomCalc:"{self.bottomcalc[i]}",bottomCalcFormatter: NUMBER, bottomCalcFormatterParams:{{"suffix": "$"}} }}, \n"""
            elif self.types[i]=="str":
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}"}}, \n"""            
            elif self.types[i]=="bool":
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}", formatter:"tickCross", hozAlign:"center" }}, \n"""
            elif self.types[i] =="percentage" and self.bottomcalc[i] is None:
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}", minWidth:100, formatter:NUMBER, formatterParams:{{"suffix": "%"}}, hozAlign:"right" }}, \n"""
            elif self.types[i] =="percentage" and self.bottomcalc[i] is not None:
                columns=columns+f"""{{title: "{self.headers[i]}", field:"{self.fields[i]}", minWidth:100, formatter:NUMBER, formatterParams:{{"suffix": "%"}}, hozAlign:"right", bottomCalc:"{self.bottomcalc[i]}",bottomCalcFormatter: NUMBER, bottomCalcFormatterParams:{{"suffix": "%"}} }}, \n"""


        return f"""
    <div id="{self.name}"></div>
    <script>
    var NUMBER = function(cell, formatterParams){{
    if (formatterParams.hasOwnProperty('suffix')){{
        suffix=" ".concat(formatterParams.suffix);
    }} else {{
        suffix="";
    }}
    if (formatterParams.hasOwnProperty('digits')){{
        digits=formatterParams.digits.parseInt();
    }} else {{
        digits=2;
    }}
    if (cell.getValue() == null) {{return "";}}
    if (cell.getValue() == '') {{return "";}}
    if (cell.getValue()<0){{
       cell.getElement().style.color="#ff0000";
    }}
    console.log(cell.getValue());
    return cell.getValue().toFixed(digits) + suffix;
}};    

    
        var tabledata = {tb_list};  
        var table = new Tabulator("#{self.name}", {{
        selectable:true,
        {str_height}
        data:tabledata, //assign data to table
        layout:"{self.layout}", //fit columns to width of table (optional)
        columns:[ {columns}
        ],
        {str_initialoptions}
        {str_destiny_url}

        }});
        
        {str_show_last_record}
    </script>
    """
    
#            alert(last.getData().id)
#        table.selectRow(last.getData().id);
#        rows = table.getRows(true);
#        last=rows[rows.length -1].getData()
#       
#        scrollToRowPosition: "bottom", //position row in the center of the table when scrolled to
#        table.selectRow(69);
#        table.selectRow(table.getRows().length);    for (let i = 0; i < tabledata.length; i++) {{
#      if (tabledata[i].amount < 0) {{
#      alert(tabledata[i].amount);
#        tabledata[i].amount = "<span class='red'>" + tabledata[i].amount*100 + "</span>";
#      }} else {{
#        tabledata[i].amount = '$' + tabledata[i].amount;
#      }}
#    }}
#        dataSorted:function(sorters, rows){{
#            this.scrollToRow(rows[rows.length -1].id, "bottom", true)
#        }},
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

