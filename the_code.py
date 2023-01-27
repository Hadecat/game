import os
import sys

import pygame


def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Arrow(pygame.sprite.Sprite):
    image = load_image("arrow.png")
    image.set_colorkey((0, 0, 0))

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Arrow.image
        self.rect = self.image.get_rect()
        self.rect.x = 75
        self.rect.y = 145

    def update(self, angle):
        self.image = pygame.transform.rotate(Arrow.image, angle)
        self.rect = self.image.get_rect()
        self.rect.x = (width - self.rect[2]) // 2
        self.rect.y = (height - self.rect[3]) // 2


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Перетаскивание')
    size = width, height = 300, 300
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    Arrow(all_sprites)
    angle = 0

    running, rotating = True, False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                rotating = True
            if event.type == pygame.MOUSEBUTTONUP:
                rotating = False
        if rotating:
            angle += 1
            all_sprites.update(angle)
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(60)
