import uuid
import sys
from pathlib import Path
from decimal import Decimal

_src_dir = str(Path(__file__).parent.parent.parent)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)


def uid():
    return str(uuid.uuid4())

def d(val):
    return Decimal(str(round(float(val), 2)))
