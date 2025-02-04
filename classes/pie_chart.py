import matplotlib.pyplot as plt
from matplotlib import animation


class PieChart:
    def __init__(self, data:list[tuple[str, int]], colors:list[str], duration:int, video_path:str):
        '''
        data: list of tuples (label, size) e.g. [('Apples', 50), ('Bananas', 0), ('Cherries', 10)]
        colors: list of mpl compatible colors e.g. ['darkred', 'yellow', 'pink']
        duration: duration of the animation in frames
        video_path: path to the video file
        '''
        self.fig, self.ax = plt.subplots()
        self.patches = None
        self.labels = None
        self.colors = None
        self.sizes = None
        self.duration = duration
        self.data = data
        self.colors = colors
        self.labels = [item[0] for item in data]
        self.init_sizes = [100 if i == 0 else 0 for i in range(len(data))] # the initial sizes
        self.sizes = [item[1] for item in data] # the dynamic sizes
        self.anim = None
        self.video_path = video_path

        # Calculate step sizes for each section to reach target values
        self.step_sizes = []
        # For each section, calculate how much it needs to change per frame
        for i, target in enumerate(self.sizes):
            # Start from 0 and increment to reach target
            step = (self.init_sizes[i] - target) / self.duration
            self.step_sizes.append(step)
        print(f'init_sizes: {self.init_sizes}')
        print(f'step_sizes: {self.step_sizes}')

        writer = animation.FFMpegWriter(fps=25)
        self.anim = animation.FuncAnimation(self.fig, self.animate, frames=self.duration, repeat=False, interval=25, blit=False)
        self.anim.save(self.video_path, writer=writer)

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
            print(f'i: {i}, section {j}: {current}')

        self.patches = plt.pie(current_sizes, colors=self.colors, startangle=90, shadow=True,
                     labels=self.labels, autopct='%1.0f%%',
                     textprops={'fontsize': 14, 'weight': 'bold'})
        return self.patches[0]  # Return only the patches, not the text elements

    # def render(self):
    #     '''Render the pie chart to a video file of a given name'''
    #     writer = animation.FFMpegWriter(fps=25)
    #     anim = animation.FuncAnimation(self.fig, self.animate, frames=self.duration, repeat=False, interval=25, blit=False)
    #     anim.save(self.video_path, writer=writer)
    #     return True


if __name__ == "__main__":
    data = [('Apples', 50), ('Bananas', 30), ('Cherries', 20)]
    colors = ['darkred', 'yellow', 'pink']
    duration = 50
    video_path = 'pie_chart.mp4'
    pie_chart = PieChart(data, colors, duration, video_path)
    # pie_chart.render()