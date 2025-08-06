// frontend/src/components/AnalysisResult.jsx
import React from 'react';
import { motion } from 'framer-motion';
import './AnalysisResult.css';

const AnalysisResult = ({ result }) => {
  if (result.status === 'ambiguous' || result.status === 'no_signal') {
    return (
      <motion.div
        className="info-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
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

  const isLong = result.direction === 'Long';
  const directionClass = isLong ? 'direction-long' : 'direction-short';
  const borderColor = isLong ? '#00e676' : '#ff5252';
  const confidence = result.confidence_score || 0;

  return (
    <motion.div
      className="result-card"
      style={{ borderColor: borderColor }}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
    >
      <div className="card-header">
        <h3>{result.symbol}</h3>
        <div className={directionClass}>{result.direction.toUpperCase()}</div>
      </div>

      <p className="summary-text">"{result.analysis_summary}"</p>

      {/* НОВЫЙ БЛОК ДЛЯ ОТОБРАЖЕНИЯ УВЕРЕННОСТИ И КОНСЕНСУСА */}
      <div className="meta-details">
        <div className="detail-item">
          <span className="label">💡 Консенсус:</span>
          <span className="value value-consensus">{result.consensus}</span>
        </div>
        <div className="detail-item">
          <span className="label">⭐ Уверенность ИИ:</span>
          <span className="value value-confidence" style={{color: confidence > 7 ? '#00e676' : '#ffeb3b'}}>
            {confidence} / 10
          </span>
        </div>
      </div>

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
      </div>

      {/* НОВЫЙ БЛОК ДЛЯ ОТОБРАЖЕНИЯ ГРАФИКОВ С СЕТАПОМ */}
      {result.chart_images && result.chart_images.length > 0 && (
        <div className="charts-container">
          <h4>Графики с сетапом, которые видел ИИ:</h4>
          {result.chart_images.map((img_path, index) => (
            <img key={index} src={`http://127.0.0.1:8000/charts/${img_path.split('/').pop()}`} alt={`Setup chart ${index + 1}`} />
          ))}
        </div>
      )}
    </motion.div>
  );
};

export default AnalysisResult;
