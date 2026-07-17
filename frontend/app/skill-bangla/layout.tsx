import { Mulish } from "next/font/google";

const mulish = Mulish({
  variable: "--font-mulish",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
});

export default function SkillBanglaLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className={`${mulish.variable} font-sb bg-sb-page text-sb-ink min-h-screen`}>
      {children}
    </div>
  );
}
