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
    file_name = "presql/pre_reward.sql"
    open(file_name, "w").close()
    file_name = "presql/pre_reward_nestedkeyval.sql"
    open(file_name, "w").close()


parser = json.loads(json.dumps(xmltodict.parse(read_data(), process_namespaces=True)))
reset_file()


def write_to_file(table, uid, *args):
    file_name = "presql/pre_reward.sql"

    if table == "nested_key_value":
        file_name = "presql/pre_reward_nestedkeyval.sql"

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
        implemented_nestedrow_uid = "Multi-language-" + lang
        nestedkeyvalue_id = id + "-" + key + "-" + lang
        write_to_file("nested_key_value", nestedkeyvalue_uid, nestedkeyvalue_id, prop_line, implemented_nestedrow_uid,keyvalue_uid)


def is_dictionary(ele):
    return type(ele) == type(dict())


def parse_xml_to_json():
    print("reward")
    version = "1.0.0"
    # objecttype -> Offers/Addons/Rewards etc..
    # object_uid = objectType
    object_type = "Rewards"
    value_type = "Reward"
    # print(parser['OfferConfig'][object_type][value_type]) # list of keyvalues
    reward_list = parser['OfferConfig'][object_type][value_type]
    for reward in reward_list:
        reward_id = reward['Id']
        object_uid = reward_id + "-" + version
        implemented_structure_uid = "Post-Offer-1.0.0"
        write_to_file("object", object_uid, reward_id, implemented_structure_uid)
        for key, val in reward.items():
            keyvalue_uid = reward_id + "-" + version + "-" + key
            keyvalue_id = reward_id + "-" + key
            implementedrow_uid = "Pre-Reward-"+version + "-" + key
            input_val = "null"

            if is_dictionary(val):
                if val['@localized'] == "true":
                    generate_multilanguage_nestedkeyvalue(object_type, key, reward_id, version, keyvalue_uid)
                else:
                    print("this shouldnt run")

            else:
                if val is not None:
                    input_val = val
            # print(keyvalue_uid, implementedrow_uid, input_val)
            write_to_file("key_value", keyvalue_uid,keyvalue_id ,input_val, implementedrow_uid,object_uid)
            gc.collect()





parse_xml_to_json()