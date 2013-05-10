import csv
import StringIO
import datetime

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth import authenticate, login

from piston.handler import BaseHandler
from piston.emitters import Emitter

from django_fixmystreet.fixmystreet.models import Report, FMSUser, ReportCategory, ReportSecondaryCategoryClass, ReportMainCategoryClass, OrganisationEntity
from django_fixmystreet.fixmystreet.forms import CitizenForm, CitizenReportForm, ProReportForm, ReportCommentForm


# ###############
# # CSV emitter #
# ###############
class CSVEmitter(Emitter):
    """
    Emitter for exporting to CSV (excel dialect).
    """
    def get_keys(self, input_dict, prefix='', field_order=None):
        if prefix:
            prefix = prefix + '.'
        keys = []
        for key in field_order or input_dict.keys():
            if isinstance(input_dict[key], dict):
                keys.extend(self.get_keys(input_dict[key], prefix + key))
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

        headers = self.get_keys(content[0], field_order=self.fields)

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
        'name_fr',
        'name_nl',
    )

class ReportSecondaryCategoryHandler(BaseHandler):
    allowed_methods = ('GET')
    model = ReportSecondaryCategoryClass
    fields = (
        'name_fr',
        'name_nl',
    )

class ReportMainCategoryHandler(BaseHandler):
    allowed_methods = ('GET')
    model = ReportMainCategoryClass
    fields = (
        'name_fr',
        'name_nl',
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
        'name_fr',
        'name_nl',
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
        'territorial_entity',
        'category',
        'secondary_category',
        'address',
        'address_number',
        'address_regional',
        'postalcode',
        'quality',
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
        if request.data.get('username', False):
            return self.create_pro(request)
        else:
            return self.create_citizen(request)

    def create_pro(self, request):
        '''Create pro report'''
        #Login the user
        user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
        if user and user.is_active == True:
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
        report.subscribe_author()

        report.save()

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