import pygame
import os

pygame.init()

# Test load grave.png
if os.path.exists('grave.png'):
    print("grave.png exists")
    try:
        img = pygame.image.load('grave.png')
        print("grave.png loaded successfully, size:", img.get_size())
    except Exception as e:
        print("Error loading grave.png:", e)
else:
    print("grave.png not found")
