import pytubefix.exceptions
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

from pyfiglet import print_figlet
import shutil

from pytubefix import YouTube, Search
import pytubefix
from urllib.parse import urlparse

import os

from video_player import *

#-------GLOBAL VARIABLES--------#
V_RES = "AUTO"
A_RES = ""
CONSOLE_COLUMNS = 0
CONSOLE_ROWS = os.get_terminal_size().lines


dim = shutil.get_terminal_size()
w = dim.columns
h = dim.lines

def CreateVideoPanel(title,
                     author,
                     idx,
                     url,
                     length):
    
    panel = Panel(f"[italic underline]{idx}.[/italic underline]    [bold white]{title}[/bold white]\n\n[magenta]Created by: {author}", title=f"  [bold white underline]{url.strip()}[/ bold white underline]  |  [bold white underline]Length:{length}[/bold white underline]", title_align="left", width=int(w/3))

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
                    CreateVideoPanel(results[result_idx].title,
                                     results[result_idx].author,
                                     result_idx,
                                     results[result_idx].watch_url,
                                     results[result_idx].length)
        
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

# pretty status updaters of downloading audio and video
def update_prog_vid(stream, chunk, bytes_remaining):
    total = stream.filesize
    downloaded = total - bytes_remaining
    perc = (downloaded/total) * 100
    prog_v.update(task_v, advance=int(perc))

def fin_prog_vid(stream, filepath):console.print("[green bold]Video downloaded")

def BuildAndPlayVideo():
    player = Player("temp/curr_vid.mp4", "temp/curr_aud.mp3")
    with Progress(console=console, transient=True) as prog_a:
        try:
            task_a = prog_a.add_task("[bold yellow]Extracting and saving audio...")
            player.convert_mp4_to_wav()
        
        except Exception as e:
            console.print(f"[bold red]Error occured while extracting audio from video. Error: {e}")
            exit(1)
    
    console.print("[green bold]Audio extracted")

    console.input("[bold italic purple3]All processing has been done. Video is ready to launch.\nJust press {ENTER}")

    CONSOLE_COLUMNS = os.get_terminal_size().columns
    if CONSOLE_COLUMNS % 2 != 0:
        CONSOLE_COLUMNS -= 1

    player.PLAY(CONSOLE_COLUMNS)

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
    with console.status("[bold yellow]Searching...", spinner="aesthetic") as spin:
        try:
            s = Search(search_for)

        except Exception as e:
            console.print(f"[bold red]Error occured while searching. Error: {e}")
            exit(1)

    # create pretty panels to display the search results in
    # and also get the url of video to watch
    url_to_watch = DisplaySearchResults(s.videos)

    try:
        Video_obj = YouTube(url_to_watch, on_progress_callback=update_prog_vid, on_complete_callback=fin_prog_vid)
    
    except Exception as e:
        console.print(f"[bold red]Error occured while created Youtube object for videos. Error: {e}")
        exit(1)

    # get video and audio seperately   
    # since most dont have them together
    try:
        if V_RES == "AUTO":
            vid = Video_obj.streams.filter(file_extension="mp4").get_highest_resolution()
            vid = [vid]
        else:
            vid = Video_obj.streams.filter(file_extension="mp4", res=V_RES)
    
    except pytubefix.exceptions.VideoUnavailable as e:
        console.print(f"[bold red]Requested video was unable to be downloaded. Error message: {e}")
        exit()
    
    except Exception as e:
        console.print(f"[bold red]Error occured while getting video. Error: {e}")
        exit(1)

    if vid == []:
        console.print("[bold red]ERROR. No [underline]VIDEO[/underline] streams were found to download. Please change some download settings")
        print(Video_obj.streams)
        exit(1)
    
    # download them fancily
    with Progress(console=console, transient=True) as prog_v:
        try:
            task_v = prog_v.add_task("[bold yellow]Downloading video...")
            vid[0].download("temp", "curr_vid.mp4")
        
        except Exception as e:
            console.print(f"[bold red]Error occured while downloading video. Error: {e}")
    
    BuildAndPlayVideo()
