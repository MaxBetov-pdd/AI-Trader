# -*- coding: utf-8 -*-

"""
AI-Трейдер v10.0 (Robust Final).
- Усилена проверка на валидность созданных графиков.
- Добавлена детальная обработка ошибок при загрузке файлов и вызове API.
- Выбор стратегии: Консервативная, Сбалансированная, Агрессивная.
"""

import os
import json
import pandas as pd
from collections import Counter
import mplfinance as mpf
import ccxt
import google.generativeai as genai
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# --- НАСТРОЙКА ---
load_dotenv()
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    exchange = ccxt.binance()
    console = Console()
except Exception as e:
    print(f"❌ Ошибка конфигурации API: {e}")
    exit()

# <--- БЛОК ВСПОМОГАТЕЛЬНЫХ ФУНКЦИЙ --->
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

# --- ФУНКЦИЯ ВЫБОРА СТРАТЕГИИ ---
def select_strategy(config: dict) -> dict:
    console.print(Panel("[bold]Выберите торговую стратегию[/bold]", expand=False))
    strategies = config['strategies']
    strategy_keys = list(strategies.keys())
    for i, key in enumerate(strategy_keys):
        strategy = strategies[key]
        console.print(f"[cyan]{i+1}. {strategy['name']}[/cyan]")
        console.print(f"   [dim]{strategy['description']}[/dim]\n")
    while True:
        try:
            choice = int(console.input("[bold]Введите номер стратегии: [/bold]"))
            if 1 <= choice <= len(strategy_keys):
                chosen_key = strategy_keys[choice - 1]
                console.print(f"\n[green]Выбрана стратегия: [bold]{strategies[chosen_key]['name']}[/bold][/green]")
                return strategies[chosen_key]
            else:
                console.print("[red]Неверный номер. Попробуйте еще раз.[/red]")
        except ValueError:
            console.print("[red]Пожалуйста, введите число.[/red]")

# --- ОСНОВНЫЕ ФУНКЦИИ ---
def fetch_and_plot(symbol: str, timeframe: str, run_id: int) -> str:
    try:
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
        filepath = f"chart_{symbol.replace('/', '')}_{timeframe}_{run_id}.png"
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

    # --- УЛУЧШЕННАЯ И БОЛЕЕ БЕЗОПАСНАЯ ЗАГРУЗКА ФАЙЛОВ ---
    uploaded_files = []
    for path in image_paths:
        try:
            console.print(f"  [dim]Загрузка {path}...[/dim]")
            uploaded_files.append(genai.upload_file(path=path))
        except Exception as e:
            console.print(f"❌ [bold red]Не удалось загрузить файл {path}: {e}[/bold red]")
            # Решаем не прерывать, а продолжить с теми файлами, что загрузились
    
    if not uploaded_files:
        console.print("❌ [bold red]Ни один файл с графиком не был успешно загружен. Анализ невозможен.[/bold red]")
        return None
    # ----------------------------------------------------

    model = genai.GenerativeModel('gemini-2.5-pro')
    safety_settings = { 'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE', 'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE', 'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE', 'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE' }
    
    try:
        response = model.generate_content([prompt] + uploaded_files, safety_settings=safety_settings)
        raw_text = response.text
        cleaned_text = raw_text.strip().replace('```json', '').replace('```', '')
        return json.loads(cleaned_text)
    except ValueError: # Срабатывает, если response.text заблокирован
        console.print(f"❌ [bold red]Ответ от Gemini был заблокирован.[/bold red]")
        if hasattr(response, 'prompt_feedback'):
             console.print(f"   [bold]Причина блокировки:[/bold] {response.prompt_feedback}")
        return None
    except json.JSONDecodeError as e:
        console.print(f"❌ [bold red]Ошибка декодирования JSON:[/bold red] {e}")
        return None
    except Exception as e:
        console.print(f"❌ [bold red]Произошла неизвестная ошибка при вызове Gemini API:[/bold red] {e}")
        return None
    finally:
        for p in image_paths: # Очистка всех исходных путей
            if p and os.path.exists(p): os.remove(p)

