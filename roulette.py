#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = 'José E. Morales Ventura'
__date__ = '15/Junio/2025'
__proyect__ = 'roulette.py'
__description__ = '''Herramienta de Ruleta'''

import msvcrt
import random
from itertools import chain
from collections import Counter
import os, sys
import cfonts
import time


class CircleRouletteLittleMachine(list):
    '''
    Representacion de una maquinita
    '''

    PROFIT_OUT = 33

    def __init__(self, numbers:list=[x for x in range(0, 13)], pay_for:int=12, history_size:int=7, total_amount:int=300):
        super().__init__()
        self.extend(numbers)
        self.ordered = sorted(numbers)
        self.pay_for = pay_for
        self.history = []
        self.total_amount = total_amount
        self.played_numbers = {}
        self.history_size = history_size
        self.selected_neighs = []
        self.hotter_numbers = []
        self.profit = 0
        # -- Recordar el monto inicial y la ronda actual
        self.ROUND_NUMBER = 0
        self.INITIAL_WALLET = 0
        self.MULTIPLICADOR = [1, 2]
        self.INDEX = 0
        
    def add_multiplier(self) -> int:
        '''
        Asigna el multiplicador a aplicar
        '''
        if self.INDEX < len(self.MULTIPLICADOR)-1:
            self.INDEX += 1
        else:
            self.INDEX = 0

    def get_multiplier(self):
        '''
        Obtiene el multiplicador aplicado
        '''
        return self.MULTIPLICADOR[self.INDEX]
    
    def calculate_percent(self) -> None:
        '''
        Calcula la probabilidad de ganar
        '''

        print(f'\t Jugando a un {(len(self.played_numbers)/len(self))*100:.2f}%')

    def select_unique_neighbors(self, neighbors_list: list, hotters: list = []) -> list:
        '''
        Devuelve una lista sin vecinos repetidos.
        Si hay repetidos, reemplaza con vecinos libres hacia la izquierda del círculo
        hasta volver a llegar al mismo número.
        Nunca selecciona como vecino a un número presente en `hotters`.
        '''
        unique_neighbors = []
        used = set()

        for neigh in neighbors_list:
            if neigh not in used and neigh not in hotters:
                unique_neighbors.append(neigh)
                used.add(neigh)
            else:
                index = self.index(neigh)
                found = False
                offset = 1

                # Buscar hacia la izquierda hasta volver al mismo número
                while offset < len(self):
                    left_index = (index - offset) % len(self)
                    candidate = self[left_index]

                    if candidate == neigh:
                        break  # Hemos dado la vuelta completa sin encontrar uno libre

                    if candidate not in used and candidate not in hotters:
                        unique_neighbors.append(candidate)
                        used.add(candidate)
                        found = True
                        break

                    offset += 1

                if not found:
                    print(f"[⚠️] Vecino repetido '{neigh}' no pudo ser sustituido.")

        return unique_neighbors

    def get_neighbors(self, numero:int) -> tuple:
        '''
        Obtiene los vecinos del numero indicado
        '''
        index = self.index(numero)
        left = self[(index - 1) % len(self)]
        right = self[(index + 1) % len(self)]
        return left, right
    
    def get_hotters(self, top:int) -> list:
        '''
        Devuelve los `top` números distintos más frecuentes de las últimas N salidas,
        con un toque de aleatoriedad ponderada por la frecuencia.
        '''
        flat = list(chain.from_iterable(self.history))
        counter = Counter(flat)

        # Aleatoriza con peso: números más frecuentes tienen más chance de salir arriba
        top_randomized = sorted(counter.keys(), key=lambda x: counter[x] * random.random(), reverse=True)

        result = top_randomized[:top]
        seen = set(result)

        # Rellenar con números aleatorios distintos si faltan
        if len(result) < top:
            restantes = [n for n in self if n not in seen]
            result.extend(restantes[:top - len(result)])

        return result

    def get_history(self) -> list:
        '''
        Muestra los ultimos numeros del historico
        '''
        if not self.history:
            print("No hay historial aún para predecir.")
            return []
        flat = list(chain.from_iterable(self.history))
        return flat

    def calculate_profit(self) -> None:
        '''
        Calcula el profit en porcentaje
        '''
        self.profit = round(100*(self.total_amount - self.INITIAL_WALLET)/self.INITIAL_WALLET,2)

    def calculate_winning_amount(self, winning_number:int) -> bool:
        '''
        Calcula el nuevo monto disponible luego de la jugada.
        Returna True si acierta, False si falla
        '''
        status = False
        if winning_number in self.played_numbers.keys():
            ganancia = self.played_numbers[winning_number] * self.pay_for
            self.total_amount += ganancia
            print(f'\t 💵 ¡Acertó {ganancia} DOP!')
            status = True
        else:
            perdida = sum(self.played_numbers.values())
            self.total_amount -= perdida
            print(f'\t ❌ Falló {perdida} DOP.')
            status = False
        self.calculate_profit()
        print(f'\t 💼 Cartera : {self.total_amount} DOP')
        if self.profit < 0:
            print(f"\t 😩 Profit -> {self.profit} %")
        else:
            print(f"\t 🤑 Profit -> {self.profit} %")
        print('\n🕹️ >>> EJECUTAR DE NUEVO (ENTER): ', end='', flush=True)
        flat = self.get_history()
        os.system(f'title {flat[-1*self.history_size:]} - {self.INITIAL_WALLET}')

        return status

    def put_bet(self, plays: dict) -> None:
        '''
        Asigna las apuestas sin descontar el saldo.
        Solo valida que haya saldo suficiente.
        '''
        total_bet = sum(plays.values())
        if total_bet > self.total_amount:
            raise ValueError("⛔ Saldo insuficiente para realizar esta apuesta.")
        self.played_numbers = plays

    def confirm_bet(self) -> None:
        total_bet = sum(self.played_numbers.values())
        if total_bet > self.total_amount:
            raise ValueError("⛔ Saldo insuficiente para descontar la apuesta")
        self.total_amount -= total_bet

    def display_number(self, number):
        os.system('cls' if os.name == 'nt' else 'clear')
        output_title = cfonts.render('ROULETTE', colors=['red', 'yellow'], align='center')

        if number == 0:
            color = ['green']
        elif number % 2 == 0:
            color = ['cyan']
        else:
            color = ['red']

        output = cfonts.render(str(number), colors=color, align='center')
        print(output_title)
        print(output)

    def config_secret(self) -> tuple:
        '''
        Establece el secreto de la rotación:
        - start_from: índice inicial
        - extra_steps: pasos extra luego de 1 vuelta completa
        '''
        start_from = random.randint(0, len(self) - 1)
        extra_steps = random.randint(2, 4)
        return start_from, extra_steps
    
    def rotate(self, secs_animation:int=3) -> int:
        size = len(self)

        winning_number = random.choice(self)
        winning_index = self.index(winning_number)

        # Usamos config_secret para obtener el inicio y las vueltas extras
        start_from, vueltas_extras = self.config_secret()

        diff = (winning_index - start_from) % size

        total_steps = vueltas_extras * size + diff + 1

        path = [(start_from + i) % size for i in range(total_steps)]

        SEGUNDOS = secs_animation
        delay = SEGUNDOS / len(path)

        for i in path:
            number = self[i]
            self.display_number(number)
            time.sleep(delay)

        apuestas_ordenadas = dict(sorted(self.played_numbers.items()))
        print(f'\t 🔄 Secrete -> Desde {start_from} con total pasos {total_steps}')
        print(f"\t ❓ RNG -> {winning_number}")
        print(f"\t 🔥 Hotters -> {self.hotter_numbers}")
        print(f"\t 🎟️ Apuestas -> {apuestas_ordenadas}")
        print(f"\t 🎯 Número Ganador -> {winning_number}")
        print(f"\t ⚡ Ronda -> {self.ROUND_NUMBER}")
        
        if not self.history:
            self.history.append([winning_number])
        else:
            ultima_sublista = self.history[-1]
            if len(ultima_sublista) < self.history_size:
                ultima_sublista.append(winning_number)
            else:
                self.history.append([winning_number])

        return winning_number

    def has_reach_profit(self) -> bool:
        '''
        Verifica si llegamos al profit requerido
        '''
        return self.profit >= CircleRouletteLittleMachine.PROFIT_OUT

    def initialize_history(self, INITIAL_HISTORY_BLOCKS:int) -> None:
        '''
        Inicializa el historial con 2 sublistas aleatorias, 
        cada una con hasta self.history_size elementos únicos.
        '''
        self.history = []

        for _ in range(INITIAL_HISTORY_BLOCKS):
            # -- Tomar números aleatorios únicos sin repetición
            sublist = random.sample(self, min(self.history_size, len(self)))
            self.history.append(sublist)

    def start(self, secs_animation:int=3) -> int:
        '''
        Ejecuta la ruleta
        '''
        self.calculate_percent()
        self.confirm_bet()
        self.ROUND_NUMBER += 1

        return self.rotate(secs_animation=secs_animation)


