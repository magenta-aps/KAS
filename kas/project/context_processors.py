from django.conf import settings


def feature_flag_processor(request):
    return {'feature_flags': settings.FEATURE_FLAGS}
