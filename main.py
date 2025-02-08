from classes.pie_chart import PieChart
import time


'''Example of how can you use the PieChart class'''

data = [('Americano', 50), ('Flat white', 40), ('Latte', 10)]
colors = ['darkred', 'green', 'pink']
duration = 35
video_path = 'pie_animation_drinks.mp4'

s = time.time()
pie_chart = PieChart(data, colors, duration, video_path)
print(f'Time taken: {time.time() - s}')