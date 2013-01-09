from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _

from django_fixmystreet.backoffice.forms import UserEditForm, FmsUserForm
from django_fixmystreet.fixmystreet.models import OrganisationEntity, FMSUser, ReportNotification

from django.contrib.sites.models import Site
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from smtplib import SMTPException

def show(request):
    user = request.fmsuser
    userType = request.REQUEST.get("userType")
    currentOrganisationId = user.organisation.id
    users = []
    if userType == 'users':
        #Get organisations dependants from the current organisation id
        dependantOrganisations = OrganisationEntity.objects.filter(dependency_id = currentOrganisationId)
        allOrganisation = list(dependantOrganisations)
        allOrganisation.append(currentOrganisationId)
        users = FMSUser.objects.filter(organisation_id__in=allOrganisation)
    if userType == 'agent':
        users = FMSUser.objects.filter(organisation_id=currentOrganisationId)
        users = users.filter(agent = True)
    if userType == 'contractor':
        dependantOrganisations = OrganisationEntity.objects.filter(dependency_id = currentOrganisationId)
        allOrganisation = list(dependantOrganisations)
        users = FMSUser.objects.filter(organisation_id__in=allOrganisation)
        users = users.filter(contractor=True)
    if userType == 'applicant':
        users = FMSUser.objects.filter(organisation_id=currentOrganisationId)
        users = users.filter(applicant=True)
    if userType == 'manager':
        users = FMSUser.objects.filter(organisation_id=currentOrganisationId)
        users = users.filter(manager=True)
    
    users = users.filter(logical_deleted = False)
    
    return render_to_response("pro/users_overview.html",{
        "users":users,
    },context_instance=RequestContext(request))


def edit(request):
    userType = request.REQUEST.get("userType")
    #Get user connected
    user = request.fmsuser
    
    currentOrganisationId = user.organisation.id
    users = []
    if userType == 'users':
        #Get organisations dependants from the current organisation id
        dependantOrganisations = OrganisationEntity.objects.filter(dependency_id = currentOrganisationId)
        allOrganisation = list(dependantOrganisations)
        allOrganisation.append(currentOrganisationId)
        users = FMSUser.objects.filter(organisation_id__in=allOrganisation)
    if userType == 'agent':
        users = FMSUser.objects.filter(organisation_id=currentOrganisationId)
        users = users.filter(agent = True)
    if userType == 'contractor':
        dependantOrganisations = OrganisationEntity.objects.filter(dependency_id = currentOrganisationId)
        allOrganisation = list(dependantOrganisations)
        users = FMSUser.objects.filter(organisation_id__in=allOrganisation)
        users = users.filter(contractor=True)
    if userType == 'impetrant':
        users = FMSUser.objects.filter(organisation_id=currentOrganisationId)
        users = users.filter(applicant=True)
    if userType == 'manager':
        users = FMSUser.objects.filter(organisation_id=currentOrganisationId)
        users = users.filter(manager=True)
    #Filter deleted users
    users = users.filter(logical_deleted = False)
    #Get used to edit
    user_to_edit = FMSUser.objects.get(pk=int(request.REQUEST.get('userId')))

    connectedUser = request.fmsuser
    canEditGivenUser = (((user_to_edit.manager or user_to_edit.agent) and connectedUser.leader) or ((user_to_edit.agent) and connectedUser.manager))
    return render_to_response("pro/users_overview.html",{
                        "users":users,
                        "canEditGivenUser":canEditGivenUser,
                        "editForm":UserEditForm(instance=user_to_edit)
                        },context_instance=RequestContext(request))


def saveChanges(request):
    userEditForm = UserEditForm(request.POST)
    userEditForm.save(request.REQUEST.get('userId'))
    return HttpResponseRedirect('/pro/users/overview?userType='+request.REQUEST.get('userType'))


def deleteUser(request):
    # todo set active = false
    user_to_delete = FMSUser.objects.get(id=request.REQUEST.get('userId'))
    user_to_delete.logical_deleted = True
    user_to_delete.is_active = False
    user_to_delete.save()
    #FMSUser.objects.get(id=request.REQUEST.get('userId')).delete()
    return HttpResponseRedirect('/pro/users/overview?userType='+request.REQUEST.get('userType'))

def createUser(request, user_type):
    connectedUser = request.fmsuser    
    isManager = connectedUser.manager    
    #a boolean value to tell the ui if the user can edit the given form content
    if request.method == "POST":
        #try:
        #   import pdb
        #   pdb.set_trace()
        #   user_type = simplejson.loads(request.body).get('user_type')
        #except ValueError as e:
        user_type = request.POST.get("user_type")
        createform = FmsUserForm(request.POST)
        if createform.is_valid():
            createdOrganisationEntity = -1;    
            #Also create the organisation too            
            if (user_type == FMSUser.CONTRACTOR):
                createdOrganisationEntity = OrganisationEntity()
                createdOrganisationEntity.name_nl = request.POST.get('first_name')+"/"+request.POST.get('last_name')
                createdOrganisationEntity.name_fr = request.POST.get('first_name')+"/"+request.POST.get('last_name')
                createdOrganisationEntity.name_en = request.POST.get('first_name')+"/"+request.POST.get('last_name')
                createdOrganisationEntity.region = False
                createdOrganisationEntity.commune = False
                createdOrganisationEntity.subcontractor = True
                createdOrganisationEntity.applicant = False
                createdOrganisationEntity.dependency_id = connectedUser.organisation.id
                createdOrganisationEntity.save()
            
            createdUser = createform.save(connectedUser, createdOrganisationEntity, user_type)

            if createdUser:
                # notification = ReportNotification(
                #     content_template='send_created_to_user',
                #     recipient=createdUser,
                #     related=createdUser,
                # )
                # notification.save()
                    # data={
                        # "password":request.POST.get('password1')
                    # })

                #Send directly an email to the created user (do not use the reportnotification class because then the password is saved in plain text in the DB)
                recipients = (createdUser.email,)

                data = {
                    "user": createdUser,
                    "password":request.POST.get('password1'),
                    "SITE_URL": Site.objects.get_current().domain
                }

                subject, html, text = '', '', ''
                try:
                    subject = render_to_string('emails/send_created_to_user/subject.txt', data)
                except TemplateDoesNotExist:
                    # instance.error_msg = "No subject"
                    print 'template does not exist'
                try:
                    text    = render_to_string('emails/send_created_to_user/message.txt', data)
                except TemplateDoesNotExist:
                    # instance.error_msg = "No content"
                    print "template does not exist"

                try:
                    html    = render_to_string('emails/send_created_to_user/message.html', data)
                except TemplateDoesNotExist:
                    pass

                subject = subject.rstrip(' \n\t').lstrip(' \n\t')

                msg = EmailMultiAlternatives(subject, text, settings.EMAIL_FROM_USER, recipients, headers={"Reply-To":connectedUser.email})

                if html:
                    msg.attach_alternative(html, "text/html")
                try:
                    msg.send()
                except SMTPException as e:
                    print "not sent successfully"

                messages.add_message(request, messages.SUCCESS, _("User has been created successfully"))
                return HttpResponseRedirect('/pro/')
    else:        
        createform = FmsUserForm()
        #user_type is used when accessing the page the first time to preset the dropdown value        
        createform.initial['user_type'] = user_type        
    
    return render_to_response("pro/user_create.html",
            {
                "createform":createform,
                "isManager":isManager
            },
            context_instance=RequestContext(request))
