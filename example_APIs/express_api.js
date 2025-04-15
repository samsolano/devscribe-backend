const express = require('express');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

// In-memory data storage
let users = [
    { id: 1, name: 'Alice', balance: 1000.0 },
    { id: 2, name: 'Bob', balance: 750.0 },
    { id: 3, name: 'Charlie', balance: 500.0 }
];

let products = [
    { id: 1, name: 'Widget', price: 19.99 },
    { id: 2, name: 'Gadget', price: 29.99 },
    { id: 3, name: 'Doohickey', price: 9.99 }
];

let transactions = [];

// --- Logic and Helper Functions ---

function calculateDiscountedPrice(price, discountRate) {
    return price * (1 - discountRate / 100);
}

function generateTransactionId() {
    return Math.floor(Math.random() * (999999 - 100000 + 1)) + 100000;
}

function recordTransaction(userId, productId, quantity, totalPrice) {
    const transaction = {
        transaction_id: generateTransactionId(),
        user_id: userId,
        product_id: productId,
        quantity: quantity,
        total_price: totalPrice,
        timestamp: new Date().toISOString()
    };
    transactions.push(transaction);
    return transaction;
}

// --- Express API Endpoints ---

// GET /users
app.get('/users', (req, res) => {
    res.json({ users });
});

// GET /products
app.get('/products', (req, res) => {
    res.json({ products });
});

// GET /transactions
app.get('/transactions', (req, res) => {
    const userId = parseInt(req.query.user_id);
    if (userId) {
        const filteredTransactions = transactions.filter(t => t.user_id === userId);
        return res.json({ transactions: filteredTransactions });
    }
    res.json({ transactions });
});

// POST /purchase
app.post('/purchase', (req, res) => {
    const { user_id, product_id, quantity = 1, discount_rate = 0 } = req.body;

    if (!user_id || !product_id) {
        return res.status(400).json({ error: 'Missing required fields: user_id, product_id' });
    }

    const user = users.find(u => u.id === user_id);
    if (!user) {
        return res.status(404).json({ error: 'User not found' });
    }

    const product = products.find(p => p.id === product_id);
    if (!product) {
        return res.status(404).json({ error: 'Product not found' });
    }

    const discountedPrice = calculateDiscountedPrice(product.price, discount_rate);
    const totalPrice = discountedPrice * quantity;

    if (user.balance < totalPrice) {
        return res.status(400).json({ error: 'Insufficient balance' });
    }

    user.balance -= totalPrice;
    const transaction = recordTransaction(user_id, product_id, quantity, totalPrice);

    res.json({
        message: 'Purchase successful',
        transaction,
        new_balance: user.balance
    });
});

// POST /recharge
app.post('/recharge', (req, res) => {
    const { user_id, amount = 0 } = req.body;

    if (!user_id || amount <= 0) {
        return res.status(400).json({ error: 'Missing or invalid fields: user_id, amount' });
    }

    const user = users.find(u => u.id === user_id);
    if (!user) {
        return res.status(404).json({ error: 'User not found' });
    }

    user.balance += amount;

    res.json({
        message: 'Recharge successful',
        new_balance: user.balance
    });
});

// GET /summary
app.get('/summary', (req, res) => {
    const totalUsers = users.length;
    const totalTransactions = transactions.length;
    const totalRevenue = transactions.reduce((sum, t) => sum + t.total_price, 0);

    const report = {
        total_users: totalUsers,
        total_transactions: totalTransactions,
        total_revenue: parseFloat(totalRevenue.toFixed(2))
    };

    res.json(report);
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Express API server running on port ${PORT}`);
});
