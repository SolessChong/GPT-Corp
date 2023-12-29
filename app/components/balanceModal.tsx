import React, { useState, useEffect } from "react";
import styles from "./balanceModal.module.scss"; // Make sure to import your actual CSS module
import { getHeaders } from "../client/api";

interface BalanceModalProps {
  userId: string; // Assuming you pass the user ID as a prop
}

const BalanceModal: React.FC<BalanceModalProps> = ({ userId }) => {
  const [balance, setBalance] = useState<number | null>(null);
  const [tokensUsed, setTokensUsed] = useState<number | null>(null);
  const [email, setEmail] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(
          `https://api.easyai.codes/api/users/${userId}`,
          {
            method: "GET",
            headers: getHeaders(),
          },
        );
        if (!response.ok) {
          throw new Error("Please login first"); // Custom error message when the response is not ok
        }
        const data = await response.json();
        setBalance(data.balance);
        setTokensUsed(data.tokens_used);
        setEmail(data.email);
      } catch (error) {
        setError("User Balance: Please login first"); // Set custom error message here
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [userId]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>{error}</div>; // Display the custom error message
  }

  return (
    <div className={styles.modalBackdrop}>
      <div className={styles.modal}>
        <h3 className={styles.modalTitle}>User Balance</h3>
        <div className={styles.modalInfo}>
          {email && <p>Email: {email}</p>}
          <p>Balance: {balance?.toFixed(2)}</p>
          <p>Tokens used: {tokensUsed?.toLocaleString()}</p>
        </div>
      </div>
    </div>
  );
};

export default BalanceModal;
