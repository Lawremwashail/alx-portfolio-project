import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import AuthContext from '../context/AuthContext';

const Header = () => {
    const { user, logoutUser } = useContext(AuthContext);  // Get user and logout function from context

    return (
        <div>
            <Link to="/">Home</Link>
            <span> | </span>
            {user ? (
                <>
                    <Link to="/sales">Sales</Link>
                    <span> | </span>
                    <Link to="/inventory">Inventory</Link>
                    <span> | </span>
                    <button onClick={logoutUser}>Logout</button>
                    
                    
                    <p>Hello, {user.username}</p> {/* Display username */}
                </>
            ) : (
                <Link to="/login">Login</Link>
            )}
        </div>
    );
};

export default Header;
