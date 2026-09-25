import math
import random

import pygame


class Fish:
    def __init__(
        self,
        x,
        y,
        direction,
        speed,
        length=8
    ):
        self.position = pygame.Vector2(
            x,
            y
        )

        self.heading = direction

        self.base_speed = speed

        self.activity = random.uniform(
            0.88,
            1.12
        )

        self.social_strength = random.uniform(
            0.75,
            1.15
        )

        self.current_speed = (
            self.base_speed
            * random.uniform(
                0.55,
                0.80
            )
        )

        self.length = length

        #
        # Turning
        #

        self.normal_turn_rate = random.uniform(
            1.25,
            1.7
        )

        self.dart_turn_rate = random.uniform(
            2.6,
            3.4
        )

        #
        # Body animation
        #

        self.swim_phase = random.uniform(
            0,
            math.tau
        )

        self.swim_frequency = random.uniform(
            3.2,
            4.2
        )

        #
        # Micro steering
        #

        self.wander_angle = random.uniform(
            -0.10,
            0.10
        )

        self.wander_target = random.uniform(
            -0.10,
            0.10
        )

        self.wander_timer = random.uniform(
            0.15,
            0.45
        )

        #
        # Natural darts
        #

        self.darting = False

        self.dart_timer = 0.0

        self.next_dart_timer = random.uniform(
            0.35,
            1.25
        )

        self.dart_heading = direction

        self.dart_speed_multiplier = 1.0

        #
        # Strong startle
        #

        self.startled = False

        self.startle_timer = 0.0

        self.startle_heading = direction

        #
        # Visitor interaction
        #

        self.awareness_radius = random.uniform(
            11.0,
            14.0
        )

        self.panic_radius = random.uniform(
            5.0,
            6.5
        )

        self.visitor_cooldown = 0.0

        #
        # Escape memory
        #

        self.escape_memory = 0.0

        self.escape_direction = pygame.Vector2(
            math.cos(direction),
            math.sin(direction)
        )

        #
        # After a disturbance the fish remains
        # nervous for a little while.
        #

        self.nervous_timer = 0.0

        self.nervous_strength = 0.0

    # --------------------------------------------------
    # Heading helpers
    # --------------------------------------------------

    def angle_difference(
        self,
        target,
        current
    ):

        return (
            target
            - current
            + math.pi
        ) % math.tau - math.pi

    def turn_toward(
        self,
        target,
        max_turn
    ):

        difference = (
            self.angle_difference(
                target,
                self.heading
            )
        )

        difference = max(
            -max_turn,
            min(
                max_turn,
                difference
            )
        )

        self.heading += (
            difference
        )

        self.heading %= math.tau

    def get_forward(
        self
    ):

        return pygame.Vector2(
            math.cos(
                self.heading
            ),
            math.sin(
                self.heading
            )
        )

    # --------------------------------------------------
    # Natural dart
    # --------------------------------------------------

    def trigger_dart(
        self,
        direction=None,
        speed_multiplier=None,
        duration=None
    ):

        if direction is None:

            self.dart_heading = (
                self.heading
                + random.uniform(
                    -0.38,
                    0.38
                )
            )

        else:

            if (
                direction.length_squared()
                == 0
            ):
                return

            direction = (
                direction.normalize()
            )

            self.dart_heading = (
                math.atan2(
                    direction.y,
                    direction.x
                )
            )

        self.darting = True

        if duration is None:

            duration = (
                random.uniform(
                    0.055,
                    0.11
                )
            )

        self.dart_timer = duration

        if speed_multiplier is None:

            speed_multiplier = (
                random.uniform(
                    6.6,
                    9.0
                )
            )

        self.dart_speed_multiplier = (
            speed_multiplier
        )

    # --------------------------------------------------
    # Strong startle
    # --------------------------------------------------

    def trigger_startle(
        self,
        direction
    ):

        if (
            direction.length_squared()
            == 0
        ):
            return

        direction = (
            direction.normalize()
        )

        self.startled = True

        self.darting = False

        self.startle_timer = (
            random.uniform(
                0.075,
                0.14
            )
        )

        self.startle_heading = (
            math.atan2(
                direction.y,
                direction.x
            )
        )

        self.escape_direction = (
            direction.copy()
        )

        self.escape_memory = (
            random.uniform(
                0.35,
                0.55
            )
        )

        self.visitor_cooldown = (
            random.uniform(
                0.30,
                0.50
            )
        )

    # --------------------------------------------------
    # Sound / ripple disturbance response
    # --------------------------------------------------

    def react_to_disturbance(
        self,
        direction,
        strength
    ):

        if (
            direction.length_squared()
            == 0
        ):
            return

        strength = max(
            0.0,
            min(
                1.0,
                strength
            )
        )

        direction = (
            direction.normalize()
        )

        #
        # Slightly imperfect escape direction
        # keeps the fish organic.
        #

        direction = (
            direction.rotate_rad(
                random.uniform(
                    -0.10,
                    0.10
                )
            )
        )

        self.escape_direction = (
            direction.copy()
        )

        #
        # Remember the disturbance.
        #

        self.escape_memory = (
            0.35
            + strength * 0.35
        )

        self.nervous_timer = (
            1.0
            + strength
            * random.uniform(
                1.0,
                2.0
            )
        )

        self.nervous_strength = (
            strength
        )

        #
        # Strong sounds create a full panic bolt.
        #

        if strength > 0.62:

            self.trigger_startle(
                direction
            )

        #
        # Moderate sounds create a fast dart.
        #

        else:

            speed_multiplier = (
                5.5
                + strength * 4.0
            )

            duration = (
                0.06
                + strength * 0.05
            )

            self.trigger_dart(
                direction=direction,
                speed_multiplier=speed_multiplier,
                duration=duration
            )

    # --------------------------------------------------
    # Update
    # --------------------------------------------------

    def update(
        self,
        dt,
        pond_width,
        pond_height,
        visitor_position,
        neighbors
    ):

        if dt <= 0:
            return

        #
        # Timers
        #

        self.visitor_cooldown = max(
            0.0,
            self.visitor_cooldown - dt
        )

        self.escape_memory = max(
            0.0,
            self.escape_memory - dt
        )

        self.nervous_timer = max(
            0.0,
            self.nervous_timer - dt
        )

        if (
            self.nervous_timer <= 0
        ):

            self.nervous_strength += (
                0.0
                - self.nervous_strength
            ) * min(
                1.0,
                dt * 3.0
            )

        #
        # Body animation
        #

        movement_ratio = max(
            0.35,
            self.current_speed
            / self.base_speed
        )

        animation_multiplier = 1.0

        if self.darting:
            animation_multiplier = 1.8

        if self.startled:
            animation_multiplier = 2.1

        self.swim_phase += (
            dt
            * self.swim_frequency
            * movement_ratio
            * animation_multiplier
        )

        # --------------------------------------------------
        # Mouse visitor
        # --------------------------------------------------

        visitor_distance = None

        visitor_away = None

        if (
            visitor_position
            is not None
        ):

            visitor_away = (
                self.position
                - visitor_position
            )

            visitor_distance = (
                visitor_away.length()
            )

            if (
                visitor_distance > 0
                and
                self.visitor_cooldown <= 0
            ):

                if (
                    visitor_distance
                    < self.panic_radius
                ):

                    escape = (
                        visitor_away.normalize()
                    )

                    escape = (
                        escape.rotate_rad(
                            random.uniform(
                                -0.08,
                                0.08
                            )
                        )
                    )

                    self.trigger_startle(
                        escape
                    )

                elif (
                    visitor_distance
                    < self.awareness_radius
                    and
                    not self.startled
                    and
                    not self.darting
                ):

                    escape = (
                        visitor_away.normalize()
                    )

                    escape = (
                        escape.rotate_rad(
                            random.uniform(
                                -0.12,
                                0.12
                            )
                        )
                    )

                    self.escape_direction = (
                        escape.copy()
                    )

                    self.escape_memory = (
                        random.uniform(
                            0.25,
                            0.45
                        )
                    )

                    self.trigger_dart(
                        direction=escape,
                        speed_multiplier=random.uniform(
                            7.8,
                            9.6
                        ),
                        duration=random.uniform(
                            0.06,
                            0.12
                        )
                    )

                    self.visitor_cooldown = (
                        random.uniform(
                            0.25,
                            0.40
                        )
                    )

        # --------------------------------------------------
        # Strong startle
        # --------------------------------------------------

        if self.startled:

            self.startle_timer -= dt

            self.turn_toward(
                self.startle_heading,
                self.dart_turn_rate * dt
            )

            target_speed = (
                self.base_speed
                * 11.4
            )

            self.current_speed += (
                target_speed
                - self.current_speed
            ) * min(
                1.0,
                dt * 38.0
            )

            self.move(
                dt,
                pond_width,
                pond_height
            )

            if (
                self.startle_timer
                <= 0
            ):

                self.startled = False

                self.next_dart_timer = (
                    random.uniform(
                        0.5,
                        1.4
                    )
                )

            return

        # --------------------------------------------------
        # Dart
        # --------------------------------------------------

        if self.darting:

            self.dart_timer -= dt

            self.turn_toward(
                self.dart_heading,
                self.dart_turn_rate * dt
            )

            target_speed = (
                self.base_speed
                * self.dart_speed_multiplier
            )

            self.current_speed += (
                target_speed
                - self.current_speed
            ) * min(
                1.0,
                dt * 34.0
            )

            self.move(
                dt,
                pond_width,
                pond_height
            )

            if (
                self.dart_timer
                <= 0
            ):

                self.darting = False

                self.next_dart_timer = (
                    random.uniform(
                        0.3,
                        1.15
                    )
                )

            return

        # --------------------------------------------------
        # Natural dart timer
        # --------------------------------------------------

        self.next_dart_timer -= dt

        #
        # Nervous fish dart a little more often.
        #

        dart_threshold = 0.0

        if (
            self.nervous_timer > 0
        ):

            self.next_dart_timer -= (
                dt
                * self.nervous_strength
                * 0.65
            )

        if (
            self.next_dart_timer
            <= dart_threshold
            and
            self.escape_memory <= 0
        ):

            self.trigger_dart()

            return

        # --------------------------------------------------
        # Micro steering
        # --------------------------------------------------

        self.wander_timer -= dt

        if (
            self.wander_timer
            <= 0
        ):

            wander_range = 0.12

            if (
                self.nervous_timer > 0
            ):

                wander_range += (
                    0.08
                    * self.nervous_strength
                )

            self.wander_target = (
                random.uniform(
                    -wander_range,
                    wander_range
                )
            )

            self.wander_timer = (
                random.uniform(
                    0.15,
                    0.45
                )
            )

        self.wander_angle += (
            self.wander_target
            - self.wander_angle
        ) * min(
            1.0,
            dt * 4.0
        )

        # --------------------------------------------------
        # Social behavior
        # --------------------------------------------------

        separation = pygame.Vector2()

        cohesion = pygame.Vector2()

        alignment = pygame.Vector2()

        nearby_count = 0

        for other in neighbors:

            offset = (
                other.position
                - self.position
            )

            distance = (
                offset.length()
            )

            if distance <= 0:
                continue

            if (
                distance < 4
            ):

                separation -= (
                    offset.normalize()
                    * (
                        1.0
                        - distance / 4.0
                    )
                )

            if (
                distance < 12
            ):

                nearby_count += 1

                cohesion += (
                    other.position
                )

                alignment += (
                    other.get_forward()
                )

        steering = pygame.Vector2()

        if (
            separation.length_squared()
            > 0
        ):

            steering += (
                separation.normalize()
                * 2.3
            )

        if (
            nearby_count > 0
        ):

            average_position = (
                cohesion
                / nearby_count
            )

            toward_group = (
                average_position
                - self.position
            )

            if (
                toward_group.length_squared()
                > 0
            ):

                steering += (
                    toward_group.normalize()
                    * 0.14
                    * self.social_strength
                )

            if (
                alignment.length_squared()
                > 0
            ):

                steering += (
                    alignment.normalize()
                    * 0.17
                    * self.social_strength
                )

        # --------------------------------------------------
        # Escape memory
        # --------------------------------------------------

        if (
            self.escape_memory > 0
            and
            self.escape_direction.length_squared()
            > 0
        ):

            steering += (
                self.escape_direction.normalize()
                * 1.7
                * (
                    self.escape_memory
                    / 0.70
                )
            )

        # --------------------------------------------------
        # Mouse repulsion
        # --------------------------------------------------

        if (
            visitor_away is not None
            and
            visitor_distance is not None
            and
            visitor_distance > 0
            and
            visitor_distance
            < self.awareness_radius
        ):

            strength = (
                1.0
                - visitor_distance
                / self.awareness_radius
            )

            steering += (
                visitor_away.normalize()
                * strength
                * 1.8
            )

        # --------------------------------------------------
        # Elliptical boundary
        # --------------------------------------------------

        center = pygame.Vector2(
            pond_width / 2,
            pond_height / 2
        )

        offset = (
            self.position
            - center
        )

        radius_x = (
            pond_width * 0.46
        )

        radius_y = (
            pond_height * 0.43
        )

        normalized_distance = math.sqrt(
            (
                offset.x
                / radius_x
            ) ** 2
            +
            (
                offset.y
                / radius_y
            ) ** 2
        )

        boundary_start = 0.78

        if (
            normalized_distance
            > boundary_start
        ):

            boundary_strength = (
                normalized_distance
                - boundary_start
            ) / (
                1.0
                - boundary_start
            )

            inward = pygame.Vector2(
                -offset.x
                / (
                    radius_x
                    * radius_x
                ),
                -offset.y
                / (
                    radius_y
                    * radius_y
                )
            )

            if (
                inward.length_squared()
                > 0
            ):

                inward.normalize_ip()

                steering += (
                    inward
                    * boundary_strength
                    * 1.9
                )

        # --------------------------------------------------
        # Normal steering
        # --------------------------------------------------

        forward = (
            self.get_forward()
        )

        wandering_forward = (
            forward.rotate_rad(
                self.wander_angle
            )
        )

        desired = (
            wandering_forward
            + steering * 0.30
        )

        if (
            desired.length_squared()
            > 0
        ):

            desired.normalize_ip()

            target_heading = (
                math.atan2(
                    desired.y,
                    desired.x
                )
            )

            self.turn_toward(
                target_heading,
                self.normal_turn_rate * dt
            )

        # --------------------------------------------------
        # Normal speed
        # --------------------------------------------------

        target_speed = (
            self.base_speed
            * 0.68
            * self.activity
        )

        if (
            self.escape_memory > 0
        ):

            target_speed *= 1.35

        if (
            self.nervous_timer > 0
        ):

            target_speed *= (
                1.0
                + 0.22
                * self.nervous_strength
            )

        self.current_speed += (
            target_speed
            - self.current_speed
        ) * min(
            1.0,
            dt * 8.0
        )

        self.move(
            dt,
            pond_width,
            pond_height
        )

    # --------------------------------------------------
    # Movement
    # --------------------------------------------------

    def move(
        self,
        dt,
        pond_width,
        pond_height
    ):

        self.position += (
            self.get_forward()
            * self.current_speed
            * dt
        )

        center = pygame.Vector2(
            pond_width / 2,
            pond_height / 2
        )

        offset = (
            self.position
            - center
        )

        radius_x = (
            pond_width * 0.47
        )

        radius_y = (
            pond_height * 0.44
        )

        normalized_distance = math.sqrt(
            (
                offset.x
                / radius_x
            ) ** 2
            +
            (
                offset.y
                / radius_y
            ) ** 2
        )

        if (
            normalized_distance
            > 1.0
        ):

            #
            # Correct projection onto the
            # elliptical boundary.
            #

            self.position = pygame.Vector2(
                center.x
                + (
                    offset.x
                    / normalized_distance
                ),
                center.y
                + (
                    offset.y
                    / normalized_distance
                )
            )

            inward = pygame.Vector2(
                -offset.x
                / (
                    radius_x
                    * radius_x
                ),
                -offset.y
                / (
                    radius_y
                    * radius_y
                )
            )

            if (
                inward.length_squared()
                > 0
            ):

                inward.normalize_ip()

                target_heading = (
                    math.atan2(
                        inward.y,
                        inward.x
                    )
                )

                self.turn_toward(
                    target_heading,
                    0.45
                )

    # --------------------------------------------------
    # Animated body
    # --------------------------------------------------

    def get_body_points(
        self
    ):

        forward = (
            self.get_forward()
        )

        perpendicular = pygame.Vector2(
            -forward.y,
            forward.x
        )

        point_count = 14

        points = []

        for i in range(
            point_count
        ):

            t = (
                i
                / (
                    point_count - 1
                )
            )

            distance_back = (
                t
                * self.length
            )

            curve_strength = max(
                0.0,
                (
                    t - 0.18
                ) / 0.82
            )

            curve_strength = (
                curve_strength
                ** 1.55
            )

            bend = (
                math.sin(
                    self.swim_phase
                )
            )

            trailing_bend = (
                math.sin(
                    self.swim_phase
                    - 0.5
                )
            )

            lateral = (
                bend
                * curve_strength
                * 0.55
            )

            lateral += (
                trailing_bend
                * (
                    curve_strength
                    ** 2.2
                )
                * 0.15
            )

            point = (
                self.position
                - forward
                * distance_back
                + perpendicular
                * lateral
            )

            points.append(
                point
            )

        return points

    # --------------------------------------------------
    # Pixel drawing
    # --------------------------------------------------

    def draw_disc(
        self,
        surface,
        center,
        radius,
        color
    ):

        cx = round(
            center.x
        )

        cy = round(
            center.y
        )

        radius_int = (
            math.ceil(
                radius
            )
        )

        for y in range(
            cy - radius_int,
            cy + radius_int + 1
        ):

            for x in range(
                cx - radius_int,
                cx + radius_int + 1
            ):

                dx = (
                    x - cx
                )

                dy = (
                    y - cy
                )

                if (
                    dx * dx
                    + dy * dy
                    <= radius * radius
                ):

                    if (
                        0 <= x
                        < surface.get_width()
                        and
                        0 <= y
                        < surface.get_height()
                    ):

                        surface.set_at(
                            (
                                x,
                                y
                            ),
                            color
                        )

    # --------------------------------------------------
    # Draw fish
    # --------------------------------------------------

    def draw(
        self,
        surface
    ):

        points = (
            self.get_body_points()
        )

        fish_red = (
            245,
            45,
            25
        )

        widths = [
            0.45,
            0.65,
            0.90,
            1.10,
            1.20,
            1.15,
            1.05,
            0.90,
            0.75,
            0.60,
            0.48,
            0.36,
            0.28,
            0.16,
        ]

        for point, width in zip(
            points,
            widths
        ):

            self.draw_disc(
                surface,
                point,
                width,
                fish_red
            )

        forward = (
            self.get_forward()
        )

        perpendicular = pygame.Vector2(
            -forward.y,
            forward.x
        )

        fin_anchor = (
            points[4]
        )

        fin_left = (
            fin_anchor
            + perpendicular * 1.3
            - forward * 0.2
        )

        fin_right = (
            fin_anchor
            - perpendicular * 1.3
            - forward * 0.2
        )

        self.draw_disc(
            surface,
            fin_left,
            0.4,
            fish_red
        )

        self.draw_disc(
            surface,
            fin_right,
            0.4,
            fish_red
        )