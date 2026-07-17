export interface Faculty {
  name: string;
  image: string | null;
  subject: string | null;
  experience_years: string | null;
  quote: string | null;
  demo_url: string | null;
  students_mentored: number;
}

export interface Plan {
  title: string;
  validity: number | null;
  validity_unit: string | null;
  validity_title: string | null;
}

export interface ExamBadge {
  name: string;
  thumbnail: string | null;
}

export interface Section {
  title: string;
  html: string;
}

export interface Faq {
  question: string;
  answer: string;
}

export interface PackageListing {
  package_id: string;
  display_code: string;
  title: string;
  thumbnail_url: string | null;
  price_bdt: string;
  language: string | null;
  batch_type: string;
  live_classes_count: number;
  video_count: number;
  start_date: string | null;
  display_order: number;
}

export interface PackagePdp {
  package_id: string;
  display_code: string;
  title: string;
  thumbnail_url: string | null;
  price_bdt: string;
  language: string | null;
  batch_type: string;
  live_classes_count: number;
  video_count: number;
  start_date: string | null;
  end_date: string | null;
  seats: number | null;
  timings: string | null;
  plan: Plan | null;
  highlights: string[];
  exam_badges: ExamBadge[];
  faculties: Faculty[];
  overview_html: string | null;
  sections: Section[];
  faqs: Faq[];
}
