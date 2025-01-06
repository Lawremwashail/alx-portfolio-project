import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './Pages.css';

const RegisterPage = () => {
    const [formData, setFormData] = useState({
        username: "",
        email: "",
        password1: "",
        password2: "",
        role: "user" // Default role is 'user'
    });
    const [isLoading, setIsLoading] = useState(false);
    const [successMessage, setSuccessMessage] = useState(null);
    const [error, setError] = useState(null);

    const navigate = useNavigate(); // To programmatically navigate to login

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (isLoading) return;
        setIsLoading(true);

        if (formData.password1 !== formData.password2) {
            setError("Passwords do not match");
            setIsLoading(false);
            return;
        }

        try {
            const response = await axios.post("http://127.0.0.1:8000/api/register/", {
                username: formData.username,
                email: formData.email,
                password1: formData.password1,
                password2: formData.password2,
                role: formData.role // Include the role in the request
            });

            if (response.status === 201) {
                setSuccessMessage("Registered successfully! Redirecting to login...");
                setTimeout(() => {
                    navigate('/login'); // Redirect to login page
                }, 1500); // Optional delay for feedback
            } else {
                setError("Registration failed. Please try again.");
            }
        } catch (err) {
            if (err.response?.data) {
                const errorDetails = Object.values(err.response.data).flat().join(", ");
                setError(errorDetails || "Registration failed. Please try again.");
            } else {
                setError("Unable to connect to the server.");
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className='container'>
            <form onSubmit={handleSubmit}>
                {error && <p style={{ color: "red" }}>{error}</p>}
                {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}
                <label>Username:</label>
                <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    required
                />
                <label>Email:</label>
                <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                />
                <label>Password:</label>
                <input
                    type="password"
                    name="password1"
                    value={formData.password1}
                    onChange={handleChange}
                    required
                />
                <label>Confirm Password:</label>
                <input
                    type="password"
                    name="password2"
                    value={formData.password2}
                    onChange={handleChange}
                    required
                />
                <label>Role:</label>
                <select
                    name="role"
                    value={formData.role}
                    onChange={handleChange}
                    required
                >
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                </select>
                <button className='container-button' type="submit" disabled={isLoading}>
                    {isLoading ? "Registering..." : "Register"}
                </button>
            </form>
        </div>
    );
};

export default RegisterPage;





// import React, { useState } from 'react';
// import axios from 'axios';
// import { useNavigate } from 'react-router-dom';
// import './Pages.css';


// const RegisterPage = () => {
//     const [formData, setFormData] = useState({
//         username: "",
//         email: "",
//         password1: "",
//         password2: ""
//     });
//     const [isLoading, setIsLoading] = useState(false);
//     const [successMessage, setSuccessMessage] = useState(null);
//     const [error, setError] = useState(null);


//     const navigate = useNavigate(); // To programmatically navigate to login

//     const handleChange = (e) => {
//         setFormData({ ...formData, [e.target.name]: e.target.value });
//     };

//     const handleSubmit = async (e) => {
//         e.preventDefault();
//         if (isLoading) return;
//         setIsLoading(true);

//         if (formData.password1 !== formData.password2) {
//             setError("Passwords do not match");
//             setIsLoading(false);
//             return;
//         }

//         try {
//             const response = await axios.post("http://127.0.0.1:8000/api/register/", {
//                 username: formData.username,
//                 email: formData.email,
//                 password1: formData.password1,
//                 password2: formData.password2,

//             });

//             if (response.status === 201) {
//                 setSuccessMessage("Registered successfully! Redirecting to login...");
//                 setTimeout(() => {
//                     navigate('/login'); // Redirect to login page
//                 }, 1500); // Optional delay for feedback
//             } else {
//                 setError("Registration failed. Please try again.");
//             }
//         } catch (err) {
//             if (err.response?.data) {
//                 const errorDetails = Object.values(err.response.data).flat().join(", ");
//                 setError(errorDetails || "Registration failed. Please try again.");
//             } else {
//                 setError("Unable to connect to the server.");
//             }
//         } finally {
//             setIsLoading(false);
//         }
//     };

//     return (
//         <div className='container'>
//             <form onSubmit={handleSubmit}>
//                 {error && <p style={{ color: "red" }}>{error}</p>}
//                 {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}
//                 <label>Username:</label>
//                 <input
//                     type="text"
//                     name="username"
//                     value={formData.username}
//                     onChange={handleChange}
//                     required
//                 />
//                 <label>Email:</label>
//                 <input
//                     type="email"
//                     name="email"
//                     value={formData.email}
//                     onChange={handleChange}
//                     required
//                 />
//                 <label>Password:</label>
//                 <input
//                     type="password"
//                     name="password1"
//                     value={formData.password1}
//                     onChange={handleChange}
//                     required
//                 />
//                 <label>Confirm Password:</label>
//                 <input
//                     type="password"
//                     name="password2"
//                     value={formData.password2}
//                     onChange={handleChange}
//                     required
//                 />
//                 <button className='container-button' type="submit" disabled={isLoading}>
//                     {isLoading ? "Registering..." : "Register"}
//                 </button>
//             </form>
//         </div>
//     );
// };

// export default RegisterPage;