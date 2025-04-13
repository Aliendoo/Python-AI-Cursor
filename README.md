# Python Virtual Mouse

A gesture-controlled virtual mouse that allows users to control their cursor using hand movements captured through a webcam.

## Overview

This application uses computer vision and hand tracking technology to convert hand gestures into mouse controls. Users can:
- Move the cursor by moving their palm
- Select (click) by holding their palm still for 8 seconds

The system uses MediaPipe's hand detection and tracking capabilities to identify and follow hand landmarks in real-time.

## Features

- **Gesture Recognition**: Detects open palm gestures
- **Cursor Movement**: Maps hand position to cursor movement on screen
- **Click Functionality**: Automatically clicks when palm is held in position
- **Visual Feedback**: Shows real-time camera feed with hand landmarks
- **User-Friendly Interface**: Simple GUI with clear instructions

## Requirements

```
pyautogui==0.9.53
opencv-python==4.5.5.64
mediapipe==0.10.7
comtypes==1.1.10
pycaw==20181226
screen-brightness-control==0.9.0
```

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/virtual-mouse.git
   cd virtual-mouse
   ```

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python Virtual_Mouse.py
   ```

2. A GUI window will appear - click "Start Tracking" to begin.

3. Position yourself in front of your webcam and show your palm.

4. Control the mouse:
   - Move your palm to move the cursor
   - Hold your palm still for 8 seconds to perform a click

5. Press Enter in the camera window to exit the application.

## How It Works

1. **Hand Detection**: The application uses MediaPipe's hand detection to locate hands in the camera frame.

2. **Gesture Recognition**: It measures distances between fingertips and palm center to detect open palm gestures.

3. **Cursor Control**: Palm position is mapped to screen coordinates, allowing natural cursor movement.

4. **Click Detection**: The application tracks when the palm remains stationary for 8 seconds and triggers a click.

## Customization

You can adjust several parameters in the code:
- Detection confidence thresholds
- Click delay (currently set to 8 seconds)
- Cursor sensitivity and smoothing

## Limitations

- Requires good lighting conditions for accurate hand detection
- Works best with a clean background
- May require adjustment for different users and camera setups

## Troubleshooting

- **No hand detected**: Check lighting conditions and make sure your hand is clearly visible to the camera
- **Cursor movement too sensitive**: Adjust the ratio parameters in the `get_position` method
- **Click not working**: Ensure you're holding your palm completely still for the required time

## License

[Include your license information here]

## Acknowledgements

- This project uses [MediaPipe](https://github.com/google/mediapipe) for hand tracking
- [PyAutoGUI](https://github.com/asweigart/pyautogui) for cursor control
- [OpenCV](https://opencv.org/) for image processing
