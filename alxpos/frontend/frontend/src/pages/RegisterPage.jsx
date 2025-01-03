import React, { useState } from 'react';
import axios from 'axios'

const RegisterPage = () => {
    const [formData, setFormData] = useState({
        username: "",
        email: "",
        password1: "",
        password2: ""
    });
    const [isLoading, setIsLoading] = useState(false);
    const [successMessage, setSuccessMessage] = useState(null);
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        setFormData({...formData, [e.target.name]: e.target.value})
    }
    
    const handleSubmit = async (e) => {
        e.preventDefault(e);
        if (isLoading) return
        setIsLoading(true);

        try {
            const response = await axios.post("http://127.0.0.1:8000/api/register/", formData)
            console.log("Success", response.data)
            setSuccessMessage("Registered Successfully")
            setIsLoading(false);
            
        } catch (error) {
            setError(error.response?.data?.detail)
            setSuccessMessage("Unable to Register the User")
        }
    }
  return (
    <div>
        <form onSubmit={handleSubmit}>
            {
                error ? (<p style={{color: "red"}}>Register Error: {error}</p>) : (successMessage && <p style={{color: "green"}}>Registered Successfully</p>) 
            }
            <label>Username:</label>
            <input 
                type='text'
                name='username'
                value={formData.username}
                onChange={handleChange}
            />
            <label>Email:</label>
            <input 
                type='email'
                name='email'
                value={formData.email}
                onChange={handleChange}
            />
            <label>Password:</label>
            <input 
                type='password'
                name='password1'
                value={formData.password1}
                onChange={handleChange}
            />
            <label>Confirm Password:</label>
            <input 
                type='password'
                name='password2'
                value={formData.password2}
                onChange={handleChange}
            />
            <button type='submit' disabled={isLoading}>Register</button>
        </form>
    </div>
  )
}

export default RegisterPage