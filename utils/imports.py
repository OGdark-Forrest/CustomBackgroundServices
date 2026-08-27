import customtkinter as ctk
import asyncio, ctypes, threading, subprocess, uvicorn, pyautogui

import pyaudio, torch, logging
from silero_vad import load_silero_vad, VADIterator

import json, time, os, datetime, sys, psutil, wmi, csv, monitorcontrol
from pathlib import Path

from fastapi import FastAPI, HTTPException, Header, APIRouter, Request
from fastapi.responses import Response, HTMLResponse

import mss
from PIL import Image
from io import BytesIO

import websockets
from contextlib import asynccontextmanager
from urllib.parse import urlencode, urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests, base64, webbrowser, uuid
from pydantic import BaseModel

from win11toast import toast
from winsdk.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager,
    GlobalSystemMediaTransportControlsSessionPlaybackStatus
)
from winsdk.windows.devices.bluetooth import (
    BluetoothDevice,
    BluetoothConnectionStatus,
)

import hmac, hashlib