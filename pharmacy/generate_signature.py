

import hmac
import hashlib
import base64


def genSha256(secret_key, data_to_sign):
    """
    Generates a Base64-encoded HMAC-SHA256 signature.

    Parameters:
        secret_key  (str): Your eSewa secret key
        data_to_sign(str): The string eSewa tells you to sign

    Returns:
        str: Base64 signature to send to eSewa
    """
    secret_key_bytes  = secret_key.encode('utf-8')
    data_bytes        = data_to_sign.encode('utf-8')

    hmac_sha256       = hmac.new(secret_key_bytes, data_bytes, hashlib.sha256)
    digest            = hmac_sha256.digest()
    signature         = base64.b64encode(digest).decode('utf-8')

    return signature