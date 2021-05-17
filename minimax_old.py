# MINIMAX METODA ZA RESEVANJE PET V VRSTO

from logika import *
from random import random, shuffle

class Minimax:
    def __init__(self, globina):
        self.max_globina = globina # Maksimalna globina iskanja
        self.prekinitev = False # Ce zelimo iskanje predcasno koncati
        self.igra: Logika = None # Razred Logika, kjer imamo shranjeno igro
        self.jaz = None # Igralec, ki ga igramo
        self.poteza = None # Sem vpisemo potezo, ko jo najdemo

        # Vrednosti igre
        self.ZMAGA = 10**5
        self.NESKONCNO = self.ZMAGA + 1 # Karkoli, kar je vec kot zmaga
        self.k = lambda: 1 - self.igra.stevilo_potez / (2*MAX_POTEZ)
        self.bias = 0.8 # Koliko manj so mi vredne nasprotnikove tocke
    
    def prekini(self):
        '''Metoda, ki jo klicemo, ko zelimo, da algoritem preneha z iskanjem.'''
        self.prekinitev = True
    
    def dodaj_igro(self, igra, jaz):
        self.igra = igra
        self.jaz = jaz
    
    def posodobi_vrednosti(self, zmaga, k=None):
        self.ZMAGA = zmaga
        self.NESKONCNO = self.ZMAGA + 1
        if k is not None:
            self.k = k
    
    def preveri_smer(self, p, dx, dy, obiskani):
        obiskani.add(p)
        x,y = p
        igralec = self.igra.board[p]
        povezanih = 1 # p bo vedno povezan
        prostih = 0 # Stevilo prostih polj na vsaki strani
        x = (x+dx) % DIM_X
        y = (y+dy) % DIM_Y
        pi = (x,y)
        while povezanih < 5 and pi in self.igra.board and self.igra.board[pi] == igralec:
            povezanih += 1
            obiskani.add(pi)
            x = (x+dx) % DIM_X
            y = (y+dy) % DIM_Y
            pi = (x,y)
        while pi != p and pi not in self.igra.board:
            prostih += 1
            x = (x+dx) % DIM_X
            y = (y+dy) % DIM_Y
            pi = (x,y)
        if pi == p:
            # Prisli smo okoli, ce gremo sedaj v obratno smer, bomo 2-krat steli vse
            return povezanih, prostih
        x,y = p
        x = (x-dx) % DIM_X
        y = (y-dy) % DIM_Y
        pi = (x,y)
        while povezanih < 5 and pi in self.igra.board and self.igra.board[pi] == igralec:
            povezanih += 1
            obiskani.add(pi)
            x = (x-dx) % DIM_X
            y = (y-dy) % DIM_Y
            pi = (x,y)
        while pi not in self.igra.board: # pogoj pi != p lahko izpustimo, ker ce bi lahko prisli okoli, sploh ne bi bili tukaj
            prostih += 1
            x = (x-dx) % DIM_X
            y = (y-dy) % DIM_Y
            pi = (x,y)
        return povezanih, prostih
    
    def preveri_potezo(self, p):
        smeri = [(0,1), (1,0), (1,1), (1,-1)] # Mozne smeri

        for dx,dy in smeri:
            pass

    def vrednost_polozaja(self):
        smeri = [(0,1), (1,0), (1,1), (1,-1)] # Mozne smeri
        obiskani = set()
        vrednosti = [0, 0] # Vrednosti za [mi, nasprotnik]

        for p,_ in self.igra.zgodovina:
            if p in obiskani:
                continue
            vrednost = 0
            for dx,dy in smeri:
                povezanih, prostih = self.preveri_smer(p, dx, dy, obiskani)
                if povezanih + prostih < 5:
                    # V to smer ni mozno vec dobiti resitve
                    continue
                elif povezanih == 5:
                    # Sem naj ne bi prisli, ker je igre konec in to minimax/alphabeta ze prej zaznata
                    assert False, "Tukaj ne bi smeli biti!"
                else:
                    vrednost += povezanih / 5
                    vrednost += prostih / 10
            if self.igra.board[p] == self.jaz:
                vrednosti[0] += vrednost
            else:
                vrednosti[1] += vrednost
        
        return vrednosti[0] - self.bias * vrednosti[1]
    
    def minimax(self, globina, maximize):
        '''Metoda minimax.
        Sprejme:
            -globina [int]: globina na kateri se nahajamo
            -maximize [bool]: True, ce maksimiziramo, False, ce minimiziramo
        Vrne:
            -poteza [tuple(int,int)]: najboljsa poteza
            -vrednost [int]: vrednost vrnjene poteze'''
        
        if self.prekinitev:
            # Igro moramo prekiniti - TODO: premisli, ce raje (None, 0)
            if maximize:
                return None, -self.NESKONCNO
            else:
                return None, self.NESKONCNO
        
        # Preverimo najprej, ce je igre konec
        zmagovalec = self.igra.trenutno_stanje
        if zmagovalec != NI_KONEC:
            # Igre je konec
            if zmagovalec == self.jaz:
                return None, self.ZMAGA * self.k()
            elif zmagovalec == NEODLOCENO:
                return None, 0
            else:
                return None, -self.ZMAGA * self.k()
        elif globina == self.max_globina:
            # Prisli smo do max globine in igre ni konec - vrnemo hevristicno vrednost polozaja
            return None, self.vrednost_polozaja()
        elif maximize:
            # Iscemo globlje in maksimiziramo
            max_vrednost = -self.NESKONCNO
            najboljsa_poteza = None
            for p in [i for i in self.igra.veljavne_poteze]:
                self.igra.odigraj_potezo(p)
                _, vrednost = self.minimax(globina+1, not maximize)
                self.igra.razveljavi_potezo()
                if vrednost > max_vrednost or (vrednost == max_vrednost and random() > 0.5):
                    max_vrednost = vrednost
                    najboljsa_poteza = p
            return najboljsa_poteza, max_vrednost
        else:
            # Iscemo globlje in minimiziramo
            min_vrednost = self.NESKONCNO
            najboljsa_poteza = None
            for p in [i for i in self.igra.veljavne_poteze]:
                self.igra.odigraj_potezo(p)
                _, vrednost = self.minimax(globina+1, not maximize)
                self.igra.razveljavi_potezo()
                if vrednost < min_vrednost or (vrednost == min_vrednost and random() > 0.5):
                    min_vrednost = vrednost
                    najboljsa_poteza = p
            return najboljsa_poteza, min_vrednost
    
    def kljuc(self, p):
        '''Izracuna vrednost, ki se uporabi za primerjavo možnih potez.'''
        # IDEJA: Najprej preverimo tiste poteze, ki so del "ideje/resitve", ki jo
        # skusamo doseci mi trenutno (torej z naso zadnjo potezo) ali pa nasprotnik

        p1 = self.igra.zgodovina[-1][0] # Nasprotnikova zadnja poteza
        # d = abs(p[0]-p1[0]) + abs(p[1]-p1[1])
        dx = abs(p[0]-p1[0])
        dy = abs(p[1]-p1[1])
        d1 = (dx+dy) * (1+min(dx, dy, abs(dx-dy))) # d = 0, ce v/na isti vrstici/stolpcu/diagonali
        d1 += 1-self.bias # pristejemo vr < 1, ker bolj tezimo k nasi zmagi kot prepricitvi
        # d1 += dx+dy # Pristejemo se oddaljenost p od p1
        if len(self.igra.zgodovina) == 1:
            return d1
        p2 = self.igra.zgodovina[-1][0]
        dx = abs(p[0]-p2[0])
        dy = abs(p[1]-p2[1])
        d2 = (dx+dy) * (1+min(dx, dy, abs(dx-dy)))
        # d2 += dx+dy
        return min(d1, d2)

    def alphabeta(self, globina, alpha, beta, maximize):
        '''Metoda minimax z alpha-beta rezanjem
        Sprejme:
            -globina [int]: globina na kateri se nahajamo
            -alpha [float]: najslabsa mozna vrednost?
            -beta [float]: najboljsa mozna vrednost?
            -maximize [bool]: True, ce maksimiziramo, False, ce minimiziramo
        Vrne:
            -poteza [tuple(int,int)]: najboljsa poteza
            -vrednost [int]: vrednost vrnjene poteze'''
        if self.prekinitev:
            # Igro moramo prekini - TODO: premisli, ce raje (None, 0)
            if maximize:
                return None, -self.NESKONCNO
            else:
                return None, self.NESKONCNO
        
        # Preverimo najprej, ce je igre konec
        zmagovalec = self.igra.trenutno_stanje
        if zmagovalec != NI_KONEC:
            # Igre je konec
            if zmagovalec == self.jaz:
                return None, self.ZMAGA * self.k()
            elif zmagovalec == NEODLOCENO:
                return None, 0
            else:
                return None, -self.ZMAGA * self.k()
        elif globina == self.max_globina:
            # Prisli smo do max globine in igre ni konec - vrnemo hevristicno vrednost polozaja
            return None, self.vrednost_polozaja()
        elif maximize:
            # Iscemo globlje in maksimiziramo
            max_vrednost = -self.NESKONCNO
            najboljsa_poteza = None
            # poteze = [i for i in self.igra.veljavne_poteze]
            # shuffle(poteze)
            for p in sorted([i for i in self.igra.veljavne_poteze], key=self.kljuc):
                self.igra.odigraj_potezo(p)
                _, vrednost = self.alphabeta(globina+1, alpha, beta, False)
                self.igra.razveljavi_potezo()
                if vrednost > max_vrednost:
                    max_vrednost = vrednost
                    najboljsa_poteza = p
                alpha = max(alpha, max_vrednost)
                if alpha >= beta:
                    break
            return najboljsa_poteza, max_vrednost
        else:
            # Iscemo globlje in minimiziramo
            min_vrednost = self.NESKONCNO
            najboljsa_poteza = None
            # poteze = [i for i in self.igra.veljavne_poteze]
            # shuffle(poteze)
            for p in sorted([i for i in self.igra.veljavne_poteze], key=self.kljuc):
                self.igra.odigraj_potezo(p)
                _, vrednost = self.alphabeta(globina+1, alpha, beta, True)
                self.igra.razveljavi_potezo()
                if vrednost < min_vrednost:
                    min_vrednost = vrednost
                    najboljsa_poteza = p
                beta = min(beta, min_vrednost)
                if beta <= alpha:
                    break
            return najboljsa_poteza, min_vrednost

