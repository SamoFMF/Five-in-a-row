from rl import ReinforcementLearning
from logika import Logika
from ai import AIPlayer

RL = ReinforcementLearning()
RL.igralca[0] = AIPlayer("ai1", 0.75, 0.75, 0.25)
RL.igralca[1] = AIPlayer("ai2", 0.3, 0.95, 0.25)

RL.train(10000)

RL.igralca[0].epsilon = 0.1
RL.igralca[1].epsilon = 0.1

RL.igralca[0].gamma = 0.95
RL.igralca[1].gamma = 0.95

RL.train(10000)