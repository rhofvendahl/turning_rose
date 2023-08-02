import os

import numpy as np
import open3d as o3d
from PIL import Image
from scipy.optimize import least_squares
from matplotlib import colors as plt_colors

from constants import INTERMEDIATE_OUTPUTS_DIRPATH, OBJ_FILENAME, TEXTURE_FILENAME
from utils import get_names


# o3d.read_triangle_mesh doesn't grab colors
def get_point_cloud(dirpath):
    with open(os.path.join(dirpath, OBJ_FILENAME), "r") as f:
        lines = f.readlines()
    # Get vertex and uv info from obj
    vertices = []
    uvs = []
    for line in lines:
        # There's a weird section after the watermark. process_obj removes it, but best not to rely on that.
        if line.startswith("o watermark"):
            break
        if line.startswith("v "):
            vertex = [float(val) for val in line.split()[1:4]]
            vertices.append(np.array(vertex))
        if line.startswith("vt "):
            uv = [float(val) for val in line.split()[1:3]]
            uvs.append(np.array(uv))
    vertex_uvs = [None] * len(vertices)
    for line in lines:
        if line.startswith("o watermark"):
            break
        if line.startswith("f "):
            face_vertices = [
                [int(val) for val in vertex.split("/")] for vertex in line.split()[1:4]
            ]
            for face_vertex in face_vertices:
                vertex_idx = face_vertex[0] - 1
                uv_idx = face_vertex[1] - 1
                vertex_uvs[vertex_idx] = uvs[uv_idx]

    # Get rbg values
    img = Image.open(os.path.join(dirpath, TEXTURE_FILENAME))
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


# Previously this was done as relative to model height, but I'd forgotten that early plants were shorter!
# My only concern I think is cases where the soil might be mysteriously low? which I think there are a few maybe.
# If need be I guess could do a think where we get blue & work with that as a reference for where the balls are.
# def lop(pcd, lower_offset=0.115, upper_offset=0.228):
def lop(pcd, lower_offset=0.11, upper_offset=0.24):
    pcd_np = np.asarray(pcd.points)

    floor = np.min(pcd_np[:, 1])
    lower_bound = floor + lower_offset
    upper_bound = floor + upper_offset

    remaining_indices = np.where(
        np.logical_and(pcd_np[:, 1] <= upper_bound, pcd_np[:, 1] >= lower_bound)
    )

    remaining_pcd = o3d.geometry.PointCloud()
    remaining_pcd.points = o3d.utility.Vector3dVector(pcd_np[remaining_indices])
    remaining_pcd.colors = o3d.utility.Vector3dVector(
        np.asarray(pcd.colors)[remaining_indices]
    )
    return remaining_pcd


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
    hsv_colors = plt_colors.rgb_to_hsv(rgb_colors)

    # Filter the points
    remaining_points = []
    remaining_colors = []
    for i, hsv_color in enumerate(hsv_colors):
        hue_match = target[0] == None or check_hue(
            hsv_color[0], target[0], tolerances[0]
        )
        # Saturation is straightforward
        saturation_match = target[1] == None or (
            target[1] - tolerances[1] <= hsv_color[1] <= target[1] + tolerances[1]
        )
        # Value is straightforward
        value_match = target[2] == None or (
            target[2] - tolerances[2] <= hsv_color[2] <= target[2] + tolerances[2]
        )

        if hue_match and saturation_match and value_match:
            remaining_points.append(pcd.points[i])
            remaining_colors.append(pcd.colors[i])

    # Create a new point cloud with the remaining points (i.e. near target)
    remaining_pcd = o3d.geometry.PointCloud()
    remaining_pcd.points = o3d.utility.Vector3dVector(remaining_points)
    remaining_pcd.colors = o3d.utility.Vector3dVector(remaining_colors)

    return remaining_pcd


def remove_outliers(pcd, neighbors, radius):
    # Tempting alternative:
    # cleaned, _ = pcd.remove_statistical_outlier(nb_neighbors=6, std_ratio=2.0)

    # Second return value is a point cloud containing removed values
    cleaned, _ = pcd.remove_radius_outlier(nb_points=neighbors, radius=radius)
    return cleaned


def filter_red(pcd):
    # Red is do-able without lop, but lop allows safe inclusion of more points.
    target = [360 / 360.0, 70 / 100.0, 60 / 100.0]
    tolerances = [5 / 360.0, 30 / 100.0, 40 / 100.0]

    red_pcd = filter_by_hsv(pcd, target, tolerances)
    return red_pcd


def filter_blue(pcd):
    # Blue is super easy, and works with or without lop
    target = [210 / 360.0, 70 / 100.0, 60 / 100.0]
    tolerances = [30 / 360.0, 30 / 100.0, 40 / 100.0]

    blue_pcd = filter_by_hsv(pcd, target, tolerances)
    return blue_pcd


def filter_yellow(pcd):
    # Yellow pretty finicky, the color of the ball is shared by a lot of ground and leaf points.
    # Isolating the ball at all relies heavily on lop to remove ground and plant
    target = [45 / 360.0, 60 / 100.0, 70 / 100.0]
    tolerances = [15 / 360.0, 40 / 100.0, 30 / 100.0]

    yellow_pcd = filter_by_hsv(pcd, target, tolerances)
    return yellow_pcd


