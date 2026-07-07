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

class ItemPoolProgressiveCrystalsNum(Range):
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

class SanityNumChallenges(Range):
    """
    This setting adds special challenges that reward location checks.
    By default, this will add 4x tier 1 challenges, 3x tier 2 challenges,
    2x tier 3 challenges and 1x tier 4 challenge.
    """
    display_name = "Amount of Challenge Locations"
    range_start = 0
    range_end = 30
    default = 10

class SanityNumChallengesTier4(Range):
    """
    Here you can choose the maximum amount of tier 4 challenges to add.
    Tier 4 challenges only appear if amount of challenge locations is set
    to at least 10.
    """
    display_name = "Maximum amount of Tier 4 Challenges"
    range_start = 0
    range_end = 6
    default = 1

@dataclass
class QUPoptions(PerGameCommonOptions):
    champ: Champ
    itemPoolTotalSkillNum: ItemPoolTotalSkillNum
    #itemPoolSignaturePercent: ItemPoolSignaturePercent
    itemPoolFixedSkillNum: ItemPoolFixedSkillNum

    itemPoolSkillUpgradeNum: ItemPoolSkillUpgradeNum
    #itemPoolCorruptionShardNum: ItemPoolCorruptionShardNum
    itemPoolProgressiveCrystalsNum: ItemPoolProgressiveCrystalsNum
    itemPoolEfficiencyCrystals: ItemPoolEfficiencyCrystals
    #itemPoolEfficiencyCorruptionShards: ItemPoolEfficiencyCorruptionShards
    itemPoolEfficiencyUpgradePoints: ItemPoolEfficiencyUpgradePoints

    sanityNumChallenges: SanityNumChallenges
    sanityNumChallengesTier4: SanityNumChallengesTier4
