
import json
import math

def calculate_distance(x, y, features):
    """Calculate distance between two points x and y with the given features."""
    return math.sqrt(sum([(x[feat] - y[feat])**2 for feat in features]))

class Node(object):
    """Node in a k-d-tree."""
    def __init__(self, point, left=None, right=None):
        self.point = point
        self.left = left
        self.right = right

    def flatten(self):
        """Flatten the subtree into an ordinary dictionary."""
        data = {
            'point': self.point,
            'left': None,
            'right': None,
        }
        if self.left is not None:
            data['left'] = self.left.flatten()
        if self.right is not None:
            data['right'] = self.right.flatten()
        return data

    @staticmethod
    def load(data):
        """Reload from an ordinary dictionary and return the tree."""
        if data is not None:
            return Node(point=data['point'], left=Node.load(data['left']),
                        right=Node.load(data['right']))
        return None


def insert(point, node, cd, features):
    """Insert into the kd-tree."""
    if node == None:
        node = Node(point)
    elif point[features[cd]] < node.point[features[cd]]:
        node.left = insert(point, node.left, (cd + 1) % len(features), features)
    else:
        node.right = insert(point, node.right, (cd + 1) % len(features),
                            features)
    return node

class KDTree(object):
    """kd-tree class."""
    def __init__(self, features, points=None, json_file=None):
        """Construct a kd-tree from the points given a list of features."""
        self.features = features
        self.root = None
        if json_file is not None:
            with open(json_file) as fp:
                data = json.load(fp)
            self.root = Node.load(data)
        else:
            for point in points:
                self.root = insert(point, self.root, 0, features)

    def nns(self, point):
        """Do a NN search for this point."""
        cut_dim = 0
        best_dist = math.inf
        best = None
        node = self.root
        features = self.features
        # Traverse down the tree until the pseudo-nearest point is found
        while node is not None:
            dist = calculate_distance(point, node.point, features)
            if dist < best_dist:
                best_dist = dist
                best = node
            if node.point[features[cut_dim]] < point[features[cut_dim]]:
                node = node.left
            else:
                node = node.right
            cut_dim = (cut_dim + 1) % len(self.features)
        return best.point
