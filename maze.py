import sys
import cv2,numpy
from PIL import Image, ImageDraw


class Node():
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action


class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

imgs = []
class Maze():

    def __init__(self, filename,search):
        # track images
        self.images = []

        # search mode
        self.search = search
        # Read file and set height and width of maze
        with open(filename) as f:
            contents = f.read()

        # Validate start and goal
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        # Determine height and width of maze
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Keep track of walls
        self.walls = []
        self.cell_size = 50
        self.cell_border = 2

        # Create a blank canvas
        self.img = Image.new(
            "RGBA",
            (self.width * self.cell_size, self.height * self.cell_size),
            "black"
        )
        draw = ImageDraw.Draw(self.img)
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                        fill = (255, 0, 0)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                        fill = (0, 171, 28)
                    elif contents[i][j] == " ":
                        row.append(False)
                        fill = (237, 240, 252)
                    else:
                        # wall fragment
                        row.append(True)
                        fill = (40, 40, 40)
                    # Draw cell
                    draw.rectangle(
                        ([(j * self.cell_size + self.cell_border, i * self.cell_size + self.cell_border),
                          ((j + 1) * self.cell_size - self.cell_border, (i + 1) * self.cell_size - self.cell_border)]),
                        fill=fill
                    )
                except IndexError:
                    row.append(False)
            self.walls.append(row)
        self.images.append(self.img)
        if self.search == "DFS":
            self.outFileName = 'DFS.avi'
        else:
            self.outFileName = 'BFS.avi'
        self.out = cv2.VideoWriter(
            self.outFileName, cv2.VideoWriter_fourcc(*'DIVX'), 1, self.img.size)
        im = cv2.cvtColor(numpy.asarray(self.img), cv2.COLOR_RGB2BGR)
        self.out.write(im)
        
        self.solution = None


    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()


    # returns a list of valid neighbours to a particular node
    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            # validating the neighbours i.e. not out of scope and not part of the wall
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result

    def solve(self):
        """Finds a solution to maze, if one exists."""

        # Keep track of number of states explored
        self.num_explored = 0

        # Initialize frontier to just the starting position
        start = Node(state=self.start, parent=None, action=None)    
        if(self.search == "DFS"):
            frontier = StackFrontier()
        else:
            frontier = QueueFrontier()
        frontier.add(start)

        # Initialize an empty explored set
        self.explored = set()

        # Keep looping until solution found
        while not frontier.empty():

            # Choose a node from the frontier
            node = frontier.remove()
            self.num_explored += 1

            # If node is the goal, then we have a solution
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                self.drawSolution()
                return

            # Mark node as explored
            self.explored.add(node.state)
            if self.num_explored > 1:
                self.drawExplored(node.state)

            # Add neighbors to frontier
            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)

    def drawExplored(self, state):
        draw = ImageDraw.Draw(self.img)
        i, j = state
        fill = (212, 97, 85)
        # Draw cell
        draw.rectangle(
            ([(j * self.cell_size + self.cell_border, i * self.cell_size + self.cell_border),
              ((j + 1) * self.cell_size - self.cell_border, (i + 1) * self.cell_size - self.cell_border)]),
            fill=fill
        )
        self.images.append(self.img)
        im = cv2.cvtColor(numpy.asarray(self.img), cv2.COLOR_RGB2BGR)
        self.out.write(im)

        

    def drawSolution(self):
        draw = ImageDraw.Draw(self.img)
        for i,j in self.solution[1][:len(self.solution[1])-1]:
            fill = (220, 235, 113)
            draw.rectangle(
                ([(j * self.cell_size + self.cell_border, i * self.cell_size + self.cell_border),
                  ((j + 1) * self.cell_size - self.cell_border, (i + 1) * self.cell_size - self.cell_border)]),
                fill=fill
            )
        self.images.append(self.img)   
        im = cv2.cvtColor(numpy.asarray(self.img), cv2.COLOR_RGB2BGR)
        self.out.write(im)
        self.out.release()
