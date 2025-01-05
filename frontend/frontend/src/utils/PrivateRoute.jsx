import React, { useContext } from 'react'; // Import React and useContext
import { Navigate } from 'react-router-dom'; // Import Navigate
import AuthContext from '../context/AuthContext'; // Import AuthContext

const PrivateRoute = ({ children, adminOnly = false }) => {
    const { user } = useContext(AuthContext); // Get user from AuthContext

    if (!user) {
        // If no user, redirect to login page
        return <Navigate to="/login" />;
    }

    if (adminOnly && user.role !== 'admin') {
        // If it's an admin route but the user is not an admin, redirect to sales page or other accessible page
        return <Navigate to="/" />;
    }

    // If user has access, render the children (the protected content)
    return children;
};

export default PrivateRoute;
