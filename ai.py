# Reinforcement learning AI igralec
from random import random, choice
from logika import PRAZNO, Logika
import pickle
from os import path
from time import time

class AIPlayer:
    def __init__(self, ime, epsilon, gamma, alpha, nagrada=0):
        self.ime = ime # Ime igralca, njegova vrednost na boardu
        self.states = [] # Seznam dosezenih stanj v igri
        self.veljavne_poteze = [] # Seznam veljavnih potez pri vsakem stanju
        self.epsilon = epsilon # Verjetnost, da naredimo nakljucno potezo
        self.gamma = gamma # Faktor mnozenja pri vrednotenju poteze .. koliko so prihodnje poteze manj vredne
        self.alpha = alpha # Koliko upostevamo novo vrednost | 1-alpha .. koliko nam pomeni trenutna ocena stanja
        self.state_values = dict() # Vrednosti stanj, ki smo jih ze obiskali
        self.R = nagrada # Nagrada po vsaki potezi

        # Za igranje proti racunalniku
        self.igra = None
        self.jaz = None
        self.prekinitev = False
        self.poteza = None
        self.vrednost = -float("inf")
    
    def prekini(self):
        '''Metoda, ki jo klicemo, ko zelimo, da algoritem preneha z iskanjem.'''
        self.prekinitev = True
    
    def izracunaj_potezo(self, igra):
        '''Izracuno potezo za trenutno stanje podane igre.'''
        self.igra: Logika = igra
        self.jaz = self.igra.na_potezi
        self.prekinitev = False # Glavno vlakno bo nastavilo to na True, ce bomo morali prekiniti
        self.poteza = None # Sem vpisemo potezo, ko jo najdemo

        timestart = time()
        poteza, vrednost = self.pridobi_max(self.igra.board, self.igra.veljavne_poteze, self.igra.na_potezi)
        timeend = time()

        self.igra = None
        self.jaz = None

        if not self.prekinitev:
            # Nismo bili prekinjeni => izvedemo potezo
            self.poteza = poteza
            # print(self.poteza, end=", ")
            print(f"Računalnik igra {poteza} z vrednostjo {round(vrednost, 2)}. Izračunano v {round((timeend-timestart)*1000)}ms.")
    
    def get_hash(self, board):
        '''Vrne board, ki je seznam seznamov intov, v obliki tupla tuplov, da ga lahko uporabimo v dictionary.'''
        return tuple(tuple(i) for i in board)
    
    def reset(self):
        # Zaceli smo novo igro
        self.states = []
        self.veljavne_poteze = []
    
    def dodaj_state(self, hash, veljavne_poteze):
        self.states.append(hash)
        self.veljavne_poteze.append(tuple(i for i in veljavne_poteze))
    
    def Q(self, state):
        if state not in self.state_values:
            self.state_values[state] = 0
    
    def pridobi_koordinate(self, board, poteza, sign):
        for i, barva in enumerate(board[poteza-1][::sign]):
            if barva == PRAZNO:
                break
        return i if sign == 1 else -1-i
    
    def pridobi_max(self, board, poteze, igralec):
        # Poiscemo potezo, ki maksimizira score ... 
        # Ce s vsako potezo dobimo se self.reward, to pri odlocitvi ne vpliva, ...
        # ker je self.reward konstanta, torej bo pri vseh skupni clen
        # V tem koraku ne posodabljamo vrednosti stanj, zato ignoriramo self.reward in pridobimo na hitrosti
        max_vrednost = -float("inf")
        for poteza in poteze:
            for sign in [-1, 1]: # Vsaka poteza je lahko tudi negativna (pi in -pi)
                pi = poteza * sign
                y = self.pridobi_koordinate(board, poteza, sign)
                # for i,barva in enumerate(board[poteza-1][::sign]):
                #     if barva == PRAZNO:
                #         break
                # y = i if sign == 1 else -1-i
                board[poteza-1][y] = igralec
                hash = self.get_hash(board)
                board[poteza-1][y] = PRAZNO
                vrednost = self.state_values[hash] if hash in self.state_values else 0 # Vrednost boarda po izvedeni potezi
                if vrednost > max_vrednost:
                    max_vrednost = vrednost
                    p = pi
        return p, max_vrednost
    
    def izberi_potezo(self, board, poteze, igralec): # POZOR: board naj bo kopija igralne povrsine in ne original
        '''Izberemo potezo.'''
        if random() < self.epsilon:
            # Naredimo nakljucno potezo
            p = choice([i for i in poteze])
            if random() < 0.5:
                p = -p
        else:
            p, _ = self.pridobi_max(board, poteze, igralec)
        return p # Vrnemo potezo
    
    def posodobi_vrednosti(self, nagrada, igralec):
        # Zadnje obiskano stanje predstavlja vrednost nagrade zagotovo:
        # Ce smo igralec, ki je opravil potezo, ki je zakljucila igro, potem je to stanje koncno
        # Ce smo nasprotnik, bomo po nasprotnikovi potezi bodisi izgubili, ali pa bo izenaceno
        # Ce bo izenaceno, je mozna samo se 1 poteza, tako da bo izenaceno neodvisno od tega, kaj odigra nasprotnik
        # Ce pa izgubimo, pa vemo, da je ta polozaj neresljiv, ker v naslednji potezi izgubimo

        self.state_values[self.states[-1]] = nagrada # Zadnje obiskano stanje je torej enako nagradi

        # Preostala stanja posodobimo glede na formulo:
        # Q(s) = Q(s) + alpha * (R + gamma * max_p {Q(s,p)} - Q(s)),
        # kjer je Q(s,p) vrednost stanja, ki ga dosezemo iz stanja s po potezi a
        for i in range(len(self.states)-2, -1, -1):
            state = self.states[i]
            board = [[i for i in j] for j in state]
            if state not in self.state_values:
                self.state_values[state] = 0
            # Poiscemo najboljso potezo a
            _, Qsp = self.pridobi_max(board, self.veljavne_poteze[i], igralec)
            self.state_values[state] += self.alpha * (self.R + self.gamma * Qsp - self.state_values[state])
            # self.state_values[state] += self.alpha * (self.gamma * nagrada - self.state_values[state])
            # nagrada = self.state_values[state]
    
    def shrani_strategijo(self, filename):
        cur_path = path.join("data", f"{filename}.pkl.gz")
        if path.exists(cur_path):
            i = 0
            cur_path = path.join("data", f"{filename}_{i}.pkl.gz")
            while path.exists(cur_path):
                i += 1
                cur_path = path.join("data", f"{filename}_{i}.pkl.gz")
        with open(cur_path, "wb") as f:
            pickle.dump(self.state_values, f)
    
    def nalozi_strategijo(self, filename):
        cur_path = path.join("data", f"{filename}.pkl.gz")
        assert path.exists(cur_path), "File does not exist!"
        with open(cur_path, "rb") as f:
            self.state_values = pickle.load(f)