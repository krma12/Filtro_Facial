# Development Notes

This document describes the development process of the Facial Filters project: the main issues found along the way, how they were diagnosed and fixed, the architecture decisions behind it, and the lessons learned. It was written with the assistance of Claude, who acted as a coding assistant throughout the project, reviewing code, researching problems, and implementing changes together with the author.

## Development Process

The project was built incrementally, one class at a time, testing each piece on a real webcam before moving to the next:

1. Setting up a Python 3.10 virtual environment and installing OpenCV, Mediapipe, and NumPy.
2. `CameraManager`: opening the webcam, reading frames, and releasing it correctly.
3. `FaceDetector`: wrapping Mediapipe's face detection, converting its output into pixel coordinates usable by the rest of the program.
4. Generating accessory images (glasses, mustache, ears, hat) with real transparency using Python/Pillow.
5. `base_filter.py` (the `Filter` base class) and four concrete filters inheriting from it.
6. `FilterManager`, to switch between filters and combos while the app runs.
7. `main.py`, tying every piece together into a single application.
8. Calibrating each filter's size and position by testing live against a real face.

## Issues Found and How They Were Solved

### Mediapipe's legacy API was removed entirely

The single biggest issue in this project: the code was originally written against Mediapipe's classic `mp.solutions.face_mesh` API, but the installed version (1.0.1) raised `AttributeError: module 'mediapipe' has no attribute 'solutions'`. This wasn't a typo or a version mismatch to roll back from - Google had deprecated that API for a while, and as of Mediapipe 1.0 it was removed from the package completely.

This was confirmed directly rather than guessed: Mediapipe 1.0.1 was installed in an isolated environment and tested three different ways (`mp.solutions`, `from mediapipe import solutions`, `import mediapipe.solutions`), all three failed. From there, the replacement API (`mp.tasks.vision.FaceLandmarker`) was found and verified the same way - installing it, inspecting its actual available methods and classes with `dir()`, and testing a real call end-to-end before writing it into the project. This also meant a model file (`face_landmarker.task`) had to be downloaded separately, since the new API doesn't bundle the model the way the old one did.

The same issue came up again later with `mp.solutions.drawing_utils`, used for drawing the debug face mesh - it had a direct equivalent in `mp.tasks.vision.drawing_utils`, found and confirmed the same way.

### `import cV2` typo

A later edit to `camara_manager.py` introduced `import cV2` (capital V) instead of `import cv2`. Since Python module names are case-sensitive and the installed package is lowercase, this raised `ModuleNotFoundError: No module named 'cV2'` the moment the file was imported, even though every other usage in the file correctly referred to `cv2` in lowercase.

### `opencv-python` and `opencv-contrib-python` installed together

Installing `opencv-python` directly, on top of `opencv-contrib-python` (which Mediapipe pulls in automatically as a dependency), left the `cv2` module in a broken state - it could still be imported, but `cv2.__version__` raised `AttributeError: module 'cv2' has no attribute '__version__'`. Both packages provide the same `cv2` module and aren't meant to be installed side by side. Fixed by uninstalling both and reinstalling only `opencv-contrib-python`, which already includes everything `opencv-python` provides.

### VS Code reporting false import errors

Even after the libraries were correctly installed inside the project's virtual environment, VS Code kept underlining `import cv2` and `import mediapipe` as errors. The cause was a workspace setting (`"python-envs.defaultEnvManager": "ms-python.python:system"`) pointing the editor at the system-wide Python installation instead of the virtual environment, so its import-checking never looked in the right place. Fixed by explicitly selecting the virtual environment's interpreter through VS Code's "Python: Select Interpreter" command. The code itself was correct the whole time; this only affected the editor's static analysis.

### Wrong camera selected by default

`cv2.VideoCapture(0)` opens whichever camera the operating system reports first, which is not necessarily the front-facing one - on this machine, index `0` turned out to be the back camera, and `1` the front camera. Solved by making the camera index a parameter the user can choose at startup, instead of hardcoding it.

## Architecture Decisions

- **Separating "open" from "configure" in `CameraManager`.** Following the same lesson learned in an earlier project, the constructor only stores configuration; the camera itself is opened in a separate `start()` method, so creating a `CameraManager` object never has a side effect on real hardware.

- **`FaceDetector` as the only class that knows about Mediapipe.** Every Mediapipe-specific detail (the Tasks API, the model file, coordinate conversion, drawing the debug mesh) lives inside `FaceDetector`. The rest of the program only deals with plain frames, landmark lists, and pixel coordinates.

- **`Filter` as a base class with a template method.** Every accessory filter (`GlassesFilter`, `MustacheFilter`, `EarsFilter`, `HatFilter`) inherits from `Filter`, which loads the accessory image and provides a shared `overlay_image()` method that does the actual alpha-blending math (resizing, rotating, clipping at the frame's edges, and compositing using the image's transparency). Each subclass only has to implement `apply()`: decide which landmarks to use, and how large/rotated the accessory should be. `Filter.apply()` itself raises `NotImplementedError`, so forgetting to override it fails loudly instead of silently.

- **`Filter` does not depend on `FaceDetector`.** Both classes need the same two-line formula to convert a normalized landmark into pixel coordinates. Rather than having `Filter` take a `FaceDetector` instance just to reuse that formula, each class keeps its own small private version of it. A tiny bit of duplicated math was considered a better trade-off than coupling two classes that otherwise have nothing to do with each other.

- **`FilterManager` and "combos".** Instead of handling only one filter at a time, `FilterManager` manages a list of named combos, where each combo is one or more filters applied together in sequence. This made it straightforward to add combinations like "Glasses + Mustache" without changing how individual filters work, and without `main.py` needing to know the difference between a single filter and a combo.

## Calibration Process

Unlike the rest of the code, the exact numbers used to size and position each filter (how much wider than the eyes the glasses should be, how far above the forehead the ears should sit, and so on) can't be reasoned out in the abstract - they depend on how the accessory images themselves are drawn. Each filter was tuned by running it live against a real face, adjusting one multiplier at a time, and testing again, until the accessory looked naturally placed. This is reflected in the individual filter files, where those numbers are the result of several rounds of trial and error rather than a single calculation.

## Testing Approach

Automated headless testing (like the dummy-driver approach used in an earlier Pygame project) doesn't apply well here, since the whole point of this project is reacting to a real face in front of a real camera. Instead, each piece was tested with small, disposable scripts (kept in `tests/`) that exercised just that piece - `CameraManager` and `FaceDetector` together, then each filter on its own - before wiring everything into `main.py`. This made it much easier to tell which class a bug belonged to, instead of debugging the whole pipeline at once.

## Lessons Learned

- A library's public API can change in breaking ways between the version a tutorial or course was built against and the version actually installed. When something that "should" work raises an `AttributeError` for a whole submodule, that's a sign to check for a removed/renamed API rather than to assume a typo.
- When unsure about a library's current behavior, installing it in an isolated environment and testing directly (`dir()`, small scripts) is more reliable than guessing from memory or from documentation that might be out of date.
- Keeping Mediapipe-specific code contained in a single class (`FaceDetector`) meant that migrating to a different API only required changes in one file, not throughout the project.
- Visual, human-tuned values (like how large an accessory should be relative to the face) are a normal and expected part of computer vision projects - they don't need to be "solved" mathematically, just calibrated iteratively against real input.
