import os
import shutil

import numpy as np
import open3d as o3d
from PIL import Image
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares

from matplotlib import colors

NAMES = [
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
    # Second return value is a point cloud containing removed values
    # cleaned, _ = pcd.remove_statistical_outlier(nb_neighbors=6, std_ratio=2.0)
    cleaned, _ = pcd.remove_radius_outlier(nb_points=neighbors, radius=0.075)
    return cleaned


def filter_red(pcd):
    # Red is do-able without lop, but lop allows safe inclusion of more points.

    # Good without lop:
    # target = [359 / 360.0, 70 / 100.0, 60 / 100.0]
    # tolerances = [4 / 360.0, 30 / 100.0, 40 / 100.0]

    # Better with lop:
    target = [360 / 360.0, 70 / 100.0, 60 / 100.0]
    tolerances = [5 / 360.0, 30 / 100.0, 40 / 100.0]

    red_pcd = filter_by_hsv(pcd, target, tolerances)
    return red_pcd


def filter_blue(pcd):
    # Blue is super easy, and works with or without lop
    target = [210 / 360.0, 70 / 100.0, 60 / 100.0]
    tolerances = [30 / 360.0, 30 / 100.0, 40 / 100.0]

    return filter_by_hsv(pcd, target, tolerances)


def filter_yellow(pcd):
    # Yellow pretty finicky, the color of the ball is shared by a lot of ground and leaf points.
    # Isolating the ball at all relies heavily on lop to remove ground and plant
    # target = [45 / 360.0, 55 / 100.0, 65 / 100.0]
    # tolerances = [15 / 360.0, 45 / 100.0, 35 / 100.0]

    target = [45 / 360.0, 60 / 100.0, 70 / 100.0]
    tolerances = [15 / 360.0, 40 / 100.0, 30 / 100.0]

    return filter_by_hsv(pcd, target, tolerances)


# Color must be one of "red", "blue", "yellow"
def get_ball_pcd(pcd, color_str):
    # # Second return value is a point cloud containing removed values
    # pcd = get_point_cloud(dirpath, name)
    # print("CLOUD", pcd)

    # A narrow range, but in the (few) models I've tested this isolates the balls quite nicely!
    # Kinda important cause soil color blends in with darker points of yellow ball otherwise
    # Only caveat being that I suspect some models will have depressions in soil throwing things off - ah well
    pcd = lop(pcd, 0.8, 0.1)
    print(f"{color_str.upper()} LOPPED", pcd)

    if color_str == "red":
        pcd = filter_red(pcd)
    elif color_str == "blue":
        pcd = filter_blue(pcd)
    elif color_str == "yellow":
        pcd = filter_yellow(pcd)
    print(f"{color_str.upper()} FILTERED", pcd)

    pcd = remove_outliers(pcd, 15)
    print(f"{color_str.upper()} CLEANED", pcd)

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
        markers.append(get_center(ball_pcd))
    return markers


# Translate model so that markers center is at origin, and rotate it so that they're flat against the xz plane; return new pcd and markers
def center_model(pcd, markers, inplace=False):
    if not inplace:
        new_pcd = o3d.geometry.PointCloud()
        new_pcd.points = pcd.points
        new_pcd.colors = pcd.colors
        pcd = new_pcd

    p1 = markers[0]
    p2 = markers[1]
    p3 = markers[2]
    triangle_centroid = (p1 + p2 + p3) / 3.0

    v1 = p2 - p1
    v2 = p3 - p1
    triangle_normal = np.cross(v1, v2)

    # Normalize vector (thx chatgpt)
    norm = np.linalg.norm(triangle_normal)
    if norm != 0:
        triangle_normal /= norm

    # Model is upside down otherwise. I'm reasonably sure that's bc triangle normal has y of -1ish
    y_axis = np.array([0, -1, 0])

    # Calculate rotation matrix
    # rotation_matrix = o3d.geometry.get_rotation_matrix_from_to(triangle_normal, y_axis)
    r = Rotation.align_vectors([y_axis], [triangle_normal])
    rotation_matrix = r[0].as_matrix()

    translation_vector = -triangle_centroid

    # Rotate and transform ref model
    pcd.rotate(rotation_matrix, center=(0, 0, 0))
    pcd.translate(translation_vector)

    # Rotate and translate markers
    new_p1 = np.dot(rotation_matrix, p1 - triangle_centroid)
    new_p2 = np.dot(rotation_matrix, p2 - triangle_centroid)
    new_p3 = np.dot(rotation_matrix, p3 - triangle_centroid)

    return pcd, np.array([new_p1, new_p2, new_p3])


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

    # [Onward I don't really get]

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


def copy_assets(input_dirpath, output_dirpath, name):
    shutil.copy(os.path.join(input_dirpath, name + ".mtl"), output_dirpath)
    shutil.copy(os.path.join(input_dirpath, "texgen_2.jpg"), output_dirpath)


# Afaik open3d save to obj involves converting to triangle mesh, which unfortunately musses things up. Hence this approach.
def save_pcd(pcd, input_dirpath, output_dirpath, name, with_assets=True):
    os.makedirs(output_dirpath, exist_ok=True)

    with open(os.path.join(input_dirpath, name + ".obj"), "r") as f:
        input_lines = f.readlines()
    vertices = np.asarray(pcd.points)

    vertex_i = 0
    with open(os.path.join(output_dirpath, name + ".obj"), "w") as f:
        for input_line in input_lines:
            if input_line.startswith("v "):
                new_vals = [str(val) for val in vertices[vertex_i]]
                new_line = f"v {' '.join(new_vals)}\n"
                f.write(new_line)
                vertex_i += 1
            else:
                f.write(input_line)

    if with_assets:
        copy_assets(input_dirpath, output_dirpath, name)


def main():
    ref_name = NAMES[-1]
    ref_dirpath = os.path.abspath(
        os.path.join("../data/models/obj/processed", ref_name)
    )
    ref_output_dirpath = os.path.abspath(
        os.path.join("../data/models/obj/aligned", ref_name)
    )

    ref_pcd = get_point_cloud(ref_dirpath, ref_name)
    ref_markers = get_markers(ref_pcd)

    # NOTE: Centering needs some debugging to work with align, and I'm honestly not even sure I want it so just gonna leave it here
    # ref_pcd_centered, ref_markers_centered = center_model(ref_pcd, ref_markers)
    # ref_pcd = ref_pcd_centered
    # ref_markers = ref_markers_centered

    save_pcd(ref_pcd, ref_dirpath, ref_output_dirpath, ref_name)

    NAMES = NAMES[:-1]
    for align_name in NAMES:
        align_dirpath = os.path.abspath(
            os.path.join("../data/models/obj/processed", align_name)
        )
        align_output_dirpath = os.path.abspath(
            os.path.join("../data/models/obj/aligned", align_name)
        )

        align_pcd = get_point_cloud(align_dirpath, align_name)

        align_markers = get_markers(align_pcd)

        align_model(align_pcd, align_markers, ref_markers, inplace=True)

        save_pcd(align_pcd, align_dirpath, align_output_dirpath, align_name)


if __name__ == "__main__":
    main()
