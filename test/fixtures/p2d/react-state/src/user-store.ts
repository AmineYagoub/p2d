import { create } from "zustand";

type UserState = {
  userId: string | null;
  displayName: string | null;
};

export const useUserStore = create<UserState>(() => ({
  userId: null,
  displayName: null,
}));
