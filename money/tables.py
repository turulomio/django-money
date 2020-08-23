
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
        else:
            return str(object)
