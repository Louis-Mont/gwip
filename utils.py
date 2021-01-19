def l_to_str(ll: list):
    """
    :return: all elements separated by a `,`
    :rtype: str
    """
    rtn = ""
    for m in ll:
        rtn += f"{m},"
    return rtn[:-1]


def rev_col(col):
    d = {}
    for m in range(len(col)):
        d[col[m]] = m
    return d


def dict_to_str(d: dict):
    """
    :return: k,v each element of keys and values separated by a `,`
    :rtype: str,str
    """
    return l_to_str(d.keys()), l_to_str(d.values())


def kcv(d: dict, c: str, sep: str = ','):
    """
    :return: k and v between c, each iteration separated by sep
    :rtype: str
    """
    rtn = ""
    for k, v in d.items():
        rtn += f"{k}{c}{v}{sep}"
    rtn = rtn[:-len(sep)]
    return rtn
