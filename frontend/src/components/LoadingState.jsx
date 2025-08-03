// frontend/src/components/LoadingState.jsx
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const LoadingState = ({ message }) => {
  const [countdown, setCountdown] = useState(90); // <-- ИЗМЕНЕНИЕ ЗДЕСЬ

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => {
        setCountdown(countdown - 1);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  return (
    <motion.div
      className="loading"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}
    >
      <div style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>{message}</div>
      <div style={{ fontSize: '1rem', color: '#a0a0a0' }}>
        Примерное время ожидания: {countdown} секунд
      </div>
      {/* Можно добавить анимированный спиннер или другой индикатор */}
      <motion.div
        className="spinner"
        animate={{ rotate: 360 }}
        transition={{ loop: Infinity, duration: 1, ease: 'linear' }}
        style={{
          width: '30px',
          height: '30px',
          border: '3px solid rgba(187, 134, 252, 0.2)',
          borderLeftColor: '#bb86fc',
          borderRadius: '50%',
          marginTop: '1rem',
        }}
      />
    </motion.div>
  );
};

export default LoadingState;
