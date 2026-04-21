import React from 'react';
import apiClient from '../api/client';

const LoginPage: React.FC = () => {
  const handleGoogleLogin = async () => {
    try {
      // Placeholder for OAuth Google login
      console.log('Google login initiated');
      // In Phase 2, implement full OAuth flow
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  const handleGithubLogin = async () => {
    try {
      // Placeholder for OAuth GitHub login
      console.log('GitHub login initiated');
      // In Phase 2, implement full OAuth flow
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Library Management System
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Sign in to your account
          </p>
        </div>
        <div className="mt-8 space-y-6">
          <button
            onClick={handleGoogleLogin}
            className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Sign in with Google
          </button>
          <button
            onClick={handleGithubLogin}
            className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Sign in with GitHub
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
