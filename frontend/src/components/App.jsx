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

const api = axios.create({
  baseURL: 'https://max-nitro-anv15-41.tailcbcc1d.ts.net',
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
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      localStorage.setItem('token', token);
    } else {
      delete api.defaults.headers.common['Authorization'];
      localStorage.removeItem('token');
    }
  }, [token]);

  const handleLoginSuccess = (newToken) => {
    setToken(newToken);
  };

  const handleLogout = () => {
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
      const queueResponse = await api.get('/analyses/active');
      setQueueSize(queueResponse.data.active_count);
      
      const response = await api.post('/analyze/', {
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
        
        {stage === 'coinInput' && <History />}

      </div>
    </div>
  );
}

export default App;
