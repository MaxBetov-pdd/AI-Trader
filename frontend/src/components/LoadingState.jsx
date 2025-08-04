// frontend/src/components/LoadingState.jsx
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const LoadingState = ({ queueSize }) => {
  // Рассчитываем время ожидания по формуле (n+1) * 120
  // Если перед нами 0 человек (n=0), время будет 120с.
  // Если перед нами 1 человек (n=1), время будет 240с.
  const estimatedWaitTime = (queueSize + 1) * 120;
  
  const [countdown, setCountdown] = useState(estimatedWaitTime);

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
      <div style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Анализ запущен...</div>
      
      {/* Новые информационные строки */}
      <div style={{ fontSize: '1.1rem', color: '#a0a0a0', marginBottom: '0.5rem' }}>
        Ваше место в очереди: <span style={{color: '#64ffda', fontWeight: 'bold'}}>{queueSize + 1}</span>
      </div>
      <div style={{ fontSize: '1.1rem', color: '#a0a0a0' }}>
        Примерное время ожидания: <span style={{color: '#64ffda', fontWeight: 'bold'}}>{countdown}</span> секунд
      </div>

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
          marginTop: '1.5rem',
        }}
      />
    </motion.div>
  );
};

export default LoadingState;
