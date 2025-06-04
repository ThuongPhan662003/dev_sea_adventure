import pygame
from os.path import join
from os import walk
from dotenv import load_dotenv
import os

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720

COLORS = {
    "black": "#000000",
    "red": "#ee1a0f",
    "gray": "gray",
    "white": "#ffffff",
    "blue": "#1a73e8",
    "dark_blue": "#174ea6",
    "light_gray": "#f0f0f0",
    "dark_gray": "#333333",
    "green": "#34a853",
    "yellow": "#fbbc05",
}
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 60
# Map for the game board
TILE_SIZE = 60
GAP = 10
LEN_MAP = 20
MAP_POSITIONS = []  # To store the positions of the tiles on the map

PORT = 5001
# Load biến môi trường từ file .env
load_dotenv()

# Lấy SERVER từ biến môi trường
server = os.getenv("SERVER_IP", "localhost")  # fallback = localhost nếu không có
