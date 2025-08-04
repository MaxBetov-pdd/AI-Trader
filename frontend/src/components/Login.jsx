import { useState } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';

const Login = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);

    try {
      const response = await axios.post('https://max-nitro-anv15-41.tailcbcc1d.ts.net/login', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      onLoginSuccess(response.data.access_token);
    } catch (err) {
      if (err.response) {
        setError(`Ошибка: ${err.response.data.detail}`);
      } else {
        setError('Не удалось подключиться к серверу.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      className="fullscreen-container"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}
    >
      <motion.h1 style={{ color: '#bb86fc', marginBottom: '2rem', fontSize: '2.5rem' }}>
        AI-Trader
      </motion.h1>
      <motion.p style={{ color: '#a0a0a0', marginTop: '-1.5rem', marginBottom: '2rem' }}>
        Войдите или зарегистрируйтесь
      </motion.p>
      <motion.form
        onSubmit={handleSubmit}
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.5 }}
        style={{ display: 'flex', flexDirection: 'column', gap: '1rem', width: '300px' }}
      >
        <input
          type="text"
          placeholder="Логин"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Вход...' : 'Войти / Регистрация'}
        </button>
        {error && <div className="error" style={{ padding: '0.5rem', marginTop: '0.5rem' }}>{error}</div>}
      </motion.form>
    </motion.div>
  );
};

export default Login;
