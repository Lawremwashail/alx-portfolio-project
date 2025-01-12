import axios from 'axios';
import React, { useEffect, useState, useContext } from 'react';
import AuthContext from '../context/AuthContext';
import './Pages.css';

const SalesPage = () => {
    const { authTokens } = useContext(AuthContext); // Access token from AuthContext
    const [products, setProducts] = useState([]);
    const [salesData, setSalesData] = useState({
        product_sold: '',
        quantity_sold: '',
        selling_price: '',
    });
    const [sales, setSales] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    const API_BASE_URL = 'http://127.0.0.1:8000/api'; // Base API URL

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [productResponse, salesResponse] = await Promise.all([
                    axios.get(`${API_BASE_URL}/inventory/`, {
                        headers: { Authorization: `Bearer ${authTokens.access}` },
                    }),
                    axios.get(`${API_BASE_URL}/sales/`, {
                        headers: { Authorization: `Bearer ${authTokens.access}` },
                    }),
                ]);

                setProducts(productResponse.data);
                setSales(salesResponse.data);
                setIsLoading(false);
            } catch (err) {
                setError('Failed to fetch data. Please try again later.');
                setIsLoading(false);
            }
        };

        if (authTokens) {
            fetchData();
        }
    }, [authTokens]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setSalesData((prevData) => ({
            ...prevData,
            [name]: value,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Validation: Ensure all fields are filled and inputs are valid
        if (!salesData.product_sold || !salesData.quantity_sold || !salesData.selling_price) {
            setError('Please fill in all fields.');
            return;
        }
        if (salesData.quantity_sold <= 0 || salesData.selling_price <= 0) {
            setError('Quantity and price must be greater than zero.');
            return;
        }

        try {
            const salesPayload = {
                product_name: salesData.product_sold,
                quantity_sold: parseInt(salesData.quantity_sold),
                selling_price: parseFloat(salesData.selling_price),
            };

            await axios.post(`${API_BASE_URL}/sales/`, salesPayload, {
                headers: { Authorization: `Bearer ${authTokens?.access}` },
            });

            setSalesData({ product_sold: '', quantity_sold: '', selling_price: '' });

            // Refetch data after successful submission
            const [productResponse, salesResponse] = await Promise.all([
                axios.get(`${API_BASE_URL}/inventory/`, {
                    headers: { Authorization: `Bearer ${authTokens.access}` },
                }),
                axios.get(`${API_BASE_URL}/sales/`, {
                    headers: { Authorization: `Bearer ${authTokens.access}` },
                }),
            ]);

            setProducts(productResponse.data);
            setSales(salesResponse.data);
            setError(null); // Clear any previous errors
        } catch (err) {
            setError('Failed to create sale. Please try again later.');
        }
    };

    if (isLoading) return <p>Loading...</p>;
    if (error) return <p className="error-message">{error}</p>;

    return (
        <div className="container">
            <h2>Sales Page</h2>
            <p>You Can Sell From this Page</p>
            <div className="form-container">
                <form onSubmit={handleSubmit}>
                    <select
                        name="product_sold"
                        value={salesData.product_sold}
                        onChange={handleChange}
                        required
                    >
                        <option value="">Select Product</option>
                        {products.length > 0 ? (
                            products.map((product) => (
                                <option key={product.id} value={product.product}>
                                    {product.product}
                                </option>
                            ))
                        ) : (
                            <option value="" disabled>
                                No products available
                            </option>
                        )}
                    </select>
                    <input
                        type="number"
                        name="quantity_sold"
                        placeholder="Quantity Sold"
                        value={salesData.quantity_sold}
                        onChange={handleChange}
                        required
                    />
                    <input
                        type="number"
                        step="0.01"
                        name="selling_price"
                        placeholder="Selling Price"
                        value={salesData.selling_price}
                        onChange={handleChange}
                        required
                    />
                    <button className="container-button" type="submit">
                        Sell Item
                    </button>
                </form>
            </div>

            <div className="scroll-table">
                {sales.length === 0 ? (
                    <p>No sales records found. Please create sales.</p>
                ) : (
                    <table>
                        <thead>
                            <tr>
                                <th>Product Sold</th>
                                <th>Quantity Sold</th>
                                <th>Selling Price</th>
                                <th>Profit</th>
                                <th>Sales Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sales.map((sale) => (
                                <tr key={sale.id}>
                                    <td>{sale.product_sold}</td>
                                    <td>{sale.quantity_sold}</td>
                                    <td>${Number(sale.selling_price).toFixed(2)}</td>
                                    <td>${Number(sale.profit).toFixed(2)}</td>
                                    <td>{new Date(sale.sale_date).toLocaleDateString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
};

export default SalesPage;