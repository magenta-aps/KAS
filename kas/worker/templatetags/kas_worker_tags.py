from django.template.defaultfilters import register
from django.utils.translation import ngettext as __


@register.filter
def duration(td):
    total_seconds = int(td.total_seconds())
    days = int(total_seconds / 86400)
    remaining_hours = total_seconds % 86400
    remaining_minutes = remaining_hours % 3600
    hours = int(remaining_hours / 3600)
    minutes = int(remaining_minutes / 60)
    seconds = (remaining_minutes % 60) + (td.total_seconds() - total_seconds)

    return ", ".join(
        [
            f"{value} {unit}"
            for value, unit in [
                (days, __("dag", "dage", days)),
                (hours, __("time", "timer", hours)),
                (minutes, __("minut", "minutter", minutes)),
                (seconds, __("sekund", "sekunder", seconds)),
            ]
            if value or unit == "s"
        ]
    )
