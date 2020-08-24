from money.reusing.call_by_name import call_by_name

def tb_datetime(dt):
    return str(dt.date())
    
def tb_queryset(queryset):
    l=[]
    for o in queryset:
        d={}
        for field in queryset[0]._meta.fields:
            d[field.name]=object_to_tb(getattr(o, field.name))
        l.append(d)
    return l
    
## @param call_by_name_list is a a list of call_by_name orders
def tb_custom_queryset(queryset, headers,  call_by_name_list):
    l=[]
    for o in queryset:
        d={}
        for i,  cbn in enumerate(call_by_name_list):
            d[headers[i]]=object_to_tb(call_by_name(o, cbn))
        l.append(d)
    return l

## Addapt a listdict to a tabulation listdict
def tb_listdict(listdict):
    r=[]
    for row in listdict:
        d={}
        for field in row.keys():
            d[field]=object_to_tb(row[field])
        r.append(d)
    return r
    
def object_to_tb(object):
        if object.__class__.__name__ in ["int",  "float", "str"]:
            return object
        elif object.__class__.__name__ in ["boolean", ]:
            return str(object).lower()
        elif object.__class__.__name__ in ["Decimal"]:
            return float(object)
        elif object.__class__.__name__ in ["Currency"]:
            return object.amount
        else:
            return str(object)
