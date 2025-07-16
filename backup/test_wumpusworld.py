import wumpusworld
import logic
import logic_440
import unittest


class Test(unittest.TestCase):
  def test_background_knowledge(self):
    agent = wumpusworld.WumpusWorldAgent(4)
    agent.KB.tell(logic.expr('B1_1'))
    agent.KB.tell(logic.expr('~P1_2'))
    self.assertTrue(logic_440.resolution(agent.KB, logic.expr('P2_1')))



if __name__ == '__main__':
  unittest.main()
