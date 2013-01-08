from piston.emitters import Emitter

import csv
import datetime
import StringIO

from piston.handler import BaseHandler

from django_fixmystreet.fixmystreet.models import Report, ReportComment, ReportFile

##################
# Extra emitters #
##################
class TextEmitter(Emitter):
    def render(self, request):
        return self.construct()

class CSVEmitter(Emitter):
    def render(self, request):
        output = StringIO.StringIO()
        seria = []
        #Test if multiple record received...
        if (self.construct().__class__ == list):
            seria.extend(self.construct())
        else:
            seria.insert(0,self.construct())
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

        # Write headers to CSV file
        headers = []
        for field in Report._meta.fields:
            headers.append(field.name)
        writer.writerow(headers)
        counter = -1
        # Write data to CSV file
        for obj in seria:
            counter = counter + 1
            if isinstance(self.data, Report):
                current_report_id = self.data.id
            else:
                current_report_id = self.data[counter].id
            row = []
            for field in headers:
                if field in headers:
                    val = None
                    if (field != 'id'):
                        val = obj.get(field)
                    if callable(val):
                        val = val()
                    if (val != None):
                        if isinstance(val, datetime.datetime):
	                    val = val.strftime("%s %s" % ('%Y-%m-%d', '%H:%M:%S'))
                        elif (hasattr(val,'encode')):
                            val = val.encode("utf-8")
                        row.append(val)
                    else:
                        row.append("")
            writer.writerow(row)
            #Append annexes (files)
            try:
                report_files = ReportFile.objects.filter(report__id = current_report_id)
                file_counter = 0
                for file_obj in report_files:
                    if file_counter == 0:
                        writer.writerow(['Files'])
                        writer.writerow(['Filename', 'Creator', 'File Creation Date', 'File Import Date'])
                    writer.writerow([file_obj.file.__str__(),file_obj.get_display_name(), file_obj.file_creation_date.strftime("%s %s" % ('%Y-%m-%d', '%H:%M:%S')), file_obj.created.strftime("%s %s" % ('%Y-%m-%d', '%H:%M:%S'))])
                    file_counter = file_counter + 1
            except ReportFile.DoesNotExist:
                print('error') 
            #Append annexes (comments)
            try:
                report_comments = ReportComment.objects.filter(report__id = current_report_id)
                comment_counter = 0
                for comment_obj in report_comments:
                    if comment_counter == 0:
                        writer.writerow(['Comments'])
                        writer.writerow(['Filename', 'Creator', 'File Import Date'])
                    writer.writerow([comment_obj.text.__str__(),comment_obj.get_display_name(), comment_obj.created.strftime("%s %s" % ('%Y-%m-%d', '%H:%M:%S'))])
                    comment_counter = comment_counter + 1
            except ReportComment.DoesNotExist:
                print('error') 
        




        #csvWriter.writerow(
	#	[	#'id', 
	#			'date_created', 
	#		'date_modified',
	#		'refusal_motivation',
	#		'address',
	#		'address_number',
	#		'postalcode',
	#		'point',
	#		'photo',
	#		'private',
	#		'close_date',
	#		'fixed_at',
	#		'quality',
	#		'responsible_manager_validated',
	#		'contractor',
	#		'valid',
	#		'citizen',
	#		'status',
	#		'description',
	#		'created',
	#		'mark_as_done_motivation',
	#		'modified',
	#		'hash_code',

	#		'created_by/last_name'
	#		'created_by/telephone'
	#		'created_by/agent'
	#		'created_by/user_ptr_id'
	#		'created_by/manager'
	#		'created_by/is_staff'
	#		'created_by/logical_deleted'
	#		'created_by/id'
	#		'created_by/date_joined'
	#		'created_by/first_name'
	#		'created_by/contractor'
	#		'created_by/is_superuser'
	#		'created_by/last_login'
	#		'created_by/leader'
	#		'created_by/username'
	#		'created_by/last_used_language'
	#		'created_by/is_active'
	#		'created_by/password'
	#		'created_by/organisation_id'
	#		'created_by/applicant'
	#		'created_by/email'
			
	#		'modified_by/last_name'
	#		'modified_by/telephone'
	#		'modified_by/agent'
	#		'modified_by/user_ptr_id'
	#		'modified_by/manager'
	#		'modified_by/is_staff'
	#		'modified_by/logical_deleted'
	#		'modified_by/id'
	#		'modified_by/date_joined'
	#		'modified_by/first_name'
	#		'modified_by/contractor'
	#		'modified_by/is_superuser'
	#		'modified_by/last_login'
	#		'modified_by/leader'
	#		'modified_by/username'
	#		'modified_by/last_used_language'
	#		'modified_by/is_active'
	#		'modified_by/password'
	#		'modified_by/organisation_id'
	#		'modified_by/applicant'
	#		'modified_by/email'

	#		'responsible_manager/last_name'
	#		'responsible_manager/telephone'
	#		'responsible_manager/agent'
	#		'responsible_manager/user_ptr_id'
	#		'responsible_manager/manager'
	#		'responsible_manager/is_staff'
	#		'responsible_manager/logical_deleted'
	#		'responsible_manager/id'
	#		'responsible_manager/date_joined'
	#		'responsible_manager/first_name'
	#		'responsible_manager/contractor'
	#		'responsible_manager/is_superuser'
	#		'responsible_manager/last_login'
	#		'responsible_manager/leader'
	#		'responsible_manager/username'
	#		'responsible_manager/last_used_language'
	#		'responsible_manager/is_active'
	#		'responsible_manager/password'
	#		'responsible_manager/organisation_id'
	#		'responsible_manager/applicant'
	#		'responsible_manager/email'

	#		'responsible_entity/dependency_id',
	#		'responsible_entity/commune',
	#		'responsible_entity/slug_en',
	#		'responsible_entity/name_fr',
	#		'responsible_entity/name_nl',
	#		'responsible_entity/created',
	#		'responsible_entity/region',
	#		'responsible_entity/applicant',
	#		'responsible_entity/modified',
	#		'responsible_entity/slug_nl',
	#		'responsible_entity/feature_id',
	#		'responsible_entity/subcontractor',
	#		'responsible_entity/modified_by_id',
	#		'responsible_entity/created_by_id',
	#		'responsible_entity/name_en',
	#		'responsible_entity/slug_fr',
	#		'responsible_entity/id',
			
	#		'category/update_date',
	#		'category/slug_en',
	#		'category/name_fr',
	#		'category/name_nl',
	#		'category/creation_date',
	#		'category/hind_id',
	#		'category/slug_nl',
	#		'category/name_en',
	#		'category/slug_fr',
	#		'category/id',


	#		'secondary_category/update_date',
	#		'secondary_category/slug_en',
	#		'secondary_category/name_fr',
	#		'secondary_category/name_nl',
	#		'secondary_category/secondary_category_class_id',
	#		'secondary_category/creation_date',
	#		'secondary_category/slug_nl',
	#		'secondary_category/public',
	#		'secondary_category/name_en',
	#		'secondary_category/slug_fr',
	#		'secondary_category/id',
	#		'secondary_category/category_class_id',
			
        #		]
	#)
        #for entry in seria:
        #    row = []
        #    import pdb
        #    pdb.set_trace()  
        #    if entry.has_key('id'):
        #        row.append(entry.pop('id'))
        #    else:
        #        row.append('')

        #if entry.has_key('has:area_of_expertise'):
        #    row.append(", ".join([x['name'] for x in entry.pop('has:area_of_expertise')]))
        #else:
        #    row.append('')

        #csvWriter.writerow([x.encode('utf-8') for x in row])
        return output.getvalue()


######################
# Map Extra Emitters #
######################
Emitter.register('text', TextEmitter, 'text/plain; charset=utf-8')
Emitter.register('csv', CSVEmitter, 'text/csv; charset=utf-8')


######################
# Hanlders (Piston)  #
######################
class ReportHandler(BaseHandler):
    """A handler centralized for report exportation to files"""
    allowed_methods = ('GET')
    model = Report
    #exclude = ('_state')

    @classmethod
    def content_length(cls, blogpost):
        return len(blogpost.content)


    def read(self, request):
        """Read the elements matching export request and delegate to the emitter"""

        #Get the first parameter as ID
        report_id = None
        try:
            report_id = int(request.REQUEST.values()[0])
        except IndexError:
            pass
        base = Report.objects
        if report_id:
            return base.get(id=report_id)
        else:
            return base.all()
