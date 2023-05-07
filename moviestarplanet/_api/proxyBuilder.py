

def fix(proxy: str):
    if proxy is None: return None
    else: return f'http://{proxy}'
