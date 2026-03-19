import ChatbotWidget from './ChatbotWidget'
import './index.css' // Import basic reset

function App() {
  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f0f2f5', fontFamily: 'sans-serif' }}>
      <h1>🤖 AI Expense Tracker Chatbot Test</h1>
      <p>Click the floating button in the bottom right corner to test!</p>
      
      {/* Our floating widget */}
      <ChatbotWidget />
    </div>
  )
}

export default App
