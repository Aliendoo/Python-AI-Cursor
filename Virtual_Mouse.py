import os

os.environ['TK_SILENCE_DEPRECATION'] = '1'

import cv2
import mediapipe as mp
import pyautogui
import math
import time
from enum import IntEnum
from google.protobuf.json_format import MessageToDict
import tkinter as tk
from PIL import ImageTk, Image

pyautogui.FAILSAFE = False
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


class Gest(IntEnum):
    # Binary Encoded
    PALM = 0  # Open palm
    FIST = 1
    PINKY = 2
    RING = 3
    MID = 4
    INDEX = 5
    THUMB = 6


class HLabel(IntEnum):
    MINOR = 0
    MAJOR = 1


class HandRecog:
    def __init__(self, hand_label):
        self.hand_result = None
        self.hand_label = hand_label
        self.palm_start_time = None
        self.palm_detected = False

    def update_hand_result(self, hand_result):
        self.hand_result = hand_result

    def get_dist(self, point):
        dist = (self.hand_result.landmark[point[0]].x - self.hand_result.landmark[point[1]].x) ** 2
        dist += (self.hand_result.landmark[point[0]].y - self.hand_result.landmark[point[1]].y) ** 2
        return math.sqrt(dist)

    def get_gesture(self):
        if self.hand_result is None:
            return None

        # Check for open palm by measuring distances between fingertips and palm center
        palm_center = self.hand_result.landmark[0]
        fingertips = [4, 8, 12, 16, 20]  # Thumb to pinky fingertips
        total_dist = 0

        for tip in fingertips:
            dist = math.sqrt(
                (self.hand_result.landmark[tip].x - palm_center.x) ** 2 +
                (self.hand_result.landmark[tip].y - palm_center.y) ** 2
            )
            total_dist += dist

        # Print palm center coordinates
        screen_w, screen_h = pyautogui.size()
        palm_x = int(palm_center.x * screen_w)
        palm_y = int(palm_center.y * screen_h)
        print(f"\rPalm Center: x={palm_x}, y={palm_y} | Screen: {screen_w}x{screen_h}", end='', flush=True)

        # Threshold for palm detection
        if total_dist > 0.5:  # Adjust this threshold as needed
            if not self.palm_detected:
                self.palm_detected = True
                self.palm_start_time = time.time()
                print("\nPalm detected - Hold for 8 seconds to select")

            # Check if palm has been held for 8 seconds
            if self.palm_start_time and (time.time() - self.palm_start_time) >= 8:
                print("\nSelection made!")
                pyautogui.click()
                self.palm_start_time = None  # Reset timer
                return Gest.PALM

            return Gest.PALM
        else:
            self.palm_detected = False
            self.palm_start_time = None
            return None


class Controller:
    prev_hand = None

    @classmethod
    def get_position(cls, hand_result):
        point = 9
        position = [hand_result.landmark[point].x, hand_result.landmark[point].y]
        sx, sy = pyautogui.size()
        x_old, y_old = pyautogui.position()
        x = int(position[0] * sx)
        y = int(position[1] * sy)

        if cls.prev_hand is None:
            cls.prev_hand = x, y

        delta_x = x - cls.prev_hand[0]
        delta_y = y - cls.prev_hand[1]
        distsq = delta_x ** 2 + delta_y ** 2
        ratio = 1

        cls.prev_hand = [x, y]

        if distsq <= 25:
            ratio = 0
        elif distsq <= 900:
            ratio = 0.07 * (distsq ** (1 / 2))
        else:
            ratio = 2.1

        x, y = x_old + delta_x * ratio, y_old + delta_y * ratio
        return (x, y)

    @classmethod
    def handle_controls(cls, gesture, hand_result):
        if gesture == Gest.PALM:
            x, y = cls.get_position(hand_result)
            pyautogui.moveTo(x, y, duration=0.1)


class GestureController:
    gc_mode = 0
    cap = None
    CAM_HEIGHT = None
    CAM_WIDTH = None
    hr_major = None
    hr_minor = None
    dom_hand = True

    def __init__(self):
        GestureController.gc_mode = 1
        GestureController.cap = cv2.VideoCapture(0)
        GestureController.CAM_HEIGHT = GestureController.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        GestureController.CAM_WIDTH = GestureController.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        print(f"\nCamera Resolution: {GestureController.CAM_WIDTH}x{GestureController.CAM_HEIGHT}")
        print("Starting hand tracking...")

    def classify_hands(results):
        left, right = None, None
        try:
            handedness_dict = MessageToDict(results.multi_handedness[0])
            if handedness_dict['classification'][0]['label'] == 'Right':
                right = results.multi_hand_landmarks[0]
            else:
                left = results.multi_hand_landmarks[0]
        except:
            pass

        try:
            handedness_dict = MessageToDict(results.multi_handedness[1])
            if handedness_dict['classification'][0]['label'] == 'Right':
                right = results.multi_hand_landmarks[1]
            else:
                left = results.multi_hand_landmarks[1]
        except:
            pass

        if GestureController.dom_hand:
            GestureController.hr_major = right
            GestureController.hr_minor = left
        else:
            GestureController.hr_major = left
            GestureController.hr_minor = right

    def start(self):
        handmajor = HandRecog(HLabel.MAJOR)

        with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
            while GestureController.cap.isOpened() and GestureController.gc_mode:
                success, image = GestureController.cap.read()

                if not success:
                    print("Ignoring empty camera frame.")
                    continue

                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = hands.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.multi_hand_landmarks:
                    GestureController.classify_hands(results)
                    handmajor.update_hand_result(GestureController.hr_major)

                    gest_name = handmajor.get_gesture()
                    if gest_name is not None:
                        Controller.handle_controls(gest_name, handmajor.hand_result)

                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                else:
                    Controller.prev_hand = None
                    print("\rNo hand detected", end='', flush=True)

                cv2.imshow('Virtual Mouse Gesture Controller', image)
                if cv2.waitKey(5) & 0xFF == 13:
                    break

        GestureController.cap.release()
        cv2.destroyAllWindows()


def runvirtualmouse():
    gc1 = GestureController()
    gc1.start()


def main():
    root = tk.Tk()
    root.title("Virtual Mouse")
    root.geometry("300x300")

    label = tk.Label(root, text="Welcome to Virtual Mouse", fg="brown", font='TkDefaultFont 16 bold')
    label.grid(row=0, columnspan=5, pady=10, padx=10)

    img_label = tk.Label(text="👆", font=('TkDefaultFont', 40))
    img_label.grid(row=1, columnspan=5, pady=10, padx=10)

    instructions = tk.Label(root, text="Show open palm to move cursor\nHold palm still for 8s to select",
                            font='TkDefaultFont 12')
    instructions.grid(row=2, columnspan=5, pady=10, padx=10)

    start_button = tk.Button(
        root,
        text="Start Tracking",
        fg="white",
        bg='green',
        font='Helvetica 12 bold italic',
        command=runvirtualmouse,
        height=2,
        width=16,
        activebackground='lightblue'
    )
    start_button.grid(row=3, column=2, pady=10, padx=20)

    root.mainloop()


if __name__ == "__main__":
    main()