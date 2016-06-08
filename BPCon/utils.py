import ssl
import subprocess
import pickle 
def save_state(fname, tosave):
    with open(fname, 'wb') as fh:
        pickle.dump(tosave, fh)

def load_state(fname):
    with open(fname, 'rb') as fh:
        return pickle.load(fh)

def get_ssl_context(path):
    cctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    cctx.check_hostname = False
    cctx.load_verify_locations(capath=path)
    return cctx

def shell(command):
    try:
        subprocess.check_output(['sh','-c', command])
    except Exception as e:
        print("shell command failed: {}".format(e))
