import { motion } from 'framer-motion';

const HistoryCard = ({ signal, onCardClick }) => {
    const isLong = signal.direction === 'Long';
    const directionColor = isLong ? '#00e676' : '#ff5252';

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
            <div style={{ textAlign: 'right', fontSize: '0.9rem', color: '#a0a0a0' }}>
                <div>Вход: <span style={{ color: '#e0e0e0', fontWeight: '500' }}>{signal.entry_price}</span></div>
                <div>Стоп: <span style={{ color: '#e0e0e0', fontWeight: '500' }}>{signal.stop_loss}</span></div>
                <div>Тейк: <span style={{ color: '#e0e0e0', fontWeight: '500' }}>{signal.take_profit}</span></div>
            </div>
        </motion.div>
    );
};

export default HistoryCard;
