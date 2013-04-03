from csrf import csrf_protected, csrf_token_input


def parse_tweep_error(e):
    try:
        error = e.args[0][0] # the first error from the first argument
        message = error['message']
        code = error['code']
        return code, message
    except:
        return -1, str(e)