"""Effect group toggling for cosmetic and informational visual layers."""

from __future__ import annotations

from solar_system_wallpaper.types import EffectGroup, RenderConfig


def is_enabled(config: RenderConfig, group: EffectGroup) -> bool:
    """Check whether an effect group is enabled in the given config."""
    if group == EffectGroup.COSMETIC:
        return config.cosmetic
    if group == EffectGroup.INFORMATIONAL:
        return config.informational
    return True
