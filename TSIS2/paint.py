import pygame
import datetime
import tools 


pygame.init()
WIDTH, HEIGHT = 1000, 800
CANVAS_Y_OFFSET = 200
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyGame Paint - Fixed for Mac")


canvas = pygame.Surface((WIDTH, HEIGHT - CANVAS_Y_OFFSET))
canvas.fill((255, 255, 255))


font = pygame.font.SysFont("Arial", 16)
text_font = pygame.font.SysFont("Arial", 24) 


PALETTE = [(0,0,0), (255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,165,0)]
color = PALETTE[0]
brush_sizes = {1: 2, 2: 5, 3: 10}
current_size = brush_sizes[2]
mode = 'pencil'
drawing = False
last_pos = None

typing = False
text_input = ""
text_pos = (0, 0)

def draw_gui():
    pygame.draw.rect(screen, (40, 40, 40), (0, 0, WIDTH, CANVAS_Y_OFFSET))
    lines = [
        f"ЦВЕТ: {color} | РАЗМЕР: {current_size}px | РЕЖИМ: {mode.upper()}",
        "Фигуры: [R]-Rect, [S]-Square, [C]-Circle, [T]-Text, [E]-Equi Tri, [H]-Rhombus",
        "Инструменты: [P]-Pencil, [L]-Line, [F]-Flood Fill | [N]-New Canvas",
        "Цвета: [F1]-[F6] | Сохранить: [Cmd/Ctrl+S] | Выход: [ESC]"
    ]
    for i, l in enumerate(lines):
        screen.blit(font.render(l, True, (250, 250, 250)), (20, 20 + i*25))
    
    for i, c in enumerate(PALETTE):
        rect = pygame.Rect(20 + i*40, 130, 30, 30)
        pygame.draw.rect(screen, c, rect)
        if c == color:
            pygame.draw.rect(screen, (255, 255, 255), rect, 3)

running = True
while running:
    screen.fill((100, 100, 100))
    draw_gui()
    screen.blit(canvas, (0, CANVAS_Y_OFFSET))
    
    m_pos = pygame.mouse.get_pos()
    c_pos = (m_pos[0], m_pos[1] - CANVAS_Y_OFFSET)

    if typing:
        preview = text_font.render(text_input + "|", True, color)
        screen.blit(preview, (text_pos[0], text_pos[1] + CANVAS_Y_OFFSET))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if typing:
                    typing = False
                    text_input = ""
                else:
                    running = False

            mods = pygame.key.get_mods()
            if event.key == pygame.K_s and (mods & (pygame.KMOD_CTRL | pygame.KMOD_META)):
                filename = f"paint_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                pygame.image.save(canvas, filename)
                print(f"Saved: {filename}")

            if typing:
                if event.key == pygame.K_RETURN: 
                    txt_surf = text_font.render(text_input, True, color)
                    canvas.blit(txt_surf, text_pos)
                    text_input = ""
                    typing = False
                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]
                else:
                    if event.unicode and event.key != pygame.K_ESCAPE:
                        text_input += event.unicode
                continue

            if pygame.K_F1 <= event.key <= pygame.K_F6:
                color = PALETTE[event.key - pygame.K_F1]
            if event.key == pygame.K_1: current_size = brush_sizes[1]
            if event.key == pygame.K_2: current_size = brush_sizes[2]
            if event.key == pygame.K_3: current_size = brush_sizes[3]
            if event.key == pygame.K_n: canvas.fill((255, 255, 255))

            modes = {pygame.K_p:'pencil', pygame.K_l:'line', pygame.K_r:'rect', 
                     pygame.K_s:'square', pygame.K_c:'circle', pygame.K_t:'text',
                     pygame.K_e:'equi_tri', pygame.K_h:'rhombus', pygame.K_f:'flood'}
            if event.key in modes: mode = modes[event.key]

        if event.type == pygame.MOUSEBUTTONDOWN and c_pos[1] >= 0:
            if mode == 'text':
                typing = True
                text_pos = c_pos
                text_input = ""
            elif mode == 'flood':
                tools.flood_fill(canvas, *c_pos, color)
            else:
                drawing = True
                start_pos = c_pos
                last_pos = c_pos

        if event.type == pygame.MOUSEBUTTONUP and drawing:
            if mode == 'line': pygame.draw.line(canvas, color, start_pos, c_pos, current_size)
            elif mode == 'rect': tools.draw_rect(canvas, color, start_pos, c_pos, current_size)
            elif mode == 'square': tools.draw_square(canvas, color, start_pos, c_pos, current_size)
            elif mode == 'circle': tools.draw_circle(canvas, color, start_pos, c_pos, current_size)
            elif mode == 'equi_tri': tools.draw_equilateral_triangle(canvas, color, start_pos, c_pos, current_size)
            elif mode == 'rhombus': tools.draw_rhombus(canvas, color, start_pos, c_pos, current_size)
            drawing = False
            last_pos = None

        if event.type == pygame.MOUSEMOTION and drawing and mode == 'pencil':
            pygame.draw.line(canvas, color, last_pos, c_pos, current_size)
            pygame.draw.circle(canvas, color, c_pos, current_size // 2)
            last_pos = c_pos

    pygame.display.flip()

pygame.quit()
