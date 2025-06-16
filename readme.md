# 🎰 Roulette Simulator - Circle Roulette Little Machine

¡Bienvenido a **Roulette Simulator**! Este proyecto es una herramienta de simulación de ruleta diseñada para ofrecer una experiencia interactiva y estratégica de juego. Desarrollado en Python, permite a los usuarios realizar apuestas, seguir un historial de jugadas y aplicar estrategias basadas en números "calientes" (hotters) y vecinos, con el objetivo de alcanzar un profit deseado. 🤑

---

## 📜 Descripción

**Roulette Simulator** simula una ruleta con un conjunto predefinido de números (0 al 12 por defecto) y permite a los jugadores realizar apuestas basadas en diferentes métodos predictivos. El programa incluye animaciones, cálculo de ganancias y pérdidas, y un sistema de historial para analizar jugadas anteriores. 🎲

### 🛠️ Características Principales
- **Simulación de Ruleta**: Gira la ruleta con una animación personalizada y genera números ganadores aleatorios. 🔄
- **Estrategias de Apuesta**: Usa métodos como `TOP2` (dos números calientes) y `TOP3` (tres números calientes) para apostar en base a estadísticas del historial. 🔥
- **Historial de Jugadas**: Registra los resultados de las rondas anteriores para analizar patrones. 📊
- **Cálculo de Profit**: Calcula automáticamente las ganancias o pérdidas en porcentaje respecto al monto inicial. 💰
- **Vecinos Únicos**: Selecciona vecinos de los números calientes sin repeticiones, optimizando las apuestas. 🧠
- **Antimartingala Opcional**: Aumenta el multiplicador de apuesta tras una victoria para maximizar ganancias. 📈
- **Modo Automático**: Ejecuta múltiples rondas sin intervención manual para probar estrategias. ⚙️
- **Interfaz Visual**: Usa `cfonts` para mostrar números y mensajes en la terminal con colores atractivos. 🌈

---

## 🚀 Instalación

1. **Clona el repositorio** o descarga el archivo `roulette.py`.
2. **Instala las dependencias** ejecutando el siguiente comando en tu terminal:

   ```bash
   pip install cfonts
    ```

## 🎮 Uso

```
python roulette.py [TOP_METHOD] [HOT_AMOUNT] [NEIGHT_AMOUNT] [OTHER_AMOUNT] [RONDAS_SOPORTADAS] [PROFIT_OUT] [USE_ANTIGALA]
python roulette.py TOP3 40 20 5 20 10 1
python roulette.py TOP2 40 20 5 20 10 1
```

## 📋 Parámetros

- TOP_METHOD: Estrategia de selección de números calientes (TOP2 o TOP3). 🔥
- HOT_AMOUNT: Monto a apostar por cada número caliente. 💵
- NEIGHT_AMOUNT: Monto a apostar por los vecinos de los números calientes. 🧩
- OTHER_AMOUNT: Monto a apostar por los números restantes. 💳
- RONDAS_SOPORTADAS: Número de rondas que el saldo inicial puede soportar. ⏳
- PROFIT_OUT: Porcentaje de profit deseado para retirarse. 🎯
- USE_ANTIGALA: Habilita (1) o deshabilita (0) el sistema Antimartingala. 📈

Ejemplo

    ```
    python roulette.py TOP3 40 20 10 10 33 1
    ```

## 🕹️ Controles

- ENTER: Inicia una nueva ronda o confirma acciones. ✅
- ESC: Sale del juego y muestra el saldo final. 🚪

## 🧠 Estrategias de Juego

### TOP2
- Selecciona los 2 números más frecuentes del historial. 🔥
- Apuesta un monto mayor en ellos y un monto menor en sus vecinos y otros números. 🧮

### TOP3
- Selecciona los 3 números más frecuentes del historial. 🔥🔥🔥
- Similar a TOP2, pero distribuye las apuestas entre tres números calientes y sus vecinos. 📊
- Antimartingala (Opcional)
- Aumenta el multiplicador de las apuestas tras cada acierto, buscando maximizar ganancias en rachas positivas. 📈

## 💻 Detalles Técnicos

- Lenguaje: Python 3.x
- Módulos Utilizados:
    `msvcrt`: Captura de teclas en Windows. ⌨️
    `cfonts`: Renderizado de texto en la terminal con colores. 🌈
    `random`: Generación de números aleatorios. 🎲
    `itertools` y `collections`: Manejo de datos para historial y frecuencias. 📊
- Clase Principal: `CircleRouletteLittleMachine` - Gestiona la ruleta, apuestas, historial y cálculos. ⚙️