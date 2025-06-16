#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = 'José E. Morales Ventura'
__date__ = '15/Junio/2025'
__proyect__ = 'roulette.py'
__description__ = '''Herramienta de Ruleta'''

import argparse
import msvcrt
import random
from itertools import chain
from collections import Counter
import os, sys
import cfonts
import time
from dotenv import load_dotenv
load_dotenv()

def singleton(cls):
    instances = {}
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@singleton
class CircleRouletteLittleMachine(list):
    '''
    Representación de una ruleta circular
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
        self.MULTIPLICADOR = [int(x) for x in os.getenv('gale').replace(' ','').split(',')]
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

    def display_number(self, number:int):
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
        print(f"\t 💥 Ronda -> {self.ROUND_NUMBER}")
        
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
    
    def show_history(self):
        '''
        Muestra el historial de jugadas
        '''
        print("\n\t📝 Historial de jugadas")
        for ronda, sublista in enumerate(self.history, 1):
            print(f"\t ✅Ronda {ronda}: {sublista}")

def main(crlm:CircleRouletteLittleMachine) -> None:
    '''
    Función de inicialización
    '''
     
    global TOP_METHOD
    global HOT_AMOUNT
    global NEIGHT_AMOUNT
    global OTHER_AMOUNT
    global RONDAS_SOPORTADAS
    global PROFIT_OUT
    global USE_ANTIGALA
    global AUTORUN
    global MAX_REPEAT
    global ANIMATION_TIME_SECS
    global COUNTER_AUTO
    global INITIAL_HISTORY_BLOCKS
    global PAUSE_AUTORUN

    ronda_actual = INITIAL_HISTORY_BLOCKS - 1
    while True:
        # Si AUTORUN es True y ya se pasó el límite de repeticiones, termina el juego
        if AUTORUN and COUNTER_AUTO >= MAX_REPEAT:
            print(f"Se completaron {MAX_REPEAT} rondas automáticas. Fin del juego.")
            crlm.show_history()
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
            print(f"\n✅Ronda {ronda_actual}")

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

                print(f"🔥 Hotters seleccionados: {a_num}, {b_num}")
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
                    print(f"🚧 ADVERTENCIA : {e}")
                    print(f'Te retiras con {crlm.total_amount} DOP')
                    crlm.show_history()
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

                print(f"🔥 Hotters seleccionados: {a_num}, {b_num}, {c_num}")
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
                    print(f"🚧 ADVERTENCIA : {e}")
                    print(f'Te retiras con {crlm.total_amount} DOP')
                    crlm.show_history()
                    break
            # -- CREA  AQUI TU PROPIA ESTRATEGIA PARA TESTEAR
            elif TOP_METHOD == 'IA1':
                try:
                    bets = {
                        0:HOT_AMOUNT*crlm.get_multiplier(),
                        1:NEIGHT_AMOUNT*crlm.get_multiplier(),
                        2:HOT_AMOUNT*crlm.get_multiplier(),
                        3:NEIGHT_AMOUNT*crlm.get_multiplier(),
                        4:HOT_AMOUNT*crlm.get_multiplier(),
                        5:NEIGHT_AMOUNT*crlm.get_multiplier(),
                        6:HOT_AMOUNT*crlm.get_multiplier(),
                        7:NEIGHT_AMOUNT*crlm.get_multiplier(),
                        8:HOT_AMOUNT*crlm.get_multiplier(),
                        9:NEIGHT_AMOUNT*crlm.get_multiplier(),
                        10:HOT_AMOUNT*crlm.get_multiplier(),
                        11:NEIGHT_AMOUNT*crlm.get_multiplier(),
                        12:HOT_AMOUNT*crlm.get_multiplier(),
                    }
                    crlm.put_bet(bets)
                except ValueError as e:
                    print(f"[Error en la apuesta]: {e}")
                    print(f'Te retiras con {crlm.total_amount} DOP')
                    crlm.show_history()
                    break
            elif TOP_METHOD == 'IA2':
                a_num, b_num = crlm.get_hotters(top=2)
                print(f"🔥 Hotters seleccionados: {a_num}, {b_num}")
                crlm.hotter_numbers = [a_num, b_num]
                try:
                    bets = {
                        a_num:HOT_AMOUNT*crlm.get_multiplier(),
                        b_num:HOT_AMOUNT*crlm.get_multiplier(),
                        0:NEIGHT_AMOUNT*crlm.get_multiplier()
                    }
                    for n in crlm:
                        if (n not in bets):
                            bets[n] = HOT_AMOUNT*crlm.get_multiplier()
                        if (n in [a_num, b_num]):
                            bets[n] += NEIGHT_AMOUNT*crlm.get_multiplier()
                    crlm.put_bet(bets)
                except ValueError as e:
                    print(f"[Error en la apuesta]: {e}")
                    print(f'Te retiras con {crlm.total_amount} DOP')
                    crlm.show_history()
                    break
            else:
                pass

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
                crlm.show_history()
                break

            # Verifica si el saldo se ha agotado
            if crlm.total_amount <= 0:
                print("Saldo insuficiente. El juego ha terminado.")
                crlm.show_history()
                break

        # ESCAPE Key para salir
        if key == b'\x1b':
            print(f'Te retiras con {crlm.total_amount} DOP')
            crlm.show_history()
            break

if __name__ == "__main__":
    # -- Configurar ARGPARSE para manejar los argumentos desde la línea de comandos
    parser = argparse.ArgumentParser(description='Simulación de Ruleta')

    parser.add_argument('--method', type=str, required=True, help='Estrategia de selección de números calientes (TOP2 o TOP3)')
    parser.add_argument('--hot_amount', type=int, required=True, help='Monto a apostar por cada número caliente')
    parser.add_argument('--neight_amount', type=int, required=True, help='Monto a apostar por los vecinos de los números calientes')
    parser.add_argument('--other_amount', type=int, required=True, help='Monto a apostar por los números restantes')
    parser.add_argument('--rondas_soportadas', type=int, required=True, help='Número de rondas que el saldo inicial puede soportar')
    parser.add_argument('--profit_out', type=int, required=True, help='Porcentaje de profit deseado para retirarse')
    parser.add_argument('--use_antigala', type=int, choices=[0, 1], required=True, help='Habilita (1) o deshabilita (0) el sistema Antimartingala')
    parser.add_argument('--autorun', type=int, choices=[0, 1], required=True, help='Ejecutar automáticamente (1) o manualmente (0)')
    parser.add_argument('--max_repeat', type=int, required=True, help='Maximo numero de jugadas en automático')

    args = parser.parse_args()

    os.system('cls')

    output = cfonts.render('ROULETTE', colors=['red', 'yellow'], align='center')
    print(output)

    TOP_METHOD = args.method
    HOT_AMOUNT = args.hot_amount
    NEIGHT_AMOUNT = args.neight_amount
    OTHER_AMOUNT = args.other_amount
    RONDAS_SOPORTADAS = args.rondas_soportadas
    PROFIT_OUT = args.profit_out
    USE_ANTIGALA = bool(args.use_antigala)
    AUTORUN = bool(args.autorun)
    MAX_REPEAT = args.max_repeat

    # -- Tiempo de visualizacion de animacion
    ANIMATION_TIME_SECS = int(os.getenv('animation_time'))
    # -- Control de autoincremento
    COUNTER_AUTO = int(os.getenv('counter_auto'))
    # -- Simular N rondas de historial para iniciar
    INITIAL_HISTORY_BLOCKS = int(os.getenv('initial_history_blocks'))
    # -- Pausa entre automatizacion de autorun
    PAUSE_AUTORUN = int(os.getenv('pause_autorun_time'))

    if TOP_METHOD == 'TOP2':
        total_amount = 160 * RONDAS_SOPORTADAS
    elif TOP_METHOD == 'TOP3':
        total_amount = 240 * RONDAS_SOPORTADAS
    elif TOP_METHOD == 'IA1':
        total_amount = 140 * RONDAS_SOPORTADAS
    elif TOP_METHOD == 'IA2':
        total_amount = 1390 * RONDAS_SOPORTADAS
    else:
        raise ValueError('El top indicado no es valido')

    crlm = CircleRouletteLittleMachine(numbers=[int(x) for x in os.getenv('numbers').replace(' ','').split(',')],
                                       pay_for=int(os.getenv('payed_wins')),
                                       history_size=int(os.getenv('display_last')),
                                       total_amount=total_amount)
    crlm.INITIAL_WALLET = total_amount
    CircleRouletteLittleMachine.PROFIT_OUT = PROFIT_OUT
    crlm.initialize_history(INITIAL_HISTORY_BLOCKS=INITIAL_HISTORY_BLOCKS)
    
    print(f"💼 Cartera Requerida: {crlm.total_amount} DOP")
    print("🎉 ¡Prepárate para girar la ruleta! 🎉")
    print("⭐ Apuesta sabiamente y alcanza el máximo profit. ⭐")
    print("💼 Revisa tu saldo y ajusta tus apuestas. 💰")
    print("⚙️ Configura tus estrategias para maximizar las ganancias. 🎯")
    input(f"\n🎰 Presiona ENTER para iniciar 🎰")

    main(crlm)