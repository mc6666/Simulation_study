from PIL import Image
import glob
import os

frames = []
imgs = glob.glob("screenshot/*.png")
for i in imgs:
    new_frame = Image.open(i)
    frames.append(new_frame)

# Save into a GIF file that loops forever
frames[0].save('animated.gif', format='GIF',
               append_images=frames[1:],
               save_all=True,
               duration=300, loop=0)
os.startfile("animated.gif")               