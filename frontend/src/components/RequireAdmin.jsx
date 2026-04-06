import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const RequireAdmin = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) return <div>Loading...</div>;

  if (!user || user.is_admin !== true) {
    return <Navigate to="/" replace />;
  }

  return children;
};

export default RequireAdmin;
