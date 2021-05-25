from rl import ReinforcementLearning
from logika import Logika, NI_KONEC
from ai import AIPlayer

def test(RL=None):
    if RL is None:
        RL = ReinforcementLearning()
        RL.igralca[0] = AIPlayer("ai1", 0.1, 0.95, 0.25)
        RL.igralca[1] = AIPlayer("ai2", 0.1, 0.95, 0.25)
        RL.igralca[0].nalozi_strategijo("test1_p1")
        RL.igralca[1].nalozi_strategijo("ai_1M_p2")
    wins = [0, 0, 0]

    print(len(RL.igralca[0].state_values), len(RL.igralca[1].state_values))

    for i in range(10000):
        if i%1000 == 0:
            print("Stevilo iger:", i)
        G = Logika()
        while G.trenutno_stanje == NI_KONEC:
            igralec = RL.igralca[G.na_potezi-1]
            p = igralec.izberi_potezo(G.kopiraj_board(), G.veljavne_poteze, G.na_potezi)

            zmagovalec, _ = G.odigraj_potezo(p)

            if zmagovalec == NI_KONEC:
                continue
            elif zmagovalec == 1:
                wins[0] += 1
            elif zmagovalec == 2:
                wins[1] += 1
            else:
                wins[2] += 1
    print(wins)

RL = ReinforcementLearning()
RL.igralca[0] = AIPlayer("ai1", 0.25, 0.95, 0.25)
RL.igralca[1] = AIPlayer("ai2", 0.75, 0.95, 0.5)

RL.train(10000, 1)

RL.igralca[0].epsilon = 0.1
RL.igralca[1].epsilon = 0.1

RL.igralca[0].nalozi_strategijo("ai_1M_p1")
test(RL)

# RL.shrani_igralca(0, "test2_p1")
# RL.shrani_igralca(1, "test2_p2")

# print(len(RL.igralca[0].state_values), len(RL.igralca[1].state_values))

# RL.igralca[0].epsilon = 0.1
# RL.igralca[1].epsilon = 0.1

# RL.igralca[0].gamma = 0.95
# RL.igralca[1].gamma = 0.95

# RL.train(10000)