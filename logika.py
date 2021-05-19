# LOGIKA ZA IGRO PET V VRSTO
from collections import defaultdict

# KONSTANTE
IGRALEC_1 = 1
IGRALEC_2 = 2
PRAZNO = 0

NEODLOCENO = 3
NI_KONEC = 4

NUM_COLS = 7
NUM_ROWS = 6
MAX_POTEZ = NUM_COLS * NUM_ROWS

def nasprotnik(igralec):
    if igralec == IGRALEC_1:
        return IGRALEC_2
    elif igralec == IGRALEC_2:
        return IGRALEC_1
    else:
        assert False, f"neveljaven nasprotnik: {igralec}"

def sign(x):
    return -1 if x<0 else 1

class Logika:
    def __init__(self, na_potezi=IGRALEC_1):
        # Ustvarimo igralno povrsino
        self.board = [[PRAZNO]*NUM_ROWS for _ in range(NUM_COLS)]

        # Ustvarimo sezname s katerimi bomo vodili, ce je poteza veljavna
        self.navoljo = [NUM_ROWS] * NUM_COLS # Koliko potez imamo v vsakem stolpcu se navoljo
        self.vrstice_plus = [0] * NUM_COLS # V kateri vrstici smo v posameznem stolpcu v pozitivni smeri
        self.vrstice_minus = [0] * NUM_COLS # V kateri vrstici smo v posameznem stolpcu v negativni smeri

        # Dolocimo igralca, ki je na potezi
        self.na_potezi = na_potezi

        # Veljavne poteze - na zacetku je to samo (0,0) # TODO - premisli, ce smiselno?
        self.veljavne_poteze = {i+1 for i in range(NUM_COLS)}

        # Zgodovina potez
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
        L.board = [[row for row in col] for col in self.board]

        # Prenesemo stanja vrstic
        L.navoljo = self.navoljo
        L.vrstice_plus = [i for i in self.vrstice_plus]
        L.vrstice_minus = [i for i in self.vrstice_minus]
        
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
    
    def kopiraj_board(self):
        return [[row for row in col] for col in self.board]
    
    def pridobi_koordinate(self, p, odigrana=False):
        '''Vrne koordinate poteze p na igralni povrsini.'''
        x = abs(p) - 1
        if odigrana:
            # Poteza je ze odigrana
            y = (self.vrstice_plus[x]-1) if p>0 else -self.vrstice_minus[x] % NUM_ROWS
        else:
            # Poteza se ni odigrana - na te koordinate BO odigrana
            y = self.vrstice_plus[x] if p>0 else -(self.vrstice_minus[x]+1) % NUM_ROWS
        return x, y

    def odigraj_potezo(self, p):
        '''Odigraj potezo p, ce je veljavna, sicer ne naredi nic.'''
        # assert self.na_potezi is not None, "Igre je konec!"
        # assert abs(p) in self.veljavne_poteze, "Neveljavna poteza!"
        if self.na_potezi is None or abs(p) not in self.veljavne_poteze:
            return None, None

        # Koordinate poteze
        x,y = self.pridobi_koordinate(p)
        if p > 0:
            # Pozitivna smer
            self.vrstice_plus[x] += 1
        else:
            # Negativna smer
            self.vrstice_minus[x] += 1
        
        self.navoljo[x] -= 1 # Navoljo je 1 poteza manj

        # Odigramo potezo p in povecamo stevilo potez
        # print(p, x, y)
        self.board[x][y] = self.na_potezi
        self.stevilo_potez += 1

        # Posodobimo veljavne poteze
        if self.navoljo[x] == 0:
            self.veljavne_poteze.remove(x+1)
        
        # Shranimo potezo v zgodovino
        self.zgodovina.append(p)
        
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
            # print(f"KONEC! Zmagal je {zmagovalec} s petko {self.petka}.")
        
        return zmagovalec, petka
    
    def razveljavi_potezo(self):
        '''Razveljavi zadnjo odigrano potezo.'''
        if len(self.zgodovina) == 0: # Ni potez za razveljaviti
            return
        
        # Iz zgodovine pridobimo zadnjo odigrano potezo
        p = self.zgodovina.pop()

        # Posodobimo self.vrstice in self.navoljo
        x, y = self.pridobi_koordinate(p, True)
        if p > 0:
            # Pozitivna smer
            self.vrstice_plus[x] -= 1
        else:
            # Negativna smer
            self.vrstice_minus[x] -= 1
        self.navoljo[x] += 1

        # Posodobimo veljavne poteze, ce potrebno
        if self.navoljo[x] == 1:
            self.veljavne_poteze.add(x+1)

        # Pridobimo igralca, ki je bil na potezi
        self.na_potezi = self.board[x][y]

        # Odstranimo potezo iz igralne povrsine
        self.board[x][y] = PRAZNO
        self.stevilo_potez -= 1
        
        # Ce je bilo igre konec, to odstranimo
        if self.trenutno_stanje != NI_KONEC:
            self.trenutno_stanje = NI_KONEC
            self.petka = None

    def preveri_resitev(self, p, dx, dy):
        '''Preveri, ce je p del resitve z x-naklonom dx in y-naklonom dy.'''
        x0,y0 = self.pridobi_koordinate(p, True)
        petka = [(x0,y0)]

        x = (x0+dx) % NUM_COLS
        y = (y0+dy) % NUM_ROWS
        while len(petka) < 5 and self.board[x][y] == self.na_potezi:
            petka.append((x,y))
            x = (x+dx) % NUM_COLS
            y = (y+dy) % NUM_ROWS
        
        x = (x0-dx) % NUM_COLS
        y = (y0-dy) % NUM_ROWS
        while len(petka) < 5 and self.board[x][y] == self.na_potezi:
            petka.append((x,y))
            x = (x-dx) % NUM_COLS
            y = (y-dy) % NUM_ROWS
        
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