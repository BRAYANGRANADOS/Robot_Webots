# Proyecto Webots - Tarea 2: Laberinto y Robótica Autónoma

¡Bienvenido! Este es el archivo **README.md**. En GitHub, este archivo es lo primero que cualquier persona verá al entrar a tu repositorio. Funciona como la "portada" y el manual de usuario de tu proyecto.

Este proyecto simula un robot E-puck navegando en un entorno dinámico de Webots con obstáculos móviles y detección de objetivos mediante visión artificial.

---

## 🔍 Análisis Profundo del Código

A continuación, se detalla el funcionamiento lógico de cada controlador desarrollado en Python.

### 1. Controlador del Robot Principal ([epuck_controller.py](file:///home/adb/Descargas/Brayan_Granados/tarea2%20(1)/tarea2/controllers/epuck_controller/epuck_controller.py))

Este es el cerebro del robot. Utiliza una arquitectura basada en **Máquina de Estados** para decidir su comportamiento en tiempo real.

#### **A. Percepción Visual (Detección de Meta)**
El robot no sabe dónde está la meta por coordenadas, sino que la "ve".
- **Cámara**: Se procesa la imagen capturada (`camera.getImage()`).
- **Algoritmo**: Recorre los píxeles de la mitad inferior de la imagen buscando el color rojo.
- **Filtro RGB**: Para evitar falsos positivos, el código verifica que el canal Rojo (`R`) sea significativamente mayor que el Verde (`G`) y el Azul (`B`) (`r > g * 2 and r > b * 2`).
- **Detección**: Si encuentra más de 15 píxeles rojos, el estado cambia a `META_ALCANZADA` y el robot se detiene activando un juego de luces LED.

#### **B. Sistema de Navegación y Evasión**
Utiliza 8 sensores de proximidad (`ps0` a `ps7`) para mapear su entorno inmediato:
- **Estado `ESPERANDO_PASO`**: Si los sensores frontales detectan un valor muy alto (>250), el robot asume que un obstáculo móvil (como el NPC o un barril) se ha cruzado. El robot retrocede ligeramente y espera, cediendo el paso.
- **Estado `EVITANDO_OBSTACULO`**: Si hay algo cerca al frente pero no es crítico, gira sobre su propio eje.
- **Estado `SIGUIENDO_PARED`**: Utiliza un algoritmo de control proporcional simple para mantener una distancia constante con la pared derecha.
- **Estado `BUSCANDO_PARED`**: Si no detecta nada a la derecha, gira suavemente en esa dirección para intentar localizar una superficie.

#### **C. Control Interactivo de Cámara**
Se implementó una función de **Supervisor** que permite al usuario interactuar con la simulación mediante el teclado:
- **Tecla `V`**: Cambia el nodo `VIEWPOINT` para que la cámara siga automáticamente al robot desde una perspectiva cercana.
- **Tecla `G`**: Resetea la cámara a una vista global del laberinto.

---

### 2. Controlador de Barriles ([barrel_controller.py](file:///home/adb/Descargas/Brayan_Granados/tarea2%20(1)/tarea2/controllers/barrel_controller/barrel_controller.py))

Este código utiliza las capacidades de **Supervisor** de Webots para manipular la física del mundo.
- **Lógica**: Define una posición inicial (`start_x`) y utiliza una variable `direction` (1 o -1) para alternar el movimiento.
- **Movimiento**: En cada paso de simulación, suma un pequeño incremento (`SPEED`) a la traslación actual. Cuando el desplazamiento supera el `range_x` (0.15m), invierte la dirección.
- **Impacto**: Crea un obstáculo dinámico que obliga al E-puck a usar su estado de "espera" o "evasión".

---

### 3. Controlador del NPC Azul ([npc_controller.py](file:///home/adb/Descargas/Brayan_Granados/tarea2%20(1)/tarea2/controllers/npc_controller/npc_controller.py))

Similar al de los barriles, pero configurado para patrullaje de largo alcance.
- **Eje de movimiento**: Se desplaza a lo largo del eje Y.
- **Límites**: Tiene un rango de patrulla de 0.7 metros hacia cada lado.
- **Independencia**: El NPC no reacciona al robot; es un elemento del entorno que el robot principal debe aprender a esquivar mediante sus sensores infrarrojos.

---

## 🛠️ Tecnologías Utilizadas
- **Webots R2023b**: Motor de simulación.
- **Python 3.12**: Lenguaje de programación de los controladores.
- **Git**: Control de versiones.

## 🚀 Instalación y Uso
1. Instala Webots.
2. Clona este repositorio: `git clone https://github.com/BRAYANGRANADOS/Robot_Webots.git`
3. Abre el archivo `worlds/tarea2robot.wbt`.
4. Haz clic en el botón de "Reproducir" en la parte superior de Webots.
