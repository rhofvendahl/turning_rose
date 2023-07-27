import os

import numpy as np
import open3d as o3d
from PIL import Image

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
    for i in range(len(vertices)):
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


def main():
    name = MODEL_NAMES[-1]
    dirpath = os.path.abspath(os.path.join("../data/models/obj/reduced_same", name))

    cloud = get_point_cloud(dirpath, MODEL_NAMES[-1])
    print("CLOUD", type(cloud), cloud)
    o3d.visualization.draw_geometries([cloud])


if __name__ == "__main__":
    main()
