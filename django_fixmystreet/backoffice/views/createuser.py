from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django_fixmystreet.fixmystreet.forms import AgentCreationForm
from django_fixmystreet.fixmystreet.models import FMSUser, ReportCategory, OrganisationEntity
from django.views.generic.edit import FormView


