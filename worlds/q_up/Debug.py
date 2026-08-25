from Data import shop_data, shop_costs, mail_crystal_rewards, crystal_rewards, corruption_shard_rewards
from math import ceil

def calc_req_crystal_num():
    bought = []
    for count_crystals in range(35):
        print(sum(crystal_rewards[0:count_crystals]))
        crystals = sum(crystal_rewards[0:count_crystals])
        crystals += max(0, count_crystals - len(crystal_rewards)) * 100
        crystals += sum(mail_crystal_rewards[0:ceil((count_crystals + 1) / 35 * 10)])
        for k, v in shop_costs.items():
            if k in bought: continue
            if "corrupted" in shop_data[k]: continue
            if crystals * 2 <= v: continue
            bought.append(k)
            print([count_crystals, k])
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
        
calc_req_shard_num()