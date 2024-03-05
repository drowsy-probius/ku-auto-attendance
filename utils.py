import warnings
from typing import Union, List, Any

import requests


def get_of(
    data: Union[dict, list],
    key_list: Union[List[Union[str, int]], str, int],
    default: Any = None,
    ignore: bool = False,
):
    if not isinstance(key_list, list):
        return get_of(data, [key_list], default=default, ignore=ignore)

    __trace: dict = {}

    try:
        result = data
        for key in key_list:
            result = result[key]
            __trace[key] = str(result)[:500]
        return result
    except KeyError as e:
        warnings.warn(f"queries: {key_list}, query_trace: {__trace}")
        warnings.warn(f"Missing Key: {e}")
        if ignore:
            return default
        raise e
    except Exception as e:
        warnings.warn(f"queries: {key_list}, query_trace: {__trace}")
        warnings.warn(str(e))
        if ignore:
            return default
        raise e


def send_message(webhooks: List[dict], message: str):
    for webhook in webhooks:
        if webhook["type"] == "discord":
            res = requests.post(
                url=webhook["url"],
                json={"content": message},
                timeout=30,
            )
            if not res.ok:
                warnings.warn(f"Failed to send message to discord: {res.text}")
        elif webhook["type"] == "slack":
            res = requests.post(
                url=webhook["url"],
                headers={"Content-Type": "application/json"},
                json={"attachments": [{"text": message}]},
                timeout=30,
            )
        else:
            warnings.warn(f"Unknown webhook type: {webhook}")
