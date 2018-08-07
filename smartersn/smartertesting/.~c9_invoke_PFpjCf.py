import xmltodict

def get_dict_from_update_set(filepath):
    with open('smartertesting/testXML/sys_remote_update_set.xml') as
        update_set_dict = xmltodict.parse(file.read())
    return update_set_dict


def get_dict_from_xml_string(xml_string):
    """"""
    pass