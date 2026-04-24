import { createContext, useContext } from "react";

type AuthState = {
  userId: string | null;
  token: string | null;
};

export const AuthContext = createContext<AuthState>({
  userId: null,
  token: null,
});

export function useAuth() {
  return useContext(AuthContext);
}
