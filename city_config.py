#!/usr/bin/env python3
"""
Конфигурационный файл для настройки параметров генерации города
"""

# Размеры города
CITY_WIDTH = 100
CITY_HEIGHT = 100

# Параметры L-системы для улиц
STREET_ITERATIONS = 3
STREET_RULES = {
    "F": "F+F-F-F+F",  # Основное правило для улиц
    "+": "+",
    "-": "-"
}

# Параметры диаграммы Вороного
NUM_DISTRICTS = 20

# Параметры клеточного автомата
NUM_RIVERS = 3
NUM_MOUNTAINS = 5

# Параметры генерации зданий
NUM_BUILDINGS = 200

# Цвета для визуализации
COLORS = {
    "mountains": "brown",
    "rivers": "blue", 
    "districts": "green",
    "streets": "black",
    "residential": "red",
    "commercial": "blue",
    "industrial": "gray"
}

# Настройки L-системы для различных типов улиц
STREET_L_SYSTEMS = {
    "main": {
        "axiom": "F",
        "rules": {"F": "F+F-F-F+F", "+": "+", "-": "-"},
        "iterations": 4,
        "width": 2.0
    },
    "secondary": {
        "axiom": "F",
        "rules": {"F": "F-F+F+F-F", "+": "+", "-": "-"},
        "iterations": 3,
        "width": 1.5
    },
    "residential": {
        "axiom": "F",
        "rules": {"F": "F[+F]F[-F]F", "+": "+", "-": "-", "[": "[", "]": "]"},
        "iterations": 2,
        "width": 1.0
    }
}

# Параметры рек
RIVER_CONFIG = {
    "min_length": 20,
    "max_length": 50,
    "min_width": 0.5,
    "max_width": 2.0
}

# Параметры гор
MOUNTAIN_CONFIG = {
    "min_radius": 5,
    "max_radius": 15,
    "min_height": 0.5,
    "max_height": 1.0
}

# Параметры зданий
BUILDING_CONFIG = {
    "residential": {
        "min_width": 0.5,
        "max_width": 2.0,
        "min_height": 0.5,
        "max_height": 2.0,
        "density": 0.8
    },
    "commercial": {
        "min_width": 1.0,
        "max_width": 3.0,
        "min_height": 1.0,
        "max_height": 3.0,
        "density": 0.6
    },
    "industrial": {
        "min_width": 2.0,
        "max_width": 4.0,
        "min_height": 1.5,
        "max_height": 2.5,
        "density": 0.4
    }
}
