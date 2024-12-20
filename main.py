from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.spinner import Spinner

from pyfiglet import print_figlet
import shutil

from pytubefix import YouTube, Search
from urllib.parse import urlparse

import logging

from moviepy import *

logging.getLogger("moviepy").setLevel(logging.WARNING)

#-------GLOBAL VARIABLES--------#
V_RES = "1080p"
A_RES = ""


dim = shutil.get_terminal_size()
w = dim.columns
h = dim.lines

def CreateVideoPanel(title,
                     author,
                     idx,
                     url):
    
    panel = Panel(f"[italic underline]{idx}.[/italic underline]    [bold white]{title}[/bold white]\n\n[magenta]Created by: {author}", title=f"  [bold white underline]{url.strip()}  ", title_align="left", width=int(w/3))

    console.print(panel)

def DisplaySearchResults(results:list):
    console.clear()
    print_figlet("Terminal-Youtube", colors="red:", width=100)
    console.rule("[i]Search results", align="left")

    print("\n")

    exit_search_page = False

    start_of_display = 0
    amount_to_display = 5
    end_of_results = False
    start_of_results = True

    while not exit_search_page:
        if not end_of_results:
            for result_idx in range(len(results)):
                if result_idx>start_of_display and result_idx<=amount_to_display:
                    CreateVideoPanel(results[result_idx].title, results[result_idx].author, result_idx, results[result_idx].watch_url)
        
        search_page_inp = console.input("(url_of_video) Watch that video, (idx_of_video) Get URL from the index, (n) Next page, (p) Previous page\n👉 ")

        # logic for displaying only a set number of results
        # and providing a paging system to see more
        if search_page_inp == "n":
            # if the end limit is the length of the results
            if amount_to_display == len(results):
                # throw an error
                console.print("[bold italic red]END OF SEARCH RESULTS.")
                end_of_results = True
            else:
                # start is the old end
                # end is +5 of previous
                start_of_display = amount_to_display
                # some basic logic to see if we reached the end
                amount_to_display = amount_to_display + 5 if amount_to_display + 5 <= len(results) else len(results)

                console.clear()
                print_figlet("Terminal-Youtube", colors="red:", width=100)
                console.rule("[i]Search results", align="left")

                print("\n")
                start_of_results = False

        # just the opposite of "n"
        elif search_page_inp == "p":
            if not start_of_results:
                amount_to_display = amount_to_display - 5
                start_of_display = start_of_display - 5

                if start_of_display < 0:
                    start_of_display = 0
                    start_of_results = True

                console.clear()
                print_figlet("Terminal-Youtube", colors="red:", width=100)
                console.rule("[i]Search results", align="left")

                print("\n")
                end_of_results = False

            else:
                console.print("[bold italic red]START OF SEARCH RESULTS")
        
        else:
            parsed_url = urlparse(search_page_inp)

            if parsed_url.scheme == "https" and "youtube" in parsed_url.netloc:
                return search_page_inp
            else:
                console.print("[bold italic red]INVALID URL ENTERED. PLEASE COPY AND PASTE THE URL")

def update_prog(stream, chunk, bytes_remaining):
    total = stream.filesize
    downloaded = total - bytes_remaining
    perc = (downloaded/total) * 100

    prog_v.update(task_v, advance=int(perc))

def fin_prog(stream, filepath):

    console.print("[green bold]Video downloaded")

def CONCATENATE_AUD_VID(aud_path,
                        vid_path,
                        save_path):
    
    v_clip = VideoFileClip(vid_path)
    a_clip = AudioFileClip(aud_path)

    conc = v_clip.with_audio(a_clip)

    conc.write_videofile(save_path, logger=None)
    console.print("[bold green]Video built successfully")

def CopyVIDEO(copy_folder):
    copy = console.input("Would you like to make a copy of the video you just downloaded?\n[blue](y/n)[/blue]👉 ")

    if copy == 'y':
        with open(f"{copy_folder}/COPY.mp4", "wb") as copy_file:
            read_file = open("temp/VIDEO.mp4", "rb")

            copy_file.write(read_file.read())
            console.print("[green bold]Copied into COPY.mp4 successfully")



if __name__ == "__main__":
    # just some basic setting up and main menu type displaying
    console = Console()
    console.clear()

    print_figlet("Terminal-Youtube", colors="red:", width=100)
    console.rule("[i]Youtube for your Terminal", align="left")

    print("\n")
    # get the search term
    search_for = console.input("Enter the search term\n👉 ")

    # create the search object
    s = Search(search_for)
    # create pretty panels to display the search results in
    # and also get the url of video to watch
    url_to_watch = DisplaySearchResults(s.videos)
    Video_obj = YouTube(url_to_watch, on_progress_callback=update_prog, on_complete_callback=fin_prog)

    # get video and audio seperately   
    # since most dont have them together
    vid = Video_obj.streams.filter(file_extension="mp4", res=V_RES)
    aud = Video_obj.streams.filter(mime_type="audio/mp4")

    # download them fancily
    with Progress(console=console, transient=True) as prog_v:
        task_v = prog_v.add_task("[bold yellow]Downloading video...")
        vid[0].download("temp", "curr_vid.mp4")
        aud[0].download("temp", "curr_aud.mp3")

    # concatenate the audio and video together
    #console.print("[bold yellow]Concatenating audio and video...")
    with Spinner('aesthetic', "[bold yellow]Concatenating audio and video...") as spin:
        CONCATENATE_AUD_VID("temp/curr_aud.mp3", "temp/curr_vid.mp4", "temp/VIDEO.mp4")
    CopyVIDEO("temp")