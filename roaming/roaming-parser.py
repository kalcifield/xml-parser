import json
import os

import gc
import xmltodict

# add apostrophe to sql

def read_data():
    with open('Roaming_Offers.xml') as file:
        raw_data = file.read()
        file.close()
        return raw_data

def reset_file():
    file_name = "roamingsql/roaming.sql"
    open(file_name, "w").close()
    file_name = "roamingsql/roaming_nestedkeyval.sql"
    open(file_name, "w").close()
    file_name = "roamingsql/roaming_objectrelation.sql"
    open(file_name, "w").close()

parser = json.loads(json.dumps(xmltodict.parse(read_data(), process_namespaces=True)))
reset_file()

def write_to_file(table, uid, *args):
    file_name = "roamingsql/roaming.sql"

    if table == "nested_key_value":
        file_name = "roamingsql/roaming_nestedkeyval.sql"

    if table == "object_relation":
        file_name = "roamingsql/roaming_objectrelation.sql"

    insert_line = "insert into " + table + " VALUES (\'" + uid + "\'"
    for arg in args:
        if arg == "null":
            insert_line += ", null"
        else:
            insert_line += ", \'" + arg + "\'"
    insert_line += "); \n"
    with open(file_name, "a") as file:
        file.write(insert_line)

def is_dictionary(ele):
    return type(ele) == type(dict())

def find_value_in_props_file(language_variable, file_name):
    with open(file_name) as file:
        raw_data = file.readlines()
        file.close()
        for line in raw_data:
            if language_variable in line:
                index_of_equalsign = line.find('=')
                return line[index_of_equalsign + 2:].rstrip()


def generate_multilanguage_nestedkeyvalue(value_type, key, offer_id, keyvalue_uid):
    prop_files = {"eng": "../language_files/Language-offers_hu.properties",
                  "hun": "../language_files/Language-offers_en.properties",
                  "def": "../language_files/Language-offers.properties",
                  "unLocalized": "null"}

    if key == "Warning_text":
        key = "WarningText"

    if key == "Throttling_text":
        key = "ThrottlingText"

    language_variable = "Roaming." + value_type + "." + offer_id + "." + key
    for eng, value in prop_files.items():
        if eng == "unLocalized":
            prop_line = "null"

        else:
            prop_line = find_value_in_props_file(language_variable, value)
            if prop_line is None:
            #             print("nán1")
                language_variable = "Roaming." + value_type + \
                                "." + offer_id + "." + "POST" + "." + key
                prop_line = find_value_in_props_file(language_variable, value)
            if prop_line is None:
            #             print("nán2")
                language_variable = "Roaming." + value_type + \
                                "." + offer_id + "." + "PRE" + "." + key
                prop_line = find_value_in_props_file(language_variable, value)
            if prop_line is None:
                print("nán3, baj van")
                print(language_variable)

        prop_line = prop_line.replace("don't", "don''t")
        nestedkeyvalue_uid = keyvalue_uid + "-" + eng
        nestedkeyvalue_id = offer_id + "-" + key + "-" + eng
        implemented_nestedrow_uid = "Multi-language-" + eng
        write_to_file("nested_key_value", nestedkeyvalue_uid, nestedkeyvalue_id, prop_line, implemented_nestedrow_uid,keyvalue_uid)


def generate_psmcode_nestedkeyvalue(dict_val, keyvalue_uid, dictkey, offer_id):
    for key, val in dict_val.items():
        nestedkeyvalue_uid = keyvalue_uid + "-" + key
        implemented_nestedrow_uid = "PSMCodes-" + key
        nestedkeyvalue_id = offer_id + "-" + dictkey + "-" + key

        write_to_file("nested_key_value",
                      nestedkeyvalue_uid, nestedkeyvalue_id, val, implemented_nestedrow_uid, keyvalue_uid)


def generate_objectrelation(relation_list, offer_id, version, key):
    for relation_id in relation_list:
        keyvalue_uid = offer_id + "-" + version + "-" + key
        objectrelation_uid = keyvalue_uid + "-" + relation_id
        relatedobject_uid = relation_id + "-" + version
        objectrelation_id = offer_id + "-" + key + "-" + relation_id

        write_to_file("object_relation", objectrelation_uid, objectrelation_id, keyvalue_uid, relatedobject_uid)


def parse_xml_to_json():
    print("offer")
    version = "1.0.0"
    value_type = "Offers"

    for offer in parser['OfferConfig']['Offers']['Offer']:
        offer_id = offer['Id']
        object_uid = offer_id + "-" + version
        write_to_file("object", object_uid, offer_id)

        for key in offer.keys():
            keyvalue_id = offer_id + "-" + key
            keyvalue_uid = offer_id + "-" + version + "-" + key
            implementedrow_uid = "Roaming-Offer-" + version + "-" + key
            implemented_structure_uid = "Roaming-Offer-1.0.0"

            value = "null"
            dict_val = offer[key]
            #         print(dict_val)
            if is_dictionary(dict_val):
                if '@localized' in dict_val:
                    if dict_val['@localized'] == "false":
                        print("not gut")
                    else:
                        generate_multilanguage_nestedkeyvalue(value_type, key, offer_id, keyvalue_uid)


                        # unlocalized null / if false -> value between tags

                elif 'Upgrade_offer_id' in dict_val:

                    offer_id_list = dict_val['Upgrade_offer_id']
                    if type(offer_id_list) is not list:
                        helper_list = []
                        helper_list.append(offer_id_list)
                        offer_id_list = helper_list
                    generate_objectrelation(offer_id_list, offer_id, version, key)

                elif 'Activation' in dict_val:
                    generate_psmcode_nestedkeyvalue(dict_val, keyvalue_uid, key, offer_id)



            elif offer[key] is not None:
                value = offer[key]

            write_to_file("key_value", keyvalue_uid,keyvalue_id ,value, implementedrow_uid,object_uid)
            gc.collect()


parse_xml_to_json()