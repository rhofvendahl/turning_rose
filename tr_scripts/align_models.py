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


def main():
    name = MODEL_NAMES[-1]
    dirpath = os.path.abspath(os.path.join("../data/models/obj/reduced_same", name))

    pcd = get_point_cloud(dirpath, name)

    # Works well for final model
    target = [358 / 360.0, 80 / 100.0, 60 / 100.0]
    tolerances = [3 / 360.0, 20 / 100.0, 40 / 100.0]
    pcd_filtered = filter_by_hsv(pcd, target, tolerances)
    o3d.visualization.draw_geometries([pcd_filtered])


if __name__ == "__main__":
    main()
