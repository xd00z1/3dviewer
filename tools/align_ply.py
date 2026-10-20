"""Rigidly align a face scan onto a reference scan (both binary PLY, Heges-style
layout: float x y z, uchar r g b reserved, triangle faces).

    pip install numpy scipy
    python3 tools/align_ply.py models/before.ply new_scan.ply models/after.ply

Only the face/head region is used (a 13 cm sphere around the nose tip), and the
worst-matching 40% of points are ignored on every iteration, so swelling, hair
changes and earbuds don't drag the fit. Only rotation + translation are applied;
the shape is never changed.
"""
import sys
import numpy as np
from scipy.spatial import cKDTree

VDT = np.dtype([('p', '<3f4'), ('c', 'u1', 4)])
FDT = np.dtype([('n', 'u1'), ('i', '<3i4')])


def read(path):
    data = open(path, 'rb').read()
    h = data.index(b'end_header\n') + 11
    hdr = data[:h].decode()
    nv = int(hdr.split('element vertex')[1].split()[0])
    nf = int(hdr.split('element face')[1].split()[0])
    v = np.frombuffer(data, VDT, nv, h)
    f = np.frombuffer(data, FDT, nf, h + nv * 16)
    assert (f['n'] == 3).all(), 'only triangle meshes are supported'
    return v['p'].astype(np.float64), v['c'].copy(), f['i'].copy()


def write(path, p, c, faces, comment):
    v = np.empty(len(p), VDT); v['p'] = p; v['c'] = c
    f = np.empty(len(faces), FDT); f['n'] = 3; f['i'] = faces
    hdr = (f"ply\nformat binary_little_endian 1.0\ncomment {comment}\nelement vertex {len(p)}\n"
           "property float x\nproperty float y\nproperty float z\nproperty uchar red\n"
           "property uchar green\nproperty uchar blue\nproperty uchar reserved\n"
           f"element face {len(faces)}\nproperty list uchar int vertex_index\nend_header\n")
    with open(path, 'wb') as o:
        o.write(hdr.encode()); o.write(v.tobytes()); o.write(f.tobytes())


def vertex_normals(p, faces):
    fn = np.cross(p[faces[:, 1]] - p[faces[:, 0]], p[faces[:, 2]] - p[faces[:, 0]])
    n = np.zeros_like(p)
    for k in range(3):
        np.add.at(n, faces[:, k], fn)
    return n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)


def nose_tip(p):
    # Y is up and the face looks toward +Z: the frontmost point near the top of the scan.
    head = p[p[:, 1] > p[:, 1].max() - 200]
    return head[np.argmax(head[:, 2])]


def face_mask(p, nose):
    return (p[:, 1] > p[:, 1].max() - 260) & (np.linalg.norm(p - nose, axis=1) < 130)


def rodrigues(w):
    th = np.linalg.norm(w)
    if th < 1e-15:
        return np.eye(3)
    k = w / th
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * K @ K


def align(ref, mov, ref_faces):
    na, nb = nose_tip(ref), nose_tip(mov)
    fa = ref[face_mask(ref, na)]
    nfa = vertex_normals(ref, ref_faces)[face_mask(ref, na)]
    fb = mov[face_mask(mov, nb)]
    fb = fb[np.random.default_rng(0).choice(len(fb), min(len(fb), 150000), replace=False)]
    tree = cKDTree(fa)

    # Coarse: nose onto nose. Then trimmed point-to-point ICP to get close...
    R, t = np.eye(3), na - nb
    for _ in range(40):
        cur = fb @ R.T + t
        d, idx = tree.query(cur)
        keep = d < np.quantile(d, 0.6)
        src, dst = cur[keep], fa[idx[keep]]
        cs, cd = src.mean(0), dst.mean(0)
        U, _, Vt = np.linalg.svd((src - cs).T @ (dst - cd))
        dR = Vt.T @ np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))]) @ U.T
        R, t = dR @ R, dR @ t + (cd - dR @ cs)
    # ...then trimmed point-to-plane ICP, which converges properly on smooth faces.
    for _ in range(200):
        cur = fb @ R.T + t
        d, idx = tree.query(cur)
        keep = d < np.quantile(d, 0.6)
        p, q, n = cur[keep], fa[idx[keep]], nfa[idx[keep]]
        x = np.linalg.lstsq(np.hstack([np.cross(p, n), n]), ((q - p) * n).sum(1), rcond=None)[0]
        dR = rodrigues(x[:3])
        R, t = dR @ R, dR @ t + x[3:]
        if np.linalg.norm(x[:3]) < 2e-6 and np.linalg.norm(x[3:]) < 1e-3:
            break
    d, _ = tree.query(fb @ R.T + t)
    return R, t, d


if __name__ == '__main__':
    ref_path, mov_path, out_path = sys.argv[1:4]
    ref, _, ref_faces = read(ref_path)
    mov, col, faces = read(mov_path)
    R, t, d = align(ref, mov, ref_faces)
    ang = np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))
    print(f'rotation {ang:.2f} deg, translation {np.round(t, 1)}')
    print(f'face residual after alignment: median {np.median(d):.2f}, 90th pct {np.quantile(d, .9):.2f} (scan units, mm)')
    write(out_path, mov @ R.T + t, col, faces, f'rigidly aligned to {ref_path}')