if __name__ == "__main__":
    os.system('cls')

    if len(sys.argv) <= 2:
        print("USE python roulette.py [TOP_METHOD] [HOT_AMOUNT] [NEIGHT_AMOUNT] [OTHER_AMOUNT] [RONDAS_SOPORTADAS] [PROFIT_OUT (30,50,60,...)] [USE_ANTIGALA 1 ó 0]")
        print("Ex. python roulette.py TOP3 40 20 10 10 33 1")
    else:
        output = cfonts.render('ROULETTE', colors=['red', 'yellow'], align='center')
        print(output)
        TOP_METHOD = sys.argv[1].upper() if len(sys.argv) > 1 else 'TOP2'
        ANIMATION_TIME_SECS = 1
        HOT_AMOUNT = int(sys.argv[2])
        NEIGHT_AMOUNT = int(sys.argv[3])
        OTHER_AMOUNT = int(sys.argv[4])
        # -- Habilita el juego automático
        AUTORUN = True
        COUNTER_AUTO = 0
        # -- Maximo numero de jugadas en automático
        MAX_REPEAT = 100
        # -- Pausa entre automatizacion de autorun
        PAUSE_AUTORUN = 1

        # -- Indique para cuantas rondas tiene dinero suficiente
        RONDAS_SOPORTADAS = int(sys.argv[5])

        # -- Simular N rondas de historial para iniciar
        INITIAL_HISTORY_BLOCKS = 5

        # -- Profit deseado
        PROFIT_OUT = int(sys.argv[6])

        # -- Use ANTIMARTINGALA
        USE_ANTIGALA =  bool(int(sys.argv[7]))

        if TOP_METHOD == 'TOP2':
            total_amount = 160 * RONDAS_SOPORTADAS
        elif TOP_METHOD == 'TOP3':
            total_amount = 240 * RONDAS_SOPORTADAS
        else:
            raise ValueError('El top indicado no es valido')

        crlm = CircleRouletteLittleMachine(numbers=[0, 5, 12, 3, 10, 1, 8, 9, 2, 7, 6, 11, 4], pay_for=12, history_size=7, total_amount=total_amount)
        crlm.INITIAL_WALLET = total_amount
        CircleRouletteLittleMachine.PROFIT_OUT = PROFIT_OUT

        print(f"💼 Cartera: {crlm.total_amount} DOP")
        crlm.initialize_history(INITIAL_HISTORY_BLOCKS=5)
        ronda_actual = INITIAL_HISTORY_BLOCKS - 1

        print(f"🎰 Presiona ENTER para jugar 🎰")

        while True:
            # Si AUTORUN es True y ya se pasó el límite de repeticiones, termina el juego
            if AUTORUN and COUNTER_AUTO >= MAX_REPEAT:
                print(f"Se completaron {MAX_REPEAT} rondas automáticas. Fin del juego.")
                print("Resumen final:")
                print("\n📜 Historial de jugadas")
                for ronda, sublista in enumerate(crlm.history, 1):
                    print(f"\t Ronda {ronda}: {sublista}")
                break

            if AUTORUN:
                # Simula ENTER
                key = b'\r'
                COUNTER_AUTO += 1
                time.sleep(PAUSE_AUTORUN)
            else:
                # Espera tecla real
                if not msvcrt.kbhit():
                    continue
                key = msvcrt.getch()

            if key == b'\r':
                ronda_actual += 1
                print(f"\n🎲 RONDA {ronda_actual}")

                # -- Validar si hay historial suficiente para predecir
                if not crlm.history:
                    print("Primera ronda sin historial. Jugada sin predicción.")
                    winning_number = crlm.start()
                    crlm.calculate_winning_amount(winning_number=winning_number)
                    continue

                if TOP_METHOD == 'TOP2':
                    a_num, b_num = crlm.get_hotters(top=2)
                    a_neigh_1, a_neigh_2 = crlm.get_neighbors(a_num)
                    b_neigh_1, b_neigh_2 = crlm.get_neighbors(b_num)

                    neighbors = [a_neigh_1, a_neigh_2, b_neigh_1, b_neigh_2]
                    crlm.selected_neighs = crlm.select_unique_neighbors(neighbors_list=neighbors, hotters=[a_num, b_num])

                    print(f"[🔍] Hotters seleccionados: {a_num}, {b_num}")
                    crlm.hotter_numbers = [a_num, b_num]
                    try:
                        bets = {
                            a_num: HOT_AMOUNT*crlm.get_multiplier(),
                            b_num: HOT_AMOUNT*crlm.get_multiplier(),
                            **{n: NEIGHT_AMOUNT*crlm.get_multiplier() for n in crlm.selected_neighs}
                        }
                        for n in crlm:
                            if n not in bets:
                                bets[n] = OTHER_AMOUNT*crlm.get_multiplier()
                        crlm.put_bet(bets)
                    except ValueError as e:
                        print(f"[Error en la apuesta]: {e}")
                        print(f'Te retiras con {crlm.total_amount} DOP')
                        print("Resumen final:")
                        print("\n📜 Historial de jugadas")
                        for ronda, sublista in enumerate(crlm.history, 1):
                            print(f"\t Ronda {ronda}: {sublista}")
                        break

                elif TOP_METHOD == 'TOP3':
                    a_num, b_num, c_num = crlm.get_hotters(top=3)
                    a_neigh_1, a_neigh_2 = crlm.get_neighbors(a_num)
                    b_neigh_1, b_neigh_2 = crlm.get_neighbors(b_num)
                    c_neigh_1, c_neigh_2 = crlm.get_neighbors(c_num)

                    neighbors = [
                        a_neigh_1, a_neigh_2,
                        b_neigh_1, b_neigh_2,
                        c_neigh_1, c_neigh_2
                    ]

                    crlm.selected_neighs = crlm.select_unique_neighbors(neighbors_list=neighbors, hotters=[a_num, b_num, c_num])

                    print(f"[🔍] Hotters seleccionados: {a_num}, {b_num}, {c_num}")
                    crlm.hotter_numbers = [a_num, b_num, c_num]
                    try:
                        bets = {
                            a_num: HOT_AMOUNT*crlm.get_multiplier(),
                            b_num: HOT_AMOUNT*crlm.get_multiplier(),
                            c_num: HOT_AMOUNT*crlm.get_multiplier(),
                            **{n: NEIGHT_AMOUNT*crlm.get_multiplier() for n in crlm.selected_neighs}
                        }
                        for n in crlm:
                            if n not in bets:
                                bets[n] = OTHER_AMOUNT*crlm.get_multiplier()
                        crlm.put_bet(bets)
                    except ValueError as e:
                        print(f"[Error en la apuesta]: {e}")
                        print(f'Te retiras con {crlm.total_amount} DOP')
                        print("\n\t📜 Historial de jugadas")
                        for ronda, sublista in enumerate(crlm.history, 1):
                            print(f"\t Ronda {ronda}: {sublista}")
                        break

                winning_number = crlm.start(secs_animation=ANIMATION_TIME_SECS)
                status = crlm.calculate_winning_amount(winning_number=winning_number)

                # -- ANTIMARTIGALA
                # -- Aumenta el multiplicador si acierta
                if USE_ANTIGALA:
                    if status:
                        crlm.add_multiplier()
                else:
                    crlm.INDEX = 0
                
                # -- Profit alcanzado
                if crlm.has_reach_profit():
                    print(f'Te retiras con {crlm.total_amount} DOP')
                    print("\n\t📜 Historial de jugadas")
                    for ronda, sublista in enumerate(crlm.history, 1):
                        print(f"\t Ronda {ronda}: {sublista}")
                    break

                # Verifica si el saldo se ha agotado
                if crlm.total_amount <= 0:
                    print("Saldo insuficiente. El juego ha terminado.")
                    print("\n\t📜 Historial de jugadas")
                    for ronda, sublista in enumerate(crlm.history, 1):
                        print(f"\t Ronda {ronda}: {sublista}")
                    break

            # ESCAPE Key para salir
            if key == b'\x1b':
                print(f'Te retiras con {crlm.total_amount} DOP')
                print("\n\t📜 Historial de jugadas")
                for ronda, sublista in enumerate(crlm.history, 1):
                    print(f"\t Ronda {ronda}: {sublista}")
                break
