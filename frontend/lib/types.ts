export interface User {
  id: string;
  name: string;
  email: string;
}

export interface Club {
  id: string;
  name: string;
  slug: string;
  phone?: string | null;
  timezone: string;
  is_active: boolean;
}

export interface MeResponse {
  user: User;
  club: Club | null;
}

export interface RegisterPayload {
  name: string;
  email: string;
  password: string;
  club_name: string;
  club_slug: string;
}