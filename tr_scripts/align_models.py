import os

import colorsys

import numpy as np
import open3d as o3d
from PIL import Image

from matplotlib import colors

MODEL_NAMES = [
    "2023-07-19_19",
    "2023-07-20_01",
    "2023-07-20_07",
    "2023-07-20_13_final",
]


# NOTE: There's a discrepancy bn o3d and raw where o3d has 4 fewer vertices. Also o3d doesn't do uv well. So, raw it is.
def get_point_cloud(dirpath: str, name: str):
    with open(os.path.join(dirpath, name + ".obj"), "r") as f:
        lines = f.readlines()

    # Get vertex and uv info from obj
    vertices = []
    uvs = []
    for line in lines:
        if line.startswith("v "):
            vertex = [float(val) for val in line.split()[1:4]]
            vertices.append(np.array(vertex))
        if line.startswith("vt "):
            uv = [float(val) for val in line.split()[1:3]]
            uvs.append(np.array(uv))

    vertex_uvs = [None] * len(vertices)
    for line in lines:
        if line.startswith("f "):
            face_vertices = [
                [int(val) for val in vertex.split("/")] for vertex in line.split()[1:4]
            ]
            for face_vertex in face_vertices:
                vertex_idx = face_vertex[0] - 1
                uv_idx = face_vertex[1] - 1
                vertex_uvs[vertex_idx] = uvs[uv_idx]

    # Get rbg values
    img = Image.open(os.path.join(dirpath, "texgen_2.jpg"))
    img_width, img_height = img.size
    img_data = np.array(img)
    colors = []
    black = np.array([0.0, 0.0, 0.0])
    for i, _ in enumerate(vertices):
        uv = vertex_uvs[i]
        if uv is None:
            colors.append(black)
            continue
        x = int(uv[0] * (img_width - 1))
        y = int((1 - uv[1]) * (img_height - 1))
        color = img_data[y, x] / 255.0  # normalize to [0, 1]
        colors.append(color)

    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(np.array(vertices))
    point_cloud.colors = o3d.utility.Vector3dVector(np.array(colors))

    return point_cloud


# For the obj converted from photocatch usdz into obj in blender, when filtered just to the ball, dims are:
# X Range :  0.07380700000000001
# Y Range :  0.040082000000000007
# Z Range :  0.07491
def print_dimensions(pcd):
    # Convert point cloud to numpy array
    point_cloud_np = np.asarray(pcd.points)

    # Get min, max of x, y, z
    min_x, min_y, min_z = np.min(point_cloud_np, axis=0)
    max_x, max_y, max_z = np.max(point_cloud_np, axis=0)

    # Print the ranges
    print("X Range : ", max_x - min_x)
    print("Y Range : ", max_y - min_y)
    print("Z Range : ", max_z - min_z)


def lop_top(pcd, take_ratio):
    # Convert point cloud to numpy array
    pcd_np = np.asarray(pcd.points)

    # Calculate the minimum and maximum x values
    min_y = np.min(pcd_np[:, 1])
    max_y = np.max(pcd_np[:, 1])

    # Calculate one third of the x range
    y_take = (max_y - min_y) * take_ratio

    # Remove the top two thirds of the point cloud
    lopped_indices = np.where(pcd_np[:, 1] <= (max_y - y_take))
    print("INDICIES", len(lopped_indices), lopped_indices)

    # Create a new point cloud with the filtered points
    lopped_pcd = o3d.geometry.PointCloud()
    lopped_pcd.points = o3d.utility.Vector3dVector(pcd_np[lopped_indices])
    lopped_pcd.colors = o3d.utility.Vector3dVector(
        np.asarray(pcd.colors)[lopped_indices]
    )
    return lopped_pcd


def lop(pcd, from_top, from_bottom=0.0):
    # Convert point cloud to numpy array
    pcd_np = np.asarray(pcd.points)

    # Calculate the minimum and maximum x values
    min_y = np.min(pcd_np[:, 1])
    max_y = np.max(pcd_np[:, 1])
    print("Y RANGE", max_y - min_y)

    # Calculate how much to take
    y_take_top = (max_y - min_y) * from_top
    y_take_bottom = (max_y - min_y) * from_bottom

    # Remove the top two thirds of the point cloud
    lopped_indices = np.where(
        np.logical_and(
            pcd_np[:, 1] <= (max_y - y_take_top,),
            pcd_np[:, 1] >= (min_y + y_take_bottom),
        )
    )
    print("INDICIES", len(lopped_indices), lopped_indices)

    # Create a new point cloud with the filtered points
    lopped_pcd = o3d.geometry.PointCloud()
    lopped_pcd.points = o3d.utility.Vector3dVector(pcd_np[lopped_indices])
    lopped_pcd.colors = o3d.utility.Vector3dVector(
        np.asarray(pcd.colors)[lopped_indices]
    )
    return lopped_pcd


