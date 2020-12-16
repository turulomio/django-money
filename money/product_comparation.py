
class ProductComparation:
    def __init__(self, a, b):
        self.a=a
        self.b=b
        
    def get_data(self):
        sql="select max(a.datetime)::date, a.id, a.quote, b.id,b.quote from (select * from quotes where products_id=81753)  a, (select * from quotes where products_id=81752)  b where a.datetime::date=b.datetime::date group by a.id, a.quote, b.id, b.quote;"

