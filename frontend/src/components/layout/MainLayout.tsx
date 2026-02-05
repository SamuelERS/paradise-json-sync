/**
 * MainLayout Component (Componente Layout Principal)
 *
 * Main page structure with header, content area, and footer.
 * Estructura principal de página con encabezado, área de contenido y pie de página.
 */
import React from 'react';
import { Header } from './Header';
import { Footer } from './Footer';
import { Container } from './Container';

interface MainLayoutProps {
  /** Page content / Contenido de la página */
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-1 pt-20 pb-8">
        <Container>{children}</Container>
      </main>
      <Footer />
    </div>
  );
}
