from rest_framework.renderers import BaseRenderer


class ProxyRender(BaseRenderer):
    media_type = ''
    format = ''

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data
