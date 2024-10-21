import { React, useContext, useState} from 'react'
// import axios from 'axios'; 
import AuthContext from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
const LoginPage = () => {
    const {loginUser} = useContext(AuthContext)
    const [formData, setFormData] = useState({
        email: "",
        password: ""
        
    });
    const [isLoading, setIsLoading] = useState(false);
    const [successMessage, setSuccessMessage] = useState(null);
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
            setSuccessMessage("User Logged In Successfully")
            setError(null)            
        } catch (error) {
            if (error.response && error.response.status === 401) {
                // If the error is due to unregistered user, redirect to registration page
                navigate('/register');
            } else {
                setError(error.response?.data?.detail)
                setSuccessMessage("Unable to Login the User")
            }    
        } finally {
            setIsLoading(false)
        }
    }
  return (
    <div>
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
            <button type='submit' disabled={isLoading}>
                {isLoading ? "Logging In..." : "Login"}
            </button>
            {successMessage && <p style={{color: 'green'}}>{successMessage}</p>}
            {error && <p style={{color: 'red'}}>{error}</p>}
        </form>
    </div>
  )
}

export default LoginPage