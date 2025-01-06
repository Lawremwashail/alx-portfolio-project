import axios from 'axios';
import React, { useEffect, useState, useContext, useCallback } from 'react';
import AuthContext from '../context/AuthContext';
import './Pages.css';

const InventoryPage = () => {
    const { authTokens } = useContext(AuthContext);
    const [products, setProducts] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [formData, setFormData] = useState({
        product: '',
        quantity: '',
        price: ''
    });
    const [editingItem, setEditingItem] = useState(null);

    // Use useCallback to memoize fetchProducts function
    const fetchProducts = useCallback(async () => {
        setIsLoading(true);
        try {
            const response = await axios.get("http://127.0.0.1:8000/api/inventory/", {
                headers: {
                    Authorization: `Bearer ${authTokens?.access}`,
                }
            });
            setProducts(response.data);
            setError(null); // Reset error on successful fetch
        } catch (error) {
            setError('Failed to load products. Please try again.');
        } finally {
            setIsLoading(false);
        }
    }, [authTokens?.access]); // Add authTokens dependency to ensure it's always up-to-date

    // Fetch products initially on mount
    useEffect(() => {
        fetchProducts();
    }, [fetchProducts]); // Only re-run if fetchProducts changes

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prevData) => ({
            ...prevData, [name]: value,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!formData.product || !formData.quantity || !formData.price) {
            setError('All fields are required');
            return;
        }

        try {
            const url = editingItem
                ? `http://127.0.0.1:8000/api/inventory/${editingItem.id}/`
                : "http://127.0.0.1:8000/api/inventory/";
            const method = editingItem ? 'put' : 'post';

            await axios[method](url, formData, {
                headers: {
                    Authorization: `Bearer ${authTokens?.access}`,
                }
            });

            fetchProducts();
            setFormData({ product: '', quantity: '', price: '' }); // Clear form after submission
            setEditingItem(null); // Reset the editing state

            // Reset error if operation succeeds
            setError(null);

        } catch (error) {
            setError('Failed to save item. Please try again.');
        }
    };

    const handleEdit = (product) => {
        setFormData({ product: product.product, quantity: product.quantity, price: product.price });
        setEditingItem(product);
    };

    const handleDelete = async (id) => {
        try {
            await axios.delete(`http://127.0.0.1:8000/api/inventory/${id}/`, {
                headers: {
                    Authorization: `Bearer ${authTokens?.access}`,
                }
            });
            fetchProducts(); // Refetch products after deletion
            setError(null); // Reset error on successful delete
        } catch (error) {
            setError('Failed to delete item. Please try again.');
        }
    };

    if (isLoading) return <p>Loading...</p>;
    if (error) return <p>{error}</p>;

    return (
        <div className='container'>
            <h2>Inventory</h2>

            <div className="form-container">
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        name="product"
                        placeholder="Product Name"
                        value={formData.product}
                        onChange={handleChange}
                        required
                    />
                    <input
                        type="number"
                        name="quantity"
                        placeholder="Quantity"
                        value={formData.quantity}
                        onChange={handleChange}
                        required
                    />
                    <input
                        type="number"
                        step="0.01"
                        name="price"
                        placeholder="Price"
                        value={formData.price}
                        onChange={handleChange}
                        required
                    />
                    <button className='container-button' type="submit">{editingItem ? 'Edit' : 'Add'} Item</button>
                </form>
            </div>
            <div className='scroll-table'>
                <h3>Current Stock</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Quantity</th>
                            <th>Price</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {products.map((product) => (
                            <tr key={product.id}>
                                <td>{product.product}</td>
                                <td>{product.quantity}</td>
                                <td>
                                    {product.price !== undefined && product.price !== null
                                        ? `$${Number(product.price).toFixed(2)}`
                                        : '$0.00'}
                                </td>
                                <td>
                                    <button className='container-button' onClick={() => handleEdit(product)}>Edit</button>
                                    <button className='container-button' onClick={() => handleDelete(product.id)}>Delete</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>            
        </div>
    );
};

export default InventoryPage;
