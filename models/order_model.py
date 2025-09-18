from datetime import datetime

class Order:
    def __init__(self, id=None, customer_name="", customer_wa="", customer_address="", 
                 items="", total=0.0, status="pending", created_at=None):
        self.id = id
        self.customer_name = customer_name
        self.customer_wa = customer_wa
        self.customer_address = customer_address
        self.items = items
        self.total = total
        self.status = status
        self.created_at = created_at if created_at else datetime.now()
    
    def __repr__(self):
        return f"Order(id={self.id}, customer={self.customer_name}, total={self.total}, status={self.status})"