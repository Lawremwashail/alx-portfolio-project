import axios from 'axios';
import React, { useEffect, useState } from 'react'

const SalesPage = () => {
    const [products, setProducts] = useState([]);
    const [salesData, setSalesData] = useState({
        product_sold: "",
        quantity_sold: "",
        selling_price: ""
    });
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [sales, setSales] = useState([]);

    useEffect(() => {
        fetchProducts();
        fetchSales();
    }, []);

    const fetchProducts = async () => {
        try {
            const response = await axios.get("http://127.0.0.1:8000/api/inventory/");
            setProducts(response.data)
        } catch (error) {
            console.error("Error fetching products", error);
            setError("Failed Loading products");            
        } finally {
            setIsLoading(false);
        }
    }
    const fetchSales = async () => {
        try {
            const response = await axios.get("http://127.0.0.1:8000/api/sales/");
            setSales(response.data)
        } catch (error) {
            console.error("Error fetching sales", error);
            setError("Failed Loading sales");            
        }
    }

    const handleChange = (e) => {
        const { name, value } = e.target;
        setSalesData((prevData) => ({
            ...prevData, [name]: value,
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault()
        try {
            const salesPayload = {
                ...salesData,
                product_sold: salesData.product_sold // Send product ID as `product_sold_id`
            };
            await axios.post("http://127.0.0.1:8000/api/sales/", salesPayload);
            setSalesData({
                product_sold: "", 
                quantity_sold: "", 
                selling_price: "" 
            });
            fetchProducts();
            fetchSales();
        } catch (error) {
            console.error("Error creating sale", error);
            setError("Failed to create sale");
        }
    }
    
    
    if (isLoading) return <p>Loading...</p>;
    if (error) return <p>{error}</p>;

    return (
        <div>
            <h2>Sales Page</h2>
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
                <button type='submit'>Sell Item</button>
            </form>
            <h3>Sales Records</h3>
            <table>
                <thead>
                    <tr>
                        <th>Product</th>
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
                                {
                                    sale.selling_price !== undefined && sale.selling_price !== null
                                    ? `$${Number(sale.selling_price).toFixed(2)}`
                                    : '$0.00'
                                }
                            </td>
                            <td>
                                {
                                    sale.profit !== undefined && sale.profit !== null
                                    ? `$${Number(sale.profit).toFixed(2)}`
                                    : '$0.00'
                                }
                            </td>
                            <td>{new Date(sale.sale_date).toLocaleDateString()}</td>
                        </tr>
                    ))}
                </tbody>
            </table>


        </div>
  )
}

export default SalesPage;