
class Transaction:
    """Generic financial transaction class common to all institutions"""
    def __init__(self, tx_date=None, tx_description=None, tx_amount=None):
        self.tx_date = tx_date
        self.tx_description = tx_description
        self.tx_amount = tx_amount

    #def __str__(self):
    #    return "%s - %amount" % (self.date, self.amount)
