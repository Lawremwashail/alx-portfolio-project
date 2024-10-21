import axios from 'axios';
import React, { useEffect, useState } from 'react'

const InventoryPage = () => {
    const [products, setProducts] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [formData, setFormData] = useState({
        product: "",
        quantity: "",
        price: ""
    });
    const [editingItem, setEditingItem] = useState(null);
    
    useEffect(() => {
        fetchProducts()
    }, []);

    const fetchProducts = async () => {
        try {
            const response = await axios.get("http://127.0.0.1:8000/api/inventory/");
            setProducts(response.data);
            console.log(response.data);

        } catch (error) {
            console.error("Error fetching products", error)
            setError("Failed Loading products")
        } finally {
            setIsLoading(false)
        }
    };

    const handleChange = (e) => {
        const {name, value} = e.target;
        setFormData((prevData) => ({
            ...prevData, [name]: value,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault(e)
        try {
            if (editingItem) {
                await axios.put(`http://127.0.0.1:8000/api/inventory/${editingItem.id}/`, formData);
                // setFormData({product: '', quantity: '', price: ''})
                // setEditingItem(null);
            } else {
                await axios.post(`http://127.0.0.1:8000/api/inventory/`, formData);

            }
            fetchProducts();
            setFormData({product: '', quantity: '', price: ''})
            setEditingItem(null);

        } catch (error) {
            console.error("Error saving item", error);
            setError("Failed to save item")
        }

    }
    const handleEdit = (product) => {
        setFormData({product: product.product, quantity: product.quantity, price: product.price})
        setEditingItem(product)
    }

    const handleDelete = async (id) => {
        try {
            await axios.delete(`http://127.0.0.1:8000/api/inventory/${id}/`);
            fetchProducts()
        } catch (error) {
            console.error("Error deleting item", error);
            setError("Failed to delete item");
        }
    }

    if (isLoading) return <p>Loading...</p>
    if (error) return <p>{error}</p>;
  return (
    <div>
        <h2>Inventory</h2>
        <form onSubmit={handleSubmit}>
            <input
                type='text'
                name='product'
                placeholder='Product Name'
                value={formData.product}
                onChange={handleChange}
                required            
            />
            <input
                type='number'
                name='quantity'
                placeholder='Quantity'
                value={formData.quantity}
                onChange={handleChange}
                required            
            />
            <input
                type='number'
                step='0.01'
                name='price'
                placeholder='Price'
                value={formData.price}
                onChange={handleChange}
                required            
            />
            <button type='submit'>{editingItem ? 'Edit' : 'Add'} Item</button>
        </form>
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
                            {
                                product.price !== undefined && product.price !== null ? 
                                `$${Number(product.price).toFixed(2)}` : 
                                '$0.00'
                            }
                        </td>
                        <td>
                            <button onClick={() => handleEdit(product)}>Edit</button>
                            <button onClick={() => handleDelete(product.id)}>Delete</button>
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
  )
}

export default InventoryPage;