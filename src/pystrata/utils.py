import secrets
import string

def rand_string(n):
    choice_set = string.ascii_uppercase + string.ascii_lowercase + string.digits    
    res = ''.join(secrets.choice(choice_set) for i in range(n))
    return str(res)
