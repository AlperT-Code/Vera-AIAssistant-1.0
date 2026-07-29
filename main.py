import sys
import io
import warnings
import tkinter as tk
import pygame
from gui.gui import AsistanGUI

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

if __name__ == "__main__":
    
    stderr = sys.stderr
    sys.stderr = io.StringIO()
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        print(f"Ses motoru hazır: {pygame.mixer.get_init()}")
    except Exception as e:
        print(f"[SES] pygame init hatası: {e}")
    finally:
        
        sys.stderr = stderr

    root = tk.Tk()
    app = AsistanGUI(root)

    root.mainloop()