# MINIMAX METODA ZA RESEVANJE PET V VRSTO

from logika import *
from random import random
from time import time

class Minimax:
    TABELA_VREDNOSTI = {0: 0, 1: 1, 2: 2.5, 3: 4, 4: 6} # Tabela vrednosti povezanih k-terk
    POVEZANI_FAKTORJI = {0: 0, 1: 1, 2: 1.25, 3: 1.33, 4: 1.5} # Tabela faktorjev za pomnoziti st. povezanih in prostih

    PETKE = []
    for x in range(NUM_COLS):
        for y in range(NUM_ROWS):
            horizontalna = [None]*5; vertikalna = [None]*5; diagonala_gor = [None]*5; diagonala_dol = [None]*5
            for i in range(5):
                horizontalna[i] = ((x+i) % NUM_COLS, y)
                vertikalna[i] = (x, (y+i) % NUM_ROWS)
                diagonala_gor[i] = ((x+i) % NUM_COLS, (y+i) % NUM_ROWS)
                diagonala_dol[i] = ((x+i) % NUM_COLS, (y-i) % NUM_ROWS)
            PETKE.append(tuple(horizontalna))
            PETKE.append(tuple(vertikalna))
            PETKE.append(tuple(diagonala_gor))
            PETKE.append(tuple(diagonala_dol))
    PETKE = tuple(PETKE)

    # Table flags
    EXACT = "exact"
    UPPERBOUND = "upperbound"
    LOWERBOUND = "lowerbound"

    def __init__(self, globina, metoda="alphabeta"):
        self.max_globina = globina # Maksimalna globina iskanja
        self.prekinitev = False # Ce zelimo iskanje predcasno koncati
        self.igra: Logika = None # Razred Logika, kjer imamo shranjeno igro
        self.jaz = None # Igralec, ki ga igramo
        self.poteza = None # Sem vpisemo potezo, ko jo najdemo
        self.algoritem = None
        self.tabela = {}
        self.ime = metoda
        if metoda == "minimax":
            self.algoritem = lambda g: self.minimax(g, True)
        elif metoda == "alphabeta":
            self.algoritem = lambda g: self.alphabeta(g, -float("inf"), float("inf"), True)
        elif metoda == "negamax":
            self.algoritem = lambda g: self.negamax(g, -float("inf"), float("inf"), 1)
        elif metoda == "negascout":
            self.algoritem = lambda g: self.negascout(g, -float("inf"), float("inf"), 1)
        elif metoda == "negamax_memo":
            self.algoritem = lambda g: self.negamax_transposition(g, -float("inf"), float("inf"), 1)
        elif metoda == "negascout_memo":
            self.algoritem = lambda g: self.negascout_transposition(g, -float("inf"), float("inf"), 1)

        # Vrednosti igre
        self.ZMAGA = 10**5
        self.NESKONCNO = self.ZMAGA + 1 # Karkoli, kar je vec kot zmaga
        self.k = lambda: 1 - self.igra.stevilo_potez / (2*MAX_POTEZ)
        self.bias = 0.9 # Koliko manj so mi vredne nasprotnikove tocke
    
    def prekini(self):
        '''Metoda, ki jo klicemo, ko zelimo, da algoritem preneha z iskanjem.'''
        self.prekinitev = True
    
    def izracunaj_potezo(self, igra):
        '''Izracuno potezo za trenutno stanje podane igre.
        Uporabi metodo self.algoritem.'''
        self.igra = igra
        self.jaz = self.igra.na_potezi
        self.prekinitev = False # Glavno vlakno bo nastavilo to na True, ce bomo morali prekiniti
        self.poteza = None # Sem vpisemo potezo, ko jo najdemo

        # # Pozenemo minimax/alphabeta na z iterative deepening
        # if self.pruning:
        #     poteza, vrednost = self.alphabeta(self.max_globina, -float("inf"), float("inf"), True)
        # else:
        #     poteza, vrednost = self.minimax(self.max_globina, True)
        timestart = time()
        poteza, vrednost = self.algoritem(self.max_globina)
        timeend = time()
        
        self.igra = None
        self.jaz = None

        if not self.prekinitev:
            # Nismo bili prekinjeni => izvedemo potezo
            self.poteza = poteza
            # print(self.poteza, end=", ")
            print(f"Računalnik igra {poteza} z vrednostjo {round(vrednost, 2)}. Izračunano v {round((timeend-timestart)*1000)}ms.")
    
    def izracunaj_potezo_test(self, igra):
        '''Izracuno potezo za trenutno stanje podane igre.
        Uporabi metodo self.algoritem.'''
        self.igra = igra
        self.jaz = self.igra.na_potezi

        # # Pozenemo minimax/alphabeta na z iterative deepening
        # if self.pruning:
        #     poteza, vrednost = self.alphabeta(self.max_globina, -float("inf"), float("inf"), True)
        # else:
        #     poteza, vrednost = self.minimax(self.max_globina, True)
        timestart = time()
        poteza, _ = self.algoritem(self.max_globina)
        timeend = time()
        
        self.igra = None
        self.jaz = None

        return poteza, timeend-timestart
   
    def dodaj_igro(self, igra, jaz):
        self.igra = igra
        self.jaz = jaz
    
    def posodobi_vrednosti(self, zmaga, k=None):
        self.ZMAGA = zmaga
        self.NESKONCNO = self.ZMAGA + 1
        if k is not None:
            self.k = k
    
    def preveri_smer(self, x0, y0, dx, dy, obiskani):
        obiskani.add((x0,y0))
        igralec = self.igra.board[x0][y0]
        povezanih = 1 # p bo vedno povezan
        prostih = 0 # Stevilo prostih polj na vsaki strani
        x = (x0+dx) % NUM_COLS
        y = (y0+dy) % NUM_ROWS
        while povezanih < 5 and self.igra.board[x][y] == igralec:
            povezanih += 1
            # obiskani.add((x,y))
            x = (x+dx) % NUM_COLS
            y = (y+dy) % NUM_ROWS
        dvosmerno = 0
        while (x != x0 or y != y0) and self.igra.board[x][y] == PRAZNO:
            prostih += 1
            dvosmerno = 1
            x = (x+dx) % NUM_COLS
            y = (y+dy) % NUM_ROWS
        if (x,y) == (x0,y0):
            # Prisli smo okoli, ce gremo sedaj v obratno smer, bomo 2-krat steli vse
            return povezanih, prostih, False
        x = (x0-dx) % NUM_COLS
        y = (y0-dy) % NUM_ROWS
        while povezanih < 5 and self.igra.board[x][y] == igralec:
            povezanih += 1
            # obiskani.add((x,y))
            x = (x-dx) % NUM_COLS
            y = (y-dy) % NUM_ROWS
        while self.igra.board[x][y] == PRAZNO: # pogoj pi != p lahko izpustimo, ker ce bi lahko prisli okoli, sploh ne bi bili tukaj
            prostih += 1
            dvosmerno += 1
            x = (x-dx) % NUM_COLS
            y = (y-dy) % NUM_ROWS
        return povezanih, prostih, dvosmerno >= 2
    
    def preveri_potezo(self, p):
        smeri = [(0,1), (1,0), (1,1), (1,-1)] # Mozne smeri

        for dx,dy in smeri:
            pass
    
    def vrednost_polozaja_old(self):
        smeri = [(0,1), (1,0), (1,1), (1,-1)] # Mozne smeri
        obiskani = set()
        vrednosti = [0, 0] # Vrednosti za [mi, nasprotnik]

        for p in self.igra.zgodovina:
            x0,y0 = self.igra.pridobi_koordinate(p, True)
            if (x0,y0) in obiskani:
                continue
            vrednost = 0
            for dx,dy in smeri:
                povezanih, prostih, dvosmerno = self.preveri_smer(x0, y0, dx, dy, obiskani)
                if povezanih + prostih < 5:
                    # V to smer ni mozno vec dobiti resitve
                    continue
                elif povezanih == 5:
                    # Sem naj ne bi prisli, ker je igre konec in to minimax/alphabeta ze prej zaznata
                    assert False, "Tukaj ne bi smeli biti!"
                else:
                    if povezanih == 3 and dvosmerno:
                        vrednost += self.ZMAGA / 1000
                    else:
                        vrednost += povezanih # Vrednosti pristejemo dolzino povezanih pokritih barv v dani smeri
                        vrednost_prostih = prostih * (1+povezanih/5) / 2 # Prazno povezano polje je vredno pol pokritega | hkrati je vredno vec, ce je zraven daljsega pokritega zaporedja
                        if not dvosmerno:
                            vrednost_prostih /= 2 # Ce so prazna polja samo na eni strani verige, so vredna pol manj
                        vrednost += vrednost_prostih
            if self.igra.board[x0][y0] == self.jaz:
                vrednosti[0] += vrednost
            else:
                vrednosti[1] += vrednost
        return vrednosti[0] - self.bias * vrednosti[1]
    
    def vrednost_polozaja(self):
        vrednosti = [0, 0] # Vrednosti za [jaz, nasprotnik]

        for petka in Minimax.PETKE:
            # Preverimo vsako mozno zmagovalno petko
            barva = PRAZNO
            stevilo = 0
            for x, y in petka:
                if self.igra.board[x][y] == PRAZNO:
                    # Prazno mesto, ne naredimo nic
                    continue
                elif self.igra.board[x][y] == barva:
                    # Zapolnjeno mesto z opazovano barvo .. se moznost, da igralec (barva) zmaga s to petko
                    stevilo += 1
                elif barva == PRAZNO:
                    # Nasli smo zapolnjen polozaj in to je prvo neprazno polje v petki, ki smo ga nasli
                    barva = self.igra.board[x][y]
                    stevilo = 1
                else:
                    # V petki imata oba igralca po vsaj 1 odigrano potezo, torej ta petka vec ni izvedljiva
                    stevilo = -1
                    break
            # stevilo = 0 ... popolnoma prazna petka
            # stevilo > 0 ... v petki je (stevilo) polj pokritih z (barva), preostali so prosti => petka mozna za (barva)
            # stevilo < 0 ... petka ne more biti vec zmagovalna za nobenega igralca
            if stevilo > 0:
                vrednosti[1-barva==self.jaz] += stevilo**5 / 5
            elif stevilo == 0: # V prihodnosti se dostopna petka ... dlje kot smo v igri, manj je taksnih, tako da so ocene polozajev nizje => hocemo cimprej zmagati
                vrednosti[0] += 0.1
                vrednosti[1] += 0.1
            else:
                # Petka vec ni dosegljiva, ni vredna nic tock
                pass
        return vrednosti[0] - self.bias * vrednosti[1] # Nasprotnikova vrednost nam je pomembna nekoliko manj kot nasa
    
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
        elif globina == 0:
            # Prisli smo do max globine in igre ni konec - vrnemo hevristicno vrednost polozaja
            return None, self.vrednost_polozaja()
        elif maximize:
            # Iscemo globlje in maksimiziramo
            max_vrednost = -self.NESKONCNO
            najboljsa_poteza = None
            for p in [i for i in self.igra.veljavne_poteze]+[-i for i in self.igra.veljavne_poteze]:
                self.igra.odigraj_potezo(p)
                _, vrednost = self.minimax(globina-1, False)
                self.igra.razveljavi_potezo()
                if vrednost > max_vrednost or (vrednost == max_vrednost and random() > 0.5):
                    max_vrednost = vrednost
                    najboljsa_poteza = p
            return najboljsa_poteza, max_vrednost
        else:
            # Iscemo globlje in minimiziramo
            min_vrednost = self.NESKONCNO
            najboljsa_poteza = None
            for p in [i for i in self.igra.veljavne_poteze]+[-i for i in self.igra.veljavne_poteze]:
                self.igra.odigraj_potezo(p)
                _, vrednost = self.minimax(globina-1, True)
                self.igra.razveljavi_potezo()
                if vrednost < min_vrednost or (vrednost == min_vrednost and random() > 0.5):
                    min_vrednost = vrednost
                    najboljsa_poteza = p
            return najboljsa_poteza, min_vrednost
    
    def kljuc(self, p):
        '''Izracuna vrednost, ki se uporabi za primerjavo možnih potez.'''
        # IDEJA: Najprej preverimo tiste poteze, ki so del "ideje/resitve", ki jo
        # skusamo doseci mi/nasprotnik trenutno (torej z naso/njegovo zadnjo potezo)
        if len(self.igra.zgodovina) == 0:
            # Prva poteza, nakljucen vrstni red with slight bias proti centru
            center = NUM_COLS // 2
            return abs(abs(p)-center) + center * random()
        else:
            x0,y0 = self.igra.pridobi_koordinate(p) # Koordinate opazovane poteze
            x1,y1 = self.igra.pridobi_koordinate(self.igra.zgodovina[-1], True) # Koordinate zadnje odigrane poteze (posledicno je to nasprotnikova poteza)
            # dx = abs(x0-x1)
            # dy = abs(y0-y1)
            # d1 = (dx+dy) * (1+min(dx, dy, abs(dx-dy))) # d = 0, ce v/na isti vrstici/stolpcu/diagonali
            dx = min((x0-x1) % NUM_COLS, (x1-x0) % NUM_COLS)
            dy = min((y0-y1) % NUM_ROWS, (y1-y0) % NUM_ROWS)
            d1 = max(dx, dy)
            d1 += 1-self.bias # pristejemo vr < 1, ker bolj tezimo k nasi zmagi kot preprecitvi nasprotnikove
            if len(self.igra.zgodovina) == 1:
                return d1
            else:
                x2,y2 = self.igra.pridobi_koordinate(self.igra.zgodovina[-2], True)
                # dx = abs(x0-x2)
                # dy = abs(y0-y2)
                # d2 = (dx+dy) * (1 + min(dx, dy, abs(dx-dy)))
                dx = min((x0-x2) % NUM_COLS, (x2-x0) % NUM_COLS)
                dy = min((y0-y2) % NUM_ROWS, (y2-y0) % NUM_ROWS)
                d2 = max(dx, dy)
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
        elif globina == 0:
            # Prisli smo do max globine in igre ni konec - vrnemo hevristicno vrednost polozaja
            return None, self.vrednost_polozaja()
        elif maximize:
            # Iscemo globlje in maksimiziramo
            max_vrednost = -self.NESKONCNO
            najboljsa_poteza = None
            for p in sorted([i for i in self.igra.veljavne_poteze] + [-i for i in self.igra.veljavne_poteze], key=self.kljuc):
                self.igra.odigraj_potezo(p)
                _, vrednost = self.alphabeta(globina-1, alpha, beta, False)
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
            for p in sorted([i for i in self.igra.veljavne_poteze] + [-i for i in self.igra.veljavne_poteze], key=self.kljuc):
                self.igra.odigraj_potezo(p)
                _, vrednost = self.alphabeta(globina-1, alpha, beta, True)
                self.igra.razveljavi_potezo()
                if vrednost < min_vrednost:
                    min_vrednost = vrednost
                    najboljsa_poteza = p
                beta = min(beta, min_vrednost)
                if beta <= alpha:
                    break
            return najboljsa_poteza, min_vrednost
    
    def negamax(self, globina, alpha, beta, barva):
        if self.prekinitev:
            # Igro moramo prekiniti
            return self.NESKONCNO * barva
        
        # Preverimo najprej, ce je igre konec
        zmagovalec = self.igra.trenutno_stanje
        if zmagovalec != NI_KONEC:
            # Igre je konec
            if zmagovalec == self.jaz:
                return None, barva * self.ZMAGA * self.k()
            elif zmagovalec == NEODLOCENO:
                return None, 0
            else:
                return None, barva * (-self.ZMAGA) * self.k()
        elif globina == 0:
            # Prisli smo do max globine in igre ni konec - vrnemo hevristicno vrednost polozaja
            return None, barva * self.vrednost_polozaja()
        else:
            # Iscemo globlje
            max_vrednost = -float("inf")
            najboljsa_poteza = None
            for p in sorted([i for i in self.igra.veljavne_poteze] + [-i for i in self.igra.veljavne_poteze], key=self.kljuc):
                self.igra.odigraj_potezo(p)
                _, vrednost = self.negamax(globina-1, -beta, -alpha, -barva)
                vrednost = -vrednost
                self.igra.razveljavi_potezo()
                if vrednost > max_vrednost:
                    max_vrednost = vrednost
                    najboljsa_poteza = p
                alpha = max(alpha, max_vrednost)
                if alpha >= beta:
                    break
            return najboljsa_poteza, max_vrednost
    
    def get_hash(self):
        '''Vrne board, ki je seznam seznamov intov, v obliki tupla tuplov, da ga lahko uporabimo v dictionary.'''
        return tuple(tuple(i) for i in self.igra.board)
    
    def negamax_transposition(self, globina, alpha, beta, barva):
        if self.prekinitev:
            # Igro moramo prekiniti
            return self.NESKONCNO * barva
        
        alpha_original = alpha

        hash = self.get_hash()
        if hash in self.tabela and self.tabela[hash]["globina"] >= globina:
            flag = self.tabela[hash]["flag"]
            if flag == Minimax.EXACT:
                return self.tabela[hash]["poteza"], self.tabela[hash]["vrednost"]
            elif flag == Minimax.LOWERBOUND:
                alpha = max(alpha, self.tabela[hash]["vrednost"])
            else:
                beta = min(beta, self.tabela[hash]["vrednost"])
            if alpha >= beta:
                return self.tabela[hash]["poteza"], self.tabela[hash]["vrednost"]
        
        # Preverimo najprej, ce je igre konec
        zmagovalec = self.igra.trenutno_stanje
        if zmagovalec != NI_KONEC:
            # Igre je konec
            if zmagovalec == self.jaz:
                return None, barva * self.ZMAGA * self.k()
            elif zmagovalec == NEODLOCENO:
                return None, 0
            else:
                return None, barva * (-self.ZMAGA) * self.k()
        elif globina == 0:
            # Prisli smo do max globine in igre ni konec - vrnemo hevristicno vrednost polozaja
            return None, barva * self.vrednost_polozaja()
        else:
            # Iscemo globlje
            max_vrednost = -float("inf")
            najboljsa_poteza = None
            for p in sorted([i for i in self.igra.veljavne_poteze] + [-i for i in self.igra.veljavne_poteze], key=self.kljuc):
                self.igra.odigraj_potezo(p)
                _, vrednost = self.negamax_transposition(globina-1, -beta, -alpha, -barva)
                vrednost = -vrednost
                self.igra.razveljavi_potezo()
                if vrednost > max_vrednost:
                    max_vrednost = vrednost
                    najboljsa_poteza = p
                alpha = max(alpha, max_vrednost)
                if alpha >= beta:
                    break
            
            # Shranimo v tabelo
            tt = {"globina": globina, "vrednost": max_vrednost, "poteza": najboljsa_poteza}
            if max_vrednost <= alpha_original:
                tt["flag"] = Minimax.UPPERBOUND
            elif max_vrednost >= beta:
                tt["flag"] = Minimax.LOWERBOUND
            else:
                tt["flag"] = Minimax.EXACT
            self.tabela[hash] = tt

            return najboljsa_poteza, max_vrednost
    
    def negascout(self, globina, alpha, beta, barva):
        if self.prekinitev:
            # Igro moramo prekiniti
            return self.NESKONCNO * barva
        
        # Najprej preverimo, ce je igre konec
        zmagovalec = self.igra.trenutno_stanje
        if zmagovalec != NI_KONEC:
            # Igre je konec
            if zmagovalec == self.jaz:
                return None, barva * self.ZMAGA * self.k()
            elif zmagovalec == NEODLOCENO:
                return None, 0
            else:
                return None, barva * (-self.ZMAGA) * self.k()
        elif globina == 0:
            # Prisli smo do max globine in igre ni konec - vrnemo hevristicno vrednost polozaja
            return None, barva * self.vrednost_polozaja()
        else:
            poteze = sorted([i for i in self.igra.veljavne_poteze] + [-i for i in self.igra.veljavne_poteze], key=self.kljuc)
            
            # Najprej naredimo prvo potezo
            self.igra.odigraj_potezo(poteze[0])
            najboljsa_poteza = poteze[0]
            _, vrednost = self.negascout(globina-1, -beta, -alpha, -barva)
            vrednost = -vrednost
            self.igra.razveljavi_potezo()
            alpha = max(alpha, vrednost)
            if alpha < beta:
                # Preverimo preostale poteze
                for p in poteze[1:]:
                    self.igra.odigraj_potezo(p)
                    _, vrednost = self.negascout(globina-1, -alpha-1, -alpha, -barva)
                    vrednost = -vrednost
                    if alpha < vrednost < beta:
                        _, vrednost = self.negascout(globina-1, -beta, -vrednost, -barva)
                        vrednost = -vrednost
                    self.igra.razveljavi_potezo()
                    if vrednost > alpha:
                        alpha = vrednost
                        najboljsa_poteza = p
                    if alpha >= beta:
                        break
            return najboljsa_poteza, alpha
    
    def negascout_transposition(self, globina, alpha, beta, barva):
        if self.prekinitev:
            # Igro moramo prekiniti
            return self.NESKONCNO * barva
        
        alpha_original = alpha

        hash = self.get_hash()
        if hash in self.tabela and self.tabela[hash]["globina"] >= globina:
            flag = self.tabela[hash]["flag"]
            if flag == Minimax.EXACT:
                return self.tabela[hash]["poteza"], self.tabela[hash]["vrednost"]
            elif flag == Minimax.LOWERBOUND:
                alpha = max(alpha, self.tabela[hash]["vrednost"])
            else:
                beta = min(beta, self.tabela[hash]["vrednost"])
            if alpha >= beta:
                return self.tabela[hash]["poteza"], self.tabela[hash]["vrednost"]
        
        # Najprej preverimo, ce je igre konec
        zmagovalec = self.igra.trenutno_stanje
        if zmagovalec != NI_KONEC:
            # Igre je konec
            if zmagovalec == self.jaz:
                return None, barva * self.ZMAGA * self.k()
            elif zmagovalec == NEODLOCENO:
                return None, 0
            else:
                return None, barva * (-self.ZMAGA) * self.k()
        elif globina == 0:
            # Prisli smo do max globine in igre ni konec - vrnemo hevristicno vrednost polozaja
            return None, barva * self.vrednost_polozaja()
        else:
            poteze = sorted([i for i in self.igra.veljavne_poteze] + [-i for i in self.igra.veljavne_poteze], key=self.kljuc)
            
            # Najprej naredimo prvo potezo
            self.igra.odigraj_potezo(poteze[0])
            najboljsa_poteza = poteze[0]
            _, vrednost = self.negascout(globina-1, -beta, -alpha, -barva)
            vrednost = -vrednost
            self.igra.razveljavi_potezo()
            alpha = max(alpha, vrednost)
            if alpha < beta:
                # Preverimo preostale poteze
                for p in poteze[1:]:
                    self.igra.odigraj_potezo(p)
                    _, vrednost = self.negascout(globina-1, -alpha-1, -alpha, -barva)
                    vrednost = -vrednost
                    if alpha < vrednost < beta:
                        _, vrednost = self.negascout(globina-1, -beta, -vrednost, -barva)
                        vrednost = -vrednost
                    self.igra.razveljavi_potezo()
                    if vrednost > alpha:
                        alpha = vrednost
                        najboljsa_poteza = p
                    if alpha >= beta:
                        break
            
            # Shranimo v tabelo
            tt = {"globina": globina, "vrednost": alpha, "poteza": najboljsa_poteza}
            if alpha <= alpha_original:
                tt["flag"] = Minimax.UPPERBOUND
            elif alpha >= beta:
                tt["flag"] = Minimax.LOWERBOUND
            else:
                tt["flag"] = Minimax.EXACT
            self.tabela[hash] = tt

            return najboljsa_poteza, alpha