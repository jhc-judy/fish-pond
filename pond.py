import math
import random

import pygame

from fish import Fish
from ripple import Ripple


class Pond:
    def __init__(
        self,
        width,
        height
    ):
        self.width = width
        self.height = height

        self.background_color = (
            1,
            2,
            4
        )

        self.fish = []

        self.ripples = []

        self.reset()

    def reset(
        self
    ):
        self.fish.clear()

        self.ripples.clear()

        fish_count = 3

        for _ in range(
            fish_count
        ):
            x = random.uniform(
                self.width * 0.25,
                self.width * 0.75
            )

            y = random.uniform(
                self.height * 0.25,
                self.height * 0.75
            )

            direction = random.uniform(
                0,
                math.tau
            )

            speed = random.uniform(
                2.6,
                3.5
            )

            length = random.choice(
                [
                    7,
                    8,
                    9
                ]
            )

            self.fish.append(
                Fish(
                    x=x,
                    y=y,
                    direction=direction,
                    speed=speed,
                    length=length
                )
            )

    # --------------------------------------------------
    # Disturbance
    # --------------------------------------------------

    def trigger_disturbance(
        self,
        position,
        strength=1.0
    ):
        strength = max(
            0.0,
            min(
                1.0,
                strength
            )
        )

        position = pygame.Vector2(
            position
        )

        self.ripples.append(
            Ripple(
                position=position,
                strength=strength
            )
        )

        #
        # Optional very-near-source response.
        #
        # Fish practically on top of the disturbance
        # can react immediately instead of waiting
        # for the first visible ring expansion.
        #

        immediate_radius = (
            2.5
            + strength * 1.5
        )

        for fish in self.fish:
            away = (
                fish.position
                - position
            )

            distance = (
                away.length()
            )

            if (
                0 < distance
                < immediate_radius
            ):
                fish.react_to_disturbance(
                    direction=away,
                    strength=strength
                )

    # --------------------------------------------------
    # Update
    # --------------------------------------------------

    def update(
        self,
        dt,
        visitor_position=None
    ):
        #
        # Fish
        #

        for fish in self.fish:
            neighbors = [
                other
                for other in self.fish
                if other is not fish
            ]

            fish.update(
                dt=dt,
                pond_width=self.width,
                pond_height=self.height,
                visitor_position=visitor_position,
                neighbors=neighbors
            )

        #
        # Ripple expansion + fish collision
        #

        for ripple in self.ripples:
            ripple.update(
                dt
            )

            for fish in self.fish:
                if ripple.check_fish_collision(
                    fish=fish,
                    dt=dt
                ):
                    escape_direction = (
                        ripple.get_escape_direction(
                            fish
                        )
                    )

                    #
                    # Keep this strong so the visual
                    # cause/effect is very obvious:
                    #
                    # ring touches fish
                    #        ↓
                    # fish bolts outward
                    #

                    fish.react_to_disturbance(
                        direction=escape_direction,
                        strength=max(
                            0.70,
                            ripple.strength
                        )
                    )

        self.ripples = [
            ripple
            for ripple in self.ripples
            if not ripple.dead
        ]

        #
        # Local panic contagion
        #

        startled_fish = [
            fish
            for fish in self.fish
            if fish.startled
        ]

        for startled in startled_fish:
            for other in self.fish:
                if (
                    other is startled
                    or other.startled
                ):
                    continue

                offset = (
                    other.position
                    - startled.position
                )

                distance = (
                    offset.length()
                )

                if (
                    0 < distance < 9
                    and
                    random.random()
                    < 0.02
                ):
                    other.trigger_startle(
                        offset
                    )

    # --------------------------------------------------
    # Draw
    # --------------------------------------------------

    def draw(
        self,
        surface
    ):
        surface.fill(
            self.background_color
        )

        for ripple in self.ripples:
            ripple.draw(
                surface
            )

        for fish in self.fish:
            fish.draw(
                surface
            )