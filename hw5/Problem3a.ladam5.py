from math import sqrt
from random import randint

center_1 = (0, 3)
center_2 = (6, 4)
cluster_1 = set()
cluster_2 = set()

def distance(a, b):
    dist = sqrt( (a[0]-b[0])**2 + (a[1] - b[1])**2 )
    return dist

def calculate_cluster_mean(cluster):
    x1_sum = 0
    x2_sum = 0
    num_points = len(cluster)
    for point in cluster:
        x1_sum = point[0] + x1_sum
        x2_sum = point[1] + x2_sum

    return x1_sum/num_points, x2_sum/num_points

def set_clusters(first_cluster, second_cluster, first_center, second_center):
    for point in data:
        first_distance = distance(point, first_center)
        second_distance = distance(point, second_center)
        if first_distance < second_distance:
            first_cluster.add(point)
        elif first_distance > second_distance:
            second_cluster.add(point)
        else:
            num = randint(0, 1)
            if num == 0:
                first_cluster.add(point)
            else:
                second_cluster.add(point)

data = []
with open('data.txt', 'r') as f:
    for line in f:
        line = line.strip()
        vals = line.split(' ')
        data.append((int(vals[0]), int(vals[1])))

set_clusters(cluster_1, cluster_2, center_1, center_2)
next_cluster_1 = set()
next_cluster_2 = set()
diff = next_cluster_1 ^ cluster_1
while len(diff) > 0:
    prev_cluster_1_mean = calculate_cluster_mean(cluster_1)
    prev_cluster_2_mean = calculate_cluster_mean(cluster_2)
    set_clusters(next_cluster_1, next_cluster_2, prev_cluster_1_mean, prev_cluster_2_mean)
    diff = next_cluster_1 ^ cluster_1
    cluster_1 = next_cluster_1
    cluster_2 = next_cluster_2
    next_cluster_1 = set()
    next_cluster_2 = set()

print('Cluster 1:')
for point in cluster_1:
    print(point)
    
print('\nCluster 2: ')
for point in cluster_2:
    print(point)
