import datetime

from django.template.defaultfilters import date as date_filter
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import formats
from django.utils.translation import get_language
from rest_framework.serializers import ModelSerializer

from worker.models import Job


class LocalizeDateModelSerializer(ModelSerializer):
    """
    instead of returning a isoformatted date as normally by a rest endpoint we return a localized date to be used directly in the bootstrap table
    """
    def __init__(self, *args, **kwargs):
        self.lang = get_language()
        self.date_time_format = formats.get_format('SHORT_DATETIME_FORMAT', lang=self.lang)
        self.date_format = formats.get_format('SHORT_DATE_FORMAT', lang=self.lang)
        super(LocalizeDateModelSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, instance):
        rep = super(LocalizeDateModelSerializer, self).to_representation(instance)
        for key, value in rep.items():
            try:
                attribute = getattr(instance, key)
            except AttributeError:
                # skip "virtuel/composite" attribute
                continue
            if isinstance(attribute, datetime.datetime):
                rep[key] = date_filter(getattr(instance, key), self.date_time_format)
            elif isinstance(attribute, datetime.date):
                rep[key] = date_filter(getattr(instance, key), self.date_format)
        return rep


class JobSerializer(LocalizeDateModelSerializer):
    def to_representation(self, instance):
        rep = super(JobSerializer, self).to_representation(instance)
        rep['created_by'] = instance.created_by.username
        rep['progress'] = render_to_string('worker/includes/progress_bar.html', context={'job': instance})
        rep['detail_url'] = '<a href="{}">{}</a>'.format(reverse('worker:job_detail', kwargs={'uuid': instance.uuid}),
                                                         instance.pretty_job_title)
        return rep

    class Meta:
        model = Job
        fields = ('uuid', 'job_type', 'created_by', 'created_at', 'started_at', 'end_at', 'parent', 'progress', 'status')
