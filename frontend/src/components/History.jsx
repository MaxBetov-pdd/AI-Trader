// frontend/src/components/History.jsx
import { useState, useEffect } from 'react';
import HistoryCard from './HistoryCard';
import AnalysisResult from './AnalysisResult';
import { AnimatePresence, motion } from 'framer-motion';
import { api } from '../App'; // <-- Импортируем единый экземпляр API

const History = () => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [selectedSignal, setSelectedSignal] = useState(null);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                // Теперь мы используем общий, уже настроенный 'api'
                const response = await api.get('/history');
                setHistory(response.data);
            } catch (err) {
                setError('Не удалось загрузить историю.');
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
    }, []);

    if (loading) return <div style={{textAlign: 'center', marginTop: '2rem', color: '#a0a0a0'}}>Загрузка истории...</div>;
    if (error) return <div className="error">{error}</div>;

    return (
        <div style={{ marginTop: '3rem' }}>
            <h2 style={{ textAlign: 'center', color: '#bb86fc' }}>История сигналов</h2>
            {history.length === 0 ? (
                <p style={{ textAlign: 'center', color: '#a0a0a0' }}>Ваша история пока пуста.</p>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {history.map((signal, index) => (
                        <HistoryCard key={index} signal={signal} onCardClick={setSelectedSignal} />
                    ))}
                </div>
            )}
            
            <AnimatePresence>
            {selectedSignal && (
                <motion.div 
                    className="modal-backdrop"
                    onClick={() => setSelectedSignal(null)}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    style={{
                        position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
                        background: 'rgba(0,0,0,0.7)', display: 'flex',
                        justifyContent: 'center', alignItems: 'center', zIndex: 1000
                    }}
                >
                    <motion.div onClick={e => e.stopPropagation()} initial={{scale: 0.8}} animate={{scale: 1}} exit={{scale: 0.8}}>
                       <AnalysisResult result={selectedSignal} />
                    </motion.div>
                </motion.div>
            )}
            </AnimatePresence>
        </div>
    );
};

export default History;
