import React, { ReactNode } from 'react';
import Navbar from './Navbar';
import RoutingDebug from './RoutingDebug';
import { useTheme } from '../contexts/ThemeContext';

interface LayoutProps {
  children: ReactNode;
}

function Layout({ children }: LayoutProps) {
  const { isDarkMode } = useTheme();
  
  return (
    <div className={`min-h-screen transition-colors duration-300 ${
      isDarkMode ? 'bg-gray-900' : 'bg-gray-50'
    }`}>
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
      <RoutingDebug />
    </div>
  );
}

export default Layout;