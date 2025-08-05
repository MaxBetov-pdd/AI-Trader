# -*- coding: utf-8 -*-
# Полное содержимое файла backend/logic.py (с исправлением для Matplotlib)

import matplotlib
matplotlib.use('Agg') # <-- ВАЖНОЕ ИСПРАВЛЕНИЕ: говорим Matplotlib не использовать GUI

import os
import json
import pandas as pd
from collections import Counter
import mplfinance as mpf
import ccxt
import google.generativeai as genai
from dotenv import load_dotenv
from rich.console import Console

# --- НАСТРОЙКА ---
# (остальной код остается без изменений)
load_dotenv()
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    exchange = ccxt.binance()
    console = Console()
except Exception as e:
    print(f"❌ Ошибка конфигурации API: {e}")
    exit()

# <--- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ --->
# (Этот блок остается без изменений)
def calculate_rsi(series: pd.Series, length: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(com=length - 1, min_periods=length).mean()
    avg_loss = loss.ewm(com=length - 1, min_periods=length).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_bbands(series: pd.Series, length: int = 20, std: int = 2):
    middle_band = series.rolling(window=length).mean()
    std_dev = series.rolling(window=length).std()
    upper_band = middle_band + (std_dev * std)
    lower_band = middle_band - (std_dev * std)
    return upper_band, lower_band

def calculate_atr(df, length=14):
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    tr = high_low.combine(high_close, max).combine(low_close, max)
    atr = tr.ewm(alpha=1/length, adjust=False).mean()
    return atr

def calculate_adx(df, length=14):
    df['ATR'] = calculate_atr(df, length)
    plus_dm = df['high'].diff()
    minus_dm = df['low'].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    plus_di = 100 * (plus_dm.ewm(alpha=1/length, adjust=False).mean() / df['ATR'])
    minus_di = 100 * (abs(minus_dm.ewm(alpha=1/length, adjust=False).mean()) / df['ATR'])
    dx = 100 * (abs(plus_di - minus_di) / (abs(plus_di + minus_di) + 1e-6))
    adx = dx.ewm(alpha=1/length, adjust=False).mean()
    df[f'ADX_{length}'] = adx
    return df

# <--- ОСНОВНЫЕ ФУНКЦИИ --->
# (Этот блок остается без изменений)
def fetch_and_plot(symbol: str, timeframe: str, run_id: int) -> str:
    try:
        # Добавим вывод текущей цены для отладки
        ticker = exchange.fetch_ticker(symbol)
        print(f"Текущая цена для {symbol}: {ticker['last']}")
        
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=200)
        if len(ohlcv) < 50:
            console.print(f"⚠️  Недостаточно данных для {timeframe}, пропускаем график.")
            return None
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df = calculate_adx(df, length=14)
        latest_adx = df.iloc[-1]['ADX_14'] if not df.empty and 'ADX_14' in df.columns else 20
        params = {"rsi_length": 21, "bb_length": 25, "bb_std": 2.5} if latest_adx > 25 else {"rsi_length": 14, "bb_length": 20, "bb_std": 2.0}
        params["mode"] = "Trend" if latest_adx > 25 else "Flat/Range"
        df['RSI'] = calculate_rsi(df['close'], length=params["rsi_length"])
        df['BBU'], df['BBL'] = calculate_bbands(df['close'], length=params["bb_length"], std=params["bb_std"])
        
        os.makedirs("temp_charts", exist_ok=True)
        filepath = f"temp_charts/chart_{symbol.replace('/', '')}_{timeframe}_{run_id}.png"
        rsi_title = f"RSI ({params['rsi_length']}) - {params['mode']} Mode"
        all_plots = [mpf.make_addplot(df['BBU'], color='cyan', width=0.7), mpf.make_addplot(df['BBL'], color='cyan', width=0.7), mpf.make_addplot(df['RSI'], panel=1, color='purple', title=rsi_title, ylim=(0, 100))]
        mpf.plot(df, type='candle', style='charles', title=f"\n{symbol} - {timeframe}", mav=(9, 21, 50), volume=True, figratio=(16, 9), addplot=all_plots, savefig=dict(fname=filepath, dpi=100))
        
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1024:
            return filepath
        else:
            console.print(f"❌ Ошибка: Создан пустой или некорректный файл графика для {timeframe}.")
            if os.path.exists(filepath): os.remove(filepath)
            return None
    except Exception as e:
        console.print(f"❌ (Прогон {run_id}) Не удалось создать график для {timeframe}: {e}")
        return None

