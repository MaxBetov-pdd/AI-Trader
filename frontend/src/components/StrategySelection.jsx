// frontend/src/components/StrategySelection.jsx
import { motion } from 'framer-motion';

const strategies = [
  {
    key: 'swing',
    name: 'Свинг-трейдинг',
    description: 'Глубокий анализ для поиска среднесрочных сделок (8-48 часов).',
  },
  {
    key: 'intraday',
    name: 'Интрадей',
    description: 'Анализ для поиска сделок внутри дня (4-24 часов), игнорируя дневной график.',
  },
  {
    key: 'scalping',
    name: 'Скальпинг',
    description: 'Агрессивный поиск быстрых импульсных движений на малых таймфреймах (1-8 часов).',
  },
];

const StrategySelection = ({ onStrategySelect, coin }) => {
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
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <motion.h1
        style={{ color: '#bb86fc', marginBottom: '2rem', fontSize: '2.2rem', textAlign: 'center' }}
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.5 }}
      >
        Выберите стратегию для <span style={{ color: '#64ffda' }}>{coin}</span>
      </motion.h1>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', justifyContent: 'center', width: '100%' }}>
        {strategies.map((strat, index) => (
          <motion.div
            key={strat.key}
            onClick={() => onStrategySelect(strat.key)}
            className="strategy-card"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.3 + index * 0.1, duration: 0.5 }}
            style={{
              backgroundColor: '#1e1e1e',
              color: '#e0e0e0',
              borderRadius: '8px',
              // --- КЛЮЧЕВЫЕ ИЗМЕНЕНИЯ ЗДЕСЬ ---
              padding: '1.5rem', // Уменьшили внутренние отступы
              width: 'auto',      // Позволяем элементу самому определять ширину
              cursor: 'pointer',
              boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
              textAlign: 'center',
              display: 'flex', 
              flexDirection: 'column',
              justifyContent: 'space-between',
              boxSizing: 'border-box' // Учитываем padding и border в общей ширине
            }}
            whileHover={{ scale: 1.02, y: -5, backgroundColor: '#2c2c2c' }}
          >
            <div>
              <h2 style={{ color: '#64ffda', margin: '0 0 1rem 0' }}>{strat.name}</h2>
              <p style={{ fontSize: '0.9rem', color: '#a0a0a0', marginBottom: '1.5rem', minHeight: '40px' }}>
                {strat.description}
              </p>
            </div>
            <motion.button
              style={{
                padding: '0.8rem 1.5rem',
                borderRadius: '5px',
                border: 'none',
                backgroundColor: '#6200ee',
                color: '#e0e0e0',
                fontSize: '1rem',
                cursor: 'pointer',
                transition: 'background-color 0.3s',
                width: '100%'
              }}
            >
              Выбрать
            </motion.button>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default StrategySelection;
