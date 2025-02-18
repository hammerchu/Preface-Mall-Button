import matplotlib.pyplot as plt
from matplotlib import animation
import time
import cv2
import threading
import numpy as np
class PieChart:
    def __init__(self):
        '''
        data: list of tuples (label, size) e.g. [('Apples', 50), ('Bananas', 0), ('Cherries', 10)]
        colors: list of mpl compatible colors e.g. ['darkred', 'yellow', 'pink']
        duration: duration of the animation in frames
        video_path: path to the video file
        '''
        # Set fixed figure size and DPI
        self.fig, self.ax = plt.subplots(figsize=(8, 6), dpi=100)
        self.ax.axis('equal')
        self.patches = None
        self.labels = None
        self.colors = None
        self.sizes = None
        # self.duration = duration
        # self.data = data
        # self.colors = colors
        # self.labels = [item[0] for item in data]
        # self.init_sizes = [100 if i == 0 else 0 for i in range(len(data))] # the initial sizes
        # self.sizes = [item[1] for item in data] # the dynamic sizes
        # self.anim = None
        # self.video_path = video_path
        # self.hold_time = hold_time
        # # Calculate step sizes for each section to reach target values
        # self.step_sizes = []
        # # For each section, calculate how much it needs to change per frame
        # for i, target in enumerate(self.sizes):
        #     # Start from 0 and increment to reach target
        #     step = (self.init_sizes[i] - target) / self.duration
        #     self.step_sizes.append(step)
        # # print(f'init_sizes: {self.init_sizes}')
        # # print(f'step_sizes: {self.step_sizes}')
        # start_time = time.time()
        # writer = animation.FFMpegWriter(fps=25)
        # self.anim = animation.FuncAnimation(self.fig, self.animate, frames=self.duration, repeat=False, interval=25, blit=False)
        # self.anim.save(self.video_path, writer=writer)

        # # Add hold time by duplicating the last frame
        # if self.hold_time > 0:
        #     # Get the last frame from the saved video
        #     cap = cv2.VideoCapture(self.video_path)
        #     fps = cap.get(cv2.CAP_PROP_FPS)
        #     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        #     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
        #     # Read all frames
        #     frames = []
        #     while cap.isOpened():
        #         ret, frame = cap.read()
        #         if not ret:
        #             break
        #         frames.append(frame)
        #     cap.release()
            
        #     # Create new video with hold time
        #     out = cv2.VideoWriter(self.video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
            
        #     # Write original frames
        #     for frame in frames:
        #         out.write(frame)
                
        #     # Duplicate last frame for hold duration
        #     last_frame = frames[-1]
        #     for _ in range(int(fps * self.hold_time)):
        #         out.write(last_frame)
                
        #     out.release()
        #     print(f"Video saved with hold time: {self.hold_time} seconds")

        # end_time = time.time()
        # print(f"Time taken to save video: {end_time - start_time:.2f} seconds")

        self.render(data, colors, duration, video_path, hold_time=5)

    def render(self, data:list[tuple[str, int]], colors:list[str], duration:int, video_path:str, hold_time:int=0):
        self.duration = duration
        self.data = data
        self.colors = colors
        self.labels = [item[0] for item in data]
        self.init_sizes = [100 if i == 0 else 0 for i in range(len(data))] # the initial sizes
        self.sizes = [item[1] for item in data] # the dynamic sizes
        self.anim = None
        self.video_path = video_path
        self.hold_time = hold_time
        # Calculate step sizes for each section to reach target values
        self.step_sizes = []
        # For each section, calculate how much it needs to change per frame
        for i, target in enumerate(self.sizes):
            # Start from 0 and increment to reach target
            step = (self.init_sizes[i] - target) / self.duration
            self.step_sizes.append(step)
        # print(f'init_sizes: {self.init_sizes}')
        # print(f'step_sizes: {self.step_sizes}')
        start_time = time.time()
        writer = animation.FFMpegWriter(fps=25)
        # self.anim = animation.FuncAnimation(self.fig, self.animate, frames=self.duration, repeat=False, interval=25, blit=False)
        
        # Convert matplotlib animation to frames and display
        for frame in range(self.duration):
            s = time.time()
            # Render the frame
            self.animate(frame)
            
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
            img = cv2.cvtColor(buf, cv2.COLOR_RGBA2BGR)
            
            # Display frame
            cv2.imshow('Pie Chart Animation', img)
            cv2.waitKey(1)  # 1ms delay
            print(f"Time taken to render frame {frame}: {time.time() - s:.2f} seconds | FPS: {1/(time.time() - s):.2f}")
        # Save final animation
        # self.anim.save(self.video_path, writer=writer)

        # # Convert matplotlib figure to cv2 format
        # canvas = self.fig.canvas
        # canvas.draw()
        
        # # Get correct dimensions from the figure
        # w, h = self.fig.get_size_inches() * self.fig.dpi
        # w, h = int(w), int(h)
        
        # # Get buffer and reshape properly
        # buf = np.frombuffer(canvas.buffer_rgba(), dtype=np.uint8)
        # buf = buf.reshape(h, w, 4)  # Note: height comes first
        
        # # Convert RGBA to BGR
        # img = cv2.cvtColor(buf, cv2.COLOR_RGBA2BGR)
        
        # # Display with cv2
        # cv2.imshow('Pie Chart Animation', img)
        # cv2.waitKey(1)

        # self.anim.save(self.video_path, writer=writer)

        # Add hold time by duplicating the last frame
        # if self.hold_time > 0:
        #     # Get the last frame from the saved video
        #     cap = cv2.VideoCapture(self.video_path)
        #     fps = cap.get(cv2.CAP_PROP_FPS)
        #     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        #     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
        #     # Read all frames
        #     frames = []
        #     while cap.isOpened():
        #         ret, frame = cap.read()
        #         if not ret:
        #             break
        #         frames.append(frame)
        #     cap.release()
            
        #     # Create new video with hold time
        #     out = cv2.VideoWriter(self.video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
            
        #     # Write original frames
        #     for frame in frames:
        #         out.write(frame)
                
        #     # Duplicate last frame for hold duration
        #     last_frame = frames[-1]
        #     for _ in range(int(fps * self.hold_time)):
        #         out.write(last_frame)
                
        #     out.release()
        #     print(f"Video saved with hold time: {self.hold_time} seconds")

        end_time = time.time()
        print(f"Time taken to save video: {end_time - start_time:.2f} seconds")

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



if __name__ == "__main__":
    data = [('Apples', 50), ('Bananas', 30), ('Cherries', 20)]
    colors = ['darkred', 'yellow', 'pink']
    duration = 50
    video_path = 'pie_chart.mp4'
    # threading.Thread(target=PieChart).start()
    PieChart().render(data, colors, duration, video_path, hold_time=5)