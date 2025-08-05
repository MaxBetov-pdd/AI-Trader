// frontend/src/App.jsx
import { useState, useEffect } from 'react';
import axios from 'axios';
import { AnimatePresence, motion } from 'framer-motion';
import CoinInput from './components/CoinInput';
import StrategySelection from './components/StrategySelection';
import AnalysisResult from './components/AnalysisResult';
import LoadingState from './components/LoadingState';
import Login from './components/Login';
import History from './components/History';
import './App.css';

// --- Глобальная настройка Axios ---
// Устанавливаем базовый URL
axios.defaults.baseURL = 'https://max-nitro-anv15-41.tailcbcc1d.ts.net';

// Добавляем "перехватчик" запросов. Эта функция будет срабатывать
// ПЕРЕД КАЖДЫМ запросом, отправленным через axios.
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  // Если токен есть, добавляем его в заголовок Authorization
  if (token && token !== 'null') {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  // В случае ошибки просто пробрасываем ее дальше
  return Promise.reject(error);
});


function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [stage, setStage] = useState('coinInput');
  const [coin, setCoin] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [queueSize, setQueueSize] = useState(0);

  useEffect(() => {
    // Эта функция теперь просто синхронизирует состояние с localStorage
    const storedToken = localStorage.getItem('token');
    if (storedToken && storedToken !== 'null') {
      setToken(storedToken);
    } else {
      localStorage.removeItem('token');
      setToken(null);
    }
  }, []);

  const handleLoginSuccess = (newToken) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };
  
  const handleCoinSubmit = (selectedCoin) => {
    setCoin(selectedCoin);
    setStage('strategySelection');
  };

  const handleStrategySelect = async (selectedStrategy) => {
    setLoading(true);
    setError('');
    setResult(null);
    setStage('loading');

    try {
      const queueResponse = await axios.get('/analyses/active');
      setQueueSize(queueResponse.data.active_count);
      
      const response = await axios.post('/analyze/', {
        pair: coin,
        strategy_key: selectedStrategy,
      });

      setResult(response.data);
      setStage('result');
    } catch (err) {
      if (err.response) {
        if(err.response.status === 401) {
            setError("Сессия истекла. Пожалуйста, войдите снова.");
            handleLogout();
        } else {
            setError(`Ошибка от сервера: ${err.response.data.detail}`);
        }
      } else {
        setError('Не удалось подключиться к серверу.');
      }
      setStage('error');
    } finally {
      setLoading(false);
    }
  };
  
  const handleAnalyzeAgain = () => {
    setStage('coinInput');
    setCoin('');
    setResult(null);
    setError('');
  };

  if (!token) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }
  
  return (
    <div className="fullscreen-container" style={{ padding: '2rem' }}>
      <div className="app-container">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h1 style={{margin: 0}}>AI-Trader</h1>
            <button onClick={handleLogout} style={{height: 'fit-content'}}>Выйти</button>
        </div>

        <AnimatePresence mode="wait">
          {stage === 'coinInput' && <CoinInput key="coinInput" onCoinSubmit={handleCoinSubmit} />}
          {stage === 'strategySelection' && (
            <StrategySelection key="strategySelection" onStrategySelect={handleStrategySelect} coin={coin} />
          )}
          {stage === 'loading' && <LoadingState key="loading" queueSize={queueSize} />}
          {stage === 'result' && (
            <motion.div
              key="result"
              style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', marginTop: '2rem' }}
            >
              <AnalysisResult result={result} />
              <button onClick={handleAnalyzeAgain}>Анализировать другую пару</button>
            </motion.div>
          )}
           {stage === 'error' && (
            <motion.div key="error" className="error">
              {error}
              <button onClick={handleAnalyzeAgain} style={{marginTop: '1rem'}}>Попробовать снова</button>
            </motion.div>
          )}
        </AnimatePresence>
        
        {stage === 'coinInput' && <History key={token} />}

      </div>
    </div>
  );
}

export default App;