# Color must be one of "red", "blue", "yellow"
def get_ball_pcd(pcd, color_str):
    # A narrow range, but in the (few) models I've tested this isolates the balls quite nicely!
    # Kinda important cause soil color blends in with darker points of yellow ball otherwise
    # Only caveat being that I suspect some models will have depressions in soil throwing things off - ah well
    pcd = lop(pcd)

    if color_str == "red":
        pcd = filter_red(pcd)
    elif color_str == "blue":
        pcd = filter_blue(pcd)
    elif color_str == "yellow":
        pcd = filter_yellow(pcd)

    pcd = remove_outliers(pcd, 15, 0.075)
    return pcd


# Another one from chatgpt
def get_center(pcd):
    points = np.asarray(pcd.points)

    # Mean is a reasonable guess as to center
    initial_guess = points.mean(axis=0)
    # Actual radius is ~.075, but this works better
    known_radius = 0.04

    def cost_function(center, points, radius):
        residuals = np.linalg.norm(points - center, axis=1) - radius
        return residuals

    result = least_squares(cost_function, initial_guess, args=(points, known_radius))
    return result.x


def get_markers(pcd):
    markers = []
    for color_str in ["red", "blue", "yellow"]:
        ball_pcd = get_ball_pcd(pcd, color_str)
        # o3d.visualization.draw_geometries([ball_pcd])
        if len(ball_pcd.points) == 0:
            print(f"Error: failed to get point cloud for {color_str} ball.")
            return
        markers.append(get_center(ball_pcd))
    return markers


def align_model(pcd, align_markers, ref_markers, inplace=False):
    if not inplace:
        new_pcd = o3d.geometry.PointCloud()
        new_pcd.points = pcd.points
        new_pcd.colors = pcd.colors
        pcd = new_pcd

    align_centroid = np.mean(align_markers, axis=0)
    ref_centroid = np.mean(ref_markers, axis=0)

    align_markers_centered = align_markers - align_centroid
    ref_markers_centered = ref_markers - ref_centroid

    # [Onward I don't understand but seems to work - thx chatgpt]

    # Compute H, cross-covariance matrix
    H = np.dot(align_markers_centered.T, ref_markers_centered)

    # Compute the Singular Value Decompositin to get U ()
    U, S, Vt = np.linalg.svd(H)

    # Compute the rotation matrix R
    R = np.dot(Vt.T, U.T)

    # Correct for reflection
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = np.dot(Vt.T, U.T)

    # Compute the translation vector t
    t = ref_centroid - np.dot(R, align_centroid)

    # Apply the transformation to the point cloud
    transformation = np.eye(4)
    transformation[:3, :3] = R
    transformation[:3, 3] = t

    pcd.transform(transformation)
    return pcd


# Afaik open3d save to obj involves converting to triangle mesh, which unfortunately musses things up. Hence this approach.
def save_pcd(pcd, source_dirpath, dest_dirpath, name):
    os.makedirs(dest_dirpath, exist_ok=True)

    with open(os.path.join(source_dirpath, OBJ_FILENAME), "r") as f:
        lines = f.readlines()
    vertices = np.asarray(pcd.points)

    vertex_i = 0
    with open(os.path.join(dest_dirpath, OBJ_FILENAME), "w") as f:
        for lines in lines:
            # NOTE: Only needed with photocatch output
            if lines.startswith("o watermark"):
                break

            if lines.startswith("v "):
                new_vals = [str(val) for val in vertices[vertex_i]]
                new_line = f"v {' '.join(new_vals)}\n"
                f.write(new_line)
                vertex_i += 1
            else:
                f.write(lines)


def align_models(
    ref_index: int = 0,
    names: list[str] = None,
    source_base_dirpath=INTERMEDIATE_OUTPUTS_DIRPATH,
    dest_base_dirpath=INTERMEDIATE_OUTPUTS_DIRPATH,
):
    if names == None:
        names = get_names()

    ref_name = names[ref_index]
    ref_dirpath = os.path.join(source_base_dirpath, ref_name)

    ref_pcd = get_point_cloud(ref_dirpath)
    ref_markers = get_markers(ref_pcd)

    print(f"ALIGNING (with {ref_name})")
    for i, align_name in enumerate(names):
        print(i, align_name)
        align_source_dirpath = os.path.join(source_base_dirpath, align_name)
        align_dest_dirpath = os.path.join(dest_base_dirpath, align_name)
        os.makedirs(align_dest_dirpath, exist_ok=True)

        align_pcd = get_point_cloud(align_source_dirpath)
        align_markers = get_markers(align_pcd)
        if align_markers == None:
            print(f"Failed to align {align_name}")
            continue
        align_model(align_pcd, align_markers, ref_markers, inplace=True)

        save_pcd(align_pcd, align_source_dirpath, align_dest_dirpath, align_name)
    print()


if __name__ == "__main__":
    align_models(-1)
