import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import PrivateRoute from './utils/PrivateRoute';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import { AuthProvider } from './context/AuthContext';
import Header from './components/Header';
import SalesPage from './pages/SalesPage';
import InventoryPage from './pages/InventoryPage';

function App() {
  return (
    <div className="App">
      <Router>
        <AuthProvider>
          <Header />
          <Routes>
            {/* PrivateRoute for protecting HomePage */}
            <Route path="/" element={<PrivateRoute><HomePage /></PrivateRoute>} />
            <Route path="/sales" element={<PrivateRoute><SalesPage/></PrivateRoute>} />
            <Route path="/inventory" element={<PrivateRoute adminOnly={true}><InventoryPage /></PrivateRoute>} />

            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
          </Routes>
        </AuthProvider>
      </Router>
    </div>
  );
}

export default App;
