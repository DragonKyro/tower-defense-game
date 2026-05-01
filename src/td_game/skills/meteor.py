"""Global Meteor skill — now a rain of meteors dropped from the sky.

Rather than instant damage at a point (which had no timing tension),
activating Meteor now spawns several falling meteors with staggered
pre-delays that impact in a cluster around the target over ~1 second.
The explosions and AoE are resolved by the normal combat system via
each meteor's `aoe_radius` — the skill itself just seeds projectiles.
"""
from __future__ import annotations

import math
import random

from td_game.core.constants import DamageType, SCREEN_HEIGHT
from td_game.core.damage import DamagePacket
from td_game.core.events import SKILL_USED
from td_game.core.resources import load_texture
from td_game.entities.projectiles.base_projectile import FallingProjectile

from .base_skill import BaseSkill, SkillContext, TargetKind


class Meteor(BaseSkill):
    id = "meteor"
    display_name = "Meteor"
    description = (
        "Calls down a rain of meteors on the target area. "
        "Several staggered impacts — time it when enemies are clustered."
    )
    icon = "meteor_0"
    target_kind = TargetKind.AREA

    def __init__(
        self,
        cooldown: float = 25.0,
        cost: int = 0,
        damage_per_meteor: float = 90.0,
        radius: float = 100.0,
        meteor_count: int = 6,
        per_meteor_aoe: float = 48.0,
        window: float = 1.1,
    ) -> None:
        super().__init__(cooldown, cost)
        self.damage = damage_per_meteor
        self.radius = radius                  # area radius the cluster lands within
        self.meteor_count = meteor_count
        self.per_meteor_aoe = per_meteor_aoe   # splash radius of each individual meteor
        self.window = window                   # seconds across which meteors arrive

    def on_activate(self, ctx: SkillContext, target) -> None:
        x, y = target
        tex = load_texture("projectiles", "meteor_0")
        rng = random.Random()
        for i in range(self.meteor_count):
            # Distribute landing points over the target disc.
            angle = rng.uniform(0, math.tau)
            r = rng.uniform(0, self.radius)
            lx = x + math.cos(angle) * r
            ly = y + math.sin(angle) * r
            # Stagger delays so meteors arrive in a rhythmic sequence.
            delay = (i / max(1, self.meteor_count - 1)) * self.window \
                if self.meteor_count > 1 else 0.0
            delay += rng.uniform(-0.08, 0.08)
            delay = max(0.0, delay)
            packet = DamagePacket(self.damage, DamageType.FIRE, source=self)
            spawn_y = SCREEN_HEIGHT + 80      # off the top of the screen
            m = FallingProjectile(
                texture=tex,
                target_x=lx,
                target_y=ly,
                spawn_y=spawn_y,
                speed=720.0,
                packet=packet,
                aoe_radius=self.per_meteor_aoe,
                fall_delay=delay,
            )
            ctx.scene.spawn_projectile(m)
        ctx.state.bus.publish(SKILL_USED, skill=self, target=target)
