import os
import sys
import random
import pygame


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, color_key, columns, rows, x, y):
        super().__init__(all_sprites)
        sheet = load_image(sheet, color_key)
        self.flipped = False
        self.frames = []
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.frames.clear()
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

    def flip(self):
        self.flipped = not self.flipped
        for i in range(len(self.frames)):
            self.frames[i] = pygame.transform.flip(self.frames[i], True, False)

    def is_flipped(self):
        return self.flipped

    def change_sprite(self, sheet, color_key, columns, rows):
        sheet = load_image(sheet, color_key)
        self.cut_sheet(sheet, columns, rows)
        if self.flipped:
            for i in range(len(self.frames)):
                self.frames[i] = pygame.transform.flip(self.frames[i], True, False)
        self.image = self.frames[self.cur_frame]


class Skull(AnimatedSprite):
    def __init__(self, sheet, color_key, columns, rows, x, y):
        super().__init__(sheet, color_key, columns, rows, x, y)
        self.x, self.y = (x - 10) // 80, y // 80

    def move(self, direction):
        move_success = True
        if mov[direction][0] == "x":
            if direction == 97 and not self.is_flipped():
                self.flip()
            elif direction == 100 and self.is_flipped():
                self.flip()
            self.rect.x += mov[direction][1]
            self.x += mov[direction][1] // 80
            if pygame.sprite.spritecollide(self, walls, False):
                self.rect.x -= mov[direction][1]
                move_success = False
        else:
            self.rect.y += mov[direction][1]
            self.y += mov[direction][1] // 80
            if pygame.sprite.spritecollide(self, walls, False):
                self.rect.y -= mov[direction][1]
                move_success = False
        return move_success

    def coords(self):
        return self.x, self.y


class Box(AnimatedSprite):
    def __init__(self, sheet, color_key, columns, rows, x, y):
        super().__init__(sheet, color_key, columns, rows, x, y)
        self.add(walls)


class Enemy(AnimatedSprite):
    def __init__(self, sheet, color_key, columns, rows, x, y):
        super().__init__(sheet, color_key, columns, rows, x, y)
        self.x, self.y = (x - 10) // 80, y // 80
        self.add(enemies)

    def where_to_move(self, mc, walls_pos):
        possible_moves = list()
        if mc.rect.x < self.rect.x:
            possible_moves.append(97)
        elif mc.rect.x > self.rect.x:
            possible_moves.append(100)
        if mc.rect.y < self.rect.y:
            possible_moves.append(119)
        elif mc.rect.y > self.rect.y:
            possible_moves.append(115)
        move_success = False
        direction = 0
        while not move_success:
            direction = possible_moves[random.randint(0, len(possible_moves)) - 1]
            if mov[direction][0] == "x":
                if (self.coords()[0] + mov[direction][1], self.coords()[1]) in walls_pos:
                    continue
                if direction == 97 and not self.is_flipped():
                    self.flip()
                elif direction == 100 and self.is_flipped():
                    self.flip()
                self.x += mov[direction][1] // 80
            else:
                if (self.coords()[0], self.coords()[1] + mov[direction][1]) in walls_pos:
                    continue
                self.y += mov[direction][1] // 80
            move_success = True
        return mov[direction]

    def coords(self):
        return self.x, self.y


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    coords, current_coords = [(385, 355), (465, 455)], 0
    cursor = load_image("cursor.png")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYUP:
                if event.key in mov:
                    current_coords = (current_coords + 1) % 2
                elif not current_coords:
                    if event.key == pygame.K_RETURN:
                        return
                elif current_coords:
                    if event.key == pygame.K_RETURN:
                        terminate()
        screen.fill((0, 0, 0))
        screen.blit(load_image('start_screen.png'), (0, 0))
        screen.blit(cursor, (coords[current_coords]))
        pygame.display.flip()
        clock.tick(60)


def create_level(level):
    player = None
    walls_pos, enemies_pos = list(), list()
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Box("box.png", -1, 1, 1, (x + 1) * 80, (y + 1) * 80)
                walls_pos.append((x + 1, y + 1))
            elif level[y][x] == '@':
                player = Skull("skull_idle_bw.png", -1, 8, 1, (x + 1) * 80 + 10, (y + 1) * 80)
            elif level[y][x] == 'X':
                Enemy("zombie_idle_bw.png", -1, 8, 1, (x + 1) * 80 + 10, (y + 1) * 80)
                enemies_pos.append((x + 1, y + 1))
    return player, walls_pos, enemies_pos


