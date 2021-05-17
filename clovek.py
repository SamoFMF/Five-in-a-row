####################
## IGRALEC ČLOVEK ##
####################

class Clovek():
    def __init__(self, gui):
        self.gui = gui

    def igraj(self):
        # To metodo kliče GUI, ko je igralec na potezi.
        # Ko je clovek na potezi, čakamo na uporabniški
        # vmesnik, da sporoči, da je uporabnik kliknil na
        # ploščo.
        pass

    def prekini(self):
        # To metodo kliče GUI, če je treba prekiniti razmišljanje.
        # Človek jo lahko ignorira.
        pass

    def klik(self, p):
        # Povlečemo potezo. Če ni veljavna, se ne bo zgodilo nič.
        self.gui.povleci_potezo(p)