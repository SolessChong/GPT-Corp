import styles from "./auth.module.scss";
import { IconButton } from "./button";

import { useNavigate } from "react-router-dom";
import { Path } from "../constant";
import { useAccessStore } from "../store";
import Locale from "../locales";

import BotIcon from "../icons/bot.svg";
import { useEffect, useState } from "react";
import { getClientConfig } from "../config/client";

// Import axios or another HTTP client to make the POST request
import axios from "axios";

export function AuthPage() {
  const navigate = useNavigate();
  const accessStore = useAccessStore();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const goHome = () => navigate(Path.Home);
  const goChat = () => navigate(Path.Chat);
  const resetAccessCode = () => {
    accessStore.update((access) => {
      access.openaiApiKey = "";
      access.accessCode = "";
    });
  };
  const handleLogin = async () => {
    try {
      // Replace with your Flask backend URL and endpoint
      const response = await axios.post("https://api.easyai.codes/login", {
        username: username,
        password: password,
      });

      // If login is successful, navigate to the chat page
      if (response.status === 200) {
        // Here you might want to store the login state in accessStore
        useAccessStore
          .getState()
          .setLocalAccessToken(response.data.access_token); // Update the store with the token
        useAccessStore.getState().setUserId(response.data.user_id);
        goChat();
      } else {
        // Handle non-successful login attempts here
        setErrorMessage("Invalid credentials. Please try again.");
      }
    } catch (error) {
      // Handle errors here (e.g., network error, server error)
      // setErrorMessage(error.response?.data?.message || 'An error occurred. Please try again.');
      setErrorMessage("An error occurred. Please try again.");
    }
  };

  useEffect(() => {
    if (getClientConfig()?.isApp) {
      navigate(Path.Settings);
    }
  }, [navigate]);

  return (
    <div className={styles["auth-page"]}>
      <div className={`no-dark ${styles["auth-logo"]}`}>
        <BotIcon />
      </div>

      <div className={styles["auth-title"]}>{Locale.Auth.Title}</div>
      <div className={styles["auth-tips"]}>{Locale.Auth.Tips}</div>

      <input
        className={styles["auth-input"]}
        type="text"
        placeholder={Locale.Auth.UsernamePlaceholder}
        value={username}
        onChange={(e) => setUsername(e.currentTarget.value)}
      />
      <input
        className={styles["auth-input"]}
        type="password"
        placeholder={Locale.Auth.PasswordPlaceholder}
        value={password}
        onChange={(e) => setPassword(e.currentTarget.value)}
      />

      {errorMessage && (
        <div className={styles["auth-error-message"]}>{errorMessage}</div>
      )}

      <div className={styles["auth-actions"]}>
        <IconButton
          text={Locale.Auth.Confirm}
          type="primary"
          onClick={handleLogin}
        />
        <IconButton
          text={Locale.Auth.Later}
          onClick={() => {
            resetAccessCode();
            goHome();
          }}
        />
      </div>
    </div>
  );
}