def pause():
    coords, current_coords = [(375, 285), (465, 380)], 0
    cursor = load_image("cursor.png", -1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYUP:
                if event.key in mov:
                    current_coords = (current_coords + 1) % 2
                elif not current_coords:
                    if event.key == pygame.K_RETURN:
                        return
                elif current_coords:
                    if event.key == pygame.K_RETURN:
                        terminate()
        screen.fill((255, 255, 255))
        screen.blit(load_image("bg.png"), (0, 0))
        all_sprites.draw(screen)
        screen.blit(load_image("pause_screen.png"), (0, 0))
        screen.blit(cursor, (coords[current_coords]))
        clock.tick(60)
        pygame.display.flip()


def game_over():
    coords, current_coords = [(375, 520), (470, 615)], 0
    cursor = load_image("cursor.png", -1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYUP:
                if event.key in mov:
                    current_coords = (current_coords + 1) % 2
                elif not current_coords:
                    if event.key == pygame.K_RETURN:
                        return
                elif current_coords:
                    if event.key == pygame.K_RETURN:
                        terminate()
        screen.fill((255, 255, 255))
        screen.blit(load_image("bg.png"), (0, 0))
        all_sprites.draw(screen)
        screen.blit(load_image("game_over_screen.png"), (0, 0))
        screen.blit(cursor, (coords[current_coords]))
        clock.tick(60)
        pygame.display.flip()


def win():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    terminate()
        screen.fill((255, 255, 255))
        screen.blit(load_image("win_screen.png"), (0, 0))
        clock.tick(60)
        pygame.display.flip()


def your_turn(mc, status, anim_timer, enemies_pos):
    status.change_sprite("your_turn_2.png", 0, 1, 1)
    left = 2
    while True:
        if left:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.KEYUP:
                    if event.key in mov:
                        if mc.move(event.key):
                            left -= 1
                            status.change_sprite("your_turn_1.png", 0, 1, 1)
                            print(mc.coords(), enemies_pos)
                            if pygame.sprite.spritecollide(mc, enemies, True):
                                enemies_pos.remove(mc.coords())
                            if not enemies:
                                return True
                    if event.key == pygame.K_RETURN:
                        pause()
        else:
            if not enemies:
                return True
            else:
                return False
        screen.fill((255, 255, 255))
        screen.blit(load_image("bg.png"), (0, 0))
        all_sprites.draw(screen)
        clock.tick(60)
        anim_timer = (anim_timer + 1) % 3
        if anim_timer == 0:
            all_sprites.update()
        pygame.display.flip()


def enemy_turn(mc, walls_pos, enemies_pos):
    enemies_pos.clear()
    for i in enemies:
        x = i.where_to_move(mc, walls_pos)
        if x[0] == "x":
            i.rect.x += x[1]
        else:
            i.rect.y += x[1]
        enemies_pos.append(i.coords())
        if pygame.sprite.spritecollide(mc, enemies, True):
            return True
    return False


def tag():
    status = AnimatedSprite("your_turn_2.png", 0, 1, 1, 0, 0)
    mc, walls_pos, enemies_pos = create_level(load_level('map.txt'))
    anim_timer = 0
    while True:
        if your_turn(mc, status, anim_timer, enemies_pos):
            win()
        if enemy_turn(mc, walls_pos, enemies_pos):
            mc.kill()
            status.kill()
            enemies.empty()
            return


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('BoneZ')
    size = width, height = 1280, 720
    screen = pygame.display.set_mode(size)
    screen.fill((255, 255, 255))

    mov = {119: ("y", -80), 97: ("x", -80), 115: ("y", 80), 100: ("x", 80)}

    all_sprites = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    started, lost = False, False
    while True:
        if not started and not lost:
            start_screen()
            started = True
        if started and not lost:
            tag()
            lost = True
        if started and lost:
            game_over()
            lost = False
'''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if started:
                if event.type == pygame.KEYUP:
                    if event.key in mov:
                        mc.move(event.key)
                    if event.key == pygame.K_RETURN:
                        pause()
'''