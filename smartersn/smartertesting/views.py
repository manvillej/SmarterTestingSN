from django.shortcuts import render
from django.views.generic import View


from .forms import UploadFileForm
from .models import UpdateSet, SNObjectType, SNObject
import xmltodict
import json


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

            for update in updates:
                #print(f'list: {list(update.keys())}')
                # decode payload xml
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


                    if(update["type"]=="Business Rule"):
                        # cart = Cart(customer=user, state=new)

                        sys_id = {record_update[table]["sys_id"]}
                        name = record_update[table]["name"]

                        try:
                            sn_object = SNObject.objects.get(sys_id=update_type)
                        except SNObject.DoesNotExist:
                            sn_object = SNObject(sys_id=sys_id, name=name, object_type=sn_type)
                            sn_object.save()
                else:
                    """
                    known unhandled types:
                    key = "sys_dictionary"
                    key = "sys_documentation"
                    key = "sys_ui_section"
                    """
                    pass





        return render(request, self.template_name, {'form': form})




