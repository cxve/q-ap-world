from test.bases import WorldTestBase
from ..Options import QUPoptions

class QUPtestBase(WorldTestBase):
    game = "Q-UP"
    options = {
        "itemPoolTotalSkillNum": 35,
        "itemPoolFixedSkillNum": 12
    }