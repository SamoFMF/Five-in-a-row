from ai import AIPlayer
import tkinter as tk # GUI

from logika import *
from minimax import *
from clovek import Clovek
from racunalnik import Racunalnik

##################################
# GRAFICNI / UPORABNISKI VMESNIK #
##################################

MIN_SIRINA = 500
MIN_VISINA = 555
ZVP = 100

class Gui:
    # Definirajmo si tage za elemente platna
    TAG_FIGURA = "figura" # figure igralcev
    TAG_OKVIR = "okvir" # Crte, ki predstavljajo igralno povrsino oz. njen okvir
    TAG_GUMB = "gumb" # Gumbi
    TAG_PETKA = "petka" # Zmagovalna petka

    BARVE = {IGRALEC_1: "red", IGRALEC_2: "blue"} # barve igralcev

    def __init__(self, master):
        self.igralec_1 = None # Objekt, ki igra IGRALCA 1
        self.igralec_2 = None # Objekt, ki igra IGRALCA 2
        self.igra = None # Objekt, ki predstavlja igro
        self.velikost_polja = ZVP # Velikost polja
        self.velikost_gap = self.velikost_polja / 20 # Razdalja med okvirjem in figuro

        # Ce uporabnik zapre okno se naj klice self.zapri_okno
        master.protocol("WM_DELETE_WINDOW", lambda: self.zapri_okno(master))

        # Glavni menu
        menu = tk.Menu(master)
        master.config(menu=menu)

        # Podmenu Igra
        menu_igra = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Igra", menu=menu_igra)
        # Gumb za zacetek nove igre
        menu_igra.add_command(label="Nova igra",
                                command=self.zacni_igro)
        
        # Podmenu Moznosti
        menu_moznosti = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Moznosti", menu=menu_moznosti)
        
        ####################
        # IGRALNA POVRSINA #
        ####################
        self.platno = tk.Canvas(master,
                                width=(NUM_COLS+1) * self.velikost_polja,
                                height=(NUM_ROWS+1) * self.velikost_polja)
        self.platno.pack(fill=tk.BOTH, expand=1, side=tk.RIGHT)

        # Narisemo crte
        self.narisi_okvir()

        # Dolocimo, kaj uporabnikovi kliki naredijo
        self.platno.bind("<Button-1>", self.platno_klik)

        # Zacnemo igro
        self.zacni_igro()
    
    def zapri_okno(self, master):
        '''Ta metoda se pokliče, ko uporabnik zapre aplikacijo.'''
        # Igralce najprej ustavimo
        self.prekini_igralce()

        # Zapremo okno
        master.destroy()
    
    def prekini_igralce(self):
        '''Sporoci igralcem, da morajo nehati razmisljati.'''
        if self.igralec_1:
            self.igralec_1.prekini()
        if self.igralec_2:
            self.igralec_2.prekini()

    def narisi_okvir(self):
        '''Narise okvir igralne povrsine.'''
        self.platno.delete(Gui.TAG_OKVIR)
        d = self.velikost_polja
        xmin = d/2
        xmax = xmin + NUM_COLS * d
        ymin = d/2
        ymax = ymin + NUM_ROWS * d
        for i in range(NUM_ROWS+1):
            self.platno.create_line(xmin, ymin + i*d, xmax, ymin + i*d)

        for i in range(NUM_COLS+1):
            self.platno.create_line(xmin + i*d, ymin, xmin + i*d, ymax)

    def platno_klik(self, event):
        x,y = event.x, event.y
        d = self.velikost_polja
        if (x < d/2) or (x > d/2 + NUM_COLS * d) or (y < d/2) or (y > d/2 + NUM_ROWS * d):
            # Klik je izven igralne povrsine
            return
        else:
            col = int((x-d/2) // d) # V katerem stolpcu smo
            p = col + 1 # Poteza do predznaka natancno
            row = NUM_ROWS - 1 - int((y-d/2) // d)

            if self.igra.board[col][row] != PRAZNO:
                # Polje je ze zasedeno
                return
            elif row == 0:
                pass
            elif row == NUM_ROWS - 1:
                p *= -1
            elif self.igra.board[col][row-1] != PRAZNO:
                pass
            elif self.igra.board[col][(row+1) % NUM_ROWS] != PRAZNO:
                p *= -1

            # print("Poteza:", p)
            
            # Narocimo igralcu, da odigra kliknjeno potezo
            if self.igra.na_potezi == IGRALEC_1:
                self.igralec_1.klik(p)
            elif self.igra.na_potezi == IGRALEC_2:
                self.igralec_2.klik(p)

    def povleci_potezo(self, p):
        '''Odigra in narise potezo.'''
        igralec = self.igra.na_potezi
        zmagovalec, petka = self.igra.odigraj_potezo(p)
        if zmagovalec is None:
            # Poteza ni veljavna
            return
        self.narisi_potezo(p, Gui.BARVE[igralec])
        if zmagovalec == NI_KONEC:
            if self.igra.na_potezi == IGRALEC_1:
                self.igralec_1.igraj()
            elif self.igra.na_potezi == IGRALEC_2:
                self.igralec_2.igraj()
        else:
            self.koncaj_igro(zmagovalec, petka)

    def narisi_potezo(self, p, col):
        d = self.velikost_polja
        x = abs(p) - 1
        y = self.igra.vrstice_plus[x] - 1 if p>0 else -(self.igra.vrstice_minus[x]) % NUM_ROWS
        xcenter = (x+1) * d
        ycenter = (NUM_ROWS-y) * d
        gap = self.velikost_gap

        self.platno.create_oval(xcenter-d/2+gap, ycenter-d/2+gap,
                                xcenter+d/2-gap, ycenter+d/2-gap,
                                fill=col,
                                width=0,
                                tag=Gui.TAG_FIGURA)
        self.platno.create_text(xcenter, ycenter,
                                text=str(self.igra.stevilo_potez),
                                font=("Purisa", 40),
                                tag=Gui.TAG_FIGURA)
    
    def obarvaj_petko(self, petka, col):
        d = self.velikost_polja
        for x,y in petka:
            ycoord = NUM_ROWS-1-y
            self.platno.create_rectangle(d/2 + x*d, d/2 + ycoord*d,
                                            d/2 + (x+1)*d, d/2 + (ycoord+1)*d,
                                            outline=col,
                                            width=4,
                                            tag=Gui.TAG_PETKA)

    def zacni_igro(self):
        '''Zacne novo/naslednjo igro. Nastavi igralce, tip igre, rezultat itd.'''
        self.prekini_igralce()

        # self.igralec_1 = Clovek(self)
        # self.igralec_2 = Clovek(self)
        self.igralec_1 = Racunalnik(self, AIPlayer("ai", 0, 0.9, 0.1))
        self.igralec_1.algoritem.nalozi_strategijo("ai_100k_p1")
        # self.igralec_1 = Racunalnik(self, Minimax(4, "alphabeta"))
        self.igralec_2 = Racunalnik(self, Minimax(5, "negamax_memo"))
        # # self.igralec_1.algoritem.vrednost_polozaja = self.igralec_1.algoritem.vrednost_polozaja_old
        # self.igralec_2.algoritem.vrednost_polozaja = self.igralec_2.algoritem.vrednost_polozaja_old
        # self.igralec_1.algoritem.bias = 1

        # Pobrisemo odigrane poteze
        self.platno.delete(Gui.TAG_FIGURA)
        self.platno.delete(Gui.TAG_PETKA)

        # Ustvarimo novo igro
        self.igra = Logika()

        # Preverimo, kdo je na potezi
        if self.igra.na_potezi == IGRALEC_1:
            self.igralec_1.igraj()
        elif self.igra.na_potezi == IGRALEC_2:
            self.igralec_2.igraj()

    def koncaj_igro(self, zmagovalec, petka):
        if petka is not None:
            self.obarvaj_petko(petka, Gui.BARVE[zmagovalec])


######################################################################
## Glavni program

if __name__ == "__main__":
    # Naredimo glavno okno in nastavimo ime
    root = tk.Tk()
    root.title("Pet v vrsto")

    # Nastavimo najmanjso velikost okna
    root.minsize(int(MIN_SIRINA), int(MIN_VISINA))

    # Naredimo objekt Gui in ga shranimo, sicer ga Python zbrise
    aplikacija = Gui(root)

    # Kontrolo prepustimo glavnemu oknu
    # Funkcija mainloop neha delovati, ko okno zapremo
    root.mainloop()