import React, { createContext, useState, useContext } from "react";

export const ProgressContext = createContext();

export const ProgressProvider = ({ children }) => {
  const [progress, setProgress] = useState({});

  const updateProgress = (taskId, value) => {
    setProgress((prevProgress) => ({
      ...prevProgress,
      [taskId]: value,
    }));
  };

  return (
    <ProgressContext.Provider value={{ progress, updateProgress }}>
      {children}
    </ProgressContext.Provider>
  );
};

export const useProgress = () => useContext(ProgressContext);
