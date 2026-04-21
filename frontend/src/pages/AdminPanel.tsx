import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';

interface Book {
  id: string;
  title: string;
  author: string;
  isbn: string;
  edition: string;
  available_quantity: number;
  total_quantity: number;
}

const AdminPanel: React.FC = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    title: '',
    author: '',
    isbn: '',
    edition: '1st Edition',
    description: '',
    total_quantity: 1,
  });

  useEffect(() => {
    const fetchBooks = async () => {
      try {
        const response = await apiClient.get('/books');
        setBooks(response.data.data);
      } catch (error) {
        console.error('Failed to load books:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchBooks();
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'total_quantity' ? parseInt(value) : value,
    });
  };

  const handleAddBook = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await apiClient.post('/books', formData);
      setBooks([...books, response.data]);
      setFormData({
        title: '',
        author: '',
        isbn: '',
        edition: '1st Edition',
        description: '',
        total_quantity: 1,
      });
      alert('Book added successfully');
    } catch (error) {
      console.error('Failed to add book:', error);
      alert('Failed to add book');
    }
  };

  const handleDeleteBook = async (bookId: string) => {
    if (window.confirm('Are you sure you want to delete this book?')) {
      try {
        await apiClient.delete(`/books/${bookId}`);
        setBooks(books.filter((b) => b.id !== bookId));
      } catch (error) {
        console.error('Failed to delete book:', error);
      }
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Admin Panel</h1>

        {/* Add Book Form */}
        <div className="bg-white shadow rounded-lg mb-8 p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Add New Book</h2>
          <form onSubmit={handleAddBook} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                type="text"
                name="title"
                placeholder="Title"
                value={formData.title}
                onChange={handleInputChange}
                required
                className="px-3 py-2 border border-gray-300 rounded-md"
              />
              <input
                type="text"
                name="author"
                placeholder="Author"
                value={formData.author}
                onChange={handleInputChange}
                required
                className="px-3 py-2 border border-gray-300 rounded-md"
              />
              <input
                type="text"
                name="isbn"
                placeholder="ISBN"
                value={formData.isbn}
                onChange={handleInputChange}
                className="px-3 py-2 border border-gray-300 rounded-md"
              />
              <input
                type="text"
                name="edition"
                placeholder="Edition"
                value={formData.edition}
                onChange={handleInputChange}
                className="px-3 py-2 border border-gray-300 rounded-md"
              />
              <input
                type="number"
                name="total_quantity"
                placeholder="Quantity"
                value={formData.total_quantity}
                onChange={handleInputChange}
                min="1"
                className="px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <textarea
              name="description"
              placeholder="Description"
              value={formData.description}
              onChange={handleInputChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Add Book
            </button>
          </form>
        </div>

        {/* Books List */}
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="px-4 py-5 sm:px-6">
            <h2 className="text-lg font-medium text-gray-900">Books ({books.length})</h2>
          </div>
          <div className="border-t border-gray-200 overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                    Title
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                    Author
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                    ISBN
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                    Available
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {books.map((book) => (
                  <tr key={book.id}>
                    <td className="px-6 py-4 text-sm text-gray-900">{book.title}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{book.author}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{book.isbn}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {book.available_quantity}/{book.total_quantity}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <button
                        onClick={() => handleDeleteBook(book.id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;
