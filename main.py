#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import LineCollection
import random
from dataclasses import dataclass
from typing import List, Tuple, Dict, Set
import math
from scipy.spatial import Voronoi, voronoi_plot_2d
from collections import defaultdict
import json

@dataclass
class Point:
    x: float
    y: float
    
    def distance_to(self, other: 'Point') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

@dataclass
class Street:
    start: Point
    end: Point
    width: float = 0.02
    street_type: str = "main"

@dataclass
class Building:
    position: Point
    width: float
    height: float
    building_type: str = "residential"

@dataclass
class River:
    points: List[Point]
    width: float = 0.05

@dataclass
class Mountain:
    center: Point
    radius: float
    height: float

class LSystem:
    def __init__(self, axiom: str, rules: Dict[str, str]):
        self.axiom = axiom
        self.rules = rules
    
    def generate(self, iterations: int) -> str:
        result = self.axiom
        for _ in range(iterations):
            new_result = ""
            for char in result:
                new_result += self.rules.get(char, char)
            result = new_result
        return result

class StreetGenerator:
    def __init__(self, width: int = 100, height: int = 100):
        self.width = width
        self.height = height
        self.streets = []
        self.l_system = LSystem(
            axiom="F",
            rules={
                "F": "F+F-F-F+F",
                "+": "+",
                "-": "-"
            }
        )
    
    def generate_streets(self, iterations: int = 3) -> List[Street]:
        l_string = self.l_system.generate(iterations)
        x, y = self.width // 2, self.height // 2
        angle = 0
        step_size = 8
        angle_step = 90
        stack = []
        for char in l_string:
            if char == 'F':
                new_x = x + step_size * math.cos(math.radians(angle))
                new_y = y + step_size * math.sin(math.radians(angle))
                if 0 <= new_x <= self.width and 0 <= new_y <= self.height:
                    street = Street(
                        start=Point(x, y),
                        end=Point(new_x, new_y),
                        width=random.uniform(0.5, 2.0),
                        street_type=random.choice(["main", "secondary", "residential"])
                    )
                    self.streets.append(street)
                x, y = new_x, new_y
            elif char == '+':
                angle += angle_step
            elif char == '-':
                angle -= angle_step
            elif char == '[':
                stack.append((x, y, angle))
            elif char == ']':
                if stack:
                    x, y, angle = stack.pop()
        return self.streets

class VoronoiGenerator:
    def __init__(self, width: int = 100, height: int = 100):
        self.width = width
        self.height = height
        self.districts = []
    
    def generate_districts(self, num_points: int = 20) -> List[List[Point]]:
        points = np.random.uniform(0, max(self.width, self.height), (num_points, 2))
        vor = Voronoi(points)
        districts = []
        for region_idx in vor.point_region:
            region = vor.regions[region_idx]
            if -1 not in region and len(region) > 0:
                district_points = [Point(vor.vertices[i][0], vor.vertices[i][1]) 
                                 for i in region]
                districts.append(district_points)
        self.districts = districts
        return districts

class CellularAutomaton:
    def __init__(self, width: int = 100, height: int = 100):
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width))
    
    def generate_rivers(self, num_rivers: int = 3) -> List[River]:
        rivers = []
        for _ in range(num_rivers):
            if random.random() < 0.5:
                start_x = 0 if random.random() < 0.5 else self.width - 1
                start_y = random.randint(0, self.height - 1)
            else:
                start_x = random.randint(0, self.width - 1)
                start_y = 0 if random.random() < 0.5 else self.height - 1
            river_points = [Point(start_x, start_y)]
            current_x, current_y = start_x, start_y
            for _ in range(random.randint(20, 50)):
                if current_x < self.width // 2:
                    direction_x = random.choice([0, 1])
                else:
                    direction_x = random.choice([-1, 0])
                if current_y < self.height // 2:
                    direction_y = random.choice([0, 1])
                else:
                    direction_y = random.choice([-1, 0])
                new_x = max(0, min(self.width - 1, current_x + direction_x))
                new_y = max(0, min(self.height - 1, current_y + direction_y))
                if (new_x, new_y) != (current_x, current_y):
                    river_points.append(Point(new_x, new_y))
                    current_x, current_y = new_x, new_y
            rivers.append(River(
                points=river_points,
                width=random.uniform(0.5, 2.0)
            ))
        return rivers
    
    def generate_mountains(self, num_mountains: int = 5) -> List[Mountain]:
        mountains = []
        for _ in range(num_mountains):
            center = Point(
                random.uniform(0, self.width),
                random.uniform(0, self.height)
            )
            radius = random.uniform(5, 15)
            height = random.uniform(0.5, 1.0)
            mountains.append(Mountain(
                center=center,
                radius=radius,
                height=height
            ))
        return mountains