def check_hue(hue, target, tolerance):
    # Hue wraps around, i.e. 0 and 360 are the same shade of red
    bound_1 = (target - tolerance) % 1.0
    bound_2 = (target + tolerance) % 1.0
    # This makes it a bit tricky to tell whether a hue is within these bounds, as one bound may have wrapped around
    if bound_1 <= bound_2:
        within_bounds = bound_1 <= hue <= bound_2
    else:
        within_bounds = hue >= bound_1 or hue <= bound_2
    return within_bounds


def filter_by_hsv(pcd, target, tolerances):
    # Convert point cloud colors to np array
    rgb_colors = np.asarray(pcd.colors)

    # Convert RGB to HSV
    hsv_colors = colors.rgb_to_hsv(rgb_colors)

    # Filter the points
    filtered_points = []
    filtered_colors = []
    for i, hsv_color in enumerate(hsv_colors):
        hue_match = check_hue(hsv_color[0], target[0], tolerances[0])
        # Saturation is straightforward
        saturation_match = (
            target[1] - tolerances[1] <= hsv_color[1] <= target[1] + tolerances[1]
        )
        # Value is straightforward
        value_match = (
            target[2] - tolerances[2] <= hsv_color[2] <= target[2] + tolerances[2]
        )

        if hue_match and saturation_match and value_match:
            filtered_points.append(pcd.points[i])
            filtered_colors.append(pcd.colors[i])

    # Create a new point cloud with the filtered points
    filtered_pc = o3d.geometry.PointCloud()
    filtered_pc.points = o3d.utility.Vector3dVector(filtered_points)
    filtered_pc.colors = o3d.utility.Vector3dVector(filtered_colors)

    return filtered_pc


def remove_outliers(pcd, neighbors):
    # Relative redius calculation not possible with lop, unfortunately
    # # Get y range
    # pcd_np = np.asarray(pcd.points)
    # min_y = np.min(pcd_np[:, 1])
    # max_y = np.max(pcd_np[:, 1])

    # # Ball has diameter of roughly .074 in a model of height ~1.17
    # # In this system a reasonable radius would be .06, so calculate that equivalent (in case model size changes)
    # radius = (max_y - min_y) * 0.05

    # Second return value is a point cloud containing removed values
    # cleaned, _ = pcd.remove_statistical_outlier(nb_neighbors=6, std_ratio=2.0)
    cleaned, _ = pcd.remove_radius_outlier(nb_points=neighbors, radius=0.075)
    return cleaned


def get_red(pcd):
    # Red is do-able without lop, but lop allows safe inclusion of more points.

    # Good without lop:
    # target = [359 / 360.0, 70 / 100.0, 60 / 100.0]
    # tolerances = [4 / 360.0, 30 / 100.0, 40 / 100.0]

    # Better with lop:
    target = [360 / 360.0, 70 / 100.0, 60 / 100.0]
    tolerances = [5 / 360.0, 30 / 100.0, 40 / 100.0]

    red_pcd = filter_by_hsv(pcd, target, tolerances)
    return red_pcd


def get_blue(pcd):
    # Blue is super easy, and works with or without lop
    target = [210 / 360.0, 70 / 100.0, 60 / 100.0]
    tolerances = [30 / 360.0, 30 / 100.0, 40 / 100.0]

    return filter_by_hsv(pcd, target, tolerances)


def get_yellow(pcd):
    # Yellow pretty finicky, the color of the ball is shared by a lot of ground and leaf points.
    # Isolating the ball at all relies heavily on lop to remove ground and plant
    target = [45 / 360.0, 55 / 100.0, 65 / 100.0]
    tolerances = [15 / 360.0, 45 / 100.0, 35 / 100.0]

    return filter_by_hsv(pcd, target, tolerances)


# Color must be one of "red", "blue", "yellow"
def get_ball_pcd(name, dirpath, color: str):
    # Second return value is a point cloud containing removed values
    pcd = get_point_cloud(dirpath, name)
    print("CLOUD", pcd)

    # A narrow range, but in the (few) models I've tested this isolates the balls quite nicely!
    # Kinda important cause soil color blends in with darker points of yellow ball otherwise
    # Only caveat being that I suspect some models will have depressions in soil throwing things off - ah well
    pcd = lop(pcd, 0.8, 0.1)
    print("CLOUD LOPPED", pcd)

    if color == "red":
        pcd = get_red(pcd)
    elif color == "blue":
        pcd = get_blue(pcd)
    elif color == "yellow":
        pcd = get_yellow(pcd)
    print("CLOUD FILTERED", color, pcd)

    pcd = remove_outliers(pcd, 15)
    print("CLOUD CLEANED", pcd)

    return pcd


def get_center(pcd):
    points = np.asarray(pcd.points)
    center = points.mean(axis=0)
    return center


def main():
    name = MODEL_NAMES[-1]
    dirpath = os.path.abspath(os.path.join("../data/models/obj/reduced_same", name))

    red = get_ball_pcd(name, dirpath, "red")
    blue = get_ball_pcd(name, dirpath, "blue")
    yellow = get_ball_pcd(name, dirpath, "yellow")
    o3d.visualization.draw_geometries([red, blue, yellow])


if __name__ == "__main__":
    main()
