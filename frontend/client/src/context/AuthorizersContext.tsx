import { createContext, useContext, useState, ReactNode } from 'react';

interface Authorizers {
  approveAuthorizer?: string;
  siloAuthorizer?: string;
}

interface AuthorizersContextType {
  authorizers: Authorizers;
  setAuthorizers: (authorizers: Authorizers) => void;
}

const AuthorizersContext = createContext<AuthorizersContextType | undefined>(undefined);

export function AuthorizersProvider({ children }: { children: ReactNode }) {
  const [authorizers, setAuthorizers] = useState<Authorizers>({});

  return (
    <AuthorizersContext.Provider value={{ authorizers, setAuthorizers }}>
      {children}
    </AuthorizersContext.Provider>
  );
}

export function useAuthorizers() {
  const context = useContext(AuthorizersContext);
  if (!context) {
    throw new Error('useAuthorizers must be used within AuthorizersProvider');
  }
  return context;
} 