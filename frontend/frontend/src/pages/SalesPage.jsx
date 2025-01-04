import axios from 'axios';
import React, { useEffect, useState, useContext } from 'react';
import AuthContext from '../context/AuthContext';
import './Pages.css';

const SalesPage = () => {
    const { authTokens, user } = useContext(AuthContext);
    const [products, setProducts] = useState([]);
    const [salesData, setSalesData] = useState({
        product_sold: '',
        quantity_sold: '',
        selling_price: ''
    });
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [sales, setSales] = useState([]);

    useEffect(() => {
        if (authTokens && user && user.id) {
            const fetchData = async () => {
                try {

                    const productResponse = await axios.get('http://127.0.0.1:8000/api/inventory/', {
                        headers: { Authorization: `Bearer ${authTokens.access}` },
                    });

                    const filteredProducts = productResponse.data.filter(
                        product => product.created_by === user.id || product.user === user.id
                    );

                    setProducts(filteredProducts);

                    const salesResponse = await axios.get('http://127.0.0.1:8000/api/sales/', {
                        headers: { Authorization: `Bearer ${authTokens.access}` },
                    });
                    setSales(salesResponse.data);

                    setIsLoading(false);
                } catch (error) {
                    console.error('Error fetching data:', error);
                    if (error.response && error.response.status === 401) {
                        setError('Session expired. Please log in again.');
                    } else {
                        setError('Failed to fetch data');
                    }
                    setIsLoading(false);
                }
            };

            fetchData();
        } else {
            setIsLoading(false);
            setError("User  not found or invalid token");
        }
    }, [authTokens, user]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setSalesData((prevData) => ({
            ...prevData, [name]: value,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const salesPayload = {
                product_name: salesData.product_sold,
                quantity_sold: salesData.quantity_sold,
                selling_price: salesData.selling_price
            };
            await axios.post('http://127.0.0.1:8000/api/sales/', salesPayload, {
                headers: { Authorization: `Bearer ${authTokens?.access}` },
            });
            setSalesData({
                product_sold: '',
                quantity_sold: '',
                selling_price: ''
            });
            // Refetch products and sales after posting new sale
            const productResponse = await axios.get('http://127.0.0.1:8000/api/inventory/', {
                headers: { Authorization: `Bearer ${authTokens.access}` },
            });
            setProducts(productResponse.data);

            const salesResponse = await axios.get('http://127.0.0.1:8000/api/sales/', {
                headers: { Authorization: `Bearer ${authTokens.access}` },
            });
            setSales(salesResponse.data);
        } catch (error) {
            setError('Failed to create sale');
            console.error(error);
        }
    };

    if (isLoading) return <p>Loading...</p>;
    if (error) return <p>{error}</p>;

    return (
        <div className='container'>
            <h2>Sales Page</h2>
            <div className="form-container">
                <form onSubmit={handleSubmit}>
                    <select
                        name='product_sold'
                        value={salesData.product_sold}
                        onChange={handleChange}
                        required
                    >
                        <option value=''>Select Product</option>
                        {products.map((product) => (
                            <option key={product.id} value={product.id}>
                                {product.product}
                            </option>
                        ))}
                    </select>
                    <input
                        type='number'
                        name='quantity_sold'
                        placeholder='Quantity Sold'
                        value={salesData.quantity_sold}
                        onChange={handleChange}
                        required
                    />
                    <input
                        type='number'
                        step='0.01'
                        name='selling_price'
                        placeholder='Selling Price'
                        value={salesData.selling_price}
                        onChange={handleChange}
                        required
                    />
                    <button className='container-button' type='submit'>Sell Item</button>
                </form>
            </div>
            <div  className='scroll-table'>
                <table>
                <h3>Sales Records</h3>
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
                                <td>
                                    {sale.selling_price !== undefined && sale.selling_price !== null
                                        ? `$${Number(sale.selling_price).toFixed(2)}`
                                        : '$0.00'}
                                </td>
                                <td>
                                    {sale.profit !== undefined && sale.profit !== null
                                        ? `$${Number(sale.profit).toFixed(2)}`
                                        : '$0.00'}
                                </td>
                                <td>{new Date(sale.sale_date).toLocaleDateString()}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default SalesPage;
