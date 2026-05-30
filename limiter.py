from slowapi import Limiter
from slowapi.util import get_remote_address

# The limiter identifies client by their IP address.
limiter = Limiter(key_func=get_remote_address)