
class Transaction:
    """Generic financial transaction class common to all institutions"""
    date = None
    amount = None

    def __str__(self):
        return "%s - %amount" % (self.date, self.amount)
