import pygame
import random
import math
from collections import Counter

# Inicialización de Pygame
pygame.init()

# Configuración de la ventana
width, height = 800, 800  # Ajustado para hacer espacio para la cuarta ventana
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Simulación VR con Ecolocalización y Proyección 3D")

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)
COLORS = [WHITE, GREEN, YELLOW, ORANGE, RED, DARK_RED]
COLOR_NAMES = ['Blanco', 'Verde', 'Amarillo', 'Naranja', 'Rojo', 'Rojo Oscuro']


# Datos simulados de sensores de ecolocalización
def generate_sensor_data():
    data = []
    radius = 100 * 1.7  # Radio del círculo rojo ajustado con escala 1.7
    center_x = width // 4
    center_y = height // 3  # Subir la zona de puntos aleatorios
    for _ in range(10):  # Generar solo 10 puntos para la proyección 3D
        x = random.uniform(center_x - radius, center_x + radius)
        y = random.uniform(center_y - radius, center_y + radius)
        z = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
        if z <= radius:  # Asegurarse de que los puntos estén dentro del círculo rojo
            data.append((x, y, z))
    return data


# Generar los datos una sola vez
sensor_data = generate_sensor_data()


# Función para proyectar puntos en 3D
def project_3d_to_2d(x, y, z, viewer_distance=500, scale=1):
    factor = viewer_distance / (viewer_distance + z)
    x = x * factor * scale + width // 4 * 3  # Ajuste para la posición en la pantalla
    y = -y * factor * scale + height // 3  # Subir la vista 3D
    return int(x), int(y)


# Función para dibujar una persona simple en 3D
def draw_person(screen, x, y, color, scale=1):
    # Ajuste de tamaño
    head_radius = 10 * scale
    body_length = 20 * scale
    arm_length = 10 * scale
    leg_length = 10 * scale

    # Dibujar cabeza
    pygame.draw.circle(screen, color, (x, y - 40 * scale), head_radius)  # Cabeza

    # Dibujar cuerpo
    pygame.draw.line(screen, color, (x, y - 30 * scale), (x, y - 10 * scale), 2)  # Cuerpo

    # Dibujar brazos
    pygame.draw.line(screen, color, (x, y - 25 * scale), (x - arm_length, y - 20 * scale), 2)  # Brazo izquierdo
    pygame.draw.line(screen, color, (x, y - 25 * scale), (x + arm_length, y - 20 * scale), 2)  # Brazo derecho

    # Dibujar piernas
    pygame.draw.line(screen, color, (x, y - 10 * scale), (x - leg_length, y), 2)  # Pierna izquierda
    pygame.draw.line(screen, color, (x, y - 10 * scale), (x + leg_length, y), 2)  # Pierna derecha


# Función para dibujar círculos de distancia
def draw_distance_circles(screen, center_x, center_y, distances, colors):
    font = pygame.font.Font(None, 24)
    for i, distance in enumerate(distances):
        pygame.draw.circle(screen, colors[i], (center_x, center_y), int(distance * 1.7), 2)  # Escalar los círculos
        label = font.render(f'{distance // 10}m', True, colors[i])
        screen.blit(label, (center_x + int(distance * 1.7), center_y))


# Función para determinar el color basado en la distancia z
def get_color_by_distance(z, distances):
    if z < distances[0] * 1.7:
        return COLORS[0]
    elif z < distances[1] * 1.7:
        return COLORS[1]
    elif z < distances[2] * 1.7:
        return COLORS[2]
    elif z < distances[3] * 1.7:
        return COLORS[3]
    else:
        return COLORS[4]


