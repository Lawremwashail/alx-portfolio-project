import React, { useContext, useState} from 'react'
// import axios from 'axios';
import AuthContext from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import './Pages.css';

const LoginPage = () => {
    const { loginUser } = useContext(AuthContext)
    const [formData, setFormData] = useState({
        email: "",
        password: ""

    });
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const navigate = useNavigate(); // Hook for programmatic navigation

    const handleChange = (e) => {
        setFormData({...formData, [e.target.name]: e.target.value})
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            await loginUser(e);
            setError(null);
        } catch (error) {
            if (error.response && error.response.status === 401) {
                setError("Invalid credentials. Please check your email and password.");
            } else if (error.response?.status === 404) {
                setError("User not found. Redirecting to registration...");
                setTimeout(() => navigate('/register'), 2000);
            } else {
                setError("An error occurred. Please try again.");
            }
        } finally {
            setIsLoading(false);
        }
    };
	return (
    <div className='container'>
        <form onSubmit={handleSubmit}>
            <label>Email: </label>
            <input
                type='email'
                name='email'
                value={formData.email}
                onChange={handleChange}
                required
            />
            <label>Password:</label>
            <input
                type='password'
                name='password'
                value={formData.password}
                onChange={handleChange}
                required
            />
            <button className='container-button' type='submit' disabled={isLoading}>
                {isLoading ? "Logging In..." : "Login"}
            </button>
            {error && <p style={{ color: 'red' }}>{error}</p>}
        </form>
    </div>
  )
}

export default LoginPage;