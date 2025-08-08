# backend/logic.py

import matplotlib
matplotlib.use('Agg')

import os
import json
import pandas as pd
from collections import Counter
import mplfinance as mpf
import ccxt
import google.generativeai as genai
from dotenv import load_dotenv
from rich.console import Console
import re
import time

# --- НАСТРОЙКА ---
load_dotenv()
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    exchange = ccxt.binance()
    console = Console()
except Exception as e:
    print(f"❌ Ошибка конфигурации API: {e}")
    exit()

# <--- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ-КАЛЬКУЛЯТОРЫ --->
# ... (все ваши функции-калькуляторы, такие как calculate_rsi, остаются здесь без изменений) ...
def calculate_rsi(series: pd.Series, length: int = 14) -> pd.Series:
    delta = series.diff(); gain = delta.where(delta > 0, 0); loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(com=length - 1, min_periods=length).mean(); avg_loss = loss.ewm(com=length - 1, min_periods=length).mean()
    if avg_loss.empty or (avg_loss == 0).all(): return pd.Series(100.0, index=series.index)
    rs = avg_gain / avg_loss; return 100 - (100 / (1 + rs))

def calculate_bbands(series: pd.Series, length: int = 20, std: int = 2):
    middle_band = series.rolling(window=length).mean(); std_dev = series.rolling(window=length).std()
    upper_band = middle_band + (std_dev * std); lower_band = middle_band - (std_dev * std)
    return upper_band, lower_band

# <--- ОСНОВНЫЕ ФУНКЦИИ --- >

def fetch_and_plot(symbol: str, timeframe: str) -> str:
    """Создает один график для указанного таймфрейма."""
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=200)
        if len(ohlcv) < 50: return None
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms'); df.set_index('timestamp', inplace=True)
        os.makedirs("temp_charts", exist_ok=True)

        df['RSI'] = calculate_rsi(df['close']); df['BBU'], df['BBL'] = calculate_bbands(df['close'])
        addplots = [
            mpf.make_addplot(df['BBU'], color='cyan', width=0.7), mpf.make_addplot(df['BBL'], color='cyan', width=0.7),
            mpf.make_addplot(df['RSI'], panel=1, color='purple', title="RSI", ylim=(0, 100))
        ]
        plot_kwargs = dict(type='candle', style='charles', volume=True, figratio=(16, 9), addplot=addplots, mav=(9, 21, 50),
                           title=f"Analysis for {symbol} - {timeframe}")
        
        # Имя файла теперь не зависит от номера прогона
        filepath = f"temp_charts/analysis_{symbol.replace('/', '')}_{timeframe}.png"
        mpf.plot(df, **plot_kwargs, savefig=dict(fname=filepath, dpi=100))
        return filepath if os.path.exists(filepath) else None
    except Exception as e:
        console.print(f"❌ Не удалось создать график для {timeframe}: {e}"); return None

def clean_json_response(raw_text: str) -> dict:
    match = re.search(r'```json\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
    cleaned_text = match.group(1) if match else raw_text.replace('```', '').strip()
    try: return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        console.print(f"❌ Ошибка декодирования JSON: {e}\n   Текст: {cleaned_text}"); return None

def analyze_with_gemini(image_paths: list, prompt_file: str, prompt_kwargs: dict):
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f: prompt_template = f.read()
        prompt = prompt_template.format(**prompt_kwargs)
    except FileNotFoundError:
        console.print(f"❌ Промпт не найден: {prompt_file}"); return None

    uploaded_files = [genai.upload_file(path=p) for p in image_paths if p and os.path.exists(p)]
    if not uploaded_files: return None

    model = genai.GenerativeModel('gemini-2.5-pro')
    safety_settings = {k: 'BLOCK_NONE' for k in ['HARM_CATEGORY_HARASSMENT', 'HARM_CATEGORY_HATE_SPEECH', 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'HARM_CATEGORY_DANGEROUS_CONTENT']}
    
    try:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = model.generate_content([prompt] + uploaded_files, safety_settings=safety_settings)
                if not response.parts:
                    console.print(f"❌ [bold red]Ответ от Gemini был заблокирован. Пропускаем.[/bold red]"); return None
                return clean_json_response(response.text)
            except Exception as e:
                console.print(f"🟡 Ошибка API (попытка {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1: time.sleep(5)
                else: console.print(f"❌ Не удалось получить ответ после {max_retries} попыток."); return None
    finally:
        for f in uploaded_files:
            try: genai.delete_file(f.name)
            except Exception: pass

def run_full_analysis(pair: str, strategy_key: str):
    try:
        with open('config.json', 'r', encoding='utf-8') as f: config = json.load(f)
        strategy = config['strategies'][strategy_key]
    except (FileNotFoundError, KeyError): return {"error": f"Стратегия '{strategy_key}' не найдена."}

    try:
        current_price = exchange.fetch_ticker(pair)['last']
    except Exception as e: return {"error": f"Не удалось получить цену для {pair}: {e}"}

    console.print(f"\n[bold cyan]--- Генерация идеи для {pair} ---[/bold cyan]")
    console.print("🖼️  Создание набора графиков для анализа...")
    chart_paths = [fetch_and_plot(pair, tf) for tf in strategy['timeframes']]
    valid_charts = [p for p in chart_paths if p]
    if not valid_charts: return {"status": "no_signal", "message": "Не удалось создать графики для анализа."}

    # --- НОВАЯ ОТКАЗОУСТОЙЧИВАЯ ЛОГИКА ---
    TARGET_SUCCESSFUL_RUNS = 3
    MAX_ATTEMPTS = 5
    results = []
    
    console.print(f"🤖 Собираем {TARGET_SUCCESSFUL_RUNS} мнения от AI (максимум {MAX_ATTEMPTS} попыток)...")
    for i in range(1, MAX_ATTEMPTS + 1):
        console.print(f"--- Попытка №{i} ---")
        prompt_kwargs = {'symbol': pair, 'current_price': current_price}
        trade_idea = analyze_with_gemini(valid_charts, strategy['prompt_file'], prompt_kwargs)
        
        if trade_idea and trade_idea.get('direction', 'None').lower() != 'none':
            results.append(trade_idea)
            console.print(f"[green]✅ Успешный анализ получен ({len(results)}/{TARGET_SUCCESSFUL_RUNS})[/green]")
        
        if len(results) >= TARGET_SUCCESSFUL_RUNS:
            console.print(f"🎯 Цель в {TARGET_SUCCESSFUL_RUNS} успешных анализа достигнута.")
            break
    # --- КОНЕЦ НОВОЙ ЛОГИКИ ---

    if not results:
        for p in valid_charts: os.remove(p)
        return {"status": "no_signal", "message": "ИИ не нашел качественных торговых сетапов."}

    directions = [r.get('direction') for r in results]
    direction_counts = Counter(directions)
    
    if not direction_counts or direction_counts.most_common(1)[0][1] < 2:
        for p in valid_charts: os.remove(p)
        return {"status": "ambiguous", "message": "Рыночная ситуация НЕОДНОЗНАЧНАЯ.", "details": dict(direction_counts)}
        
    most_common_direction, count = direction_counts.most_common(1)[0]
    confident_result = next(r for r in results if r.get('direction') == most_common_direction)
    
    console.print(f"\n[bold green]--- Анализ завершен. Консенсус найден: {count}/{len(results)} за {most_common_direction} ---[/bold green]")
    
    final_result = confident_result
    final_result.update({
        'status': 'success',
        'chart_images': [os.path.basename(p) for p in valid_charts],
        'consensus': f"{count}/{len(results)}"
    })

    return final_result
