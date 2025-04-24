from tkinter import*
from PIL import ImageTk, Image
from main import main

player1 = 1
player2 = 0


root = None

def close_function():
    global root
    print("THIS RAN")
    root.destroy()

def startScreen():
    global player1
    global player2
    global root
    root = Tk()
    root.title("Grid Wars")
    root.attributes("-fullscreen", True) # makes window fullscreen

    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Load image and resize
    bg_image = Image.open("CardArt/Grid_background.png")
    bg_image = bg_image.resize((screen_width, screen_height))  # Resize to fit screen
    bg = ImageTk.PhotoImage(bg_image)

    canvas = Canvas(root, width=screen_width, height=screen_height)
    canvas.pack(fill="both", expand=True)

    canvas.create_image(0, 0, image=bg, anchor="nw")  # Draw background image

    # Create text label for Play Again
    # play_label = Label(root, text="Press Button to Play!", wraplength=250, width=10,
    #                   font=("Terminal", 25),
    #                   fg="red", bg="#000000",  # Set background to match style
    #                   padx=0, pady=20)
    # play_label_window = canvas.create_window(screen_width // 2.0, screen_height // 1.55, window=play_label)

    button_start = Button(root, text="Push Button to Start!", wraplength=250, 
                        font=("Terminal", 25),
                        command=close_function,
                        bg="#222222",  # Match this to part of your image
                        fg="red",
                        activebackground="#222222",
                        bd=10, highlightthickness=2, highlightbackground="red", highlightcolor="red",
                        padx=0, pady=0)
    button_start_window = canvas.create_window(screen_width // 1.975, screen_height // 1.55, window=button_start)
    root.mainloop()


def endScreen(winner, loser):
    root = Tk()
    root.title("Grid Wars")
    root.attributes("-fullscreen", True) # makes window fullscreen

    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Load image and resize
    bg_image = Image.open("CardArt/Grid_end.png")
    bg_image = bg_image.resize((screen_width, screen_height))  # Resize to fit screen
    bg = ImageTk.PhotoImage(bg_image)

    canvas = Canvas(root, width=screen_width, height=screen_height)
    canvas.pack(fill="both", expand=True)

    canvas.create_image(0, 0, image=bg, anchor="nw")  # Draw background image

    if (winner == player1) and (loser == player2):
        win_text = "PLAYER 1 :)"
        lose_text = "PLAYER 2 :("

        # Create text label for result
        win_label = Label(root, text=win_text, 
                        font=("Terminal", 45),
                        fg="green", bg="#99D9EA",  # Set background to match style
                        padx=10, pady=10)
        lose_label = Label(root, text=lose_text, 
                        font=("Terminal", 45),
                        fg="red", bg="#99D9EA",  # Set background to match style
                        padx=10, pady=10)
        win_label_window = canvas.create_window(screen_width // 3.8, screen_height // 1.15, window=win_label)
        lose_label_window = canvas.create_window(screen_width // 1.4, screen_height // 1.15, window=lose_label)
    if (winner == player2) and (loser == player1):
        win_text = "PLAYER 2 :)"
        lose_text = "PLAYER 1 :("

        # Create text label for result
        win_label = Label(root, text=win_text, 
                        font=("Terminal", 45),
                        fg="green", bg="#99D9EA",  # Set background to match style
                        padx=10, pady=10)
        lose_label = Label(root, text=lose_text, 
                        font=("Terminal", 45),
                        fg="red", bg="#99D9EA",  # Set background to match style
                        padx=10, pady=10)
        win_label_window = canvas.create_window(screen_width // 3.8, screen_height // 1.15, window=win_label)
        lose_label_window = canvas.create_window(screen_width // 1.4, screen_height // 1.15, window=lose_label)

    # Create text label for Play Again
    play_again_label = Label(root, text="Press Button to Play Again!", 
                      font=("Terminal", 20),
                      fg="black", bg="#99D9EA",  # Set background to match style
                      padx=10, pady=10)
    play_again_label_window = canvas.create_window(screen_width // 2.0, screen_height // 1.275, window=play_again_label)

    root.after(10000, root.destroy)
    root.mainloop()

if __name__ == "__main__":
    # startScreen()
   

    endScreen(winner= player1, loser= player2)
    # endScreen(winner= player2, loser= player1)