from django.core.checks import Error, register, Tags


@register(Tags.models)
def check_models(app_configs, **kwargs):
    errors = []
    if app_configs is not None:
        for app_config in app_configs:
            for model in app_config.get_models():
                if not model._meta.abstract and model._meta.managed:
                    # Check ordering
                    if len(model._meta.ordering) == 0:
                        errors.append(
                            Error(
                                "Model should specify an ordering",
                                hint="To provide a default ordering in lists, all "
                                "models should specify how they are ordered",
                                obj=model,
                                id="kas.E001",
                            )
                        )

                # TODO: More checks
    return errors
