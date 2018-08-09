from django.shortcuts import render, redirect
from django.views.generic import View
from django.template import loader
from django.http import HttpResponse
from django.db import IntegrityError
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

import xmltodict
import json

from .forms import UploadFileForm, ObjectTestRelationshipForm, UserForm
from .models import UpdateSet, SNObjectType, SNObject, SNTest, SNTestObjectRelation, Upload, ObjectUploadRelation
from .SNIntegration import SNInstance


@login_required
def uploads(request):
    """returns a list view of of uploads"""
    template = loader.get_template("smartertesting/uploads.html")
    context = {
        "uploads":Upload.objects.all(),
    }

    # update tests from SN
    dev = SNInstance()
    dev.get_tests()

    return HttpResponse(template.render(context, request))


@login_required
def upload_details(request, upload_id):
    """returns a details view of a upload and a list view of related tests and objects"""
    template = loader.get_template("smartertesting/upload_details.html")

    # update tests from SN
    dev = SNInstance()
    dev.get_tests()

    upload = Upload.objects.get(id=upload_id)
    sn_objects = SNObject.objects.all()
    tests = SNTest.objects.all()

    object_relations = ObjectUploadRelation.objects.all().filter(upload=upload)
    sn_objects = {relation.sn_object for relation in object_relations}

    relations = SNTestObjectRelation.objects.all().filter(sn_object__in=sn_objects)
    tests = {relation.test for relation in relations}

    context = {
        "upload":upload,
        "sn_objects":sn_objects,
        "tests":tests,
    }

    return HttpResponse(template.render(context, request))


@login_required
def sn_objects(request):
    """returns a list view of sn objects"""
    template = loader.get_template("smartertesting/sn_objects.html")
    context = {
        "sn_objects":SNObject.objects.all(),
    }

    # update tests from SN
    dev = SNInstance()
    dev.get_tests()

    return HttpResponse(template.render(context, request))


@login_required
def sn_object_details(request, object_id):
    """returns a detail view of an sn object and its related tests"""
    # update tests from SN
    dev = SNInstance()
    dev.get_tests()

    template = loader.get_template("smartertesting/sn_object_details.html")

    sn_object = SNObject.objects.get(id=object_id)

    relations = SNTestObjectRelation.objects.all().filter(sn_object=object_id)
    tests = {relation.test for relation in relations}

    context = {
        "sn_object":sn_object,
        "tests":tests,
    }

    return HttpResponse(template.render(context, request))


@login_required
def sn_tests(request):
    """returns a list view of tests"""

    # update tests from SN
    dev = SNInstance()
    dev.get_tests()

    template = loader.get_template("smartertesting/sn_tests.html")
    context = {
        "tests":SNTest.objects.all(),
    }
    return HttpResponse(template.render(context, request))

@login_required
def sn_test_details(request, test_id):
    """returns a detail view of a test and a list of its related objects"""

    # update tests from SN
    dev = SNInstance()
    dev.get_tests()

    template = loader.get_template("smartertesting/sn_test_details.html")

    test = SNTest.objects.get(id=test_id)

    relations = SNTestObjectRelation.objects.all().filter(test=test_id)
    sn_objects = {relation.sn_object for relation in relations}

    context = {
        "test":test,
        "sn_objects":sn_objects,
    }

    return HttpResponse(template.render(context, request))


class ObjectTestRelationFormView(LoginRequiredMixin, View):
    """meant for adding tests to an object"""
    form_class = ObjectTestRelationshipForm
    template_name = "smartertesting/upload.html"

    def get(self, request):
        """"""
        # update tests from SN
        dev = SNInstance()
        dev.get_tests()

        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """"""
        form = self.form_class(request.POST)

        if(form.is_valid()):
            sn_object = form.cleaned_data['sn_object']
            test = form.cleaned_data['test']
            relationship = form.cleaned_data['relationship']

            # catch error if the user tries to create an existing relationship
            try:
                sn_relation = SNTestObjectRelation(test=test, sn_object=sn_object, description=relationship)
                sn_relation.save()
            except IntegrityError:
                # TODO: tell the user they can't insert the same relationship twice
                pass

        return render(request, self.template_name, {'form': self.form_class(None)})


class UploadFormView(LoginRequiredMixin, View):
    """form for uploading update sets into application"""
    form_class = UploadFileForm
    template_name = "smartertesting/upload.html"

    def get(self, request):
        """"""
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})


    def post(self, request):
        """"""
        form = self.form_class(request.POST, request.FILES)

        if(form.is_valid()):

            xml_file = request.FILES['file']


            remote_update_set = xmltodict.parse(xml_file)
            updates = remote_update_set["unload"]["sys_update_xml"]


            # create upload to add objects against
            update_set_name = remote_update_set["unload"]["sys_remote_update_set"]["name"]
            update_set_id = remote_update_set["unload"]["sys_remote_update_set"]["sys_id"]
            description = remote_update_set["unload"]["sys_remote_update_set"]["description"]

            # create upload to log objects against
            upload = Upload(
                update_set_name=update_set_name,
                update_set_id=update_set_id,
                description=description,)
            upload.save()


            # iterate through the updates
            for update in updates:
                # decode payload xml

                # used to skip a particular set of updaes that it can't handle yet
                if(not isinstance(update, dict)):
                    continue

                update_payload = xmltodict.parse(update["payload"])

                record_update = update_payload["record_update"]
                record_update_keys = list(record_update.keys())

                # only handling @table for now.
                if("@table" in record_update_keys):

                    table = record_update["@table"]
                    # get or create the type of SN object
                    update_type = update["type"]

                    try:
                        sn_type = SNObjectType.objects.get(name=update_type)
                    except SNObjectType.DoesNotExist:
                        sn_type = SNObjectType(name=update_type, code_name=table)
                        sn_type.save()

                    # another unhandled type
                    if(update_type=="Workflow"):
                        continue

                    # print(update_type)
                    # print(f'{update["type"]}, {table}: {record_update[table]["sys_id"]}')
                    # print(sorted(list(record_update[table].keys())))


                    if(update_type=="Business Rule"):
                        # cart = Cart(customer=user, state=new)

                        sys_id = record_update[table]["sys_id"]
                        name = record_update[table]["name"]

                        try:
                            sn_object = SNObject.objects.get(sys_id=sys_id)
                        except SNObject.DoesNotExist:
                            sn_object = SNObject(sys_id=sys_id, name=name, object_type=sn_type)
                            sn_object.save()

                        relation = ObjectUploadRelation(upload=upload, sn_object=sn_object)
                        relation.save()

                else:
                    """
                    known unhandled types:
                    key = "sys_dictionary"
                    key = "sys_documentation"
                    key = "sys_ui_section"
                    """
                    pass

        return render(request, self.template_name, {'form': form})

class UserFormView(View):
    """"""
    # TODO: UserFormView class docstring
    form_class = UserForm
    template_name = "smartertesting/registration_form.html"

    def get(self, request):
        """display a blank form"""
        # TODO: UserFormView.get docstring
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """Process form data"""
        # TODO: UserFormView.post docstring
        form = self.form_class(request.POST)

        if(form.is_valid()):
            user = form.save(commit=False)

            # cleaned normalized data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']

            user.username = username
            user.email = email

            # hash the password
            user.set_password(password)
            user.save()


            # returns user object if credentials are correct
            user = authenticate(username=username, password=password)

            if user is not None:
                 if user.is_active:
                     login(request, user)
                     return redirect('index')

        return render(request, self.template_name, {'form': form})
