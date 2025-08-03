// frontend/src/components/AnalysisResult.jsx

import React from 'react';
import { motion } from 'framer-motion';
import './AnalysisResult.css'; // <-- Импортируем наши новые стили

const AnalysisResult = ({ result }) => {
  // --- Сначала обработаем случаи, когда нет чёткого сигнала ---
  if (result.status === 'ambiguous' || result.status === 'no_signal') {
    return (
      <motion.div
        className="info-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2>{result.status === 'ambiguous' ? '⚠️ Рынок неоднозначен' : 'ℹ️ Нет сигнала'}</h2>
        <p>{result.message}</p>
        {result.details && (
          <p style={{ color: '#a0a0a0' }}>
            Детали: Long ({result.details.Long || 0}), Short ({result.details.Short || 0})
          </p>
        )}
      </motion.div>
    );
  }

  // --- Основная логика для успешного результата ---
  const isLong = result.direction === 'Long';
  const directionClass = isLong ? 'direction-long' : 'direction-short';
  const borderColor = isLong ? '#00e676' : '#ff5252';

  return (
    <motion.div
      className="result-card"
      style={{ borderColor: borderColor }}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="card-header">
        <h3>{result.symbol}</h3>
        <div className={directionClass}>{result.direction.toUpperCase()}</div>
      </div>

      <p className="summary-text">"{result.analysis_summary}"</p>

      <div className="trade-details">
        <div className="detail-item">
          <span className="label">➡️ Вход:</span>
          <span className="value value-entry">
            {result.entry_type?.toLowerCase() === 'market' ? 'По рынку' : result.entry_price}
          </span>
        </div>
        <div className="detail-item">
          <span className="label">🛡️ Стоп-лосс:</span>
          <span className="value value-stoploss">{result.stop_loss}</span>
        </div>
        <div className="detail-item">
          <span className="label">🎯 Тейк-профит:</span>
          <span className="value value-takeprofit">{result.take_profit}</span>
        </div>
        <div className="detail-item">
          <span className="label">📈 Риск/Прибыль:</span>
          <span className="value value-risk">{result.risk_reward_ratio}</span>
        </div>
        <div className="detail-item">
          <span className="label">⏳ Актуальность:</span>
          <span className="value">{result.invalidation_hours} ч.</span>
        </div>
        <div className="detail-item">
          <span className="label">💡 Консенсус:</span>
          <span className="value">{result.consensus}</span>
        </div>
      </div>
    </motion.div>
  );
};

export default AnalysisResult;
