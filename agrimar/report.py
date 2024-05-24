import matplotlib.pyplot as plt
import datetime

def create_soil_graph(layer, file_name):
    depths = [d['label'] for d in layer['depths']]
    values = [d['values']['mean'] for d in layer['depths']]
    
    plt.figure(figsize=(10, 6))
    plt.plot(depths, values, marker='o', linestyle='-', color='b')
    if layer['name'] == 'sand': layer['name']='sable'
    if layer['name'] == 'clay': layer['name']='argile'
    if layer['name'] == 'silt': layer['name']='limon'
    plt.title(f"{layer['name'].upper()} Niveaux par profondeur")
    plt.xlabel('Profondeur')
    plt.ylabel(f"{layer['unit_measure']['target_units']}")
    plt.grid(True)
    plt.savefig(file_name)
    plt.close()

def create_weather_graphs(dates, values, title, ylabel, filename , color = 'b'):

    plt.figure(figsize=(10, 6))
    plt.plot(dates, values, marker='o', color=color)
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


