def concat_dict(dict):
    rez = b''
    for key, val in dict.items():
        rez += dict[key]
    return rez
