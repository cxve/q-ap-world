from Options import OptionGroup
from dataclasses import dataclass

from Options import Choice, Range, DefaultOnToggle, PerGameCommonOptions


class Champ(Choice):
    """
    Choose the champion you want to play as, or randomize this option.
    """
    display_name = "Champ"
    option_gambler = 0
    option_medic = 1
    option_pro = 2
    option_troll = 3
    option_streamer = 4
    option_whale = 5
    option_robot = 6
    option_wizard = 7
    default = "random"

class Goal(Choice):
    """
    Choose which rank must be reached in order to goal.

    Novice: Complete the game, which requires 55 rank ups.
    Fifty: Reach CHEATER 1, which requires 50 rank ups.
    Anomaly: Reach Act 2, which requires 35 rank ups.
    Master: Reach Master 1, which requires 25 rank ups.
    """
    display_name = "Goal Condition"
    option_novice = 55
    option_fifty = 50
    option_anomaly = 35
    option_master = 25
    default = 55

class AutoFixYAML(Choice):
    """
    Choose what the randomizer should do, if your YAML introduces more
    progression items than locations.

    **Adjust Efficiency** will reduce the number of item drops by increasing
    the contents of each drop. For example, instead of receiving one upgrade
    point twice, you receive two upgrade points once. (Recommended!)
    **Fail Generation** will disable YAML fixing. If your YAML has too many
    progression items, generating a multiworld is going to always fail.
    """
    option_prefer_adjusting_efficiency = 1
    option_prefer_failing_generation = 0
    default = 1

class ItemPoolTotalSkillNum(Range):
    """
    Set the maximum amount of skills you want to find in total.
    This amount includes the amount of signature and upgradable skills.
    Defaults to 35, which is the vanilla amount.

    To avoid fill errors, the generator may decide to lower this number automatically.
    """
    display_name = "Total Number of Skills"
    range_start = 20
    range_end = 50
    default = 35

class ItemPoolSkillUpgradeNum(Range):
    """
    Set the number of skill upgrades in the item pool.
    These are used to upgrade fixed skills.
    Defaults to 35, which is the vanilla amount.

    You can calculate the recommended amount like this:
    3 * (number of fixed skills)

    To avoid fill errors, the generator may decide to lower this number automatically.

    The generator will cap this number at 6 * (number of fixed skills).
    """
    display_name = "Maximum Number of Skill Upgrades"
    range_start = 0
    range_end = 50
    default = 35

class ItemPoolFixedSkillNum(Range):
    """
    Set the number of fixed, upgradable skills.
    Defaults to 12, which is the vanilla amount.
    """
    display_name = "Maximum Number of Fixed Skills"
    range_start = 0
    range_end = 18
    default = 12

class ItemPoolHypernodeNum(Range):
    """
    Hypernodes are unique powerful nodes purchasable in the item shop.
    In vanilla, they are unlocked by reaching Novice with a champ.
    """
    display_name = "Number of Hypernode items"
    range_start = 0
    range_end = 8
    default = 3

class ItemPoolCrystalNum(Range):
    """
    Crystals are usually a major part of the game's progression,
    but they also take up a high number of possible locations.

    Here you can set a minimum amount of Crystals to be included
    in the item pool. Crystals can still appear as filler item,
    regardless of this setting.
    """
    display_name = "Minimum amount of Crystals to include"
    range_start = 20
    range_end = 50
    default = 35

class ItemPoolEfficiencyCrystals(Range):
    """
    This setting increases the amount of crystals you receive at once.
    In turn, it reduces the amount of crystals drops in the item pool.
    For example, when set to 2, it will give twice as many crystals at
    once and reduce the number of crystals in the item pool by half (1/2).

    To avoid fill errors, it is recommended to set this to at least 2.
    """
    display_name = "Crystal Item Efficiency"
    range_start = 1
    range_end = 4
    default = 2

class ItemPoolCorruptionShardNum(Range):
    """
    Corruption Shards are part of the game's act 2 progression,
    but they also take up a high number of possible locations.

    Here you can set a minimum amount of Corruption Shards to be included
    in the item pool. Corruption Shards can still appear as filler item,
    regardless of this setting.

    The vanilla amount of corruption shard drops is 19, but since
    corruption shards can also drop as filler items the default
    amount was decreased to 10.
    """
    display_name = "Minimum amount of Corruption Shards to include"
    range_start = 0
    range_end = 20
    default = 10

class ItemPoolEfficiencyCorruptionShards(Range):
    """
    This setting increases the amount of Corruption Shards you receive at once.
    In turn, it reduces the amount of Corruption Shard drops in the item pool.
    For example, when set to 2, it will give twice as many shards at
    once and reduce the number of shards in the item pool by half (1/2).

    To avoid fill errors, it is recommended to set this to at least 2.
    """
    display_name = "Corruption Shard Item Efficiency"
    range_start = 1
    range_end = 4
    default = 2

class ItemPoolEfficiencyUpgradePoints(Range):
    """
    This setting increases the amount of upgrade points you receive at once.
    In turn, it reduces the amount of upgrade points drops in the item pool.
    For example, when set to 2, it will give twice as many upgrade points at
    once and reduce the number of upgrade points in the item pool by half (1/2).

    To avoid fill errors, it is recommended to set this to at least 2.
    """
    display_name = "Upgrade Point Efficiency"
    range_start = 1
    range_end = 4
    default = 2

