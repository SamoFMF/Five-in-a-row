# MINIMAX METODA ZA RESEVANJE PET V VRSTO

from logika import *
from random import random

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
    
    def vrednost_polozaja(self):
        return 1
    
    def minimax(self, globina, maximize):
        '''Metoda minimax.
        Sprejme:
            -globina [int]: globina na kateri se nahajamo
            -maximize [bool]: True, ce maksimiziramo, False, ce minimiziramo
        Vrne:
            -poteza [tuple(int,int)]: najboljsa poteza
            -score [int]: vrednost vrnjene poteze'''
        
        if self.prekinitev:
            # Igro moramo prekiniti - TODO - premisli, ce raje (None, 0)
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