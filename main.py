import pygame

from pond import Pond


VIRTUAL_WIDTH = 64
VIRTUAL_HEIGHT = 32

PIXEL_SCALE = 12

WINDOW_WIDTH = (
    VIRTUAL_WIDTH
    * PIXEL_SCALE
)

WINDOW_HEIGHT = (
    VIRTUAL_HEIGHT
    * PIXEL_SCALE
)

FPS = 60


def screen_to_virtual(
    screen_position
):
    x = (
        screen_position[0]
        / PIXEL_SCALE
    )

    y = (
        screen_position[1]
        / PIXEL_SCALE
    )

    return pygame.Vector2(
        x,
        y
    )


def main():

    pygame.init()

    window = pygame.display.set_mode(
        (
            WINDOW_WIDTH,
            WINDOW_HEIGHT
        )
    )

    pygame.display.set_caption(
        "Fish Pond"
    )

    clock = pygame.time.Clock()

    virtual_surface = pygame.Surface(
        (
            VIRTUAL_WIDTH,
            VIRTUAL_HEIGHT
        )
    )

    pond = Pond(
        width=VIRTUAL_WIDTH,
        height=VIRTUAL_HEIGHT
    )

    running = True

    while running:

        dt = (
            clock.tick(FPS)
            / 1000.0
        )

        mouse_position = (
            pygame.mouse.get_pos()
        )

        virtual_mouse = (
            screen_to_virtual(
                mouse_position
            )
        )

        for event in pygame.event.get():

            if (
                event.type
                == pygame.QUIT
            ):
                running = False

            elif (
                event.type
                == pygame.KEYDOWN
            ):

                if (
                    event.key
                    == pygame.K_ESCAPE
                ):
                    running = False

                elif (
                    event.key
                    == pygame.K_r
                ):
                    pond.reset()

            elif (
                event.type
                == pygame.MOUSEBUTTONDOWN
            ):

                #
                # Left click currently simulates
                # a sudden sound disturbance.
                #
                # Later this exact call can come
                # from the microphone system.
                #

                if (
                    event.button
                    == 1
                ):

                    disturbance_position = (
                        screen_to_virtual(
                            event.pos
                        )
                    )

                    pond.trigger_disturbance(
                        position=disturbance_position,
                        strength=1.0
                    )

        #
        # Mouse hover still represents
        # nearby presence.
        #

        pond.update(
            dt=dt,
            visitor_position=virtual_mouse
        )

        pond.draw(
            virtual_surface
        )

        #
        # Nearest-neighbor enlargement.
        #
        # Important because this preview
        # represents a 64 x 32 LED matrix.
        #

        scaled_surface = (
            pygame.transform.scale(
                virtual_surface,
                (
                    WINDOW_WIDTH,
                    WINDOW_HEIGHT
                )
            )
        )

        window.blit(
            scaled_surface,
            (
                0,
                0
            )
        )

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()