import urllib.parse

def json_to_query_params(json_data):
    if not json_data:
        return ""

    query_params = urllib.parse.urlencode(json_data)
    return f"?{query_params}"

def add_query_params_to_url(base_url, json_data):
    query_params = json_to_query_params(json_data)
    return f"{base_url}{query_params}"