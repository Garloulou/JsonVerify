def estimate_bytes(text):
    repls = [('é','Ğ'),('è','ò'),('ê','¿'),('ô','Æ'),('É','Ņ'),
             ('È','Ũ'),('Î','£'),('Ô','ō'),('Û','ĵ'),('œ','ë'),('Œ','Ǩ')]
    for old, new in repls:
        text = text.replace(old, new)

    CTRL_TAGS = ["[SP]","\n","[E1]","[E2]","[E3]","[E4]","[1205]","[001E]",
                 "[1432]","[0014]","[0002]","[0010]","[NULL]"]
    count = 0
    i = 0
    while i < len(text):
        if text[i] == '[':
            if ']' not in text[i:]: return -1
            end = text.index(']', i)
            tag = text[i:end+1]
            if tag == "[NULL]":
                i = end + 1
                continue
            found = (tag in CTRL_TAGS) or (tag.startswith("[U+") and len(tag)==8) or (len(tag)==6)
            count += 2 if found else len(tag[1:-1]) * 2
            i = end + 1
        else:
            count += 2
            i += 1
    return count
