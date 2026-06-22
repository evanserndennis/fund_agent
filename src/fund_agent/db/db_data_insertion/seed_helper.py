import uuid
from decimal import Decimal


def uid():
    return str(uuid.uuid4())

def d(val):
    return Decimal(str(round(float(val), 2)))
