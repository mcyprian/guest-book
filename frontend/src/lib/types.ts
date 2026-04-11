export interface Child {
  id: string;
  name: string;
  position: number;
}

export interface Guest {
  id: string;
  stay_from: string;
  stay_to: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  birth_place: string;
  nationality: string;
  permanent_address: string;
  travel_purpose: string;
  passport_number: string;
  visa_details: string | null;
  accommodation_name: string;
  accommodation_address: string;
  children: Child[];
  pdf_generated_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface GuestListResponse {
  items: Guest[];
  total: number;
  page: number;
  size: number;
}

export interface ChildCreate {
  name: string;
  position: number;
}

export interface GuestCreate {
  stay_from: string;
  stay_to: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  birth_place: string;
  nationality: string;
  permanent_address: string;
  travel_purpose: string;
  passport_number: string;
  visa_details?: string | null;
  children: ChildCreate[];
}

export interface ConfigResponse {
  accommodation_name: string;
  accommodation_address: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}
