import hashlib
import hmac

def mac(file_name, file_hash, token):

    mensaje = b'{}{}'.format(file_name, file_hash)
    clave_aux = token + challenge
    clave = b'{}'.format(clave_aux)
    my_hmac = hmac.new(mensaje, clave, hashlib.sha256)
    return my_hmac.digest()