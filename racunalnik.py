import threading

########################
## IGRALEC RAČUNALNIK ##
########################

class Racunalnik:
    def __init__(self, gui, algoritem):
        self.gui = gui
        self.algoritem = algoritem # Algoritem, ki izračuna potezo
        self.mislec = None # Thread, ki razmišlja

    def igraj(self):
        '''Igraj potezo, ki jo vrne algoritem.'''
        # Naredimo vlakno in mu podamo kopijo igre
        self.mislec = threading.Thread(
            target = lambda: self.algoritem.izracunaj_potezo(
                self.gui.igra.kopija()))

        # Poženemo vlakno
        self.mislec.start()

        # Preverimo, ali je bila najdena poteza
        self.gui.platno.after(100, self.preveri_potezo)

    def preveri_potezo(self):
        '''Vsakih 100ms preveri, če je algoritem že izračunal potezo.'''
        if self.algoritem.poteza:
            # Algoritem je našel potezo

            # Vzporedno vlakno ni več aktivno, zato ga pozabimo
            self.mislec = None
            
            # Če ni bilo prekinitve, povleci potezo
            self.gui.povleci_potezo(self.algoritem.poteza)
        else:
            # Algoritem še ni našel poteze, čez 100ms naj ponovno preveri
            self.gui.platno.after(100, self.preveri_potezo)

    def prekini(self):
        '''Metodo pokliče GUI, če je potrebno prekiniti razmišljanje.'''
        if self.mislec:
            # Algoritmu sporočimo, da mora nehati z razmišljanjem
            self.algoritem.prekini()

            # Počakamo, da se vlakno ustavi in ga pozabimo
            self.mislec.join()
            self.mislec = None

    def klik(self, p):
        # Računalnik ignorira klike
        pass