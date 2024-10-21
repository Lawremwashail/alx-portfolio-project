import axios from 'axios';
import { jwtDecode } from 'jwt-decode';
import React, { createContext, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext()

export default AuthContext;

export const AuthProvider = ({children}) =>{
    const [authTokens, setAuthTokens] = useState(() => 
        localStorage.getItem("authTokens") ? JSON.parse(localStorage.getItem('authTokens')) : null
    )
    const [user, setUser] = useState(() => 
        localStorage.getItem("authTokens") ? jwtDecode(localStorage.getItem("authTokens")) : null
    )
    const [isLoading, setIsLoading] = useState(true);

    const navigate = useNavigate();

    const loginUser = async (e) => {
        e.preventDefault()
        try {
            const response = await axios.post('http://127.0.0.1:8000/api/token/', {
                email: e.target.email.value,
                password: e.target.password.value,
            });
            
            let data = response.data;
            if (response.status === 200) {
                setAuthTokens(data);
                setUser(jwtDecode(data.access));
                localStorage.setItem('authTokens', JSON.stringify(data));
                navigate('/');
            }
        } catch (error) {
            console.error("Login failed", error);
            alert("Something went wrong!");
        }
    };
    const logoutUser = () => {
        setAuthTokens(null);
        setUser(null)
        localStorage.removeItem("authTokens");
        navigate('/login');
    };

    const updateToken = async () => {
        try {
            let response = await axios.post('http://127.0.0.1:8000/api/token/refresh/', {
                refresh: authTokens?.refresh,
            });

            let data = response.data;

            if (response.status === 200) {
                setAuthTokens(data);  // Update tokens
                setUser(jwtDecode(data.access));  // Decode the new access token to get user data
                localStorage.setItem('authTokens', JSON.stringify(data));  // Save new tokens to localStorage
            } else {
                logoutUser();  // Log out if refresh token is invalid
            }
        } catch (error) {
            console.error("Token refresh error:", error);
            logoutUser();  // Log out if there's an error
        }

        if (isLoading) {
            setIsLoading(false);  // Mark loading as false once the token is updated
        }
    };

    useEffect(() => {
        if (isLoading) {
            updateToken();
        }
        const fourMinutes = 1000 * 6 * 4
        const interval = setInterval(() => {
            if (authTokens) {
                updateToken();
            }
        }, fourMinutes)
        return () => clearInterval(interval);
    }, [authTokens, isLoading])

    const contextData = {
        user: user,
        authTokens: authTokens,
        loginUser: loginUser,
        logoutUser: logoutUser,
    };

    return (
        <AuthContext.Provider value={contextData}>
            {children}
        </AuthContext.Provider>
    )
};