class BuildingGenerator:
    def __init__(self, width: int = 100, height: int = 100):
        self.width = width
        self.height = height
        self.buildings = []
    
    def generate_buildings(self, streets: List[Street], districts: List[List[Point]], 
                          num_buildings: int = 200) -> List[Building]:
        buildings = []
        for street in streets:
            street_length = street.start.distance_to(street.end)
            num_street_buildings = int(street_length / 3)
            for i in range(num_street_buildings):
                t = i / max(1, num_street_buildings - 1)
                pos_x = street.start.x + t * (street.end.x - street.start.x)
                pos_y = street.start.y + t * (street.end.y - street.start.y)
                offset_x = random.uniform(-1, 1)
                offset_y = random.uniform(-1, 1)
                building = Building(
                    position=Point(pos_x + offset_x, pos_y + offset_y),
                    width=random.uniform(0.5, 2.0),
                    height=random.uniform(0.5, 2.0),
                    building_type=random.choice(["residential", "commercial", "industrial"])
                )
                buildings.append(building)
        for district in districts:
            if len(district) < 3:
                continue
            center_x = sum(p.x for p in district) / len(district)
            center_y = sum(p.y for p in district) / len(district)
            district_buildings = random.randint(5, 15)
            for _ in range(district_buildings):
                pos_x = center_x + random.uniform(-10, 10)
                pos_y = center_y + random.uniform(-10, 10)
                building = Building(
                    position=Point(pos_x, pos_y),
                    width=random.uniform(0.5, 2.0),
                    height=random.uniform(0.5, 2.0),
                    building_type=random.choice(["residential", "commercial", "industrial"])
                )
                buildings.append(building)
        self.buildings = buildings
        return buildings