def display_results(result: dict, confidence: str):
    title = f"[bold]Торговый план от AI {confidence}[/bold]"
    direction = result.get("direction", "N/A")
    color = "green" if direction == "Long" else "red"
    panel_content = Text()
    panel_content.append(f"Торговая пара: {result.get('symbol', 'N/A')}\n", style="bold white")
    panel_content.append(f"Направление: ", style="white")
    panel_content.append(f"{direction}\n", style=f"bold {color}")
    panel_content.append("-" * 30 + "\n", style="dim")
    panel_content.append(f"Обоснование: {result.get('analysis_summary', 'N/A')}\n\n", style="italic white")
    entry_type = result.get("entry_type", "Limit")
    entry_price = result.get("entry_price")
    panel_content.append(f"Вход: По рынку (Market)\n", style="bold cyan") if entry_type.lower() == 'market' else panel_content.append(f"Вход (Limit): {entry_price}\n", style="bold cyan")
    panel_content.append(f"Причина входа: {result.get('entry_reason', 'N/A')}\n\n", style="cyan")
    panel_content.append(f"Стоп-лосс: {result.get('stop_loss')}\n", style="bold red")
    panel_content.append(f"Тейк-профит: {result.get('take_profit')}\n", style="bold green")
    panel_content.append(f"Риск/Прибыль: {result.get('risk_reward_ratio', 'N/A')}\n\n", style="yellow")
    panel_content.append(f"❗️ Идея актуальна примерно {result.get('invalidation_hours', 'N/A')} часов.", style="bold magenta")
    console.print(Panel(panel_content, title=title, border_style=color))

# --- ГЛАВНЫЙ БЛОК ИСПОЛНЕНИЯ ---
if __name__ == "__main__":
    console.print(Panel("[bold cyan]AI-Трейдер v10.0 (Robust Final) запущен.[/bold cyan]", expand=False))
    if not os.getenv("GOOGLE_API_KEY"):
        console.print("[bold red]Ошибка: API ключ не найден.[/bold red]")
        exit()
    
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        strategy = select_strategy(config)
        pair_input = console.input("[bold]Введите торговую пару (например, BTC/USDT): [/bold]").upper()
        NUMBER_OF_RUNS = 3
        results = []
        console.print(f"\n[yellow]Запускаю анализ для [bold]{pair_input}[/bold] с тройной проверкой...[/yellow]")
        
        for i in range(1, NUMBER_OF_RUNS + 1):
            timeframes = strategy['timeframes']
            prompt_file = strategy['prompt_file']
            chart_paths = [fetch_and_plot(pair_input, tf, run_id=i) for tf in timeframes]
            
            valid_chart_paths = [p for p in chart_paths if p]
            if len(valid_chart_paths) < len(timeframes):
                 console.print(f"⚠️ (Прогон {i}) Не все графики удалось создать, анализ может быть неполным.")

            if valid_chart_paths:
                trade_idea = analyze_with_gemini(pair_input, valid_chart_paths, run_id=i, prompt_file=prompt_file)
                if trade_idea and trade_idea.get('direction') and trade_idea.get('direction').lower() != 'none':
                    results.append(trade_idea)
            else:
                console.print(f"❌ (Прогон {i}) Не удалось создать ни одного графика. Анализ пропущен.")
        
        console.print("\n[yellow]Анализ завершен. Проверка на консенсус...[/yellow]\n")

        if not results:
            console.print(Panel("ИИ не нашел качественных торговых сетапов по выбранной стратегии.", title="[bold]Нет сигнала[/bold]", border_style="yellow"))
        else:
            directions = [r.get('direction') for r in results]
            direction_counts = Counter(directions)
            most_common_direction, count = direction_counts.most_common(1)[0]
            if count >= 2:
                confident_result = next(r for r in results if r.get('direction') == most_common_direction)
                confidence_str = f"[green]УВЕРЕННЫЙ ({count}/{len(results)})[/green]"
                display_results(confident_result, confidence=confidence_str)
            else:
                warning_text = Text()
                warning_text.append("Рыночная ситуация НЕОДНОЗНАЧНАЯ.\n\n", style="bold yellow")
                warning_text.append("ИИ дал противоречивые сигналы:\n")
                for direction, num in direction_counts.items():
                    warning_text.append(f"- {direction}: {num} раз(а)\n", style="yellow")
                warning_text.append("\nРекомендуется воздержаться от сделок до появления ясности.", style="bold")
                console.print(Panel(warning_text, title="[bold red]ПРЕДУПРЕЖДЕНИЕ[/bold red]", border_style="red"))

    except KeyboardInterrupt:
        console.print("\n[yellow]Программа завершена пользователем.[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Произошла критическая ошибка: {e}[/bold red]")
        import traceback
        traceback.print_exc() # Добавим полный traceback для диагностики
    
    console.print(Panel("[bold yellow]⚠️ ПОМНИТЕ: Этот инструмент является вспомогательным...", title="[red]Дисклеймер[/red]", border_style="red"))
