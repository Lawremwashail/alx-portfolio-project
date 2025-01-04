import axios from 'axios';
import { jwtDecode } from 'jwt-decode';
import React, { createContext, useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext();

export default AuthContext;

export const AuthProvider = ({ children }) => {
    const [authTokens, setAuthTokens] = useState(() =>
        localStorage.getItem('authTokens') ? JSON.parse(localStorage.getItem('authTokens')) : null
    );
    const [user, setUser] = useState(() =>
        localStorage.getItem('authTokens') ? jwtDecode(localStorage.getItem('authTokens')) : null
    );
    const [isLoading, setIsLoading] = useState(true);

    const navigate = useNavigate();

    const loginUser = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://127.0.0.1:8000/api/token/', {
                email: e.target.email.value,
                password: e.target.password.value,
            });

            // let data = response.data;
            if (response.status === 200) {
                const data = response.data;
                setAuthTokens(data);
                setUser(jwtDecode(data.access));
                localStorage.setItem('authTokens', JSON.stringify(data));
                navigate('/');
            }
        } catch (error) {
            console.error('Login failed', error);
            alert('Something went wrong!');
        }
    };

    const logoutUser = useCallback(() => {  // Wrap in useCallback
        setAuthTokens(null);
        setUser(null);
        localStorage.removeItem('authTokens');
        navigate('/login');
    }, [navigate]);

    const updateToken = useCallback(async () => {
        try {
            let response = await axios.post('http://127.0.0.1:8000/api/token/refresh/', {
                refresh: authTokens?.refresh,
            });


            if (response.status === 200) {
                const data = response.data
                setAuthTokens(data);
                setUser(jwtDecode(data.access));
                localStorage.setItem('authTokens', JSON.stringify(data));
            } else {
                logoutUser();
            }
        } catch (error) {
            console.error('Token refresh error:', error);
            logoutUser();
        }

        if (isLoading) {
            setIsLoading(false);
        }
    }, [authTokens, isLoading, logoutUser]);

    useEffect(() => {
        if (isLoading) {
            updateToken();
        }
        const fourMinutes = 1000 * 60 * 4;
        const interval = setInterval(() => {
            if (authTokens) {
                updateToken();
            }
        }, fourMinutes);
        return () => clearInterval(interval);
    }, [authTokens, isLoading, updateToken]);

    const contextData = {
        user: user,
        userRole: user?.role,
        authTokens: authTokens,
        loginUser: loginUser,
        logoutUser: logoutUser,
    };

    return <AuthContext.Provider value={contextData}>
        {children}
    </AuthContext.Provider>;
};
