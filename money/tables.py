
def tb_datetime(dt):
    return str(dt.date())
    
    
## Addapt a listdict to a tabulation listdict
def tb_listdict(listdict):
    r=[]
    for row in listdict:
        d={}
        for field in row.keys():
            if row[field].__class__.__name__ in ["int",  "float", "str"]:
                d[field]=row[field]
            elif row[field].__class__.__name__ in ["boolean", ]:
                d[field]=str(row[field]).lower()
            elif row[field].__class__.__name__ in ["Decimal"]:
                d[field]=float(row[field])
            else:
                d[field]=str(row[field])
                
        r.append(d)
    return r
