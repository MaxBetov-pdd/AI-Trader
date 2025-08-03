// frontend/src/components/CoinInput.jsx
import { useState } from 'react';
import { motion } from 'framer-motion';

const CoinInput = ({ onCoinSubmit }) => {
  const [coin, setCoin] = useState('');

  const handleChange = (e) => {
    setCoin(e.target.value.toUpperCase());
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (coin.trim()) {
      onCoinSubmit(coin);
    }
  };

  return (
    <motion.div
      className="fullscreen-container"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <motion.h1
        style={{ color: '#bb86fc', marginBottom: '2rem', fontSize: '2.5rem' }}
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.5 }}
      >
        Введите торговую пару
      </motion.h1>
      <motion.form
        onSubmit={handleSubmit}
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.4, duration: 0.5 }}
      >
        <input
          type="text"
          placeholder="Например, BTC/USDT"
          value={coin}
          onChange={handleChange}
          style={{
            padding: '1rem',
            borderRadius: '5px',
            border: '1px solid #333',
            backgroundColor: '#2c2c2c',
            color: '#e0e0e0',
            fontSize: '1.2rem',
            marginBottom: '1rem',
            width: '300px',
            textAlign: 'center',
          }}
        />
        <motion.button // <-- ИСПРАВЛЕНИЕ ЗДЕСЬ
          type="submit"
          style={{
            padding: '1rem 2rem',
            borderRadius: '5px',
            border: 'none',
            backgroundColor: '#6200ee',
            color: '#e0e0e0',
            fontSize: '1.2rem',
            cursor: 'pointer',
            transition: 'background-color 0.3s',
          }}
          whileHover={{ scale: 1.05, backgroundColor: '#3700b3' }} // <-- ТЕПЕРЬ ЭТО РАБОТАЕТ ПРАВИЛЬНО
        >
          Далее
        </motion.button>
      </motion.form>
    </motion.div>
  );
};

export default CoinInput;
