import cv2
import os
import re
from ascii_magic import AsciiArt
import time

from PIL import Image


CONSOLE_COLUMNS = os.get_terminal_size().columns
if CONSOLE_COLUMNS % 2 != 0:
    CONSOLE_COLUMNS-=1


class Player:
    def __init__(self, video_file_path, audio_file_path, video_save_path, frames_save_path):
        self.video_path = video_file_path
        self.audio_path = audio_file_path
        self.save_path = video_save_path
        self.frames_path = frames_save_path
    
    def sorted_alphanumeric(self, data):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
        return sorted(data, key=alphanum_key)

    def split_video_into_frames(self):
        cap = cv2.VideoCapture(self.video_path)

        succ, img = cap.read()
        c = 1
        while succ:
            cv2.imwrite(f"{self.save_path}/frame_{c}.jpg", img)

            succ, img = cap.read()

            c+=1
    
    def set_framerate(self, rate:int):
        # sets the framerate by deleting rate number of frames
        # starting from frame_1

        contents = self.sorted_alphanumeric(os.listdir(self.save_path))

        # save only the frames that are needed as per the rate
        for i in range(1, len(contents), rate):
            open(f"{self.frames_path}/{contents[i]}", "a").close()

            f_w = open(f"{self.frames_path}/{contents[i]}", "wb")
            f_r = open(f"{self.save_path}/{contents[i]}", "rb")

            f_w.write(f_r.read())

            f_w.close()
            f_r.close()
        
        # cleaning up aka deleting all the initial frames
        for file in contents:
            f = f"{self.save_path}/{file}"
            #os.remove(f)
    
    def create_ascii_text(self):
        contents = self.sorted_alphanumeric(os.listdir(self.frames_path))

        for f in contents:
            file = f"{self.frames_path}/{f}"
            
            art = AsciiArt.from_image(file)
            
            art.to_terminal(columns=CONSOLE_COLUMNS, width_ratio=2)
    
    def scale(self, img:Image.Image, width):
        (og_w, og_h) = img.size
        ratio = og_h/float(og_w)

        height = int(ratio * width / 2)

        new_img = img.resize((width, height))
        return new_img
    
    def map_pixel_to_ascii(self, img:Image.Image, width=CONSOLE_COLUMNS):
        pixels = img.getdata()

        ascii_str = ""
        range_width = 25.5

        i = 0

        for pixel_val in pixels:
            intensity = (0.299 * pixel_val[0] + 0.587 * pixel_val[1] + 0.114 * pixel_val[2])

            index = int(intensity//range_width)

            if index >= len(self.CHARS):
                index = len(self.CHARS) -1
            
            ascii_str += self.CHARS[index]

            if i % width == 0:
                ascii_str += '\n'
            
            i+=1

        return ascii_str

    def ASCII(self, img_path, width):
        img = Image.open(img_path)
        self.CHARS = '.:-=+*#%@'

        image = self.scale(img, width)
        art = self.map_pixel_to_ascii(image)

        return art
    
    def PLAY(self, w):
        frames = self.sorted_alphanumeric(os.listdir(self.frames_path))

        for frame in frames:
            art = self.ASCII(f"{self.frames_path}/{frame}", width=w)
            
            print(art)

if __name__ == "__main__":
    print("starting player")
    plyr = Player("temp/COPY.mp4", "temp/curr_aud.mp3", "player_temp", "player_frames")
    
    fps = 1
    
    #plyr.split_video_into_frames()
    #plyr.set_framerate(fps)

    plyr.PLAY()

    print("player ended")