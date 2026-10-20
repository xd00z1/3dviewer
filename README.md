# Swelling Timeline Viewer

Two 3D face scans side by side with a **locked camera**: rotate, zoom or pan
either one and the other follows exactly. Static site, no build step: it works on GitHub Pages.

## Put your scans in

1. Replace `models/before.ply` and `models/after.ply` with your two scans
   (keep the names, or edit the `CONFIG` block at the top of the script in `index.html`).
   `.ply` and `.stl` both work. Vertex colours in a PLY are displayed.
2. Optionally change the labels (`'Day 0'`, `'Day 14'`) in `CONFIG`.
3. Commit and push.

## Publish

Repo → **Settings → Pages → Build and deployment → Deploy from a branch** →
pick the branch and `/ (root)` → Save. The site appears at
`https://<user>.github.io/<repo>/` after a minute.

## Controls

- Left-drag: rotate · Scroll / pinch: zoom · Right-drag (or two-finger drag): pan
- Front / Left / Right / Reset: preset views, applied to both panes

## Notes

- **Alignment.** Phone scans (e.g. Heges) are stored relative to the phone, so two
  sessions never line up on their own. `models/after.ply` has already been rigidly aligned
  onto `models/before.ply` (rotation + translation only, shape untouched; face residual
  median ≈1.8 mm). To add or replace a scan, align it the same way:

      pip install numpy scipy
      python3 tools/align_ply.py models/before.ply path/to/new_scan.ply models/after.ply

  The viewer then shifts both meshes by the *same* offset, preserving that alignment.
- **Framing.** `focus` in `CONFIG` sets the point the camera orbits and how much it frames
  (scan units, mm). It's set to the face; delete it to frame the whole scan.
- **Up axis.** If the face shows up lying down, set `rotation: { x: -90, y: 0, z: 0 }` in `CONFIG`.
- **File size.** GitHub refuses files over 100 MB and warns above 50 MB. Decimate large
  scans (MeshLab: *Quadric Edge Collapse Decimation*) to ~200k–500k faces. A face needs no more than that.
- **Privacy.** A public repo plus GitHub Pages means anyone with the URL can download your face scans.
- Opening `index.html` straight from disk (`file://`) won't load the models. Locally, run
  `python3 -m http.server` in this folder and open http://localhost:8000.
