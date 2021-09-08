from rest_framework.renderers import BaseRenderer


class PdfProxyRender(BaseRenderer):
    media_type = 'application/pdf'
    format = ''

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data
