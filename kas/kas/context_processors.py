from django.conf import settings
from kas.models import RepresentationToken


def representation_processor(request):
    if request.user.is_authenticated:
        return {
            "representing": RepresentationToken.objects.filter(
                user=request.user, consumed=True
            ).first(),
            "representation_stop": settings.SELVBETJENING_REPRESENTATION_STOP,
        }
    return {}
