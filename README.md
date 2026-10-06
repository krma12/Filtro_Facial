# Facial Filters (AR)

A real-time augmented reality filter application built in Python with OpenCV and Mediapipe. It detects a face through the webcam using Mediapipe's Face Landmarker, and overlays virtual accessories (glasses, mustache, animal ears, a party hat, and combinations of these) that follow the face's position, size, and tilt.

## Description

The webcam feed is captured and analyzed frame by frame to detect 478 facial landmarks. Specific landmarks (eye corners, mouth corners, forehead, chin, face edges) are used to calculate where, how big, and at what angle each accessory should be drawn, so the filters move and rotate naturally as the user moves their head.

## Features

- Real-time face detection and landmark tracking through the webcam.
- Four individual AR filters: glasses, mustache, animal ears, and a party hat.
- Filter combos that apply several accessories at once (Cool, Party, Full look).
- Filters automatically scale and rotate to match the size and tilt of the face.
- Choice of front or back camera at startup.
- Keyboard-controlled filter switching while the app is running.

## Filters and Combos

| Option     | Accessories              |
|------------|---------------------------|
| Glasses    | Round glasses              |
| Mustache   | Handlebar mustache         |
| Ears       | Animal ears (headband style) |
| Hat        | Striped party hat with pompom |
| Cool       | Glasses + mustache         |
| Party      | Hat + mustache              |
| Full look  | Glasses + mustache + ears + hat |
| None       | Plain video, no filter     |

## Requirements

- Python 3.10 (required specifically for compatibility with this project's Mediapipe version).
- OpenCV, Mediapipe, and NumPy (see `requirements.txt`).
- A working webcam.

## Installation and running

1. Download or clone this repository.
2. Create a virtual environment using Python 3.10 (outside of any cloud-synced folder, such as OneDrive, to avoid file-locking issues):

   ```
   py -3.10 -m venv path\to\your\venv
   ```

3. Activate the virtual environment.

   On Windows (PowerShell):
   ```
   path\to\your\venv\Scripts\Activate.ps1
   ```

4. Install the dependencies:

   ```
   pip install -r requirements.txt
   ```

5. Run the app:

   ```
   python main.py
   ```

6. Choose the camera (front or back) when prompted.

## Controls

| Action                 | Key |
|-------------------------|-----|
| Switch filter / combo    | F   |
| Quit                     | Q   |

## Project structure

```
Filtro_Facial/
├── main.py                 # Entry point: FacialFilterApp, ties everything together
├── camara_manager.py        # Webcam handling (open, read frames, release)
├── face_detector.py         # Wraps Mediapipe's Face Landmarker
├── filter_manager.py        # Keeps track of filters/combos and which one is active
├── filters/
│   ├── base_filter.py        # Base class: loads an accessory image, overlays it with transparency
│   ├── glasses_filter.py      # Glasses filter
│   ├── mustache_filter.py     # Mustache filter
│   ├── ears_filter.py         # Animal ears filter
│   └── hat_filter.py          # Party hat filter
├── assets/
│   ├── face_landmarker.task    # Mediapipe's face landmark detection model
│   ├── lentes.png               # Glasses accessory image
│   ├── bigote.png                # Mustache accessory image
│   ├── orejas.png                 # Ears accessory image
│   └── sombrero.png                # Hat accessory image
├── tests/                    # Small standalone scripts used to test each piece individually
├── requirements.txt
└── README.md
```

## Notes

- All accessory images in `assets/` have a transparent background (alpha channel), generated with Python/Pillow so the overlay blends correctly with the video.
- `assets/face_landmarker.task` is Mediapipe's pretrained face landmark detection model, downloaded from Google's official model repository.
- This project specifically requires Python 3.10, since the Mediapipe/OpenCV versions used were tested and calibrated against that version.

## Author

Hugo, with assistance from Claude for debugging, class design, and the implementation of new features.
