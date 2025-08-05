/* frontend/src/components/AnalysisResult.css */

.result-card {
  width: 100%;
  border-radius: 12px;
  border-left: 5px solid;
  color: #e0e0e0;
  box-sizing: border-box;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid #333;
}

.card-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.direction-badge {
  font-size: 1rem;
  font-weight: bold;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  flex-shrink: 0; /* Не позволяет элементу сжиматься */
}

.direction-long {
  color: #1e1e1e;
  background-color: #00e676;
}

.direction-short {
  color: #1e1e1e;
  background-color: #ff5252;
}

.summary-text {
  font-style: italic;
  color: #a0a0a0;
  margin: 1.5rem 0;
  line-height: 1.6;
  font-size: 0.95rem;
}

.trade-details {
  display: flex;
  flex-direction: column; /* Всегда колонка */
  gap: 1rem; /* Отступ между элементами списка */
}

/* Стили по умолчанию (Mobile-First) */
.detail-item {
  display: flex;
  flex-direction: column; /* Лейбл и значение друг под другом */
  align-items: flex-start; /* Выравнивание по левому краю */
}

.label {
  font-weight: bold;
  color: #a0a0a0;
  font-size: 0.9rem;
  margin-bottom: 0.25rem; /* Отступ под лейблом */
}

.value {
  font-weight: 500;
  font-size: 1.1rem;
}

/* Стили для разных типов значений */
.value-entry { color: #82aaff; font-weight: bold; }
.value-stoploss { color: #ff8a80; font-weight: bold; }
.value-takeprofit { color: #b9f6ca; font-weight: bold; }
.value-risk { color: #ffeb3b; }


/* Адаптация для больших экранов (например, планшеты и десктопы) */
@media (min-width: 480px) {
  .detail-item {
    flex-direction: row; /* Возвращаем лейбл и значение в одну строку */
    justify-content: space-between;
    align-items: center;
  }

  .label {
    margin-bottom: 0; /* Убираем нижний отступ у лейбла */
  }

  .value {
     font-size: 1rem; /* Возвращаем стандартный размер шрифта */
  }
}
