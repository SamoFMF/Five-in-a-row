# Reinforcement learning

from logika import *
from ai import *

class ReinforcementLearning:
    def __init__(self):
        self.igra: Logika = None
        self.igralca: list[AIPlayer] = [None, None]
    
    def shrani_igralca(self, idx, filename):
        self.igralca[idx].shrani_strategijo(filename)
    
    def train(self, rounds=1000, reset_globina=0):
        '''Train agents.'''
        wins = [0,0,0] # [p1, p2, tie]
        for i in range(rounds):
            if i%1000 == 0:
                print("Stevilo iger:", i)
            self.igra = Logika()
            obiskani = set()
            while self.igra.trenutno_stanje == NI_KONEC:
                igralec = self.igralca[self.igra.na_potezi - 1]
                p = igralec.izberi_potezo(self.igra.kopiraj_board(), self.igra.veljavne_poteze, self.igra.na_potezi)

                zmagovalec, _ = self.igra.odigraj_potezo(p)

                hash = igralec.get_hash(self.igra.board)
                igralec.dodaj_state(hash, self.igra.veljavne_poteze)

                if zmagovalec != NI_KONEC:
                    # Igre je konec
                    self.razdeli_nagrade(zmagovalec)
                    konec = True if reset_globina == 0 else False

                    if zmagovalec == NEODLOCENO:
                        konec = True
                        wins[2] += 1
                    elif zmagovalec == IGRALEC_1:
                        if hash in obiskani:
                            konec = True
                        else:
                            wins[0] += 1
                            obiskani.add(hash)
                    elif zmagovalec == IGRALEC_2:
                        if hash in obiskani:
                            konec = True
                        else:
                            wins[1] += 1
                            obiskani.add(hash)
                    
                    if konec:
                        self.igralca[0].reset()
                        self.igralca[1].reset()
                    else:
                        for _ in range(reset_globina):
                            self.igra.razveljavi_potezo()
                            self.igra.razveljavi_potezo()
                            self.igralca[0].states.pop()
                            self.igralca[1].states.pop()
        print(wins)
    
    def razdeli_nagrade(self, zmagovalec):
        if zmagovalec == NEODLOCENO:
            # Neodlocen rezultat - pricakujemo, da ima prvi igralec majhno prednost, zato mu je ta rezultat slabsi
            self.igralca[0].posodobi_vrednosti(-0.1, IGRALEC_1)
            self.igralca[1].posodobi_vrednosti(0.1, IGRALEC_2)
        elif zmagovalec == IGRALEC_1:
            # Zmagal je IGRALEC_1 (idx=0)
            self.igralca[0].posodobi_vrednosti(1, IGRALEC_1)
            self.igralca[1].posodobi_vrednosti(-1, IGRALEC_2)
        elif zmagovalec == IGRALEC_2:
            self.igralca[0].posodobi_vrednosti(-1, IGRALEC_1)
            self.igralca[1].posodobi_vrednosti(1, IGRALEC_2)
        else:
            assert False, f"Konec igre z neznanim zmagovalcem: {zmagovalec}"

# rl = ReinforcementLearning()
# # rl.igra = Logika()
# rl.igralca[0] = AIPlayer("test1", 0.4, 0.9, 0.1)
# rl.igralca[1] = AIPlayer("test2", 0.4, 0.9, 0.1)

# rl.train(250000)

# rl.igralca[0].epsilon = 0.3
# rl.igralca[0].epsilon = 0.3
# rl.train(250000)

# rl.igralca[0].epsilon = 0.2
# rl.igralca[0].epsilon = 0.2
# rl.train(250000)

# rl.igralca[0].epsilon = 0.1
# rl.igralca[0].epsilon = 0.1
# rl.train(250000)


# print(len(rl.igralca[0].state_values))
# print(len(rl.igralca[1].state_values))

# print("SAVING ...", end=" ")
# rl.igralca[0].shrani_strategijo("ai_1M_p1")
# rl.igralca[1].shrani_strategijo("ai_1M_p2")
# print("DONE")