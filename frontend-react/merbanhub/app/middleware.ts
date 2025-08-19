import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const url = request.nextUrl;
  const userRole = localStorage.getItem("userRole") || "ROLE_USER";

  // Redirect / to /login
  if (url.pathname === "/") {
    return NextResponse.redirect(new URL("/login", url));
  }

  // Protect /dashboard and /dashboard/upload for admin only
  if (
    (url.pathname.startsWith("/dashboard") ||
      url.pathname.startsWith("/dashboard/upload")) &&
    userRole !== "ROLE_ADMIN"
  ) {
    return NextResponse.redirect(new URL("/403", url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/", "/dashboard", "/dashboard/upload"],
};
