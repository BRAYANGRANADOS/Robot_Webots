from controller import Supervisor, Keyboard

def run_robot(robot):
    # Parámetros de simulación
    TIME_STEP = 32
    MAX_SPEED = 6.28

    # Inicializar Teclado
    kb = Keyboard()
    kb.enable(TIME_STEP)

    # Obtener nodo de la Viewpoint para cambiar la cámara
    viewpoint = robot.getFromDef("VIEWPOINT")
    follow_mode = False

    # Inicializar Motores
    left_motor = robot.getDevice('left wheel motor')
    right_motor = robot.getDevice('right wheel motor')
    left_motor.setPosition(float('inf'))
    right_motor.setPosition(float('inf'))
    left_motor.setVelocity(0.0)
    right_motor.setVelocity(0.0)

    # Inicializar Sensores de Proximidad (ps0 - ps7)
    proximity_sensors = []
    for i in range(8):
        sensor_name = 'ps' + str(i)
        sensor = robot.getDevice(sensor_name)
        sensor.enable(TIME_STEP)
        proximity_sensors.append(sensor)

    # Inicializar Sensores de Luz (ls0 - ls7)
    light_sensors = []
    for i in range(8):
        sensor_name = 'ls' + str(i)
        sensor = robot.getDevice(sensor_name)
        sensor.enable(TIME_STEP)
        light_sensors.append(sensor)

    # Inicializar LEDs (led0 - led9)
    leds = []
    for i in range(10):
        led_name = 'led' + str(i)
        led = robot.getDevice(led_name)
        leds.append(led)

    # Inicializar Otros Sensores
    gyro = robot.getDevice('gyro')
    gyro.enable(TIME_STEP)

    accelerometer = robot.getDevice('accelerometer')
    accelerometer.enable(TIME_STEP)

    camera = robot.getDevice('camera')
    camera.enable(TIME_STEP)
    cam_width = camera.getWidth()
    cam_height = camera.getHeight()

    # Variables de estado
    reached_goal = False
    state = "BUSCANDO_PARED"

    print("Controlador del E-Puck iniciado. Navegando por el laberinto...")

    while robot.step(TIME_STEP) != -1:
        # 0. Gestión de la Cámara mediante Teclado
        key = kb.getKey()
        if key != -1:
            # Convertir a mayúsculas para simplificar
            actual_key = chr(key).upper() if key < 256 else ""
            
            if actual_key == 'V':
                # Activar modo seguimiento
                viewpoint.getField("follow").setSFString("E-puck")
                viewpoint.getField("followType").setSFString("Tracking Shot")
                # Forzar una posición cercana al robot relativo a su posición inicial
                # Esto obliga a la cámara a bajar desde la vista global
                viewpoint.getField("position").setSFVec3f([-0.7, -0.7, 0.4])
                viewpoint.getField("orientation").setSFRotation([-0.5, 0.5, 0.8, 1.2])
                print(">>> Cámara: Siguiendo al robot (V) - Zoom activado.")
                follow_mode = True
            elif actual_key == 'G':
                # Desactivar seguimiento y resetear vista
                viewpoint.getField("follow").setSFString("")
                # Pequeña pausa interna para asegurar que el campo se limpie
                viewpoint.getField("position").setSFVec3f([1.5, 1.5, 2.5])
                viewpoint.getField("orientation").setSFRotation([-0.5, 0.5, 0.8, 1.5])
                print(">>> Cámara: Vista Global restaurada (G).")
                follow_mode = False

        # 1. Leer datos de sensores
        ps_values = [sensor.getValue() for sensor in proximity_sensors]
        
        # 2. Procesar imagen de la CÁMARA para detectar la META ROJA
        image = camera.getImage()
        red_pixels = 0
        
        # Analizamos la mitad inferior de la imagen (donde suele estar el objeto en el suelo)
        # y un ancho mayor
        for x in range(int(cam_width/8), int(7*cam_width/8)):
            for y in range(int(cam_height/2), cam_height):
                r = camera.imageGetRed(image, cam_width, x, y)
                g = camera.imageGetGreen(image, cam_width, x, y)
                b = camera.imageGetBlue(image, cam_width, x, y)
                # Detección de rojo más robusta: R mucho mayor que G y B
                if r > 120 and r > g * 2 and r > b * 2:
                    red_pixels += 1
        
        # Si detectamos rojo, mostramos un aviso en consola
        if red_pixels > 10:
            print(f"Meta detectada: {red_pixels} px rojos.")

        # Condición de parada sensible (como antes, para que no pase de largo)
        # Se detiene en cuanto ve una cantidad mínima de rojo
        if red_pixels > 15: 
            reached_goal = True

        if reached_goal:
            left_motor.setVelocity(0.0)
            right_motor.setVelocity(0.0)
            state = "META_ALCANZADA"
            # Juego de luces de éxito
            t = robot.getTime()
            for i, led in enumerate(leds):
                led.set(1 if int(t * 10 + i) % 2 == 0 else 0)
            
            if not hasattr(run_robot, "logged_finish"):
                print(f">>> META DETECTADA POR CÁMARA ({red_pixels} px rojos). Deteniendo robot.")
                run_robot.logged_finish = True
            continue

        # 3. Lógica de Navegación "Consciente"
        # Ajustamos umbrales para que el robot vaya a aprox 20cm
        OBSTACLE_THRESHOLD = 120 
        WALL_DISTANCE_LOW = 70  
        WALL_DISTANCE_HIGH = 120 
        
        # Sensores frontales y laterales derechos para detectar barriles o NPC
        front_val = max(ps_values[0], ps_values[7])
        right_val = max(ps_values[1], ps_values[2])
        
        # Umbral MUCHO más sensible para el NPC y barriles para evitar el choque
        DANGER_THRESHOLD = 250 # Detecta obstáculos móviles desde más lejos
        
        left_speed = MAX_SPEED * 0.6
        right_speed = MAX_SPEED * 0.6

        if front_val > DANGER_THRESHOLD or ps_values[1] > DANGER_THRESHOLD:
            # EL CUBO AZUL O BARRIL ESTÁ MUY CERCA: Retroceder y esperar a que pase
            state = "ESPERANDO_PASO"
            # Retroceso suave para dar espacio al NPC móvil
            left_speed = -MAX_SPEED * 0.25
            right_speed = -MAX_SPEED * 0.25
            for led in leds: led.set(1) 
            if not hasattr(run_robot, "wait_msg") or not run_robot.wait_msg:
                print(">>> Obstáculo móvil detectado. Cediendo el paso...")
                run_robot.wait_msg = True
        elif front_val > OBSTACLE_THRESHOLD:
            # Algo al frente: Girar para esquivar
            state = "EVITANDO_OBSTACULO"
            left_speed = -MAX_SPEED * 0.4
            right_speed = MAX_SPEED * 0.4
            for led in leds: led.set(0)
            leds[0].set(1)
            run_robot.wait_msg = False
        elif right_val > OBSTACLE_THRESHOLD:
            # Siguiendo pared o barril a distancia segura
            state = "SIGUIENDO_PARED"
            run_robot.wait_msg = False
            if ps_values[1] > WALL_DISTANCE_HIGH:
                left_speed = MAX_SPEED * 0.4
                right_speed = MAX_SPEED * 0.6
            elif ps_values[1] < WALL_DISTANCE_LOW:
                left_speed = MAX_SPEED * 0.6
                right_speed = MAX_SPEED * 0.4
            else:
                left_speed = MAX_SPEED * 0.6
                right_speed = MAX_SPEED * 0.6
            for led in leds: led.set(0)
            leds[8].set(1)
        else:
            # Camino despejado: Buscar pared
            state = "BUSCANDO_PARED"
            run_robot.wait_msg = False
            left_speed = MAX_SPEED * 0.6
            right_speed = MAX_SPEED * 0.45
            for led in leds: led.set(0)
            leds[1].set(1)

        # Imprimir estado si cambia (opcional para depuración)
        if not hasattr(run_robot, "last_state") or run_robot.last_state != state:
            print(f"Estado: {state}")
            run_robot.last_state = state

        # Aplicar velocidades
        left_motor.setVelocity(left_speed)
        right_motor.setVelocity(right_speed)

if __name__ == "__main__":
    my_robot = Supervisor()
    run_robot(my_robot)
