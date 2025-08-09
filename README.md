Multi-Agent System for Colony Simulation 

1.Overall Goal of the MAS  
The main goal of this MAS system is to simulate a gamified dynamic competition 
between two ant colonies. The agents within each colony must work collaboratively, 
achieving the goals of each role (Scout, Worker, and Attacker) to efficiently gather food 
from the environment and defend their colony. The game ends once one colony 
manages to eliminate all the ants from the opposing colony. 

2. Features of the MAS 
Role-based Agents  
• Scout Ants: Scans the environment, finds food and creates paths from the food 
back to the nest using pheromones. 
• Worker Ants: Stay near the nest in search for pheromone trails, follow trails to 
collect food, returning it back to the nest. 
• Attacker Ants: Follow Scout ants protecting them, can eliminate enemy colony 
ants when they get to close, changes behaviour when only attackers remain to 
fight.

Pheromone Trails 
• Scout ants leave trails from the food to the nest guiding worker ants. 
• Each colony has its own trails, the trails are removed once food is fully eaten, or 
  the time limit is reached. 
  
Dynamic Agent Behaviour 
• To avoid ants becoming redundant when eliminations occur, ants can adapt their 
roles based on what the colony requires.  
• Agents change behaviour to properly act to different scenarios.  
Colony Growth 
• Colonies can spawn new ants each time they collect six foods. 
• Colonies spawn either new worker ants or attacker ants. 

Environment 
• Food is dynamically positioned around the environment starting with fifteen 
sources. 
• Food will respawn in the environment, ensuring colonies can always find new 
sources. 
• Hazards are randomly placed around the environment, ants must avoid them. 
Display information 
• Game displays real-time updates for the number of food collected, and number 
of each type of ants for both colonies. 

Victory Condition 
• A colony wins once it eliminates all ants from opposing colony, the winning 
colony displays on screen. 

4. Agent-Oriented Design 
Agent Types and Roles: 
The Scout Ant has a vital role in the colony, it efficiently locates food sources leaving 
pheromone trails leading back to the nest for worker ants to follow. Scouts have three 
behavioural states, scanning, traveling, and returning. When in scanning state the entire 
grid is scanned, finding all food sources and hazards, creating lists for further decision 
making. A random food source is selected, and the optimal path is found using the A* 
search algorithm. It then transitions to traveling, following its path to the food. Now at 
the food, state changes to returning state, it deposits its pheromones on each cell it 
visits while returning to the nest.
The A* search algorithm allows effective path navigation using the Manhattan distance 
heuristic and cost-tracking dictionaries. Paths are dynamically recalculated to find new 
food sources and forget old sources. The Scout ants design enhances the colony, 
efficiently producing pheromone trails allowing worker ants to focus on food collection. 
The Worker Ant focus on food collection, its behaviour changes between seeking 
pheromone trails/food and returning to the nest.

• Worker ants move randomly near the nest, waiting for colony specific 
pheromone trails, once found they prioritise moves with pheromone trails 
heading away from the nest, with food collected they head back to the nest to 
deposit it.  

• Worker ants have a time out system making them return to the nest, this helps 
stopping them from getting lost. They also keep track of their last few moves to 
stop them from using recently visited positions. 
The Attack Ant acts as the colonies main defence. When the colony still has scouts and 
workers it focuses on protecting scout ants, following them and keeping a short 
distance, targeting enemy ants that come into range. Once only attack ants remain in 
the colony their behaviour changes, becoming more aggressive and actively seeking out 
enemy colony ants. This uses heuristics to find and eliminate nearby enemy ants. The 
change in behaviour creates an exciting ultimate battle to end the simulation.  

Adaptation & respawning: 
This MAS ensures colony balance and competition by using a dynamic adaptation and 
respawning system. Every time a colony reaches six foods, they can spawn in a new ant, 
this alternates between worker ants and attack ants, balancing resource gathering and 
defence. To continue this balance, adaptation allows ants to change roles. If a colony 
loses all its scout or attack ants, worker ants will be changed to take on these roles, 
ensuring colonies still have a chance to compete. 
Other scenarios have been accounted for as well, colonies with only one scout and one 
attack changes the scout to an attack ant, these two attack ants will both attack the 
other colony in a final effort to claim victory. If no worker ants are alive but a scout ant 
and multiple attacker ants exist, this triggers one attacker ant to change to a worker. 
This ensures resilience and functionality throughout the simulation. 

Environment: 
The environment for the MAS is a dynamic grid, allowing agent interaction with cell 
attributes like food, hazards, and pheromone trails. A nest is placed for each colony at 
opposite sides of the grid, serving as starting points for the agents. 
The food sources are placed randomly across the grid with different amounts of food 
within them. Each time food is collected its number goes down until its removed from 
the grid. When food is removed pheromone connected are removed, checking for 
overlapping trails to not delete still in use trails. Food slowly respawns onto the grid 
allowing the game to continue for longer.  
Hazards are also placed randomly across the grid, apart from the three-by-three safe 
zone around the nests, this was implemented to give ants spawn space and stop 
hazards unfairly affecting gameplay. 
Pheromone trails are managed by the environment enabling pathfinding, they are 
removed by either the food collected function or specific amount of time. This stops the 
grid becoming full of pheromone trails as they are visible. 

6. Proposed Enhancements 
Further Gamification 
As the MAS has prioritised gamification over realism, further user interaction would 
enhance engagement and enjoyment. An example could be implementing the ability to 
change amounts of colonies or types of ants. Another could be ability to control Scout 
Ants, more user interaction overall would create a more entertaining game. 
More Food Types 
Implementing different food types would require changes to the scout ant, adding 
further complexity and new strategies. Examples of new food types could be rare food 
being less likely to spawn and spawns further from nests but is more valuable, adding 
two foods for each collection. Another example is decaying special food that loses its 
value over time but the collection of this food speeds up all ants in the colony. These 
additions would add varied gameplay.  
Graphical Improvements 
Enhancing the visuals MAS system would improve the viewing experience. This could be 
done by adding textures for each of the visual components and adding animations for 
ant movement and combat. These improvements would make the simulation more 
visually engaging.

8. Challenges and Achievements 
Challenges 
Implementing the worker ant logic allowing them to reliably follow pheromone trails to 
the food source presented a significant challenge. As they would reverse direction or get 
stuck especially by intersecting trails. Fixing their behaviour required debugging and 
many adjustments ensuring they effectively use pheromone trails. 
Implementing the pheromone trails system, especially converting it to work for multiple 
colonies, proved to be another challenge. Originally using a decay system that faced too 
many issues, with worker ants struggling to follow it effectively. Managing different 
colonies interaction with the pheromone trails required debugging and system testing. 
Achievements

Successfully implementing dynamic role changing, allowing ants to fill other roles in 
their colony to allow for seamless continuation of gameplay. While this took time to test 
and manage edge cases, the resulting mechanics created an effective and engaging 
system. 
Incorporating the A* search algorithm into the scouts ants behaviour greatly enhanced 
the scout ants ability to find food and create pheromone trails. This improvement made 
the entire colony more effective and added further strategic depth to the simulation.  

Conclusion 
This multi-agent system demonstrates how agent-based simulations can be used to 
model complex behaviour and communication. This gamified implementation 
successfully shows two colonies competing in a dynamic environment using 
collaborative agents fulfilling their own important roles of scouting, working and 
attacking. 
