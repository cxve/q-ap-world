from BaseClasses import Location
from worlds.q_up.Data import features

# apparently, can be any number greater than 0
base_id = 1_000_000


class QUPlocation(Location):
    game: str = "Q-UP"


ranks = ["Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster", "Anomaly", "Improbability",
         "Exploiter", "CHEATER"]

rank_locations = ["Bronze 2", "Bronze 3", "Bronze 4", "Bronze 5"] + [rank + " " + str(i + 1) for rank in ranks for i in
                                                                     range(5)] + ["Novice"]

rank_location_ids = {location: i + base_id for i, location in enumerate(rank_locations)}

level_locations = ["Level " + str(i + 2) for i in range(49)]

level_location_ids = {location: i + 100 + base_id for i, location in enumerate(level_locations)}

feature_location_ids = {location: i + 200 + base_id for i, location in enumerate(features)}

build_challenge_location = lambda tier, amount: ["Tier " + str(tier) + " Challenge " + str(i + 1) for i in range(
    amount)]

build_challenge_location_ids = lambda tier, amount: \
    { location: i + 300 + 10 * (tier - 1) + base_id for i, location in enumerate(build_challenge_location(tier, amount)) }

all_locations = level_locations + rank_locations + features

all_location_ids = {**rank_location_ids, **level_location_ids, **feature_location_ids,
                    **build_challenge_location_ids(1,10),**build_challenge_location_ids(2,10),
                    **build_challenge_location_ids(3,10), **build_challenge_location_ids(4,10)}