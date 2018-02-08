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
    file_name = "posql/post_pool.sql"
    open(file_name, "w").close()


parser = json.loads(json.dumps(xmltodict.parse(read_data(), process_namespaces=True)))
reset_file()


def write_to_file(table, uid, *args):
    file_name = "posql/post_pool.sql"

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
    print("pool")
    version = "1.0.0"
    # objecttype -> Offers/Addons/Rewards etc..
    object_type = "Pools"
    value_type = "Pool"
    # print(parser['OfferConfig'][object_type][value_type]) # list of keyvalues
    pool_list = parser['OfferConfig'][object_type][value_type]
    for pool in pool_list:
        pool_id = pool['Id']
        object_uid = pool_id + "-" + version
        write_to_file("object", object_uid, pool_id)
        for key, val in pool.items():
            keyvalue_uid = pool_id + "-" + version + "-" + key
            implementedrow_uid = "Post-Pool-"+version + "-" + key
            input_val = "null"

            if is_dictionary(val):
                if '@localized' in val:
                    if val['@localized'] == "false":
                        print("we dont like consistency")

                    else:
                        generate_multilanguage_nestedkeyvalue(object_type, key, pool_id, version, keyvalue_uid)

                elif 'Addon_id' in val:
                    addon_id_list = val['Addon_id']
                    if type(addon_id_list) is not list:
                        helper_list = []
                        helper_list.append(addon_id_list)
                        addon_id_list = helper_list
                    generate_objectrelation(addon_id_list, pool_id, version, key)

                elif 'Refill_id' in val:
                    refill_id_list = val['Refill_id']
                    if type(refill_id_list) is not list:
                        helper_list = []
                        helper_list.append(refill_id_list)
                        refill_id_list = helper_list
                    generate_objectrelation(refill_id_list, pool_id, version, key)

                elif 'Activation' in val:
                    generate_psmcode_nestedkeyvalue(val, keyvalue_uid)

                elif 'UnlimitedContentPackage' in val:
                    unlcontpack_id_list = val['UnlimitedContentPackage']
                    if type(unlcontpack_id_list) is not list:
                        helper_list = []
                        helper_list.append(unlcontpack_id_list)
                        unlcontpack_id_list = helper_list
                    generate_objectrelation(unlcontpack_id_list, pool_id, version, key)

                else:
                    print(val)

            else:
                if val is not None:
                    input_val = val
            # print(keyvalue_uid, implementedrow_uid, input_val)
            write_to_file("keyvalue", keyvalue_uid, object_uid, implementedrow_uid, input_val)
            gc.collect()



parse_xml_to_json()