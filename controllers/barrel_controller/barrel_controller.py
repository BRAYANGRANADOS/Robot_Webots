from controller import Supervisor

def run_barrels(robot):
    TIME_STEP = 32
    # Velocidad de movimiento lateral
    SPEED = 0.005 
    
    self_node = robot.getSelf()
    translation_field = self_node.getField("translation")
    
    # Obtener la posición inicial
    initial_pos = self_node.getPosition()
    start_x = initial_pos[0]
    start_y = initial_pos[1]
    start_z = initial_pos[2]
    
    # Rango de movimiento en X (izquierda-derecha)
    range_x = 0.15 
    direction = 1
    current_offset_x = 0.0

    print(f"Barril {robot.getName()} iniciado: Movimiento lateral activo.")

    while robot.step(TIME_STEP) != -1:
        current_offset_x += SPEED * direction
        
        # Cambiar dirección al llegar a los límites
        if abs(current_offset_x) > range_x:
            direction *= -1
            
        # Aplicar la nueva posición
        translation_field.setSFVec3f([start_x + current_offset_x, start_y, start_z])

if __name__ == "__main__":
    my_robot = Supervisor()
    run_barrels(my_robot)
