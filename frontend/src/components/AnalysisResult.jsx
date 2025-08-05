/* frontend/src/components/AnalysisResult.css */

.result-card, .info-card {
  width: 100%;
  max-width: 550px;
  background-color: #1e1e1e;
  border-radius: 12px;
  padding: 1.5rem 2rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  border-left: 5px solid;
  color: #e0e0e0;
  box-sizing: border-box; /* Важное правило для правильного расчета ширины */
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #333;
}

.card-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.direction-long, .direction-short {
  font-size: 1.2rem;
  font-weight: bold;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
}

.direction-long {
  color: #1e1e1e;
  background-color: #00e676; /* Яркий зеленый */
}

.direction-short {
  color: #1e1e1e;
  background-color: #ff5252; /* Яркий красный */
}

.summary-text {
  font-style: italic;
  color: #a0a0a0;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.trade-details {
  display: grid;
  gap: 1rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
}

.label {
  font-weight: bold;
  color: #a0a0a0;
  white-space: nowrap; /* Запрещаем перенос самого лейбла */
  margin-right: 1rem;  /* Добавляем отступ справа */
}

.value {
  font-weight: 500;
  text-align: right;
  word-break: break-all; /* Разрешаем перенос значения, если оно слишком длинное */
}

.value-entry {
  color: #82aaff;
  font-weight: bold;
}
.value-stoploss {
  color: #ff8a80; /* Светло-красный */
  font-weight: bold;
}
.value-takeprofit {
  color: #b9f6ca; /* Светло-зеленый */
  font-weight: bold;
}
.value-risk {
  color: #ffeb3b; /* Желтый */
}

/* Стили для информационных карточек */
.info-card {
  text-align: center;
  border-color: #ffeb3b; /* Желтый */
}
.info-card h2 {
  color: #ffeb3b;
  margin-top: 0;
}


/* --- КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ ДЛЯ МОБИЛЬНЫХ --- */
@media (max-width: 600px) {
  .result-card, .info-card {
    padding: 1rem; /* Уменьшаем боковые отступы */
  }

  .summary-text {
    font-size: 0.95rem;
  }

  .card-header h3 {
    font-size: 1.3rem;
  }
  
  .direction-long, .direction-short {
    font-size: 1rem;
    padding: 0.2rem 0.6rem;
  }

  .detail-item {
    /* Это позволит элементам переноситься, если им не хватает места */
    flex-wrap: wrap; 
  }
}
