import os
import shutil
from mathutils import Matrix

import numpy as np
import open3d as o3d
import bpy

from PIL import Image

MODEL_NAMES = [
    "2023-07-19_19",
    "2023-07-20_01",
    "2023-07-20_07",
    "2023-07-20_13_final",
]


def get_point_cloud(dirpath: str, name: str):
    # Load the mesh
    mesh = o3d.io.read_triangle_mesh(os.path.join(dirpath, name + ".obj"))
    print("MESH", mesh)

    # Load the texture image
    img = Image.open(os.path.join(dirpath, "texgen_2.png"))

    # For resulting array, origin is top left and colors can be accessed with texture_data[y, x]
    texture_data = np.array(img)

    # Drop opacity to fit open3d expectations
    texture_data = texture_data[:, :, :3]

    # Initialize an empty list for each vertex
    vertex_colors = [[] for _ in range(len(mesh.vertices))]

    # For each triangle, map its vertices to colors from the texture
    for triangle, triangle_uv in zip(
        np.asarray(mesh.triangles), np.asarray(mesh.triangle_uvs)
    ):
        u, v = triangle_uv
        for vertex_index in triangle:
            # texture_data.shape returns something like (height, width); so, shape[1] gives width
            x = int(u * (texture_data.shape[1] - 1))
            # NOTE: It's a bit of a tossup whether a v of 0 corrresponds to the top or the bottom of a tex file, depends on software
            y = int((1 - v) * (texture_data.shape[0] - 1))
            color = texture_data[y, x] / 255.0  # normalize to [0, 1]
            vertex_colors[vertex_index].append(color)

    # Compute the average color for each vertex, defaulting to black
    black = np.array([0.0, 0.0, 0.0], dtype=np.float64)
    vertex_colors = [
        np.mean(colors, axis=0) if len(colors) > 0 else black
        for colors in vertex_colors
    ]

    # Create point cloud
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(mesh.vertices)
    point_cloud.colors = o3d.utility.Vector3dVector(np.array(vertex_colors))
    return point_cloud


name = MODEL_NAMES[-1]
dirpath = os.path.abspath(os.path.join("../data/models/obj/reduced_decp5_512", name))
cloud = get_point_cloud(dirpath, MODEL_NAMES[-1])
o3d.visualization.draw_geometries([cloud])
print("CLOUD", type(cloud), cloud)


# # Define colors for the colored balls (in RGB format)
# RED = np.array([1, 0, 0])
# YELLOW = np.array([1, 1, 0])
# BLUE = np.array([0, 0, 1])


# def find_refs(filepath: str):
#     # Load the 3D model
#     mesh = o3d.io.read_triangle_mesh(filepath)
#     print(type(mesh), mesh)

#     # Convert the vertices and vertex colors into numpy arrays
#     vertices = np.asarray(mesh.vertices)
#     colors = np.asarray(mesh.vertex_colors)

#     # Find the indices of the vertices that are closest to the target colors
#     red_ball_index = np.argmin(np.sum((colors - RED) ** 2, axis=1))
#     yellow_ball_index = np.argmin(np.sum((colors - YELLOW) ** 2, axis=1))
#     blue_ball_index = np.argmin(np.sum((colors - BLUE) ** 2, axis=1))

#     # Return the coordinates of these vertices
#     return (
#         vertices[red_ball_index],
#         vertices[yellow_ball_index],
#         vertices[blue_ball_index],
#     )


# dirpath = os.path.abspath("../data/models/obj/reduced_decp5_512")
# filepath = os.path.join(dirpath, MODEL_NAMES[-1] + ".obj")
# red_ref_coords, yellow_ref_coords, blue_ref_coords = find_refs(filepath)

# print("COORDS", red_ref_coords, yellow_ref_coords, blue_ref_coords)

# # # Define target locations for the colored balls
# # RED_TARGET = np.array([0, 0, 0])
# # YELLOW_TARGET = np.array([1, 0, 0])
# # BLUE_TARGET = np.array([0, 1, 0])

# # # Calculate the translation matrix
# # translation_vector = (RED_TARGET + YELLOW_TARGET + BLUE_TARGET) / 3 - (
# #     red_ball_coords + yellow_ball_coords + blue_ball_coords
# # ) / 3
# # translation_matrix = Matrix.Translation(translation_vector)

# # # Load the 3D model into Blender
# # bpy.ops.import_scene.obj(filepath="example.obj")

# # # Apply the translation to the 3D model
# # bpy.context.selected_objects[0].matrix_world = translation_matrix

# # # Save the result
# # bpy.ops.wm.save_as_mainfile(filepath="example_transformed.blend")

# TODO: Try instead using sample points - might work a lot better
# import numpy as np
# import open3d as o3d
# from PIL import Image

# def image_color_to_point_cloud(point_cloud, image):
#     image_width, image_height = image.size
#     colors = list(image.getdata())

#     for point in np.array(point_cloud.points):
#         # Scale x, y, and z to match the range of the image dimensions
#         x_scaled = int((point[0] / max(point_cloud.points[:, 0])) * image_width)
#         y_scaled = int((point[1] / max(point_cloud.points[:, 1])) * image_height)

#         # Ensure indices fall within the range of the image size
#         x_scaled = max(0, min(x_scaled, image_width - 1))
#         y_scaled = max(0, min(y_scaled, image_height - 1))

#         # Map color from image to point cloud
#         color = colors[y_scaled * image_width + x_scaled]
#         point_cloud.colors.append(color)

#     return point_cloud

# def main():
#     # Read the 3D model
#     pcd = o3d.io.read_triangle_mesh("model.obj")

#     # Convert TriangleMesh to PointCloud
#     pcd = pcd.sample_points_poisson_disk(number_of_points=3000)

#     # Read the texture image
#     texture_img = Image.open("texture.png")

#     # Apply the color to the point cloud
#     colored_pcd = image_color_to_point_cloud(pcd, texture_img)

#     # Save the colored point cloud
#     o3d.io.write_point_cloud("colored_point_cloud.ply", colored_pcd)

#     print("Saved the colored point cloud as colored_point_cloud.ply")

# if __name__ == "__main__":
#     main()

# Also TODO: Start considering the endgame. Say I have a bunch of points of some color. What then? How do I align it reeeally well?