class SkillDistGates(Choice):
    """
    Decide when the randomizer will enforce skill type distribution settings.
    By default, the randomizer will make sure your in-logic inventory will match
    the distribution settings once every 10 levels. Lower values result in more
    linear progression while higher values cause a more unpredictable distribution.

    "Never" means skill type distribution will be entirely random and the settings below will be ignored.
    """
    display_name = "Number of Skill Distribution Gates"
    option_never = -1
    option_after_50_levels = 1
    option_every_25_levels = 2
    option_every_10_levels = 5
    option_every_5_levels = 10
    default = 5

class SkillDistQFlat(Range):
    """
    Set how many skills should be of type "Flat Q".
    Higher values = more skills of that type, lower values = fewer skills of that type.
    Based on the game's default skill distribution, the recommended value is 8.
    """
    display_name = "Skill Weight: Flat Q"
    range_start = 5
    range_end = 15
    default = 8

class SkillDistQMult(Range):
    """
    Set how many skills should be of type "Q Mult".
    Higher values = more skills of that type, lower values = fewer skills of that type.
    Based on the game's default skill distribution, the recommended value is 7 or 8.
    """
    display_name = "Skill Weight: Q Mult"
    range_start = 5
    range_end = 15
    default = 7

class SkillDistTrigger(Range):
    """
    Set how many skills should be of type "Trigger".
    Higher values = more skills of that type, lower values = fewer skills of that type.
    Based on the game's default skill distribution, the recommended value is 10.
    """
    display_name = "Skill Weight: Trigger"
    range_start = 5
    range_end = 15
    default = 10

class SkillDistGold(Range):
    """
    Set how many skills should be of type "Gold".
    Higher values = more skills of that type, lower values = fewer skills of that type.
    Based on the game's default skill distribution, the recommended value is 2.
    """
    display_name = "Skill Weight: Gold"
    range_start = 0
    range_end = 5
    default = 2

class SkillDistXP(Range):
    """
    Set how many skills should be of type "XP".
    Higher values = more skills of that type, lower values = fewer skills of that type.
    Based on the game's default skill distribution, the recommended value is 2.
    """
    display_name = "Skill Weight: XP"
    range_start = 0
    range_end = 5
    default = 2

class SkillDistOther(Range):
    """
    Set how many skills should be of other types not listed above.
    Higher values = more skills of that type, lower values = fewer skills of that type.
    Based on the game's default skill distribution, the recommended value is 6.
    """
    display_name = "Skill Weight: Other"
    range_start = 0
    range_end = 15
    default = 6

class SkillDistSignature(Range):
    """
    Most champion have special skills that can only be used in combination with their gimmick.
    For example: Luke's Action Junky requires his Tiltmeter gimmick to work.
    This setting forces some of your skills to be signature skills, making sure your gimmick is not useless.
    """
    display_name = "Maximum Percentage of Signature Skills"
    range_start = 0
    range_end = 50
    default = 25

class SanityNumChallenges(Range):
    """
    This setting adds special challenges that reward location checks.
    By default, this will add 4x tier 1 challenges, 3x tier 2 challenges,
    2x tier 3 challenges and 1x tier 4 challenge.
    """
    display_name = "Amount of Challenge Locations"
    range_start = 0
    range_end = 27
    default = 10

class SanityNumChallengesTier4(Range):
    """
    Here you can choose the maximum amount of tier 4 challenges to add.
    Tier 4 challenges only appear if amount of challenge locations is set
    to at least 10.
    """
    display_name = "Maximum amount of Tier 4 Challenges"
    range_start = 0
    range_end = 5
    default = 1

@dataclass
class QUPoptions(PerGameCommonOptions):
    champ: Champ
    itemPoolTotalSkillNum: ItemPoolTotalSkillNum
    #itemPoolSignaturePercent: ItemPoolSignaturePercent
    itemPoolFixedSkillNum: ItemPoolFixedSkillNum
    itemPoolHypernodeNum: ItemPoolHypernodeNum

    itemPoolSkillUpgradeNum: ItemPoolSkillUpgradeNum
    itemPoolCorruptionShardNum: ItemPoolCorruptionShardNum
    itemPoolCrystalNum: ItemPoolCrystalNum
    itemPoolEfficiencyCrystals: ItemPoolEfficiencyCrystals
    itemPoolEfficiencyCorruptionShards: ItemPoolEfficiencyCorruptionShards
    itemPoolEfficiencyUpgradePoints: ItemPoolEfficiencyUpgradePoints

    skillDistGates: SkillDistGates
    skillDistQFlat: SkillDistQFlat
    skillDistQMult: SkillDistQMult
    skillDistTrigger: SkillDistTrigger
    skillDistGold: SkillDistGold
    skillDistXP: SkillDistXP
    skillDistOther: SkillDistOther
    skillDistSignature: SkillDistSignature

    sanityNumChallenges: SanityNumChallenges
    sanityNumChallengesTier4: SanityNumChallengesTier4
    fixStrategy: AutoFixYAML
    goal: Goal

option_groups = [
        OptionGroup("Item Pool", [
            ItemPoolTotalSkillNum,
            ItemPoolFixedSkillNum,
            ItemPoolSkillUpgradeNum,
            ItemPoolCrystalNum,
            ItemPoolCorruptionShardNum,
            ItemPoolEfficiencyUpgradePoints,
            ItemPoolEfficiencyCrystals,
            ItemPoolEfficiencyCorruptionShards
        ]),
        OptionGroup("Item Distribution", [
            SkillDistGates,
            SkillDistSignature,
            SkillDistQFlat,
            SkillDistQMult,
            SkillDistTrigger,
            SkillDistGold,
            SkillDistXP,
            SkillDistOther
        ]),
        OptionGroup("Sanity", [
           SanityNumChallenges,
           SanityNumChallengesTier4,
        ])
    ]