class CityGenerator:
    def __init__(self, width: int = 100, height: int = 100):
        self.width = width
        self.height = height
        self.street_generator = StreetGenerator(width, height)
        self.voronoi_generator = VoronoiGenerator(width, height)
        self.cellular_automaton = CellularAutomaton(width, height)
        self.building_generator = BuildingGenerator(width, height)
        self.streets = []
        self.districts = []
        self.rivers = []
        self.mountains = []
        self.buildings = []
    
    def generate_city(self, street_iterations: int = 3, num_districts: int = 20, 
                     num_rivers: int = 3, num_mountains: int = 5, 
                     num_buildings: int = 200):
        print("Генерация улиц...")
        self.streets = self.street_generator.generate_streets(street_iterations)
        print("Генерация районов...")
        self.districts = self.voronoi_generator.generate_districts(num_districts)
        print("Генерация рек...")
        self.rivers = self.cellular_automaton.generate_rivers(num_rivers)
        print("Генерация гор...")
        self.mountains = self.cellular_automaton.generate_mountains(num_mountains)
        print("Генерация зданий...")
        self.buildings = self.building_generator.generate_buildings(
            self.streets, self.districts, num_buildings
        )
        print(f"Город сгенерирован!")
        print(f"- Улиц: {len(self.streets)}")
        print(f"- Районов: {len(self.districts)}")
        print(f"- Рек: {len(self.rivers)}")
        print(f"- Гор: {len(self.mountains)}")
        print(f"- Зданий: {len(self.buildings)}")
    
    def visualize(self, save_path: str = None):
        import matplotlib
        matplotlib.use('Agg')
        fig, ax = plt.subplots(1, 1, figsize=(12, 12))
        for mountain in self.mountains:
            circle = patches.Circle(
                (mountain.center.x, mountain.center.y),
                mountain.radius,
                color='brown',
                alpha=0.3,
                zorder=1
            )
            ax.add_patch(circle)
        for river in self.rivers:
            if len(river.points) > 1:
                x_coords = [p.x for p in river.points]
                y_coords = [p.y for p in river.points]
                ax.plot(x_coords, y_coords, 'b-', linewidth=river.width, alpha=0.7, zorder=2)
        for district in self.districts:
            if len(district) >= 3:
                x_coords = [p.x for p in district] + [district[0].x]
                y_coords = [p.y for p in district] + [district[0].y]
                ax.plot(x_coords, y_coords, 'g-', alpha=0.3, linewidth=1, zorder=3)
        for street in self.streets:
            ax.plot([street.start.x, street.end.x], 
                   [street.start.y, street.end.y], 
                   'k-', linewidth=street.width, zorder=4)
        for building in self.buildings:
            color = 'red' if building.building_type == 'residential' else \
                   'blue' if building.building_type == 'commercial' else 'gray'
            rect = patches.Rectangle(
                (building.position.x - building.width/2, 
                 building.position.y - building.height/2),
                building.width,
                building.height,
                color=color,
                alpha=0.7,
                zorder=5
            )
            ax.add_patch(rect)
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.set_aspect('equal')
        ax.set_title('Сгенерированный город', fontsize=16)
        ax.grid(True, alpha=0.3)
        legend_elements = [
            patches.Patch(color='brown', alpha=0.3, label='Горы'),
            patches.Patch(color='blue', alpha=0.7, label='Реки'),
            patches.Patch(color='green', alpha=0.3, label='Районы'),
            patches.Patch(color='black', label='Улицы'),
            patches.Patch(color='red', alpha=0.7, label='Жилые здания'),
            patches.Patch(color='blue', alpha=0.7, label='Коммерческие здания'),
            patches.Patch(color='gray', alpha=0.7, label='Промышленные здания')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Изображение сохранено: {save_path}")
        plt.close()
    
    def save_city_data(self, filename: str = "city_data.json"):
        city_data = {
            "width": self.width,
            "height": self.height,
            "streets": [
                {
                    "start": {"x": s.start.x, "y": s.start.y},
                    "end": {"x": s.end.x, "y": s.end.y},
                    "width": s.width,
                    "type": s.street_type
                } for s in self.streets
            ],
            "buildings": [
                {
                    "position": {"x": b.position.x, "y": b.position.y},
                    "width": b.width,
                    "height": b.height,
                    "type": b.building_type
                } for b in self.buildings
            ],
            "rivers": [
                {
                    "points": [{"x": p.x, "y": p.y} for p in r.points],
                    "width": r.width
                } for r in self.rivers
            ],
            "mountains": [
                {
                    "center": {"x": m.center.x, "y": m.center.y},
                    "radius": m.radius,
                    "height": m.height
                } for m in self.mountains
            ]
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(city_data, f, ensure_ascii=False, indent=2)
        print(f"Данные города сохранены: {filename}")

def main():
    print("=== Генератор городов ===")
    print("Использует L-системы, алгоритм Voronoi и клеточные автоматы")
    print()
    city_gen = CityGenerator(width=100, height=100)
    city_gen.generate_city(
        street_iterations=3,
        num_districts=20,
        num_rivers=3,
        num_mountains=5,
        num_buildings=200
    )
    city_gen.visualize(save_path="generated_city.png")
    city_gen.save_city_data("city_data.json")
    print("\nГенерация завершена!")

if __name__ == "__main__":
    main()
