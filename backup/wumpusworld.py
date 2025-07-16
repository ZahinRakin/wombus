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

  """
  Create a set of safe spaces, and, using two for loops, go throuh every space.
  If we have safely visited the space, add it to the safe set. If we can resolve
  that the space does not have a wumpus and does not have a pit, add it to the 
  safe set.
  """
  def safe(self):
    safe_set = Set([])
    for i in range(1, self.size + 1):
      for j in range(1, self.size + 1):
        not_pit    = logic.expr("~P%d_%d" % (i,j))
        not_wumpus = logic.expr("~W%d_%d" % (i,j))
        if 'L%d_%d' in self.KB.clauses:
          safe_set.add((i,j))
        elif ((logic_440.resolution(self.KB, not_pit) and logic_440.resolution(self.KB, not_wumpus))):
          safe_set.add((i,j))
    return safe_set

  """
  Create a set of not unsafe spaces, and, using two for loops, go through every space.
  If we can resolve that the space does not contain a wumpus or a pit, add the space
  to the set of not unsafe spaces.
  """
  def not_unsafe(self):
    notunsafe_set = Set([])
    for i in range(1, self.size + 1):
      for j in range(1, self.size + 1):
        pit    = logic.expr("P%d_%d" % (i,j))
        wumpus = logic.expr("W%d_%d" % (i,j))
        if not(((logic_440.resolution(self.KB, pit) or logic_440.resolution(self.KB, wumpus)))):
          notunsafe_set.add((i,j))
    return notunsafe_set

  """
  Create a set of unvisited spaces, and, using two for loops, go through every space.
  If the space does not appear in the KB as having been visited, add the space to
  the set of unvisited spaces.
  """
  def unvisited(self):
    unvisited = Set([])
    for i in range(1, self.size + 1):
      for j in range(1, self.size +1):
        if logic.expr('L%d_%d' % (i,j)) not in self.KB.clauses:
          unvisited.add((i,j))
    return unvisited

NEIGHBOR_DELTAS = ((+1, 0), (-1, 0), (0, +1), (0, -1))

def get_neighbors(x, y, cave_size):
  possible_neighbors = [(x + dx, y + dy) for dx, dy in NEIGHBOR_DELTAS]
  return [(x1, y1) for x1, y1 in possible_neighbors if 
      1 <= x1 <= cave_size and 1 <= y1 <= cave_size]


class World:
  def __init__(self, size, gold, pits, wumpus):
    self.size = size
    self.gold = gold
    self.pits = pits
    self.wumpus = wumpus

  def perceive(self, (x, y), KB):
    print 'You enter room (%d, %d)' % (x, y)
    KB.tell('L%d_%d' % (x, y))

    if (x, y) in self.pits:
      print 'Oh no, you have fallen into a pit!'
      raise logic_440.GameOver(logic_440.RESULT_DEATH)
    else:
      KB.tell('~P%d_%d' % (x, y))

    if (x, y) == self.wumpus:
      print 'Oh no, you have wandered into the Wumpus\' room!'
      raise logic_440.GameOver(logic_440.RESULT_DEATH)
    else:
      KB.tell('~W%d_%d' % (x, y))

    if any((x1, y1) in self.pits for x1, y1 in get_neighbors(x,y, self.size)):
      print 'You feel a breeze'
      KB.tell('B%d_%d' % (x, y))
    else:
      KB.tell('~B%d_%d' % (x, y))

    if any((x1, y1) == self.wumpus for x1, y1 in get_neighbors(x,y, self.size)):
      print 'You smell a stench'
      KB.tell('S%d_%d' % (x, y))
    else:
      KB.tell('~S%d_%d' % (x, y))

    if (x, y) == self.gold:
      print 'You found the gold!'
      raise logic_440.GameOver(logic_440.RESULT_WIN)

def play(world):
  agent = WumpusWorldAgent(world.size)
  location = 1, 1
  try:
    while True:
      world.perceive(location, agent.KB)
      location = agent.choose_location()
  except logic_440.GameOver as e:
    print {logic_440.RESULT_WIN: 'You have won!',
           logic_440.RESULT_DEATH: 'You have died :(',
           logic_440.RESULT_GIVE_UP: 
           'You have left the cave without finding the gold :( '}[e.result]
    print
    print

def main():
  # Play a world with no Wumpus
  play(World(4, (2, 3), ((3, 1), (3, 3), (4, 4)), (-1, -1)))

  # Play a world with a Wumpus
  play(World(4, (2, 3), ((3, 1), (3, 3), (4, 4)), (1, 3)))

  # Feel free to make up additional worlds and see how your agent does at exploring them!

if __name__ == '__main__':
  main()
