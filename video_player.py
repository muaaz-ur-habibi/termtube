import cv2
import os
import time
import sys
from moviepy import AudioFileClip
import pygame.mixer as mixer
from PIL import Image



CONSOLE_COLUMNS = os.get_terminal_size().columns
if CONSOLE_COLUMNS % 2 != 0:
    CONSOLE_COLUMNS-=1
CONSOLE_ROWS = os.get_terminal_size().lines


class Player:
    def __init__(self, video_file_path, audio_file_path):
        self.video_path = video_file_path
        self.audio_path = audio_file_path

        mixer.init()

    def convert_mp4_to_wav(self):
        mp4 = AudioFileClip(self.video_path)
        mp4.write_audiofile(self.audio_path, logger=None)
        mp4.close()
    
    def scale(self, img:Image.Image, width):
        #w = (CONSOLE_ROWS/img.height) * (img.width/img.height) * 2.5

        #w = int(CONSOLE_COLUMNS * w)
        w = CONSOLE_COLUMNS

        new_img = img.resize((w, CONSOLE_ROWS))
        #new_img = cv2.resize(img, (0, 0), fx=CONSOLE_COLUMNS/og_w, fy=CONSOLE_ROWS/og_h)
        return new_img
    
    def map_pixel_to_ascii(self, img:Image.Image, width=CONSOLE_COLUMNS):
        pixels = img.getdata()
        ascii_str = ""
        range_width = 255/(len(self.CHARS)-1.001)

        i = 1
        
        for pixel_val in pixels:
            intensity = (0.299 * pixel_val[0] + 0.587 * pixel_val[1] + 0.114 * pixel_val[2])
            #intensity = ((pixel_val[0] + pixel_val[1] + pixel_val[2])/3)

            index = int(intensity//range_width)

            if index >= len(self.CHARS):
                index = len(self.CHARS)

            ascii_str += f'\x1b[38;2;{int(pixel_val[2])};{int(pixel_val[1])};{int(pixel_val[0])}m{self.CHARS[index]}'
            #ascii_str += self.CHARS[index]

            if i % width == 0:
                ascii_str += '\n'
                i = 0
            
            i+=1

        return ascii_str
    
    def clear_screen(self):
        sys.stdout.write(f"\033[{CONSOLE_ROWS}F")

    def ASCII(self, frame, width):
        img = Image.fromarray(frame)

        self.CHARS = ' .-=:+"*#%@'
        #self.CHARS = '@%#*"x+=-:. '

        image = self.scale(img, width)
        art = self.map_pixel_to_ascii(image)

        return art
    
    def PLAY(self, w):
        #self.player = MediaPlayer(self.audio_path)
        mixer.music.load(self.audio_path)
        
        #a, v = self.player.get_frame()

        vid = cv2.VideoCapture(self.video_path)
        fps = vid.get(cv2.CAP_PROP_FPS)

        fps = 1/fps

        try:
            succ = True

            mixer.music.play()
            
            while succ:
                current_time = time.time()
                succ, img = vid.read()

                #self.player.set_pause(False)
                mixer.music.unpause()

                art = self.ASCII(
                    img,
                    width=w)

                sys.stdout.write(art[:-1])
                #print(art[:-1], end="")
                
                while True:
                    if time.time() - current_time < fps:
                        pass
                    else:
                        self.clear_screen()
                        #self.player.set_pause(True)
                        mixer.music.pause()
                        break
                
        except KeyboardInterrupt:
            print("Interrupt detected while playing video")


if __name__ == "__main__":
    print("starting player")
    plyr = Player("temp/curr_vid.mp4", "temp/curr_aud.mp3")
    plyr.convert_mp4_to_wav()

    plyr.PLAY(CONSOLE_COLUMNS)

    print("player ended")
