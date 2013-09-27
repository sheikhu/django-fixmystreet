import csv
import StringIO
import datetime

from django.db.models import ForeignKey
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth import authenticate, login
from django.contrib.gis.geos import GEOSGeometry

from piston.handler import BaseHandler
from piston.emitters import Emitter

from django_fixmystreet.fixmystreet.models import Report, FMSUser, ReportCategory, ReportSecondaryCategoryClass, ReportMainCategoryClass, OrganisationEntity
from django_fixmystreet.fixmystreet.forms import CitizenForm, CitizenReportForm, ProReportForm, ReportCommentForm
from django_fixmystreet.fixmystreet.utils import RequestFingerprint

from rest_framework import viewsets, routers, serializers, renderers


class JSONRenderer(renderers.JSONRenderer):
    media_type = 'application/json'
    format = 'json'

    def render(self, data, media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        geom_field = getattr(renderer_context.get('view'), 'geometry_field_name')

        for elem in data:
            geometry = elem[geom_field]

            if isinstance(geometry, basestring):
                geometry = GEOSGeometry(geometry)

            elem[geom_field] = (geometry.x, geometry.y)

        return super(JSONRenderer, self).render(data, media_type, renderer_context)


class GeoJSONRenderer(renderers.JSONRenderer):
    media_type = 'application/json'
    format = 'geojson'

    def render(self, data, media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        geom_field = getattr(renderer_context.get('view'), 'geometry_field_name')

        if isinstance(data, list):
            new_data = {
              'type': 'FeatureCollection',
              'features': [(self.get_feature(elem, geom_field) or elem) for elem in data]
            }
        else:
            new_data = self.get_feature(data, geom_field) or data

        return super(GeoJSONRenderer, self).render(new_data, media_type, renderer_context)

    def get_feature(self, data, geom_field):

        geometry = data.pop(geom_field)

        if isinstance(geometry, basestring):
            geometry = GEOSGeometry(geometry)
        feature = {
            'type': 'Feature',
            'geometry':{
                'type': 'Point',
                'coordinates': [
                    geometry.x,
                    geometry.y
                ]
            },
            'properties': data,
        }

        return feature



class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('id', 'status', 'point')


class ReportViewSet(viewsets.ModelViewSet):
    allowed_methods = ('GET', 'OPTIONS')
    model = Report
    serializer_class = ReportSerializer
    renderer_classes = (
        JSONRenderer,
        renderers.BrowsableAPIRenderer,
        GeoJSONRenderer
        )
    geometry_field_name = 'point'


router = routers.DefaultRouter()
router.register(r'reports', ReportViewSet)


# ###############
# # CSV emitter #
# ###############
class CSVEmitter(Emitter):
    """
    Emitter for exporting to CSV (excel dialect).
    """
    def get_keys(self, prefix='', handler=None):
        if prefix:
            prefix = prefix + '.'
        keys = []

        fields = handler.fields
        current_model = handler.model
        for key in fields:
            if key in current_model._meta.get_all_field_names() and isinstance(current_model._meta.get_field(key), ForeignKey):
                keys.extend(self.get_keys(prefix + key, handler=self.in_typemapper(current_model._meta.get_field(key).rel.to, self.anonymous)))
                # keys.extend(self.get_keys(item[1]))
            else:
                keys.append(prefix + key)

        return keys

    def get_values(self, input_dict, field_order=None):
        values = []
        for key in field_order:

            if key in input_dict:
                value = input_dict[key]
            else:
                value = input_dict
                for n in key.split('.'):
                    if value is not None:
                        value = value[n]

            values.append(unicode(value).encode('iso-8859-15'))
        return values

    def render(self, request):
        output = StringIO.StringIO()
        content = self.construct()

        if not isinstance(content, (list, tuple)):
            content = [content]

        headers = self.get_keys(handler=self.handler)

        writer = csv.writer(output, delimiter=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

        writer.writerow(headers)


        for row in content:
            writer.writerow(self.get_values(row, field_order=headers))

        # return  output.getvalue()

        csv_content = output.getvalue()
        output.close()

        response = HttpResponse()
        response['Content-Type'] = 'application/csv; charset=iso-8859-15'
        response['Content-Disposition'] = 'attachment; filename=' + self.handler.get_csv_filename(request)
        response.write(csv_content)

        return response

Emitter.register('csv', CSVEmitter, 'application/csv; charset=iso-8859-15')


class CategoryHandler(BaseHandler):
    allowed_methods = ('GET')
    model = ReportCategory
    fields = (
        'name',
    )

class ReportSecondaryCategoryHandler(BaseHandler):
    allowed_methods = ('GET')
    model = ReportSecondaryCategoryClass
    fields = (
        'name',
    )

class ReportMainCategoryHandler(BaseHandler):
    allowed_methods = ('GET')
    model = ReportMainCategoryClass
    fields = (
        'name',
    )

class FMSUserHandler(BaseHandler):
    allowed_methods = ('GET')
    model = FMSUser
    fields = (
        'get_full_name',
        'organisation',
        'email',
    )

class EntityHandler(BaseHandler):
    allowed_methods = ('GET')
    model = OrganisationEntity
    fields = (
        'name',
    )


class ReportHandler(BaseHandler):
    '''This handler is called by mobile to manage reports'''
    allowed_methods = ('GET', 'POST')
    model = Report
    fields = (
        'id',
        'point',
        'status',
        'get_public_status_display',
        'get_status_display',
        'created',
        'created_by',
        'is_pro',
        'responsible_manager',
        'contractor',
        'category',
        'secondary_category',
        'address',
        'address_number',
        'address_regional',
        'postalcode'
    )


    def read(self, request, *args, **kwargs):

        if 'time_ago' in kwargs:
            time_ago = kwargs['time_ago']
            if time_ago=='week':
                return Report.objects.one_week_ago()
            elif time_ago=='month':
                return Report.objects.one_month_ago()
            else:
                return HttpResponseBadRequest("invalid argument time_ago {0}".format(time_ago))
        elif 'id' in kwargs:
            return Report.objects.get(pk=kwargs['id'])
        else:
            return Report.objects.all()


#    @validate(CitizenReportForm, 'POST')
    def create(self, request):
        fingerprint = RequestFingerprint(request)
        if not fingerprint.is_duplicate():
            fingerprint.save()
            if request.data.get('username', False):
                return self.create_pro(request)
            else:
                return self.create_citizen(request)

    def create_pro(self, request):
        '''Create pro report'''
        #Login the user
        user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
        if user and user.is_active:
            login(request, user)
        else:
            return HttpResponseForbidden('invalid username or password')

        #Create report self'''
        report_form = ProReportForm(request.data, prefix='report')
        comment_form = ReportCommentForm(request.data, prefix='comment')
        if not report_form.is_valid():
            return HttpResponse(unicode(report_form.errors), status=400)
        report = report_form.save(commit=False)

        report.private = True
        report.save()

        report.subscribe_author()

        #Create the comment is a comment has been given'''
        if (request.data["comment-text"] or comment_form.is_valid()):
            comment = comment_form.save(commit=False)
            comment.report = report
            comment.save()

        return report

    def create_citizen(self, request):
        '''Create citizen report'''
        try:
            citizen = FMSUser.objects.get(email=request.data.get('citizen-email'))
        except FMSUser.DoesNotExist:
            citizen_form = CitizenForm(request.data, prefix='citizen')
            if not citizen_form.is_valid():
                return HttpResponse(unicode(citizen_form.errors), status=400)
            citizen = citizen_form.save()

        #Create report self'''
        report_form = CitizenReportForm(request.data, prefix='report')
        comment_form = ReportCommentForm(request.data, prefix='comment')
        if not report_form.is_valid():
            return HttpResponse(unicode(report_form.errors), status=400)

        report = report_form.save(commit=False)
        report.citizen = citizen
        #report.category = ReportMainCategoryClass(request.data['secondary_category'])
        #report.secondary_category = ReportCategory(request.data['category'])
        report.save()

        report.subscribe_author()

        #Create the comment is a comment has been given'''
        if (request.data["comment-text"] or comment_form.is_valid()):
            comment = comment_form.save(commit=False)
            comment.created_by = citizen
            comment.report = report
            comment.save()

        return report

    def get_csv_filename(self, request):
        return 'incident_{0}_{1}.csv'.format(request.GET.get('id') or 'all', datetime.date.today())
