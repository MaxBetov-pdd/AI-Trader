// frontend/src/components/HistoryCard.jsx
import { motion } from 'framer-motion';

// Функция для получения стилей статуса
const getStatusBadge = (status) => {
    switch (status) {
        case 'take_profit_hit':
            return { text: '✅ Тейк-профит', color: '#00e676' };
        case 'stop_loss_hit':
            return { text: '🛡️ Стоп-лосс', color: '#ff5252' };
        case 'activated':
            return { text: '🔥 В рынке', color: '#82aaff' };
        case 'expired':
            return { text: '⌛ Истек', color: '#a0a0a0' };
        case 'active':
        default:
            return { text: '⏳ Ожидает', color: '#ffeb3b' };
    }
};

const HistoryCard = ({ signal, onCardClick }) => {
    const isLong = signal.direction === 'Long';
    const directionColor = isLong ? '#00e676' : '#ff5252';
    const statusBadge = getStatusBadge(signal.status);

    return (
        <motion.div
            onClick={() => onCardClick(signal)}
            style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '1rem',
                backgroundColor: '#2c2c2c',
                borderRadius: '8px',
                cursor: 'pointer',
                borderLeft: `4px solid ${directionColor}`
            }}
            whileHover={{ backgroundColor: '#3a3a3a' }}
        >
            <div>
                <div style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{signal.symbol}</div>
                <div style={{ color: directionColor, fontSize: '0.9rem', textTransform: 'uppercase' }}>
                    {signal.direction}
                </div>
            </div>
            {/* НОВЫЙ БЛОК СТАТУСА */}
            <div style={{
                backgroundColor: 'rgba(0,0,0,0.2)',
                color: statusBadge.color,
                padding: '0.25rem 0.6rem',
                borderRadius: '12px',
                fontSize: '0.85rem',
                fontWeight: 'bold',
            }}>
                {statusBadge.text}
            </div>
            <div style={{ textAlign: 'right', fontSize: '0.9rem', color: '#a0a0a0' }}>
                <div>Вход: <span style={{ color: '#e0e0e0', fontWeight: '500' }}>{signal.entry_price}</span></div>
                <div>Стоп: <span style={{ color: '#e0e0e0', fontWeight: '500' }}>{signal.stop_loss}</span></div>
                <div>Тейк: <span style={{ color: '#e0e0e0', fontWeight: '500' }}>{signal.take_profit}</span></div>
            </div>
        </motion.div>
    );
};

export default HistoryCard;
