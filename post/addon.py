import json

import gc
import xmltodict

## DONE i guess


def read_data():
    with open('POST_Offers.xml') as file:
        raw_data = file.read()
        file.close()
        return raw_data


def reset_file():
    file_name = "posql/post_addon.sql"
    open(file_name, "w").close()
    file_name = "posql/post_addon_nestedkeyval.sql"
    open(file_name, "w").close()
    file_name = "posql/post_addon_objectrelation.sql"
    open(file_name, "w").close()


parser = json.loads(json.dumps(xmltodict.parse(read_data(), process_namespaces=True)))
reset_file()


def write_to_file(table, uid, *args):
    file_name = "posql/post_addon.sql"
    if table == "object_relation":
        file_name = "posql/post_addon_objectrelation.sql"

    if table == "nested_key_value":
        file_name = "posql/post_addon_nestedkeyval.sql"

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

    language_variable = "POST." + object_type + "." + id + "." + key
    for lang, path in prop_files.items():
        if lang == "unLocalized":
            prop_line = path

        else:
            prop_line = find_value_in_props_file(language_variable, path)
            if prop_line is None:
                #print(language_variable)
                prop_line = "null"

        prop_line = prop_line.replace("don't", "don''t")
        nestedkeyvalue_uid = keyvalue_uid + "-" + lang
        nestedkeyvalue_id = id + "-" + key + "-" + lang
        implemented_nestedrow_uid = "Multi-language-" + lang
        write_to_file("nested_key_value", nestedkeyvalue_uid, nestedkeyvalue_id, prop_line, implemented_nestedrow_uid,keyvalue_uid)

def generate_psmcode_nestedkeyvalue(dict_val, keyvalue_uid, dictkey, id):
    for key, val in dict_val.items():
        nestedkeyvalue_uid = keyvalue_uid + "-" + key
        nestedkeyvalue_id = id + "-" + dictkey + "-" + key
        if val is None:
            val = "null"

        implemented_nestedrow_uid = "PSMCodes-" + key

        write_to_file("nested_key_value",
                      nestedkeyvalue_uid, nestedkeyvalue_id, val, implemented_nestedrow_uid, keyvalue_uid)


def generate_objectrelation(relation_list, id, version, key):
    for relation_id in relation_list:
        keyvalue_uid = id + "-" + version + "-" + key
        objectrelation_uid = keyvalue_uid + "-" + relation_id
        relatedobject_uid = relation_id + "-" + version
        objectrelation_id = id + "-" + key + "-" + relation_id

        write_to_file("object_relation", objectrelation_uid, objectrelation_id, keyvalue_uid, relatedobject_uid)


def is_dictionary(ele):
    return type(ele) == type(dict())


def parse_xml_to_json():
    print("addon")
    version = "1.0.0"
    # objecttype -> Offers/Addons/Rewards etc..
    object_type = "Addons"
    value_type = "Addon"
    # print(parser['OfferConfig'][object_type][value_type]) # list of keyvalues
    addon_list = parser['OfferConfig'][object_type][value_type]
    for addon in addon_list:
        addon_id = addon['Id']
        object_uid = addon_id + "-" + version
        implemented_structure_uid = "Post-Addon-1.0.0"
        write_to_file("object", object_uid, addon_id, implemented_structure_uid)
        for key, val in addon.items():
            keyvalue_id = addon_id + "-" + key
            keyvalue_uid = addon_id + "-" + version + "-" + key
            implementedrow_uid = "Post-Addon-"+version + "-" + key
            input_val = "null"

            if is_dictionary(val):
                if '@localized' in val:
                    if val['@localized'] == "false":
                        input_val = val['#text']
                        nestedkeyvalue_uid = keyvalue_uid + "-" + "un"
                        write_to_file("nested_key_value", nestedkeyvalue_uid, keyvalue_uid, "unLocalized")

                    else:
                        generate_multilanguage_nestedkeyvalue(object_type, key, addon_id, version, keyvalue_uid)

                elif 'Refill_id' in val:
                    refill_id_list = val['Refill_id']
                    if type(refill_id_list) is not list:
                        helper_list = []
                        helper_list.append(refill_id_list)
                        refill_id_list = helper_list
                    generate_objectrelation(refill_id_list, addon_id, version, key)


                elif 'Activation' in val:
                    generate_psmcode_nestedkeyvalue(val, keyvalue_uid, key, addon_id)

                else:
                    print("this shouldnt run")

            else:
                if val is not None:
                    input_val = val
            # print(keyvalue_uid, implementedrow_uid, input_val)
            write_to_file("key_value", keyvalue_uid, keyvalue_id, input_val, implementedrow_uid, object_uid)
            gc.collect()




parse_xml_to_json()