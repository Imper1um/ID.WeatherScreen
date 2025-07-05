import math

from config.WeatherConfig import WeatherConfig
from core.WeatherDisplay import WeatherDisplay

class WindBuilder:
    def WindCircle(weatherDisplay: WeatherDisplay, weatherConfig: WeatherConfig) -> str:
        current = weatherDisplay.CurrentData
        radius = 60
        center = radius + 10
        wind_units = weatherConfig.Weather.Wind.name
        compass = [
            'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
            'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'
        ]

        def polar_to_cart(deg, scale=1.2):
            rad = math.radians(deg - 90)
            x = center + math.cos(rad) * radius * scale
            y = center + math.sin(rad) * radius * scale
            return (x, y)

        arrows = []
        points = []
        lines = [
            line for line in reversed(weatherDisplay.HistoryData.Lines[:-1])
            if line.WindDirection is not None
        ][:10]

        for i, line in enumerate(reversed(lines)):
            fade_ratio = 1.0 - ((i + 1) / len(lines))  # 0.9 to 0.0
            green = int(255 * fade_ratio)
            color = f"rgb(0,{green},0)"
            x, y = polar_to_cart(line.WindDirection, scale=0.9)
            arrows.append(f'<line x1="{center}" y1="{center}" x2="{x:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="3" marker-end="url(#arrow{i})"/>')
            points.append(f'''
                <marker id="arrow{i}" markerWidth="10" markerHeight="10" refX="6" refY="3"
                            orient="auto" markerUnits="strokeWidth">
                        <path d="M0,0 L0,6 L9,3 z" fill="{color}" />
                    </marker>
                    ''')

        x, y = polar_to_cart(current.WindDirection or 0)
        main_arrow = f'<line x1="{center}" y1="{center}" x2="{x:.1f}" y2="{y:.1f}" stroke="lime" stroke-width="5" marker-end="url(#arrow)"/>'

        deg = int(current.WindDirection or 0)
        compass_dir = compass[int((deg + 11.25) % 360 / 22.5)]
        direction_label = f"{deg}° ({compass_dir})"
        speed = f"{current.WindSpeed:.1f} {wind_units}"
        gust = f"({current.WindGust:.1f} {wind_units})"

        return f'''
        <div class="wind-circle p-2 text-center">
            <svg width="{center*2}" height="{center*2}" viewBox="0 0 {center*2} {center*2}">
                <defs>
                    <marker id="arrow" markerWidth="10" markerHeight="10" refX="6" refY="3"
                            orient="auto" markerUnits="strokeWidth">
                        <path d="M0,0 L0,6 L9,3 z" fill="lime" />
                    </marker>
                    {"".join(points)}
                </defs>
                <circle cx="{center}" cy="{center}" r="{radius}" stroke="black" stroke-width="3" fill="none" />
                {"".join(arrows)}
                {main_arrow}
            </svg>
            <div class="fw-bold">{speed}</div>
            <div class="fst-italic">{gust}</div>
            <div>{direction_label}</div>
        </div>
        '''