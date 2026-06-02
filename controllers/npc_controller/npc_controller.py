from controller import Supervisor

def run_npc(robot):
    TIME_STEP = 32
    # Velocidad de patrullaje constante
    SPEED = 0.005 
    
    self_node = robot.getSelf()
    translation_field = self_node.getField("translation")
    
    current_y = 0.0
    direction = 1
    # Límites para el patrullaje
    limit_y = 0.7 

    print("NPC azul: Patrullaje continuo activado.")

    while robot.step(TIME_STEP) != -1:
        # El NPC ahora se mueve siempre, sin importar dónde esté el robot principal
        current_y += SPEED * direction
        
        # Cambiar dirección al llegar a los límites
        if current_y > limit_y:
            direction = -1
        elif current_y < -limit_y:
            direction = 1
            
        # Aplicar el movimiento de traslación
        translation_field.setSFVec3f([-0.25, current_y, 0.05])

if __name__ == "__main__":
    my_robot = Supervisor()
    run_npc(my_robot)
