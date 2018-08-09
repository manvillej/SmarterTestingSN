from django.shortcuts import render
from django.views.generic import View
from django.db import IntegrityError

import xmltodict
import json

from .forms import UploadFileForm, ObjectTestRelationshipForm
from .models import UpdateSet, SNObjectType, SNObject, SNTestObjectRelation, Upload, ObjectUploadRelation

class ObjectTestRelationFormView(View):
    form_class = ObjectTestRelationshipForm
    template_name = "smartertesting/upload.html"

    def get(self, request):
        """"""
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


class UploadFormView(View):
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
            title = form.cleaned_data['title']


            remote_update_set = xmltodict.parse(xml_file)
            updates = remote_update_set["unload"]["sys_update_xml"]


            # create upload to add objects against
            update_set_name = remote_update_set["unload"]["sys_remote_update_set"]["name"]
            update_set_id = remote_update_set["unload"]["sys_remote_update_set"]["sys_id"]
            description = remote_update_set["unload"]["sys_remote_update_set"]["description"]
            #print(description)
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

