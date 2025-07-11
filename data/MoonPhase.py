from enum import Enum

class MoonPhase(Enum):
    NewMoon = "New Moon"
    WaxingCrescent = "Waxing Crescent"
    FirstQuarter = "First Quarter"
    WaxingGibbous = "Waxing Gibbous"
    FullMoon = "Full Moon"
    WaningGibbous = "Waning Gibbous"
    LastQuarter = "Last Quarter"
    WaningCrescent = "Waning Crescent"

    @classmethod
    def FromString(cls, phase_str: str):
        for phase in cls:
            if phase.value.lower() == phase_str.lower():
                return phase
        if (phase_str.lower() == "third quarter"):
            return MoonPhase.LastQuarter
        raise ValueError(f"Unknown moon phase: {phase_str}")

    @property
    def ToEmoji(self) -> str:
        return {
            MoonPhase.NewMoon: "🌑",
            MoonPhase.WaxingCrescent: "🌒",
            MoonPhase.FirstQuarter: "🌓",
            MoonPhase.WaxingGibbous: "🌔",
            MoonPhase.FullMoon: "🌕",
            MoonPhase.WaningGibbous: "🌖",
            MoonPhase.LastQuarter: "🌗",
            MoonPhase.WaningCrescent: "🌘",
        }.get(self, "❓")