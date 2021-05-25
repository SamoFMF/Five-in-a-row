from logika import *
from minimax import *
from typing import List

def odigraj_igro(algorithms: List[Minimax], igra=None):
    G = Logika() if igra is None else igra
    casi = {alg.ime: 0 for alg in algorithms}
    casi_max = {alg.ime: -float("inf") for alg in algorithms}
    st_potez = -G.stevilo_potez
    while G.trenutno_stanje == NI_KONEC:
        for alg in algorithms:
            p, cas = alg.izracunaj_potezo_test(G.kopija())
            casi[alg.ime] += cas
            casi_max[alg.ime] = max(casi_max[alg.ime], cas)
        G.odigraj_potezo(p)
    st_potez += G.stevilo_potez
    for alg in casi:
        casi[alg] = round(1000 * casi[alg] / st_potez)
    return casi, casi_max

def izpisi_case_old(imena, casi, f):
    maxlen = max(max(len(i) for i in imena), 9)
    for globina in casi:
        strglobina = f"globina ="
        dx = maxlen - len(strglobina)
        dleft = dx // 2
        dright = dleft + (dx%2 == 1)
        line = " " * dleft + strglobina + " " * dright + "| "
        for ime in imena:
            line += " " + ime + " "
        print(line)
        print("=" * len(line))
        casi_globina = {ime: 0 for ime in imena}
        for p in casi[globina]:
            for ime in casi[globina][p]:
                casi_globina[ime] = f(casi[globina][p][ime], casi_globina[ime], len(imena))
        lines = {ime: "" for ime in imena}

def izpisi_case(imena, casi, f):
    maxlen = max(max(len(i) for i in imena), 7)
    lines = {}
    maxlens = {globina: len(str(max(casi[globina][p][ime] for p in casi[globina] for ime in casi[globina][p]))) for globina in casi}
    line = "globina"
    dx = maxlen - len(line)
    dright = dx // 2
    dleft = dright + (dx%2 == 1)
    line = " " * dleft + line + " " * (1+dright) + "| "
    for globina in casi:
        strg = str(globina)
        dx = maxlens[globina] - len(strg)
        dleft =  dx // 2
        dright = dleft + (dx%2 == 1)
        line += " " * (1+dleft) + strg + " " * (1+dright)
    print(line)
    print("=" * len(line))
    for ime in imena:
        line = " " * (maxlen - len(ime)) + ime + " | "
        for globina in casi:
            cas = 0
            for c in casi[globina].values():
                cas = f(cas, c[ime], len(imena))
            cas = str(cas)
            dx = maxlens[globina] - len(cas)
            dleft = dx // 2
            dright = dleft + (dx%2 == 1)
            line += " " * (1+dleft) + cas + " " * (1+dright)
        lines[ime] = line
        print(line)
    

# algoritmi_imena = ["minimax", "alphabeta", "negamax", "negascout", "negamax_memo", "negascout_memo"]
# algoritmi_imena = ["negamax", "negamax_memo"]
algoritmi_imena = ["alphabeta", "negamax", "negascout", "negamax_memo", "negascout_memo"]

casi = {}
casi_max = {}
algoritmi = [Minimax(0, ime) for ime in algoritmi_imena]
for globina in range(1, 5):
    print(f"GLOBINA = {globina}")
    casi[globina] = {}
    casi_max[globina] = {}
    algoritmi = [Minimax(globina, ime) for ime in algoritmi_imena]
    # for alg in algoritmi:
    #     alg.max_globina = globina
    for p in [i+1 for i in range(7)] + [-i-1 for i in range(7)]:
        print(p)
        G = Logika()
        G.odigraj_potezo(p)
        c, cmax = odigraj_igro(algoritmi, G)
        casi[globina][p] = c
        casi_max[globina][p] = cmax
    print()
print(casi)
print()

izpisi_case(algoritmi_imena, casi, lambda x,y,z: round((x+y) / z))
print()
izpisi_case(algoritmi_imena, casi, lambda x,y,z: max(x,y))