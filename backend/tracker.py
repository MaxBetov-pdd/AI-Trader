# backend/tracker.py
import asyncio
import time
from datetime import datetime, timedelta, timezone
import ccxt.async_support as ccxt
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import sessionmaker
from database import analyses

# --- ИЗМЕНЕНИЕ: Забираем DATABASE_URL из database.py ---
from database import DATABASE_URL

# Используем СИНХРОННЫЙ движок, так как скрипт простой и линейный
# Заменяем "+asyncpg" на "" для синхронного драйвера psycopg2
sync_db_url = DATABASE_URL.replace("+asyncpg", "")
engine = create_engine(sync_db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def run_tracker():
    print("🚀 Трекер сигналов запущен. Проверка каждые 5 минут.")
    
    while True:
        # Помещаем создание биржи внутрь цикла для переподключения в случае ошибок
        exchange = ccxt.binance()
        db_session = SessionLocal()
        try:
            query = select(analyses).where(analyses.c.status.in_(['active', 'activated']))
            signals_to_track = db_session.execute(query).fetchall()

            if not signals_to_track:
                print("Активных сигналов для отслеживания нет. Следующая проверка через 5 минут.")
            else:
                symbols = list(set([s.symbol for s in signals_to_track]))
                print(f"Отслеживается {len(signals_to_track)} сигналов для символов: {symbols}")
                
                tickers = await exchange.fetch_tickers(symbols)
                
                for signal in signals_to_track:
                    current_price = tickers[signal.symbol]['last']
                    now = datetime.now(timezone.utc)

                    if signal.status == 'active':
                        # --- КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ ЗДЕСЬ ---
                        # Проверяем, что это не рыночный ордер, перед сравнением цен
                        if signal.entry_price != 'Market':
                            is_long_activation = signal.direction == 'Long' and current_price <= float(signal.entry_price)
                            is_short_activation = signal.direction == 'Short' and current_price >= float(signal.entry_price)

                            if is_long_activation or is_short_activation:
                                print(f"✅ Сигнал #{signal.id} ({signal.symbol}) АКТИВИРОВАН по цене {current_price}")
                                update_query = update(analyses).where(analyses.c.id == signal.id).values(status='activated', entry_timestamp=now)
                                db_session.execute(update_query)
                        
                        # Проверка на "протухание" (продолжает работать для всех типов)
                        if now > signal.timestamp.replace(tzinfo=timezone.utc) + timedelta(hours=signal.invalidation_hours):
                            print(f"⌛ Сигнал #{signal.id} ({signal.symbol}) ИСТЕК по времени")
                            update_query = update(analyses).where(analyses.c.id == signal.id).values(status='expired', closed_timestamp=now)
                            db_session.execute(update_query)

                    elif signal.status == 'activated':
                        is_tp_hit = (signal.direction == 'Long' and current_price >= signal.take_profit) or \
                                    (signal.direction == 'Short' and current_price <= signal.take_profit)
                        is_sl_hit = (signal.direction == 'Long' and current_price <= signal.stop_loss) or \
                                    (signal.direction == 'Short' and current_price >= signal.stop_loss)

                        if is_tp_hit:
                            print(f"🎯 ТЕЙК-ПРОФИТ для сигнала #{signal.id} ({signal.symbol}) по цене {current_price}")
                            update_query = update(analyses).where(analyses.c.id == signal.id).values(status='take_profit_hit', closed_timestamp=now)
                            db_session.execute(update_query)
                        elif is_sl_hit:
                            print(f"🛡️ СТОП-ЛОСС для сигнала #{signal.id} ({signal.symbol}) по цене {current_price}")
                            update_query = update(analyses).where(analyses.c.id == signal.id).values(status='stop_loss_hit', closed_timestamp=now)
                            db_session.execute(update_query)
                
                db_session.commit()

        except Exception as e:
            print(f"Произошла ошибка в цикле трекера: {e}")
            db_session.rollback()
        finally:
            db_session.close()
            await exchange.close()

        # Пауза 5 минут
        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(run_tracker())
