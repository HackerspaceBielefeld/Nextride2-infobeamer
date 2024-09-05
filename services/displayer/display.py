import pygame
import time

def init_pygame():
    """
    Initialize pygame and set up the display in fullscreen mode.
    """
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    return screen, clock


# Function to display an image using pygame and handle exit on ESC key
def display_image(screen, clock, image_surface, duration):
    if image_surface:
        screen_width, screen_height = screen.get_size()
        image_width, image_height = image_surface.get_size()

        # Calculate aspect ratios
        screen_aspect_ratio = screen_width / screen_height
        image_aspect_ratio = image_width / image_height

        if image_aspect_ratio > screen_aspect_ratio:
            # Image is wider than screen
            new_width = screen_width
            new_height = int(screen_width / image_aspect_ratio)
        else:
            # Image is taller than screen or same aspect ratio
            new_height = screen_height
            new_width = int(screen_height * image_aspect_ratio)

        # Scale the image
        image_surface = pygame.transform.scale(image_surface, (new_width, new_height))

        # Fill screen with black background
        screen.fill((0, 0, 0))

        # Calculate position to center the image
        x_offset = (screen_width - new_width) // 2
        y_offset = (screen_height - new_height) // 2

        # Blit the image at the centered position
        screen.blit(image_surface, (x_offset, y_offset))

        # Update the display
        pygame.display.flip()

        start_time = time.time()

        # Event loop to check for ESC key to exit
        running = True
        while running:
            clock.tick(20)  # Cap the frame rate at 20 FPS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        pygame.quit()
                        exit()

            # Stop displaying after the duration
            if time.time() - start_time >= duration:
                break