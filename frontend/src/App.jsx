// frontend/src/App.jsx

import { useState } from 'react';
import axios from 'axios';
import { AnimatePresence, motion } from 'framer-motion';
import CoinInput from './components/CoinInput';
import StrategySelection from './components/StrategySelection';
import AnalysisResult from './components/AnalysisResult';
import LoadingState from './components/LoadingState';
import './App.css';

function App() {
  const [coin, setCoin] = useState('');
  const [strategy, setStrategy] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [stage, setStage] = useState('coinInput'); // 'coinInput', 'strategySelection', 'loading', 'result', 'error'
  const [queueSize, setQueueSize] = useState(0); // <-- Состояние для хранения размера очереди

  const handleCoinSubmit = (selectedCoin) => {
    setCoin(selectedCoin);
    setStage('strategySelection');
  };

  const handleStrategySelect = async (selectedStrategy) => {
    setStrategy(selectedStrategy);
    setLoading(true);
    setError('');
    setResult(null);
    setStage('loading');

    try {
      // 1. Сначала получаем текущий размер очереди
      const queueResponse = await axios.get('https://max-nitro-anv15-41.tailcbcc1d.ts.net/analyses/active');
      setQueueSize(queueResponse.data.active_count);
      
      // 2. Затем отправляем наш запрос на анализ
      const response = await axios.post('https://max-nitro-anv15-41.tailcbcc1d.ts.net/analyze/', {
        pair: coin,
        strategy_key: selectedStrategy,
      });
      setResult(response.data);
      setStage('result');
    } catch (err) {
      if (err.response) {
        setError(`Ошибка от сервера: ${err.response.data.detail}`);
      } else {
        setError('Не удалось подключиться к серверу. Убедитесь, что он запущен.');
      }
      console.error(err);
      setStage('error');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToStrategies = () => {
    setStage('strategySelection');
    setResult(null);
    setError('');
  };

  const handleAnalyzeAgain = () => {
    setStage('coinInput');
    setCoin('');
    setResult(null);
    setError('');
    setStrategy('');
  };

  return (
    <div className="fullscreen-container" style={{ minHeight: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '2rem' }}>
      <div className="app-container">
        <AnimatePresence mode="wait">
          {stage === 'coinInput' && <CoinInput key="coinInput" onCoinSubmit={handleCoinSubmit} />}
          {stage === 'strategySelection' && (
            <StrategySelection key="strategySelection" onStrategySelect={handleStrategySelect} coin={coin} />
          )}
          {stage === 'loading' && <LoadingState key="loading" queueSize={queueSize} />}
          {stage === 'result' && (
            <motion.div
              key="result"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5 }}
              style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', marginTop: '2rem' }}
            >
              <AnalysisResult result={result} />
              <button onClick={handleBackToStrategies}>Выбрать другую стратегию</button>
              <button onClick={handleAnalyzeAgain}>Анализировать другую пару</button>
            </motion.div>
          )}
          {stage === 'error' && (
            <motion.div
              key="error"
              className="error"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5 }}
              style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', marginTop: '2rem' }}
            >
              {error}
              <button onClick={handleBackToStrategies}>Выбрать стратегию</button>
              <button onClick={handleAnalyzeAgain}>Ввести другую пару</button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default App;
