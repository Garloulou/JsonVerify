# -*- coding: utf-8 -*-

def estimate_bytes(text):
    """
    Calcule la taille en bytes d'une chaîne selon les règles spécifiques
    du moteur de Persona 2: Innocent Sin (PSP).

    - Chaque caractère standard = 2 bytes.
    - Les balises reconnues ([SP], [E1], ...) = 2 bytes.
    - Les balises [U+XXXX] (8 caractères) = 2 bytes.
    - Les balises entre crochets de 6 caractères (ex: [1205]) = 2 bytes.
    - [NULL] est ignoré (0 byte).
    - Les balises entre chevrons <XXXX> (4 caractères alphanumériques) = 2 bytes.
    - <NULL> est ignoré (0 byte).
    - Toute autre balise non reconnue est comptée caractère par caractère (2 bytes chacun).
    - Retourne -1 si une balise '[' n'est pas fermée.
    """

    # Remplacements pour les caractères spéciaux (encodage propriétaire)
    repls = [
        ('챕','휒'), ('챔','챵'), ('챗','쩔'), ('척','횈'), ('횋','흧'),
        ('횊','큠'), ('횓','짙'), ('횚','흲'), ('횤','캔'), ('흹','챘'), ('흸','푭')
    ]
    for old, new in repls:
        text = text.replace(old, new)

    # Balises reconnues entre crochets
    CTRL_TAGS_BRACKETS = [
        "[SP]", "\n", "[E1]", "[E2]", "[E3]", "[E4]",
        "[1205]", "[001E]", "[1432]", "[0014]", "[0002]", "[0010]",
        "[NULL]", "[1109]", "[1208]", "[1107]", "[1108]",
        "[1112]", "[1113]", "[120C]", "[120D]", "[120E]",
        "[120F]", "[1210]", "[121E]"
    ]

    count = 0
    i = 0
    L = len(text)

    while i < L:
        ch = text[i]

        # --- Balises entre crochets ---
        if ch == '[':
            if ']' not in text[i:]:
                return -1
            end = text.index(']', i)
            tag = text[i:end+1]

            if tag == "[NULL]":
                i = end + 1
                continue

            is_known = (
                tag in CTRL_TAGS_BRACKETS or
                (tag.startswith("[U+") and len(tag) == 8) or
                (len(tag) == 6)
            )
            count += 2 if is_known else len(tag[1:-1]) * 2
            i = end + 1
            continue

        # --- Balises entre chevrons ---
        if ch == '<':
            if '>' not in text[i:]:
                count += 2
                i += 1
                continue

            end = text.index('>', i)
            tag = text[i:end+1]

            if tag == "<NULL>":
                i = end + 1
                continue

            inner = tag[1:-1]
            if len(tag) == 6 and inner.isalnum():
                count += 2
                i = end + 1
                continue

            count += len(tag) * 2
            i = end + 1
            continue

        # --- Caractère standard ---
        count += 2
        i += 1

    return count