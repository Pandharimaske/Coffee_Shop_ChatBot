export const callChatBotAPI = async (messages) => {
  // Simulate an API response with a delay
  const botResponse = {
    content: "How can I assist you with your coffee order?",
  };

  // Simulate a delay to make it feel like an actual API call
  return new Promise((resolve) => setTimeout(() => resolve(botResponse), 1000));
};
