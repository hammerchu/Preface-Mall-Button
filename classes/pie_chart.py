import matplotlib.pyplot as plt
from matplotlib import animation
import time
import cv2
import threading
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
class PieChart:
    def __init__(self, w=1920, h=1080):
        '''
        data: list of tuples (label, size) e.g. [('Apples', 50), ('Bananas', 0), ('Cherries', 10)]
        colors: list of mpl compatible colors e.g. ['darkred', 'yellow', 'pink']
        duration: duration of the animation in frames
        video_path: path to the video file
        '''
        # Set fixed figure size and DPI
        self.fig, self.ax = plt.subplots(figsize=(8, 6), dpi=100)
        self.ax.axis('equal')

        # Add this line to suppress the aspect ratio warning
        self.ax.set_adjustable('datalim')

        self.patches = None
        self.labels = None
        self.colors = None
        self.sizes = None
        self.output_frame = None

        self.canvas_width = w
        self.canvas_height = h

    
    def render_single_frame(self, data:list[tuple[str, int]], colors:list[str], duration:int, title:str, frame_index:int, player=True):
        self.duration = duration
        self.data = data
        self.colors = colors
        self.title = title
        self.labels = [item[0] for item in data]
        self.init_sizes = [100 if i == 0 else 0 for i in range(len(data))] # the initial sizes
        self.sizes = [item[1] for item in data] # the dynamic sizes
        self.anim = None
        # Calculate step sizes for each section to reach target values
        self.step_sizes = []
        # For each section, calculate how much it needs to change per frame
        for i, target in enumerate(self.sizes):
            # Start from 0 and increment to reach target
            step = (self.init_sizes[i] - target) / self.duration
            self.step_sizes.append(step)

        self.animate(frame_index)
        
        # Convert matplotlib figure to cv2 format
        canvas = self.fig.canvas
        canvas.draw()
        
        # Get dimensions from figure
        w, h = self.fig.get_size_inches() * self.fig.dpi
        w, h = int(w), int(h)
        
        # Convert canvas to image array
        buf = np.frombuffer(canvas.buffer_rgba(), dtype=np.uint8)
        buf = buf.reshape(h, w, 4)
        
        # Convert RGBA to BGR for cv2
        self.output_frame = cv2.cvtColor(buf, cv2.COLOR_RGBA2BGR)

        '''Move the pie chart to the right side of the canvas and add title text'''
        # Create a black canvas of size (w, h)
        canvas = np.ones((self.canvas_height, self.canvas_width, 3), dtype=np.uint8)*255
        
        # Calculate x offset to align output_frame to right
        x_offset = self.canvas_width - self.output_frame.shape[1]
        
        # Resize output_frame to fit canvas height while maintaining aspect ratio
        aspect_ratio = self.output_frame.shape[1] / self.output_frame.shape[0]
        new_height = self.canvas_height
        new_width = int(new_height * aspect_ratio)
        resized_output = cv2.resize(self.output_frame, (new_width, new_height))
        
        # Recalculate x offset with resized frame
        x_offset = self.canvas_width - new_width
        
        # Place resized output_frame on right side of canvas
        canvas[:, x_offset:self.canvas_width] = resized_output

        # Add title text on left side
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 3.0
        font_thickness = 3
        text_color = (0, 0, 0)  # White color
        
        # Get text size to center vertically
        text_size = cv2.getTextSize(title, font, font_scale, font_thickness)[0]
        text_x = 150  # Padding from left
        text_y = self.canvas_height // 2 + text_size[1] // 2  # Vertical center
        text_y = text_y + 300 # move the text down

        # fontpath = "/Users/hammerchu/Desktop/DEV/Preface/Mall/classes/Microsoft_YaHei_Bold.ttf"
        # font = ImageFont.truetype(fontpath, 32)

        # Load Microsoft YaHei Bold font
        # Get system font path for Microsoft YaHei Bold on Linux
        if os.name == 'posix':  # Linux/Unix
            font_path = "/usr/share/fonts/truetype/msttcorefonts/Microsoft_YaHei_Bold.ttf"
            if not os.path.exists(font_path):
                font_path = "./classes/Microsoft_YaHei_Bold.ttf"  # Fallback to local path
        else:
            font_path = "/Users/hammerchu/Desktop/DEV/Preface/Mall/classes/Microsoft_YaHei_Bold.ttf"
        # font_path = "classes/Microsoft_YaHei_Bold.ttf"
        font_size = 80
        img_pil = Image.fromarray(canvas)
        draw = ImageDraw.Draw(img_pil)
        font = ImageFont.truetype(font_path, font_size)
        

        b,g,r,a = 10,10,10,0
        draw.text((text_x, text_y),  "睇吓其他人點睇！", font = font, fill = (b, g, r, a))
        canvas = np.array(img_pil)

        # cv2.putText(canvas, title, (text_x, text_y), font, font_scale, text_color, font_thickness)
        
        # Update output_frame to be the full canvas
        self.output_frame = canvas
        
        if player:
            # Display frame
            cv2.imshow('Pie Chart Animation', self.output_frame)
            cv2.waitKey(1)
        else:
            return self.output_frame


    def animate(self, i):
        """Animate pie chart with easing out effect"""
        # Clear the previous frame to avoid ghost text
        plt.clf()
        plt.axis('equal')
        plt.tight_layout()
        
        # Calculate easing factor (quadratic ease out)
        progress = i / self.duration
        ease = 1 - (1 - progress) * (1 - progress)  # Quadratic ease out
        
        # Apply easing to the current frame
        current_sizes = []
        for j in range(len(self.sizes)):
            start = self.init_sizes[j]
            end = self.sizes[j]
            current = start + (end - start) * ease
            current_sizes.append(current)
            # print(f'i: {i}, section {j}: {current}')

        self.patches = plt.pie(current_sizes, colors=self.colors, startangle=90, shadow=True,
                     labels=self.labels, autopct='%1.0f%%',
                     textprops={'fontsize': 14, 'weight': 'bold'})
        return self.patches[0]  # Return only the patches, not the text elements



    # def render(self, data:list[tuple[str, int]], colors:list[str], duration:int, title:str=f"polling result",  hold_time:int=0):
    #     self.title = title
    #     self.duration = duration
    #     self.data = data
    #     self.colors = colors
    #     self.labels = [item[0] for item in data]
    #     self.init_sizes = [100 if i == 0 else 0 for i in range(len(data))] # the initial sizes
    #     self.sizes = [item[1] for item in data] # the dynamic sizes
    #     self.anim = None
    #     # self.video_path = video_path
    #     self.hold_time = hold_time
    #     # Calculate step sizes for each section to reach target values
    #     self.step_sizes = []

    #     # For each section, calculate how much it needs to change per frame
    #     for i, target in enumerate(self.sizes):
    #         # Start from 0 and increment to reach target
    #         step = (self.init_sizes[i] - target) / self.duration
    #         self.step_sizes.append(step)       
        
    #     start_time = time.time()
             
    #     # Convert matplotlib animation to frames and display
    #     for frame in range(self.duration):
    #         s = time.time()
    #         # Render the frame
    #         self.animate(frame)
            
    #         # Convert matplotlib figure to cv2 format
    #         canvas = self.fig.canvas
    #         canvas.draw()
            
    #         # Get dimensions from figure
    #         w, h = self.fig.get_size_inches() * self.fig.dpi
    #         w, h = int(w), int(h)
            
    #         # Convert canvas to image array
    #         buf = np.frombuffer(canvas.buffer_rgba(), dtype=np.uint8)
    #         buf = buf.reshape(h, w, 4)
            
    #         # Convert RGBA to BGR for cv2
    #         self.output_frame = cv2.cvtColor(buf, cv2.COLOR_RGBA2BGR)
    #         title = f"polling result"

    #         # Create a black canvas of size (w, h)
    #         canvas = np.zeros((h, w, 3), dtype=np.uint8)
            
    #         # Calculate x offset to align output_frame to right
    #         x_offset = w - self.output_frame.shape[1]
            
    #         # Place output_frame on right side of canvas
    #         canvas[:self.output_frame.shape[0], x_offset:w] = self.output_frame
            
    #         # Update output_frame to be the full canvas
    #         self.output_frame = canvas


            
    #         # Display frame
    #         cv2.imshow(title, self.output_frame)
    #         cv2.waitKey(1)  # 1ms delay
    #         print(f"Time taken to render frame {frame}: {time.time() - s:.2f} seconds | FPS: {1/(time.time() - s):.2f}")
        

    #     end_time = time.time()
    #     print(f"Time taken to save video: {end_time - start_time:.2f} seconds")
    


if __name__ == "__main__":
    data = [('Apples', 50), ('Bananas', 30), ('Cherries', 20)]
    colors = ['darkred', 'yellow', 'pink']
    duration = 50
    video_path = 'pie_chart.mp4'
    # threading.Thread(target=PieChart).start()
    # PieChart().render(data, colors, duration, video_path, hold_time=5)

    pie_chart = PieChart()
    for i in range(50):
        pie_chart.render_single_frame(data, colors, duration, video_path, 50-i)