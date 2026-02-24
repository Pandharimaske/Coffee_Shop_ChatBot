import { createContext, useContext, useState, useEffect } from "react";
import { authAPI, userAPI } from "../services/api";

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);       // { id, email, username }
  const [loading, setLoading] = useState(true); // checking token on mount

  // On mount — if token exists, fetch current user
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      userAPI.getMe()
        .then(setUser)
        .catch(() => {
          // Token expired or invalid — clear it
          authAPI.logout();
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    await authAPI.login(email, password);
    const me = await userAPI.getMe();
    setUser(me);
    return me;
  };

  const register = async (username, email, password) => {
    await authAPI.register(username, email, password);
    await login(email, password);
  };

  const logout = () => {
    authAPI.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