def analyze_with_gemini(symbol: str, image_paths: list, run_id: int, prompt_file: str):
    console.print(f"🧠 (Прогон {run_id}) Анализ в Gemini по стратегии...")
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
        prompt = prompt_template.format(symbol=symbol)
    except FileNotFoundError:
        console.print(f"[bold red]Ошибка: Файл с промптом не найден: {prompt_file}[/bold red]")
        return None

    uploaded_files = []
    for path in image_paths:
        try:
            console.print(f"  [dim]Загрузка {path}...[/dim]")
            uploaded_files.append(genai.upload_file(path=path))
        except Exception as e:
            console.print(f"❌ [bold red]Не удалось загрузить файл {path}: {e}[/bold red]")
    
    if not uploaded_files:
        console.print("❌ [bold red]Ни один файл с графиком не был успешно загружен. Анализ невозможен.[/bold red]")
        return None

    model = genai.GenerativeModel('gemini-2.5-pro')
    safety_settings = { 'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE', 'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE', 'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE', 'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE' }
    
    try:
        response = model.generate_content([prompt] + uploaded_files, safety_settings=safety_settings)
        raw_text = response.text
        cleaned_text = raw_text.strip().replace('```json', '').replace('```', '')
        return json.loads(cleaned_text)
    except Exception as e:
        console.print(f"❌ [bold red]Ошибка при вызове Gemini API или обработке ответа:[/bold red] {e}")
        if hasattr(response, 'prompt_feedback'):
             console.print(f"    [bold]Причина блокировки:[/bold] {response.prompt_feedback}")
        return None
    finally:
        for uploaded_file in uploaded_files:
            genai.delete_file(uploaded_file.name)
            console.print(f"  [dim]Удален временный файл Gemini: {uploaded_file.name}[/dim]")
        for p in image_paths:
            if p and os.path.exists(p): os.remove(p)

def run_full_analysis(pair: str, strategy_key: str):
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        strategy = config['strategies'][strategy_key]
    except (FileNotFoundError, KeyError):
        return {"error": f"Стратегия '{strategy_key}' или config.json не найдены."}

    NUMBER_OF_RUNS = 3
    results = []
    
    for i in range(1, NUMBER_OF_RUNS + 1):
        timeframes = strategy['timeframes']
        prompt_file = strategy['prompt_file']
        chart_paths = [fetch_and_plot(pair, tf, run_id=i) for tf in timeframes]
        
        valid_chart_paths = [p for p in chart_paths if p]
        if not valid_chart_paths:
            console.print(f"❌ (Прогон {i}) Не удалось создать ни одного графика. Анализ пропущен.")
            continue

        trade_idea = analyze_with_gemini(pair, valid_chart_paths, run_id=i, prompt_file=prompt_file)
        if trade_idea and trade_idea.get('direction') and trade_idea.get('direction').lower() != 'none':
            results.append(trade_idea)

    if not results:
        return {"status": "no_signal", "message": "ИИ не нашел качественных торговых сетапов по выбранной стратегии."}

    directions = [r.get('direction') for r in results]
    direction_counts = Counter(directions)
    most_common_direction, count = direction_counts.most_common(1)[0]
    
    if count >= 2:
        confident_result = next(r for r in results if r.get('direction') == most_common_direction)
        confident_result['status'] = 'success'
        confident_result['consensus'] = f"{count}/{len(results)}"
        return confident_result
    else:
        return {
            "status": "ambiguous", 
            "message": "Рыночная ситуация НЕОДНОЗНАЧНАЯ. ИИ дал противоречивые сигналы.",
            "details": dict(direction_counts)
        }
