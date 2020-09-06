

def listdict_sum(listdict, key):
    r=0
    for d in listdict:
        r=r+d[key]
    return r
        
        
def listdict_average_ponderated(listdict, key_numbers, key_values):
    prods=0
    for d in listdict:
        prods=prods+d[key_numbers]*d[key_values]
    return prods/listdict_sum(listdict, key_numbers)
