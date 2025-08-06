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

# --- НАСТРОЙКА ---
load_dotenv()
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    exchange = ccxt.binance()
    console = Console()
except Exception as e:
    print(f"❌ Ошибка конфигурации API: {e}")
    exit()

# <--- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ --->
# ... (оставьте здесь все ваши функции-калькуляторы: calculate_rsi и т.д.) ...

# <--- ОСНОВНЫЕ ФУНКЦИИ --- >

def fetch_and_plot(symbol: str, timeframe: str, run_id: int, trade_idea: dict = None) -> str:
    """
    Универсальная функция: создает график. Если передан 'trade_idea', наносит на него линии.
    """
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=200)
        if len(ohlcv) < 50: return None
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        os.makedirs("temp_charts", exist_ok=True)
        
        plot_kwargs = dict(type='candle', style='charles', volume=True, figratio=(16, 9))
        
        if trade_idea:
            hlines_data, colors = [], []
            if trade_idea.get('entry_price') and str(trade_idea.get('entry_type', '')).lower() == 'limit':
                hlines_data.append(float(trade_idea['entry_price']))
                colors.append('blue')
            if trade_idea.get('take_profit'):
                hlines_data.append(float(trade_idea['take_profit']))
                colors.append('green')
            if trade_idea.get('stop_loss'):
                hlines_data.append(float(trade_idea['stop_loss']))
                colors.append('red')
            
            filepath = f"temp_charts/setup_{symbol.replace('/', '')}_{timeframe}_{run_id}.png"
            plot_kwargs['title'] = f"AI Setup for {symbol} - {timeframe}"
            plot_kwargs['hlines'] = dict(hlines=hlines_data, colors=colors, linestyle='-.', linewidths=1.2)
        else:
            filepath = f"temp_charts/initial_{symbol.replace('/', '')}_{timeframe}_{run_id}.png"
            plot_kwargs['title'] = f"Initial Analysis for {symbol} - {timeframe}"
            plot_kwargs['mav'] = (9, 21, 50)
            
        mpf.plot(df, **plot_kwargs, savefig=dict(fname=filepath, dpi=100))
        return filepath if os.path.exists(filepath) else None
    except Exception as e:
        console.print(f"❌ Не удалось создать график для {timeframe}: {e}")
        return None

def clean_json_response(raw_text: str) -> dict:
    """Очищает ответ от Gemini и декодирует его."""
    match = re.search(r'```json\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
    cleaned_text = match.group(1) if match else raw_text.replace('```', '').strip()
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        console.print(f"❌ Ошибка декодирования JSON: {e}\n   Текст: {cleaned_text}")
        return None

def analyze_with_gemini(symbol: str, image_paths: list, run_id: int, prompt_file: str, **kwargs):
    console.print(f"🧠 (Прогон {run_id}) Вызов Gemini с промптом '{prompt_file}'...")
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f: prompt_template = f.read()
        prompt = prompt_template.format(symbol=symbol, **kwargs)
    except FileNotFoundError:
        return None

    uploaded_files = [genai.upload_file(path=p) for p in image_paths if p and os.path.exists(p)]
    if not uploaded_files: return None

    model = genai.GenerativeModel('gemini-2.5-pro')
    safety_settings = {k: 'BLOCK_NONE' for k in ['HARM_CATEGORY_HARASSMENT', 'HARM_CATEGORY_HATE_SPEECH', 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'HARM_CATEGORY_DANGEROUS_CONTENT']}
    
    try:
        response = model.generate_content([prompt] + uploaded_files, safety_settings=safety_settings)
        return clean_json_response(response.text)
    except Exception as e:
        console.print(f"❌ Ошибка API Gemini: {e}")
        return None
    finally:
        for f in uploaded_files: genai.delete_file(f.name)

def run_full_analysis(pair: str, strategy_key: str):
    try:
        with open('config.json', 'r', encoding='utf-8') as f: config = json.load(f)
        strategy = config['strategies'][strategy_key]
    except (FileNotFoundError, KeyError):
        return {"error": f"Стратегия '{strategy_key}' не найдена."}
    
    # --- ЭТАП 1: ПОИСК КОНСЕНСУСА ---
    console.print(f"\n[bold cyan]--- Этап 1: Поиск консенсуса для {pair} ---[/bold cyan]")
    try:
        current_price = exchange.fetch_ticker(pair)['last']
    except Exception as e:
        return {"error": f"Не удалось получить цену для {pair}: {e}"}

    NUMBER_OF_RUNS = 3
    results = []
    timeframes = strategy['timeframes']
    prompt_file = strategy['prompt_file']

    for i in range(1, NUMBER_OF_RUNS + 1):
        chart_paths = [fetch_and_plot(pair, tf, i) for tf in timeframes]
        valid_charts = [p for p in chart_paths if p]
        if valid_charts:
            trade_idea = analyze_with_gemini(pair, valid_charts, i, prompt_file, current_price=current_price)
            if trade_idea and trade_idea.get('direction', 'None').lower() != 'none':
                results.append(trade_idea)
        for p in valid_charts: os.remove(p)

    if not results:
        return {"status": "no_signal", "message": "ИИ не нашел качественных торговых сетапов."}

    directions = [r.get('direction') for r in results]
    direction_counts = Counter(directions)
    most_common_direction, count = direction_counts.most_common(1)[0]

    if count < 2:
        return {"status": "ambiguous", "message": "Рыночная ситуация НЕОДНОЗНАЧНАЯ. ИИ дал противоречивые сигналы.", "details": dict(direction_counts)}

    confident_result = next(r for r in results if r.get('direction') == most_common_direction)
    confident_result['consensus'] = f"{count}/{len(results)}"
    
    # --- ЭТАП 2: ВАЛИДАЦИЯ ЧЕРЕЗ САМОАНАЛИЗ ---
    console.print(f"\n[bold cyan]--- Этап 2: Валидация сетапа через самоанализ (Консенсус: {confident_result['consensus']}) ---[/bold cyan]")
    
    setup_charts = [fetch_and_plot(pair, tf, 99, trade_idea=confident_result) for tf in timeframes]
    valid_setup_charts = [p for p in setup_charts if p]
    if not valid_setup_charts:
        return {"error": "Не удалось создать графики с сетапом для самоанализа."}
        
    final_trade_idea = analyze_with_gemini(
        pair, valid_setup_charts, 99, "prompts/self_analysis_prompt.txt",
        current_price=current_price, base_idea_str=json.dumps(confident_result, indent=2, ensure_ascii=False)
    )
    
    if not final_trade_idea or final_trade_idea.get('direction', 'None').lower() == 'none':
        for p in valid_setup_charts: os.remove(p)
        return {"status": "no_signal", "message": "Сетап был отвергнут ИИ на этапе самоанализа."}
        
    final_trade_idea.update({
        'status': 'success',
        'chart_images': valid_setup_charts,
        'consensus': confident_result['consensus']
    })

    return final_trade_idea
