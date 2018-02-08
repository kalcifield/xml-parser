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
    file_name = "posql/post_offer.sql"
    open(file_name, "w").close()


parser = json.loads(json.dumps(xmltodict.parse(read_data(), process_namespaces=True)))
reset_file()


def write_to_file(table, uid, *args):
    file_name = "posql/post_offer.sql"

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

        nestedkeyvalue_uid = keyvalue_uid + "-" + lang
        # print(prop_line)
        write_to_file("nestedkeyvalue", nestedkeyvalue_uid, keyvalue_uid, prop_line)

def generate_psmcode_nestedkeyvalue(dict_val, keyvalue_uid):
    for key, val in dict_val.items():
        nestedkeyvalue_uid = keyvalue_uid + "-" + key
        if val is None:
            val = "null"
        write_to_file("nestedkeyvalue", nestedkeyvalue_uid, keyvalue_uid, val)

def generate_objectrelation(relation_list, id, version, key):
    for relation_id in relation_list:
        keyvalue_uid = id + "-" + version + "-" + key
        objectrelation_uid = keyvalue_uid + "-" + relation_id
        relatedobject_uid = relation_id + "-" + version

        write_to_file("objectrelation", objectrelation_uid, keyvalue_uid, relatedobject_uid)


def is_dictionary(ele):
    return type(ele) == type(dict())


def parse_xml_to_json():
    print("offer")
    version = "1.0.0"
    # objecttype -> Offers/Addons/Rewards etc..
    object_type = "Offers"
    value_type = "Offer"
    # print(parser['OfferConfig'][object_type][value_type]) # list of keyvalues
    offer_list = parser['OfferConfig'][object_type][value_type]
    for offer in offer_list:
        offer_id = offer['Id']
        object_uid = offer_id + "-" + version
        write_to_file("object", object_uid, offer_id)
        for key, val in offer.items():
            keyvalue_uid = offer_id + "-" + version + "-" + key
            implementedrow_uid = "Post-Offer-"+version + "-" + key
            input_val = "null"

            if is_dictionary(val):
                if '@localized' in val:
                    if val['@localized'] == "false":
                        if '#text' in val:
                            input_val = val['#text']
                            print("we dont like consistency")
                        nestedkeyvalue_uid = keyvalue_uid + "-" + "un"
                        write_to_file("nestedkeyvalue", nestedkeyvalue_uid, keyvalue_uid, "unLocalized")

                    else:
                        generate_multilanguage_nestedkeyvalue(object_type, key, offer_id, version, keyvalue_uid)

                elif 'Upgrade_offer_id' in val:
                    offer_id_list = val['Upgrade_offer_id']
                    if type(offer_id_list) is not list:
                        helper_list = []
                        helper_list.append(offer_id_list)
                        offer_id_list = helper_list
                    generate_objectrelation(offer_id_list, offer_id, version, key)

                elif 'Addon_id' in val:
                    addon_id_list = val['Addon_id']
                    if type(addon_id_list) is not list:
                        helper_list = []
                        helper_list.append(addon_id_list)
                        addon_id_list = helper_list
                    generate_objectrelation(addon_id_list, offer_id, version, key)

                elif 'Pool_id' in val:
                    pool_id_list = val['Pool_id']
                    if type(pool_id_list) is not list:
                        helper_list = []
                        helper_list.append(pool_id_list)
                        pool_id_list = helper_list
                    generate_objectrelation(pool_id_list, offer_id, version, key)


                elif 'Activation' in val:
                    generate_psmcode_nestedkeyvalue(val, keyvalue_uid)

                elif 'UnlimitedContentPackage' in val:
                    unlcontpack_id_list = val['UnlimitedContentPackage']
                    if type(unlcontpack_id_list) is not list:
                        helper_list = []
                        helper_list.append(unlcontpack_id_list)
                        unlcontpack_id_list = helper_list
                    generate_objectrelation(unlcontpack_id_list, offer_id, version, key)

                else:
                    print(val)

            else:
                if val is not None:
                    input_val = val
            # print(keyvalue_uid, implementedrow_uid, input_val)
    #
            write_to_file("keyvalue", keyvalue_uid, object_uid, implementedrow_uid, input_val)
            gc.collect()




parse_xml_to_json()