import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';

interface Book {
  id: string;
  title: string;
  author: string;
  isbn: string;
  description: string;
  available_quantity: number;
}

const BrowseBooks: React.FC = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBooks = async () => {
      try {
        const params = search ? { search } : {};
        const response = await apiClient.get('/books', { params });
        setBooks(response.data.data);
      } catch (error) {
        console.error('Failed to load books:', error);
      } finally {
        setLoading(false);
      }
    };

    const debounceTimer = setTimeout(() => {
      fetchBooks();
    }, 300);

    return () => clearTimeout(debounceTimer);
  }, [search]);

  const handleCheckout = async (bookId: string) => {
    try {
      await apiClient.post('/checkouts', { book_id: bookId });
      alert('Book checked out successfully');
      // Refresh books
      const response = await apiClient.get('/books');
      setBooks(response.data.data);
    } catch (error: any) {
      const message = error.response?.data?.error || 'Failed to checkout book';
      alert(message);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Browse Books</h1>

        <div className="mb-6">
          <input
            type="text"
            placeholder="Search by title or author..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {books.map((book) => (
            <div key={book.id} className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-bold text-gray-900">{book.title}</h2>
              <p className="text-sm text-gray-600 mt-1">by {book.author}</p>
              <p className="text-xs text-gray-500 mt-2">ISBN: {book.isbn}</p>
              <p className="text-sm text-gray-700 mt-3">{book.description}</p>
              <div className="mt-4 flex items-center justify-between">
                <span
                  className={`text-sm font-medium ${
                    book.available_quantity > 0 ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {book.available_quantity > 0
                    ? `${book.available_quantity} available`
                    : 'Not available'}
                </span>
                <button
                  onClick={() => handleCheckout(book.id)}
                  disabled={book.available_quantity === 0}
                  className={`px-4 py-2 rounded-md text-white text-sm font-medium ${
                    book.available_quantity > 0
                      ? 'bg-blue-600 hover:bg-blue-700 cursor-pointer'
                      : 'bg-gray-400 cursor-not-allowed'
                  }`}
                >
                  Checkout
                </button>
              </div>
            </div>
          ))}
        </div>

        {books.length === 0 && (
          <div className="text-center text-gray-500 mt-12">
            No books found
          </div>
        )}
      </div>
    </div>
  );
};

export default BrowseBooks;
