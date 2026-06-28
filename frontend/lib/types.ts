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
  timezone?: string | null;
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

export interface Court {
  id: string;
  club_id: string;
  name: string;
  price_per_hour: number | null;
  is_active: boolean;
  created_at: string;
}