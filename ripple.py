import math
import random

import pygame


class Ripple:
    def __init__(
        self,
        position,
        strength=1.0
    ):
        self.position = pygame.Vector2(
            position
        )

        self.strength = max(
            0.0,
            min(
                1.0,
                strength
            )
        )

        self.age = 0.0

        self.lifetime = (
            0.55
            + self.strength * 0.25
        )

        self.start_radius = 1.0

        self.max_radius = (
            8.0
            + self.strength * 8.0
        )

        self.sample_count = int(
            20
            + self.strength * 16
        )

        self.angle_offsets = []

        self.visibility = []

        for _ in range(
            self.sample_count
        ):
            self.angle_offsets.append(
                random.uniform(
                    -0.08,
                    0.08
                )
            )

            self.visibility.append(
                random.random()
                > 0.30
            )

        #
        # Keep track of which fish this
        # ripple has already touched.
        #

        self.triggered_fish = set()

    @property
    def dead(
        self
    ):
        return (
            self.age
            >= self.lifetime
        )

    def get_progress(
        self
    ):
        return max(
            0.0,
            min(
                1.0,
                self.age
                / self.lifetime
            )
        )

    def get_radius(
        self
    ):
        progress = (
            self.get_progress()
        )

        eased_progress = (
            1.0
            - (
                1.0
                - progress
            ) ** 2
        )

        return (
            self.start_radius
            + (
                self.max_radius
                - self.start_radius
            )
            * eased_progress
        )

    def get_previous_radius(
        self,
        dt
    ):
        previous_age = max(
            0.0,
            self.age - dt
        )

        previous_progress = max(
            0.0,
            min(
                1.0,
                previous_age
                / self.lifetime
            )
        )

        eased_progress = (
            1.0
            - (
                1.0
                - previous_progress
            ) ** 2
        )

        return (
            self.start_radius
            + (
                self.max_radius
                - self.start_radius
            )
            * eased_progress
        )

    def update(
        self,
        dt
    ):
        self.age += dt

    # --------------------------------------------------
    # Fish interaction
    # --------------------------------------------------

    def check_fish_collision(
        self,
        fish,
        dt
    ):
        if self.dead:
            return False

        fish_id = id(
            fish
        )

        if (
            fish_id
            in self.triggered_fish
        ):
            return False

        offset = (
            fish.position
            - self.position
        )

        distance = (
            offset.length()
        )

        current_radius = (
            self.get_radius()
        )

        previous_radius = (
            self.get_previous_radius(
                dt
            )
        )

        #
        # Give the wavefront a little thickness.
        #
        # This is important on a 64x32 grid,
        # otherwise the ring may step over
        # a fish between frames.
        #

        wave_thickness = (
            1.5
            + self.strength
            * 0.75
        )

        inner_edge = (
            previous_radius
            - wave_thickness
        )

        outer_edge = (
            current_radius
            + wave_thickness
        )

        if (
            inner_edge
            <= distance
            <= outer_edge
        ):
            self.triggered_fish.add(
                fish_id
            )

            return True

        return False

    def get_escape_direction(
        self,
        fish
    ):
        direction = (
            fish.position
            - self.position
        )

        if (
            direction.length_squared()
            == 0
        ):
            direction = pygame.Vector2(
                random.uniform(
                    -1.0,
                    1.0
                ),
                random.uniform(
                    -1.0,
                    1.0
                )
            )

        return (
            direction.normalize()
        )

    # --------------------------------------------------
    # Drawing
    # --------------------------------------------------

    def draw(
        self,
        surface
    ):
        if self.dead:
            return

        progress = (
            self.get_progress()
        )

        radius = (
            self.get_radius()
        )

        fade = (
            1.0
            - progress
        )

        fade = (
            fade
            * fade
        )

        brightness = int(
            65
            * fade
            * (
                0.55
                + 0.45
                * self.strength
            )
        )

        brightness = max(
            0,
            min(
                80,
                brightness
            )
        )

        ripple_color = (
            brightness,
            brightness,
            int(
                brightness * 1.10
            )
        )

        width = (
            surface.get_width()
        )

        height = (
            surface.get_height()
        )

        for i in range(
            self.sample_count
        ):
            if (
                not self.visibility[i]
            ):
                continue

            angle = (
                (
                    i
                    / self.sample_count
                )
                * math.tau
                + self.angle_offsets[i]
            )

            local_radius = (
                radius
                + math.sin(
                    angle * 3.0
                    + self.age * 5.0
                )
                * 0.25
            )

            x = round(
                self.position.x
                + math.cos(angle)
                * local_radius
            )

            y = round(
                self.position.y
                + math.sin(angle)
                * local_radius
            )

            if (
                0 <= x < width
                and
                0 <= y < height
            ):
                surface.set_at(
                    (
                        x,
                        y
                    ),
                    ripple_color
                )