G = Logika()
G.odigraj_potezo((0,0))
G.odigraj_potezo((0,7))
G.odigraj_potezo((0,6))
G.odigraj_potezo((0,1))
G.odigraj_potezo((7,2))

G.odigraj_potezo((7,3))
G.odigraj_potezo((6,4))
G.odigraj_potezo((7,1))
G.odigraj_potezo((1,2))
G.odigraj_potezo((2,2))

G.odigraj_potezo((3,3))
G.odigraj_potezo((1,6))
G.odigraj_potezo((6,3))
G.odigraj_potezo((7,6))
G.odigraj_potezo((6,7))

G.odigraj_potezo((5,0))
G.odigraj_potezo((2,3))
G.odigraj_potezo((6,6))
G.odigraj_potezo((2,7))
G.odigraj_potezo((5,6))

G.odigraj_potezo((7,0))
G.odigraj_potezo((3,7))
G.odigraj_potezo((6,2))
G.odigraj_potezo((2,0))

G.odigraj_potezo((6,5))

print(G.na_potezi)

from time import time

M = Minimax(4)
M.dodaj_igro(G.kopija(), G.na_potezi)
print(sorted([i for i in M.igra.veljavne_poteze], key=M.kljuc))
# print(M.minimax(0, True))
t = time()
# print(M.alphabeta(0, -float("inf"), float("inf"), True))
# print(M.alphabeta(0, -M.ZMAGA / 2, M.ZMAGA / 2, True))
print(time()-t)
# G = Logika()

# M = Minimax(4)
# M.dodaj_igro(G.kopija(), IGRALEC_1)
# print(M.minimax(0, True))
# print(M.alphabeta(0, -float("inf"), float("inf"), True))

G = Logika()
G.odigraj_potezo((0,0))
M = Minimax(4)
i = 1
while G.na_potezi is not None:
    M.dodaj_igro(G.kopija(), G.na_potezi)
    t = time()
    p,val = M.alphabeta(0, -float("inf"), float("inf"), True)
    print(f"Poteza {i} || Igralec {G.na_potezi}: {p} = {val} || {round((time()-t) * 1000)}ms")
    G.odigraj_potezo(p)
    i += 1