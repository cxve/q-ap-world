from Data import shop_data, shop_costs, mail_crystal_rewards, crystal_rewards, corruption_shard_rewards, skill_directory, skill_names
from math import ceil

def calc_req_crystal_num():
    bought = []
    for count_crystals in range(35):
        crystals = sum(crystal_rewards[0:count_crystals])
        crystals += max(0, count_crystals - len(crystal_rewards)) * 100
        crystals += sum(mail_crystal_rewards[0:ceil((count_crystals + 1) / 35 * 10)])
        print(crystals)
        for k, v in shop_costs.items():
            if k in bought: continue
            if "corrupted" in shop_data[k]: continue
            if crystals < v: continue
            bought.append(k)
            print([count_crystals, k, v])
    for k in shop_costs.keys():
        if k in bought: continue
        if "corrupted" in shop_data[k]: continue
        print([35, k])

def calc_req_shard_num():
    bought = []
    for count_shards in range(19):
        print(sum(corruption_shard_rewards[0:count_shards]))
        shards = sum(corruption_shard_rewards[0:count_shards])
        shards += max(0, count_shards - len(corruption_shard_rewards)) * 10
        for k, v in shop_costs.items():
            if k in bought: continue
            if not "corrupted" in shop_data[k]: continue
            if shards * 1.5 <= v: continue
            bought.append(k)
            print([count_shards, k])
    for k in shop_costs.keys():
        if k in bought: continue
        if not "corrupted" in shop_data[k]: continue
        print([35, k])
        
#def transform_tagged_skills():
#    return { key: { "trigger": "", "tags": tagged_skills[key] } for key in tagged_skills }

def get_trigger_ratio():
    for champ, skills in skill_names.items():
        num_on_trigger = 0
        num_auto_trigger = 0
        for skill in skills:
            if skill_directory[skill]["trigger"] == "trigger": num_on_trigger += 1
            elif len(skill_directory[skill]["tags"]) > 0 and skill_directory[skill]["tags"][0] == "trigger":
                num_auto_trigger += 1
        print(f"Champ {champ} has {num_on_trigger} on trigger skills and {num_auto_trigger} auto trigger skills.")
        print(f"    That's {num_on_trigger / num_auto_trigger} on trigger skills for each auto trigger skill!")

calc_req_crystal_num()