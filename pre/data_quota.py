import json

import gc
import xmltodict

## DONE i guess


def read_data():
    with open('PRE_Offers.xml') as file:
        raw_data = file.read()
        file.close()
        return raw_data


def reset_file():
    file_name = "presql/pre_dataquota.sql"
    open(file_name, "w").close()


parser = json.loads(json.dumps(xmltodict.parse(read_data(), process_namespaces=True)))
reset_file()


def write_to_file(table, uid, *args):
    file_name = "presql/pre_dataquota.sql"

    insert_line = "insert into " + table + " VALUES (\'" + uid + "\'"
    for arg in args:
        if arg == "null":
            insert_line += ", null"
        else:
            insert_line += ", \'" + arg + "\'"
    insert_line += "); \n"
    with open(file_name, "a") as file:
        file.write(insert_line)

def find_value_in_props_file(language_variable, file_name):
    with open(file_name) as file:
        raw_data = file.readlines()
        file.close()
        for line in raw_data:
            if language_variable in line:
                index_of_equalsign = line.find('=')
                return line[index_of_equalsign + 2:].rstrip()

def generate_multilanguage_nestedkeyvalue(object_type, key, id, version, keyvalue_uid):
    prop_files = {"eng": "../language_files/Language-offers_hu.properties",
                  "hun": "../language_files/Language-offers_en.properties",
                  "def": "../language_files/Language-offers.properties",
                  "unLocalized": "null"}

    language_variable = "PRE." + object_type + "." + id + "." + key
    for lang, path in prop_files.items():
        if lang == "unLocalized":
            prop_line = path

        else:
            prop_line = find_value_in_props_file(language_variable, path)
            if prop_line is None:
                #print(language_variable)
                prop_line = "null"

        nestedkeyvalue_uid = keyvalue_uid + "-" + lang
        # print(prop_line)
        write_to_file("nestedkeyvalue", nestedkeyvalue_uid, keyvalue_uid, prop_line)


def is_dictionary(ele):
    return type(ele) == type(dict())


def parse_xml_to_json():
    print("data_quota")
    version = "1.0.0"
    # objecttype -> Offers/Addons/Rewards etc..
    # object_uid = objectType
    object_type = "DataQuotas"
    value_type = "DataQuota"
    # print(parser['OfferConfig'][object_type][value_type]) # list of keyvalues
    dataquota_list = parser['OfferConfig'][object_type][value_type]
    for dataquota in dataquota_list:
        dataquota_id = dataquota['Id']
        object_uid = dataquota_id + "-" + version
        write_to_file("object", object_uid, dataquota_id)
        for key, val in dataquota.items():
            keyvalue_uid = dataquota_id + "-" + version + "-" + key
            implementedrow_uid = "Pre-DataQuota-"+version + "-" + key
            input_val = "null"

            if is_dictionary(val):
                if val['@localized'] == "true":
                    generate_multilanguage_nestedkeyvalue(object_type, key, dataquota_id, version, keyvalue_uid)
                else:
                    print("this shouldnt run")

            else:
                if val is not None:
                    input_val = val
            # print(keyvalue_uid, implementedrow_uid, input_val)
            gc.collect()
            write_to_file("keyvalue", keyvalue_uid, object_uid, implementedrow_uid, input_val)





parse_xml_to_json()