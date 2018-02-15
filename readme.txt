run: -post/post-parser.py
     -pre/pre-parser.py
     -roaming/roaming-parser.py

concat the sql files with this bash command:
cat post/posql/post_addon.sql post/posql/post_addon_nestedkeyval.sql post/posql/post_offer.sql post/posql/post_offer_nestedkeyval.sql post/posql/post_pool.sql post/posql/post_pool_nestedkeyval.sql post/posql/post_refill.sql post/posql/post_refill_nestedkeyval.sql post/posql/post_unlimitedcontentpackage.sql post/posql/post_unlimitedcontentpackage_nestedkeyval.sql pre/presql/pre_addon.sql pre/presql/pre_addon_nestedkeyval.sql pre/presql/pre_dataquota.sql pre/presql/pre_dataquota_groups.sql pre/presql/pre_dataquota_groups_nestedkeyval.sql pre/presql/pre_dataquota_nestedkeyval.sql pre/presql/pre_freedata_offer.sql pre/presql/pre_freedata_offer_nestedkeyval.sql pre/presql/pre_offer.sql pre/presql/pre_offer_nestedkeyval.sql pre/presql/pre_reward.sql pre/presql/pre_reward_nestedkeyval.sql roaming/roamingsql/roaming.sql roaming/roamingsql/roaming_nestedkeyval.sql roaming/roamingsql/roaming_objectrelation.sql pre/presql/pre_offer_objectrelation.sql post/posql/post_pool_objectrelation.sql post/posql/post_addon_objectrelation.sql post/posql/post_offer_objectrelation.sql > data_loader.sql

then:
    psql -U [username] -d [database] -a -f path/to/data_loader.sql