# Función para dibujar el cono de visión de 90 grados
def draw_vision_cone(screen, center_x, center_y, length, color, angle):
    half_angle = math.radians(45)  # 90 grados dividido por 2
    left_angle = angle - half_angle
    right_angle = angle + half_angle

    left_x = center_x + length * math.cos(left_angle)
    left_y = center_y + length * math.sin(left_angle)
    right_x = center_x + length * math.cos(right_angle)
    right_y = center_y + length * math.sin(right_angle)

    # Dibujar los lados del cono
    pygame.draw.line(screen, color, (center_x, center_y), (left_x, left_y), 2)
    pygame.draw.line(screen, color, (center_x, center_y), (right_x, right_y), 2)

    # Dibujar los 90 grados del círculo base del cono en blanco
    base_radius = length
    pygame.draw.arc(screen, color, (center_x - base_radius, center_y - base_radius, base_radius * 2, base_radius * 2),
                    left_angle, right_angle, 2)


# Función para verificar si un punto está dentro del cono de visión y calcular su posición relativa
def is_point_in_cone(point, cone_origin, cone_angle, cone_width, cone_length):
    px, py = point
    ox, oy = cone_origin
    dx, dy = px - ox, py - oy
    distance = math.hypot(dx, dy)

    if distance > cone_length:
        return False, None

    angle_to_point = math.atan2(dy, dx)
    angle_diff = (angle_to_point - cone_angle + math.pi) % (2 * math.pi) - math.pi

    if abs(angle_diff) < cone_width / 2:
        relative_angle = angle_diff / cone_width
        return True, relative_angle
    return False, None


