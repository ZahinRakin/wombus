"""
Jacob Davidson
CS440 - Eric Breck
wumpusworld.py

This module implements an logical agent and a world for it to explore.
"""
import logic
import logic_440
from sets import Set

class WumpusWorldAgent(logic_440.KnowledgeBasedAgent):

  """
  Use two for loops to cycle through each of the squares on the board.
  Then, acquire a set of neighboring spaces using the get_neighbors 
  function provided. From here, we use another for loop to cycle through
  each neighbor, and make two expressions that we will feed to the 
  knowledge base. These expressions are co-implications that give the KB
  the knowledge that the squares adjacent to a pit have a breeze/one of
  the adjacent squares to a breeze has a pit and that the squares adjacent 
  to a wumpus have a stench/one of the adjacent squares to a stench has a 
  wumpus. The goal here is to give the KB the minimum amount of information
  necessary, while still providing enough so that it can resolve any
  information that it needs to obtain.
  """
  def __init__(self, cave_size):
    self.KB = logic.PropKB()
    self.size = cave_size
    for i in range(1, cave_size + 1):
      for j in range(1, cave_size + 1):
        neighbors = get_neighbors(i, j, cave_size)
        exp1 = 'B%d_%d <=> (' % (i,j)
        exp2 = 'S%d_%d <=> (' % (i,j)
        for k in range(len(neighbors)):
          if k == len(neighbors) - 1:
            exp1 += ' P%d_%d)' % neighbors[k]
            exp2 += ' W%d_%d)' % neighbors[k]
          else:
            exp1 += ' P%d_%d |' % neighbors[k]
            exp2 += ' W%d_%d |' % neighbors[k]
        self.KB.tell(logic.expr(exp1))
        self.KB.tell(logic.expr(exp2))

 