# LOGIKA ZA IGRO PET V VRSTO
from collections import defaultdict

# KONSTANTE
IGRALEC_1 = 1
IGRALEC_2 = 2
PRAZNO = 0

NEODLOCENO = 3
NI_KONEC = 4

DIM_X = 8
DIM_Y = 8
MAX_POTEZ = DIM_X * DIM_Y

def nasprotnik(igralec):
    if igralec == IGRALEC_1:
        return IGRALEC_2
    elif igralec == IGRALEC_2:
        return IGRALEC_1
    else:
        assert False, f"neveljaven nasprotnik: {igralec}"

class Logika:
    def __init__(self, na_potezi=IGRALEC_1):
        # Ustvarimo igralno povrsino
        # To bo dict, kjer bodo kljuci koordinate, vrednosti pa barva (IGRALEC_1/IGRALEC_2/PRAZNO), defaut=PRAZNO
        self.board = dict()

        # Dolocimo igralca, ki je na potezi
        self.na_potezi = na_potezi

        # Veljavne poteze - na zacetku je to samo (0,0)
        self.veljavne_poteze = {(0,0)}

        # Zgodovina potez - par (poteza, novi), kjer je novi tuple z vsemi novimi veljavnimi potezami, ki jih je prinesla poteza
        self.zgodovina = []

        # Stevilo potez
        self.stevilo_potez = 0

        # Hranimo stanje igre in resitev, ce imamo zmagovalca
        self.trenutno_stanje = NI_KONEC
        self.petka = None
    
    def kopija(self):
        '''Vrne kopijo razreda.'''
        # Ustvarimo nov razred s trenutnim igralcem na potezi
        L = Logika(self.na_potezi)
        
        # Prenesemo položaj na igralni povrsini
        for pos in self.board:
            L.board[pos] = self.board[pos]
        
        # Prenesemo veljavne poteze
        L.veljavne_poteze = self.veljavne_poteze.copy()

        # Prenesemo zgodovino potez
        L.zgodovina = [i for i in self.zgodovina]

        # Prenesemo stevilo potez
        L.stevilo_potez = self.stevilo_potez

        # Prekopiramo se trenutno stanje
        L.trenutno_stanje = self.trenutno_stanje
        L.petka = self.petka

        return L
    
    def odigraj_potezo(self, p):
        '''Odigraj potezo p, ce je veljavna, sicer ne naredi nic.'''
        assert self.na_potezi is not None, "Igre je konec!"
        assert p in self.veljavne_poteze, "Neveljavna poteza!"

        # Odigramo potezo p in povecamo stevilo potez
        self.board[p] = self.na_potezi
        self.stevilo_potez += 1

        # Posodobimo veljavne poteze in zgodovino
        self.veljavne_poteze.remove(p) # p vec ni veljavna poteza
        novi = self.dodaj_veljavne_poteze(p)
        self.zgodovina.append((p, novi))
        
        # Preverimo, ce je igre konec
        zmagovalec, petka = self.stanje_po_potezi(p)

        if zmagovalec == NI_KONEC:
            # Igra se nadaljuje
            self.na_potezi = nasprotnik(self.na_potezi)
        else:
            # Igre je konec
            self.na_potezi = None
            self.trenutno_stanje = zmagovalec
            self.petka = petka
        return zmagovalec, petka
    
    def razveljavi_potezo(self):
        '''Razveljavi zadnjo odigrano potezo.'''
        if len(self.zgodovina) == 0: # Ni potez za razveljaviti
            return
        
        # Iz zgodovine pridobimo zadnjo odigrano potezo in nove veljavne poteze, ki jih je doprinesla
        p, novi = self.zgodovina.pop()

        # Pridobimo igralca, ki je bil na potezi
        self.na_potezi = self.board[p]

        # Odstranimo potezo iz igralne povrsine
        del self.board[p]
        self.stevilo_potez -= 1

        # Posodobimo veljavne poteze
        self.veljavne_poteze.add(p)
        for pi in novi:
            self.veljavne_poteze.remove(pi)
        
        # Ce je bilo igre konec, to odstranimo
        if self.trenutno_stanje != NI_KONEC:
            self.trenutno_stanje = NI_KONEC
            self.petka = None

    def preveri_resitev(self, p, dx, dy):
        '''Preveri, ce je p del resitve z x-naklonom dx in y-naklonom dy.'''
        x,y = p
        petka = [p]

        x = (x+dx) % DIM_X
        y = (y+dy) % DIM_Y
        pi = (x, y)
        while len(petka) < 5 and pi in self.board and self.board[pi] == self.na_potezi:
            petka.append(pi)
            x = (x+dx) % DIM_X
            y = (y+dy) % DIM_Y
            pi = (x, y)
        x,y = p
        x = (x-dx) % DIM_X
        y = (y-dy) % DIM_Y
        pi = (x, y)
        while len(petka) < 5 and pi in self.board and self.board[pi] == self.na_potezi:
            petka.append(pi)
            x = (x-dx) % DIM_X
            y = (y-dy) % DIM_Y
            pi = (x, y)
        return petka
    
    def stanje_igre(self):
        '''Preveri stanje igre.'''
        if len(self.zgodovina) == 0:
            # Smo na zacetku - ni se bilo odigranih potez
            return NI_KONEC, None
        else:
            # Uporabimo metodo 'stanje_po_potezi' in ji podamo zadnje odigrano potezo
            return self.stanje_po_potezi(self.zgodovina[-1][0])

    def stanje_po_potezi(self, p):
        '''Preveri stanje igre po potezi p.'''
        # Mozne smeri v katerih iscemo resitev
        smeri = [(0,1), (1,0), (1,1), (1,-1)]
        
        # Preverimo, ce v kateri od teh smeri obstaja resitev
        for dx,dy in smeri:
            petka = self.preveri_resitev(p, dx, dy)
            if len(petka) == 5:
                return self.na_potezi, sorted(petka)
        
        # Nismo zmagali ... preverimo, ce smo presegli max stevilo dovoljenih potez
        if self.stevilo_potez == MAX_POTEZ:
            return NEODLOCENO, None
        else:
            return NI_KONEC, None
    
    def dodaj_veljavne_poteze(self, p):
        '''Dodamo veljavne poteze, ki jih je prinesla poteza p, in vrnemo na novo dodane polozaje.'''
        novi = []
        x,y = p
        y1 = (y+1) % DIM_Y
        y2 = (y-1) % DIM_Y
        for i in range(3):
            pi1 = ((x-1+i) % DIM_X, y1)
            pi2 = ((x-1+i) % DIM_X, y2)
            if pi1 not in self.board and pi1 not in self.veljavne_poteze:
                novi.append(pi1)
                self.veljavne_poteze.add(pi1)
            if pi2 not in self.board and pi2 not in self.veljavne_poteze:
                novi.append(pi2)
                self.veljavne_poteze.add(pi2)
        pi1 = ((x-1) % DIM_X, y)
        pi2 = ((x+1) % DIM_X, y)
        if pi1 not in self.board and pi1 not in self.veljavne_poteze:
            novi.append(pi1)
            self.veljavne_poteze.add(pi1)
        if pi2 not in self.board and pi2 not in self.veljavne_poteze:
            novi.append(pi2)
            self.veljavne_poteze.add(pi2)
        return tuple(novi)