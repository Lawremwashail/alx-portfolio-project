import React, { useContext } from 'react'; // Import React and useContext
import { Navigate } from 'react-router-dom'; // Import Navigate
import AuthContext from '../context/AuthContext'; // Import AuthContext

const PrivateRoute = ({ children }) => {
    const { user } = useContext(AuthContext); // Get user from AuthContext

    return user ? children : <Navigate to="/login" />;
};

export default PrivateRoute;
