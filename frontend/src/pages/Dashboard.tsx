import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';

interface Checkout {
  id: string;
  book: {
    title: string;
    author: string;
    isbn: string;
  };
  due_date: string;
  returned_at: string | null;
  status: string;
}

const Dashboard: React.FC = () => {
  const [checkouts, setCheckouts] = useState<Checkout[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCheckouts = async () => {
      try {
        const response = await apiClient.get('/checkouts');
        setCheckouts(response.data.data);
      } catch (err) {
        setError('Failed to load checkouts');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchCheckouts();
  }, []);

  const handleReturn = async (checkoutId: string) => {
    try {
      await apiClient.post(`/checkouts/${checkoutId}/return`);
      // Refresh checkouts
      const response = await apiClient.get('/checkouts');
      setCheckouts(response.data.data);
    } catch (err) {
      setError('Failed to return book');
      console.error(err);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">My Dashboard</h1>

        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:px-6">
            <h2 className="text-lg font-medium text-gray-900">
              Checked Out Books ({checkouts.length})
            </h2>
          </div>
          <div className="border-t border-gray-200">
            {checkouts.length === 0 ? (
              <div className="px-4 py-5 sm:px-6 text-center text-gray-500">
                No checked out books
              </div>
            ) : (
              <ul className="divide-y divide-gray-200">
                {checkouts.map((checkout) => (
                  <li key={checkout.id} className="px-4 py-5 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-medium text-gray-900">
                          {checkout.book.title}
                        </h3>
                        <p className="mt-1 text-sm text-gray-600">
                          by {checkout.book.author}
                        </p>
                        <p className="mt-1 text-sm text-gray-600">
                          Due: {new Date(checkout.due_date).toLocaleDateString()}
                        </p>
                      </div>
                      {checkout.status === 'active' && (
                        <button
                          onClick={() => handleReturn(checkout.id)}
                          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
                        >
                          Return
                        </button>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
