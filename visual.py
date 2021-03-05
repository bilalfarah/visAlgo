import maze
import sys

# A script that outputs .avis that visualise the DFS and BFS images
# search algorithms using a maze as in the popular MIT CS50 course.

if len(sys.argv) != 2:
    sys.exit("Usage: python visual.py {file.txt}")

m = maze.Maze(sys.argv[1],'BFS')
m.solve()
m2 = maze.Maze(sys.argv[1], 'DFS')
m2.solve()
print("Done!")
