"""Consistent rules for expression types (applied in assemble.py).

phrasal verb = a verb that forms a unit with a particle, a preposition and/or 'zich':
  separable compounds (meedoen, opgeven), prepositional verbs (kijken naar, afhangen van),
  reflexive verbs with a preposition (zich bemoeien met). Placeholders (iets, iemand, ergens, er)
  may appear. Anything built around a noun or adjective (bezig zijn met, rekening houden met,
  op basis van, vies zijn van) is NOT a phrasal verb: it becomes a collocation unless it was
  labeled idiom.
OVERRIDES fixes individual items by hand: {expression (lowercase): type}.
"""
import re

FILLERS = {"zich", "iets", "iemand", "ergens", "er", "je", "me", "mij", "jezelf", "zichzelf",
           "erop", "ervan", "erin", "eraan", "erover", "ermee", "ervoor", "erbij", "eruit", "erdoor",
           "ertoe", "erom", "ernaar", "eromheen", "ertussenuit", "het", "weer", "elkaar"}
PARTICLES = {"aan", "af", "op", "in", "uit", "mee", "om", "over", "toe", "terug", "weg", "door",
             "voor", "na", "bij", "tegen", "naar", "van", "met", "tot", "onder", "achter", "boven",
             "langs", "rond", "samen", "binnen", "buiten", "heen", "neer", "voorbij", "vast", "los",
             "uiteen", "vooruit", "achteruit", "omhoog", "omlaag", "tussen", "toe", "bijeen",
             "teweeg", "tegemoet", "kwijt", "thuis", "open", "dicht", "aaneen", "op/tot", "om/tot",
             "als", "overheen", "bovenop", "opzij", "overeind", "beet", "uit/van"}
NOT_PV_VERBS = {"zijn", "hebben", "worden", "raken", "staan", "liggen", "zitten", "maken",
                "doen", "nemen", "geven", "krijgen", "houden", "brengen", "stellen", "leggen",
                "zetten", "komen", "gaan", "vinden", "lopen", "spelen", "voeren"}
SHORT_VERBS = {"gaan", "staan", "doen", "zien", "slaan", "zijn", "verslaan", "ontstaan", "bestaan"}
# hand-checked items the rules can't decide
OVERRIDES = {
    "overeenkomen": "phrasal verb", "overeenstemmen": "phrasal verb", "plaatsnemen": "phrasal verb",
    "gereedmaken": "phrasal verb", "toevoegen": "phrasal verb", "tegemoet zien": "phrasal verb",
    "kiezen tussen": "phrasal verb", "stemmen voor/tegen": "phrasal verb",
    "ervoor kiezen om": "phrasal verb", "tot iemand doordringen": "phrasal verb",
    "internetten": "collocation", "winkelen": "collocation", "fietsrijden": "collocation",
    "paardrijden": "collocation", "touwtjespringen": "collocation",
    "inademen / uitademen": "phrasal verb",
    "te voorschijn komen": "collocation", "zich staande houden": "idiom",
    "zich laten verleiden tot": "collocation",
    "zich": "phrasal verb",  # 'zich (aan)kleden', shortened by the parenthesis
    "de rust bewaren": "collocation",
    "dikke vrienden": "collocation",
    "dom geluk": "collocation",
    "frisse lucht scheppen": "collocation",
    "geen wonder": "collocation",
    "in de handen klappen": "collocation",
    "in de weg staan": "collocation",
    "in grote lijnen": "collocation",
    "in mijn eentje": "collocation",
    "in slaap vallen": "collocation",
    "op de hoogte": "collocation",
    "op grote schaal": "collocation",
    "op je gemak": "collocation",
    "prijs stellen op": "collocation",
    "stand houden": "collocation",
    "te hulp komen": "collocation",
    "ter wereld komen": "collocation",
    "tot mijn spijt": "collocation",
    "van plan zijn": "collocation",
    "zijn uiterste best doen": "collocation",
    "het giet": "collocation",
    "het is uit": "collocation",
    "in acht nemen": "collocation",
    "kippenvel": "collocation",
    "geen steek": "collocation",
    "neem me niet kwalijk": "collocation",
    "nu eenmaal": "collocation",
    "kruis of munt": "collocation",
    "rang en stand": "collocation",
    "lusten en lasten": "collocation",
    "bij nader inzien": "collocation",
    "stapel zijn op": "idiom",
    "het hout is vergaan": "idiom",
    "dat is vers twee": "idiom",
    "een grote bek hebben": "idiom",
    "in beton gegoten": "idiom",
    "berg je maar": "idiom",
    "met de schrik vrijkomen": "idiom",
    "een vuist maken": "idiom",
    "het witte doek": "idiom",
    "te kijk zetten": "idiom",
    "gretig aftrek vinden": "idiom",
    "op de voorgrond treden": "idiom",
    "tussen haakjes": "idiom", "alarm slaan": "idiom", "in godsnaam": "idiom",
    "stalen zenuwen": "idiom",
    "zich thuis voelen": "collocation", "zich naar voelen": "collocation",
    "dwars zitten": "phrasal verb", "afgezien van": "collocation",
    "borrelen": "collocation", "knipperen": "collocation", "liften": "collocation",
    "ontbijten": "collocation", "verbranden": "collocation", "verdwalen": "collocation",
    "stofzuigen": "collocation", "ondertekenen": "collocation", "in lachen uitbarsten": "collocation",
}


def is_verb(tok: str) -> bool:
    return tok.endswith("en") or tok in SHORT_VERBS or tok.endswith("aan") or tok.endswith("oen") \
        or tok.endswith("ien")


def is_phrasal_verb(expr: str) -> bool:
    toks = [t for t in re.split(r"[\s/]+", expr.lower().strip(" .!?…")) if t]
    toks = [t for t in toks if t not in ("...", "…")]
    if not toks:
        return False
    if len(toks) == 1:
        t = toks[0]
        # a single compound verb: particle + verb (meedoen, opgeven, terugkomen, wijsmaken)
        return is_verb(t) and len(t) > 5
    verbs = [t for t in toks if t not in FILLERS and t not in PARTICLES]
    if len(verbs) != 1 or not is_verb(verbs[0]):
        return False
    v = verbs[0]
    rest = [t for t in toks if t != v]
    has_er = any(t.startswith("er") and t in FILLERS for t in rest)
    compound = any(v.startswith(p) and len(v) > len(p) + 3 for p in PARTICLES | {"beet", "dwars"})
    if not any(t in PARTICLES for t in rest) and "zich" not in rest and not has_er and not compound:
        return False
    # light verbs + particle only count when the particle makes a new verb (opgaan, aankomen):
    # with a separate preposition but no reflexive they're still prepositional verbs (gaan over)
    return True


def normalize(expr: str, kind: str) -> str:
    e = expr.lower().strip()
    if e in OVERRIDES:
        return OVERRIDES[e]
    if kind == "phrasal verb" and not is_phrasal_verb(e):
        return "collocation"
    # collocations are only promoted for reflexive verbs ('zich bevinden', 'zich iets herinneren');
    # other promotions go through OVERRIDES (nouns ending in -en look like verbs to the rules)
    if kind == "collocation" and e.startswith("zich ") and is_phrasal_verb(e):
        return "phrasal verb"
    return kind


def normalize_field(value: str) -> str:
    out = []
    for part in str(value).split("|"):
        if "=" in part:
            e, k = part.rsplit("=", 1)
            out.append(f"{e.strip()} = {normalize(e.strip(), k.strip())}")
    return " | ".join(out)
