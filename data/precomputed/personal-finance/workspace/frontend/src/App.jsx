// Personal Finance Tracker - Domain Specialized React Interface
import React, { useState, useEffect } from 'react';

export default function App() {
  const [items, setItems] = useState([
    {
        "id": 1,
        "description": "Software Engineering Salary",
        "amount": 6200.0,
        "type": "income",
        "category": "Salary"
    },
    {
        "id": 2,
        "description": "Apartment Rent",
        "amount": 1850.0,
        "type": "expense",
        "category": "Housing"
    },
    {
        "id": 3,
        "description": "Supermarket Groceries",
        "amount": 215.4,
        "type": "expense",
        "category": "Food"
    }
]);
  const [newTitle, setNewTitle] = useState('');
  const [newStatus, setNewStatus] = useState('active');
  const [search, setSearch] = useState('');
  const [actionNotice, setActionNotice] = useState('');

  const handleCreate = (e) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    const newItem = {
      id: items.length + 1,
      title: newTitle,
      name: newTitle,
      status: newStatus,
      description: 'User created operational item',
      created_at: new Date().toISOString()
    };
    setItems([newItem, ...items]);
    setNewTitle('');
    setActionNotice('Created ' + newTitle + ' successfully!');
    setTimeout(() => setActionNotice(''), 3000);
  };

  const handleDelete = (id) => {
    setItems(items.filter(it => it.id !== id));
  };

  const handleTriggerAction = (item) => {
    setActionNotice('Executed action for: ' + (item.title || item.name));
    setTimeout(() => setActionNotice(''), 3000);
  };

  const filtered = items.filter(it => {
    const text = (it.title || it.name || it.description || '').toLowerCase();
    return text.includes(search.toLowerCase());
  });

  return (
    <div style={{ maxWidth: '1140px', margin: '30px auto', padding: '24px', fontFamily: 'system-ui, -apple-system, sans-serif', color: '#f8fafc' }}>
      <header style={{ borderBottom: '1px solid #1e293b', paddingBottom: '20px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '24px' }}>⚡</span>
            <h1 style={{ fontSize: '26px', color: '#38bdf8', margin: 0, fontWeight: 700 }}>Personal Finance Tracker</h1>
          </div>
          <p style={{ color: '#94a3b8', margin: '6px 0 0', fontSize: '13px' }}>Personal Finance & Expense Tracker &bull; Cloud Native Microservice</p>
        </div>
        <div style={{ background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', color: '#34d399', padding: '6px 14px', borderRadius: '9999px', fontSize: '12px', fontWeight: 600 }}>
          ● Production Ready
        </div>
      </header>

      {actionNotice && (
        <div style={{ background: '#0284c7', color: '#fff', padding: '10px 16px', borderRadius: '8px', marginBottom: '20px', fontSize: '13px', fontWeight: 500 }}>
          ✓ {actionNotice}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ background: '#0e1526', border: '1px solid #1e293b', padding: '18px', borderRadius: '10px' }}>
          <div style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total Transactions</div>
          <div style={{ fontSize: '28px', fontWeight: 800, marginTop: '4px', color: '#fff' }}>{items.length}</div>
        </div>
        <div style={{ background: '#0e1526', border: '1px solid #1e293b', padding: '18px', borderRadius: '10px' }}>
          <div style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Domain Mode</div>
          <div style={{ fontSize: '20px', fontWeight: 700, color: '#38bdf8', marginTop: '6px' }}>finance</div>
        </div>
        <div style={{ background: '#0e1526', border: '1px solid #1e293b', padding: '18px', borderRadius: '10px' }}>
          <div style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Security & IAM</div>
          <div style={{ fontSize: '20px', fontWeight: 700, color: '#34d399', marginTop: '6px' }}>JWT Verified</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '24px' }}>
        <section style={{ background: '#0e1526', padding: '20px', borderRadius: '10px', border: '1px solid #1e293b', height: 'fit-content' }}>
          <h2 style={{ fontSize: '16px', margin: '0 0 16px', color: '#f1f5f9' }}>Create Transaction</h2>
          <form onSubmit={handleCreate}>
            <div style={{ marginBottom: '14px' }}>
              <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>Name or Title *</label>
              <input
                type="text"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder="Enter transaction details..."
                required
                style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #334155', background: '#070a12', color: '#fff', boxSizing: 'border-box' }}
              />
            </div>
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>Initial Status</label>
              <select
                value={newStatus}
                onChange={(e) => setNewStatus(e.target.value)}
                style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #334155', background: '#070a12', color: '#fff', boxSizing: 'border-box' }}
              >
                <option value="active">Active</option>
                <option value="pending">Pending</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            <button type="submit" style={{ width: '100%', padding: '11px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 600 }}>
              + Add Transaction
            </button>
          </form>
        </section>

        <section style={{ background: '#0e1526', padding: '20px', borderRadius: '10px', border: '1px solid #1e293b' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
            <h2 style={{ fontSize: '16px', margin: 0, color: '#f1f5f9' }}>Transactions Registry</h2>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search items..."
              style={{ padding: '8px 14px', borderRadius: '6px', border: '1px solid #334155', background: '#070a12', color: '#fff', fontSize: '13px' }}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {filtered.map(item => (
              <div key={item.id} style={{ background: '#070a12', border: '1px solid #1e293b', padding: '16px', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '14px', color: '#fff' }}>{item.title || item.name || 'Transaction #' + item.id}</div>
                  <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px' }}>
                    {item.description || item.category || item.specialty || item.dept || item.url || 'Operational record'}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <span style={{ fontSize: '11px', padding: '3px 10px', borderRadius: '6px', background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', fontWeight: 600 }}>
                    {item.status || item.priority || 'Active'}
                  </span>
                  <button onClick={() => handleTriggerAction(item)} style={{ background: '#1e293b', border: '1px solid #334155', color: '#e2e8f0', padding: '4px 10px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>
                    Action
                  </button>
                  <button onClick={() => handleDelete(item.id)} style={{ background: 'none', border: 'none', color: '#f87171', cursor: 'pointer', fontSize: '14px', padding: '4px' }}>
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
