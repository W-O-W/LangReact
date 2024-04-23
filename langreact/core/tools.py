from typing import List, TypeVar, Union

T = TypeVar("T")


def flatten_and_dropduplicate(value: Union[List[List[T]], List[T], T]) -> List[T]:
    if isinstance(value, List):
        res = []
        for v in value:
            res += flatten_and_dropduplicate(v)
        return list(set(res))
    else:
        return [
            value,
        ]

def clean_default_values(m : dict,**default_values):
    result = {}
    for k,v in m.items():
        if k in default_values and v == default_values[k]:
            pass
        else:
            if isinstance(v,list):
                elements = []
                for element in v:
                    if isinstance(element,dict):
                        elements.append(clean_default_values(element,**default_values))
                    else:
                        elements.append(element)
                result[k] = elements
            elif isinstance(v,dict):
                result[k] = clean_default_values(v,**default_values)
            elif v != "" and v is not None:
                result[k] = v
    return result


import time


def get_timer():
    def new_timer():
        start_time = time.time()
        while True:
            current = time.time()
            yield current - start_time
            start_time = current
    timer = new_timer()
    next(timer)
    return timer

def is_sub_match(text,search_text,skip_num = 2)->int:
    buffer = [1 if text[i] != search_text[0] else 0 for i in range(len(text))]
    for idx in range(1,len(search_text)):
        tmp = [(1 if text[0] != search_text[idx] else 0) + idx]
        for i in range(1,len(text)):
            if text[i] == search_text[idx]:
                tmp.append(buffer[i-1])
            else:
                tmp.append(min(buffer[i-1],tmp[i-1],buffer[i]) + 1)
        buffer = tmp
    for i in range(len(buffer)):
        if buffer[i] <= skip_num:
            return i

