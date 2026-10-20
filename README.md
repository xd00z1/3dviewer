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

- **Alignment.** Both meshes are shifted by the *same* offset, so their relative
  position from the scanner is preserved. If your two scans were captured in different
  coordinate frames, register them first (CloudCompare: *Tools → Registration → Fine
  registration (ICP)*, or MeshLab *Align*), then export both. Otherwise the side-by-side
  comparison is misleading.
- **Up axis.** If the face shows up lying down, set `rotation: { x: -90, y: 0, z: 0 }` in `CONFIG`.
- **File size.** GitHub refuses files over 100 MB and warns above 50 MB. Decimate large
  scans (MeshLab: *Quadric Edge Collapse Decimation*) to ~200k–500k faces. A face needs no more than that.
- **Privacy.** A public repo plus GitHub Pages means anyone with the URL can download your face scans.
- Opening `index.html` straight from disk (`file://`) won't load the models. Locally, run
  `python3 -m http.server` in this folder and open http://localhost:8000.
