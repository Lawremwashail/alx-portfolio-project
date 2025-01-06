import React, { useContext } from 'react';
import { NavLink } from 'react-router-dom';
import AuthContext from '../context/AuthContext';
import './Header.css'

const Header = () => {
    const { user, logoutUser } = useContext(AuthContext);
    // console.log("User Token:", JSON.stringify(user));

const getActiveClass = ({ isActive }) => (isActive ? 'active-link' : '');

    return (
      <header>
        <div className="navbar">
          <NavLink to="/" className={getActiveClass}>Home</NavLink> 
          <NavLink to="/sales" className={getActiveClass}>Sales</NavLink>
          {user && user.role === "admin" && <NavLink to="/inventory" className={getActiveClass}>Inventory</NavLink>}
          {user ? (
            <>
              <button className='navbar-button' onClick={logoutUser}>Logout</button>
              <p>Hello, {user.username}</p>
            </>
          ) : (
            <>
              <NavLink to="/login" className={getActiveClass}>Login</NavLink>
              <NavLink to="/register" className={getActiveClass}>Register</NavLink>
            </>
          )}
        </div>
      </header>
    );
    
  };
  

export default Header;