# Función para dibujar una flecha
def draw_arrow(screen, x, y, color, direction='left'):
    arrow_size = 20
    if direction == 'left':
        points = [(x, y), (x + arrow_size, y - arrow_size // 2), (x + arrow_size, y + arrow_size // 2)]
    else:
        points = [(x, y), (x - arrow_size, y - arrow_size // 2), (x - arrow_size, y + arrow_size // 2)]
    pygame.draw.polygon(screen, color, points)


# Loop principal
running = True
clock = pygame.time.Clock()

distances = [20, 40, 60, 80, 100]
cone_length = int(distances[-1] * 1.7)
circle_center_x = width // 4
circle_center_y = height // 3
cone_angle = 0  # Inicializar el ángulo del cono

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse_x, mouse_y = pygame.mouse.get_pos()
    if (0 <= mouse_x <= width // 2) and (0 <= mouse_y <= height // 2):
        # Calcular el ángulo entre el centro del círculo y el cursor
        dx = mouse_x - circle_center_x
        dy = mouse_y - circle_center_y
        cone_angle = math.atan2(dy, dx)

    screen.fill(BLACK)

    # Contadores para los puntos y monigotes por color
    point_colors = Counter()
    person_colors = Counter()
    left_arrows = Counter()
    right_arrows = Counter()

    # Dibujar círculos de distancia
    draw_distance_circles(screen, circle_center_x, circle_center_y, distances, COLORS)

    # Dibujar el cono de visión, centrado en el círculo rojo
    draw_vision_cone(screen, circle_center_x, circle_center_y, cone_length, WHITE, cone_angle)

    # Dibujar puntos 2D en el mapa plano (mitad izquierda)
    for point in sensor_data:
        x, y, z = point
        if x < width // 2:
            color = get_color_by_distance(z, distances)
            if color != RED or z <= distances[
                -1] * 1.7:  # Asegurarse de que los puntos rojos estén dentro del círculo rojo
                pygame.draw.circle(screen, color, (int(x), int(y)), 5)
                point_colors[color] += 1

    # Dibujar línea de suelo en la vista 3D (mitad derecha)
    ground_level = height // 3 + 100
    pygame.draw.line(screen, WHITE, (width // 2, ground_level), (width, ground_level), 2)

    # Dibujar proyección 3D con forma de personas (mitad derecha) correlacionadas con los puntos
    for point in sensor_data:
        x, y, z = point
        in_cone, relative_angle = is_point_in_cone((x, y), (circle_center_x, circle_center_y), cone_angle,
                                                   math.radians(90), cone_length)
        if in_cone:
            x2d = int(((relative_angle + 0.5) * width // 2) + width // 2)
            y2d = ground_level
            color = get_color_by_distance(z, distances)

            # Escala basada en color
            if color == WHITE:
                scale = 7
            elif color == GREEN:
                scale = 6
            elif color == YELLOW:
                scale = 4
            elif color == ORANGE:
                scale = 2
            else:
                scale = 1  # Para otros colores no especificados, usar escala normal

            draw_person(screen, x2d, y2d, color, scale)
            person_colors[color] += 1
        else:
            angle_to_point = math.atan2(y - circle_center_y, x - circle_center_x)
            if (color != RED or z <= distances[-1] * 1.7):  # No contar puntos rojos fuera del círculo rojo
                if -math.pi < angle_to_point < -math.pi / 2 or math.pi / 2 < angle_to_point < math.pi:
                    left_arrows[get_color_by_distance(z, distances)] += 1
                else:
                    right_arrows[get_color_by_distance(z, distances)] += 1

    # Dibujar flechas y contadores
    y_offset_start = ground_level + 20
    y_offsets = {
        WHITE: y_offset_start,
        GREEN: y_offset_start + 40,
        YELLOW: y_offset_start + 80,
        ORANGE: y_offset_start + 120,
        RED: y_offset_start + 160,
    }

    for color in COLORS[:-1]:  # Excluir DARK_RED ya que no se usa en el contador
        if color in left_arrows:
            draw_arrow(screen, width // 2 + 10, y_offsets[color], color, 'left')
            font = pygame.font.Font(None, 36)
            text_surface = font.render(str(left_arrows[color]), True, color)
            text_rect = text_surface.get_rect(center=(width // 2 + 50, y_offsets[color]))
            screen.blit(text_surface, text_rect.topleft)

        if color in right_arrows:
            draw_arrow(screen, width - 30, y_offsets[color], color, 'right')
            font = pygame.font.Font(None, 36)
            text_surface = font.render(str(right_arrows[color]), True, color)
            text_rect = text_surface.get_rect(center=(width - 60, y_offsets[color]))
            screen.blit(text_surface, text_rect.topleft)

    # Línea divisoria
    pygame.draw.line(screen, WHITE, (width // 2, 0), (width // 2, height), 2)

    # Dibujar textos en cada recuadro
    font_title = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)

    text_eco = font_title.render("Sensor Eco simulado 2D", True, WHITE)
    text_vr = font_title.render("Visor en Primera Persona VR", True, WHITE)
    text_log = font_title.render("Log:", True, WHITE)
    text_extra = font_title.render("Ventana Extra", True, WHITE)

    screen.blit(text_eco, (10, 10))
    screen.blit(text_vr, (width // 2 + 10, 10))
    screen.blit(text_log, (width // 2 + 10, height - 215))  # Ajustado para subir el techo del cuadro de los logs
    screen.blit(text_extra, (10, height - 290))

    # Texto adicional en el área de log
    log_text_lines = ["", ""]
    log_text_lines += [f"{COLOR_NAMES[COLORS.index(color)]}: {count}" for color, count in person_colors.items()]

    y_offset = height - 185  # Ajustado para subir el texto en el cuadro de los logs
    for line in log_text_lines:
        log_surface = font_small.render(line, True, WHITE)
        screen.blit(log_surface, (width // 2 + 10, y_offset))
        y_offset += log_surface.get_height() + 5

    # Texto adicional en el área de datos generales
    data_general_lines = ["Datos Generales:"]
    data_general_lines += [f"{COLOR_NAMES[COLORS.index(color)]}: {count}" for color, count in point_colors.items()]

    y_offset = height - 260
    for line in data_general_lines:
        data_surface = font_small.render(line, True, WHITE)
        screen.blit(data_surface, (10, y_offset))
        y_offset += data_surface.get_height() + 5

    # Dibujar el área de log (mitad derecha inferior)
    pygame.draw.rect(screen, WHITE, (width // 2, height - 225, width // 2, 225),
                     2)  # Ajustado para subir el techo del cuadro de los logs

    # Dibujar el área extra (cuarta ventana)
    pygame.draw.rect(screen, WHITE, (0, height - 300, width // 2, 300), 2)

    # Actualizar la pantalla
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
